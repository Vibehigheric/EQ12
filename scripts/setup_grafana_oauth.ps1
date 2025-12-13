<#
.SYNOPSIS
    Configures GitHub and GitLab OAuth for Grafana in the EQ12 Cluster.
.DESCRIPTION
    This script prompts for OAuth credentials and updates the monitoring stack configuration.
    It then redeploys the stack to the M70q node.
.EXAMPLE
    .\setup_grafana_oauth.ps1
#>

[CmdletBinding()]
param()

Write-Host "EQ12 Grafana OAuth Setup" -ForegroundColor Cyan
Write-Host "------------------------" -ForegroundColor Cyan
Write-Host "This script will enable GitHub and GitLab authentication for your Grafana dashboard."
Write-Host "You will need your Client IDs and Secrets from:"
Write-Host " - GitHub: https://github.com/settings/developers"
Write-Host " - GitLab: https://gitlab.com/-/profile/applications"
Write-Host ""

# GitHub Config
$EnableGitHub = Read-Host "Enable GitHub Auth? (y/n)"
if ($EnableGitHub -eq 'y') {
    $GitHubClientID = Read-Host "Enter GitHub Client ID"
    $GitHubClientSecret = Read-Host "Enter GitHub Client Secret"
    $GitHubAllowedOrgs = Read-Host "Enter Allowed GitHub Organizations (space separated, optional)"
}

# GitLab Config
$EnableGitLab = Read-Host "Enable GitLab Auth? (y/n)"
if ($EnableGitLab -eq 'y') {
    $GitLabClientID = Read-Host "Enter GitLab Client ID"
    $GitLabClientSecret = Read-Host "Enter GitLab Client Secret"
    $GitLabAllowedGroups = Read-Host "Enter Allowed GitLab Groups (space separated, optional)"
}

$StackFile = "c:\EQ12_BROKEN_20251122_210342\stacks\monitoring.yml"
$Content = Get-Content $StackFile -Raw

# Helper to add env var if not present or update it
function Update-EnvVar {
    param($Content, $Name, $Value)
    $Pattern = "$Name=.*"
    if ($Content -match $Pattern) {
        return $Content -replace $Pattern, "$Name=$Value"
    }
    else {
        # Find the environment section of grafana
        $InsertPoint = "      - GF_USERS_ALLOW_SIGN_UP=false"
        return $Content.Replace($InsertPoint, "$InsertPoint`n      - $Name=$Value")
    }
}

if ($EnableGitHub -eq 'y') {
    $Content = Update-EnvVar -Content $Content -Name "GF_AUTH_GITHUB_ENABLED" -Value "true"
    $Content = Update-EnvVar -Content $Content -Name "GF_AUTH_GITHUB_CLIENT_ID" -Value $GitHubClientID
    $Content = Update-EnvVar -Content $Content -Name "GF_AUTH_GITHUB_CLIENT_SECRET" -Value $GitHubClientSecret
    $Content = Update-EnvVar -Content $Content -Name "GF_AUTH_GITHUB_SCOPES" -Value "user:email,read:org"
    if ($GitHubAllowedOrgs) {
        $Content = Update-EnvVar -Content $Content -Name "GF_AUTH_GITHUB_ALLOWED_ORGANIZATIONS" -Value $GitHubAllowedOrgs
    }
}

if ($EnableGitLab -eq 'y') {
    $Content = Update-EnvVar -Content $Content -Name "GF_AUTH_GITLAB_ENABLED" -Value "true"
    $Content = Update-EnvVar -Content $Content -Name "GF_AUTH_GITLAB_CLIENT_ID" -Value $GitLabClientID
    $Content = Update-EnvVar -Content $Content -Name "GF_AUTH_GITLAB_CLIENT_SECRET" -Value $GitLabClientSecret
    $Content = Update-EnvVar -Content $Content -Name "GF_AUTH_GITLAB_SCOPES" -Value "read_user"
    if ($GitLabAllowedGroups) {
        $Content = Update-EnvVar -Content $Content -Name "GF_AUTH_GITLAB_ALLOWED_GROUPS" -Value $GitLabAllowedGroups
    }
}

# Save updated file
Set-Content -Path $StackFile -Value $Content
Write-Host "Updated $StackFile" -ForegroundColor Green

# Deploy
Write-Host "Deploying to M70q..." -ForegroundColor Yellow
scp $StackFile ricoj100@192.168.100.3:/opt/monitoring/monitoring.yml
ssh ricoj100@192.168.100.3 "cd /opt/monitoring && sudo docker stack deploy -c monitoring.yml monitoring"

Write-Host "Deployment triggered. Grafana will restart with new settings." -ForegroundColor Green
Write-Host "Access Grafana at http://192.168.100.3:3000" -ForegroundColor Cyan
