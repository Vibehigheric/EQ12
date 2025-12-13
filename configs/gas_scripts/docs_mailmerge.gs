/**
 * EQ12 Docs & Mail Merge System - Google Apps Script
 * Handles document templating and Gmail mail-merge campaigns
 * Integrates with EQ12 monetization workflows
 */

// Configuration
const FROM_NAME = 'EQ12 Sports Analytics';
const TRACKING_PIXEL_BASE = 'https://your-tracker.com/px';

/**
 * Render document from template with data substitution
 * @param {string} templateFileId - Google Docs template file ID
 * @param {Object} dataObj - Data object for template substitution
 * @param {string} outputName - Name for the rendered document
 * @returns {Object} Generated file information
 */
function renderDocFromTemplate_(templateFileId, dataObj, outputName = null) {
  try {
    const templateFile = DriveApp.getFileById(templateFileId);
    const copyName = outputName || `EQ12_Rendered_${Date.now()}`;
    const copiedFile = templateFile.makeCopy(copyName);
    
    // Open the document and perform substitutions
    const doc = DocumentApp.openById(copiedFile.getId());
    const body = doc.getBody();
    
    // Replace all template variables {{variable}}
    Object.keys(dataObj).forEach(key => {
      const placeholder = `{{${key}}}`;
      const value = String(dataObj[key] || '');
      body.replaceText(placeholder, value);
    });
    
    // Add timestamp and branding
    body.replaceText('{{generated_timestamp}}', new Date().toLocaleString());
    body.replaceText('{{generated_by}}', 'EQ12 Sports Betting Terminal');
    
    doc.saveAndClose();
    
    // Generate PDF version
    const pdfBlob = DriveApp.getFileById(copiedFile.getId())
      .getBlob()
      .setName(copyName + '.pdf')
      .getAs('application/pdf');
    
    // Log the rendering for monetization tracking
    logDocActivity_('RENDER', templateFileId, copyName, 'success');
    
    return {
      docId: copiedFile.getId(),
      docUrl: copiedFile.getUrl(),
      pdfBlob: pdfBlob,
      name: copyName,
      size: pdfBlob.getBytes().length
    };
    
  } catch (error) {
    logDocActivity_('RENDER', templateFileId, 'ERROR', 'failed', error.toString());
    throw new Error(`Document rendering failed: ${error.message}`);
  }
}

/**
 * Render presentation (Slides) from template
 * @param {string} templateFileId - Google Slides template file ID
 * @param {Object} dataObj - Data object for template substitution
 * @param {string} outputName - Name for the rendered presentation
 * @returns {Object} Generated file information
 */
function renderSlidesFromTemplate_(templateFileId, dataObj, outputName = null) {
  try {
    const templateFile = DriveApp.getFileById(templateFileId);
    const copyName = outputName || `EQ12_Slides_${Date.now()}`;
    const copiedFile = templateFile.makeCopy(copyName);
    
    // Open the presentation and perform substitutions
    const presentation = SlidesApp.openById(copiedFile.getId());
    const slides = presentation.getSlides();
    
    // Replace text in all slides
    slides.forEach((slide, slideIndex) => {
      Object.keys(dataObj).forEach(key => {
        const placeholder = `{{${key}}}`;
        const value = String(dataObj[key] || '');
        
        // Replace in text boxes
        slide.getShapes().forEach(shape => {
          if (shape.getShapeType() === SlidesApp.ShapeType.TEXT_BOX) {
            const textRange = shape.getText();
            textRange.replaceAllText(placeholder, value);
          }
        });
      });
    });
    
    presentation.saveAndClose();
    
    // Generate PDF version
    const pdfBlob = DriveApp.getFileById(copiedFile.getId())
      .getBlob()
      .setName(copyName + '.pdf')
      .getAs('application/pdf');
    
    logDocActivity_('RENDER_SLIDES', templateFileId, copyName, 'success');
    
    return {
      slideId: copiedFile.getId(),
      slideUrl: copiedFile.getUrl(),
      pdfBlob: pdfBlob,
      name: copyName,
      slides: slides.length
    };
    
  } catch (error) {
    logDocActivity_('RENDER_SLIDES', templateFileId, 'ERROR', 'failed', error.toString());
    throw new Error(`Slides rendering failed: ${error.message}`);
  }
}

/**
 * Run mail merge campaign from Google Sheets data
 * @param {Object} config - Mail merge configuration
 * @returns {Object} Campaign results
 */
function runMailMerge(config) {
  const {
    templateFileId,
    sheetName = 'Campaigns',
    subjectTemplate,
    bodyTemplate,
    attachTemplate = true,
    campaignName = 'EQ12_Campaign',
    trackOpens = true
  } = config;
  
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(sheetName);
    
    if (!sheet) {
      throw new Error(`Sheet '${sheetName}' not found`);
    }
    
    const dataRange = sheet.getDataRange();
    const values = dataRange.getValues();
    const headers = values[0];
    const dataRows = values.slice(1);
    
    let sentCount = 0;
    let errors = [];
    
    // Process each recipient
    dataRows.forEach((row, index) => {
      try {
        // Convert row to data object
        const data = {};
        headers.forEach((header, colIndex) => {
          data[header] = row[colIndex] || '';
        });
        
        // Skip if no email
        if (!data.email || !data.email.includes('@')) {
          errors.push(`Row ${index + 2}: Invalid email`);
          return;
        }
        
        // Render document if template provided
        let attachments = [];
        if (attachTemplate && templateFileId) {
          const rendered = renderDocFromTemplate_(
            templateFileId, 
            data, 
            `${campaignName}_${data.name || index + 1}`
          );
          attachments.push(rendered.pdfBlob);
        }
        
        // Process email templates
        const subject = fillTemplate_(subjectTemplate, data);
        let bodyHtml = fillTemplate_(bodyTemplate, data);
        
        // Add tracking pixel if enabled
        if (trackOpens) {
          const trackingId = `${campaignName}_${index + 1}_${Date.now()}`;
          bodyHtml += createTrackingPixel_(trackingId, data.email);
        }
        
        // Add EQ12 branding and disclaimers
        bodyHtml += createEmailFooter_(data);
        
        // Convert HTML to plain text for fallback
        const bodyText = bodyHtml.replace(/<[^>]+>/g, '');
        
        // Send email
        GmailApp.sendEmail(data.email, subject, bodyText, {
          htmlBody: bodyHtml,
          attachments: attachments,
          name: FROM_NAME,
          replyTo: Session.getActiveUser().getEmail()
        });
        
        sentCount++;
        
        // Log individual send
        logMailActivity_(data.email, campaignName, 'sent', subject);
        
      } catch (emailError) {
        errors.push(`Row ${index + 2}: ${emailError.message}`);
        logMailActivity_(data.email || 'unknown', campaignName, 'failed', emailError.toString());
      }
    });
    
    // Log campaign summary
    logCampaignSummary_(campaignName, sentCount, errors.length, config);
    
    return {
      ok: true,
      campaign: campaignName,
      sent: sentCount,
      errors: errors,
      total_recipients: dataRows.length,
      timestamp: new Date().toISOString()
    };
    
  } catch (error) {
    logCampaignSummary_(campaignName || 'unknown', 0, 1, config, error.toString());
    throw new Error(`Mail merge failed: ${error.message}`);
  }
}

/**
 * Handle mail merge via POST request
 * @param {Object} body - Request body
 * @returns {ContentService.TextOutput} JSON response
 */
function mailMerge_(body) {
  try {
    const result = runMailMerge(body);
    return ContentService
      .createTextOutput(JSON.stringify(result))
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
 * Create newsletter campaign from recent EQ12 data
 * @param {Object} config - Newsletter configuration
 * @returns {Object} Campaign results
 */
function createNewsletterCampaign(config) {
  const {
    templateId,
    recipientSheet = 'Subscribers',
    contentSheet = 'RecentBets',
    subject = 'EQ12 Weekly Sports Betting Digest'
  } = config;
  
  try {
    // Get recent betting data for content
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const contentData = getSheetData_(contentSheet, 10); // Last 10 rows
    
    // Generate newsletter content
    const newsletterContent = generateNewsletterContent_(contentData);
    
    // Run mail merge with generated content
    const mergeConfig = {
      templateFileId: templateId,
      sheetName: recipientSheet,
      subjectTemplate: subject,
      bodyTemplate: newsletterContent,
      campaignName: `Newsletter_${new Date().toISOString().split('T')[0]}`,
      trackOpens: true
    };
    
    return runMailMerge(mergeConfig);
    
  } catch (error) {
    throw new Error(`Newsletter campaign failed: ${error.message}`);
  }
}

/**
 * Helper functions
 */

function fillTemplate_(template, data) {
  if (!template) return '';
  
  return template.replace(/\{\{(\w+)\}\}/g, (match, key) => {
    return String(data[key] || '');
  });
}

function createTrackingPixel_(trackingId, email) {
  return `<img src="${TRACKING_PIXEL_BASE}?id=${encodeURIComponent(trackingId)}&email=${encodeURIComponent(email)}&t=${Date.now()}" width="1" height="1" style="display:none;" />`;
}

function createEmailFooter_(data) {
  return `
<div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ccc; font-size: 12px; color: #666;">
  <p><strong>EQ12 Sports Betting Terminal</strong> - Advanced Analytics & Insights</p>
  <p>This email contains affiliate links. We may earn a commission from qualifying purchases.</p>
  <p>For questions or to unsubscribe, reply to this email.</p>
  <p><em>Paper trading recommended. Past performance does not guarantee future results.</em></p>
</div>`;
}

function getSheetData_(sheetName, limit = 0) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(sheetName);
  
  if (!sheet) return [];
  
  const values = sheet.getDataRange().getValues();
  if (values.length <= 1) return [];
  
  const headers = values[0];
  let dataRows = values.slice(1);
  
  if (limit > 0) {
    dataRows = dataRows.slice(-limit); // Get last N rows
  }
  
  return dataRows.map(row => {
    const obj = {};
    headers.forEach((header, index) => {
      obj[header] = row[index] || '';
    });
    return obj;
  });
}

function generateNewsletterContent_(recentData) {
  if (!recentData.length) {
    return `
<h2>EQ12 Weekly Digest</h2>
<p>Hello {{name}},</p>
<p>No recent betting activity to report this week. Check back soon for the latest insights!</p>
<p>Best regards,<br>The EQ12 Team</p>`;
  }
  
  let content = `
<h2>EQ12 Weekly Sports Betting Digest</h2>
<p>Hello {{name}},</p>
<p>Here are your latest betting insights and opportunities:</p>
<ul>`;
  
  recentData.slice(0, 5).forEach(bet => {
    content += `<li><strong>${bet.team || 'Game'}</strong> - ${bet.analysis || 'Analysis available'} (${bet.confidence || 'TBD'}% confidence)</li>`;
  });
  
  content += `</ul>
<p><a href="{{upgrade_link}}" style="background: #007cba; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Upgrade to Premium</a></p>
<p>Best regards,<br>The EQ12 Team</p>`;
  
  return content;
}

/**
 * Logging functions for monetization tracking
 */

function logDocActivity_(action, templateId, docName, status, error = '') {
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let logSheet = ss.getSheetByName('DocActivity');
    
    if (!logSheet) {
      logSheet = ss.insertSheet('DocActivity');
      logSheet.getRange(1, 1, 1, 6).setValues([
        ['Timestamp', 'Action', 'TemplateId', 'DocName', 'Status', 'Error']
      ]);
    }
    
    logSheet.appendRow([
      new Date().toISOString(),
      action,
      templateId,
      docName,
      status,
      error
    ]);
    
  } catch (e) {
    console.error('Doc activity logging failed:', e);
  }
}

function logMailActivity_(email, campaign, status, details) {
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let logSheet = ss.getSheetByName('MailActivity');
    
    if (!logSheet) {
      logSheet = ss.insertSheet('MailActivity');
      logSheet.getRange(1, 1, 1, 5).setValues([
        ['Timestamp', 'Email', 'Campaign', 'Status', 'Details']
      ]);
    }
    
    logSheet.appendRow([
      new Date().toISOString(),
      email,
      campaign,
      status,
      String(details).substring(0, 500)
    ]);
    
  } catch (e) {
    console.error('Mail activity logging failed:', e);
  }
}

function logCampaignSummary_(campaign, sent, errors, config, error = '') {
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let logSheet = ss.getSheetByName('CampaignSummary');
    
    if (!logSheet) {
      logSheet = ss.insertSheet('CampaignSummary');
      logSheet.getRange(1, 1, 1, 7).setValues([
        ['Timestamp', 'Campaign', 'Sent', 'Errors', 'Config', 'Status', 'Error']
      ]);
    }
    
    logSheet.appendRow([
      new Date().toISOString(),
      campaign,
      sent,
      errors,
      JSON.stringify(config).substring(0, 200),
      error ? 'failed' : 'success',
      error
    ]);
    
  } catch (e) {
    console.error('Campaign summary logging failed:', e);
  }
}