// secure-error-handler.js - Secure error handling for EQ12 Governance Assistant
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
            
            // Implement secure HTTPS endpoint (placeholder - replace with actual endpoint)
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

// Initialize global security components
let permissionManager, secureErrorHandler;

// Security initialization function
async function initializeSecurity(privacyConsent) {
    permissionManager = new PermissionManager();
    secureErrorHandler = new SecureErrorHandler(privacyConsent);
    
    // Check required permissions
    const hasRequired = await permissionManager.checkRequiredPermissions();
    if (!hasRequired) {
        console.error('Missing required permissions');
    }
    
    return { permissionManager, secureErrorHandler };
}

// Secure error handling wrapper
function handleSecureError(error, context, sensitive = false) {
    if (secureErrorHandler) {
        secureErrorHandler.handleError(error, context, sensitive);
    } else {
        console.error('Security not initialized:', error);
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        SecureErrorHandler,
        PermissionManager,
        SecureCommunication,
        InputValidator,
        initializeSecurity,
        handleSecureError
    };
}