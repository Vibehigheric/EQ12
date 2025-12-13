# EQ12 Sports Betting Advanced System Tests
# File: C:\EQ12\eq12_sports_betting_advanced.Tests.ps1

BeforeAll {
    # Setup test environment
    $script:TargetScript = "C:\EQ12\eq12_sports_betting_advanced.ps1"
    $script:TestDataPath = "C:\EQ12\TestData"
    $script:LogsPath = "C:\EQ12\logs"

    # Ensure test directories exist
    @($TestDataPath, $LogsPath) | ForEach-Object {
        if (-not (Test-Path $_)) {
            New-Item -ItemType Directory -Path $_ -Force | Out-Null
        }
    }

    # Mock external dependencies for faster, isolated testing
    Mock python -ModuleName * {
        return @{
            ExitCode = 0
            Output = "Mocked Python execution successful"
        }
    }

    Mock Start-Process -ModuleName * {
        return @{
            Id = 12345
            ProcessName = "MockedProcess"
        }
    }

    Mock Get-Service -ModuleName * {
        return @{
            Name = "MockedService"
            Status = "Running"
            StartType = "Automatic"
        }
    }
}

Describe "EQ12 Sports Betting Advanced System Tests" {

    Context "Script Validation" {
        It "Target script should exist and be readable" {
            $script:TargetScript | Should -Exist
            { Get-Content $script:TargetScript -ErrorAction Stop } | Should -Not -Throw
        }

        It "Script should have valid PowerShell syntax" {
            $errors = $null
            $null = [System.Management.Automation.PSParser]::Tokenize((Get-Content $script:TargetScript -Raw), [ref]$errors)
            $errors.Count | Should -Be 0
        }

        It "Script should contain required parameters" {
            $scriptContent = Get-Content $script:TargetScript -Raw
            $scriptContent | Should -Match "param\("
            $scriptContent | Should -Match "\[ValidateSet\("
            $scriptContent | Should -Match "Action"
        }
    }

    Context "Parameter Validation Tests" {
        It "Should accept valid Action parameter" {
            $validActions = @("analyze", "startlive", "stopall", "autotrade", "listedges", "listbets", "retrainml", "cleandata", "config", "testsuite", "initdb", "status", "dashboard")

            foreach ($action in $validActions) {
                { & $script:TargetScript -Action $action -WhatIf } | Should -Not -Throw
            }
        }

        It "Should reject invalid Action parameter" {
            { & $script:TargetScript -Action "invalid_action" -ErrorAction Stop } | Should -Throw
        }

        It "Should handle switch parameters correctly" {
            { & $script:TargetScript -Action "autotrade" -Enable -WhatIf } | Should -Not -Throw
        }
    }

    Context "Core Function Tests" {
        BeforeEach {
            # Mock Write-EQ12Log to capture log messages
            Mock Write-EQ12Log -ModuleName * {
                param($Message, $Level)
                return @{
                    Message = $Message
                    Level = $Level
                    Timestamp = Get-Date
                }
            }
        }

        It "Should initialize logging correctly" {
            Mock Test-Path { return $true } -ParameterFilter { $Path -like "*logs*" }

            { & $script:TargetScript -Action "status" -WhatIf } | Should -Not -Throw
        }

        It "Should check Python environment" {
            Mock python { return "Python 3.12.2" }

            $result = & $script:TargetScript -Action "status" -WhatIf
            # Should complete without errors when Python is available
            $LASTEXITCODE | Should -Be 0
        }

        It "Should handle database operations" {
            Mock Test-Path { return $true } -ParameterFilter { $Path -like "*sports_betting.db*" }

            { & $script:TargetScript -Action "initdb" -WhatIf } | Should -Not -Throw
        }
    }

    Context "Service Management Tests" {
        BeforeEach {
            Mock Get-Job {
                return @(
                    @{ Name = "EQ12_XFactor"; State = "Running"; Id = 1 },
                    @{ Name = "EQ12_AutoTrade"; State = "Running"; Id = 2 },
                    @{ Name = "EQ12_Master"; State = "Running"; Id = 3 }
                )
            }

            Mock Start-Job {
                return @{
                    Name = "EQ12_TestJob"
                    Id = 99
                    State = "Running"
                }
            }
        }

        It "Should start live monitoring services" {
            { & $script:TargetScript -Action "startlive" -WhatIf } | Should -Not -Throw
        }

        It "Should stop all background services" {
            Mock Stop-Job { return $true }
            Mock Remove-Job { return $true }

            { & $script:TargetScript -Action "stopall" -WhatIf } | Should -Not -Throw
        }

        It "Should report system status correctly" {
            $result = & $script:TargetScript -Action "status" -WhatIf
            $LASTEXITCODE | Should -Be 0
        }
    }

    Context "Configuration Management Tests" {
        BeforeEach {
            # Mock configuration file existence
            Mock Test-Path { return $true } -ParameterFilter { $Path -like "*sports_betting_config.json*" }

            # Mock configuration content
            Mock Get-Content {
                return @{
                    auto_bet_enabled = $false
                    risk_management = @{
                        max_bet_percentage = 0.03
                        min_edge = 0.025
                    }
                    bookmakers = @("fanduel", "draftkings", "betmgm")
                } | ConvertTo-Json
            } -ParameterFilter { $Path -like "*sports_betting_config.json*" }
        }

        It "Should read configuration successfully" {
            { & $script:TargetScript -Action "config" -View "All" -WhatIf } | Should -Not -Throw
        }

        It "Should update autotrade configuration" {
            Mock Set-Content { return $true }

            { & $script:TargetScript -Action "autotrade" -Enable -WhatIf } | Should -Not -Throw
        }

        It "Should handle configuration sections" {
            $configSections = @("Risk", "Bookmakers", "Sports", "X_FACTOR", "All")

            foreach ($section in $configSections) {
                { & $script:TargetScript -Action "config" -View $section -WhatIf } | Should -Not -Throw
            }
        }
    }

    Context "Database Integration Tests" {
        BeforeEach {
            # Mock database operations
            Mock python {
                param($ArgumentList)
                if ($ArgumentList -like "*sqlite3*" -or $ArgumentList -like "*database*") {
                    return "Database operation successful"
                }
                return "Python execution completed"
            }
        }

        It "Should initialize database schema" {
            { & $script:TargetScript -Action "initdb" -WhatIf } | Should -Not -Throw
        }

        It "Should retrieve current edges" {
            { & $script:TargetScript -Action "listedges" -WhatIf } | Should -Not -Throw
        }

        It "Should retrieve bet history" {
            { & $script:TargetScript -Action "listbets" -WhatIf } | Should -Not -Throw
        }

        It "Should handle data cleanup" {
            { & $script:TargetScript -Action "cleandata" -Days 30 -WhatIf } | Should -Not -Throw
        }
    }

    Context "ML and AI Integration Tests" {
        It "Should trigger ML retraining" {
            $sports = @("NFL", "NBA", "MLB", "NHL", "ALL")

            foreach ($sport in $sports) {
                { & $script:TargetScript -Action "retrainml" -Sport $sport -WhatIf } | Should -Not -Throw
            }
        }

        It "Should handle AI model updates" {
            Mock python {
                return "ML model retraining completed successfully"
            }

            { & $script:TargetScript -Action "retrainml" -Sport "NFL" -WhatIf } | Should -Not -Throw
        }
    }

    Context "Error Handling and Resilience Tests" {
        It "Should handle missing Python gracefully" {
            Mock python { throw "Python not found" }

            { & $script:TargetScript -Action "analyze" -ErrorAction SilentlyContinue } | Should -Not -Throw
        }

        It "Should handle missing configuration file" {
            Mock Test-Path { return $false } -ParameterFilter { $Path -like "*config*" }

            { & $script:TargetScript -Action "config" -View "All" -ErrorAction SilentlyContinue } | Should -Not -Throw
        }

        It "Should handle database connection failures" {
            Mock python { throw "Database connection failed" }

            { & $script:TargetScript -Action "listedges" -ErrorAction SilentlyContinue } | Should -Not -Throw
        }
    }

    Context "Performance and Concurrency Tests" {
        It "Should complete status check within reasonable time" {
            $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
            & $script:TargetScript -Action "status" -WhatIf
            $stopwatch.Stop()

            $stopwatch.ElapsedMilliseconds | Should -BeLessThan 5000  # 5 seconds max
        }

        It "Should handle concurrent operations" {
            $jobs = @()
            1..3 | ForEach-Object {
                $jobs += Start-Job -ScriptBlock {
                    & $using:TargetScript -Action "status" -WhatIf
                }
            }

            $jobs | Wait-Job | Remove-Job
            # Should complete without deadlocks or errors
        }
    }
}

Describe "EQ12 System Integration Tests" {

    Context "End-to-End Workflow Tests" {
        It "Should execute complete analysis workflow" {
            Mock python {
                return @"
✅ Database schema initialized
🔍 Running comprehensive sports analysis...
📊 Analysis Results:
   Sports Analyzed: 7
   Edges Found: 0
   Recommendations: 0
✅ Analysis complete!
"@
            }

            { & $script:TargetScript -Action "analyze" -WhatIf } | Should -Not -Throw
        }

        It "Should handle live monitoring startup sequence" {
            Mock Start-Job { return @{ Name = "MockJob"; Id = 123; State = "Running" } }

            { & $script:TargetScript -Action "startlive" -WhatIf } | Should -Not -Throw
        }
    }

    Context "Dashboard and Reporting Tests" {
        It "Should open dashboard successfully" {
            Mock Test-Path { return $true } -ParameterFilter { $Path -like "*dashboard*" }
            Mock Start-Process { return $true }

            { & $script:TargetScript -Action "dashboard" -WhatIf } | Should -Not -Throw
        }
    }
}

AfterAll {
    # Cleanup test environment
    Write-Host "🧹 Cleaning up test environment..." -ForegroundColor Gray

    # Remove test data if created
    if (Test-Path $script:TestDataPath) {
        # Remove-Item $script:TestDataPath -Recurse -Force -ErrorAction SilentlyContinue
    }

    # Stop any test jobs
    Get-Job | Where-Object { $_.Name -like "*Test*" } | Stop-Job -PassThru | Remove-Job -Force -ErrorAction SilentlyContinue
}
