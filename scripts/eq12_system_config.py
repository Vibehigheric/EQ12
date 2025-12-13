"""
EQ12 System Configuration - Auto-tuned for Hardware
Generated: 2025-11-28
Based on: 12th Gen Intel i3-1220P (12 threads), 32GB RAM, 564GB free
"""

import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class SystemCapabilities:
    """Hardware-based performance tuning"""
    
    # CPU Configuration
    cpu_cores: int = 10
    cpu_threads: int = 12
    max_workers: int = 10  # cores - 2 for system stability
    
    # Memory Configuration
    total_ram_gb: float = 31.77
    ram_per_worker_gb: float = 3.18
    max_memory_mb: int = 28000  # Leave 4GB for OS
    
    # Disk Configuration
    disk_free_gb: float = 563.81
    cache_size_gb: int = 10  # Conservative cache limit
    log_rotation_gb: int = 5
    
    # Network Configuration
    network_speed: str = "100 Gbps"
    max_concurrent_requests: int = 50
    request_timeout: int = 30
    
    # Python Configuration
    python_version: str = "3.12.10"
    pip_version: str = "25.3"
    
    # Performance Tuning
    batch_size: int = 100
    chunk_size: int = 1000
    max_queue_size: int = 500
    
    # API Rate Limits (based on network capability)
    odds_api_calls_per_minute: int = 60
    odds_api_calls_per_hour: int = 500
    
    @classmethod
    def get_optimal_workers(cls, task_type: str) -> int:
        """Get optimal worker count for specific task types"""
        configs = {
            'cpu_intensive': cls.max_workers // 2,  # 5 workers
            'io_intensive': cls.max_workers,  # 10 workers
            'memory_intensive': min(4, cls.max_workers // 3),  # 4 workers
            'mixed': cls.max_workers - 2,  # 8 workers
            'light': cls.max_workers,  # 10 workers
        }
        return configs.get(task_type, cls.max_workers // 2)
    
    @classmethod
    def get_batch_config(cls, data_size: int) -> Dict[str, int]:
        """Calculate optimal batch configuration"""
        if data_size < 100:
            return {'batch_size': 10, 'workers': 2}
        elif data_size < 1000:
            return {'batch_size': 50, 'workers': 5}
        elif data_size < 10000:
            return {'batch_size': 100, 'workers': 10}
        else:
            return {'batch_size': 200, 'workers': 10}
    
    @classmethod
    def validate_memory_available(cls, required_gb: float) -> bool:
        """Check if enough memory is available for operation"""
        return required_gb < (cls.total_ram_gb * 0.8)  # Use max 80% RAM
    
    @classmethod
    def get_cache_config(cls) -> Dict[str, Any]:
        """Get optimal cache configuration"""
        return {
            'max_size_mb': cls.cache_size_gb * 1024,
            'ttl_seconds': 3600,  # 1 hour
            'cleanup_interval': 300,  # 5 minutes
            'compression': True,
        }
    
    @classmethod
    def export_env_vars(cls) -> Dict[str, str]:
        """Export as environment variables for external tools"""
        return {
            'EQ12_MAX_WORKERS': str(cls.max_workers),
            'EQ12_BATCH_SIZE': str(cls.batch_size),
            'EQ12_MAX_MEMORY_MB': str(cls.max_memory_mb),
            'EQ12_CACHE_SIZE_GB': str(cls.cache_size_gb),
            'EQ12_CPU_THREADS': str(cls.cpu_threads),
        }


# Task-Specific Configurations
SPORTS_SCANNER_CONFIG = {
    'workers': SystemCapabilities.get_optimal_workers('io_intensive'),  # 10
    'batch_size': 100,
    'timeout': 30,
    'max_retries': 3,
    'concurrent_apis': 10,
}

PARLAY_VALIDATOR_CONFIG = {
    'workers': SystemCapabilities.get_optimal_workers('cpu_intensive'),  # 5
    'batch_size': 50,
    'timeout': 10,
    'cache_enabled': True,
}

BANKROLL_MANAGER_CONFIG = {
    'workers': SystemCapabilities.get_optimal_workers('light'),  # 10
    'batch_size': 200,
    'db_pool_size': 5,
    'cache_enabled': True,
}

SYSTEM_SCAN_CONFIG = {
    'workers': SystemCapabilities.get_optimal_workers('mixed'),  # 8
    'max_files': 50000,  # Increased from 5000 based on RAM
    'batch_size': 1000,
    'timeout': 300,
}

DATA_EXPORT_CONFIG = {
    'workers': SystemCapabilities.get_optimal_workers('io_intensive'),  # 10
    'chunk_size': 10000,
    'compression': 'gzip',
    'buffer_size_mb': 512,
}


def print_config_summary():
    """Display optimized configuration summary"""
    print("\n" + "="*80)
    print("EQ12 OPTIMIZED CONFIGURATION")
    print("="*80)
    
    print("\n[HARDWARE PROFILE]")
    print(f"  CPU: {SystemCapabilities.cpu_threads} threads (using {SystemCapabilities.max_workers})")
    print(f"  RAM: {SystemCapabilities.total_ram_gb:.1f} GB ({SystemCapabilities.ram_per_worker_gb:.1f} GB/worker)")
    print(f"  Disk: {SystemCapabilities.disk_free_gb:.1f} GB free")
    
    print("\n[TASK CONFIGURATIONS]")
    print(f"  Sports Scanner: {SPORTS_SCANNER_CONFIG['workers']} workers, batch {SPORTS_SCANNER_CONFIG['batch_size']}")
    print(f"  Parlay Validator: {PARLAY_VALIDATOR_CONFIG['workers']} workers, batch {PARLAY_VALIDATOR_CONFIG['batch_size']}")
    print(f"  Bankroll Manager: {BANKROLL_MANAGER_CONFIG['workers']} workers, batch {BANKROLL_MANAGER_CONFIG['batch_size']}")
    print(f"  System Scan: {SYSTEM_SCAN_CONFIG['workers']} workers, max {SYSTEM_SCAN_CONFIG['max_files']:,} files")
    
    print("\n[PERFORMANCE LIMITS]")
    print(f"  Max Workers: {SystemCapabilities.max_workers}")
    print(f"  Max Memory: {SystemCapabilities.max_memory_mb:,} MB")
    print(f"  Cache Size: {SystemCapabilities.cache_size_gb} GB")
    print(f"  API Rate: {SystemCapabilities.odds_api_calls_per_minute}/min")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    print_config_summary()
    
    # Export environment variables
    env_vars = SystemCapabilities.export_env_vars()
    print("\n[ENVIRONMENT VARIABLES]")
    for key, value in env_vars.items():
        print(f"  {key}={value}")
