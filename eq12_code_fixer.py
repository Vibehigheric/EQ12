#!/usr/bin/env python3
"""
EQ12 Code Quality Fixer
Automated script to fix common code quality issues identified in the diagnostic
"""

import os
import re
from pathlib import Path


def fix_python_files():
    """Fix common Python code quality issues"""
    python_files = list(Path(".").glob("*.py"))

    print(f"🔧 Fixing {len(python_files)} Python files...")

    for file_path in python_files:
        if file_path.name in ["eq12_code_fixer.py", "eq12_diagnose.py"]:
            continue  # Skip self and diagnostic files

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Fix common issues
            # 1. Remove unused imports (basic detection)
            lines = content.split("\n")
            new_lines = []

            for line in lines:
                # Skip obviously unused imports
                if (
                    line.strip().startswith("from typing import")
                    and "Optional" in line
                    and "Optional" not in content.replace(line, "")
                ):
                    # Remove Optional if not used
                    line = (
                        line.replace(", Optional", "")
                        .replace("Optional, ", "")
                        .replace("Optional", "")
                    )
                    if line.strip().endswith("import"):
                        continue  # Skip empty import line

                new_lines.append(line)

            content = "\n".join(new_lines)

            # 2. Fix common spacing issues
            # Add blank lines before class definitions
            content = re.sub(r"\n(class [A-Z])", r"\n\n\1", content)

            # 3. Fix None type hints
            content = re.sub(r": str = None", r": Optional[str] = None", content)
            content = re.sub(r": int = None", r": Optional[int] = None", content)
            content = re.sub(r": Dict = None", r": Optional[Dict] = None", content)

            # Only write if content changed
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✅ Fixed: {file_path.name}")
            else:
                print(f"📄 No changes: {file_path.name}")

        except Exception as e:
            print(f"❌ Error fixing {file_path.name}: {e}")


def fix_environment_setup():
    """Ensure proper environment configuration"""
    print("\n🌍 Checking environment setup...")

    # Check if .env exists
    if not Path(".env").exists():
        if Path(".env.template").exists():
            print("📝 Creating .env from template...")
            with open(".env.template") as template:
                template_content = template.read()

            # Set some defaults for development
            env_content = (
                template_content.replace(
                    "your_secret_key_here_change_in_production_32_chars_min",
                    "dev_secret_key_eq12_2025_change_in_production_abcd1234",
                )
                .replace(
                    "your_jwt_secret_key_here_change_in_production_32_chars",
                    "dev_jwt_secret_key_eq12_2025_change_in_production_xyz789",
                )
                .replace(
                    "sk_test_your_stripe_test_secret_key_here",
                    "sk_test_dev_mode_placeholder_stripe_secret_key",
                )
                .replace(
                    "pk_test_your_stripe_test_publishable_key_here",
                    "pk_test_dev_mode_placeholder_stripe_publishable_key",
                )
            )

            with open(".env", "w") as env_file:
                env_file.write(env_content)
            print("✅ Created .env file with development defaults")
        else:
            print("⚠️ No .env.template found, creating basic .env...")
            basic_env = """# EQ12 Basic Environment
DEBUG=true
DATABASE_URL=sqlite:///./eq12_dev.db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=dev_secret_key_change_in_production
DEVELOPMENT_MODE=true
"""
            with open(".env", "w") as env_file:
                env_file.write(basic_env)
            print("✅ Created basic .env file")
    else:
        print("✅ .env file exists")


def fix_requirements():
    """Consolidate and fix requirements files"""
    print("\n📦 Checking requirements files...")

    missing_deps = []

    # Check if core dependencies are specified
    core_deps = {
        "fastapi": "fastapi>=0.104.1",
        "uvicorn": "uvicorn[standard]>=0.24.0",
        "sqlalchemy": "SQLAlchemy>=2.0.0",
        "stripe": "stripe>=7.0.0",
        "redis": "redis>=5.0.0",
        "python-dotenv": "python-dotenv>=1.0.0",
        "pydantic": "pydantic>=2.0.0",
        "psycopg2-binary": "psycopg2-binary>=2.9.0",
    }

    # Check main requirements.txt
    if Path("requirements.txt").exists():
        with open("requirements.txt") as f:
            req_content = f.read()

        for dep, spec in core_deps.items():
            if dep not in req_content:
                missing_deps.append(spec)

    if missing_deps:
        print(f"⚠️ Found {len(missing_deps)} missing dependencies")

        # Append missing deps to requirements.txt
        with open("requirements.txt", "a") as f:
            f.write("\n# Added by EQ12 Code Fixer\n")
            for dep in missing_deps:
                f.write(f"{dep}\n")
                print(f"📦 Added: {dep}")
    else:
        print("✅ All core dependencies found")


def create_quick_start_script():
    """Create a quick start script for developers"""
    print("\n🚀 Creating quick start script...")

    script_content = """#!/bin/bash
# EQ12 Quick Start Script

echo "🚀 EQ12 Quick Start"
echo "=================="

# Check Python version
python3 --version || { echo "❌ Python 3 not found"; exit 1; }

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Set up environment
if [ ! -f ".env" ]; then
    echo "🌍 Setting up environment..."
    cp .env.template .env 2>/dev/null || echo "⚠️ No .env.template found"
fi

# Run basic health check
echo "🔍 Running health check..."
python -c "
import sys
print('✅ Python import test passed')
try:
    from eq12_openai_optimizer import OpenAIOptimizer
    print('✅ EQ12 OpenAI Optimizer available')
except ImportError as e:
    print(f'⚠️ OpenAI Optimizer issue: {e}')

try:
    import fastapi
    print('✅ FastAPI available')
except ImportError:
    print('❌ FastAPI not installed')
"

echo "🎉 Quick start complete!"
echo "💡 Next steps:"
echo "   1. Edit .env file with your API keys"
echo "   2. Run: python eq12_enterprise_api_v2.py"
echo "   3. Visit: http://localhost:8000/health"
"""

    with open("quick_start.sh", "w") as f:
        f.write(script_content)

    # Make it executable
    os.chmod("quick_start.sh", 0o755)
    print("✅ Created quick_start.sh")


def main():
    """Main fix routine"""
    print("🔧 EQ12 Code Quality Fixer")
    print("=" * 30)

    # 1. Fix Python files
    fix_python_files()

    # 2. Fix environment setup
    fix_environment_setup()

    # 3. Fix requirements
    fix_requirements()

    # 4. Create quick start script
    create_quick_start_script()

    print("\n🎉 Code quality fixes complete!")
    print("\n📋 Summary of fixes:")
    print("  ✅ Python code quality improvements")
    print("  ✅ Environment configuration setup")
    print("  ✅ Requirements dependencies check")
    print("  ✅ Quick start script created")

    print("\n🚀 Next steps:")
    print("  1. Review the created .env file and add your API keys")
    print("  2. Run: pip install -r requirements.txt")
    print("  3. Test: python eq12_openai_demo.py")
    print("  4. Deploy: python eq12_enterprise_api_v2.py")


if __name__ == "__main__":
    main()
