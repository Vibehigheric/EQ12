# 📝 EQ12 Commit Message Conventions

This project follows [Conventional Commits](https://www.conventionalcommits.org/) with custom types and scopes tailored for the EQ12 betting automation stack.

## 🎯 Commit Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Example:
```
feat(extension): Add real-time EV highlighting to popup interface

- Implement background script communication
- Add visual indicators for positive EV bets
- Include confidence percentage display

Closes #123
```

## 🏷️ Available Types

### Standard Types
- **feat**: New feature
- **fix**: Bug fix
- **chore**: Maintenance tasks
- **docs**: Documentation changes
- **refactor**: Code refactoring
- **style**: Formatting changes
- **test**: Adding or fixing tests
- **perf**: Performance improvements
- **ci**: CI/CD changes
- **build**: Build system changes

### EQ12 Custom Types
- **bet**: Betting logic and algorithms
- **agent**: Multi-agent orchestration
- **ext**: Browser extension code
- **parlay**: Parlay generation specific
- **ev**: Expected value calculations
- **risk**: Risk management and bankroll
- **telegram**: Telegram bot functionality
- **vpn**: VPN guard and networking
- **audit**: Compliance & logging
- **infra**: Infrastructure and pipelines

## 🎯 Available Scopes

### Browser Extension
- **extension**: General extension code
- **popup**: Extension popup interface
- **options**: Extension settings page
- **content**: Content scripts for sportsbooks
- **background**: Service worker/background scripts

### Backend API
- **api**: EQ12 FastAPI backend
- **endpoints**: Specific API endpoints
- **auth**: Authentication and security
- **cors**: CORS configuration
- **middleware**: API middleware

### EQ12 Agents & Modules
- **telegram**: Telegram bot logic
- **audit**: Compliance and audit agent
- **vpn**: VPN guard and scripts
- **pipeline**: Betting pipeline orchestration
- **parlay**: Parlay builder agent
- **ev**: EV/probability calculations
- **props**: Player props agent
- **risk**: Bankroll/risk management
- **odds**: Odds parsing and normalization

### Infrastructure & Tooling
- **ci**: GitHub Actions workflows
- **build**: Build scripts and tools
- **docker**: Docker configuration
- **nginx**: Nginx/reverse proxy
- **database**: SQLite/database operations

### Documentation & Configuration
- **docs**: Documentation files
- **config**: Configuration files
- **manifest**: Extension manifests
- **deps**: Dependency management
- **scripts**: Utility scripts

### Testing & Quality
- **tests**: Test files and configuration
- **lint**: Linting configuration
- **format**: Code formatting

### Sportsbook Integration
- **draftkings**: DraftKings integration
- **fanduel**: FanDuel integration
- **betmgm**: BetMGM integration
- **caesars**: Caesars integration
- **barstool**: Barstool integration

## ✅ Good Examples

```bash
# New features
feat(extension): Add 10-leg parlay generation button
feat(api): Implement real-time odds tracking endpoint
bet(parlay): Add MLB player prop combinations
agent(pipeline): Orchestrate multiple EV agents

# Bug fixes
fix(popup): Resolve authentication token refresh issue
fix(odds): Correct decimal odds conversion for EU books
fix(vpn): Handle WireGuard reconnection timeout

# Infrastructure
infra(ci): Add automated extension packaging workflow
infra(docker): Optimize FastAPI container build time
ci(release): Auto-generate changelog from commits

# Documentation
docs(api): Add endpoint documentation with examples
docs(extension): Update installation instructions
```

## ❌ Bad Examples

```bash
# Too vague
fix: stuff
update things
chore: misc

# Wrong format
Fixed the popup bug
Add new feature
Updated documentation

# Missing scope when needed
feat: add button
fix: API issue
```

## 🔧 Enforcement

This project uses automated commit message validation:

- **Pre-commit hooks**: Validate locally before commits
- **GitHub Actions**: Check all PR commits
- **Changelog generation**: Auto-generate release notes from commit messages

### Setting Up Locally

```bash
# Install development dependencies
npm install

# Set up git hooks
npm run prepare

# Test commit message validation
npm run lint:commits
```

## 📋 Changelog Integration

Commits are automatically categorized in changelogs:

- **🎯 Betting Logic**: `bet:` commits
- **🤖 Multi-Agent System**: `agent:` commits
- **🦊 Browser Extensions**: `ext:` commits
- **🚀 Features**: `feat:` commits
- **🐛 Bug Fixes**: `fix:` commits
- **📖 Documentation**: `docs:` commits

## 💡 Tips

1. **Use imperative mood**: "Add feature" not "Added feature"
2. **Be specific**: Include what and why, not just what
3. **Reference issues**: Use `Closes #123` or `Fixes #456`
4. **Keep first line under 72 characters**
5. **Use body for detailed explanations**

## 🆘 Need Help?

Run the setup script to configure your environment:

```bash
.\setup-dev-env.ps1
```

This will install commit linting, set up git hooks, and provide a commit message template with examples.
