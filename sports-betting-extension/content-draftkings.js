// DraftKings Content Script - Sports Betting Assistant
// Handles bet slip injection and odds monitoring on DraftKings

(async () => {
    console.log("🎯 DraftKings Content Script Loaded");

    class DraftKingsAssistant {
        constructor() {
            this.init();
        }

        async init() {
            // Wait for page to be fully loaded
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.setup());
            } else {
                this.setup();
            }
        }

        async setup() {
            console.log("🚀 Setting up DraftKings integration...");

            // Add assistant UI overlay
            this.createAssistantOverlay();

            // Monitor for bet slip changes
            this.monitorBetSlip();

            // Listen for messages from background script
            browser.runtime.onMessage.addListener((request, sender, sendResponse) => {
                this.handleMessage(request, sender, sendResponse);
            });

            // Scan current page for odds
            this.scanCurrentOdds();
        }

        createAssistantOverlay() {
            const overlay = document.createElement('div');
            overlay.id = 'betting-assistant-overlay';
            overlay.innerHTML = `
        <div style="
          position: fixed;
          top: 10px;
          right: 10px;
          width: 300px;
          background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
          border: 1px solid #475569;
          border-radius: 12px;
          padding: 16px;
          box-shadow: 0 10px 25px rgba(0,0,0,0.3);
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          font-size: 14px;
          color: #f1f5f9;
          z-index: 10000;
          display: none;
        ">
          <div style="display: flex; align-items: center; margin-bottom: 12px;">
            <span style="font-size: 18px; margin-right: 8px;">🎯</span>
            <strong>Betting Assistant</strong>
            <button id="assistant-close" style="
              margin-left: auto;
              background: none;
              border: none;
              color: #94a3b8;
              cursor: pointer;
              font-size: 16px;
            ">×</button>
          </div>
          <div id="assistant-content">
            <div id="parlay-info" style="margin-bottom: 12px;">
              <div style="color: #94a3b8; font-size: 12px; margin-bottom: 4px;">Latest Parlay</div>
              <div id="parlay-details">No parlay loaded</div>
            </div>
            <button id="apply-parlay" style="
              width: 100%;
              background: linear-gradient(135deg, #10b981 0%, #059669 100%);
              color: white;
              border: none;
              border-radius: 6px;
              padding: 8px 12px;
              font-weight: 500;
              cursor: pointer;
              margin-bottom: 8px;
            ">Apply to Bet Slip</button>
            <button id="request-new" style="
              width: 100%;
              background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
              color: white;
              border: none;
              border-radius: 6px;
              padding: 8px 12px;
              font-weight: 500;
              cursor: pointer;
            ">Request New Parlay</button>
          </div>
        </div>
      `;

            document.body.appendChild(overlay);

            // Event listeners
            document.getElementById('assistant-close').onclick = () => {
                overlay.style.display = 'none';
            };

            document.getElementById('apply-parlay').onclick = () => {
                this.applyCurrentParlay();
            };

            document.getElementById('request-new').onclick = () => {
                this.requestNewParlay();
            };

            // Show overlay when extension icon is clicked
            browser.runtime.onMessage.addListener((request) => {
                if (request.action === 'showOverlay') {
                    overlay.style.display = 'block';
                    this.updateParlayDisplay();
                }
            });

            // Keyboard shortcut to toggle overlay
            document.addEventListener('keydown', (e) => {
                if (e.ctrlKey && e.shiftKey && e.key === 'B') {
                    overlay.style.display = overlay.style.display === 'none' ? 'block' : 'none';
                    if (overlay.style.display === 'block') {
                        this.updateParlayDisplay();
                    }
                }
            });
        }

        async updateParlayDisplay() {
            try {
                const response = await browser.runtime.sendMessage({ action: 'getParlayData' });
                const parlay = response.parlay;

                const parlayDetails = document.getElementById('parlay-details');

                if (!parlay) {
                    parlayDetails.innerHTML = '<div style="color: #94a3b8;">No parlay available</div>';
                    return;
                }

                parlayDetails.innerHTML = `
          <div style="margin-bottom: 8px;">
            <strong>${parlay.sport.toUpperCase()}</strong> - ${parlay.promo_type}
          </div>
          <div style="font-size: 12px; color: #94a3b8; margin-bottom: 4px;">
            ${parlay.legs.length} legs | EV: ${parlay.ev} | Stake: $${parlay.stake}
          </div>
          <div style="max-height: 100px; overflow-y: auto;">
            ${parlay.legs.map(leg => `
              <div style="font-size: 11px; margin-bottom: 2px; padding: 2px 4px; background: rgba(255,255,255,0.05); border-radius: 3px;">
                ${leg.label} (${leg.odds})
              </div>
            `).join('')}
          </div>
        `;
            } catch (error) {
                console.error("❌ Failed to update parlay display:", error);
            }
        }

        async applyCurrentParlay() {
            try {
                const response = await browser.runtime.sendMessage({ action: 'getParlayData' });
                const parlay = response.parlay;

                if (!parlay) {
                    alert('No parlay available to apply');
                    return;
                }

                console.log("🎯 Applying parlay to DraftKings bet slip...");

                // Clear existing bet slip
                const clearButton = document.querySelector('[data-testid="clear-all-button"], .clear-all-button, [class*="clear"], button[class*="Clear"]');
                if (clearButton) {
                    clearButton.click();
                    await this.sleep(1000);
                }

                // Add each leg with improved selectors
                for (let i = 0; i < parlay.legs.length; i++) {
                    const leg = parlay.legs[i];
                    await this.addBetSlipLeg(leg, i);
                    await this.sleep(800); // Wait between clicks
                }

                // Set stake
                await this.sleep(2000);
                await this.setStake(parlay.stake);

                console.log("✅ Parlay applied successfully!");

            } catch (error) {
                console.error("❌ Error applying parlay:", error);
                alert('Error applying parlay. Check console for details.');
            }
        }

        async addBetSlipLeg(leg, index) {
            // Multiple selector strategies for DraftKings
            const selectors = [
                `[data-outcome-label*="${leg.label}"]`,
                `[data-sb-id*="${leg.market}"]`,
                `button[aria-label*="${leg.label}"]`,
                `[class*="outcome"][class*="button"]:has-text("${leg.label}")`,
                `.sportsbook-outcome-cell:contains("${leg.label}")`,
                `button:contains("${leg.odds}")`
            ];

            for (const selector of selectors) {
                try {
                    const element = document.querySelector(selector);
                    if (element && element.offsetParent !== null) { // Check if visible
                        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        await this.sleep(300);
                        element.click();
                        console.log(`✅ Added leg ${index + 1}: ${leg.label} (${selector})`);
                        return;
                    }
                } catch (e) {
                    // Continue to next selector
                }
            }

            console.warn(`❌ Could not find leg: ${leg.label}`);
        }

        async setStake(amount) {
            const stakeSelectors = [
                'input[data-testid="betslip-stake-input"]',
                'input[placeholder*="stake"]',
                'input[placeholder*="Stake"]',
                '.betslip-stake input',
                'input[class*="stake"]'
            ];

            for (const selector of stakeSelectors) {
                const input = document.querySelector(selector);
                if (input) {
                    input.focus();
                    input.select();
                    input.value = amount;
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                    console.log(`💰 Set stake: $${amount}`);
                    return;
                }
            }

            console.warn("❌ Could not find stake input");
        }

        async requestNewParlay() {
            // Get current sport from URL or page context
            const sport = this.getCurrentSport();

            try {
                await browser.runtime.sendMessage({
                    action: 'requestNewParlay',
                    sport: sport,
                    promo: 'mystery', // Default to mystery boost
                    stake: 100
                });

                alert(`Requested new ${sport} parlay. Check back in a moment.`);
            } catch (error) {
                console.error("❌ Error requesting new parlay:", error);
            }
        }

        getCurrentSport() {
            const url = window.location.href;
            const path = window.location.pathname;

            // Extract sport from URL
            if (url.includes('/nfl') || path.includes('/nfl')) return 'nfl';
            if (url.includes('/cfb') || path.includes('/college-football')) return 'cfb';
            if (url.includes('/nba') || path.includes('/nba')) return 'nba';
            if (url.includes('/nhl') || path.includes('/nhl')) return 'nhl';
            if (url.includes('/mlb') || path.includes('/mlb')) return 'mlb';
            if (url.includes('/soccer') || path.includes('/soccer')) return 'soccer';
            if (url.includes('/ufc') || path.includes('/mma')) return 'ufc';
            if (url.includes('/tennis') || path.includes('/tennis')) return 'tennis';

            return 'nfl'; // Default
        }

        monitorBetSlip() {
            // Watch for bet slip changes
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.target.classList && mutation.target.classList.contains('betslip')) {
                        console.log("👀 Bet slip changed");
                        // Could send updates back to Python backend
                    }
                });
            });

            const betslip = document.querySelector('.betslip, [class*="betslip"], [data-testid*="betslip"]');
            if (betslip) {
                observer.observe(betslip, { childList: true, subtree: true });
            }
        }

        async scanCurrentOdds() {
            // Scan page for current odds and send to backend
            const odds = [];

            document.querySelectorAll('[data-outcome-label], .sportsbook-outcome').forEach(el => {
                const label = el.getAttribute('data-outcome-label') || el.textContent.trim();
                const oddsText = el.querySelector('.odds, [class*="odds"]')?.textContent;

                if (label && oddsText) {
                    odds.push({ label, odds: oddsText });
                }
            });

            if (odds.length > 0) {
                // Send to background script
                browser.runtime.sendMessage({
                    action: 'updateOdds',
                    odds: odds,
                    url: window.location.href
                });
            }
        }

        handleMessage(request, sender, sendResponse) {
            switch (request.action) {
                case 'showOverlay':
                    document.getElementById('betting-assistant-overlay').style.display = 'block';
                    this.updateParlayDisplay();
                    break;
                case 'applyParlay':
                    this.applyCurrentParlay();
                    break;
            }
        }

        sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }
    }

    // Initialize DraftKings assistant
    new DraftKingsAssistant();
})();
