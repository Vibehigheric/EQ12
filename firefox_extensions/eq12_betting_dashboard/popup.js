// EQ12 Betting Dashboard - Popup Script
// Handles UI interactions and EQ12 API communication

class EQ12Dashboard {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000'; // EQ12 FastAPI server
        this.telegramBotToken = null;
        this.telegramChatId = null;
        this.init();
    }

    async init() {
        await this.loadSettings();
        this.setupEventListeners();
        await this.refreshStatus();

        // Auto-refresh every 30 seconds
        setInterval(() => this.refreshStatus(), 30000);
    }

    async loadSettings() {
        const settings = await browser.storage.local.get([
            'eq12_api_url',
            'telegram_bot_token',
            'telegram_chat_id',
            'vpn_check_enabled'
        ]);

        this.apiBaseUrl = settings.eq12_api_url || 'http://localhost:8000';
        this.telegramBotToken = settings.telegram_bot_token;
        this.telegramChatId = settings.telegram_chat_id;
    }

    setupEventListeners() {
        document.getElementById('refresh-status').addEventListener('click', () => this.refreshStatus());
        document.getElementById('toggle-vpn').addEventListener('click', () => this.toggleVPN());
        document.getElementById('fetch-parlays').addEventListener('click', () => this.fetchParlays());
        document.getElementById('run-audit').addEventListener('click', () => this.runAudit());
        document.getElementById('telegram-bot').addEventListener('click', () => this.openTelegramBot());
        document.getElementById('odds-scraper').addEventListener('click', () => this.runOddsScraper());
        document.getElementById('settings').addEventListener('click', () => this.openSettings());
    }

    async refreshStatus() {
        try {
            // Check VPN status
            await this.checkVPNStatus();

            // Check EQ12 API status
            await this.checkAPIStatus();

            this.showNotification('Status updated', 'success');
        } catch (error) {
            console.error('Error refreshing status:', error);
            this.showNotification('Status update failed', 'error');
        }
    }

    async checkVPNStatus() {
        try {
            // Get current IP
            const ipResponse = await fetch('https://api.ipify.org?format=json');
            const ipData = await ipResponse.json();
            const currentIP = ipData.ip;

            document.getElementById('current-ip').textContent = currentIP;

            // Check if IP is from VPN (basic check - you might want to enhance this)
            const vpnStatus = await this.isVPNActive(currentIP);

            const statusElement = document.getElementById('vpn-status');
            const regionElement = document.getElementById('vpn-region');

            if (vpnStatus.active) {
                statusElement.textContent = 'Connected';
                statusElement.className = 'status-value status-connected';
                regionElement.textContent = vpnStatus.region || 'Unknown';
            } else {
                statusElement.textContent = 'Disconnected';
                statusElement.className = 'status-value status-disconnected';
                regionElement.textContent = 'Local';
            }

        } catch (error) {
            console.error('Error checking VPN status:', error);
            document.getElementById('vpn-status').textContent = 'Error';
            document.getElementById('vpn-status').className = 'status-value status-warning';
        }
    }

    async isVPNActive(ip) {
        try {
            // Call EQ12 VPN Guard status API
            const response = await fetch(`${this.apiBaseUrl}/vpn/status`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.ok) {
                const data = await response.json();
                return {
                    active: data.vpn_active || false,
                    region: data.region || 'eq12-betting'
                };
            }
        } catch (error) {
            console.log('EQ12 VPN API not available, using fallback detection');
        }

        // Fallback: basic IP-based detection
        // You can enhance this with your specific VPN IP ranges
        return {
            active: !this.isLocalIP(ip),
            region: 'Unknown'
        };
    }

    isLocalIP(ip) {
        // Check if IP is from local network ranges
        const localRanges = [
            /^192\.168\./,
            /^10\./,
            /^172\.(1[6-9]|2\d|3[01])\./,
            /^127\./
        ];

        return localRanges.some(range => range.test(ip));
    }

    async checkAPIStatus() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`, {
                method: 'GET',
                timeout: 5000
            });

            const statusElement = document.getElementById('api-status');

            if (response.ok) {
                statusElement.textContent = 'Connected';
                statusElement.className = 'status-value status-connected';
            } else {
                statusElement.textContent = 'Error';
                statusElement.className = 'status-value status-warning';
            }
        } catch (error) {
            document.getElementById('api-status').textContent = 'Offline';
            document.getElementById('api-status').className = 'status-value status-disconnected';
        }
    }

    async toggleVPN() {
        try {
            this.showNotification('Toggling VPN...', 'info');

            // Call EQ12 VPN control API
            const response = await fetch(`${this.apiBaseUrl}/vpn/toggle`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.ok) {
                const result = await response.json();
                this.showNotification(`VPN ${result.status}`, 'success');

                // Refresh status after toggle
                setTimeout(() => this.refreshStatus(), 3000);
            } else {
                throw new Error('VPN toggle failed');
            }
        } catch (error) {
            console.error('Error toggling VPN:', error);
            this.showNotification('VPN toggle failed - check EQ12 VPN Guard', 'error');
        }
    }

    async fetchParlays() {
        try {
            this.showNotification('Fetching parlays...', 'info');

            const response = await fetch(`${this.apiBaseUrl}/parlay/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    legs: 5,
                    max_odds: 1000,
                    min_ev: 0.05
                })
            });

            if (response.ok) {
                const parlays = await response.json();
                this.displayParlays(parlays);
                this.showNotification(`Generated ${parlays.length} parlays`, 'success');
            } else {
                throw new Error('Parlay generation failed');
            }
        } catch (error) {
            console.error('Error fetching parlays:', error);
            this.showNotification('Parlay fetch failed - check EQ12 API', 'error');
        }
    }

    displayParlays(parlays) {
        const container = document.getElementById('parlay-container');
        container.innerHTML = '';

        if (!parlays || parlays.length === 0) {
            container.innerHTML = '<div class="parlay-section"><div class="parlay-title">No parlays available</div></div>';
            return;
        }

        parlays.slice(0, 3).forEach((parlay, index) => {
            const parlayDiv = document.createElement('div');
            parlayDiv.className = 'parlay-section';

            const ev = parlay.expected_value || 0;
            const evClass = ev > 0 ? 'ev-positive' : 'ev-negative';

            parlayDiv.innerHTML = `
                <div class="parlay-title">Parlay ${index + 1} (EV: ${(ev * 100).toFixed(1)}%)</div>
                ${parlay.legs.map(leg => `
                    <div class="parlay-item ${evClass}">
                        ${leg.team} ${leg.bet_type} ${leg.odds > 0 ? '+' : ''}${leg.odds}
                    </div>
                `).join('')}
                <div style="font-size: 10px; color: #888; margin-top: 5px;">
                    Stake: $${parlay.stake} | Potential: $${parlay.potential_payout}
                </div>
            `;

            container.appendChild(parlayDiv);
        });
    }

    async runAudit() {
        try {
            this.showNotification('Running audit...', 'info');

            const response = await fetch(`${this.apiBaseUrl}/audit/run`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.ok) {
                const auditResult = await response.json();

                // Send to Telegram if configured
                if (this.telegramBotToken && this.telegramChatId) {
                    await this.sendTelegramMessage(`📊 EQ12 Audit Complete:\n\nPNL: $${auditResult.pnl}\nBets: ${auditResult.total_bets}\nWin Rate: ${auditResult.win_rate}%`);
                }

                this.showNotification('Audit completed successfully', 'success');
            } else {
                throw new Error('Audit failed');
            }
        } catch (error) {
            console.error('Error running audit:', error);
            this.showNotification('Audit failed - check EQ12 API', 'error');
        }
    }

    async sendTelegramMessage(message) {
        try {
            const response = await fetch(`https://api.telegram.org/bot${this.telegramBotToken}/sendMessage`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    chat_id: this.telegramChatId,
                    text: message,
                    parse_mode: 'HTML'
                })
            });

            return response.ok;
        } catch (error) {
            console.error('Error sending Telegram message:', error);
            return false;
        }
    }

    openTelegramBot() {
        if (this.telegramChatId) {
            window.open(`https://t.me/${this.telegramChatId}`, '_blank');
        } else {
            this.showNotification('Configure Telegram in settings', 'warning');
        }
    }

    async runOddsScraper() {
        try {
            this.showNotification('Running odds scraper...', 'info');

            const response = await fetch(`${this.apiBaseUrl}/scraper/odds`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (response.ok) {
                const result = await response.json();
                this.showNotification(`Scraped ${result.games_updated} games`, 'success');
            } else {
                throw new Error('Scraper failed');
            }
        } catch (error) {
            console.error('Error running scraper:', error);
            this.showNotification('Scraper failed - check EQ12 API', 'error');
        }
    }

    openSettings() {
        browser.runtime.openOptionsPage();
    }

    showNotification(message, type = 'info') {
        const notification = document.getElementById('notification');
        notification.textContent = message;
        notification.className = `notification show ${type}`;

        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    }
}

// Initialize dashboard when popup loads
document.addEventListener('DOMContentLoaded', () => {
    new EQ12Dashboard();
});
