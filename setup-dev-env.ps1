# EQ12 Development Environment Setup
# Sets up commit linting, pre-commit hooks, and git-cliff

Write-Host "🔧 Setting up EQ12 development environment..." -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Check if Node.js is installed
$nodeVersion = node --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Node.js not found. Please install Node.js 18+ first." -ForegroundColor Red
    Write-Host "🔗 Download: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "✅ Node.js version: $nodeVersion" -ForegroundColor Green
}

# Install root dependencies (commitlint, husky)
Write-Host "`n📦 Installing commit linting dependencies..." -ForegroundColor Yellow
npm install

# Initialize husky
Write-Host "`n🪝 Setting up Git hooks with Husky..." -ForegroundColor Yellow
npx husky install

# Create commit message hook
Write-Host "📝 Creating commit-msg hook..." -ForegroundColor Yellow
npx husky add .husky/commit-msg "npx --no -- commitlint --edit `$1"

# Create pre-commit hook for extension linting
Write-Host "🧹 Creating pre-commit hook..." -ForegroundColor Yellow
$preCommitContent = @'
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

echo "🔍 Running pre-commit checks..."

# Check if extension files were modified
if git diff --cached --name-only | grep -E "^eq12-firefox-ext/" > /dev/null; then
    echo "📱 Extension files modified, running validation..."

    # Validate JavaScript syntax in extension
    cd eq12-firefox-ext
    for js_file in src/*.js; do
        if [ -f "$js_file" ]; then
            echo "  Checking $js_file..."
            node -c "$js_file" || {
                echo "❌ Syntax error in $js_file"
                exit 1
            }
        fi
    done

    # Validate manifest JSON
    for manifest in manifest.firefox.json manifest.chromium.json; do
        if [ -f "$manifest" ]; then
            echo "  Validating $manifest..."
            npx jsonlint "$manifest" > /dev/null || {
                echo "❌ JSON syntax error in $manifest"
                exit 1
            }
        fi
    done

    cd ..
    echo "✅ Extension validation passed"
fi

# Check Python files for basic syntax
if git diff --cached --name-only | grep -E "\.py$" > /dev/null; then
    echo "🐍 Python files modified, checking syntax..."

    for py_file in $(git diff --cached --name-only | grep -E "\.py$"); do
        if [ -f "$py_file" ]; then
            echo "  Checking $py_file..."
            python -m py_compile "$py_file" || {
                echo "❌ Syntax error in $py_file"
                exit 1
            }
        fi
    done

    echo "✅ Python validation passed"
fi

echo "✅ Pre-commit checks completed successfully"
'@

$preCommitContent | Out-File -FilePath ".husky\pre-commit" -Encoding UTF8
npx husky add .husky/pre-commit ""

# Install git-cliff if not present
Write-Host "`n📋 Checking for git-cliff..." -ForegroundColor Yellow
$cliffVersion = git-cliff --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⬇️ Installing git-cliff for changelog generation..." -ForegroundColor Yellow

    # Try to install via cargo if available
    $cargoVersion = cargo --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        cargo install git-cliff
    } else {
        Write-Host "ℹ️ git-cliff not installed locally. It will be available in GitHub Actions." -ForegroundColor Cyan
        Write-Host "   To install locally: https://git-cliff.org/docs/installation" -ForegroundColor Cyan
    }
} else {
    Write-Host "✅ git-cliff version: $cliffVersion" -ForegroundColor Green
}

# Set up git configuration for better commit messages
Write-Host "`n📝 Configuring Git settings..." -ForegroundColor Yellow
git config commit.template .gitmessage 2>$null

# Create a commit message template
$gitMessageTemplate = @'
# <type>(<scope>): <subject>
#
# <body>
#
# <footer>

# Type: feat|fix|chore|docs|refactor|style|test|perf|ci|build|revert
#       bet|agent|ext|infra|audit|parlay|ev|risk|telegram|vpn
#
# Scope: extension|popup|options|content|background|api|endpoints|auth
#        telegram|audit|vpn|pipeline|parlay|ev|props|risk|odds
#        ci|build|docker|nginx|database|docs|config|manifest|deps
#        tests|lint|format|draftkings|fanduel|betmgm|caesars|barstool
#
# Examples:
# feat(extension): Add audit tab to popup interface
# fix(api): Correct odds normalization in parlay endpoint
# bet(parlay): Generate MLB/NFL mixed 10-leg slips
# agent(pipeline): Orchestrate EV and props agents
# ext(chrome): Add audit tab to popup
# infra(vpn): Auto-reconnect WireGuard if dropped
# audit(compliance): Include VPN logs in audit output
'@

$gitMessageTemplate | Out-File -FilePath ".gitmessage" -Encoding UTF8

Write-Host "`n🎉 EQ12 Development Environment Ready!" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

Write-Host "`n📋 What was set up:" -ForegroundColor Cyan
Write-Host "✅ Commitlint with EQ12 custom types and scopes" -ForegroundColor White
Write-Host "✅ Husky pre-commit hooks for code validation" -ForegroundColor White
Write-Host "✅ Git commit message template with examples" -ForegroundColor White
Write-Host "✅ Changelog generation configuration" -ForegroundColor White

Write-Host "`n🛠️ Available commands:" -ForegroundColor Cyan
Write-Host "npm run lint:commits    - Check recent commit messages" -ForegroundColor White
Write-Host "npm run changelog       - Generate full changelog" -ForegroundColor White
Write-Host "npm run changelog:latest - Generate latest version notes" -ForegroundColor White

Write-Host "`n💡 Next steps:" -ForegroundColor Cyan
Write-Host "1. Try making a commit - hooks will validate your message" -ForegroundColor White
Write-Host "2. Use format: type(scope): Description" -ForegroundColor White
Write-Host "3. Example: feat(extension): Add new parlay generation button" -ForegroundColor White

Write-Host "`n🔗 Documentation:" -ForegroundColor Cyan
Write-Host "• Conventional Commits: https://www.conventionalcommits.org/" -ForegroundColor White
Write-Host "• git-cliff: https://git-cliff.org/" -ForegroundColor White
Write-Host "• Commitlint: https://commitlint.js.org/" -ForegroundColor White
