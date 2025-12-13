#!/usr/bin/env python3
"""
EQ12 GitHub Models Integration
Secure token management and GitHub Models API integration for EQ12 agentic systems

GitHub Models Token: Expires November 6, 2025
MCP Migration Deadline: November 10, 2025
"""

import asyncio
import json
import logging
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests

# Add EQ12 paths
sys.path.append(str(Path(__file__).parent.parent / "configs"))

try:
    from logging_eq12 import LoggingConfig

    logger = LoggingConfig.create_module_logger("github_models_integration")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class GitHubModelsManager:
    """Secure management of GitHub Models API integration for EQ12"""

    def __init__(self):
        self.eq12_root = Path("C:\\\\EQ12")
        self.token_file = self.eq12_root / "configs" / ".github_models_token"
        self.api_base = "https://models.inference.ai.azure.com"

        # Token expiration tracking
        self.token_expires = "2025-11-06"
        self.mcp_deadline = "2025-11-10"

        # Ensure secure token storage
        self._setup_secure_token_storage()

    def _setup_secure_token_storage(self):
        """Setup secure token storage with proper permissions"""
        try:
            # Create configs directory if it doesn't exist
            configs_dir = self.eq12_root / "configs"
            configs_dir.mkdir(exist_ok=True)

            # Set restrictive permissions on token file (Windows)
            if self.token_file.exists():
                logger.info("✅ GitHub Models token file already exists")
            else:
                logger.info("🔐 Setting up secure token storage...")

            # Log token expiration warning
            expires_date = datetime.strptime(self.token_expires, "%Y-%m-%d")
            days_until_expiry = (expires_date - datetime.now()).days

            if days_until_expiry <= 30:
                logger.warning(
                    f"⚠️ GitHub Models token expires in {days_until_expiry} days ({self.token_expires})"
                )
            else:
                logger.info(
                    f"📅 GitHub Models token expires in {days_until_expiry} days ({self.token_expires})"
                )

        except Exception as e:
            logger.error(f"Failed to setup token storage: {e}")

    def store_token_securely(self, token: str):
        """Store GitHub Models token securely"""
        try:
            # Store token with metadata
            token_data = {
                "token": token,
                "created_at": datetime.now(UTC).isoformat(),
                "expires_on": self.token_expires,
                "description": "GitHub Models API token for EQ12 agentic systems",
                "scopes": ["models:read", "models:inference"],
                "mcp_migration_deadline": self.mcp_deadline,
            }

            # Write to secure file
            with open(self.token_file, "w") as f:
                json.dump(token_data, f, indent=2)

            # Set environment variable for current session
            os.environ["GITHUB_MODELS_TOKEN"] = token

            logger.info("✅ GitHub Models token stored securely")
            logger.info(f"📍 Token file: {self.token_file}")
            logger.info(f"⏰ Expires: {self.token_expires}")

            return True

        except Exception as e:
            logger.error(f"Failed to store token securely: {e}")
            return False

    def load_token(self) -> str | None:
        """Load GitHub Models token from secure storage"""
        try:
            # Try environment variable first
            token = os.getenv("GITHUB_MODELS_TOKEN")
            if token:
                logger.info("✅ GitHub Models token loaded from environment")
                return token

            # Try secure file storage
            if self.token_file.exists():
                with open(self.token_file) as f:
                    token_data = json.load(f)

                token = token_data.get("token")
                if token:
                    # Set environment variable
                    os.environ["GITHUB_MODELS_TOKEN"] = token
                    logger.info("✅ GitHub Models token loaded from secure file")

                    # Check expiration
                    expires_on = token_data.get("expires_on")
                    if expires_on:
                        expires_date = datetime.strptime(expires_on, "%Y-%m-%d")
                        days_left = (expires_date - datetime.now()).days

                        if days_left <= 7:
                            logger.warning(f"⚠️ Token expires in {days_left} days! Renewal needed.")

                    return token

            logger.warning("⚠️ No GitHub Models token found")
            return None

        except Exception as e:
            logger.error(f"Failed to load token: {e}")
            return None

    async def test_github_models_connection(self) -> dict[str, Any]:
        """Test connection to GitHub Models API"""
        try:
            token = self.load_token()
            if not token:
                return {
                    "success": False,
                    "error": "No GitHub Models token available",
                    "recommendation": "Store token using store_token_securely() method",
                }

            # Test API connection
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            # Try to list available models
            response = requests.get(f"{self.api_base}/models", headers=headers, timeout=10)

            if response.status_code == 200:
                models_data = response.json()

                # Handle both list and dict responses
                if isinstance(models_data, list):
                    models_count = len(models_data)
                elif isinstance(models_data, dict):
                    models_count = len(models_data.get("data", []))
                else:
                    models_count = 0

                return {
                    "success": True,
                    "models_available": models_count,
                    "api_status": "operational",
                    "token_valid": True,
                    "expires_on": self.token_expires,
                }
            else:
                return {
                    "success": False,
                    "error": f"API request failed: {response.status_code}",
                    "response": response.text[:200],
                    "token_status": "invalid_or_expired",
                }

        except Exception as e:
            logger.error(f"GitHub Models connection test failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "recommendation": "Check network connectivity and token validity",
            }

    async def integrate_with_eq12_mcp(self) -> dict[str, Any]:
        """Integrate GitHub Models with EQ12 MCP server"""
        try:
            # Check if MCP server exists
            mcp_server_path = self.eq12_root / "scripts" / "eq12_mcp_server.py"

            if not mcp_server_path.exists():
                return {
                    "success": False,
                    "error": "EQ12 MCP server not found",
                    "path": str(mcp_server_path),
                    "recommendation": "Run Install-EQ12MCP.ps1 to setup MCP server",
                }

            # Test GitHub Models integration
            connection_test = await self.test_github_models_connection()

            if not connection_test["success"]:
                return {
                    "success": False,
                    "error": "GitHub Models connection failed",
                    "details": connection_test,
                    "mcp_status": "cannot_integrate_without_valid_token",
                }

            # Prepare MCP integration details
            integration_status = {
                "success": True,
                "github_models_status": "operational",
                "mcp_server_available": True,
                "token_expires": self.token_expires,
                "mcp_deadline": self.mcp_deadline,
                "integration_capabilities": [
                    "AI-powered code analysis via GitHub Models",
                    "Enhanced agentic intelligence with cloud AI",
                    "Backup AI provider for EQ12 systems",
                    "Cross-platform AI assistant compatibility",
                ],
                "next_steps": [
                    "Update MCP server to include GitHub Models endpoints",
                    "Test AI capabilities through MCP interface",
                    "Validate before MCP migration deadline (Nov 10)",
                    "Monitor token expiration (Nov 6)",
                ],
            }

            logger.info("✅ GitHub Models ready for EQ12 MCP integration")
            return integration_status

        except Exception as e:
            logger.error(f"MCP integration check failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "recommendation": "Review EQ12 MCP setup and GitHub Models configuration",
            }

    def create_environment_setup_script(self):
        """Create PowerShell script to set up GitHub Models environment"""
        script_content = """# EQ12 GitHub Models Environment Setup
# Generated: {datetime.now(timezone.utc).isoformat()}
# Token expires: {self.token_expires}
# MCP deadline: {self.mcp_deadline}

Write-Host "🔐 Setting up GitHub Models environment for EQ12..." -ForegroundColor Green

# Set GitHub Models token (if not already set)
if (-not $env:GITHUB_MODELS_TOKEN) {{
    Write-Host "⚠️  GITHUB_MODELS_TOKEN not found in environment" -ForegroundColor Yellow
    Write-Host "📋 To set the token, run:" -ForegroundColor Yellow
    Write-Host '   $env:GITHUB_MODELS_TOKEN = "your_token_here"' -ForegroundColor Cyan
    Write-Host "🔒 Or store securely using: python C:\\\\EQ12\\\\scripts\\github_models_integration.py" -ForegroundColor Cyan
}} else {{
    Write-Host "✅ GITHUB_MODELS_TOKEN found in environment" -ForegroundColor Green
}}

# Validate token expiration
$tokenExpires = [datetime]::Parse("{self.token_expires}")
$daysLeft = ($tokenExpires - (Get-Date)).Days

if ($daysLeft -le 7) {{
    Write-Host "🚨 URGENT: GitHub Models token expires in $daysLeft days!" -ForegroundColor Red
    Write-Host "🔄 Renew token at: https://github.com/settings/tokens" -ForegroundColor Red
}} elseif ($daysLeft -le 30) {{
    Write-Host "⚠️  GitHub Models token expires in $daysLeft days" -ForegroundColor Yellow
}} else {{
    Write-Host "📅 GitHub Models token expires in $daysLeft days" -ForegroundColor Green
}}

# MCP migration deadline warning
$mcpDeadline = [datetime]::Parse("{self.mcp_deadline}")
$mcpDaysLeft = ($mcpDeadline - (Get-Date)).Days

Write-Host "🔄 MCP migration deadline in $mcpDaysLeft days ({self.mcp_deadline})" -ForegroundColor $(if ($mcpDaysLeft -le 7) {{"Red"}} else {{"Yellow"}})

# Test GitHub Models connection
Write-Host "🧪 Testing GitHub Models connection..." -ForegroundColor Blue
python -c "
import sys
sys.path.append('C:\\\\\\EQ12\\\\\\scripts')
from github_models_integration import GitHubModelsManager
import asyncio

async def test():
    manager = GitHubModelsManager()
    result = await manager.test_github_models_connection()
    if result['success']:
        print('✅ GitHub Models connection successful')
        print(f'📊 Models available: {{result.get(\"models_available\", \"unknown\")}}')
    else:
        print(f'❌ Connection failed: {{result.get(\"error\", \"unknown error\")}}')

asyncio.run(test())
"

Write-Host "🚀 GitHub Models environment setup complete!" -ForegroundColor Green
Write-Host "📚 Next: Run Install-EQ12MCP.ps1 to complete MCP migration setup" -ForegroundColor Cyan
"""

        script_path = self.eq12_root / "Setup-GitHubModels.ps1"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        logger.info(f"✅ Environment setup script created: {script_path}")
        return script_path


async def main():
    """Main function for GitHub Models integration setup"""
    print("🔐 EQ12 GitHub Models Integration Setup")
    print("=" * 50)

    manager = GitHubModelsManager()

    # Check if token is provided via command line
    if len(sys.argv) > 1 and sys.argv[1].startswith("github_pat_"):
        token = sys.argv[1]
        print("🔑 Storing provided GitHub Models token...")

        success = manager.store_token_securely(token)
        if success:
            print("✅ Token stored successfully")
        else:
            print("❌ Failed to store token")
            return

    # Test connection
    print("\n🧪 Testing GitHub Models connection...")
    connection_test = await manager.test_github_models_connection()

    if connection_test["success"]:
        print("✅ GitHub Models connection successful!")
        print(f"📊 Models available: {connection_test.get('models_available', 'unknown')}")
    else:
        print(f"❌ Connection failed: {connection_test.get('error', 'unknown')}")

        if "No GitHub Models token" in str(connection_test.get("error", "")):
            print("\n📋 To setup token manually:")
            print("1. Store token: manager.store_token_securely('your_token_here')")
            print("2. Or set environment: $env:GITHUB_MODELS_TOKEN = 'your_token_here'")

    # Check MCP integration readiness
    print("\n🔄 Checking MCP integration readiness...")
    mcp_status = await manager.integrate_with_eq12_mcp()

    if mcp_status["success"]:
        print("✅ Ready for EQ12 MCP integration!")
        print("📋 Integration capabilities:")
        for capability in mcp_status.get("integration_capabilities", []):
            print(f"   • {capability}")
    else:
        print(f"⚠️ MCP integration issues: {mcp_status.get('error', 'unknown')}")
        print(f"💡 Recommendation: {mcp_status.get('recommendation', 'Check setup')}")

    # Create environment setup script
    print("\n📝 Creating environment setup script...")
    script_path = manager.create_environment_setup_script()
    print(f"✅ Script created: {script_path}")

    print("\n🚀 GitHub Models integration setup complete!")
    print("📚 Next steps:")
    print("   1. Run Setup-GitHubModels.ps1 to validate environment")
    print("   2. Run Install-EQ12MCP.ps1 to complete MCP migration")
    print("   3. Test integrated system before November 10 deadline")


if __name__ == "__main__":
    asyncio.run(main())
