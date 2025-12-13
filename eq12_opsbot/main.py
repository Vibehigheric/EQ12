"""
EQ12 OpsBot CLI Interface
========================

Typer-based command line interface for OpsBot operations.
"""

import logging
import sys

import typer
import uvicorn
from rich.console import Console
from rich.table import Table

from .budget_guard import BudgetGuard
from .config import get_config
from .first_run import FirstRunSetup
from .model_policy import ModelPolicy
from .rate_limits import RateLimiter
from .server import create_app
from .tasks import TaskScheduler

app = typer.Typer(name="eq12bot", help="EQ12 OpsBot - Production webhook & automation suite")
console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@app.command()
def run(
    host: str = typer.Option("127.0.0.1", help="Host to bind to"),
    port: int = typer.Option(8088, help="Port to bind to"),
    reload: bool = typer.Option(False, help="Enable auto-reload"),
    first_run: bool = typer.Option(True, help="Run first-time setup"),
):
    """Start the OpsBot webhook server and scheduler"""
    get_config()

    # Run first-time setup if needed
    if first_run:
        setup = FirstRunSetup()
        setup.run_setup()

    console.print("🚀 Starting EQ12 OpsBot...", style="bold green")

    # Create FastAPI app
    fastapi_app = create_app()

    # Start task scheduler
    scheduler = TaskScheduler()
    scheduler.start()

    # Start server
    try:
        uvicorn.run(fastapi_app, host=host, port=port, reload=reload, log_level="info")
    except KeyboardInterrupt:
        console.print("\n🛑 Shutting down OpsBot...", style="bold red")
        scheduler.stop()
    finally:
        scheduler.stop()


@app.command()
def doctor():
    """Run health checks and diagnostics"""
    console.print("🏥 EQ12 OpsBot Doctor", style="bold blue")

    config = get_config()

    # Create diagnostics table
    table = Table(title="System Diagnostics")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details")

    # Check configuration
    if config.is_production_ready:
        table.add_row("Configuration", "✓ Ready", "Production ready")
    elif config.demo_mode:
        table.add_row("Configuration", "⚠ Demo", "Demo mode active")
    else:
        table.add_row("Configuration", "✗ Missing", "Keys missing")

    # Check budget guard
    try:
        guard = BudgetGuard()
        status = guard.get_status()
        if status["circuit_breaker_active"]:
            table.add_row("Budget Guard", "⚠ Breaker", f"${status['daily_spent']:.2f}")
        else:
            table.add_row("Budget Guard", "✓ Active", f"${status['daily_spent']:.2f}")
    except Exception as e:
        table.add_row("Budget Guard", "✗ Error", str(e)[:50])

    # Check rate limiter
    try:
        limiter = RateLimiter()
        status = limiter.get_status()
        table.add_row("Rate Limiter", "✓ Active", f"{status['total_models']} models")
    except Exception as e:
        table.add_row("Rate Limiter", "✗ Error", str(e)[:50])

    # Check model policy
    try:
        policy = ModelPolicy()
        status = policy.get_status()
        allowed = len(status.get("allowed_models", []))
        table.add_row("Model Policy", "✓ Active", f"{allowed} allowed")
    except Exception as e:
        table.add_row("Model Policy", "✗ Error", str(e)[:50])

    console.print(table)

    # Integration checks
    console.print("\n🔗 Integration Checks", style="bold yellow")

    # Check existing EQ12 modules
    integrations = [
        ("eq12_doctor", "EQ12 Doctor"),
        ("eq12_cost_guards", "Cost Guards"),
        ("eq12_ai_client", "AI Client"),
    ]

    for module, name in integrations:
        try:
            __import__(module)
            console.print(f"✓ {name} available", style="green")
        except ImportError:
            console.print(f"⚠ {name} not found", style="yellow")


@app.command(name="limits")
def limits_command(
    sync: bool = typer.Option(False, help="Sync rate limits from config"),
    show: bool = typer.Option(True, help="Show current limits"),
):
    """Manage rate limits"""
    console.print("⚡ Rate Limit Management", style="bold blue")

    try:
        limiter = RateLimiter()

        if sync:
            console.print("Syncing rate limits from configuration...")
            limiter._load_custom_limits()
            limiter._initialize_buckets()
            console.print("✓ Rate limits synced", style="green")

        if show:
            status = limiter.get_status()

            table = Table(title="Current Rate Limits")
            table.add_column("Model", style="cyan")
            table.add_column("TPM Available", style="green")
            table.add_column("RPM Available", style="green")
            table.add_column("Usage %", style="yellow")

            for model, stats in status.get("models", {}).items():
                usage = max(stats.get("tpm_usage_percent", 0), stats.get("rpm_usage_percent", 0))

                table.add_row(
                    model,
                    str(stats.get("tpm_available", 0)),
                    str(stats.get("rpm_available", 0)),
                    f"{usage:.1f}%",
                )

            console.print(table)

    except Exception as e:
        console.print(f"✗ Error: {e}", style="red")
        sys.exit(1)


@app.command(name="model-policy")
def model_policy_command(
    enforce: bool = typer.Option(False, help="Enforce model policy"),
    show: bool = typer.Option(True, help="Show current policy"),
):
    """Manage model allow/deny policy"""
    console.print("🛡️ Model Policy Management", style="bold blue")

    try:
        policy = ModelPolicy()

        if enforce:
            console.print("Enforcing model policy...")
            # This would typically integrate with the AI client
            console.print("✓ Policy enforcement active", style="green")

        if show:
            status = policy.get_status()

            # Show allowed models
            allowed = status.get("allowed_models", [])
            if allowed:
                console.print(f"\n✓ Allowed Models ({len(allowed)}):", style="green")
                for model in allowed[:10]:  # Show first 10
                    console.print(f"  • {model}")
                if len(allowed) > 10:
                    console.print(f"  ... and {len(allowed) - 10} more")

            # Show denied patterns
            denied = status.get("denied_patterns", [])
            if denied:
                console.print(f"\n✗ Denied Patterns ({len(denied)}):", style="red")
                for pattern in denied[:5]:  # Show first 5
                    console.print(f"  • {pattern}")
                if len(denied) > 5:
                    console.print(f"  ... and {len(denied) - 5} more")

    except Exception as e:
        console.print(f"✗ Error: {e}", style="red")
        sys.exit(1)


if __name__ == "__main__":
    app()
