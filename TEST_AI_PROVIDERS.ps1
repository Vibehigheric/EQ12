<#
.SYNOPSIS
    EQ12 AI Provider Test - Test multi-provider fallback
#>

Write-Host "`n===========================================================" -ForegroundColor Cyan
Write-Host "EQ12 AI PROVIDER TEST - Multi-Provider Fallback" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan

Write-Host "`nChecking API keys in .env...`n" -ForegroundColor Yellow

$envPath = "C:\EQ12_BROKEN_20251122_210342\.env"
$keys = @{}

if (Test-Path $envPath) {
    $envContent = Get-Content $envPath
    foreach ($line in $envContent) {
        if ($line -match "^OPENAI_API_KEY=(.+)") {
            $keys["OpenAI"] = $Matches[1].Substring(0, 15) + "..."
        }
        if ($line -match "^GROQ_API_KEY=(.+)") {
            $keys["Groq"] = $Matches[1].Substring(0, 15) + "..."
        }
        if ($line -match "^OPENROUTER_API_KEY=(.+)") {
            $keys["OpenRouter"] = $Matches[1].Substring(0, 15) + "..."
        }
    }
}

foreach ($provider in @("OpenAI", "Groq", "OpenRouter")) {
    if ($keys.ContainsKey($provider)) {
        Write-Host "  $provider : $($keys[$provider])" -ForegroundColor Green
    }
    else {
        Write-Host "  $provider : NOT SET" -ForegroundColor Red
    }
}

Write-Host "`n===========================================================" -ForegroundColor Cyan
Write-Host "FALLBACK ORDER" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan

Write-Host "`n1. OpenAI (gpt-4o) - Try first" -ForegroundColor Gray
Write-Host "2. Groq (llama-3.1-70b) - FREE fallback" -ForegroundColor Green
Write-Host "3. OpenRouter (llama-3.1-70b) - Backup" -ForegroundColor Yellow
Write-Host "4. Claude (claude-3-sonnet) - Final fallback" -ForegroundColor Yellow

Write-Host "`n===========================================================" -ForegroundColor Cyan
Write-Host "TESTING AI QUERY" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan

Write-Host "`nSending test query...`n" -ForegroundColor Yellow

$testPrompt = "Say hello in one sentence"
$result = python "C:\EQ12_BROKEN_20251122_210342\scripts\eq12_ai_query.py" $testPrompt 2>&1

Write-Host $result
Write-Host ""

if ($result -match "\[Groq") {
    Write-Host "SUCCESS: Using Groq (FREE alternative)" -ForegroundColor Green
    Write-Host "Your AI commands work even with OpenAI quota exceeded!" -ForegroundColor Green
}
elseif ($result -match "\[OpenRouter") {
    Write-Host "SUCCESS: Using OpenRouter (alternative provider)" -ForegroundColor Green
    Write-Host "Your AI commands work even with OpenAI quota exceeded!" -ForegroundColor Green
}
elseif ($result -match "\[Claude\]") {
    Write-Host "SUCCESS: Using Claude (Anthropic)" -ForegroundColor Green
}
elseif ($result -match "\[OpenAI\]") {
    Write-Host "SUCCESS: Using OpenAI (primary provider)" -ForegroundColor Green
}
elseif ($result -match "All AI providers failed") {
    Write-Host "FAILED: All providers failed" -ForegroundColor Red
    Write-Host "`nGet FREE Groq API key:" -ForegroundColor Yellow
    Write-Host "1. Visit https://console.groq.com/" -ForegroundColor Cyan
    Write-Host "2. Sign up (free)" -ForegroundColor Cyan
    Write-Host "3. Create API key" -ForegroundColor Cyan
    Write-Host "4. Add to .env: GROQ_API_KEY=your_key" -ForegroundColor Cyan
}
else {
    Write-Host "Response received (check above for details)" -ForegroundColor Yellow
}

Write-Host "`n===========================================================" -ForegroundColor Cyan
Write-Host "QUICK TEST COMMANDS" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan

Write-Host "`nTry these (will use free Groq if OpenAI quota exceeded):`n" -ForegroundColor Yellow
Write-Host "  ai `"Explain Kelly Criterion`"" -ForegroundColor Cyan
Write-Host "  diagnose `"STO W8114`"" -ForegroundColor Cyan
Write-Host "  gen-script `"Monitor CPU`"" -ForegroundColor Cyan
Write-Host ""
