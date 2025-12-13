// Sports Betting Assistant - Popup Script
// Handles the extension popup interface and communication with background script

class BettingAssistantPopup {
    constructor() {
        this.currentParlay = null;
        this.init();
    }

    async init() {
        console.log("🚀 Initializing Betting Assistant Popup...");

        // Load initial data
        await this.loadData();

        // Set up event listeners
        this.setupEventListeners();

        // Check connection status
        this.updateConnectionStatus();

        // Update display
        this.updateParlayDisplay();
    }

    async loadData() {
        try {
            // Get current parlay from storage
            const response = await browser.runtime.sendMessage({ action: 'getParlayData' });
            this.currentParlay = response.parlay;

            // Load user settings
            const settings = await browser.storage.local.get([
                'preferredSport',
                'preferredPromo',
                'defaultStake',
                'maxLegs'
            ]);

            // Apply saved settings to form
            if (settings.preferredSport) {
                document.getElementById('sportSelect').value = settings.preferredSport;
            }
            if (settings.preferredPromo) {
                document.getElementById('promoSelect').value = settings.preferredPromo;
            }
            if (settings.defaultStake) {
                document.getElementById('stakeInput').value = settings.defaultStake;
            }
            if (settings.maxLegs) {
                document.getElementById('maxLegsInput').value = settings.maxLegs;
            }

        } catch (error) {
            console.error("❌ Error loading data:", error);
        }
    }

    setupEventListeners() {
        // Apply Parlay Button
        document.getElementById('applyParlayBtn').onclick = async () => {
            await this.applyParlay();
        };

        // Request New Parlay Button
        document.getElementById('requestParlayBtn').onclick = async () => {
            await this.requestNewParlay();
        };

        // Settings Toggle
        document.getElementById('showSettingsBtn').onclick = () => {
            this.toggleSettings();
        };

        // Save Settings Button
        document.getElementById('saveSettingsBtn').onclick = async () => {
            await this.saveSettingsAndRequest();
        };

        // Listen for storage changes (real-time updates)
        browser.storage.onChanged.addListener((changes) => {
            if (changes.latestParlay) {
                this.currentParlay = changes.latestParlay.newValue;
                this.updateParlayDisplay();
            }
        });
    }

    async updateConnectionStatus() {
        try {
            const { pythonStatus } = await browser.storage.local.get('pythonStatus');
            const indicator = document.getElementById('connectionStatus');

            if (pythonStatus === 'connected') {
                indicator.classList.add('connected');
                indicator.title = 'Connected to Python backend';
            } else {
                indicator.classList.remove('connected');
                indicator.title = 'Disconnected from Python backend';
            }
        } catch (error) {
            console.error("❌ Error checking connection status:", error);
        }
    }

    updateParlayDisplay() {
        const container = document.getElementById('parlayContainer');
        const applyBtn = document.getElementById('applyParlayBtn');

        if (!this.currentParlay) {
            container.innerHTML = `
        <div class="no-parlay">
          No parlay available. Request a new one below.
        </div>
      `;
            applyBtn.style.display = 'none';
            return;
        }

        const parlay = this.currentParlay;

        container.innerHTML = `
      <div class="parlay-card">
        <div class="parlay-header">
          <div class="sport-badge">${parlay.sport.toUpperCase()}</div>
          <div class="ev-badge">EV: ${parlay.ev}</div>
        </div>

        <div class="parlay-meta">
          <span><strong>${parlay.legs.length}</strong> legs</span>
          <span><strong>$${parlay.stake}</strong> stake</span>
          <span><strong>${parlay.promo_type}</strong></span>
        </div>

        <div class="legs-container">
          ${parlay.legs.map(leg => `
            <div class="leg">
              <span class="leg-label">${leg.label}</span>
              <span class="leg-odds">${leg.odds}</span>
            </div>
          `).join('')}
        </div>

        ${parlay.boost_percentage ? `
          <div style="margin-top: 12px; padding: 8px; background: rgba(16, 185, 129, 0.1); border-radius: 6px; font-size: 12px; color: #10b981;">
            🚀 Boost: +${parlay.boost_percentage}% | Potential Win: $${parlay.potential_payout}
          </div>
        ` : ''}
      </div>
    `;

        applyBtn.style.display = 'block';

        // Show stats section if we have parlay data
        document.getElementById('statsSection').style.display = 'block';
        this.updateStats();
    }

    async applyParlay() {
        if (!this.currentParlay) {
            alert('No parlay to apply');
            return;
        }

        try {
            // Get current active tab
            const [tab] = await browser.tabs.query({ active: true, currentWindow: true });

            if (!tab.url.includes('draftkings.com')) {
                const shouldRedirect = confirm('This will open DraftKings. Continue?');
                if (shouldRedirect) {
                    await browser.tabs.create({ url: 'https://sportsbook.draftkings.com' });
                }
                return;
            }

            // Send message to content script
            await browser.tabs.sendMessage(tab.id, {
                action: 'applyParlay',
                parlay: this.currentParlay
            });

            // Show success message
            this.showNotification('Parlay applied to bet slip!', 'success');

            // Close popup after applying
            window.close();

        } catch (error) {
            console.error("❌ Error applying parlay:", error);
            this.showNotification('Error applying parlay. Make sure you\'re on DraftKings.', 'error');
        }
    }

    async requestNewParlay() {
        const sport = document.getElementById('sportSelect').value;
        const promo = document.getElementById('promoSelect').value;
        const stake = parseInt(document.getElementById('stakeInput').value);
        const maxLegs = parseInt(document.getElementById('maxLegsInput').value);

        try {
            // Show loading state
            this.showLoading('Requesting new parlay...');

            const response = await browser.runtime.sendMessage({
                action: 'requestNewParlay',
                sport,
                promo,
                stake,
                maxLegs
            });

            if (response.status === 'requested') {
                this.showNotification(`${sport.toUpperCase()} parlay requested. Check back in a moment.`, 'success');

                // Auto-refresh after 5 seconds
                setTimeout(() => {
                    this.loadData();
                }, 5000);
            }

        } catch (error) {
            console.error("❌ Error requesting parlay:", error);
            this.showNotification('Error requesting parlay. Check Python backend connection.', 'error');
        }
    }

    toggleSettings() {
        const form = document.getElementById('settingsForm');
        const parlaySection = document.getElementById('parlaySection');
        const btn = document.getElementById('showSettingsBtn');

        if (form.classList.contains('active')) {
            form.classList.remove('active');
            parlaySection.style.display = 'block';
            btn.textContent = 'Settings';
        } else {
            form.classList.add('active');
            parlaySection.style.display = 'none';
            btn.textContent = 'Back';
        }
    }

    async saveSettingsAndRequest() {
        const sport = document.getElementById('sportSelect').value;
        const promo = document.getElementById('promoSelect').value;
        const stake = parseInt(document.getElementById('stakeInput').value);
        const maxLegs = parseInt(document.getElementById('maxLegsInput').value);

        // Save settings
        await browser.storage.local.set({
            preferredSport: sport,
            preferredPromo: promo,
            defaultStake: stake,
            maxLegs: maxLegs
        });

        // Hide settings and request new parlay
        this.toggleSettings();
        await this.requestNewParlay();
    }

    updateStats() {
        // Mock stats for now - could be enhanced with real data
        document.getElementById('totalParlays').textContent = '3';
        document.getElementById('avgEV').textContent = '+12.5%';
    }

    showLoading(message) {
        const container = document.getElementById('parlayContainer');
        container.innerHTML = `
      <div class="loading">
        ${message}
      </div>
    `;
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.style.cssText = `
      position: fixed;
      top: 10px;
      left: 50%;
      transform: translateX(-50%);
      background: ${type === 'error' ? '#ef4444' : '#10b981'};
      color: white;
      padding: 12px 20px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 500;
      z-index: 1000;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      animation: slideDown 0.3s ease;
    `;

        notification.textContent = message;
        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideUp 0.3s ease forwards';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translate(-50%, -20px);
    }
    to {
      opacity: 1;
      transform: translate(-50%, 0);
    }
  }

  @keyframes slideUp {
    from {
      opacity: 1;
      transform: translate(-50%, 0);
    }
    to {
      opacity: 0;
      transform: translate(-50%, -20px);
    }
  }
`;
document.head.appendChild(style);

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new BettingAssistantPopup();
});

// Handle keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // ESC to close popup
    if (e.key === 'Escape') {
        window.close();
    }

    // Enter to apply parlay (if available)
    if (e.key === 'Enter' && e.ctrlKey) {
        const applyBtn = document.getElementById('applyParlayBtn');
        if (applyBtn.style.display !== 'none') {
            applyBtn.click();
        }
    }
});
