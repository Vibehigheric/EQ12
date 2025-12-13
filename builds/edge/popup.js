// EQ12 Cross-Browser Extension Popup Logic with Enhanced Debugging
// Implements Mozilla Extension Workshop popup debugging best practices

// Initialize debug utilities for popup context
if (typeof EQ12Debug === 'undefined') {
  // Fallback debug system for popup
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

EQ12Debug.logger.info('Popup', 'EQ12 Extension popup initializing', {
  timestamp: new Date().toISOString(),
  dimensions: {
    width: window.innerWidth,
    height: window.innerHeight
  }
});

EQ12Debug.performance.startTimer('popup_initialization');

// Unified browser API (from polyfill)
const api = typeof browser !== 'undefined' ? browser : chrome;

// Enhanced error handling for popup
function handlePopupError(error, context = 'unknown') {
  EQ12Debug.logger.error('Popup', `Error in ${context}`, {
    message: error.message,
    stack: error.stack,
    timestamp: new Date().toISOString()
  });
  
  // Show user-friendly error in popup
  showErrorMessage(`Error: ${error.message}`);
}

// Show error messages in popup UI
function showErrorMessage(message) {
  let errorDiv = document.getElementById('error-message');
  if (!errorDiv) {
    errorDiv = document.createElement('div');
    errorDiv.id = 'error-message';
    errorDiv.style.cssText = `
      background: #dc3545;
      color: white;
      padding: 10px;
      border-radius: 4px;
      margin: 10px 0;
      font-size: 12px;
    `;
    document.body.insertBefore(errorDiv, document.body.firstChild);
  }
  
  errorDiv.textContent = message;
  errorDiv.style.display = 'block';
  
  // Auto-hide after 5 seconds
  setTimeout(() => {
    if (errorDiv) {
      errorDiv.style.display = 'none';
    }
  }, 5000);
}

// Enhanced message sending for popup
function sendMessageWithDebug(message, timeout = 3000) {
  return new Promise((resolve, reject) => {
    const startTime = performance.now();
    
    EQ12Debug.logger.debug('Popup', 'Sending message to background', message);
    
    const timeoutId = setTimeout(() => {
      EQ12Debug.logger.warn('Popup', 'Message timeout', { message, timeout });
      reject(new Error(`Message timeout: ${message.action}`));
    }, timeout);
    
    try {
      api.runtime.sendMessage(message, (response) => {
        clearTimeout(timeoutId);
        const duration = performance.now() - startTime;
        
        if (api.runtime.lastError) {
          EQ12Debug.logger.error('Popup', 'Message failed', {
            error: api.runtime.lastError.message,
            duration: `${duration.toFixed(2)}ms`
          });
          reject(new Error(api.runtime.lastError.message));
        } else {
          EQ12Debug.logger.debug('Popup', 'Message response received', {
            response,
            duration: `${duration.toFixed(2)}ms`
          });
          resolve(response);
        }
      });
    } catch (error) {
      clearTimeout(timeoutId);
      EQ12Debug.logger.error('Popup', 'Message send failed', error);
      reject(error);
    }
  });
}

class EQ12PopupController {
  constructor() {
    try {
      EQ12Debug.logger.info('Popup', 'EQ12PopupController initializing');
      EQ12Debug.performance.startTimer('popup_controller_init');
      
      this.config = {
        eq12_enabled: false,
        governance_mode: 'standard',
        debug_mode: false
      };
      
      this.elements = {};
      this.debugMode = false;
      this.errors = [];
      
      this.initElements();
      this.init();
      
    } catch (error) {
      handlePopupError(error, 'constructor');
    }
  }
  
  initElements() {
    try {
      // Store references to DOM elements with error checking
      const elementIds = [
        'statusDot', 'statusText', 'modeSelect', 'toggleBtn',
        'analyzeBtn', 'reportBtn', 'lastAnalysis', 'analysisResults'
      ];
      
      elementIds.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
          this.elements[id] = element;
          EQ12Debug.logger.debug('Popup', `Element found: ${id}`);
        } else {
          EQ12Debug.logger.warn('Popup', `Element not found: ${id}`);
        }
      });
      
      // Add debug panel container if not exists
      if (!document.getElementById('debugPanel')) {
        this.createDebugPanel();
      }
      
      EQ12Debug.logger.debug('Popup', 'Element initialization completed', {
        foundElements: Object.keys(this.elements).length,
        expectedElements: elementIds.length
      });
      
    } catch (error) {
      handlePopupError(error, 'element_initialization');
    }
  }
  
  createDebugPanel() {
    const debugPanel = document.createElement('div');
    debugPanel.id = 'debugPanel';
    debugPanel.style.cssText = `
      border-top: 1px solid #ddd;
      margin-top: 15px;
      padding-top: 10px;
      display: none;
    `;
    
    debugPanel.innerHTML = `
      <h4 style="margin: 0 0 10px 0; font-size: 12px; color: #666;">Debug Panel</h4>
      <div style="font-size: 11px; margin-bottom: 5px;">
        <button id="debugToggle" style="font-size: 10px; padding: 2px 6px;">Toggle Debug</button>
        <button id="debugClear" style="font-size: 10px; padding: 2px 6px;">Clear Errors</button>
        <button id="debugInfo" style="font-size: 10px; padding: 2px 6px;">Show Info</button>
      </div>
      <div id="debugOutput" style="background: #f8f9fa; padding: 5px; border-radius: 3px; font-size: 10px; max-height: 100px; overflow-y: auto; display: none;"></div>
    `;
    
    document.body.appendChild(debugPanel);
    
    // Add debug panel event listeners
    document.getElementById('debugToggle')?.addEventListener('click', () => this.toggleDebugOutput());
    document.getElementById('debugClear')?.addEventListener('click', () => this.clearDebugOutput());
    document.getElementById('debugInfo')?.addEventListener('click', () => this.showDebugInfo());
  }
  
  async init() {
    try {
      EQ12Debug.performance.startTimer('popup_load_config');
      await this.loadConfig();
      EQ12Debug.performance.endTimer('popup_load_config');
      
      this.setupEventListeners();
      this.updateUI();
      
      // Show debug panel if in debug mode
      if (this.config.debug_mode) {
        document.getElementById('debugPanel').style.display = 'block';
        this.debugMode = true;
      }
      
      EQ12Debug.performance.endTimer('popup_controller_init');
      EQ12Debug.logger.info('Popup', 'Popup controller initialized successfully');
      
    } catch (error) {
      handlePopupError(error, 'initialization');
    }
  }
  
  async loadConfig() {
    try {
      EQ12Debug.logger.debug('Popup', 'Loading configuration from storage');
      
      const result = await sendMessageWithDebug({
        action: 'get_governance_status'
      });
      
      this.config.eq12_enabled = result.enabled || false;
      this.config.governance_mode = result.mode || 'standard';
      this.config.debug_mode = result.debug || false;
      
      EQ12Debug.logger.info('Popup', 'Configuration loaded', this.config);
      
    } catch (error) {
      handlePopupError(error, 'load_config');
      
      // Fallback to direct storage access
      return new Promise((resolve) => {
        api.storage.sync.get(['eq12_enabled', 'governance_mode', 'debug_mode'], (result) => {
          this.config.eq12_enabled = result.eq12_enabled || false;
          this.config.governance_mode = result.governance_mode || 'standard';
          this.config.debug_mode = result.debug_mode || false;
          EQ12Debug.logger.warn('Popup', 'Used fallback config loading', this.config);
          resolve();
        });
      });
    }
  }
  
  async saveConfig() {
    try {
      EQ12Debug.logger.debug('Popup', 'Saving configuration', this.config);
      
      const response = await sendMessageWithDebug({
        action: 'update_governance_config',
        config: this.config
      });
      
      if (response.success) {
        EQ12Debug.logger.info('Popup', 'Configuration saved successfully');
        return true;
      } else {
        throw new Error('Failed to save configuration');
      }
      
    } catch (error) {
      handlePopupError(error, 'save_config');
      
      // Fallback to direct storage access
      return new Promise((resolve) => {
        api.storage.sync.set(this.config, () => {
          if (api.runtime.lastError) {
            EQ12Debug.logger.error('Popup', 'Fallback config save failed', api.runtime.lastError);
          } else {
            EQ12Debug.logger.warn('Popup', 'Used fallback config saving');
          }
          resolve();
        });
      });
    }
  }
  
  setupEventListeners() {
    // Toggle governance on/off
    this.elements.toggleBtn.addEventListener('click', async () => {
      this.config.eq12_enabled = !this.config.eq12_enabled;
      await this.saveConfig();
      this.updateUI();
      this.notifyContentScript();
    });
    
    // Mode selector
    this.elements.modeSelect.addEventListener('change', async () => {
      this.config.governance_mode = this.elements.modeSelect.value;
      await this.saveConfig();
      this.notifyContentScript();
    });
    
    // Analyze current page
    this.elements.analyzeBtn.addEventListener('click', () => {
      this.analyzeCurrentPage();
    });
    
    // Generate report
    this.elements.reportBtn.addEventListener('click', () => {
      this.generateReport();
    });
  }
  
  updateUI() {
    // Update status indicator
    if (this.config.eq12_enabled) {
      this.elements.statusDot.className = 'status-dot active';
      this.elements.statusText.textContent = 'Governance Active';
      this.elements.toggleBtn.textContent = 'Disable Governance';
      this.elements.toggleBtn.className = 'btn btn-warning';
    } else {
      this.elements.statusDot.className = 'status-dot inactive';
      this.elements.statusText.textContent = 'Governance Inactive';
      this.elements.toggleBtn.textContent = 'Enable Governance';
      this.elements.toggleBtn.className = 'btn btn-primary';
    }
    
    // Update mode selector
    this.elements.modeSelect.value = this.config.governance_mode;
    
    // Enable/disable controls based on status
    this.elements.analyzeBtn.disabled = !this.config.eq12_enabled;
    this.elements.reportBtn.disabled = !this.config.eq12_enabled;
  }
  
  notifyContentScript() {
    // Notify all tabs of config changes
    api.tabs.query({}, (tabs) => {
      tabs.forEach((tab) => {
        api.tabs.sendMessage(tab.id, {
          action: 'config_updated',
          config: this.config
        }, () => {
          // Ignore errors for tabs without content script
          if (api.runtime.lastError) {
            console.log('Content script not available on tab:', tab.id);
          }
        });
      });
    });
  }
  
  analyzeCurrentPage() {
    api.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        api.tabs.sendMessage(tabs[0].id, {
          action: 'analyze_page',
          url: tabs[0].url
        }, (response) => {
          if (api.runtime.lastError) {
            console.error('Analysis failed:', api.runtime.lastError);
            this.showAnalysisResults({
              error: 'Could not analyze page. Content script may not be loaded.'
            });
          } else {
            console.log('Analysis completed:', response);
            this.showAnalysisResults({
              success: true,
              url: tabs[0].url,
              timestamp: new Date().toLocaleString()
            });
          }
        });
      }
    });
  }
  
  generateReport() {
    // Generate comprehensive governance report
    const report = {
      timestamp: new Date().toISOString(),
      config: this.config,
      browser: this.detectBrowser(),
      version: '1.0.0'
    };
    
    // Get current tab info
    api.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        report.current_page = {
          url: tabs[0].url,
          title: tabs[0].title,
          protocol: new URL(tabs[0].url).protocol
        };
      }
      
      // Download report as JSON
      this.downloadReport(report);
    });
  }
  
  showAnalysisResults(results) {
    this.elements.lastAnalysis.style.display = 'block';
    
    if (results.error) {
      this.elements.analysisResults.innerHTML = `
        <div style="color: #dc3545;">
          Error: ${results.error}
        </div>
      `;
    } else {
      this.elements.analysisResults.innerHTML = `
        <div style="color: #28a745;">
          ✓ Analysis completed
        </div>
        <div style="font-size: 12px; margin-top: 5px;">
          ${results.url}<br>
          ${results.timestamp}
        </div>
      `;
    }
  }
  
  detectBrowser() {
    const userAgent = navigator.userAgent;
    
    if (userAgent.includes('Firefox')) {
      return 'Firefox';
    } else if (userAgent.includes('Edg/')) {
      return 'Edge';
    } else if (userAgent.includes('Chrome')) {
      return 'Chrome';
    } else if (userAgent.includes('Safari') && !userAgent.includes('Chrome')) {
      return 'Safari';
    } else {
      return 'Unknown';
    }
  }
  
  downloadReport(report) {
    try {
      EQ12Debug.logger.debug('Popup', 'Downloading report', { reportSize: JSON.stringify(report).length });
      
      const blob = new Blob([JSON.stringify(report, null, 2)], {
        type: 'application/json'
      });
      
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `eq12-governance-report-${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);
      
      EQ12Debug.logger.info('Popup', 'Report download initiated');
      
    } catch (error) {
      handlePopupError(error, 'download_report');
    }
  }
  
  // Debug panel methods
  toggleDebugOutput() {
    const debugOutput = document.getElementById('debugOutput');
    if (debugOutput) {
      debugOutput.style.display = debugOutput.style.display === 'none' ? 'block' : 'none';
      if (debugOutput.style.display === 'block') {
        this.updateDebugOutput();
      }
    }
  }
  
  clearDebugOutput() {
    const debugOutput = document.getElementById('debugOutput');
    if (debugOutput) {
      debugOutput.innerHTML = '';
    }
    this.errors = [];
    EQ12Debug.logger.info('Popup', 'Debug output cleared');
  }
  
  updateDebugOutput() {
    const debugOutput = document.getElementById('debugOutput');
    if (!debugOutput) return;
    
    const debugInfo = {
      timestamp: new Date().toLocaleTimeString(),
      config: this.config,
      elements: Object.keys(this.elements).length + ' elements found',
      errors: this.errors.length + ' errors',
      performance: Object.keys(EQ12Debug.performance.timers).length + ' active timers'
    };
    
    debugOutput.innerHTML = `
      <div><strong>Last Update:</strong> ${debugInfo.timestamp}</div>
      <div><strong>Config:</strong> ${JSON.stringify(debugInfo.config)}</div>
      <div><strong>Elements:</strong> ${debugInfo.elements}</div>
      <div><strong>Errors:</strong> ${debugInfo.errors}</div>
      <div><strong>Performance:</strong> ${debugInfo.performance}</div>
    `;
  }
  
  async showDebugInfo() {
    try {
      // Get debug errors from background
      const response = await sendMessageWithDebug({
        action: 'get_debug_errors'
      });
      
      const debugWindow = window.open('', 'EQ12Debug', 'width=600,height=400');
      debugWindow.document.write(`
        <html>
        <head><title>EQ12 Extension Debug Info</title></head>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
          <h2>EQ12 Extension Debug Information</h2>
          <h3>Popup State</h3>
          <pre>${JSON.stringify(this.config, null, 2)}</pre>
          <h3>Background Errors</h3>
          <pre>${JSON.stringify(response.errors || [], null, 2)}</pre>
          <h3>Popup Errors</h3>
          <pre>${JSON.stringify(this.errors, null, 2)}</pre>
          <button onclick="window.close()">Close</button>
        </body>
        </html>
      `);
      
      EQ12Debug.logger.info('Popup', 'Debug info window opened');
      
    } catch (error) {
      handlePopupError(error, 'show_debug_info');
    }
  }
}

// Initialize popup when DOM is loaded with enhanced error handling
document.addEventListener('DOMContentLoaded', () => {
  try {
    EQ12Debug.logger.info('Popup', 'DOM loaded, initializing popup controller');
    
    // Log popup dimensions for debugging
    EQ12Debug.logger.debug('Popup', 'Popup dimensions', {
      width: window.innerWidth,
      height: window.innerHeight,
      devicePixelRatio: window.devicePixelRatio
    });
    
    // Initialize controller
    window.popupController = new EQ12PopupController();
    
    // Make debug utilities available in console
    window.EQ12Debug = EQ12Debug;
    
    EQ12Debug.performance.endTimer('popup_initialization');
    EQ12Debug.logger.info('Popup', 'Popup fully initialized and ready');
    
  } catch (error) {
    console.error('[EQ12][Popup][CRITICAL] Failed to initialize popup:', error);
    
    // Show critical error message
    document.body.innerHTML = `
      <div style="padding: 20px; background: #dc3545; color: white; text-align: center;">
        <h3>EQ12 Extension Error</h3>
        <p>Failed to initialize popup. Check console for details.</p>
        <button onclick="location.reload()">Retry</button>
      </div>
    `;
  }
});

// Popup auto-hide prevention helper (user must manually disable in about:debugging)
EQ12Debug.logger.info('Popup', 'To disable popup auto-hide for debugging: Open about:debugging > Inspect extension > Options menu > Disable Popup Auto-Hide');