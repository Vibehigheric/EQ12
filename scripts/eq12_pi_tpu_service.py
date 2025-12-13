#!/usr/bin/env python3
"""
EQ12 Pi TPU Service API
Lightweight FastAPI service for remote TPU management on Raspberry Pi nodes

Provides endpoints for:
- TPU device discovery and status
- Model loading and management  
- Remote inference execution
- Performance monitoring

Usage:
    # Run on Pi: python eq12_pi_tpu_service.py --port 8080
    # From EQ12: curl http://192.168.100.2:8080/api/tpus
"""

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("WARNING: FastAPI not installed. Install with: pip install fastapi uvicorn")

try:
    from pycoral.utils.edgetpu import list_edge_tpus, make_interpreter
    from pycoral.utils import dataset
    from pycoral.adapters import common
    CORAL_AVAILABLE = True
except ImportError:
    CORAL_AVAILABLE = False
    print("WARNING: PyCoral not installed. Install with: pip install pycoral")

import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pydantic models for API
class ModelLoadRequest(BaseModel):
    model_name: str
    model_path: str

class InferenceRequest(BaseModel):
    model_name: str
    input_data: List[List[List[int]]]  # 3D array as nested lists
    task_id: str

class TPUStatus(BaseModel):
    device_path: str
    device_type: str
    is_available: bool
    current_model: Optional[str] = None
    total_inferences: int = 0
    avg_inference_time: float = 0.0

class TPUServiceManager:
    """Manages TPU devices and inference on Pi node"""
    
    def __init__(self):
        self.devices: Dict[str, Dict] = {}
        self.models: Dict[str, Any] = {}  # model_name -> interpreter
        self.stats = {
            "total_inferences": 0,
            "successful_inferences": 0,
            "failed_inferences": 0,
            "uptime_start": time.time()
        }
        
        # Discover local TPUs
        self.discover_tpus()
        
    def discover_tpus(self):
        """Discover available TPU devices"""
        if not CORAL_AVAILABLE:
            logger.error("PyCoral not available for TPU discovery")
            return
        
        try:
            tpus = list_edge_tpus()
            for i, tpu in enumerate(tpus):
                device_id = f"tpu_{i}"
                self.devices[device_id] = {
                    "path": tpu['path'],
                    "type": tpu.get('type', 'USB'),
                    "is_available": True,
                    "current_model": None,
                    "interpreter": None,
                    "total_inferences": 0,
                    "inference_times": [],
                    "last_used": time.time()
                }
                logger.info(f"Discovered TPU: {device_id} at {tpu['path']}")
                
        except Exception as e:
            logger.error(f"TPU discovery failed: {e}")
    
    def get_device_stats(self) -> List[TPUStatus]:
        """Get status of all TPU devices"""
        stats = []
        for device_id, device in self.devices.items():
            avg_time = 0.0
            if device["inference_times"]:
                avg_time = sum(device["inference_times"]) / len(device["inference_times"])
            
            stats.append(TPUStatus(
                device_path=device["path"],
                device_type=device["type"],
                is_available=device["is_available"],
                current_model=device["current_model"],
                total_inferences=device["total_inferences"],
                avg_inference_time=avg_time
            ))
        return stats
    
    def load_model(self, model_name: str, model_path: str) -> bool:
        """Load model onto available TPU"""
        if not CORAL_AVAILABLE:
            logger.error("PyCoral not available")
            return False
            
        # Find available device
        available_device = None
        for device_id, device in self.devices.items():
            if device["is_available"]:
                available_device = device
                break
        
        if not available_device:
            logger.error("No available TPU devices")
            return False
        
        try:
            # Check if model file exists (for remote paths, assume valid)
            if not model_path.startswith("http") and not Path(model_path).exists():
                logger.error(f"Model file not found: {model_path}")
                return False
            
            # Create interpreter
            interpreter = make_interpreter(model_path, available_device["path"])
            interpreter.allocate_tensors()
            
            # Store interpreter and update device
            self.models[model_name] = interpreter
            available_device["current_model"] = model_name
            available_device["interpreter"] = interpreter
            
            logger.info(f"Loaded model {model_name} on {available_device['path']}")
            return True
            
        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            return False
    
    def run_inference(self, model_name: str, input_data: np.ndarray, task_id: str) -> Optional[np.ndarray]:
        """Execute inference with loaded model"""
        if model_name not in self.models:
            logger.error(f"Model {model_name} not loaded")
            return None
        
        interpreter = self.models[model_name]
        start_time = time.time()
        
        try:
            # Get input/output details
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            
            # Prepare input data
            if input_data.dtype != input_details[0]['dtype']:
                input_data = input_data.astype(input_details[0]['dtype'])
            
            # Set input tensor
            interpreter.set_tensor(input_details[0]['index'], input_data)
            
            # Run inference
            interpreter.invoke()
            
            # Get output
            output_data = interpreter.get_tensor(output_details[0]['index'])
            
            # Update statistics
            inference_time = (time.time() - start_time) * 1000  # ms
            self.update_device_stats(model_name, inference_time)
            self.stats["successful_inferences"] += 1
            self.stats["total_inferences"] += 1
            
            logger.debug(f"Inference {task_id} completed in {inference_time:.2f}ms")
            return output_data.copy()
            
        except Exception as e:
            logger.error(f"Inference failed for {task_id}: {e}")
            self.stats["failed_inferences"] += 1
            self.stats["total_inferences"] += 1
            return None
    
    def update_device_stats(self, model_name: str, inference_time: float):
        """Update device performance statistics"""
        for device in self.devices.values():
            if device["current_model"] == model_name:
                device["total_inferences"] += 1
                device["inference_times"].append(inference_time)
                device["last_used"] = time.time()
                
                # Keep only last 100 inference times for averaging
                if len(device["inference_times"]) > 100:
                    device["inference_times"] = device["inference_times"][-100:]
                break

# Create FastAPI app
if FASTAPI_AVAILABLE:
    app = FastAPI(title="EQ12 Pi TPU Service", version="1.0.0")
    tpu_manager = TPUServiceManager()

    @app.get("/")
    async def root():
        return {"message": "EQ12 Pi TPU Service", "status": "online"}

    @app.get("/api/tpus")
    async def get_tpus():
        """Get list of available TPU devices"""
        try:
            devices = tpu_manager.get_device_stats()
            return {"devices": [device.dict() for device in devices]}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/load_model")
    async def load_model(request: ModelLoadRequest):
        """Load model onto TPU"""
        try:
            success = tpu_manager.load_model(request.model_name, request.model_path)
            if success:
                return {"status": "success", "message": f"Model {request.model_name} loaded"}
            else:
                raise HTTPException(status_code=400, detail="Model loading failed")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/inference")
    async def run_inference(request: InferenceRequest):
        """Execute inference on loaded model"""
        try:
            # Convert input data to numpy array
            input_array = np.array(request.input_data, dtype=np.uint8)
            
            # Run inference
            result = tpu_manager.run_inference(
                request.model_name, 
                input_array, 
                request.task_id
            )
            
            if result is not None:
                return {
                    "status": "success",
                    "task_id": request.task_id,
                    "output": result.tolist()
                }
            else:
                raise HTTPException(status_code=400, detail="Inference failed")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/stats")
    async def get_stats():
        """Get service statistics"""
        try:
            uptime = time.time() - tpu_manager.stats["uptime_start"]
            return {
                "stats": tpu_manager.stats,
                "uptime_seconds": uptime,
                "devices": len(tpu_manager.devices),
                "loaded_models": list(tpu_manager.models.keys())
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "devices_available": len([d for d in tpu_manager.devices.values() if d["is_available"]])
        }

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="EQ12 Pi TPU Service")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", default=8080, type=int, help="Port to bind to")
    parser.add_argument("--workers", default=1, type=int, help="Number of worker processes")
    parser.add_argument("--log-level", default="info", help="Log level")
    
    args = parser.parse_args()
    
    if not FASTAPI_AVAILABLE:
        print("ERROR: FastAPI not available. Install with: pip install fastapi uvicorn")
        return 1
    
    if not CORAL_AVAILABLE:
        print("WARNING: PyCoral not available. TPU functionality will be limited.")
    
    # Log startup info
    logger.info(f"Starting EQ12 Pi TPU Service on {args.host}:{args.port}")
    logger.info(f"Found {len(tpu_manager.devices)} TPU devices")
    
    # Start the service
    try:
        uvicorn.run(
            "eq12_pi_tpu_service:app",
            host=args.host,
            port=args.port,
            workers=args.workers,
            log_level=args.log_level,
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
    except Exception as e:
        logger.error(f"Service failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())