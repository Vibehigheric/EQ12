<#
.SYNOPSIS
Monitor EQ12 prompt execution progress in real-time

.DESCRIPTION
Displays live statistics from the prompt_execution database
without interrupting the running process
#>

param(
    [int]$RefreshSeconds = 30,
    [switch]$Continuous
)

$dbPath = "C:\EQ12_BROKEN_20251122_210342\logs\prompt_execution.db"

function Get-ExecutionStats {
    if (-not (Test-Path $dbPath)) {
        Write-Host "Database not found: $dbPath" -ForegroundColor Red
        return
    }

    $stats = python -c @"
import sqlite3
conn = sqlite3.connect('$dbPath')
c = conn.cursor()

# Overall stats
c.execute('''SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN success=1 THEN 1 ELSE 0 END) as successful,
    SUM(tokens_used) as total_tokens,
    ROUND(AVG(execution_time), 2) as avg_time,
    SUM(CASE WHEN cache_hit=1 THEN 1 ELSE 0 END) as cache_hits
FROM prompts_executed''')
row = c.fetchone()
print(f'{row[0]}|{row[1]}|{row[2]}|{row[3]}|{row[4]}')

# Category breakdown
c.execute('''SELECT category, COUNT(*) FROM prompts_executed 
             WHERE success=1 GROUP BY category ORDER BY COUNT(*) DESC LIMIT 5''')
categories = c.fetchall()
for cat in categories:
    print(f'CAT|{cat[0]}|{cat[1]}')

# Provider breakdown
c.execute('''SELECT provider, COUNT(*) FROM prompts_executed 
             WHERE success=1 AND provider IS NOT NULL 
             GROUP BY provider ORDER BY COUNT(*) DESC''')
providers = c.fetchall()
for prov in providers:
    print(f'PROV|{prov[0]}|{prov[1]}')

conn.close()
"@

    $lines = $stats -split "`n"
    $main = $lines[0] -split '\|'
    
    $total = [int]$main[0]
    $successful = [int]$main[1]
    $tokens = [long]$main[2]
    $avgTime = $main[3]
    $cacheHits = [int]$main[4]
    
    $successRate = if ($total -gt 0) { [math]::Round(($successful / $total) * 100, 1) } else { 0 }
    $cacheRate = if ($total -gt 0) { [math]::Round(($cacheHits / $total) * 100, 1) } else { 0 }
    $remaining = 20000 - $total
    $progress = if ($total -gt 0) { [math]::Round(($total / 20000) * 100, 2) } else { 0 }
    
    Clear-Host
    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  EQ12 PROMPT EXECUTION - LIVE MONITORING                 ║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📊 PROGRESS: " -NoNewline -ForegroundColor Yellow
    Write-Host "$total / 20,000 " -NoNewline -ForegroundColor Green
    Write-Host "($progress%)" -ForegroundColor Cyan
    Write-Host "⏱️  REMAINING: " -NoNewline -ForegroundColor Yellow
    Write-Host "$remaining prompts" -ForegroundColor White
    Write-Host ""
    Write-Host "✅ SUCCESS RATE: " -NoNewline -ForegroundColor Yellow
    Write-Host "$successful / $total " -NoNewline -ForegroundColor Green
    Write-Host "($successRate%)" -ForegroundColor Cyan
    Write-Host "⚡ CACHE HITS: " -NoNewline -ForegroundColor Yellow
    Write-Host "$cacheHits / $total " -NoNewline -ForegroundColor Green
    Write-Host "($cacheRate%)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🎯 TOTAL TOKENS: " -NoNewline -ForegroundColor Yellow
    Write-Host "$($tokens.ToString('N0'))" -ForegroundColor Green
    Write-Host "⏱️  AVG TIME: " -NoNewline -ForegroundColor Yellow
    Write-Host "${avgTime}s per prompt" -ForegroundColor Green
    
    # Categories
    Write-Host ""
    Write-Host "📁 TOP CATEGORIES:" -ForegroundColor Yellow
    $catLines = $lines | Where-Object { $_ -like "CAT|*" }
    foreach ($line in $catLines) {
        $parts = $line -split '\|'
        Write-Host "   • $($parts[1]): " -NoNewline -ForegroundColor White
        Write-Host "$($parts[2]) prompts" -ForegroundColor Cyan
    }
    
    # Providers
    Write-Host ""
    Write-Host "🤖 AI PROVIDERS:" -ForegroundColor Yellow
    $provLines = $lines | Where-Object { $_ -like "PROV|*" }
    foreach ($line in $provLines) {
        $parts = $line -split '\|'
        Write-Host "   • $($parts[1]): " -NoNewline -ForegroundColor White
        Write-Host "$($parts[2]) prompts" -ForegroundColor Green
    }
    
    # Estimated completion
    if ($total -gt $cacheHits) {
        $newPrompts = $total - $cacheHits
        $timePerNew = if ($avgTime -gt 0) { [double]$avgTime } else { 20 }
        $remainingNew = $remaining
        $estimatedMinutes = [math]::Round(($remainingNew * $timePerNew) / 60, 0)
        $estimatedHours = [math]::Round($estimatedMinutes / 60, 1)
        
        Write-Host ""
        Write-Host "⏰ ESTIMATED COMPLETION:" -ForegroundColor Yellow
        if ($estimatedHours -gt 1) {
            Write-Host "   ~$estimatedHours hours ($estimatedMinutes minutes)" -ForegroundColor Cyan
        }
        else {
            Write-Host "   ~$estimatedMinutes minutes" -ForegroundColor Cyan
        }
    }
    
    Write-Host ""
    Write-Host "Last Updated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
    Write-Host ""
}

# Main loop
if ($Continuous) {
    Write-Host "Monitoring execution every $RefreshSeconds seconds..." -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop monitoring" -ForegroundColor Gray
    Write-Host ""
    
    while ($true) {
        Get-ExecutionStats
        Start-Sleep -Seconds $RefreshSeconds
    }
}
else {
    Get-ExecutionStats
}
