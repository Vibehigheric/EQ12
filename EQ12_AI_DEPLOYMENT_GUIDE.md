# EQ12 AI System - Deployment Guide & Quick Start

## 🚀 System Overview

The EQ12 AI System is a comprehensive, production-ready AI integration platform featuring:

- **Modern OpenAI API Integration** (v1.50+) with structured outputs
- **Advanced Prompt Engineering Framework** with modular templates
- **Sophisticated Conversation Management** with SQLite persistence
- **Unified AI Orchestration** with budget management and monitoring
- **Intelligent Model Selection** across GPT-4o, GPT-4o-mini, o1-preview, o1-mini

## 📋 Pre-Deployment Checklist

### ✅ Environment Setup
- [ ] Python 3.8+ installed
- [ ] Required directories created: `C:\EQ12\logs`, `C:\EQ12\prompts`, `C:\EQ12\conversations`
- [ ] PowerShell execution policy allows script execution
- [ ] Git repository properly configured with signed commits

### ✅ Dependencies
- [ ] OpenAI Python library v1.50+ (`pip install openai>=1.50.0`)
- [ ] Pydantic v2+ (`pip install pydantic>=2.0.0`)
- [ ] Tiktoken (`pip install tiktoken`)
- [ ] PyYAML (`pip install pyyaml`)
- [ ] SQLite3 (included with Python)

### ✅ Configuration
- [ ] OpenAI API key configured (`OPENAI_API_KEY` environment variable)
- [ ] Budget limits set appropriately for production workload
- [ ] Logging directory permissions configured
- [ ] Conversation database path accessible

### ✅ Security
- [ ] API keys stored securely (environment variables, not hardcoded)
- [ ] File permissions properly restricted
- [ ] Logging configured to avoid sensitive data exposure
- [ ] Budget limits prevent runaway costs

## 🛠️ Installation Steps

### 1. Quick Installation
```powershell
# Navigate to EQ12 directory
cd C:\EQ12

# Install Python dependencies
pip install openai>=1.50.0 pydantic>=2.0.0 tiktoken pyyaml

# Set OpenAI API key (replace with your actual key)
$env:OPENAI_API_KEY = "sk-your-api-key-here"

# Run comprehensive test suite
python eq12_ai_test_suite.py
```

### 2. Verify Installation
```powershell
# Run system status check
python -c "
from eq12_unified_ai_system import EQ12AIOrchestrator
import asyncio
ai = EQ12AIOrchestrator()
print('System Status:', ai.get_system_status())
asyncio.run(ai.shutdown())
"
```

### 3. Basic Usage Test
```powershell
# Test sports betting analysis
python -c "
from eq12_unified_ai_system import EQ12AIOrchestrator
import asyncio

async def test():
    ai = EQ12AIOrchestrator()
    # Add your test here when API key is configured
    await ai.shutdown()

asyncio.run(test())
"
```

## 📖 Usage Examples

### Sports Betting Analysis
```python
from eq12_unified_ai_system import EQ12AIOrchestrator
import asyncio

async def analyze_bet():
    ai = EQ12AIOrchestrator()

    result = await ai.analyze_sports_bet(
        game_info="Lakers vs Warriors, NBA Regular Season",
        bet_type="Moneyline",
        odds="-150",
        estimated_probability=0.60,
        bankroll=1000.0
    )

    print(f"Recommended bet size: ${result.recommended_bet_amount}")
    print(f"Expected value: {result.expected_value:.3f}")
    print(f"Risk level: {result.risk_assessment}")

    await ai.shutdown()

# Run the analysis
asyncio.run(analyze_bet())
```

### Code Review
```python
from eq12_unified_ai_system import EQ12AIOrchestrator
import asyncio

async def review_code():
    ai = EQ12AIOrchestrator()

    code_sample = """
def calculate_bet_size(bankroll, probability, odds):
    if probability <= 0 or probability >= 1:
        return 0
    kelly_fraction = (probability * odds - 1) / (odds - 1)
    return max(0, min(bankroll * kelly_fraction * 0.25, bankroll * 0.05))
"""

    result = await ai.review_code(
        code=code_sample,
        language="Python",
        file_path="betting_utils.py"
    )

    print(f"Overall quality: {result.overall_assessment}")
    print(f"Security issues: {len(result.security_issues)}")
    print(f"Improvement suggestions: {len(result.improvement_suggestions)}")

    await ai.shutdown()

# Run the code review
asyncio.run(review_code())
```

### Interactive Conversation
```python
from eq12_conversation_manager import ConversationManager, ConversationRole, MessageType

# Create conversation manager
conv_manager = ConversationManager()

# Start a new conversation
conv_id = conv_manager.create_conversation(title="Sports Betting Strategy")

# Add messages
conv_manager.add_message(
    conv_id,
    ConversationRole.USER,
    "Help me analyze this NBA game for betting opportunities",
    MessageType.QUERY
)

# Add memory for context
conv_manager.add_memory(
    conv_id,
    "user_bankroll",
    "5000.00",
    "User's available betting bankroll"
)

# Retrieve conversation for AI processing
messages = conv_manager.get_conversation_messages(conv_id)
print(f"Conversation has {len(messages)} messages")
```

## 🔧 Configuration Options

### Budget Management
```python
# Set daily budget limit
ai = EQ12AIOrchestrator(budget_limit=50.0)  # $50/day limit

# Check current budget status
status = ai.get_system_status()
print(f"Budget used today: ${status['budget']['used_today']}")
print(f"Budget remaining: ${status['budget']['remaining']}")
```

### Model Selection
```python
from eq12_openai_enhanced_v2 import EQ12OpenAIEnhanced, TaskComplexity

client = EQ12OpenAIEnhanced()

# Automatic model selection based on task complexity
simple_model = client.select_optimal_model(TaskComplexity.LOW)      # gpt-4o-mini
moderate_model = client.select_optimal_model(TaskComplexity.MODERATE)  # gpt-4o
complex_model = client.select_optimal_model(TaskComplexity.HIGH)     # o1-preview
```

### Prompt Customization
```python
from eq12_prompt_engineering_framework import PromptTemplateManager

manager = PromptTemplateManager()

# List available templates
templates = manager.list_templates()
print("Available templates:", templates)

# Generate conversation with custom parameters
messages = manager.generate_conversation(
    "sports_betting_expert",
    game_info="Custom game information",
    bet_type="Spread",
    odds="+110",
    estimated_probability="0.52",
    bankroll="2500.00"
)
```

## 📊 Monitoring & Logging

### System Health Monitoring
```python
# Get comprehensive system status
ai = EQ12AIOrchestrator()
status = ai.get_system_status()

print("System Health:")
print(f"  OpenAI Client: {'✓' if status['openai_client'] else '✗'}")
print(f"  Prompt Engine: {'✓' if status['prompt_engine'] else '✗'}")
print(f"  Conversation Manager: {'✓' if status['conversation_manager'] else '✗'}")
print(f"  Database: {'✓' if status['database'] else '✗'}")
```

### Performance Metrics
```python
# Get conversation metrics
conv_manager = ConversationManager()
metrics = conv_manager.get_metrics()

print(f"Total conversations: {metrics.get('total_conversations', 0)}")
print(f"Total messages: {metrics.get('total_messages', 0)}")
print(f"Average messages per conversation: {metrics.get('avg_messages_per_conversation', 0):.1f}")
```

### Log Files
- **System logs**: `C:\EQ12\logs\eq12_ai_system_YYYYMMDD_HHMMSS.log`
- **Test results**: `C:\EQ12\logs\ai_test_results_YYYYMMDD_HHMMSS.json`
- **Conversation database**: `C:\EQ12\conversations\eq12_conversations.db`

## 🚨 Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```
   Error: OpenAI API key not found
   Solution: Set OPENAI_API_KEY environment variable
   ```

2. **Module Import Errors**
   ```
   Error: ModuleNotFoundError: No module named 'openai'
   Solution: pip install openai>=1.50.0 pydantic>=2.0.0 tiktoken pyyaml
   ```

3. **Database Permission Errors**
   ```
   Error: Permission denied accessing conversation database
   Solution: Ensure C:\EQ12\conversations directory is writable
   ```

4. **Budget Exceeded**
   ```
   Error: Daily budget limit exceeded
   Solution: Check budget usage or increase limit in EQ12AIOrchestrator(budget_limit=X)
   ```

### Debug Mode
```python
# Enable detailed logging
import logging
logging.getLogger('eq12').setLevel(logging.DEBUG)

# Run with error details
ai = EQ12AIOrchestrator(budget_limit=10.0, enable_memory=True)
status = ai.get_system_status()
print("Detailed status:", status)
```

## 🔄 Production Deployment

### Automated Deployment Script
```powershell
# Save as deploy_eq12_ai.ps1
param(
    [string]$ApiKey = $env:OPENAI_API_KEY,
    [double]$BudgetLimit = 100.0
)

Write-Host "🚀 EQ12 AI System Deployment" -ForegroundColor Green

# Validate environment
if (-not $ApiKey) {
    Write-Error "OpenAI API key required. Set OPENAI_API_KEY or pass -ApiKey parameter"
    exit 1
}

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
pip install openai>=1.50.0 pydantic>=2.0.0 tiktoken pyyaml

# Set environment
$env:OPENAI_API_KEY = $ApiKey

# Run tests
Write-Host "🧪 Running system tests..." -ForegroundColor Yellow
python C:\EQ12\eq12_ai_test_suite.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ EQ12 AI System deployed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Deployment failed. Check test results." -ForegroundColor Red
    exit 1
}
```

### Scheduled Tasks Integration
The system integrates with existing EQ12 scheduled tasks:
- **Chrome Daily Governance Refresh**: Includes AI analysis
- **Security Audits**: AI-powered security assessment
- **Performance Monitoring**: Automated system health checks

## 📚 Additional Resources

- **API Documentation**: OpenAI API v1.50+ docs
- **Model Comparison**: GPT-4o vs o1-preview performance characteristics
- **Cost Optimization**: Budget management and token usage strategies
- **Security Best Practices**: API key management and data protection

## 🆘 Support

For issues and questions:
1. Check logs in `C:\EQ12\logs\`
2. Run diagnostic: `python eq12_ai_test_suite.py`
3. Review system status: `EQ12AIOrchestrator().get_system_status()`
4. Consult troubleshooting section above

---

**EQ12 GODSTACK Team**
*Enterprise AI Integration Platform*
*Version 1.0.0 - Production Ready*
