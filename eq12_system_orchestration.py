# eq12_system_orchestration.py
"""
EQ12 System Orchestration & Automation Innovation
Intelligent process management, automated failover, real-time health monitoring
"""

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import aiohttp
import psutil

from eq12_helpers import setup_utf8_logging

setup_utf8_logging()


class ServiceState(Enum):
    """Service state enumeration"""

    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"
    RECOVERING = "recovering"


class HealthStatus(Enum):
    """Health check status"""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class ServiceConfig:
    """Service configuration"""

    name: str
    command: list[str]
    working_directory: Path
    environment: dict[str, str] = field(default_factory=dict)
    restart_policy: str = "always"  # always, on-failure, never
    max_restarts: int = 3
    restart_delay: float = 5.0
    health_check_interval: float = 30.0
    health_check_timeout: float = 10.0
    health_check_url: str | None = None
    dependencies: list[str] = field(default_factory=list)
    resource_limits: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessInfo:
    """Process information"""

    pid: int
    name: str
    status: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    create_time: float
    command_line: str


@dataclass
class HealthCheckResult:
    """Health check result"""

    service_name: str
    status: HealthStatus
    timestamp: datetime
    response_time_ms: float
    details: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class ProcessMonitor:
    """Advanced process monitoring and management"""

    def __init__(self):
        self.monitored_processes: dict[str, psutil.Process] = {}
        self.process_stats_history: dict[str, list[ProcessInfo]] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def monitor_process(self, name: str, pid: int) -> ProcessInfo:
        """Monitor single process"""

        try:
            process = psutil.Process(pid)

            # Get process information
            with process.oneshot():
                process_info = ProcessInfo(
                    pid=process.pid,
                    name=process.name(),
                    status=process.status(),
                    cpu_percent=process.cpu_percent(),
                    memory_percent=process.memory_percent(),
                    memory_mb=process.memory_info().rss / 1024 / 1024,
                    create_time=process.create_time(),
                    command_line=" ".join(process.cmdline()),
                )

            # Store in history
            if name not in self.process_stats_history:
                self.process_stats_history[name] = []

            self.process_stats_history[name].append(process_info)

            # Keep only last 100 entries
            if len(self.process_stats_history[name]) > 100:
                self.process_stats_history[name] = self.process_stats_history[name][-100:]

            return process_info

        except psutil.NoSuchProcess:
            return ProcessInfo(
                pid=pid,
                name=name,
                status="terminated",
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_mb=0.0,
                create_time=0.0,
                command_line="",
            )

    async def get_system_resource_usage(self) -> dict[str, Any]:
        """Get system-wide resource usage"""

        # Run CPU-intensive operations in thread pool
        cpu_percent = await asyncio.get_event_loop().run_in_executor(
            self.executor, psutil.cpu_percent, 1
        )

        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "percent": cpu_percent,
                "count": psutil.cpu_count(),
                "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            },
            "memory": {
                "total_gb": memory.total / 1024**3,
                "available_gb": memory.available / 1024**3,
                "percent": memory.percent,
                "used_gb": memory.used / 1024**3,
            },
            "disk": {
                "total_gb": disk.total / 1024**3,
                "free_gb": disk.free / 1024**3,
                "percent": (disk.used / disk.total) * 100,
            },
            "processes": len(psutil.pids()),
        }

    def cleanup(self):
        """Cleanup resources"""
        self.executor.shutdown(wait=False)


class HealthChecker:
    """Service health monitoring system"""

    def __init__(self):
        self.health_history: dict[str, list[HealthCheckResult]] = {}
        self.session: aiohttp.ClientSession | None = None

    async def initialize(self):
        """Initialize HTTP session for health checks"""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))

    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()

    async def check_http_health(
        self, service_name: str, url: str, timeout: float = 10.0
    ) -> HealthCheckResult:
        """Perform HTTP health check"""

        start_time = time.time()

        try:
            if not self.session:
                await self.initialize()

            async with self.session.get(url, timeout=timeout) as response:
                response_time_ms = (time.time() - start_time) * 1000

                if response.status == 200:
                    status = HealthStatus.HEALTHY
                elif 400 <= response.status < 500:
                    status = HealthStatus.WARNING
                else:
                    status = HealthStatus.CRITICAL

                # Try to parse response body for additional details
                details = {}
                try:
                    if "application/json" in response.headers.get("content-type", ""):
                        details = await response.json()
                except:
                    pass

                result = HealthCheckResult(
                    service_name=service_name,
                    status=status,
                    timestamp=datetime.now(),
                    response_time_ms=response_time_ms,
                    details=details,
                )

                # Store in history
                if service_name not in self.health_history:
                    self.health_history[service_name] = []

                self.health_history[service_name].append(result)

                # Keep only last 50 results
                if len(self.health_history[service_name]) > 50:
                    self.health_history[service_name] = self.health_history[service_name][-50:]

                return result

        except TimeoutError:
            response_time_ms = timeout * 1000
            return HealthCheckResult(
                service_name=service_name,
                status=HealthStatus.CRITICAL,
                timestamp=datetime.now(),
                response_time_ms=response_time_ms,
                error="Request timed out",
            )
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                service_name=service_name,
                status=HealthStatus.CRITICAL,
                timestamp=datetime.now(),
                response_time_ms=response_time_ms,
                error=str(e),
            )

    async def check_process_health(self, service_name: str, pid: int) -> HealthCheckResult:
        """Check process health by PID"""

        start_time = time.time()

        try:
            process = psutil.Process(pid)

            # Check if process is running and responsive
            status = process.status()
            cpu_percent = process.cpu_percent()
            memory_percent = process.memory_percent()

            # Determine health based on process metrics
            if status == psutil.STATUS_RUNNING:
                if cpu_percent < 80 and memory_percent < 90:
                    health_status = HealthStatus.HEALTHY
                elif cpu_percent < 95 and memory_percent < 95:
                    health_status = HealthStatus.WARNING
                else:
                    health_status = HealthStatus.CRITICAL
            else:
                health_status = HealthStatus.CRITICAL

            response_time_ms = (time.time() - start_time) * 1000

            return HealthCheckResult(
                service_name=service_name,
                status=health_status,
                timestamp=datetime.now(),
                response_time_ms=response_time_ms,
                details={
                    "pid": pid,
                    "status": status,
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_percent,
                },
            )

        except psutil.NoSuchProcess:
            return HealthCheckResult(
                service_name=service_name,
                status=HealthStatus.CRITICAL,
                timestamp=datetime.now(),
                response_time_ms=(time.time() - start_time) * 1000,
                error="Process not found",
            )


class ServiceManager:
    """Intelligent service lifecycle management"""

    def __init__(self):
        self.services: dict[str, ServiceConfig] = {}
        self.service_processes: dict[str, asyncio.subprocess.Process] = {}
        self.service_states: dict[str, ServiceState] = {}
        self.restart_counts: dict[str, int] = {}
        self.health_checker = HealthChecker()
        self.process_monitor = ProcessMonitor()
        self.running = False

    async def initialize(self):
        """Initialize service manager"""
        await self.health_checker.initialize()
        self.running = True

        # Start monitoring loop
        asyncio.create_task(self.monitoring_loop())

    async def cleanup(self):
        """Cleanup service manager"""
        self.running = False
        await self.stop_all_services()
        await self.health_checker.cleanup()
        self.process_monitor.cleanup()

    def register_service(self, config: ServiceConfig):
        """Register a service for management"""
        self.services[config.name] = config
        self.service_states[config.name] = ServiceState.STOPPED
        self.restart_counts[config.name] = 0

        logging.info(f"Registered service: {config.name}")

    async def start_service(self, service_name: str) -> bool:
        """Start a specific service"""

        if service_name not in self.services:
            logging.error(f"Service not found: {service_name}")
            return False

        config = self.services[service_name]

        # Check dependencies first
        for dep in config.dependencies:
            if dep not in self.service_states or self.service_states[dep] != ServiceState.RUNNING:
                logging.error(f"Dependency {dep} not running for service {service_name}")
                return False

        self.service_states[service_name] = ServiceState.STARTING

        try:
            # Prepare environment
            env = dict(os.environ)
            env.update(config.environment)

            # Start process
            process = await asyncio.create_subprocess_exec(
                *config.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=str(config.working_directory),
            )

            self.service_processes[service_name] = process
            self.service_states[service_name] = ServiceState.RUNNING

            logging.info(f"Started service: {service_name} (PID: {process.pid})")
            return True

        except Exception as e:
            self.service_states[service_name] = ServiceState.FAILED
            logging.error(f"Failed to start service {service_name}: {e}")
            return False

    async def stop_service(self, service_name: str, graceful: bool = True) -> bool:
        """Stop a specific service"""

        if service_name not in self.service_processes:
            return True

        self.service_states[service_name] = ServiceState.STOPPING

        try:
            process = self.service_processes[service_name]

            if graceful:
                # Try graceful shutdown first
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), timeout=10.0)
                except TimeoutError:
                    # Force kill if graceful shutdown failed
                    process.kill()
                    await process.wait()
            else:
                process.kill()
                await process.wait()

            del self.service_processes[service_name]
            self.service_states[service_name] = ServiceState.STOPPED

            logging.info(f"Stopped service: {service_name}")
            return True

        except Exception as e:
            logging.error(f"Failed to stop service {service_name}: {e}")
            self.service_states[service_name] = ServiceState.FAILED
            return False

    async def restart_service(self, service_name: str) -> bool:
        """Restart a specific service"""

        config = self.services.get(service_name)
        if not config:
            return False

        # Check restart policy
        if config.restart_policy == "never":
            return False

        if config.restart_policy == "on-failure":
            if self.service_states.get(service_name) != ServiceState.FAILED:
                return False

        # Check max restarts
        if self.restart_counts[service_name] >= config.max_restarts:
            logging.error(f"Max restarts exceeded for service: {service_name}")
            return False

        self.restart_counts[service_name] += 1
        self.service_states[service_name] = ServiceState.RECOVERING

        # Stop service
        await self.stop_service(service_name, graceful=True)

        # Wait before restart
        await asyncio.sleep(config.restart_delay)

        # Start service
        success = await self.start_service(service_name)

        if success:
            logging.info(
                f"Restarted service: {service_name} (attempt {self.restart_counts[service_name]})"
            )

        return success

    async def start_all_services(self) -> dict[str, bool]:
        """Start all registered services in dependency order"""

        results = {}

        # Sort services by dependencies (simple topological sort)
        sorted_services = self._sort_services_by_dependencies()

        for service_name in sorted_services:
            results[service_name] = await self.start_service(service_name)

            # Small delay between services
            await asyncio.sleep(1)

        return results

    async def stop_all_services(self) -> dict[str, bool]:
        """Stop all services in reverse dependency order"""

        results = {}

        # Sort services in reverse dependency order
        sorted_services = self._sort_services_by_dependencies()
        sorted_services.reverse()

        for service_name in sorted_services:
            if service_name in self.service_processes:
                results[service_name] = await self.stop_service(service_name)

        return results

    def _sort_services_by_dependencies(self) -> list[str]:
        """Simple topological sort by dependencies"""

        sorted_services = []
        remaining = set(self.services.keys())

        while remaining:
            # Find services with no unresolved dependencies
            ready = []
            for service_name in remaining:
                config = self.services[service_name]
                if all(dep in sorted_services for dep in config.dependencies):
                    ready.append(service_name)

            if not ready:
                # Circular dependency or missing dependency
                ready = list(remaining)  # Add remaining services anyway

            for service_name in ready:
                sorted_services.append(service_name)
                remaining.remove(service_name)

        return sorted_services

    async def monitoring_loop(self):
        """Main monitoring loop for all services"""

        while self.running:
            try:
                # Check health of all running services
                health_tasks = []

                for service_name, process in self.service_processes.items():
                    config = self.services[service_name]

                    # HTTP health check if URL provided
                    if config.health_check_url:
                        task = self.health_checker.check_http_health(
                            service_name,
                            config.health_check_url,
                            config.health_check_timeout,
                        )
                        health_tasks.append(task)

                    # Process health check
                    if process.pid:
                        task = self.health_checker.check_process_health(service_name, process.pid)
                        health_tasks.append(task)

                # Execute health checks
                if health_tasks:
                    health_results = await asyncio.gather(*health_tasks, return_exceptions=True)

                    for result in health_results:
                        if isinstance(result, HealthCheckResult):
                            await self._handle_health_result(result)

                # Check for failed processes and restart if needed
                for service_name in list(self.service_processes.keys()):
                    process = self.service_processes[service_name]

                    if process.returncode is not None:
                        # Process has exited
                        self.service_states[service_name] = ServiceState.FAILED
                        del self.service_processes[service_name]

                        # Attempt restart based on policy
                        config = self.services[service_name]
                        if config.restart_policy in ["always", "on-failure"]:
                            asyncio.create_task(self.restart_service(service_name))

                # Wait before next monitoring cycle
                await asyncio.sleep(10)

            except Exception as e:
                logging.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)

    async def _handle_health_result(self, result: HealthCheckResult):
        """Handle health check result"""

        if result.status == HealthStatus.CRITICAL:
            logging.warning(f"Critical health status for {result.service_name}: {result.error}")

            # Consider restarting service if it's consistently unhealthy
            service_history = self.health_checker.health_history.get(result.service_name, [])

            # Check last 3 health checks
            if len(service_history) >= 3:
                recent_results = service_history[-3:]
                if all(r.status == HealthStatus.CRITICAL for r in recent_results):
                    logging.info(
                        f"Attempting restart of consistently unhealthy service: {result.service_name}"
                    )
                    asyncio.create_task(self.restart_service(result.service_name))

    async def get_service_status(self) -> dict[str, Any]:
        """Get status of all services"""

        status = {
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "system_resources": await self.process_monitor.get_system_resource_usage(),
        }

        for service_name, _config in self.services.items():
            service_status = {
                "name": service_name,
                "state": self.service_states.get(service_name, ServiceState.UNKNOWN).value,
                "restart_count": self.restart_counts.get(service_name, 0),
                "pid": None,
                "health": None,
            }

            # Get process info
            if service_name in self.service_processes:
                process = self.service_processes[service_name]
                service_status["pid"] = process.pid

            # Get latest health check
            health_history = self.health_checker.health_history.get(service_name, [])
            if health_history:
                latest_health = health_history[-1]
                service_status["health"] = {
                    "status": latest_health.status.value,
                    "response_time_ms": latest_health.response_time_ms,
                    "timestamp": latest_health.timestamp.isoformat(),
                    "error": latest_health.error,
                }

            status["services"][service_name] = service_status

        return status


async def main():
    """Demonstrate system orchestration"""

    setup_utf8_logging()
    logging.info("🎭 Starting System Orchestration & Automation")

    # Initialize service manager
    service_manager = ServiceManager()
    await service_manager.initialize()

    try:
        # Register sample services

        # Redis service (if available)
        redis_service = ServiceConfig(
            name="redis",
            command=["redis-server", "--port", "6379"],
            working_directory=Path("/"),
            health_check_url="http://localhost:6379/ping",
            health_check_interval=30.0,
            restart_policy="always",
            max_restarts=5,
        )
        service_manager.register_service(redis_service)

        # Web server service
        web_service = ServiceConfig(
            name="web_server",
            command=["python", "-m", "http.server", "8000"],
            working_directory=Path("C:/EQ12"),
            dependencies=["redis"],
            health_check_url="http://localhost:8000",
            health_check_interval=15.0,
            restart_policy="always",
        )
        service_manager.register_service(web_service)

        print("✅ Services registered:")
        for name in service_manager.services:
            print(f"   - {name}")

        # Start all services
        print("\n🚀 Starting services...")
        start_results = await service_manager.start_all_services()

        for service, success in start_results.items():
            status = "✅" if success else "❌"
            print(f"   {status} {service}")

        # Monitor for a short time
        print("\n📊 Monitoring services...")

        for i in range(3):
            await asyncio.sleep(5)
            status = await service_manager.get_service_status()

            print(f"\n--- Status Update {i + 1} ---")
            for service_name, service_info in status["services"].items():
                state = service_info["state"]
                pid = service_info["pid"]
                health = service_info["health"]["status"] if service_info["health"] else "unknown"
                print(f"{service_name}: {state} (PID: {pid}) [{health}]")

        print("\n🎉 System Orchestration Complete!")

    finally:
        # Cleanup
        await service_manager.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
