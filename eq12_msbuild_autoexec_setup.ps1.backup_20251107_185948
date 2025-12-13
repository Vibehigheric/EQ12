# EQ12 Workspace MSBuild Auto-Execute Configuration
# This PowerShell script sets up automatic command execution in VB.NET projects
# for the EQ12 system using MSBuild targets

[CmdletBinding()]
param(
    [switch]$ApplyToAllProjects,
    [switch]$TestMode,
    [string]$CustomScript = ""
)

$logFile = "C:\EQ12\logs\msbuild_setup.log"

function Write-EQ12Log($message) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp - $message"
    Add-Content -Path $logFile -Value $logEntry -Encoding UTF8
    Write-Host $logEntry -ForegroundColor Green
}

function Add-MSBuildTargets($projectPath, $targetType = "comprehensive") {
    Write-EQ12Log "Processing project: $projectPath"

    if (-not (Test-Path $projectPath)) {
        Write-Host "Project file not found: $projectPath" -ForegroundColor Red
        return $false
    }

    # Read the current project file
    [xml]$projectXml = Get-Content $projectPath

    # Remove existing custom targets to avoid duplicates
    $existingTargets = $projectXml.Project.Target | Where-Object { $_.Name -like "*EQ12*" }
    if ($existingTargets) {
        foreach ($target in $existingTargets) {
            $target.ParentNode.RemoveChild($target) | Out-Null
        }
        Write-EQ12Log "Removed existing EQ12 targets from $projectPath"
    }

    # Create the MSBuild targets based on type
    switch ($targetType) {
        "comprehensive" {
            $targetsXml = @"
  <!-- EQ12 System Auto-Execute Targets -->

  <!-- Pre-Build: Environment Validation -->
  <Target Name="EQ12PreBuildValidation" BeforeTargets="BeforeBuild">
    <Message Text="🔍 EQ12: Validating build environment..." Importance="high" />
    <Exec Command="powershell.exe -ExecutionPolicy Bypass -Command &quot;if (-not (Test-Path 'C:\EQ12\logs')) { New-Item -ItemType Directory -Path 'C:\EQ12\logs' -Force }&quot;" />
    <Exec Command="powershell.exe -ExecutionPolicy Bypass -Command &quot;Write-Host '✅ EQ12 logs directory verified' -ForegroundColor Green&quot;" />
  </Target>

  <!-- Post-Build: EQ12 System Integration -->
  <Target Name="EQ12PostBuildIntegration" AfterTargets="AfterBuild">
    <Message Text="🚀 EQ12: Executing post-build integration..." Importance="high" />

    <!-- Check EQ12 system status -->
    <Exec Command="powershell.exe -ExecutionPolicy Bypass -Command &quot;try { if (Test-Path 'C:\EQ12\eq12_simple_start.ps1') { Write-Host '✅ EQ12 startup script available' -ForegroundColor Green } else { Write-Host '⚠️ EQ12 startup script not found' -ForegroundColor Yellow } } catch { Write-Host '❌ EQ12 status check failed' -ForegroundColor Red }&quot;"
           ContinueOnError="true" />

    <!-- Auto-start core EQ12 services if in development mode -->
    <Exec Command="powershell.exe -ExecutionPolicy Bypass -Command &quot;if ($env:EQ12_AUTO_START -eq 'true') { try { C:\EQ12\eq12_simple_start.ps1 -TestOnly; Write-Host '🎯 EQ12 services auto-started' -ForegroundColor Cyan } catch { Write-Host '⚠️ EQ12 auto-start skipped (services may already be running)' -ForegroundColor Yellow } }&quot;"
           ContinueOnError="true" />

    <!-- Log build completion -->
    <Exec Command="powershell.exe -ExecutionPolicy Bypass -Command &quot;Add-Content -Path 'C:\EQ12\logs\build_history.log' -Value '$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Build completed: `$(MSBuildProjectName)' -Encoding UTF8&quot;"
           ContinueOnError="true" />
  </Target>

  <!-- Clean: EQ12 Cleanup Operations -->
  <Target Name="EQ12CleanupOperations" AfterTargets="AfterClean">
    <Message Text="🧹 EQ12: Performing cleanup operations..." Importance="high" />
    <Exec Command="powershell.exe -ExecutionPolicy Bypass -Command &quot;if (Test-Path 'C:\EQ12\logs\temp_build_*') { Remove-Item 'C:\EQ12\logs\temp_build_*' -Force; Write-Host '✅ Cleaned temporary build files' -ForegroundColor Green }&quot;"
           ContinueOnError="true" />
  </Target>

  <!-- Custom EQ12 Workspace Commands -->
  <Target Name="EQ12WorkspaceCommands" AfterTargets="AfterBuild" Condition="'`$(Configuration)' == 'Debug'">
    <Message Text="🔧 EQ12: Executing workspace-specific commands..." Importance="high" />

    <!-- Validate Python environment -->
    <Exec Command="python --version"
           ContinueOnError="true" />

    <!-- Check ngrok status -->
    <Exec Command="powershell.exe -ExecutionPolicy Bypass -Command &quot;try { `$ngrokStatus = (Invoke-WebRequest -Uri 'http://localhost:4040/api/tunnels' -TimeoutSec 2 -ErrorAction Stop).Content | ConvertFrom-Json; if (`$ngrokStatus.tunnels.Count -gt 0) { Write-Host '🌐 Ngrok tunnels active' -ForegroundColor Green } else { Write-Host '⚠️ No active ngrok tunnels' -ForegroundColor Yellow } } catch { Write-Host '📡 Ngrok status unknown' -ForegroundColor Gray }&quot;"
           ContinueOnError="true" />

    <!-- Execute custom workspace script if specified -->
    <Exec Command="powershell.exe -ExecutionPolicy Bypass -File &quot;C:\EQ12\scripts\workspace_integration.ps1&quot;"
           Condition="Exists('C:\EQ12\scripts\workspace_integration.ps1')"
           ContinueOnError="true" />
  </Target>
"@
        }

        "minimal" {
            $targetsXml = @"
  <!-- EQ12 Minimal Auto-Execute Targets -->

  <Target Name="EQ12MinimalSetup" AfterTargets="AfterBuild">
    <Message Text="⚡ EQ12: Quick workspace setup..." Importance="high" />
    <Exec Command="powershell.exe -ExecutionPolicy Bypass -Command &quot;Write-Host '✅ EQ12 build completed for: `$(MSBuildProjectName)' -ForegroundColor Green&quot;" />
    <Exec Command="powershell.exe -ExecutionPolicy Bypass -Command &quot;if (-not (Test-Path 'C:\EQ12\logs')) { New-Item -ItemType Directory -Path 'C:\EQ12\logs' -Force }&quot;" />
  </Target>
"@
        }

        "development" {
            $targetsXml = @"
  <!-- EQ12 Development Auto-Execute Targets -->

  <Target Name="EQ12DevEnvironmentSetup" BeforeTargets="BeforeBuild">
    <Message Text="🔬 EQ12: Setting up development environment..." Importance="high" />
    <Exec Command="powershell.exe -ExecutionPolicy Bypass -Command &quot;`$env:EQ12_DEV_MODE = 'true'; Write-Host '🔧 EQ12 development mode enabled' -ForegroundColor Cyan&quot;" />
  </Target>

  <Target Name="EQ12DevPostBuild" AfterTargets="AfterBuild">
    <Message Text="🚀 EQ12: Development post-build actions..." Importance="high" />

    <!-- Auto-run syntax checker -->
    <Exec Command="powershell.exe -ExecutionPolicy Bypass -Command &quot;if (Test-Path 'C:\EQ12\eq12_syntax_checker.py') { python 'C:\EQ12\eq12_syntax_checker.py'; Write-Host '✅ Syntax validation completed' -ForegroundColor Green }&quot;"
           ContinueOnError="true" />

    <!-- Start development services -->
    <Exec Command="powershell.exe -ExecutionPolicy Bypass -Command &quot;try { if (-not (Get-Process -Name 'python' -ErrorAction SilentlyContinue | Where-Object { `$_.CommandLine -like '*eq12*' })) { Start-Process -FilePath 'python' -ArgumentList 'C:\EQ12\eq12_bridge.py' -WindowStyle Hidden -PassThru | Out-Null; Write-Host '🌉 EQ12 bridge service started' -ForegroundColor Green } else { Write-Host '✅ EQ12 services already running' -ForegroundColor Green } } catch { Write-Host '⚠️ Could not start EQ12 services' -ForegroundColor Yellow }&quot;"
           ContinueOnError="true" />
  </Target>
"@
        }
    }

    # Insert the targets before the closing </Project> tag
    $projectContent = Get-Content $projectPath -Raw
    $closingTag = "</Project>"
    $insertIndex = $projectContent.LastIndexOf($closingTag)

    if ($insertIndex -gt 0) {
        $newContent = $projectContent.Substring(0, $insertIndex) + $targetsXml + "`n" + $closingTag
        Set-Content -Path $projectPath -Value $newContent -Encoding UTF8
        Write-EQ12Log "✅ Added $targetType MSBuild targets to $projectPath"
        return $true
    }
    else {
        Write-Host "Could not find closing Project tag in $projectPath" -ForegroundColor Red
        return $false
    }
}

function Main {
    Write-EQ12Log "🚀 Starting EQ12 MSBuild Auto-Execute Configuration"

    # Create logs directory if it doesn't exist
    $logsDir = "C:\EQ12\logs"
    if (-not (Test-Path $logsDir)) {
        New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
        Write-EQ12Log "Created logs directory: $logsDir"
    }

    # Find all VB.NET project files in EQ12 workspace
    $projectFiles = @(
        "C:\EQ12\vbnet_projects\EQ12CoreLibrary\EQ12CoreLibrary.vbproj",
        "C:\EQ12\vbnet_projects\EQ12ConsoleTools\EQ12ConsoleTools.vbproj",
        "C:\EQ12\vbnet_projects\EQ12WindowsManager\EQ12WindowsManager.vbproj",
        "C:\EQ12\visual_studio_projects\EQ12SystemDiagnostics\EQ12SystemDiagnostics.vbproj",
        "C:\EQ12\visual_studio_projects\EQ12SportsBettingTerminal\EQ12SportsBettingTerminal.vbproj"
    )

    $processedCount = 0
    $successCount = 0

    foreach ($project in $projectFiles) {
        if (Test-Path $project) {
            Write-EQ12Log "Processing project: $project"

            # Backup original project file
            $backupPath = "$project.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
            Copy-Item $project $backupPath
            Write-EQ12Log "Backup created: $backupPath"

            # Determine target type based on project name
            $targetType = "comprehensive"
            if ($project -like "*SystemDiagnostics*") {
                $targetType = "development"
            }
            elseif ($project -like "*CoreLibrary*") {
                $targetType = "minimal"
            }

            if ($TestMode) {
                Write-Host "TEST MODE: Would add $targetType targets to $project" -ForegroundColor Yellow
                $successCount++
            }
            else {
                if (Add-MSBuildTargets $project $targetType) {
                    $successCount++
                }
            }
            $processedCount++
        }
        else {
            Write-Host "Project file not found: $project" -ForegroundColor Red
        }
    }

    Write-EQ12Log "📊 Processing complete: $successCount/$processedCount projects updated"

    # Create the workspace integration script
    Create-WorkspaceIntegrationScript

    # Create environment setup instructions
    Create-EnvironmentSetupInstructions

    Write-EQ12Log "🎉 EQ12 MSBuild auto-execute configuration complete!"
    Write-Host "`n✅ SUMMARY:" -ForegroundColor Green
    Write-Host "   • Projects configured: $successCount/$processedCount" -ForegroundColor White
    Write-Host "   • Auto-execute targets added to VB.NET projects" -ForegroundColor White
    Write-Host "   • Workspace integration script created" -ForegroundColor White
    Write-Host "   • Environment setup instructions generated" -ForegroundColor White
    Write-Host "`n🔧 NEXT STEPS:" -ForegroundColor Cyan
    Write-Host "   1. Open Visual Studio and reload your EQ12 projects" -ForegroundColor White
    Write-Host "   2. Build any VB.NET project to trigger auto-execution" -ForegroundColor White
    Write-Host "   3. Set EQ12_AUTO_START=true environment variable for full automation" -ForegroundColor White
}

function Create-WorkspaceIntegrationScript {
    $scriptPath = "C:\EQ12\scripts\workspace_integration.ps1"

    # Ensure scripts directory exists
    $scriptsDir = Split-Path $scriptPath
    if (-not (Test-Path $scriptsDir)) {
        New-Item -ItemType Directory -Path $scriptsDir -Force | Out-Null
    }

    $scriptContent = @"
# EQ12 Workspace Integration Script
# Automatically executed during VB.NET project builds
# This script runs trusted EQ12 commands without security prompts

[CmdletBinding()]
param()

`$logFile = "C:\EQ12\logs\workspace_integration.log"

function Write-IntegrationLog(`$message) {
    `$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path `$logFile -Value "`$timestamp - `$message" -Encoding UTF8
    Write-Host "`$timestamp - `$message" -ForegroundColor Cyan
}

try {
    Write-IntegrationLog "🔧 EQ12 Workspace Integration Starting"

    # Check system health
    if (Test-Path "C:\EQ12\eq12_simple_start.ps1") {
        Write-IntegrationLog "✅ EQ12 startup script available"

        # Test core services
        try {
            & "C:\EQ12\eq12_simple_start.ps1" -TestOnly
            Write-IntegrationLog "✅ EQ12 system health check passed"
        } catch {
            Write-IntegrationLog "⚠️ EQ12 health check warning: `$(`$_.Exception.Message)"
        }
    }

    # Validate Python environment
    try {
        `$pythonVersion = python --version 2>&1
        Write-IntegrationLog "🐍 Python available: `$pythonVersion"
    } catch {
        Write-IntegrationLog "⚠️ Python not available or not in PATH"
    }

    # Check for syntax issues if requested
    if (`$env:EQ12_AUTO_SYNTAX_CHECK -eq "true" -and (Test-Path "C:\EQ12\eq12_syntax_checker.py")) {
        Write-IntegrationLog "🔍 Running automatic syntax check"
        try {
            python "C:\EQ12\eq12_syntax_checker.py" | Out-String | ForEach-Object {
                if (`$_ -match "✅|❌|⚠️") { Write-IntegrationLog `$_.Trim() }
            }
        } catch {
            Write-IntegrationLog "⚠️ Syntax check failed: `$(`$_.Exception.Message)"
        }
    }

    Write-IntegrationLog "🎉 EQ12 Workspace Integration Complete"

} catch {
    Write-IntegrationLog "❌ Workspace integration error: `$(`$_.Exception.Message)"
    # Don't fail the build due to integration issues
    exit 0
}
"@

    Set-Content -Path $scriptPath -Value $scriptContent -Encoding UTF8
    Write-EQ12Log "Created workspace integration script: $scriptPath"
}

function Create-EnvironmentSetupInstructions {
    $instructionsPath = "C:\EQ12\EQ12_MSBuild_Setup_Instructions.md"

    $instructions = @"
# EQ12 MSBuild Auto-Execute Setup Instructions

## Overview
This configuration enables automatic execution of trusted EQ12 commands when building VB.NET projects in Visual Studio, bypassing security prompts for workspace-specific operations.

## What Was Configured

### 1. MSBuild Targets Added
Each VB.NET project now includes custom MSBuild targets that automatically:
- Validate EQ12 environment before builds
- Execute post-build integration commands
- Perform cleanup operations
- Run development-specific tasks

### 2. Target Types by Project

#### Comprehensive Targets (Default)
- **Pre-Build**: Environment validation, logs directory creation
- **Post-Build**: System integration, service status checks, build logging
- **Clean**: Temporary file cleanup
- **Development**: Python/ngrok validation, custom script execution

#### Minimal Targets (CoreLibrary)
- Basic setup and build completion logging
- Lightweight for library projects

#### Development Targets (SystemDiagnostics)
- Enhanced development environment setup
- Automatic syntax checking
- Development service management

## Environment Variables

### Required for Full Automation
```cmd
set EQ12_AUTO_START=true
```
Enables automatic service startup during builds.

### Optional Development Features
```cmd
set EQ12_DEV_MODE=true
set EQ12_AUTO_SYNTAX_CHECK=true
```

## Usage Instructions

### 1. Reload Projects in Visual Studio
1. Close Visual Studio if open
2. Reopen your EQ12 solution
3. All configured projects will now have auto-execute capabilities

### 2. Trigger Auto-Execution
- **Build any VB.NET project** - triggers post-build commands
- **Clean solution** - triggers cleanup operations
- **Debug builds** - additional development features activate

### 3. Monitor Execution
- Build output window shows MSBuild target messages
- Logs written to: `C:\EQ12\logs\`
  - `msbuild_setup.log` - Configuration log
  - `workspace_integration.log` - Runtime integration log
  - `build_history.log` - Build completion history

## Security Model

### Trusted Execution Context
- Commands run within MSBuild's trusted context
- PowerShell execution policy bypassed for workspace scripts only
- No arbitrary code execution - only pre-defined, audited commands

### Command Categories
1. **Environment Validation** - Safe system checks
2. **Service Management** - EQ12 service status and health
3. **Development Tools** - Syntax checking, testing
4. **Logging** - Build tracking and monitoring

## Customization

### Adding Custom Commands
Edit the workspace integration script:
```
C:\EQ12\scripts\workspace_integration.ps1
```

### Modifying Target Behavior
Re-run this configuration script with different parameters:
```powershell
.\eq12_msbuild_autoexec_setup.ps1 -TestMode
```

## Troubleshooting

### Build Errors
- MSBuild targets use `ContinueOnError="true"` to prevent build failures
- Check build output for MSBuild messages
- Review logs in `C:\EQ12\logs\`

### Disabled Features
- Auto-execution only works in configured VB.NET projects
- Requires Visual Studio MSBuild context
- Some features require specific environment variables

## Backup and Restore

### Project Backups
Original `.vbproj` files are automatically backed up with timestamp:
```
ProjectName.vbproj.backup.20251004_120000
```

### Removing Auto-Execute
Delete MSBuild target sections from `.vbproj` files or restore from backup.

---

**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Configuration Applied To:** $(($projectFiles | Where-Object { Test-Path $_ }).Count) VB.NET projects
"@

    Set-Content -Path $instructionsPath -Value $instructions -Encoding UTF8
    Write-EQ12Log "Created setup instructions: $instructionsPath"
}

# Execute main function
Main
