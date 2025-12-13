"""
Hugging Face Repository Search Implementation
Ethical search of public Hugging Face repositories using official APIs and HTML fallback
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Any
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
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


class HuggingFaceSearchError(Exception):
    """Hugging Face search related errors"""

    pass


class HuggingFaceRateLimitError(HuggingFaceSearchError):
    """Hugging Face rate limit exceeded"""

    pass


class HuggingFaceSearcher:
    """
    Ethical Hugging Face repository searcher using official API and HTML fallback

    Searches both models and spaces repositories while respecting rate limits
    and only accessing public content.
    """

    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.huggingface.base_url
        self.api_base_url = config.huggingface.api_base_url
        self.token = config.huggingface.token
        self.audit_log: list[AuditLogEntry] = []

        # Setup HTTP client with proper headers
        headers = {
            "User-Agent": "EdgeFinder/1.0.0 (Ethical Repository Analysis)",
            "Accept": "application/json",
        }

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
            logger.info("Using authenticated Hugging Face API requests")
        else:
            logger.warning("Using unauthenticated Hugging Face requests")

        self.client = httpx.AsyncClient(
            headers=headers,
            timeout=self.config.huggingface.timeout_seconds,
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
            action="huggingface_api_call",
            api_endpoint=endpoint,
            response_code=response_code,
            details=details or {},
        )
        self.audit_log.append(entry)

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10), reraise=True
    )
    async def _make_request(
        self, url: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """
        Make request to Hugging Face API with retry logic

        Args:
            url: API endpoint URL
            params: Query parameters

        Returns:
            JSON response data

        Raises:
            HuggingFaceRateLimitError: If rate limit exceeded
            HuggingFaceSearchError: If request fails
        """
        try:
            response = await self.client.get(url, params=params)
            self._log_api_call(url, response.status_code, {"params": params})

            # Handle rate limiting
            if response.status_code == 429:
                raise HuggingFaceRateLimitError("Hugging Face rate limit exceeded")

            # Handle other errors
            if response.status_code >= 400:
                raise HuggingFaceSearchError(f"Hugging Face API error {response.status_code}")

            return response.json()

        except httpx.HTTPError as e:
            raise HuggingFaceSearchError(f"HTTP error during Hugging Face request: {e}") from e
        except Exception as e:
            raise HuggingFaceSearchError(
                f"Unexpected error during Hugging Face request: {e}"
            ) from e

    async def _make_html_request(self, url: str) -> str:
        """
        Make HTML request for web scraping fallback (public pages only)

        Args:
            url: Web page URL

        Returns:
            HTML content
        """
        try:
            response = await self.client.get(url)
            self._log_api_call(url, response.status_code, {"type": "html_scraping"})

            if response.status_code >= 400:
                raise HuggingFaceSearchError(f"HTML request failed: {response.status_code}")

            return response.text

        except httpx.HTTPError as e:
            raise HuggingFaceSearchError(f"HTML request error: {e}") from e

    def _extract_license_from_html(self, html_content: str) -> LicenseInfo | None:
        """
        Extract license information from repository HTML page

        Args:
            html_content: HTML content of the repository page

        Returns:
            LicenseInfo object or None
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Look for license in meta tags or specific elements
            license_elements = soup.find_all(text=re.compile(r"license", re.IGNORECASE))

            for element in license_elements:
                # Common license patterns
                license_patterns = {
                    "MIT": r"\bMIT\b",
                    "Apache-2.0": r"\bApache-2\.0\b|\bApache License 2\.0\b",
                    "GPL-3.0": r"\bGPL-3\.0\b|\bGPL v3\b",
                    "BSD-3-Clause": r"\bBSD-3-Clause\b|\bBSD 3-Clause\b",
                    "GPL-2.0": r"\bGPL-2\.0\b|\bGPL v2\b",
                }

                text_content = str(element).lower()
                for license_name, pattern in license_patterns.items():
                    if re.search(pattern, text_content, re.IGNORECASE):
                        # Determine compatibility
                        compatibility = LicenseCompatibility.UNKNOWN
                        if self.config.is_license_allowed(license_name):
                            compatibility = LicenseCompatibility.COMPATIBLE
                        elif self.config.is_license_blocked(license_name):
                            compatibility = LicenseCompatibility.INCOMPATIBLE
                        else:
                            compatibility = LicenseCompatibility.REQUIRES_REVIEW

                        return LicenseInfo(
                            name=license_name,
                            spdx_id=license_name,
                            compatibility=compatibility,
                            requires_attribution=True,
                            commercial_use_allowed=compatibility == LicenseCompatibility.COMPATIBLE,
                        )

            return LicenseInfo(compatibility=LicenseCompatibility.UNKNOWN)

        except Exception as e:
            logger.debug(f"Failed to extract license from HTML: {e}")
            return LicenseInfo(compatibility=LicenseCompatibility.UNKNOWN)

    def _parse_model_data(self, model_data: dict[str, Any]) -> Candidate:
        """
        Parse Hugging Face model data into Candidate model

        Args:
            model_data: Model data from Hugging Face API

        Returns:
            Candidate object
        """
        model_id = model_data.get("id", "")
        model_name = model_id.split("/")[-1] if "/" in model_id else model_id
        owner = model_id.split("/")[0] if "/" in model_id else "huggingface"

        # Parse timestamps
        created_at = None
        updated_at = None
        if model_data.get("createdAt"):
            created_at = datetime.fromisoformat(model_data["createdAt"].replace("Z", "+00:00"))
        if model_data.get("lastModified"):
            updated_at = datetime.fromisoformat(model_data["lastModified"].replace("Z", "+00:00"))

        # Create repository stats
        stats = RepositoryStats(
            stars=model_data.get("likes", 0),
            forks=0,  # HF doesn't track forks the same way
            watchers=model_data.get("downloads", 0),
            open_issues=0,
            size_kb=0,  # Would need additional API call
            created_at=created_at,
            updated_at=updated_at,
            pushed_at=updated_at,
        )

        # Extract tags as topics
        tags = model_data.get("tags", [])

        return Candidate(
            source=SourceType.HUGGINGFACE,
            owner=owner,
            name=model_name,
            full_name=model_id,
            description=model_data.get("description"),
            url=f"{self.base_url}/{model_id}",
            clone_url=f"https://huggingface.co/{model_id}.git",
            stats=stats,
            topics=tags,
            # Will need to fetch license separately
            license_info=LicenseInfo(compatibility=LicenseCompatibility.UNKNOWN),
        )

    def _parse_space_data(self, space_data: dict[str, Any]) -> Candidate:
        """
        Parse Hugging Face space data into Candidate model

        Args:
            space_data: Space data from Hugging Face API

        Returns:
            Candidate object
        """
        space_id = space_data.get("id", "")
        space_name = space_id.split("/")[-1] if "/" in space_id else space_id
        owner = space_id.split("/")[0] if "/" in space_id else "huggingface"

        # Parse timestamps
        created_at = None
        updated_at = None
        if space_data.get("createdAt"):
            created_at = datetime.fromisoformat(space_data["createdAt"].replace("Z", "+00:00"))
        if space_data.get("lastModified"):
            updated_at = datetime.fromisoformat(space_data["lastModified"].replace("Z", "+00:00"))

        # Create repository stats
        stats = RepositoryStats(
            stars=space_data.get("likes", 0),
            forks=0,
            watchers=0,
            open_issues=0,
            size_kb=0,
            created_at=created_at,
            updated_at=updated_at,
            pushed_at=updated_at,
        )

        # Extract tags as topics
        tags = space_data.get("tags", [])

        return Candidate(
            source=SourceType.HUGGINGFACE,
            owner=owner,
            name=space_name,
            full_name=space_id,
            description=space_data.get("description"),
            url=f"{self.base_url}/spaces/{space_id}",
            clone_url=f"https://huggingface.co/spaces/{space_id}.git",
            stats=stats,
            topics=tags,
            license_info=LicenseInfo(compatibility=LicenseCompatibility.UNKNOWN),
        )

    async def _search_models(self, criteria: SearchCriteria) -> list[Candidate]:
        """
        Search Hugging Face models

        Args:
            criteria: Search criteria

        Returns:
            List of model candidates
        """
        logger.info("Searching Hugging Face models")

        candidates = []

        # Build search parameters
        params = {
            "limit": min(100, criteria.max_results_per_source),
            "sort": "downloads",
            "direction": -1,
        }

        # Add search query
        if criteria.keywords:
            params["search"] = " ".join(criteria.keywords)

        # Add filters
        filters = []

        # Language filters (map to HF pipeline tags)
        language_to_pipeline = {
            "python": "text-generation",
            "javascript": "text-generation",
            "rust": "text-generation",
        }

        for lang in criteria.languages:
            pipeline = language_to_pipeline.get(lang.lower())
            if pipeline:
                filters.append(f"pipeline_tag:{pipeline}")

        if filters:
            params["filter"] = ",".join(filters)

        try:
            url = urljoin(self.api_base_url, "/models")
            data = await self._make_request(url, params)

            if isinstance(data, list):
                for model_data in data:
                    if (
                        len(candidates) >= criteria.max_results_per_source // 2
                    ):  # Split quota between models and spaces
                        break

                    try:
                        candidate = self._parse_model_data(model_data)

                        # Try to get license information
                        try:
                            model_url = candidate.url
                            html_content = await self._make_html_request(model_url)
                            candidate.license_info = self._extract_license_from_html(html_content)
                        except Exception as e:
                            logger.debug(f"Failed to get license for {candidate.full_name}: {e}")

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
                        logger.debug(f"Added model candidate: {candidate.full_name}")

                    except Exception as e:
                        logger.warning(
                            f"Failed to process model {model_data.get('id', 'unknown')}: {e}"
                        )
                        continue

        except Exception as e:
            logger.error(f"Failed to search Hugging Face models: {e}")

        return candidates

    async def _search_spaces(self, criteria: SearchCriteria) -> list[Candidate]:
        """
        Search Hugging Face spaces

        Args:
            criteria: Search criteria

        Returns:
            List of space candidates
        """
        logger.info("Searching Hugging Face spaces")

        candidates = []

        # Build search parameters
        params = {
            "limit": min(100, criteria.max_results_per_source),
            "sort": "likes",
            "direction": -1,
        }

        # Add search query
        if criteria.keywords:
            params["search"] = " ".join(criteria.keywords)

        try:
            url = urljoin(self.api_base_url, "/spaces")
            data = await self._make_request(url, params)

            if isinstance(data, list):
                for space_data in data:
                    if (
                        len(candidates) >= criteria.max_results_per_source // 2
                    ):  # Split quota between models and spaces
                        break

                    try:
                        candidate = self._parse_space_data(space_data)

                        # Try to get license information
                        try:
                            space_url = candidate.url
                            html_content = await self._make_html_request(space_url)
                            candidate.license_info = self._extract_license_from_html(html_content)
                        except Exception as e:
                            logger.debug(f"Failed to get license for {candidate.full_name}: {e}")

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
                        logger.debug(f"Added space candidate: {candidate.full_name}")

                    except Exception as e:
                        logger.warning(
                            f"Failed to process space {space_data.get('id', 'unknown')}: {e}"
                        )
                        continue

        except Exception as e:
            logger.error(f"Failed to search Hugging Face spaces: {e}")

        return candidates

    async def search_repositories(self, criteria: SearchCriteria) -> list[Candidate]:
        """
        Search Hugging Face repositories (models and spaces)

        Args:
            criteria: Search criteria

        Returns:
            List of candidate repositories

        Raises:
            HuggingFaceSearchError: If search fails
            HuggingFaceRateLimitError: If rate limit exceeded
        """
        logger.info(f"Searching Hugging Face repositories with keywords: {criteria.keywords}")

        # Search both models and spaces in parallel
        model_task = self._search_models(criteria)
        space_task = self._search_spaces(criteria)

        try:
            model_candidates, space_candidates = await asyncio.gather(
                model_task, space_task, return_exceptions=True
            )

            candidates = []

            # Add model candidates
            if not isinstance(model_candidates, Exception):
                candidates.extend(model_candidates)
            else:
                logger.warning(f"Model search failed: {model_candidates}")

            # Add space candidates
            if not isinstance(space_candidates, Exception):
                candidates.extend(space_candidates)
            else:
                logger.warning(f"Space search failed: {space_candidates}")

            # Sort by popularity (likes/stars)
            candidates.sort(key=lambda c: c.stats.stars, reverse=True)

            # Limit to max results
            candidates = candidates[: criteria.max_results_per_source]

            logger.info(f"Found {len(candidates)} Hugging Face repositories")
            return candidates

        except Exception as e:
            logger.error(f"Hugging Face search failed: {e}")
            return []

    def get_audit_log(self) -> list[AuditLogEntry]:
        """Get audit log of all API calls"""
        return self.audit_log.copy()

    async def get_repository_download_url(self, full_name: str, repo_type: str = "model") -> str:
        """
        Get download URL for Hugging Face repository

        Args:
            full_name: Full repository name (owner/repo)
            repo_type: Type of repository ("model" or "space")

        Returns:
            Download URL for repository archive
        """
        if repo_type == "space":
            return f"https://huggingface.co/spaces/{full_name}/resolve/main/archive.tar.gz"
        else:
            return f"https://huggingface.co/{full_name}/resolve/main/archive.tar.gz"
