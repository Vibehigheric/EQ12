#!/usr/bin/env python3
"""
EQ12 TPU Performance Monitor
Real-time monitoring and optimization for multi-TPU distributed inference

Features:
- Live performance dashboard
- Thermal monitoring and throttling
- Load balancing optimization
- Model performance profiling
- Cluster health alerts

Usage:
    monitor = EQ12TPUMonitor()
    await monitor.start_monitoring()
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading
from collections import deque
import statistics

try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import tkinter as tk
    from tkinter import ttk
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    print("WARNING: Plotting libraries not available. Install with: pip install matplotlib")

import requests
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Container for device performance metrics"""
    timestamp: float
    device_id: str
    inference_time: float
    throughput: float
    error_rate: float
    thermal_state: str
    load_percentage: float
    model_name: str = ""


@dataclass
class ClusterHealth:
    """Overall cluster health status"""
    total_devices: int
    active_devices: int
    avg_inference_time: float
    total_throughput: float
    error_rate: float
    cluster_efficiency: float
    critical_devices: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class EQ12TPUMonitor:
    """Advanced TPU cluster monitoring and optimization"""
    
    def __init__(self, config_path: str = "C:/EQ12/configs/tpu_monitor_config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.metrics_history: Dict[str, deque] = {}
        self.current_metrics: Dict[str, PerformanceMetrics] = {}
        self.cluster_health = ClusterHealth(0, 0, 0.0, 0.0, 0.0, 0.0)
        self.is_monitoring = False
        self.alert_conditions: Dict[str, Any] = {}
        
        # Performance thresholds
        self.thresholds = {
            "max_inference_time": 100.0,  # ms
            "min_throughput": 10.0,       # inferences/second
            "max_error_rate": 0.05,       # 5%
            "max_thermal_temp": 80.0,     # celsius
            "min_efficiency": 0.7         # 70%
        }
        
        # GUI components (if available)
        self.gui_root = None
        self.gui_canvas = None
        self.gui_figures = {}
        
        logger.info("EQ12 TPU Monitor initialized")

    def load_config(self) -> Dict[str, Any]:
        """Load monitoring configuration"""
        default_config = {
            "monitoring_interval": 5.0,  # seconds
            "history_length": 100,       # data points to keep
            "cluster_nodes": ["localhost", "192.168.100.2"],
            "balancer_api": "http://localhost:8090/api",
            "alerts": {
                "email_enabled": False,
                "slack_webhook": "",
                "alert_cooldown": 300  # seconds
            },
            "auto_optimization": {
                "enabled": True,
                "thermal_throttling": True,
                "load_rebalancing": True,
                "model_caching": True
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    default_config.update(config)
            except Exception as e:
                logger.warning(f"Error loading config: {e}, using defaults")
        else:
            # Save default config
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
        
        return default_config

    async def collect_device_metrics(self, device_id: str, node_ip: str) -> Optional[PerformanceMetrics]:
        """Collect metrics from a specific device"""
        try:
            if node_ip == "localhost":
                # Local device metrics via load balancer API
                response = requests.get(
                    f"{self.config['balancer_api']}/device/{device_id}/stats",
                    timeout=5
                )
            else:
                # Remote device metrics via Pi service
                response = requests.get(
                    f"http://{node_ip}:8080/api/stats",
                    timeout=5
                )
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract relevant metrics (simplified example)
                device_stats = data.get('device_stats', {}).get(device_id, {})
                
                metrics = PerformanceMetrics(
                    timestamp=time.time(),
                    device_id=device_id,
                    inference_time=device_stats.get('avg_inference_time', 0.0),
                    throughput=1000.0 / max(device_stats.get('avg_inference_time', 1.0), 1.0),
                    error_rate=0.0,  # Calculate from success/failure ratio
                    thermal_state=device_stats.get('thermal_state', 'UNKNOWN'),
                    load_percentage=device_stats.get('current_load', 0.0) * 100,
                    model_name=device_stats.get('current_model', '')
                )
                
                return metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics from {device_id} on {node_ip}: {e}")
        
        return None

    async def collect_cluster_metrics(self):
        """Collect metrics from all devices in the cluster"""
        tasks = []
        
        # Collect from local devices
        for i in range(2):  # Assume 2 local TPUs on EQ12
            device_id = f"local_tpu_{i}"
            tasks.append(self.collect_device_metrics(device_id, "localhost"))
        
        # Collect from remote nodes
        for node_ip in self.config["cluster_nodes"]:
            if node_ip != "localhost":
                device_id = f"remote_{node_ip}_0"
                tasks.append(self.collect_device_metrics(device_id, node_ip))
        
        # Gather all metrics
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Update metrics history
        current_time = time.time()
        active_devices = 0
        total_inference_time = 0.0
        total_throughput = 0.0
        total_errors = 0
        total_inferences = 0
        critical_devices = []
        
        for result in results:
            if isinstance(result, PerformanceMetrics):
                device_id = result.device_id
                
                # Initialize history if needed
                if device_id not in self.metrics_history:
                    self.metrics_history[device_id] = deque(maxlen=self.config["history_length"])
                
                # Add to history
                self.metrics_history[device_id].append(result)
                self.current_metrics[device_id] = result
                
                # Aggregate for cluster health
                active_devices += 1
                total_inference_time += result.inference_time
                total_throughput += result.throughput
                
                # Check for critical conditions
                if (result.inference_time > self.thresholds["max_inference_time"] or
                    result.thermal_state == "CRITICAL"):
                    critical_devices.append(device_id)
        
        # Update cluster health
        if active_devices > 0:
            self.cluster_health = ClusterHealth(
                total_devices=len(tasks),
                active_devices=active_devices,
                avg_inference_time=total_inference_time / active_devices,
                total_throughput=total_throughput,
                error_rate=total_errors / max(total_inferences, 1),
                cluster_efficiency=min(total_throughput / (active_devices * 100.0), 1.0),
                critical_devices=critical_devices
            )

    def analyze_performance_trends(self, device_id: str) -> Dict[str, Any]:
        """Analyze performance trends for optimization"""
        if device_id not in self.metrics_history or len(self.metrics_history[device_id]) < 10:
            return {"status": "insufficient_data"}
        
        history = list(self.metrics_history[device_id])
        
        # Calculate trends
        inference_times = [m.inference_time for m in history[-20:]]
        throughputs = [m.throughput for m in history[-20:]]
        loads = [m.load_percentage for m in history[-20:]]
        
        analysis = {
            "device_id": device_id,
            "trend_analysis": {
                "inference_time_trend": self.calculate_trend(inference_times),
                "throughput_trend": self.calculate_trend(throughputs),
                "load_trend": self.calculate_trend(loads)
            },
            "performance_stats": {
                "avg_inference_time": statistics.mean(inference_times),
                "max_inference_time": max(inference_times),
                "min_inference_time": min(inference_times),
                "std_dev": statistics.stdev(inference_times) if len(inference_times) > 1 else 0.0,
                "avg_throughput": statistics.mean(throughputs),
                "avg_load": statistics.mean(loads)
            },
            "recommendations": []
        }
        
        # Generate recommendations
        if analysis["trend_analysis"]["inference_time_trend"] > 0.1:
            analysis["recommendations"].append("Performance degrading - consider thermal throttling")
        
        if analysis["performance_stats"]["avg_load"] > 80:
            analysis["recommendations"].append("High load detected - consider load balancing")
        
        if analysis["performance_stats"]["std_dev"] > 20:
            analysis["recommendations"].append("High variance - check for interference")
        
        return analysis

    def calculate_trend(self, values: List[float]) -> float:
        """Calculate simple linear trend (-1 to 1)"""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x = list(range(n))
        
        # Simple linear regression slope
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        # Normalize to -1 to 1 range
        max_val = max(values)
        min_val = min(values)
        range_val = max_val - min_val
        
        if range_val == 0:
            return 0.0
        
        return min(max(slope / range_val, -1.0), 1.0)

    async def optimize_cluster(self):
        """Automatic cluster optimization based on current metrics"""
        if not self.config["auto_optimization"]["enabled"]:
            return
        
        optimizations_applied = []
        
        try:
            # Thermal throttling
            if self.config["auto_optimization"]["thermal_throttling"]:
                for device_id, metrics in self.current_metrics.items():
                    if metrics.thermal_state in ["HOT", "CRITICAL"]:
                        # Request throttling via balancer API
                        requests.post(
                            f"{self.config['balancer_api']}/device/{device_id}/throttle",
                            json={"action": "reduce_load", "factor": 0.7},
                            timeout=5
                        )
                        optimizations_applied.append(f"Thermal throttling applied to {device_id}")
            
            # Load rebalancing
            if self.config["auto_optimization"]["load_rebalancing"]:
                overloaded_devices = [
                    device_id for device_id, metrics in self.current_metrics.items()
                    if metrics.load_percentage > 85
                ]
                
                if overloaded_devices:
                    # Request load rebalancing
                    requests.post(
                        f"{self.config['balancer_api']}/rebalance",
                        json={"overloaded_devices": overloaded_devices},
                        timeout=10
                    )
                    optimizations_applied.append("Load rebalancing triggered")
            
            if optimizations_applied:
                logger.info(f"Applied optimizations: {optimizations_applied}")
        
        except Exception as e:
            logger.error(f"Optimization error: {e}")

    def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive cluster health report"""
        report = {
            "timestamp": time.time(),
            "cluster_overview": {
                "total_devices": self.cluster_health.total_devices,
                "active_devices": self.cluster_health.active_devices,
                "availability": self.cluster_health.active_devices / max(self.cluster_health.total_devices, 1),
                "avg_inference_time": self.cluster_health.avg_inference_time,
                "total_throughput": self.cluster_health.total_throughput,
                "cluster_efficiency": self.cluster_health.cluster_efficiency
            },
            "device_details": {},
            "alerts": [],
            "recommendations": []
        }
        
        # Device-specific analysis
        for device_id in self.current_metrics:
            analysis = self.analyze_performance_trends(device_id)
            report["device_details"][device_id] = analysis
        
        # Generate alerts
        for device_id in self.cluster_health.critical_devices:
            report["alerts"].append({
                "severity": "CRITICAL",
                "device": device_id,
                "message": "Device in critical state"
            })
        
        if self.cluster_health.avg_inference_time > self.thresholds["max_inference_time"]:
            report["alerts"].append({
                "severity": "WARNING",
                "message": f"Cluster average inference time ({self.cluster_health.avg_inference_time:.1f}ms) exceeds threshold"
            })
        
        # Generate recommendations
        if self.cluster_health.cluster_efficiency < self.thresholds["min_efficiency"]:
            report["recommendations"].append("Consider load balancing optimization")
        
        if len(self.cluster_health.critical_devices) > 0:
            report["recommendations"].append("Review thermal management for critical devices")
        
        return report

    def save_report(self, report: Dict[str, Any]):
        """Save health report to file"""
        reports_dir = Path("C:/EQ12/logs/tpu_reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_path = reports_dir / f"tpu_health_report_{timestamp}.json"
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Health report saved to {report_path}")

    async def monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Collect metrics
                await self.collect_cluster_metrics()
                
                # Apply optimizations
                await self.optimize_cluster()
                
                # Generate and save periodic reports
                if time.time() % 300 < self.config["monitoring_interval"]:  # Every 5 minutes
                    report = self.generate_health_report()
                    self.save_report(report)
                
                # Wait for next interval
                await asyncio.sleep(self.config["monitoring_interval"])
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(self.config["monitoring_interval"])

    async def start_monitoring(self):
        """Start the monitoring service"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        logger.info("Starting TPU cluster monitoring...")
        
        # Start monitoring loop
        await self.monitoring_loop()

    def stop_monitoring(self):
        """Stop the monitoring service"""
        self.is_monitoring = False
        logger.info("TPU monitoring stopped")

    def get_current_status(self) -> Dict[str, Any]:
        """Get current cluster status"""
        return {
            "cluster_health": {
                "total_devices": self.cluster_health.total_devices,
                "active_devices": self.cluster_health.active_devices,
                "avg_inference_time": self.cluster_health.avg_inference_time,
                "total_throughput": self.cluster_health.total_throughput,
                "cluster_efficiency": self.cluster_health.cluster_efficiency,
                "critical_devices": self.cluster_health.critical_devices
            },
            "current_metrics": {
                device_id: {
                    "inference_time": metrics.inference_time,
                    "throughput": metrics.throughput,
                    "load_percentage": metrics.load_percentage,
                    "thermal_state": metrics.thermal_state
                }
                for device_id, metrics in self.current_metrics.items()
            },
            "thresholds": self.thresholds
        }


# Example usage
async def main():
    """Example monitoring usage"""
    monitor = EQ12TPUMonitor()
    
    try:
        # Start monitoring (this will run indefinitely)
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
    finally:
        monitor.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(main())