#  External Repository Integration Guide

##  Overview

This document catalogs all external repositories, APIs, and third-party integrations used in the EQ12 Expert Quantum environment. It provides setup instructions, API documentation links, and integration patterns.

##  Core External Dependencies

###  **AI/ML Platforms**

#### **OpenAI Platform**
- **Repository**: https://github.com/openai/openai-python
- **API Docs**: https://platform.openai.com/docs
- **Integration**: `scripts/` - GPT-4, Claude, embedding models
- **Environment Variables**:
  ```bash
  OPENAI_API_KEY=your-api-key
  OPENAI_SERVICE_KEY=your-service-key
  ```
- **Usage Pattern**:
  ```python
  from openai import OpenAI
  client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
  ```

#### **Anthropic Claude**
- **Repository**: https://github.com/anthropics/anthropic-sdk-python
- **API Docs**: https://docs.anthropic.com/
- **Integration**: Advanced reasoning, code analysis
- **Environment Variables**:
  ```bash
  ANTHROPIC_API_KEY=your-api-key
  ```

#### **Hugging Face Transformers**
- **Repository**: https://github.com/huggingface/transformers
- **Hub**: https://huggingface.co/models
- **Integration**: Local model hosting, fine-tuning
- **Models Used**: BERT, GPT variants, DistilBERT

###  **Data Sources & APIs**

#### **Sports Data APIs**
- **The Odds API**
  - **Website**: https://the-odds-api.com/
  - **Environment**: `ODDS_API_KEY=your-key`
  - **Usage**: Sports betting odds, live scores
  - **Integration**: `scripts/eq12_odds_*` files

#### **Financial Data**
- **Alpha Vantage**
  - **Website**: https://www.alphavantage.co/
  - **Environment**: `ALPHA_VANTAGE_KEY=your-key`
  - **Usage**: Stock data, forex, crypto prices
  
- **Yahoo Finance API**
  - **Repository**: https://github.com/ranaroussi/yfinance
  - **Usage**: Market data, historical prices
  - **Integration**: `scripts/financial_analysis_*`

#### **E-commerce & Affiliate**
- **eBay API**
  - **Developer Program**: https://developer.ebay.com/
  - **Environment**: `EBAY_APP_ID`, `EBAY_CERT_ID`
  - **Usage**: Product search, price monitoring
  
- **Amazon Product Advertising**
  - **Website**: https://webservices.amazon.com/paapi5/
  - **Usage**: Product search, affiliate tracking

###  **Development Tools & Platforms**

#### **GitHub Integration**
- **GitHub CLI**: https://cli.github.com/
- **GitHub Actions**: CI/CD workflows in `.github/workflows/`
- **Dependabot**: Automated dependency updates
- **CodeQL**: Security analysis
- **Environment Variables**:
  ```bash
  GITHUB_TOKEN=your-token
  CODECOV_TOKEN=your-codecov-token
  ```

#### **Docker Hub**
- **Registry**: https://hub.docker.com/
- **Images Used**:
  - `python:3.12-slim`
  - `postgres:15`
  - `redis:7-alpine`
  - `grafana/grafana:latest`
  - `jupyter/datascience-notebook`

#### **Google Cloud Platform**
- **AI Platform**: https://cloud.google.com/ai-platform
- **Environment Variables**:
  ```bash
  GOOGLE_KEY=your-api-key
  GOOGLE_CSE_ID=your-search-engine-id
  ```
- **Services**: Custom Search, AI Platform, Cloud Functions

###  **Monitoring & Analytics**

#### **Grafana Cloud**
- **Website**: https://grafana.com/
- **Integration**: Custom dashboards, alert management
- **Data Sources**: Prometheus, PostgreSQL, InfluxDB

#### **Prometheus**
- **Repository**: https://github.com/prometheus/prometheus
- **Website**: https://prometheus.io/
- **Integration**: Metrics collection, alerting rules

#### **SonarQube**
- **Website**: https://www.sonarqube.org/
- **Environment**: `SONAR_TOKEN=your-token`
- **Usage**: Code quality analysis, technical debt tracking

###  **Communication & Notifications**

#### **Telegram Bot API**
- **Documentation**: https://core.telegram.org/bots/api
- **Environment Variables**:
  ```bash
  TELEGRAM_BOT_TOKEN=your-bot-token
  TELEGRAM_CHAT_ID=your-chat-id
  TG_CHAT_ID=your-chat-id
  ```
- **Usage**: Automated notifications, alert routing

#### **Discord Webhooks**
- **Documentation**: https://discord.com/developers/docs/resources/webhook
- **Usage**: Development team notifications

###  **Security & Compliance**

#### **Bandit Security Linter**
- **Repository**: https://github.com/PyCQA/bandit
- **Usage**: Python security vulnerability scanning
- **Integration**: Pre-commit hooks, CI/CD pipeline

#### **Safety**
- **Repository**: https://github.com/pyupio/safety
- **Usage**: Python dependency vulnerability checking

#### **Gitleaks**
- **Repository**: https://github.com/gitleaks/gitleaks
- **Usage**: Secret scanning in git repositories
- **Integration**: `.github/workflows/gitleaks.yml`

###  **Browser Automation**

#### **Playwright**
- **Repository**: https://github.com/microsoft/playwright-python
- **Website**: https://playwright.dev/
- **Usage**: Web scraping, automated testing
- **Browsers**: Chromium, Firefox, WebKit

#### **Selenium WebDriver**
- **Repository**: https://github.com/SeleniumHQ/selenium
- **Usage**: Legacy browser automation
- **Integration**: `scripts/scraper_*` files

##  **Setup & Configuration**

###  **Environment Variables Setup**

Create a `.env` file based on `.env.example`:

```bash
# AI/ML Services
OPENAI_API_KEY=your-openai-key
OPENAI_SERVICE_KEY=your-service-key
ANTHROPIC_API_KEY=your-anthropic-key

# Data APIs
ODDS_API_KEY=your-odds-api-key
ALPHA_VANTAGE_KEY=your-alphavantage-key
GOOGLE_KEY=your-google-key
GOOGLE_CSE_ID=your-search-engine-id

# E-commerce
EBAY_APP_ID=your-ebay-app-id
EBAY_CERT_ID=your-ebay-cert-id

# Communications
TELEGRAM_BOT_TOKEN=your-telegram-token
TELEGRAM_CHAT_ID=your-chat-id
TG_CHAT_ID=your-chat-id

# Development Tools
GITHUB_TOKEN=your-github-token
CODECOV_TOKEN=your-codecov-token
SONAR_TOKEN=your-sonar-token

# Search APIs
BING_KEY=your-bing-key
```

###  **Docker Service Dependencies**

External services that complement our local Docker stack:

```yaml
# Additional external services (optional)
services:
  external-ai:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-models:/root/.ollama

  external-vector-db:
    image: weaviate/weaviate:latest
    ports:
      - "8080:8080"
    environment:
      - ENABLE_MODULES=text2vec-openai
```

##  **Integration Patterns**

###  **API Client Pattern**

```python
# Standard API client setup
import os
import requests
from typing import Optional

class ExternalAPIClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("API_KEY")
        self.base_url = "https://api.external-service.com"
        
    def make_request(self, endpoint: str, **kwargs):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(f"{self.base_url}/{endpoint}", 
                              headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()
```

###  **Async Integration Pattern**

```python
# Async API integration
import asyncio
import aiohttp

async def async_api_call(session: aiohttp.ClientSession, 
                        url: str, **kwargs):
    async with session.get(url, **kwargs) as response:
        return await response.json()
```

###  **Data Pipeline Pattern**

```python
# External data ingestion
from sqlalchemy import create_engine
import pandas as pd

def ingest_external_data(source_api: str, target_table: str):
    # Fetch from external API
    data = fetch_from_api(source_api)
    
    # Transform data
    df = pd.DataFrame(data)
    df = transform_data(df)
    
    # Load to local database
    engine = create_engine(os.getenv("DATABASE_URL"))
    df.to_sql(target_table, engine, if_exists="append")
```

##  **Rate Limiting & Best Practices**

###  **API Rate Limits**

| Service | Rate Limit | Best Practice |
|---------|------------|---------------|
| **OpenAI** | 3,500 RPM | Use exponential backoff |
| **The Odds API** | 500/month free | Cache responses |
| **Google APIs** | 100 QPD | Implement request queuing |
| **Telegram Bot** | 30 msg/sec | Batch notifications |

###  **Security Best Practices**

1. **API Key Management**: Use environment variables, never commit keys
2. **Request Validation**: Validate all external API responses
3. **Error Handling**: Implement proper exception handling
4. **Logging**: Log API usage for monitoring and debugging
5. **Encryption**: Use HTTPS for all external communications

###  **Reliability Patterns**

```python
# Retry with exponential backoff
import time
from functools import wraps

def retry_with_backoff(retries=3, backoff_in_seconds=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            x = 0
            while x <= retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        raise e
                    time.sleep(backoff_in_seconds * 2 ** x)
                    x += 1
        return wrapper
    return decorator
```

##  **Maintenance & Updates**

###  **Regular Tasks**

1. **Weekly**: Check for API deprecations and new features
2. **Monthly**: Update external library versions
3. **Quarterly**: Review rate limits and usage patterns
4. **Annually**: Audit and remove unused integrations

###  **Monitoring External Services**

```python
# Service health check
async def check_external_service_health():
    services = {
        "openai": "https://api.openai.com/v1/models",
        "odds_api": "https://api.the-odds-api.com/v4/sports",
        "telegram": "https://api.telegram.org/bot{token}/getMe"
    }
    
    results = {}
    for name, url in services.items():
        try:
            # Perform health check
            results[name] = "healthy"
        except:
            results[name] = "unhealthy"
    
    return results
```

##  **Integration Roadmap**

###  **Planned Integrations**

1. **Slack API** - Team notifications and bot commands
2. **GitLab CI** - Alternative CI/CD platform
3. **AWS Services** - Cloud deployment and scaling
4. **Stripe API** - Payment processing for monetization
5. **Twilio** - SMS notifications and communication

###  **Performance Optimization**

1. **Connection Pooling**: Implement for frequent API calls
2. **Caching Strategy**: Redis for API response caching
3. **Async Processing**: Use Celery for long-running external requests
4. **Request Batching**: Combine multiple API calls where possible

---

**Last Updated**: November 9, 2025  
**Maintainer**: EQ12 Expert Quantum Team  
**Status**:  Active and Maintained