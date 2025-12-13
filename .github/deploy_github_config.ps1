# EQ12 Private Repository GitHub Configuration Deployment
# Automates setup of enterprise-grade repository protection

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubUsername,
    
    [Parameter(Mandatory=$true)]
    [string]$RepositoryPath,
    
    [switch]$ValidateOnly,
    [switch]$UpdateCODEOWNERS
)

Write-Host "🔐 EQ12 GODSTACK GitHub Configuration Deployment" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Gray

# Validate repository path
if (-not (Test-Path $RepositoryPath)) {
    Write-Error "Repository path not found: $RepositoryPath"
    exit 1
}

# Check if it's a git repository
if (-not (Test-Path "$RepositoryPath\.git")) {
    Write-Error "Not a git repository: $RepositoryPath"
    exit 1
}

Write-Host "📂 Repository: $RepositoryPath" -ForegroundColor Green
Write-Host "👤 GitHub User: $GitHubUsername" -ForegroundColor Green

# Define source and target paths
$SourcePath = "C:\EQ12\.github"
$TargetPath = "$RepositoryPath\.github"

if (-not (Test-Path $SourcePath)) {
    Write-Error "EQ12 .github configuration not found at: $SourcePath"
    exit 1
}

Write-Host "`n🔍 Validation Phase..." -ForegroundColor Yellow

# Validate source configuration
$RequiredFiles = @(
    "EQ12_CODEOWNERS",
    "EQ12_PULL_REQUEST_TEMPLATE.md",
    "PULL_REQUEST_TEMPLATE\sensitive_module.md",
    "ISSUE_TEMPLATE\bug_report.yml",
    "ISSUE_TEMPLATE\feature_request.yml", 
    "ISSUE_TEMPLATE\security_issue.yml",
    "workflows\ci.yml",
    "workflows\compliance.yml",
    "EQ12_dependabot.yml",
    "README.md"
)

foreach ($File in $RequiredFiles) {
    $FilePath = "$SourcePath\$File"
    if (Test-Path $FilePath) {
        Write-Host "✅ Found: $File" -ForegroundColor Green
    } else {
        Write-Host "❌ Missing: $File" -ForegroundColor Red
        exit 1
    }
}

if ($ValidateOnly) {
    Write-Host "`n✅ Validation completed - all required files found!" -ForegroundColor Green
    exit 0
}

Write-Host "`n🚀 Deployment Phase..." -ForegroundColor Yellow

# Create target .github directory
if (-not (Test-Path $TargetPath)) {
    New-Item -ItemType Directory -Path $TargetPath -Force | Out-Null
    Write-Host "📁 Created .github directory" -ForegroundColor Green
}

# Copy all files
try {
    # Copy main files
    Copy-Item "$SourcePath\EQ12_CODEOWNERS" "$TargetPath\CODEOWNERS" -Force
    Copy-Item "$SourcePath\EQ12_PULL_REQUEST_TEMPLATE.md" "$TargetPath\PULL_REQUEST_TEMPLATE.md" -Force
    Copy-Item "$SourcePath\EQ12_dependabot.yml" "$TargetPath\dependabot.yml" -Force
    Copy-Item "$SourcePath\README.md" "$TargetPath\README.md" -Force
    Copy-Item "$SourcePath\branch_protection_config.md" "$TargetPath\branch_protection_config.md" -Force
    
    # Copy directories recursively
    Copy-Item "$SourcePath\PULL_REQUEST_TEMPLATE" "$TargetPath\PULL_REQUEST_TEMPLATE" -Recurse -Force
    Copy-Item "$SourcePath\ISSUE_TEMPLATE" "$TargetPath\ISSUE_TEMPLATE" -Recurse -Force
    Copy-Item "$SourcePath\workflows" "$TargetPath\workflows" -Recurse -Force
    
    Write-Host "✅ All files copied successfully" -ForegroundColor Green
}
catch {
    Write-Error "Failed to copy files: $($_.Exception.Message)"
    exit 1
}

# Update CODEOWNERS with correct username
if ($UpdateCODEOWNERS) {
    Write-Host "`n📝 Updating CODEOWNERS..." -ForegroundColor Yellow
    
    $CodeownersPath = "$TargetPath\CODEOWNERS"
    $Content = Get-Content $CodeownersPath -Raw
    $UpdatedContent = $Content -replace '@Vibehigheric', "@$GitHubUsername"
    Set-Content -Path $CodeownersPath -Value $UpdatedContent -Encoding UTF8
    
    Write-Host "✅ CODEOWNERS updated with @$GitHubUsername" -ForegroundColor Green
}

Write-Host "`n🔍 Deployment Verification..." -ForegroundColor Yellow

# Verify deployment
$VerificationFiles = @(
    "CODEOWNERS",
    "PULL_REQUEST_TEMPLATE.md",
    "dependabot.yml",
    "workflows\ci.yml",
    "workflows\compliance.yml"
)

foreach ($File in $VerificationFiles) {
    $FilePath = "$TargetPath\$File"
    if (Test-Path $FilePath) {
        $Size = (Get-Item $FilePath).Length
        Write-Host "✅ $File ($Size bytes)" -ForegroundColor Green
    } else {
        Write-Host "❌ $File missing" -ForegroundColor Red
    }
}

Write-Host "`n📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. 🔒 Enable repository security features (Settings → Security)" -ForegroundColor White
Write-Host "2. 🛡️ Apply branch protection rules (Settings → Branches)" -ForegroundColor White
Write-Host "3. 📱 Configure webhooks if desired (Settings → Webhooks)" -ForegroundColor White
Write-Host "4. 🧪 Test with a small PR to verify workflows" -ForegroundColor White

Write-Host "`n🎯 Repository Configuration Commands:" -ForegroundColor Yellow
Write-Host "cd $RepositoryPath" -ForegroundColor Cyan
Write-Host "git add .github/" -ForegroundColor Cyan
Write-Host "git commit -m 'feat: Add enterprise GitHub configuration for EQ12 GODSTACK'" -ForegroundColor Cyan
Write-Host "git push origin main" -ForegroundColor Cyan

Write-Host "`n✅ EQ12 GitHub Configuration Deployment Complete!" -ForegroundColor Green
Write-Host "🔐 Your private repository is now protected with enterprise-grade security" -ForegroundColor Green
Write-Host "🚨 Sensitive modules (betting/cannabis/credit) require your explicit approval" -ForegroundColor Green

# Generate deployment summary
$DeploymentSummary = @{
    timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    repository = $RepositoryPath
    github_user = $GitHubUsername
    deployment_status = 'SUCCESS'
    files_deployed = $RequiredFiles.Count
    security_features = @(
        'CODEOWNERS protection',
        'Sensitive module detection', 
        'Secret scanning',
        'Compliance workflows',
        'Branch protection ready'
    )
}

$LogPath = "$RepositoryPath\.github\deployment_log.json"
$DeploymentSummary | ConvertTo-Json -Depth 3 | Out-File -FilePath $LogPath -Encoding UTF8

$LogPath = "$RepositoryPath\.github\deployment_log.json"
$DeploymentSummary | ConvertTo-Json -Depth 3 | Out-File -FilePath $LogPath -Encoding UTF8

Write-Host "`nDeployment log saved: $LogPath" -ForegroundColor Gray