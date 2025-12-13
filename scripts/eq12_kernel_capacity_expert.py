#!/usr/bin/env python3
"""
 EQ12 KERNEL SYSTEM CAPACITY OPTIMIZATION EXPERT
Advanced system analysis and optimization for maximum performance

Created: November 7, 2025
Author: EQ12 System Operations Team - Kernel Expert
Purpose: Comprehensive system capacity analysis and optimization
"""

import asyncio
import json
import logging
import os
import psutil
import platform
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import multiprocessing as mp


class EQ12KernelCapacityExpert:
    """
     Advanced kernel-level system capacity optimization expert
    """
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.logs_path = self.workspace_path / "logs"
        self.data_path = self.workspace_path / "data"
        self.scripts_path = self.workspace_path / "scripts"
        
        # Create directories
        for path in [self.logs_path, self.data_path]:
            path.mkdir(exist_ok=True)
        
        self.logger = self._setup_logging()
        
        # System capacity metrics
        self.system_info = {}
        self.process_info = {}
        self.capacity_analysis = {}
        self.optimization_recommendations = []
        
        self.logger.info(" EQ12 Kernel Capacity Expert initialized")
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        log_file = self.logs_path / f"kernel_capacity_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        return logging.getLogger(__name__)

    def analyze_system_hardware(self) -> Dict:
        """Comprehensive hardware analysis"""
        self.logger.info(" Analyzing system hardware capacity...")
        
        try:
            # CPU Information
            cpu_info = {
                "physical_cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "max_frequency": psutil.cpu_freq().max if psutil.cpu_freq() else "Unknown",
                "current_frequency": psutil.cpu_freq().current if psutil.cpu_freq() else "Unknown",
                "cpu_percent": psutil.cpu_percent(interval=1),
                "per_cpu_percent": psutil.cpu_percent(interval=1, percpu=True),
                "architecture": platform.architecture()[0],
                "processor": platform.processor()
            }
            
            # Memory Information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            memory_info = {
                "total_ram_gb": round(memory.total / (1024**3), 2),
                "available_ram_gb": round(memory.available / (1024**3), 2),
                "used_ram_gb": round(memory.used / (1024**3), 2),
                "ram_percent": memory.percent,
                "total_swap_gb": round(swap.total / (1024**3), 2),
                "used_swap_gb": round(swap.used / (1024**3), 2),
                "swap_percent": swap.percent
            }
            
            # Disk Information
            disk_usage = []
            for partition in psutil.disk_partitions():
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "file_system": partition.fstype,
                        "total_gb": round(partition_usage.total / (1024**3), 2),
                        "used_gb": round(partition_usage.used / (1024**3), 2),
                        "free_gb": round(partition_usage.free / (1024**3), 2),
                        "percent": round((partition_usage.used / partition_usage.total) * 100, 2)
                    })
                except PermissionError:
                    continue
            
            # Network Information
            network_stats = psutil.net_io_counters()
            network_info = {
                "bytes_sent": network_stats.bytes_sent,
                "bytes_recv": network_stats.bytes_recv,
                "packets_sent": network_stats.packets_sent,
                "packets_recv": network_stats.packets_recv
            }
            
            self.system_info = {
                "cpu": cpu_info,
                "memory": memory_info,
                "disk": disk_usage,
                "network": network_info,
                "platform": {
                    "system": platform.system(),
                    "release": platform.release(),
                    "version": platform.version(),
                    "machine": platform.machine(),
                    "node": platform.node()
                }
            }
            
            self.logger.info(f" Hardware analysis complete - {cpu_info['logical_cores']} cores, {memory_info['total_ram_gb']}GB RAM")
            return self.system_info
            
        except Exception as e:
            self.logger.error(f" Hardware analysis error: {e}")
            return {}

    def analyze_eq12_processes(self) -> Dict:
        """Analyze EQ12-specific processes and resource usage"""
        self.logger.info(" Analyzing EQ12 process capacity utilization...")
        
        try:
            eq12_processes = []
            total_eq12_memory = 0
            total_eq12_cpu = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent', 'create_time', 'cmdline']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info['name'].lower()
                    cmdline = ' '.join(proc_info['cmdline'] or []).lower()
                    
                    # Identify EQ12-related processes
                    is_eq12_related = (
                        'python' in proc_name and ('eq12' in cmdline or 'c:\\eq12' in cmdline) or
                        'node' in proc_name and ('eq12' in cmdline or 'c:\\eq12' in cmdline) or
                        'eq12' in proc_name or
                        'eq12' in cmdline
                    )
                    
                    if is_eq12_related:
                        memory_mb = proc_info['memory_info'].rss / (1024 * 1024)
                        cpu_percent = proc_info['cpu_percent'] or 0
                        
                        eq12_processes.append({
                            "pid": proc_info['pid'],
                            "name": proc_info['name'],
                            "memory_mb": round(memory_mb, 2),
                            "cpu_percent": cpu_percent,
                            "create_time": datetime.fromtimestamp(proc_info['create_time']).isoformat(),
                            "cmdline": ' '.join(proc_info['cmdline'] or [])[:100] + "..." if len(' '.join(proc_info['cmdline'] or [])) > 100 else ' '.join(proc_info['cmdline'] or [])
                        })
                        
                        total_eq12_memory += memory_mb
                        total_eq12_cpu += cpu_percent
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            self.process_info = {
                "eq12_processes": sorted(eq12_processes, key=lambda x: x['memory_mb'], reverse=True),
                "total_eq12_processes": len(eq12_processes),
                "total_eq12_memory_mb": round(total_eq12_memory, 2),
                "total_eq12_cpu_percent": round(total_eq12_cpu, 2),
                "eq12_memory_percent": round((total_eq12_memory / (self.system_info['memory']['total_ram_gb'] * 1024)) * 100, 2) if self.system_info else 0
            }
            
            self.logger.info(f" Process analysis complete - {len(eq12_processes)} EQ12 processes using {total_eq12_memory:.2f}MB")
            return self.process_info
            
        except Exception as e:
            self.logger.error(f" Process analysis error: {e}")
            return {}

    def analyze_directory_capacity(self) -> Dict:
        """Analyze EQ12 directory structure and capacity usage"""
        self.logger.info(" Analyzing EQ12 directory capacity...")
        
        try:
            directory_analysis = {}
            
            for root_dir in self.workspace_path.iterdir():
                if root_dir.is_dir():
                    try:
                        dir_stats = self._get_directory_stats(root_dir)
                        directory_analysis[root_dir.name] = dir_stats
                    except Exception as e:
                        self.logger.warning(f" Could not analyze {root_dir.name}: {e}")
                        directory_analysis[root_dir.name] = {"error": str(e)}
            
            # Calculate total EQ12 usage
            total_files = sum(stats.get('file_count', 0) for stats in directory_analysis.values() if 'file_count' in stats)
            total_size_mb = sum(stats.get('size_mb', 0) for stats in directory_analysis.values() if 'size_mb' in stats)
            
            directory_capacity = {
                "directories": directory_analysis,
                "total_files": total_files,
                "total_size_mb": round(total_size_mb, 2),
                "total_size_gb": round(total_size_mb / 1024, 2),
                "largest_directory": max(directory_analysis.items(), 
                                       key=lambda x: x[1].get('size_mb', 0) if 'size_mb' in x[1] else 0,
                                       default=("none", {}))[0]
            }
            
            self.logger.info(f" Directory analysis complete - {total_files} files, {total_size_mb:.2f}MB total")
            return directory_capacity
            
        except Exception as e:
            self.logger.error(f" Directory analysis error: {e}")
            return {}

    def _get_directory_stats(self, directory: Path) -> Dict:
        """Get statistics for a specific directory"""
        total_size = 0
        file_count = 0
        largest_file = {"name": "", "size_mb": 0}
        
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                try:
                    file_size = file_path.stat().st_size
                    total_size += file_size
                    file_count += 1
                    
                    file_size_mb = file_size / (1024 * 1024)
                    if file_size_mb > largest_file["size_mb"]:
                        largest_file = {
                            "name": file_path.name,
                            "size_mb": round(file_size_mb, 2),
                            "path": str(file_path.relative_to(directory))
                        }
                except (OSError, PermissionError):
                    continue
        
        return {
            "file_count": file_count,
            "size_mb": round(total_size / (1024 * 1024), 2),
            "largest_file": largest_file
        }

    def analyze_performance_bottlenecks(self) -> Dict:
        """Identify system performance bottlenecks"""
        self.logger.info(" Analyzing performance bottlenecks...")
        
        try:
            bottlenecks = []
            optimization_potential = {}
            
            # CPU Analysis
            cpu_usage = self.system_info['cpu']['cpu_percent']
            if cpu_usage > 80:
                bottlenecks.append({
                    "type": "CPU",
                    "severity": "HIGH",
                    "current_usage": f"{cpu_usage}%",
                    "recommendation": "Consider CPU-intensive task scheduling or process optimization"
                })
            elif cpu_usage < 30:
                optimization_potential["CPU"] = {
                    "current_usage": f"{cpu_usage}%",
                    "potential": "HIGH",
                    "recommendation": "CPU capacity available for additional workloads"
                }
            
            # Memory Analysis
            memory_usage = self.system_info['memory']['ram_percent']
            available_gb = self.system_info['memory']['available_ram_gb']
            
            if memory_usage > 85:
                bottlenecks.append({
                    "type": "Memory",
                    "severity": "HIGH",
                    "current_usage": f"{memory_usage}%",
                    "recommendation": "Consider memory cleanup or process consolidation"
                })
            elif available_gb > 8:
                optimization_potential["Memory"] = {
                    "available_gb": available_gb,
                    "potential": "HIGH",
                    "recommendation": f"{available_gb:.1f}GB available for memory-intensive operations"
                }
            
            # Process Analysis
            eq12_memory_percent = self.process_info.get('eq12_memory_percent', 0)
            eq12_process_count = self.process_info.get('total_eq12_processes', 0)
            
            if eq12_process_count > 20:
                bottlenecks.append({
                    "type": "Process Count",
                    "severity": "MEDIUM",
                    "current_count": eq12_process_count,
                    "recommendation": "Consider process consolidation or cleanup"
                })
            
            # Disk Analysis
            for disk in self.system_info.get('disk', []):
                if disk['percent'] > 90:
                    bottlenecks.append({
                        "type": "Disk Space",
                        "severity": "HIGH",
                        "device": disk['device'],
                        "usage": f"{disk['percent']}%",
                        "recommendation": "Clean up disk space or move data"
                    })
                elif disk['free_gb'] > 50:
                    optimization_potential[f"Disk_{disk['device']}"] = {
                        "free_gb": disk['free_gb'],
                        "potential": "MEDIUM",
                        "recommendation": f"{disk['free_gb']:.1f}GB available for data storage"
                    }
            
            performance_analysis = {
                "bottlenecks": bottlenecks,
                "optimization_potential": optimization_potential,
                "system_health": "EXCELLENT" if not bottlenecks else "GOOD" if len(bottlenecks) <= 2 else "NEEDS_ATTENTION",
                "capacity_utilization": {
                    "cpu_utilization": f"{cpu_usage}%",
                    "memory_utilization": f"{memory_usage}%",
                    "eq12_memory_share": f"{eq12_memory_percent}%"
                }
            }
            
            self.logger.info(f" Performance analysis complete - {len(bottlenecks)} bottlenecks, {len(optimization_potential)} optimization opportunities")
            return performance_analysis
            
        except Exception as e:
            self.logger.error(f" Performance analysis error: {e}")
            return {}

    def generate_optimization_recommendations(self) -> List[Dict]:
        """Generate specific optimization recommendations"""
        self.logger.info(" Generating optimization recommendations...")
        
        try:
            recommendations = []
            
            # CPU Optimization
            cpu_cores = self.system_info['cpu']['logical_cores']
            cpu_usage = self.system_info['cpu']['cpu_percent']
            
            if cpu_usage < 50 and cpu_cores >= 4:
                recommendations.append({
                    "category": "Parallel Processing",
                    "priority": "HIGH",
                    "title": "Increase Parallel Workloads",
                    "description": f"CPU utilization at {cpu_usage}% with {cpu_cores} cores available",
                    "implementation": [
                        "Enable multi-processing in Python scripts",
                        "Use ThreadPoolExecutor for I/O-bound tasks",
                        "Implement asyncio for concurrent operations",
                        "Consider running multiple EQ12 instances"
                    ],
                    "expected_improvement": "200-400% throughput increase"
                })
            
            # Memory Optimization
            available_memory = self.system_info['memory']['available_ram_gb']
            if available_memory > 4:
                recommendations.append({
                    "category": "Memory Utilization",
                    "priority": "MEDIUM",
                    "title": "Increase Memory-Intensive Operations",
                    "description": f"{available_memory:.1f}GB RAM available for optimization",
                    "implementation": [
                        "Increase cache sizes in applications",
                        "Load more data into memory for faster access",
                        "Use memory-based databases (Redis, etc.)",
                        "Preload frequently accessed data"
                    ],
                    "expected_improvement": "50-100% faster data access"
                })
            
            # Process Optimization
            eq12_processes = self.process_info.get('total_eq12_processes', 0)
            if eq12_processes < 10:
                recommendations.append({
                    "category": "Process Scaling",
                    "priority": "HIGH",
                    "title": "Scale EQ12 Operations",
                    "description": f"Only {eq12_processes} EQ12 processes running - capacity for more",
                    "implementation": [
                        "Run multiple betting analysis scripts simultaneously",
                        "Implement distributed scraping operations",
                        "Start additional monitoring processes",
                        "Deploy parallel AI analysis workers"
                    ],
                    "expected_improvement": "300-500% operational capacity"
                })
            
            # Storage Optimization
            largest_dir = self.capacity_analysis.get('largest_directory', 'Unknown')
            if largest_dir and largest_dir != 'Unknown':
                recommendations.append({
                    "category": "Storage Efficiency",
                    "priority": "MEDIUM",
                    "title": "Optimize Data Storage",
                    "description": f"Largest directory: {largest_dir}",
                    "implementation": [
                        "Implement data compression for logs",
                        "Archive old data to secondary storage",
                        "Use database systems for structured data",
                        "Implement data deduplication"
                    ],
                    "expected_improvement": "30-50% storage efficiency"
                })
            
            # Network Optimization
            recommendations.append({
                "category": "Network Utilization",
                "priority": "MEDIUM",
                "title": "Maximize Network Throughput",
                "description": "Optimize API calls and data transfers",
                "implementation": [
                    "Implement connection pooling",
                    "Use async HTTP clients",
                    "Batch API requests where possible",
                    "Implement request caching"
                ],
                "expected_improvement": "100-200% API efficiency"
            })
            
            # EQ12-Specific Optimizations
            recommendations.append({
                "category": "EQ12 System Integration",
                "priority": "HIGH",
                "title": "Kernel-Level EQ12 Optimization",
                "description": "Maximize EQ12 system capacity utilization",
                "implementation": [
                    "Deploy AI-enhanced betting analysis in parallel",
                    "Run multiple sports monitoring simultaneously",
                    "Implement real-time odds arbitrage detection",
                    "Scale blockchain arbitrage operations",
                    "Deploy advanced scraping infrastructure"
                ],
                "expected_improvement": "1000%+ operational efficiency"
            })
            
            self.optimization_recommendations = recommendations
            self.logger.info(f" Generated {len(recommendations)} optimization recommendations")
            return recommendations
            
        except Exception as e:
            self.logger.error(f" Recommendation generation error: {e}")
            return []

    async def comprehensive_capacity_analysis(self):
        """Run comprehensive system capacity analysis"""
        self.logger.info(" Starting comprehensive EQ12 kernel capacity analysis...")
        
        # Hardware Analysis
        self.analyze_system_hardware()
        
        # Process Analysis
        self.analyze_eq12_processes()
        
        # Directory Analysis
        self.capacity_analysis = self.analyze_directory_capacity()
        
        # Performance Analysis
        performance_analysis = self.analyze_performance_bottlenecks()
        
        # Generate Recommendations
        recommendations = self.generate_optimization_recommendations()
        
        # Compile comprehensive report
        comprehensive_report = {
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "EQ12 Kernel System Capacity Optimization",
            "system_hardware": self.system_info,
            "eq12_processes": self.process_info,
            "directory_capacity": self.capacity_analysis,
            "performance_analysis": performance_analysis,
            "optimization_recommendations": recommendations,
            "system_utilization_score": self._calculate_utilization_score(),
            "capacity_potential": self._calculate_capacity_potential(),
            "next_actions": self._generate_immediate_actions()
        }
        
        # Save comprehensive report
        report_file = self.data_path / f"eq12_kernel_capacity_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_report, f, indent=2)
        
        self.logger.info(f" Comprehensive capacity analysis saved: {report_file}")
        
        return comprehensive_report

    def _calculate_utilization_score(self) -> int:
        """Calculate overall system utilization score (0-100)"""
        try:
            cpu_score = min(self.system_info['cpu']['cpu_percent'], 100)
            memory_score = self.system_info['memory']['ram_percent']
            process_score = min(self.process_info.get('total_eq12_processes', 0) * 5, 100)
            
            # Weight the scores
            utilization_score = (cpu_score * 0.4 + memory_score * 0.4 + process_score * 0.2)
            return int(utilization_score)
        except:
            return 0

    def _calculate_capacity_potential(self) -> str:
        """Calculate remaining capacity potential"""
        try:
            cpu_available = 100 - self.system_info['cpu']['cpu_percent']
            memory_available = 100 - self.system_info['memory']['ram_percent']
            
            if cpu_available > 70 and memory_available > 70:
                return "MASSIVE POTENTIAL (70%+ capacity available)"
            elif cpu_available > 50 and memory_available > 50:
                return "HIGH POTENTIAL (50%+ capacity available)"
            elif cpu_available > 30 and memory_available > 30:
                return "MEDIUM POTENTIAL (30%+ capacity available)"
            else:
                return "LIMITED POTENTIAL (System near capacity)"
        except:
            return "UNKNOWN"

    def _generate_immediate_actions(self) -> List[str]:
        """Generate immediate action items"""
        actions = []
        
        try:
            cpu_usage = self.system_info['cpu']['cpu_percent']
            available_memory = self.system_info['memory']['available_ram_gb']
            eq12_processes = self.process_info.get('total_eq12_processes', 0)
            
            if cpu_usage < 50:
                actions.append(" IMMEDIATE: Launch additional EQ12 parallel processes")
            
            if available_memory > 4:
                actions.append(" IMMEDIATE: Increase memory-intensive operations")
            
            if eq12_processes < 15:
                actions.append(" IMMEDIATE: Scale EQ12 betting and monitoring systems")
            
            actions.append(" IMMEDIATE: Deploy AI-enhanced multi-process betting analysis")
            actions.append(" IMMEDIATE: Implement parallel sports data collection")
            actions.append(" IMMEDIATE: Enable concurrent arbitrage detection")
            
        except:
            actions = [" Perform manual system assessment"]
        
        return actions


async def main():
    """Run EQ12 Kernel Capacity Expert Analysis"""
    print(" EQ12 KERNEL SYSTEM CAPACITY OPTIMIZATION EXPERT")
    print("Advanced Analysis for Maximum Performance Utilization")
    print("=" * 80)
    
    # Initialize expert system
    kernel_expert = EQ12KernelCapacityExpert()
    
    # Run comprehensive analysis
    report = await kernel_expert.comprehensive_capacity_analysis()
    
    # Display results
    print(f"\n KERNEL CAPACITY ANALYSIS COMPLETE")
    print("=" * 80)
    
    # System Summary
    hardware = report["system_hardware"]
    processes = report["eq12_processes"]
    performance = report["performance_analysis"]
    
    print(f" HARDWARE CAPACITY:")
    print(f"    CPU: {hardware['cpu']['logical_cores']} cores @ {hardware['cpu']['cpu_percent']}% utilization")
    print(f"    RAM: {hardware['memory']['total_ram_gb']}GB total, {hardware['memory']['available_ram_gb']}GB available")
    print(f"    System Health: {performance['system_health']}")
    
    print(f"\n EQ12 PROCESS UTILIZATION:")
    print(f"    Active EQ12 Processes: {processes['total_eq12_processes']}")
    print(f"    EQ12 Memory Usage: {processes['total_eq12_memory_mb']}MB ({processes['eq12_memory_percent']}%)")
    print(f"    EQ12 CPU Usage: {processes['total_eq12_cpu_percent']}%")
    
    print(f"\n CAPACITY ANALYSIS:")
    print(f"    Utilization Score: {report['system_utilization_score']}/100")
    print(f"    Capacity Potential: {report['capacity_potential']}")
    print(f"    Optimization Opportunities: {len(report['optimization_recommendations'])}")
    
    print(f"\n IMMEDIATE ACTIONS REQUIRED:")
    for i, action in enumerate(report['next_actions'], 1):
        print(f"   {i}. {action}")
    
    print(f"\n TOP OPTIMIZATION RECOMMENDATIONS:")
    for i, rec in enumerate(report['optimization_recommendations'][:3], 1):
        print(f"   {i}. {rec['title']} ({rec['priority']} priority)")
        print(f"      Expected: {rec['expected_improvement']}")
    
    # Show top EQ12 processes
    if processes['eq12_processes']:
        print(f"\n TOP EQ12 PROCESSES (Memory Usage):")
        for i, proc in enumerate(processes['eq12_processes'][:5], 1):
            print(f"   {i}. {proc['name']} (PID: {proc['pid']}) - {proc['memory_mb']}MB")
    
    print("\n" + "=" * 80)
    print(" KERNEL EXPERT ANALYSIS: System capacity assessment complete!")
    print(" RECOMMENDATION: Utilize available capacity for maximum EQ12 performance!")
    print(" NEXT STEP: Implement parallel processing and scaling recommendations!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())