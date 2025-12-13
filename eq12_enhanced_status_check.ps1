# EQ12 Enhanced Status Check - PowerShell Edition
# Handles 3xx redirects properly and provides comprehensive status

param(
    [switch]$Detailed,
    [switch]$Json,
    [string]$LogPath = "logs"
)

# UTF-8 output for emoji support
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Test-UrlWithRedirects {
    param([string]$Url, [string]$Name)

    try {
        # Allow up to 5 redirects and don't throw on 3xx
        $response = Invoke-WebRequest -Uri $Url -MaximumRedirection 5 -UseBasicParsing -ErrorAction Stop

        $status = $response.StatusCode
        if ($status -ge 200 -and $status -lt 300) {
            Write-Host "  ✅ $Name : HTTP $status (OK)" -ForegroundColor Green
            return @{ Success = $true; Status = $status; Type = "success" }
        }
        elseif ($status -ge 300 -and $status -lt 400) {
            $location = $response.Headers.Location
            Write-Host "  ✅ $Name : HTTP $status (Redirect to $location)" -ForegroundColor Yellow
            return @{ Success = $true; Status = $status; Type = "redirect"; Location = $location }
        }
        else {
            Write-Host "  ⚠️ $Name : HTTP $status (Unexpected)" -ForegroundColor Yellow
            return @{ Success = $false; Status = $status; Type = "unexpected" }
        }
    }
    catch {
        $ex = $_.Exception

        # Check if it's a redirect that wasn't followed
        if ($ex.Response -and $ex.Response.StatusCode.value__ -ge 300 -and $ex.Response.StatusCode.value__ -lt 400) {
            $location = $ex.Response.Headers.Location
            Write-Host "  ✅ $Name : HTTP $($ex.Response.StatusCode.value__) (Redirect)" -ForegroundColor Yellow
            return @{ Success = $true; Status = $ex.Response.StatusCode.value__; Type = "redirect"; Location = $location }
        }

        Write-Host "  ❌ $Name : FAIL ($($ex.Message))" -ForegroundColor Red
        return @{ Success = $false; Error = $ex.Message; Type = "error" }
    }
}

function Test-ProcessRunning {
    param([string]$ProcessName)

    $processes = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue
    if ($processes) {
        $count = $processes.Count
        Write-Host "  ✅ $ProcessName : $count process(es) running" -ForegroundColor Green
        return @{ Running = $true; Count = $count; PIDs = $processes.Id }
    }
    else {
        Write-Host "  ❌ $ProcessName : Not running" -ForegroundColor Red
        return @{ Running = $false; Count = 0 }
    }
}

function Test-PythonModule {
    param([string]$ModuleName)

    try {
        $result = python -c \"try: import $ModuleName; print('OK'); except: print('FAIL')\" 2>$null
        if ($result -eq "OK") {
            Write-Host "  ✅ Python module '$ModuleName' : Available" -ForegroundColor Green
            return @{ Available = $true }
        }
        else {
            Write-Host "  ❌ Python module '$ModuleName' : Missing" -ForegroundColor Red
            return @{ Available = $false }
        }
    }
    catch {
        Write-Host "  ❌ Python module '$ModuleName' : Error ($($_.Exception.Message))" -ForegroundColor Red
        return @{ Available = $false; Error = $_.Exception.Message }
    }
}

function Test-EnvironmentVariable {
    param([string]$VarName, [string]$ExpectedPattern = ".*")

    $value = [Environment]::GetEnvironmentVariable($VarName, "User")
    if (-not $value) {
        $value = [Environment]::GetEnvironmentVariable($VarName, "Machine")
    }
    if (-not $value) {
        $value = $env:($VarName)
    }

    if ($value -and ($value -match $ExpectedPattern)) {
        $maskedValue = if ($VarName -like "*KEY*" -or $VarName -like "*TOKEN*") {
            $value.Substring(0, [Math]::Min(10, $value.Length)) + "..."
        }
        else { $value }

        Write-Host "  ✅ $VarName : $maskedValue" -ForegroundColor Green
        return @{ Set = $true; Value = $value; Masked = $maskedValue }
    }
    else {
        Write-Host "  ❌ $VarName : Not set or invalid" -ForegroundColor Red
        return @{ Set = $false }
    }
}

# Main status check
Write-Host ""
Write-Host "🚀 EQ12 ENHANCED SYSTEM STATUS CHECK" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host ""

$results = @{}

# 1. Environment Variables
Write-Host "🔍 Environment Configuration" -ForegroundColor Yellow
$results.Environment = @{
    OPENAI_API_KEY = Test-EnvironmentVariable "OPENAI_API_KEY" "sk-.*"
    EQ12_USE_LLM   = Test-EnvironmentVariable "EQ12_USE_LLM" "[01]"
    OPENAI_MODEL   = Test-EnvironmentVariable "OPENAI_MODEL"
    PORT           = Test-EnvironmentVariable "PORT" "\d+"
}
Write-Host ""

# 2. Process Status
Write-Host "⚙️ Process Status" -ForegroundColor Yellow
$results.Processes = @{
    Python     = Test-ProcessRunning "python"
    Node       = Test-ProcessRunning "node"
    PowerShell = Test-ProcessRunning "powershell"
}
Write-Host ""

# 3. Python Modules
Write-Host "🐍 Python Dependencies" -ForegroundColor Yellow
$results.PythonModules = @{
    OpenAI   = Test-PythonModule "openai"
    Asyncio  = Test-PythonModule "asyncio"
    Requests = Test-PythonModule "requests"
    Flask    = Test-PythonModule "flask"
}
Write-Host ""

# 4. Web Services
Write-Host "🌐 Web Services Status" -ForegroundColor Yellow
$results.WebServices = @{
    Health    = Test-UrlWithRedirects "http://localhost:3000/health" "Health Endpoint"
    Dashboard = Test-UrlWithRedirects "http://localhost:3000/dashboard" "Dashboard"
    Root      = Test-UrlWithRedirects "http://localhost:3000/" "Root Redirect"
    API       = Test-UrlWithRedirects "http://localhost:3000/api/health" "API Health"
}
Write-Host ""

# 5. File System
Write-Host "📁 File System Check" -ForegroundColor Yellow
$directories = @("logs", "configs", "scripts", "dashboard", "server")
$results.FileSystem = @{}

foreach ($dir in $directories) {
    if (Test-Path $dir) {
        $itemCount = (Get-ChildItem $dir -ErrorAction SilentlyContinue).Count
        Write-Host "  ✅ $dir/ : $itemCount items" -ForegroundColor Green
        $results.FileSystem.$dir = @{ Exists = $true; ItemCount = $itemCount }
    }
    else {
        Write-Host "  ❌ $dir/ : Missing" -ForegroundColor Red
        $results.FileSystem.$dir = @{ Exists = $false }
    }
}
Write-Host ""

# 6. Calculate Overall Health
$healthScore = 0
$totalChecks = 0

# Count successful checks
foreach ($category in $results.Keys) {
    foreach ($item in $results[$category].Keys) {
        $totalChecks++
        $check = $results[$category][$item]

        $isHealthy = $false
        if ($check.Success -eq $true -or $check.Running -eq $true -or $check.Available -eq $true -or $check.Set -eq $true -or $check.Exists -eq $true) {
            $isHealthy = $true
        }

        if ($isHealthy) { $healthScore++ }
    }
}

$healthPercentage = if ($totalChecks -gt 0) { [Math]::Round(($healthScore / $totalChecks) * 100, 1) } else { 0 }

# Determine overall status
$overallStatus = if ($healthPercentage -ge 80) {
    "🟢 HEALTHY"
}
elseif ($healthPercentage -ge 60) {
    "🟡 DEGRADED"
}
else {
    "🔴 CRITICAL"
}

# Summary
Write-Host "🎯 SYSTEM STATUS SUMMARY" -ForegroundColor Cyan
Write-Host "=" * 40 -ForegroundColor Cyan
Write-Host "Overall Status: $overallStatus" -ForegroundColor $(if ($healthPercentage -ge 80) { "Green" } elseif ($healthPercentage -ge 60) { "Yellow" } else { "Red" })
Write-Host "Health Score: $healthScore/$totalChecks ($healthPercentage%)" -ForegroundColor Gray
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray

# Specific recommendations
Write-Host ""
Write-Host "📋 RECOMMENDATIONS:" -ForegroundColor Yellow

if ($results.Environment.OPENAI_API_KEY.Set -eq $false) {
    Write-Host "  ⚠️ Set OPENAI_API_KEY environment variable" -ForegroundColor Red
}

if ($results.WebServices.Root.Success -eq $false) {
    Write-Host "  ⚠️ Check dashboard server (should handle root redirect properly)" -ForegroundColor Red
}

if ($results.Processes.Node.Running -eq $false) {
    Write-Host "  ⚠️ Start Node.js server: cd server && npm start" -ForegroundColor Red
}

if ($results.PythonModules.OpenAI.Available -eq $false) {
    Write-Host "  ⚠️ Install OpenAI: pip install openai>=2.1.0" -ForegroundColor Red
}

Write-Host ""

# Save detailed report if requested
if ($Json -or $Detailed) {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $reportPath = Join-Path $LogPath "eq12_powershell_status_$timestamp.json"

    $report = @{
        Timestamp        = (Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')
        OverallStatus    = $overallStatus
        HealthScore      = $healthScore
        TotalChecks      = $totalChecks
        HealthPercentage = $healthPercentage
        Results          = $results
    }

    try {
        New-Item -ItemType Directory -Path $LogPath -Force | Out-Null
        $report | ConvertTo-Json -Depth 5 | Out-File -FilePath $reportPath -Encoding UTF8
        Write-Host "📊 Detailed report saved: $reportPath" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️ Could not save report: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🎉 Status check complete!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
