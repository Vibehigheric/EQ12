"""
EQ12 Webhook Configuration and Testing
Sets up webhook environment, starts server, and tests event flow
"""

import json
import logging
import os
import secrets
import subprocess
import sys
import time
from pathlib import Path

logger = logging.getLogger(__name__)


class WebhookManager:
    """Manages EQ12 webhook configuration, startup, and testing"""

    def __init__(self):
        self.eq12_root = Path("C:/EQ12")
        self.webhook_port = 8000
        self.webhook_url = f"http://127.0.0.1:{self.webhook_port}/webhooks/openai"

    def generate_webhook_secret(self) -> str:
        """Generate secure random webhook secret"""
        return secrets.token_urlsafe(32)

    def setup_environment(self):
        """Set up webhook environment variables"""
        print("🔧 Setting up webhook environment...")

        # Generate or use existing webhook secret
        webhook_secret = os.getenv("EQ12_WEBHOOK_SECRET")
        if not webhook_secret or webhook_secret == "change-me-in-production":
            webhook_secret = self.generate_webhook_secret()
            print(f"🔑 Generated new webhook secret: {webhook_secret[:16]}...")
        else:
            print(f"🔑 Using existing webhook secret: {webhook_secret[:16]}...")

        # Set environment variables for current session
        os.environ["EQ12_WEBHOOK_SECRET"] = webhook_secret
        os.environ["EQ12_WEBHOOK_URL"] = self.webhook_url

        # Create PowerShell script to set persistent environment variables
        ps_script = f"""
# Set EQ12 webhook environment variables persistently
[System.Environment]::SetEnvironmentVariable("EQ12_WEBHOOK_SECRET", "{webhook_secret}", "User")
[System.Environment]::SetEnvironmentVariable("EQ12_WEBHOOK_URL", "{self.webhook_url}", "User")

Write-Host "✅ Webhook environment variables set persistently"
Write-Host "🔑 EQ12_WEBHOOK_SECRET: {webhook_secret[:16]}..."
Write-Host "🌐 EQ12_WEBHOOK_URL: {self.webhook_url}"
"""

        # Write and execute PowerShell script
        ps_file = self.eq12_root / "set_webhook_env.ps1"
        with open(ps_file, "w") as f:
            f.write(ps_script)

        try:
            subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(ps_file)],
                check=True,
                capture_output=True,
            )
            print("✅ Environment variables set persistently")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Could not set persistent env vars: {e}")

        # Clean up PowerShell script
        ps_file.unlink(missing_ok=True)

        return webhook_secret

    def install_dependencies(self):
        """Install required dependencies for webhook server"""
        print("📦 Installing webhook dependencies...")

        required_packages = ["fastapi", "uvicorn[standard]", "httpx"]

        for package in required_packages:
            try:
                __import__(package.split("[")[0])  # Remove [standard] for import test
                print(f"✅ {package} already installed")
            except ImportError:
                print(f"📦 Installing {package}...")
                try:
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", package],
                        check=True,
                        capture_output=True,
                    )
                    print(f"✅ {package} installed successfully")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed to install {package}: {e}")
                    return False

        return True

    def start_webhook_server(self) -> subprocess.Popen:
        """Start the webhook server in background"""
        print(f"🚀 Starting webhook server on port {self.webhook_port}...")

        try:
            # Start uvicorn server
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "eq12_webhooks:app",
                    "--host",
                    "0.0.0.0",
                    "--port",
                    str(self.webhook_port),
                    "--log-level",
                    "info",
                ],
                cwd=str(self.eq12_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Wait a moment for server to start
            time.sleep(3)

            # Check if server is running
            if process.poll() is None:
                print(f"✅ Webhook server started (PID: {process.pid})")
                return process
            else:
                stdout, stderr = process.communicate()
                print("❌ Webhook server failed to start:")
                print(f"STDOUT: {stdout.decode()}")
                print(f"STDERR: {stderr.decode()}")
                return None

        except Exception as e:
            print(f"❌ Failed to start webhook server: {e}")
            return None

    def test_webhook_health(self) -> bool:
        """Test webhook server health endpoint"""
        print("🩺 Testing webhook server health...")

        try:
            import httpx

            health_url = f"http://127.0.0.1:{self.webhook_port}/webhooks/health"
            response = httpx.get(health_url, timeout=5.0)

            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Webhook server healthy: {health_data['status']}")
                print(f"📊 Events seen: {health_data['events_seen']}")
                return True
            else:
                print(f"❌ Webhook health check failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Webhook health check error: {e}")
            return False

    def test_ai_webhook_integration(self) -> bool:
        """Test AI client webhook integration"""
        print("🤖 Testing AI client webhook integration...")

        try:
            # Import and test AI client
            sys.path.insert(0, str(self.eq12_root))
            from eq12_ai_client import EQ12AIClient

            client = EQ12AIClient()

            # Make a small test request
            response = client.ask(
                prompt="Test webhook integration - respond with 'OK'",
                feature="webhook_test",
                model="gpt-4o-mini",
                max_tokens=10,
            )

            print(f"✅ AI request successful: {response[:50]}...")

            # Wait for webhook processing
            time.sleep(2)

            # Check webhook logs
            logs_dir = Path("C:/EQ12/logs/webhooks")
            if logs_dir.exists():
                event_files = list(logs_dir.glob("events_*.jsonl"))
                if event_files:
                    latest_file = max(event_files, key=lambda f: f.stat().st_mtime)
                    with open(latest_file) as f:
                        lines = f.readlines()

                    recent_events = [json.loads(line) for line in lines[-5:]]
                    webhook_events = [e for e in recent_events if e.get("source") == "openai"]

                    if webhook_events:
                        print(f"✅ Found {len(webhook_events)} webhook events in logs")
                        return True
                    else:
                        print("⚠️  No webhook events found in recent logs")
                        return False
                else:
                    print("⚠️  No webhook event files found")
                    return False
            else:
                print("⚠️  Webhook logs directory not found")
                return False

        except Exception as e:
            print(f"❌ AI webhook test failed: {e}")
            return False

    def show_webhook_stats(self):
        """Display webhook statistics"""
        print("📊 WEBHOOK STATISTICS")
        print("=" * 50)

        try:
            import httpx

            stats_url = f"http://127.0.0.1:{self.webhook_port}/webhooks/stats"
            response = httpx.get(stats_url, timeout=5.0)

            if response.status_code == 200:
                stats = response.json()
                print(f"Events processed: {stats['events_processed']}")
                print(f"Log directory: {stats['log_directory']}")
                print()

                if stats.get("log_files"):
                    print("Log files:")
                    for log_file in stats["log_files"]:
                        size_mb = log_file["size_bytes"] / 1024 / 1024
                        print(f"  📄 {log_file['name']}: {size_mb:.2f} MB")
                else:
                    print("No log files found")
            else:
                print(f"Failed to get stats: {response.status_code}")

        except Exception as e:
            print(f"Failed to get webhook stats: {e}")


def main():
    """Main webhook setup and testing workflow"""
    print("🎯 EQ12 WEBHOOK SETUP & TESTING")
    print("=" * 60)

    manager = WebhookManager()

    # Step 1: Install dependencies
    if not manager.install_dependencies():
        print("❌ Failed to install dependencies")
        return False

    # Step 2: Setup environment
    secret = manager.setup_environment()

    # Step 3: Start webhook server
    server_process = manager.start_webhook_server()
    if not server_process:
        print("❌ Failed to start webhook server")
        return False

    try:
        # Step 4: Test server health
        if not manager.test_webhook_health():
            print("❌ Webhook server health check failed")
            return False

        # Step 5: Test AI integration
        if not manager.test_ai_webhook_integration():
            print("⚠️  AI webhook integration test had issues")

        # Step 6: Show statistics
        manager.show_webhook_stats()

        print()
        print("🎉 WEBHOOK SYSTEM SETUP COMPLETE!")
        print("=" * 60)
        print(f"🌐 Webhook URL: {manager.webhook_url}")
        print(f"🔑 Secret: {secret[:16]}...")
        print("📁 Logs: C:/EQ12/logs/webhooks/")
        print()
        print("Next steps:")
        print("1. Keep webhook server running for event processing")
        print("2. Monitor webhook logs for event activity")
        print("3. Check dashboard for AI usage updates")
        print()
        print("Commands:")
        print("  Health: curl http://127.0.0.1:8000/webhooks/health")
        print("  Stats:  curl http://127.0.0.1:8000/webhooks/stats")
        print("  Logs:   ls C:/EQ12/logs/webhooks/")

        # Keep server running
        print("Press Ctrl+C to stop webhook server...")
        try:
            server_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping webhook server...")
            server_process.terminate()

        return True

    except KeyboardInterrupt:
        print("\n🛑 Setup interrupted")
        if server_process:
            server_process.terminate()
        return False

    except Exception as e:
        print(f"❌ Setup failed: {e}")
        if server_process:
            server_process.terminate()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
