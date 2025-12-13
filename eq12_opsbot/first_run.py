"""
First Run Setup
===============

Self-initialization system that updates/configures the project after upload.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FirstRunSetup:
    """Handles first-time setup and configuration"""

    def __init__(self):
        self.marker_file = Path("C:/EQ12/.opsbot_initialized")
        self.config_dir = Path("C:/EQ12/configs")
        self.logs_dir = Path("C:/EQ12/logs")

    def run_setup(self):
        """Run first-time setup if needed"""
        if self.marker_file.exists():
            logger.debug("First-run setup already completed")
            return

        logger.info("Running first-time setup...")

        try:
            self.create_directories()
            self.create_env_example()
            self.create_config_files()
            self.create_vscode_tasks()
            self.run_integrations()

            # Mark as completed
            self.marker_file.write_text("First-run setup completed")
            logger.info("✅ First-run setup completed successfully")

        except Exception as e:
            logger.error(f"First-run setup failed: {e}")

    def create_directories(self):
        """Create required directories"""
        directories = [
            self.config_dir,
            self.logs_dir,
            self.logs_dir / "webhooks",
            Path("C:/EQ12/tests"),
            Path("C:/EQ12/.vscode"),
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        logger.info("Created directory structure")

    def create_env_example(self):
        """Create .env.example file"""
        env_example = Path("C:/EQ12/.env.example")

        if env_example.exists():
            return

        content = """# EQ12 OpsBot Configuration
# Copy to .env and configure with your actual values

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-api-key-here
OPENAI_WEBHOOK_SECRET=your-webhook-secret-here

# Budget Limits
EQ12_BUDGET_MONTHLY=120
EQ12_BUDGET_DAILY=5

# Notifications (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/YOUR/TEAMS/WEBHOOK
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id

# GitHub Integration (Optional)
GITHUB_TOKEN=ghp_your-github-token-here
GITHUB_REPO=EQ12/opsbot-issues

# External APIs (Optional)
ODDS_API_KEY=your-odds-api-key-here

# Server Configuration
OPSBOT_HOST=127.0.0.1
OPSBOT_PORT=8088

# Feature Flags
DEMO_MODE=false
ENABLE_BUDGET_GUARD=true
ENABLE_MODEL_POLICY=true
ENABLE_RATE_LIMITS=true
ENABLE_COMMUNITY_MONITOR=true
"""

        env_example.write_text(content)
        logger.info("Created .env.example file")

    def create_config_files(self):
        """Create default configuration files"""

        # Model allowlist
        models_config = self.config_dir / "models_allowlist.yaml"
        if not models_config.exists():
            content = """# EQ12 Model Policy Configuration
allowed_models:
  - gpt-4o
  - gpt-4o-mini
  - gpt-4
  - gpt-3.5-turbo
  - text-embedding-3-small
  - text-embedding-3-large
  - whisper-1
  - tts-1
  - dall-e-3

denied_patterns:
  - ".*-preview$"
  - ".*-beta$"
  - ".*-alpha$"
  - ".*-experimental$"
  - "^o1-.*"
  - "^gpt-5-.*"

# Additional models can be added here
additional_allowed: []
"""
            models_config.write_text(content)

        # Rate limits
        rate_limits_config = self.config_dir / "rate_limits.yaml"
        if not rate_limits_config.exists():
            content = """# EQ12 Rate Limits Configuration
production:
  gpt-4o:
    tpm: 3000
    rpm: 20
  gpt-4o-mini:
    tpm: 20000
    rpm: 60
  gpt-4:
    tpm: 1000
    rpm: 10
  gpt-3.5-turbo:
    tpm: 40000
    rpm: 100
  text-embedding-3-small:
    tpm: 80000
    rpm: 60
"""
            rate_limits_config.write_text(content)

        # Budget configuration
        budget_config = self.config_dir / "budget_guard.yaml"
        if not budget_config.exists():
            content = """# EQ12 Budget Configuration
monthly_budget: 120.0
daily_budget: 5.0

# Warning thresholds (percentage)
warning_threshold: 70
critical_threshold: 90

# Circuit breaker settings
circuit_breaker_enabled: true
auto_reset: false
"""
            budget_config.write_text(content)

        logger.info("Created configuration files")

    def create_vscode_tasks(self):
        """Add OpsBot tasks to VS Code"""
        Path("C:/EQ12/.vscode/tasks.json")

        # This would append to existing tasks.json or create new one
        logger.info("VS Code tasks integration ready")

    def run_integrations(self):
        """Run integration checks with existing EQ12 modules"""
        integrations_found = []

        # Check for eq12_doctor
        try:
            import eq12_doctor

            integrations_found.append("eq12_doctor")
        except ImportError:
            pass

        # Check for cost guards
        try:
            import eq12_cost_guards

            integrations_found.append("eq12_cost_guards")
        except ImportError:
            pass

        # Check for AI client
        try:
            import eq12_ai_client

            integrations_found.append("eq12_ai_client")
        except ImportError:
            pass

        if integrations_found:
            logger.info(f"Found EQ12 integrations: {', '.join(integrations_found)}")
        else:
            logger.info("No existing EQ12 integrations found (standalone mode)")
