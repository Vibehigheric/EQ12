# EQ12 OpsBot - Production Webhook & Automation Suite

**Production-ready automation bot for EQ12 platform with OpenAI webhook handling, budget guardrails, model policy enforcement, and community monitoring.**

## 🚀 Quick Start

### 1. Install Dependencies
```powershell
# Create virtual environment (if not exists)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install OpsBot requirements
pip install -r requirements_opsbot.txt
```

### 2. Configuration
```powershell
# Copy environment template
copy .env.example .env

# Edit with your API keys
notepad .env
```

### 3. Run OpsBot
```powershell
# Start webhook server + scheduler (first run will auto-configure)
python -m eq12_opsbot.main run

# Or use specific host/port
python -m eq12_opsbot.main run --host 0.0.0.0 --port 8088
```

### 4. Health Check
Visit `http://127.0.0.1:8088/healthz` for system status.

## 🎯 Features

### Webhook Processing
- **OpenAI Webhooks**: HMAC-verified webhook handling for `job.completed`, `billing.updated`, `rate_limit.warning`
- **Idempotency**: TTL cache prevents duplicate event processing
- **Event Routing**: Automatic dispatch to appropriate handlers
- **Logging**: Daily JSONL logs in `logs/webhooks/`

### Budget & Cost Control
- **Daily/Monthly Limits**: Configurable budget caps with circuit breaker
- **Real-time Tracking**: Per-model cost estimation and usage recording
- **Alert Thresholds**: 70% warning, 90% critical, 100% circuit breaker
- **Integration**: Works with existing `eq12_cost_guards` if available

### Rate Limiting
- **Token Buckets**: TPM/RPM enforcement per model with automatic refill
- **Polite Backoff**: Full jitter and wait time calculation
- **Local Ledger**: Thread-safe token tracking without external dependencies
- **Custom Limits**: YAML-based configuration override

### Model Policy Enforcement
- **Allowlist/Denylist**: YAML-configured model restrictions
- **Pattern Matching**: Regex-based blocking (e.g., `.*-preview$`)
- **Client-layer Blocking**: Prevents unauthorized model usage
- **Smart Suggestions**: Alternative model recommendations for blocked requests

### Community Monitoring
- **RSS Feeds**: OpenAI Community announcements, API updates, responses-api
- **Smart Classification**: Priority and actionability detection
- **Multi-channel Alerts**: Slack, Teams, Telegram notifications
- **GitHub Issues**: Automated issue creation for actionable items

### Task Scheduling
- **RSS Polling**: 15-minute intervals for community updates
- **Budget Snapshots**: Hourly usage tracking
- **Cache Cleanup**: Daily maintenance tasks
- **Config Drift**: Daily configuration validation

## 🔧 CLI Commands

### Core Operations
```powershell
# Start server with scheduler
python -m eq12_opsbot.main run

# Health diagnostics
python -m eq12_opsbot.main doctor

# Rate limit management
python -m eq12_opsbot.main limits --sync --show

# Model policy enforcement
python -m eq12_opsbot.main model-policy --enforce --show
```

## 🛡️ Security

### Webhook Verification
- **HMAC SHA-256**: Validates OpenAI webhook signatures
- **Timestamp Check**: Rejects events older than 5 minutes
- **Replay Protection**: TTL cache prevents duplicate processing

### Configuration Security
- **Environment Variables**: Sensitive data stored in `.env`
- **No Hardcoding**: API keys and secrets externalized
- **Demo Mode**: Safe fallback when credentials missing

## 📊 Endpoints

### Production Endpoints
- `POST /webhooks/openai` - OpenAI webhook handler (HMAC verified)
- `GET /healthz` - System health and status
- `GET /` - Basic service information

### Health Response Example
```json
{
  "status": "healthy",
  "uptime_seconds": 3600,
  "config_summary": {
    "production_ready": true,
    "notifications_enabled": true,
    "github_enabled": true
  },
  "budget_status": {
    "daily_spent": 1.23,
    "monthly_spent": 45.67,
    "circuit_breaker_active": false
  },
  "rate_limit_status": {
    "total_models": 9,
    "stats": {
      "total_requests": 150,
      "rate_limited_requests": 2
    }
  }
}
```

## ⚙️ Configuration Files

### Environment Variables (`.env`)
```bash
# Core Configuration
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_WEBHOOK_SECRET=your-webhook-secret

# Budget Limits
EQ12_BUDGET_MONTHLY=120
EQ12_BUDGET_DAILY=5

# Notifications (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
GITHUB_TOKEN=ghp_your-token-here
```

### Model Policy (`configs/models_allowlist.yaml`)
```yaml
allowed_models:
  - gpt-4o
  - gpt-4o-mini
  - gpt-3.5-turbo

denied_patterns:
  - ".*-preview$"
  - "^o1-.*"
```

### Rate Limits (`configs/rate_limits.yaml`)
```yaml
production:
  gpt-4o-mini:
    tpm: 20000
    rpm: 60
  gpt-4o:
    tpm: 3000
    rpm: 20
```

## 🔄 Integration with Existing EQ12

### Auto-Detection
OpsBot automatically integrates with existing EQ12 modules:
- `eq12_cost_guards` - Preferred budget system if available
- `eq12_ai_client` - AI client integration for model calls
- `eq12_doctor` - Health check integration

### Graceful Fallback
If integrations aren't available, OpsBot uses internal implementations with clear warnings.

## 🧪 Testing Webhook Locally

### 1. Start OpsBot
```powershell
python -m eq12_opsbot.main run --port 8088
```

### 2. Test with Sample Payload
```powershell
# Test webhook endpoint (replace with actual signature)
curl -X POST http://127.0.0.1:8088/webhooks/openai \
  -H "Content-Type: application/json" \
  -H "OpenAI-Signature: t=1696531200,v1=your-signature-here" \
  -d '{"id":"evt_test","type":"job.completed","created_at":1696531200,"data":{"model":"gpt-4o-mini","usage":{"prompt_tokens":10,"completion_tokens":15}}}'
```

## 🎛️ VS Code Integration

OpsBot integrates with VS Code tasks for one-click operations:

1. **EQ12: Start OpsBot** - Launch webhook server
2. **EQ12: OpsBot Doctor** - Run health diagnostics
3. **EQ12: Sync Rate Limits** - Update rate limit configuration
4. **EQ12: Enforce Model Policy** - Apply model restrictions

## 📈 Monitoring & Observability

### Logs Structure
```
C:/EQ12/logs/
├── opsbot.log              # Main application log
├── budget_tracking.json    # Budget usage tracking
├── webhooks/
│   └── openai_20251005.jsonl  # Daily webhook events
└── community_posts_20251005.jsonl  # RSS monitoring
```

### Key Metrics
- Budget usage (daily/monthly percentages)
- Rate limit utilization per model
- Webhook event counts and types
- Community monitoring activity
- Circuit breaker activations

## 🚨 Troubleshooting

### Common Issues

**Webhook 401 Errors**
- Verify `OPENAI_WEBHOOK_SECRET` is correct
- Check timestamp skew (max 5 minutes)

**Budget Circuit Breaker Active**
- Check daily/monthly spend in `/healthz`
- Manually reset: `python -m eq12_opsbot.main doctor`

**Rate Limits Triggering**
- Review model usage patterns in logs
- Adjust limits in `configs/rate_limits.yaml`

**Missing Notifications**
- Verify webhook URLs in `.env`
- Check notification logs for errors

### Debug Mode
```powershell
# Enable verbose logging
set LOG_LEVEL=DEBUG
python -m eq12_opsbot.main run
```

## 📋 First Commit

After generating all files:

```bash
git add .
git commit -S -m "feat(opsbot): EQ12 webhook+budget+model-policy bot with first-run self-init"
```

## 🎯 Next Steps

1. **Configure Webhooks**: Set up OpenAI webhook endpoint pointing to your server
2. **Set Budget Limits**: Adjust `EQ12_BUDGET_DAILY` and `EQ12_BUDGET_MONTHLY`
3. **Enable Notifications**: Configure Slack/Teams webhooks for alerts
4. **Model Policy**: Review and customize `configs/models_allowlist.yaml`
5. **Monitor & Tune**: Watch `/healthz` endpoint and adjust thresholds

**Ready to run with**: `python -m eq12_opsbot.main run` 🚀
