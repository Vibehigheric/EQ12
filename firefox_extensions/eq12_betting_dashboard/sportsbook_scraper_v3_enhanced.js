// EQ12 Sportsbook Content Script - Enhanced with MDN Best Practices
// Implements modern content script patterns for odds scraping, EV highlighting, and secure communication

class EQ12SportsbookScraper {
    constructor() {
        this.siteConfig = null;
        this.observerActive = false;
        this.messagePort = null;
        this.lastScrapeData = null;

        this.init();
    }

    async init() {
        // Mark as injected to prevent duplicate injection
        window.EQ12_INJECTED = true;

        console.log('🎯 EQ12 Sportsbook Scraper initializing on:', window.location.hostname);

        // Detect sportsbook and load configuration
        this.siteConfig = await this.detectSportsbook();

        if (!this.siteConfig) {
            console.warn('Unsupported sportsbook site');
            return;
        }

        // Setup communication with background script
        await this.setupCommunication();

        // Start monitoring
        await this.startMonitoring();

        console.log('✅ EQ12 Sportsbook Scraper ready');
    }

    async detectSportsbook() {
        const hostname = window.location.hostname;
        const configs = {
            'sportsbook.draftkings.com': {
                name: 'DraftKings',
                selectors: {
                    oddsContainer: '[data-testid="event-cell"]',
                    odds: '[data-testid="outcome-cell"]',
                    gameTitle: '[data-testid="event-cell-game-title"]',
                    playerProps: '[data-testid="player-prop-card"]'
                },
                patterns: {
                    americanOdds: /^[+-]\d+$/,
                    decimalOdds: /^\d+\.\d+$/
                }
            },
            'sportsbook.fanduel.com': {
                name: 'FanDuel',
                selectors: {
                    oddsContainer: '[data-test-id="MarketGrid"]',
                    odds: '[role="button"][aria-label*="odds"]',
                    gameTitle: '[data-test-id="GameCardTitle"]',
                    playerProps: '[data-test-id="PlayerPropCard"]'
                },
                patterns: {
                    americanOdds: /^[+-]\d+$/,
                    decimalOdds: /^\d+\.\d+$/
                }
            },
            'sports.betmgm.com': {
                name: 'BetMGM',
                selectors: {
                    oddsContainer: '.option-group',
                    odds: '.option',
                    gameTitle: '.fixture-name',
                    playerProps: '.player-props'
                },
                patterns: {
                    americanOdds: /^[+-]\d+$/,
                    decimalOdds: /^\d+\.\d+$/
                }
            }
        };

        return configs[hostname] || null;
    }

    async setupCommunication() {
        // Establish long-lived connection for real-time updates
        try {
            this.messagePort = chrome.runtime.connect({ name: 'sportsbook-scraper' });

            this.messagePort.onMessage.addListener((message) => {
                this.handleBackgroundMessage(message);
            });

            this.messagePort.onDisconnect.addListener(() => {
                console.warn('Background connection lost, attempting reconnect...');
                setTimeout(() => this.setupCommunication(), 5000);
            });

            // Register with background script
            this.messagePort.postMessage({
                action: 'register',
                data: {
                    sportsbook: this.siteConfig.name,
                    url: window.location.href,
                    timestamp: Date.now()
                }
            });

        } catch (error) {
            console.error('Failed to establish background communication:', error);
        }

        // Fallback message listener for one-off communications
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            this.handleRuntimeMessage(message, sender, sendResponse);
            return true; // Keep channel open
        });
    }

    async handleBackgroundMessage(message) {
        switch (message.action) {
            case 'vpnStatusUpdate':
                await this.handleVpnStatusUpdate(message.data);
                break;
            case 'scrapeRequest':
                const data = await this.performScrape();
                this.messagePort.postMessage({
                    action: 'scrapeResponse',
                    data: data
                });
                break;
            case 'highlightOpportunities':
                await this.highlightEVOpportunities(message.data);
                break;
        }
    }

    async handleRuntimeMessage(message, sender, sendResponse) {
        try {
            let response = null;

            switch (message.action) {
                case 'getSportsbookData':
                    response = await this.performScrape();
                    break;
                case 'highlightBets':
                    await this.highlightEVOpportunities(message.data);
                    response = { success: true };
                    break;
                case 'captureOdds':
                    response = await this.captureCurrentOdds();
                    break;
                case 'injectEVIndicators':
                    await this.injectEVIndicators();
                    response = { success: true };
                    break;
            }

            sendResponse({ success: true, data: response });
        } catch (error) {
            sendResponse({ success: false, error: error.message });
        }
    }

    async handleVpnStatusUpdate(vpnStatus) {
        // Update visual indicators based on VPN status
        this.updateVpnStatusIndicator(vpnStatus);

        if (!vpnStatus.connected) {
            this.showVpnWarningOverlay();
        } else {
            this.hideVpnWarningOverlay();
        }
    }

    async startMonitoring() {
        // Start DOM observation for dynamic content
        this.setupDOMObserver();

        // Initial scrape
        await this.performInitialScrape();

        // Setup periodic monitoring
        setInterval(() => this.performPeriodicCheck(), 30000); // 30 seconds
    }

    setupDOMObserver() {
        if (this.observerActive) return;

        const observer = new MutationObserver((mutations) => {
            const hasRelevantChanges = mutations.some(mutation =>
                mutation.type === 'childList' &&
                mutation.addedNodes.length > 0 &&
                Array.from(mutation.addedNodes).some(node =>
                    node.nodeType === Node.ELEMENT_NODE &&
                    this.isOddsElement(node)
                )
            );

            if (hasRelevantChanges) {
                this.debounce(() => this.handleOddsUpdate(), 1000)();
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['data-odds', 'aria-label']
        });

        this.observerActive = true;
        console.log('DOM observer started');
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    isOddsElement(element) {
        if (!this.siteConfig) return false;

        return element.matches && (
            element.matches(this.siteConfig.selectors.odds) ||
            element.querySelector(this.siteConfig.selectors.odds)
        );
    }

    async handleOddsUpdate() {
        const currentData = await this.performScrape();

        if (this.hasSignificantChanges(currentData, this.lastScrapeData)) {
            this.lastScrapeData = currentData;

            // Notify background script of changes
            this.messagePort?.postMessage({
                action: 'oddsUpdate',
                data: currentData
            });

            // Auto-highlight new opportunities
            await this.autoHighlightOpportunities(currentData);
        }
    }

    hasSignificantChanges(current, previous) {
        if (!previous) return true;

        // Compare odds counts and values
        return current.games?.length !== previous.games?.length ||
            current.totalOdds !== previous.totalOdds;
    }

    async performInitialScrape() {
        console.log('Performing initial scrape...');

        // Wait for dynamic content to load
        await this.waitForOddsElements();

        const data = await this.performScrape();
        this.lastScrapeData = data;

        // Send initial data to background
        this.messagePort?.postMessage({
            action: 'initialScrape',
            data: data
        });
    }

    async waitForOddsElements(timeout = 10000) {
        const startTime = Date.now();

        while (Date.now() - startTime < timeout) {
            const elements = document.querySelectorAll(this.siteConfig.selectors.odds);
            if (elements.length > 0) {
                return elements;
            }
            await this.sleep(500);
        }

        throw new Error('Odds elements not found within timeout');
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async performScrape() {
        if (!this.siteConfig) {
            throw new Error('Sportsbook configuration not loaded');
        }

        const scrapeData = {
            sportsbook: this.siteConfig.name,
            url: window.location.href,
            timestamp: Date.now(),
            games: [],
            totalOdds: 0
        };

        try {
            // Scrape game containers
            const gameContainers = document.querySelectorAll(this.siteConfig.selectors.oddsContainer);

            for (const container of gameContainers) {
                const game = await this.scrapeGameContainer(container);
                if (game && game.odds.length > 0) {
                    scrapeData.games.push(game);
                    scrapeData.totalOdds += game.odds.length;
                }
            }

            // Scrape player props if available
            const playerPropElements = document.querySelectorAll(this.siteConfig.selectors.playerProps);
            if (playerPropElements.length > 0) {
                scrapeData.playerProps = await this.scrapePlayerProps(playerPropElements);
            }

            console.log(`Scraped ${scrapeData.totalOdds} odds from ${scrapeData.games.length} games`);
            return scrapeData;

        } catch (error) {
            console.error('Scraping error:', error);
            throw error;
        }
    }

    async scrapeGameContainer(container) {
        try {
            const titleElement = container.querySelector(this.siteConfig.selectors.gameTitle);
            const oddsElements = container.querySelectorAll(this.siteConfig.selectors.odds);

            if (!titleElement || oddsElements.length === 0) {
                return null;
            }

            const game = {
                title: this.cleanText(titleElement.textContent),
                odds: [],
                container: this.getElementSelector(container)
            };

            for (const oddsElement of oddsElements) {
                const odds = this.extractOdds(oddsElement);
                if (odds) {
                    game.odds.push(odds);
                }
            }

            return game;
        } catch (error) {
            console.warn('Error scraping game container:', error);
            return null;
        }
    }

    extractOdds(element) {
        const text = this.cleanText(element.textContent);
        const ariaLabel = element.getAttribute('aria-label') || '';

        // Try to extract American odds first
        let oddsValue = this.extractAmericanOdds(text) || this.extractAmericanOdds(ariaLabel);

        if (!oddsValue) {
            // Try decimal odds
            oddsValue = this.extractDecimalOdds(text) || this.extractDecimalOdds(ariaLabel);
        }

        if (!oddsValue) return null;

        return {
            value: oddsValue,
            text: text,
            type: this.classifyBet(text, ariaLabel),
            element: this.getElementSelector(element),
            impliedProbability: this.calculateImpliedProbability(oddsValue)
        };
    }

    extractAmericanOdds(text) {
        const match = text.match(/([+-]\d+)/);
        return match ? parseInt(match[1]) : null;
    }

    extractDecimalOdds(text) {
        const match = text.match(/(\d+\.\d+)/);
        return match ? parseFloat(match[1]) : null;
    }

    classifyBet(text, ariaLabel) {
        const combined = (text + ' ' + ariaLabel).toLowerCase();

        if (combined.includes('moneyline') || combined.includes('win')) return 'moneyline';
        if (combined.includes('spread') || combined.includes('point')) return 'spread';
        if (combined.includes('total') || combined.includes('over') || combined.includes('under')) return 'total';
        if (combined.includes('prop')) return 'prop';

        return 'unknown';
    }

    calculateImpliedProbability(odds) {
        if (typeof odds === 'number' && odds > 0) {
            // American odds
            if (odds > 0) {
                return 100 / (odds + 100);
            } else {
                return Math.abs(odds) / (Math.abs(odds) + 100);
            }
        } else if (typeof odds === 'number' && odds >= 1) {
            // Decimal odds
            return 1 / odds;
        }
        return null;
    }

    async scrapePlayerProps(elements) {
        const props = [];

        for (const element of elements) {
            try {
                const prop = {
                    player: this.extractPlayerName(element),
                    stat: this.extractStatType(element),
                    line: this.extractLine(element),
                    odds: this.extractOddsFromProp(element)
                };

                if (prop.player && prop.stat) {
                    props.push(prop);
                }
            } catch (error) {
                console.warn('Error scraping player prop:', error);
            }
        }

        return props;
    }

    extractPlayerName(element) {
        const playerSelectors = ['.player-name', '[data-player]', '.name'];
        for (const selector of playerSelectors) {
            const nameElement = element.querySelector(selector);
            if (nameElement) {
                return this.cleanText(nameElement.textContent);
            }
        }
        return null;
    }

    extractStatType(element) {
        const statSelectors = ['.stat-type', '[data-stat]', '.prop-type'];
        for (const selector of statSelectors) {
            const statElement = element.querySelector(selector);
            if (statElement) {
                return this.cleanText(statElement.textContent);
            }
        }
        return null;
    }

    extractLine(element) {
        const lineMatch = element.textContent.match(/(\d+\.?\d*)/);
        return lineMatch ? parseFloat(lineMatch[1]) : null;
    }

    extractOddsFromProp(element) {
        const oddsElements = element.querySelectorAll('[data-odds], .odds');
        return Array.from(oddsElements).map(el => this.extractOdds(el)).filter(Boolean);
    }

    async highlightEVOpportunities(opportunities) {
        if (!opportunities || opportunities.length === 0) return;

        for (const opportunity of opportunities) {
            await this.highlightOpportunity(opportunity);
        }
    }

    async highlightOpportunity(opportunity) {
        const selector = opportunity.selector || opportunity.element;
        if (!selector) return;

        const element = document.querySelector(selector);
        if (!element) {
            console.warn('Could not find element to highlight:', selector);
            return;
        }

        // Create EV indicator
        const indicator = this.createEVIndicator(opportunity);

        // Position indicator relative to odds element
        this.positionIndicator(indicator, element);

        // Add to DOM
        document.body.appendChild(indicator);

        // Add highlight styling to original element
        element.classList.add('eq12-ev-opportunity');
        element.style.cssText += `
            border: 2px solid #00ff88 !important;
            box-shadow: 0 0 10px rgba(0, 255, 136, 0.5) !important;
            background-color: rgba(0, 255, 136, 0.1) !important;
        `;
    }

    createEVIndicator(opportunity) {
        const indicator = document.createElement('div');
        indicator.className = 'eq12-ev-indicator';
        indicator.innerHTML = `
            <div class="eq12-ev-badge">
                <span class="eq12-ev-value">+EV ${opportunity.expectedValue?.toFixed(1)}%</span>
                <span class="eq12-ev-confidence">Confidence: ${opportunity.confidence || 'High'}</span>
            </div>
        `;

        indicator.style.cssText = `
            position: absolute;
            z-index: 10000;
            background: linear-gradient(45deg, #00ff88, #00cc6a);
            color: white;
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: bold;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            animation: eq12Pulse 2s infinite;
            cursor: pointer;
            pointer-events: none;
        `;

        return indicator;
    }

    positionIndicator(indicator, targetElement) {
        const rect = targetElement.getBoundingClientRect();
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

        indicator.style.top = (rect.top + scrollTop - 40) + 'px';
        indicator.style.left = (rect.left + scrollLeft + rect.width + 10) + 'px';
    }

    async autoHighlightOpportunities(scrapeData) {
        // Simple EV detection - in practice, this would call your EQ12 API
        const opportunities = scrapeData.games.flatMap(game =>
            game.odds
                .filter(odds => odds.impliedProbability && odds.impliedProbability < 0.45) // Rough EV threshold
                .map(odds => ({
                    game: game.title,
                    odds: odds.value,
                    expectedValue: ((1 / odds.impliedProbability - 1) * 100),
                    selector: odds.element,
                    confidence: 'Medium'
                }))
        );

        if (opportunities.length > 0) {
            await this.highlightEVOpportunities(opportunities);
        }
    }

    updateVpnStatusIndicator(vpnStatus) {
        // Remove existing indicator
        const existing = document.querySelector('.eq12-vpn-status');
        if (existing) existing.remove();

        // Create new indicator
        const indicator = document.createElement('div');
        indicator.className = 'eq12-vpn-status';
        indicator.innerHTML = `
            <div class="eq12-vpn-badge ${vpnStatus.connected ? 'connected' : 'disconnected'}">
                <span class="eq12-vpn-icon">${vpnStatus.connected ? '🔒' : '🚨'}</span>
                <span class="eq12-vpn-text">${vpnStatus.connected ? 'VPN Connected' : 'VPN Disconnected'}</span>
            </div>
        `;

        indicator.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 10001;
            background: ${vpnStatus.connected ? '#00ff88' : '#ff4444'};
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        `;

        document.body.appendChild(indicator);

        // Auto-hide after 5 seconds if connected
        if (vpnStatus.connected) {
            setTimeout(() => {
                if (indicator.parentNode) {
                    indicator.style.opacity = '0';
                    setTimeout(() => indicator.remove(), 300);
                }
            }, 5000);
        }
    }

    showVpnWarningOverlay() {
        // Remove existing overlay
        const existing = document.querySelector('.eq12-vpn-overlay');
        if (existing) return;

        const overlay = document.createElement('div');
        overlay.className = 'eq12-vpn-overlay';
        overlay.innerHTML = `
            <div class="eq12-vpn-warning">
                <h2>🚨 VPN Connection Lost</h2>
                <p>Betting operations are paused for security.</p>
                <p>Please reconnect your VPN before placing any bets.</p>
                <button id="eq12-check-vpn">Check VPN Status</button>
            </div>
        `;

        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 0, 0, 0.9);
            z-index: 10002;
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
            text-align: center;
            font-family: Arial, sans-serif;
        `;

        overlay.querySelector('#eq12-check-vpn').addEventListener('click', () => {
            this.messagePort?.postMessage({ action: 'checkVpnStatus' });
        });

        document.body.appendChild(overlay);
    }

    hideVpnWarningOverlay() {
        const overlay = document.querySelector('.eq12-vpn-overlay');
        if (overlay) {
            overlay.style.opacity = '0';
            setTimeout(() => overlay.remove(), 300);
        }
    }

    // Utility functions
    cleanText(text) {
        return text ? text.trim().replace(/\s+/g, ' ') : '';
    }

    getElementSelector(element) {
        // Generate a unique selector for the element
        if (element.id) return '#' + element.id;

        const path = [];
        let current = element;

        while (current && current !== document.body) {
            let selector = current.tagName.toLowerCase();

            if (current.className) {
                selector += '.' + current.className.split(' ').join('.');
            }

            path.unshift(selector);
            current = current.parentElement;
        }

        return path.join(' > ');
    }

    async performPeriodicCheck() {
        try {
            // Check if odds have changed
            await this.handleOddsUpdate();

            // Report status to background
            this.messagePort?.postMessage({
                action: 'periodicStatus',
                data: {
                    lastScrape: this.lastScrapeData?.timestamp,
                    totalOdds: this.lastScrapeData?.totalOdds || 0,
                    observerActive: this.observerActive
                }
            });
        } catch (error) {
            console.error('Periodic check error:', error);
        }
    }

    async captureCurrentOdds() {
        return await this.performScrape();
    }

    async injectEVIndicators() {
        // Add CSS animations for indicators
        if (!document.querySelector('#eq12-styles')) {
            const style = document.createElement('style');
            style.id = 'eq12-styles';
            style.textContent = `
                @keyframes eq12Pulse {
                    0%, 100% { transform: scale(1); }
                    50% { transform: scale(1.05); }
                }

                .eq12-ev-opportunity {
                    animation: eq12Pulse 2s infinite !important;
                }
            `;
            document.head.appendChild(style);
        }
    }
}

// Initialize scraper when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new EQ12SportsbookScraper();
    });
} else {
    new EQ12SportsbookScraper();
}
