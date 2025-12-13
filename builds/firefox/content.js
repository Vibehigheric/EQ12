// EQ12 Cross-Browser Content Script with Enhanced Debugging
// Analyzes web pages for governance compliance
// Implements Mozilla Extension Workshop content script debugging best practices

// Initialize debug utilities for content script context
if (typeof EQ12Debug === 'undefined') {
  // Fallback debug system for content scripts
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
    },
    messaging: {
      debugMode: true,
      messageId: 0,
      pendingMessages: new Map()
    }
  };
}

EQ12Debug.logger.info('Content', 'EQ12 Content script loading', {
  url: window.location.href,
  title: document.title,
  timestamp: new Date().toISOString(),
  userAgent: navigator.userAgent
});

EQ12Debug.performance.startTimer('content_script_initialization');

// Unified browser API (from polyfill)
const api = typeof browser !== 'undefined' ? browser : chrome;

// Enhanced error handling for content script
function handleContentError(error, context = 'unknown') {
  EQ12Debug.logger.error('Content', `Error in ${context}`, {
    message: error.message,
    stack: error.stack,
    url: window.location.href,
    timestamp: new Date().toISOString()
  });
  
  // Report critical errors to background script
  if (context.includes('critical')) {
    try {
      api.runtime.sendMessage({
        action: 'report_content_error',
        error: {
          message: error.message,
          stack: error.stack,
          context,
          url: window.location.href,
          timestamp: new Date().toISOString()
        }
      });
    } catch (reportError) {
      EQ12Debug.logger.error('Content', 'Failed to report error to background', reportError);
    }
  }
}

// Enhanced message sending with debugging
function sendMessageWithDebug(message, timeout = 5000) {
  return new Promise((resolve, reject) => {
    const messageId = ++EQ12Debug.messaging.messageId;
    const startTime = performance.now();
    
    if (EQ12Debug.messaging.debugMode) {
      EQ12Debug.logger.debug('Content', `Sending message #${messageId}`, message);
    }
    
    // Track pending message
    EQ12Debug.messaging.pendingMessages.set(messageId, {
      message,
      startTime,
      timeout: setTimeout(() => {
        EQ12Debug.messaging.pendingMessages.delete(messageId);
        EQ12Debug.logger.warn('Content', `Message #${messageId} timed out`, message);
        reject(new Error(`Message timeout: ${message.action}`));
      }, timeout)
    });
    
    try {
      api.runtime.sendMessage(message, (response) => {
        const pendingMessage = EQ12Debug.messaging.pendingMessages.get(messageId);
        if (pendingMessage) {
          clearTimeout(pendingMessage.timeout);
          EQ12Debug.messaging.pendingMessages.delete(messageId);
          
          const duration = performance.now() - startTime;
          
          if (api.runtime.lastError) {
            EQ12Debug.logger.warn('Content', `Message #${messageId} failed`, {
              error: api.runtime.lastError.message,
              duration: `${duration.toFixed(2)}ms`
            });
            reject(new Error(api.runtime.lastError.message));
          } else {
            if (EQ12Debug.messaging.debugMode) {
              EQ12Debug.logger.debug('Content', `Message #${messageId} response received`, {
                response,
                duration: `${duration.toFixed(2)}ms`
              });
            }
            resolve(response);
          }
        }
      });
    } catch (error) {
      const pendingMessage = EQ12Debug.messaging.pendingMessages.get(messageId);
      if (pendingMessage) {
        clearTimeout(pendingMessage.timeout);
        EQ12Debug.messaging.pendingMessages.delete(messageId);
      }
      EQ12Debug.logger.error('Content', `Message #${messageId} send failed`, error);
      reject(error);
    }
  });
}

class EQ12GovernanceAnalyzer {
  constructor() {
    this.isEnabled = false;
    this.mode = 'standard';
    this.debugMode = false;
    this.analysisResults = {};
    this.errors = [];
    
    EQ12Debug.logger.info('Content', 'EQ12GovernanceAnalyzer initializing');
    this.init();
  }
  
  async init() {
    try {
      EQ12Debug.performance.startTimer('analyzer_initialization');
      
      // Get governance configuration with enhanced debugging
      const response = await sendMessageWithDebug({
        action: 'get_governance_status'
      });
      
      this.isEnabled = response.enabled || false;
      this.mode = response.mode || 'standard';
      this.debugMode = response.debug || false;
      
      EQ12Debug.logger.info('Content', 'Configuration received', {
        enabled: this.isEnabled,
        mode: this.mode,
        debug: this.debugMode
      });
      
      if (this.isEnabled) {
        await this.startAnalysis();
      } else {
        EQ12Debug.logger.info('Content', 'Governance analysis disabled');
      }
      
      EQ12Debug.performance.endTimer('analyzer_initialization');
      
    } catch (error) {
      handleContentError(error, 'critical_analyzer_init');
    }
  }
  
  // Enhanced message sending (deprecated in favor of global function)
  sendMessage(message) {
    EQ12Debug.logger.warn('Content', 'Using deprecated sendMessage method, use sendMessageWithDebug instead');
    return sendMessageWithDebug(message);
  }
  
  async startAnalysis() {
    try {
      EQ12Debug.logger.info('Content', 'Starting governance analysis', {
        mode: this.mode,
        url: window.location.href,
        timestamp: new Date().toISOString()
      });
      
      EQ12Debug.performance.startTimer('governance_analysis');
      
      // Analyze page security headers
      await this.analyzeSecurityHeaders();
      
      // Check for sensitive data patterns
      await this.scanSensitiveData();
      
      // Monitor network requests
      this.monitorNetworkActivity();
      
      // Add governance indicators
      await this.addGovernanceUI();
      
      EQ12Debug.performance.endTimer('governance_analysis');
      EQ12Debug.logger.info('Content', 'Governance analysis completed successfully', this.analysisResults);
      
    } catch (error) {
      handleContentError(error, 'governance_analysis');
    }
  }
  
  analyzeSecurityHeaders() {
    // Check for common security headers via meta tags or fetch
    const securityChecks = {
      'Content-Security-Policy': false,
      'Strict-Transport-Security': false,
      'X-Frame-Options': false,
      'X-Content-Type-Options': false
    };
    
    // Check meta tags
    document.querySelectorAll('meta[http-equiv]').forEach(meta => {
      const httpEquiv = meta.getAttribute('http-equiv');
      if (securityChecks.hasOwnProperty(httpEquiv)) {
        securityChecks[httpEquiv] = true;
      }
    });
    
    console.log('EQ12: Security headers analysis:', securityChecks);
    return securityChecks;
  }
  
  scanSensitiveData() {
    const sensitivePatterns = [
      /\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b/, // Credit card
      /\b\d{3}-\d{2}-\d{4}\b/, // SSN
      /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/, // Email
      /\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b/ // Phone
    ];
    
    const textContent = document.body.textContent;
    const findings = [];
    
    sensitivePatterns.forEach((pattern, index) => {
      const matches = textContent.match(pattern);
      if (matches) {
        findings.push({
          type: ['credit_card', 'ssn', 'email', 'phone'][index],
          count: matches.length
        });
      }
    });
    
    if (findings.length > 0) {
      console.warn('EQ12: Sensitive data patterns detected:', findings);
    }
    
    return findings;
  }
  
  monitorNetworkActivity() {
    // Override fetch to monitor outgoing requests
    const originalFetch = window.fetch;
    window.fetch = (...args) => {
      const url = args[0];
      console.log('EQ12: Network request intercepted:', url);
      
      // Check for insecure HTTP requests
      if (typeof url === 'string' && url.startsWith('http://')) {
        console.warn('EQ12: Insecure HTTP request detected:', url);
      }
      
      return originalFetch.apply(this, args);
    };
  }
  
  addGovernanceUI() {
    // Add floating governance status indicator
    const indicator = document.createElement('div');
    indicator.id = 'eq12-governance-indicator';
    indicator.style.cssText = `
      position: fixed;
      top: 10px;
      right: 10px;
      background: #28a745;
      color: white;
      padding: 8px 12px;
      border-radius: 4px;
      font-family: Arial, sans-serif;
      font-size: 12px;
      z-index: 10000;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
      cursor: pointer;
    `;
    indicator.textContent = `EQ12 Active (${this.mode})`;
    
    indicator.addEventListener('click', () => {
      this.showGovernanceReport();
    });
    
    document.body.appendChild(indicator);
  }
  
  showGovernanceReport() {
    const report = {
      url: window.location.href,
      timestamp: new Date().toISOString(),
      security_headers: this.analyzeSecurityHeaders(),
      sensitive_data: this.scanSensitiveData(),
      compliance_score: this.calculateComplianceScore()
    };
    
    console.log('EQ12 Governance Report:', report);
    alert(`EQ12 Governance Report:\nCompliance Score: ${report.compliance_score}/100\nSee console for details.`);
  }
  
  calculateComplianceScore() {
    let score = 100;
    
    // Deduct points for missing security headers
    const headers = this.analyzeSecurityHeaders();
    Object.values(headers).forEach(present => {
      if (!present) score -= 10;
    });
    
    // Deduct points for sensitive data exposure
    const sensitive = this.scanSensitiveData();
    score -= sensitive.length * 15;
    
    // Check HTTPS
    if (window.location.protocol !== 'https:') {
      score -= 20;
    }
    
    return Math.max(0, score);
  }
}

// Enhanced message listener with debugging
api.runtime.onMessage.addListener((request, sender, sendResponse) => {
  try {
    EQ12Debug.logger.debug('Content', 'Message received from background', {
      action: request.action,
      sender: sender,
      timestamp: new Date().toISOString()
    });
    
    EQ12Debug.performance.startTimer(`handle_${request.action}`);
    
    switch (request.action) {
      case 'analyze_page':
        EQ12Debug.logger.info('Content', 'Page analysis requested');
        const analyzer = new EQ12GovernanceAnalyzer();
        EQ12Debug.performance.endTimer(`handle_${request.action}`);
        sendResponse({ 
          success: true, 
          timestamp: new Date().toISOString(),
          url: window.location.href 
        });
        break;
        
      case 'show_debug_info':
        EQ12Debug.logger.info('Content', 'Debug info requested');
        showDebugModal();
        EQ12Debug.performance.endTimer(`handle_${request.action}`);
        sendResponse({ 
          success: true, 
          debug_info: getDebugInfo(),
          timestamp: new Date().toISOString()
        });
        break;
        
      case 'get_page_info':
        const pageInfo = {
          url: window.location.href,
          title: document.title,
          domain: window.location.hostname,
          protocol: window.location.protocol,
          userAgent: navigator.userAgent,
          timestamp: new Date().toISOString(),
          performance: performance.timing ? {
            loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
            domReady: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart
          } : null
        };
        EQ12Debug.performance.endTimer(`handle_${request.action}`);
        sendResponse(pageInfo);
        break;
        
      default:
        EQ12Debug.logger.warn('Content', 'Unknown message action', { action: request.action });
        EQ12Debug.performance.endTimer(`handle_${request.action}`);
        sendResponse({ error: `Unknown action: ${request.action}` });
    }
    
  } catch (error) {
    handleContentError(error, 'message_handling');
    sendResponse({ error: 'Internal error processing message' });
  }
  
  return false; // Synchronous response
});

// Debug modal display function
function showDebugModal() {
  try {
    // Remove existing modal if present
    const existingModal = document.getElementById('eq12-debug-modal');
    if (existingModal) {
      existingModal.remove();
    }
    
    const debugInfo = getDebugInfo();
    
    const modal = document.createElement('div');
    modal.id = 'eq12-debug-modal';
    modal.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      width: 400px;
      max-height: 500px;
      background: white;
      border: 2px solid #007cba;
      border-radius: 8px;
      padding: 20px;
      font-family: Arial, sans-serif;
      font-size: 12px;
      z-index: 10000;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      overflow-y: auto;
    `;
    
    modal.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
        <h3 style="margin: 0; color: #007cba;">EQ12 Debug Info</h3>
        <button onclick="document.getElementById('eq12-debug-modal').remove()" 
                style="background: #dc3545; color: white; border: none; border-radius: 3px; padding: 5px 10px; cursor: pointer;">×</button>
      </div>
      <div style="background: #f8f9fa; padding: 10px; border-radius: 4px; margin-bottom: 10px;">
        <strong>Page Info:</strong><br>
        URL: ${debugInfo.pageInfo.url}<br>
        Title: ${debugInfo.pageInfo.title}<br>
        Domain: ${debugInfo.pageInfo.domain}<br>
        Protocol: ${debugInfo.pageInfo.protocol}
      </div>
      <div style="background: #f8f9fa; padding: 10px; border-radius: 4px; margin-bottom: 10px;">
        <strong>Extension Status:</strong><br>
        Debug Mode: ${debugInfo.extension.debugMode ? 'Enabled' : 'Disabled'}<br>
        Pending Messages: ${debugInfo.extension.pendingMessages}<br>
        Errors: ${debugInfo.extension.errors}
      </div>
      <div style="background: #f8f9fa; padding: 10px; border-radius: 4px; margin-bottom: 10px;">
        <strong>Performance:</strong><br>
        Active Timers: ${debugInfo.performance.activeTimers}<br>
        Load Time: ${debugInfo.performance.loadTime}ms<br>
        DOM Ready: ${debugInfo.performance.domReady}ms
      </div>
      <div style="text-align: center;">
        <button onclick="EQ12Debug.logger.info('Content', 'Manual debug test triggered')"
                style="background: #007cba; color: white; border: none; border-radius: 3px; padding: 8px 15px; cursor: pointer; margin: 5px;">
          Test Logging
        </button>
        <button onclick="window.EQ12Debug = EQ12Debug; console.log('EQ12Debug available in console:', EQ12Debug)"
                style="background: #28a745; color: white; border: none; border-radius: 3px; padding: 8px 15px; cursor: pointer; margin: 5px;">
          Expose to Console
        </button>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    // Auto-remove after 30 seconds
    setTimeout(() => {
      if (document.getElementById('eq12-debug-modal')) {
        modal.remove();
      }
    }, 30000);
    
    EQ12Debug.logger.info('Content', 'Debug modal displayed');
    
  } catch (error) {
    handleContentError(error, 'debug_modal');
  }
}

// Get comprehensive debug information
function getDebugInfo() {
  return {
    timestamp: new Date().toISOString(),
    pageInfo: {
      url: window.location.href,
      title: document.title,
      domain: window.location.hostname,
      protocol: window.location.protocol,
      userAgent: navigator.userAgent
    },
    extension: {
      debugMode: EQ12Debug.messaging.debugMode,
      pendingMessages: EQ12Debug.messaging.pendingMessages.size,
      errors: analyzer ? analyzer.errors.length : 0
    },
    performance: {
      activeTimers: Object.keys(EQ12Debug.performance.timers).length,
      loadTime: performance.timing ? performance.timing.loadEventEnd - performance.timing.navigationStart : 'N/A',
      domReady: performance.timing ? performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart : 'N/A'
    }
  };
}

// Auto-initialize if governance is enabled
EQ12Debug.performance.endTimer('content_script_initialization');
const analyzer = new EQ12GovernanceAnalyzer();

// Make debug utilities available globally for console debugging
window.EQ12Debug = EQ12Debug;
window.EQ12Analyzer = analyzer;

EQ12Debug.logger.info('Content', 'EQ12 Content script fully loaded and ready', {
  url: window.location.href,
  timestamp: new Date().toISOString()
});