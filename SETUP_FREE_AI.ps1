<#
.SYNOPSIS
    EQ12 Free AI Provider Setup - Configure Groq as OpenAI Alternative
.DESCRIPTION
    Sets up Groq API (FREE, unlimited for Llama models) as fallback when OpenAI quota is exceeded
#>

[CmdletBinding()]
param()

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "EQ12 FREE AI PROVIDER SETUP" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Check existing .env
$envPath = "C:\EQ12_BROKEN_20251122_210342\.env"
if (-not (Test-Path $envPath)) {
    Write-Host "❌ .env file not found at $envPath" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Current API Keys Status:`n" -ForegroundColor Yellow

$envContent = Get-Content $envPath
$keys = @{
    "OPENAI_API_KEY"     = $null
    "GROQ_API_KEY"       = $null
    "OPENROUTER_API_KEY" = $null
    "CLAUDE_API_KEY"     = $null
}

foreach ($line in $envContent) {
    if ($line -match "^(OPENAI_API_KEY|GROQ_API_KEY|OPENROUTER_API_KEY)=(.+)") {
        $keyName = $Matches[1]
        $keyValue = $Matches[2].Trim("""")
        $keys[$keyName] = $keyValue
    }
    if ($line -match "claud ai key:(.+)") {
        $keys["CLAUDE_API_KEY"] = $Matches[1].Trim()
    }
}

# Display status
foreach ($key in $keys.Keys | Sort-Object) {
    if ($keys[$key]) {
        $masked = $keys[$key].Substring(0, [Math]::Min(15, $keys[$key].Length)) + "..."
        Write-Host "  ✅ $key = $masked" -ForegroundColor Green
    }
    else {
        Write-Host "  ❌ $key = NOT SET" -ForegroundColor Red
    }
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "PROVIDER RECOMMENDATIONS" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "1. GROQ (RECOMMENDED - FREE & FAST)" -ForegroundColor Green
Write-Host "   • Models: Llama-3.1-70B, Mixtral-8x7B, Gemma-7B" -ForegroundColor Gray
Write-Host "   • Speed: 500+ tokens/sec (fastest free API)" -ForegroundColor Gray
Write-Host "   • Limit: No hard quota (rate limit only)" -ForegroundColor Gray
Write-Host "   • Signup: https://console.groq.com/" -ForegroundColor Cyan
if ($keys["GROQ_API_KEY"]) {
    Write-Host "   ✅ ALREADY CONFIGURED" -ForegroundColor Green
}
else {
    Write-Host "   ⚠️  NOT CONFIGURED - Get free key!" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "2. OpenRouter (Backup - Free tier available)" -ForegroundColor Yellow
Write-Host "   • Models: 100+ models including GPT-4, Claude, Llama" -ForegroundColor Gray
Write-Host "   • Free tier: Limited requests/day" -ForegroundColor Gray
Write-Host "   • Signup: https://openrouter.ai/" -ForegroundColor Cyan
if ($keys["OPENROUTER_API_KEY"]) {
    Write-Host "   ✅ ALREADY CONFIGURED" -ForegroundColor Green
}
else {
    Write-Host "   ⚠️  NOT CONFIGURED" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "3. Claude (Anthropic - Pay as you go)" -ForegroundColor Yellow
Write-Host "   • Models: Claude-3-Sonnet, Claude-3-Opus" -ForegroundColor Gray
Write-Host "   • Free tier: $5 credit for new accounts" -ForegroundColor Gray
Write-Host "   • Signup: https://console.anthropic.com/" -ForegroundColor Cyan
if ($keys["CLAUDE_API_KEY"]) {
    Write-Host "   ✅ ALREADY CONFIGURED" -ForegroundColor Green
}
else {
    Write-Host "   ⚠️  NOT CONFIGURED" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "AUTOMATIC FALLBACK CHAIN" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "Your AI commands now use this fallback order:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. OpenAI (gpt-4o) - Try first" -ForegroundColor Gray
Write-Host "     └─ ❌ Quota exceeded" -ForegroundColor Red
Write-Host ""
Write-Host "  2. Groq (llama-3.1-70b) - FREE fallback ✅" -ForegroundColor Green
Write-Host "     └─ Fast & unlimited for most queries" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. OpenRouter (llama-3.1-70b) - Backup" -ForegroundColor Yellow
Write-Host "     └─ If Groq fails" -ForegroundColor Gray
Write-Host ""
Write-Host "  4. Claude (claude-3-sonnet) - Final fallback" -ForegroundColor Yellow
Write-Host "     └─ If all else fails" -ForegroundColor Gray
Write-Host ""

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TESTING PROVIDERS" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "Testing AI query with fallback..." -ForegroundColor Yellow
Write-Host ""

$testPrompt = "Say EQ12 AI is working in one sentence"
$testResult = python "C:\EQ12_BROKEN_20251122_210342\scripts\eq12_ai_query.py" $testPrompt

Write-Host $testResult
Write-Host ""

if ($testResult -match "\[Groq|OpenRouter|Claude\]") {
    Write-Host "✅ SUCCESS: Alternative AI provider working!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your AI commands will now work even when OpenAI quota is exceeded." -ForegroundColor Green
}
elseif ($testResult -match "❌ All AI providers failed") {
    Write-Host "⚠️  ALL PROVIDERS FAILED" -ForegroundColor Red
    Write-Host ""
    Write-Host "ACTION REQUIRED: Get a FREE Groq API key" -ForegroundColor Yellow
    Write-Host "1. Visit: https://console.groq.com/" -ForegroundColor Cyan
    Write-Host "2. Sign up (free, no credit card)" -ForegroundColor Cyan
    Write-Host "3. Create API key" -ForegroundColor Cyan
    Write-Host "4. Add to .env: GROQ_API_KEY=your_key_here" -ForegroundColor Cyan
}
else {
    Write-Host "✅ OpenAI still working (no fallback needed)" -ForegroundColor Green
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "QUICK START" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "Try these commands (will use free Groq if OpenAI quota exceeded):" -ForegroundColor Yellow
Write-Host ""
Write-Host "  ai `"Explain the Kelly Criterion`"" -ForegroundColor Cyan
Write-Host "  diagnose `"STO W8114`"" -ForegroundColor Cyan
Write-Host "  gen-script `"Monitor CPU usage`"" -ForegroundColor Cyan
Write-Host "  parlay-ai" -ForegroundColor Cyan
Write-Host ""

Write-Host "Setup complete! 🚀" -ForegroundColor Green
Write-Host ""
