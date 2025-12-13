#!/usr/bin/env python3
"""
EQ12 TPU Optimization Assistant
AI-powered optimization engine for multi-TPU cluster performance

Intelligent features:
- Model placement optimization
- Dynamic batch sizing
- Predictive load balancing  
- Performance anomaly detection
- Auto-scaling recommendations

Usage:
    optimizer = EQ12TPUOptimizer()
    recommendations = await optimizer.analyze_and_optimize()
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import statistics
import math

try:
    import numpy as np
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("WARNING: ML libraries not available. Install with: pip install scikit-learn numpy")

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class OptimizationRecommendation:
    """Container for optimization recommendations"""
    priority: int  # 1=low, 5=critical
    category: str  # performance, thermal, load_balancing, model_placement
    device_id: Optional[str]
    recommendation: str
    expected_improvement: float  # percentage
    implementation_effort: str  # low, medium, high
    automated: bool = False


@dataclass
class ModelPerformanceProfile:
    """Performance profile for a specific model"""
    model_name: str
    avg_inference_time: float
    memory_usage: float
    tpu_utilization: float
    optimal_batch_size: int
    thermal_impact: float
    compatibility_score: float


class EQ12TPUOptimizer:
    """Advanced AI-powered TPU optimization engine"""
    
    def __init__(self, config_path: str = "C:/EQ12/configs/tpu_optimizer_config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.historical_data: List[Dict] = []
        self.model_profiles: Dict[str, ModelPerformanceProfile] = {}
        self.anomaly_detector = None
        self.scaler = None
        
        # Performance baselines
        self.baselines = {
            "inference_time": {"mobilenet_v2": 15.0, "efficientdet": 25.0},
            "throughput": {"mobilenet_v2": 66.0, "efficientdet": 40.0},
            "thermal_normal": 45.0,  # celsius
            "power_efficiency": 0.85  # TOPS/Watt target
        }
        
        self.optimization_history: List[OptimizationRecommendation] = []
        
        if ML_AVAILABLE:
            self.initialize_ml_models()
        
        logger.info("EQ12 TPU Optimizer initialized")

    def load_config(self) -> Dict[str, Any]:
        """Load optimizer configuration"""
        default_config = {
            "optimization_interval": 300,  # 5 minutes
            "ml_analysis_enabled": True,
            "anomaly_detection_threshold": 0.3,
            "auto_apply_optimizations": False,
            "performance_targets": {
                "max_inference_time": 50.0,
                "min_throughput": 20.0,
                "max_thermal_temp": 75.0,
                "min_cluster_efficiency": 0.8
            },
            "model_optimization": {
                "enable_batch_optimization": True,
                "enable_model_sharding": True,
                "enable_dynamic_placement": True,
                "cache_optimization": True
            },
            "balancer_api": "http://localhost:8090/api",
            "monitor_api": "http://localhost:8091/api"
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    default_config.update(config)
            except Exception as e:
                logger.warning(f"Error loading config: {e}, using defaults")
        else:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
        
        return default_config

    def initialize_ml_models(self):
        """Initialize machine learning models for optimization"""
        if not ML_AVAILABLE:
            return
        
        try:
            # Anomaly detection for performance issues
            self.anomaly_detector = IsolationForest(
                contamination=self.config["anomaly_detection_threshold"],
                random_state=42
            )
            
            # Feature scaler for normalization
            self.scaler = StandardScaler()
            
            logger.info("ML models initialized successfully")
        except Exception as e:
            logger.error(f"ML initialization failed: {e}")

    async def collect_performance_data(self) -> Dict[str, Any]:
        """Collect comprehensive performance data from cluster"""
        try:
            # Get data from monitor
            monitor_response = requests.get(
                f"{self.config['monitor_api']}/status",
                timeout=10
            )
            
            # Get data from balancer
            balancer_response = requests.get(
                f"{self.config['balancer_api']}/stats",
                timeout=10
            )
            
            performance_data = {
                "timestamp": time.time(),
                "monitor_data": monitor_response.json() if monitor_response.status_code == 200 else {},
                "balancer_data": balancer_response.json() if balancer_response.status_code == 200 else {},
                "system_metrics": await self.collect_system_metrics()
            }
            
            # Store in historical data
            self.historical_data.append(performance_data)
            
            # Keep only last 1000 data points
            if len(self.historical_data) > 1000:
                self.historical_data = self.historical_data[-1000:]
            
            return performance_data
            
        except Exception as e:
            logger.error(f"Error collecting performance data: {e}")
            return {}

    async def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level metrics"""
        system_metrics = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "usb_bandwidth": 0.0,
            "power_consumption": 0.0,
            "ambient_temperature": 25.0
        }
        
        try:
            # For Windows, use PowerShell to get system metrics
            import subprocess
            
            # CPU usage
            result = subprocess.run(
                ["powershell", "-Command", "Get-WmiObject win32_processor | Measure-Object -Property LoadPercentage -Average | Select-Object Average"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and "Average" in result.stdout:
                cpu_line = [line for line in result.stdout.split('\n') if line.strip().replace('-', '').isdigit()]
                if cpu_line:
                    system_metrics["cpu_usage"] = float(cpu_line[0].strip())
            
            # Memory usage
            result = subprocess.run(
                ["powershell", "-Command", "Get-WmiObject win32_operatingsystem | Select-Object @{Name='MemUsage';Expression={[math]::round((($_.TotalVisibleMemorySize - $_.FreePhysicalMemory)/$_.TotalVisibleMemorySize) * 100, 2)}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # Parse memory usage from output
                pass  # Simplified for now
            
        except Exception as e:
            logger.debug(f"System metrics collection error: {e}")
        
        return system_metrics

    def analyze_performance_patterns(self) -> List[OptimizationRecommendation]:
        """Analyze historical performance patterns for optimization opportunities"""
        recommendations = []
        
        if len(self.historical_data) < 10:
            return recommendations
        
        try:
            # Analyze inference time patterns
            inference_times = []
            throughputs = []
            thermal_states = []
            
            for data in self.historical_data[-50:]:  # Last 50 data points
                monitor_data = data.get("monitor_data", {})
                current_metrics = monitor_data.get("current_metrics", {})
                
                for device_id, metrics in current_metrics.items():
                    inference_times.append(metrics.get("inference_time", 0))
                    throughputs.append(metrics.get("throughput", 0))
                    thermal_states.append(metrics.get("thermal_state", "NORMAL"))
            
            if inference_times:
                # Performance degradation detection
                recent_avg = statistics.mean(inference_times[-10:])
                historical_avg = statistics.mean(inference_times[:-10]) if len(inference_times) > 10 else recent_avg
                
                if recent_avg > historical_avg * 1.2:  # 20% degradation
                    recommendations.append(OptimizationRecommendation(
                        priority=4,
                        category="performance",
                        device_id=None,
                        recommendation="Performance degradation detected. Consider thermal management or load redistribution.",
                        expected_improvement=15.0,
                        implementation_effort="medium"
                    ))
                
                # High variance detection
                if len(inference_times) > 5:
                    std_dev = statistics.stdev(inference_times)
                    mean_time = statistics.mean(inference_times)
                    
                    if std_dev > mean_time * 0.3:  # High variance
                        recommendations.append(OptimizationRecommendation(
                            priority=3,
                            category="load_balancing",
                            device_id=None,
                            recommendation="High inference time variance detected. Implement dynamic load balancing.",
                            expected_improvement=12.0,
                            implementation_effort="low",
                            automated=True
                        ))
            
            # Thermal analysis
            critical_thermal_count = thermal_states.count("CRITICAL")
            hot_thermal_count = thermal_states.count("HOT")
            
            if critical_thermal_count > 0:
                recommendations.append(OptimizationRecommendation(
                    priority=5,
                    category="thermal",
                    device_id=None,
                    recommendation="Critical thermal conditions detected. Implement aggressive cooling or load reduction.",
                    expected_improvement=25.0,
                    implementation_effort="high"
                ))
            elif hot_thermal_count > len(thermal_states) * 0.3:
                recommendations.append(OptimizationRecommendation(
                    priority=3,
                    category="thermal",
                    device_id=None,
                    recommendation="Frequent thermal throttling detected. Consider workload optimization.",
                    expected_improvement=18.0,
                    implementation_effort="medium"
                ))
            
        except Exception as e:
            logger.error(f"Pattern analysis error: {e}")
        
        return recommendations

    def detect_anomalies(self) -> List[OptimizationRecommendation]:
        """Use ML to detect performance anomalies"""
        recommendations = []
        
        if not ML_AVAILABLE or len(self.historical_data) < 20:
            return recommendations
        
        try:
            # Prepare features for anomaly detection
            features = []
            timestamps = []
            
            for data in self.historical_data:
                monitor_data = data.get("monitor_data", {})
                current_metrics = monitor_data.get("current_metrics", {})
                
                # Extract numeric features
                feature_row = []
                for device_id, metrics in current_metrics.items():
                    feature_row.extend([
                        metrics.get("inference_time", 0),
                        metrics.get("throughput", 0),
                        metrics.get("load_percentage", 0)
                    ])
                
                if feature_row:
                    features.append(feature_row)
                    timestamps.append(data["timestamp"])
            
            if len(features) < 20:
                return recommendations
            
            # Ensure consistent feature dimensions
            max_features = max(len(f) for f in features)
            features = [f + [0] * (max_features - len(f)) for f in features]
            
            features_array = np.array(features)
            
            # Scale features
            features_scaled = self.scaler.fit_transform(features_array)
            
            # Detect anomalies
            anomaly_scores = self.anomaly_detector.fit_predict(features_scaled)
            
            # Analyze recent anomalies
            recent_anomalies = sum(1 for score in anomaly_scores[-10:] if score == -1)
            
            if recent_anomalies > 2:
                recommendations.append(OptimizationRecommendation(
                    priority=4,
                    category="performance",
                    device_id=None,
                    recommendation="ML anomaly detection identified performance irregularities. Investigation recommended.",
                    expected_improvement=20.0,
                    implementation_effort="medium"
                ))
            
        except Exception as e:
            logger.error(f"Anomaly detection error: {e}")
        
        return recommendations

    def optimize_model_placement(self) -> List[OptimizationRecommendation]:
        """Optimize model placement across devices"""
        recommendations = []
        
        try:
            # Analyze current model distribution
            device_models = {}
            device_performance = {}
            
            if not self.historical_data:
                return recommendations
            
            latest_data = self.historical_data[-1]
            monitor_data = latest_data.get("monitor_data", {})
            current_metrics = monitor_data.get("current_metrics", {})
            
            for device_id, metrics in current_metrics.items():
                device_models[device_id] = metrics.get("model_name", "")
                device_performance[device_id] = {
                    "inference_time": metrics.get("inference_time", 0),
                    "load": metrics.get("load_percentage", 0),
                    "thermal": metrics.get("thermal_state", "NORMAL")
                }
            
            # Check for suboptimal placements
            overloaded_devices = [
                device_id for device_id, perf in device_performance.items()
                if perf["load"] > 80 or perf["thermal"] in ["HOT", "CRITICAL"]
            ]
            
            underloaded_devices = [
                device_id for device_id, perf in device_performance.items()
                if perf["load"] < 30 and perf["thermal"] == "NORMAL"
            ]
            
            if overloaded_devices and underloaded_devices:
                recommendations.append(OptimizationRecommendation(
                    priority=3,
                    category="model_placement",
                    device_id=None,
                    recommendation=f"Rebalance models from overloaded devices {overloaded_devices} to underloaded devices {underloaded_devices}",
                    expected_improvement=22.0,
                    implementation_effort="low",
                    automated=True
                ))
            
        except Exception as e:
            logger.error(f"Model placement optimization error: {e}")
        
        return recommendations

    def calculate_optimal_batch_sizes(self) -> Dict[str, int]:
        """Calculate optimal batch sizes for different models"""
        optimal_batches = {}
        
        try:
            # Analyze historical performance vs batch size
            for model_name in ["mobilenet_v2", "efficientdet", "betting_classifier"]:
                # Simplified heuristic based on model complexity
                if model_name == "mobilenet_v2":
                    optimal_batches[model_name] = 4  # Lightweight model
                elif model_name == "efficientdet":
                    optimal_batches[model_name] = 2  # Medium complexity
                else:
                    optimal_batches[model_name] = 1  # Conservative default
            
        except Exception as e:
            logger.error(f"Batch size optimization error: {e}")
        
        return optimal_batches

    async def apply_optimization(self, recommendation: OptimizationRecommendation) -> bool:
        """Apply an optimization recommendation if automated"""
        if not recommendation.automated or not self.config["auto_apply_optimizations"]:
            return False
        
        try:
            if recommendation.category == "load_balancing":
                # Trigger load rebalancing
                response = requests.post(
                    f"{self.config['balancer_api']}/rebalance",
                    json={"trigger": "optimization_engine"},
                    timeout=10
                )
                return response.status_code == 200
            
            elif recommendation.category == "model_placement":
                # Trigger model redistribution
                response = requests.post(
                    f"{self.config['balancer_api']}/redistribute_models",
                    json={"strategy": "load_based"},
                    timeout=15
                )
                return response.status_code == 200
            
            # Other optimizations would be implemented here
            
        except Exception as e:
            logger.error(f"Optimization application error: {e}")
        
        return False

    async def analyze_and_optimize(self) -> Dict[str, Any]:
        """Main optimization analysis and recommendation engine"""
        logger.info("Starting TPU optimization analysis...")
        
        # Collect current performance data
        performance_data = await self.collect_performance_data()
        
        if not performance_data:
            return {"error": "Failed to collect performance data"}
        
        # Generate recommendations from different analysis methods
        recommendations = []
        
        # Pattern-based analysis
        pattern_recommendations = self.analyze_performance_patterns()
        recommendations.extend(pattern_recommendations)
        
        # ML-based anomaly detection
        if self.config["ml_analysis_enabled"]:
            anomaly_recommendations = self.detect_anomalies()
            recommendations.extend(anomaly_recommendations)
        
        # Model placement optimization
        placement_recommendations = self.optimize_model_placement()
        recommendations.extend(placement_recommendations)
        
        # Sort recommendations by priority
        recommendations.sort(key=lambda x: x.priority, reverse=True)
        
        # Apply automated optimizations
        applied_optimizations = []
        for rec in recommendations:
            if rec.automated:
                success = await self.apply_optimization(rec)
                if success:
                    applied_optimizations.append(rec.recommendation)
        
        # Calculate optimization potential
        total_improvement = sum(rec.expected_improvement for rec in recommendations[:5])  # Top 5
        
        # Generate optimization report
        optimization_report = {
            "timestamp": time.time(),
            "analysis_summary": {
                "total_recommendations": len(recommendations),
                "high_priority_recommendations": len([r for r in recommendations if r.priority >= 4]),
                "automated_optimizations_applied": len(applied_optimizations),
                "estimated_improvement_potential": f"{total_improvement:.1f}%"
            },
            "recommendations": [
                {
                    "priority": rec.priority,
                    "category": rec.category,
                    "device_id": rec.device_id,
                    "recommendation": rec.recommendation,
                    "expected_improvement": rec.expected_improvement,
                    "implementation_effort": rec.implementation_effort,
                    "automated": rec.automated
                }
                for rec in recommendations[:10]  # Top 10 recommendations
            ],
            "applied_optimizations": applied_optimizations,
            "optimal_batch_sizes": self.calculate_optimal_batch_sizes(),
            "performance_baseline": self.baselines,
            "next_analysis": time.time() + self.config["optimization_interval"]
        }
        
        # Save optimization report
        self.save_optimization_report(optimization_report)
        
        logger.info(f"Optimization analysis complete. {len(recommendations)} recommendations generated.")
        
        return optimization_report

    def save_optimization_report(self, report: Dict[str, Any]):
        """Save optimization report to file"""
        reports_dir = Path("C:/EQ12/logs/optimization_reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_path = reports_dir / f"tpu_optimization_report_{timestamp}.json"
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Optimization report saved to {report_path}")

    async def continuous_optimization(self):
        """Run continuous optimization loop"""
        logger.info("Starting continuous TPU optimization...")
        
        while True:
            try:
                # Run optimization analysis
                report = await self.analyze_and_optimize()
                
                # Wait for next optimization cycle
                await asyncio.sleep(self.config["optimization_interval"])
                
            except KeyboardInterrupt:
                logger.info("Continuous optimization stopped by user")
                break
            except Exception as e:
                logger.error(f"Optimization loop error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error


# Example usage
async def main():
    """Example optimization usage"""
    optimizer = EQ12TPUOptimizer()
    
    # Run single optimization analysis
    report = await optimizer.analyze_and_optimize()
    
    print("\n=== TPU Optimization Report ===")
    print(f"Total Recommendations: {report['analysis_summary']['total_recommendations']}")
    print(f"High Priority: {report['analysis_summary']['high_priority_recommendations']}")
    print(f"Improvement Potential: {report['analysis_summary']['estimated_improvement_potential']}")
    
    print("\n=== Top Recommendations ===")
    for i, rec in enumerate(report["recommendations"][:5], 1):
        print(f"{i}. [{rec['priority']}/5] {rec['category'].upper()}: {rec['recommendation']}")
        print(f"   Expected improvement: {rec['expected_improvement']:.1f}%")
        print(f"   Implementation: {rec['implementation_effort']}")
        print()


if __name__ == "__main__":
    asyncio.run(main())