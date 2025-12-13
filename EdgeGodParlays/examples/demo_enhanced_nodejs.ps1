# Demo script for EdgeGod Enhanced Node.js samples
# This demonstrates the 429 error prevention features

param(
    [string]$ApiKey = $env:ODDS_API_KEY
)

Write-Host "🎯 EdgeGod Enhanced Node.js Samples Demo" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

if (-not $ApiKey) {
    Write-Host "⚠️  No ODDS_API_KEY found in environment variables" -ForegroundColor Yellow
    Write-Host "   Set your API key: `$env:ODDS_API_KEY = 'your-key-here'" -ForegroundColor Cyan
    Write-Host "   Then run: .\demo_enhanced_nodejs.ps1" -ForegroundColor Cyan
    Write-Host ""
}

# Check if Node.js is available
$nodeExists = Get-Command node -ErrorAction SilentlyContinue
if (-not $nodeExists) {
    Write-Host "📋 Node.js Installation Required" -ForegroundColor Yellow
    Write-Host "   1. Download from: [Node.js Official Site](https://nodejs.org)" -ForegroundColor Cyan
    Write-Host "   2. Install Node.js (LTS version recommended)" -ForegroundColor Cyan
    Write-Host "   3. Install axios: npm install axios" -ForegroundColor Cyan
    Write-Host ""
}

# Show what files we have
Write-Host "📁 Enhanced Files Available:" -ForegroundColor Magenta
Get-ChildItem -Filter "*enhanced*" | ForEach-Object {
    $sizeKB = [math]::Round($_.Length / 1024, 1)
    Write-Host "   ✅ $($_.Name) ($sizeKB KB)" -ForegroundColor Green
}

Write-Host ""
Write-Host "🚀 Usage Examples:" -ForegroundColor Magenta

Write-Host ""
Write-Host "Option 1: Drop-in Replacement" -ForegroundColor Cyan
Write-Host "   # Copy enhanced version over official sample" -ForegroundColor Gray
Write-Host "   cp sample-v4-enhanced.js sample-v4.js" -ForegroundColor White
Write-Host "   node sample-v4.js" -ForegroundColor White

Write-Host ""
Write-Host "Option 2: Production Client" -ForegroundColor Cyan
Write-Host "   # Use the full-featured enhanced client" -ForegroundColor Gray
Write-Host "   node enhanced_sample_v4.js" -ForegroundColor White

Write-Host ""
Write-Host "🛡️ 429 Error Prevention Features:" -ForegroundColor Magenta
Write-Host "   ✅ Rate limiting (25 requests/second)" -ForegroundColor Green
Write-Host "   ✅ Intelligent caching (15-minute duration)" -ForegroundColor Green
Write-Host "   ✅ Exponential backoff retry logic" -ForegroundColor Green
Write-Host "   ✅ Automatic 429 error recovery" -ForegroundColor Green
Write-Host "   ✅ Same reliability as Python EdgeGod system" -ForegroundColor Green

Write-Host ""
Write-Host "💡 What This Solves:" -ForegroundColor Magenta
Write-Host "   • Eliminates 429 EXCEEDED_FREQ_LIMIT errors" -ForegroundColor Yellow
Write-Host "   • Prevents quota exhaustion" -ForegroundColor Yellow
Write-Host "   • Provides bulletproof API reliability" -ForegroundColor Yellow
Write-Host "   • Maintains official sample compatibility" -ForegroundColor Yellow

if ($nodeExists -and $ApiKey) {
    Write-Host ""
    Write-Host "🎉 Ready to run! Execute:" -ForegroundColor Green
    Write-Host "   node enhanced_sample_v4.js" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "⏳ Setup Required:" -ForegroundColor Yellow
    if (-not $nodeExists) { Write-Host "   • Install Node.js" -ForegroundColor Red }
    if (-not $ApiKey) { Write-Host "   • Set ODDS_API_KEY environment variable" -ForegroundColor Red }
}

Write-Host ""
