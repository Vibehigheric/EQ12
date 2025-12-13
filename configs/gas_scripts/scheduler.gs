/**
 * EQ12 Scheduler & Trigger Management - Google Apps Script
 * Handles time-based triggers for automated workflows
 * Integrates with EQ12 webhook system for monetization
 */

// Configuration
const EQ12_WEBHOOK = PropertiesService.getScriptProperties().getProperty('EQ12_WEBHOOK');
const SHARED_SECRET = PropertiesService.getScriptProperties().getProperty('SHARED_SECRET');

/**
 * Setup all automated triggers for EQ12 workflows
 */
function setupTriggers() {
  try {
    // Delete existing triggers to avoid duplicates
    ScriptApp.getProjectTriggers().forEach(trigger => {
      ScriptApp.deleteTrigger(trigger);
    });
    
    // Daily triggers
    ScriptApp.newTrigger('dailyDigest')
      .timeBased()
      .everyDays(1)
      .atHour(9)
      .create();
    
    ScriptApp.newTrigger('dailyBackup')
      .timeBased()
      .everyDays(1)
      .atHour(2)
      .create();
    
    // Weekly triggers
    ScriptApp.newTrigger('weeklyDigest')
      .timeBased()
      .onWeekDay(ScriptApp.WeekDay.MONDAY)
      .atHour(9)
      .create();
    
    ScriptApp.newTrigger('weeklyCleanup')
      .timeBased()
      .onWeekDay(ScriptApp.WeekDay.SUNDAY)
      .atHour(23)
      .create();
    
    // Monthly triggers
    ScriptApp.newTrigger('monthlyReport')
      .timeBased()
      .onMonthDay(1)
      .atHour(10)
      .create();
    
    logTriggerActivity_('SETUP', 'All triggers configured', 'success');
    
    return {
      ok: true,
      triggers_created: ScriptApp.getProjectTriggers().length,
      message: 'All triggers configured successfully'
    };
    
  } catch (error) {
    logTriggerActivity_('SETUP', error.toString(), 'failed');
    throw new Error(`Trigger setup failed: ${error.message}`);
  }
}

/**
 * Daily digest workflow - Generate and send daily reports
 */
function dailyDigest() {
  try {
    logTriggerActivity_('DAILY_DIGEST', 'Starting daily digest workflow', 'running');
    
    const startTime = Date.now();
    let results = {
      sheets_updated: 0,
      emails_sent: 0,
      webhook_called: false,
      errors: []
    };
    
    // 1. Update activity summary in Sheets
    try {
      updateDailySummarySheet_();
      results.sheets_updated++;
    } catch (e) {
      results.errors.push(`Sheet update failed: ${e.message}`);
    }
    
    // 2. Generate and send daily newsletter if configured
    try {
      const newsletterConfig = {
        templateId: PropertiesService.getScriptProperties().getProperty('NEWSLETTER_TEMPLATE_ID'),
        recipientSheet: 'DailySubscribers',
        subject: `EQ12 Daily Digest - ${new Date().toLocaleDateString()}`
      };
      
      if (newsletterConfig.templateId) {
        const campaignResult = createNewsletterCampaign(newsletterConfig);
        results.emails_sent = campaignResult.sent || 0;
      }
    } catch (e) {
      results.errors.push(`Newsletter failed: ${e.message}`);
    }
    
    // 3. Notify EQ12 webhook
    try {
      const webhookResult = notifyEQ12Webhook_('daily_digest', {
        timestamp: new Date().toISOString(),
        summary: results,
        duration: Date.now() - startTime
      });
      results.webhook_called = webhookResult.ok;
    } catch (e) {
      results.errors.push(`Webhook failed: ${e.message}`);
    }
    
    const status = results.errors.length === 0 ? 'success' : 'partial';
    logTriggerActivity_('DAILY_DIGEST', JSON.stringify(results), status);
    
    return results;
    
  } catch (error) {
    logTriggerActivity_('DAILY_DIGEST', error.toString(), 'failed');
    throw error;
  }
}

/**
 * Weekly digest workflow - Comprehensive weekly analytics
 */
function weeklyDigest() {
  try {
    logTriggerActivity_('WEEKLY_DIGEST', 'Starting weekly digest workflow', 'running');
    
    const startTime = Date.now();
    let results = {
      analytics_generated: false,
      premium_emails_sent: 0,
      reports_created: 0,
      webhook_called: false,
      errors: []
    };
    
    // 1. Generate weekly analytics
    try {
      generateWeeklyAnalytics_();
      results.analytics_generated = true;
    } catch (e) {
      results.errors.push(`Analytics failed: ${e.message}`);
    }
    
    // 2. Create and send premium reports
    try {
      const premiumConfig = {
        templateId: PropertiesService.getScriptProperties().getProperty('PREMIUM_TEMPLATE_ID'),
        recipientSheet: 'PremiumSubscribers',
        contentSheet: 'WeeklyAnalytics',
        subject: `EQ12 Premium Weekly Report - Week of ${getWeekDate_()}`
      };
      
      if (premiumConfig.templateId) {
        const campaignResult = createNewsletterCampaign(premiumConfig);
        results.premium_emails_sent = campaignResult.sent || 0;
      }
    } catch (e) {
      results.errors.push(`Premium reports failed: ${e.message}`);
    }
    
    // 3. Generate PDF reports for Drive storage
    try {
      const reportsGenerated = generateWeeklyPDFReports_();
      results.reports_created = reportsGenerated;
    } catch (e) {
      results.errors.push(`PDF generation failed: ${e.message}`);
    }
    
    // 4. Notify EQ12 webhook
    try {
      const webhookResult = notifyEQ12Webhook_('weekly_digest', {
        timestamp: new Date().toISOString(),
        week: getWeekDate_(),
        summary: results,
        duration: Date.now() - startTime
      });
      results.webhook_called = webhookResult.ok;
    } catch (e) {
      results.errors.push(`Webhook failed: ${e.message}`);
    }
    
    const status = results.errors.length === 0 ? 'success' : 'partial';
    logTriggerActivity_('WEEKLY_DIGEST', JSON.stringify(results), status);
    
    return results;
    
  } catch (error) {
    logTriggerActivity_('WEEKLY_DIGEST', error.toString(), 'failed');
    throw error;
  }
}

/**
 * Monthly report workflow - Comprehensive monthly analytics
 */
function monthlyReport() {
  try {
    logTriggerActivity_('MONTHLY_REPORT', 'Starting monthly report workflow', 'running');
    
    const startTime = Date.now();
    let results = {
      revenue_calculated: false,
      stakeholder_reports_sent: 0,
      analytics_archived: false,
      webhook_called: false,
      errors: []
    };
    
    // 1. Calculate monthly revenue metrics
    try {
      calculateMonthlyRevenue_();
      results.revenue_calculated = true;
    } catch (e) {
      results.errors.push(`Revenue calculation failed: ${e.message}`);
    }
    
    // 2. Send stakeholder reports
    try {
      const stakeholderResult = sendStakeholderReports_();
      results.stakeholder_reports_sent = stakeholderResult.sent || 0;
    } catch (e) {
      results.errors.push(`Stakeholder reports failed: ${e.message}`);
    }
    
    // 3. Archive previous month's data
    try {
      archivePreviousMonth_();
      results.analytics_archived = true;
    } catch (e) {
      results.errors.push(`Archiving failed: ${e.message}`);
    }
    
    // 4. Notify EQ12 webhook
    try {
      const webhookResult = notifyEQ12Webhook_('monthly_report', {
        timestamp: new Date().toISOString(),
        month: new Date().getMonth() + 1,
        year: new Date().getFullYear(),
        summary: results,
        duration: Date.now() - startTime
      });
      results.webhook_called = webhookResult.ok;
    } catch (e) {
      results.errors.push(`Webhook failed: ${e.message}`);
    }
    
    const status = results.errors.length === 0 ? 'success' : 'partial';
    logTriggerActivity_('MONTHLY_REPORT', JSON.stringify(results), status);
    
    return results;
    
  } catch (error) {
    logTriggerActivity_('MONTHLY_REPORT', error.toString(), 'failed');
    throw error;
  }
}

/**
 * Daily backup workflow - Backup critical data
 */
function dailyBackup() {
  try {
    logTriggerActivity_('DAILY_BACKUP', 'Starting backup workflow', 'running');
    
    const backupResults = {
      sheets_backed_up: 0,
      files_created: 0,
      errors: []
    };
    
    // Backup critical sheets to Drive
    const sheetsToBackup = ['Bets', 'Arbitrage', 'Deliverables', 'Campaigns', 'ActivityLog'];
    const backupFolder = getOrCreateBackupFolder_();
    
    sheetsToBackup.forEach(sheetName => {
      try {
        backupSheetToDrive_(sheetName, backupFolder);
        backupResults.sheets_backed_up++;
      } catch (e) {
        backupResults.errors.push(`Backup failed for ${sheetName}: ${e.message}`);
      }
    });
    
    // Create consolidated backup file
    try {
      const consolidatedFile = createConsolidatedBackup_(backupFolder);
      backupResults.files_created = 1;
    } catch (e) {
      backupResults.errors.push(`Consolidated backup failed: ${e.message}`);
    }
    
    const status = backupResults.errors.length === 0 ? 'success' : 'partial';
    logTriggerActivity_('DAILY_BACKUP', JSON.stringify(backupResults), status);
    
    return backupResults;
    
  } catch (error) {
    logTriggerActivity_('DAILY_BACKUP', error.toString(), 'failed');
    throw error;
  }
}

/**
 * Weekly cleanup workflow - Maintain system health
 */
function weeklyCleanup() {
  try {
    logTriggerActivity_('WEEKLY_CLEANUP', 'Starting cleanup workflow', 'running');
    
    const cleanupResults = {
      logs_cleaned: 0,
      files_archived: 0,
      errors: []
    };
    
    // Clean old log entries
    try {
      const logsCleared = cleanupOldLogs_();
      cleanupResults.logs_cleaned = logsCleared;
    } catch (e) {
      cleanupResults.errors.push(`Log cleanup failed: ${e.message}`);
    }
    
    // Archive old backup files
    try {
      const filesArchived = archiveOldBackups_();
      cleanupResults.files_archived = filesArchived;
    } catch (e) {
      cleanupResults.errors.push(`Backup archiving failed: ${e.message}`);
    }
    
    const status = cleanupResults.errors.length === 0 ? 'success' : 'partial';
    logTriggerActivity_('WEEKLY_CLEANUP', JSON.stringify(cleanupResults), status);
    
    return cleanupResults;
    
  } catch (error) {
    logTriggerActivity_('WEEKLY_CLEANUP', error.toString(), 'failed');
    throw error;
  }
}

/**
 * Manual trigger runner - Called via POST request
 * @param {Object} body - Request body with trigger name
 * @returns {ContentService.TextOutput} JSON response
 */
function runTrigger_(body) {
  try {
    const { trigger, force = false } = body;
    
    if (!trigger) {
      return ContentService
        .createTextOutput(JSON.stringify({ ok: false, error: 'Trigger name required' }))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    let result;
    
    switch (trigger.toLowerCase()) {
      case 'daily':
      case 'daily_digest':
        result = dailyDigest();
        break;
      case 'weekly':
      case 'weekly_digest':
        result = weeklyDigest();
        break;
      case 'monthly':
      case 'monthly_report':
        result = monthlyReport();
        break;
      case 'backup':
      case 'daily_backup':
        result = dailyBackup();
        break;
      case 'cleanup':
      case 'weekly_cleanup':
        result = weeklyCleanup();
        break;
      case 'setup':
        result = setupTriggers();
        break;
      default:
        return ContentService
          .createTextOutput(JSON.stringify({ ok: false, error: `Unknown trigger: ${trigger}` }))
          .setMimeType(ContentService.MimeType.JSON);
    }
    
    return ContentService
      .createTextOutput(JSON.stringify({ ok: true, trigger, result }))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    return ContentService
      .createTextOutput(JSON.stringify({
        ok: false,
        error: error.message,
        timestamp: new Date().toISOString()
      }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Helper functions
 */

function updateDailySummarySheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let summarySheet = ss.getSheetByName('DailySummary');
  
  if (!summarySheet) {
    summarySheet = ss.insertSheet('DailySummary');
    summarySheet.getRange(1, 1, 1, 5).setValues([
      ['Date', 'Bets', 'Revenue', 'Visitors', 'Conversions']
    ]);
  }
  
  // Calculate daily metrics
  const today = new Date().toLocaleDateString();
  const betsCount = getBetsCount_();
  const revenue = getEstimatedRevenue_();
  const visitors = getVisitorCount_();
  const conversions = getConversions_();
  
  summarySheet.appendRow([today, betsCount, revenue, visitors, conversions]);
}

function generateWeeklyAnalytics_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let analyticsSheet = ss.getSheetByName('WeeklyAnalytics');
  
  if (!analyticsSheet) {
    analyticsSheet = ss.insertSheet('WeeklyAnalytics');
    analyticsSheet.getRange(1, 1, 1, 8).setValues([
      ['Week', 'Total_Bets', 'Win_Rate', 'ROI', 'Revenue', 'Costs', 'Profit', 'Growth']
    ]);
  }
  
  const weekData = calculateWeeklyMetrics_();
  analyticsSheet.appendRow([
    getWeekDate_(),
    weekData.totalBets,
    weekData.winRate,
    weekData.roi,
    weekData.revenue,
    weekData.costs,
    weekData.profit,
    weekData.growth
  ]);
}

function notifyEQ12Webhook_(event, data) {
  if (!EQ12_WEBHOOK) {
    return { ok: false, error: 'Webhook URL not configured' };
  }
  
  try {
    const payload = {
      event: event,
      timestamp: new Date().toISOString(),
      source: 'gas_scheduler',
      data: data,
      secret: SHARED_SECRET
    };
    
    const response = UrlFetchApp.fetch(EQ12_WEBHOOK, {
      method: 'POST',
      contentType: 'application/json',
      payload: JSON.stringify(payload),
      headers: {
        'X-Shared-Secret': SHARED_SECRET
      }
    });
    
    return { ok: true, status: response.getResponseCode() };
    
  } catch (error) {
    return { ok: false, error: error.message };
  }
}

function getOrCreateBackupFolder_() {
  const folderName = `EQ12_Backups_${new Date().getFullYear()}`;
  const folders = DriveApp.getFoldersByName(folderName);
  
  if (folders.hasNext()) {
    return folders.next();
  } else {
    return DriveApp.createFolder(folderName);
  }
}

function backupSheetToDrive_(sheetName, folder) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(sheetName);
  
  if (!sheet) return;
  
  const today = new Date().toISOString().split('T')[0];
  const fileName = `${sheetName}_backup_${today}.csv`;
  
  const csvContent = convertSheetToCSV_(sheet);
  const blob = Utilities.newBlob(csvContent, 'text/csv', fileName);
  
  folder.createFile(blob);
}

function convertSheetToCSV_(sheet) {
  const data = sheet.getDataRange().getValues();
  return data.map(row => 
    row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')
  ).join('\n');
}

function logTriggerActivity_(trigger, details, status) {
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let logSheet = ss.getSheetByName('TriggerLog');
    
    if (!logSheet) {
      logSheet = ss.insertSheet('TriggerLog');
      logSheet.getRange(1, 1, 1, 4).setValues([
        ['Timestamp', 'Trigger', 'Status', 'Details']
      ]);
    }
    
    logSheet.appendRow([
      new Date().toISOString(),
      trigger,
      status,
      String(details).substring(0, 1000)
    ]);
    
    // Keep only last 500 entries
    if (logSheet.getLastRow() > 501) {
      logSheet.deleteRows(2, logSheet.getLastRow() - 501);
    }
    
  } catch (e) {
    console.error('Trigger logging failed:', e);
  }
}

// Placeholder functions for metrics calculation
function getBetsCount_() { return Math.floor(Math.random() * 50) + 10; }
function getEstimatedRevenue_() { return Math.floor(Math.random() * 500) + 100; }
function getVisitorCount_() { return Math.floor(Math.random() * 1000) + 500; }
function getConversions_() { return Math.floor(Math.random() * 20) + 5; }
function getWeekDate_() { 
  const date = new Date();
  const week = Math.ceil(date.getDate() / 7);
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-W${week}`;
}

function calculateWeeklyMetrics_() {
  return {
    totalBets: Math.floor(Math.random() * 200) + 100,
    winRate: (Math.random() * 0.4 + 0.4).toFixed(3),
    roi: (Math.random() * 0.3 + 0.05).toFixed(3),
    revenue: Math.floor(Math.random() * 2000) + 1000,
    costs: Math.floor(Math.random() * 500) + 200,
    profit: 0, // Calculated after
    growth: (Math.random() * 0.2 - 0.1).toFixed(3)
  };
}

function calculateMonthlyRevenue_() { /* Implementation */ }
function sendStakeholderReports_() { return { sent: 3 }; }
function archivePreviousMonth_() { /* Implementation */ }
function generateWeeklyPDFReports_() { return 2; }
function createConsolidatedBackup_(folder) { /* Implementation */ }
function cleanupOldLogs_() { return 150; }
function archiveOldBackups_() { return 5; }