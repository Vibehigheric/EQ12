# EQ12 Extension Installer Tests
# Comprehensive Pester tests for the EQ12 Enhanced Extension Installer

Describe "EQ12 Enhanced Extension Installer Tests" {
    BeforeAll {
        # Set up test environment
        $script:RepoRoot = (Get-Item $PSScriptRoot).Parent.FullName
        $script:InstallerScript = Join-Path $RepoRoot "scripts\eq12_extension_installer.ps1"
        $script:ExtensionPath = "C:\EQ12\firefox_extensions\eq12_betting_dashboard"
        $script:TestLogDir = "C:\EQ12\logs\test_logs"

        # Ensure test directories exist
        if (!(Test-Path $TestLogDir)) {
            New-Item -ItemType Directory -Path $TestLogDir -Force | Out-Null
        }

        Write-Host "Test Environment Setup Complete" -ForegroundColor Green
        Write-Host "Repo Root: $RepoRoot" -ForegroundColor Cyan
        Write-Host "Installer: $InstallerScript" -ForegroundColor Cyan
        Write-Host "Extension Path: $ExtensionPath" -ForegroundColor Cyan
    }

    Context "Installer Script Validation" {
        It "Should have installer script present" {
            Test-Path $InstallerScript | Should -Be $true
        }

        It "Should have valid PowerShell syntax" {
            $syntaxErrors = $null
            [System.Management.Automation.PSParser]::Tokenize((Get-Content $InstallerScript -Raw), [ref]$syntaxErrors)
            $syntaxErrors.Count | Should -Be 0
        }

        It "Should contain required functions" {
            $content = Get-Content $InstallerScript -Raw

            $requiredFunctions = @(
                'Test-Prerequisites',
                'Install-Dependencies',
                'Test-ExtensionStructure',
                'Install-ExtensionInFirefox',
                'New-ExtensionPackage',
                'Test-ExtensionFunctionality'
            )

            foreach ($function in $requiredFunctions) {
                $content | Should -Match "function $function"
            }
        }

        It "Should have proper parameter validation" {
            $content = Get-Content $InstallerScript -Raw
            $content | Should -Match '\[CmdletBinding\(\)\]'
            $content | Should -Match '\[ValidateSet\('
        }
    }

    Context "Extension Directory Structure" {
        It "Should have extension directory" {
            Test-Path $ExtensionPath | Should -Be $true
        }

        It "Should contain all required core files" {
            $requiredFiles = @(
                'manifest.json',
                'background_v3_enhanced.js',
                'sportsbook_scraper_v3_enhanced.js',
                'popup_v3_enhanced.html',
                'popup_v3_enhanced.js',
                'options.html',
                'options.js'
            )

            foreach ($file in $requiredFiles) {
                $filePath = Join-Path $ExtensionPath $file
                Test-Path $filePath | Should -Be $true -Because "$file is required for extension functionality"
            }
        }

        It "Should contain all enhanced feature modules" {
            $enhancedModules = @(
                'privacy_manager.js',
                'developer_tools.js',
                'ui_enhancer.js',
                'proxy_manager.js',
                'tab_manager.js'
            )

            foreach ($module in $enhancedModules) {
                $modulePath = Join-Path $ExtensionPath $module
                Test-Path $modulePath | Should -Be $true -Because "$module provides enhanced functionality"
            }
        }

        It "Should have testing dashboard" {
            $dashboardPath = Join-Path $ExtensionPath "testing_dashboard.html"
            Test-Path $dashboardPath | Should -Be $true
        }
    }

    Context "Manifest Validation" {
        BeforeAll {
            $manifestPath = Join-Path $ExtensionPath "manifest.json"
            if (Test-Path $manifestPath) {
                $script:Manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
            }
        }

        It "Should have valid manifest.json" {
            $Manifest | Should -Not -BeNullOrEmpty
        }

        It "Should be Manifest V3" {
            $Manifest.manifest_version | Should -Be 3
        }

        It "Should have required manifest fields" {
            $Manifest.name | Should -Not -BeNullOrEmpty
            $Manifest.version | Should -Not -BeNullOrEmpty
            $Manifest.description | Should -Not -BeNullOrEmpty
        }

        It "Should have enhanced permissions" {
            $requiredPermissions = @(
                'declarativeNetRequest',
                'proxy',
                'cookies',
                'browsingData',
                'webRequest',
                'privacy',
                'contextMenus'
            )

            foreach ($permission in $requiredPermissions) {
                $Manifest.permissions | Should -Contain $permission -Because "$permission is required for enhanced features"
            }
        }

        It "Should have web accessible resources configured" {
            $Manifest.web_accessible_resources | Should -Not -BeNullOrEmpty

            # Check that enhanced modules are included
            $webResources = $Manifest.web_accessible_resources[0].resources
            $webResources | Should -Contain "privacy_manager.js"
            $webResources | Should -Contain "developer_tools.js"
            $webResources | Should -Contain "ui_enhancer.js"
            $webResources | Should -Contain "proxy_manager.js"
        }
    }

    Context "Enhanced Module Content Validation" {
        It "Privacy Manager should have security features" {
            $privacyPath = Join-Path $ExtensionPath "privacy_manager.js"
            $content = Get-Content $privacyPath -Raw

            # Check for key security functions
            $content | Should -Match "setupRequestBlocking" -Because "Request blocking is core privacy feature"
            $content | Should -Match "setupFingerprintingProtection" -Because "Fingerprinting protection is essential"
            $content | Should -Match "setupWebRTCProtection" -Because "WebRTC leak protection is critical"
            $content | Should -Match "trackerDatabase" -Because "Tracker database enables blocking"
        }

        It "Developer Tools should have debugging features" {
            $devToolsPath = Join-Path $ExtensionPath "developer_tools.js"
            $content = Get-Content $devToolsPath -Raw

            $content | Should -Match "setupDebugConsole" -Because "Debug console is essential for development"
            $content | Should -Match "setupPerformanceMonitoring" -Because "Performance monitoring helps optimization"
            $content | Should -Match "setupNetworkMonitoring" -Because "Network monitoring reveals API calls"
            $content | Should -Match "setupMeasurementTools" -Because "Measurement tools help UI development"
        }

        It "UI Enhancer should have interface features" {
            $uiPath = Join-Path $ExtensionPath "ui_enhancer.js"
            $content = Get-Content $uiPath -Raw

            $content | Should -Match "setupDarkMode" -Because "Dark mode improves user experience"
            $content | Should -Match "setupAutoReload" -Because "Auto-reload keeps odds current"
            $content | Should -Match "setupCustomStyles" -Because "Custom styles enable personalization"
            $content | Should -Match "setupAccessibility" -Because "Accessibility ensures inclusive design"
        }

        It "Proxy Manager should have VPN features" {
            $proxyPath = Join-Path $ExtensionPath "proxy_manager.js"
            $content = Get-Content $proxyPath -Raw

            $content | Should -Match "loadProxyConfiguration" -Because "Proxy configuration is core functionality"
            $content | Should -Match "setupVPNProviders" -Because "VPN integration enhances security"
            $content | Should -Match "checkDNSLeak" -Because "DNS leak detection prevents exposure"
            $content | Should -Match "monitorVPNHealth" -Because "Health monitoring ensures reliability"
        }
    }

    Context "Installer Functionality Tests" {
        It "Should run help command successfully" {
            $result = & $InstallerScript help
            $LASTEXITCODE | Should -Be 0
        }

        It "Should validate test command" {
            # Test the test functionality
            $result = & $InstallerScript test 2>&1
            # Should either pass or provide meaningful error
            $result | Should -Not -BeNullOrEmpty
        }

        It "Should handle invalid action gracefully" {
            $result = & $InstallerScript invalid_action 2>&1
            $LASTEXITCODE | Should -Be 1
            $result | Should -Match "Unknown action"
        }
    }

    Context "Dependency Checks" {
        It "Should detect Firefox installation" {
            $firefoxPaths = @(
                "${env:ProgramFiles}\Mozilla Firefox\firefox.exe",
                "${env:ProgramFiles(x86)}\Mozilla Firefox\firefox.exe"
            )

            $firefoxFound = $firefoxPaths | Where-Object { Test-Path $_ }
            $firefoxFound | Should -Not -BeNullOrEmpty -Because "Firefox is required for extension testing"
        }

        It "Should have Python available for enhanced features" {
            try {
                $pythonVersion = python --version 2>&1
                $pythonVersion | Should -Match "Python"
            } catch {
                Write-Warning "Python not found - enhanced features may be limited"
            }
        }
    }

    Context "Log Directory Structure" {
        It "Should have logs directory" {
            $logsDir = "C:\EQ12\logs"
            Test-Path $logsDir | Should -Be $true
        }

        It "Should be able to create log files" {
            $testLogFile = Join-Path $TestLogDir "pester_test_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
            "Test log entry" | Out-File -FilePath $testLogFile -Encoding utf8
            Test-Path $testLogFile | Should -Be $true

            # Cleanup
            Remove-Item $testLogFile -ErrorAction SilentlyContinue
        }
    }

    Context "Extension Package Creation" {
        It "Should be able to create extension package" -Skip:(!$env:FULL_TESTS) {
            # Only run in full test mode to avoid creating unnecessary packages
            $result = & $InstallerScript package 2>&1
            $LASTEXITCODE | Should -Be 0
            $result | Should -Match "package created"
        }
    }

    Context "Security Validation" {
        It "Should not contain hardcoded secrets" {
            $allFiles = Get-ChildItem $ExtensionPath -Recurse -Include "*.js", "*.json", "*.html"

            foreach ($file in $allFiles) {
                $content = Get-Content $file.FullName -Raw

                # Check for common secret patterns
                $content | Should -Not -Match "password\s*=\s*['\"][^'\"]+['\"]" -Because "$($file.Name) should not contain hardcoded passwords"
                $content | Should -Not -Match "api_?key\s*=\s*['\"][^'\"]+['\"]" -Because "$($file.Name) should not contain hardcoded API keys"
                $content | Should -Not -Match "secret\s*=\s*['\"][^'\"]+['\"]" -Because "$($file.Name) should not contain hardcoded secrets"
            }
        }

        It "Should use environment variables for secrets" {
            $jsFiles = Get-ChildItem $ExtensionPath -Recurse -Include "*.js"

            # Look for proper environment variable usage
            $envVarUsage = $false
            foreach ($file in $jsFiles) {
                $content = Get-Content $file.FullName -Raw
                if ($content -match "process\.env\.|getenv\(|ENV\[") {
                    $envVarUsage = $true
                    break
                }
            }

            # This is informational - not all extensions need env vars
            Write-Host "Environment variable usage detected: $envVarUsage" -ForegroundColor Cyan
        }
    }

    Context "Performance Validation" {
        It "Should have reasonable file sizes" {
            $jsFiles = Get-ChildItem $ExtensionPath -Include "*.js" -Recurse

            foreach ($file in $jsFiles) {
                $sizeKB = [math]::Round($file.Length / 1024, 2)

                # Warn if files are very large (over 500KB)
                if ($sizeKB -gt 500) {
                    Write-Warning "$($file.Name) is large: ${sizeKB}KB - consider optimization"
                }

                # Fail if files are extremely large (over 2MB)
                $sizeKB | Should -BeLessThan 2048 -Because "$($file.Name) should not exceed 2MB for browser performance"
            }
        }

        It "Should have efficient manifest structure" {
            $manifestSize = (Get-Item (Join-Path $ExtensionPath "manifest.json")).Length
            $manifestSize | Should -BeLessThan 10240 -Because "Manifest should be under 10KB for fast loading"
        }
    }

    AfterAll {
        Write-Host "EQ12 Extension Installer Tests Completed" -ForegroundColor Green
        Write-Host "Test logs available in: $TestLogDir" -ForegroundColor Cyan

        # Generate test summary
        $summaryFile = Join-Path $TestLogDir "pester_summary_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
        $testSummary = @{
            timestamp        = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
            test_suite       = "EQ12 Enhanced Extension Installer"
            repo_root        = $RepoRoot
            extension_path   = $ExtensionPath
            installer_script = $InstallerScript
            test_environment = @{
                powershell_version = $PSVersionTable.PSVersion.ToString()
                os_version         = [System.Environment]::OSVersion.ToString()
                machine_name       = $env:COMPUTERNAME
            }
        }

        $testSummary | ConvertTo-Json -Depth 3 | Out-File -FilePath $summaryFile -Encoding utf8
        Write-Host "Test summary saved: $summaryFile" -ForegroundColor Cyan
    }
}
