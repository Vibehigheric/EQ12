"""
Repository Download System
Secure downloading of public repositories with safety checks and validation
"""

import asyncio
import hashlib
import logging
import os
import zipfile
from pathlib import Path
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import Config
from .models import AuditLogEntry, Candidate, SourceType

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    """Repository download related errors"""

    pass


class DownloadSizeError(DownloadError):
    """Download size exceeds limits"""

    pass


class DownloadSecurityError(DownloadError):
    """Security issue with download"""

    pass


class RepositoryDownloader:
    """
    Secure downloader for public repositories

    Downloads repositories with safety checks, size limits,
    and security validation.
    """

    def __init__(self, config: Config):
        self.config = config
        self.downloads_dir = Path(config.downloads_dir)
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
        self.audit_log: list[AuditLogEntry] = []

        # Setup HTTP client with proper limits
        self.client = httpx.AsyncClient(
            timeout=config.analysis.timeout_seconds,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            follow_redirects=True,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def _log_download_action(
        self, action: str, candidate_id: str, details: dict[str, Any] | None = None
    ):
        """Log download action for audit trail"""
        entry = AuditLogEntry(
            action=f"download_{action}", details={"candidate_id": candidate_id, **(details or {})}
        )
        self.audit_log.append(entry)

    def _get_download_path(self, candidate: Candidate, file_format: str = "zip") -> Path:
        """
        Get standardized download path for candidate

        Args:
            candidate: Repository candidate
            file_format: File format extension

        Returns:
            Path to download file
        """
        source_dir = self.downloads_dir / candidate.source.value
        source_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize filename
        safe_name = f"{candidate.owner}-{candidate.name}".replace("/", "-").replace("\\", "-")
        safe_name = "".join(c for c in safe_name if c.isalnum() or c in ".-_")

        filename = f"{safe_name}-main.{file_format}"
        return source_dir / filename

    def _validate_download_size(self, response: httpx.Response) -> None:
        """
        Validate download size against limits

        Args:
            response: HTTP response with content-length header

        Raises:
            DownloadSizeError: If file is too large
        """
        content_length = response.headers.get("content-length")
        if content_length:
            size_bytes = int(content_length)
            max_size_bytes = self.config.analysis.max_repo_size_mb * 1024 * 1024

            if size_bytes > max_size_bytes:
                raise DownloadSizeError(
                    f"Repository size ({size_bytes / 1024 / 1024:.1f}MB) "
                    f"exceeds limit ({self.config.analysis.max_repo_size_mb}MB)"
                )

    def _calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate SHA256 hash of downloaded file

        Args:
            file_path: Path to file

        Returns:
            SHA256 hash as hex string
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def _validate_archive_security(self, archive_path: Path) -> None:
        """
        Validate archive security to prevent zip bombs and path traversal

        Args:
            archive_path: Path to archive file

        Raises:
            DownloadSecurityError: If archive has security issues
        """
        try:
            with zipfile.ZipFile(archive_path, "r") as zip_file:
                # Check for zip bombs (excessive compression ratio)
                total_compressed = 0
                total_uncompressed = 0

                for info in zip_file.infolist():
                    total_compressed += info.compress_size
                    total_uncompressed += info.file_size

                    # Check for path traversal attempts
                    if os.path.isabs(info.filename) or ".." in info.filename:
                        raise DownloadSecurityError(
                            f"Archive contains suspicious path: {info.filename}"
                        )

                    # Check individual file size
                    max_file_size = self.config.analysis.max_file_size_mb * 1024 * 1024
                    if info.file_size > max_file_size:
                        raise DownloadSecurityError(
                            f"Archive contains file too large: {info.filename} "
                            f"({info.file_size / 1024 / 1024:.1f}MB)"
                        )

                # Check compression ratio
                if total_compressed > 0:
                    compression_ratio = total_uncompressed / total_compressed
                    if compression_ratio > 100:  # Arbitrary threshold
                        raise DownloadSecurityError(
                            f"Suspicious compression ratio: {compression_ratio:.1f}:1"
                        )

                # Check total uncompressed size
                max_total_size = self.config.analysis.max_repo_size_mb * 1024 * 1024
                if total_uncompressed > max_total_size:
                    raise DownloadSecurityError(
                        f"Archive uncompressed size too large: "
                        f"{total_uncompressed / 1024 / 1024:.1f}MB"
                    )

        except zipfile.BadZipFile as e:
            raise DownloadSecurityError(f"Invalid zip file: {e}") from e

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10), reraise=True
    )
    async def _download_file(self, url: str, output_path: Path) -> dict[str, Any]:
        """
        Download file with streaming and validation

        Args:
            url: Download URL
            output_path: Output file path

        Returns:
            Download metadata

        Raises:
            DownloadError: If download fails
            DownloadSizeError: If file is too large
            DownloadSecurityError: If file has security issues
        """
        logger.info(f"Downloading from {url} to {output_path}")

        try:
            # Make HEAD request first to check size
            head_response = await self.client.head(url)
            if head_response.status_code >= 400:
                # If HEAD fails, continue with GET (some servers don't support HEAD)
                logger.debug(f"HEAD request failed for {url}, proceeding with GET")
            else:
                self._validate_download_size(head_response)

            # Stream download
            async with self.client.stream("GET", url) as response:
                if response.status_code >= 400:
                    raise DownloadError(f"Download failed with status {response.status_code}")

                # Validate size from response headers
                self._validate_download_size(response)

                # Download with size tracking
                total_size = 0
                max_size_bytes = self.config.analysis.max_repo_size_mb * 1024 * 1024

                with open(output_path, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        total_size += len(chunk)

                        # Check size during download
                        if total_size > max_size_bytes:
                            f.close()
                            output_path.unlink(missing_ok=True)
                            raise DownloadSizeError(
                                f"Download exceeded size limit during transfer: "
                                f"{total_size / 1024 / 1024:.1f}MB"
                            )

                        f.write(chunk)

            # Calculate file hash
            file_hash = self._calculate_file_hash(output_path)

            # Validate archive security if it's a zip file
            if output_path.suffix.lower() == ".zip":
                self._validate_archive_security(output_path)

            return {
                "size_bytes": total_size,
                "sha256": file_hash,
                "content_type": response.headers.get("content-type", "unknown"),
            }

        except httpx.HTTPError as e:
            raise DownloadError(f"HTTP error during download: {e}") from e
        except (DownloadSizeError, DownloadSecurityError):
            # Re-raise security/size errors as-is
            raise
        except Exception as e:
            raise DownloadError(f"Unexpected error during download: {e}") from e

    def _extract_archive(self, archive_path: Path, extract_dir: Path) -> dict[str, Any]:
        """
        Safely extract archive to directory

        Args:
            archive_path: Path to archive file
            extract_dir: Directory to extract to

        Returns:
            Extraction metadata

        Raises:
            DownloadSecurityError: If extraction has security issues
        """
        logger.info(f"Extracting {archive_path} to {extract_dir}")

        extract_dir.mkdir(parents=True, exist_ok=True)

        try:
            if archive_path.suffix.lower() == ".zip":
                with zipfile.ZipFile(archive_path, "r") as zip_file:
                    # Extract with safety checks
                    extracted_files = []
                    for info in zip_file.infolist():
                        # Final security check during extraction
                        if os.path.isabs(info.filename) or ".." in info.filename:
                            raise DownloadSecurityError(
                                f"Refusing to extract suspicious path: {info.filename}"
                            )

                        # Extract file
                        zip_file.extract(info, extract_dir)
                        extracted_files.append(info.filename)

                    return {
                        "extracted_files": len(extracted_files),
                        "files": extracted_files[:10],  # Sample of files
                    }
            else:
                raise DownloadError(f"Unsupported archive format: {archive_path.suffix}")

        except zipfile.BadZipFile as e:
            raise DownloadSecurityError(f"Invalid zip file during extraction: {e}") from e
        except Exception as e:
            raise DownloadError(f"Extraction failed: {e}") from e

    async def download_github_repository(self, candidate: Candidate) -> dict[str, Any]:
        """
        Download GitHub repository archive

        Args:
            candidate: GitHub repository candidate

        Returns:
            Download results
        """
        if candidate.source != SourceType.GITHUB:
            raise ValueError("Candidate must be from GitHub")

        self._log_download_action("start", candidate.id, {"source": "github"})

        # Build GitHub archive URL
        archive_url = f"https://api.github.com/repos/{candidate.full_name}/zipball/HEAD"

        # Add authorization if available
        headers = {}
        if self.config.github.token:
            headers["Authorization"] = f"Bearer {self.config.github.token}"

        # Update client headers for this request
        original_headers = self.client.headers
        self.client.headers.update(headers)

        try:
            output_path = self._get_download_path(candidate, "zip")

            # Download repository
            download_info = await self._download_file(archive_url, output_path)

            # Extract if requested
            extract_dir = output_path.parent / f"{output_path.stem}_extracted"
            extraction_info = self._extract_archive(output_path, extract_dir)

            result = {
                "candidate_id": candidate.id,
                "source": candidate.source.value,
                "download_path": str(output_path),
                "extract_path": str(extract_dir),
                "download_info": download_info,
                "extraction_info": extraction_info,
                "success": True,
            }

            self._log_download_action("success", candidate.id, result)
            return result

        except Exception as e:
            self._log_download_action("error", candidate.id, {"error": str(e)})
            raise
        finally:
            # Restore original headers
            self.client.headers = original_headers

    async def download_huggingface_repository(self, candidate: Candidate) -> dict[str, Any]:
        """
        Download Hugging Face repository archive

        Args:
            candidate: Hugging Face repository candidate

        Returns:
            Download results
        """
        if candidate.source != SourceType.HUGGINGFACE:
            raise ValueError("Candidate must be from Hugging Face")

        self._log_download_action("start", candidate.id, {"source": "huggingface"})

        # Determine repository type and build URL
        if "/spaces/" in candidate.url:
            archive_url = (
                f"https://huggingface.co/spaces/{candidate.full_name}/resolve/main/archive.tar.gz"
            )
        else:
            archive_url = (
                f"https://huggingface.co/{candidate.full_name}/resolve/main/archive.tar.gz"
            )

        # Add authorization if available
        headers = {}
        if self.config.huggingface.token:
            headers["Authorization"] = f"Bearer {self.config.huggingface.token}"

        # Update client headers for this request
        original_headers = self.client.headers
        self.client.headers.update(headers)

        try:
            output_path = self._get_download_path(candidate, "tar.gz")

            # Try different archive formats as fallback
            formats_to_try = [
                ("zip", f"https://huggingface.co/{candidate.full_name}/resolve/main/archive.zip"),
                ("tar.gz", archive_url),
            ]

            download_info = None
            for fmt, url in formats_to_try:
                try:
                    current_path = self._get_download_path(candidate, fmt)
                    download_info = await self._download_file(url, current_path)
                    output_path = current_path
                    break
                except DownloadError as e:
                    logger.debug(f"Failed to download {fmt} format: {e}")
                    continue

            if not download_info:
                raise DownloadError("All download formats failed")

            # For now, just return download info without extraction for tar.gz
            # Full tar.gz extraction would require additional libraries
            result = {
                "candidate_id": candidate.id,
                "source": candidate.source.value,
                "download_path": str(output_path),
                "extract_path": None,
                "download_info": download_info,
                "extraction_info": {"note": "Tar.gz extraction not implemented"},
                "success": True,
            }

            self._log_download_action("success", candidate.id, result)
            return result

        except Exception as e:
            self._log_download_action("error", candidate.id, {"error": str(e)})
            raise
        finally:
            # Restore original headers
            self.client.headers = original_headers

    async def download_candidate(self, candidate: Candidate) -> dict[str, Any]:
        """
        Download repository for any supported source

        Args:
            candidate: Repository candidate

        Returns:
            Download results
        """
        if not self.config.analysis.download_enabled:
            raise DownloadError("Downloads are disabled in configuration")

        logger.info(f"Downloading candidate: {candidate.id}")

        if candidate.source == SourceType.GITHUB:
            return await self.download_github_repository(candidate)
        elif candidate.source == SourceType.HUGGINGFACE:
            return await self.download_huggingface_repository(candidate)
        else:
            raise DownloadError(f"Unsupported source: {candidate.source}")

    async def download_multiple_candidates(
        self, candidates: list[Candidate], max_concurrent: int = 3
    ) -> list[dict[str, Any]]:
        """
        Download multiple candidates with concurrency control

        Args:
            candidates: List of candidates to download
            max_concurrent: Maximum concurrent downloads

        Returns:
            List of download results
        """
        logger.info(f"Downloading {len(candidates)} candidates (max concurrent: {max_concurrent})")

        semaphore = asyncio.Semaphore(max_concurrent)

        async def download_with_semaphore(candidate: Candidate) -> dict[str, Any]:
            async with semaphore:
                try:
                    return await self.download_candidate(candidate)
                except Exception as e:
                    logger.error(f"Failed to download {candidate.id}: {e}")
                    return {"candidate_id": candidate.id, "success": False, "error": str(e)}

        # Execute downloads with concurrency control
        tasks = [download_with_semaphore(candidate) for candidate in candidates]
        results = await asyncio.gather(*tasks, return_exceptions=False)

        successful = len([r for r in results if r.get("success", False)])
        logger.info(f"Download completed: {successful}/{len(candidates)} successful")

        return results

    def cleanup_downloads(self, older_than_days: int = 7) -> dict[str, Any]:
        """
        Clean up old downloaded files

        Args:
            older_than_days: Remove files older than this many days

        Returns:
            Cleanup statistics
        """
        import time

        logger.info(f"Cleaning up downloads older than {older_than_days} days")

        cutoff_time = time.time() - (older_than_days * 24 * 60 * 60)
        removed_files = 0
        removed_size = 0

        for root, dirs, files in os.walk(self.downloads_dir):
            for file in files:
                file_path = Path(root) / file
                try:
                    if file_path.stat().st_mtime < cutoff_time:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        removed_files += 1
                        removed_size += file_size
                        logger.debug(f"Removed old download: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove {file_path}: {e}")

        # Remove empty directories
        for root, dirs, files in os.walk(self.downloads_dir, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    if not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        logger.debug(f"Removed empty directory: {dir_path}")
                except Exception as e:
                    logger.debug(f"Could not remove directory {dir_path}: {e}")

        return {
            "removed_files": removed_files,
            "removed_size_mb": removed_size / 1024 / 1024,
            "cleanup_time": older_than_days,
        }

    def get_audit_log(self) -> list[AuditLogEntry]:
        """Get audit log of all download actions"""
        return self.audit_log.copy()

    def get_download_statistics(self) -> dict[str, Any]:
        """
        Get statistics about downloaded files

        Returns:
            Download statistics
        """
        total_files = 0
        total_size = 0
        source_counts = {}

        for root, _dirs, files in os.walk(self.downloads_dir):
            for file in files:
                file_path = Path(root) / file
                try:
                    file_size = file_path.stat().st_size
                    total_files += 1
                    total_size += file_size

                    # Count by source (based on directory structure)
                    relative_path = file_path.relative_to(self.downloads_dir)
                    source = relative_path.parts[0] if relative_path.parts else "unknown"
                    source_counts[source] = source_counts.get(source, 0) + 1

                except Exception as e:
                    logger.debug(f"Could not stat file {file_path}: {e}")

        return {
            "total_files": total_files,
            "total_size_mb": total_size / 1024 / 1024,
            "source_counts": source_counts,
            "downloads_dir": str(self.downloads_dir),
        }
