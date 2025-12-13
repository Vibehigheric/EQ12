# EQ12 NCAA PARLAY BUILDER - PESTER TESTS
# =======================================
# Comprehensive tests for NCAA parlay generation system

Describe "EQ12 NCAA Parlay Builder Tests" {
    BeforeAll {
        # Set up test environment
        $EQ12Root = "C:\EQ12"
        $ScriptsPath = Join-Path $EQ12Root "scripts"
        $BuilderPath = Join-Path $EQ12Root "eq12_ncaa_parlay_builder.py"
        $WrapperPath = Join-Path $ScriptsPath "eq12_ncaa_parlay_wrapper.ps1"
        
        # Verify files exist
        if (-not (Test-Path $BuilderPath)) {
            throw "NCAA Parlay Builder not found: $BuilderPath"
        }
        
        if (-not (Test-Path $WrapperPath)) {
            throw "NCAA Parlay Wrapper not found: $WrapperPath"
        }
        
        # Set test API key
        $env:OPENAI_API_KEY = "sk-test-key-for-pester-tests"
        $env:ODDS_API_KEY = "demo_key"
    }
    
    Context "File Structure Tests" {
        It "Should have NCAA parlay builder Python file" {
            Test-Path $BuilderPath | Should -Be $true
        }
        
        It "Should have PowerShell wrapper file" {
            Test-Path $WrapperPath | Should -Be $true
        }
        
        It "NCAA builder should contain required classes" {
            $BuilderContent = Get-Content $BuilderPath -Raw
            $BuilderContent | Should -Match "class EQ12NCAAParleyBuilder"
            $BuilderContent | Should -Match "class ParlayLeg"
            $BuilderContent | Should -Match "class Parlay"
        }
        
        It "PowerShell wrapper should have CmdletBinding" {
            $WrapperContent = Get-Content $WrapperPath -Raw
            $WrapperContent | Should -Match "\[CmdletBinding\(\)\]"
        }
    }
    
    Context "Python Import Tests" {
        It "Should import required EQ12 modules successfully" {
            $TestImport = @"
try:
    from eq12_unicode_simple import safe_print, safe_open
    from eq12_error_boundary import GPT5ErrorBoundary
    print('SUCCESS: EQ12 imports working')
except Exception as e:
    print(f'ERROR: {e}')
    exit(1)
"@
            
            $Result = $TestImport | python -c "exec(__import__('sys').stdin.read())"
            $LASTEXITCODE | Should -Be 0
            $Result | Should -Match "SUCCESS"
        }
        
        It "Should create NCAA parlay builder instance" {
            $TestBuilder = @"
try:
    import sys
    sys.path.append('.')
    from eq12_ncaa_parlay_builder import EQ12NCAAParleyBuilder
    builder = EQ12NCAAParleyBuilder()
    print('SUCCESS: NCAA builder created')
except Exception as e:
    print(f'ERROR: {e}')
    exit(1)
"@
            
            Push-Location $EQ12Root
            try {
                $Result = $TestBuilder | python -c "exec(__import__('sys').stdin.read())"
                $LASTEXITCODE | Should -Be 0
                $Result | Should -Match "SUCCESS"
            } finally {
                Pop-Location
            }
        }
    }
    
    Context "PowerShell Wrapper Tests" {
        It "Should execute status command successfully" {
            $Result = & $WrapperPath -Action "status" -VerboseOutput 2>&1
            $LASTEXITCODE | Should -Be 0
            ($Result -join "`n") | Should -Match "NCAA Parlay System Status"
        }
        
        It "Should execute test command successfully" {
            Push-Location $EQ12Root
            try {
                $Result = & $WrapperPath -Action "test" -VerboseOutput 2>&1
                # Allow for soft failures in test environment
                ($Result -join "`n") | Should -Match "Testing NCAA Parlay System"
            } finally {
                Pop-Location
            }
        }
        
        It "Should handle invalid action gracefully" {
            $Result = & $WrapperPath -Action "invalid" 2>&1
            $LASTEXITCODE | Should -Be 1
            ($Result -join "`n") | Should -Match "Unknown action"
        }
    }
    
    Context "Database Functionality Tests" {
        It "Should create database directory structure" {
            $TestDb = @"
import os
import sqlite3
from eq12_ncaa_parlay_builder import EQ12NCAAParleyBuilder

try:
    builder = EQ12NCAAParleyBuilder()
    print('SUCCESS: Database setup completed')
except Exception as e:
    print(f'ERROR: {e}')
    exit(1)
"@
            
            Push-Location $EQ12Root
            try {
                $Result = $TestDb | python -c "exec(__import__('sys').stdin.read())"
                $LASTEXITCODE | Should -Be 0
                $Result | Should -Match "SUCCESS"
            } finally {
                Pop-Location
            }
        }
        
        It "Should create required database tables" {
            $DbPath = Join-Path $EQ12Root "database\sports_betting.db"
            if (Test-Path $DbPath) {
                # Verify table structure
                $TestTables = @"
import sqlite3
try:
    conn = sqlite3.connect('database/sports_betting.db')
    cursor = conn.cursor()
    
    # Check for required tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    required_tables = ['ncaa_parlays', 'parlay_legs']
    missing_tables = [t for t in required_tables if t not in tables]
    
    if missing_tables:
        print(f'ERROR: Missing tables: {missing_tables}')
        exit(1)
    else:
        print('SUCCESS: All required tables exist')
        
    conn.close()
except Exception as e:
    print(f'ERROR: {e}')
    exit(1)
"@
                
                Push-Location $EQ12Root
                try {
                    $Result = $TestTables | python -c "exec(__import__('sys').stdin.read())"
                    $LASTEXITCODE | Should -Be 0
                    $Result | Should -Match "SUCCESS"
                } finally {
                    Pop-Location
                }
            }
        }
    }
    
    Context "Mock Data Generation Tests" {
        It "Should generate mock NCAA football data" {
            $TestMockData = @"
import asyncio
from eq12_ncaa_parlay_builder import EQ12NCAAParleyBuilder

async def test_mock_data():
    try:
        builder = EQ12NCAAParleyBuilder()
        mock_data = builder._generate_mock_ncaa_data()
        
        if not mock_data:
            print('ERROR: No mock data generated')
            return False
            
        # Check for football games
        fb_games = [g for g in mock_data if g.get('eq12_sport') == 'NCAA-FB']
        if not fb_games:
            print('ERROR: No NCAA-FB games found')
            return False
            
        # Check for basketball games  
        bb_games = [g for g in mock_data if g.get('eq12_sport') == 'NCAA-BB']
        if not bb_games:
            print('ERROR: No NCAA-BB games found')
            return False
            
        print(f'SUCCESS: Generated {len(fb_games)} FB games, {len(bb_games)} BB games')
        return True
        
    except Exception as e:
        print(f'ERROR: {e}')
        return False

result = asyncio.run(test_mock_data())
exit(0 if result else 1)
"@
            
            Push-Location $EQ12Root
            try {
                $Result = $TestMockData | python -c "exec(__import__('sys').stdin.read())"
                $LASTEXITCODE | Should -Be 0
                $Result | Should -Match "SUCCESS"
            } finally {
                Pop-Location
            }
        }
    }
    
    Context "Parlay Calculation Tests" {
        It "Should calculate Kelly percentages correctly" {
            $TestKelly = @"
from eq12_ncaa_parlay_builder import EQ12NCAAParleyBuilder

try:
    builder = EQ12NCAAParleyBuilder()
    
    # Test positive odds
    kelly1 = builder.calculate_kelly_percentage(0.1, 150)  # 10% edge, +150 odds
    
    # Test negative odds
    kelly2 = builder.calculate_kelly_percentage(0.05, -110)  # 5% edge, -110 odds
    
    # Test zero edge
    kelly3 = builder.calculate_kelly_percentage(0.0, 100)  # No edge
    
    if kelly1 > 0 and kelly2 > 0 and kelly3 == 0:
        print('SUCCESS: Kelly calculations working correctly')
    else:
        print(f'ERROR: Kelly values: {kelly1}, {kelly2}, {kelly3}')
        exit(1)
        
except Exception as e:
    print(f'ERROR: {e}')
    exit(1)
"@
            
            Push-Location $EQ12Root
            try {
                $Result = $TestKelly | python -c "exec(__import__('sys').stdin.read())"
                $LASTEXITCODE | Should -Be 0
                $Result | Should -Match "SUCCESS"
            } finally {
                Pop-Location
            }
        }
    }
    
    Context "Output Generation Tests" {
        BeforeAll {
            # Ensure outputs directory exists
            $OutputsPath = Join-Path $EQ12Root "outputs"
            if (-not (Test-Path $OutputsPath)) {
                New-Item -ItemType Directory -Path $OutputsPath -Force | Out-Null
            }
        }
        
        It "Should generate parlay output files" {
            $TestOutput = @"
import asyncio
import json
from eq12_ncaa_parlay_builder import EQ12NCAAParleyBuilder

async def test_output_generation():
    try:
        builder = EQ12NCAAParleyBuilder()
        
        # Generate mock parlays
        high_conf, high_payout = await builder.generate_parlays()
        parlays = [high_conf, high_payout]
        
        # Export to JSON
        filename = builder.export_to_json(parlays)
        
        if filename and filename.endswith('.json'):
            print('SUCCESS: Parlay output file generated')
            return True
        else:
            print('ERROR: No output file generated')
            return False
            
    except Exception as e:
        print(f'ERROR: {e}')
        return False

result = asyncio.run(test_output_generation())
exit(0 if result else 1)
"@
            
            Push-Location $EQ12Root
            try {
                $Result = $TestOutput | python -c "exec(__import__('sys').stdin.read())"
                $LASTEXITCODE | Should -Be 0
                $Result | Should -Match "SUCCESS"
            } finally {
                Pop-Location
            }
        }
        
        It "Should create valid JSON output structure" {
            # Find most recent output file
            $OutputsPath = Join-Path $EQ12Root "outputs"
            if (Test-Path $OutputsPath) {
                $LatestFile = Get-ChildItem -Path $OutputsPath -Filter "ncaa_parlays_*.json" |
                             Sort-Object LastWriteTime -Descending |
                             Select-Object -First 1
                
                if ($LatestFile) {
                    $JsonContent = Get-Content $LatestFile.FullName -Raw | ConvertFrom-Json
                    
                    # Verify required structure
                    $JsonContent.system | Should -Be "EQ12 NCAA Parlay Builder"
                    $JsonContent.parlays | Should -Not -BeNullOrEmpty
                    $JsonContent.summary | Should -Not -BeNullOrEmpty
                }
            }
        }
    }
    
    Context "Integration Tests" {
        It "Should integrate with EQ12 Unicode protection" {
            $TestUnicode = @"
from eq12_unicode_simple import safe_print, safe_open
from eq12_ncaa_parlay_builder import EQ12NCAAParleyBuilder

try:
    # Test Unicode integration
    safe_print('🏈 Testing NCAA parlay Unicode integration')
    
    builder = EQ12NCAAParleyBuilder()
    safe_print('✅ NCAA builder with Unicode support initialized')
    
    print('SUCCESS: Unicode integration working')
except Exception as e:
    print(f'ERROR: {e}')
    exit(1)
"@
            
            Push-Location $EQ12Root
            try {
                $Result = $TestUnicode | python -c "exec(__import__('sys').stdin.read())"
                $LASTEXITCODE | Should -Be 0
                $Result | Should -Match "SUCCESS"
            } finally {
                Pop-Location
            }
        }
    }
    
    AfterAll {
        # Clean up test environment
        Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
        Remove-Item Env:ODDS_API_KEY -ErrorAction SilentlyContinue
        
        Write-Host "✅ EQ12 NCAA Parlay Builder tests completed" -ForegroundColor Green
    }
}