// EQ12 Options Page Controller - Advanced Tab Management and Settings
// Implements MDN best practices for extension options and tab manipulation

class EQ12OptionsController {
    constructor() {
        this.settings = {};
        this.defaultSettings = {
            vpn: {
                provider: 'wireguard',
                configPath: 'C:\\EQ12\\eq12-betting.conf',
                checkInterval: 30,
                autoReconnect: true
            },
            telegram: {
                botToken: '',
                chatId: '',
                notifications: true,
                betConfirmations: true
            },
            sportsbooks: {
                draftkings: true,
                fanduel: true,
                betmgm: true,
                scrapeInterval: 60,
                minEV: 5
            },
            api: {
                baseUrl: 'http://localhost:8000',
                apiKey: '',
                autoSync: true
            },
            advanced: {
                debugMode: false,
                maxLogEntries: 1000,
                customCSS: ''
            }
        };

        this.init();
    }

    async init() {
        console.log('🎯 EQ12 Options Controller initializing...');

        try {
            await this.loadSettings();
            this.setupEventListeners();
            this.populateForm();

            console.log('✅ Options controller ready');
        } catch (error) {
            console.error('Options initialization error:', error);
            this.showError('Failed to initialize options: ' + error.message);
        }
    }

    async loadSettings() {
        try {
            const stored = await chrome.storage.sync.get(['eq12Settings']);
            this.settings = { ...this.defaultSettings, ...stored.eq12Settings };
        } catch (error) {
            console.warn('Failed to load settings, using defaults:', error);
            this.settings = this.defaultSettings;
        }
    }

    setupEventListeners() {
        // Test buttons
        document.getElementById('test-vpn')?.addEventListener('click', () => {
            this.testVPNConnection();
        });

        document.getElementById('test-telegram')?.addEventListener('click', () => {
            this.testTelegramBot();
        });

        document.getElementById('test-api')?.addEventListener('click', () => {
            this.testAPIConnection();
        });

        // Save/Reset buttons
        document.getElementById('save-settings')?.addEventListener('click', () => {
            this.saveSettings();
        });

        document.getElementById('reset-settings')?.addEventListener('click', () => {
            this.resetSettings();
        });

        // Export/Import
        document.getElementById('export-settings')?.addEventListener('click', () => {
            this.exportSettings();
        });

        document.getElementById('import-settings')?.addEventListener('click', () => {
            this.importSettings();
        });

        // Real-time validation
        this.setupFormValidation();
    }

    populateForm() {
        // VPN Settings
        document.getElementById('vpn-provider').value = this.settings.vpn.provider;
        document.getElementById('vpn-config').value = this.settings.vpn.configPath;
        document.getElementById('vpn-check-interval').value = this.settings.vpn.checkInterval;
        document.getElementById('vpn-auto-reconnect').checked = this.settings.vpn.autoReconnect;

        // Telegram Settings
        document.getElementById('telegram-token').value = this.settings.telegram.botToken;
        document.getElementById('telegram-chat-id').value = this.settings.telegram.chatId;
        document.getElementById('telegram-notifications').checked = this.settings.telegram.notifications;
        document.getElementById('telegram-bet-confirmations').checked = this.settings.telegram.betConfirmations;

        // Sportsbook Settings
        document.getElementById('sb-draftkings').checked = this.settings.sportsbooks.draftkings;
        document.getElementById('sb-fanduel').checked = this.settings.sportsbooks.fanduel;
        document.getElementById('sb-betmgm').checked = this.settings.sportsbooks.betmgm;
        document.getElementById('scrape-interval').value = this.settings.sportsbooks.scrapeInterval;
        document.getElementById('min-ev').value = this.settings.sportsbooks.minEV;

        // API Settings
        document.getElementById('api-base-url').value = this.settings.api.baseUrl;
        document.getElementById('api-key').value = this.settings.api.apiKey;
        document.getElementById('api-auto-sync').checked = this.settings.api.autoSync;

        // Advanced Settings
        document.getElementById('debug-mode').checked = this.settings.advanced.debugMode;
        document.getElementById('max-log-entries').value = this.settings.advanced.maxLogEntries;
        document.getElementById('custom-css').value = this.settings.advanced.customCSS;
    }

    async saveSettings() {
        try {
            // Collect form data
            const newSettings = {
                vpn: {
                    provider: document.getElementById('vpn-provider').value,
                    configPath: document.getElementById('vpn-config').value,
                    checkInterval: parseInt(document.getElementById('vpn-check-interval').value),
                    autoReconnect: document.getElementById('vpn-auto-reconnect').checked
                },
                telegram: {
                    botToken: document.getElementById('telegram-token').value,
                    chatId: document.getElementById('telegram-chat-id').value,
                    notifications: document.getElementById('telegram-notifications').checked,
                    betConfirmations: document.getElementById('telegram-bet-confirmations').checked
                },
                sportsbooks: {
                    draftkings: document.getElementById('sb-draftkings').checked,
                    fanduel: document.getElementById('sb-fanduel').checked,
                    betmgm: document.getElementById('sb-betmgm').checked,
                    scrapeInterval: parseInt(document.getElementById('scrape-interval').value),
                    minEV: parseFloat(document.getElementById('min-ev').value)
                },
                api: {
                    baseUrl: document.getElementById('api-base-url').value,
                    apiKey: document.getElementById('api-key').value,
                    autoSync: document.getElementById('api-auto-sync').checked
                },
                advanced: {
                    debugMode: document.getElementById('debug-mode').checked,
                    maxLogEntries: parseInt(document.getElementById('max-log-entries').value),
                    customCSS: document.getElementById('custom-css').value
                }
            };

            // Validate settings
            const validation = this.validateSettings(newSettings);
            if (!validation.valid) {
                throw new Error(validation.error);
            }

            // Save to storage
            await chrome.storage.sync.set({ eq12Settings: newSettings });
            this.settings = newSettings;

            // Notify background script of settings change
            chrome.runtime.sendMessage({
                action: 'settingsUpdated',
                data: newSettings
            });

            this.showSuccess('Settings saved successfully');

            // Update content scripts in open sportsbook tabs
            await this.updateContentScripts();

        } catch (error) {
            console.error('Save settings error:', error);
            this.showError('Failed to save settings: ' + error.message);
        }
    }

    validateSettings(settings) {
        // Validate VPN check interval
        if (settings.vpn.checkInterval < 10 || settings.vpn.checkInterval > 300) {
            return { valid: false, error: 'VPN check interval must be between 10-300 seconds' };
        }

        // Validate Telegram bot token format
        if (settings.telegram.botToken && !settings.telegram.botToken.match(/^\d+:[A-Za-z0-9_-]+$/)) {
            return { valid: false, error: 'Invalid Telegram bot token format' };
        }

        // Validate chat ID format
        if (settings.telegram.chatId && !settings.telegram.chatId.match(/^-?\d+$/)) {
            return { valid: false, error: 'Invalid Telegram chat ID format' };
        }

        // Validate API URL
        if (settings.api.baseUrl && !this.isValidUrl(settings.api.baseUrl)) {
            return { valid: false, error: 'Invalid API base URL' };
        }

        // Validate scrape interval
        if (settings.sportsbooks.scrapeInterval < 30) {
            return { valid: false, error: 'Scrape interval must be at least 30 seconds' };
        }

        // Validate EV threshold
        if (settings.sportsbooks.minEV < 0 || settings.sportsbooks.minEV > 50) {
            return { valid: false, error: 'Expected value threshold must be between 0-50%' };
        }

        return { valid: true };
    }

    async updateContentScripts() {
        try {
            // Get all tabs with sportsbook domains
            const tabs = await chrome.tabs.query({});
            const sportsbookTabs = tabs.filter(tab => this.isSportsbookTab(tab.url));

            for (const tab of sportsbookTabs) {
                try {
                    // Send updated settings to content script
                    await chrome.tabs.sendMessage(tab.id, {
                        action: 'updateSettings',
                        data: this.settings
                    });
                } catch (error) {
                    console.warn(`Failed to update content script in tab ${tab.id}:`, error);
                }
            }

            if (sportsbookTabs.length > 0) {
                this.showSuccess(`Updated settings in ${sportsbookTabs.length} sportsbook tabs`);
            }
        } catch (error) {
            console.error('Content script update error:', error);
        }
    }

    async resetSettings() {
        if (!confirm('This will reset all settings to defaults. Continue?')) {
            return;
        }

        try {
            this.settings = { ...this.defaultSettings };
            this.populateForm();
            await chrome.storage.sync.remove(['eq12Settings']);

            this.showSuccess('Settings reset to defaults');
        } catch (error) {
            console.error('Reset settings error:', error);
            this.showError('Failed to reset settings');
        }
    }

    async testVPNConnection() {
        const button = document.getElementById('test-vpn');
        const resultsDiv = document.getElementById('vpn-test-results');

        this.setButtonLoading(button, true);

        try {
            const response = await chrome.runtime.sendMessage({
                action: 'testVpnConnection',
                data: {
                    provider: document.getElementById('vpn-provider').value,
                    configPath: document.getElementById('vpn-config').value
                }
            });

            if (response.success) {
                this.showTestResult(resultsDiv, 'success',
                    `✅ VPN connection successful\nIP: ${response.data.ip}\nLocation: ${response.data.location || 'Unknown'}`);
            } else {
                throw new Error(response.error);
            }
        } catch (error) {
            this.showTestResult(resultsDiv, 'error',
                `❌ VPN connection failed: ${error.message}`);
        } finally {
            this.setButtonLoading(button, false);
        }
    }

    async testTelegramBot() {
        const button = document.getElementById('test-telegram');
        const resultsDiv = document.getElementById('telegram-test-results');

        const botToken = document.getElementById('telegram-token').value;
        const chatId = document.getElementById('telegram-chat-id').value;

        if (!botToken || !chatId) {
            this.showTestResult(resultsDiv, 'error', '❌ Bot token and chat ID are required');
            return;
        }

        this.setButtonLoading(button, true);

        try {
            const response = await chrome.runtime.sendMessage({
                action: 'testTelegramBot',
                data: { botToken, chatId }
            });

            if (response.success) {
                this.showTestResult(resultsDiv, 'success',
                    `✅ Telegram bot connected\nBot: ${response.data.botName}\nTest message sent successfully`);
            } else {
                throw new Error(response.error);
            }
        } catch (error) {
            this.showTestResult(resultsDiv, 'error',
                `❌ Telegram bot test failed: ${error.message}`);
        } finally {
            this.setButtonLoading(button, false);
        }
    }

    async testAPIConnection() {
        const button = document.getElementById('test-api');
        const resultsDiv = document.getElementById('api-test-results');

        const baseUrl = document.getElementById('api-base-url').value;
        const apiKey = document.getElementById('api-key').value;

        if (!baseUrl) {
            this.showTestResult(resultsDiv, 'error', '❌ API base URL is required');
            return;
        }

        this.setButtonLoading(button, true);

        try {
            const response = await chrome.runtime.sendMessage({
                action: 'testApiConnection',
                data: { baseUrl, apiKey }
            });

            if (response.success) {
                this.showTestResult(resultsDiv, 'success',
                    `✅ EQ12 API connected\nVersion: ${response.data.version}\nStatus: ${response.data.status}`);
            } else {
                throw new Error(response.error);
            }
        } catch (error) {
            this.showTestResult(resultsDiv, 'error',
                `❌ API connection failed: ${error.message}`);
        } finally {
            this.setButtonLoading(button, false);
        }
    }

    async exportSettings() {
        try {
            const exportData = {
                version: '1.0.0',
                timestamp: new Date().toISOString(),
                settings: this.settings
            };

            const blob = new Blob([JSON.stringify(exportData, null, 2)],
                { type: 'application/json' });

            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `eq12-settings-${new Date().toISOString().split('T')[0]}.json`;
            a.click();

            URL.revokeObjectURL(url);
            this.showSuccess('Settings exported successfully');
        } catch (error) {
            console.error('Export settings error:', error);
            this.showError('Failed to export settings');
        }
    }

    async importSettings() {
        try {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.json';

            input.onchange = async (e) => {
                const file = e.target.files[0];
                if (!file) return;

                try {
                    const text = await file.text();
                    const importData = JSON.parse(text);

                    if (!importData.settings) {
                        throw new Error('Invalid settings file format');
                    }

                    // Validate imported settings
                    const validation = this.validateSettings(importData.settings);
                    if (!validation.valid) {
                        throw new Error('Invalid settings: ' + validation.error);
                    }

                    this.settings = { ...this.defaultSettings, ...importData.settings };
                    this.populateForm();

                    this.showSuccess('Settings imported successfully');
                } catch (error) {
                    console.error('Import settings error:', error);
                    this.showError('Failed to import settings: ' + error.message);
                }
            };

            input.click();
        } catch (error) {
            console.error('Import settings error:', error);
            this.showError('Failed to import settings');
        }
    }

    setupFormValidation() {
        // Real-time validation for various fields
        const telegramToken = document.getElementById('telegram-token');
        if (telegramToken) {
            telegramToken.addEventListener('input', (e) => {
                const isValid = !e.target.value || e.target.value.match(/^\d+:[A-Za-z0-9_-]+$/);
                e.target.style.borderColor = isValid ? '#e0e6ed' : '#ff4757';
            });
        }

        const telegramChatId = document.getElementById('telegram-chat-id');
        if (telegramChatId) {
            telegramChatId.addEventListener('input', (e) => {
                const isValid = !e.target.value || e.target.value.match(/^-?\d+$/);
                e.target.style.borderColor = isValid ? '#e0e6ed' : '#ff4757';
            });
        }

        const apiUrl = document.getElementById('api-base-url');
        if (apiUrl) {
            apiUrl.addEventListener('input', (e) => {
                const isValid = !e.target.value || this.isValidUrl(e.target.value);
                e.target.style.borderColor = isValid ? '#e0e6ed' : '#ff4757';
            });
        }

        // Add range validation for numeric inputs
        const numericInputs = ['vpn-check-interval', 'scrape-interval', 'min-ev', 'max-log-entries'];
        numericInputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('input', (e) => {
                    const value = parseFloat(e.target.value);
                    const min = parseFloat(e.target.min);
                    const max = parseFloat(e.target.max);

                    const isValid = !isNaN(value) && value >= min && value <= max;
                    e.target.style.borderColor = isValid ? '#e0e6ed' : '#ff4757';
                });
            }
        });
    }

    // Utility Methods
    isSportsbookTab(url) {
        if (!url) return false;
        const sportsbookDomains = ['draftkings.com', 'fanduel.com', 'betmgm.com'];
        return sportsbookDomains.some(domain => url.includes(domain));
    }

    isValidUrl(string) {
        try {
            new URL(string);
            return true;
        } catch {
            return false;
        }
    }

    setButtonLoading(button, loading) {
        if (!button) return;

        button.disabled = loading;

        if (loading) {
            button.dataset.originalText = button.textContent;
            button.textContent = 'Testing...';
            button.style.opacity = '0.6';
        } else {
            button.textContent = button.dataset.originalText || button.textContent;
            button.style.opacity = '1';
        }
    }

    showTestResult(container, type, message) {
        if (!container) return;

        container.innerHTML = `
            <div class="test-results test-${type}">
                ${message.split('\n').join('<br>')}
            </div>
        `;
    }

    showMessage(type, message) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div style="
                position: fixed;
                top: 20px;
                right: 20px;
                background: ${type === 'success' ? '#00ff88' : '#ff4757'};
                color: white;
                padding: 16px 24px;
                border-radius: 8px;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
                z-index: 10000;
                font-weight: 500;
            ">
                ${message}
            </div>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    showSuccess(message) {
        this.showMessage('success', message);
    }

    showError(message) {
        this.showMessage('error', message);
    }
}

// Initialize options controller when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new EQ12OptionsController();
});
