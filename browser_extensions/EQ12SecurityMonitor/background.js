
// EQ12 Security Monitor Background Script
chrome.runtime.onInstalled.addListener(() => {
    console.log("EQ12 Security Monitor installed");
    
    // Initialize security settings
    chrome.storage.local.set({
        securityLevel: "medium",
        threatsBlocked: 0,
        maliciousDomainsBlocked: 0,
        trackersBlocked: 0,
        isEnabled: true
    });
});

// Security monitoring
const maliciousDomains = [
    "malware-test.com",
    "phishing-test.com", 
    "suspicious-site.com",
    "fake-bank.com",
    "scam-store.com"
];

const trackingDomains = [
    "google-analytics.com",
    "facebook.com/tr",
    "doubleclick.net",
    "googletagmanager.com"
];

// Monitor web requests
chrome.webNavigation.onBeforeNavigate.addListener((details) => {
    if (details.frameId === 0) { // Main frame only
        checkSiteSecurity(details.url, details.tabId);
    }
});

function checkSiteSecurity(url, tabId) {
    try {
        const domain = new URL(url).hostname;
        
        // Check for malicious domains
        if (maliciousDomains.some(malicious => domain.includes(malicious))) {
            blockMaliciousSite(url, tabId, "malware");
            return;
        }
        
        // Check for HTTP sites (insecure)
        if (url.startsWith("http://") && !url.startsWith("http://localhost")) {
            warnInsecureSite(url, tabId);
        }
        
        // Check for tracking
        if (trackingDomains.some(tracker => domain.includes(tracker))) {
            incrementCounter("trackersBlocked");
        }
        
    } catch (error) {
        console.error("Security check error:", error);
    }
}

function blockMaliciousSite(url, tabId, threatType) {
    // Block the site and show warning
    chrome.tabs.update(tabId, {
        url: chrome.runtime.getURL("security-panel.html") + 
             "?blocked=" + encodeURIComponent(url) + 
             "&threat=" + threatType
    });
    
    incrementCounter("threatsBlocked");
    incrementCounter("maliciousDomainsBlocked");
}

function warnInsecureSite(url, tabId) {
    // Inject warning for insecure sites
    chrome.tabs.sendMessage(tabId, {
        type: "INSECURE_WARNING",
        url: url
    });
}

function incrementCounter(counterName) {
    chrome.storage.local.get([counterName], (result) => {
        const newValue = (result[counterName] || 0) + 1;
        chrome.storage.local.set({[counterName]: newValue});
    });
}

// Handle extension icon clicks
chrome.action.onClicked.addListener((tab) => {
    chrome.tabs.sendMessage(tab.id, {type: "TOGGLE_SECURITY_PANEL"});
});

// Premium features (monetization)
function checkPremiumStatus() {
    return new Promise((resolve) => {
        chrome.storage.local.get(["isPremium"], (result) => {
            resolve(result.isPremium || false);
        });
    });
}

// API for premium upgrade
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "UPGRADE_TO_PREMIUM") {
        // Redirect to premium purchase page
        chrome.tabs.create({
            url: "https://eq12security.com/premium-upgrade"
        });
    }
    
    if (request.type === "GET_PREMIUM_STATUS") {
        checkPremiumStatus().then(sendResponse);
        return true; // Keep message channel open
    }
});
