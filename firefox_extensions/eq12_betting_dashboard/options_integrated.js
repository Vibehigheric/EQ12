// EQ12 Options Configuration Script
const elements = {
    // API Configuration
    apiBase: document.getElementById("apiBase"),
    apiKey: document.getElementById("apiKey"),
    testConnection: document.getElementById("testConnection"),

    // Parlay Configuration
    evThreshold: document.getElementById("evThreshold"),
    autoRefreshInterval: document.getElementById("autoRefreshInterval"),
    enableNotifications: document.getElementById("enableNotifications"),

    // Privacy & Security
    privacyLevel: document.getElementById("privacyLevel"),
    vpnRequired: document.getElementById("vpnRequired"),

    // Advanced Settings
    debugLevel: document.getElementById("debugLevel"),
    customCSS: document.getElementById("customCSS"),
    developerMode: document.getElementById("developerMode"),

    // Actions
    save: document.getElementById("save"),
    reset: document.getElementById("reset"),
    export: document.getElementById("export"),
    import: document.getElementById("import"),
    importFile: document.getElementById("importFile"),

    // Status
    status: document.getElementById("status")
};

// Show status message
function showStatus(message, type = 'info') {
    elements.status.textContent = message;
    elements.status.className = `status ${type}`;
    elements.status.style.display = 'block';

    // Auto-hide success/info messages after 5 seconds
    if (type === 'success' || type === 'info') {
        setTimeout(() => {
            elements.status.style.display = 'none';
        }, 5000);
    }
}

// Load current settings
async function loadSettings() {
    try {
        showStatus("Loading current settings...", 'info');

        const response = await browser.runtime.sendMessage({ type: "GET_SETTINGS" });

        if (!response?.ok) {
            throw new Error(response?.error || "Failed to load settings");
        }

        const settings = response.data;

        // Populate API settings
        elements.apiBase.value = settings.apiBase || "";
        elements.apiKey.value = settings.apiKey || "";

        // Populate parlay settings
        elements.evThreshold.value = settings.evThreshold || 0.5;
        elements.autoRefreshInterval.value = settings.autoRefreshInterval || 60;
        elements.enableNotifications.checked = settings.enableNotifications !== false;

        // Populate privacy settings
        elements.privacyLevel.value = settings.privacyLevel || "balanced";
        elements.vpnRequired.checked = settings.vpnRequired || false;

        // Populate advanced settings
        elements.debugLevel.value = settings.debugLevel || "info";
        elements.customCSS.value = settings.customCSS || "";
        elements.developerMode.checked = settings.developerMode || false;

        showStatus("✅ Settings loaded successfully", 'success');

    } catch (err) {
        console.error('Failed to load settings:', err);
        showStatus(`❌ Failed to load settings: ${err.message}`, 'error');
    }
}

// Save current settings
async function saveSettings() {
    try {
        showStatus("Saving settings...", 'info');

        const settings = {
            // API Configuration
            apiBase: elements.apiBase.value.trim(),
            apiKey: elements.apiKey.value.trim(),

            // Parlay Configuration
            evThreshold: parseFloat(elements.evThreshold.value) || 0.5,
            autoRefreshInterval: parseInt(elements.autoRefreshInterval.value) || 60,
            enableNotifications: elements.enableNotifications.checked,

            // Privacy & Security
            privacyLevel: elements.privacyLevel.value,
            vpnRequired: elements.vpnRequired.checked,

            // Advanced Settings
            debugLevel: elements.debugLevel.value,
            customCSS: elements.customCSS.value.trim(),
            developerMode: elements.developerMode.checked
        };

        // Validate settings
        if (settings.apiBase && !isValidUrl(settings.apiBase)) {
            throw new Error("Invalid API Base URL format");
        }

        if (settings.evThreshold < 0 || settings.evThreshold > 100) {
            throw new Error("EV Threshold must be between 0 and 100");
        }

        if (settings.autoRefreshInterval < 0 || settings.autoRefreshInterval > 3600) {
            throw new Error("Auto-refresh interval must be between 0 and 3600 seconds");
        }

        const response = await browser.runtime.sendMessage({
            type: "SET_SETTINGS",
            ...settings
        });

        if (!response?.ok) {
            throw new Error(response?.error || "Failed to save settings");
        }

        showStatus("✅ Settings saved successfully", 'success');

        // Show additional info if developer mode was enabled
        if (settings.developerMode) {
            setTimeout(() => {
                showStatus("🔧 Developer mode enabled. Check extension console for debug logs.", 'info');
            }, 2000);
        }

    } catch (err) {
        console.error('Failed to save settings:', err);
        showStatus(`❌ Failed to save settings: ${err.message}`, 'error');
    }
}

// Test API connection
async function testConnection() {
    try {
        showStatus("Testing API connection...", 'info');

        // First save current API settings temporarily
        const tempApiBase = elements.apiBase.value.trim();
        const tempApiKey = elements.apiKey.value.trim();

        if (!tempApiBase) {
            throw new Error("Please enter an API Base URL first");
        }

        if (!isValidUrl(tempApiBase)) {
            throw new Error("Invalid API Base URL format");
        }

        // Save temporarily for testing
        await browser.runtime.sendMessage({
            type: "SET_SETTINGS",
            apiBase: tempApiBase,
            apiKey: tempApiKey
        });

        // Test the connection
        const response = await browser.runtime.sendMessage({ type: "PING" });

        if (!response?.ok) {
            throw new Error(response?.error || "Connection failed");
        }

        const serverInfo = response.data?.server || {};
        const status = `✅ Connection successful!\n` +
            `Server: ${serverInfo.name || 'EQ12 Backend'}\n` +
            `Version: ${serverInfo.version || 'Unknown'}\n` +
            `Status: ${serverInfo.status || 'OK'}\n` +
            `Response Time: ${response.responseTime || 0}ms`;

        showStatus(status, 'success');

    } catch (err) {
        console.error('Connection test failed:', err);
        showStatus(`❌ Connection test failed: ${err.message}`, 'error');
    }
}

// Reset to default settings
async function resetSettings() {
    if (!confirm("Are you sure you want to reset all settings to defaults? This cannot be undone.")) {
        return;
    }

    try {
        showStatus("Resetting to default settings...", 'info');

        // Clear all stored settings
        await browser.storage.local.clear();

        // Reload the page to get defaults
        await loadSettings();

        showStatus("✅ Settings reset to defaults", 'success');

    } catch (err) {
        console.error('Failed to reset settings:', err);
        showStatus(`❌ Failed to reset settings: ${err.message}`, 'error');
    }
}

// Export configuration
async function exportConfig() {
    try {
        showStatus("Exporting configuration...", 'info');

        const response = await browser.runtime.sendMessage({
            type: "EXPORT_DATA",
            exportType: 'settings'
        });

        if (!response?.ok) {
            throw new Error(response?.error || "Failed to export configuration");
        }

        const configData = {
            version: "1.0.0",
            timestamp: new Date().toISOString(),
            settings: response.data.settings,
            exported_by: "EQ12 Extension v1.0.0"
        };

        const blob = new Blob([JSON.stringify(configData, null, 2)], {
            type: 'application/json'
        });

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `eq12_config_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        showStatus("✅ Configuration exported successfully", 'success');

    } catch (err) {
        console.error('Failed to export configuration:', err);
        showStatus(`❌ Failed to export configuration: ${err.message}`, 'error');
    }
}

// Import configuration
function importConfig() {
    elements.importFile.click();
}

// Handle file import
async function handleFileImport(event) {
    const file = event.target.files[0];
    if (!file) return;

    try {
        showStatus("Importing configuration...", 'info');

        const text = await file.text();
        const configData = JSON.parse(text);

        // Validate config structure
        if (!configData.settings) {
            throw new Error("Invalid configuration file format");
        }

        // Apply imported settings
        const response = await browser.runtime.sendMessage({
            type: "SET_SETTINGS",
            ...configData.settings
        });

        if (!response?.ok) {
            throw new Error(response?.error || "Failed to apply imported settings");
        }

        // Reload settings display
        await loadSettings();

        showStatus(`✅ Configuration imported successfully from ${configData.timestamp || 'unknown date'}`, 'success');

    } catch (err) {
        console.error('Failed to import configuration:', err);
        showStatus(`❌ Failed to import configuration: ${err.message}`, 'error');
    } finally {
        // Reset file input
        elements.importFile.value = '';
    }
}

// URL validation helper
function isValidUrl(string) {
    try {
        const url = new URL(string);
        return url.protocol === 'http:' || url.protocol === 'https:';
    } catch (_) {
        return false;
    }
}

// Event listeners
elements.save.addEventListener("click", saveSettings);
elements.testConnection.addEventListener("click", testConnection);
elements.reset.addEventListener("click", resetSettings);
elements.export.addEventListener("click", exportConfig);
elements.import.addEventListener("click", importConfig);
elements.importFile.addEventListener("change", handleFileImport);

// Auto-save on certain changes
elements.enableNotifications.addEventListener("change", () => {
    // Auto-save notification preference immediately
    setTimeout(saveSettings, 100);
});

elements.vpnRequired.addEventListener("change", () => {
    // Auto-save VPN requirement immediately for security
    setTimeout(saveSettings, 100);
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
            case 's':
                e.preventDefault();
                saveSettings();
                break;
            case 'r':
                e.preventDefault();
                resetSettings();
                break;
            case 't':
                e.preventDefault();
                testConnection();
                break;
        }
    }
});

// Privacy level change handler
elements.privacyLevel.addEventListener('change', () => {
    const level = elements.privacyLevel.value;
    let description = "";

    switch (level) {
        case 'minimal':
            description = "Basic tracker blocking only. Fastest performance.";
            break;
        case 'balanced':
            description = "Recommended setting. Good balance of protection and performance.";
            break;
        case 'strict':
            description = "Maximum protection. May break some sites.";
            break;
        case 'custom':
            description = "Manual configuration required in advanced settings.";
            break;
    }

    showStatus(`Privacy level: ${description}`, 'info');
});

// Initialize the options page
async function initialize() {
    showStatus("Initializing EQ12 settings...", 'info');

    try {
        await loadSettings();

        // Show welcome message for first-time users
        const response = await browser.runtime.sendMessage({ type: "GET_SETTINGS" });
        if (response?.ok && (!response.data.apiBase || response.data.apiBase === "http://localhost:8000")) {
            setTimeout(() => {
                showStatus("👋 Welcome to EQ12! Please configure your API settings to get started.", 'info');
            }, 1000);
        }

    } catch (err) {
        console.error('Failed to initialize options page:', err);
        showStatus(`❌ Initialization failed: ${err.message}`, 'error');
    }
}

// Start initialization
initialize();
