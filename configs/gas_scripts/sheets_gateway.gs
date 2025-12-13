/**
 * EQ12 Google Sheets Gateway - Web App JSON API
 * Deploy: Apps Script → Deploy → New Deployment → Web app
 * Execute as: Me; Who has access: Anyone with the link
 * Set Script Property: SHARED_SECRET to match EQ12 config
 * 
 * Provides bi-directional CRUD for Sheets tabs: Bets, Arbs, Deliverables
 * Handles JSON in/out with authentication and monetization tracking
 */

// Configuration - Set as Script Properties
const SHARED_SECRET = PropertiesService.getScriptProperties().getProperty('SHARED_SECRET');
const EQ12_WEBHOOK = PropertiesService.getScriptProperties().getProperty('EQ12_WEBHOOK');

/**
 * Handle GET requests - Pull data from Sheets
 * @param {Object} e - Event object with parameters
 * @returns {ContentService.TextOutput} JSON response
 */
function doGet(e) {
  try {
    // Log all GET requests for monetization tracking
    logActivity_('GET', e.parameter, 'incoming');
    
    if (!authOK(e)) {
      return forbidden_('Invalid authentication');
    }
    
    const action = (e.parameter.action || '').toLowerCase();
    
    switch (action) {
      case 'pull':
        return pull_(e);
      case 'status':
        return status_();
      case 'health':
        return health_();
      default:
        return bad_('Unknown action: ' + action);
    }
    
  } catch (error) {
    logActivity_('GET', e.parameter, 'error', error.toString());
    return error_('Server error: ' + error.message);
  }
}

/**
 * Handle POST requests - Push data to Sheets
 * @param {Object} e - Event object with post data
 * @returns {ContentService.TextOutput} JSON response
 */
function doPost(e) {
  try {
    const body = JSON.parse(e.postData.contents || '{}');
    
    // Log all POST requests for monetization tracking
    logActivity_('POST', body, 'incoming');
    
    if (!authOK(e, body)) {
      return forbidden_('Invalid authentication');
    }
    
    const action = (body.action || '').toLowerCase();
    
    switch (action) {
      case 'push':
        return push_(body);
      case 'append':
        return append_(body);
      case 'merge':
        return mailMerge_(body);
      case 'trigger':
        return runTrigger_(body);
      default:
        return bad_('Unknown action: ' + action);
    }
    
  } catch (error) {
    logActivity_('POST', {}, 'error', error.toString());
    return error_('Server error: ' + error.message);
  }
}

/**
 * Authentication check for requests
 * @param {Object} e - Event object
 * @param {Object} body - POST body (optional)
 * @returns {boolean} Authentication success
 */
function authOK(e, body = null) {
  if (!SHARED_SECRET) {
    console.warn('SHARED_SECRET not configured');
    return false;
  }
  
  // Check multiple possible locations for the secret
  const token = e.parameter?.secret || 
                body?.secret || 
                e.headers?.['x-shared-secret'] ||
                e.headers?.['X-Shared-Secret'];
                
  const isValid = token && token === SHARED_SECRET;
  
  logActivity_('AUTH', { hasToken: !!token, valid: isValid }, isValid ? 'success' : 'failed');
  
  return isValid;
}

/**
 * Pull data from specified Sheet
 * @param {Object} e - Event object with sheet parameter
 * @returns {ContentService.TextOutput} JSON response with sheet data
 */
function pull_(e) {
  const sheetName = e.parameter.sheet || 'Bets';
  const limit = parseInt(e.parameter.limit) || 0;
  const offset = parseInt(e.parameter.offset) || 0;
  
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(sheetName);
    
    if (!sheet) {
      return bad_(`Sheet '${sheetName}' not found`);
    }
    
    const dataRange = sheet.getDataRange();
    if (dataRange.getNumRows() === 0) {
      return ok_({ sheet: sheetName, rows: [], count: 0 });
    }
    
    const values = dataRange.getValues();
    const headers = values[0];
    let dataRows = values.slice(1);
    
    // Apply offset and limit for pagination
    if (offset > 0) {
      dataRows = dataRows.slice(offset);
    }
    if (limit > 0) {
      dataRows = dataRows.slice(0, limit);
    }
    
    // Convert to objects
    const data = dataRows.map(row => {
      const obj = {};
      headers.forEach((header, index) => {
        obj[header] = row[index] || '';
      });
      return obj;
    });
    
    // Log successful pull for monetization tracking
    logActivity_('PULL', { sheet: sheetName, rows: data.length }, 'success');
    
    return ok_({ 
      sheet: sheetName, 
      rows: data, 
      count: data.length,
      total_rows: values.length - 1,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    logActivity_('PULL', { sheet: sheetName }, 'error', error.toString());
    return error_('Failed to pull from sheet: ' + error.message);
  }
}

/**
 * Push data to specified Sheet (replaces all content)
 * @param {Object} body - Request body with sheet name and rows
 * @returns {ContentService.TextOutput} JSON response
 */
function push_(body) {
  const { sheet = 'Bets', rows = [] } = body;
  
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let targetSheet = ss.getSheetByName(sheet);
    
    // Create sheet if it doesn't exist
    if (!targetSheet) {
      targetSheet = ss.insertSheet(sheet);
    }
    
    // Clear existing content
    targetSheet.clear();
    
    if (rows.length === 0) {
      logActivity_('PUSH', { sheet, rows: 0 }, 'success');
      return ok_({ sheet, count: 0, message: 'Sheet cleared' });
    }
    
    // Get headers from first row
    const headers = Object.keys(rows[0]);
    
    // Set headers
    targetSheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    
    // Set data rows
    const values = rows.map(row => 
      headers.map(header => row[header] !== undefined ? row[header] : '')
    );
    
    if (values.length > 0) {
      targetSheet.getRange(2, 1, values.length, headers.length).setValues(values);
    }
    
    // Auto-resize columns for better presentation
    targetSheet.autoResizeColumns(1, headers.length);
    
    // Log successful push for monetization tracking
    logActivity_('PUSH', { sheet, rows: rows.length }, 'success');
    
    return ok_({ 
      sheet, 
      count: rows.length,
      headers: headers,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    logActivity_('PUSH', { sheet, rows: rows.length }, 'error', error.toString());
    return error_('Failed to push to sheet: ' + error.message);
  }
}

/**
 * Append data to specified Sheet
 * @param {Object} body - Request body with sheet name and rows
 * @returns {ContentService.TextOutput} JSON response
 */
function append_(body) {
  const { sheet = 'Logs', rows = [] } = body;
  
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let targetSheet = ss.getSheetByName(sheet);
    
    // Create sheet if it doesn't exist
    if (!targetSheet) {
      targetSheet = ss.insertSheet(sheet);
    }
    
    if (rows.length === 0) {
      return ok_({ sheet, appended: 0 });
    }
    
    let headers = [];
    
    // Handle headers
    if (targetSheet.getLastRow() === 0) {
      // New sheet - set headers from first row
      headers = Object.keys(rows[0]);
      targetSheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    } else {
      // Existing sheet - get current headers
      headers = targetSheet.getRange(1, 1, 1, targetSheet.getLastColumn()).getValues()[0];
    }
    
    // Prepare data rows
    const values = rows.map(row => 
      headers.map(header => row[header] !== undefined ? row[header] : '')
    );
    
    // Append data
    const startRow = targetSheet.getLastRow() + 1;
    targetSheet.getRange(startRow, 1, values.length, headers.length).setValues(values);
    
    // Log successful append for monetization tracking
    logActivity_('APPEND', { sheet, rows: rows.length }, 'success');
    
    return ok_({ 
      sheet, 
      appended: rows.length,
      total_rows: targetSheet.getLastRow() - 1,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    logActivity_('APPEND', { sheet, rows: rows.length }, 'error', error.toString());
    return error_('Failed to append to sheet: ' + error.message);
  }
}

/**
 * Get system status
 * @returns {ContentService.TextOutput} Status JSON
 */
function status_() {
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheets = ss.getSheets().map(sheet => ({
      name: sheet.getName(),
      rows: sheet.getLastRow(),
      columns: sheet.getLastColumn()
    }));
    
    return ok_({
      status: 'healthy',
      spreadsheet_id: ss.getId(),
      sheets: sheets,
      timestamp: new Date().toISOString(),
      version: '1.0.0'
    });
    
  } catch (error) {
    return error_('Status check failed: ' + error.message);
  }
}

/**
 * Health check endpoint
 * @returns {ContentService.TextOutput} Health status
 */
function health_() {
  return ok_({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: 'running'
  });
}

/**
 * Log activity for monetization and debugging
 * @param {string} action - Action performed
 * @param {Object} data - Action data
 * @param {string} status - Success/error/info
 * @param {string} error - Error message if any
 */
function logActivity_(action, data = {}, status = 'info', error = '') {
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let logSheet = ss.getSheetByName('ActivityLog');
    
    if (!logSheet) {
      logSheet = ss.insertSheet('ActivityLog');
      // Set headers
      logSheet.getRange(1, 1, 1, 6).setValues([
        ['Timestamp', 'Action', 'Status', 'Data', 'Error', 'UserAgent']
      ]);
    }
    
    const timestamp = new Date().toISOString();
    const dataStr = JSON.stringify(data).substring(0, 500); // Limit data size
    const userAgent = ''; // Can't access user agent in Apps Script
    
    logSheet.appendRow([timestamp, action, status, dataStr, error, userAgent]);
    
    // Keep only last 1000 rows to prevent sheet bloat
    if (logSheet.getLastRow() > 1001) {
      logSheet.deleteRows(2, logSheet.getLastRow() - 1001);
    }
    
  } catch (e) {
    console.error('Logging failed:', e);
  }
}

/**
 * Response helper functions
 */
function ok_(data = {}) {
  return ContentService
    .createTextOutput(JSON.stringify({ ok: true, ...data }))
    .setMimeType(ContentService.MimeType.JSON);
}

function bad_(message) {
  return ContentService
    .createTextOutput(JSON.stringify({ ok: false, error: message }))
    .setMimeType(ContentService.MimeType.JSON);
}

function error_(message) {
  return ContentService
    .createTextOutput(JSON.stringify({ ok: false, error: message, timestamp: new Date().toISOString() }))
    .setMimeType(ContentService.MimeType.JSON);
}

function forbidden_(message = 'Forbidden') {
  return ContentService
    .createTextOutput(JSON.stringify({ ok: false, error: message, code: 403 }))
    .setMimeType(ContentService.MimeType.JSON);
}