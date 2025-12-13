#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 Script Integrity Suite - Multi-Language Linting and Auto-Repair System
    
.DESCRIPTION
    Comprehensive script validation, linting, and automated repair for Python, JavaScript,
    PowerShell, Bash, and other scripting languages in the EQ12 ecosystem.
    
.PARAMETER Action
    Action to perform: Scan, Lint, Fix, Audit, Report, All
    
.PARAMETER Language
    Target language: Python, JavaScript, PowerShell, Bash, All
    
.PARAMETER Workspace
    Path to workspace directory (default: current directory)
    
.PARAMETER AutoFix
    Automatically fix detected issues where possible
    
.PARAMETER GenerateReport
    Generate detailed integrity report
    
.EXAMPLE
    .\eq12_script_integrity_suite.ps1 -Action All -AutoFix
    Runs complete integrity check with automatic fixes
    
.EXAMPLE
    .\eq12_script_integrity_suite.ps1 -Action Lint -Language Python
    Lints only Python files
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet('Scan', 'Lint', 'Fix', 'Audit', 'Report', 'All')]
    [string]$Action = 'All',
    
    [Parameter(Mandatory = $false)]
    [ValidateSet('Python', 'JavaScript', 'PowerShell', 'Bash', 'All')]
    [string]$Language = 'All',
    
    [Parameter(Mandatory = $false)]
    [string]$Workspace = $PWD.Path,
    
    [Parameter(Mandatory = $false)]
    [switch]$AutoFix = $true,
    
    [Parameter(Mandatory = $false)]
    [switch]$GenerateReport = $true,
    
    [Parameter(Mandatory = $false)]
    [switch]$Verbose
)

# Initialize logging and directories
$LogDir = "C:\EQ12\logs"
$ConfigDir = "C:\EQ12\configs"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = "$LogDir\script_integrity_$Timestamp.log"
$ReportFile = "$LogDir\ScriptIntegrityReport_$Timestamp.json"

foreach ($dir in @($LogDir, $ConfigDir)) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

function Write-EQ12Log {
    param(
        [string]$Level,
        [string]$Message,
        [object]$Data = $null
    )
    
    $LogEntry = @{
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ")
        level = $Level
        message = $Message
        workspace = $Workspace
        action = $Action
        language = $Language
    }
    
    if ($Data) {
        $LogEntry.data = $Data
    }
    
    $JsonLog = $LogEntry | ConvertTo-Json -Compress
    Add-Content -Path $LogFile -Value $JsonLog
    
    $Color = switch ($Level) {
        'ERROR' { 'Red' }
        'WARN' { 'Yellow' }
        'SUCCESS' { 'Green' }
        'INFO' { 'Cyan' }
        default { 'White' }
    }
    
    Write-Host "[$Level] $Message" -ForegroundColor $Color
}

function Test-ScriptPrerequisites {
    Write-EQ12Log "INFO" "🔍 Checking script linting prerequisites..."
    
    $tools = @{
        'Python' = @('python', 'pip')
        'JavaScript' = @('node', 'npm')
        'PowerShell' = @('pwsh')
        'Bash' = @('bash')
    }
    
    $missing = @()
    $available = @()
    
    foreach ($lang in $tools.Keys) {
        if ($Language -eq 'All' -or $Language -eq $lang) {
            foreach ($tool in $tools[$lang]) {
                if (Get-Command $tool -ErrorAction SilentlyContinue) {
                    $available += "$lang`: $tool"
                } else {
                    $missing += "$lang`: $tool"
                }
            }
        }
    }
    
    if ($available) {
        Write-EQ12Log "SUCCESS" "✅ Available tools: $($available -join ', ')"
    }
    
    if ($missing) {
        Write-EQ12Log "WARN" "⚠️ Missing tools: $($missing -join ', ')"
    }
    
    return @{
        Available = $available
        Missing = $missing
    }
}

function Install-LintingTools {
    Write-EQ12Log "INFO" "📦 Installing/updating linting tools..."
    
    $installations = @()
    
    try {
        # Python linting tools
        if ($Language -eq 'All' -or $Language -eq 'Python') {
            if (Get-Command python -ErrorAction SilentlyContinue) {
                Write-EQ12Log "INFO" "Installing Python linting tools..."
                
                $pythonTools = @('flake8', 'black', 'pylint', 'mypy', 'bandit', 'safety')
                foreach ($tool in $pythonTools) {
                    try {
                        pip install --upgrade $tool --quiet
                        $installations += "Python: $tool"
                    } catch {
                        Write-EQ12Log "WARN" "Failed to install $tool"
                    }
                }
            }
        }
        
        # JavaScript linting tools
        if ($Language -eq 'All' -or $Language -eq 'JavaScript') {
            if (Get-Command npm -ErrorAction SilentlyContinue) {
                Write-EQ12Log "INFO" "Installing JavaScript linting tools..."
                
                # Check if we're in a Node.js project
                if (Test-Path "$Workspace\package.json") {
                    npm install --save-dev eslint prettier @eslint/js typescript 2>$null
                    $installations += "JavaScript: ESLint, Prettier"
                } else {
                    # Global installation
                    npm install -g eslint prettier 2>$null
                    $installations += "JavaScript: ESLint, Prettier (global)"
                }
            }
        }
        
        # PowerShell linting tools
        if ($Language -eq 'All' -or $Language -eq 'PowerShell') {
            if (Get-Command pwsh -ErrorAction SilentlyContinue) {
                Write-EQ12Log "INFO" "Installing PowerShell linting tools..."
                
                try {
                    pwsh -Command "Install-Module -Name PSScriptAnalyzer -Scope CurrentUser -Force -AllowClobber" 2>$null
                    $installations += "PowerShell: PSScriptAnalyzer"
                } catch {
                    Write-EQ12Log "WARN" "Failed to install PSScriptAnalyzer"
                }
            }
        }
        
        # Bash linting tools
        if ($Language -eq 'All' -or $Language -eq 'Bash') {
            if (Get-Command shellcheck -ErrorAction SilentlyContinue) {
                $installations += "Bash: ShellCheck (already available)"
            } else {
                Write-EQ12Log "WARN" "ShellCheck not available - install from https://github.com/koalaman/shellcheck"
            }
        }
        
    } catch {
        Write-EQ12Log "ERROR" "Error during tool installation: $($_.Exception.Message)"
    }
    
    return $installations
}

function Get-ScriptFiles {
    Write-EQ12Log "INFO" "🔍 Discovering script files in workspace..."
    
    $patterns = @{
        'Python' = '*.py'
        'JavaScript' = @('*.js', '*.jsx', '*.ts', '*.tsx', '*.mjs')
        'PowerShell' = @('*.ps1', '*.psm1', '*.psd1')
        'Bash' = @('*.sh', '*.bash')
    }
    
    $scriptFiles = @{}
    
    foreach ($lang in $patterns.Keys) {
        if ($Language -eq 'All' -or $Language -eq $lang) {
            $files = @()
            
            foreach ($pattern in $patterns[$lang]) {
                $found = Get-ChildItem -Path $Workspace -Recurse -Include $pattern -File | 
                        Where-Object { $_.FullName -notmatch '(node_modules|__pycache__|\.git|\.vs|bin|obj)' }
                $files += $found
            }
            
            if ($files) {
                $scriptFiles[$lang] = $files
                Write-EQ12Log "INFO" "📋 Found $($files.Count) $lang files"
            }
        }
    }
    
    return $scriptFiles
}

function Invoke-PythonLinting {
    param([System.IO.FileInfo[]]$Files)
    
    Write-EQ12Log "INFO" "🐍 Running Python linting and security checks..."
    
    $results = @{
        Flake8 = @()
        Black = @()
        Pylint = @()
        MyPy = @()
        Bandit = @()
        Safety = @()
        Errors = @()
    }
    
    Push-Location $Workspace
    try {
        # Flake8 - Style and syntax checking
        if (Get-Command flake8 -ErrorAction SilentlyContinue) {
            Write-EQ12Log "INFO" "Running Flake8..."
            $flake8Output = flake8 --max-line-length=120 --extend-ignore=E203,W503 $Files.FullName 2>&1
            if ($LASTEXITCODE -ne 0) {
                $results.Flake8 = $flake8Output -split "`n" | Where-Object { $_ -ne "" }
            }
            
            if ($AutoFix) {
                # Flake8 doesn't auto-fix, but we can use autopep8
                if (Get-Command autopep8 -ErrorAction SilentlyContinue) {
                    autopep8 --in-place --max-line-length=120 $Files.FullName 2>$null
                }
            }
        }
        
        # Black - Code formatting
        if (Get-Command black -ErrorAction SilentlyContinue) {
            Write-EQ12Log "INFO" "Running Black formatter..."
            if ($AutoFix) {
                $blackOutput = black --line-length=120 $Files.FullName 2>&1
                $results.Black = $blackOutput -split "`n" | Where-Object { $_ -like "*reformatted*" }
            } else {
                $blackOutput = black --check --line-length=120 $Files.FullName 2>&1
                if ($LASTEXITCODE -ne 0) {
                    $results.Black = $blackOutput -split "`n" | Where-Object { $_ -ne "" }
                }
            }
        }
        
        # Pylint - Comprehensive analysis
        if (Get-Command pylint -ErrorAction SilentlyContinue) {
            Write-EQ12Log "INFO" "Running Pylint..."
            $pylintOutput = pylint --disable=C0114,C0115,C0116 --output-format=text $Files.FullName 2>&1
            if ($LASTEXITCODE -ne 0) {
                $results.Pylint = $pylintOutput -split "`n" | Where-Object { $_ -match "^\w+:" }
            }
        }
        
        # MyPy - Type checking
        if (Get-Command mypy -ErrorAction SilentlyContinue) {
            Write-EQ12Log "INFO" "Running MyPy type checking..."
            $mypyOutput = mypy --ignore-missing-imports $Files.FullName 2>&1
            if ($LASTEXITCODE -ne 0) {
                $results.MyPy = $mypyOutput -split "`n" | Where-Object { $_ -ne "" }
            }
        }
        
        # Bandit - Security analysis
        if (Get-Command bandit -ErrorAction SilentlyContinue) {
            Write-EQ12Log "INFO" "Running Bandit security analysis..."
            $banditOutput = bandit -r . -f json 2>&1
            if ($LASTEXITCODE -ne 0 -and $banditOutput -match "^\{") {
                try {
                    $banditJson = $banditOutput | ConvertFrom-Json
                    $results.Bandit = $banditJson.results
                } catch {
                    $results.Bandit = @("Bandit analysis completed with warnings")
                }
            }
        }
        
        # Safety - Dependency vulnerability check
        if (Get-Command safety -ErrorAction SilentlyContinue) {
            Write-EQ12Log "INFO" "Running Safety vulnerability check..."
            $safetyOutput = safety check --json 2>&1
            if ($LASTEXITCODE -ne 0 -and $safetyOutput -match "^\[") {
                try {
                    $safetyJson = $safetyOutput | ConvertFrom-Json
                    $results.Safety = $safetyJson
                } catch {
                    $results.Safety = @("Safety check completed with warnings")
                }
            }
        }
        
    } catch {
        $results.Errors += "Python linting error: $($_.Exception.Message)"
    } finally {
        Pop-Location
    }
    
    return $results
}

function Invoke-JavaScriptLinting {
    param([System.IO.FileInfo[]]$Files)
    
    Write-EQ12Log "INFO" "🟨 Running JavaScript/TypeScript linting..."
    
    $results = @{
        ESLint = @()
        Prettier = @()
        TypeScript = @()
        Errors = @()
    }
    
    Push-Location $Workspace
    try {
        # ESLint
        if (Get-Command eslint -ErrorAction SilentlyContinue -or (Test-Path "node_modules\.bin\eslint.cmd")) {
            Write-EQ12Log "INFO" "Running ESLint..."
            
            $eslintCmd = if (Test-Path "node_modules\.bin\eslint.cmd") { 
                "node_modules\.bin\eslint.cmd" 
            } else { 
                "eslint" 
            }
            
            if ($AutoFix) {
                $eslintOutput = & $eslintCmd --fix --ext .js,.jsx,.ts,.tsx . 2>&1
            } else {
                $eslintOutput = & $eslintCmd --ext .js,.jsx,.ts,.tsx . 2>&1
            }
            
            if ($LASTEXITCODE -ne 0) {
                $results.ESLint = $eslintOutput -split "`n" | Where-Object { $_ -ne "" }
            }
        }
        
        # Prettier
        if (Get-Command prettier -ErrorAction SilentlyContinue -or (Test-Path "node_modules\.bin\prettier.cmd")) {
            Write-EQ12Log "INFO" "Running Prettier..."
            
            $prettierCmd = if (Test-Path "node_modules\.bin\prettier.cmd") { 
                "node_modules\.bin\prettier.cmd" 
            } else { 
                "prettier" 
            }
            
            if ($AutoFix) {
                $prettierOutput = & $prettierCmd --write "**/*.{js,jsx,ts,tsx,json,css,md}" 2>&1
                $results.Prettier = $prettierOutput -split "`n" | Where-Object { $_ -ne "" }
            } else {
                $prettierOutput = & $prettierCmd --check "**/*.{js,jsx,ts,tsx,json,css,md}" 2>&1
                if ($LASTEXITCODE -ne 0) {
                    $results.Prettier = $prettierOutput -split "`n" | Where-Object { $_ -ne "" }
                }
            }
        }
        
        # TypeScript compiler check
        if (Get-Command tsc -ErrorAction SilentlyContinue -and (Test-Path "tsconfig.json")) {
            Write-EQ12Log "INFO" "Running TypeScript compiler check..."
            $tscOutput = tsc --noEmit 2>&1
            if ($LASTEXITCODE -ne 0) {
                $results.TypeScript = $tscOutput -split "`n" | Where-Object { $_ -ne "" }
            }
        }
        
    } catch {
        $results.Errors += "JavaScript linting error: $($_.Exception.Message)"
    } finally {
        Pop-Location
    }
    
    return $results
}

function Invoke-PowerShellLinting {
    param([System.IO.FileInfo[]]$Files)
    
    Write-EQ12Log "INFO" "💙 Running PowerShell script analysis..."
    
    $results = @{
        PSScriptAnalyzer = @()
        Errors = @()
    }
    
    try {
        # Check if PSScriptAnalyzer is available
        $psaAvailable = $false
        try {
            Import-Module PSScriptAnalyzer -ErrorAction Stop
            $psaAvailable = $true
        } catch {
            try {
                pwsh -Command "Import-Module PSScriptAnalyzer" 2>$null
                if ($LASTEXITCODE -eq 0) {
                    $psaAvailable = $true
                }
            } catch {
                Write-EQ12Log "WARN" "PSScriptAnalyzer not available"
            }
        }
        
        if ($psaAvailable) {
            Write-EQ12Log "INFO" "Running PSScriptAnalyzer..."
            
            foreach ($file in $Files) {
                try {
                    if ($AutoFix) {
                        # Run with fix capability
                        $analysis = pwsh -Command "Invoke-ScriptAnalyzer -Path '$($file.FullName)' -Fix"
                    } else {
                        # Analysis only
                        $analysis = pwsh -Command "Invoke-ScriptAnalyzer -Path '$($file.FullName)'"
                    }
                    
                    if ($analysis) {
                        $results.PSScriptAnalyzer += $analysis
                    }
                } catch {
                    $results.Errors += "Error analyzing $($file.Name): $($_.Exception.Message)"
                }
            }
        } else {
            $results.Errors += "PSScriptAnalyzer not available - install with: Install-Module PSScriptAnalyzer"
        }
        
    } catch {
        $results.Errors += "PowerShell linting error: $($_.Exception.Message)"
    }
    
    return $results
}

function Invoke-BashLinting {
    param([System.IO.FileInfo[]]$Files)
    
    Write-EQ12Log "INFO" "🐚 Running Bash script analysis..."
    
    $results = @{
        ShellCheck = @()
        Errors = @()
    }
    
    try {
        if (Get-Command shellcheck -ErrorAction SilentlyContinue) {
            Write-EQ12Log "INFO" "Running ShellCheck..."
            
            foreach ($file in $Files) {
                try {
                    $shellcheckOutput = shellcheck -f json $file.FullName 2>&1
                    if ($LASTEXITCODE -ne 0 -and $shellcheckOutput -match "^\[") {
                        $shellcheckJson = $shellcheckOutput | ConvertFrom-Json
                        $results.ShellCheck += $shellcheckJson
                    }
                } catch {
                    $results.Errors += "Error checking $($file.Name): $($_.Exception.Message)"
                }
            }
        } else {
            $results.Errors += "ShellCheck not available - install from: https://github.com/koalaman/shellcheck"
        }
        
    } catch {
        $results.Errors += "Bash linting error: $($_.Exception.Message)"
    }
    
    return $results
}

function New-IntegrityReport {
    param($AllResults, $ScriptFiles, $Prerequisites)
    
    Write-EQ12Log "INFO" "📊 Generating comprehensive integrity report..."
    
    $report = @{
        Timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ")
        Workspace = $Workspace
        Action = $Action
        Language = $Language
        AutoFix = $AutoFix.IsPresent
        Prerequisites = $Prerequisites
        ScriptFiles = @{}
        LintingResults = $AllResults
        Summary = @{
            TotalFiles = 0
            IssuesFound = 0
            IssuesFixed = 0
            Errors = 0
        }
    }
    
    # Add file counts
    foreach ($lang in $ScriptFiles.Keys) {
        $report.ScriptFiles[$lang] = $ScriptFiles[$lang].Count
        $report.Summary.TotalFiles += $ScriptFiles[$lang].Count
    }
    
    # Count issues and errors
    foreach ($lang in $AllResults.Keys) {
        foreach ($tool in $AllResults[$lang].Keys) {
            if ($tool -eq 'Errors') {
                $report.Summary.Errors += $AllResults[$lang][$tool].Count
            } else {
                $report.Summary.IssuesFound += $AllResults[$lang][$tool].Count
            }
        }
    }
    
    # Save report
    if ($GenerateReport) {
        $report | ConvertTo-Json -Depth 10 | Set-Content -Path $ReportFile
        Write-EQ12Log "SUCCESS" "📋 Integrity report saved: $ReportFile"
    }
    
    return $report
}

# Main execution logic
Write-EQ12Log "INFO" "🚀 EQ12 Script Integrity Suite starting..."
Write-EQ12Log "INFO" "Action: $Action | Language: $Language | Workspace: $Workspace"

$allResults = @{}
$scriptFiles = @{}

try {
    # Step 1: Check prerequisites
    $prerequisites = Test-ScriptPrerequisites
    
    # Step 2: Install/update linting tools if requested
    if ($Action -eq 'All' -or $Action -eq 'Audit') {
        $installations = Install-LintingTools
        if ($installations) {
            Write-EQ12Log "SUCCESS" "✅ Installed tools: $($installations -join ', ')"
        }
    }
    
    # Step 3: Discover script files
    if ($Action -ne 'Report') {
        $scriptFiles = Get-ScriptFiles
        
        if ($scriptFiles.Count -eq 0) {
            Write-EQ12Log "WARN" "⚠️ No script files found for specified language(s)"
        }
    }
    
    # Step 4: Run linting based on action and language
    foreach ($lang in $scriptFiles.Keys) {
        Write-EQ12Log "INFO" "🔍 Processing $lang files..."
        
        switch ($lang) {
            'Python' {
                $allResults[$lang] = Invoke-PythonLinting -Files $scriptFiles[$lang]
            }
            'JavaScript' {
                $allResults[$lang] = Invoke-JavaScriptLinting -Files $scriptFiles[$lang]
            }
            'PowerShell' {
                $allResults[$lang] = Invoke-PowerShellLinting -Files $scriptFiles[$lang]
            }
            'Bash' {
                $allResults[$lang] = Invoke-BashLinting -Files $scriptFiles[$lang]
            }
        }
    }
    
    # Step 5: Generate report
    $report = New-IntegrityReport -AllResults $allResults -ScriptFiles $scriptFiles -Prerequisites $prerequisites
    
    # Step 6: Summary
    Write-EQ12Log "SUCCESS" "✅ Script integrity check completed"
    Write-EQ12Log "INFO" "📊 Summary:"
    Write-EQ12Log "INFO" "   Total files processed: $($report.Summary.TotalFiles)"
    Write-EQ12Log "INFO" "   Issues found: $($report.Summary.IssuesFound)"
    Write-EQ12Log "INFO" "   Errors: $($report.Summary.Errors)"
    
    if ($report.Summary.IssuesFound -eq 0 -and $report.Summary.Errors -eq 0) {
        Write-EQ12Log "SUCCESS" "🎉 All scripts are clean and compliant!"
        exit 0
    } elseif ($report.Summary.Errors -gt 0) {
        Write-EQ12Log "ERROR" "❌ Script integrity check completed with errors"
        exit 1
    } else {
        Write-EQ12Log "WARN" "⚠️ Issues found - review report for details"
        exit 2
    }
    
} catch {
    Write-EQ12Log "ERROR" "❌ Fatal error: $($_.Exception.Message)"
    exit 1
}