"""
EQ12 OpsBot Configuration Management
===================================

Pydantic-based configuration with .env support and validation.
Provides sane defaults and never crashes on missing keys.
"""

from pathlib import Path
from typing import Any

from pydantic import BaseSettings, Field


class OpsConfig(BaseSettings):
    """Main configuration for EQ12 OpsBot"""

    # OpenAI Configuration
    openai_api_key: str | None = Field(None, env="OPENAI_API_KEY")
    openai_webhook_secret: str | None = Field(None, env="OPENAI_WEBHOOK_SECRET")

    # EQ12 Platform
    eq12_budget_monthly: float = Field(120.0, env="EQ12_BUDGET_MONTHLY")
    eq12_budget_daily: float = Field(5.0, env="EQ12_BUDGET_DAILY")

    # Notifications
    slack_webhook_url: str | None = Field(None, env="SLACK_WEBHOOK_URL")
    teams_webhook_url: str | None = Field(None, env="TEAMS_WEBHOOK_URL")
    telegram_bot_token: str | None = Field(None, env="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str | None = Field(None, env="TELEGRAM_CHAT_ID")

    # GitHub Integration
    github_token: str | None = Field(None, env="GITHUB_TOKEN")
    github_repo: str = Field("EQ12/opsbot-issues", env="GITHUB_REPO")

    # External APIs
    odds_api_key: str | None = Field(None, env="ODDS_API_KEY")

    # Server Configuration
    server_host: str = Field("127.0.0.1", env="OPSBOT_HOST")
    server_port: int = Field(8088, env="OPSBOT_PORT")

    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_directory: Path = Field(Path("C:/EQ12/logs"), env="LOG_DIRECTORY")

    # Cache and Storage
    cache_ttl_minutes: int = Field(10, env="CACHE_TTL_MINUTES")
    webhook_replay_window_minutes: int = Field(10, env="WEBHOOK_REPLAY_WINDOW")

    # RSS Monitoring
    rss_poll_interval_minutes: int = Field(15, env="RSS_POLL_INTERVAL")
    community_github_issues: bool = Field(True, env="COMMUNITY_CREATE_ISSUES")

    # Feature Flags
    enable_budget_guard: bool = Field(True, env="ENABLE_BUDGET_GUARD")
    enable_model_policy: bool = Field(True, env="ENABLE_MODEL_POLICY")
    enable_rate_limits: bool = Field(True, env="ENABLE_RATE_LIMITS")
    enable_community_monitor: bool = Field(True, env="ENABLE_COMMUNITY_MONITOR")
    demo_mode: bool = Field(False, env="DEMO_MODE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def is_production_ready(self) -> bool:
        """Check if configuration is ready for production use"""
        if self.demo_mode:
            return False

        required_for_production = [self.openai_api_key, self.openai_webhook_secret]

        return all(val is not None for val in required_for_production)

    @property
    def notifications_enabled(self) -> bool:
        """Check if any notification channel is configured"""
        return any(
            [
                self.slack_webhook_url,
                self.teams_webhook_url,
                self.telegram_bot_token and self.telegram_chat_id,
            ]
        )

    @property
    def github_integration_enabled(self) -> bool:
        """Check if GitHub integration is configured"""
        return self.github_token is not None

    def get_config_summary(self) -> dict[str, Any]:
        """Get configuration summary for health endpoint"""
        return {
            "production_ready": self.is_production_ready,
            "demo_mode": self.demo_mode,
            "notifications_enabled": self.notifications_enabled,
            "github_enabled": self.github_integration_enabled,
            "features": {
                "budget_guard": self.enable_budget_guard,
                "model_policy": self.enable_model_policy,
                "rate_limits": self.enable_rate_limits,
                "community_monitor": self.enable_community_monitor,
            },
            "budgets": {"daily": self.eq12_budget_daily, "monthly": self.eq12_budget_monthly},
            "server": {"host": self.server_host, "port": self.server_port},
        }

    def create_missing_directories(self):
        """Ensure required directories exist"""
        self.log_directory.mkdir(parents=True, exist_ok=True)

        # Create config directories
        config_dir = Path("C:/EQ12/configs")
        config_dir.mkdir(parents=True, exist_ok=True)

        # Create webhook logs directory
        webhook_logs = self.log_directory / "webhooks"
        webhook_logs.mkdir(parents=True, exist_ok=True)


# Global configuration instance
config = OpsConfig()


def get_config() -> OpsConfig:
    """Get the global configuration instance"""
    return config


def reload_config() -> OpsConfig:
    """Reload configuration from environment/files"""
    global config
    config = OpsConfig()
    return config
