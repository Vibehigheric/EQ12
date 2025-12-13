#!/usr/bin/env pwsh
<#
.SYNOPSIS
    EQ12 External Repository Fetcher
.DESCRIPTION
    Clone and analyze external repositories for EQ12 integration
.PARAMETER Repo
    Specific repository to clone (format: owner/repo)
.PARAMETER Update
    Update existing repositories
.PARAMETER Analyze
    Generate analysis reports after cloning
.PARAMETER Clean
    Clean _third_party directory before cloning
#>

param(
    [string]$Repo = "",
    [switch]$Update,
    [switch]$Analyze,
    [switch]$Clean
)

# Repository list from EXTERNAL_REPOS.md
$repositories = @(
    @{ name = "swar/nba_api"; priority = "P0"; purpose = "NBA API wrapper" },
    @{ name = "microsoft/LightGBM"; priority = "P0"; purpose = "ML framework" },
    @{ name = "PrefectHQ/prefect"; priority = "P1"; purpose = "Workflow orchestration" },
    @{ name = "streamlit/streamlit"; priority = "P1"; purpose = "Dashboard framework" },
    @{ name = "great-expectations/great_expectations"; priority = "P1"; purpose = "Data quality" },
    @{ name = "gitleaks/gitleaks"; priority = "P0"; purpose = "Secret scanning" },
    @{ name = "psf/black"; priority = "P1"; purpose = "Code formatting" },
    @{ name = "pytest-dev/pytest"; priority = "P0"; purpose = "Testing framework" },
    @{ name = "facebook/prophet"; priority = "P2"; purpose = "Time series forecasting" },
    @{ name = "docker/awesome-compose"; priority = "P1"; purpose = "Docker examples" }
)

$thirdPartyPath = "C:\EQ12\_third_party"

function Write-Header($message) {
    Write-Host "`n $message" -ForegroundColor Cyan
    Write-Host ("=" * ($message.Length + 4)) -ForegroundColor DarkCyan
}

function Test-GitAvailable {
    if (!(Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Host " Git not found. Please install Git first." -ForegroundColor Red
        exit 1
    }
}

function New-ThirdPartyDirectory {
    if ($Clean -and (Test-Path $thirdPartyPath)) {
        Write-Host "  Cleaning existing _third_party directory..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force $thirdPartyPath
    }
    
    if (!(Test-Path $thirdPartyPath)) {
        New-Item -ItemType Directory -Path $thirdPartyPath -Force | Out-Null
        Write-Host " Created _third_party directory" -ForegroundColor Green
    }
}

function Invoke-GitClone($repoName, $priority, $purpose) {
    $repoPath = Join-Path $thirdPartyPath $repoName.Replace("/", "_")
    $gitUrl = "https://github.com/$repoName.git"
    
    if (Test-Path $repoPath) {
        if ($Update) {
            Write-Host " Updating $repoName..." -ForegroundColor Yellow
            Push-Location $repoPath
            try {
                git pull origin main 2>$null || git pull origin master 2>$null
                Write-Host " Updated $repoName" -ForegroundColor Green
            }
            catch {
                Write-Host "  Failed to update $repoName" -ForegroundColor Yellow
            }
            finally {
                Pop-Location
            }
        }
        else {
            Write-Host " $repoName already exists (use -Update to refresh)" -ForegroundColor Blue
        }
    }
    else {
        Write-Host " Cloning $repoName ($priority)..." -ForegroundColor Yellow
        try {
            git clone --depth 1 $gitUrl $repoPath 2>$null
            Write-Host " Cloned $repoName" -ForegroundColor Green
            
            # Create metadata file
            $metadata = @{
                repository  = $repoName
                priority    = $priority
                purpose     = $purpose
                cloned_date = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
                git_url     = $gitUrl
            } | ConvertTo-Json -Depth 2
            
            $metadata | Out-File -FilePath (Join-Path $repoPath "_eq12_metadata.json") -Encoding UTF8
            
        }
        catch {
            Write-Host " Failed to clone $repoName" -ForegroundColor Red
        }
    }
}

function New-AnalysisReport {
    Write-Header "Generating Analysis Report"
    
    $reportPath = Join-Path $thirdPartyPath "_analysis_report.md"
    $report = @"
# EQ12 Third-Party Repository Analysis
**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## Summary
- **Total Repositories:** $($repositories.Count)
- **Successfully Cloned:** $(Get-ChildItem $thirdPartyPath -Directory | Where-Object { $_.Name -ne "_analysis_report.md" } | Measure-Object).Count
- **Analysis Date:** $(Get-Date -Format "yyyy-MM-dd")

## Repository Analysis

"@

    foreach ($repo in $repositories) {
        $repoPath = Join-Path $thirdPartyPath $repo.name.Replace("/", "_")
        $exists = Test-Path $repoPath
        
        $report += @"

### $($repo.name)
- **Priority:** $($repo.priority)
- **Purpose:** $($repo.purpose)
- **Status:** $(if ($exists) { " Cloned" } else { " Missing" })

"@
        
        if ($exists) {
            # Basic file analysis
            $pyFiles = Get-ChildItem $repoPath -Recurse -Filter "*.py" -ErrorAction SilentlyContinue | Measure-Object
            $jsFiles = Get-ChildItem $repoPath -Recurse -Filter "*.js" -ErrorAction SilentlyContinue | Measure-Object
            $dockerFiles = Get-ChildItem $repoPath -Recurse -Filter "Dockerfile*" -ErrorAction SilentlyContinue | Measure-Object
            $testFiles = Get-ChildItem $repoPath -Recurse -Path "*/test*" -ErrorAction SilentlyContinue | Measure-Object
            
            $report += @"
- **Python Files:** $($pyFiles.Count)
- **JavaScript Files:** $($jsFiles.Count)
- **Docker Files:** $($dockerFiles.Count)
- **Test Files:** $($testFiles.Count)

"@
            
            # Check for key files
            $keyFiles = @("README.md", "requirements.txt", "pyproject.toml", "package.json", "Dockerfile", ".github/workflows")
            foreach ($file in $keyFiles) {
                $filePath = Join-Path $repoPath $file
                if (Test-Path $filePath) {
                    $report += "- **$file:**  Present`n"
                }
            }
        }
    }
    
    $report += @"

## Integration Recommendations

### Immediate Actions
1. Study structure and patterns from P0 repositories
2. Extract reusable configuration files (.github/workflows, pyproject.toml)
3. Adapt testing strategies from pytest-dev/pytest
4. Implement security scanning patterns from gitleaks/gitleaks

### Code Quality Improvements
1. Adopt formatting standards from psf/black
2. Implement testing patterns from high-quality repositories
3. Use CI/CD patterns from mature projects
4. Apply documentation standards

### Architecture Insights
1. Study modular design patterns
2. Analyze dependency management approaches
3. Review security and secret handling
4. Examine deployment and containerization strategies

---
**Next Steps:** Review individual repositories and extract applicable patterns for EQ12 integration.
"@

    $report | Out-File -FilePath $reportPath -Encoding UTF8
    Write-Host " Analysis report generated: $reportPath" -ForegroundColor Green
}

# Main execution
Write-Header "EQ12 External Repository Fetcher"

Test-GitAvailable
New-ThirdPartyDirectory

if ($Repo) {
    # Clone specific repository
    $targetRepo = $repositories | Where-Object { $_.name -eq $Repo }
    if ($targetRepo) {
        Invoke-GitClone $targetRepo.name $targetRepo.priority $targetRepo.purpose
    }
    else {
        Write-Host " Repository '$Repo' not found in curated list" -ForegroundColor Red
        Write-Host "Available repositories:" -ForegroundColor Yellow
        $repositories | ForEach-Object { Write-Host "   $($_.name)" -ForegroundColor White }
        exit 1
    }
}
else {
    # Clone all repositories
    foreach ($repo in $repositories) {
        Invoke-GitClone $repo.name $repo.priority $repo.purpose
    }
}

if ($Analyze) {
    New-AnalysisReport
}

Write-Host "`n Repository fetching complete!" -ForegroundColor Green
Write-Host " Location: $thirdPartyPath" -ForegroundColor Cyan
Write-Host " Run with -Analyze to generate detailed analysis report" -ForegroundColor Yellow

if ($Analyze) {
    Write-Host "`n Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Review _analysis_report.md" -ForegroundColor White
    Write-Host "  2. Extract applicable patterns" -ForegroundColor White
    Write-Host "  3. Integrate best practices into EQ12" -ForegroundColor White
    Write-Host "  4. Update development workflows" -ForegroundColor White
}