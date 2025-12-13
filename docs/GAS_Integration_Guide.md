# EQ12 Google Apps Script Integration - Complete Implementation Guide

## Overview
This document provides comprehensive setup and usage instructions for the EQ12 Google Apps Script (GAS) integration, enabling cloud-based automation of Google Workspace services (Gmail, Sheets, Docs, Drive) with the EQ12 monetization stack.

## Architecture
```
EQ12 VB.NET Terminal ←→ Google Apps Script Web App ←→ Google Workspace APIs
     (Local/Cloud)              (Cloud Middleware)         (Gmail, Sheets, Docs)
```

## Components Implemented

### 1. Google Apps Script Files (JavaScript)
- **`sheets_gateway.gs`** - Web App with Sheet CRUD operations, authentication
- **`docs_mailmerge.gs`** - Document generation and mail merge campaigns
- **`scheduler.gs`** - Automated triggers for daily/weekly/monthly workflows

### 2. VB.NET Integration Modules
- **`GASClient.vb`** - HTTP client with authentication and retry logic
- **`SheetsSync.vb`** - DataTable↔Sheets synchronization with tracking
- **`GASMailMerge.vb`** - Mail merge campaigns with Bitly tracking

### 3. CLI Commands (in Eq12Cli.vb)
- `gas-pull` - Pull data from Google Sheets
- `gas-push` - Push data to Google Sheets
- `gas-mailmerge` - Run mail merge campaigns
- `gas-run-trigger` - Execute scheduled triggers
- `gas-analytics` - Get campaign analytics
- `gas-newsletter` - Send automated newsletters

### 4. Database Schema (`sql/gas_integration_schema.sql`)
- Comprehensive tracking tables for logs, campaigns, syncs, revenue
- Performance analytics and health monitoring
- Revenue attribution and conversion tracking

## Setup Instructions

### Step 1: Deploy Google Apps Script Web App

1. **Create New Google Apps Script Project**
   - Go to https://script.google.com
   - Create new project: "EQ12 Integration Hub"

2. **Deploy the Scripts**
   ```javascript
   // Copy contents of sheets_gateway.gs, docs_mailmerge.gs, scheduler.gs
   // into separate files in your GAS project
   ```

3. **Configure Shared Secret**
   ```javascript
   // In sheets_gateway.gs, update:
   const SHARED_SECRET = 'your-super-secret-key-here';
   ```

4. **Deploy as Web App**
   - Click "Deploy" → "New deployment"
   - Type: Web app
   - Execute as: Me
   - Who has access: Anyone
   - Copy the Web App URL

5. **Enable Required APIs** (in GAS project settings)
   - Gmail API
   - Google Sheets API
   - Google Docs API
   - Google Drive API

### Step 2: Configure EQ12 Terminal

1. **Update config.json**
   ```json
   {
     "google_apps_script": {
       "enabled": true,
       "web_app_url": "YOUR_GAS_WEB_APP_URL_HERE",
       "shared_secret": "your-super-secret-key-here",
       "templates": {
         "newsletter_daily": "YOUR_TEMPLATE_DOC_ID",
         "newsletter_weekly": "YOUR_TEMPLATE_DOC_ID"
       },
       "sheets": {
         "subscribers": "Subscribers",
         "arbitrage_opportunities": "Arbitrage_Opportunities"
       }
     }
   }
   ```

2. **Initialize Database Schema**
   ```powershell
   # Run SQL schema against your SQLite database
   sqlite3 Data/eq12_terminal.db < sql/gas_integration_schema.sql
   ```

### Step 3: Create Google Sheets Structure

1. **Create Master Spreadsheet**: "EQ12 Data Hub"

2. **Required Sheet Tabs:**
   - `Subscribers` - Email list with columns: name, email, segment, signup_date
   - `PremiumSubscribers` - Premium users subset
   - `TestSubscribers` - Test recipients (small list for testing)
   - `Arbitrage_Opportunities` - Betting data sync target
   - `ActivityLog` - GAS operation logging
   - `CampaignSummary` - Mail merge campaign results

3. **Sample Subscribers Sheet Structure:**
   ```
   | A: name | B: email | C: segment | D: signup_date | E: status |
   |---------|----------|------------|---------------|-----------|
   | John    | j@ex.com | premium    | 2024-01-15    | active    |
   ```

### Step 4: Create Document Templates

1. **Newsletter Templates** (Google Docs)
   - Daily: Simple update with betting insights
   - Weekly: Comprehensive digest with analysis
   - Monthly: Deep-dive report with monetization CTAs

2. **Template Placeholders:**
   ```html
   {{name}} - Subscriber name
   {{date}} - Current date
   {{recent_arbs}} - Recent arbitrage opportunities
   {{upgrade_link}} - Premium upgrade CTA
   {{affiliate_link}} - Sportsbook affiliate link
   {{unsubscribe_link}} - Unsubscribe URL
   ```

## Usage Examples

### Pull Data from Sheets
```powershell
# Pull all subscriber data
Eq12Cli.exe gas-pull Subscribers --output json

# Pull specific range
Eq12Cli.exe gas-pull Arbitrage_Opportunities --range A1:H100 --output csv
```

### Push Data to Sheets
```powershell
# Push arbitrage opportunities table
Eq12Cli.exe gas-push arbitrage_opportunities Arbitrage_Opportunities --clear

# Append new subscribers
Eq12Cli.exe gas-push new_signups Subscribers --append
```

### Send Newsletters
```powershell
# Daily newsletter to all subscribers
Eq12Cli.exe gas-newsletter daily --template YOUR_TEMPLATE_ID --segment all

# Weekly newsletter to premium only
Eq12Cli.exe gas-newsletter weekly --template YOUR_TEMPLATE_ID --segment premium

# Test newsletter (small group)
Eq12Cli.exe gas-newsletter daily --template YOUR_TEMPLATE_ID --test
```

### Run Mail Merge Campaigns
```powershell
# Generic promotion campaign
Eq12Cli.exe gas-mailmerge promotion --template YOUR_TEMPLATE_ID --segment premium --name "January_Promo"

# Newsletter campaign
Eq12Cli.exe gas-mailmerge newsletter --type weekly --segment all
```

### Execute Triggers
```powershell
# Run daily digest trigger
Eq12Cli.exe gas-run-trigger digest --frequency daily

# Execute monthly backup
Eq12Cli.exe gas-run-trigger backup --frequency monthly
```

### Analytics and Tracking
```powershell
# Get campaign performance metrics
Eq12Cli.exe gas-analytics 12345 --days 30 --export

# Check recent campaigns
Eq12Cli.exe gas-analytics --recent 10
```

## Monetization Workflows

### 1. Daily Newsletter Automation
```powershell
# Automated via Windows Task Scheduler
Eq12Cli.exe gas-newsletter daily --template daily_template --segment all
```

### 2. Affiliate Promotion Campaigns
```powershell
# Targeted promotion with Bitly tracking
Eq12Cli.exe gas-mailmerge promotion --template promo_template --segment high_value --link "https://affiliate.example.com/signup"
```

### 3. Premium Upsell Sequences
```powershell
# Weekly premium-focused content
Eq12Cli.exe gas-newsletter weekly --template premium_template --segment all
```

## Security Considerations

1. **Shared Secret Protection**
   - Store in environment variables, not code
   - Rotate regularly (monthly recommended)
   - Use strong cryptographic random generation

2. **API Quotas and Limits**
   - Gmail: 1 billion quota units per day
   - Sheets: 300 requests per minute per project
   - Monitor usage via GAS dashboard

3. **Data Privacy**
   - Subscriber data encrypted in transit (HTTPS)
   - No sensitive data logged in plain text
   - Respect unsubscribe requests immediately

## Troubleshooting

### Common Issues

1. **"Authentication Failed"**
   - Verify shared secret matches in both GAS and config.json
   - Check Web App permissions (Anyone can access)

2. **"Quota Exceeded"**
   - Check Google Apps Script quotas
   - Implement rate limiting in VB.NET client

3. **"Template Not Found"**
   - Verify Google Docs template ID in config
   - Ensure template is publicly readable or shared with GAS account

### Debug Commands
```powershell
# Test GAS connectivity
Eq12Cli.exe gas-run-trigger health

# Verify authentication
Eq12Cli.exe gas-pull ActivityLog --range A1:A1

# Check recent errors
sqlite3 Data/eq12_terminal.db "SELECT * FROM gas_logs WHERE success = 0 ORDER BY timestamp DESC LIMIT 10;"
```

## Performance Optimization

1. **Batch Operations**: Group multiple sheet operations into single requests
2. **Caching**: Cache template and subscriber data locally when possible
3. **Async Processing**: Use VB.NET async/await for all HTTP operations
4. **Retry Logic**: Implement exponential backoff for failed requests

## Revenue Attribution

The system tracks revenue through multiple channels:
- **Bitly Click Tracking**: Monitor affiliate link clicks
- **Email Open Tracking**: Estimate engagement rates
- **Conversion Attribution**: Link signups to specific campaigns
- **Premium Upgrades**: Track upsells from newsletter CTAs

## Future Enhancements

1. **Advanced Segmentation**: ML-based subscriber segmentation
2. **A/B Testing**: Template and subject line optimization
3. **Real-time Triggers**: Webhook-based event processing
4. **Cross-platform Sync**: Sync with other marketing platforms
5. **Advanced Analytics**: Revenue prediction and churn analysis

---

**Note**: This integration transforms EQ12 from a local terminal into a hybrid cloud system capable of automated content generation, email marketing, and revenue optimization at scale.
