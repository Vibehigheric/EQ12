/**
 * EQ12 Data Pusher - Content Script
 * Runs on all web pages to capture data and inject functionality
 */

class EQ12ContentScript {
    constructor() {
        this.isInitialized = false;
        this.capturedData = {};
        this.affiliateConfig = {};
        this.dataExtractors = {};

        this.init();
    }

    init() {
        if (this.isInitialized) return;

        console.log('🧠 EQ12 Content Script initializing on:', window.location.href);

        // Setup message listener
        browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
            this.handleMessage(message, sender, sendResponse);
            return true; // Keep channel open for async response
        });

        // Load configuration
        this.loadConfig();

        // Setup data extractors
        this.setupExtractors();

        // Setup context menu handlers
        this.setupContextMenu();

        // Auto-detect and capture if enabled
        this.autoDetectData();

        this.isInitialized = true;
        console.log('✅ EQ12 Content Script ready');
    }

    async loadConfig() {
        try {
            const stored = await browser.storage.local.get([
                'affiliate_config',
                'auto_capture',
                'ai_analysis'
            ]);

            this.affiliateConfig = stored.affiliate_config || {
                stubhub: { id: 'EQ12STUBHUB', param: 'ref' },
                expedia: { id: 'EQ12EXPEDIA', param: 'SEMCID' },
                booking: { id: 'EQ12BOOKING', param: 'aid' },
                kayak: { id: 'EQ12KAYAK', param: 'a' }
            };

            this.autoCapture = stored.auto_capture || false;
            this.aiAnalysis = stored.ai_analysis || true;

        } catch (error) {
            console.error('Error loading config:', error);
        }
    }

    setupExtractors() {
        this.dataExtractors = {
            odds: {
                selectors: [
                    '.odds-table', '.betting-odds', '.sportsbook-odds',
                    '[data-testid*="odds"]', '.odds-grid', '.bet-button'
                ],
                patterns: {
                    odds: /[+-]\d{3,4}|(\d+\/\d+)|(\d+\.\d{2})/g,
                    teams: /vs\.|@|\s-\s/,
                    spreads: /[+-]\d+\.?5?/g
                }
            },
            deals: {
                selectors: [
                    '.deal-price', '.price', '.cost', '.total-cost',
                    '[data-testid*="price"]', '.fare', '.rate'
                ],
                patterns: {
                    price: /\$[\d,]+\.?\d*/g,
                    discount: /\d+%\s*off|save\s*\$\d+/gi,
                    dates: /\d{1,2}\/\d{1,2}\/\d{4}|\d{4}-\d{2}-\d{2}/g
                }
            },
            tickets: {
                selectors: [
                    '.ticket-price', '.seat-price', '.listing-price',
                    '.price-display', '[data-testid*="ticket"]'
                ],
                patterns: {
                    price: /\$[\d,]+/g,
                    section: /section\s+\w+/gi,
                    row: /row\s+\w+/gi
                }
            },
            finance: {
                selectors: [
                    '.apr', '.interest-rate', '.credit-score',
                    '.annual-fee', '.reward-rate'
                ],
                patterns: {
                    apr: /\d+\.?\d*%\s*APR/gi,
                    fee: /\$\d+\s*annual\s*fee/gi,
                    rewards: /\d+\.?\d*%\s*(cash\s*back|points)/gi
                }
            }
        };
    }

    setupContextMenu() {
        // Add EQ12 overlay CSS if not already present
        if (!document.getElementById('eq12-overlay-css')) {
            const css = document.createElement('style');
            css.id = 'eq12-overlay-css';
            css.textContent = `
                .eq12-highlight {
                    outline: 2px solid #00d4ff !important;
                    background: rgba(0, 212, 255, 0.1) !important;
                }
                .eq12-captured {
                    outline: 2px solid #00ff88 !important;
                    background: rgba(0, 255, 136, 0.1) !important;
                }
                .eq12-tooltip {
                    position: absolute;
                    background: #1a1f3a;
                    color: #ffffff;
                    padding: 5px 10px;
                    border-radius: 4px;
                    font-size: 12px;
                    z-index: 10000;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
                }
            `;
            document.head.appendChild(css);
        }
    }

    async handleMessage(message, sender, sendResponse) {
        try {
            switch (message.action) {
                case 'captureData':
                    const result = await this.captureData(message.type, message.options);
                    sendResponse(result);
                    break;

                case 'injectAffiliate':
                    const injectResult = await this.injectAffiliateLinks();
                    sendResponse(injectResult);
                    break;

                case 'highlightElements':
                    this.highlightCaptureElements(message.type);
                    sendResponse({ success: true });
                    break;

                case 'getPageInfo':
                    const pageInfo = this.getPageInfo();
                    sendResponse(pageInfo);
                    break;

                default:
                    sendResponse({ error: 'Unknown action' });
            }
        } catch (error) {
            console.error('Error handling message:', error);
            sendResponse({ error: error.message });
        }
    }

    async captureData(type, options = {}) {
        console.log(`🔍 Capturing ${type} data...`);

        try {
            let data = {};

            switch (type) {
                case 'odds':
                    data = this.captureOddsData();
                    break;
                case 'deals':
                    data = this.captureDealsData();
                    break;
                case 'selection':
                    data = this.captureSelectedText();
                    break;
                case 'page':
                    data = this.capturePageData();
                    break;
                case 'intelligent':
                    data = this.intelligentCapture();
                    break;
                default:
                    data = this.captureGenericData();
            }

            // Add metadata
            data._metadata = {
                url: window.location.href,
                title: document.title,
                timestamp: new Date().toISOString(),
                type: type,
                userAgent: navigator.userAgent
            };

            // Highlight captured elements
            this.highlightCapturedElements();

            return { success: true, data: data };

        } catch (error) {
            console.error(`Error capturing ${type} data:`, error);
            return { error: error.message };
        }
    }

    captureOddsData() {
        const data = {
            odds: [],
            games: [],
            spreads: [],
            totals: []
        };

        const extractor = this.dataExtractors.odds;

        // Find odds elements
        extractor.selectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                const text = element.textContent.trim();

                // Extract odds
                const oddsMatches = text.match(extractor.patterns.odds);
                if (oddsMatches) {
                    data.odds.push({
                        element: this.getElementPath(element),
                        text: text,
                        odds: oddsMatches,
                        position: this.getElementPosition(element)
                    });
                }

                // Extract spreads
                const spreadMatches = text.match(extractor.patterns.spreads);
                if (spreadMatches) {
                    data.spreads.push({
                        element: this.getElementPath(element),
                        text: text,
                        spreads: spreadMatches
                    });
                }
            });
        });

        // Try to identify games and matchups
        const gameElements = document.querySelectorAll([
            '.game', '.matchup', '.event', '.fixture',
            '[data-testid*="game"]', '[data-testid*="event"]'
        ].join(','));

        gameElements.forEach(element => {
            const text = element.textContent.trim();
            if (extractor.patterns.teams.test(text)) {
                data.games.push({
                    element: this.getElementPath(element),
                    text: text,
                    teams: text.split(extractor.patterns.teams).map(t => t.trim())
                });
            }
        });

        return data;
    }

    captureDealsData() {
        const data = {
            prices: [],
            deals: [],
            dates: [],
            locations: []
        };

        const extractor = this.dataExtractors.deals;

        // Capture prices
        extractor.selectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                const text = element.textContent.trim();

                const priceMatches = text.match(extractor.patterns.price);
                if (priceMatches) {
                    data.prices.push({
                        element: this.getElementPath(element),
                        text: text,
                        prices: priceMatches,
                        position: this.getElementPosition(element)
                    });
                }
            });
        });

        // Capture discount information
        const discountElements = document.querySelectorAll('*');
        discountElements.forEach(element => {
            const text = element.textContent.trim();
            const discountMatch = text.match(extractor.patterns.discount);
            if (discountMatch) {
                data.deals.push({
                    element: this.getElementPath(element),
                    text: text,
                    discount: discountMatch[0]
                });
            }
        });

        // Capture dates
        const bodyText = document.body.textContent;
        const dateMatches = bodyText.match(extractor.patterns.dates);
        if (dateMatches) {
            data.dates = [...new Set(dateMatches)]; // Remove duplicates
        }

        return data;
    }

    captureSelectedText() {
        const selection = window.getSelection();

        if (!selection.rangeCount) {
            return { error: 'No text selected' };
        }

        const range = selection.getRangeAt(0);
        const selectedText = selection.toString().trim();

        if (!selectedText) {
            return { error: 'No text in selection' };
        }

        return {
            selectedText: selectedText,
            html: range.cloneContents().textContent,
            startContainer: this.getElementPath(range.startContainer.parentElement),
            endContainer: this.getElementPath(range.endContainer.parentElement),
            position: this.getSelectionPosition(selection)
        };
    }

    capturePageData() {
        return {
            title: document.title,
            url: window.location.href,
            metaTags: this.extractMetaTags(),
            headings: this.extractHeadings(),
            links: this.extractLinks(),
            forms: this.extractForms(),
            images: this.extractImages(),
            scripts: this.extractScripts(),
            pageText: document.body.textContent.trim().substring(0, 5000) // First 5000 chars
        };
    }

    intelligentCapture() {
        // Combine multiple capture methods based on page type
        const url = window.location.href.toLowerCase();
        let data = {};

        // Determine page type and capture accordingly
        if (url.includes('draftkings') || url.includes('fanduel') ||
            url.includes('mybookie') || url.includes('betrivers') ||
            url.includes('bovada') || url.includes('sportsbook')) {
            data = { ...data, ...this.captureOddsData() };
        }

        if (url.includes('expedia') || url.includes('booking') ||
            url.includes('kayak') || url.includes('hotels')) {
            data = { ...data, ...this.captureDealsData() };
        }

        if (url.includes('stubhub') || url.includes('ticketmaster') ||
            url.includes('seatgeek')) {
            data = { ...data, ...this.captureTicketData() };
        }

        // Always include basic page data
        data.pageInfo = this.capturePageData();

        // Add intelligent analysis
        data.analysis = this.analyzePageContent();

        return data;
    }

    captureTicketData() {
        const data = {
            tickets: [],
            sections: [],
            prices: []
        };

        const extractor = this.dataExtractors.tickets;

        extractor.selectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                const text = element.textContent.trim();

                const priceMatches = text.match(extractor.patterns.price);
                const sectionMatches = text.match(extractor.patterns.section);
                const rowMatches = text.match(extractor.patterns.row);

                if (priceMatches || sectionMatches || rowMatches) {
                    data.tickets.push({
                        element: this.getElementPath(element),
                        text: text,
                        prices: priceMatches,
                        sections: sectionMatches,
                        rows: rowMatches
                    });
                }
            });
        });

        return data;
    }

    analyzePageContent() {
        const analysis = {
            pageType: 'unknown',
            dataQuality: 'low',
            captureConfidence: 0,
            recommendedActions: []
        };

        const url = window.location.href.toLowerCase();
        const title = document.title.toLowerCase();
        const bodyText = document.body.textContent.toLowerCase();

        // Determine page type
        const patterns = {
            'sportsbook': ['odds', 'bet', 'sportsbook', 'parlay', 'moneyline'],
            'travel': ['hotel', 'flight', 'car rental', 'vacation', 'booking'],
            'tickets': ['tickets', 'seats', 'event', 'concert', 'game'],
            'finance': ['credit card', 'loan', 'apr', 'interest', 'banking']
        };

        for (const [type, keywords] of Object.entries(patterns)) {
            const matches = keywords.filter(keyword =>
                url.includes(keyword) || title.includes(keyword) || bodyText.includes(keyword)
            );

            if (matches.length > 0) {
                analysis.pageType = type;
                analysis.captureConfidence = Math.min(matches.length / keywords.length * 100, 100);
                break;
            }
        }

        // Assess data quality
        const dataElements = document.querySelectorAll([
            '.price', '.odds', '.deal', '.discount', '[data-price]',
            '[data-odds]', '.cost', '.rate', '.fee'
        ].join(','));

        if (dataElements.length > 10) {
            analysis.dataQuality = 'high';
        } else if (dataElements.length > 3) {
            analysis.dataQuality = 'medium';
        }

        // Generate recommendations
        if (analysis.pageType !== 'unknown') {
            analysis.recommendedActions.push(`Capture ${analysis.pageType} data`);
        }

        if (analysis.dataQuality === 'high') {
            analysis.recommendedActions.push('Run AI analysis');
        }

        if (this.detectAffiliateOpportunity()) {
            analysis.recommendedActions.push('Inject affiliate links');
        }

        return analysis;
    }

    async injectAffiliateLinks() {
        console.log('💰 Injecting affiliate links...');

        let injectedCount = 0;

        try {
            // Find links that match affiliate patterns
            const links = document.querySelectorAll('a[href]');

            links.forEach(link => {
                const href = link.href.toLowerCase();

                // Check each affiliate pattern
                for (const [site, config] of Object.entries(this.affiliateConfig)) {
                    if (href.includes(site)) {
                        // Don't modify if already has affiliate ID
                        if (href.includes(config.param)) continue;

                        // Add affiliate parameter
                        const separator = href.includes('?') ? '&' : '?';
                        const newHref = `${link.href}${separator}${config.param}=${config.id}`;

                        link.href = newHref;
                        link.classList.add('eq12-affiliate-injected');
                        injectedCount++;
                    }
                }
            });

            return { success: true, count: injectedCount };

        } catch (error) {
            console.error('Error injecting affiliate links:', error);
            return { error: error.message };
        }
    }

    detectAffiliateOpportunity() {
        const url = window.location.href.toLowerCase();
        return Object.keys(this.affiliateConfig).some(site => url.includes(site));
    }

    highlightCaptureElements(type) {
        // Remove existing highlights
        document.querySelectorAll('.eq12-highlight').forEach(el => {
            el.classList.remove('eq12-highlight');
        });

        if (!type) return;

        const extractor = this.dataExtractors[type];
        if (!extractor) return;

        extractor.selectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => {
                element.classList.add('eq12-highlight');
            });
        });
    }

    highlightCapturedElements() {
        // Mark elements as captured (green outline)
        document.querySelectorAll('.eq12-highlight').forEach(el => {
            el.classList.remove('eq12-highlight');
            el.classList.add('eq12-captured');
        });

        // Remove captured class after 3 seconds
        setTimeout(() => {
            document.querySelectorAll('.eq12-captured').forEach(el => {
                el.classList.remove('eq12-captured');
            });
        }, 3000);
    }

    getElementPath(element) {
        if (!element || element === document.body) return '';

        const names = [];
        while (element && element !== document.body) {
            let name = element.localName;
            if (element.id) {
                name += `#${element.id}`;
            } else if (element.className) {
                name += `.${element.className.split(' ').join('.')}`;
            }
            names.unshift(name);
            element = element.parentElement;
        }

        return names.join(' > ');
    }

    getElementPosition(element) {
        const rect = element.getBoundingClientRect();
        return {
            top: rect.top + window.scrollY,
            left: rect.left + window.scrollX,
            width: rect.width,
            height: rect.height
        };
    }

    getSelectionPosition(selection) {
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        return {
            top: rect.top + window.scrollY,
            left: rect.left + window.scrollX,
            width: rect.width,
            height: rect.height
        };
    }

    extractMetaTags() {
        const metaTags = {};
        document.querySelectorAll('meta').forEach(meta => {
            const name = meta.name || meta.property || meta.httpEquiv;
            if (name) {
                metaTags[name] = meta.content;
            }
        });
        return metaTags;
    }

    extractHeadings() {
        const headings = [];
        document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(heading => {
            headings.push({
                level: parseInt(heading.tagName.substring(1)),
                text: heading.textContent.trim(),
                id: heading.id
            });
        });
        return headings;
    }

    extractLinks() {
        const links = [];
        document.querySelectorAll('a[href]').forEach(link => {
            links.push({
                href: link.href,
                text: link.textContent.trim(),
                title: link.title
            });
        });
        return links.slice(0, 50); // Limit to first 50 links
    }

    extractForms() {
        const forms = [];
        document.querySelectorAll('form').forEach(form => {
            const inputs = Array.from(form.querySelectorAll('input, select, textarea')).map(input => ({
                type: input.type,
                name: input.name,
                id: input.id,
                placeholder: input.placeholder
            }));

            forms.push({
                action: form.action,
                method: form.method,
                inputs: inputs
            });
        });
        return forms;
    }

    extractImages() {
        const images = [];
        document.querySelectorAll('img').forEach(img => {
            images.push({
                src: img.src,
                alt: img.alt,
                title: img.title
            });
        });
        return images.slice(0, 20); // Limit to first 20 images
    }

    extractScripts() {
        const scripts = [];
        document.querySelectorAll('script[src]').forEach(script => {
            scripts.push(script.src);
        });
        return scripts;
    }

    autoDetectData() {
        if (!this.autoCapture) return;

        // Auto-detect after page load with delay
        setTimeout(() => {
            const analysis = this.analyzePageContent();
            if (analysis.captureConfidence > 70) {
                console.log('🤖 Auto-capturing data based on page analysis');
                this.captureData('intelligent');
            }
        }, 2000);
    }

    getPageInfo() {
        return {
            url: window.location.href,
            title: document.title,
            domain: window.location.hostname,
            analysis: this.analyzePageContent()
        };
    }
}

// Initialize content script
if (typeof window !== 'undefined') {
    const eq12Content = new EQ12ContentScript();
}
