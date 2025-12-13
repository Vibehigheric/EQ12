
// EQ12 Cross-Browser Polyfill
// Based on Mozilla WebExtension Polyfill patterns

(function() {
    'use strict';
    
    // Detect browser environment
    const isFirefox = typeof browser !== 'undefined';
    const isChrome = typeof chrome !== 'undefined' && !isFirefox;
    
    // Create unified API object
    window.browserAPI = isFirefox ? browser : chrome;
    
    // Promise polyfill for Chrome callback APIs
    if (isChrome) {
        const promisifyAPI = (apiObj, methods) => {
            methods.forEach(method => {
                if (apiObj[method]) {
                    const originalMethod = apiObj[method];
                    apiObj[method + 'Async'] = (...args) => {
                        return new Promise((resolve, reject) => {
                            originalMethod(...args, (result) => {
                                if (chrome.runtime.lastError) {
                                    reject(chrome.runtime.lastError);
                                } else {
                                    resolve(result);
                                }
                            });
                        });
                    };
                }
            });
        };
        
        // Promisify common APIs
        if (chrome.tabs) {
            promisifyAPI(chrome.tabs, ['query', 'create', 'update', 'remove']);
        }
        if (chrome.storage && chrome.storage.sync) {
            promisifyAPI(chrome.storage.sync, ['get', 'set', 'remove']);
        }
        if (chrome.cookies) {
            promisifyAPI(chrome.cookies, ['get', 'set', 'remove']);
        }
    }
    
    console.log('EQ12 Cross-Browser Polyfill loaded for:', isFirefox ? 'Firefox' : 'Chrome');
})();
