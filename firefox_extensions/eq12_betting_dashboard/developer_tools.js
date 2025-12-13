// EQ12 Developer Tools Manager
// Enhanced with features inspired by Mobile DevTools, Clear Cache, Measure-it, and debugging extensions
// Provides comprehensive development and debugging capabilities

class EQ12DeveloperTools {
    constructor() {
        this.debugMode = false;
        this.measurements = new Map();
        this.performanceMetrics = new Map();
        this.networkLogs = [];
        this.consoleLogs = [];
        this.errorLogs = [];
        this.cacheManager = null;

        this.init();
    }

    async init() {
        console.log('🔧 EQ12 Developer Tools initializing...');

        await this.setupDebugConsole();
        await this.setupPerformanceMonitoring();
        await this.setupNetworkMonitoring();
        await this.setupMeasurementTools();
        await this.setupCacheManager();
        await this.setupErrorTracking();

        // Check if in developer mode
        this.debugMode = await this.checkDeveloperMode();

        if (this.debugMode) {
            console.log('🚀 Developer mode enabled - Advanced tools available');
            await this.enableAdvancedDebugging();
        }

        console.log('✅ Developer Tools ready');
    }

    // Enhanced console debugging inspired by Mobile DevTools
    async setupDebugConsole() {
        // Enhanced console with remote logging capability
        const originalConsole = {
            log: console.log,
            warn: console.warn,
            error: console.error,
            info: console.info
        };

        // Wrap console methods for enhanced logging
        ['log', 'warn', 'error', 'info'].forEach(method => {
            console[method] = (...args) => {
                const logEntry = {
                    method,
                    timestamp: Date.now(),
                    args: args.map(arg => this.serializeLogArg(arg)),
                    stackTrace: new Error().stack,
                    url: window.location?.href || 'background'
                };

                this.consoleLogs.push(logEntry);

                // Keep only last 1000 logs
                if (this.consoleLogs.length > 1000) {
                    this.consoleLogs = this.consoleLogs.slice(-1000);
                }

                // Call original method
                originalConsole[method].apply(console, args);

                // Send to remote debugging if enabled
                if (this.debugMode) {
                    this.sendRemoteLog(logEntry);
                }
            };
        });

        // Add developer console commands
        if (typeof window !== 'undefined') {
            window.EQ12Debug = {
                getLogs: () => this.consoleLogs,
                clearLogs: () => this.consoleLogs = [],
                getPerformance: () => this.performanceMetrics,
                getNetworkLogs: () => this.networkLogs,
                measure: (selector) => this.measureElement(selector),
                inspect: (element) => this.inspectElement(element),
                exportDebugData: () => this.exportDebugData()
            };
        }
    }

    // Performance monitoring with detailed metrics
    async setupPerformanceMonitoring() {
        if (typeof window === 'undefined') return;

        // Page load performance
        window.addEventListener('load', () => {
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                if (perfData) {
                    this.performanceMetrics.set('page_load', {
                        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
                        loadComplete: perfData.loadEventEnd - perfData.loadEventStart,
                        firstPaint: this.getFirstPaint(),
                        firstContentfulPaint: this.getFirstContentfulPaint(),
                        domInteractive: perfData.domInteractive - perfData.navigationStart,
                        timestamp: Date.now()
                    });
                }
            }, 100);
        });

        // Resource loading performance
        const observer = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (entry.entryType === 'resource') {
                    this.performanceMetrics.set(`resource_${entry.name}`, {
                        duration: entry.duration,
                        size: entry.transferSize,
                        type: entry.initiatorType,
                        timestamp: Date.now()
                    });
                }
            }
        });

        observer.observe({ entryTypes: ['resource', 'paint', 'largest-contentful-paint'] });

        // Memory monitoring
        if (performance.memory) {
            setInterval(() => {
                this.performanceMetrics.set('memory', {
                    used: performance.memory.usedJSHeapSize,
                    total: performance.memory.totalJSHeapSize,
                    limit: performance.memory.jsHeapSizeLimit,
                    timestamp: Date.now()
                });
            }, 5000);
        }
    }

    // Network request monitoring and debugging
    async setupNetworkMonitoring() {
        // Monitor fetch requests
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const startTime = performance.now();
            const url = args[0];
            const options = args[1] || {};

            try {
                const response = await originalFetch.apply(window, args);
                const endTime = performance.now();

                const logEntry = {
                    url,
                    method: options.method || 'GET',
                    status: response.status,
                    duration: endTime - startTime,
                    size: response.headers.get('content-length'),
                    timestamp: Date.now(),
                    success: response.ok
                };

                this.networkLogs.push(logEntry);
                this.cleanupLogs();

                return response;
            } catch (error) {
                const endTime = performance.now();

                const logEntry = {
                    url,
                    method: options.method || 'GET',
                    duration: endTime - startTime,
                    error: error.message,
                    timestamp: Date.now(),
                    success: false
                };

                this.networkLogs.push(logEntry);
                this.cleanupLogs();

                throw error;
            }
        };

        // Monitor XMLHttpRequest
        const originalXHROpen = XMLHttpRequest.prototype.open;
        const originalXHRSend = XMLHttpRequest.prototype.send;

        XMLHttpRequest.prototype.open = function (method, url) {
            this._eq12_method = method;
            this._eq12_url = url;
            this._eq12_startTime = performance.now();
            return originalXHROpen.apply(this, arguments);
        };

        XMLHttpRequest.prototype.send = function () {
            this.addEventListener('loadend', function () {
                const endTime = performance.now();
                const logEntry = {
                    url: this._eq12_url,
                    method: this._eq12_method,
                    status: this.status,
                    duration: endTime - this._eq12_startTime,
                    timestamp: Date.now(),
                    success: this.status >= 200 && this.status < 300
                };

                window.EQ12Debug?.networkLogs?.push(logEntry);
            });

            return originalXHRSend.apply(this, arguments);
        };
    }

    // Element measurement tools inspired by Measure-it extension
    async setupMeasurementTools() {
        if (typeof window === 'undefined') return;

        // Add measurement overlay
        this.measurementOverlay = this.createMeasurementOverlay();

        // Keyboard shortcut for measurement mode
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'M') {
                this.toggleMeasurementMode();
            }
        });
    }

    createMeasurementOverlay() {
        const overlay = document.createElement('div');
        overlay.id = 'eq12-measurement-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 999999;
            display: none;
        `;

        if (document.body) {
            document.body.appendChild(overlay);
        } else {
            document.addEventListener('DOMContentLoaded', () => {
                document.body.appendChild(overlay);
            });
        }

        return overlay;
    }

    toggleMeasurementMode() {
        if (!this.measurementOverlay) return;

        const isActive = this.measurementOverlay.style.display !== 'none';

        if (isActive) {
            this.measurementOverlay.style.display = 'none';
            document.body.style.cursor = '';
            this.removeMeasurementListeners();
        } else {
            this.measurementOverlay.style.display = 'block';
            document.body.style.cursor = 'crosshair';
            this.addMeasurementListeners();
        }
    }

    addMeasurementListeners() {
        document.addEventListener('mousedown', this.startMeasurement.bind(this));
        document.addEventListener('mousemove', this.updateMeasurement.bind(this));
        document.addEventListener('mouseup', this.endMeasurement.bind(this));
    }

    removeMeasurementListeners() {
        document.removeEventListener('mousedown', this.startMeasurement.bind(this));
        document.removeEventListener('mousemove', this.updateMeasurement.bind(this));
        document.removeEventListener('mouseup', this.endMeasurement.bind(this));
    }

    startMeasurement(e) {
        this.measurementStart = { x: e.clientX, y: e.clientY };
        this.measurementActive = true;
    }

    updateMeasurement(e) {
        if (!this.measurementActive || !this.measurementStart) return;

        const current = { x: e.clientX, y: e.clientY };
        const width = Math.abs(current.x - this.measurementStart.x);
        const height = Math.abs(current.y - this.measurementStart.y);

        this.showMeasurementTooltip(e.clientX, e.clientY, width, height);
    }

    endMeasurement(e) {
        if (!this.measurementActive) return;

        const current = { x: e.clientX, y: e.clientY };
        const width = Math.abs(current.x - this.measurementStart.x);
        const height = Math.abs(current.y - this.measurementStart.y);

        this.measurements.set(Date.now(), {
            start: this.measurementStart,
            end: current,
            width,
            height,
            timestamp: Date.now()
        });

        this.measurementActive = false;
        this.hideMeasurementTooltip();
    }

    showMeasurementTooltip(x, y, width, height) {
        let tooltip = document.getElementById('eq12-measurement-tooltip');
        if (!tooltip) {
            tooltip = document.createElement('div');
            tooltip.id = 'eq12-measurement-tooltip';
            tooltip.style.cssText = `
                position: fixed;
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-family: monospace;
                font-size: 12px;
                z-index: 1000000;
                pointer-events: none;
            `;
            document.body.appendChild(tooltip);
        }

        tooltip.textContent = `${width}px × ${height}px`;
        tooltip.style.left = `${x + 10}px`;
        tooltip.style.top = `${y - 30}px`;
        tooltip.style.display = 'block';
    }

    hideMeasurementTooltip() {
        const tooltip = document.getElementById('eq12-measurement-tooltip');
        if (tooltip) {
            tooltip.style.display = 'none';
        }
    }

    // Advanced cache management inspired by Clear Cache extension
    async setupCacheManager() {
        this.cacheManager = {
            clearAll: async () => {
                try {
                    // Clear browser cache
                    await chrome.browsingData?.removeCache({});

                    // Clear local storage
                    if (typeof window !== 'undefined') {
                        window.localStorage.clear();
                        window.sessionStorage.clear();
                    }

                    // Clear IndexedDB
                    await this.clearIndexedDB();

                    console.log('🧹 All caches cleared');
                    return true;
                } catch (error) {
                    console.error('Cache clearing failed:', error);
                    return false;
                }
            },

            clearSiteData: async (url) => {
                try {
                    const domain = new URL(url).hostname;

                    // Clear cookies for domain
                    await chrome.browsingData?.removeCookies({
                        origins: [`https://${domain}`, `http://${domain}`]
                    });

                    // Clear cache for domain
                    await chrome.browsingData?.removeCache({
                        origins: [`https://${domain}`, `http://${domain}`]
                    });

                    console.log(`🧹 Cleared data for ${domain}`);
                    return true;
                } catch (error) {
                    console.error('Site data clearing failed:', error);
                    return false;
                }
            },

            getCacheSize: async () => {
                try {
                    if ('storage' in navigator && 'estimate' in navigator.storage) {
                        const estimate = await navigator.storage.estimate();
                        return {
                            used: estimate.usage,
                            available: estimate.quota,
                            percentage: (estimate.usage / estimate.quota * 100).toFixed(2)
                        };
                    }
                    return null;
                } catch (error) {
                    console.error('Cache size estimation failed:', error);
                    return null;
                }
            }
        };
    }

    async clearIndexedDB() {
        try {
            const databases = await indexedDB.databases();
            await Promise.all(
                databases.map(db => {
                    return new Promise((resolve, reject) => {
                        const deleteReq = indexedDB.deleteDatabase(db.name);
                        deleteReq.onsuccess = () => resolve();
                        deleteReq.onerror = () => reject(deleteReq.error);
                    });
                })
            );
        } catch (error) {
            console.error('IndexedDB clearing failed:', error);
        }
    }

    // Error tracking and reporting
    async setupErrorTracking() {
        // Global error handler
        window.addEventListener('error', (e) => {
            const errorEntry = {
                message: e.message,
                filename: e.filename,
                line: e.lineno,
                column: e.colno,
                stack: e.error?.stack,
                timestamp: Date.now(),
                type: 'javascript'
            };

            this.errorLogs.push(errorEntry);
            this.cleanupLogs();

            if (this.debugMode) {
                this.sendRemoteError(errorEntry);
            }
        });

        // Unhandled promise rejections
        window.addEventListener('unhandledrejection', (e) => {
            const errorEntry = {
                message: e.reason?.message || 'Unhandled Promise Rejection',
                stack: e.reason?.stack,
                timestamp: Date.now(),
                type: 'promise'
            };

            this.errorLogs.push(errorEntry);
            this.cleanupLogs();

            if (this.debugMode) {
                this.sendRemoteError(errorEntry);
            }
        });
    }

    // Remote debugging capabilities
    async enableAdvancedDebugging() {
        // Enable remote console
        try {
            const ws = new WebSocket('ws://localhost:9222/devtools/browser');
            ws.onopen = () => {
                console.log('🔗 Remote debugging connected');
            };
            ws.onmessage = (event) => {
                const message = JSON.parse(event.data);
                this.handleRemoteDebugMessage(message);
            };
        } catch (error) {
            console.log('Remote debugging not available');
        }
    }

    async sendRemoteLog(logEntry) {
        try {
            await fetch('http://localhost:8000/api/debug/logs', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(logEntry)
            });
        } catch (error) {
            // Remote logging not available
        }
    }

    async sendRemoteError(errorEntry) {
        try {
            await fetch('http://localhost:8000/api/debug/errors', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(errorEntry)
            });
        } catch (error) {
            // Remote error reporting not available
        }
    }

    // Utility methods
    serializeLogArg(arg) {
        if (typeof arg === 'object' && arg !== null) {
            try {
                return JSON.parse(JSON.stringify(arg));
            } catch (e) {
                return '[Object - could not serialize]';
            }
        }
        return arg;
    }

    cleanupLogs() {
        if (this.networkLogs.length > 1000) {
            this.networkLogs = this.networkLogs.slice(-1000);
        }
        if (this.errorLogs.length > 1000) {
            this.errorLogs = this.errorLogs.slice(-1000);
        }
    }

    getFirstPaint() {
        const paintEntries = performance.getEntriesByType('paint');
        const firstPaint = paintEntries.find(entry => entry.name === 'first-paint');
        return firstPaint ? firstPaint.startTime : null;
    }

    getFirstContentfulPaint() {
        const paintEntries = performance.getEntriesByType('paint');
        const fcp = paintEntries.find(entry => entry.name === 'first-contentful-paint');
        return fcp ? fcp.startTime : null;
    }

    async checkDeveloperMode() {
        try {
            // Check if developer tools are open
            const devtools = window.outerHeight - window.innerHeight > 200 ||
                window.outerWidth - window.innerWidth > 200;

            // Check if extension is in developer mode
            const manifest = chrome.runtime?.getManifest?.();
            const isDev = manifest && !('update_url' in manifest);

            return devtools || isDev;
        } catch (error) {
            return false;
        }
    }

    measureElement(selector) {
        const element = document.querySelector(selector);
        if (!element) {
            console.error('Element not found:', selector);
            return null;
        }

        const rect = element.getBoundingClientRect();
        const computedStyle = window.getComputedStyle(element);

        const measurement = {
            selector,
            dimensions: {
                width: rect.width,
                height: rect.height,
                top: rect.top,
                left: rect.left
            },
            style: {
                margin: computedStyle.margin,
                padding: computedStyle.padding,
                border: computedStyle.border,
                position: computedStyle.position
            },
            timestamp: Date.now()
        };

        console.log('📏 Element measurement:', measurement);
        return measurement;
    }

    inspectElement(element) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }

        if (!element) {
            console.error('Element not found');
            return null;
        }

        const inspection = {
            tagName: element.tagName,
            id: element.id,
            className: element.className,
            attributes: Array.from(element.attributes).map(attr => ({
                name: attr.name,
                value: attr.value
            })),
            computedStyle: window.getComputedStyle(element),
            eventListeners: this.getEventListeners(element),
            children: element.children.length,
            parent: element.parentElement?.tagName
        };

        console.log('🔍 Element inspection:', inspection);
        return inspection;
    }

    getEventListeners(element) {
        // This is a simplified version - actual implementation would need developer tools integration
        return ['click', 'mouseover', 'mouseout'].filter(event => {
            return element[`on${event}`] !== null;
        });
    }

    async exportDebugData() {
        const debugData = {
            timestamp: Date.now(),
            consoleLogs: this.consoleLogs,
            networkLogs: this.networkLogs,
            errorLogs: this.errorLogs,
            performanceMetrics: Object.fromEntries(this.performanceMetrics),
            measurements: Object.fromEntries(this.measurements),
            cacheInfo: await this.cacheManager.getCacheSize(),
            userAgent: navigator.userAgent,
            url: window.location.href
        };

        // Create downloadable file
        const blob = new Blob([JSON.stringify(debugData, null, 2)], {
            type: 'application/json'
        });

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `eq12-debug-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        console.log('📄 Debug data exported');
        return debugData;
    }

    // Public API
    getDebugInfo() {
        return {
            consoleLogs: this.consoleLogs.length,
            networkLogs: this.networkLogs.length,
            errorLogs: this.errorLogs.length,
            performanceEntries: this.performanceMetrics.size,
            measurements: this.measurements.size,
            debugMode: this.debugMode
        };
    }
}

// Export for use in content scripts and background
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EQ12DeveloperTools;
} else if (typeof self !== 'undefined') {
    self.EQ12DeveloperTools = EQ12DeveloperTools;
}
