import os
import sys
import psutil
import time
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("QuantumProfiler")

class QuantumMemoryProfiler:
    def __init__(self, interval=1.0):
        self.interval = interval
        self.process = psutil.Process(os.getpid())
        self.history = []

    def snapshot(self, label=""):
        """Captures a memory snapshot of the current process and system."""
        mem_info = self.process.memory_info()
        sys_mem = psutil.virtual_memory()
        
        snapshot = {
            "timestamp": datetime.utcnow().isoformat(),
            "label": label,
            "process_rss_mb": mem_info.rss / (1024 * 1024),
            "process_vms_mb": mem_info.vms / (1024 * 1024),
            "system_percent": sys_mem.percent,
            "system_available_mb": sys_mem.available / (1024 * 1024)
        }
        self.history.append(snapshot)
        logger.info(f"[{label}] RSS: {snapshot['process_rss_mb']:.2f} MB | Sys: {snapshot['system_percent']}%")
        return snapshot

    def save_report(self, filepath="logs/memory_profile.json"):
        """Saves the profile history to a JSON file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.history, f, indent=2)
        logger.info(f"Memory profile saved to {filepath}")

def profile_engine(engine_class, engine_name):
    """Runs a dummy cycle of an engine while profiling memory."""
    profiler = QuantumMemoryProfiler()
    logger.info(f"Starting Quantum Profile for: {engine_name}")
    
    profiler.snapshot("Pre-Init")
    
    try:
        # Import dynamically to avoid loading everything at once
        engine = engine_class()
        profiler.snapshot("Post-Init")
        
        if hasattr(engine, 'run'):
            logger.info(f"Running {engine_name}...")
            # Mock run if needed, or just call it if it's safe
            # For safety in this script, we just instantiate. 
            # In a real profile, we'd feed it mock data.
            pass
            
        profiler.snapshot("Post-Run")
        
        del engine
        import gc
        gc.collect()
        profiler.snapshot("Post-GC")
        
    except Exception as e:
        logger.error(f"Profiling failed for {engine_name}: {e}")

    profiler.save_report(f"logs/profile_{engine_name}.json")

if __name__ == "__main__":
    # Example usage: Profile the Parlay Engine
    try:
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        from src.intelligences.parlay_construction.engine import ParlayConstructionEngine
        profile_engine(ParlayConstructionEngine, "ParlayEngine")
    except ImportError:
        logger.error("Could not import engines. Run this from the repo root.")
