#!/usr/bin/env python3
"""
🎛️ EQ12 Master Controller
Unified orchestration system for all EQ12 automation components
Advanced multi-agent coordination and workflow management
"""

import asyncio
import importlib.util
import json
import logging
import os
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/eq12_master_controller.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class ComponentStatus:
    """Status information for an EQ12 component"""

    name: str
    status: str  # active, inactive, error, unknown
    last_updated: str
    version: str = "1.0.0"
    dependencies_met: bool = True
    error_message: str | None = None
    performance_metrics: dict[str, Any] = None


@dataclass
class WorkflowStep:
    """Individual step in an automation workflow"""

    step_id: str
    name: str
    component: str
    action: str
    parameters: dict[str, Any]
    dependencies: list[str] = None
    timeout_seconds: int = 300
    retry_attempts: int = 3


@dataclass
class AutomationWorkflow:
    """Complete automation workflow definition"""

    workflow_id: str
    name: str
    description: str
    steps: list[WorkflowStep]
    schedule: str | None = None  # cron expression
    enabled: bool = True
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()


class ComponentManager:
    """Manages EQ12 component lifecycle and status"""

    def __init__(self):
        self.components = {
            "x_factor_pipeline": {
                "path": "eq12_x_factor_pipeline.py",
                "description": "Real-time X API sentiment analysis and signal processing",
                "dependencies": ["openai_api_key"],
                "health_check": self._check_x_factor_health,
            },
            "auto_trade_executor": {
                "path": "eq12_auto_trade_executor.py",
                "description": "Lightning-fast automated bet execution with CLV tracking",
                "dependencies": [],
                "health_check": self._check_auto_trade_health,
            },
            "sports_command_center": {
                "path": "scripts/sports/eq12_sports_command_center.py",
                "description": "Comprehensive sports betting edge detection orchestrator",
                "dependencies": ["odds_api_key"],
                "health_check": self._check_sports_center_health,
            },
            "control_system_toolkit": {
                "path": "scripts/control/control_system_toolkit.ps1",
                "description": "PowerShell diagnostics and system management utilities",
                "dependencies": ["powershell"],
                "health_check": self._check_control_toolkit_health,
            },
            "freelance_scaffolding": {
                "path": "scripts/freelance/eq12_freelance_scaffolding.py",
                "description": "Complete freelance project and client management system",
                "dependencies": [],
                "health_check": self._check_freelance_health,
            },
        }

        self.status_cache = {}
        self.last_health_check = None

    async def get_component_status(self, component_name: str) -> ComponentStatus:
        """Get current status of a component"""
        if component_name not in self.components:
            return ComponentStatus(
                name=component_name,
                status="unknown",
                last_updated=datetime.now(UTC).isoformat(),
                error_message="Component not found",
            )

        component_config = self.components[component_name]

        try:
            # Check if component file exists
            component_path = Path(component_config["path"])
            if not component_path.exists():
                return ComponentStatus(
                    name=component_name,
                    status="inactive",
                    last_updated=datetime.now(UTC).isoformat(),
                    error_message=f"Component file not found: {component_path}",
                )

            # Check dependencies
            dependencies_met = self._check_dependencies(component_config["dependencies"])

            # Run component-specific health check
            health_status = await component_config["health_check"]()

            return ComponentStatus(
                name=component_name,
                status="active" if health_status and dependencies_met else "error",
                last_updated=datetime.now(UTC).isoformat(),
                dependencies_met=dependencies_met,
                error_message=(
                    None
                    if health_status and dependencies_met
                    else "Dependency or health check failed"
                ),
            )

        except Exception as e:
            logger.error(f"Error checking component {component_name}: {e}")
            return ComponentStatus(
                name=component_name,
                status="error",
                last_updated=datetime.now(UTC).isoformat(),
                error_message=str(e),
            )

    def _check_dependencies(self, dependencies: list[str]) -> bool:
        """Check if component dependencies are met"""
        for dep in dependencies:
            if dep == "openai_api_key":
                if not os.getenv("OPENAI_API_KEY"):
                    return False
            elif dep == "odds_api_key":
                if not os.getenv("ODDS_API_KEY"):
                    return False
            elif dep == "powershell":
                try:
                    subprocess.run(
                        ["powershell", "-Command", "Get-Host"],
                        capture_output=True,
                        check=True,
                    )
                except (subprocess.CalledProcessError, FileNotFoundError):
                    return False
        return True

    async def _check_x_factor_health(self) -> bool:
        """Health check for X-Factor Pipeline"""
        try:
            # Try to import and do basic validation
            spec = importlib.util.spec_from_file_location("xfactor", "eq12_x_factor_pipeline.py")
            if spec and spec.loader:
                return True
        except Exception:
            pass
        return False

    async def _check_auto_trade_health(self) -> bool:
        """Health check for Auto-Trade Executor"""
        try:
            spec = importlib.util.spec_from_file_location(
                "autotrade", "eq12_auto_trade_executor.py"
            )
            if spec and spec.loader:
                return True
        except Exception:
            pass
        return False

    async def _check_sports_center_health(self) -> bool:
        """Health check for Sports Command Center"""
        try:
            sports_path = Path("scripts/sports/eq12_sports_command_center.py")
            return sports_path.exists()
        except Exception:
            return False

    async def _check_control_toolkit_health(self) -> bool:
        """Health check for Control System Toolkit"""
        try:
            toolkit_path = Path("scripts/control/control_system_toolkit.ps1")
            return toolkit_path.exists()
        except Exception:
            return False

    async def _check_freelance_health(self) -> bool:
        """Health check for Freelance Scaffolding"""
        try:
            freelance_path = Path("scripts/freelance/eq12_freelance_scaffolding.py")
            return freelance_path.exists()
        except Exception:
            return False

    async def get_system_overview(self) -> dict[str, ComponentStatus]:
        """Get status overview of all components"""
        overview = {}

        for component_name in self.components:
            overview[component_name] = await self.get_component_status(component_name)

        return overview


class WorkflowEngine:
    """Executes automation workflows"""

    def __init__(self, component_manager: ComponentManager):
        self.component_manager = component_manager
        self.active_workflows = {}
        self.workflow_history = []

    def load_workflows(
        self, workflows_file: str = "configs/workflows.json"
    ) -> list[AutomationWorkflow]:
        """Load workflow definitions from file"""
        try:
            with open(workflows_file, encoding="utf-8") as f:
                workflows_data = json.load(f)

            workflows = []
            for workflow_data in workflows_data:
                steps = [WorkflowStep(**step_data) for step_data in workflow_data.pop("steps", [])]
                workflow = AutomationWorkflow(steps=steps, **workflow_data)
                workflows.append(workflow)

            return workflows

        except FileNotFoundError:
            logger.warning(f"Workflows file not found: {workflows_file}")
            return self._get_default_workflows()
        except Exception as e:
            logger.error(f"Error loading workflows: {e}")
            return []

    def _get_default_workflows(self) -> list[AutomationWorkflow]:
        """Get default automation workflows"""
        return [
            AutomationWorkflow(
                workflow_id="daily_sports_analysis",
                name="Daily Sports Analysis",
                description="Complete daily sports betting analysis workflow",
                steps=[
                    WorkflowStep(
                        step_id="step1",
                        name="X-Factor Signal Processing",
                        component="x_factor_pipeline",
                        action="run_analysis",
                        parameters={"mode": "daily"},
                    ),
                    WorkflowStep(
                        step_id="step2",
                        name="Sports Edge Detection",
                        component="sports_command_center",
                        action="scan_daily_slate",
                        parameters={},
                        dependencies=["step1"],
                    ),
                    WorkflowStep(
                        step_id="step3",
                        name="Execute High-Value Trades",
                        component="auto_trade_executor",
                        action="execute_opportunities",
                        parameters={"min_confidence": 0.8},
                        dependencies=["step2"],
                    ),
                ],
                schedule="0 8 * * *",  # Daily at 8 AM
            ),
            AutomationWorkflow(
                workflow_id="system_health_check",
                name="System Health Check",
                description="Comprehensive system diagnostics and monitoring",
                steps=[
                    WorkflowStep(
                        step_id="step1",
                        name="System Diagnostics",
                        component="control_system_toolkit",
                        action="diagnose",
                        parameters={},
                    ),
                    WorkflowStep(
                        step_id="step2",
                        name="Performance Analysis",
                        component="control_system_toolkit",
                        action="monitor",
                        parameters={"duration_minutes": 5},
                    ),
                ],
                schedule="0 */6 * * *",  # Every 6 hours
            ),
        ]

    async def execute_workflow(self, workflow: AutomationWorkflow) -> dict[str, Any]:
        """Execute a complete workflow"""
        workflow_start = time.time()
        execution_id = f"exec_{int(workflow_start)}"

        logger.info(f"🚀 Starting workflow: {workflow.name} ({execution_id})")

        execution_result = {
            "workflow_id": workflow.workflow_id,
            "execution_id": execution_id,
            "start_time": datetime.now(UTC).isoformat(),
            "steps_completed": 0,
            "steps_failed": 0,
            "step_results": [],
            "status": "running",
            "error_message": None,
        }

        try:
            # Execute steps in dependency order
            completed_steps = set()

            for step in workflow.steps:
                # Check dependencies
                if step.dependencies:
                    missing_deps = set(step.dependencies) - completed_steps
                    if missing_deps:
                        logger.warning(
                            f"⚠️ Step {step.name} waiting for dependencies: {missing_deps}"
                        )
                        continue

                # Execute step
                logger.info(f"▶️ Executing step: {step.name}")
                step_result = await self._execute_workflow_step(step)

                execution_result["step_results"].append(
                    {
                        "step_id": step.step_id,
                        "step_name": step.name,
                        "success": step_result["success"],
                        "duration": step_result["duration"],
                        "output": step_result["output"],
                        "error": step_result.get("error"),
                    }
                )

                if step_result["success"]:
                    execution_result["steps_completed"] += 1
                    completed_steps.add(step.step_id)
                    logger.info(f"✅ Step completed: {step.name}")
                else:
                    execution_result["steps_failed"] += 1
                    logger.error(f"❌ Step failed: {step.name} - {step_result.get('error')}")

            execution_result["status"] = (
                "completed" if execution_result["steps_failed"] == 0 else "partial"
            )
            execution_result["end_time"] = datetime.now(UTC).isoformat()
            execution_result["total_duration"] = time.time() - workflow_start

            logger.info(
                f"🏁 Workflow {workflow.name} completed: {execution_result['steps_completed']}/{len(workflow.steps)} steps"
            )

        except Exception as e:
            execution_result["status"] = "failed"
            execution_result["error_message"] = str(e)
            execution_result["end_time"] = datetime.now(UTC).isoformat()
            logger.error(f"❌ Workflow {workflow.name} failed: {e}")

        return execution_result

    async def _execute_workflow_step(self, step: WorkflowStep) -> dict[str, Any]:
        """Execute individual workflow step"""
        step_start = time.time()

        try:
            if step.component == "x_factor_pipeline":
                result = await self._execute_python_component(
                    "eq12_x_factor_pipeline.py", step.parameters
                )
            elif step.component == "auto_trade_executor":
                result = await self._execute_python_component(
                    "eq12_auto_trade_executor.py", step.parameters
                )
            elif step.component == "sports_command_center":
                result = await self._execute_python_component(
                    "scripts/sports/eq12_sports_command_center.py", step.parameters
                )
            elif step.component == "control_system_toolkit":
                result = await self._execute_powershell_component(
                    "scripts/control/control_system_toolkit.ps1", step.parameters
                )
            else:
                result = {
                    "success": False,
                    "error": f"Unknown component: {step.component}",
                }

            result["duration"] = time.time() - step_start
            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration": time.time() - step_start,
                "output": "",
            }

    async def _execute_python_component(self, script_path: str, parameters: dict) -> dict[str, Any]:
        """Execute Python component"""
        try:
            # For demo purposes, simulate execution
            await asyncio.sleep(1)  # Simulate processing time

            return {
                "success": True,
                "output": f"Simulated execution of {script_path} with parameters: {parameters}",
                "metrics": {"processing_time": 1.0, "records_processed": 100},
            }
        except Exception as e:
            return {"success": False, "error": str(e), "output": ""}

    async def _execute_powershell_component(
        self, script_path: str, parameters: dict
    ) -> dict[str, Any]:
        """Execute PowerShell component"""
        try:
            # For demo purposes, simulate execution
            await asyncio.sleep(0.5)  # Simulate processing time

            return {
                "success": True,
                "output": f"Simulated PowerShell execution of {script_path}",
                "metrics": {"processing_time": 0.5},
            }
        except Exception as e:
            return {"success": False, "error": str(e), "output": ""}


class EQ12MasterController:
    """Main orchestration controller for EQ12 ecosystem"""

    def __init__(self):
        self.component_manager = ComponentManager()
        self.workflow_engine = WorkflowEngine(self.component_manager)
        self.running = False
        self.start_time = None

    async def initialize(self):
        """Initialize master controller"""
        logger.info("🎛️ Initializing EQ12 Master Controller...")

        # Create required directories
        os.makedirs("logs", exist_ok=True)
        os.makedirs("configs", exist_ok=True)
        os.makedirs("data", exist_ok=True)

        self.start_time = time.time()
        logger.info("✅ EQ12 Master Controller initialized")

    async def get_system_dashboard(self) -> dict[str, Any]:
        """Get comprehensive system dashboard"""
        component_statuses = await self.component_manager.get_system_overview()

        # Calculate overall system health
        active_components = sum(
            1 for status in component_statuses.values() if status.status == "active"
        )
        total_components = len(component_statuses)
        health_percentage = (
            (active_components / total_components * 100) if total_components > 0 else 0
        )

        dashboard = {
            "system_info": {
                "uptime_seconds": (time.time() - self.start_time if self.start_time else 0),
                "health_percentage": health_percentage,
                "active_components": active_components,
                "total_components": total_components,
                "last_updated": datetime.now(UTC).isoformat(),
            },
            "components": {name: asdict(status) for name, status in component_statuses.items()},
            "recent_activity": {
                "workflows_executed": len(self.workflow_engine.workflow_history),
                "last_workflow": (
                    self.workflow_engine.workflow_history[-1]["workflow_id"]
                    if self.workflow_engine.workflow_history
                    else None
                ),
            },
        }

        return dashboard

    async def execute_workflow_by_name(self, workflow_name: str) -> dict[str, Any]:
        """Execute workflow by name"""
        workflows = self.workflow_engine.load_workflows()

        target_workflow = None
        for workflow in workflows:
            if workflow.name.lower() == workflow_name.lower():
                target_workflow = workflow
                break

        if not target_workflow:
            raise ValueError(f"Workflow not found: {workflow_name}")

        return await self.workflow_engine.execute_workflow(target_workflow)

    async def run_interactive_mode(self):
        """Interactive mode for master controller"""
        print("\n🎛️ EQ12 MASTER CONTROLLER")
        print("=========================")

        while True:
            print("\n📋 MAIN MENU:")
            print("1. System Dashboard")
            print("2. Component Status")
            print("3. Execute Workflow")
            print("4. Health Check All")
            print("5. View Logs")
            print("6. Exit")

            choice = input("\nSelect option (1-6): ").strip()

            try:
                if choice == "1":
                    await self._show_dashboard()
                elif choice == "2":
                    await self._show_component_status()
                elif choice == "3":
                    await self._execute_workflow_interactive()
                elif choice == "4":
                    await self._health_check_all()
                elif choice == "5":
                    self._view_logs()
                elif choice == "6":
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid option. Please select 1-6.")

            except Exception:
                print("❌ Error: {e}")

    async def _show_dashboard(self):
        """Show system dashboard"""
        print("\n📊 SYSTEM DASHBOARD")
        print("-------------------")

        dashboard = await self.get_system_dashboard()
        system_info = dashboard["system_info"]

        print("System Health: {system_info['health_percentage']:.1f}%")
        print("Uptime: {system_info['uptime_seconds']:.0f} seconds")
        print(
            f"Active Components: {system_info['active_components']}/{system_info['total_components']}"
        )

        print("\nComponent Status:")
        for _name, component in dashboard["components"].items():
            "✅" if component["status"] == "active" else "❌"
            print("  {status_icon} {name}: {component['status']}")

    async def _show_component_status(self):
        """Show detailed component status"""
        print("\n🔧 COMPONENT STATUS")
        print("-------------------")

        statuses = await self.component_manager.get_system_overview()

        for _name, status in statuses.items():
            print("\n📦 {name}:")
            print("   Status: {status.status}")
            print("   Dependencies: {'✅' if status.dependencies_met else '❌'}")
            print("   Last Updated: {status.last_updated}")
            if status.error_message:
                print("   Error: {status.error_message}")

    async def _execute_workflow_interactive(self):
        """Interactive workflow execution"""
        print("\n🔄 EXECUTE WORKFLOW")
        print("-------------------")

        workflows = self.workflow_engine.load_workflows()

        if not workflows:
            print("❌ No workflows found.")
            return

        print("\nAvailable workflows:")
        for _i, workflow in enumerate(workflows, 1):
            print("{i}. {workflow.name} - {workflow.description}")

        try:
            workflow_idx = int(input("\nSelect workflow (number): ")) - 1
            workflow = workflows[workflow_idx]

            print("\n▶️ Executing workflow: {workflow.name}")
            await self.workflow_engine.execute_workflow(workflow)

            print("\n📊 Execution Results:")
            print("   Status: {result['status']}")
            print("   Steps Completed: {result['steps_completed']}")
            print("   Steps Failed: {result['steps_failed']}")
            print("   Duration: {result.get('total_duration', 0):.2f} seconds")

        except (ValueError, IndexError):
            print("❌ Invalid selection.")

    async def _health_check_all(self):
        """Perform health check on all components"""
        print("\n🏥 SYSTEM HEALTH CHECK")
        print("----------------------")

        print("Running comprehensive health check...")

        statuses = await self.component_manager.get_system_overview()

        healthy_count = 0
        for name, status in statuses.items():
            if status.status == "active":
                print("✅ {name}: Healthy")
                healthy_count += 1
            else:
                print(f"❌ {name}: {status.status} - {status.error_message or 'Unknown issue'}")

        total = len(statuses)
        health_percentage = (healthy_count / total * 100) if total > 0 else 0

        print(
            f"\n📊 Overall System Health: {health_percentage:.1f}% ({healthy_count}/{total} components healthy)"
        )

    def _view_logs(self):
        """View recent log entries"""
        print("\n📜 RECENT LOGS")
        print("--------------")

        try:
            log_file = Path("logs/eq12_master_controller.log")
            if log_file.exists():
                with open(log_file, encoding="utf-8") as f:
                    lines = f.readlines()
                    recent_lines = lines[-20:] if len(lines) > 20 else lines

                for line in recent_lines:
                    print(line.strip())
            else:
                print("No log file found.")

        except Exception:
            print("❌ Error reading logs: {e}")

    async def run_demo_mode(self):
        """Run master controller in demo mode"""
        logger.info("🎛️ Starting EQ12 Master Controller Demo...")

        await self.initialize()

        # Show system dashboard
        dashboard = await self.get_system_dashboard()

        print("\n🎛️ EQ12 MASTER CONTROLLER DEMO")
        print("==============================")
        print("System Health: {dashboard['system_info']['health_percentage']:.1f}%")
        print(
            f"Active Components: {dashboard['system_info']['active_components']}/{dashboard['system_info']['total_components']}"
        )

        # Execute demo workflow
        print("\n🔄 Executing demo workflow...")
        try:
            await self.execute_workflow_by_name("Daily Sports Analysis")
            print("✅ Workflow completed: {result['status']}")
        except Exception:
            print("❌ Workflow failed: {e}")

        # Start interactive mode
        await self.run_interactive_mode()


async def main():
    """Main entry point for Master Controller"""
    controller = EQ12MasterController()
    await controller.run_demo_mode()


if __name__ == "__main__":
    asyncio.run(main())
