#!/usr/bin/env pwsh
<#
.SYNOPSIS
    EQ12 GODSTACK Task Scheduler Installation Script
    
.DESCRIPTION
    Installs Windows Task Scheduler tasks for automated EQ12 GODSTACK operations:
    - Daily Collection: News aggregation, Swagbucks offers, GPT enrichment
    - Hourly Updates: Meta search and autosuggest generation  
    - Dashboard Server: FastAPI web interface auto-startup
    
.PARAMETER Install
    Install all GODSTACK tasks
    
.PARAMETER Uninstall
    Remove all GODSTACK tasks
    
.PARAMETER List
    List current GODSTACK task status
    
.EXAMPLE
    .\Install-GODSTACKTasks.ps1 -Install
    .\Install-GODSTACKTasks.ps1 -List
    .\Install-GODSTACKTasks.ps1 -Uninstall
    
.NOTES
    Author: EQ12 AI Assistant
    Created: 2025-01-27
    Requires: Administrator privileges
#>

[CmdletBinding()]
param(
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$List
)

# Ensure running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script must be run as Administrator. Exiting..."
    exit 1
}

# Task definitions
$TaskDefinitions = @{
    "EQ12 GODSTACK Daily Collection" = @{
        File = "EQ12_GODSTACK_Daily.xml"
        Description = "Daily news, offers, and enrichment analysis"
        Schedule = "Daily at 8:00 AM"
    }
    "EQ12 GODSTACK Hourly Updates" = @{
        File = "EQ12_GODSTACK_Hourly.xml" 
        Description = "Hourly meta search and autosuggest generation"
        Schedule = "Every hour from 9:00 AM"
    }
    "EQ12 GODSTACK Dashboard" = @{
        File = "EQ12_GODSTACK_Dashboard.xml"
        Description = "FastAPI dashboard server auto-startup"
        Schedule = "On system startup"
    }
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

function Install-GODSTACKTasks {
    Write-Host "🚀 Installing EQ12 GODSTACK Task Scheduler Tasks..." -ForegroundColor Green
    Write-Host ""
    
    foreach ($TaskName in $TaskDefinitions.Keys) {
        $TaskDef = $TaskDefinitions[$TaskName]
        $XmlPath = Join-Path $ScriptDir $TaskDef.File
        
        Write-Host "📋 Installing: $TaskName" -ForegroundColor Cyan
        Write-Host "   Description: $($TaskDef.Description)" -ForegroundColor Gray
        Write-Host "   Schedule: $($TaskDef.Schedule)" -ForegroundColor Gray
        
        if (-not (Test-Path $XmlPath)) {
            Write-Warning "   ❌ XML file not found: $XmlPath"
            continue
        }
        
        try {
            # Remove existing task if it exists
            $ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
            if ($ExistingTask) {
                Write-Host "   🗑️ Removing existing task..." -ForegroundColor Yellow
                Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
            }
            
            # Register new task
            Register-ScheduledTask -Xml (Get-Content $XmlPath | Out-String) -TaskName $TaskName -Force | Out-Null
            Write-Host "   ✅ Task installed successfully" -ForegroundColor Green
            
        } catch {
            Write-Error "   ❌ Failed to install task: $_"
        }
        
        Write-Host ""
    }
    
    Write-Host "🎯 Installation Summary:" -ForegroundColor Green
    List-GODSTACKTasks
}

function Uninstall-GODSTACKTasks {
    Write-Host "🗑️ Uninstalling EQ12 GODSTACK Task Scheduler Tasks..." -ForegroundColor Red
    Write-Host ""
    
    foreach ($TaskName in $TaskDefinitions.Keys) {
        Write-Host "📋 Removing: $TaskName" -ForegroundColor Cyan
        
        try {
            $ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
            if ($ExistingTask) {
                Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
                Write-Host "   ✅ Task removed successfully" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️ Task not found (already removed)" -ForegroundColor Yellow
            }
        } catch {
            Write-Error "   ❌ Failed to remove task: $_"
        }
        
        Write-Host ""
    }
    
    Write-Host "✅ All GODSTACK tasks have been uninstalled" -ForegroundColor Green
}

function List-GODSTACKTasks {
    Write-Host "📊 EQ12 GODSTACK Task Status:" -ForegroundColor Cyan
    Write-Host "=" * 80
    
    foreach ($TaskName in $TaskDefinitions.Keys) {
        $TaskDef = $TaskDefinitions[$TaskName]
        
        try {
            $Task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
            
            if ($Task) {
                $TaskInfo = Get-ScheduledTaskInfo -TaskName $TaskName
                $Status = if ($Task.State -eq 'Ready') { "✅ Enabled" } else { "❌ $($Task.State)" }
                $LastRun = if ($TaskInfo.LastRunTime) { $TaskInfo.LastRunTime.ToString() } else { "Never" }
                $NextRun = if ($TaskInfo.NextRunTime) { $TaskInfo.NextRunTime.ToString() } else { "Not scheduled" }
                
                Write-Host "📋 $TaskName" -ForegroundColor Green
                Write-Host "   Status: $Status" -ForegroundColor $(if ($Task.State -eq 'Ready') { 'Green' } else { 'Red' })
                Write-Host "   Description: $($TaskDef.Description)" -ForegroundColor Gray
                Write-Host "   Schedule: $($TaskDef.Schedule)" -ForegroundColor Gray
                Write-Host "   Last Run: $LastRun" -ForegroundColor Gray
                Write-Host "   Next Run: $NextRun" -ForegroundColor Gray
                
            } else {
                Write-Host "📋 $TaskName" -ForegroundColor Red
                Write-Host "   Status: ❌ Not Installed" -ForegroundColor Red
                Write-Host "   Description: $($TaskDef.Description)" -ForegroundColor Gray
                Write-Host "   Schedule: $($TaskDef.Schedule)" -ForegroundColor Gray
            }
            
        } catch {
            Write-Host "📋 $TaskName" -ForegroundColor Red
            Write-Host "   Status: ❌ Error: $_" -ForegroundColor Red
        }
        
        Write-Host ""
    }
    
    Write-Host "🔧 Management Commands:" -ForegroundColor Cyan
    Write-Host "   View in Task Scheduler: taskschd.msc" -ForegroundColor Gray
    Write-Host "   Manual trigger: schtasks /run /tn `"<TaskName>`"" -ForegroundColor Gray
    Write-Host "   Dashboard URL: http://localhost:8000" -ForegroundColor Yellow
}

function Show-Usage {
    Write-Host "🚀 EQ12 GODSTACK Task Scheduler Manager" -ForegroundColor Green
    Write-Host ""
    Write-Host "USAGE:" -ForegroundColor Cyan
    Write-Host "   .\Install-GODSTACKTasks.ps1 -Install      # Install all tasks"
    Write-Host "   .\Install-GODSTACKTasks.ps1 -Uninstall    # Remove all tasks"  
    Write-Host "   .\Install-GODSTACKTasks.ps1 -List         # Show task status"
    Write-Host ""
    Write-Host "TASKS:" -ForegroundColor Cyan
    foreach ($TaskName in $TaskDefinitions.Keys) {
        $TaskDef = $TaskDefinitions[$TaskName]
        Write-Host "   📋 $TaskName" -ForegroundColor Green
        Write-Host "      $($TaskDef.Description)" -ForegroundColor Gray
        Write-Host "      Schedule: $($TaskDef.Schedule)" -ForegroundColor Gray
        Write-Host ""
    }
}

# Main execution
if ($Install) {
    Install-GODSTACKTasks
} elseif ($Uninstall) {
    Uninstall-GODSTACKTasks
} elseif ($List) {
    List-GODSTACKTasks
} else {
    Show-Usage
}