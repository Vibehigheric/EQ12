# EQ12 Cost Guard Action

Monitor and optimize your GitHub Actions usage costs with intelligent analysis and recommendations.

## Features

🔍 **Real-time Cost Monitoring** - Track GitHub Actions usage costs across your repositories
💡 **Smart Optimization** - AI-powered recommendations for cost reduction
📊 **Detailed Analytics** - Comprehensive breakdown by workflow, runner, and time period
🚨 **Threshold Alerts** - Automated notifications when costs exceed limits
⚡ **Premium Analysis** - Advanced optimization with EQ12 intelligence (optional)

## Usage

### Basic Setup

```yaml
name: Cost Monitoring
on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9 AM
  workflow_dispatch:

jobs:
  cost-guard:
    runs-on: ubuntu-latest
    steps:
      - uses: eq12/cost-guard@v1
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          cost-threshold: '25.00'
          analysis-level: 'standard'
```

### Premium Setup (with EQ12 API)

```yaml
- uses: eq12/cost-guard@v1
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
    cost-threshold: '50.00'
    analysis-level: 'premium'
    eq12-api-key: ${{ secrets.EQ12_API_KEY }}
    notification-webhook: ${{ secrets.SLACK_WEBHOOK }}
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `token` | GitHub token with Actions read permissions | Yes | - |
| `cost-threshold` | Maximum monthly cost threshold in USD | No | `10.00` |
| `analysis-level` | Analysis depth: basic, standard, premium | No | `standard` |
| `eq12-api-key` | EQ12 API key for premium analysis | No | - |
| `notification-webhook` | Webhook URL for cost alerts | No | - |

## Outputs

| Output | Description |
|--------|-------------|
| `cost-analysis` | JSON object with detailed cost breakdown |
| `recommendations` | Array of optimization recommendations |
| `projected-savings` | Calculated potential savings |

## Analysis Levels

### Basic
- Cost calculation by runner type
- Simple workflow cost breakdown
- Basic threshold checking

### Standard (Default)
- Detailed workflow analysis
- Runner optimization recommendations
- Daily cost trending
- Matrix job analysis

### Premium (EQ12 API Required)
- AI-powered optimization suggestions
- Advanced pattern recognition
- Predictive cost modeling
- Custom optimization strategies
- Integration with EQ12 intelligence platform

## Cost Optimization Strategies

### 1. Runner Optimization
- **Ubuntu vs. Windows/macOS**: Ubuntu runners cost 50-90% less
- **Self-hosted runners**: Eliminate per-minute charges for high-volume usage
- **Matrix optimization**: Reduce unnecessary combinations

### 2. Workflow Efficiency
- **Path filtering**: Run only when relevant files change
- **Dependency caching**: Reduce build times significantly
- **Parallel jobs**: Optimize critical path timing
- **Conditional execution**: Skip unnecessary steps

### 3. Advanced Techniques
- **Workflow consolidation**: Combine related workflows
- **Smart triggering**: Use repository dispatch for complex logic
- **Resource pooling**: Share artifacts across workflows
- **Gradual rollout**: Implement changes incrementally

## Premium Features (EQ12 API)

### Intelligent Analysis
```json
{
  "pattern_detection": {
    "inefficient_matrices": ["detected_workflows"],
    "redundant_jobs": ["optimization_targets"],
    "caching_opportunities": ["high_impact_areas"]
  },
  "predictive_modeling": {
    "cost_forecast": "monthly_projection",
    "usage_trends": "growth_analysis",
    "optimization_impact": "savings_estimate"
  }
}
```

### Custom Recommendations
- Repository-specific optimization
- Industry best practices
- Cost/performance trade-off analysis
- Implementation priority scoring

## Example Output

```markdown
## 💰 EQ12 Cost Guard Report

### Cost Summary (Last 30 Days)
- **Total Cost:** $47.82
- **Monthly Projected:** $52.15
- **Average Daily:** $1.59
- **Total Workflow Runs:** 284

### 🎯 Optimization Recommendations

**Optimize expensive runners** (HIGH)
- Consider using Ubuntu runners instead of macos-latest
- Potential Savings: $18.45/month
- Implementation: Change runner labels in workflow files

**Optimize high-cost workflows** (MEDIUM)
- Workflows CI, Deploy consume significant resources
- Potential Savings: $8.23/month
- Implementation: Add path filters, reduce matrix size

### 💡 Projected Savings
- **Monthly:** $26.68
- **Annual:** $320.16
- **Cost Reduction:** 51.2%
```

## Pricing

### Free Tier
- Basic cost monitoring
- Standard optimization recommendations
- Up to 10 repositories

### EQ12 Premium ($9.99/month)
- Advanced AI analysis
- Custom optimization strategies
- Unlimited repositories
- Priority support
- Integration with EQ12 platform

## Security & Privacy

- **No repository code access**: Only reads workflow run metadata
- **Encrypted communication**: All API calls use TLS 1.3
- **Minimal permissions**: Requires only Actions:read scope
- **Data retention**: Analysis data stored for 30 days maximum
- **GDPR compliant**: Full data deletion on request

## Support

- 📚 [Documentation](https://docs.eq12.com/cost-guard)
- 💬 [Community Forum](https://community.eq12.com)
- 📧 [Premium Support](mailto:support@eq12.com)
- 🐛 [Issue Tracker](https://github.com/eq12/cost-guard/issues)

## License

MIT License - see [LICENSE](LICENSE) for details.

---

*Built with ❤️ by the EQ12 team. Making GitHub Actions cost-effective for everyone.*
