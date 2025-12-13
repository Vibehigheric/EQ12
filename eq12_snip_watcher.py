#!/usr/bin/env python3
"""
EQ12 Snip Watcher - Visual Data Capture Pipeline

Monitors screenshot folder for new images, OCRs text content,
and routes data to appropriate EQ12 modules:
- Betting odds → /api/parlay
- Travel deals → /api/deal
- Finance/credit → /api/finance

Integrates with Apple TV Command Center and Telegram bot.
"""

import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

try:
    import asyncio

    import aiohttp
    import pytesseract
    import requests
    from PIL import Image
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    OCR_AVAILABLE = True
except ImportError as e:
    OCR_AVAILABLE = False
    print(f"[ERROR] Missing snip watcher dependencies: {e}")
    print("Install: pip install pytesseract watchdog pillow requests aiohttp")

# EQ12 Configuration
EQ12_HOME = Path(os.getenv("EQ12_HOME", r"C:\EQ12"))
SNIP_FOLDER = EQ12_HOME / "snips"
SNIP_LOGS_DIR = EQ12_HOME / "logs" / "snip_watcher"

# Ensure directories exist
SNIP_FOLDER.mkdir(parents=True, exist_ok=True)
SNIP_LOGS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class SnipResult:
    """Result of processing a snip"""

    filepath: str
    text: str
    route: str | None
    payload: dict | None
    success: bool
    error: str | None = None


class EQ12SnipWatcher:
    """Watches for screenshots and routes OCR'd content"""

    def __init__(self):
        self.snip_folder = SNIP_FOLDER
        self.logs_dir = SNIP_LOGS_DIR

        # Setup logging
        self._setup_logging()

        # API endpoints
        self.eq12_api_base = "http://localhost:8000"
        self.appletv_api_base = "http://localhost:8080"

        # Routing configuration
        self.route_map = {
            "odds": "/api/parlay",
            "deal": "/api/deal",
            "finance": "/api/finance",
            "credit": "/api/finance",
        }

        # OCR configuration
        self.tesseract_path = self._find_tesseract()
        if self.tesseract_path and OCR_AVAILABLE:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path

        # File patterns to watch
        self.watch_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp")

        # Processing stats
        self.stats = {
            "total_processed": 0,
            "successful_routes": 0,
            "failed_routes": 0,
            "ocr_errors": 0,
            "start_time": datetime.now(),
        }

    def _setup_logging(self):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            handlers=[
                logging.FileHandler(self.logs_dir / "snip_watcher.log", encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger("EQ12SnipWatcher")

    def _find_tesseract(self) -> str | None:
        """Find Tesseract OCR executable"""
        common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Tools\tesseract\tesseract.exe",
        ]

        for path in common_paths:
            if os.path.exists(path):
                return path

        # Try PATH
        import shutil

        tesseract = shutil.which("tesseract")
        if tesseract:
            return tesseract

        self.logger.warning("Tesseract not found. OCR will not work.")
        return None

    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image using OCR"""
        if not self.tesseract_path or not OCR_AVAILABLE:
            self.logger.error("OCR not available")
            return ""

        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, config="--psm 6")
            return text.strip()
        except Exception as e:
            self.logger.error(f"OCR failed for {image_path}: {e}")
            self.stats["ocr_errors"] += 1
            return ""

    def route_text_content(self, text: str, filename: str) -> SnipResult:
        """Route extracted text to appropriate EQ12 module"""
        text_lower = text.lower()

        # Betting/Odds detection
        if any(
            keyword in text_lower
            for keyword in [
                "odds",
                "ml",
                "moneyline",
                "spread",
                "+",
                "-",
                "over",
                "under",
            ]
        ):
            return self._create_betting_payload(text, filename)

        # Travel/Flight detection
        if any(
            keyword in text_lower
            for keyword in [
                "$",
                "flight",
                "hotel",
                "rt",
                "roundtrip",
                "buf",
                "nyc",
                "lax",
                "mco",
            ]
        ):
            return self._create_travel_payload(text, filename)

        # Finance/Credit detection
        if any(
            keyword in text_lower
            for keyword in [
                "credit",
                "score",
                "utilization",
                "balance",
                "payment",
                "apr",
            ]
        ):
            return self._create_finance_payload(text, filename)

        # Unrouted content
        return SnipResult(
            filepath=filename,
            text=text,
            route=None,
            payload=None,
            success=False,
            error="Could not determine content type",
        )

    def _create_betting_payload(self, text: str, filename: str) -> SnipResult:
        """Create betting parlay payload"""
        payload = {
            "title": f"Snip Parlay from {Path(filename).name}",
            "source": "snip_watcher",
            "legs": [
                {
                    "market": "Snip Detection",
                    "selection": text[:100] + "..." if len(text) > 100 else text,
                    "odds": "TBD",
                    "book": "Manual Entry",
                }
            ],
            "raw_ocr": text,
            "timestamp": datetime.now().isoformat(),
        }

        return SnipResult(
            filepath=filename,
            text=text,
            route=self.route_map["odds"],
            payload=payload,
            success=True,
        )

    def _create_travel_payload(self, text: str, filename: str) -> SnipResult:
        """Create travel deal payload"""
        payload = {
            "route": f"Snip Deal from {Path(filename).name}",
            "source": "snip_watcher",
            "price": self._extract_price(text),
            "carrier": "TBD",
            "dates": "TBD",
            "link": "",
            "raw_ocr": text,
            "timestamp": datetime.now().isoformat(),
        }

        return SnipResult(
            filepath=filename,
            text=text,
            route=self.route_map["deal"],
            payload=payload,
            success=True,
        )

    def _create_finance_payload(self, text: str, filename: str) -> SnipResult:
        """Create finance/credit payload"""
        payload = {
            "snapshot": f"Snip Finance from {Path(filename).name}",
            "source": "snip_watcher",
            "credit_score": self._extract_credit_score(text),
            "raw_ocr": text,
            "timestamp": datetime.now().isoformat(),
        }

        return SnipResult(
            filepath=filename,
            text=text,
            route=self.route_map["finance"],
            payload=payload,
            success=True,
        )

    def _extract_price(self, text: str) -> int:
        """Extract price from text"""
        import re

        price_match = re.search(r"\$(\d+)", text)
        return int(price_match.group(1)) if price_match else 0

    def _extract_credit_score(self, text: str) -> int:
        """Extract credit score from text"""
        import re

        score_match = re.search(r"(\d{3})", text)
        return int(score_match.group(1)) if score_match else 0

    async def send_to_eq12_api(self, result: SnipResult) -> bool:
        """Send payload to EQ12 API"""
        if not result.route or not result.payload:
            return False

        try:
            url = f"{self.eq12_api_base}{result.route}"

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=result.payload) as response:
                    if response.status == 200:
                        self.logger.info(f"Successfully sent snip data to {result.route}")
                        self.stats["successful_routes"] += 1
                        return True
                    error_text = await response.text()
                    self.logger.error(f"API request failed ({response.status}): {error_text}")
                    self.stats["failed_routes"] += 1
                    return False

        except Exception as e:
            self.logger.error(f"API request error: {e}")
            self.stats["failed_routes"] += 1
            return False

    def save_unrouted_content(self, result: SnipResult):
        """Save content that couldn't be routed"""
        unrouted_file = self.snip_folder / "unrouted_snips.txt"

        with open(unrouted_file, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"\n--- {timestamp} - {Path(result.filepath).name} ---\n")
            f.write(f"{result.text}\n")
            f.write(f"Error: {result.error}\n\n")

    def get_stats(self) -> dict:
        """Get processing statistics"""
        runtime = datetime.now() - self.stats["start_time"]
        return {
            **self.stats,
            "runtime_seconds": runtime.total_seconds(),
            "success_rate": self.stats["successful_routes"]
            / max(1, self.stats["total_processed"])
            * 100,
        }


class SnipFileHandler(FileSystemEventHandler):
    """File system event handler for new snips"""

    def __init__(self, watcher: EQ12SnipWatcher):
        self.watcher = watcher

    def on_created(self, event):
        if event.is_directory:
            return

        filepath = event.src_path
        if not filepath.lower().endswith(self.watcher.watch_extensions):
            return

        self.watcher.logger.info(f"New snip detected: {filepath}")

        # Small delay to ensure file is fully written
        time.sleep(1)

        # Process the snip
        asyncio.create_task(self.process_snip(filepath))

    async def process_snip(self, filepath: str):
        """Process a new snip file"""
        try:
            self.watcher.stats["total_processed"] += 1

            # Extract text via OCR
            text = self.watcher.extract_text_from_image(filepath)
            if not text:
                self.watcher.logger.warning(f"No text extracted from {filepath}")
                return

            self.watcher.logger.info(
                f"OCR extracted {len(text)} characters from {Path(filepath).name}"
            )
            self.watcher.logger.debug(f"OCR Text: {text[:200]}...")

            # Route content
            result = self.watcher.route_text_content(text, filepath)

            if result.success:
                # Send to EQ12 API
                success = await self.watcher.send_to_eq12_api(result)
                if success:
                    self.watcher.logger.info(f"Successfully processed snip: {Path(filepath).name}")
                else:
                    self.watcher.logger.error(
                        f"Failed to send snip data for: {Path(filepath).name}"
                    )
            else:
                # Save unrouted content
                self.watcher.save_unrouted_content(result)
                self.watcher.logger.warning(
                    f"Could not route snip: {Path(filepath).name} - {result.error}"
                )

        except Exception as e:
            self.watcher.logger.error(f"Error processing snip {filepath}: {e}")


async def main():
    """Main entry point"""
    if not OCR_AVAILABLE:
        print("ERROR: Missing dependencies for snip watcher")
        print("Install with: pip install pytesseract watchdog pillow requests aiohttp")
        return

    watcher = EQ12SnipWatcher()

    if not watcher.tesseract_path:
        print("ERROR: Tesseract OCR not found")
        print("Install from: https://github.com/tesseract-ocr/tesseract")
        return

    watcher.logger.info("Starting EQ12 Snip Watcher")
    watcher.logger.info(f"Watching folder: {watcher.snip_folder}")
    watcher.logger.info(f"OCR engine: {watcher.tesseract_path}")

    # Setup file system watcher
    event_handler = SnipFileHandler(watcher)
    observer = Observer()
    observer.schedule(event_handler, str(watcher.snip_folder), recursive=False)
    observer.start()

    watcher.logger.info("EQ12 Snip Watcher is running...")
    watcher.logger.info("Save screenshots to the snips folder to process them automatically")

    try:
        # Keep running and log stats periodically
        while True:
            await asyncio.sleep(300)  # 5 minutes
            stats = watcher.get_stats()
            watcher.logger.info(
                f"Stats: {stats['total_processed']} processed, "
                f"{stats['successful_routes']} routed, "
                f"{stats['success_rate']:.1f}% success rate"
            )

    except KeyboardInterrupt:
        watcher.logger.info("Stopping EQ12 Snip Watcher...")
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    asyncio.run(main())
