/**
 * EQ12 Data Pusher - Popup JavaScript
 * Handles UI interactions and communication with background scripts
 */

class EQ12PopupManager {
    constructor() {
        this.apiEndpoints = {
            local: 'http://127.0.0.1:8000',
            ngrok: null // Will be detected
        };
        this.currentUrl = '';
        this.pageType = 'unknown';
        this.stats = { today: 0, success: 0, errors: 0 };

        this.init();
    }

    async init() {
        console.log('🧠 EQ12 Popup Manager initializing...');

        // Load current tab info
        await this.loadCurrentTab();

        // Check API status
        await this.checkApiStatus();

        // Load stats
        await this.loadStats();

        // Setup event listeners
        this.setupEventListeners();

        // Update UI
        this.updateUI();

        console.log('✅ EQ12 Popup Manager ready');
    }

    async loadCurrentTab() {
        try {
            const [tab] = await browser.tabs.query({ active: true, currentWindow: true });
            this.currentUrl = tab.url;
            this.pageType = this.detectPageType(tab.url);

            document.getElementById('current-url').textContent =
                this.currentUrl.length > 60 ? this.currentUrl.substring(0, 60) + '...' : this.currentUrl;
            document.getElementById('page-type').textContent = this.pageType;

        } catch (error) {
            console.error('Error loading current tab:', error);
        }
    }

    detectPageType(url) {
        const patterns = {
            'Sports Betting': [
                'draftkings', 'fanduel', 'mybookie', 'betrivers', 'bovada',
                'sportsbook', 'bet365', 'williamhill'
            ],
            'Travel Deals': [
                'expedia', 'booking', 'kayak', 'priceline', 'trivago',
                'hotels', 'airbnb', 'vrbo'
            ],
            'Tickets': [
                'stubhub', 'ticketmaster', 'seatgeek', 'vivid'
            ],
            'Finance': [
                'chase', 'americanexpress', 'discover', 'creditcards'
            ]
        };

        const urlLower = url.toLowerCase();

        for (const [type, keywords] of Object.entries(patterns)) {
            if (keywords.some(keyword => urlLower.includes(keyword))) {
                return type;
            }
        }

        return 'General';
    }

    async checkApiStatus() {
        const statusDot = document.getElementById('api-status');
        const statusText = document.getElementById('api-status-text');

        try {
            // Try local API first
            const response = await fetch(`${this.apiEndpoints.local}/api/ping`, {
                method: 'GET',
                timeout: 3000
            });

            if (response.ok) {
                const data = await response.json();
                statusDot.className = 'status-dot online';
                statusText.textContent = `API Online (${data.server || 'Local'})`;
                return true;
            }
        } catch (error) {
            console.log('Local API not available, checking for ngrok...');
        }

        // Try to detect ngrok endpoint from storage
        try {
            const stored = await browser.storage.local.get(['ngrok_url']);
            if (stored.ngrok_url) {
                const response = await fetch(`${stored.ngrok_url}/api/ping`, {
                    method: 'GET',
                    timeout: 3000
                });

                if (response.ok) {
                    this.apiEndpoints.ngrok = stored.ngrok_url;
                    statusDot.className = 'status-dot online';
                    statusText.textContent = 'API Online (Ngrok)';
                    return true;
                }
            }
        } catch (error) {
            console.log('Ngrok API not available');
        }

        // API not available
        statusDot.className = 'status-dot offline';
        statusText.textContent = 'API Offline';
        return false;
    }

    async loadStats() {
        try {
            const stored = await browser.storage.local.get(['eq12_stats']);
            if (stored.eq12_stats) {
                this.stats = stored.eq12_stats;
                document.getElementById('stat-today').textContent = this.stats.today || 0;
                document.getElementById('stat-success').textContent = this.stats.success || 0;
                document.getElementById('stat-errors').textContent = this.stats.errors || 0;
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    async saveStats() {
        try {
            await browser.storage.local.set({ eq12_stats: this.stats });
        } catch (error) {
            console.error('Error saving stats:', error);
        }
    }

    setupEventListeners() {
        // Capture buttons
        document.getElementById('capture-odds').addEventListener('click', () => {
            this.captureData('odds');
        });

        document.getElementById('capture-deals').addEventListener('click', () => {
            this.captureData('deals');
        });

        document.getElementById('capture-selection').addEventListener('click', () => {
            this.captureData('selection');
        });

        document.getElementById('capture-page').addEventListener('click', () => {
            this.captureData('page');
        });

        document.getElementById('ai-analyze').addEventListener('click', () => {
            this.aiAnalyze();
        });

        // Advanced actions
        document.getElementById('affiliate-inject').addEventListener('click', () => {
            this.injectAffiliate();
        });

        document.getElementById('open-dashboard').addEventListener('click', () => {
            this.openDashboard();
        });

        document.getElementById('vpn-rotate').addEventListener('click', () => {
            this.rotateVPN();
        });

        document.getElementById('test-api').addEventListener('click', () => {
            this.testAPI();
        });

        // Toggle switches
        document.getElementById('auto-capture-toggle').addEventListener('click', (e) => {
            this.toggleSetting(e.target, 'auto_capture');
        });

        document.getElementById('affiliate-toggle').addEventListener('click', (e) => {
            this.toggleSetting(e.target, 'affiliate_injection');
        });

        document.getElementById('ai-toggle').addEventListener('click', (e) => {
            this.toggleSetting(e.target, 'ai_analysis');
        });
    }

    async captureData(type) {
        this.showLoading(true);
        this.showAlert('info', `Capturing ${type} data...`);

        try {
            // Send message to content script
            const [tab] = await browser.tabs.query({ active: true, currentWindow: true });

            const response = await browser.tabs.sendMessage(tab.id, {
                action: 'captureData',
                type: type,
                url: this.currentUrl,
                pageType: this.pageType
            });

            if (response && response.success) {
                // Display captured data
                const preview = document.getElementById('data-preview');
                preview.textContent = JSON.stringify(response.data, null, 2);

                // Update stats
                this.stats.today++;
                this.stats.success++;
                await this.saveStats();

                this.showAlert('success', `Successfully captured ${type} data (${Object.keys(response.data).length} fields)`);

                // Auto-push to EQ12 if enabled
                const settings = await browser.storage.local.get(['auto_push']);
                if (settings.auto_push) {
                    await this.pushToEQ12(response.data, type);
                }

            } else {
                throw new Error(response?.error || 'Capture failed');
            }

        } catch (error) {
            console.error(`Error capturing ${type}:`, error);
            this.stats.errors++;
            await this.saveStats();
            this.showAlert('error', `Failed to capture ${type}: ${error.message}`);
        } finally {
            this.showLoading(false);
            await this.loadStats();
        }
    }

    async aiAnalyze() {
        this.showLoading(true);
        this.showAlert('info', 'Running AI analysis...');

        try {
            const [tab] = await browser.tabs.query({ active: true, currentWindow: true });

            // First capture current page data
            const captureResponse = await browser.tabs.sendMessage(tab.id, {
                action: 'captureData',
                type: 'intelligent',
                url: this.currentUrl,
                pageType: this.pageType
            });

            if (captureResponse && captureResponse.success) {
                // Send to AI analysis
                const aiResponse = await this.callEQ12API('/api/ai-analyze', {
                    data: captureResponse.data,
                    url: this.currentUrl,
                    pageType: this.pageType,
                    timestamp: new Date().toISOString()
                });

                if (aiResponse.success) {
                    // Display AI insights
                    const preview = document.getElementById('data-preview');
                    preview.innerHTML = `
<span style="color: #00d4ff;">🤖 AI Analysis:</span>
<span style="color: #00ff88;">Category:</span> ${aiResponse.analysis.category}
<span style="color: #00ff88;">Confidence:</span> ${aiResponse.analysis.confidence}%
<span style="color: #00ff88;">Key Data:</span> ${aiResponse.analysis.key_fields.join(', ')}
<span style="color: #00ff88;">Recommendation:</span> ${aiResponse.analysis.recommendation}

<span style="color: #ffaa00;">Raw Data:</span>
${JSON.stringify(captureResponse.data, null, 2)}
                    `;

                    this.stats.success++;
                    this.showAlert('success', `AI analysis complete: ${aiResponse.analysis.recommendation}`);

                    // Auto-push analyzed data
                    await this.pushToEQ12(aiResponse.structured_data, aiResponse.analysis.category);

                } else {
                    throw new Error(aiResponse.error || 'AI analysis failed');
                }
            } else {
                throw new Error('Failed to capture page data for analysis');
            }

        } catch (error) {
            console.error('AI analysis error:', error);
            this.stats.errors++;
            this.showAlert('error', `AI analysis failed: ${error.message}`);
        } finally {
            this.showLoading(false);
            await this.saveStats();
            await this.loadStats();
        }
    }

    async pushToEQ12(data, type) {
        try {
            const endpoint = this.getEQ12Endpoint(type);
            const response = await this.callEQ12API(endpoint, {
                source: 'firefox_extension',
                type: type,
                data: data,
                url: this.currentUrl,
                timestamp: new Date().toISOString(),
                user_agent: navigator.userAgent
            });

            if (response.success) {
                this.showAlert('success', `Data pushed to EQ12 ${type} pipeline`);
            } else {
                throw new Error(response.error || 'Push failed');
            }

        } catch (error) {
            console.error('Error pushing to EQ12:', error);
            throw error;
        }
    }

    getEQ12Endpoint(type) {
        const endpoints = {
            'odds': '/api/parlay/add-odds',
            'deals': '/api/deals/add',
            'finance': '/api/finance/add',
            'tickets': '/api/tickets/add',
            'selection': '/api/data/add',
            'page': '/api/data/add',
            'intelligent': '/api/ai/process'
        };

        return endpoints[type] || '/api/data/add';
    }

    async callEQ12API(endpoint, data) {
        const baseUrl = this.apiEndpoints.ngrok || this.apiEndpoints.local;

        const response = await fetch(`${baseUrl}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': 'eq12-firefox-extension'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`API call failed: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    }

    async injectAffiliate() {
        this.showLoading(true);
        this.showAlert('info', 'Injecting affiliate links...');

        try {
            const [tab] = await browser.tabs.query({ active: true, currentWindow: true });

            const response = await browser.tabs.sendMessage(tab.id, {
                action: 'injectAffiliate',
                url: this.currentUrl,
                pageType: this.pageType
            });

            if (response && response.success) {
                this.showAlert('success', `Injected ${response.count} affiliate links`);
            } else {
                throw new Error(response?.error || 'Affiliate injection failed');
            }

        } catch (error) {
            console.error('Affiliate injection error:', error);
            this.showAlert('error', `Affiliate injection failed: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }

    openDashboard() {
        const dashboardUrl = this.apiEndpoints.ngrok
            ? `${this.apiEndpoints.ngrok}/`
            : `${this.apiEndpoints.local}/`;

        browser.tabs.create({ url: dashboardUrl });
    }

    async rotateVPN() {
        this.showLoading(true);
        this.showAlert('info', 'Rotating VPN profile...');

        try {
            const response = await this.callEQ12API('/api/vpn/rotate', {
                current_site: this.currentUrl,
                page_type: this.pageType
            });

            if (response.success) {
                this.showAlert('success', `VPN rotated to: ${response.new_location}`);
            } else {
                throw new Error(response.error || 'VPN rotation failed');
            }

        } catch (error) {
            console.error('VPN rotation error:', error);
            this.showAlert('error', `VPN rotation failed: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }

    async testAPI() {
        this.showLoading(true);
        document.getElementById('footer-status').textContent = 'Testing API...';

        try {
            const isOnline = await this.checkApiStatus();

            if (isOnline) {
                // Test endpoints
                const tests = [
                    { name: 'Ping', endpoint: '/api/ping' },
                    { name: 'Health', endpoint: '/api/health' },
                    { name: 'Status', endpoint: '/api/status' }
                ];

                let results = [];

                for (const test of tests) {
                    try {
                        const baseUrl = this.apiEndpoints.ngrok || this.apiEndpoints.local;
                        const response = await fetch(`${baseUrl}${test.endpoint}`);
                        results.push(`✅ ${test.name}: OK`);
                    } catch {
                        results.push(`❌ ${test.name}: Failed`);
                    }
                }

                this.showAlert('success', `API Test Results:\n${results.join('\n')}`);

            } else {
                this.showAlert('error', 'API is offline - cannot run tests');
            }

        } catch (error) {
            console.error('API test error:', error);
            this.showAlert('error', `API test failed: ${error.message}`);
        } finally {
            this.showLoading(false);
            document.getElementById('footer-status').textContent = 'Ready';
        }
    }

    async toggleSetting(element, setting) {
        element.classList.toggle('active');
        const enabled = element.classList.contains('active');

        try {
            const settings = await browser.storage.local.get([setting]);
            settings[setting] = enabled;
            await browser.storage.local.set(settings);

            this.showAlert('info', `${setting.replace('_', ' ')} ${enabled ? 'enabled' : 'disabled'}`);

        } catch (error) {
            console.error('Error saving setting:', error);
        }
    }

    updateUI() {
        // Update page-specific elements
        const pageTypeElement = document.getElementById('page-type');
        pageTypeElement.textContent = this.pageType;

        // Update button states based on page type
        if (this.pageType === 'Sports Betting') {
            document.getElementById('capture-odds').style.background = 'linear-gradient(45deg, #ff6b35, #f7931e)';
        } else if (this.pageType === 'Travel Deals') {
            document.getElementById('capture-deals').style.background = 'linear-gradient(45deg, #4ecdc4, #44a08d)';
        }
    }

    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        overlay.style.display = show ? 'block' : 'none';
    }

    showAlert(type, message) {
        const alertElement = document.getElementById(`${type === 'error' ? 'error' : 'success'}-alert`);
        alertElement.textContent = message;
        alertElement.style.display = 'block';

        // Auto-hide after 5 seconds
        setTimeout(() => {
            alertElement.style.display = 'none';
        }, 5000);
    }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new EQ12PopupManager();
});
