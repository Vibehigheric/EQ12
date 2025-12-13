"""
EdgeFinder Configuration Management
Handles configuration loading, validation, and environment variables
"""

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings


class GitHubConfig(BaseModel):
    """GitHub API configuration"""

    base_url: str = "https://api.github.com"
    token: str | None = None
    rate_limit_buffer: int = 10
    search_delay_ms: int = 100
    timeout_seconds: int = 30

    @field_validator("token", mode="before")
    @classmethod
    def get_token_from_env(cls, v):
        return v or os.getenv("GITHUB_TOKEN")


class HuggingFaceConfig(BaseModel):
    """Hugging Face API configuration"""

    base_url: str = "https://huggingface.co"
    api_base_url: str = "https://huggingface.co/api"
    token: str | None = None
    models_endpoint: str = "/models"
    spaces_endpoint: str = "/spaces"
    timeout_seconds: int = 30

    @field_validator("token", mode="before")
    @classmethod
    def get_token_from_env(cls, v):
        return v or os.getenv("HUGGINGFACE_TOKEN")


class SearchConfig(BaseModel):
    """Search operation configuration"""

    max_results_per_source: int = 50
    timeout_seconds: int = 30
    retry_attempts: int = 3
    default_keywords: list[str] = Field(default_factory=lambda: ["api", "library", "tool"])


class AnalysisConfig(BaseModel):
    """Analysis operation configuration"""

    download_enabled: bool = True
    security_scan_enabled: bool = True
    max_file_size_mb: int = 100
    max_repo_size_mb: int = 500
    timeout_seconds: int = 300


class ScoringConfig(BaseModel):
    """Scoring algorithm configuration"""

    license_bonus: int = 20
    stars_weight: float = 0.3
    activity_weight: float = 0.2
    keyword_weight: float = 0.2
    language_bonus: int = 10
    security_penalty: int = -50
    max_score: int = 100


class LicenseConfig(BaseModel):
    """License compatibility configuration"""

    allowed: list[str] = Field(
        default_factory=lambda: [
            "MIT",
            "Apache-2.0",
            "BSD-3-Clause",
            "BSD-2-Clause",
            "ISC",
            "Unlicense",
        ]
    )
    blocked: list[str] = Field(
        default_factory=lambda: [
            "GPL-3.0",
            "GPL-2.0",
            "AGPL-3.0",
            "LGPL-3.0",
            "LGPL-2.1",
            "CC-BY-NC",
            "CC-BY-NC-SA",
        ]
    )


class SecurityConfig(BaseModel):
    """Security scanning configuration"""

    bandit_enabled: bool = True
    safety_enabled: bool = True
    custom_rules_enabled: bool = True
    max_security_warnings: int = 5

    @field_validator("bandit_enabled", "safety_enabled", mode="before")
    @classmethod
    def get_security_from_env(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return v


class PatchConfig(BaseModel):
    """Patch generation configuration"""

    enabled: bool = True
    ast_based: bool = True
    sandbox_test: bool = True
    max_patch_size_lines: int = 1000
    backup_original: bool = True


class EQ12IntegrationConfig(BaseModel):
    """EQ12-specific integration settings"""

    dashboard_base_url: str = "https://eq12.local/dashboards"
    betting_keywords: list[str] = Field(
        default_factory=lambda: ["odds", "parlay", "sportsbook", "betting", "wager"]
    )
    ai_keywords: list[str] = Field(
        default_factory=lambda: ["llama", "transformer", "agent", "ml", "ai", "gpt"]
    )
    analytics_keywords: list[str] = Field(
        default_factory=lambda: ["statistics", "analysis", "prediction", "model"]
    )


class Config(BaseSettings):
    """Main EdgeFinder configuration"""

    # Core configurations
    github: GitHubConfig = Field(default_factory=GitHubConfig)
    huggingface: HuggingFaceConfig = Field(default_factory=HuggingFaceConfig)
    search: SearchConfig = Field(default_factory=SearchConfig)
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    scoring: ScoringConfig = Field(default_factory=ScoringConfig)
    licenses: LicenseConfig = Field(default_factory=LicenseConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    patch_generation: PatchConfig = Field(default_factory=PatchConfig)
    eq12_integration: EQ12IntegrationConfig = Field(default_factory=EQ12IntegrationConfig)

    # Global settings
    debug: bool = False
    verbose: bool = False
    output_dir: str = "./output"
    downloads_dir: str = "./downloads"
    cache_dir: str = "./.cache"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        case_sensitive = False

    @field_validator("debug", "verbose", mode="before")
    @classmethod
    def get_debug_from_env(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return v

    @classmethod
    def from_file(cls, config_path: Path) -> "Config":
        """Load configuration from YAML file"""
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, encoding="utf-8") as f:
            config_data = yaml.safe_load(f) or {}

        return cls.parse_obj(config_data)

    @classmethod
    def get_default(cls) -> "Config":
        """Get default configuration with environment variable overrides"""
        return cls()

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary"""
        return self.dict()

    def save_to_file(self, config_path: Path) -> None:
        """Save configuration to YAML file"""
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, indent=2)

    def is_license_allowed(self, license_name: str) -> bool:
        """Check if license is in the allowed list"""
        if not license_name:
            return False
        return license_name.upper() in [lic.upper() for lic in self.licenses.allowed]

    def is_license_blocked(self, license_name: str) -> bool:
        """Check if license is in the blocked list"""
        if not license_name:
            return False
        return license_name.upper() in [lic.upper() for lic in self.licenses.blocked]

    def get_dashboard_url(self, dashboard_name: str) -> str:
        """Get full dashboard URL"""
        base_url = self.eq12_integration.dashboard_base_url.rstrip("/")
        return f"{base_url}/{dashboard_name}"

    def is_eq12_betting_related(self, keywords: list[str]) -> bool:
        """Check if keywords are related to EQ12 betting functionality"""
        betting_kw = [kw.lower() for kw in self.eq12_integration.betting_keywords]
        search_kw = [kw.lower() for kw in keywords]
        return any(bkw in " ".join(search_kw) for bkw in betting_kw)

    def is_eq12_ai_related(self, keywords: list[str]) -> bool:
        """Check if keywords are related to EQ12 AI functionality"""
        ai_kw = [kw.lower() for kw in self.eq12_integration.ai_keywords]
        search_kw = [kw.lower() for kw in keywords]
        return any(aikw in " ".join(search_kw) for aikw in ai_kw)

    def get_rate_limit_delay(self, source: str) -> float:
        """Get appropriate delay between API calls"""
        if source == "github":
            return self.github.search_delay_ms / 1000.0
        return 0.1  # Default 100ms delay


def load_config(config_path: Path | None = None) -> Config:
    """
    Load configuration from file or environment variables

    Args:
        config_path: Optional path to YAML configuration file

    Returns:
        Configuration instance
    """
    if config_path and config_path.exists():
        return Config.from_file(config_path)

    # Check for config file in common locations
    common_paths = [
        Path("config.yaml"),
        Path("edgefinder.yaml"),
        Path("~/.edgefinder/config.yaml").expanduser(),
        Path("/etc/edgefinder/config.yaml"),
    ]

    for path in common_paths:
        if path.exists():
            return Config.from_file(path)

    # Fall back to default configuration
    return Config.get_default()
