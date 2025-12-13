
# EQ12 GODSTACK - Complete Intelligence Ecosystem

🚀 **Advanced multi-source search intelligence system with GPT enrichment, automated scheduling, and web dashboard management.**

## 🎯 Overview

EQ12 GODSTACK is a comprehensive intelligence gathering and analysis platform that combines:

- **Multi-Source Search Intelligence** - Dual-engine Bing + Google search with deduplication
- **Real-Time News Aggregation** - Bing News API + Google News RSS feeds
- **Swagbucks Offer Analysis** - Automated scraping and intelligence analysis  
- **GPT-Powered Enrichment** - OpenAI integration for intelligent content analysis
- **FastAPI Web Dashboard** - Local web interface for browsing and management
- **Automated Task Scheduling** - Windows Task Scheduler integration
- **Telegram Alert Integration** - Real-time notifications and reports

## 🛠️ Quick Start

### 1. Installation

```bash
# Clone or navigate to the GODSTACK directory
cd C:\EQ12\eq12_godstack2

# Run the automated setup
python setup.py
```

### 2. Configuration  

Edit `.env` file with your API keys:

```env
# Required for GPT enrichment
OPENAI_API_KEY=your_openai_api_key_here

# Required for search intelligence  
BING_SEARCH_API_KEY=your_bing_search_api_key_here

# Optional for enhanced search
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_custom_search_engine_id_here

# Required for Telegram alerts
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
```

### 3. Launch Dashboard

```bash
# Start the web dashboard
python dashboard.py

# Or use the launch script
launch_godstack.bat  # Windows
./launch_godstack.sh # Unix/Linux
```

Access dashboard at: **http://localhost:8000**

## 📊 System Components

### Core Intelligence Modules

| Module | Purpose | Key Features |
|--------|---------|--------------|
| `meta_search.py` | Multi-source search | Bing + Google dual-engine search with deduplication |
| `news_aggregator.py` | News collection | Real-time news from multiple APIs and RSS feeds |
| `swagbucks_offers.py` | Offer scraping | Automated Swagbucks offer collection and analysis |
| `enrichment.py` | GPT analysis | Stack-specific intelligence analysis with OpenAI |
| `autosuggest_merge.py` | Keyword generation | SEO keyword suggestions and query expansion |

### System Management

| Module | Purpose | Key Features |
|--------|---------|--------------|
| `dashboard.py` | Web interface | FastAPI dashboard for browsing and management |
| `task_scheduler.py` | Automation | Task execution controller for scheduled operations |
| `db.py` | Data persistence | SQLite database with comprehensive schema |
| `alert_pipe.py` | Notifications | Telegram integration for alerts and reports |

### Task Scheduler Integration

| Task | Schedule | Purpose |
|------|----------|---------|
| Daily Collection | 8:00 AM daily | News aggregation, offers scraping, GPT enrichment |
| Hourly Updates | Every hour from 9 AM | Meta search and autosuggest generation |
| Dashboard Server | On system startup | Auto-start web interface |

## 🚀 Usage Examples

### Manual Execution

```bash
# Run daily collection sequence
python task_scheduler.py --daily

# Execute specific components
python news_aggregator.py --query "tech news"
python swagbucks_offers.py --auto
python enrichment.py --stack betting --hours 24

# Run custom meta search
python meta_search.py --query "artificial intelligence trends"
```

### Dashboard Operations

1. **Browse Results**: Navigate search results with pagination and filtering
2. **View Offers**: Browse Swagbucks offers with category filtering  
3. **Search Interface**: Execute custom searches across all sources
4. **Analytics View**: Visualize query patterns and source distribution
5. **Tools Panel**: Execute operations and monitor system health

### API Integration

```python
# FastAPI endpoints for programmatic access
GET /results?query=ai&source=bing&hours=24    # Search results
GET /offers?category=shopping                  # Swagbucks offers  
POST /api/run/enrichment                       # Trigger GPT analysis
GET /api/database/status                       # System health check
```

## 🧠 Intelligence Analysis

### Stack Detection

The enrichment engine automatically detects business stacks and applies specialized analysis:

- **Betting Stack**: Odds analysis, betting trends, risk assessment
- **Travel Stack**: Destination insights, booking opportunities, pricing trends  
- **Cannabis Stack**: Market analysis, regulatory updates, investment opportunities
- **Finance Stack**: Market trends, investment insights, economic indicators
- **Fleet Stack**: Logistics optimization, fuel trends, route analysis

### GPT Enrichment Features

- **Automated Content Analysis**: Smart categorization and sentiment analysis
- **Stack-Specific Prompts**: Tailored analysis for each business domain  
- **Trend Identification**: Pattern recognition across search results
- **Investment Insights**: Financial opportunity identification
- **Risk Assessment**: Automated risk evaluation and scoring

## 📱 Telegram Integration

### Alert Types

- **Daily Summaries**: Comprehensive daily intelligence reports
- **Enrichment Results**: GPT analysis findings with insights
- **System Status**: Task execution status and error notifications
- **Offer Alerts**: High-value Swagbucks opportunities

### Alert Format

```
🚀 EQ12 GODSTACK Daily Summary
📊 Collected: 150 news articles, 25 offers
🧠 GPT Analysis: 5 betting insights, 3 travel opportunities  
⚠️ Alerts: 2 high-value offers detected
```

## 🗄️ Database Schema

### Core Tables

- **`results`**: Search results with metadata and deduplication
- **`offers`**: Swagbucks offers with reward and category data
- **`news_articles`**: News content with sentiment analysis
- **`enrichment_analysis`**: GPT analysis results and insights
- **`autosuggest_data`**: SEO keywords and query expansions

### Data Retention

- **Search Results**: 30 days rolling retention
- **Offers**: 7 days for active offers tracking  
- **News Articles**: 14 days for trend analysis
- **Enrichment Analysis**: 60 days for historical insights

## ⚙️ Configuration

### Environment Variables

```env
# Core Configuration
META_DB_PATH=meta_search.sqlite3
DASHBOARD_HOST=127.0.0.1
DASHBOARD_PORT=8000
LOG_LEVEL=INFO

# Auto-execution Settings  
AUTO_ENRICHMENT=true
AUTO_TELEGRAM_ALERTS=true
MAX_RESULTS_PER_QUERY=20
```

### Advanced Settings

- **Search Engine Priority**: Configure Bing vs Google preference
- **Enrichment Triggers**: Set conditions for automatic GPT analysis
- **Alert Thresholds**: Define criteria for high-priority notifications
- **Rate Limiting**: Control API usage and request frequency

## 🔧 Management Commands

### Task Scheduler Management

```powershell
# Install automated tasks
powershell -ExecutionPolicy Bypass -File Install-GODSTACKTasks.ps1 -Install

# View task status  
powershell -ExecutionPolicy Bypass -File Install-GODSTACKTasks.ps1 -List

# Manual task execution
schtasks /run /tn "EQ12 GODSTACK Daily Collection"
```

### Database Management

```bash
# Check database status
python -c "import db; db.get_stats()"

# Cleanup old data
python dashboard.py  # Use /api/database/cleanup endpoint
```

### System Health Monitoring

```bash
# View recent logs
tail -f logs/eq12_scheduler.log

# Check task execution reports
ls logs/task_report_*.json

# Monitor dashboard access
tail -f logs/dashboard.log  
```

## 📈 Performance Optimization

### Search Optimization

- **Result Deduplication**: Automatic duplicate removal across sources
- **Caching Strategy**: Intelligent caching of frequent queries
- **Parallel Execution**: Concurrent API calls for faster results
- **Rate Limiting**: Respectful API usage within provider limits

### Database Optimization

- **Indexing Strategy**: Optimized indexes for common query patterns
- **Data Archival**: Automatic cleanup of old data
- **Query Optimization**: Efficient SQL queries for large datasets
- **Connection Pooling**: Optimized database connections

## 🛡️ Security Considerations

### API Key Management

- Store sensitive keys in `.env` file (never commit)
- Use environment variables in production
- Rotate keys regularly for security
- Monitor API usage for anomalies

### Network Security

- Dashboard runs on localhost by default
- Use reverse proxy for external access
- Implement rate limiting for API endpoints
- Monitor access logs for suspicious activity

## 🚨 Troubleshooting

### Common Issues

**Dashboard won't start**:
```bash
# Check port availability
netstat -an | findstr :8000

# Check dependencies
pip install -r requirements.txt

# Check logs
tail -f logs/dashboard.log
```

**Task scheduler failures**:
```bash
# Check task status
python task_scheduler.py --list

# View error logs
type logs\task_report_*.json | findstr error

# Manual execution test
python news_aggregator.py --query test
```

**Database connection issues**:
```bash
# Reinitialize database
python -c "import db; db.init_db()"

# Check file permissions
ls -la meta_search.sqlite3
```

### Support Resources

- **Logs Directory**: `logs/` contains all execution logs
- **Task Reports**: `logs/task_report_*.json` for detailed execution data  
- **Dashboard API**: `http://localhost:8000/docs` for API documentation
- **Agent Integration**: See `AGENTS.md` for AI agent development specs

## 🎯 Advanced Features

### Custom Intelligence Stacks

Create custom business stack analysis by extending `enrichment.py`:

```python
def analyze_custom_stack(self, results: List[Dict]) -> Dict:
    """Custom stack analysis implementation"""
    prompt = """
    Analyze these results for custom business intelligence:
    - Key market trends
    - Competitive insights  
    - Growth opportunities
    """
    return self.enrich_with_gpt(results, prompt, "custom")
```

### Webhook Integration

Extend `alert_pipe.py` for custom webhook notifications:

```python
def send_webhook_alert(self, webhook_url: str, data: Dict):
    """Send alert to custom webhook endpoint"""
    requests.post(webhook_url, json=data)
```

### Custom Search Sources

Add new search providers in `clients.py`:

```python
class CustomSearchClient:
    """Custom search provider integration"""
    def search(self, query: str) -> List[Dict]:
        # Implementation for custom search API
        pass
```

## 📝 Development

### Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-intelligence-module`
3. Add tests for new functionality  
4. Follow EQ12 coding standards (see `AGENTS.md`)
5. Submit pull request with clear description

### Testing

```bash
# Run unit tests
python -m pytest tests/

# Integration tests
python test_integration.py

# Load testing
python benchmark_dashboard.py
```

---

**🚀 EQ12 GODSTACK - Where Intelligence Meets Automation**

*Built for the EQ12 ecosystem - Empowering data-driven decisions through intelligent automation.*

## Components
- `clients.py` — Bing + Google API wrappers (web, news, autosuggest).
- `db.py` — SQLite with tables `results` and `offers`.
- `alert_pipe.py` — Telegram glue.
- `meta_search.py` — dual-engine web search (Google CSE + Bing) with dedupe + DB + optional Telegram.
- `news_aggregator.py` — **Bing News API** + **Google News RSS** → DB.
- `swagbucks_offers.py` — Playwright scraper for Swagbucks public offers → DB + Telegram optional.
- `autosuggest_merge.py` — merges Bing + Google autosuggest for SEO/keyword generation.

## Install (Windows / EQ12)
```powershell
py -3 -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
# Playwright browsers (for swagbucks scraping)
python -m playwright install chromium
```
Copy `.env.example` → `.env` and fill:
- `BING_KEY` (+ optional `BING_NEWS_ENDPOINT` override)
- `GOOGLE_KEY`, `GOOGLE_CSE_ID`
- `TG_TOKEN`, `TG_CHAT_ID` (optional)
- `META_DB_PATH` (optional path to .sqlite3)

## Usage
**Web search (dual):**
```powershell
python meta_search.py --query "Buffalo dispensary news" --telegram --show-latest
```

**News (Bing News + Google News RSS):**
```powershell
python news_aggregator.py --query "NHL injuries" 
```

**Swagbucks offers (public pages):**
```powershell
python swagbucks_offers.py --telegram
```

**Autosuggest merge (SEO/keywords):**
```powershell
python autosuggest_merge.py --query "Buffalo cheap flights" --json
```

## Scheduling (Task Scheduler)
Create daily jobs similar to:
```powershell
schtasks /create /sc hourly /mo 1 /tn "EQ12_Godstack_News" /tr "`"%CD%\.venv\Scripts\python.exe`" `"%CD%\news_aggregator.py`" --query-file queries_news.txt"
schtasks /create /sc daily /st 06:00 /tn "EQ12_Godstack_Swagbucks" /tr "`"%CD%\.venv\Scripts\python.exe`" `"%CD%\swagbucks_offers.py`" --telegram"
```

## Notes / Ethics
- Respect provider TOS. Swagbucks scraping targets **public offer lists** only. Avoid automating login or rewards workflows.
- Google News API is not public; we use **RSS**, which is allowed. For web search, we use **Google CSE**.
- For richer ranking, add your LLM step after DB insert to score and filter results per stack.
