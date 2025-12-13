# EQ12 Extension Debugging Guide
## Based on Mozilla Extension Workshop Standards

This comprehensive debugging guide implements the best practices from Mozilla's Extension Workshop documentation, specifically:
- https://extensionworkshop.com/documentation/develop/debugging/
- https://extensionworkshop.com/documentation/develop/
- https://extensionworkshop.com/extension-basics/

## Table of Contents

1. [Quick Start Debugging](#quick-start-debugging)
2. [Developer Tools Setup](#developer-tools-setup)
3. [Component-Specific Debugging](#component-specific-debugging)
4. [Debug Utilities Reference](#debug-utilities-reference)
5. [Troubleshooting Common Issues](#troubleshooting-common-issues)
6. [Performance Monitoring](#performance-monitoring)
7. [Error Tracking and Reporting](#error-tracking-and-reporting)

## Quick Start Debugging

### 1. Load Extension in Firefox
```bash
# Open Firefox and navigate to:
about:debugging

# Click "This Firefox" in left menu
# Click "Load Temporary Add-on"
# Select manifest.json from example_extension folder
```

### 2. Access Developer Tools
```bash
# Method 1: From about:debugging
# Click "Inspect" next to your extension

# Method 2: Direct access
# Press F12 on any webpage (for content scripts)
# Open about:debugging > Inspect (for background/popup)
```

### 3. Open Debug Test Page
Open `example_extension/debug-test-page.html` in Firefox to verify extension functionality.

## Developer Tools Setup

### Toolbox Configuration
The EQ12 extension uses Firefox's Toolbox for debugging. Key tools available:

- **Console**: View logs, errors, and execute JavaScript
- **Debugger**: Set breakpoints and inspect code
- **Inspector**: Examine HTML/CSS (for popup, options pages)
- **Storage**: Inspect extension storage data

### Split Console Mode
Enable split console for simultaneous debugging:
```bash
# Press Esc in any developer tools tab
# Console appears at bottom of current tool
```

### Disable Popup Auto-Hide
For popup debugging:
```bash
# In about:debugging > Inspect > Options menu
# Click "Disable Popup Auto-Hide"
# Or set ui.popup.disable_autohide = true in about:config
```

## Component-Specific Debugging

### Background Script Debugging

**Location**: `example_extension/background.js`

**Features**:
- Structured logging with EQ12Debug.logger
- Performance timing for all operations
- Error tracking and storage
- Health checks every 60 seconds

**Debug Commands**:
```javascript
// In background script console:
EQ12Debug.logger.info('Test', 'Manual test message');
EQ12Debug.performance.startTimer('test_operation');
EQ12Debug.performance.endTimer('test_operation');

// View stored errors
api.storage.local.get(['background_errors'], console.log);
```

**Common Issues**:
- Check Console for `[EQ12][Background]` messages
- Verify extension permissions in manifest.json
- Monitor health check messages (every 60 seconds)

### Content Script Debugging

**Location**: `example_extension/content.js`

**Features**:
- Message passing with timeout handling
- Debug modal overlay on pages
- Performance monitoring
- Cross-frame communication

**Debug Commands**:
```javascript
// In webpage console (F12):
EQ12Debug.logger.info('Content', 'Test from page');
EQ12Analyzer.showGovernanceReport();

// Show debug modal
EQ12Debug.messaging.sendMessage({
  action: 'show_debug_info'
});

// Inspect analyzer state
console.log('Analyzer:', EQ12Analyzer);
```

**Content Script Visibility**:
```bash
# In webpage F12 > Debugger > Sources
# Click gear icon > "Show content scripts"
# Navigate to moz-extension://[uuid]/content.js
```

### Popup Debugging

**Location**: `example_extension/popup.js`

**Features**:
- Built-in debug panel (when debug mode enabled)
- Error message display in popup UI
- Configuration state monitoring
- Debug window for detailed info

**Debug Commands**:
```javascript
// In popup console (about:debugging > Inspect):
popupController.showDebugInfo();
EQ12Debug.logger.info('Popup', 'Test message');

// Toggle debug panel
document.getElementById('debugPanel').style.display = 'block';
```

**Popup-Specific Issues**:
- Disable auto-hide: about:debugging > Options > Disable Popup Auto-Hide
- Check popup dimensions: EQ12Debug logs size on load
- Verify DOM elements exist before interaction

### Storage Debugging

**Browser Storage Inspector**:
```bash
# In about:debugging > Inspect > Storage tab
# Navigate to "Extension Storage"
# View/modify all stored extension data
```

**Programmatic Access**:
```javascript
// Test storage operations
EQ12Debug.storage.inspect();     // View all data
EQ12Debug.storage.clear();       // Clear all data

// Background script storage
api.storage.sync.get(null, console.log);     // All sync data
api.storage.local.get(null, console.log);    // All local data
```

## Debug Utilities Reference

### EQ12Debug.logger
Centralized logging system with component-based filtering:

```javascript
EQ12Debug.logger.debug('Component', 'Debug message', optionalData);
EQ12Debug.logger.info('Component', 'Info message', optionalData);
EQ12Debug.logger.warn('Component', 'Warning message', optionalData);
EQ12Debug.logger.error('Component', 'Error message', errorObject);
```

### EQ12Debug.performance
Performance monitoring and timing:

```javascript
EQ12Debug.performance.startTimer('operation_name');
// ... perform operation ...
const duration = EQ12Debug.performance.endTimer('operation_name');
```

### EQ12Debug.errorTracker
Error collection and storage:

```javascript
// View collected errors
const errors = EQ12Debug.errorTracker.getErrors();

// Clear error history
EQ12Debug.errorTracker.clearErrors();

// Manually track error
EQ12Debug.errorTracker.trackError('Component', 'Description', errorObject);
```

### EQ12Debug.messaging
Enhanced message passing with debugging:

```javascript
// Content script to background
sendMessageWithDebug({
  action: 'get_governance_status'
}).then(response => {
  console.log('Response:', response);
});

// Check pending messages
console.log('Pending:', EQ12Debug.messaging.pendingMessages);
```

## Troubleshooting Common Issues

### Extension Not Loading
```bash
# Check manifest.json syntax
# Verify file paths in manifest
# Check browser console for manifest errors
# Ensure all referenced files exist
```

### Content Script Not Injecting
```bash
# Verify match patterns in manifest.json
# Check for CSP (Content Security Policy) blocking
# Ensure page is not a system page (chrome://, about:)
# Look for injection errors in background console
```

### Messages Not Passing
```bash
# Check both sender and receiver consoles
# Verify message format and action names
# Look for [EQ12][Messaging] debug logs
# Check for runtime.lastError in callbacks
```

### Storage Not Persisting
```bash
# Verify storage permissions in manifest.json
# Check for quota limitations
# Look for storage operation errors in console
# Test both sync and local storage
```

### Performance Issues
```bash
# Monitor EQ12Debug.performance timer logs
# Check memory usage in performance timers
# Look for long-running operations
# Verify efficient DOM manipulation
```

## Performance Monitoring

### Built-in Monitoring
The extension includes automatic performance monitoring:

```javascript
// All operations are timed automatically
// View active timers
console.log('Active timers:', Object.keys(EQ12Debug.performance.timers));

// Background script health checks
// Memory usage logged every 60 seconds (if available)
```

### Manual Performance Testing
```javascript
// Test message round-trip time
EQ12Debug.performance.startTimer('message_test');
sendMessageWithDebug({ action: 'debug_test' }).then(() => {
  EQ12Debug.performance.endTimer('message_test');
});

// Test analysis performance
EQ12Debug.performance.startTimer('analysis_test');
EQ12Analyzer.startAnalysis().then(() => {
  EQ12Debug.performance.endTimer('analysis_test');
});
```

## Error Tracking and Reporting

### Automatic Error Collection
Errors are automatically collected and stored:

- **Background errors**: Stored in `background_errors` local storage
- **Content errors**: Reported to background script for critical errors
- **Popup errors**: Displayed in UI and logged to console

### Viewing Errors
```javascript
// Background script errors
api.storage.local.get(['background_errors'], result => {
  console.log('Background errors:', result.background_errors);
});

// All tracked errors
console.log('EQ12 Errors:', EQ12Debug.errorTracker.getErrors());
```

### Error Reporting
```javascript
// Send error report (implement your reporting endpoint)
async function sendErrorReport() {
  const errors = EQ12Debug.errorTracker.getErrors();
  const report = {
    timestamp: new Date().toISOString(),
    version: chrome.runtime.getManifest().version,
    userAgent: navigator.userAgent,
    errors: errors
  };
  
  // Send to your error reporting service
  console.log('Error report:', report);
}
```

## Debug Configuration

### Configuration File
Location: `example_extension/debug-config.json`

```json
{
  "debug_level": "INFO",
  "enable_console_logs": true,
  "enable_error_tracking": true,
  "enable_performance_monitoring": true,
  "debug_components": {
    "background": true,
    "content_scripts": true,
    "popup": true,
    "options": true,
    "storage": true
  },
  "log_filters": {
    "exclude_patterns": ["webpack", "hot-reload"],
    "include_patterns": ["EQ12", "governance"]
  }
}
```

### Runtime Configuration
```javascript
// Enable/disable debug mode
EQ12Debug.config.enableConsoleLogging = false;
EQ12Debug.config.enableErrorTracking = true;

// Component-specific debugging
EQ12Debug.messaging.debugMode = true;
```

## Testing Procedures

### 1. Basic Functionality Test
```bash
# Load extension in Firefox
# Open debug test page
# Click "Test Extension Presence" - should show green checkmark
# Click "Test Storage Operations" - should show success
# Click "Test Background Communication" - should show response
```

### 2. Error Handling Test
```bash
# Click "Trigger Test Error" in debug test page
# Verify error appears in console with [EQ12] prefix
# Check that error is stored: EQ12Debug.errorTracker.getErrors()
```

### 3. Performance Test
```bash
# Monitor console for performance timing logs
# All major operations should show [Performance] logs
# Background health checks should appear every 60 seconds
```

### 4. Cross-Browser Test
```bash
# Test in Firefox, Chrome, Edge (if supported)
# Verify polyfill handles browser differences
# Check console for browser-specific warnings
```

## Advanced Debugging

### Remote Debugging
```bash
# For mobile Firefox debugging:
# Enable remote debugging in Firefox mobile
# Connect via USB/WiFi debugging tools
# Use desktop Firefox developer tools
```

### Extension Debugging with VS Code
```bash
# Install "Debugger for Firefox" VS Code extension
# Configure launch.json for extension debugging
# Set breakpoints in VS Code
# Debug directly from IDE
```

### Network Monitoring
```javascript
// Monitor extension network requests
// Check for CORS issues with content scripts
// Verify API calls from background script
// Monitor CSP compliance
```

## Best Practices Summary

1. **Always use structured logging** with component names
2. **Time all operations** for performance monitoring
3. **Handle errors gracefully** with user-friendly messages
4. **Test in multiple browsers** for compatibility
5. **Use split console mode** for efficient debugging
6. **Disable popup auto-hide** when debugging popups
7. **Monitor storage usage** and quota limits
8. **Test message passing** thoroughly between components
9. **Verify permissions** are correctly configured
10. **Use debug test page** for comprehensive testing

## Additional Resources

- [Mozilla Extension Workshop - Debugging](https://extensionworkshop.com/documentation/develop/debugging/)
- [MDN WebExtensions API](https://developer.mozilla.org/docs/Mozilla/Add-ons/WebExtensions)
- [Firefox Developer Tools](https://developer.mozilla.org/docs/Tools)
- [EQ12 Extension Debug Manager](scripts/eq12_extension_debug_manager.py)

---

**Generated by EQ12 Extension Debug Framework**  
*Following Mozilla Extension Workshop best practices*