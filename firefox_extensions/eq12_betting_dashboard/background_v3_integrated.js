// EQ12 Enhanced Background Service Worker - Integrated API & Advanced Features
import './developer_tools.js';
import './privacy_manager.js';
import './proxy_manager.js';
import './tab_manager.js';
import './ui_enhancer.js';

// Default configuration
const DEFAULTS = {
    apiBase: "http://localhost:8000", // EQ12 FastAPI backend
    apiKey: "",                       // X-API-Key header
    enableNotifications: true,
    autoRefreshInterval: 60,          // seconds
    evThreshold: 0.5,                 // minimum EV for notifications
    privacyLevel: "balanced",         // strict, balanced, minimal
    vpnRequired: false                // require VPN for betting sites
};

// Enhanced settings management
async function getSettings() {
    const stored = await browser.storage.local.get(Object.keys(DEFAULTS));
    return { ...DEFAULTS, ...stored };
}

async function saveSettings(settings) {
    await browser.storage.local.set(settings);
    return settings;
}

// Enhanced API calling with retry logic
async function callEq12(path, params = {}, options = {}) {
    const { apiBase, apiKey } = await getSettings();
    const url = new URL(path, apiBase);

    // Add query parameters
    Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null) {
            url.searchParams.set(k, String(v));
        }
    });

    const headers = {
        "Content-Type": "application/json",
        "User-Agent": "EQ12-Extension/1.0"
    };

    if (apiKey) {
        headers["X-API-Key"] = apiKey;
    }

    const fetchOptions = {
        method: options.method || 'GET',
        headers,
        ...options
    };

    // Add request body for POST/PUT requests
    if (options.body && (options.method === 'POST' || options.method === 'PUT')) {
        fetchOptions.body = JSON.stringify(options.body);
    }

    try {
        const res = await fetch(url.toString(), fetchOptions);

        if (!res.ok) {
            const errorText = await res.text();
            throw new Error(`EQ12 API ${res.status}: ${errorText}`);
        }

        const contentType = res.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
            return await res.json();
        } else {
            return await res.text();
        }
    } catch (err) {
        console.error('EQ12 API Error:', err);
        throw err;
    }
}

// Enhanced message routing with caching
browser.runtime.onMessage.addListener(async (msg, sender, sendResponse) => {
    try {
        const startTime = Date.now();
        let result = null;

        switch (msg.type) {
            case "GET_PARLAY":
                result = await handleGetParlay(msg);
                break;

            case "GET_AUDIT":
                result = await handleGetAudit(msg);
                break;

            case "GET_PRIVACY_STATUS":
                result = await handleGetPrivacyStatus();
                break;

            case "GET_DEV_TOOLS_STATUS":
                result = await handleGetDevToolsStatus();
                break;

            case "GET_VPN_STATUS":
                result = await handleGetVpnStatus();
                break;

            case "GET_SETTINGS":
                result = await getSettings();
                break;

            case "SET_SETTINGS":
                result = await handleSetSettings(msg);
                break;

            case "PING":
                result = await handlePing();
                break;

            case "CLEAR_CACHE":
                result = await handleClearCache();
                break;

            case "EXPORT_DATA":
                result = await handleExportData(msg);
                break;

            default:
                throw new Error(`Unknown message type: ${msg.type}`);
        }

        const responseTime = Date.now() - startTime;
        console.log(`EQ12 API: ${msg.type} completed in ${responseTime}ms`);

        return { ok: true, data: result, responseTime };

    } catch (err) {
        console.error(`EQ12 API Error (${msg.type}):`, err);
        return { ok: false, error: String(err) };
    }
});

// Parlay generation handler with caching
async function handleGetParlay(msg) {
    const size = msg.size || 5;
    const cacheKey = `parlay_${size}_${Date.now() - (Date.now() % 300000)}`; // 5min cache

    // Check cache first
    const cached = await browser.storage.local.get([cacheKey]);
    if (cached[cacheKey]) {
        console.log('EQ12: Returning cached parlay');
        return cached[cacheKey];
    }

    // Generate new parlay
    const data = await callEq12("/api/parlay", {
        size,
        include_ev: true,
        include_analysis: true,
        risk_level: msg.riskLevel || 'medium'
    });

    // Cache result
    await browser.storage.local.set({
        [cacheKey]: data,
        lastParlay: data
    });

    // Send notification for high-EV parlays
    const settings = await getSettings();
    if (settings.enableNotifications && data.ev && data.ev > settings.evThreshold) {
        await browser.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon-48.png',
            title: 'EQ12: High EV Parlay Found!',
            message: `${size}-leg parlay with +$${data.ev.toFixed(2)} expected value`
        });
    }

    return data;
}

// Audit report handler
async function handleGetAudit(msg) {
    const last = msg.last || 10;

    const data = await callEq12("/api/audit", {
        last,
        include_summary: true,
        include_performance: true
    });

    // Cache audit data
    await browser.storage.local.set({ lastAudit: data });

    return data;
}

// Privacy status handler
async function handleGetPrivacyStatus() {
    // Get status from privacy manager
    const privacyStats = await browser.storage.local.get([
        'trackersBlocked', 'fingerprintingEnabled', 'webrtcProtected', 'dnsProtected'
    ]);

    return {
        trackers_blocked: privacyStats.trackersBlocked || 0,
        fingerprint_protection: privacyStats.fingerprintingEnabled !== false,
        webrtc_protected: privacyStats.webrtcProtected !== false,
        dns_protected: privacyStats.dnsProtected !== false,
        last_scan: privacyStats.lastPrivacyScan || null
    };
}

// Developer tools status handler
async function handleGetDevToolsStatus() {
    const devToolsStats = await browser.storage.local.get([
        'debugConsoleActive', 'performanceMonitoring', 'networkInterception'
    ]);

    return {
        console_active: devToolsStats.debugConsoleActive || false,
        performance_active: devToolsStats.performanceMonitoring || false,
        network_active: devToolsStats.networkInterception || false,
        last_check: Date.now()
    };
}

// VPN status handler with leak detection
async function handleGetVpnStatus() {
    try {
        // Get VPN status from proxy manager
        const vpnStats = await browser.storage.local.get([
            'vpnConnected', 'vpnLocation', 'lastLeakCheck', 'leakDetected'
        ]);

        // Get current public IP
        let publicIp = null;
        try {
            const ipResponse = await fetch('https://api.ipify.org?format=json');
            const ipData = await ipResponse.json();
            publicIp = ipData.ip;
        } catch (err) {
            console.warn('Failed to get public IP:', err);
        }

        return {
            connected: vpnStats.vpnConnected || false,
            location: vpnStats.vpnLocation || null,
            public_ip: publicIp,
            leak_detected: vpnStats.leakDetected || false,
            leak_type: vpnStats.leakType || null,
            last_check: vpnStats.lastLeakCheck || null
        };
    } catch (err) {
        console.error('VPN status error:', err);
        return {
            connected: false,
            error: String(err)
        };
    }
}

// Settings update handler
async function handleSetSettings(msg) {
    const newSettings = {
        apiBase: msg.apiBase?.trim() || DEFAULTS.apiBase,
        apiKey: msg.apiKey?.trim() || DEFAULTS.apiKey,
        enableNotifications: msg.enableNotifications !== false,
        autoRefreshInterval: msg.autoRefreshInterval || DEFAULTS.autoRefreshInterval,
        evThreshold: msg.evThreshold || DEFAULTS.evThreshold,
        privacyLevel: msg.privacyLevel || DEFAULTS.privacyLevel,
        vpnRequired: msg.vpnRequired || false
    };

    await saveSettings(newSettings);

    // Update alarm for auto-refresh if changed
    if (msg.autoRefreshInterval !== undefined) {
        await browser.alarms.clear('autoRefresh');
        if (newSettings.autoRefreshInterval > 0) {
            await browser.alarms.create('autoRefresh', {
                delayInMinutes: newSettings.autoRefreshInterval / 60,
                periodInMinutes: newSettings.autoRefreshInterval / 60
            });
        }
    }

    return newSettings;
}

// Ping handler with health check
async function handlePing() {
    const health = await callEq12("/api/health");

    // Store connection status
    await browser.storage.local.set({
        lastPing: Date.now(),
        serverHealth: health
    });

    return {
        status: "ok",
        timestamp: new Date().toISOString(),
        server: health
    };
}

// Cache clearing handler
async function handleClearCache() {
    const keys = await browser.storage.local.get();
    const cacheKeys = Object.keys(keys).filter(key =>
        key.startsWith('parlay_') ||
        key.startsWith('audit_') ||
        key.startsWith('cache_')
    );

    await browser.storage.local.remove(cacheKeys);

    return {
        cleared: cacheKeys.length,
        keys: cacheKeys
    };
}

// Data export handler
async function handleExportData(msg) {
    const allData = await browser.storage.local.get();

    const exportData = {
        timestamp: new Date().toISOString(),
        version: "1.0.0",
        settings: await getSettings(),
        cache: allData,
        type: msg.exportType || 'full'
    };

    return exportData;
}

// Auto-refresh alarm handler
browser.alarms.onAlarm.addListener(async (alarm) => {
    if (alarm.name === 'autoRefresh') {
        console.log('EQ12: Auto-refreshing data...');

        try {
            // Refresh parlay data in background
            const settings = await getSettings();
            if (settings.autoRefreshInterval > 0) {
                await handleGetParlay({ size: 5 });
                await handleGetAudit({ last: 5 });
            }
        } catch (err) {
            console.error('Auto-refresh error:', err);
        }
    }
});

// Enhanced installation and updates
browser.runtime.onInstalled.addListener(async (details) => {
    console.log('EQ12 Extension installed/updated:', details);

    if (details.reason === 'install') {
        // First-time installation
        await saveSettings(DEFAULTS);

        // Create welcome notification
        await browser.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon-48.png',
            title: 'Welcome to EQ12!',
            message: 'Your betting dashboard is ready. Configure API settings to get started.'
        });

        // Open options page
        await browser.runtime.openOptionsPage();
    }

    if (details.reason === 'update') {
        // Extension update - preserve settings but add new defaults
        const current = await browser.storage.local.get();
        const updated = { ...DEFAULTS, ...current };
        await saveSettings(updated);
    }
});

// Enhanced startup initialization
browser.runtime.onStartup.addListener(async () => {
    console.log('EQ12 Extension starting up...');

    // Initialize enhanced modules
    try {
        // Privacy manager initialization
        const privacyManager = await import('./privacy_manager.js');
        await privacyManager.initialize();

        // Developer tools initialization
        const developerTools = await import('./developer_tools.js');
        await developerTools.initialize();

        // UI enhancer initialization
        const uiEnhancer = await import('./ui_enhancer.js');
        await uiEnhancer.initialize();

        // Proxy manager initialization
        const proxyManager = await import('./proxy_manager.js');
        await proxyManager.initialize();

        // Tab manager initialization
        const tabManager = await import('./tab_manager.js');
        await tabManager.initialize();

        console.log('EQ12: All enhanced modules initialized');
    } catch (err) {
        console.error('EQ12 Enhanced module initialization error:', err);
    }

    // Set up auto-refresh alarm
    const settings = await getSettings();
    if (settings.autoRefreshInterval > 0) {
        await browser.alarms.create('autoRefresh', {
            delayInMinutes: 1, // Start after 1 minute
            periodInMinutes: settings.autoRefreshInterval / 60
        });
    }
});

// Context menu setup for enhanced features
browser.contextMenus.onClicked.addListener(async (info, tab) => {
    if (info.menuItemId === 'eq12-analyze-selection') {
        // Analyze selected text as potential bet
        const selection = info.selectionText;
        if (selection) {
            try {
                const analysis = await callEq12('/api/analyze', { selection });

                await browser.notifications.create({
                    type: 'basic',
                    iconUrl: 'icons/icon-48.png',
                    title: 'EQ12 Bet Analysis',
                    message: `${selection}: ${analysis.recommendation || 'Analysis complete'}`
                });
            } catch (err) {
                console.error('Selection analysis error:', err);
            }
        }
    }
});

// Create context menus on installation
browser.runtime.onInstalled.addListener(() => {
    browser.contextMenus.create({
        id: 'eq12-analyze-selection',
        title: 'Analyze with EQ12',
        contexts: ['selection']
    });
});

console.log('EQ12 Enhanced Background Service Worker loaded successfully!');
