"""
EQ12 Adaptive Resource Monitor & Auto-Scaler
Dynamically adjusts worker pools based on real-time resource metrics
Based on: Conservative scaling, measurement-first approach, safety nets
"""

import psutil
import time
import os
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from collections import deque
import threading
import gc

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ResourceMetrics:
    """Snapshot of system resource usage"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_available_gb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    active_workers: int
    queue_depth: int
    
    def to_dict(self):
        return asdict(self)


@dataclass
class WorkerMetrics:
    """Per-worker performance tracking"""
    worker_id: int
    cpu_percent: float
    memory_mb: float
    tasks_completed: int
    tasks_failed: int
    avg_task_duration: float
    last_gc_time: Optional[float]
    
    def to_dict(self):
        return asdict(self)


@dataclass
class ThrottleDecision:
    """Auto-scaling decision with reasoning"""
    action: str  # "scale_up", "scale_down", "maintain", "emergency_stop"
    current_workers: int
    recommended_workers: int
    reason: str
    confidence: float  # 0.0 to 1.0
    metrics_snapshot: ResourceMetrics


class ResourceMonitor:
    """
    Continuous resource monitoring with auto-scaling recommendations
    
    Conservative approach:
    - Start with 6-8 workers (not 10)
    - Scale up slowly with proof of stability
    - Scale down aggressively on resource pressure
    - Emergency stop on critical thresholds
    """
    
    # Safety thresholds (conservative)
    CRITICAL_MEMORY_PERCENT = 85.0  # Emergency stop
    WARNING_MEMORY_PERCENT = 75.0   # Scale down
    SAFE_MEMORY_PERCENT = 60.0      # Can scale up
    
    CRITICAL_CPU_PERCENT = 95.0     # Emergency throttle
    WARNING_CPU_PERCENT = 85.0      # Scale down
    SAFE_CPU_PERCENT = 70.0         # Can scale up
    
    # Worker limits (conservative start)
    MIN_WORKERS = 2
    SAFE_START_WORKERS = 6          # Start here, not 10
    MAX_WORKERS = 10                # Hardware limit
    
    # Measurement window
    METRICS_WINDOW_SIZE = 60        # Keep last 60 measurements
    DECISION_INTERVAL = 30          # Make decisions every 30 seconds
    
    def __init__(self, log_dir: str = None):
        self.log_dir = Path(log_dir or "C:/EQ12_BROKEN_20251122_210342/logs/resource_monitor")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Metrics history
        self.metrics_history: deque = deque(maxlen=self.METRICS_WINDOW_SIZE)
        self.worker_metrics: Dict[int, WorkerMetrics] = {}
        
        # Baseline measurements
        self.baseline_disk_io = psutil.disk_io_counters()
        self.baseline_network = psutil.net_io_counters()
        
        # Current state
        self.current_workers = self.SAFE_START_WORKERS
        self.is_monitoring = False
        self.monitor_thread = None
        
        # Decision history
        self.decision_history: List[ThrottleDecision] = []
        
        logger.info(f"ResourceMonitor initialized. Log dir: {self.log_dir}")
        logger.info(f"Starting with {self.SAFE_START_WORKERS} workers (conservative)")
    
    def capture_metrics(self, active_workers: int = None, queue_depth: int = 0) -> ResourceMetrics:
        """Capture current system resource snapshot"""
        
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        
        # Disk I/O
        disk_io = psutil.disk_io_counters()
        disk_read_mb = (disk_io.read_bytes - self.baseline_disk_io.read_bytes) / 1024 / 1024
        disk_write_mb = (disk_io.write_bytes - self.baseline_disk_io.write_bytes) / 1024 / 1024
        
        # Network I/O
        net_io = psutil.net_io_counters()
        net_sent_mb = (net_io.bytes_sent - self.baseline_network.bytes_sent) / 1024 / 1024
        net_recv_mb = (net_io.bytes_recv - self.baseline_network.bytes_recv) / 1024 / 1024
        
        metrics = ResourceMetrics(
            timestamp=datetime.utcnow().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=mem.percent,
            memory_used_gb=mem.used / 1024 / 1024 / 1024,
            memory_available_gb=mem.available / 1024 / 1024 / 1024,
            disk_io_read_mb=disk_read_mb,
            disk_io_write_mb=disk_write_mb,
            network_sent_mb=net_sent_mb,
            network_recv_mb=net_recv_mb,
            active_workers=active_workers or self.current_workers,
            queue_depth=queue_depth
        )
        
        self.metrics_history.append(metrics)
        return metrics
    
    def analyze_trend(self, metric_name: str, window: int = 10) -> Tuple[float, str]:
        """
        Analyze trend for a specific metric
        Returns: (current_value, trend: "rising"|"falling"|"stable")
        """
        if len(self.metrics_history) < window:
            return 0.0, "insufficient_data"
        
        recent = list(self.metrics_history)[-window:]
        values = [getattr(m, metric_name) for m in recent]
        
        current = values[-1]
        avg_early = sum(values[:window//2]) / (window//2)
        avg_late = sum(values[window//2:]) / (window//2)
        
        change_percent = ((avg_late - avg_early) / avg_early * 100) if avg_early > 0 else 0
        
        if change_percent > 5:
            trend = "rising"
        elif change_percent < -5:
            trend = "falling"
        else:
            trend = "stable"
        
        return current, trend
    
    def make_scaling_decision(self) -> ThrottleDecision:
        """
        Conservative auto-scaling logic
        
        Priority:
        1. Emergency stop on critical thresholds
        2. Scale down on warning thresholds
        3. Maintain if unstable or trending poorly
        4. Scale up only if proven safe + stable
        """
        
        if len(self.metrics_history) < 5:
            return ThrottleDecision(
                action="maintain",
                current_workers=self.current_workers,
                recommended_workers=self.current_workers,
                reason="Insufficient metrics history (need warmup)",
                confidence=0.5,
                metrics_snapshot=self.metrics_history[-1] if self.metrics_history else None
            )
        
        # Get current metrics and trends
        current_metrics = self.metrics_history[-1]
        mem_value, mem_trend = self.analyze_trend("memory_percent")
        cpu_value, cpu_trend = self.analyze_trend("cpu_percent")
        
        # CRITICAL: Emergency stop
        if mem_value >= self.CRITICAL_MEMORY_PERCENT or cpu_value >= self.CRITICAL_CPU_PERCENT:
            logger.critical(f"EMERGENCY: Memory {mem_value:.1f}% or CPU {cpu_value:.1f}% critical!")
            return ThrottleDecision(
                action="emergency_stop",
                current_workers=self.current_workers,
                recommended_workers=self.MIN_WORKERS,
                reason=f"CRITICAL threshold exceeded (Mem: {mem_value:.1f}%, CPU: {cpu_value:.1f}%)",
                confidence=1.0,
                metrics_snapshot=current_metrics
            )
        
        # WARNING: Scale down
        if mem_value >= self.WARNING_MEMORY_PERCENT or cpu_value >= self.WARNING_CPU_PERCENT:
            new_workers = max(self.MIN_WORKERS, self.current_workers - 2)
            logger.warning(f"High resource usage. Scaling down: {self.current_workers} → {new_workers}")
            return ThrottleDecision(
                action="scale_down",
                current_workers=self.current_workers,
                recommended_workers=new_workers,
                reason=f"WARNING threshold (Mem: {mem_value:.1f}%, CPU: {cpu_value:.1f}%)",
                confidence=0.9,
                metrics_snapshot=current_metrics
            )
        
        # WARNING: Rising trends - preemptive scale down
        if mem_trend == "rising" and mem_value > 65.0:
            new_workers = max(self.MIN_WORKERS, self.current_workers - 1)
            logger.warning(f"Memory rising trend detected. Preemptive scale down: {self.current_workers} → {new_workers}")
            return ThrottleDecision(
                action="scale_down",
                current_workers=self.current_workers,
                recommended_workers=new_workers,
                reason=f"Rising memory trend at {mem_value:.1f}% (preemptive)",
                confidence=0.8,
                metrics_snapshot=current_metrics
            )
        
        # SAFE: Can consider scaling up
        if (mem_value < self.SAFE_MEMORY_PERCENT and 
            cpu_value < self.SAFE_CPU_PERCENT and
            mem_trend != "rising" and
            self.current_workers < self.MAX_WORKERS):
            
            # Only scale up if proven stable (10+ measurements with safe metrics)
            stable_count = sum(1 for m in list(self.metrics_history)[-10:] 
                             if m.memory_percent < self.SAFE_MEMORY_PERCENT 
                             and m.cpu_percent < self.SAFE_CPU_PERCENT)
            
            if stable_count >= 8:  # 80% stability required
                new_workers = min(self.MAX_WORKERS, self.current_workers + 1)
                logger.info(f"System stable. Scaling up: {self.current_workers} → {new_workers}")
                return ThrottleDecision(
                    action="scale_up",
                    current_workers=self.current_workers,
                    recommended_workers=new_workers,
                    reason=f"Safe metrics + proven stability (Mem: {mem_value:.1f}%, CPU: {cpu_value:.1f}%)",
                    confidence=0.7,
                    metrics_snapshot=current_metrics
                )
        
        # DEFAULT: Maintain current state
        return ThrottleDecision(
            action="maintain",
            current_workers=self.current_workers,
            recommended_workers=self.current_workers,
            reason=f"Stable operation (Mem: {mem_value:.1f}%, CPU: {cpu_value:.1f}%)",
            confidence=0.6,
            metrics_snapshot=current_metrics
        )
    
    def apply_decision(self, decision: ThrottleDecision) -> bool:
        """
        Apply scaling decision
        Returns: True if action was taken
        """
        self.decision_history.append(decision)
        
        # Log decision
        log_file = self.log_dir / f"scaling_decisions_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps({
                'timestamp': datetime.utcnow().isoformat(),
                'action': decision.action,
                'current_workers': decision.current_workers,
                'recommended_workers': decision.recommended_workers,
                'reason': decision.reason,
                'confidence': decision.confidence
            }) + '\n')
        
        if decision.action in ["scale_up", "scale_down", "emergency_stop"]:
            logger.info(f"DECISION: {decision.action} - {decision.reason}")
            self.current_workers = decision.recommended_workers
            return True
        
        return False
    
    def force_gc_cleanup(self):
        """Force garbage collection and resource cleanup"""
        logger.info("Forcing garbage collection...")
        collected = gc.collect()
        logger.info(f"GC collected {collected} objects")
    
    def export_metrics_report(self) -> str:
        """Export comprehensive metrics report"""
        if not self.metrics_history:
            return "No metrics collected yet"
        
        recent = list(self.metrics_history)[-10:]
        
        report = f"""
=== EQ12 RESOURCE MONITOR REPORT ===
Generated: {datetime.now().isoformat()}

[CURRENT STATE]
Workers: {self.current_workers}
CPU: {recent[-1].cpu_percent:.1f}%
Memory: {recent[-1].memory_percent:.1f}% ({recent[-1].memory_used_gb:.2f} GB used)
Available: {recent[-1].memory_available_gb:.2f} GB

[10-MEASUREMENT TRENDS]
Avg CPU: {sum(m.cpu_percent for m in recent) / len(recent):.1f}%
Avg Memory: {sum(m.memory_percent for m in recent) / len(recent):.1f}%
Peak Memory: {max(m.memory_percent for m in recent):.1f}%
Peak CPU: {max(m.cpu_percent for m in recent):.1f}%

[RECENT DECISIONS]
"""
        for decision in self.decision_history[-5:]:
            report += f"  {decision.action.upper()}: {decision.reason}\n"
        
        report += "\n" + "="*50
        
        # Save to file
        report_file = self.log_dir / f"monitor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"Report saved: {report_file}")
        return report
    
    def start_monitoring(self, interval: int = 30):
        """Start continuous background monitoring"""
        if self.is_monitoring:
            logger.warning("Monitoring already active")
            return
        
        self.is_monitoring = True
        
        def monitor_loop():
            logger.info(f"Starting monitor loop (interval: {interval}s)")
            while self.is_monitoring:
                try:
                    # Capture metrics
                    metrics = self.capture_metrics()
                    
                    # Make scaling decision
                    decision = self.make_scaling_decision()
                    
                    # Apply if needed
                    if decision.action != "maintain":
                        self.apply_decision(decision)
                    
                    # Periodic GC (every 5 minutes)
                    if len(self.metrics_history) % 10 == 0:
                        self.force_gc_cleanup()
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"Monitor loop error: {e}", exc_info=True)
                    time.sleep(interval)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Background monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Monitoring stopped")


# Convenience functions for integration
def create_monitor(log_dir: str = None) -> ResourceMonitor:
    """Factory function to create and start monitor"""
    monitor = ResourceMonitor(log_dir=log_dir)
    logger.info(f"Monitor created with {monitor.current_workers} initial workers")
    return monitor


def get_safe_worker_count() -> int:
    """Get conservative starting worker count"""
    return ResourceMonitor.SAFE_START_WORKERS


if __name__ == "__main__":
    # Demo usage
    print("EQ12 Resource Monitor - Demo Mode")
    print("="*60)
    
    monitor = create_monitor()
    
    print(f"\n[INITIAL STATE]")
    print(f"  Recommended workers: {monitor.current_workers}")
    print(f"  Min workers: {monitor.MIN_WORKERS}")
    print(f"  Max workers: {monitor.MAX_WORKERS}")
    
    print(f"\n[CAPTURING 5 SNAPSHOTS...]")
    for i in range(5):
        metrics = monitor.capture_metrics()
        print(f"  {i+1}. CPU: {metrics.cpu_percent:.1f}%, "
              f"Memory: {metrics.memory_percent:.1f}%, "
              f"Available: {metrics.memory_available_gb:.1f} GB")
        time.sleep(2)
    
    print(f"\n[MAKING SCALING DECISION...]")
    decision = monitor.make_scaling_decision()
    print(f"  Action: {decision.action}")
    print(f"  Workers: {decision.current_workers} → {decision.recommended_workers}")
    print(f"  Reason: {decision.reason}")
    print(f"  Confidence: {decision.confidence:.0%}")
    
    print(f"\n[GENERATING REPORT...]")
    report = monitor.export_metrics_report()
    print(report)
    
    print(f"\n✅ Demo complete. Check logs at: {monitor.log_dir}")
