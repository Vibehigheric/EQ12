#!/usr/bin/env python3
"""
EQ12 Cross-Browser Extension Builder
Builds browser extensions with compatibility for Chrome, Firefox, Edge, and Safari.

Based on Mozilla Extension Workshop browser compatibility guidelines:
https://extensionworkshop.com/documentation/develop/browser-compatibility/

Author: EQ12 AI Agent
"""

import argparse
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class CrossBrowserExtensionBuilder:
    """
    Builds cross-browser compatible extensions following Mozilla guidelines.

    Key compatibility patterns:
    - Namespace: chrome.* vs browser.*
    - Async: callbacks vs promises
    - Manifest: V2 vs V3 differences
    - API coverage variations
    """

    def __init__(self, source_dir: str, output_dir: str):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.manifest_template = {}

    def load_base_manifest(self) -> dict[str, Any]:
        """Load base manifest.json template"""
        manifest_path = self.source_dir / "manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"Base manifest.json not found at {manifest_path}")

        with open(manifest_path, encoding="utf-8") as f:
            return json.load(f)

    def create_chrome_manifest(self, base_manifest: dict[str, Any]) -> dict[str, Any]:
        """
        Create Chrome-compatible manifest (Manifest V3)
        - Uses chrome.* namespace
        - Uses callbacks for async APIs
        - Service worker background script
        """
        chrome_manifest = base_manifest.copy()

        # Manifest V3 requirements
        chrome_manifest["manifest_version"] = 3

        # Convert background page to service worker
        if "background" in chrome_manifest:
            if "scripts" in chrome_manifest["background"]:
                chrome_manifest["background"] = {
                    "service_worker": chrome_manifest["background"]["scripts"][0]
                }
            elif "page" in chrome_manifest["background"]:
                # Convert background page to service worker
                chrome_manifest["background"] = {"service_worker": "background.js"}

        # Convert browser_action/page_action to action (V3)
        if "browser_action" in chrome_manifest:
            chrome_manifest["action"] = chrome_manifest.pop("browser_action")
        if "page_action" in chrome_manifest:
            chrome_manifest["action"] = chrome_manifest.pop("page_action")

        # Update host permissions (V3)
        if "permissions" in chrome_manifest:
            permissions = chrome_manifest["permissions"]
            host_permissions = []
            filtered_permissions = []

            for perm in permissions:
                if perm.startswith("http") or "*" in perm:
                    host_permissions.append(perm)
                else:
                    filtered_permissions.append(perm)

            chrome_manifest["permissions"] = filtered_permissions
            if host_permissions:
                chrome_manifest["host_permissions"] = host_permissions

        # Add Chrome-specific keys
        chrome_manifest["minimum_chrome_version"] = "88"

        return chrome_manifest

    def create_firefox_manifest(self, base_manifest: dict[str, Any]) -> dict[str, Any]:
        """
        Create Firefox-compatible manifest (Manifest V2 or V3)
        - Uses browser.* namespace
        - Uses promises for async APIs
        - Background scripts support
        """
        firefox_manifest = base_manifest.copy()

        # Firefox supports both V2 and V3, but V2 is more stable
        firefox_manifest["manifest_version"] = 2

        # Firefox-specific keys
        firefox_manifest["applications"] = {"gecko": {"strict_min_version": "91.0"}}

        # Ensure background scripts format for V2
        if "background" in firefox_manifest and "service_worker" in firefox_manifest["background"]:
            firefox_manifest["background"] = {
                "scripts": [firefox_manifest["background"]["service_worker"]],
                "persistent": False,
            }

        # Convert action back to browser_action for V2
        if "action" in firefox_manifest:
            firefox_manifest["browser_action"] = firefox_manifest.pop("action")

        return firefox_manifest

    def create_edge_manifest(self, base_manifest: dict[str, Any]) -> dict[str, Any]:
        """
        Create Edge-compatible manifest (Manifest V3)
        Edge uses Chromium base, similar to Chrome
        """
        # Edge follows Chrome patterns mostly
        edge_manifest = self.create_chrome_manifest(base_manifest)

        # Edge-specific minimum version
        edge_manifest["minimum_chrome_version"] = "79"  # First Chromium-based Edge

        return edge_manifest

    def create_safari_manifest(self, base_manifest: dict[str, Any]) -> dict[str, Any]:
        """
        Create Safari-compatible manifest (Safari App Extensions)
        Note: Safari has different architecture, may need native app wrapper
        """
        safari_manifest = base_manifest.copy()

        # Safari uses Manifest V2 style
        safari_manifest["manifest_version"] = 2

        # Safari-specific considerations
        if "background" in safari_manifest and "service_worker" in safari_manifest["background"]:
            safari_manifest["background"] = {
                "scripts": [safari_manifest["background"]["service_worker"]],
                "persistent": False,
            }

        # Convert action to browser_action
        if "action" in safari_manifest:
            safari_manifest["browser_action"] = safari_manifest.pop("action")

        return safari_manifest

    def create_polyfill_script(self) -> str:
        """
        Create browser API polyfill script for cross-browser compatibility
        Uses webextension-polyfill pattern
        """
        return """
// EQ12 Cross-Browser Polyfill
// Based on Mozilla WebExtension Polyfill patterns

(function() {
    'use strict';

    // Detect browser environment
    const isFirefox = typeof browser !== 'undefined';
    const isChrome = typeof chrome !== 'undefined' && !isFirefox;

    // Create unified API object
    window.browserAPI = isFirefox ? browser : chrome;

    // Promise polyfill for Chrome callback APIs
    if (isChrome) {
        const promisifyAPI = (apiObj, methods) => {
            methods.forEach(method => {
                if (apiObj[method]) {
                    const originalMethod = apiObj[method];
                    apiObj[method + 'Async'] = (...args) => {
                        return new Promise((resolve, reject) => {
                            originalMethod(...args, (result) => {
                                if (chrome.runtime.lastError) {
                                    reject(chrome.runtime.lastError);
                                } else {
                                    resolve(result);
                                }
                            });
                        });
                    };
                }
            });
        };

        // Promisify common APIs
        if (chrome.tabs) {
            promisifyAPI(chrome.tabs, ['query', 'create', 'update', 'remove']);
        }
        if (chrome.storage && chrome.storage.sync) {
            promisifyAPI(chrome.storage.sync, ['get', 'set', 'remove']);
        }
        if (chrome.cookies) {
            promisifyAPI(chrome.cookies, ['get', 'set', 'remove']);
        }
    }

    console.log('EQ12 Cross-Browser Polyfill loaded for:', isFirefox ? 'Firefox' : 'Chrome');
})();
"""

    def convert_background_script(self, script_path: Path, target_browser: str) -> str:
        """
        Convert background script for browser compatibility
        """
        if not script_path.exists():
            return ""

        with open(script_path, encoding="utf-8") as f:
            content = f.read()

        if target_browser == "chrome":
            # Convert browser.* to chrome.*
            content = content.replace("browser.", "chrome.")
            # Add service worker patterns for V3
            content = """
// Chrome Manifest V3 Service Worker
{content}

// Service worker event listeners
self.addEventListener('install', (event) => {{
    console.log('EQ12 Extension Service Worker installed');
}});

self.addEventListener('activate', (event) => {{
    console.log('EQ12 Extension Service Worker activated');
}});
"""
        elif target_browser == "firefox":
            # Ensure browser.* namespace
            content = content.replace("chrome.", "browser.")

        return content

    def build_for_browser(self, browser: str):
        """Build extension for specific browser"""
        logger.info(f"Building extension for {browser.upper()}")

        # Create output directory
        browser_dir = self.output_dir / browser
        browser_dir.mkdir(parents=True, exist_ok=True)

        # Load base manifest
        base_manifest = self.load_base_manifest()

        # Create browser-specific manifest
        if browser == "chrome":
            manifest = self.create_chrome_manifest(base_manifest)
        elif browser == "firefox":
            manifest = self.create_firefox_manifest(base_manifest)
        elif browser == "edge":
            manifest = self.create_edge_manifest(base_manifest)
        elif browser == "safari":
            manifest = self.create_safari_manifest(base_manifest)
        else:
            raise ValueError(f"Unsupported browser: {browser}")

        # Write manifest
        with open(browser_dir / "manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        # Copy static files
        for item in self.source_dir.iterdir():
            if item.name in ["manifest.json"]:
                continue

            dest = browser_dir / item.name
            if item.is_file():
                shutil.copy2(item, dest)

                # Process JavaScript files for browser compatibility
                if item.suffix == ".js" and item.name in [
                    "background.js",
                    "content.js",
                ]:
                    converted = self.convert_background_script(item, browser)
                    if converted:
                        with open(dest, "w", encoding="utf-8") as f:
                            f.write(converted)

            elif item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)

        # Add polyfill script
        polyfill_content = self.create_polyfill_script()
        with open(browser_dir / "polyfill.js", "w", encoding="utf-8") as f:
            f.write(polyfill_content)

        logger.info(f"✅ {browser.upper()} extension built in {browser_dir}")

    def build_all(self):
        """Build extensions for all supported browsers"""
        browsers = ["chrome", "firefox", "edge", "safari"]

        for browser in browsers:
            try:
                self.build_for_browser(browser)
            except Exception as e:
                logger.error(f"❌ Failed to build {browser} extension: {e}")

        logger.info("🎉 Cross-browser extension build complete!")

        # Create package info
        info = {
            "build_time": datetime.utcnow().isoformat(),
            "browsers": browsers,
            "compatibility_notes": {
                "chrome": "Manifest V3, service workers, chrome.* namespace",
                "firefox": "Manifest V2, browser.* namespace, promises",
                "edge": "Chromium-based, follows Chrome patterns",
                "safari": "Requires native app wrapper for distribution",
            },
        }

        with open(self.output_dir / "build_info.json", "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="EQ12 Cross-Browser Extension Builder")
    parser.add_argument("--source", "-s", required=True,
                        help="Source extension directory")
    parser.add_argument(
        "--output", "-o", required=True, help="Output directory for built extensions"
    )
    parser.add_argument(
        "--browser",
        "-b",
        help="Build for specific browser (chrome/firefox/edge/safari)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    builder = CrossBrowserExtensionBuilder(args.source, args.output)

    if args.browser:
        builder.build_for_browser(args.browser)
    else:
        builder.build_all()


if __name__ == "__main__":
    main()
