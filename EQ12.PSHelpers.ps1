# EQ12.PSHelpers.ps1

# --- UTF-8 console (stops emoji/🔍 logging crashes) ---
function Set-ConsoleUtf8 {
    [CmdletBinding()]
    param()

    try {
        [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
        $env:LC_ALL = "en_US.UTF-8"
        Write-Verbose "Console encoding set to UTF-8"
    }
    catch {
        Write-Warning "Failed to set UTF-8 encoding: $($_.Exception.Message)"
    }
}

# --- Safe env getter (string name) ---
function Get-EnvVar {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [string]$Default = $null,
        [switch]$Required
    )

    $val = [System.Environment]::GetEnvironmentVariable($Name)
    if ([string]::IsNullOrWhiteSpace($val)) {
        $val = $Default
    }

    if ($Required -and [string]::IsNullOrWhiteSpace($val)) {
        throw "Missing required env: $Name"
    }

    return $val
}

# --- Color log ---
function Write-Log {
    [CmdletBinding()]
    param(
        [ValidateSet("INFO", "WARN", "ERROR", "OK")][string]$Level = "INFO",
        [Parameter(Mandatory = $true)][string]$Message
    )

    $map = @{
        "INFO"  = "Cyan"
        "WARN"  = "Yellow"
        "ERROR" = "Red"
        "OK"    = "Green"
    }

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $map[$Level]
}

# --- Quick port & HTTP checks ---
function Test-PortOpen {
    [CmdletBinding()]
    param([int]$Port = 3000)

    try {
        $conn = netstat -ano | Select-String (":$Port\s+.*LISTENING")
        return [bool]$conn
    }
    catch {
        Write-Warning "Failed to check port $Port`: $($_.Exception.Message)"
        return $false
    }
}

function Invoke-Head {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$Url)

    try {
        $response = Invoke-WebRequest -Uri $Url -Method Head -TimeoutSec 5 -ErrorAction Stop
        return $response.StatusCode
    }
    catch {
        if ($_.Exception.Response) {
            return $_.Exception.Response.StatusCode.value__
        }
        return 0
    }
}

# --- Fix file encoding to UTF-8 (no BOM) to avoid "string terminator" oddities ---
function Set-FileUtf8NoBom {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$Path)

    try {
        if (-not (Test-Path -LiteralPath $Path)) {
            throw "File not found: $Path"
        }

        $text = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
        $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($Path, $text, $utf8NoBom)
        Write-Log -Level OK -Message "Rewrote $Path as UTF-8 (no BOM)"
    }
    catch {
        Write-Log -Level ERROR -Message "Failed to convert $Path to UTF-8: $($_.Exception.Message)"
        throw
    }
}

# --- Replace curly quotes & bad characters that break PS parsing ---
function Normalize-Quotes {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$Path)

    try {
        if (-not (Test-Path -LiteralPath $Path)) {
            throw "File not found: $Path"
        }

        $raw = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
        $fixed = $raw -replace '[\u2018\u2019\u201A\u201B]', "'" `
            -replace '[\u201C\u201D\u201E\u201F]', '"'

        if ($fixed -ne $raw) {
            $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
            [IO.File]::WriteAllText($Path, $fixed, $utf8NoBom)
            Write-Log -Level OK -Message "Normalized quotes in $Path"
        }
        else {
            Write-Log -Level INFO -Message "No quote normalization needed in $Path"
        }
    }
    catch {
        Write-Log -Level ERROR -Message "Failed to normalize quotes in $Path`: $($_.Exception.Message)"
        throw
    }
}

# --- Brace balance sanity check (fast lint) ---
function Assert-BracesBalanced {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$Path)

    try {
        if (-not (Test-Path -LiteralPath $Path)) {
            throw "File not found: $Path"
        }

        $t = Get-Content -LiteralPath $Path -Raw -Encoding UTF8
        $open = ($t.ToCharArray() | Where-Object { $_ -eq '{' }).Count
        $close = ($t.ToCharArray() | Where-Object { $_ -eq '}' }).Count

        if ($open -ne $close) {
            throw "Brace mismatch in $Path`: {=$open }=$close"
        }

        Write-Log -Level OK -Message "Brace balance verified in $Path"
    }
    catch {
        Write-Log -Level ERROR -Message "Brace validation failed for $Path`: $($_.Exception.Message)"
        throw
    }
}

# --- One-liner fixer for your scripts that failed ---
function Repair-PSScript {
    [CmdletBinding()]
    param([Parameter(Mandatory = $true)][string]$Path)

    try {
        Set-ConsoleUtf8
        Write-Log -Level INFO -Message "Starting repair for $Path"

        Normalize-Quotes -Path $Path
        Set-FileUtf8NoBom -Path $Path
        Assert-BracesBalanced -Path $Path

        Write-Log -Level OK -Message "Repair pass completed for $Path"
    }
    catch {
        Write-Log -Level ERROR -Message "Repair failed for $Path`: $($_.Exception.Message)"
        throw
    }
}

# --- Test HTTP endpoint with proper error handling ---
function Test-HttpEndpoint {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Url,
        [int]$TimeoutSec = 5,
        [string]$Method = "GET"
    )

    try {
        $response = Invoke-WebRequest -Uri $Url -Method $Method -TimeoutSec $TimeoutSec -ErrorAction Stop
        return @{
            Success    = $true
            StatusCode = $response.StatusCode
            Error      = $null
        }
    }
    catch {
        return @{
            Success    = $false
            StatusCode = if ($_.Exception.Response) { $_.Exception.Response.StatusCode.value__ } else { 0 }
            Error      = $_.Exception.Message
        }
    }
}

# --- EQ12 Status Check Helper ---
function Test-EQ12Services {
    [CmdletBinding()]
    param(
        [string[]]$Endpoints = @("http://localhost:3000/health", "http://localhost:3000/dashboard"),
        [int[]]$Ports = @(3000, 8080, 8081)
    )

    Write-Log -Level INFO -Message "EQ12 Services Status Check"
    Write-Host "=" * 50

    # Check ports
    foreach ($port in $Ports) {
        $isOpen = Test-PortOpen -Port $port
        $status = if ($isOpen) { "LISTENING" } else { "CLOSED" }
        $color = if ($isOpen) { "Green" } else { "Yellow" }
        Write-Host "Port $port`: $status" -ForegroundColor $color
    }

    Write-Host ""

    # Check endpoints
    foreach ($endpoint in $Endpoints) {
        $result = Test-HttpEndpoint -Url $endpoint
        if ($result.Success) {
            Write-Host "$endpoint`: HTTP $($result.StatusCode)" -ForegroundColor Green
        }
        else {
            Write-Host "$endpoint`: $($result.Error)" -ForegroundColor Red
        }
    }
}

# --- Environment Validation ---
function Test-EQ12Environment {
    [CmdletBinding()]
    param()

    Write-Log -Level INFO -Message "EQ12 Environment Validation"

    $requiredVars = @("OPENAI_API_KEY")
    $optionalVars = @("CHATGPT_API_KEY", "TELEGRAM_BOT_TOKEN", "ODDS_API_KEY")

    foreach ($var in $requiredVars) {
        try {
            $val = Get-EnvVar -Name $var -Required
            Write-Log -Level OK -Message "$var is set"
        }
        catch {
            Write-Log -Level ERROR -Message "$var is missing (required)"
        }
    }

    foreach ($var in $optionalVars) {
        $val = Get-EnvVar -Name $var
        if ($val) {
            Write-Log -Level OK -Message "$var is set"
        }
        else {
            Write-Log -Level WARN -Message "$var is not set (optional)"
        }
    }
}

# Functions are available when dot-sourced
# Remove Export-ModuleMember for script usage
