"""
GitHub Repository Search Implementation
Ethical search of public GitHub repositories using official APIs
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import Config
from .models import (
    AuditLogEntry,
    Candidate,
    LicenseCompatibility,
    LicenseInfo,
    RepositoryStats,
    SearchCriteria,
    SourceType,
)

logger = logging.getLogger(__name__)


class GitHubSearchError(Exception):
    """GitHub search related errors"""

    pass


class GitHubRateLimitError(GitHubSearchError):
    """GitHub rate limit exceeded"""

    pass


class GitHubSearcher:
    """
    Ethical GitHub repository searcher using official REST API

    Respects rate limits, uses authentication when available,
    and only accesses public repositories.
    """

    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.github.base_url
        self.token = config.github.token
        self.rate_limit_remaining = None
        self.rate_limit_reset = None
        self.audit_log: list[AuditLogEntry] = []

        # Setup HTTP client with proper headers
        headers = {
            "User-Agent": "EdgeFinder/1.0.0 (Ethical Repository Analysis)",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
            logger.info("Using authenticated GitHub API requests")
        else:
            logger.warning("Using unauthenticated GitHub API (very low rate limit)")

        self.client = httpx.AsyncClient(
            headers=headers,
            timeout=self.config.github.timeout_seconds,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def _log_api_call(
        self, endpoint: str, response_code: int, details: dict[str, Any] | None = None
    ):
        """Log API call for audit trail"""
        entry = AuditLogEntry(
            action="github_api_call",
            api_endpoint=endpoint,
            response_code=response_code,
            rate_limit_remaining=self.rate_limit_remaining,
            details=details or {},
        )
        self.audit_log.append(entry)

    def _update_rate_limit_info(self, response: httpx.Response):
        """Update rate limit information from response headers"""
        self.rate_limit_remaining = int(response.headers.get("x-ratelimit-remaining", 0))
        self.rate_limit_reset = int(response.headers.get("x-ratelimit-reset", 0))

        # Log rate limit status
        logger.debug(f"GitHub rate limit: {self.rate_limit_remaining} remaining")

        # Warn if approaching rate limit
        if self.rate_limit_remaining < self.config.github.rate_limit_buffer:
            logger.warning(
                f"Approaching GitHub rate limit: {self.rate_limit_remaining} requests remaining"
            )

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10), reraise=True
    )
    async def _make_request(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Make authenticated request to GitHub API with retry logic

        Args:
            url: API endpoint URL
            params: Query parameters

        Returns:
            JSON response data

        Raises:
            GitHubRateLimitError: If rate limit exceeded
            GitHubSearchError: If request fails
        """
        try:
            response = await self.client.get(url, params=params)
            self._update_rate_limit_info(response)
            self._log_api_call(url, response.status_code, {"params": params})

            # Handle rate limiting
            if response.status_code == 429:
                raise GitHubRateLimitError("GitHub rate limit exceeded")

            # Handle other client/server errors
            if response.status_code >= 400:
                error_data = (
                    response.json()
                    if response.headers.get("content-type", "").startswith("application/json")
                    else {}
                )
                raise GitHubSearchError(
                    f"GitHub API error {response.status_code}: {error_data.get('message', 'Unknown error')}"
                )

            return response.json()

        except httpx.HTTPError as e:
            raise GitHubSearchError(f"HTTP error during GitHub request: {e}") from e
        except Exception as e:
            raise GitHubSearchError(f"Unexpected error during GitHub request: {e}") from e

    def _build_search_query(self, criteria: SearchCriteria) -> str:
        """
        Build GitHub search query string from criteria

        Args:
            criteria: Search criteria

        Returns:
            GitHub search query string
        """
        query_parts = []

        # Add keywords
        if criteria.keywords:
            keywords_str = " ".join(f'"{kw}"' if " " in kw else kw for kw in criteria.keywords)
            query_parts.append(keywords_str)

        # Add language filters
        for lang in criteria.languages:
            query_parts.append(f"language:{lang}")

        # Add stars filter
        if criteria.min_stars > 0:
            query_parts.append(f"stars:>={criteria.min_stars}")

        # Add updated date filter
        if criteria.updated_since:
            date_str = criteria.updated_since.strftime("%Y-%m-%d")
            query_parts.append(f"pushed:>={date_str}")

        # Add other quality filters
        query_parts.extend(
            [
                "is:public",  # Only public repositories
                "archived:false",  # Exclude archived repositories
                "mirror:false",  # Exclude mirror repositories
            ]
        )

        return " ".join(query_parts)

    async def _get_repository_details(self, owner: str, repo: str) -> dict[str, Any]:
        """
        Get detailed repository information

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Detailed repository data
        """
        url = f"{self.base_url}/repos/{owner}/{repo}"
        return await self._make_request(url)

    async def _get_repository_languages(self, owner: str, repo: str) -> dict[str, int]:
        """
        Get repository programming languages

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Dictionary of language -> bytes of code
        """
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/languages"
            return await self._make_request(url)
        except GitHubSearchError:
            logger.debug(f"Failed to get languages for {owner}/{repo}")
            return {}

    async def _get_repository_license(self, license_data: dict[str, Any]) -> LicenseInfo | None:
        """
        Parse repository license information

        Args:
            license_data: License data from GitHub API

        Returns:
            LicenseInfo object or None
        """
        if not license_data:
            return LicenseInfo(compatibility=LicenseCompatibility.UNKNOWN)

        license_name = license_data.get("spdx_id") or license_data.get("name")

        # Determine compatibility
        compatibility = LicenseCompatibility.UNKNOWN
        if license_name:
            if self.config.is_license_allowed(license_name):
                compatibility = LicenseCompatibility.COMPATIBLE
            elif self.config.is_license_blocked(license_name):
                compatibility = LicenseCompatibility.INCOMPATIBLE
            else:
                compatibility = LicenseCompatibility.REQUIRES_REVIEW

        return LicenseInfo(
            name=license_data.get("name"),
            spdx_id=license_data.get("spdx_id"),
            compatibility=compatibility,
            url=license_data.get("html_url"),
            requires_attribution=True,  # Most licenses require attribution
            commercial_use_allowed=compatibility == LicenseCompatibility.COMPATIBLE,
        )

    def _parse_repository_data(self, repo_data: dict[str, Any]) -> Candidate:
        """
        Parse GitHub repository data into Candidate model

        Args:
            repo_data: Repository data from GitHub API

        Returns:
            Candidate object
        """
        # Parse timestamps
        created_at = (
            datetime.fromisoformat(repo_data["created_at"].replace("Z", "+00:00"))
            if repo_data.get("created_at")
            else None
        )
        updated_at = (
            datetime.fromisoformat(repo_data["updated_at"].replace("Z", "+00:00"))
            if repo_data.get("updated_at")
            else None
        )
        pushed_at = (
            datetime.fromisoformat(repo_data["pushed_at"].replace("Z", "+00:00"))
            if repo_data.get("pushed_at")
            else None
        )

        # Create repository stats
        stats = RepositoryStats(
            stars=repo_data.get("stargazers_count", 0),
            forks=repo_data.get("forks_count", 0),
            watchers=repo_data.get("watchers_count", 0),
            open_issues=repo_data.get("open_issues_count", 0),
            size_kb=repo_data.get("size", 0),
            default_branch=repo_data.get("default_branch", "main"),
            created_at=created_at,
            updated_at=updated_at,
            pushed_at=pushed_at,
        )

        # Parse license information
        license_info = None
        if repo_data.get("license"):
            license_info = self._get_repository_license(repo_data["license"])

        # Extract topics (GitHub repository topics)
        topics = repo_data.get("topics", [])

        return Candidate(
            source=SourceType.GITHUB,
            owner=repo_data["owner"]["login"],
            name=repo_data["name"],
            full_name=repo_data["full_name"],
            description=repo_data.get("description"),
            url=repo_data["html_url"],
            clone_url=repo_data.get("clone_url"),
            homepage=repo_data.get("homepage"),
            stats=stats,
            license_info=license_info,
            topics=topics,
        )

    async def search_repositories(self, criteria: SearchCriteria) -> list[Candidate]:
        """
        Search GitHub repositories based on criteria

        Args:
            criteria: Search criteria

        Returns:
            List of candidate repositories

        Raises:
            GitHubSearchError: If search fails
            GitHubRateLimitError: If rate limit exceeded
        """
        logger.info(f"Searching GitHub repositories with keywords: {criteria.keywords}")

        query = self._build_search_query(criteria)
        logger.debug(f"GitHub search query: {query}")

        candidates = []
        page = 1
        per_page = min(100, criteria.max_results_per_source)  # GitHub max is 100

        while len(candidates) < criteria.max_results_per_source:
            # Build search URL
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": per_page,
                "page": page,
            }

            url = f"{self.base_url}/search/repositories"

            try:
                # Add delay between requests to be respectful
                if page > 1:
                    delay = self.config.get_rate_limit_delay("github")
                    await asyncio.sleep(delay)

                # Make search request
                data = await self._make_request(url, params)

                repositories = data.get("items", [])
                if not repositories:
                    logger.debug("No more repositories found")
                    break

                # Process each repository
                for repo_data in repositories:
                    if len(candidates) >= criteria.max_results_per_source:
                        break

                    try:
                        # Get detailed repository information and languages
                        owner = repo_data["owner"]["login"]
                        repo_name = repo_data["name"]

                        # Get additional details in parallel
                        detail_task = self._get_repository_details(owner, repo_name)
                        languages_task = self._get_repository_languages(owner, repo_name)

                        detailed_data, languages = await asyncio.gather(
                            detail_task, languages_task, return_exceptions=True
                        )

                        # Use detailed data if available, fallback to search result
                        repo_info = (
                            detailed_data if not isinstance(detailed_data, Exception) else repo_data
                        )
                        repo_languages = languages if not isinstance(languages, Exception) else {}

                        # Parse repository data
                        candidate = self._parse_repository_data(repo_info)
                        candidate.languages = repo_languages

                        # Filter by license if specified
                        if (
                            criteria.license_allowlist
                            and candidate.license_info
                            and candidate.license_info.spdx_id
                            and not any(
                                allowed.upper() == candidate.license_info.spdx_id.upper()
                                for allowed in criteria.license_allowlist
                            )
                        ):
                            logger.debug(
                                f"Skipping {candidate.full_name} due to license incompatibility"
                            )
                            continue

                        candidates.append(candidate)
                        logger.debug(f"Added candidate: {candidate.full_name}")

                    except Exception as e:
                        logger.warning(
                            f"Failed to process repository {repo_data.get('full_name', 'unknown')}: {e}"
                        )
                        continue

                # Check if we've reached the end
                if len(repositories) < per_page:
                    break

                page += 1

                # GitHub search API has a maximum of 1000 results
                if page > 10:  # 10 pages * 100 results = 1000 max
                    logger.warning("Reached GitHub search API limit (1000 results)")
                    break

            except GitHubRateLimitError:
                logger.error("GitHub rate limit exceeded")
                break
            except GitHubSearchError as e:
                logger.error(f"GitHub search error: {e}")
                break

        logger.info(f"Found {len(candidates)} GitHub repositories")
        return candidates

    async def get_repository_archive_url(self, owner: str, repo: str, ref: str = "HEAD") -> str:
        """
        Get download URL for repository archive

        Args:
            owner: Repository owner
            repo: Repository name
            ref: Git reference (branch, tag, or commit)

        Returns:
            Archive download URL
        """
        # GitHub provides archive download URLs
        return f"{self.base_url}/repos/{owner}/{repo}/zipball/{ref}"

    def get_audit_log(self) -> list[AuditLogEntry]:
        """Get audit log of all API calls"""
        return self.audit_log.copy()

    async def check_rate_limit(self) -> dict[str, int]:
        """
        Check current rate limit status

        Returns:
            Rate limit information
        """
        try:
            url = f"{self.base_url}/rate_limit"
            data = await self._make_request(url)
            return data.get("rate", {})
        except Exception as e:
            logger.error(f"Failed to check rate limit: {e}")
            return {"remaining": 0, "limit": 0}
