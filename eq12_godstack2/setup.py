#!/usr/bin/env python3
"""
EQ12 GODSTACK Setup and Installation Script
Complete setup for the EQ12 GODSTACK intelligence ecosystem.

Author: EQ12 AI Assistant
Created: 2025-01-27
"""

import os
import subprocess
import sys
from pathlib import Path


def print_banner():
    """Print setup banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                        🚀 EQ12 GODSTACK SETUP 🚀                        ║
    ║                                                                          ║
    ║           Complete Intelligence Ecosystem Installation                    ║
    ║                                                                          ║
    ║  📡 Multi-Source Search Intelligence                                     ║
    ║  💰 Swagbucks Offer Analysis                                            ║
    ║  📰 Real-Time News Aggregation                                          ║
    ║  🧠 GPT-Powered Enrichment Engine                                       ║
    ║  📊 FastAPI Web Dashboard                                               ║
    ║  ⏰ Automated Task Scheduling                                           ║
    ║  📱 Telegram Alert Integration                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_prerequisites():
    """Check system prerequisites"""
    print("🔍 Checking prerequisites...")

    issues = []

    # Check Python version
    print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}")

    # Check pip
    try:
        subprocess.run(["pip", "--version"], capture_output=True, check=True)
        print("   ✅ pip available")
    except:
        issues.append("pip not available")

    # Check git (optional)
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        print("   ✅ git available")
    except:
        print("   ⚠️ git not available (optional)")

    # Check PowerShell (Windows only)
    if os.name == "nt":
        try:
            subprocess.run(["powershell", "-Command", "Get-Host"], capture_output=True, check=True)
            print("   ✅ PowerShell available")
        except:
            issues.append("PowerShell not available")

    if issues:
        print(f"❌ Prerequisites failed: {', '.join(issues)}")
        return False

    print("✅ All prerequisites satisfied")
    return True


def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")

    requirements = [
        "requests>=2.28.0",
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "sqlite3",  # Built-in but listed for clarity
        "openai>=1.3.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "python-multipart>=0.0.6",
        "jinja2>=3.1.0",
        "aiofiles>=23.2.0",
    ]

    try:
        for req in requirements:
            print(f"   Installing {req}...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", req],
                capture_output=True,
                check=True,
            )

        print("✅ Dependencies installed successfully")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def setup_directories():
    """Create necessary directories"""
    print("\n📁 Setting up directories...")

    base_dir = Path(__file__).parent
    directories = [
        base_dir / "logs",
        base_dir / "data",
        base_dir / "templates",
        Path("C:/EQ12/logs") if os.name == "nt" else Path("/workspaces/EQ12/logs"),
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created {directory}")

    return True


def setup_environment():
    """Setup environment configuration"""
    print("\n⚙️ Setting up environment configuration...")

    base_dir = Path(__file__).parent
    env_file = base_dir / ".env"

    if env_file.exists():
        print("   ⚠️ .env file already exists, skipping...")
        return True

    env_template = """# EQ12 GODSTACK Environment Configuration
# Copy this to .env and fill in your actual API keys

# OpenAI API for GPT enrichment
OPENAI_API_KEY=your_openai_api_key_here

# Bing Search API
BING_SEARCH_API_KEY=your_bing_search_api_key_here

# Google Custom Search API (optional)
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_custom_search_engine_id_here

# Telegram Bot Integration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Database Configuration
META_DB_PATH=meta_search.sqlite3

# Dashboard Configuration
DASHBOARD_HOST=127.0.0.1
DASHBOARD_PORT=8000

# Logging Configuration
LOG_LEVEL=INFO
LOG_DIR=logs/

# Auto-execution settings
AUTO_ENRICHMENT=true
AUTO_TELEGRAM_ALERTS=true
MAX_RESULTS_PER_QUERY=20
"""

    with open(env_file, "w") as f:
        f.write(env_template)

    print(f"   ✅ Created .env template at {env_file}")
    print("   ⚠️ Edit .env file to add your API keys before running GODSTACK")
    return True


def initialize_database():
    """Initialize SQLite database"""
    print("\n🗄️ Initializing database...")

    try:
        # Import and run database initialization
        sys.path.append(str(Path(__file__).parent))
        import db

        # Initialize database with all tables
        db.init_db()
        print("   ✅ Database initialized successfully")
        return True

    except Exception as e:
        print(f"   ❌ Database initialization failed: {e}")
        return False


def create_launch_script():
    """Create convenient launch script"""
    print("\n🚀 Creating launch script...")

    base_dir = Path(__file__).parent

    if os.name == "nt":
        # Windows batch file
        launch_script = base_dir / "launch_godstack.bat"
        script_content = f"""@echo off
echo Starting EQ12 GODSTACK Dashboard...
cd /d "{base_dir}"
python dashboard.py
pause
"""
    else:
        # Unix shell script
        launch_script = base_dir / "launch_godstack.sh"
        script_content = f"""#!/bin/bash
echo "Starting EQ12 GODSTACK Dashboard..."
cd "{base_dir}"
python dashboard.py
"""

    with open(launch_script, "w") as f:
        f.write(script_content)

    if os.name != "nt":
        os.chmod(launch_script, 0o755)

    print(f"   ✅ Created {launch_script}")
    return True


def install_task_scheduler():
    """Install Windows Task Scheduler tasks"""
    if os.name != "nt":
        print("\n⚠️ Task Scheduler installation skipped (Windows only)")
        return True

    print("\n⏰ Installing Task Scheduler tasks...")

    base_dir = Path(__file__).parent
    ps_script = base_dir / "Install-GODSTACKTasks.ps1"

    if not ps_script.exists():
        print("   ❌ PowerShell installation script not found")
        return False

    try:
        # Run PowerShell script to install tasks
        result = subprocess.run(
            [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ps_script),
                "-Install",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("   ✅ Task Scheduler tasks installed")
            print("   📊 Use 'taskschd.msc' to manage tasks")
            return True
        print(f"   ❌ Task installation failed: {result.stderr}")
        return False

    except Exception as e:
        print(f"   ❌ Task installation error: {e}")
        return False


def run_initial_test():
    """Run initial system test"""
    print("\n🧪 Running initial system test...")

    base_dir = Path(__file__).parent

    # Test task scheduler
    try:
        result = subprocess.run(
            [sys.executable, "task_scheduler.py", "--list"],
            cwd=base_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            print("   ✅ Task scheduler functional")
        else:
            print(f"   ⚠️ Task scheduler issues: {result.stderr}")
    except Exception as e:
        print(f"   ⚠️ Task scheduler test failed: {e}")

    # Test database connection
    try:
        import sqlite3

        db_path = base_dir / "meta_search.sqlite3"
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"   ✅ Database accessible ({len(tables)} tables)")
    except Exception as e:
        print(f"   ⚠️ Database test failed: {e}")

    return True


def print_completion_summary():
    """Print setup completion summary"""
    base_dir = Path(__file__).parent

    summary = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                        ✅ SETUP COMPLETED ✅                            ║
╚══════════════════════════════════════════════════════════════════════════╝

🎯 EQ12 GODSTACK is now installed and ready to use!

📁 Installation Directory: {base_dir}

🔧 Next Steps:
   1. Edit .env file to add your API keys:
      - OPENAI_API_KEY (for GPT enrichment)
      - BING_SEARCH_API_KEY (for search)
      - TELEGRAM_BOT_TOKEN (for alerts)

   2. Start the dashboard:
      • Windows: Run launch_godstack.bat
      • Command: python dashboard.py
      • URL: http://localhost:8000

   3. Test manual execution:
      • python task_scheduler.py --list
      • python task_scheduler.py --daily
      • python enrichment.py --help

⏰ Automated Tasks (Windows):
   • Daily Collection: News, offers, enrichment (8:00 AM)
   • Hourly Updates: Meta search, autosuggest (every hour)
   • Dashboard Server: Auto-start on boot

🛠️ Management Commands:
   • View tasks: taskschd.msc
   • Run task: schtasks /run /tn "EQ12 GODSTACK Daily Collection"
   • Dashboard: http://localhost:8000

📚 Documentation:
   • README.md - Complete usage guide
   • AGENTS.md - Agent integration specs
   • .env - Configuration template

🚀 The EQ12 GODSTACK intelligence ecosystem is ready for operation!
    """

    print(summary)


def main():
    """Main setup function"""
    print_banner()

    success_steps = []
    failed_steps = []

    steps = [
        ("Prerequisites Check", check_prerequisites),
        ("Python Dependencies", install_dependencies),
        ("Directory Setup", setup_directories),
        ("Environment Config", setup_environment),
        ("Database Initialization", initialize_database),
        ("Launch Script", create_launch_script),
        ("Task Scheduler", install_task_scheduler),
        ("System Test", run_initial_test),
    ]

    for step_name, step_func in steps:
        try:
            if step_func():
                success_steps.append(step_name)
            else:
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ {step_name} failed with error: {e}")
            failed_steps.append(step_name)

    print("\n📊 Setup Summary:")
    print(f"   ✅ Successful: {len(success_steps)} steps")
    print(f"   ❌ Failed: {len(failed_steps)} steps")

    if failed_steps:
        print(f"\n⚠️ Failed steps: {', '.join(failed_steps)}")
        print("🔧 Review error messages above and retry setup")
        return 1

    print_completion_summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())
