
// EQ12 Security Monitor Popup Script
document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    setupEventListeners();
});

function loadStats() {
    chrome.storage.local.get([
        'threatsBlocked',
        'trackersBlocked', 
        'sitesScanned',
        'isEnabled'
    ], function(result) {
        document.getElementById('threats-blocked').textContent = result.threatsBlocked || 0;
        document.getElementById('trackers-blocked').textContent = result.trackersBlocked || 0;
        document.getElementById('sites-scanned').textContent = result.sitesScanned || 0;
        
        const isEnabled = result.isEnabled !== false;
        document.getElementById('protection-status').textContent = isEnabled ? 'Active' : 'Disabled';
        document.getElementById('toggle-protection').textContent = isEnabled ? 'Disable Protection' : 'Enable Protection';
    });
}

function setupEventListeners() {
    document.getElementById('toggle-protection').addEventListener('click', function() {
        chrome.storage.local.get(['isEnabled'], function(result) {
            const newState = !result.isEnabled;
            chrome.storage.local.set({isEnabled: newState});
            loadStats();
        });
    });
    
    document.getElementById('scan-site').addEventListener('click', function() {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.tabs.sendMessage(tabs[0].id, {type: 'MANUAL_SCAN'});
            // Increment scanned counter
            chrome.storage.local.get(['sitesScanned'], function(result) {
                chrome.storage.local.set({sitesScanned: (result.sitesScanned || 0) + 1});
                loadStats();
            });
        });
    });
    
    document.getElementById('upgrade-premium').addEventListener('click', function() {
        chrome.runtime.sendMessage({type: 'UPGRADE_TO_PREMIUM'});
    });
}
