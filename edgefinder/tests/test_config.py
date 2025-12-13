"""
Unit tests for EdgeFinder configuration management
"""

from pathlib import Path

import pytest
import yaml

from edgefinder.config import (
    Config,
    EQ12IntegrationConfig,
    GitHubConfig,
    HuggingFaceConfig,
    SecurityConfig,
    load_config,
)


class TestConfig:
    """Test configuration management"""

    def test_default_config_creation(self):
        """Test creating default configuration"""
        config = Config()

        assert config.output_dir == "output"
        assert config.downloads_dir == "downloads"
        assert config.github.rate_limit_requests == 5000
        assert config.huggingface.rate_limit_requests == 1000
        assert config.security.max_file_size_mb == 100
        assert config.eq12_integration.dashboard_base_url == "https://eq12.local/dashboards/"

    def test_github_config(self):
        """Test GitHub configuration"""
        github_config = GitHubConfig(
            token="test_token", rate_limit_requests=1000, rate_limit_window=3600
        )

        assert github_config.token == "test_token"
        assert github_config.rate_limit_requests == 1000
        assert github_config.base_url == "https://api.github.com"

    def test_huggingface_config(self):
        """Test Hugging Face configuration"""
        hf_config = HuggingFaceConfig(token="test_hf_token", rate_limit_requests=500)

        assert hf_config.token == "test_hf_token"
        assert hf_config.rate_limit_requests == 500
        assert hf_config.base_url == "https://huggingface.co"

    def test_security_config(self):
        """Test security configuration"""
        security_config = SecurityConfig(
            max_file_size_mb=50,
            allowed_extensions=[".py", ".js"],
            dangerous_patterns=["eval(", "exec("],
        )

        assert security_config.max_file_size_mb == 50
        assert ".py" in security_config.allowed_extensions
        assert "eval(" in security_config.dangerous_patterns

    def test_eq12_integration_config(self):
        """Test EQ12 integration configuration"""
        eq12_config = EQ12IntegrationConfig(
            dashboard_base_url="https://custom.eq12.local/",
            betting_keywords=["odds", "betting"],
            scoring_bonuses={"eq12_integration": 2.0},
        )

        assert eq12_config.dashboard_base_url == "https://custom.eq12.local/"
        assert "odds" in eq12_config.betting_keywords
        assert eq12_config.scoring_bonuses["eq12_integration"] == 2.0

    def test_get_dashboard_url(self):
        """Test dashboard URL generation"""
        config = Config()
        url = config.get_dashboard_url("test.html")
        expected = "https://eq12.local/dashboards/test.html"
        assert url == expected

    def test_environment_variable_override(self):
        """Test configuration from environment variables"""
        env_vars = {
            "EDGEFINDER_OUTPUT_DIR": "/custom/output",
            "GITHUB_TOKEN": "env_github_token",
            "HUGGINGFACE_TOKEN": "env_hf_token",
        }

        with pytest.MonkeyPatch().context() as m:
            for key, value in env_vars.items():
                m.setenv(key, value)

            Config()
            # Note: This assumes env var loading is implemented in Config

    def test_config_validation(self):
        """Test configuration validation"""
        # Test invalid rate limit
        with pytest.raises(ValueError):
            GitHubConfig(rate_limit_requests=-1)

        # Test invalid file size
        with pytest.raises(ValueError):
            SecurityConfig(max_file_size_mb=0)


class TestConfigLoading:
    """Test configuration loading from files"""

    def test_load_config_from_yaml(self, temp_dir):
        """Test loading configuration from YAML file"""
        config_data = {
            "output_dir": str(temp_dir / "custom_output"),
            "downloads_dir": str(temp_dir / "custom_downloads"),
            "github": {"token": "yaml_github_token", "rate_limit_requests": 2000},
            "huggingface": {"token": "yaml_hf_token", "rate_limit_requests": 800},
            "security": {"max_file_size_mb": 75, "scan_timeout": 300},
        }

        config_file = temp_dir / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        config = load_config(config_file)

        assert config.output_dir == str(temp_dir / "custom_output")
        assert config.github.token == "yaml_github_token"
        assert config.github.rate_limit_requests == 2000
        assert config.huggingface.rate_limit_requests == 800
        assert config.security.max_file_size_mb == 75

    def test_load_config_file_not_exists(self):
        """Test loading config when file doesn't exist"""
        non_existent_path = Path("/non/existent/config.yaml")
        config = load_config(non_existent_path)

        # Should return default config
        assert isinstance(config, Config)
        assert config.output_dir == "output"

    def test_load_config_invalid_yaml(self, temp_dir):
        """Test loading config with invalid YAML"""
        config_file = temp_dir / "invalid.yaml"
        config_file.write_text("invalid: yaml: content: [")

        with pytest.raises(yaml.YAMLError):
            load_config(config_file)

    def test_load_config_partial_yaml(self, temp_dir):
        """Test loading config with partial YAML (missing sections)"""
        config_data = {
            "output_dir": str(temp_dir / "partial_output"),
            "github": {
                "token": "partial_token"
                # Missing other github fields
            },
            # Missing huggingface section entirely
        }

        config_file = temp_dir / "partial.yaml"
        config_file.write_text(yaml.dump(config_data))

        config = load_config(config_file)

        # Should merge with defaults
        assert config.output_dir == str(temp_dir / "partial_output")
        assert config.github.token == "partial_token"
        assert config.github.rate_limit_requests == 5000  # Default
        assert config.huggingface.token is None  # Default


class TestConfigIntegration:
    """Test configuration integration features"""

    def test_eq12_dashboard_integration(self):
        """Test EQ12 dashboard integration URLs"""
        config = Config()

        # Test various dashboard URLs
        search_url = config.get_dashboard_url("search_results.html")
        analysis_url = config.get_dashboard_url("analysis.html")
        security_url = config.get_dashboard_url("security_report.html")

        expected_base = "https://eq12.local/dashboards/"
        assert search_url == f"{expected_base}search_results.html"
        assert analysis_url == f"{expected_base}analysis.html"
        assert security_url == f"{expected_base}security_report.html"

    def test_security_pattern_matching(self):
        """Test security pattern configuration"""
        config = Config()

        dangerous_patterns = config.security.dangerous_patterns
        assert "eval(" in dangerous_patterns
        assert "exec(" in dangerous_patterns
        assert "__import__" in dangerous_patterns

    def test_eq12_keyword_enhancement(self):
        """Test EQ12 keyword enhancement"""
        config = Config()

        betting_keywords = config.eq12_integration.betting_keywords
        ai_keywords = config.eq12_integration.ai_keywords
        analytics_keywords = config.eq12_integration.analytics_keywords

        # Check for expected EQ12-specific keywords
        assert "odds" in betting_keywords
        assert "parlay" in betting_keywords
        assert "transformer" in ai_keywords
        assert "neural" in ai_keywords
        assert "analytics" in analytics_keywords
        assert "dashboard" in analytics_keywords
