# EQ12 GitHub CLI Task Integration
# Add these tasks to your tasks.json for easy GitHub CLI management

$TasksToAdd = @"
{
    "label": "EQ12: GitHub CLI Status",
    "type": "shell",
    "command": "powershell",
    "args": [
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        "`${workspaceFolder}/scripts/eq12_github_cli_manager.ps1",
        "-Action",
        "Status"
    ],
    "group": "test",
    "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
    }
},
{
    "label": "EQ12: Install GitHub CLI",
    "type": "shell",
    "command": "powershell",
    "args": [
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        "`${workspaceFolder}/scripts/eq12_github_cli_manager.ps1",
        "-Action",
        "Install"
    ],
    "group": "build",
    "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": true,
        "panel": "dedicated"
    }
},
{
    "label": "EQ12: Download GitHub CLI",
    "type": "shell",
    "command": "powershell",
    "args": [
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        "`${workspaceFolder}/scripts/eq12_github_cli_manager.ps1",
        "-Action",
        "Download"
    ],
    "group": "build",
    "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
    }
},
{
    "label": "EQ12: Test GitHub CLI",
    "type": "shell",
    "command": "powershell",
    "args": [
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        "`${workspaceFolder}/scripts/eq12_github_cli_manager.ps1",
        "-Action",
        "Test"
    ],
    "group": "test",
    "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "shared"
    }
}
"@

Write-Host "🚀 EQ12 GitHub CLI Task Integration" -ForegroundColor Green
Write-Host "=" * 50

Write-Host "`nAdd these tasks to your .vscode/tasks.json file:" -ForegroundColor Yellow
Write-Host $TasksToAdd

Write-Host "`n📋 Quick Commands:" -ForegroundColor Cyan
Write-Host "  Status Check: .\scripts\eq12_github_cli_manager.ps1 -Action Status"
Write-Host "  Download:     .\scripts\eq12_github_cli_manager.ps1 -Action Download"
Write-Host "  Install:      .\scripts\eq12_github_cli_manager.ps1 -Action Install"
Write-Host "  Test:         .\scripts\eq12_github_cli_manager.ps1 -Action Test"

Write-Host "`n[SUCCESS] GitHub CLI integration ready for EQ12 stack!" -ForegroundColor Green