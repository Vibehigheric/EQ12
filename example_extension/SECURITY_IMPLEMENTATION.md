# Security Implementation Guide

## Content Security Policy (CSP) Implementation

### Current CSP Configuration
```json
"content_security_policy": "script-src 'self'; object-src 'none'; connect-src https: data: blob: filesystem:;"
```

### Enhanced Security Features

#### 1. Secure Communication
```javascript
// secure-communication.js - Add to extension
class SecureCommunication {
    constructor() {
        this.encryptionKey = null;
        this.initializeEncryption();
    }
    
    async initializeEncryption() {
        // Generate or retrieve encryption key for sensitive data
        const keyData = await this.getOrCreateKey();
        this.encryptionKey = await crypto.subtle.importKey(
            'raw',
            keyData,
            { name: 'AES-GCM' },
            false,
            ['encrypt', 'decrypt']
        );
    }
    
    async getOrCreateKey() {
        let keyData = await this.getStoredKey();
        if (!keyData) {
            keyData = crypto.getRandomValues(new Uint8Array(32));
            await this.storeKey(keyData);
        }
        return keyData;
    }
    
    async getStoredKey() {
        return new Promise((resolve) => {
            chrome.storage.local.get(['encryptionKey'], (result) => {
                resolve(result.encryptionKey ? new Uint8Array(result.encryptionKey) : null);
            });
        });
    }
    
    async storeKey(keyData) {
        return new Promise((resolve) => {
            chrome.storage.local.set({ 
                encryptionKey: Array.from(keyData) 
            }, resolve);
        });
    }
    
    async encryptData(data) {
        if (!this.encryptionKey) {
            await this.initializeEncryption();
        }
        
        const encoder = new TextEncoder();
        const encodedData = encoder.encode(JSON.stringify(data));
        const iv = crypto.getRandomValues(new Uint8Array(12));
        
        const encryptedData = await crypto.subtle.encrypt(
            { name: 'AES-GCM', iv: iv },
            this.encryptionKey,
            encodedData
        );
        
        return {
            iv: Array.from(iv),
            data: Array.from(new Uint8Array(encryptedData))
        };
    }
    
    async decryptData(encryptedObj) {
        if (!this.encryptionKey) {
            await this.initializeEncryption();
        }
        
        const iv = new Uint8Array(encryptedObj.iv);
        const encryptedData = new Uint8Array(encryptedObj.data);
        
        const decryptedData = await crypto.subtle.decrypt(
            { name: 'AES-GCM', iv: iv },
            this.encryptionKey,
            encryptedData
        );
        
        const decoder = new TextDecoder();
        const decodedData = decoder.decode(decryptedData);
        return JSON.parse(decodedData);
    }
}
```

#### 2. Input Validation and Sanitization
```javascript
// input-validator.js - Add to extension
class InputValidator {
    static sanitizeHTML(input) {
        const div = document.createElement('div');
        div.textContent = input;
        return div.innerHTML;
    }
    
    static validateURL(url) {
        try {
            const parsedURL = new URL(url);
            // Only allow HTTP/HTTPS protocols
            if (!['http:', 'https:'].includes(parsedURL.protocol)) {
                return false;
            }
            // Prevent data: and javascript: URLs
            return !url.toLowerCase().startsWith('data:') && 
                   !url.toLowerCase().startsWith('javascript:');
        } catch {
            return false;
        }
    }
    
    static sanitizeErrorMessage(error) {
        // Remove potentially sensitive information from error messages
        const sanitized = error.toString()
            .replace(/file:\/\/[^\s]*/g, '[LOCAL_FILE]')
            .replace(/chrome-extension:\/\/[^\s]*/g, '[EXTENSION_FILE]')
            .replace(/\/[^\s]*\/[^\s]*/g, '[PATH]')
            .substring(0, 500); // Limit length
        return this.sanitizeHTML(sanitized);
    }
    
    static validateStorageKey(key) {
        // Validate storage keys to prevent injection
        return /^[a-zA-Z0-9_\-\.]+$/.test(key) && key.length <= 100;
    }
    
    static sanitizeStorageValue(value) {
        // Ensure storage values are safe
        if (typeof value === 'string') {
            return value.substring(0, 10000); // Limit size
        }
        return value;
    }
}
```

#### 3. Permission Management
```javascript
// permission-manager.js - Add to extension
class PermissionManager {
    constructor() {
        this.requiredPermissions = ['activeTab', 'storage'];
        this.optionalPermissions = ['contextMenus', 'notifications'];
    }
    
    async checkRequiredPermissions() {
        return new Promise((resolve) => {
            chrome.permissions.contains({
                permissions: this.requiredPermissions
            }, resolve);
        });
    }
    
    async requestOptionalPermission(permission) {
        if (!this.optionalPermissions.includes(permission)) {
            throw new Error('Permission not in allowed list');
        }
        
        return new Promise((resolve) => {
            chrome.permissions.request({
                permissions: [permission]
            }, (granted) => {
                if (granted) {
                    this.logPermissionChange('granted', permission);
                }
                resolve(granted);
            });
        });
    }
    
    async removeOptionalPermission(permission) {
        return new Promise((resolve) => {
            chrome.permissions.remove({
                permissions: [permission]
            }, (removed) => {
                if (removed) {
                    this.logPermissionChange('removed', permission);
                }
                resolve(removed);
            });
        });
    }
    
    logPermissionChange(action, permission) {
        const timestamp = new Date().toISOString();
        console.log(`[${timestamp}] Permission ${action}: ${permission}`);
        
        // Store permission change log locally
        chrome.storage.local.get(['permissionLog'], (result) => {
            const log = result.permissionLog || [];
            log.push({
                timestamp,
                action,
                permission
            });
            
            // Keep only last 100 entries
            if (log.length > 100) {
                log.splice(0, log.length - 100);
            }
            
            chrome.storage.local.set({ permissionLog: log });
        });
    }
}
```

#### 4. Secure Error Handling
```javascript
// secure-error-handler.js - Add to extension
class SecureErrorHandler {
    constructor(privacyConsent) {
        this.privacyConsent = privacyConsent;
        this.errorCount = 0;
        this.maxErrors = 50; // Rate limiting
    }
    
    handleError(error, context = '', sensitiveData = false) {
        this.errorCount++;
        
        // Rate limiting for error reporting
        if (this.errorCount > this.maxErrors) {
            console.warn('Error reporting rate limit reached');
            return;
        }
        
        const timestamp = new Date().toISOString();
        const errorInfo = {
            timestamp,
            context,
            message: InputValidator.sanitizeErrorMessage(error),
            userAgent: navigator.userAgent.split(' ')[0], // Minimal UA info
            url: location.protocol === 'chrome-extension:' ? '[EXTENSION]' : '[WEB]'
        };
        
        // Log locally
        this.logErrorLocally(errorInfo);
        
        // Only consider remote logging if user consented and not sensitive
        if (!sensitiveData && this.privacyConsent.canCollectErrorData()) {
            this.considerRemoteLogging(errorInfo);
        }
    }
    
    logErrorLocally(errorInfo) {
        chrome.storage.local.get(['errorLog'], (result) => {
            const log = result.errorLog || [];
            log.push(errorInfo);
            
            // Keep only last 50 errors locally
            if (log.length > 50) {
                log.splice(0, log.length - 50);
            }
            
            chrome.storage.local.set({ errorLog: log });
        });
    }
    
    async considerRemoteLogging(errorInfo) {
        // Additional user confirmation for sensitive contexts
        const confirmed = await this.getUserConfirmation(
            'An error occurred. Send anonymous error report to help improve the extension?'
        );
        
        if (confirmed) {
            // Implement secure transmission
            this.sendSecureErrorReport(errorInfo);
        }
    }
    
    async getUserConfirmation(message) {
        return new Promise((resolve) => {
            // Show notification with user choice
            chrome.notifications.create({
                type: 'basic',
                iconUrl: 'icons/icon48.png',
                title: 'EQ12 Governance Assistant',
                message,
                buttons: [{ title: 'Yes, send report' }, { title: 'No, keep local' }]
            }, (notificationId) => {
                const listener = (clickedId, buttonIndex) => {
                    if (clickedId === notificationId) {
                        chrome.notifications.onButtonClicked.removeListener(listener);
                        chrome.notifications.clear(notificationId);
                        resolve(buttonIndex === 0);
                    }
                };
                chrome.notifications.onButtonClicked.addListener(listener);
                
                // Auto-resolve to false after 10 seconds
                setTimeout(() => {
                    chrome.notifications.onButtonClicked.removeListener(listener);
                    chrome.notifications.clear(notificationId);
                    resolve(false);
                }, 10000);
            });
        });
    }
    
    async sendSecureErrorReport(errorInfo) {
        try {
            // Encrypt sensitive data before transmission
            const secureCommunication = new SecureCommunication();
            const encryptedData = await secureCommunication.encryptData(errorInfo);
            
            // Implement secure HTTPS endpoint
            const response = await fetch('https://your-secure-endpoint.com/error-report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Extension-Version': chrome.runtime.getManifest().version
                },
                body: JSON.stringify({
                    encrypted: encryptedData,
                    timestamp: new Date().toISOString()
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to send error report');
            }
            
            console.log('Error report sent successfully');
        } catch (reportError) {
            console.warn('Failed to send error report:', reportError);
            // Don't create infinite error loops
        }
    }
}
```

## Integration with Existing Code

### Update background.js
```javascript
// Add to background.js
let permissionManager, secureErrorHandler;

// Initialize security components
async function initializeSecurity() {
    permissionManager = new PermissionManager();
    secureErrorHandler = new SecureErrorHandler(privacyConsent);
    
    // Check required permissions
    const hasRequired = await permissionManager.checkRequiredPermissions();
    if (!hasRequired) {
        console.error('Missing required permissions');
    }
}

// Update error handling in existing functions
function handleSecureError(error, context, sensitive = false) {
    if (secureErrorHandler) {
        secureErrorHandler.handleError(error, context, sensitive);
    } else {
        console.error('Security not initialized:', error);
    }
}

// Initialize on startup
initializeSecurity();
```

### Update manifest.json for Security
```json
{
  "content_security_policy": "script-src 'self'; object-src 'none'; connect-src https: data: blob: filesystem:; frame-src 'none'; base-uri 'self';",
  "permissions": [
    "activeTab",
    "storage",
    "notifications"
  ],
  "optional_permissions": [
    "contextMenus"
  ],
  "host_permissions": [
  ],
  "web_accessible_resources": [
    {
      "resources": ["privacy-consent.html"],
      "matches": ["<all_urls>"],
      "use_dynamic_url": false
    }
  ]
}
```

## Security Testing Checklist

### 1. CSP Compliance
- [ ] No inline scripts or styles
- [ ] All external resources over HTTPS
- [ ] No eval() or similar dynamic code execution
- [ ] Proper nonce or hash for any necessary inline content

### 2. Input Validation
- [ ] All user inputs sanitized
- [ ] URL validation for any external requests
- [ ] Storage key validation
- [ ] Error message sanitization

### 3. Permission Management
- [ ] Minimal required permissions
- [ ] Optional permissions requested on-demand
- [ ] Permission changes logged
- [ ] User consent for sensitive permissions

### 4. Data Protection
- [ ] Encryption for sensitive data
- [ ] Secure key management
- [ ] Rate limiting for sensitive operations
- [ ] Data minimization practices

### 5. Error Handling
- [ ] No sensitive data in error messages
- [ ] Secure error reporting
- [ ] User consent for error transmission
- [ ] Local error logging limits

This security implementation ensures Mozilla policy compliance while maintaining user privacy and system security.