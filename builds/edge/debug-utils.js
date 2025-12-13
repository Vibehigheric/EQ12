
/**
 * EQ12 Extension Debug Utilities
 * Based on Mozilla Extension Workshop debugging guidelines
 */

// Debug namespace to avoid conflicts
const EQ12Debug = {
    config: {
        debugLevel: 'INFO',
        enableConsoleLogging: true,
        enableErrorTracking: true,
        componentPrefix: '[EQ12]'
    },
    
    // Centralized logging system
    logger: {
        debug: function(component, message, data = null) {
            if (EQ12Debug.config.enableConsoleLogging) {
                const prefix = `${EQ12Debug.config.componentPrefix}[${component}][DEBUG]`;
                console.debug(prefix, message, data || '');
            }
        },
        
        info: function(component, message, data = null) {
            if (EQ12Debug.config.enableConsoleLogging) {
                const prefix = `${EQ12Debug.config.componentPrefix}[${component}][INFO]`;
                console.info(prefix, message, data || '');
            }
        },
        
        warn: function(component, message, data = null) {
            if (EQ12Debug.config.enableConsoleLogging) {
                const prefix = `${EQ12Debug.config.componentPrefix}[${component}][WARN]`;
                console.warn(prefix, message, data || '');
            }
        },
        
        error: function(component, message, error = null) {
            if (EQ12Debug.config.enableConsoleLogging) {
                const prefix = `${EQ12Debug.config.componentPrefix}[${component}][ERROR]`;
                console.error(prefix, message, error || '');
                
                // Track errors for debugging
                if (EQ12Debug.config.enableErrorTracking) {
                    EQ12Debug.errorTracker.trackError(component, message, error);
                }
            }
        }
    },
    
    // Error tracking and reporting
    errorTracker: {
        errors: [],
        
        trackError: function(component, message, error) {
            const errorEntry = {
                timestamp: new Date().toISOString(),
                component: component,
                message: message,
                error: error ? {
                    name: error.name,
                    message: error.message,
                    stack: error.stack
                } : null,
                url: window.location ? window.location.href : 'unknown'
            };
            
            this.errors.push(errorEntry);
            
            // Keep only last 100 errors
            if (this.errors.length > 100) {
                this.errors = this.errors.slice(-100);
            }
            
            // Store in extension storage for debugging
            if (typeof browser !== 'undefined' && browser.storage) {
                browser.storage.local.set({
                    'eq12_debug_errors': this.errors
                }).catch(err => {
                    console.error('Failed to store debug errors:', err);
                });
            }
        },
        
        getErrors: function() {
            return this.errors;
        },
        
        clearErrors: function() {
            this.errors = [];
            if (typeof browser !== 'undefined' && browser.storage) {
                browser.storage.local.remove('eq12_debug_errors');
            }
        }
    },
    
    // Performance monitoring
    performance: {
        timers: {},
        
        startTimer: function(label) {
            this.timers[label] = performance.now();
            EQ12Debug.logger.debug('Performance', `Timer started: ${label}`);
        },
        
        endTimer: function(label) {
            if (this.timers[label]) {
                const duration = performance.now() - this.timers[label];
                EQ12Debug.logger.info('Performance', `Timer ${label}: ${duration.toFixed(2)}ms`);
                delete this.timers[label];
                return duration;
            }
            return null;
        }
    },
    
    // Storage debugging utilities
    storage: {
        inspect: async function() {
            if (typeof browser === 'undefined' || !browser.storage) {
                EQ12Debug.logger.warn('Storage', 'Storage API not available');
                return {};
            }
            
            try {
                const data = await browser.storage.local.get();
                EQ12Debug.logger.info('Storage', 'Current storage data:', data);
                return data;
            } catch (error) {
                EQ12Debug.logger.error('Storage', 'Failed to inspect storage', error);
                return {};
            }
        },
        
        clear: async function(keys = null) {
            if (typeof browser === 'undefined' || !browser.storage) {
                EQ12Debug.logger.warn('Storage', 'Storage API not available');
                return false;
            }
            
            try {
                if (keys) {
                    await browser.storage.local.remove(keys);
                    EQ12Debug.logger.info('Storage', 'Cleared keys:', keys);
                } else {
                    await browser.storage.local.clear();
                    EQ12Debug.logger.info('Storage', 'Cleared all storage data');
                }
                return true;
            } catch (error) {
                EQ12Debug.logger.error('Storage', 'Failed to clear storage', error);
                return false;
            }
        }
    },
    
    // Message debugging for content scripts
    messaging: {
        debugMode: true,
        
        sendMessage: function(message, responseCallback) {
            if (this.debugMode) {
                EQ12Debug.logger.debug('Messaging', 'Sending message:', message);
            }
            
            if (typeof browser !== 'undefined' && browser.runtime) {
                browser.runtime.sendMessage(message).then(response => {
                    if (this.debugMode) {
                        EQ12Debug.logger.debug('Messaging', 'Received response:', response);
                    }
                    if (responseCallback) responseCallback(response);
                }).catch(error => {
                    EQ12Debug.logger.error('Messaging', 'Message failed', error);
                });
            }
        }
    },
    
    // Popup debugging utilities
    popup: {
        disableAutoHide: function() {
            // Note: This is handled by Firefox developer tools
            // Users need to manually disable in about:debugging
            EQ12Debug.logger.info('Popup', 'To disable auto-hide: Open about:debugging > Inspect > Options menu > Disable Popup Auto-Hide');
        },
        
        logDimensions: function() {
            if (document.body) {
                const rect = document.body.getBoundingClientRect();
                EQ12Debug.logger.info('Popup', `Dimensions: ${rect.width}x${rect.height}`);
            }
        }
    },
    
    // Initialize debug system
    init: function() {
        EQ12Debug.logger.info('Debug', 'EQ12 Debug utilities initialized');
        
        // Global error handler
        if (typeof window !== 'undefined') {
            window.addEventListener('error', function(event) {
                EQ12Debug.logger.error('Global', 'Uncaught error', {
                    message: event.message,
                    filename: event.filename,
                    lineno: event.lineno,
                    colno: event.colno,
                    error: event.error
                });
            });
            
            // Promise rejection handler
            window.addEventListener('unhandledrejection', function(event) {
                EQ12Debug.logger.error('Global', 'Unhandled promise rejection', event.reason);
            });
        }
        
        // Make debug utilities globally available in development
        if (typeof window !== 'undefined') {
            window.EQ12Debug = EQ12Debug;
        }
    }
};

// Auto-initialize
EQ12Debug.init();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EQ12Debug;
}
