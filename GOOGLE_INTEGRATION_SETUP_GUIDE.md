# EQ12 Google Integration Setup Guide

Complete setup guide for Google Drive + DocHub PDF editing and Google Sheets + AppSheet low-code app integration.

## 🚀 Overview

The EQ12 Google ecosystem integration enables:

- **Google Drive**: Automated PDF report uploads with DocHub editing workflows
- **Google Sheets**: Real-time database synchronization with AppSheet mobile app creation
- **DocHub**: Professional PDF editing and digital signature capabilities
- **AppSheet**: No-code mobile and web apps from EQ12 data for premium subscribers

## 📋 Prerequisites

### 1. Google Cloud Console Setup

1. **Create Google Cloud Project**
   ```
   - Go to https://console.cloud.google.com/
   - Click "New Project" or select existing project
   - Note the Project ID for later use
   ```

2. **Enable Required APIs**
   ```
   Enable these APIs in your Google Cloud project:
   - Google Drive API
   - Google Sheets API
   - Google Apps Script API (optional for advanced automation)
   ```

3. **Create OAuth2 Credentials**
   ```
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client ID"
   - Application type: "Desktop application"
   - Name: "EQ12 Sports Betting Terminal"
   - Download the JSON credentials file
   ```

### 2. Google Drive Setup

1. **Create EQ12 Reports Folder**
   ```
   - Create a new folder in Google Drive: "EQ12 Reports"
   - Share the folder with appropriate permissions
   - Note the Folder ID from the URL:
     https://drive.google.com/drive/folders/{FOLDER_ID}
   ```

### 3. Google Sheets Setup

1. **Create EQ12 Data Spreadsheet**
   ```
   - Create a new Google Sheets spreadsheet: "EQ12 Sports Data"
   - Note the Spreadsheet ID from the URL:
     https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit
   ```

## ⚙️ Configuration Setup

### 1. Update config.json

Add Google integration settings to your `Config/config.json`:

```json
{
  "google_drive": {
    "client_id": "YOUR_GOOGLE_CLIENT_ID",
    "client_secret": "YOUR_GOOGLE_CLIENT_SECRET",
    "redirect_uri": "http://localhost:8080/callback",
    "token_path": "Config/google_tokens.json",
    "folder_id": "YOUR_GOOGLE_DRIVE_FOLDER_ID",
    "scope": "https://www.googleapis.com/auth/drive.file"
  },
  "google_sheets": {
    "sheet_id": "YOUR_GOOGLE_SPREADSHEET_ID",
    "scope": "https://www.googleapis.com/auth/spreadsheets"
  },
  "dochub": {
    "base_url": "https://dochub.com/edit/",
    "integration_method": "direct_link"
  },
  "appsheet": {
    "app_id": "YOUR_APPSHEET_APP_ID",
    "webhook_url": "YOUR_APPSHEET_WEBHOOK_URL",
    "sync_method": "webhook",
    "auto_sync": true
  }
}
```

### 2. OAuth2 Client Credentials

From your downloaded Google Cloud credentials JSON:

```json
{
  "installed": {
    "client_id": "123456789-abcdef.apps.googleusercontent.com",
    "client_secret": "YOUR_CLIENT_SECRET",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "redirect_uris": ["http://localhost:8080/callback"]
  }
}
```

Extract `client_id` and `client_secret` for your config.json.

## 🔐 Authentication Flow

### 1. Initial OAuth2 Setup

```bash
# Test Google Drive connection (starts OAuth flow)
.\Eq12Cli.exe test-google-drive

# Test Google Sheets connection
.\Eq12Cli.exe test-google-sheets
```

**First-time authentication process:**

1. CLI opens browser to Google OAuth consent screen
2. Sign in with your Google account
3. Grant permissions for Drive and Sheets access
4. Browser redirects to localhost callback
5. CLI captures authorization code and exchanges for tokens
6. Tokens saved to `Config/google_tokens.json` for future use

### 2. Token Management

- **Access tokens**: Valid for 1 hour, automatically refreshed
- **Refresh tokens**: Long-lived, used to get new access tokens
- **Token storage**: Encrypted JSON file with automatic backup
- **Token refresh**: Automatic background refresh when needed

## 📤 Google Drive + DocHub Workflow

### 1. Upload Reports to Drive

```bash
# Upload single PDF report
.\Eq12Cli.exe upload-report --file="Reports\Daily_Report_2024-01-15.pdf"

# Upload with custom filename
.\Eq12Cli.exe upload-report --file="Reports\report.pdf" --name="EQ12_Analysis_Jan15"
```

**Upload workflow includes:**
- File upload to Google Drive folder
- Generate DocHub editing URL
- Create shareable Google Drive link
- Bitly URL shortening (if configured)
- Database logging with complete audit trail

### 2. DocHub PDF Editing

**Generated URLs provide:**
- **DocHub Edit URL**: Direct link to DocHub PDF editor
- **Google Drive View**: Standard Google Drive preview
- **Bitly Short URLs**: Branded short links for sharing

**DocHub capabilities:**
- Digital signature insertion
- Form field completion
- Annotation and markup
- Comment and review workflows
- Export to multiple formats

### 3. Database Tracking

All uploads logged to `drive_uploads` table:
```sql
CREATE TABLE drive_uploads (
  id INTEGER PRIMARY KEY,
  ts TEXT DEFAULT (datetime('now')),
  local_path TEXT NOT NULL,     -- Original file path
  drive_id TEXT NOT NULL,       -- Google Drive file ID
  file_name TEXT NOT NULL,      -- Display name in Drive
  dochub_url TEXT,              -- DocHub editing URL
  dochub_bitly_url TEXT,        -- Bitly shortened DocHub URL
  shareable_url TEXT,           -- Google Drive shareable URL
  shareable_bitly_url TEXT,     -- Bitly shortened shareable URL
  created_at TEXT DEFAULT (datetime('now'))
);
```

## 📊 Google Sheets + AppSheet Workflow

### 1. Database Synchronization

```bash
# Sync specific table (incremental)
.\Eq12Cli.exe sync-sheets --table=events

# Full sync (replaces existing data)
.\Eq12Cli.exe sync-sheets --table=bets --full

# Sync multiple key tables
.\Eq12Cli.exe sync-sheets
```

**Default sync tables:**
- `events`: Game/match data with teams, dates, scores
- `bets`: Placed bets with odds, stakes, results
- `arbitrage`: Detected arbitrage opportunities
- `deliverables`: Content deliverables and reports
- `bitly_stats`: URL shortening statistics

### 2. Sync Process Details

**Incremental Sync (default):**
- Only syncs new/updated records since last sync
- Appends data to existing Google Sheets tabs
- Preserves manual edits in sheets
- Faster execution for large datasets

**Full Sync:**
- Replaces entire sheet content
- Includes header row with column names
- Overwrites any manual sheet modifications
- Complete data refresh

### 3. AppSheet Integration

**Automatic sync triggers:**
- Webhook notifications to AppSheet after each sync
- Real-time data updates in mobile apps
- Push notifications for critical updates
- Scheduled sync automation

**AppSheet app capabilities:**
- Interactive dashboards from EQ12 data
- Mobile-first betting analysis tools
- Real-time arbitrage opportunity alerts
- Custom workflow automation
- Premium subscriber features

## 🛠️ Command Reference

### Testing Commands

```bash
# Test Google Drive API connectivity
.\Eq12Cli.exe test-google-drive

# Test Google Sheets API connectivity
.\Eq12Cli.exe test-google-sheets
```

### Google Drive Commands

```bash
# Upload report with full workflow
.\Eq12Cli.exe upload-report --file="path/to/report.pdf"

# Upload to specific folder
.\Eq12Cli.exe upload-report --file="report.pdf" --folder="FOLDER_ID"
```

### Google Sheets Commands

```bash
# Sync specific table (incremental)
.\Eq12Cli.exe sync-sheets --table=TABLE_NAME

# Full sync (replace all data)
.\Eq12Cli.exe sync-sheets --table=TABLE_NAME --full

# Sync multiple default tables
.\Eq12Cli.exe sync-sheets
```

## 🔍 Troubleshooting

### Common Issues

**1. OAuth2 Authentication Errors**
```
Error: Invalid client credentials
Solution:
- Verify client_id and client_secret in config.json
- Check OAuth consent screen configuration
- Ensure redirect URI matches exactly
```

**2. Token Expiration**
```
Error: Token has expired
Solution:
- Automatic refresh should handle this
- Delete Config/google_tokens.json to force re-auth
- Check refresh token validity
```

**3. Permission Errors**
```
Error: Insufficient permissions
Solution:
- Verify API scopes in OAuth consent screen
- Check Google Drive folder sharing permissions
- Ensure Google Sheets write access
```

**4. File Upload Failures**
```
Error: Upload failed
Solution:
- Check file size limits (Google Drive: 5TB max)
- Verify MIME type support
- Ensure stable internet connection
- Check Google Drive storage quota
```

### Debugging Steps

1. **Enable Verbose Logging**
   ```bash
   .\Eq12Cli.exe test-google-drive --verbose
   ```

2. **Check Token Status**
   ```
   Look for Config/google_tokens.json file
   Verify token expiration timestamps
   Check refresh token presence
   ```

3. **Validate Configuration**
   ```
   Run: python validate_google_integration.py
   Check all required config sections present
   Verify API credentials format
   ```

4. **Test API Connectivity**
   ```bash
   # Test basic Google Drive access
   .\Eq12Cli.exe test-google-drive

   # Test Google Sheets access
   .\Eq12Cli.exe test-google-sheets
   ```

## 📈 Production Deployment

### 1. Security Considerations

- **Token Storage**: Encrypt google_tokens.json in production
- **Client Secrets**: Use environment variables for sensitive data
- **Access Logging**: Monitor all API calls and access patterns
- **Rate Limiting**: Implement exponential backoff for API calls

### 2. Monitoring and Alerts

```sql
-- Monitor sync performance
SELECT
  table_name,
  COUNT(*) as sync_count,
  AVG(record_count) as avg_records,
  MAX(synced_at) as last_sync
FROM sheet_syncs
GROUP BY table_name;

-- Monitor upload activity
SELECT
  DATE(created_at) as upload_date,
  COUNT(*) as upload_count,
  SUM(file_size) as total_size_bytes
FROM drive_uploads
GROUP BY DATE(created_at)
ORDER BY upload_date DESC;
```

### 3. Automation Setup

**Windows Task Scheduler:**
```xml
<!-- Daily sync automation -->
<Task>
  <Actions>
    <Exec>
      <Command>C:\EQ12\visual_studio_projects\EQ12SportsBettingTerminal\Eq12Cli.exe</Command>
      <Arguments>sync-sheets</Arguments>
    </Exec>
  </Actions>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2024-01-01T09:00:00</StartBoundary>
      <DaysInterval>1</DaysInterval>
    </CalendarTrigger>
  </Triggers>
</Task>
```

## 💰 Premium Subscriber Features

### 1. Enhanced PDF Workflows

- **Automated Report Generation**: Daily/weekly reports with DocHub editing
- **Digital Signature Integration**: Streamlined document signing
- **Custom Branding**: Personalized report templates
- **Advanced Analytics**: Enhanced reporting with ML insights

### 2. AppSheet Mobile Apps

- **Real-time Dashboards**: Live betting data and analytics
- **Push Notifications**: Instant arbitrage opportunity alerts
- **Offline Capability**: Mobile access without internet
- **Custom Workflows**: Personalized betting strategies

### 3. Advanced Integrations

- **Multi-tenant Support**: Separate data spaces for different users
- **API Access**: Direct data access for custom applications
- **Webhook Integration**: Real-time data feeds for external systems
- **Advanced Permissions**: Role-based access control

## 📞 Support

For technical support:
1. Check troubleshooting section above
2. Run validation script: `python validate_google_integration.py`
3. Review logs in `Logs/` directory
4. Check Google Cloud Console for API quotas and errors

---

**Next Steps After Setup:**
1. Complete OAuth2 authentication flow
2. Test file upload with sample report
3. Test database sync with sample data
4. Set up AppSheet app with synced data
5. Configure automated daily sync schedule
6. Implement premium subscriber features
