# EQ12 Intelligent URL Learning System

## Overview

The EQ12 Intelligent URL Learning System is an AI-powered automation tool that automatically scans, analyzes, and learns from URLs submitted to Copilot or the EQ12 system. It intelligently categorizes c## 🧠 AI Classification System

### GPT-5 Enhanced Intelligence
The URL learning system now supports the latest OpenAI models including:

- **GPT-5**: Latest and most advanced model (when available)
- **o1-preview**: Advanced reasoning model for complex analysis
- **GPT-4 Turbo**: High-performance GPT-4 with latest features
- **o1-mini**: Fast reasoning model for quick classification
- **GPT-4**: Standard high-quality model
- **GPT-3.5 Turbo**: Reliable fallback model

### Model Selection Strategy
The system automatically selects the best available model:
1. **Environment Override**: `EQ12_OPENAI_MODEL` environment variable
2. **Auto-Detection**: Tests model availability and selects highest-tier available
3. **Graceful Fallback**: Falls back to lower-tier models if needed
4. **Configuration-Driven**: Uses `ai_enhanced_config.json` for preferences

### Supported Categories
- **Betting**: Sports betting, odds, parlays, gambling content
- **Automation**: Scripts, bots, automation tools, APIs
- **Finance**: Stocks, crypto, trading, investment data
- **AI**: Machine learning, AI models, GPT, techniques
- **Dashboard**: Analytics, dashboards, monitoring tools
- **Config**: Configuration, settings, environment variables
- **Data**: Data processing, databases, exports, importsnerates insights, and automatically updates relevant EQ12 folders based on the learned information.

## 🎯 Key Features

### Intelligent URL Processing
- **Automatic URL Detection**: Detects URLs in Copilot messages and text inputs
- **Multi-Method Content Extraction**: Uses httpx, Playwright, and feed parsing
- **GPT-5 Enhanced Classification**: Advanced AI categorization using GPT-5, o1-preview, and GPT-4 Turbo
- **Smart Content Analysis**: Extracts code snippets, API endpoints, configuration data
- **Advanced Reasoning**: Uses latest OpenAI models for superior content understanding

### Learning and Adaptation
- **Dynamic Learning**: Generates insights from scanned content
- **Category-Specific Analysis**: Specialized processing for betting, automation, finance, AI content
- **Confidence Scoring**: Applies confidence thresholds for automatic actions
- **Historical Tracking**: Maintains database of all scans and insights

### EQ12 Integration
- **Automatic Folder Updates**: Updates relevant EQ12 folders based on learned content
- **Configuration Management**: Adds new API endpoints, sportsbook sources, etc.
- **Dashboard Integration**: Real-time monitoring via EQ12 Unified Dashboard
- **Webhook API**: RESTful API for external integrations

### Copilot Integration
- **Real-Time Processing**: Automatically processes URLs when submitted to Copilot
- **Background Processing**: Non-blocking URL analysis
- **Batch Operations**: Handles multiple URLs simultaneously
- **Context Awareness**: Uses submission context for better classification

## 🏗️ Architecture

### Core Components

#### 1. URL Scanner (`eq12_url_scanner.py`)
- **Content Extraction**: Multi-method URL content retrieval
- **AI Classification**: Intelligent content categorization
- **Insight Generation**: Learning system with confidence scoring
- **Database Management**: SQLite storage for scans, insights, and updates

#### 2. Copilot Handler (`eq12_copilot_url_handler.py`)
- **URL Detection**: Pattern-based URL extraction from text
- **Webhook Server**: FastAPI server for real-time integration
- **Batch Processing**: Efficient handling of multiple URLs
- **Status Tracking**: Comprehensive processing statistics

#### 3. Dashboard Integration
- **Real-Time Status**: Live monitoring of scanning activity
- **API Endpoints**: RESTful interface for system control
- **WebSocket Updates**: Live data streaming to dashboard
- **Historical Analytics**: Processing trends and statistics

#### 4. Management Tools
- **PowerShell Scripts**: Complete system management and monitoring
- **Setup Automation**: One-click installation and configuration
- **Health Monitoring**: System status and performance tracking
- **Testing Framework**: Comprehensive functionality validation

### Data Flow

```
URL Submission → Content Extraction → AI Classification → Insight Generation → EQ12 Updates
     ↓                ↓                      ↓                  ↓               ↓
  Copilot/API    Multi-Method       OpenAI/HuggingFace   Learning Engine   Folder Updates
     ↓            Scraping              Models             Database         File Creation
  Detection         ↓                      ↓                  ↓               ↓
     ↓         httpx/Playwright      Classification     Confidence Scoring  Config Updates
Dashboard      BeautifulSoup          Categories         Action Planning    Data Files
Monitoring     Feed Parsing          Structured Data       Automation       References
```

## 🚀 Installation

### Quick Setup
```powershell
# Navigate to EQ12 directory
cd C:\EQ12

# Run complete setup (installs dependencies and initializes system)
.\scripts\eq12_url_system_setup.ps1 -TestAfterSetup

# Start the URL learning system
.\scripts\eq12_url_manager.ps1 -Action start
```

### Manual Installation
```powershell
# Install Python dependencies
pip install -r requirements_url_system.txt

# Install Playwright browsers
python -m playwright install chromium --with-deps

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"

# Initialize database
python scripts/eq12_url_scanner.py

# Start webhook server
python scripts/eq12_copilot_url_handler.py
```

### Environment Configuration
```bash
# Optional: Set API keys for enhanced functionality
export OPENAI_API_KEY="your_openai_api_key"
export ODDS_API_KEY="your_odds_api_key"
export TELEGRAM_BOT_TOKEN="your_telegram_token"

# System configuration
export EQ12_URL_SCANNER_LOG_LEVEL="INFO"
export EQ12_URL_HANDLER_PORT="8080"
```

## 📖 Usage

### Automatic Processing (Copilot Integration)
When you paste URLs in Copilot or submit them via the API, the system automatically:

1. **Detects URLs** in your message or input
2. **Extracts content** using multiple methods (httpx, Playwright, feed parsing)
3. **Classifies content** using AI models (OpenAI GPT, Hugging Face)
4. **Generates insights** specific to EQ12 categories
5. **Updates folders** with relevant information automatically

### Manual URL Submission
```powershell
# Test with a specific URL
.\scripts\eq12_url_manager.ps1 -Action test -TestUrl "https://fastapi.tiangolo.com/"

# Submit via API
curl -X POST "http://localhost:8080/webhook/url" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com", "source": "manual", "context": "Testing submission"}'
```

### System Management
```powershell
# Start the system
.\scripts\eq12_url_manager.ps1 -Action start

# Check status
.\scripts\eq12_url_manager.ps1 -Action status

# Stop the system
.\scripts\eq12_url_manager.ps1 -Action stop

# Restart with force
.\scripts\eq12_url_manager.ps1 -Action restart -Force
```

### GPT-5 Enhanced Features
```powershell
# Test GPT-5 availability and configuration
python scripts/eq12_gpt5_manager.py --test-gpt5

# Test enhanced URL analysis with GPT-5
python scripts/eq12_gpt5_manager.py --enhanced-test "https://fastapi.tiangolo.com"

# Configure preferred model
python scripts/eq12_gpt5_manager.py --configure --model gpt-5

# Set model via environment variable
$env:EQ12_OPENAI_MODEL = "gpt-5"

# View GPT-5 usage guide
python scripts/eq12_gpt5_manager.py --usage-guide
```

## 🔧 Configuration

### Scanner Configuration (`configs/url_scanner_config.json`)
```json
{
  "scanner_settings": {
    "max_content_length": 10000,
    "request_timeout": 30,
    "max_retries": 3,
    "enable_playwright": true,
    "enable_ai_classification": true
  },
  "classification_thresholds": {
    "minimum_confidence": 0.1,
    "high_confidence": 0.7,
    "auto_apply_threshold": 0.8
  }
}
```

### Handler Configuration (`configs/url_handler_config.json`)
```json
{
  "webhook_settings": {
    "host": "127.0.0.1",
    "port": 8080,
    "log_level": "info",
    "enable_cors": true
  },
  "processing_settings": {
    "batch_size": 10,
    "concurrent_limit": 3,
    "cache_duration_hours": 24
  }
}
```

## 📊 API Reference

### Webhook Endpoints

#### Submit Single URL
```http
POST /webhook/url
Content-Type: application/json

{
  "url": "https://example.com",
  "source": "copilot",
  "context": "User submitted this URL for analysis"
}
```

#### Submit Copilot Message
```http
POST /webhook/copilot
Content-Type: application/json

{
  "content": "Check out https://fastapi.tiangolo.com/ and github.com/microsoft/playwright",
  "user": "username",
  "channel": "general"
}
```

#### Get System Status
```http
GET /status
```

#### Get Recent Submissions
```http
GET /recent-submissions
```

### Dashboard API Integration

#### URL Scanner Status
```http
GET /api/url-scanner/status
```

#### Submit URL via Dashboard
```http
POST /api/url-scanner/submit
Content-Type: application/json

{
  "url": "https://example.com",
  "context": "Dashboard submission",
  "source": "dashboard"
}
```

#### Get Scanner Insights
```http
GET /api/url-scanner/insights
```

#### Get EQ12 Updates
```http
GET /api/url-scanner/updates
```

## 🧠 AI Classification System

### Supported Categories
- **Betting**: Sports betting, odds, parlays, gambling content
- **Automation**: Scripts, bots, automation tools, APIs
- **Finance**: Stocks, crypto, trading, investment data
- **AI**: Machine learning, AI models, GPT, techniques
- **Dashboard**: Analytics, dashboards, monitoring tools
- **Config**: Configuration, settings, environment variables
- **Data**: Data analysis, databases, exports, imports

### Classification Methods

#### 1. Keyword-Based Classification
```python
categories = {
    "betting": ["bet", "odds", "sportsbook", "parlay", "gambling"],
    "automation": ["automation", "script", "bot", "scraper", "api"],
    "finance": ["stock", "crypto", "portfolio", "investment", "trading"]
}
```

#### 2. AI-Powered Classification (OpenAI)
```python
prompt = """
Classify this content into EQ12 categories:
- betting, automation, finance, ai, dashboard, config, data

Content: {content}
Respond with: "category confidence"
"""
```

#### 3. Transformer Models (Hugging Face)
```python
classifier = pipeline("text-classification", model="facebook/bart-large-mnli")
result = classifier(content, ["This is about betting", "This is about automation"])
```

## 📁 EQ12 Folder Update System

### Automatic Updates
The system automatically updates EQ12 folders based on classified content:

#### Betting Content
- **Location**: `EdgeGodParlays/`, `scripts/`, `scraper_starter/`
- **Updates**: New sportsbook sources, betting strategies, odds APIs
- **Files**: `sportsbook_sources.json`, strategy references

#### Automation Content
- **Location**: `scripts/`, `omni_scraper/`, `modules/`
- **Updates**: New API endpoints, automation scripts, bot configurations
- **Files**: `api_endpoints.json`, script templates

#### Finance Content
- **Location**: `data/`, `configs/`
- **Updates**: Financial data sources, market APIs, trading tools
- **Files**: Data source configurations, market feed URLs

#### AI Content
- **Location**: `openai-python-project/`, `scripts/`
- **Updates**: AI model references, API configurations, techniques
- **Files**: Model documentation, API examples

#### Configuration Content
- **Location**: `configs/`
- **Updates**: Environment variables, API keys, configuration templates
- **Files**: `config_template.env`, API configurations

### Update Types
- **Create**: New files with extracted information
- **Append**: Add to existing JSON arrays or configuration files
- **Modify**: Update existing configuration templates
- **Reference**: Create markdown references with source URLs

## 📊 Database Schema

### URL Scans Table
```sql
CREATE TABLE url_scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    title TEXT,
    content_hash TEXT,
    classification TEXT,
    confidence REAL,
    scan_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    processing_time REAL,
    metadata TEXT,
    extracted_data TEXT,
    error TEXT
);
```

### Learning Insights Table
```sql
CREATE TABLE learning_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    insight_id TEXT UNIQUE NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    confidence REAL,
    source_url TEXT,
    applicable_folders TEXT,
    update_actions TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    applied BOOLEAN DEFAULT FALSE
);
```

### EQ12 Updates Table
```sql
CREATE TABLE eq12_updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    update_id TEXT UNIQUE NOT NULL,
    folder_path TEXT NOT NULL,
    update_type TEXT NOT NULL,
    file_name TEXT,
    content_hash TEXT,
    priority INTEGER DEFAULT 5,
    status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    applied_at DATETIME,
    metadata TEXT
);
```

## 🔍 Monitoring and Logging

### Log Files
- **Setup Log**: `C:\EQ12\logs\url_system_setup.log`
- **Scanner Log**: `C:\EQ12\logs\url_scanner.log`
- **Handler Log**: `C:\EQ12\logs\copilot_url_handler.log`
- **Manager Log**: `C:\EQ12\logs\url_manager.log`

### Dashboard Integration
The URL learning system is fully integrated with the EQ12 Unified Dashboard:

- **Real-Time Status**: Live monitoring of scanning activity
- **Processing Statistics**: Daily/weekly processing metrics
- **Insight Analytics**: Generated insights and applied updates
- **System Health**: Service status and performance metrics

### Performance Metrics
- **Scan Speed**: Average processing time per URL
- **Classification Accuracy**: AI model performance statistics
- **Update Success Rate**: Percentage of successful folder updates
- **Cache Hit Rate**: Efficiency of content caching system

## 🚨 Troubleshooting

### Common Issues

#### URL Scanner Not Starting
```powershell
# Check Python and dependencies
python --version
pip list | findstr "httpx fastapi beautifulsoup4"

# Reinstall dependencies
pip install -r requirements_url_system.txt

# Check logs
Get-Content "C:\EQ12\logs\url_scanner.log" -Tail 20
```

#### Webhook Server Connection Issues
```powershell
# Check if port is available
netstat -an | findstr "8080"

# Test server health
Invoke-RestMethod -Uri "http://localhost:8080/status"

# Check firewall settings
Get-NetFirewallRule -DisplayName "*8080*"
```

#### AI Classification Not Working
```powershell
# Check OpenAI API key
$env:OPENAI_API_KEY
echo $env:OPENAI_API_KEY

# Test API connection
python -c "from openai import OpenAI; client = OpenAI(); print('API Key valid')"

# Fallback to keyword classification (automatic)
```

#### Database Issues
```powershell
# Check database file
Test-Path "C:\EQ12\url_scanner.db"

# Reinitialize database
python -c "from scripts.eq12_url_scanner import EQ12URLScanner; EQ12URLScanner()"

# Check SQLite installation
sqlite3 --version
```

### Performance Optimization
- **Concurrent Processing**: Adjust `concurrent_limit` in configuration
- **Cache Settings**: Increase `cache_duration_hours` for frequently accessed URLs
- **Content Limits**: Reduce `max_content_length` for faster processing
- **AI Model Selection**: Use lighter models for better performance

## 🔒 Security Considerations

### API Security
- **Local Binding**: Webhook server binds to localhost by default
- **Input Validation**: All URLs and content are validated before processing
- **Rate Limiting**: Configurable processing limits to prevent abuse
- **Error Handling**: Comprehensive error handling prevents system crashes

### Data Privacy
- **Local Storage**: All data stored locally in SQLite database
- **Content Truncation**: Large content is truncated for storage efficiency
- **No External Sharing**: Processed content not shared with external services
- **API Key Security**: Environment variable storage for sensitive credentials

### Network Security
- **HTTPS Preferred**: Automatic HTTPS upgrade for HTTP URLs
- **User-Agent Rotation**: Prevents blocking by target servers
- **Request Timeouts**: Prevents hanging connections
- **Error Boundaries**: Isolated processing prevents system-wide failures

## 🔮 Future Enhancements

### Planned Features
- **Advanced AI Models**: Integration with GPT-4, Claude, and specialized models
- **Image Analysis**: OCR and image content extraction capabilities
- **Video Processing**: Extract information from video URLs (YouTube, etc.)
- **Multi-Language Support**: Content analysis in multiple languages
- **Advanced Caching**: Redis integration for high-performance caching

### Integration Improvements
- **Slack Integration**: Direct Slack bot for URL processing
- **Discord Bot**: Enhanced Discord integration with rich embeds
- **Email Processing**: Extract URLs from email content
- **Browser Extension**: Chrome/Firefox extension for one-click URL submission

### Analytics Enhancements
- **Machine Learning Pipeline**: Learn from user feedback and corrections
- **Trend Analysis**: Identify trending topics and content patterns
- **Recommendation Engine**: Suggest related URLs and content
- **Content Clustering**: Group related URLs and insights

## 📝 Contributing

### Development Setup
```powershell
# Clone development environment
git clone <repo> eq12-url-system
cd eq12-url-system

# Install development dependencies
pip install -r requirements_url_system.txt
pip install pytest black isort mypy

# Run tests
pytest tests/

# Code formatting
black scripts/
isort scripts/
```

### Testing Framework
```powershell
# Run all tests
pytest tests/ -v

# Test specific component
pytest tests/test_url_scanner.py -v

# Test with coverage
pytest tests/ --cov=scripts --cov-report=html
```

### Code Standards
- **Type Hints**: All functions should include type hints
- **Docstrings**: Comprehensive documentation for all classes/functions
- **Error Handling**: Robust error handling with logging
- **Testing**: Unit tests for all core functionality
- **Formatting**: Black code formatting, isort import organization

---

**EQ12 Intelligent URL Learning System v1.0.0**
*Automatic URL processing, AI-powered learning, and intelligent EQ12 integration*

For support and updates, check the EQ12 logs directory and dashboard integration.
