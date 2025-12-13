// EQ12 Sportsbook Scraper - Content Script
// Runs on sportsbook sites to extract odds and highlight EV opportunities

class EQ12SportsbookScraper {
    constructor() {
        this.siteName = this.detectSite();
        this.odds = [];
        this.evOpportunities = [];
        this.init();
    }

    init() {
        console.log(`EQ12 Scraper active on ${this.siteName}`);

        // Only run on supported sites
        if (!this.siteName) {
            return;
        }

        // Set up observers and scrapers
        this.setupObservers();
        this.startScraping();

        // Add EQ12 overlay interface
        this.createOverlay();

        // Periodic scraping
        setInterval(() => this.performScrape(), 30000); // Every 30 seconds
    }

    detectSite() {
        const hostname = window.location.hostname.toLowerCase();

        if (hostname.includes('draftkings')) return 'draftkings';
        if (hostname.includes('fanduel')) return 'fanduel';
        if (hostname.includes('betmgm')) return 'betmgm';
        if (hostname.includes('caesars')) return 'caesars';
        if (hostname.includes('pointsbet')) return 'pointsbet';

        return null;
    }

    setupObservers() {
        // Watch for dynamic content changes
        const observer = new MutationObserver((mutations) => {
            let shouldScrape = false;

            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    // Check if odds-related elements were added
                    const hasOddsContent = Array.from(mutation.addedNodes).some(node =>
                        node.nodeType === 1 && (
                            node.textContent?.includes('+') ||
                            node.textContent?.includes('-') ||
                            node.className?.toLowerCase().includes('odd') ||
                            node.className?.toLowerCase().includes('bet')
                        )
                    );

                    if (hasOddsContent) {
                        shouldScrape = true;
                    }
                }
            });

            if (shouldScrape) {
                // Debounce scraping to avoid excessive calls
                clearTimeout(this.scrapeTimeout);
                this.scrapeTimeout = setTimeout(() => this.performScrape(), 2000);
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    startScraping() {
        // Initial scrape after page load
        setTimeout(() => this.performScrape(), 3000);
    }

    performScrape() {
        try {
            const scraped = this.scrapeOdds();

            if (scraped.length > 0) {
                this.odds = scraped;
                this.analyzeEV();
                this.updateOverlay();
                this.sendToEQ12(scraped);
            }

        } catch (error) {
            console.error('Scraping error:', error);
        }
    }

    scrapeOdds() {
        switch (this.siteName) {
            case 'draftkings':
                return this.scrapeDraftKings();
            case 'fanduel':
                return this.scrapeFanDuel();
            case 'betmgm':
                return this.scrapeBetMGM();
            default:
                return this.scrapeGeneric();
        }
    }

    scrapeDraftKings() {
        const odds = [];

        try {
            // DraftKings specific selectors
            const gameElements = document.querySelectorAll('[data-testid="event-cell"], .event-card, .sportsbook-event-accordion__wrapper');

            gameElements.forEach((element, index) => {
                try {
                    const teams = element.querySelectorAll('.event-cell__name, .sportsbook-row-name, [data-testid="team-name"]');
                    const oddsElements = element.querySelectorAll('.sportsbook-odds, [data-testid="american-odds"], .odds-value');

                    if (teams.length >= 2 && oddsElements.length >= 2) {
                        const game = {
                            site: 'draftkings',
                            gameId: `dk_${index}`,
                            teams: Array.from(teams).map(t => t.textContent.trim()),
                            odds: Array.from(oddsElements).map(o => this.parseOdds(o.textContent.trim())),
                            timestamp: Date.now(),
                            url: window.location.href
                        };

                        odds.push(game);
                    }
                } catch (error) {
                    console.error('Error parsing DK game:', error);
                }
            });

        } catch (error) {
            console.error('DraftKings scraping error:', error);
        }

        return odds;
    }

    scrapeFanDuel() {
        const odds = [];

        try {
            // FanDuel specific selectors
            const gameElements = document.querySelectorAll('[aria-label*="game"], .market-grid, .bet-grid-container');

            gameElements.forEach((element, index) => {
                try {
                    const teams = element.querySelectorAll('[aria-label*="team"], .team-name, [data-test-id="team-name"]');
                    const oddsElements = element.querySelectorAll('[aria-label*="odd"], .bet-price, [data-test-id="odds"]');

                    if (teams.length >= 2 && oddsElements.length >= 2) {
                        const game = {
                            site: 'fanduel',
                            gameId: `fd_${index}`,
                            teams: Array.from(teams).map(t => t.textContent.trim()),
                            odds: Array.from(oddsElements).map(o => this.parseOdds(o.textContent.trim())),
                            timestamp: Date.now(),
                            url: window.location.href
                        };

                        odds.push(game);
                    }
                } catch (error) {
                    console.error('Error parsing FD game:', error);
                }
            });

        } catch (error) {
            console.error('FanDuel scraping error:', error);
        }

        return odds;
    }

    scrapeBetMGM() {
        const odds = [];

        try {
            // BetMGM specific selectors
            const gameElements = document.querySelectorAll('.fixture, .game-lines, .option-group');

            gameElements.forEach((element, index) => {
                try {
                    const teams = element.querySelectorAll('.participant-name, .team-name, .selection-name');
                    const oddsElements = element.querySelectorAll('.option, .selection-price, .odds-button');

                    if (teams.length >= 2 && oddsElements.length >= 2) {
                        const game = {
                            site: 'betmgm',
                            gameId: `mgm_${index}`,
                            teams: Array.from(teams).map(t => t.textContent.trim()),
                            odds: Array.from(oddsElements).map(o => this.parseOdds(o.textContent.trim())),
                            timestamp: Date.now(),
                            url: window.location.href
                        };

                        odds.push(game);
                    }
                } catch (error) {
                    console.error('Error parsing MGM game:', error);
                }
            });

        } catch (error) {
            console.error('BetMGM scraping error:', error);
        }

        return odds;
    }

    scrapeGeneric() {
        // Generic scraper for unknown sites
        const odds = [];

        try {
            // Look for common odds patterns
            const potentialOdds = document.querySelectorAll('*');
            const oddsPattern = /^[+-]\d{3,4}$/;

            Array.from(potentialOdds).forEach(element => {
                const text = element.textContent?.trim();
                if (text && oddsPattern.test(text)) {
                    // Found potential odds element
                    const parent = element.closest('[class*="game"], [class*="match"], [class*="event"]');
                    if (parent && !parent.dataset.eq12Scraped) {
                        parent.dataset.eq12Scraped = 'true';

                        // Try to extract game info
                        const teamElements = parent.querySelectorAll('[class*="team"], [class*="player"]');
                        const oddsElements = parent.querySelectorAll('[class*="odd"], [class*="price"]');

                        if (teamElements.length >= 2 && oddsElements.length >= 2) {
                            odds.push({
                                site: 'unknown',
                                gameId: `generic_${odds.length}`,
                                teams: Array.from(teamElements).map(t => t.textContent.trim()),
                                odds: Array.from(oddsElements).map(o => this.parseOdds(o.textContent.trim())),
                                timestamp: Date.now(),
                                url: window.location.href
                            });
                        }
                    }
                }
            });

        } catch (error) {
            console.error('Generic scraping error:', error);
        }

        return odds;
    }

    parseOdds(oddsText) {
        try {
            // Remove any non-numeric characters except +/-
            const cleaned = oddsText.replace(/[^\d+-]/g, '');
            const odds = parseInt(cleaned);

            return isNaN(odds) ? 0 : odds;
        } catch (error) {
            return 0;
        }
    }

    analyzeEV() {
        // Simple EV analysis (you can enhance this with your EQ12 models)
        this.evOpportunities = this.odds.filter(game => {
            // Basic EV calculation - you can integrate your sophisticated models here
            const avgOdds = game.odds.reduce((sum, odd) => sum + Math.abs(odd), 0) / game.odds.length;

            // Look for potential value (this is simplified)
            return avgOdds > 200 && game.odds.some(odd => odd > 0);
        });

        // Highlight EV opportunities on page
        this.highlightOpportunities();
    }

    highlightOpportunities() {
        // Remove previous highlights
        document.querySelectorAll('.eq12-ev-highlight').forEach(el => {
            el.classList.remove('eq12-ev-highlight');
        });

        // Add EQ12 highlighting styles if not already added
        if (!document.getElementById('eq12-scraper-styles')) {
            const style = document.createElement('style');
            style.id = 'eq12-scraper-styles';
            style.textContent = `
                .eq12-ev-highlight {
                    border: 2px solid #00ff88 !important;
                    background-color: rgba(0, 255, 136, 0.1) !important;
                    box-shadow: 0 0 10px rgba(0, 255, 136, 0.3) !important;
                }
                .eq12-ev-badge {
                    position: absolute;
                    top: -8px;
                    right: -8px;
                    background: #00ff88;
                    color: #000;
                    padding: 2px 6px;
                    border-radius: 10px;
                    font-size: 10px;
                    font-weight: bold;
                    z-index: 9999;
                }
            `;
            document.head.appendChild(style);
        }

        // Highlight EV opportunities (simplified - you can enhance this)
        this.evOpportunities.forEach(opportunity => {
            // Find elements on page that match this opportunity
            const gameElements = document.querySelectorAll('[class*="game"], [class*="event"], [class*="match"]');

            gameElements.forEach(element => {
                const text = element.textContent.toLowerCase();
                const hasMatchingTeams = opportunity.teams.some(team =>
                    text.includes(team.toLowerCase())
                );

                if (hasMatchingTeams) {
                    element.classList.add('eq12-ev-highlight');

                    // Add EV badge
                    const badge = document.createElement('div');
                    badge.className = 'eq12-ev-badge';
                    badge.textContent = 'EQ12 +EV';
                    element.style.position = 'relative';
                    element.appendChild(badge);
                }
            });
        });
    }

    createOverlay() {
        // Create EQ12 overlay interface
        const overlay = document.createElement('div');
        overlay.id = 'eq12-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            width: 200px;
            background: rgba(26, 26, 46, 0.95);
            border: 1px solid #00d4ff;
            border-radius: 8px;
            padding: 10px;
            color: white;
            font-family: Arial, sans-serif;
            font-size: 12px;
            z-index: 10000;
            display: none;
        `;

        overlay.innerHTML = `
            <div style="font-weight: bold; margin-bottom: 8px; color: #00d4ff;">
                🎯 EQ12 Scraper
            </div>
            <div id="eq12-stats">
                Games: <span id="eq12-game-count">0</span><br>
                +EV: <span id="eq12-ev-count">0</span><br>
                Last: <span id="eq12-last-update">--:--</span>
            </div>
            <button id="eq12-toggle" style="
                margin-top: 8px;
                padding: 4px 8px;
                background: #00d4ff;
                border: none;
                border-radius: 4px;
                color: #1a1a2e;
                font-size: 10px;
                cursor: pointer;
            ">Hide</button>
        `;

        document.body.appendChild(overlay);

        // Show overlay by default
        setTimeout(() => {
            overlay.style.display = 'block';
        }, 2000);

        // Toggle functionality
        document.getElementById('eq12-toggle').addEventListener('click', () => {
            const isVisible = overlay.style.display !== 'none';
            overlay.style.display = isVisible ? 'none' : 'block';
            document.getElementById('eq12-toggle').textContent = isVisible ? 'Show' : 'Hide';
        });
    }

    updateOverlay() {
        const gameCount = document.getElementById('eq12-game-count');
        const evCount = document.getElementById('eq12-ev-count');
        const lastUpdate = document.getElementById('eq12-last-update');

        if (gameCount) gameCount.textContent = this.odds.length;
        if (evCount) evCount.textContent = this.evOpportunities.length;
        if (lastUpdate) lastUpdate.textContent = new Date().toLocaleTimeString();
    }

    async sendToEQ12(odds) {
        try {
            // Send scraped odds to EQ12 backend
            const message = {
                action: 'logBettingOperation',
                data: {
                    operation: 'odds_scrape',
                    success: true,
                    details: {
                        site: this.siteName,
                        games_found: odds.length,
                        ev_opportunities: this.evOpportunities.length,
                        url: window.location.href
                    }
                }
            };

            browser.runtime.sendMessage(message);

            // Also try direct API call if available
            try {
                const response = await fetch('http://localhost:8000/scraper/odds', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        site: this.siteName,
                        odds: odds,
                        ev_opportunities: this.evOpportunities,
                        timestamp: Date.now()
                    })
                });

                if (response.ok) {
                    console.log('Odds sent to EQ12 API successfully');
                }
            } catch (error) {
                console.log('EQ12 API not available:', error);
            }

        } catch (error) {
            console.error('Error sending to EQ12:', error);
        }
    }
}

// Initialize scraper when page is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new EQ12SportsbookScraper());
} else {
    new EQ12SportsbookScraper();
}
