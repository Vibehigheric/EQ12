"""
EQ12 Memory Safety Utilities (Chromium-inspired)
Resource management and memory safety patterns
"""

import contextlib
import gc
import psutil
import threading
import weakref
from typing import Any, Callable, Optional, Dict, List

class EQ12ResourceManager:
    """Chromium-inspired resource management for EQ12"""
    
    def __init__(self):
        self._resources: Dict[str, Any] = {}
        self._weak_refs: List[weakref.ref] = []
        self._lock = threading.RLock()
    
    @contextlib.contextmanager
    def managed_resource(self, resource_name: str, resource: Any):
        """Context manager for automatic resource cleanup"""
        try:
            with self._lock:
                self._resources[resource_name] = resource
            yield resource
        finally:
            with self._lock:
                if resource_name in self._resources:
                    # Cleanup resource if it has a close method
                    if hasattr(resource, 'close'):
                        resource.close()
                    elif hasattr(resource, '__exit__'):
                        resource.__exit__(None, None, None)
                    del self._resources[resource_name]
    
    def add_weak_reference(self, obj: Any, callback: Optional[Callable] = None):
        """Add weak reference to prevent circular references"""
        weak_ref = weakref.ref(obj, callback)
        self._weak_refs.append(weak_ref)
        return weak_ref
    
    def cleanup_dead_references(self):
        """Clean up dead weak references"""
        self._weak_refs = [ref for ref in self._weak_refs if ref() is not None]
    
    def force_garbage_collection(self):
        """Force garbage collection (use sparingly)"""
        self.cleanup_dead_references()
        gc.collect()
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024, 
            "percent": process.memory_percent(),
            "available_mb": psutil.virtual_memory().available / 1024 / 1024
        }

# Global resource manager instance
resource_manager = EQ12ResourceManager()

# Decorators for automatic resource management
def auto_cleanup(func: Callable) -> Callable:
    """Decorator to ensure resource cleanup after function execution"""
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            resource_manager.cleanup_dead_references()
    return wrapper

def memory_monitor(threshold_mb: float = 500.0):
    """Decorator to monitor memory usage and warn if threshold exceeded"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            memory_before = resource_manager.get_memory_usage()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                memory_after = resource_manager.get_memory_usage()
                memory_used = memory_after["rss_mb"] - memory_before["rss_mb"]
                if memory_used > threshold_mb:
                    print(f" Memory usage warning: {func.__name__} used {memory_used:.2f} MB")
        return wrapper
    return decorator
