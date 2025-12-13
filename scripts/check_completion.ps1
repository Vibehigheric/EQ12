<#
.SYNOPSIS
Check if prompt execution is complete and notify

.DESCRIPTION
Monitors the database to detect completion of all 20,000 prompts
Can send notifications when done
#>

param(
    [switch]$WaitForCompletion,
    [int]$CheckIntervalSeconds = 60
)

$dbPath = "C:\EQ12_BROKEN_20251122_210342\logs\prompt_execution.db"
$targetTotal = 20000

function Test-ExecutionComplete {
    if (-not (Test-Path $dbPath)) {
        Write-Host "❌ Database not found" -ForegroundColor Red
        return $false
    }

    $result = python -c @"
import sqlite3
conn = sqlite3.connect('$dbPath')
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM prompts_executed WHERE success=1')
count = c.fetchone()[0]
conn.close()
print(count)
"@

    $completed = [int]$result
    return $completed -ge $targetTotal
}

function Show-CompletionStatus {
    $result = python -c @"
import sqlite3
from datetime import datetime
conn = sqlite3.connect('$dbPath')
c = conn.cursor()

# Get overall stats
c.execute('''SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN success=1 THEN 1 ELSE 0 END) as successful,
    SUM(tokens_used) as total_tokens,
    SUM(CASE WHEN cache_hit=1 THEN 1 ELSE 0 END) as cache_hits
FROM prompts_executed''')
row = c.fetchone()
total, succ, tokens, cache = row

# Get knowledge count
c.execute('SELECT COUNT(*) FROM knowledge_base')
knowledge_count = c.fetchone()[0]

# Get first and last timestamps
c.execute('SELECT MIN(timestamp), MAX(timestamp) FROM prompts_executed')
start, end = c.fetchone()

print(f'{total}|{succ}|{tokens}|{cache}|{knowledge_count}|{start}|{end}')
conn.close()
"@

    $parts = $result -split '\|'
    $total = [int]$parts[0]
    $successful = [int]$parts[1]
    $tokens = [long]$parts[2]
    $cacheHits = [int]$parts[3]
    $knowledgeCount = [int]$parts[4]
    $startTime = $parts[5]
    $endTime = $parts[6]

    $progress = [math]::Round(($total / $targetTotal) * 100, 2)
    $cacheRate = if ($total -gt 0) { [math]::Round(($cacheHits / $total) * 100, 1) } else { 0 }

    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║         EQ12 EXECUTION COMPLETION STATUS              ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 PROGRESS: " -NoNewline -ForegroundColor Yellow
    Write-Host "$total / $targetTotal " -NoNewline -ForegroundColor White
    Write-Host "($progress%)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "✅ SUCCESSFUL: " -NoNewline -ForegroundColor Yellow
    Write-Host "$successful" -ForegroundColor Green
    Write-Host "⚡ CACHE HITS: " -NoNewline -ForegroundColor Yellow
    Write-Host "$cacheHits ($cacheRate%)" -ForegroundColor Cyan
    Write-Host "🎯 TOTAL TOKENS: " -NoNewline -ForegroundColor Yellow
    Write-Host "$($tokens.ToString('N0'))" -ForegroundColor Green
    Write-Host "🧠 KNOWLEDGE ENTRIES: " -NoNewline -ForegroundColor Yellow
    Write-Host "$knowledgeCount" -ForegroundColor Green
    Write-Host ""
    
    if ($total -ge $targetTotal) {
        Write-Host "🎉 ✨ EXECUTION COMPLETE! ✨ 🎉" -ForegroundColor Green
        Write-Host ""
        Write-Host "Started:  $startTime" -ForegroundColor Gray
        Write-Host "Finished: $endTime" -ForegroundColor Gray
        Write-Host ""
        Write-Host "📁 Database: $dbPath" -ForegroundColor Cyan
        Write-Host "📊 Final Report: Run '.\EQ12_PROMPT_RUNNER.ps1 -ReportOnly'" -ForegroundColor Cyan
        Write-Host ""
        return $true
    }
    else {
        $remaining = $targetTotal - $total
        Write-Host "⏳ STILL RUNNING..." -ForegroundColor Yellow
        Write-Host "   Remaining: $remaining prompts" -ForegroundColor White
        Write-Host ""
        return $false
    }
}

# Main execution
if ($WaitForCompletion) {
    Write-Host "Waiting for execution to complete..." -ForegroundColor Cyan
    Write-Host "Checking every $CheckIntervalSeconds seconds" -ForegroundColor Gray
    Write-Host "Press Ctrl+C to stop monitoring`n" -ForegroundColor Gray

    while ($true) {
        $isComplete = Show-CompletionStatus
        
        if ($isComplete) {
            # Play completion sound (Windows)
            [console]::beep(800, 300)
            [console]::beep(1000, 300)
            [console]::beep(1200, 500)
            
            Write-Host "✅ Notification: Execution complete!" -ForegroundColor Green
            break
        }
        
        Write-Host "Next check in $CheckIntervalSeconds seconds..." -ForegroundColor Gray
        Start-Sleep -Seconds $CheckIntervalSeconds
        Clear-Host
    }
}
else {
    Show-CompletionStatus
}
