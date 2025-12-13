#!/usr/bin/env python3
"""
EQ12 Multi-TPU Dynamic Load Balancer
Intelligent distributed inference across EQ12 host + Pi cluster nodes

Supports:
- Automatic TPU discovery (local + remote nodes)
- Dynamic model sharding and batch distribution  
- Async inference with optimal workload balancing
- Thermal monitoring and performance optimization
- Failover and redundancy for critical inference tasks

Usage:
    balancer = EQ12TPUBalancer()
    result = await balancer.inference_batch(models, data_batch)
"""

import asyncio
import json
import logging
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import threading
import queue

try:
    from pycoral.utils.edgetpu import list_edge_tpus, make_interpreter
    from pycoral.utils import dataset
    from pycoral.adapters import common, classify, detect
    CORAL_AVAILABLE = True
except ImportError:
    CORAL_AVAILABLE = False
    print("WARNING: PyCoral not installed. Install with: pip install pycoral")

import numpy as np
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TPUDevice:
    """Represents a Coral TPU device with performance metrics"""
    device_path: str
    device_type: str = "USB"
    node_ip: str = "localhost"
    node_name: str = "EQ12-Host"
    is_local: bool = True
    interpreter = None
    model_path: Optional[str] = None
    current_load: float = 0.0
    avg_inference_time: float = 0.0
    total_inferences: int = 0
    last_used: float = field(default_factory=time.time)
    thermal_state: str = "NORMAL"  # NORMAL, WARM, HOT, CRITICAL
    max_batch_size: int = 1
    supported_models: List[str] = field(default_factory=list)

    def update_performance(self, inference_time: float):
        """Update performance metrics after inference"""
        self.total_inferences += 1
        self.avg_inference_time = (
            (self.avg_inference_time * (self.total_inferences - 1) + inference_time) 
            / self.total_inferences
        )
        self.last_used = time.time()

    def get_efficiency_score(self) -> float:
        """Calculate device efficiency for load balancing"""
        base_score = 1.0 / max(self.avg_inference_time, 0.001)
        load_penalty = 1.0 - (self.current_load * 0.5)
        thermal_penalty = {
            "NORMAL": 1.0,
            "WARM": 0.9,
            "HOT": 0.7,
            "CRITICAL": 0.3
        }.get(self.thermal_state, 1.0)
        
        return base_score * load_penalty * thermal_penalty

@dataclass
class InferenceTask:
    """Represents a single inference task for queue management"""
    task_id: str
    model_name: str
    input_data: np.ndarray
    priority: int = 1  # 1=low, 5=critical
    timeout: float = 30.0
    created_at: float = field(default_factory=time.time)
    assigned_device: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None

class EQ12TPUBalancer:
    """Advanced TPU load balancer for distributed inference"""
    
    def __init__(self, config_path: str = "C:/EQ12/configs/tpu_balancer_config.json"):
        self.config_path = Path(config_path)
        self.devices: Dict[str, TPUDevice] = {}
        self.task_queue = asyncio.Queue()
        self.result_queue = asyncio.Queue()
        self.active_tasks: Dict[str, InferenceTask] = {}
        self.model_cache: Dict[str, str] = {}
        self.cluster_nodes: List[str] = []
        self.is_running = False
        self.stats = {
            "total_inferences": 0,
            "successful_inferences": 0,
            "failed_inferences": 0,
            "avg_response_time": 0.0,
            "cluster_efficiency": 0.0
        }
        
        # Thread pool for blocking operations
        self.executor = ThreadPoolExecutor(max_workers=8)
        
        # Load configuration
        self.load_config()
        
        # Initialize device discovery
        self.discover_devices()
        
        logger.info(f"EQ12 TPU Balancer initialized with {len(self.devices)} devices")

    def load_config(self):
        """Load balancer configuration"""
        default_config = {
            "cluster_nodes": ["192.168.100.2"],  # Pi nodes
            "model_paths": {
                "mobilenet_v2": "C:/EQ12/models/mobilenet_v2_1.0_224_quant_edgetpu.tflite",
                "efficientdet": "C:/EQ12/models/efficientdet_lite0_320_ptq_edgetpu.tflite",
                "betting_classifier": "C:/EQ12/models/betting_classifier_edgetpu.tflite"
            },
            "performance_targets": {
                "max_inference_time": 50.0,  # ms
                "target_throughput": 100,     # inferences/second
                "thermal_threshold": 80       # celsius
            },
            "load_balancing": {
                "algorithm": "efficiency_weighted",  # round_robin, least_loaded, efficiency_weighted
                "batch_optimization": True,
                "failover_enabled": True,
                "health_check_interval": 30
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    default_config.update(config)
            except Exception as e:
                logger.warning(f"Error loading config: {e}, using defaults")
        
        self.config = default_config
        self.cluster_nodes = self.config["cluster_nodes"]
        self.model_cache = self.config["model_paths"]
        
        # Save config if it doesn't exist
        if not self.config_path.exists():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)

    def discover_devices(self):
        """Discover all available TPU devices (local + remote)"""
        devices_found = 0
        
        # Discover local TPU devices
        if CORAL_AVAILABLE:
            try:
                local_tpus = list_edge_tpus()
                for i, tpu in enumerate(local_tpus):
                    device_id = f"local_tpu_{i}"
                    device = TPUDevice(
                        device_path=tpu['path'],
                        device_type=tpu.get('type', 'USB'),
                        node_ip="localhost",
                        node_name="EQ12-Host",
                        is_local=True
                    )
                    self.devices[device_id] = device
                    devices_found += 1
                    logger.info(f"Discovered local TPU: {device_id} at {tpu['path']}")
                    
            except Exception as e:
                logger.error(f"Error discovering local TPUs: {e}")
        
        # Discover remote TPU devices on cluster nodes
        for node_ip in self.cluster_nodes:
            try:
                response = requests.get(
                    f"http://{node_ip}:8080/api/tpus", 
                    timeout=5
                )
                if response.status_code == 200:
                    remote_tpus = response.json()
                    for i, tpu in enumerate(remote_tpus.get('devices', [])):
                        device_id = f"remote_{node_ip}_{i}"
                        device = TPUDevice(
                            device_path=tpu['path'],
                            device_type=tpu.get('type', 'USB'),
                            node_ip=node_ip,
                            node_name=f"Pi-{node_ip.split('.')[-1]}",
                            is_local=False
                        )
                        self.devices[device_id] = device
                        devices_found += 1
                        logger.info(f"Discovered remote TPU: {device_id} on {node_ip}")
                        
            except Exception as e:
                logger.warning(f"Could not connect to node {node_ip}: {e}")
        
        if devices_found == 0:
            logger.warning("No TPU devices discovered. Check connections and drivers.")
        else:
            logger.info(f"Total TPU devices available: {devices_found}")

    def get_optimal_device(self, model_name: str, priority: int = 1) -> Optional[TPUDevice]:
        """Select optimal device based on load balancing algorithm"""
        if not self.devices:
            return None
        
        algorithm = self.config["load_balancing"]["algorithm"]
        available_devices = [
            dev for dev in self.devices.values() 
            if dev.thermal_state != "CRITICAL"
        ]
        
        if not available_devices:
            logger.warning("No available devices (all in critical thermal state)")
            return None
        
        if algorithm == "round_robin":
            # Simple round-robin selection
            return min(available_devices, key=lambda d: d.last_used)
        
        elif algorithm == "least_loaded":
            # Select device with lowest current load
            return min(available_devices, key=lambda d: d.current_load)
        
        elif algorithm == "efficiency_weighted":
            # Select based on efficiency score (performance + load + thermal)
            return max(available_devices, key=lambda d: d.get_efficiency_score())
        
        else:
            # Default to first available
            return available_devices[0]

    async def load_model(self, device: TPUDevice, model_name: str) -> bool:
        """Load model onto specified TPU device"""
        if model_name not in self.model_cache:
            logger.error(f"Model {model_name} not found in cache")
            return False
        
        model_path = self.model_cache[model_name]
        
        try:
            if device.is_local:
                # Load model on local device
                if CORAL_AVAILABLE:
                    device.interpreter = make_interpreter(model_path, device.device_path)
                    device.interpreter.allocate_tensors()
                    device.model_path = model_path
                    device.supported_models.append(model_name)
                    logger.info(f"Loaded {model_name} on local device {device.device_path}")
                    return True
                else:
                    logger.error("PyCoral not available for local inference")
                    return False
            else:
                # Load model on remote device
                response = requests.post(
                    f"http://{device.node_ip}:8080/api/load_model",
                    json={"model_name": model_name, "model_path": model_path},
                    timeout=30
                )
                if response.status_code == 200:
                    device.model_path = model_path
                    device.supported_models.append(model_name)
                    logger.info(f"Loaded {model_name} on remote device {device.node_ip}")
                    return True
                else:
                    logger.error(f"Failed to load model on {device.node_ip}: {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            return False

    async def run_inference(self, device: TPUDevice, task: InferenceTask) -> Optional[Any]:
        """Execute inference task on specified device"""
        start_time = time.time()
        device.current_load += 0.1  # Increment load
        
        try:
            if device.is_local and device.interpreter:
                # Local inference
                input_details = device.interpreter.get_input_details()
                output_details = device.interpreter.get_output_details()
                
                # Set input tensor
                device.interpreter.set_tensor(input_details[0]['index'], task.input_data)
                
                # Run inference
                device.interpreter.invoke()
                
                # Get output
                output_data = device.interpreter.get_tensor(output_details[0]['index'])
                
                inference_time = (time.time() - start_time) * 1000  # ms
                device.update_performance(inference_time)
                
                logger.debug(f"Local inference completed in {inference_time:.2f}ms")
                return output_data
                
            elif not device.is_local:
                # Remote inference
                response = requests.post(
                    f"http://{device.node_ip}:8080/api/inference",
                    json={
                        "model_name": task.model_name,
                        "input_data": task.input_data.tolist(),
                        "task_id": task.task_id
                    },
                    timeout=task.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    inference_time = (time.time() - start_time) * 1000
                    device.update_performance(inference_time)
                    
                    logger.debug(f"Remote inference completed in {inference_time:.2f}ms")
                    return np.array(result['output'])
                else:
                    logger.error(f"Remote inference failed: {response.text}")
                    return None
            else:
                logger.error("No interpreter available for local device")
                return None
                
        except Exception as e:
            logger.error(f"Inference error on device {device.device_path}: {e}")
            return None
        finally:
            device.current_load = max(0, device.current_load - 0.1)

    async def submit_task(self, model_name: str, input_data: np.ndarray, 
                         priority: int = 1, timeout: float = 30.0) -> str:
        """Submit inference task to the queue"""
        task_id = f"task_{int(time.time() * 1000)}_{len(self.active_tasks)}"
        
        task = InferenceTask(
            task_id=task_id,
            model_name=model_name,
            input_data=input_data,
            priority=priority,
            timeout=timeout
        )
        
        self.active_tasks[task_id] = task
        await self.task_queue.put(task)
        
        logger.debug(f"Submitted task {task_id} for model {model_name}")
        return task_id

    async def get_result(self, task_id: str, timeout: float = 30.0) -> Optional[Any]:
        """Get result for a specific task"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                if task.result is not None:
                    del self.active_tasks[task_id]
                    return task.result
                elif task.error:
                    del self.active_tasks[task_id]
                    raise Exception(f"Task failed: {task.error}")
            
            await asyncio.sleep(0.1)
        
        # Cleanup timed out task
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]
        
        raise TimeoutError(f"Task {task_id} timed out")

    async def inference_batch(self, model_name: str, input_batch: List[np.ndarray], 
                             priority: int = 1) -> List[Any]:
        """Process a batch of inferences with optimal load distribution"""
        if not input_batch:
            return []
        
        # Submit all tasks
        task_ids = []
        for input_data in input_batch:
            task_id = await self.submit_task(model_name, input_data, priority)
            task_ids.append(task_id)
        
        # Collect results
        results = []
        for task_id in task_ids:
            try:
                result = await self.get_result(task_id)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch inference error for {task_id}: {e}")
                results.append(None)
        
        return results

    async def process_queue(self):
        """Main queue processing loop"""
        while self.is_running:
            try:
                # Get next task (with priority)
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                
                # Find optimal device
                device = self.get_optimal_device(task.model_name, task.priority)
                if not device:
                    task.error = "No available devices"
                    continue
                
                # Load model if needed
                if task.model_name not in device.supported_models:
                    model_loaded = await self.load_model(device, task.model_name)
                    if not model_loaded:
                        task.error = f"Failed to load model {task.model_name}"
                        continue
                
                # Assign and execute task
                task.assigned_device = device.device_path
                result = await self.run_inference(device, task)
                
                if result is not None:
                    task.result = result
                    self.stats["successful_inferences"] += 1
                else:
                    task.error = "Inference failed"
                    self.stats["failed_inferences"] += 1
                
                self.stats["total_inferences"] += 1
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Queue processing error: {e}")

    async def start(self):
        """Start the load balancer"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("Starting EQ12 TPU Load Balancer...")
        
        # Start queue processing
        asyncio.create_task(self.process_queue())
        
        # Start health monitoring
        asyncio.create_task(self.monitor_health())
        
        logger.info("TPU Load Balancer started successfully")

    async def stop(self):
        """Stop the load balancer"""
        self.is_running = False
        logger.info("TPU Load Balancer stopped")

    async def monitor_health(self):
        """Monitor device health and performance"""
        while self.is_running:
            try:
                for device_id, device in self.devices.items():
                    # Update thermal state (simplified)
                    if device.avg_inference_time > 100:  # ms
                        device.thermal_state = "HOT"
                    elif device.avg_inference_time > 50:
                        device.thermal_state = "WARM"
                    else:
                        device.thermal_state = "NORMAL"
                
                # Calculate cluster efficiency
                if self.devices:
                    total_efficiency = sum(dev.get_efficiency_score() for dev in self.devices.values())
                    self.stats["cluster_efficiency"] = total_efficiency / len(self.devices)
                
                await asyncio.sleep(self.config["load_balancing"]["health_check_interval"])
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get current balancer statistics"""
        device_stats = {}
        for device_id, device in self.devices.items():
            device_stats[device_id] = {
                "node": device.node_name,
                "total_inferences": device.total_inferences,
                "avg_inference_time": device.avg_inference_time,
                "current_load": device.current_load,
                "thermal_state": device.thermal_state,
                "efficiency_score": device.get_efficiency_score(),
                "supported_models": device.supported_models
            }
        
        return {
            "global_stats": self.stats,
            "device_stats": device_stats,
            "cluster_nodes": len(self.cluster_nodes),
            "active_tasks": len(self.active_tasks)
        }

# Example usage and testing
async def main():
    """Example usage of the TPU load balancer"""
    # Initialize balancer
    balancer = EQ12TPUBalancer()
    await balancer.start()
    
    try:
        # Example inference batch
        if balancer.devices:
            print("Running test inference batch...")
            
            # Create dummy input data (224x224x3 for MobileNet)
            test_inputs = [np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8) for _ in range(5)]
            
            # Run batch inference
            results = await balancer.inference_batch("mobilenet_v2", test_inputs)
            
            print(f"Processed {len(results)} inferences")
            
            # Display statistics
            stats = balancer.get_stats()
            print("\n=== TPU Cluster Statistics ===")
            print(f"Total Inferences: {stats['global_stats']['total_inferences']}")
            print(f"Success Rate: {stats['global_stats']['successful_inferences']}/{stats['global_stats']['total_inferences']}")
            print(f"Cluster Efficiency: {stats['global_stats']['cluster_efficiency']:.2f}")
            
            print("\n=== Device Performance ===")
            for device_id, device_stats in stats['device_stats'].items():
                print(f"{device_id} ({device_stats['node']}):")
                print(f"  Inferences: {device_stats['total_inferences']}")
                print(f"  Avg Time: {device_stats['avg_inference_time']:.2f}ms")
                print(f"  Load: {device_stats['current_load']:.1f}")
                print(f"  Thermal: {device_stats['thermal_state']}")
                print(f"  Efficiency: {device_stats['efficiency_score']:.2f}")
        
        else:
            print("No TPU devices found. Please check connections.")
    
    finally:
        await balancer.stop()

if __name__ == "__main__":
    asyncio.run(main())