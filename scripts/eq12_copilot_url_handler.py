#!/usr/bin/env python3
"""
EQ12 Copilot URL Submission Handler
Automatically processes URLs when submitted to Copilot and triggers learning system

Author: EQ12 AI System
Version: 1.0.0
"""

from eq12_url_scanner import EQ12URLScanner
import asyncio
import json
import logging
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import uvicorn

# FastAPI for webhook handling
from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

# EQ12 imports
sys.path.append(str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/copilot_url_handler.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("EQ12CopilotURLHandler")


class URLSubmission(BaseModel):
    """URL submission model"""

    url: str
    source: str = "copilot"
    context: str | None = None
    user_id: str | None = None
    timestamp: str | None = None


class CopilotMessage(BaseModel):
    """Copilot message model"""

    content: str
    user: str | None = None
    channel: str | None = None
    timestamp: str | None = None


class EQ12CopilotURLHandler:
    """Handles URL submissions from Copilot and other sources"""

    def __init__(self):
        self.scanner = EQ12URLScanner()
        self.processed_urls = set()

        # URL patterns to match
        self.url_patterns = [
            r"https?://[^\s]+",
            r"www\.[^\s]+",
            r"[^\s]+\.[a-z]{2,}(?:/[^\s]*)?",
        ]

        # Initialize FastAPI app for webhook handling
        self.app = FastAPI(
            title="EQ12 Copilot URL Handler",
            description="Handles URL submissions from Copilot and triggers learning",
            version="1.0.0",
        )

        self._setup_routes()

    def _setup_routes(self):
        """Setup FastAPI routes"""

        @self.app.post("/webhook/copilot")
        async def handle_copilot_webhook(
            message: CopilotMessage, background_tasks: BackgroundTasks
        ):
            """Handle Copilot webhook with potential URLs"""
            urls = self.extract_urls_from_text(message.content)

            if urls:
                logger.info(f"Found {len(urls)} URLs in Copilot message")

                # Process URLs in background
                for url in urls:
                    background_tasks.add_task(
                        self.process_copilot_url,
                        url,
                        message.user or "unknown",
                        message.content,
                    )

                return {
                    "status": "success",
                    "message": f"Processing {len(urls)} URLs",
                    "urls": urls,
                }

            return {"status": "no_urls", "message": "No URLs found in message"}

        @self.app.post("/webhook/url")
        async def handle_direct_url(
                submission: URLSubmission,
                background_tasks: BackgroundTasks):
            """Handle direct URL submission"""
            logger.info(f"Direct URL submission: {submission.url}")

            background_tasks.add_task(
                self.process_copilot_url,
                submission.url,
                submission.source,
                submission.context,
            )

            return {
                "status": "success",
                "message": "URL submitted for processing",
                "url": submission.url,
            }

        @self.app.get("/status")
        async def get_handler_status():
            """Get handler status"""
            scanner_status = self.scanner.get_scanner_status()

            return {
                "handler_status": "active",
                "processed_urls_count": len(self.processed_urls),
                "scanner_status": scanner_status,
                "timestamp": datetime.now(UTC).isoformat(),
            }

        @self.app.get("/recent-submissions")
        async def get_recent_submissions():
            """Get recent URL submissions"""
            return await self.get_recent_submissions()

    def extract_urls_from_text(self, text: str) -> list[str]:
        """Extract URLs from text using multiple patterns"""
        urls = []

        for pattern in self.url_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Clean up the URL
                url = match.strip(".,!?();\"' ")

                # Add protocol if missing
                if url.startswith("www.") or (
                        not url.startswith("http") and "." in url):
                    url = f"https://{url}"

                # Validate and add if not already found
                if self._is_valid_url_format(url) and url not in urls:
                    urls.append(url)

        return urls

    def _is_valid_url_format(self, url: str) -> bool:
        """Basic URL format validation"""
        try:
            from urllib.parse import urlparse

            result = urlparse(url)
            return all([result.scheme, result.netloc]) and len(result.netloc) > 3
        except BaseException:
            return False

    async def process_copilot_url(
            self,
            url: str,
            submitted_by: str,
            context: str | None = None):
        """Process a URL submitted via Copilot"""

        # Check if already processed recently
        if url in self.processed_urls:
            logger.info(f"URL already processed: {url}")
            return None

        try:
            logger.info(f"Processing Copilot URL: {url} from {submitted_by}")

            # Process URL through scanner
            result = await self.scanner.process_url_submission(
                url=url, submitted_by=submitted_by, submission_method="copilot"
            )

            # Add to processed set
            self.processed_urls.add(url)

            # Log result
            if result["success"]:
                logger.info(
                    f"Successfully processed {url}: "
                    f"{result['classification']} ({result['confidence']:.2f}), "
                    f"{result['insights_generated']} insights, "
                    f"{result['updates_applied']} updates"
                )

                # Create summary for user
                await self._create_processing_summary(url, result, context)

            else:
                logger.error(
                    f"Failed to process {url}: {
                        result.get(
                            'error',
                            'Unknown error')}")

            return result

        except Exception as e:
            logger.error(f"Error processing Copilot URL {url}: {e}")
            return {"success": False, "error": str(e)}

    async def _create_processing_summary(
        self, url: str, result: dict[str, Any], context: str | None
    ):
        """Create a summary of URL processing for logging/dashboard"""

        summary = {
            "url": url,
            "processed_at": datetime.now(UTC).isoformat(),
            "classification": result.get("classification", "unknown"),
            "confidence": result.get("confidence", 0.0),
            "insights_count": result.get("insights_generated", 0),
            "updates_count": result.get("updates_applied", 0),
            "processing_time": result.get("processing_time", 0.0),
            "context": context,
            "success": result.get("success", False),
        }

        # Save summary to file
        summary_file = (
            f"C:/EQ12/logs/url_processing_summary_{datetime.now().strftime('%Y%m%d')}.json"
        )

        try:
            # Load existing summaries
            summaries = []
            if os.path.exists(summary_file):
                with open(summary_file) as f:
                    summaries = json.load(f)

            # Add new summary
            summaries.append(summary)

            # Keep only last 100 entries
            summaries = summaries[-100:]

            # Save back
            with open(summary_file, "w") as f:
                json.dump(summaries, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving processing summary: {e}")

        # Also create a readable log entry
        log_entry = (
            f"URL_PROCESSED: {url} -> {summary['classification']} "
            f"({summary['confidence']:.2f}) | "
            f"Insights: {summary['insights_count']} | "
            f"Updates: {summary['updates_count']} | "
            f"Time: {summary['processing_time']:.2f}s"
        )

        logger.info(log_entry)

    async def get_recent_submissions(self) -> dict[str, Any]:
        """Get recent URL submissions and their status"""

        try:
            # Get today's summary file
            summary_file = (
                f"C:/EQ12/logs/url_processing_summary_{datetime.now().strftime('%Y%m%d')}.json"
            )

            summaries = []
            if os.path.exists(summary_file):
                with open(summary_file) as f:
                    summaries = json.load(f)

            # Get last 20 submissions
            recent = summaries[-20:] if summaries else []

            # Calculate statistics
            total_processed = len(summaries)
            successful = sum(1 for s in summaries if s.get("success", False))
            categories = {}

            for summary in summaries:
                cat = summary.get("classification", "unknown")
                categories[cat] = categories.get(cat, 0) + 1

            return {
                "recent_submissions": recent,
                "statistics": {
                    "total_today": total_processed,
                    "successful_today": successful,
                    "success_rate": (
                        successful /
                        total_processed if total_processed > 0 else 0),
                    "categories": categories,
                },
                "timestamp": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting recent submissions: {e}")
            return {
                "recent_submissions": [],
                "statistics": {"error": str(e)},
                "timestamp": datetime.now(UTC).isoformat(),
            }

    async def batch_process_urls(
            self, urls: list[str], source: str = "batch") -> dict[str, Any]:
        """Process multiple URLs in batch"""

        logger.info(f"Batch processing {len(urls)} URLs")

        results = []
        for url in urls:
            try:
                result = await self.process_copilot_url(url, source)
                results.append({"url": url, "result": result})
            except Exception as e:
                results.append(
                    {"url": url, "result": {"success": False, "error": str(e)}})

        # Calculate batch statistics
        successful = sum(1 for r in results if r["result"].get("success", False))
        total_insights = sum(r["result"].get("insights_generated", 0) for r in results)
        total_updates = sum(r["result"].get("updates_applied", 0) for r in results)

        batch_summary = {
            "total_urls": len(urls),
            "successful": successful,
            "failed": len(urls) - successful,
            "success_rate": successful / len(urls) if urls else 0,
            "total_insights": total_insights,
            "total_updates": total_updates,
            "results": results,
            "processed_at": datetime.now(UTC).isoformat(),
        }

        logger.info(
            f"Batch processing complete: {successful}/{len(urls)} successful, "
            f"{total_insights} insights, {total_updates} updates"
        )

        return batch_summary

    def start_webhook_server(self, host: str = "127.0.0.1", port: int = 8080):
        """Start the webhook server"""
        logger.info(f"Starting Copilot URL handler webhook server on {host}:{port}")

        uvicorn.run(self.app, host=host, port=port, log_level="info", access_log=True)


# Standalone URL processing functions for direct use
async def process_url_from_copilot(url: str) -> dict[str, Any]:
    """Process a single URL directly"""
    handler = EQ12CopilotURLHandler()
    return await handler.process_copilot_url(url, "direct_call")


async def process_text_for_urls(text: str) -> dict[str, Any]:
    """Process text content for URLs and handle them"""
    handler = EQ12CopilotURLHandler()
    urls = handler.extract_urls_from_text(text)

    if not urls:
        return {"success": False, "message": "No URLs found in text"}

    return await handler.batch_process_urls(urls, "text_extraction")


# Main entry point
async def main():
    """Main entry point"""

    # Test URL extraction
    test_text = """
    Check out this great article: https://example.com/article
    Also see www.github.com/microsoft/playwright
    And this API: https://api.odds.com/v1/sports
    """

    handler = EQ12CopilotURLHandler()
    urls = handler.extract_urls_from_text(test_text)

    print(f"Extracted URLs: {urls}")

    # Test processing
    if urls:
        # Process first URL only
        result = await handler.batch_process_urls(urls[:1], "test")
        print(f"Processing result: {json.dumps(result, indent=2)}")

    # Start webhook server (commented out for testing)
    # handler.start_webhook_server()


if __name__ == "__main__":
    asyncio.run(main())
