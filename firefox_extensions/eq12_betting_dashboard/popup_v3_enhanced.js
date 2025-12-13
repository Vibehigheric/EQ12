// EQ12 Popup Controller - Enhanced with MDN Best Practices
// Implements modern extension UI patterns and advanced messaging

class EQ12PopupController {
    constructor() {
        this.sessionStartTime = Date.now();
        this.backgroundPort = null;
        this.updateInterval = null;
        this.currentTab = null;
        this.cache = new Map();

        this.init();
    }

    async init() {
        console.log('🎯 EQ12 Popup initializing...');

        try {
            // Setup communication with background script
            await this.setupCommunication();

            // Initialize UI components
            await this.initializeUI();

            // Load initial data
            await this.loadInitialData();

            // Start periodic updates
            this.startPeriodicUpdates();

            console.log('✅ EQ12 Popup ready');
        } catch (error) {
            console.error('Popup initialization error:', error);
            this.showError('Failed to initialize dashboard: ' + error.message);
        }
    }

    async setupCommunication() {
        // Establish persistent connection with background script
        try {
            this.backgroundPort = chrome.runtime.connect({ name: 'popup-dashboard' });

            this.backgroundPort.onMessage.addListener((message) => {
                this.handleBackgroundMessage(message);
            });

            this.backgroundPort.onDisconnect.addListener(() => {
                console.warn('Background connection lost');
                this.showError('Connection lost. Please reopen the dashboard.');
            });

            // Send initial registration
            this.backgroundPort.postMessage({
                action: 'register',
                data: { type: 'popup', timestamp: Date.now() }
            });

        } catch (error) {
            console.error('Failed to establish background communication:', error);
            // Fallback to runtime messaging
            chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
                this.handleRuntimeMessage(message, sender, sendResponse);
            });
        }

        // Get current active tab info
        try {
            const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
            this.currentTab = tabs[0];
        } catch (error) {
            console.warn('Could not get current tab:', error);
        }
    }

    async handleBackgroundMessage(message) {
        switch (message.action) {
            case 'vpnStatusUpdate':
                this.updateVPNStatus(message.data);
                break;
            case 'parlayUpdate':
                this.updateParlays(message.data);
                break;
            case 'statsUpdate':
                this.updateStats(message.data);
                break;
            case 'telegramStatus':
                this.updateTelegramStatus(message.data);
                break;
            case 'notification':
                this.showNotification(message.data);
                break;
        }
    }

    async initializeUI() {
        // Setup all event listeners with enhanced error handling
        this.setupEventListeners();

        // Initialize component states
        this.initializeComponents();

        // Setup keyboard shortcuts
        this.setupKeyboardShortcuts();

        // Initialize session timer
        this.initializeSessionTimer();
    }

    setupEventListeners() {
        // VPN Controls
        document.getElementById('check-vpn')?.addEventListener('click', () => {
            this.handleVPNCheck();
        });

        // Odds Scanning
        document.getElementById('scan-odds')?.addEventListener('click', () => {
            this.handleOddsScan();
        });

        // Dashboard Controls
        document.getElementById('open-dashboard')?.addEventListener('click', () => {
            this.openExternalDashboard();
        });

        document.getElementById('refresh-parlays')?.addEventListener('click', () => {
            this.refreshParlays();
        });

        // Emergency Controls
        document.getElementById('emergency-stop')?.addEventListener('click', () => {
            this.handleEmergencyStop();
        });

        // Telegram Controls
        document.getElementById('send-telegram')?.addEventListener('click', () => {
            this.sendTelegramMessage();
        });

        document.getElementById('test-telegram')?.addEventListener('click', () => {
            this.testTelegramBot();
        });

        const telegramInput = document.getElementById('telegram-message');
        if (telegramInput) {
            telegramInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendTelegramMessage();
                }
            });
        }

        // Footer Links
        document.getElementById('open-options')?.addEventListener('click', () => {
            this.openOptionsPage();
        });

        document.getElementById('view-logs')?.addEventListener('click', () => {
            this.openLogsViewer();
        });

        document.getElementById('help')?.addEventListener('click', () => {
            this.openHelpPage();
        });

        // Add click handlers for parlay items
        document.addEventListener('click', (e) => {
            if (e.target.closest('.parlay-item')) {
                this.handleParlayClick(e.target.closest('.parlay-item'));
            }
        });
    }

    initializeComponents() {
        // Set initial states
        this.updateSessionTime();
        this.showLoadingState('Connecting to EQ12 services...');

        // Initialize form validation
        this.setupFormValidation();
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + R: Refresh data
            if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
                e.preventDefault();
                this.refreshAllData();
            }

            // Ctrl/Cmd + D: Open dashboard
            if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
                e.preventDefault();
                this.openExternalDashboard();
            }

            // Escape: Emergency stop
            if (e.key === 'Escape') {
                this.handleEmergencyStop();
            }
        });
    }

    initializeSessionTimer() {
        setInterval(() => {
            this.updateSessionTime();
        }, 1000);
    }

    updateSessionTime() {
        const elapsed = Date.now() - this.sessionStartTime;
        const minutes = Math.floor(elapsed / 60000);
        const seconds = Math.floor((elapsed % 60000) / 1000);
        const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

        const sessionElement = document.getElementById('session-time');
        if (sessionElement) {
            sessionElement.textContent = timeString;
        }
    }

    async loadInitialData() {
        try {
            // Load VPN status
            await this.loadVPNStatus();

            // Load parlays
            await this.loadParlays();

            // Load statistics
            await this.loadStats();

            // Check Telegram status
            await this.checkTelegramStatus();

            this.hideLoadingState();
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.showError('Failed to load dashboard data');
            this.hideLoadingState();
        }
    }

    async loadVPNStatus() {
        try {
            const response = await this.sendBackgroundMessage({ action: 'getVpnStatus' });
            if (response.success) {
                this.updateVPNStatus(response.data);
            } else {
                throw new Error(response.error);
            }
        } catch (error) {
            console.error('VPN status load error:', error);
            this.updateVPNStatus({ connected: false, error: error.message });
        }
    }

    updateVPNStatus(status) {
        const statusElement = document.getElementById('vpn-status');
        const iconElement = statusElement?.querySelector('.status-icon');
        const titleElement = statusElement?.querySelector('.status-title');
        const subtitleElement = document.getElementById('vpn-subtitle');
        const detailsElement = document.getElementById('vpn-details');
        const lastCheckElement = document.getElementById('vpn-last-check');
        const ipElement = document.getElementById('vpn-ip');

        if (!statusElement) return;

        // Update visual state
        statusElement.classList.toggle('connected', status.connected);
        statusElement.classList.toggle('disconnected', !status.connected);

        // Update content
        if (iconElement) {
            iconElement.textContent = status.connected ? '🔒' : '🚨';
        }

        if (titleElement) {
            titleElement.textContent = status.connected ? 'VPN Connected' : 'VPN Disconnected';
        }

        if (subtitleElement) {
            subtitleElement.textContent = status.connected
                ? 'Secure connection active'
                : 'Connection required for betting';
        }

        if (lastCheckElement && status.lastCheck) {
            const lastCheck = new Date(status.lastCheck);
            lastCheckElement.textContent = lastCheck.toLocaleTimeString();
        }

        if (ipElement) {
            ipElement.textContent = status.ip || 'Unknown';
        }

        // Update button states based on VPN status
        this.updateButtonStates(status.connected);
    }

    updateButtonStates(vpnConnected) {
        const scanButton = document.getElementById('scan-odds');
        const emergencyButton = document.getElementById('emergency-stop');

        if (scanButton) {
            scanButton.disabled = !vpnConnected;
            scanButton.title = vpnConnected ? 'Scan sportsbooks for opportunities' : 'VPN required for scanning';
        }

        if (emergencyButton) {
            emergencyButton.disabled = !vpnConnected;
        }
    }

    async loadParlays() {
        try {
            const response = await this.sendBackgroundMessage({ action: 'getParlays' });
            if (response.success) {
                this.updateParlays(response.data);
            }
        } catch (error) {
            console.error('Parlays load error:', error);
            this.updateParlays([]);
        }
    }

    updateParlays(parlays) {
        const container = document.getElementById('parlay-content');
        if (!container) return;

        if (!parlays || parlays.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 20px; color: #666; font-style: italic;">
                    No active parlays found.<br>
                    <small>Scan odds to generate new opportunities</small>
                </div>
            `;
            return;
        }

        container.innerHTML = parlays.map(parlay => `
            <div class="parlay-item ${parlay.featured ? 'featured' : ''}" data-parlay-id="${parlay.id}">
                <div class="parlay-meta">
                    <span>${parlay.sport} • ${parlay.game}</span>
                    <span class="parlay-ev">+${parlay.expectedValue.toFixed(1)}% EV</span>
                </div>
                <div style="font-size: 13px; margin-bottom: 4px;">${parlay.description}</div>
                <div class="parlay-meta">
                    <span class="parlay-odds">${this.formatOdds(parlay.odds)}</span>
                    <span style="font-size: 11px; color: #666;">Confidence: ${parlay.confidence}</span>
                </div>
            </div>
        `).join('');

        // Update stats
        document.getElementById('active-parlays').textContent = parlays.length;
    }

    async loadStats() {
        try {
            const response = await this.sendBackgroundMessage({ action: 'getStats' });
            if (response.success) {
                this.updateStats(response.data);
            }
        } catch (error) {
            console.error('Stats load error:', error);
        }
    }

    updateStats(stats) {
        if (!stats) return;

        const elements = {
            'active-parlays': stats.activeParlays || 0,
            'opportunities': stats.opportunities || 0,
            'success-rate': `${stats.successRate || 0}%`
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    async checkTelegramStatus() {
        try {
            const response = await this.sendBackgroundMessage({ action: 'checkTelegramStatus' });
            if (response.success) {
                this.updateTelegramStatus(response.data);
            }
        } catch (error) {
            console.error('Telegram status check error:', error);
            this.updateTelegramStatus({ connected: false, error: error.message });
        }
    }

    updateTelegramStatus(status) {
        const statusIndicator = document.getElementById('telegram-status');
        if (statusIndicator) {
            statusIndicator.textContent = status.connected ? '●' : '○';
            statusIndicator.style.color = status.connected ? '#00ff88' : '#ff4757';
            statusIndicator.title = status.connected ? 'Bot connected' : 'Bot disconnected';
        }

        const sendButton = document.getElementById('send-telegram');
        if (sendButton) {
            sendButton.disabled = !status.connected;
        }
    }

    startPeriodicUpdates() {
        // Update every 30 seconds
        this.updateInterval = setInterval(() => {
            this.refreshCriticalData();
        }, 30000);
    }

    async refreshCriticalData() {
        try {
            await Promise.all([
                this.loadVPNStatus(),
                this.loadStats()
            ]);
        } catch (error) {
            console.error('Periodic update error:', error);
        }
    }

    async refreshAllData() {
        this.showLoadingState('Refreshing all data...');

        try {
            await Promise.all([
                this.loadVPNStatus(),
                this.loadParlays(),
                this.loadStats(),
                this.checkTelegramStatus()
            ]);

            this.showSuccess('Data refreshed successfully');
        } catch (error) {
            console.error('Data refresh error:', error);
            this.showError('Failed to refresh data');
        } finally {
            this.hideLoadingState();
        }
    }

    // Event Handlers
    async handleVPNCheck() {
        const button = document.getElementById('check-vpn');
        this.setButtonLoading(button, true);

        try {
            const response = await this.sendBackgroundMessage({ action: 'checkVpnStatus' });
            if (response.success) {
                this.updateVPNStatus(response.data);
                this.showSuccess('VPN status updated');
            } else {
                throw new Error(response.error);
            }
        } catch (error) {
            console.error('VPN check error:', error);
            this.showError('VPN check failed: ' + error.message);
        } finally {
            this.setButtonLoading(button, false);
        }
    }

    async handleOddsScan() {
        if (!this.currentTab || !this.isSportsbookTab(this.currentTab.url)) {
            this.showError('Please navigate to a supported sportsbook first');
            return;
        }

        const button = document.getElementById('scan-odds');
        this.setButtonLoading(button, true);

        try {
            // Inject content script and scan odds
            const response = await chrome.tabs.sendMessage(this.currentTab.id, {
                action: 'getSportsbookData'
            });

            if (response.success) {
                this.showSuccess(`Found ${response.data.totalOdds} odds opportunities`);

                // Request analysis from background
                await this.sendBackgroundMessage({
                    action: 'analyzeOdds',
                    data: response.data
                });

                // Refresh parlays to show new opportunities
                await this.loadParlays();
            } else {
                throw new Error(response.error);
            }
        } catch (error) {
            console.error('Odds scan error:', error);
            this.showError('Odds scan failed: ' + error.message);
        } finally {
            this.setButtonLoading(button, false);
        }
    }

    async handleEmergencyStop() {
        if (!confirm('This will stop all betting operations. Continue?')) {
            return;
        }

        const button = document.getElementById('emergency-stop');
        this.setButtonLoading(button, true);

        try {
            const response = await this.sendBackgroundMessage({ action: 'emergencyStop' });
            if (response.success) {
                this.showSuccess('Emergency stop activated');

                // Send Telegram notification
                await this.sendBackgroundMessage({
                    action: 'sendTelegram',
                    data: { message: '🚨 Emergency stop activated from dashboard' }
                });
            } else {
                throw new Error(response.error);
            }
        } catch (error) {
            console.error('Emergency stop error:', error);
            this.showError('Emergency stop failed: ' + error.message);
        } finally {
            this.setButtonLoading(button, false);
        }
    }

    async sendTelegramMessage() {
        const input = document.getElementById('telegram-message');
        const button = document.getElementById('send-telegram');

        if (!input || !input.value.trim()) {
            this.showError('Please enter a message');
            return;
        }

        this.setButtonLoading(button, true);

        try {
            const response = await this.sendBackgroundMessage({
                action: 'sendTelegram',
                data: { message: input.value.trim() }
            });

            if (response.success) {
                this.showSuccess('Message sent');
                input.value = '';
            } else {
                throw new Error(response.error);
            }
        } catch (error) {
            console.error('Telegram send error:', error);
            this.showError('Failed to send message: ' + error.message);
        } finally {
            this.setButtonLoading(button, false);
        }
    }

    async testTelegramBot() {
        const button = document.getElementById('test-telegram');
        this.setButtonLoading(button, true);

        try {
            const response = await this.sendBackgroundMessage({
                action: 'sendTelegram',
                data: { message: '🤖 EQ12 Dashboard test message - ' + new Date().toLocaleTimeString() }
            });

            if (response.success) {
                this.showSuccess('Test message sent');
            } else {
                throw new Error(response.error);
            }
        } catch (error) {
            console.error('Telegram test error:', error);
            this.showError('Bot test failed: ' + error.message);
        } finally {
            this.setButtonLoading(button, false);
        }
    }

    async refreshParlays() {
        const button = document.getElementById('refresh-parlays');
        this.setButtonLoading(button, true);

        try {
            await this.loadParlays();
            this.showSuccess('Parlays refreshed');
        } catch (error) {
            console.error('Parlay refresh error:', error);
            this.showError('Failed to refresh parlays');
        } finally {
            this.setButtonLoading(button, false);
        }
    }

    async openExternalDashboard() {
        try {
            await chrome.tabs.create({ url: 'http://localhost:8000/dashboard' });
            window.close();
        } catch (error) {
            console.error('Dashboard open error:', error);
            this.showError('Failed to open dashboard');
        }
    }

    async openOptionsPage() {
        try {
            await chrome.runtime.openOptionsPage();
        } catch (error) {
            console.error('Options page error:', error);
            // Fallback
            await chrome.tabs.create({ url: chrome.runtime.getURL('options.html') });
        }
    }

    async openLogsViewer() {
        try {
            await chrome.tabs.create({ url: 'http://localhost:8000/logs' });
        } catch (error) {
            console.error('Logs viewer error:', error);
            this.showError('Failed to open logs viewer');
        }
    }

    async openHelpPage() {
        try {
            await chrome.tabs.create({ url: 'https://github.com/your-repo/eq12-help' });
        } catch (error) {
            console.error('Help page error:', error);
            this.showError('Failed to open help page');
        }
    }

    handleParlayClick(parlayElement) {
        const parlayId = parlayElement.dataset.parlayId;
        if (!parlayId) return;

        // Show parlay details or copy to clipboard
        const parlayText = parlayElement.textContent.trim();
        navigator.clipboard.writeText(parlayText).then(() => {
            this.showSuccess('Parlay copied to clipboard');
        }).catch(error => {
            console.error('Clipboard error:', error);
            this.showError('Failed to copy parlay');
        });
    }

    // Utility Methods
    async sendBackgroundMessage(message) {
        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error('Message timeout'));
            }, 10000);

            if (this.backgroundPort) {
                // Use port messaging
                const messageId = Date.now() + Math.random();
                message.id = messageId;

                const responseHandler = (response) => {
                    if (response.id === messageId) {
                        clearTimeout(timeout);
                        this.backgroundPort.onMessage.removeListener(responseHandler);
                        resolve(response);
                    }
                };

                this.backgroundPort.onMessage.addListener(responseHandler);
                this.backgroundPort.postMessage(message);
            } else {
                // Fallback to runtime messaging
                chrome.runtime.sendMessage(message, (response) => {
                    clearTimeout(timeout);
                    if (chrome.runtime.lastError) {
                        reject(new Error(chrome.runtime.lastError.message));
                    } else {
                        resolve(response || { success: false, error: 'No response' });
                    }
                });
            }
        });
    }

    isSportsbookTab(url) {
        if (!url) return false;
        const sportsbookDomains = ['draftkings.com', 'fanduel.com', 'betmgm.com'];
        return sportsbookDomains.some(domain => url.includes(domain));
    }

    formatOdds(odds) {
        if (typeof odds === 'number') {
            return odds > 0 ? `+${odds}` : odds.toString();
        }
        return odds;
    }

    setButtonLoading(button, loading) {
        if (!button) return;

        button.disabled = loading;
        button.classList.toggle('loading', loading);

        if (loading) {
            button.dataset.originalText = button.textContent;
            button.textContent = 'Loading...';
        } else {
            button.textContent = button.dataset.originalText || button.textContent;
        }
    }

    showLoadingState(message = 'Loading...') {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.remove('hidden');
        }
    }

    hideLoadingState() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.add('hidden');
        }
    }

    showNotification(notification) {
        // This would integrate with the browser notification system
        console.log('Notification:', notification);
    }

    showMessage(type, message) {
        const container = document.getElementById('message-container');
        if (!container) return;

        const messageElement = document.createElement('div');
        messageElement.className = `message ${type}`;
        messageElement.textContent = message;

        container.appendChild(messageElement);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            messageElement.remove();
        }, 5000);
    }

    showSuccess(message) {
        this.showMessage('success', message);
    }

    showError(message) {
        this.showMessage('error', message);
    }

    setupFormValidation() {
        const telegramInput = document.getElementById('telegram-message');
        if (telegramInput) {
            telegramInput.addEventListener('input', (e) => {
                const maxLength = 200;
                const remaining = maxLength - e.target.value.length;

                if (remaining < 20) {
                    e.target.style.borderColor = remaining < 0 ? '#ff4757' : '#f39c12';
                } else {
                    e.target.style.borderColor = '#e0e6ed';
                }
            });
        }
    }

    // Cleanup on popup close
    cleanup() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }

        if (this.backgroundPort) {
            this.backgroundPort.disconnect();
        }
    }
}

// Initialize popup when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const controller = new EQ12PopupController();

    // Cleanup on window unload
    window.addEventListener('beforeunload', () => {
        controller.cleanup();
    });
});
