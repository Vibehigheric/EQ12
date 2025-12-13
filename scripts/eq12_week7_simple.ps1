# EQ12 NCAA Week 7 Conference Parlay Automation
# PowerShell automation wrapper for comprehensive Week 7 conference parlay generation

param(
    [string]$Action = "generate-all"
)

$ErrorActionPreference = "Stop"
$EQ12Root = "C:\EQ12"
$StartTime = Get-Date

Write-Host "🏈 EQ12 NCAA WEEK 7 CONFERENCE PARLAY SUITE" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor DarkGray
Write-Host "📅 Target: Week 7, 2025 NCAA Football Season" -ForegroundColor Cyan
Write-Host "🎯 Covering ALL FBS Conferences + Top 25 Master Ticket" -ForegroundColor Yellow

try {
    # Verify Python environment
    $PythonPath = Get-Command python -ErrorAction SilentlyContinue
    if (-not $PythonPath) {
        throw "Python not found in PATH. Please install Python 3.12+"
    }
    
    # Verify EQ12 Week 7 builder exists
    $BuilderPath = Join-Path $EQ12Root "eq12_ncaa_week7_conference_builder.py"
    if (-not (Test-Path $BuilderPath)) {
        throw "Week 7 Conference Builder not found at: $BuilderPath"
    }
    
    # Check for Week 7 pack integration
    $Week7PackPath = Join-Path $EQ12Root "EQ12_NCAA_Parlay_Week7_Pack"
    if (Test-Path $Week7PackPath) {
        Write-Host "✅ Week 7 Pack detected - Enhanced features available" -ForegroundColor Green
    }
    
    # Set up OpenAI API key if needed
    $OpenAIApiKey = [Environment]::GetEnvironmentVariable("OPENAI_API_KEY")
    if (-not $OpenAIApiKey) {
        Write-Warning "⚠️ OPENAI_API_KEY not set. Setting for session."
        $env:OPENAI_API_KEY = "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"
    }
    
    # Ensure output directories exist
    $Directories = @("outputs", "logs\parlays", "database")
    foreach ($Dir in $Directories) {
        $FullPath = Join-Path $EQ12Root $Dir
        if (-not (Test-Path $FullPath)) {
            New-Item -ItemType Directory -Path $FullPath -Force | Out-Null
            Write-Verbose "Created directory: $FullPath"
        }
    }
    
    # Execute action
    if ($Action -eq "generate-all") {
        Write-Host "🎯 Generating ALL Conference Week 7 Parlays..." -ForegroundColor Yellow
        Write-Host "📊 This includes: SEC, Big Ten, ACC, Big 12, American, Mountain West, MAC, Sun Belt, Pac-12, Independent" -ForegroundColor Cyan
        
        & python $BuilderPath
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Week 7 conference parlays generated successfully!" -ForegroundColor Green
            
            # Show results
            Write-Host "`n📊 Conference Coverage Check:" -ForegroundColor Cyan
            $Conferences = @("sec", "bigten", "acc", "big12", "american", "mountainwest", "mac", "sunbelt", "pac12", "independent")
            $FoundOutputs = 0
            
            foreach ($Conf in $Conferences) {
                $Pattern = "outputs\$Conf" + "_week7_*.json"
                $Files = Get-ChildItem -Path $Pattern -ErrorAction SilentlyContinue
                if ($Files) {
                    $FoundOutputs++
                    Write-Host "   ✅ $($Conf.ToUpper())" -ForegroundColor Green
                } else {
                    Write-Host "   ⚠️ $($Conf.ToUpper()): No output" -ForegroundColor Yellow
                }
            }
            
            Write-Host "`n🏆 Total Conference Coverage: $FoundOutputs/10" -ForegroundColor $(if ($FoundOutputs -eq 10) { "Green" } else { "Yellow" })
        } else {
            throw "Week 7 conference parlay generation failed with exit code: $LASTEXITCODE"
        }
    }
    elseif ($Action -eq "status") {
        Write-Host "📊 EQ12 Week 7 Parlay System Status" -ForegroundColor Yellow
        
        # Check database
        $DbPath = Join-Path $EQ12Root "database\sports_betting.db"
        if (Test-Path $DbPath) {
            $DbSize = (Get-Item $DbPath).Length / 1KB
            $DbSizeRounded = [math]::Round($DbSize, 1)
            Write-Host "✅ Database exists: $DbSizeRounded KB" -ForegroundColor Green
        } else {
            Write-Host "❌ Database not found" -ForegroundColor Red
        }
        
        # Check outputs
        Write-Host "`n🏈 Output Files:" -ForegroundColor Yellow
        $OutputFiles = Get-ChildItem -Path "outputs\*week7*.json" -ErrorAction SilentlyContinue
        if ($OutputFiles) {
            foreach ($File in ($OutputFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 10)) {
                Write-Host "   📄 $($File.Name)" -ForegroundColor White
            }
        } else {
            Write-Host "   ⚠️ No Week 7 outputs found" -ForegroundColor Yellow
        }
    }
    elseif ($Action -eq "test") {
        Write-Host "🧪 Testing Week 7 Conference System..." -ForegroundColor Yellow
        
        # Simple Python test
        $TestResult = & python -c @"
try:
    import json
    from eq12_ncaa_week7_conference_builder import EQ12NCAAWeek7ConferenceBuilder
    print('SUCCESS: Week 7 imports working')
    builder = EQ12NCAAWeek7ConferenceBuilder()
    print('SUCCESS: Week 7 Conference Builder initialized')
    conferences = list(builder.conferences.keys())
    print(f'SUCCESS: {len(conferences)} conferences loaded')
except Exception as e:
    print(f'ERROR: {e}')
    exit(1)
"@
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Week 7 Conference System test passed!" -ForegroundColor Green
        } else {
            Write-Host "❌ Week 7 Conference System test failed!" -ForegroundColor Red
        }
        
        Write-Host $TestResult -ForegroundColor Cyan
    }
    elseif ($Action -eq "clean") {
        Write-Host "🧹 Cleaning Week 7 outputs..." -ForegroundColor Yellow
        
        $CleanedFiles = 0
        $CleanPatterns = @("outputs\*week7*.json", "logs\parlays\*week7*")
        
        foreach ($Pattern in $CleanPatterns) {
            $Files = Get-ChildItem -Path $Pattern -ErrorAction SilentlyContinue
            foreach ($File in $Files) {
                Remove-Item $File.FullName -Force
                $CleanedFiles++
            }
        }
        
        Write-Host "✅ Cleaned $CleanedFiles Week 7 files" -ForegroundColor Green
    }
    else {
        Write-Host "❌ Unknown action: $Action" -ForegroundColor Red
        Write-Host "Available actions: generate-all, status, test, clean" -ForegroundColor Yellow
        exit 1
    }
    
    # Performance summary
    Write-Host "`n⚡ Performance Summary:" -ForegroundColor Magenta
    Write-Host "   🕒 Execution Time: $((Get-Date) - $StartTime)" -ForegroundColor White
    Write-Host "   🎯 Action: $Action" -ForegroundColor White
    
} catch {
    Write-Error "❌ EQ12 Week 7 operation failed: $($_.Exception.Message)"
    Write-Host "`nTroubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Verify Python 3.12+ is installed" -ForegroundColor White
    Write-Host "2. Ensure eq12_ncaa_week7_conference_builder.py exists" -ForegroundColor White
    Write-Host "3. Check logs in: $EQ12Root\logs\parlays\" -ForegroundColor White
    exit 1
}

Write-Host "`n🎉 EQ12 NCAA Week 7 Conference Suite completed!" -ForegroundColor Green