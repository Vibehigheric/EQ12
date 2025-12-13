"""
EdgeFinder Test Configuration and Fixtures
pytest configuration and shared test fixtures
"""

import os
import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import patch

import pytest

from edgefinder.config import Config, GitHubConfig, HuggingFaceConfig
from edgefinder.models import (
    AnalysisResult,
    Candidate,
    LicenseCompatibility,
    LicenseInfo,
    RepositoryStats,
    SearchCriteria,
    SearchResult,
    SecurityWarning,
    SeverityLevel,
    SourceType,
)


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def config(temp_dir) -> Config:
    """Create test configuration"""
    return Config(
        output_dir=str(temp_dir / "output"),
        downloads_dir=str(temp_dir / "downloads"),
        github=GitHubConfig(
            token="test_token_123",
            base_url="https://api.github.com",
            rate_limit_requests=60,
            rate_limit_window=3600,
        ),
        huggingface=HuggingFaceConfig(
            token="test_hf_token_123",
            base_url="https://huggingface.co",
            api_base_url="https://huggingface.co/api",
        ),
    )


@pytest.fixture
def sample_search_criteria() -> SearchCriteria:
    """Sample search criteria for testing"""
    return SearchCriteria(
        keywords=["odds", "api", "betting"],
        languages=["python", "javascript"],
        min_stars=10,
        max_results_per_source=50,
        sources=[SourceType.GITHUB, SourceType.HUGGINGFACE],
        license_allowlist=["MIT", "Apache-2.0"],
    )


@pytest.fixture
def sample_github_candidate() -> Candidate:
    """Sample GitHub candidate for testing"""
    return Candidate(
        id="github_123",
        full_name="example/betting-api",
        name="betting-api",
        description="A Python API for sports betting odds",
        url="https://github.com/example/betting-api",
        clone_url="https://github.com/example/betting-api.git",
        source=SourceType.GITHUB,
        stats=RepositoryStats(stars=125, forks=23, watchers=45, open_issues=8, size_kb=1024),
        license_info=LicenseInfo(
            name="MIT License",
            spdx_id="MIT",
            url="https://github.com/example/betting-api/blob/main/LICENSE",
            compatibility=LicenseCompatibility.COMPATIBLE,
        ),
        topics=["api", "betting", "odds", "sports"],
        score=8.5,
        matching_keywords=["api", "betting", "odds"],
    )


@pytest.fixture
def sample_huggingface_candidate() -> Candidate:
    """Sample Hugging Face candidate for testing"""
    return Candidate(
        id="hf_456",
        full_name="huggingface/sports-prediction-model",
        name="sports-prediction-model",
        description="Machine learning model for sports outcome prediction",
        url="https://huggingface.co/huggingface/sports-prediction-model",
        clone_url="https://huggingface.co/huggingface/sports-prediction-model.git",
        source=SourceType.HUGGINGFACE,
        stats=RepositoryStats(stars=89, downloads=1500, size_kb=2048),
        license_info=LicenseInfo(
            name="Apache License 2.0",
            spdx_id="Apache-2.0",
            compatibility=LicenseCompatibility.COMPATIBLE,
        ),
        topics=["machine-learning", "sports", "prediction"],
        score=7.2,
        matching_keywords=["prediction", "sports"],
    )


@pytest.fixture
def sample_search_result(sample_github_candidate, sample_huggingface_candidate) -> SearchResult:
    """Sample search result with multiple candidates"""
    return SearchResult(
        query="betting api odds",
        candidates=[sample_github_candidate, sample_huggingface_candidate],
        total_found=2,
        sources_searched=[SourceType.GITHUB, SourceType.HUGGINGFACE],
    )


@pytest.fixture
def sample_analysis_result() -> AnalysisResult:
    """Sample analysis result for testing"""
    return AnalysisResult(
        candidate_id="github_123",
        dependencies=["requests", "numpy", "pandas"],
        security_warnings=[
            SecurityWarning(
                rule_id="B101",
                message="Use of assert detected",
                severity=SeverityLevel.LOW,
                file_path="src/main.py",
                line_number=42,
            )
        ],
        code_quality_score=8.5,
        maintainability_score=7.8,
        security_score=9.2,
        license_compliance=True,
        eq12_integration_potential=8.9,
    )


@pytest.fixture
def mock_github_api_response():
    """Mock GitHub API response"""
    return {
        "total_count": 1,
        "incomplete_results": False,
        "items": [
            {
                "id": 123456789,
                "name": "betting-api",
                "full_name": "example/betting-api",
                "description": "A Python API for sports betting odds",
                "html_url": "https://github.com/example/betting-api",
                "clone_url": "https://github.com/example/betting-api.git",
                "stargazers_count": 125,
                "forks_count": 23,
                "watchers_count": 45,
                "open_issues_count": 8,
                "size": 1024,
                "updated_at": "2024-01-15T10:30:00Z",
                "language": "Python",
                "topics": ["api", "betting", "odds", "sports"],
                "license": {
                    "key": "mit",
                    "name": "MIT License",
                    "spdx_id": "MIT",
                    "url": "https://api.github.com/licenses/mit",
                },
            }
        ],
    }


@pytest.fixture
def mock_huggingface_api_response():
    """Mock Hugging Face API response"""
    return [
        {
            "id": "huggingface/sports-prediction-model",
            "modelId": "huggingface/sports-prediction-model",
            "author": "huggingface",
            "sha": "abc123def456",
            "lastModified": "2024-01-10T15:45:00.000Z",
            "tags": ["pytorch", "sports", "prediction"],
            "downloads": 1500,
            "likes": 89,
            "library_name": "pytorch",
        }
    ]


@pytest.fixture
def mock_file_system(temp_dir):
    """Mock file system with sample repository structure"""
    repo_dir = temp_dir / "sample_repo"
    repo_dir.mkdir()

    # Create sample files
    (repo_dir / "requirements.txt").write_text("requests==2.31.0\nnumpy>=1.21.0\npandas>=1.3.0\n")
    (repo_dir / "setup.py").write_text(
        """
from setuptools import setup, find_packages

setup(
    name="betting-api",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.30.0",
        "numpy>=1.21.0"
    ]
)
"""
    )
    (repo_dir / "pyproject.toml").write_text(
        """
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "betting-api"
version = "1.0.0"
dependencies = [
    "requests>=2.30.0",
    "click>=8.0.0"
]
"""
    )

    # Create source code with some security issues for testing
    src_dir = repo_dir / "src" / "betting_api"
    src_dir.mkdir(parents=True)

    (src_dir / "__init__.py").write_text('__version__ = "1.0.0"')
    (src_dir / "main.py").write_text(
        """
import subprocess
import os

def get_odds(sport):
    # Security issue: subprocess with shell=True  
    cmd = f"curl -X GET https://api.example.com/odds/{sport}"
    result = subprocess.run(cmd, shell=True, capture_output=True)
    return result.stdout.decode()

def debug_assert(value):
    # Security issue: assert statement
    assert value > 0, "Value must be positive"
    return True
"""
    )

    return repo_dir


# Environment variable mocking
@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for tests"""
    env_vars = {
        "GITHUB_TOKEN": "test_github_token",
        "HUGGINGFACE_TOKEN": "test_hf_token",
        "EDGEFINDER_OUTPUT_DIR": "/tmp/edgefinder/output",
        "EDGEFINDER_DOWNLOADS_DIR": "/tmp/edgefinder/downloads",
    }

    with patch.dict(os.environ, env_vars):
        yield env_vars


# Async test utilities
@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    import asyncio

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
