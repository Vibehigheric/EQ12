[CmdletBinding()]
param(
    [switch]$TestAll,
    [switch]$ShowLogs,
    [switch]$ValidateTargets
)

Write-Host "🎯 EQ12 MSBuild Auto-Execute Demonstration" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Green

function Test-VBNetProject($projectPath, $projectName) {
    Write-Host "`n🔧 Testing: $projectName" -ForegroundColor Cyan

    if (-not (Test-Path $projectPath)) {
        Write-Host "   ❌ Project not found: $projectPath" -ForegroundColor Red
        return $false
    }

    Write-Host "   📁 Project found: $projectPath" -ForegroundColor White

    # Check if MSBuild targets are present
    $projectContent = Get-Content $projectPath -Raw
    if ($projectContent -match "EQ12.*Target") {
        Write-Host "   ✅ MSBuild auto-execute targets detected" -ForegroundColor Green

        # Count targets
        $targetCount = ([regex]::Matches($projectContent, '<Target Name="EQ12[^"]*"')).Count
        Write-Host "   📊 Auto-execute targets found: $targetCount" -ForegroundColor White

        return $true
    } else {
        Write-Host "   ❌ MSBuild targets not found" -ForegroundColor Red
        return $false
    }
}

function Show-AutoExecuteFeatures {
    Write-Host "`n🚀 AUTO-EXECUTE FEATURES ENABLED:" -ForegroundColor Green
    Write-Host "   🔍 Pre-Build Environment Validation" -ForegroundColor White
    Write-Host "     • Creates C:\EQ12\logs directory if missing" -ForegroundColor Gray
    Write-Host "     • Validates build environment setup" -ForegroundColor Gray

    Write-Host "   🎯 Post-Build EQ12 Integration" -ForegroundColor White
    Write-Host "     • Checks EQ12 startup script availability" -ForegroundColor Gray
    Write-Host "     • Auto-starts services if EQ12_AUTO_START=true" -ForegroundColor Gray
    Write-Host "     • Logs build completion to build_history.log" -ForegroundColor Gray

    Write-Host "   🧹 Cleanup Operations" -ForegroundColor White
    Write-Host "     • Removes temporary build files on clean" -ForegroundColor Gray

    Write-Host "   🔧 Development Mode (Debug builds only)" -ForegroundColor White
    Write-Host "     • Python environment validation" -ForegroundColor Gray
    Write-Host "     • Ngrok tunnel status checking" -ForegroundColor Gray
    Write-Host "     • Custom workspace script execution" -ForegroundColor Gray
}

function Show-EnvironmentVariables {
    Write-Host "`n🌐 ENVIRONMENT VARIABLES:" -ForegroundColor Cyan

    $vars = @(
        @{Name="EQ12_AUTO_START"; Value=$env:EQ12_AUTO_START; Description="Auto-start EQ12 services on build"},
        @{Name="EQ12_DEV_MODE"; Value=$env:EQ12_DEV_MODE; Description="Enable development features"},
        @{Name="EQ12_AUTO_SYNTAX_CHECK"; Value=$env:EQ12_AUTO_SYNTAX_CHECK; Description="Run syntax checks automatically"}
    )

    foreach ($var in $vars) {
        $status = if ($var.Value -eq "true") { "✅ ENABLED" } else { "⚪ DISABLED" }
        Write-Host "   $($var.Name): $status" -ForegroundColor White
        Write-Host "     Description: $($var.Description)" -ForegroundColor Gray
    }
}

function Test-BuildProcess($projectPath) {
    Write-Host "`n🔨 TESTING BUILD PROCESS:" -ForegroundColor Yellow
    $projectDir = Split-Path $projectPath
    $projectName = Split-Path $projectPath -Leaf

    try {
        Write-Host "   Building: $projectName" -ForegroundColor White
        Push-Location $projectDir

        $buildOutput = dotnet build 2>&1
        $buildSuccess = $LASTEXITCODE -eq 0

        if ($buildSuccess) {
            Write-Host "   ✅ Build succeeded" -ForegroundColor Green

            # Check for auto-execute messages in output
            if ($buildOutput -match "EQ12:") {
                Write-Host "   🎯 Auto-execute targets ran successfully" -ForegroundColor Cyan
                $eq12Messages = $buildOutput | Select-String "EQ12:"
                foreach ($msg in $eq12Messages) {
                    Write-Host "     $($msg.ToString().Trim())" -ForegroundColor Gray
                }
            } else {
                Write-Host "   ⚠️ No EQ12 auto-execute output detected" -ForegroundColor Yellow
            }
        } else {
            Write-Host "   ❌ Build failed" -ForegroundColor Red
            Write-Host "     $($buildOutput[-5..-1] -join "`n")" -ForegroundColor Red
        }

        Pop-Location
        return $buildSuccess
    } catch {
        Write-Host "   ❌ Build test error: $($_.Exception.Message)" -ForegroundColor Red
        Pop-Location
        return $false
    }
}

function Show-LogFiles {
    Write-Host "`n📋 LOG FILES GENERATED:" -ForegroundColor Cyan
    $logDir = "C:\EQ12\logs"

    if (Test-Path $logDir) {
        $logFiles = @(
            @{Name="msbuild_setup.log"; Description="MSBuild configuration log"},
            @{Name="workspace_integration.log"; Description="Auto-execute runtime log"},
            @{Name="build_history.log"; Description="Build completion tracking"}
        )

        foreach ($log in $logFiles) {
            $logPath = Join-Path $logDir $log.Name
            if (Test-Path $logPath) {
                $size = (Get-Item $logPath).Length
                $modified = (Get-Item $logPath).LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                Write-Host "   ✅ $($log.Name) (${size} bytes, modified: $modified)" -ForegroundColor Green
                Write-Host "     $($log.Description)" -ForegroundColor Gray

                if ($ShowLogs) {
                    Write-Host "     Last 3 entries:" -ForegroundColor White
                    $lastEntries = Get-Content $logPath | Select-Object -Last 3
                    foreach ($entry in $lastEntries) {
                        Write-Host "       $entry" -ForegroundColor Gray
                    }
                }
            } else {
                Write-Host "   ⚪ $($log.Name) - Not created yet" -ForegroundColor Gray
                Write-Host "     $($log.Description)" -ForegroundColor Gray
            }
        }
    } else {
        Write-Host "   ❌ Logs directory not found: $logDir" -ForegroundColor Red
    }
}

function Main {
    # Show current configuration
    Show-AutoExecuteFeatures
    Show-EnvironmentVariables

    # Test configured projects
    Write-Host "`n🔍 TESTING CONFIGURED VB.NET PROJECTS:" -ForegroundColor Cyan

    $projects = @(
        @{Path="C:\EQ12\vbnet_projects\EQ12CoreLibrary\EQ12CoreLibrary.vbproj"; Name="EQ12CoreLibrary (Minimal)"},
        @{Path="C:\EQ12\vbnet_projects\EQ12ConsoleTools\EQ12ConsoleTools.vbproj"; Name="EQ12ConsoleTools (Comprehensive)"},
        @{Path="C:\EQ12\vbnet_projects\EQ12WindowsManager\EQ12WindowsManager.vbproj"; Name="EQ12WindowsManager (Comprehensive)"},
        @{Path="C:\EQ12\visual_studio_projects\EQ12SystemDiagnostics\EQ12SystemDiagnostics.vbproj"; Name="EQ12SystemDiagnostics (Development)"},
        @{Path="C:\EQ12\visual_studio_projects\EQ12SportsBettingTerminal\EQ12SportsBettingTerminal.vbproj"; Name="EQ12SportsBettingTerminal (Comprehensive)"}
    )

    $configuredCount = 0
    foreach ($project in $projects) {
        if (Test-VBNetProject $project.Path $project.Name) {
            $configuredCount++
        }
    }

    Write-Host "`n📊 CONFIGURATION SUMMARY:" -ForegroundColor Green
    Write-Host "   Configured projects: $configuredCount/$($projects.Count)" -ForegroundColor White

    # Test build process if requested
    if ($TestAll) {
        Write-Host "`n🧪 TESTING BUILD AUTOMATION:" -ForegroundColor Yellow
        $testProject = "C:\EQ12\vbnet_projects\EQ12CoreLibrary\EQ12CoreLibrary.vbproj"
        Test-BuildProcess $testProject
    }

    # Show log files
    Show-LogFiles

    # Usage instructions
    Write-Host "`n📖 USAGE INSTRUCTIONS:" -ForegroundColor Cyan
    Write-Host "   1. Open Visual Studio" -ForegroundColor White
    Write-Host "   2. Load any EQ12 VB.NET project" -ForegroundColor White
    Write-Host "   3. Build the project (Ctrl+Shift+B)" -ForegroundColor White
    Write-Host "   4. Watch build output for auto-execute messages" -ForegroundColor White
    Write-Host "   5. Check C:\EQ12\logs for execution logs" -ForegroundColor White

    Write-Host "`n🎉 EQ12 MSBuild Auto-Execute System Active!" -ForegroundColor Green
    Write-Host "   No security prompts • Trusted workspace execution • Full automation" -ForegroundColor White
}

# Execute demonstration
Main
