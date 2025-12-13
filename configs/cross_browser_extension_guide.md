# EQ12 Cross-Browser Extension Template

A production-ready template for building browser extensions compatible with Chrome, Firefox, Edge, and Safari.

## Browser Compatibility Matrix

Based on [Mozilla Extension Workshop](https://extensionworkshop.com/documentation/develop/browser-compatibility/) guidelines:

| Feature | Chrome | Firefox | Edge | Safari |
|---------|--------|---------|------|--------|
| **Manifest Version** | V3 | V2/V3 | V3 | V2 |
| **Namespace** | `chrome.*` | `browser.*` | `chrome.*` | `browser.*` |
| **Async Pattern** | Callbacks | Promises | Callbacks | Promises |
| **Background** | Service Worker | Scripts | Service Worker | Scripts |
| **Minimum Version** | 88+ | 91+ | 79+ | 14+ |

## Key Compatibility Differences

### 1. **Namespace Differences**
```javascript
// Chrome/Edge
chrome.browserAction.setIcon({path: "icon.png"});

// Firefox/Safari  
browser.browserAction.setIcon({path: "icon.png"});
```

### 2. **Asynchronous APIs**
```javascript
// Chrome (callbacks)
chrome.cookies.set({url: "https://example.com"}, function(cookie) {
  if (chrome.runtime.lastError) {
    console.error(chrome.runtime.lastError);
  } else {
    console.log(cookie);
  }
});

// Firefox (promises)
browser.cookies.set({url: "https://example.com"})
  .then(cookie => console.log(cookie))
  .catch(error => console.error(error));
```

### 3. **Manifest V3 vs V2 Differences**

**Chrome/Edge (Manifest V3):**
```json
{
  "manifest_version": 3,
  "background": {
    "service_worker": "background.js"
  },
  "action": {
    "default_popup": "popup.html"
  },
  "host_permissions": ["https://*/*"]
}
```

**Firefox/Safari (Manifest V2):**
```json
{
  "manifest_version": 2,
  "background": {
    "scripts": ["background.js"],
    "persistent": false
  },
  "browser_action": {
    "default_popup": "popup.html"
  },
  "permissions": ["https://*/*"]
}
```

## Usage

### Build for all browsers:
```bash
python scripts/eq12_cross_browser_extension_builder.py -s ./my_extension -o ./dist
```

### Build for specific browser:
```bash
python scripts/eq12_cross_browser_extension_builder.py -s ./my_extension -o ./dist -b chrome
```

## Cross-Browser Polyfill

The builder automatically includes a polyfill that:
- Unifies `chrome.*` and `browser.*` namespaces
- Promisifies Chrome callback APIs
- Provides compatibility layer for async patterns

```javascript
// Use browserAPI for unified access
browserAPI.tabs.queryAsync({active: true})
  .then(tabs => console.log(tabs))
  .catch(error => console.error(error));
```

## API Coverage Differences

### Supported Across All Browsers:
- ✅ Storage API
- ✅ Tabs API  
- ✅ Runtime API
- ✅ Browser Action/Action
- ✅ Content Scripts
- ✅ Background Scripts

### Firefox-Specific APIs:
- 🦊 `contextualIdentities` (containers)
- 🦊 `sessions` (advanced session management)
- 🦊 Enhanced `notifications` API

### Chrome-Specific APIs:
- 🟡 `enterprise.*` APIs
- 🟡 Advanced `declarativeContent`
- 🟡 `desktopCapture`

## Manifest Key Differences

| Key | Chrome | Firefox | Edge | Safari | Notes |
|-----|--------|---------|------|--------|--------|
| `developer` | ❌ | ✅ | ❌ | ❌ | Firefox/Opera only |
| `commands` | ✅ | ✅ | ❌ | ✅ | Edge has limited support |
| `applications` | ❌ | ✅ | ❌ | ❌ | Firefox-specific |
| `minimum_chrome_version` | ✅ | ❌ | ✅ | ❌ | Chrome/Edge only |

## Browser-Specific Behaviors

### URL Resolution in CSS:
- **Firefox**: Resolves relative to CSS file
- **Chrome/Edge**: Resolves relative to injected page

### Web Accessible Resources:
- **Firefox**: Uses random UUID
- **Chrome**: Can use fixed ID with `key` property

### Content Script Context:
- **Chrome/Edge**: `fetch("/api")` → `https://example.com/api`
- **Firefox**: Requires absolute URLs

## Development Recommendations

1. **Start with Firefox** - Most compliant with proposed standards
2. **Use WebExtension Polyfill** - `webextension-polyfill` library for compatibility
3. **Test Cross-Browser** - Different behaviors even with same APIs
4. **Manifest Strategy**:
   - Primary: Manifest V2 for broader compatibility
   - Chrome-specific: Manifest V3 for store requirements

## Testing Strategy

```bash
# Test in multiple browsers
web-ext run --target=chromium
web-ext run --target=firefox-desktop  
web-ext run --target=firefox-android

# Lint for compatibility
web-ext lint --source-dir=dist/firefox
```

## EQ12 Integration

This cross-browser builder integrates with EQ12's governance automation:
- Chrome: Corporate policy compliance
- Firefox: Privacy-focused browsing
- Edge: Enterprise integration
- Safari: iOS/macOS ecosystem

Built extensions can be deployed via EQ12's enterprise management system with browser-specific policies and configurations.

## References

- [Mozilla Extension Workshop - Browser Compatibility](https://extensionworkshop.com/documentation/develop/browser-compatibility/)
- [WebExtension Polyfill](https://github.com/mozilla/webextension-polyfill)
- [Chrome Extension Manifest V3](https://developer.chrome.com/docs/extensions/mv3/)
- [Firefox Extension APIs](https://developer.mozilla.org/docs/Mozilla/Add-ons/WebExtensions)