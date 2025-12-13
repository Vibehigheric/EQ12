# EQ12 Development Environment Setup
# Sets up commit linting and pre-commit hooks

Write-Host "Setting up EQ12 development environment..." -ForegroundColor Cyan

# Check Node.js
$nodeCheck = Get-Command node -ErrorAction SilentlyContinue
if (-not $nodeCheck) {
    Write-Host "Node.js not found. Please install Node.js first." -ForegroundColor Red
    exit 1
}

Write-Host "Node.js found: $(node --version)" -ForegroundColor Green

# Install dependencies
Write-Host "Installing commit linting dependencies..." -ForegroundColor Yellow
npm install

# Set up Husky
Write-Host "Setting up Git hooks..." -ForegroundColor Yellow
npx husky install

# Create commit message hook
Write-Host "Creating commit-msg hook..." -ForegroundColor Yellow
npx husky add .husky/commit-msg "npx --no -- commitlint --edit `$1"

# Create git message template
$template = @'
# <type>(<scope>): <subject>
#
# Examples:
# feat(extension): Add audit tab to popup interface
# fix(api): Correct odds normalization in parlay endpoint
# bet(parlay): Generate MLB/NFL mixed 10-leg slips
# agent(pipeline): Orchestrate EV and props agents
'@

$template | Out-File -FilePath ".gitmessage" -Encoding UTF8

Write-Host "EQ12 Development Environment Ready!" -ForegroundColor Green
Write-Host "Available commands:" -ForegroundColor Cyan
Write-Host "  npm run lint:commits    - Check recent commits" -ForegroundColor White
Write-Host "  npm run changelog       - Generate changelog" -ForegroundColor White

Write-Host "Try making a commit with format: type(scope): Description" -ForegroundColor Yellow
