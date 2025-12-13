
// Chrome Manifest V3 Service Worker
// EQ12 Cross-Browser Background Script with Enhanced Debugging
// Uses polyfill for chrome.* vs chrome.* compatibility
// Implements Mozilla Extension Workshop debugging best practices

// Initialize debug utilities first
if (typeof EQ12Debug === 'undefined') {
  // Fallback debug system if main debug utils not loaded
  window.EQ12Debug = {
    logger: {
      debug: (component, message, data) => console.debug(`[EQ12][${component}][DEBUG]`, message, data || ''),
      info: (component, message, data) => console.info(`[EQ12][${component}][INFO]`, message, data || ''),
      warn: (component, message, data) => console.warn(`[EQ12][${component}][WARN]`, message, data || ''),
      error: (component, message, error) => console.error(`[EQ12][${component}][ERROR]`, message, error || '')
    },
    performance: {
      timers: {},
      startTimer: function(label) { this.timers[label] = performance.now(); },
      endTimer: function(label) {
        if (this.timers[label]) {
          const duration = performance.now() - this.timers[label];
          console.info(`[EQ12][Performance] ${label}: ${duration.toFixed(2)}ms`);
          delete this.timers[label];
          return duration;
        }
        return null;
      }
    }
  };
}

EQ12Debug.logger.info('Background', 'EQ12 Extension background script loading...');
EQ12Debug.performance.startTimer('background_initialization');

// Unified browser API (from polyfill)
const api = typeof browser !== 'undefined' ? browser : chrome;

// Enhanced error handling for background script
function handleBackgroundError(error, context = 'unknown') {
  EQ12Debug.logger.error('Background', `Error in ${context}`, {
    message: error.message,
    stack: error.stack,
    timestamp: new Date().toISOString()
  });
  
  // Store error for debugging
  if (api && api.storage) {
    api.storage.local.get(['background_errors'], (result) => {
      const errors = result.background_errors || [];
      errors.push({
        context,
        error: error.message,
        timestamp: new Date().toISOString(),
        stack: error.stack
      });
      
      // Keep only last 50 errors
      if (errors.length > 50) {
        errors.splice(0, errors.length - 50);
      }
      
      api.storage.local.set({ background_errors: errors });
    });
  }
}

// Wrap all async operations in try-catch
async function safeAsyncOperation(operation, context) {
  try {
    EQ12Debug.performance.startTimer(context);
    const result = await operation();
    EQ12Debug.performance.endTimer(context);
    return result;
  } catch (error) {
    handleBackgroundError(error, context);
    throw error;
  }
}

// Handle extension installation with enhanced debugging
api.runtime.onInstalled.addListener(async (details) => {
  try {
    EQ12Debug.logger.info('Background', 'Extension installed/updated', {
      reason: details.reason,
      version: details.previousVersion || 'new',
      timestamp: new Date().toISOString()
    });
    
    // Initialize default storage values with debugging
    const defaultConfig = {
      eq12_enabled: true,
      governance_mode: 'standard',
      debug_mode: true,
      installation_timestamp: new Date().toISOString(),
      installation_reason: details.reason
    };
    
    await safeAsyncOperation(async () => {
      return new Promise((resolve, reject) => {
        api.storage.sync.set(defaultConfig, () => {
          if (api.runtime.lastError) {
            reject(new Error(api.runtime.lastError.message));
          } else {
            EQ12Debug.logger.info('Background', 'Default configuration stored', defaultConfig);
            resolve();
          }
        });
      });
    }, 'installation_setup');
    
    // Create debug badges for easy identification
    if (api.browserAction && api.browserAction.setBadgeText) {
      api.browserAction.setBadgeText({ text: 'DBG' });
      api.browserAction.setBadgeBackgroundColor({ color: '#007cba' });
    }
    
    EQ12Debug.logger.info('Background', 'Installation setup completed successfully');
    
  } catch (error) {
    handleBackgroundError(error, 'installation');
  }
});

// Handle browser action clicks with enhanced debugging
if (api.browserAction && api.browserAction.onClicked) {
  api.browserAction.onClicked.addListener(async (tab) => {
    try {
      EQ12Debug.logger.info('Background', 'Browser action clicked', {
        tabId: tab.id,
        url: tab.url,
        title: tab.title,
        timestamp: new Date().toISOString()
      });
      
      // Validate tab before injection
      if (!tab.url || tab.url.startsWith('chrome://') || tab.url.startsWith('about:') || tab.url.startsWith('moz-extension://')) {
        EQ12Debug.logger.warn('Background', 'Cannot inject script into system page', { url: tab.url });
        return;
      }
      
      // Inject content script with error handling
      await safeAsyncOperation(async () => {
        return new Promise((resolve, reject) => {
          api.tabs.executeScript(tab.id, { file: 'content.js' }, (result) => {
            if (api.runtime.lastError) {
              reject(new Error(api.runtime.lastError.message));
            } else {
              EQ12Debug.logger.debug('Background', 'Content script injected successfully', { 
                tabId: tab.id,
                result: result 
              });
              resolve(result);
            }
          });
        });
      }, 'content_script_injection');
      
    } catch (error) {
      handleBackgroundError(error, 'browser_action_click');
      
      // Show user-friendly notification on error
      if (api.notifications) {
        api.notifications.create({
          type: 'basic',
          iconUrl: 'icon-48.png',
          title: 'EQ12 Extension',
          message: 'Failed to activate on this page. Check console for details.'
        });
      }
    }
  });
}

// Enhanced message handling for content scripts with debugging
api.runtime.onMessage.addListener((request, sender, sendResponse) => {
  try {
    EQ12Debug.logger.debug('Background', 'Message received', {
      action: request.action,
      sender: {
        tab: sender.tab ? { id: sender.tab.id, url: sender.tab.url } : null,
        frameId: sender.frameId,
        origin: sender.origin
      },
      timestamp: new Date().toISOString()
    });
    
    // Validate message structure
    if (!request || typeof request.action !== 'string') {
      EQ12Debug.logger.warn('Background', 'Invalid message format', request);
      sendResponse({ error: 'Invalid message format' });
      return false;
    }
    
    EQ12Debug.performance.startTimer(`message_${request.action}`);
    
    switch (request.action) {
      case 'get_governance_status':
        safeAsyncOperation(async () => {
          return new Promise((resolve, reject) => {
            api.storage.sync.get(['eq12_enabled', 'governance_mode', 'debug_mode'], (result) => {
              if (api.runtime.lastError) {
                reject(new Error(api.runtime.lastError.message));
              } else {
                const response = {
                  enabled: result.eq12_enabled || false,
                  mode: result.governance_mode || 'standard',
                  debug: result.debug_mode || false,
                  timestamp: new Date().toISOString()
                };
                
                EQ12Debug.logger.debug('Background', 'Governance status retrieved', response);
                EQ12Debug.performance.endTimer(`message_${request.action}`);
                sendResponse(response);
                resolve(response);
              }
            });
          });
        }, 'get_governance_status').catch(error => {
          handleBackgroundError(error, 'get_governance_status');
          sendResponse({ error: error.message });
        });
        return true; // Async response
        
      case 'update_governance_config':
        if (!request.config || typeof request.config !== 'object') {
          EQ12Debug.logger.warn('Background', 'Invalid config in update request', request);
          sendResponse({ error: 'Invalid configuration data' });
          return false;
        }
        
        safeAsyncOperation(async () => {
          return new Promise((resolve, reject) => {
            // Add timestamp to config
            const configWithTimestamp = {
              ...request.config,
              last_updated: new Date().toISOString()
            };
            
            api.storage.sync.set(configWithTimestamp, () => {
              if (api.runtime.lastError) {
                reject(new Error(api.runtime.lastError.message));
              } else {
                EQ12Debug.logger.info('Background', 'Configuration updated', configWithTimestamp);
                EQ12Debug.performance.endTimer(`message_${request.action}`);
                sendResponse({ success: true, timestamp: configWithTimestamp.last_updated });
                resolve();
              }
            });
          });
        }, 'update_governance_config').catch(error => {
          handleBackgroundError(error, 'update_governance_config');
          sendResponse({ error: error.message });
        });
        return true;
        
      case 'debug_test':
        // Special debug message handler
        EQ12Debug.logger.info('Background', 'Debug test message received', request.data);
        sendResponse({ 
          success: true, 
          message: 'Debug test successful',
          background_active: true,
          timestamp: new Date().toISOString()
        });
        EQ12Debug.performance.endTimer(`message_${request.action}`);
        return false;
        
      case 'get_debug_errors':
        // Return stored debug errors
        safeAsyncOperation(async () => {
          return new Promise((resolve, reject) => {
            api.storage.local.get(['background_errors'], (result) => {
              if (api.runtime.lastError) {
                reject(new Error(api.runtime.lastError.message));
              } else {
                const errors = result.background_errors || [];
                EQ12Debug.logger.debug('Background', `Returning ${errors.length} debug errors`);
                EQ12Debug.performance.endTimer(`message_${request.action}`);
                sendResponse({ errors });
                resolve();
              }
            });
          });
        }, 'get_debug_errors').catch(error => {
          handleBackgroundError(error, 'get_debug_errors');
          sendResponse({ error: error.message });
        });
        return true;
        
      default:
        EQ12Debug.logger.warn('Background', 'Unknown action requested', { action: request.action });
        EQ12Debug.performance.endTimer(`message_${request.action}`);
        sendResponse({ error: `Unknown action: ${request.action}` });
        return false;
    }
    
  } catch (error) {
    handleBackgroundError(error, 'message_handling');
    sendResponse({ error: 'Internal error processing message' });
    return false;
  }
});

// Cross-browser context menu support with enhanced debugging
if (api.contextMenus) {
  try {
    // Create debug-enabled context menu
    api.contextMenus.create({
      id: 'eq12_analyze',
      title: 'EQ12: Analyze Page',
      contexts: ['page']
    });
    
    // Add debug context menu
    api.contextMenus.create({
      id: 'eq12_debug',
      title: 'EQ12: Debug Info',
      contexts: ['page']
    });
    
    EQ12Debug.logger.info('Background', 'Context menus created successfully');
    
  } catch (error) {
    handleBackgroundError(error, 'context_menu_creation');
  }
  
  api.contextMenus.onClicked.addListener(async (info, tab) => {
    try {
      EQ12Debug.logger.debug('Background', 'Context menu clicked', {
        menuItemId: info.menuItemId,
        tabId: tab.id,
        url: tab.url
      });
      
      switch (info.menuItemId) {
        case 'eq12_analyze':
          await safeAsyncOperation(async () => {
            return new Promise((resolve, reject) => {
              api.tabs.sendMessage(tab.id, {
                action: 'analyze_page',
                url: tab.url,
                timestamp: new Date().toISOString()
              }, (response) => {
                if (api.runtime.lastError) {
                  reject(new Error(api.runtime.lastError.message));
                } else {
                  EQ12Debug.logger.debug('Background', 'Page analysis message sent', response);
                  resolve(response);
                }
              });
            });
          }, 'context_menu_analyze');
          break;
          
        case 'eq12_debug':
          // Show debug information
          await safeAsyncOperation(async () => {
            return new Promise((resolve, reject) => {
              api.tabs.sendMessage(tab.id, {
                action: 'show_debug_info',
                debug: true,
                timestamp: new Date().toISOString()
              }, (response) => {
                if (api.runtime.lastError) {
                  EQ12Debug.logger.warn('Background', 'Debug info message failed - content script may not be loaded');
                  // Try to inject content script first
                  api.tabs.executeScript(tab.id, { file: 'content.js' }, () => {
                    if (!api.runtime.lastError) {
                      // Retry message after injection
                      setTimeout(() => {
                        api.tabs.sendMessage(tab.id, {
                          action: 'show_debug_info',
                          debug: true,
                          timestamp: new Date().toISOString()
                        });
                      }, 100);
                    }
                  });
                  resolve();
                } else {
                  EQ12Debug.logger.debug('Background', 'Debug info message sent', response);
                  resolve(response);
                }
              });
            });
          }, 'context_menu_debug');
          break;
      }
      
    } catch (error) {
      handleBackgroundError(error, 'context_menu_click');
    }
  });
}

// Finalize background script initialization
EQ12Debug.performance.endTimer('background_initialization');
EQ12Debug.logger.info('Background', 'EQ12 Extension background script fully loaded and ready');

// Periodic debug health check
setInterval(() => {
  try {
    EQ12Debug.logger.debug('Background', 'Health check - Background script active', {
      timestamp: new Date().toISOString(),
      memoryUsage: performance.memory ? {
        used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024) + ' MB',
        total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024) + ' MB'
      } : 'not available'
    });
  } catch (error) {
    // Ignore health check errors
  }
}, 60000); // Every minute

// Service worker event listeners
self.addEventListener('install', (event) => {
    console.log('EQ12 Extension Service Worker installed');
});

self.addEventListener('activate', (event) => {
    console.log('EQ12 Extension Service Worker activated');
});
