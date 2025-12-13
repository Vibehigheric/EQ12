// EQ12 Cross-Browser Polyfill for WebExtension APIs
// Provides compatibility layer between Chrome extensions API and WebExtensions API

(() => {
  'use strict';

  // Only apply polyfill if browser API doesn't exist (i.e., we're in Chrome/Edge)
  if (typeof browser === 'undefined' && typeof chrome !== 'undefined') {
    // Create browser namespace based on Chrome API
    window.browser = {
      // Runtime API
      runtime: {
        getManifest: () => chrome.runtime.getManifest(),
        getURL: (path) => chrome.runtime.getURL(path),
        onMessage: chrome.runtime.onMessage,
        sendMessage: (extensionId, message, options, callback) => {
          if (typeof extensionId === 'object') {
            // Handle case where extensionId is actually the message
            callback = options;
            options = message;
            message = extensionId;
            extensionId = null;
          }
          return chrome.runtime.sendMessage(extensionId, message, options, callback);
        },
        lastError: chrome.runtime.lastError,
        onInstalled: chrome.runtime.onInstalled,
        onStartup: chrome.runtime.onStartup,
        id: chrome.runtime.id
      },

      // Storage API
      storage: {
        local: {
          get: (keys, callback) => chrome.storage.local.get(keys, callback),
          set: (items, callback) => chrome.storage.local.set(items, callback),
          remove: (keys, callback) => chrome.storage.local.remove(keys, callback),
          clear: (callback) => chrome.storage.local.clear(callback),
          onChanged: chrome.storage.onChanged
        },
        sync: {
          get: (keys, callback) => chrome.storage.sync.get(keys, callback),
          set: (items, callback) => chrome.storage.sync.set(items, callback),
          remove: (keys, callback) => chrome.storage.sync.remove(keys, callback),
          clear: (callback) => chrome.storage.sync.clear(callback)
        },
        onChanged: chrome.storage.onChanged
      },

      // Tabs API
      tabs: {
        query: (queryInfo, callback) => chrome.tabs.query(queryInfo, callback),
        get: (tabId, callback) => chrome.tabs.get(tabId, callback),
        create: (createProperties, callback) => chrome.tabs.create(createProperties, callback),
        update: (tabId, updateProperties, callback) => chrome.tabs.update(tabId, updateProperties, callback),
        remove: (tabIds, callback) => chrome.tabs.remove(tabIds, callback),
        sendMessage: (tabId, message, options, callback) => chrome.tabs.sendMessage(tabId, message, options, callback),
        executeScript: (tabId, details, callback) => chrome.tabs.executeScript(tabId, details, callback),
        insertCSS: (tabId, details, callback) => chrome.tabs.insertCSS(tabId, details, callback),
        onActivated: chrome.tabs.onActivated,
        onUpdated: chrome.tabs.onUpdated,
        onCreated: chrome.tabs.onCreated,
        onRemoved: chrome.tabs.onRemoved
      },

      // Context Menus API (if available)
      contextMenus: chrome.contextMenus ? {
        create: (createProperties, callback) => chrome.contextMenus.create(createProperties, callback),
        update: (id, updateProperties, callback) => chrome.contextMenus.update(id, updateProperties, callback),
        remove: (menuItemId, callback) => chrome.contextMenus.remove(menuItemId, callback),
        removeAll: (callback) => chrome.contextMenus.removeAll(callback),
        onClicked: chrome.contextMenus.onClicked
      } : undefined,

      // Notifications API (if available)
      notifications: chrome.notifications ? {
        create: (notificationId, options, callback) => chrome.notifications.create(notificationId, options, callback),
        update: (notificationId, options, callback) => chrome.notifications.update(notificationId, options, callback),
        clear: (notificationId, callback) => chrome.notifications.clear(notificationId, callback),
        getAll: (callback) => chrome.notifications.getAll(callback),
        onClicked: chrome.notifications.onClicked,
        onButtonClicked: chrome.notifications.onButtonClicked,
        onClosed: chrome.notifications.onClosed
      } : undefined,

      // Permissions API (if available)
      permissions: chrome.permissions ? {
        contains: (permissions, callback) => chrome.permissions.contains(permissions, callback),
        request: (permissions, callback) => chrome.permissions.request(permissions, callback),
        remove: (permissions, callback) => chrome.permissions.remove(permissions, callback),
        getAll: (callback) => chrome.permissions.getAll(callback),
        onAdded: chrome.permissions.onAdded,
        onRemoved: chrome.permissions.onRemoved
      } : undefined,

      // Browser Action API
      browserAction: chrome.browserAction ? {
        setTitle: (details, callback) => chrome.browserAction.setTitle(details, callback),
        getTitle: (details, callback) => chrome.browserAction.getTitle(details, callback),
        setIcon: (details, callback) => chrome.browserAction.setIcon(details, callback),
        setPopup: (details, callback) => chrome.browserAction.setPopup(details, callback),
        getPopup: (details, callback) => chrome.browserAction.getPopup(details, callback),
        setBadgeText: (details, callback) => chrome.browserAction.setBadgeText(details, callback),
        getBadgeText: (details, callback) => chrome.browserAction.getBadgeText(details, callback),
        setBadgeBackgroundColor: (details, callback) => chrome.browserAction.setBadgeBackgroundColor(details, callback),
        getBadgeBackgroundColor: (details, callback) => chrome.browserAction.getBadgeBackgroundColor(details, callback),
        onClicked: chrome.browserAction.onClicked
      } : undefined
    };

    console.log('[EQ12 Polyfill] Browser API polyfill loaded for Chrome/Edge compatibility');
  } else if (typeof browser !== 'undefined') {
    console.log('[EQ12 Polyfill] Native browser API detected (Firefox)');
  } else {
    console.warn('[EQ12 Polyfill] No WebExtension API available');
  }

  // Promise wrapper helper for Chrome callback-based APIs
  if (typeof browser !== 'undefined' && browser.runtime && !browser.runtime.sendMessage.then) {
    // Add Promise support to APIs that don't have it in Chrome
    const wrapWithPromise = (fn) => {
      return (...args) => {
        return new Promise((resolve, reject) => {
          fn(...args, (result) => {
            if (chrome.runtime.lastError) {
              reject(new Error(chrome.runtime.lastError.message));
            } else {
              resolve(result);
            }
          });
        });
      };
    };

    // Add Promise support to commonly used APIs
    if (browser.storage && browser.storage.local) {
      browser.storage.local.get = wrapWithPromise(browser.storage.local.get);
      browser.storage.local.set = wrapWithPromise(browser.storage.local.set);
    }
    
    if (browser.tabs) {
      browser.tabs.query = wrapWithPromise(browser.tabs.query);
      browser.tabs.sendMessage = wrapWithPromise(browser.tabs.sendMessage);
    }
  }
})();

// Global API reference for convenience
const api = typeof browser !== 'undefined' ? browser : chrome;

console.log('[EQ12 Polyfill] Cross-browser WebExtension API ready');