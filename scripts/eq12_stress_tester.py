"""
EQ12 Stress Testing Framework
Simulate peak loads to identify bottlenecks, memory leaks, and resource limits

Tests:
1. Sustained high-throughput (hours/days)
2. Spike loads (sudden bursts)
3. Memory leak detection
4. Resource exhaustion scenarios
5. Concurrent task interference
"""

import time
import psutil
import multiprocessing as mp
from multiprocessing import Pool, Queue, Manager
import random
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Callable
import gc
import tracemalloc

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(processName)s] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StressTest:
    """Base class for stress tests"""
    
    def __init__(self, name: str, log_dir: str = None):
        self.name = name
        self.log_dir = Path(log_dir or "C:/EQ12_BROKEN_20251122_210342/logs/stress_tests")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
        
    def log_result(self, result: Dict):
        """Log test result"""
        result['timestamp'] = datetime.utcnow().isoformat()
        result['test_name'] = self.name
        self.results.append(result)
        
        # Write to JSONL
        log_file = self.log_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(result) + '\n')
    
    def get_memory_snapshot(self) -> Dict:
        """Get current memory usage snapshot"""
        mem = psutil.virtual_memory()
        process = psutil.Process()
        
        return {
            'system_memory_percent': mem.percent,
            'system_memory_used_gb': mem.used / 1024 / 1024 / 1024,
            'system_memory_available_gb': mem.available / 1024 / 1024 / 1024,
            'process_memory_mb': process.memory_info().rss / 1024 / 1024,
            'process_cpu_percent': process.cpu_percent()
        }
    
    def run(self):
        """Override in subclasses"""
        raise NotImplementedError


# Simulated workloads
def cpu_intensive_task(task_id: int, duration: float = 0.1) -> Dict:
    """Simulate CPU-heavy computation"""
    start = time.time()
    
    # Simulate computation (factorization)
    n = random.randint(10000, 50000)
    factors = []
    for i in range(2, int(n**0.5) + 1):
        while n % i == 0:
            factors.append(i)
            n //= i
    if n > 1:
        factors.append(n)
    
    elapsed = time.time() - start
    return {
        'task_id': task_id,
        'type': 'cpu_intensive',
        'duration': elapsed,
        'result_size': len(factors)
    }


def io_intensive_task(task_id: int, size_mb: float = 1.0) -> Dict:
    """Simulate I/O-heavy operation"""
    start = time.time()
    
    # Simulate file I/O
    temp_file = Path(f"C:/EQ12_BROKEN_20251122_210342/logs/temp_stress_{task_id}.tmp")
    data = b'X' * int(size_mb * 1024 * 1024)
    
    temp_file.write_bytes(data)
    read_data = temp_file.read_bytes()
    temp_file.unlink()
    
    elapsed = time.time() - start
    return {
        'task_id': task_id,
        'type': 'io_intensive',
        'duration': elapsed,
        'bytes_written': len(data),
        'bytes_read': len(read_data)
    }


def memory_leak_task(task_id: int, leak_mb: float = 10.0) -> Dict:
    """Simulate task that leaks memory"""
    start = time.time()
    
    # Allocate memory that won't be freed
    leaked_data = [random.random() for _ in range(int(leak_mb * 1024 * 128))]  # ~1MB per 128k floats
    
    # Simulate some work
    result = sum(leaked_data[:1000])
    
    elapsed = time.time() - start
    return {
        'task_id': task_id,
        'type': 'memory_leak',
        'duration': elapsed,
        'leaked_mb': leak_mb,
        'checksum': result
    }


def mixed_task(task_id: int) -> Dict:
    """Simulate realistic mixed workload"""
    start = time.time()
    
    # Mix of CPU, I/O, and memory
    # 1. CPU work
    x = sum([i**2 for i in range(10000)])
    
    # 2. Memory allocation
    data = [random.random() for _ in range(100000)]
    
    # 3. Simulated API call delay
    time.sleep(random.uniform(0.01, 0.05))
    
    # 4. Data processing
    result = sum(data) / len(data)
    
    elapsed = time.time() - start
    return {
        'task_id': task_id,
        'type': 'mixed',
        'duration': elapsed,
        'result': result
    }


class SustainedLoadTest(StressTest):
    """Test sustained high-throughput over extended period"""
    
    def __init__(self, duration_minutes: int = 60, workers: int = 6, tasks_per_sec: int = 10):
        super().__init__(f"sustained_load_{workers}w_{tasks_per_sec}tps")
        self.duration_minutes = duration_minutes
        self.workers = workers
        self.tasks_per_sec = tasks_per_sec
        
    def run(self):
        logger.info(f"Starting sustained load test: {self.duration_minutes}min, "
                   f"{self.workers} workers, {self.tasks_per_sec} tasks/sec")
        
        start_time = time.time()
        end_time = start_time + (self.duration_minutes * 60)
        task_count = 0
        
        tracemalloc.start()
        initial_memory = self.get_memory_snapshot()
        
        with Pool(processes=self.workers) as pool:
            while time.time() < end_time:
                batch_start = time.time()
                
                # Submit batch of tasks
                batch_size = self.tasks_per_sec
                tasks = [pool.apply_async(mixed_task, (task_count + i,)) 
                        for i in range(batch_size)]
                
                # Wait for completion
                results = [t.get() for t in tasks]
                task_count += len(results)
                
                # Log every minute
                elapsed_minutes = (time.time() - start_time) / 60
                if int(elapsed_minutes) > int((batch_start - start_time) / 60):
                    current_memory = self.get_memory_snapshot()
                    memory_growth = (current_memory['process_memory_mb'] - 
                                   initial_memory['process_memory_mb'])
                    
                    logger.info(f"[{int(elapsed_minutes)}min] Tasks: {task_count}, "
                              f"Memory: {current_memory['process_memory_mb']:.1f} MB "
                              f"(+{memory_growth:.1f} MB), "
                              f"CPU: {current_memory['process_cpu_percent']:.1f}%")
                    
                    self.log_result({
                        'elapsed_minutes': elapsed_minutes,
                        'tasks_completed': task_count,
                        **current_memory,
                        'memory_growth_mb': memory_growth
                    })
                
                # Rate limiting
                batch_duration = time.time() - batch_start
                sleep_time = max(0, 1.0 - batch_duration)
                time.sleep(sleep_time)
        
        final_memory = self.get_memory_snapshot()
        total_growth = final_memory['process_memory_mb'] - initial_memory['process_memory_mb']
        
        tracemalloc.stop()
        
        logger.info(f"✅ Sustained load test complete: {task_count} tasks in {self.duration_minutes}min")
        logger.info(f"   Memory growth: {total_growth:.1f} MB")
        logger.info(f"   Final memory: {final_memory['process_memory_mb']:.1f} MB")
        
        return {
            'total_tasks': task_count,
            'duration_minutes': self.duration_minutes,
            'memory_growth_mb': total_growth,
            'final_memory': final_memory
        }


class SpikeLoadTest(StressTest):
    """Test sudden burst loads"""
    
    def __init__(self, spike_workers: int = 10, spike_tasks: int = 1000, num_spikes: int = 5):
        super().__init__(f"spike_load_{spike_workers}w_{spike_tasks}t")
        self.spike_workers = spike_workers
        self.spike_tasks = spike_tasks
        self.num_spikes = num_spikes
        
    def run(self):
        logger.info(f"Starting spike load test: {self.num_spikes} spikes, "
                   f"{self.spike_workers} workers, {self.spike_tasks} tasks per spike")
        
        for spike_num in range(self.num_spikes):
            logger.info(f"[Spike {spike_num + 1}/{self.num_spikes}] Starting burst...")
            
            pre_memory = self.get_memory_snapshot()
            spike_start = time.time()
            
            with Pool(processes=self.spike_workers) as pool:
                results = pool.map(mixed_task, range(self.spike_tasks))
            
            spike_duration = time.time() - spike_start
            post_memory = self.get_memory_snapshot()
            memory_impact = post_memory['process_memory_mb'] - pre_memory['process_memory_mb']
            
            logger.info(f"[Spike {spike_num + 1}] Complete in {spike_duration:.2f}s, "
                       f"Memory impact: +{memory_impact:.1f} MB")
            
            self.log_result({
                'spike_num': spike_num + 1,
                'duration': spike_duration,
                'tasks_completed': len(results),
                'throughput_tasks_per_sec': len(results) / spike_duration,
                'memory_impact_mb': memory_impact,
                **post_memory
            })
            
            # Cool-down between spikes
            logger.info(f"[Spike {spike_num + 1}] Cooling down (30s)...")
            time.sleep(30)
            gc.collect()
        
        logger.info(f"✅ Spike load test complete: {self.num_spikes} spikes")


class MemoryLeakTest(StressTest):
    """Detect memory leaks over time"""
    
    def __init__(self, workers: int = 6, iterations: int = 100, leak_per_task_mb: float = 5.0):
        super().__init__(f"memory_leak_{workers}w")
        self.workers = workers
        self.iterations = iterations
        self.leak_per_task_mb = leak_per_task_mb
        
    def run(self):
        logger.info(f"Starting memory leak test: {self.iterations} iterations, "
                   f"{self.workers} workers, {self.leak_per_task_mb} MB leak per task")
        
        tracemalloc.start()
        initial_memory = self.get_memory_snapshot()
        
        for iteration in range(self.iterations):
            with Pool(processes=self.workers) as pool:
                # Run tasks that intentionally leak memory
                results = pool.starmap(memory_leak_task, 
                                     [(i, self.leak_per_task_mb) for i in range(10)])
            
            current_memory = self.get_memory_snapshot()
            memory_growth = current_memory['process_memory_mb'] - initial_memory['process_memory_mb']
            
            if iteration % 10 == 0:
                logger.warning(f"[Iteration {iteration}] Memory: {current_memory['process_memory_mb']:.1f} MB "
                             f"(+{memory_growth:.1f} MB from start)")
                
                self.log_result({
                    'iteration': iteration,
                    'memory_growth_mb': memory_growth,
                    **current_memory
                })
            
            # Intentionally NOT calling gc.collect() to simulate leak
        
        final_memory = self.get_memory_snapshot()
        total_leak = final_memory['process_memory_mb'] - initial_memory['process_memory_mb']
        
        tracemalloc.stop()
        
        logger.warning(f"⚠️ Memory leak test complete: {total_leak:.1f} MB leaked over {self.iterations} iterations")
        logger.warning(f"   Expected leak: ~{self.iterations * 10 * self.leak_per_task_mb:.1f} MB")
        logger.warning(f"   Actual leak: {total_leak:.1f} MB")
        
        return {
            'total_leak_mb': total_leak,
            'iterations': self.iterations,
            'final_memory': final_memory
        }


class ResourceExhaustionTest(StressTest):
    """Test behavior at resource limits"""
    
    def __init__(self, target_memory_percent: float = 80.0):
        super().__init__(f"resource_exhaustion_{int(target_memory_percent)}pct")
        self.target_memory_percent = target_memory_percent
        
    def run(self):
        logger.info(f"Starting resource exhaustion test: target {self.target_memory_percent}% memory")
        
        initial_memory = self.get_memory_snapshot()
        target_mb = (psutil.virtual_memory().total / 1024 / 1024) * (self.target_memory_percent / 100)
        
        # Allocate memory in chunks until target reached
        chunks = []
        chunk_size_mb = 100
        
        while True:
            current_memory = self.get_memory_snapshot()
            
            if current_memory['system_memory_percent'] >= self.target_memory_percent:
                logger.warning(f"⚠️ Target memory usage reached: {current_memory['system_memory_percent']:.1f}%")
                break
            
            # Allocate chunk
            chunk = [random.random() for _ in range(int(chunk_size_mb * 1024 * 128))]
            chunks.append(chunk)
            
            logger.info(f"Allocated {len(chunks) * chunk_size_mb} MB total, "
                       f"System memory: {current_memory['system_memory_percent']:.1f}%")
            
            self.log_result({
                'allocated_mb': len(chunks) * chunk_size_mb,
                **current_memory
            })
            
            time.sleep(1)
        
        final_memory = self.get_memory_snapshot()
        logger.warning(f"⚠️ Resource exhaustion test complete")
        logger.warning(f"   Allocated: {len(chunks) * chunk_size_mb} MB in {len(chunks)} chunks")
        logger.warning(f"   System memory: {final_memory['system_memory_percent']:.1f}%")
        
        # Cleanup
        chunks.clear()
        gc.collect()
        
        return {
            'allocated_mb': len(chunks) * chunk_size_mb,
            'final_memory': final_memory
        }


def run_all_stress_tests():
    """Run comprehensive stress test suite"""
    print("="*80)
    print("EQ12 STRESS TEST SUITE")
    print("="*80)
    
    tests = [
        # Quick tests (for demo/validation)
        SustainedLoadTest(duration_minutes=5, workers=6, tasks_per_sec=10),
        SpikeLoadTest(spike_workers=8, spike_tasks=500, num_spikes=3),
        MemoryLeakTest(workers=6, iterations=20, leak_per_task_mb=2.0),
        
        # Uncomment for full stress testing (hours)
        # SustainedLoadTest(duration_minutes=60, workers=6, tasks_per_sec=20),
        # SustainedLoadTest(duration_minutes=180, workers=8, tasks_per_sec=15),
        # ResourceExhaustionTest(target_memory_percent=75.0),
    ]
    
    results = {}
    for test in tests:
        print(f"\n{'='*80}")
        print(f"Running: {test.name}")
        print(f"{'='*80}")
        
        try:
            result = test.run()
            results[test.name] = result
        except Exception as e:
            logger.error(f"Test {test.name} failed: {e}", exc_info=True)
            results[test.name] = {'error': str(e)}
    
    # Summary
    print(f"\n{'='*80}")
    print("STRESS TEST SUMMARY")
    print(f"{'='*80}")
    for test_name, result in results.items():
        print(f"\n[{test_name}]")
        if 'error' in result:
            print(f"  ❌ FAILED: {result['error']}")
        else:
            for key, value in result.items():
                if isinstance(value, dict):
                    continue
                print(f"  {key}: {value}")
    
    return results


if __name__ == "__main__":
    run_all_stress_tests()
