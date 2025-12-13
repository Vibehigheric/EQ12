#!/usr/bin/env python3
"""
EQ12 Extension Debug Manager
Implements Mozilla Extension Workshop debugging best practices

Based on: https://extensionworkshop.com/documentation/develop/debugging/
Provides comprehensive debugging framework for browser extensions
"""

import argparse
import datetime
import json
import logging
import sys
from pathlib import Path
from typing import Any


class ExtensionDebugManager:
    """
    Comprehensive extension debugging system following Mozilla guidelines
    Provides debugging capabilities for all extension components
    """

    def __init__(self, extension_path: str, verbose: bool = False):
        self.extension_path = Path(extension_path)
        self.verbose = verbose
        self.debug_config = self._load_debug_config()

        # Setup logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler("C:\\\\EQ12\\logs\\\\extension_debug.log"),
            ],
        )
        self.logger = logging.getLogger("EQ12ExtensionDebug")

    def _load_debug_config(self) -> dict[str, Any]:
        """Load debug configuration for the extension"""
        config_path = self.extension_path / "debug-config.json"

        default_config = {
            "debug_level": "INFO",
            "enable_console_logs": True,
            "enable_error_tracking": True,
            "enable_performance_monitoring": True,
            "debug_components": {
                "background": True,
                "content_scripts": True,
                "popup": True,
                "options": True,
                "storage": True,
            },
            "log_filters": {
                "exclude_patterns": ["webpack", "hot-reload"],
                "include_patterns": ["EQ12", "governance"],
            },
        }

        if config_path.exists():
            try:
                with open(config_path, encoding="utf-8") as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Failed to load debug config: {e}")

        return default_config

    def inject_debug_utilities(self) -> bool:
        """Inject debug utilities into extension scripts"""
        try:
            # Create debug utility script
            debug_utils = self._generate_debug_utils()
            debug_path = self.extension_path / "debug-utils.js"

            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(debug_utils)

            self.logger.info(f"Debug utilities injected: {debug_path}")

            # Update manifest to include debug utils
            self._update_manifest_for_debugging()

            return True

        except Exception as e:
            self.logger.error(f"Failed to inject debug utilities: {e}")
            return False

    def _generate_debug_utils(self) -> str:
        """Generate debug utilities JavaScript following Mozilla guidelines"""
        return """
/**
 * EQ12 Extension Debug Utilities
 * Based on Mozilla Extension Workshop debugging guidelines
 */

// Debug namespace to avoid conflicts
const EQ12Debug = {
    config: {
        debugLevel: 'INFO',
        enableConsoleLogging: true,
        enableErrorTracking: true,
        componentPrefix: '[EQ12]'
    },

    // Centralized logging system
    logger: {
        debug: function(component, message, data = null) {
            if (EQ12Debug.config.enableConsoleLogging) {
                const prefix = `${EQ12Debug.config.componentPrefix}[${component}][DEBUG]`;
                console.debug(prefix, message, data || '');
            }
        },

        info: function(component, message, data = null) {
            if (EQ12Debug.config.enableConsoleLogging) {
                const prefix = `${EQ12Debug.config.componentPrefix}[${component}][INFO]`;
                console.info(prefix, message, data || '');
            }
        },

        warn: function(component, message, data = null) {
            if (EQ12Debug.config.enableConsoleLogging) {
                const prefix = `${EQ12Debug.config.componentPrefix}[${component}][WARN]`;
                console.warn(prefix, message, data || '');
            }
        },

        error: function(component, message, error = null) {
            if (EQ12Debug.config.enableConsoleLogging) {
                const prefix = `${EQ12Debug.config.componentPrefix}[${component}][ERROR]`;
                console.error(prefix, message, error || '');

                // Track errors for debugging
                if (EQ12Debug.config.enableErrorTracking) {
                    EQ12Debug.errorTracker.trackError(component, message, error);
                }
            }
        }
    },

    // Error tracking and reporting
    errorTracker: {
        errors: [],

        trackError: function(component, message, error) {
            const errorEntry = {
                timestamp: new Date().toISOString(),
                component: component,
                message: message,
                error: error ? {
                    name: error.name,
                    message: error.message,
                    stack: error.stack
                } : null,
                url: window.location ? window.location.href : 'unknown'
            };

            this.errors.push(errorEntry);

            // Keep only last 100 errors
            if (this.errors.length > 100) {
                this.errors = this.errors.slice(-100);
            }

            // Store in extension storage for debugging
            if (typeof browser !== 'undefined' && browser.storage) {
                browser.storage.local.set({
                    'eq12_debug_errors': this.errors
                }).catch(err => {
                    console.error('Failed to store debug errors:', err);
                });
            }
        },

        getErrors: function() {
            return this.errors;
        },

        clearErrors: function() {
            this.errors = [];
            if (typeof browser !== 'undefined' && browser.storage) {
                browser.storage.local.remove('eq12_debug_errors');
            }
        }
    },

    // Performance monitoring
    performance: {
        timers: {},

        startTimer: function(label) {
            this.timers[label] = performance.now();
            EQ12Debug.logger.debug('Performance', `Timer started: ${label}`);
        },

        endTimer: function(label) {
            if (this.timers[label]) {
                const duration = performance.now() - this.timers[label];
                EQ12Debug.logger.info('Performance', `Timer ${label}: ${duration.toFixed(2)}ms`);
                delete this.timers[label];
                return duration;
            }
            return null;
        }
    },

    // Storage debugging utilities
    storage: {
        inspect: async function() {
            if (typeof browser === 'undefined' || !browser.storage) {
                EQ12Debug.logger.warn('Storage', 'Storage API not available');
                return {};
            }

            try {
                const data = await browser.storage.local.get();
                EQ12Debug.logger.info('Storage', 'Current storage data:', data);
                return data;
            } catch (error) {
                EQ12Debug.logger.error('Storage', 'Failed to inspect storage', error);
                return {};
            }
        },

        clear: async function(keys = null) {
            if (typeof browser === 'undefined' || !browser.storage) {
                EQ12Debug.logger.warn('Storage', 'Storage API not available');
                return false;
            }

            try {
                if (keys) {
                    await browser.storage.local.remove(keys);
                    EQ12Debug.logger.info('Storage', 'Cleared keys:', keys);
                } else {
                    await browser.storage.local.clear();
                    EQ12Debug.logger.info('Storage', 'Cleared all storage data');
                }
                return true;
            } catch (error) {
                EQ12Debug.logger.error('Storage', 'Failed to clear storage', error);
                return false;
            }
        }
    },

    // Message debugging for content scripts
    messaging: {
        debugMode: true,

        sendMessage: function(message, responseCallback) {
            if (this.debugMode) {
                EQ12Debug.logger.debug('Messaging', 'Sending message:', message);
            }

            if (typeof browser !== 'undefined' && browser.runtime) {
                browser.runtime.sendMessage(message).then(response => {
                    if (this.debugMode) {
                        EQ12Debug.logger.debug('Messaging', 'Received response:', response);
                    }
                    if (responseCallback) responseCallback(response);
                }).catch(error => {
                    EQ12Debug.logger.error('Messaging', 'Message failed', error);
                });
            }
        }
    },

    // Popup debugging utilities
    popup: {
        disableAutoHide: function() {
            // Note: This is handled by Firefox developer tools
            // Users need to manually disable in about:debugging
            EQ12Debug.logger.info(
                'Popup',
                'To disable auto-hide: Open about:debugging > Inspect > Options menu > Disable Popup Auto-Hide'
            );
        },

        logDimensions: function() {
            if (document.body) {
                const rect = document.body.getBoundingClientRect();
                EQ12Debug.logger.info('Popup', `Dimensions: ${rect.width}x${rect.height}`);
            }
        }
    },

    // Initialize debug system
    init: function() {
        EQ12Debug.logger.info('Debug', 'EQ12 Debug utilities initialized');

        // Global error handler
        if (typeof window !== 'undefined') {
            window.addEventListener('error', function(event) {
                EQ12Debug.logger.error('Global', 'Uncaught error', {
                    message: event.message,
                    filename: event.filename,
                    lineno: event.lineno,
                    colno: event.colno,
                    error: event.error
                });
            });

            // Promise rejection handler
            window.addEventListener('unhandledrejection', function(event) {
                EQ12Debug.logger.error('Global', 'Unhandled promise rejection', event.reason);
            });
        }

        // Make debug utilities globally available in development
        if (typeof window !== 'undefined') {
            window.EQ12Debug = EQ12Debug;
        }
    }
};

// Auto-initialize
EQ12Debug.init();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EQ12Debug;
}
"""

    def _update_manifest_for_debugging(self) -> bool:
        """Update manifest.json to include debug utilities"""
        try:
            manifest_path = self.extension_path / "manifest.json"
            if not manifest_path.exists():
                self.logger.error("manifest.json not found")
                return False

            with open(manifest_path, encoding="utf-8") as f:
                manifest = json.load(f)

            # Add debug utils to all script sections
            debug_script = "debug-utils.js"

            # Background scripts
            if "background" in manifest:
                if "scripts" in manifest["background"]:
                    if debug_script not in manifest["background"]["scripts"]:
                        manifest["background"]["scripts"].insert(0, debug_script)
                elif "service_worker" in manifest["background"]:
                    # For Manifest V3, we'll need to import in the service worker
                    pass

            # Content scripts
            if "content_scripts" in manifest:
                for content_script in manifest["content_scripts"]:
                    if "js" in content_script:
                        if debug_script not in content_script["js"]:
                            content_script["js"].insert(0, debug_script)

            # Web accessible resources for debugging
            if "web_accessible_resources" not in manifest:
                manifest["web_accessible_resources"] = []
            if debug_script not in manifest["web_accessible_resources"]:
                manifest["web_accessible_resources"].append(debug_script)

            # Save updated manifest
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)

            self.logger.info("Manifest updated for debugging")
            return True

        except Exception as e:
            self.logger.error(f"Failed to update manifest: {e}")
            return False

    def create_debug_test_page(self) -> bool:
        """Create a test page for debugging extension functionality"""
        try:
            test_html = """<!DOCTYPE html>
<html>
<head>
    <title>EQ12 Extension Debug Test Page</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .debug-section { margin: 20px 0; padding: 15px; border: 1px solid #ccc; border-radius: 5px; }
        .debug-button { padding: 10px 15px; margin: 5px; cursor: pointer; background: #007cba; color: white; border: none; border-radius: 3px; }
        .debug-output { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 3px; font-family: monospace; }
        #console-output { max-height: 300px; overflow-y: auto; }
    </style>
</head>
<body>
    <h1>EQ12 Extension Debug Test Page</h1>

    <div class="debug-section">
        <h3>Extension Detection</h3>
        <button class = (
            "debug-button" onclick="testExtensionPresence()">Test Extension Presence</button>
        )
        <div id="extension-status" class="debug-output"></div>
    </div>

    <div class="debug-section">
        <h3>Storage Testing</h3>
        <button class="debug-button" onclick="testStorage()">Test Storage Operations</button>
        <button class="debug-button" onclick="inspectStorage()">Inspect Storage</button>
        <button class="debug-button" onclick="clearStorage()">Clear Storage</button>
        <div id="storage-output" class="debug-output"></div>
    </div>

    <div class="debug-section">
        <h3>Messaging Testing</h3>
        <button class = (
            "debug-button" onclick="testMessaging()">Test Background Communication</button>
        )
        <div id="messaging-output" class="debug-output"></div>
    </div>

    <div class="debug-section">
        <h3>Error Testing</h3>
        <button class="debug-button" onclick="triggerError()">Trigger Test Error</button>
        <button class="debug-button" onclick="showErrors()">Show Tracked Errors</button>
        <button class="debug-button" onclick="clearErrors()">Clear Errors</button>
        <div id="error-output" class="debug-output"></div>
    </div>

    <div class="debug-section">
        <h3>Console Output</h3>
        <div id="console-output" class="debug-output"></div>
    </div>

    <script>
        // Override console methods to capture output
        const originalConsole = {
            log: console.log,
            info: console.info,
            warn: console.warn,
            error: console.error,
            debug: console.debug
        };

        function addToConsoleOutput(type, ...args) {
            const output = document.getElementById('console-output');
            const entry = document.createElement('div');
            entry.style.color = type === 'error' ? 'red' : type === 'warn' ? 'orange' : type === 'debug' ? 'gray' : 'black';
            entry.textContent = `[${type.toUpperCase()}] ${new Date().toLocaleTimeString()}: ${args.map(arg =>
                typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
            ).join(' ')}`;
            output.appendChild(entry);
            output.scrollTop = output.scrollHeight;

            // Call original console method
            originalConsole[type](...args);
        }

        console.log = (...args) => addToConsoleOutput('log', ...args);
        console.info = (...args) => addToConsoleOutput('info', ...args);
        console.warn = (...args) => addToConsoleOutput('warn', ...args);
        console.error = (...args) => addToConsoleOutput('error', ...args);
        console.debug = (...args) => addToConsoleOutput('debug', ...args);

        function testExtensionPresence() {
            const status = document.getElementById('extension-status');
            if (typeof EQ12Debug !== 'undefined') {
                status.innerHTML = (
                    '<span style="color: green;">✓ EQ12 Extension Debug utilities detected</span>';
                )
                EQ12Debug.logger.info('Test', 'Extension debug utilities are working');
            } else {
                status.innerHTML = (
                    '<span style="color: red;">✗ EQ12 Extension not detected or debug utilities not loaded</span>';
                )
            }
        }

        async function testStorage() {
            const output = document.getElementById('storage-output');
            if (typeof EQ12Debug === 'undefined') {
                output.textContent = 'Extension not detected';
                return;
            }

            try {
                // Test data
                const testData = {
                    test_key: 'test_value',
                    timestamp: new Date().toISOString(),
                    debug_test: true
                };

                if (typeof browser !== 'undefined' && browser.storage) {
                    await browser.storage.local.set(testData);
                    output.innerHTML = (
                        '<span style="color: green;">✓ Storage write test successful</span>';
                    )
                    EQ12Debug.logger.info('Test', 'Storage write test completed');
                } else {
                    output.innerHTML = (
                        '<span style="color: red;">✗ Browser storage API not available</span>';
                    )
                }
            } catch (error) {
                output.innerHTML = (
                    `<span style="color: red;">✗ Storage test failed: ${error.message}</span>`;
                )
                EQ12Debug.logger.error('Test', 'Storage test failed', error);
            }
        }

        async function inspectStorage() {
            const output = document.getElementById('storage-output');
            if (typeof EQ12Debug === 'undefined') {
                output.textContent = 'Extension not detected';
                return;
            }

            const data = await EQ12Debug.storage.inspect();
            output.textContent = JSON.stringify(data, null, 2);
        }

        async function clearStorage() {
            const output = document.getElementById('storage-output');
            if (typeof EQ12Debug === 'undefined') {
                output.textContent = 'Extension not detected';
                return;
            }

            const success = await EQ12Debug.storage.clear();
            output.innerHTML = success ?
                '<span style="color: green;">✓ Storage cleared</span>' :
                '<span style="color: red;">✗ Failed to clear storage</span>';
        }

        function testMessaging() {
            const output = document.getElementById('messaging-output');
            if (typeof EQ12Debug === 'undefined') {
                output.textContent = 'Extension not detected';
                return;
            }

            const testMessage = {
                type: 'debug_test',
                timestamp: new Date().toISOString(),
                data: 'Test message from debug page'
            };

            EQ12Debug.messaging.sendMessage(testMessage, (response) => {
                if (response) {
                    output.innerHTML = (
                        `<span style="color: green;">✓ Message sent and response received: ${JSON.stringify(response)}</span>`;
                    )
                } else {
                    output.innerHTML = (
                        '<span style="color: orange;">⚠ Message sent but no response received</span>';
                    )
                }
            });
        }

        function triggerError() {
            if (typeof EQ12Debug === 'undefined') {
                throw new Error('Test error: Extension not detected');
            }

            try {
                // Intentional error for testing
                throw new Error('Intentional test error for debugging');
            } catch (error) {
                EQ12Debug.logger.error('Test', 'Triggered test error', error);
            }
        }

        function showErrors() {
            const output = document.getElementById('error-output');
            if (typeof EQ12Debug === 'undefined') {
                output.textContent = 'Extension not detected';
                return;
            }

            const errors = EQ12Debug.errorTracker.getErrors();
            output.textContent = JSON.stringify(errors, null, 2);
        }

        function clearErrors() {
            const output = document.getElementById('error-output');
            if (typeof EQ12Debug === 'undefined') {
                output.textContent = 'Extension not detected';
                return;
            }

            EQ12Debug.errorTracker.clearErrors();
            output.innerHTML = '<span style="color: green;">✓ Errors cleared</span>';
        }

        // Auto-test on page load
        window.addEventListener('load', function() {
            setTimeout(testExtensionPresence, 1000);
        });
    </script>
</body>
</html>"""

            test_path = self.extension_path / "debug-test-page.html"
            with open(test_path, "w", encoding="utf-8") as f:
                f.write(test_html)

            self.logger.info(f"Debug test page created: {test_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create debug test page: {e}")
            return False

    def generate_debug_report(self) -> dict[str, Any]:
        """Generate comprehensive debug report for the extension"""
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "extension_path": str(self.extension_path),
            "debug_config": self.debug_config,
            "files": {},
            "manifest_analysis": {},
            "debug_utilities_status": "not_checked",
        }

        try:
            # Analyze extension files
            for file_path in self.extension_path.rglob("*"):
                if file_path.is_file() and file_path.suffix in [
                    ".js",
                    ".html",
                    ".css",
                    ".json",
                ]:
                    try:
                        with open(file_path, encoding="utf-8") as f:
                            content = f.read()
                            report["files"][str(file_path.relative_to(self.extension_path))] = {
                                "size": len(content),
                                "lines": content.count("\n") + 1,
                                "has_debug_code": "EQ12Debug" in content or "console." in content,
                            }
                    except Exception as e:
                        report["files"][str(file_path.relative_to(self.extension_path))] = {
                            "error": str(e)}

            # Analyze manifest
            manifest_path = self.extension_path / "manifest.json"
            if manifest_path.exists():
                with open(manifest_path, encoding="utf-8") as f:
                    manifest = json.load(f)
                    report["manifest_analysis"] = {
                        "manifest_version": manifest.get("manifest_version", "unknown"),
                        "has_background": "background" in manifest,
                        "has_content_scripts": "content_scripts" in manifest,
                        "has_popup": "browser_action" in manifest or "action" in manifest,
                        "permissions": manifest.get("permissions", []),
                        "debug_ready": "debug-utils.js" in str(manifest),
                    }

            # Check debug utilities status
            debug_utils_path = self.extension_path / "debug-utils.js"
            report["debug_utilities_status"] = (
                "installed" if debug_utils_path.exists() else "not_installed"
            )

            self.logger.info("Debug report generated successfully")

        except Exception as e:
            self.logger.error(f"Failed to generate debug report: {e}")
            report["error"] = str(e)

        return report

    def create_debug_config_file(self) -> bool:
        """Create a debug configuration file for the extension"""
        try:
            config_path = self.extension_path / "debug-config.json"

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self.debug_config, f, indent=2)

            self.logger.info(f"Debug configuration saved: {config_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create debug config: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="EQ12 Extension Debug Manager")
    parser.add_argument("-e", "--extension", required=True,
                        help="Path to extension directory")
    parser.add_argument(
        "--inject-debug",
        action="store_true",
        help="Inject debug utilities into extension",
    )
    parser.add_argument(
        "--create-test-page",
        action="store_true",
        help="Create debug test page")
    parser.add_argument(
        "--generate-report",
        action="store_true",
        help="Generate debug report")
    parser.add_argument(
        "--create-config", action="store_true", help="Create debug configuration file"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Perform all debug setup operations")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    debug_manager = ExtensionDebugManager(args.extension, args.verbose)

    success = True

    if args.all or args.inject_debug:
        print("🔧 Injecting debug utilities...")
        success &= debug_manager.inject_debug_utilities()

    if args.all or args.create_test_page:
        print("📄 Creating debug test page...")
        success &= debug_manager.create_debug_test_page()

    if args.all or args.create_config:
        print("⚙️ Creating debug configuration...")
        success &= debug_manager.create_debug_config_file()

    if args.all or args.generate_report:
        print("📊 Generating debug report...")
        report = debug_manager.generate_debug_report()

        report_path = Path(args.extension) / "debug-report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Debug report saved: {report_path}")

    if success:
        print("✅ Debug setup completed successfully!")
        print("\n🔍 To debug your extension:")
        print("1. Open Firefox and navigate to about:debugging")
        print("2. Click 'This Firefox' and load your extension")
        print("3. Click 'Inspect' next to your extension")
        print("4. Open the debug test page to verify functionality")
        print("5. Use the Console tab to view debug messages")
    else:
        print("❌ Some debug setup operations failed. Check logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
