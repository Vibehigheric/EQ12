// FanDuel Content Script - Sports Betting Assistant
// Similar to DraftKings but adapted for FanDuel's interface

(async () => {
    console.log("🎯 FanDuel Content Script Loaded");

    class FanDuelAssistant {
        constructor() {
            this.init();
        }

        async init() {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.setup());
            } else {
                this.setup();
            }
        }

        async setup() {
            console.log("🚀 Setting up FanDuel integration...");

            // FanDuel-specific setup
            this.createAssistantOverlay();
            this.monitorBetSlip();

            browser.runtime.onMessage.addListener((request, sender, sendResponse) => {
                this.handleMessage(request, sender, sendResponse);
            });

            this.scanCurrentOdds();
        }

        createAssistantOverlay() {
            // Same overlay as DraftKings but with FanDuel-specific styling
            const overlay = document.createElement('div');
            overlay.id = 'betting-assistant-overlay-fd';
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
            <strong>Betting Assistant (FD)</strong>
            <button id="assistant-close-fd" style="
              margin-left: auto;
              background: none;
              border: none;
              color: #94a3b8;
              cursor: pointer;
              font-size: 16px;
            ">×</button>
          </div>
          <div id="assistant-content-fd">
            <div style="color: #94a3b8; font-size: 12px; margin-bottom: 8px;">
              FanDuel integration coming soon. Use DraftKings for now.
            </div>
          </div>
        </div>
      `;

            document.body.appendChild(overlay);

            document.getElementById('assistant-close-fd').onclick = () => {
                overlay.style.display = 'none';
            };
        }

        async applyCurrentParlay() {
            // FanDuel-specific bet slip implementation
            console.log("🚧 FanDuel bet slip integration coming soon");
            alert("FanDuel integration is in development. Please use DraftKings for now.");
        }

        getCurrentSport() {
            const url = window.location.href;
            const path = window.location.pathname;

            // FanDuel URL patterns
            if (url.includes('/nfl') || path.includes('/nfl')) return 'nfl';
            if (url.includes('/college-football') || path.includes('/cfb')) return 'cfb';
            if (url.includes('/nba') || path.includes('/nba')) return 'nba';
            if (url.includes('/nhl') || path.includes('/nhl')) return 'nhl';
            if (url.includes('/mlb') || path.includes('/mlb')) return 'mlb';
            if (url.includes('/soccer') || path.includes('/soccer')) return 'soccer';

            return 'nfl';
        }

        monitorBetSlip() {
            // FanDuel bet slip monitoring
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.target.classList &&
                        (mutation.target.classList.contains('betslip') ||
                            mutation.target.classList.contains('bet-slip'))) {
                        console.log("👀 FanDuel bet slip changed");
                    }
                });
            });

            const betslip = document.querySelector('.betslip, .bet-slip, [data-testid*="betslip"]');
            if (betslip) {
                observer.observe(betslip, { childList: true, subtree: true });
            }
        }

        async scanCurrentOdds() {
            // FanDuel odds scanning
            const odds = [];

            document.querySelectorAll('[data-test-id*="odds"], .odds-button, [class*="odds"]').forEach(el => {
                const label = el.textContent.trim();
                const oddsMatch = label.match(/[+-]\d+/);

                if (oddsMatch) {
                    odds.push({ label: label, odds: oddsMatch[0] });
                }
            });

            if (odds.length > 0) {
                browser.runtime.sendMessage({
                    action: 'updateOdds',
                    odds: odds,
                    url: window.location.href,
                    sportsbook: 'fanduel'
                });
            }
        }

        handleMessage(request, sender, sendResponse) {
            switch (request.action) {
                case 'showOverlay':
                    document.getElementById('betting-assistant-overlay-fd').style.display = 'block';
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

    // Initialize FanDuel assistant
    new FanDuelAssistant();
})();
