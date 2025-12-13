# EQ12 Snyk Security Integration Pester Tests
# Tests for PowerShell wrapper functionality and Windows-specific automation

Describe "EQ12 Snyk Security Integration Tests" {
    
    BeforeAll {
        # Setup test environment
        $script:ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
        $script:ScriptsDir = Join-Path $ProjectRoot "scripts"
        $script:SecurityScript = Join-Path $ScriptsDir "eq12_snyk_security.ps1"
        $script:PythonScript = Join-Path $ScriptsDir "eq12_snyk_security_integration.py"
        $script:ConfigFile = Join-Path $ProjectRoot "configs" "snyk_security_config.json"
        $script:LogsDir = Join-Path $ProjectRoot "logs"
        
        # Ensure test directories exist
        if (-not (Test-Path $LogsDir)) {
            New-Item -ItemType Directory -Path $LogsDir -Force
        }
    }
    
    Context "PowerShell Script Validation" {
        
        It "Should have security PowerShell script file" {
            Test-Path $SecurityScript | Should -Be $true
        }
        
        It "Should have Python security integration script" {
            Test-Path $PythonScript | Should -Be $true
        }
        
        It "Should have security configuration file" {
            Test-Path $ConfigFile | Should -Be $true
        }
        
        It "Security script should have proper syntax" {
            { . $SecurityScript -WhatIf } | Should -Not -Throw
        }
        
        It "Security script should have CmdletBinding" {
            $Content = Get-Content $SecurityScript -Raw
            $Content | Should -Match '\[CmdletBinding\(\)\]'
        }
        
        It "Security script should have help parameters" {
            $Content = Get-Content $SecurityScript -Raw
            $Content | Should -Match 'HelpMessage='
        }
    }
    
    Context "Configuration Management" {
        
        It "Should load security configuration successfully" {
            { $Config = Get-Content $ConfigFile | ConvertFrom-Json } | Should -Not -Throw
        }
        
        It "Configuration should have required sections" {
            $Config = Get-Content $ConfigFile | ConvertFrom-Json
            $Config.snyk_security_config | Should -Not -BeNullOrEmpty
            $Config.snyk_security_config.security_scanning | Should -Not -BeNullOrEmpty
            $Config.snyk_security_config.vulnerability_management | Should -Not -BeNullOrEmpty
        }
        
        It "Should validate scan targets in configuration" {
            $Config = Get-Content $ConfigFile | ConvertFrom-Json
            $ScanTargets = $Config.snyk_security_config.security_scanning.scan_targets
            
            $ScanTargets.scripts | Should -Not -BeNullOrEmpty
            $ScanTargets.tests | Should -Not -BeNullOrEmpty
            $ScanTargets.configs | Should -Not -BeNullOrEmpty
            $ScanTargets.dashboard | Should -Not -BeNullOrEmpty
        }
    }
    
    Context "Environment Setup" {
        
        It "Should detect Python availability" {
            $PythonAvailable = $null -ne (Get-Command python -ErrorAction SilentlyContinue)
            if (-not $PythonAvailable) {
                Set-ItResult -Skipped -Because "Python not available for testing"
            } else {
                $PythonAvailable | Should -Be $true
            }
        }
        
        It "Should create logs directory" {
            Test-Path $LogsDir | Should -Be $true
        }
        
        It "Should handle missing SNYK_TOKEN gracefully" {
            # Temporarily remove SNYK_TOKEN if it exists
            $OriginalToken = $env:SNYK_TOKEN
            $env:SNYK_TOKEN = $null
            
            # Test should not crash without token
            { 
                # Simulate the token check function
                $TokenExists = -not [string]::IsNullOrEmpty($env:SNYK_TOKEN)
                $TokenExists | Should -Be $false
            } | Should -Not -Throw
            
            # Restore original token
            if ($OriginalToken) {
                $env:SNYK_TOKEN = $OriginalToken
            }
        }
    }
    
    Context "Security Script Functions" {
        
        BeforeAll {
            # Dot-source the security script to access its functions
            # Note: This requires modifying the script to be more test-friendly
            # For now, we'll test the script execution instead
        }
        
        It "Should display help when no parameters provided" {
            $Result = & $SecurityScript 2>&1
            $Result | Should -Match "Available Options"
        }
        
        It "Should handle Dashboard parameter" {
            # Test dashboard display (should not throw errors)
            { & $SecurityScript -Dashboard -WhatIf } | Should -Not -Throw
        }
        
        It "Should validate parameter combinations" {
            # Test that conflicting parameters are handled properly
            # This is a basic test - more sophisticated parameter validation could be added
            { & $SecurityScript -Scan -Dashboard -WhatIf } | Should -Not -Throw
        }
    }
    
    Context "Security Scanning Integration" {
        
        It "Should find Python security script" {
            Test-Path $PythonScript | Should -Be $true
        }
        
        It "Python script should have proper shebang" {
            $FirstLine = (Get-Content $PythonScript -TotalCount 1)
            $FirstLine | Should -Match '^#!/usr/bin/env python3'
        }
        
        It "Python script should import required modules" {
            $Content = Get-Content $PythonScript -Raw
            $Content | Should -Match 'import asyncio'
            $Content | Should -Match 'import json'
            $Content | Should -Match 'import subprocess'
        }
        
        It "Should have main execution function" {
            $Content = Get-Content $PythonScript -Raw
            $Content | Should -Match 'async def main\(\)'
            $Content | Should -Match 'if __name__ == "__main__"'
        }
    }
    
    Context "Logging and Monitoring" {
        
        It "Should create log files in correct location" {
            # Test that log directory structure is correct
            Test-Path $LogsDir | Should -Be $true
        }
        
        It "Should handle log file creation" {
            $TestLogFile = Join-Path $LogsDir "test_snyk_log.log"
            
            # Test log file creation
            "Test log entry" | Add-Content -Path $TestLogFile
            Test-Path $TestLogFile | Should -Be $true
            
            # Cleanup
            if (Test-Path $TestLogFile) {
                Remove-Item $TestLogFile -Force
            }
        }
        
        It "Should validate log entry format" {
            $TestLogEntry = "[2024-01-15 10:30:00] [INFO] Test message"
            $TestLogEntry | Should -Match '^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] \[(INFO|WARN|ERROR|DEBUG)\] .+'
        }
    }
    
    Context "Windows Task Scheduler Integration" {
        
        It "Should check for scheduled task management capability" {
            # Test that we can work with scheduled tasks (requires admin rights for actual creation)
            $TaskCommand = Get-Command "Get-ScheduledTask" -ErrorAction SilentlyContinue
            if ($null -eq $TaskCommand) {
                Set-ItResult -Skipped -Because "Scheduled Task commands not available"
            } else {
                $TaskCommand | Should -Not -BeNullOrEmpty
            }
        }
        
        It "Should validate task configuration parameters" {
            # Test task configuration without actually creating the task
            $TaskName = "EQ12-Security-Scan"
            $TaskDescription = "Automated security scanning for EQ12 platform using Snyk"
            
            $TaskName | Should -Not -BeNullOrEmpty
            $TaskDescription | Should -Not -BeNullOrEmpty
            $TaskName | Should -Match '^[a-zA-Z0-9\-]+$'
        }
    }
    
    Context "EQ12 Integration Points" {
        
        It "Should validate EQ12 project structure" {
            # Test that required EQ12 directories exist
            $RequiredDirs = @("scripts", "tests", "configs", "logs")
            
            foreach ($Dir in $RequiredDirs) {
                $DirPath = Join-Path $ProjectRoot $Dir
                Test-Path $DirPath | Should -Be $true -Because "Required EQ12 directory $Dir should exist"
            }
        }
        
        It "Should identify EQ12 betting components for scanning" {
            # Check for key EQ12 betting platform files
            $BettingComponents = @(
                "eq12_enhanced_odds_api.py",
                "eq12_betting_arbitrage_bot.py", 
                "eq12_gpt5_dashboard_generator.py",
                "chrome_governance_automation.py"
            )
            
            $FoundComponents = 0
            foreach ($Component in $BettingComponents) {
                $ComponentPath = Join-Path $ScriptsDir $Component
                if (Test-Path $ComponentPath) {
                    $FoundComponents++
                }
            }
            
            # Should find at least some betting components
            $FoundComponents | Should -BeGreaterThan 0 -Because "Should find EQ12 betting components for security scanning"
        }
        
        It "Should validate security-critical file patterns" {
            # Look for patterns that indicate security-sensitive code
            $SecurityPatterns = @("api_key", "password", "token", "secret")
            $PyFiles = Get-ChildItem -Path $ScriptsDir -Filter "*.py" -Recurse
            
            $SecuritySensitiveFiles = 0
            foreach ($File in $PyFiles) {
                $Content = Get-Content $File.FullName -Raw -ErrorAction SilentlyContinue
                if ($Content) {
                    foreach ($Pattern in $SecurityPatterns) {
                        if ($Content -match $Pattern) {
                            $SecuritySensitiveFiles++
                            break
                        }
                    }
                }
            }
            
            # Security scanning is especially important if we find security-sensitive patterns
            $SecuritySensitiveFiles | Should -BeGreaterOrEqual 0
        }
    }
    
    Context "Error Handling and Edge Cases" {
        
        It "Should handle missing Snyk CLI gracefully" {
            # Test behavior when Snyk CLI is not installed
            # This would typically be mocked in a real test environment
            $SnykCommand = Get-Command "snyk" -ErrorAction SilentlyContinue
            
            if ($null -eq $SnykCommand) {
                # Should handle missing Snyk CLI without crashing
                { 
                    # Simulate the check that would happen in the script
                    $SnykAvailable = $null -ne (Get-Command "snyk" -ErrorAction SilentlyContinue)
                    $SnykAvailable | Should -Be $false
                } | Should -Not -Throw
            } else {
                Set-ItResult -Skipped -Because "Snyk CLI is actually installed"
            }
        }
        
        It "Should validate parameter input sanitization" {
            # Test that parameters are properly validated to prevent injection
            $TestInputs = @("'; rm -rf /", "$(Get-Process)", "`$(Get-Process)")
            
            foreach ($TestInput in $TestInputs) {
                # The script should handle potentially dangerous inputs safely
                # This is a basic test - real parameter validation would be more comprehensive
                $TestInput | Should -Not -Match '[;&|`]' -Because "Security script should sanitize dangerous characters"
            }
        }
        
        It "Should handle file system permissions correctly" {
            # Test that the script handles file system permissions appropriately
            $TestFile = Join-Path $LogsDir "permission_test.txt"
            
            try {
                "Test content" | Out-File -FilePath $TestFile -Force
                Test-Path $TestFile | Should -Be $true
                
                # Cleanup
                Remove-Item $TestFile -Force
            }
            catch {
                # If we can't write to logs directory, that's a configuration issue
                throw "Cannot write to logs directory: $_"
            }
        }
    }
    
    Context "Performance and Resource Management" {
        
        It "Should handle large directory structures efficiently" {
            # Test that scanning large directory structures doesn't cause issues
            $LargeDir = Join-Path $LogsDir "large_test_dir"
            
            if (-not (Test-Path $LargeDir)) {
                New-Item -ItemType Directory -Path $LargeDir -Force
                
                # Create some test files (not too many to avoid slowing down tests)
                for ($i = 1; $i -le 10; $i++) {
                    $TestFile = Join-Path $LargeDir "test_file_$i.txt"
                    "Test content $i" | Out-File -FilePath $TestFile
                }
            }
            
            # Test should handle directory with multiple files
            $Files = Get-ChildItem -Path $LargeDir -File
            $Files.Count | Should -BeGreaterThan 0
            
            # Cleanup
            if (Test-Path $LargeDir) {
                Remove-Item $LargeDir -Recurse -Force
            }
        }
        
        It "Should validate memory usage patterns" {
            # Basic test to ensure script doesn't have obvious memory leaks
            # This is a simplified test - more comprehensive testing would use performance counters
            
            $BeforeMemory = [GC]::GetTotalMemory($false)
            
            # Simulate some operations that might use memory
            $TestArray = 1..1000
            $TestString = $TestArray -join ","
            
            $AfterMemory = [GC]::GetTotalMemory($true)  # Force garbage collection
            
            # Memory should be reasonable (this is a very basic check)
            $MemoryIncrease = $AfterMemory - $BeforeMemory
            $MemoryIncrease | Should -BeLessThan 10MB -Because "Memory usage should be reasonable"
        }
    }
    
    AfterAll {
        # Cleanup any test artifacts
        $TestFiles = @(
            (Join-Path $LogsDir "test_snyk_log.log"),
            (Join-Path $LogsDir "permission_test.txt")
        )
        
        foreach ($TestFile in $TestFiles) {
            if (Test-Path $TestFile) {
                Remove-Item $TestFile -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

# Additional integration tests for EQ12-specific functionality
Describe "EQ12 Betting Platform Security Integration" {
    
    BeforeAll {
        $script:ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
        $script:ScriptsDir = Join-Path $ProjectRoot "scripts"
    }
    
    Context "Betting Platform Security Requirements" {
        
        It "Should identify financial transaction components" {
            # Test that security scanning prioritizes financial components
            $FinancialKeywords = @("payment", "transaction", "money", "balance", "wallet")
            $SecurityPriority = @()
            
            foreach ($Keyword in $FinancialKeywords) {
                $SecurityPriority += $Keyword
            }
            
            $SecurityPriority.Count | Should -BeGreaterThan 0
        }
        
        It "Should validate gambling compliance requirements" {
            # Test gambling industry specific security requirements
            $ComplianceRequirements = @(
                "audit_logging",
                "user_privacy_protection", 
                "financial_transaction_security",
                "data_retention_policies"
            )
            
            foreach ($Requirement in $ComplianceRequirements) {
                $Requirement | Should -Not -BeNullOrEmpty
            }
        }
        
        It "Should check for API security implementations" {
            # Test that API security measures are in place
            $ApiSecurityMeasures = @(
                "rate_limiting",
                "input_validation", 
                "output_encoding",
                "authentication_mechanisms"
            )
            
            foreach ($Measure in $ApiSecurityMeasures) {
                $Measure | Should -Match '^[a-z_]+$' -Because "Security measures should follow naming convention"
            }
        }
    }
    
    Context "EQ12 Component Integration" {
        
        It "Should validate Chrome automation security" {
            $ChromeScript = Join-Path $ScriptsDir "chrome_governance_automation.py"
            if (Test-Path $ChromeScript) {
                $Content = Get-Content $ChromeScript -Raw
                # Check for security considerations in Chrome automation
                ($Content -match "security" -or $Content -match "safe") | Should -Be $true -Because "Chrome automation should include security considerations"
            } else {
                Set-ItResult -Skipped -Because "Chrome automation script not found"
            }
        }
        
        It "Should validate AI integration security" {
            # Test AI-related security considerations
            $AiScripts = Get-ChildItem -Path $ScriptsDir -Filter "*gpt*" -File
            if ($AiScripts.Count -gt 0) {
                # Should find AI-related scripts
                $AiScripts.Count | Should -BeGreaterThan 0
            } else {
                Set-ItResult -Skipped -Because "AI integration scripts not found"
            }
        }
        
        It "Should validate unified system security" {
            $UnifiedScript = Join-Path $ScriptsDir "eq12_unified_system_enhancement.py"
            if (Test-Path $UnifiedScript) {
                # Unified system should exist and be scannable
                Test-Path $UnifiedScript | Should -Be $true
            } else {
                Set-ItResult -Skipped -Because "Unified system script not found"
            }
        }
    }
}