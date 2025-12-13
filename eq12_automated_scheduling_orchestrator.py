#!/usr/bin/env python3
"""
 EQ12 AUTOMATED SCHEDULING ORCHESTRATOR
=========================================

Advanced scheduling system that coordinates automated execution cycles
for all EQ12 systems with intelligent timing and dependency management.

Scheduling Features:
- Intelligent interval-based scheduling
- Dependency-aware execution order
- Load balancing and resource optimization
- Failure detection and automatic retry
- Performance-based schedule adjustment
- Business hours and timezone awareness

Integration Points:
- Daily Maintenance Pack (24-hour cycles)
- Self-Healing Orchestrator (5-minute cycles)
- International Weather Engine (1-hour cycles)
- Multi-Tier Architecture (30-minute cycles)
- Business Intelligence (12-hour cycles)
- Revenue Accelerator (6-hour cycles)

Author: EQ12 Quantum Development Team
Version: 1.0.0 - Automated Scheduling
Date: November 7, 2025
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import sqlite3


class ScheduleStatus(Enum):
    """Schedule status enumeration."""
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"
    ERROR = "error"


class ExecutionMode(Enum):
    """Execution mode enumeration."""
    IMMEDIATE = "immediate"
    SCHEDULED = "scheduled"
    CONDITIONAL = "conditional"
    MANUAL = "manual"


@dataclass
class ScheduledTask:
    """Scheduled task configuration."""
    task_id: str
    task_name: str
    system_script: str
    execution_mode: ExecutionMode
    schedule_interval_minutes: int
    next_execution: datetime
    last_execution: Optional[datetime]
    status: ScheduleStatus
    priority: int
    dependencies: List[str]
    max_runtime_minutes: int
    retry_count: int
    success_count: int
    failure_count: int


class EQ12SchedulingOrchestrator:
    """Automated scheduling and orchestration system for EQ12."""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.scripts_path = self.workspace_path / "scripts"
        self.logs_path = self.workspace_path / "logs"
        self.data_path = self.workspace_path / "data"
        
        # Ensure directories exist
        for path in [self.logs_path, self.data_path]:
            path.mkdir(exist_ok=True)
        
        # Setup logging
        self.timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        log_file = self.logs_path / f"scheduling_orchestrator_{self.timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self.db_path = self.data_path / "scheduling_orchestrator.db"
        self._initialize_database()
        
        # Initialize scheduled tasks
        self.scheduled_tasks = self._initialize_scheduled_tasks()
        self.running_tasks = {}
        
        # Orchestrator settings
        self.check_interval_seconds = 30
        self.max_concurrent_tasks = 4
        self.business_hours_start = 6  # 6 AM
        self.business_hours_end = 22   # 10 PM
    
    def _initialize_database(self):
        """Initialize the scheduling database."""
        conn = sqlite3.connect(self.db_path)
        
        # Scheduled tasks table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_tasks (
                task_id TEXT PRIMARY KEY,
                task_name TEXT NOT NULL,
                system_script TEXT NOT NULL,
                execution_mode TEXT NOT NULL,
                schedule_interval_minutes INTEGER NOT NULL,
                next_execution TIMESTAMP NOT NULL,
                last_execution TIMESTAMP,
                status TEXT NOT NULL,
                priority INTEGER NOT NULL,
                dependencies TEXT,
                max_runtime_minutes INTEGER NOT NULL,
                retry_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Execution logs table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS execution_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                execution_start TIMESTAMP NOT NULL,
                execution_end TIMESTAMP,
                status TEXT NOT NULL,
                exit_code INTEGER,
                output_log TEXT,
                error_message TEXT,
                performance_metrics TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Schedule adjustments table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS schedule_adjustments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                old_interval_minutes INTEGER NOT NULL,
                new_interval_minutes INTEGER NOT NULL,
                adjustment_reason TEXT NOT NULL,
                adjustment_timestamp TIMESTAMP NOT NULL,
                performance_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _initialize_scheduled_tasks(self) -> List[ScheduledTask]:
        """Initialize the scheduled tasks configuration."""
        now = datetime.now(timezone.utc)
        
        tasks = [
            ScheduledTask(
                task_id="daily_maintenance_schedule",
                task_name="Daily Maintenance Pack",
                system_script="eq12_daily_maintenance.py",
                execution_mode=ExecutionMode.SCHEDULED,
                schedule_interval_minutes=1440,  # 24 hours
                next_execution=now + timedelta(hours=1),
                last_execution=None,
                status=ScheduleStatus.ACTIVE,
                priority=1,
                dependencies=[],
                max_runtime_minutes=30,
                retry_count=0,
                success_count=0,
                failure_count=0
            ),
            ScheduledTask(
                task_id="self_healing_schedule",
                task_name="Self-Healing Orchestrator",
                system_script="eq12_self_healing_orchestrator.py",
                execution_mode=ExecutionMode.SCHEDULED,
                schedule_interval_minutes=5,  # 5 minutes
                next_execution=now + timedelta(minutes=2),
                last_execution=None,
                status=ScheduleStatus.ACTIVE,
                priority=1,
                dependencies=[],
                max_runtime_minutes=10,
                retry_count=0,
                success_count=0,
                failure_count=0
            ),
            ScheduledTask(
                task_id="international_weather_schedule",
                task_name="International Sports Weather Engine",
                system_script="eq12_international_sports_weather_engine.py",
                execution_mode=ExecutionMode.SCHEDULED,
                schedule_interval_minutes=60,  # 1 hour
                next_execution=now + timedelta(minutes=15),
                last_execution=None,
                status=ScheduleStatus.ACTIVE,
                priority=2,
                dependencies=["daily_maintenance_schedule"],
                max_runtime_minutes=20,
                retry_count=0,
                success_count=0,
                failure_count=0
            ),
            ScheduledTask(
                task_id="multi_tier_architecture_schedule",
                task_name="Multi-Tier Architecture Engine",
                system_script="eq12_multi_tier_architecture_engine.py",
                execution_mode=ExecutionMode.SCHEDULED,
                schedule_interval_minutes=30,  # 30 minutes
                next_execution=now + timedelta(minutes=10),
                last_execution=None,
                status=ScheduleStatus.ACTIVE,
                priority=2,
                dependencies=["self_healing_schedule"],
                max_runtime_minutes=15,
                retry_count=0,
                success_count=0,
                failure_count=0
            ),
            ScheduledTask(
                task_id="business_intelligence_schedule",
                task_name="Business Intelligence Strategy",
                system_script="eq12_business_intelligence_prompt_pack_generator.py",
                execution_mode=ExecutionMode.SCHEDULED,
                schedule_interval_minutes=720,  # 12 hours
                next_execution=now + timedelta(hours=2),
                last_execution=None,
                status=ScheduleStatus.ACTIVE,
                priority=3,
                dependencies=["international_weather_schedule"],
                max_runtime_minutes=45,
                retry_count=0,
                success_count=0,
                failure_count=0
            ),
            ScheduledTask(
                task_id="revenue_accelerator_schedule",
                task_name="Revenue Scale Accelerator",
                system_script="eq12_revenue_scale_accelerator.py",
                execution_mode=ExecutionMode.SCHEDULED,
                schedule_interval_minutes=360,  # 6 hours
                next_execution=now + timedelta(hours=3),
                last_execution=None,
                status=ScheduleStatus.ACTIVE,
                priority=3,
                dependencies=["business_intelligence_schedule"],
                max_runtime_minutes=30,
                retry_count=0,
                success_count=0,
                failure_count=0
            )
        ]
        
        return tasks
    
    def is_business_hours(self) -> bool:
        """Check if current time is within business hours."""
        now = datetime.now()
        current_hour = now.hour
        return self.business_hours_start <= current_hour <= self.business_hours_end
    
    def calculate_next_execution(self, task: ScheduledTask) -> datetime:
        """Calculate next execution time for a task."""
        now = datetime.now(timezone.utc)
        
        # Base next execution time
        next_time = now + timedelta(minutes=task.schedule_interval_minutes)
        
        # Adjust for business hours (only for non-critical tasks)
        if task.priority > 2 and not self.is_business_hours():
            # Schedule for next business day start
            tomorrow = now + timedelta(days=1)
            next_time = tomorrow.replace(hour=self.business_hours_start, minute=0, second=0)
        
        return next_time
    
    async def execute_scheduled_task(self, task: ScheduledTask) -> Dict[str, Any]:
        """Execute a scheduled task."""
        self.logger.info(f" Executing scheduled task: {task.task_name}")
        
        execution_data = {
            "task_id": task.task_id,
            "task_name": task.task_name,
            "execution_start": datetime.now(timezone.utc).isoformat(),
            "execution_end": None,
            "status": "running",
            "exit_code": None,
            "output": "",
            "error": None,
            "duration_seconds": 0.0
        }
        
        start_time = time.time()
        
        try:
            # Check dependencies
            for dep_id in task.dependencies:
                dep_task = next((t for t in self.scheduled_tasks if t.task_id == dep_id), None)
                if dep_task and dep_task.last_execution is None:
                    raise Exception(f"Dependency {dep_id} has not been executed yet")
            
            # Construct script path
            script_path = self.scripts_path / task.system_script
            
            if not script_path.exists():
                raise Exception(f"Script not found: {script_path}")
            
            # Execute the task
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(script_path), "--workspace", str(self.workspace_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Store running process
            self.running_tasks[task.task_id] = process
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=task.max_runtime_minutes * 60
                )
                
                execution_data["exit_code"] = process.returncode
                execution_data["output"] = stdout.decode('utf-8', errors='ignore')
                
                if stderr:
                    execution_data["error"] = stderr.decode('utf-8', errors='ignore')
                
                if process.returncode == 0:
                    execution_data["status"] = "success"
                    task.success_count += 1
                    self.logger.info(f" Task {task.task_name} completed successfully")
                else:
                    execution_data["status"] = "failed"
                    task.failure_count += 1
                    self.logger.error(f" Task {task.task_name} failed with exit code {process.returncode}")
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                execution_data["status"] = "timeout"
                execution_data["error"] = f"Task exceeded maximum runtime of {task.max_runtime_minutes} minutes"
                task.failure_count += 1
                self.logger.error(f" Task {task.task_name} timed out")
            
        except Exception as e:
            execution_data["status"] = "error"
            execution_data["error"] = str(e)
            task.failure_count += 1
            self.logger.error(f" Task {task.task_name} error: {e}")
        
        finally:
            # Clean up
            if task.task_id in self.running_tasks:
                del self.running_tasks[task.task_id]
            
            # Update execution data
            execution_data["execution_end"] = datetime.now(timezone.utc).isoformat()
            execution_data["duration_seconds"] = time.time() - start_time
            
            # Update task
            task.last_execution = datetime.now(timezone.utc)
            task.next_execution = self.calculate_next_execution(task)
            
            # Log execution
            self._log_execution(execution_data)
        
        return execution_data
    
    def _log_execution(self, execution_data: Dict[str, Any]):
        """Log task execution to database."""
        conn = sqlite3.connect(self.db_path)
        
        conn.execute('''
            INSERT INTO execution_logs 
            (task_id, execution_start, execution_end, status, exit_code, output_log, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            execution_data["task_id"],
            execution_data["execution_start"],
            execution_data["execution_end"],
            execution_data["status"],
            execution_data["exit_code"],
            execution_data.get("output", ""),
            execution_data.get("error")
        ))
        
        conn.commit()
        conn.close()
    
    async def check_and_execute_due_tasks(self) -> List[Dict[str, Any]]:
        """Check for due tasks and execute them."""
        now = datetime.now(timezone.utc)
        executed_tasks = []
        
        # Get due tasks
        due_tasks = [
            task for task in self.scheduled_tasks
            if task.status == ScheduleStatus.ACTIVE 
            and task.next_execution <= now
            and task.task_id not in self.running_tasks
        ]
        
        # Sort by priority
        due_tasks.sort(key=lambda t: t.priority)
        
        # Execute tasks (respecting concurrency limit)
        concurrent_count = len(self.running_tasks)
        
        for task in due_tasks:
            if concurrent_count >= self.max_concurrent_tasks:
                self.logger.info(f" Task {task.task_name} delayed - max concurrency reached")
                break
            
            print(f" Executing: {task.task_name}")
            execution_result = await self.execute_scheduled_task(task)
            executed_tasks.append(execution_result)
            concurrent_count += 1
        
        return executed_tasks
    
    def adjust_schedule_based_on_performance(self, task: ScheduledTask):
        """Adjust task schedule based on performance metrics."""
        # Calculate success rate
        total_executions = task.success_count + task.failure_count
        if total_executions < 5:
            return  # Need more data
        
        success_rate = task.success_count / total_executions
        
        old_interval = task.schedule_interval_minutes
        adjustment_reason = ""
        
        # Adjust based on success rate
        if success_rate < 0.5:
            # Poor performance - increase interval
            task.schedule_interval_minutes = int(task.schedule_interval_minutes * 1.5)
            adjustment_reason = f"Poor success rate ({success_rate:.1%}) - increased interval"
        elif success_rate > 0.9 and task.schedule_interval_minutes > 30:
            # Excellent performance - might decrease interval
            task.schedule_interval_minutes = int(task.schedule_interval_minutes * 0.9)
            adjustment_reason = f"Excellent success rate ({success_rate:.1%}) - decreased interval"
        
        # Log adjustment if made
        if old_interval != task.schedule_interval_minutes:
            self.logger.info(f" Schedule adjusted for {task.task_name}: {old_interval} -> {task.schedule_interval_minutes} minutes")
            self._log_schedule_adjustment(task.task_id, old_interval, task.schedule_interval_minutes, adjustment_reason)
    
    def _log_schedule_adjustment(self, task_id: str, old_interval: int, new_interval: int, reason: str):
        """Log schedule adjustment to database."""
        conn = sqlite3.connect(self.db_path)
        
        conn.execute('''
            INSERT INTO schedule_adjustments 
            (task_id, old_interval_minutes, new_interval_minutes, adjustment_reason, adjustment_timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            task_id,
            old_interval,
            new_interval,
            reason,
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        conn.close()
    
    async def run_scheduling_orchestrator(self) -> Dict[str, Any]:
        """Run the main scheduling orchestrator loop."""
        print(" EQ12 AUTOMATED SCHEDULING ORCHESTRATOR")
        print("=" * 44)
        print("Intelligent automation scheduling with dependency management...")
        print()
        
        orchestrator_data = {
            "start_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_tasks": len(self.scheduled_tasks),
            "executions_completed": 0,
            "executions_failed": 0,
            "schedule_adjustments": 0,
            "uptime_seconds": 0.0
        }
        
        start_time = time.time()
        
        print(" Scheduling orchestrator started")
        print(f" Monitoring {len(self.scheduled_tasks)} scheduled tasks")
        print(f" Check interval: {self.check_interval_seconds} seconds")
        print(f" Business hours: {self.business_hours_start}:00 - {self.business_hours_end}:00")
        print()
        
        try:
            cycle_count = 0
            
            while True:
                cycle_count += 1
                print(f" Scheduling cycle #{cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
                
                # Check and execute due tasks
                executed_tasks = await self.check_and_execute_due_tasks()
                
                if executed_tasks:
                    for execution in executed_tasks:
                        if execution["status"] == "success":
                            orchestrator_data["executions_completed"] += 1
                            print(f"    {execution['task_name']}: {execution['status']}")
                        else:
                            orchestrator_data["executions_failed"] += 1
                            print(f"    {execution['task_name']}: {execution['status']}")
                
                # Perform schedule adjustments
                for task in self.scheduled_tasks:
                    if (task.success_count + task.failure_count) % 10 == 0 and (task.success_count + task.failure_count) > 0:
                        self.adjust_schedule_based_on_performance(task)
                        orchestrator_data["schedule_adjustments"] += 1
                
                # Display next upcoming tasks
                now = datetime.now(timezone.utc)
                upcoming_tasks = sorted(
                    [t for t in self.scheduled_tasks if t.status == ScheduleStatus.ACTIVE],
                    key=lambda t: t.next_execution
                )[:3]
                
                print("    Next upcoming:")
                for task in upcoming_tasks:
                    time_until = task.next_execution - now
                    minutes_until = int(time_until.total_seconds() / 60)
                    print(f"      {task.task_name}: {minutes_until} minutes")
                
                orchestrator_data["uptime_seconds"] = time.time() - start_time
                
                # Wait for next check
                await asyncio.sleep(self.check_interval_seconds)
                
        except KeyboardInterrupt:
            print("\n Orchestrator shutdown requested...")
            
            # Stop running tasks
            for task_id, process in self.running_tasks.items():
                print(f"    Stopping {task_id}...")
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
            
            orchestrator_data["uptime_seconds"] = time.time() - start_time
            
            print(f"\n ORCHESTRATOR SUMMARY:")
            print(f" Total uptime: {orchestrator_data['uptime_seconds']:.1f} seconds")
            print(f" Executions completed: {orchestrator_data['executions_completed']}")
            print(f" Executions failed: {orchestrator_data['executions_failed']}")
            print(f" Schedule adjustments: {orchestrator_data['schedule_adjustments']}")
            
            # Save orchestrator report
            report_file = self.logs_path / f"scheduling_orchestrator_{self.timestamp}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(orchestrator_data, f, indent=2, ensure_ascii=False)
            
            print(f" Report saved: {report_file}")
        
        return orchestrator_data


async def main():
    """Main execution function for scheduling orchestrator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="EQ12 Automated Scheduling Orchestrator")
    parser.add_argument("--workspace", default="C:\\EQ12", help="EQ12 workspace path")
    parser.add_argument("--check-interval", type=int, default=30, help="Check interval in seconds")
    parser.add_argument("--max-concurrent", type=int, default=4, help="Maximum concurrent tasks")
    parser.add_argument("--business-start", type=int, default=6, help="Business hours start (24h format)")
    parser.add_argument("--business-end", type=int, default=22, help="Business hours end (24h format)")
    args = parser.parse_args()
    
    try:
        # Initialize scheduling orchestrator
        orchestrator = EQ12SchedulingOrchestrator(args.workspace)
        
        # Apply configuration
        orchestrator.check_interval_seconds = args.check_interval
        orchestrator.max_concurrent_tasks = args.max_concurrent
        orchestrator.business_hours_start = args.business_start
        orchestrator.business_hours_end = args.business_end
        
        # Run orchestrator
        await orchestrator.run_scheduling_orchestrator()
        
        return 0
        
    except Exception as e:
        print(f" SCHEDULING ORCHESTRATOR ERROR: {e}")
        logging.error(f"Scheduling orchestrator error: {e}")
        return 1


if __name__ == "__main__":
    # Ensure proper event loop for Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)