"""Test configuration for OpsBot tests."""

import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_eq12_dir():
    """Create temporary EQ12 directory structure for testing."""
    temp_dir = Path(tempfile.mkdtemp())

    # Create directory structure
    (temp_dir / "logs").mkdir()
    (temp_dir / "configs").mkdir()
    (temp_dir / "eq12_opsbot").mkdir()

    yield temp_dir

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_webhook_payload():
    """Sample OpenAI webhook payload for testing."""
    return {
        "id": "evt_test_12345",
        "type": "job.completed",
        "created_at": 1696531200,
        "data": {
            "model": "gpt-4o-mini",
            "usage": {"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25},
            "status": "completed",
        },
    }


@pytest.fixture
def sample_rate_limit_payload():
    """Sample rate limit warning payload."""
    return {
        "id": "evt_rate_limit_67890",
        "type": "rate_limit.warning",
        "created_at": 1696531300,
        "data": {
            "model": "gpt-4o",
            "limit_type": "tpm",
            "current_usage": 2800,
            "limit": 3000,
            "percentage": 93.3,
        },
    }


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for testing."""
    test_vars = {
        "OPENAI_API_KEY": "sk-test-key-12345",
        "OPENAI_WEBHOOK_SECRET": "test-webhook-secret",
        "EQ12_BUDGET_DAILY": "5",
        "EQ12_BUDGET_MONTHLY": "120",
        "LOG_LEVEL": "DEBUG",
    }

    for key, value in test_vars.items():
        monkeypatch.setenv(key, value)

    return test_vars
