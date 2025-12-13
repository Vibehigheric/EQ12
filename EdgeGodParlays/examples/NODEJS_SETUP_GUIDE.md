# Quick Setup Guide for EdgeGod Enhanced Node.js Samples

## 📋 Prerequisites Setup

### 1. Install Node.js
```powershell
# Option 1: Direct download (Recommended)
# Visit: [Node.js Official Download](https://nodejs.org)
# Download the LTS version (Currently 18.x or 20.x)
# Run the installer

# Option 2: Using winget (Windows Package Manager)
winget install OpenJS.NodeJS

# Option 3: Using Chocolatey (if installed)
choco install nodejs
```

### 2. Install Required Dependencies
```powershell
# Navigate to the examples directory
cd "C:\EQ12\EdgeGodParlays\examples"

# Install axios (HTTP client library)
npm install axios

# Verify installation
node --version
npm --version
```

### 3. Set Your API Key
```powershell
# Set environment variable for current session
$env:ODDS_API_KEY = "YOUR_API_KEY_HERE"

# Or set permanently (requires admin)
[Environment]::SetEnvironmentVariable("ODDS_API_KEY", "YOUR_API_KEY_HERE", "User")
```

## 🚀 Usage Examples

### Quick Test (Drop-in Replacement)
```powershell
# Copy enhanced version over original
cp sample-v4-enhanced.js sample-v4.js

# Run with Node.js
node sample-v4.js
```

### Production Usage
```javascript
// Use the full-featured enhanced client
const { EnhancedOddsAPIClient } = require('./enhanced_sample_v4.js');

const client = new EnhancedOddsAPIClient(process.env.ODDS_API_KEY);

// Get odds with automatic 429 prevention
const odds = await client.getOdds('upcoming', 'soccer_epl');
console.log(odds);
```

## ✅ Verification
After setup, you should be able to:
1. Run `node --version` and see Node.js version
2. Run `npm --version` and see npm version
3. Execute enhanced samples without 429 errors
4. Enjoy the same reliability as your Python EdgeGod system!

## 🛡️ What You Get
- **Zero 429 errors** - Built-in rate limiting prevents API overuse
- **Automatic retry** - Exponential backoff handles temporary failures
- **Smart caching** - Reduces API calls with intelligent caching
- **Drop-in compatibility** - Works with existing code using official samples
- **Production ready** - Same enterprise-grade reliability as Python EdgeGod system
