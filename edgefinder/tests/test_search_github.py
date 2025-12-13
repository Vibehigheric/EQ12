"""
Unit tests for EdgeFinder GitHub search functionality
"""

import asyncio
from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from edgefinder.config import Config, GitHubConfig
from edgefinder.models import (
    Candidate,
    LicenseCompatibility,
    SearchCriteria,
    SourceType,
)
from edgefinder.search_github import GitHubRateLimiter, GitHubSearcher


class TestGitHubRateLimiter:
    """Test GitHub rate limiter"""

    def test_rate_limiter_creation(self):
        """Test creating rate limiter"""
        limiter = GitHubRateLimiter(requests_per_hour=1000, window_seconds=3600)

        assert limiter.requests_per_hour == 1000
        assert limiter.window_seconds == 3600
        assert limiter.request_count == 0

    @pytest.mark.asyncio
    async def test_rate_limiter_allows_requests(self):
        """Test rate limiter allows requests under limit"""
        limiter = GitHubRateLimiter(requests_per_hour=100, window_seconds=3600)

        # Should allow requests under limit
        await limiter.acquire()
        assert limiter.request_count == 1

        await limiter.acquire()
        assert limiter.request_count == 2

    @pytest.mark.asyncio
    async def test_rate_limiter_reset(self):
        """Test rate limiter resets after window"""
        limiter = GitHubRateLimiter(requests_per_hour=2, window_seconds=1)

        # Use up limit
        await limiter.acquire()
        await limiter.acquire()
        assert limiter.request_count == 2

        # Wait for window reset
        await asyncio.sleep(1.1)

        # Should reset and allow new requests
        await limiter.acquire()
        assert limiter.request_count == 1


class TestGitHubSearcher:
    """Test GitHub searcher functionality"""

    @pytest.fixture
    def github_config(self):
        """GitHub configuration for testing"""
        return GitHubConfig(
            token="test_token_123",
            base_url="https://api.github.com",
            rate_limit_requests=1000,
            rate_limit_window=3600,
        )

    @pytest.fixture
    def config_with_github(self, github_config, temp_dir):
        """Config with GitHub settings"""
        return Config(output_dir=str(temp_dir / "output"), github=github_config)

    @pytest.fixture
    def searcher(self, config_with_github):
        """GitHub searcher instance"""
        return GitHubSearcher(config_with_github)

    def test_searcher_initialization(self, searcher, config_with_github):
        """Test GitHub searcher initialization"""
        assert searcher.config == config_with_github
        assert searcher.base_url == "https://api.github.com"
        assert searcher.session is None  # Not initialized yet

    @pytest.mark.asyncio
    async def test_searcher_session_management(self, searcher):
        """Test searcher session lifecycle"""
        # Session starts as None
        assert searcher.session is None

        # Enter context manager
        async with searcher:
            assert searcher.session is not None
            assert isinstance(searcher.session, httpx.AsyncClient)

        # Session should be closed after context
        # Note: We can't easily test session.is_closed without implementation details

    def test_build_search_url(self, searcher):
        """Test building GitHub search URL"""
        criteria = SearchCriteria(keywords=["api", "betting"], languages=["python"], min_stars=10)

        url = searcher._build_search_url(criteria)

        # Should contain base search URL
        assert url.startswith("https://api.github.com/search/repositories")

        # Should contain query parameters
        assert "api betting" in url
        assert "language:python" in url
        assert "stars:>=10" in url

    def test_build_search_url_with_date(self, searcher):
        """Test building search URL with date filter"""
        criteria = SearchCriteria(
            keywords=["machine-learning"], updated_since=datetime(2024, 1, 1, tzinfo=UTC)
        )

        url = searcher._build_search_url(criteria)

        assert "machine-learning" in url
        assert "pushed:>=2024-01-01" in url

    def test_build_search_url_multiple_languages(self, searcher):
        """Test search URL with multiple languages"""
        criteria = SearchCriteria(
            keywords=["neural", "network"], languages=["python", "javascript", "typescript"]
        )

        url = searcher._build_search_url(criteria)

        # Should contain language filters
        assert "language:python" in url
        assert "language:javascript" in url
        assert "language:typescript" in url

    def test_parse_license_compatibility(self, searcher):
        """Test parsing license compatibility"""
        # MIT license should be compatible
        mit_license = {"key": "mit", "name": "MIT License", "spdx_id": "MIT"}
        compatibility = searcher._parse_license_compatibility(mit_license)
        assert compatibility == LicenseCompatibility.COMPATIBLE

        # GPL should be incompatible
        gpl_license = {
            "key": "gpl-3.0",
            "name": "GNU General Public License v3.0",
            "spdx_id": "GPL-3.0",
        }
        compatibility = searcher._parse_license_compatibility(gpl_license)
        assert compatibility == LicenseCompatibility.INCOMPATIBLE

        # Unknown license
        unknown_license = {"key": "custom", "name": "Custom License"}
        compatibility = searcher._parse_license_compatibility(unknown_license)
        assert compatibility == LicenseCompatibility.UNKNOWN

    def test_parse_repository_from_api_response(self, searcher, mock_github_api_response):
        """Test parsing repository from GitHub API response"""
        repo_data = mock_github_api_response["items"][0]
        candidate = searcher._parse_repository(repo_data)

        assert isinstance(candidate, Candidate)
        assert candidate.source == SourceType.GITHUB
        assert candidate.full_name == "example/betting-api"
        assert candidate.name == "betting-api"
        assert candidate.description == "A Python API for sports betting odds"
        assert candidate.stats.stars == 125
        assert candidate.stats.forks == 23
        assert candidate.license_info.spdx_id == "MIT"
        assert candidate.license_info.compatibility == LicenseCompatibility.COMPATIBLE

    @pytest.mark.asyncio
    async def test_search_repositories_success(self, searcher, mock_github_api_response):
        """Test successful repository search"""
        criteria = SearchCriteria(
            keywords=["betting", "api"], languages=["python"], max_results_per_source=10
        )

        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_github_api_response
        mock_response.headers = {"X-RateLimit-Remaining": "4999"}

        with patch.object(searcher, "session") as mock_session:
            mock_session.get = AsyncMock(return_value=mock_response)

            candidates = await searcher.search_repositories(criteria)

            assert len(candidates) == 1
            assert candidates[0].full_name == "example/betting-api"
            assert candidates[0].source == SourceType.GITHUB

            # Verify API call
            mock_session.get.assert_called_once()
            call_args = mock_session.get.call_args
            assert "betting api" in call_args[0][0]  # URL contains keywords

    @pytest.mark.asyncio
    async def test_search_repositories_with_license_filter(
        self, searcher, mock_github_api_response
    ):
        """Test repository search with license filtering"""
        criteria = SearchCriteria(keywords=["test"], license_allowlist=["MIT", "Apache-2.0"])

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_github_api_response
        mock_response.headers = {"X-RateLimit-Remaining": "4999"}

        with patch.object(searcher, "session") as mock_session:
            mock_session.get = AsyncMock(return_value=mock_response)

            candidates = await searcher.search_repositories(criteria)

            # Should include MIT licensed repo
            assert len(candidates) == 1
            assert candidates[0].license_info.spdx_id == "MIT"

    @pytest.mark.asyncio
    async def test_search_repositories_license_filtering_excludes_incompatible(self, searcher):
        """Test that incompatible licenses are filtered out"""
        criteria = SearchCriteria(keywords=["test"], license_allowlist=["MIT"])  # Only allow MIT

        # Mock response with GPL licensed repo
        gpl_response = {
            "total_count": 1,
            "items": [
                {
                    "id": 123,
                    "name": "gpl-repo",
                    "full_name": "example/gpl-repo",
                    "description": "GPL licensed repository",
                    "html_url": "https://github.com/example/gpl-repo",
                    "clone_url": "https://github.com/example/gpl-repo.git",
                    "stargazers_count": 50,
                    "forks_count": 10,
                    "watchers_count": 25,
                    "open_issues_count": 2,
                    "size": 512,
                    "updated_at": "2024-01-15T10:30:00Z",
                    "language": "Python",
                    "topics": ["test"],
                    "license": {
                        "key": "gpl-3.0",
                        "name": "GNU General Public License v3.0",
                        "spdx_id": "GPL-3.0",
                    },
                }
            ],
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = gpl_response
        mock_response.headers = {"X-RateLimit-Remaining": "4999"}

        with patch.object(searcher, "session") as mock_session:
            mock_session.get = AsyncMock(return_value=mock_response)

            candidates = await searcher.search_repositories(criteria)

            # Should filter out GPL repo
            assert len(candidates) == 0

    @pytest.mark.asyncio
    async def test_search_repositories_rate_limit_error(self, searcher):
        """Test handling rate limit errors"""
        criteria = SearchCriteria(keywords=["test"])

        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.headers = {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1640995200"}
        mock_response.json.return_value = {"message": "API rate limit exceeded"}

        with patch.object(searcher, "session") as mock_session:
            mock_session.get = AsyncMock(return_value=mock_response)

            with pytest.raises(Exception, match="rate limit"):
                await searcher.search_repositories(criteria)

    @pytest.mark.asyncio
    async def test_search_repositories_http_error(self, searcher):
        """Test handling HTTP errors"""
        criteria = SearchCriteria(keywords=["test"])

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Internal server error"}

        with patch.object(searcher, "session") as mock_session:
            mock_session.get = AsyncMock(return_value=mock_response)

            with pytest.raises(Exception):
                await searcher.search_repositories(criteria)

    @pytest.mark.asyncio
    async def test_search_repositories_network_error(self, searcher):
        """Test handling network errors"""
        criteria = SearchCriteria(keywords=["test"])

        with patch.object(searcher, "session") as mock_session:
            mock_session.get = AsyncMock(side_effect=httpx.RequestError("Network error"))

            with pytest.raises(httpx.RequestError):
                await searcher.search_repositories(criteria)

    @pytest.mark.asyncio
    async def test_search_repositories_empty_response(self, searcher):
        """Test handling empty search results"""
        criteria = SearchCriteria(keywords=["nonexistent"])

        empty_response = {"total_count": 0, "incomplete_results": False, "items": []}

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = empty_response
        mock_response.headers = {"X-RateLimit-Remaining": "4999"}

        with patch.object(searcher, "session") as mock_session:
            mock_session.get = AsyncMock(return_value=mock_response)

            candidates = await searcher.search_repositories(criteria)

            assert len(candidates) == 0

    def test_calculate_keyword_matches(self, searcher):
        """Test keyword matching calculation"""
        repo_data = {
            "name": "betting-api",
            "description": "Python API for sports betting odds",
            "topics": ["api", "sports", "gambling"],
        }

        criteria = SearchCriteria(keywords=["betting", "api", "odds", "nonmatch"])

        matches = searcher._calculate_keyword_matches(repo_data, criteria)

        # Should match: betting (in name and description), api (in topics and description), odds (in description)
        expected_matches = ["betting", "api", "odds"]
        assert set(matches) == set(expected_matches)
        assert "nonmatch" not in matches

    @pytest.mark.asyncio
    async def test_search_pagination(self, searcher):
        """Test search result pagination"""
        criteria = SearchCriteria(
            keywords=["popular"], max_results_per_source=150  # More than GitHub's per_page limit
        )

        # Mock first page response
        first_page = {
            "total_count": 200,
            "items": [
                {
                    "id": i,
                    "name": f"repo-{i}",
                    "full_name": f"user/repo-{i}",
                    "html_url": f"https://github.com/user/repo-{i}",
                    "clone_url": f"https://github.com/user/repo-{i}.git",
                    "stargazers_count": 100 - i,
                    "forks_count": 10,
                    "watchers_count": 20,
                    "open_issues_count": 1,
                    "size": 1024,
                    "updated_at": "2024-01-15T10:30:00Z",
                    "language": "Python",
                    "topics": ["popular"],
                }
                for i in range(100)
            ],  # GitHub max per page
        }

        # Mock second page response
        second_page = {
            "total_count": 200,
            "items": [
                {
                    "id": i + 100,
                    "name": f"repo-{i + 100}",
                    "full_name": f"user/repo-{i + 100}",
                    "html_url": f"https://github.com/user/repo-{i + 100}",
                    "clone_url": f"https://github.com/user/repo-{i + 100}.git",
                    "stargazers_count": 100 - (i + 100),
                    "forks_count": 10,
                    "watchers_count": 20,
                    "open_issues_count": 1,
                    "size": 1024,
                    "updated_at": "2024-01-15T10:30:00Z",
                    "language": "Python",
                    "topics": ["popular"],
                }
                for i in range(50)
            ],  # Remaining results
        }

        responses = [first_page, second_page]
        response_index = 0

        def mock_get_side_effect(*args, **kwargs):
            nonlocal response_index
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = responses[response_index]
            mock_resp.headers = {"X-RateLimit-Remaining": "4999"}
            response_index += 1
            return mock_resp

        with patch.object(searcher, "session") as mock_session:
            mock_session.get = AsyncMock(side_effect=mock_get_side_effect)

            candidates = await searcher.search_repositories(criteria)

            # Should get 150 results (as requested in max_results_per_source)
            assert len(candidates) == 150

            # Should make 2 API calls (pagination)
            assert mock_session.get.call_count == 2
