# 🎯 EQ12 GitHub App - CI-as-a-Service

Transform every commit into actionable sports betting intelligence with the EQ12 GitHub App.

## 🚀 Features

- **Automated Analysis** - Every commit triggers comprehensive betting intelligence analysis
- **License Management** - Credit-based system with usage tracking
- **Premium Reports** - Arbitrage opportunities, line movements, correlation updates
- **Real-time Alerts** - Instant notifications for profitable betting scenarios
- **Integration Ready** - Seamless connection to EQ12 platform and dashboard

## 📦 Installation

1. **Install the GitHub App**
   - Visit [EQ12 GitHub App](https://github.com/apps/eq12-ci-service)
   - Click "Install" and select repositories

2. **Configure Repository Secrets**
   ```
   EQ12_API_KEY=your-api-key
   EQ12_LICENSE_TOKEN=your-license-token
   ```

3. **Verify Installation**
   - Push a commit to trigger analysis
   - Check the "EQ12 Analysis" status check

## 🔧 Configuration

### Environment Variables

- `EQ12_LICENSE` - License server URL
- `EQ12_TOKEN` - Authentication token for license validation
- `EQ12_API` - EQ12 analysis API endpoint
- `EQ12_API_KEY` - API key for premium analysis
- `EQ12_DASHBOARD` - Dashboard URL for report links

### Skip Analysis

Add `[skip-eq12]` to commit messages to bypass analysis and save credits.

## 💰 Pricing

- **Free Tier**: 100 commits/month
- **Pro Tier**: $29/month - 2,000 commits + premium features
- **Enterprise**: Custom pricing with dedicated support

## 🛠️ Local Development

```bash
# Install dependencies
npm install

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Start development server
npm run dev
```

## 📊 Analytics Provided

- Arbitrage opportunity detection
- Line movement analysis and alerts
- Player prop correlations
- Bankroll optimization recommendations
- Live betting opportunities
- Risk assessment and management

## 🔐 Security

- All API calls use secure authentication
- No sensitive betting data stored in GitHub
- Rate limiting and abuse protection
- Comprehensive audit logging

## 📞 Support

- **Documentation**: [docs.eq12.com](https://docs.eq12.com)
- **Support Email**: support@eq12.com
- **Discord**: [EQ12 Community](https://discord.gg/eq12)

---

**Transform your commits into cash with EQ12 intelligence** 💸
