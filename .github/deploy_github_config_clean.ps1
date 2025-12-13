# EQ12 Private Repository GitHub Configuration Deployment
param(
    [Parameter(Mandatory=$true)][string]$GitHubUsername,
    [Parameter(Mandatory=$true)][string]$RepositoryPath,
    [switch]$ValidateOnly,
    [switch]$UpdateCODEOWNERS
)

Write-Host "EQ12 GODSTACK GitHub Configuration Deployment" -ForegroundColor Cyan
Write-Host "Repository: $RepositoryPath" -ForegroundColor Green
Write-Host "GitHub User: $GitHubUsername" -ForegroundColor Green

# Validate repository path
if (-not (Test-Path $RepositoryPath)) {
    Write-Error "Repository path not found: $RepositoryPath"
    exit 1
}

if (-not (Test-Path "$RepositoryPath\.git")) {
    Write-Error "Not a git repository: $RepositoryPath"
    exit 1
}

$SourcePath = "C:\EQ12\.github"
$TargetPath = "$RepositoryPath\.github"

if (-not (Test-Path $SourcePath)) {
    Write-Error "EQ12 .github configuration not found at: $SourcePath"
    exit 1
}

Write-Host "`nValidation Phase..." -ForegroundColor Yellow

$RequiredFiles = @(
    "EQ12_CODEOWNERS",
    "EQ12_PULL_REQUEST_TEMPLATE.md", 
    "PULL_REQUEST_TEMPLATE\sensitive_module.md",
    "workflows\ci.yml",
    "workflows\compliance.yml",
    "README.md"
)

foreach ($File in $RequiredFiles) {
    $FilePath = "$SourcePath\$File"
    if (Test-Path $FilePath) {
        Write-Host "Found: $File" -ForegroundColor Green
    } else {
        Write-Host "Missing: $File" -ForegroundColor Red
        exit 1
    }
}

if ($ValidateOnly) {
    Write-Host "`nValidation completed - all required files found!" -ForegroundColor Green
    exit 0
}

Write-Host "`nDeployment Phase..." -ForegroundColor Yellow

# Create target directory
if (-not (Test-Path $TargetPath)) {
    New-Item -ItemType Directory -Path $TargetPath -Force | Out-Null
    Write-Host "Created .github directory" -ForegroundColor Green
}

# Copy files
try {
    Copy-Item "$SourcePath\EQ12_CODEOWNERS" "$TargetPath\CODEOWNERS" -Force
    Copy-Item "$SourcePath\EQ12_PULL_REQUEST_TEMPLATE.md" "$TargetPath\PULL_REQUEST_TEMPLATE.md" -Force
    Copy-Item "$SourcePath\EQ12_dependabot.yml" "$TargetPath\dependabot.yml" -Force
    Copy-Item "$SourcePath\README.md" "$TargetPath\README.md" -Force
    Copy-Item "$SourcePath\PULL_REQUEST_TEMPLATE" "$TargetPath\PULL_REQUEST_TEMPLATE" -Recurse -Force
    Copy-Item "$SourcePath\ISSUE_TEMPLATE" "$TargetPath\ISSUE_TEMPLATE" -Recurse -Force  
    Copy-Item "$SourcePath\workflows" "$TargetPath\workflows" -Recurse -Force
    
    Write-Host "All files copied successfully" -ForegroundColor Green
}
catch {
    Write-Error "Failed to copy files: $($_.Exception.Message)"
    exit 1
}

# Update CODEOWNERS
if ($UpdateCODEOWNERS) {
    Write-Host "`nUpdating CODEOWNERS..." -ForegroundColor Yellow
    $CodeownersPath = "$TargetPath\CODEOWNERS"
    $Content = Get-Content $CodeownersPath -Raw
    $UpdatedContent = $Content -replace '@Vibehigheric', "@$GitHubUsername"
    Set-Content -Path $CodeownersPath -Value $UpdatedContent -Encoding UTF8
    Write-Host "CODEOWNERS updated with @$GitHubUsername" -ForegroundColor Green
}

Write-Host "`nDeployment Complete!" -ForegroundColor Green
Write-Host "Your private repository is now protected with enterprise-grade security" -ForegroundColor Green