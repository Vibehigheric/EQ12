#Requires -RunAsAdministrator

<#
.SYNOPSIS
EQ12 Complete VS Code Cleanup and Optimization System

.DESCRIPTION
Comprehensive cleanup script that eliminates all VS Code performance issues:
- Removes deprecated extensions and their corrupt caches
- Cleans Edge browser extension contamination from workspace
- Fixes Tailwind CSS path resolution errors
- Resets Pylance, Copilot, and Tabnine to pristine state
- Eliminates Node heap memory crashes
- Optimizes extension loading and workspace indexing

.PARAMETER Action
- DeepClean: Remove all deprecated extensions and corrupt caches
- ResetExtensions: Reset all AI extensions (Copilot, Pylance, Tabnine)
- CleanWorkspace: Remove browser extension contamination
- OptimizeSettings: Configure optimal VS Code settings
- Complete: Execute all cleanup operations

.EXAMPLE
.\eq12_vscode_complete_cleanup.ps1 -Action Complete
Performs comprehensive cleanup and optimization
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("DeepClean", "ResetExtensions", "CleanWorkspace", "OptimizeSettings", "Complete")]
    [string]$Action = "Complete",

    [Parameter(Mandatory = $false)]
    [string]$Workspace = "C:\EQ12",

    [Parameter(Mandatory = $false)]
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

function Write-CleanupLog {
    param([string]$Message, [string]$Level = "Info")

    $colors = @{
        Info = "White"
        Warning = "Yellow"
        Error = "Red"
        Success = "Green"
        Critical = "Magenta"
    }

    Write-Host "[$Level] $Message" -ForegroundColor $colors[$Level]
}

function Stop-AllVSCodeProcesses {
    Write-CleanupLog "Stopping all VS Code processes..." "Info"

    $processes = Get-Process -Name "Code", "code-insiders", "node" -ErrorAction SilentlyContinue
    foreach ($proc in $processes) {
        try {
            $proc.Kill()
            Write-CleanupLog "Stopped process: $($proc.ProcessName) (PID: $($proc.Id))" "Success"
        }
        catch {
            Write-CleanupLog "Failed to stop process: $($proc.ProcessName)" "Warning"
        }
    }

    Start-Sleep -Seconds 3
}

function Remove-DeprecatedExtensions {
    Write-CleanupLog "=== REMOVING DEPRECATED EXTENSIONS ===" "Critical"

    $extensionsPath = "$env:USERPROFILE\.vscode\extensions"

    if (Test-Path $extensionsPath) {
        # Common deprecated extensions patterns
        $deprecatedPatterns = @(
            "ms-python.python-2021*",
            "ms-toolsai.jupyter-2021*",
            "*-deprecated-*",
            "*-old-*"
        )

        foreach ($pattern in $deprecatedPatterns) {
            $deprecated = Get-ChildItem $extensionsPath -Filter $pattern -Directory -ErrorAction SilentlyContinue
            foreach ($ext in $deprecated) {
                Write-CleanupLog "Removing deprecated: $($ext.Name)" "Warning"
                Remove-Item $ext.FullName -Recurse -Force -ErrorAction SilentlyContinue
            }
        }
    }

    Write-CleanupLog "Deprecated extensions removed" "Success"
}

function Clear-ExtensionCaches {
    Write-CleanupLog "=== CLEARING EXTENSION CACHES ===" "Critical"

    $cachePaths = @(
        "$env:APPDATA\Code\Cache",
        "$env:APPDATA\Code\CachedData",
        "$env:APPDATA\Code\CachedExtensionVSIXs",
        "$env:APPDATA\Code\User\workspaceStorage",
        "$env:APPDATA\Code\logs",
        "$env:USERPROFILE\.tabnine",
        "$env:USERPROFILE\AppData\Roaming\TabNine",
        "$env:LOCALAPPDATA\Microsoft\TypeScript"
    )

    foreach ($cachePath in $cachePaths) {
        if (Test-Path $cachePath) {
            Write-CleanupLog "Clearing cache: $cachePath" "Info"
            Remove-Item $cachePath -Recurse -Force -ErrorAction SilentlyContinue
        }
    }

    Write-CleanupLog "Extension caches cleared" "Success"
}

function Remove-BrowserExtensionContamination {
    Write-CleanupLog "=== CLEANING BROWSER EXTENSION CONTAMINATION ===" "Critical"

    $contaminatedPaths = @(
        "$Workspace\profiles",
        "$Workspace\Extensions"
    )

    foreach ($contamPath in $contaminatedPaths) {
        if (Test-Path $contamPath) {
            Write-CleanupLog "Removing contamination: $contamPath" "Warning"
            Remove-Item $contamPath -Recurse -Force -ErrorAction SilentlyContinue
        }
    }

    # Find and remove any .crx or .asar files
    $junkFiles = Get-ChildItem $Workspace -Recurse -Include "*.crx", "*.asar", "*.pak" -ErrorAction SilentlyContinue
    foreach ($junk in $junkFiles) {
        Write-CleanupLog "Removing junk file: $($junk.Name)" "Info"
        Remove-Item $junk.FullName -Force -ErrorAction SilentlyContinue
    }

    Write-CleanupLog "Browser extension contamination removed" "Success"
}

function Reset-AIExtensions {
    Write-CleanupLog "=== RESETTING AI EXTENSIONS ===" "Critical"

    # Reset Copilot
    $copilotPaths = @(
        "$env:USERPROFILE\.github-copilot",
        "$env:APPDATA\Code\User\globalStorage\github.copilot"
    )

    foreach ($copilotPath in $copilotPaths) {
        if (Test-Path $copilotPath) {
            Write-CleanupLog "Resetting Copilot: $copilotPath" "Info"
            Remove-Item $copilotPath -Recurse -Force -ErrorAction SilentlyContinue
        }
    }

    # Reset Pylance
    $pylancePaths = @(
        "$env:APPDATA\Code\User\globalStorage\ms-python.vscode-pylance",
        "$env:LOCALAPPDATA\Microsoft\pylance"
    )

    foreach ($pylancePath in $pylancePaths) {
        if (Test-Path $pylancePath) {
            Write-CleanupLog "Resetting Pylance: $pylancePath" "Info"
            Remove-Item $pylancePath -Recurse -Force -ErrorAction SilentlyContinue
        }
    }

    # Reset Tabnine completely
    $tabninePaths = @(
        "$env:USERPROFILE\.tabnine",
        "$env:APPDATA\TabNine",
        "$env:USERPROFILE\AppData\Roaming\TabNine"
    )

    foreach ($tabninePath in $tabninePaths) {
        if (Test-Path $tabninePath) {
            Write-CleanupLog "Resetting Tabnine: $tabninePath" "Info"
            Remove-Item $tabninePath -Recurse -Force -ErrorAction SilentlyContinue
        }
    }

    Write-CleanupLog "AI extensions reset successfully" "Success"
}

function Set-OptimalVSCodeSettings {
    Write-CleanupLog "=== CONFIGURING OPTIMAL VS CODE SETTINGS ===" "Critical"

    $vscodeDir = "$Workspace\.vscode"
    if (-not (Test-Path $vscodeDir)) {
        New-Item -ItemType Directory -Path $vscodeDir -Force | Out-Null
    }

    # Optimal settings for EQ12
    $optimalSettings = @{
        # Extension Management
        "extensions.autoCheckUpdates" = $true
        "extensions.autoUpdate" = $true
        "extensions.showDeprecated" = $false
        "extensions.ignoreRecommendations" = $false

        # Python Configuration
        "python.defaultInterpreterPath" = "$Workspace\.venv\Scripts\python.exe"
        "python.venvPath" = $Workspace
        "python.venvFolders" = @(".venv")

        # Pylance Optimization
        "python.analysis.typeCheckingMode" = "basic"
        "python.analysis.autoSearchPaths" = $true
        "python.analysis.indexing" = $true
        "python.analysis.diagnosticMode" = "workspace"

        # CRITICAL: File Exclusions (prevents contamination scanning)
        "files.exclude" = @{
            "**/profiles" = $true
            "**/Extensions" = $true
            "**/*.crx" = $true
            "**/*.asar" = $true
            "**/*.pak" = $true
            "**/envs" = $true
            "**/.venv_new" = $true
            "**/node_modules" = $true
            "**/__pycache__" = $true
            "**/.pytest_cache" = $true
            "**/data" = $true
            "**/.git" = $true
            "**/.mypy_cache" = $true
        }

        # Search Exclusions
        "search.exclude" = @{
            "**/profiles" = $true
            "**/Extensions" = $true
            "**/envs" = $true
            "**/.venv_new" = $true
            "**/node_modules" = $true
            "**/data" = $true
        }

        # File Watcher Exclusions (reduces CPU usage)
        "files.watcherExclude" = @{
            "**/profiles/**" = $true
            "**/Extensions/**" = $true
            "**/envs/**" = $true
            "**/.venv_new/**" = $true
            "**/data/**" = $true
            "**/node_modules/**" = $true
            "**/__pycache__/**" = $true
        }

        # Python Analysis Exclusions
        "python.analysis.exclude" = @(
            "**/profiles/**",
            "**/Extensions/**",
            "**/envs/**",
            "**/.venv_new/**",
            "**/data/**",
            "**/node_modules/**"
        )

        # Tailwind CSS Configuration (fixes path resolution)
        "tailwindCSS.includeLanguages" = @{
            "html" = "html"
            "javascript" = "javascript"
            "python" = "python"
        }
        "tailwindCSS.experimental.classRegex" = @(
            "class[:]\\s*['\"]([^'\"]*)['\"]"
        )

        # Extension Kind (workspace isolation)
        "remote.extensionKind" = @{
            "ms-python.python" = "workspace"
            "ms-python.vscode-pylance" = "workspace"
            "GitHub.copilot" = "workspace"
            "TabNine.tabnine-vscode" = "workspace"
            "WallabyJs.wallaby-vscode" = "workspace"
        }

        # Performance Optimizations
        "editor.suggest.maxVisibleSuggestions" = 10
        "editor.quickSuggestionsDelay" = 100
        "files.trimTrailingWhitespace" = $true
        "files.insertFinalNewline" = $true
    }

    $settingsPath = "$vscodeDir\settings.json"
    $settingsJson = $optimalSettings | ConvertTo-Json -Depth 4
    Set-Content -Path $settingsPath -Value $settingsJson -Encoding UTF8

    Write-CleanupLog "Optimal settings configured: $settingsPath" "Success"
}

function Set-JavaScriptConfig {
    Write-CleanupLog "Creating jsconfig.json for Tailwind path resolution..." "Info"

    $jsconfigContent = @{
        "compilerOptions" = @{
            "moduleResolution" = "node"
            "baseUrl" = "./"
            "paths" = @{
                "*" = @("node_modules/*")
            }
        }
        "exclude" = @(
            "profiles",
            "Extensions",
            "envs",
            ".venv_new",
            "node_modules",
            "data"
        )
    }

    $jsconfigPath = "$Workspace\jsconfig.json"
    $jsconfigJson = $jsconfigContent | ConvertTo-Json -Depth 3
    Set-Content -Path $jsconfigPath -Value $jsconfigJson -Encoding UTF8

    Write-CleanupLog "jsconfig.json created successfully" "Success"
}

function Set-VSCodeMemoryLimit {
    Write-CleanupLog "Configuring VS Code memory limit..." "Info"

    $argvPath = "$env:APPDATA\Code\User\argv.json"
    $argvDir = Split-Path $argvPath -Parent

    if (-not (Test-Path $argvDir)) {
        New-Item -ItemType Directory -Path $argvDir -Force | Out-Null
    }

    $argvConfig = @{
        "max-memory" = 8192
        "disable-extensions" = $false
        "enable-crash-reporter" = $false
    }

    $argvJson = $argvConfig | ConvertTo-Json -Depth 2
    Set-Content -Path $argvPath -Value $argvJson -Encoding UTF8

    Write-CleanupLog "Memory limit set to 8GB" "Success"
}

function Invoke-CompleteCleanup {
    Write-CleanupLog "=== STARTING COMPLETE VS CODE CLEANUP ===" "Critical"

    try {
        # Step 1: Stop VS Code
        Stop-AllVSCodeProcesses

        # Step 2: Remove deprecated extensions
        Remove-DeprecatedExtensions

        # Step 3: Clear all caches
        Clear-ExtensionCaches

        # Step 4: Clean workspace contamination
        Remove-BrowserExtensionContamination

        # Step 5: Reset AI extensions
        Reset-AIExtensions

        # Step 6: Configure optimal settings
        Set-OptimalVSCodeSettings

        # Step 7: Set JavaScript config
        Set-JavaScriptConfig

        # Step 8: Set memory limit
        Set-VSCodeMemoryLimit

        Write-CleanupLog "=== CLEANUP COMPLETED SUCCESSFULLY ===" "Success"
        Write-CleanupLog "" "Info"
        Write-CleanupLog "NEXT STEPS:" "Info"
        Write-CleanupLog "1. Restart VS Code" "Info"
        Write-CleanupLog "2. Open workspace: code $Workspace\EQ12-Optimal.code-workspace" "Info"
        Write-CleanupLog "3. Verify extensions are loading correctly" "Info"

        return $true
    }
    catch {
        Write-CleanupLog "Cleanup failed: $($_.Exception.Message)" "Critical"
        return $false
    }
}

# Main execution
try {
    Write-CleanupLog "Starting EQ12 VS Code Complete Cleanup System" "Info"

    switch ($Action) {
        "DeepClean" {
            Stop-AllVSCodeProcesses
            Remove-DeprecatedExtensions
            Clear-ExtensionCaches
        }

        "ResetExtensions" {
            Stop-AllVSCodeProcesses
            Reset-AIExtensions
        }

        "CleanWorkspace" {
            Remove-BrowserExtensionContamination
            Set-JavaScriptConfig
        }

        "OptimizeSettings" {
            Set-OptimalVSCodeSettings
            Set-VSCodeMemoryLimit
        }

        "Complete" {
            $success = Invoke-CompleteCleanup
            exit ($success ? 0 : 1)
        }
    }

    Write-CleanupLog "Cleanup operation completed" "Success"
    exit 0
}
catch {
    Write-CleanupLog "Cleanup system error: $($_.Exception.Message)" "Critical"
    exit 1
}
