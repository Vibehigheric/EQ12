// Content script for EV highlighting on sportsbook sites
const HIGHLIGHT_COLOR = "rgba(16, 185, 129, 0.25)"; // green tint for EV+ bets
const EV_THRESHOLD = 0.05; // 5% EV threshold

let isHighlightingEnabled = true;
let cachedEVData = new Map();

// Debounce function to limit API calls
function debounce(func, wait) {
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

// Extract odds from different sportsbook formats
function extractOdds(text) {
    // Handle American odds (+150, -200)
    const americanMatch = text.match(/([+-])(\d+)/);
    if (americanMatch) {
        const sign = americanMatch[1];
        const value = parseInt(americanMatch[2]);
        return sign === '+' ? `+${value}` : `-${value}`;
    }

    // Handle decimal odds (2.50, 1.75)
    const decimalMatch = text.match(/(\d+\.\d+)/);
    if (decimalMatch) {
        return parseFloat(decimalMatch[1]);
    }

    // Handle fractional odds (3/2, 5/1)
    const fractionalMatch = text.match(/(\d+)\/(\d+)/);
    if (fractionalMatch) {
        return `${fractionalMatch[1]}/${fractionalMatch[2]}`;
    }

    return null;
}

// Site-specific selectors for major sportsbooks
const SPORTSBOOK_SELECTORS = {
    'draftkings.com': {
        odds: '[data-testid*="odds"], .sportsbook-odds-american-odds, .outcome-cell',
        bet: '.sportsbook-outcome-cell, .outcome-wrapper'
    },
    'fanduel.com': {
        odds: '[data-testid*="price"], .bet-price, .price',
        bet: '.market-btn, .bet-btn'
    },
    'betmgm.com': {
        odds: '.option-pick-odds, .odds-value',
        bet: '.option-pick'
    },
    'caesars.com': {
        odds: '.odds, .price-value',
        bet: '.selection'
    },
    'barstoolsportsbook.com': {
        odds: '.odds-value, .price',
        bet: '.bet-option'
    }
};

// Get selectors for current site
function getCurrentSiteSelectors() {
    const hostname = window.location.hostname;
    for (const [site, selectors] of Object.entries(SPORTSBOOK_SELECTORS)) {
        if (hostname.includes(site)) {
            return selectors;
        }
    }
    return null;
}

// Check if bet has positive EV via EQ12 backend
async function checkEV(selection, odds) {
    try {
        const response = await browser.runtime.sendMessage({
            type: 'CHECK_EV',
            selection,
            odds
        });

        if (response?.ok && response.data) {
            return {
                ev: response.data.expected_value,
                isPositive: response.data.expected_value > EV_THRESHOLD
            };
        }
    } catch (error) {
        console.log('EV check failed:', error);
    }

    return { ev: 0, isPositive: false };
}

// Highlight elements with positive EV
function highlightElement(element, ev) {
    element.style.backgroundColor = HIGHLIGHT_COLOR;
    element.style.border = '2px solid #10b981';
    element.style.borderRadius = '4px';
    element.setAttribute('title', `🎯 EV+: ${(ev * 100).toFixed(1)}% advantage`);

    // Add EV badge
    const badge = document.createElement('div');
    badge.innerHTML = `🎯 +${(ev * 100).toFixed(1)}%`;
    badge.style.cssText = `
    position: absolute;
    top: -8px;
    right: -8px;
    background: #10b981;
    color: white;
    font-size: 10px;
    font-weight: bold;
    padding: 2px 6px;
    border-radius: 10px;
    z-index: 9999;
  `;

    element.style.position = 'relative';
    element.appendChild(badge);
}

// Scan page for odds and highlight EV+ bets
async function scanAndHighlight() {
    if (!isHighlightingEnabled) return;

    const selectors = getCurrentSiteSelectors();
    if (!selectors) return;

    const oddsElements = document.querySelectorAll(selectors.odds);
    const processed = new Set();

    for (const element of oddsElements) {
        const text = element.textContent?.trim();
        if (!text || processed.has(text)) continue;

        const odds = extractOdds(text);
        if (!odds) continue;

        processed.add(text);

        // Check cache first
        const cacheKey = `${text}_${odds}`;
        if (cachedEVData.has(cacheKey)) {
            const { ev, isPositive } = cachedEVData.get(cacheKey);
            if (isPositive) {
                highlightElement(element, ev);
            }
            continue;
        }

        // Check EV with backend (throttled)
        const evData = await checkEV(text, odds);
        cachedEVData.set(cacheKey, evData);

        if (evData.isPositive) {
            highlightElement(element, evData.ev);
        }
    }
}

// Debounced scan function
const debouncedScan = debounce(scanAndHighlight, 1000);

// Listen for messages from popup/background
browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'TOGGLE_HIGHLIGHTING') {
        isHighlightingEnabled = message.enabled;
        if (!isHighlightingEnabled) {
            // Remove all highlights
            document.querySelectorAll('[title*="EV+"]').forEach(el => {
                el.style.backgroundColor = '';
                el.style.border = '';
                el.removeAttribute('title');
                const badge = el.querySelector('div[style*="position: absolute"]');
                if (badge) badge.remove();
            });
        } else {
            scanAndHighlight();
        }
        sendResponse({ ok: true });
    }

    if (message.type === 'SCAN_NOW') {
        scanAndHighlight();
        sendResponse({ ok: true });
    }
});

// Set up mutation observer for dynamic content
const observer = new MutationObserver(() => {
    debouncedScan();
});

// Start observing
if (document.documentElement) {
    observer.observe(document.documentElement, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['data-testid', 'class']
    });
}

// Initial scan when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', scanAndHighlight);
} else {
    scanAndHighlight();
}

// Periodic cache cleanup (every 5 minutes)
setInterval(() => {
    if (cachedEVData.size > 100) {
        cachedEVData.clear();
    }
}, 300000);
