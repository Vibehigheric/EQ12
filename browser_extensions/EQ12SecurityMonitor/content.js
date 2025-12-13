
// EQ12 Security Monitor Content Script
(function() {
    'use strict';
    
    let securityPanel = null;
    let isMonitoring = true;
    
    // Initialize security monitoring
    initializeSecurityMonitor();
    
    function initializeSecurityMonitor() {
        // Monitor for suspicious content
        monitorPageContent();
        
        // Check for forms (potential phishing)
        monitorForms();
        
        // Monitor for suspicious scripts
        monitorScripts();
        
        // Create floating security indicator
        createSecurityIndicator();
    }
    
    function monitorPageContent() {
        // Check for phishing keywords
        const phishingKeywords = [
            "urgent action required",
            "verify your account",
            "suspended account",
            "click here immediately",
            "limited time offer",
            "congratulations you won"
        ];
        
        const pageText = document.body.innerText.toLowerCase();
        const foundKeywords = phishingKeywords.filter(keyword => 
            pageText.includes(keyword)
        );
        
        if (foundKeywords.length >= 2) {
            showPhishingWarning(foundKeywords);
        }
    }
    
    function monitorForms() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            const hasPasswordField = form.querySelector('input[type="password"]');
            const hasEmailField = form.querySelector('input[type="email"]');
            
            if (hasPasswordField && hasEmailField) {
                // Check if form is on HTTPS
                if (location.protocol !== 'https:') {
                    showInsecureFormWarning(form);
                }
                
                // Check for suspicious form actions
                const action = form.action || form.getAttribute('action');
                if (action && !action.startsWith(location.origin)) {
                    showSuspiciousFormWarning(form, action);
                }
            }
        });
    }
    
    function monitorScripts() {
        // Monitor for suspicious script injections
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1 && node.tagName === 'SCRIPT') {
                        checkSuspiciousScript(node);
                    }
                });
            });
        });
        
        observer.observe(document, {
            childList: true,
            subtree: true
        });
    }
    
    function checkSuspiciousScript(scriptElement) {
        const src = scriptElement.src;
        const content = scriptElement.textContent;
        
        // Check for suspicious domains
        const suspiciousDomains = [
            'malware.com',
            'tracking-evil.com',
            'crypto-miner.com'
        ];
        
        if (src && suspiciousDomains.some(domain => src.includes(domain))) {
            blockSuspiciousScript(scriptElement, 'Suspicious domain');
        }
        
        // Check for cryptocurrency mining code
        if (content && (content.includes('CryptoJS') || content.includes('mining'))) {
            blockSuspiciousScript(scriptElement, 'Potential crypto mining');
        }
    }
    
    function createSecurityIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'eq12-security-indicator';
        indicator.innerHTML = '🔒 EQ12';
        indicator.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: #28a745;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: bold;
            z-index: 999999;
            cursor: pointer;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        `;
        
        indicator.addEventListener('click', toggleSecurityPanel);
        document.body.appendChild(indicator);
    }
    
    function showPhishingWarning(keywords) {
        showSecurityAlert(
            'Potential Phishing Detected',
            `This page contains suspicious content: ${keywords.join(', ')}`,
            'warning'
        );
    }
    
    function showInsecureFormWarning(form) {
        showSecurityAlert(
            'Insecure Form Detected',
            'This login form is not using HTTPS encryption',
            'error'
        );
    }
    
    function showSuspiciousFormWarning(form, action) {
        showSecurityAlert(
            'Suspicious Form Action',
            `Form submits to external domain: ${action}`,
            'warning'
        );
    }
    
    function blockSuspiciousScript(script, reason) {
        script.remove();
        showSecurityAlert(
            'Malicious Script Blocked',
            `Blocked script: ${reason}`,
            'success'
        );
    }
    
    function showSecurityAlert(title, message, type) {
        const alert = document.createElement('div');
        alert.style.cssText = `
            position: fixed;
            top: 50px;
            right: 10px;
            background: ${type === 'error' ? '#dc3545' : type === 'warning' ? '#ffc107' : '#28a745'};
            color: ${type === 'warning' ? '#000' : '#fff'};
            padding: 15px;
            border-radius: 5px;
            max-width: 300px;
            z-index: 1000000;
            font-family: Arial, sans-serif;
            font-size: 14px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        `;
        
        alert.innerHTML = `
            <strong>${title}</strong><br>
            ${message}
            <button onclick="this.parentElement.remove()" style="
                float: right;
                background: none;
                border: none;
                color: inherit;
                font-weight: bold;
                cursor: pointer;
                margin-left: 10px;
            ">×</button>
        `;
        
        document.body.appendChild(alert);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentElement) {
                alert.remove();
            }
        }, 5000);
    }
    
    function toggleSecurityPanel() {
        if (securityPanel) {
            securityPanel.remove();
            securityPanel = null;
        } else {
            createSecurityPanel();
        }
    }
    
    function createSecurityPanel() {
        securityPanel = document.createElement('div');
        securityPanel.id = 'eq12-security-panel';
        securityPanel.innerHTML = `
            <div style="background: white; border: 2px solid #007bff; border-radius: 10px; padding: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.3);">
                <h3 style="margin: 0 0 15px 0; color: #007bff;">🔒 EQ12 Security Monitor</h3>
                <div id="security-stats">
                    <p><strong>Site Security:</strong> <span id="site-status">Checking...</span></p>
                    <p><strong>Threats Blocked:</strong> <span id="threats-count">0</span></p>
                    <p><strong>Trackers Blocked:</strong> <span id="trackers-count">0</span></p>
                </div>
                <div style="margin-top: 15px;">
                    <button id="premium-upgrade" style="background: #ff6b35; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer;">
                        Upgrade to Premium
                    </button>
                    <button onclick="document.getElementById('eq12-security-panel').remove(); securityPanel = null;" style="background: #6c757d; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; margin-left: 10px;">
                        Close
                    </button>
                </div>
            </div>
        `;
        
        securityPanel.style.cssText = `
            position: fixed;
            top: 50%;
            right: 20px;
            transform: translateY(-50%);
            z-index: 1000001;
            font-family: Arial, sans-serif;
        `;
        
        document.body.appendChild(securityPanel);
        
        // Load and display stats
        loadSecurityStats();
        
        // Premium upgrade handler
        document.getElementById('premium-upgrade').addEventListener('click', () => {
            chrome.runtime.sendMessage({type: 'UPGRADE_TO_PREMIUM'});
        });
    }
    
    function loadSecurityStats() {
        chrome.storage.local.get(['threatsBlocked', 'trackersBlocked'], (result) => {
            document.getElementById('threats-count').textContent = result.threatsBlocked || 0;
            document.getElementById('trackers-count').textContent = result.trackersBlocked || 0;
        });
        
        // Check site security
        const isSecure = location.protocol === 'https:';
        const statusElement = document.getElementById('site-status');
        if (isSecure) {
            statusElement.textContent = '✅ Secure';
            statusElement.style.color = '#28a745';
        } else {
            statusElement.textContent = '⚠️ Insecure';
            statusElement.style.color = '#dc3545';
        }
    }
    
    // Listen for messages from background script
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        if (request.type === 'INSECURE_WARNING') {
            showSecurityAlert(
                'Insecure Connection',
                'This website is not using HTTPS encryption',
                'warning'
            );
        }
        
        if (request.type === 'TOGGLE_SECURITY_PANEL') {
            toggleSecurityPanel();
        }
    });
    
})();
