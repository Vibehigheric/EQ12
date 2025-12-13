# EQ12 Files Module (Fixed Watcher)

function Write-EQ12Log {
    param([string]$Message)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$ts - $Message" | Out-File -FilePath "C:\EQ12\logs\eq12_files.log" -Append -Encoding UTF8
}

function Start-EQ12Watcher {
    param(
        [string]$Folder = "C:\EQ12\scripts",
        [string]$Filter = "*.*",
        [switch]$IncludeSubfolders
    )
    $fsw = New-Object System.IO.FileSystemWatcher $Folder, $Filter
    $fsw.IncludeSubdirectories = [bool]$IncludeSubfolders
    $fsw.EnableRaisingEvents = $true

    Register-ObjectEvent -InputObject $fsw -EventName Created -Action {
        $arg = $Event.SourceEventArgs
        $msg = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - CREATED -> $($arg.FullPath)"
        Write-Host $msg
        Write-EQ12Log $msg
    }
    Register-ObjectEvent -InputObject $fsw -EventName Changed -Action {
        $arg = $Event.SourceEventArgs
        $msg = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - CHANGED -> $($arg.FullPath)"
        Write-Host $msg
        Write-EQ12Log $msg
    }
    Register-ObjectEvent -InputObject $fsw -EventName Deleted -Action {
        $arg = $Event.SourceEventArgs
        $msg = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - DELETED -> $($arg.FullPath)"
        Write-Host $msg
        Write-EQ12Log $msg
    }
    Register-ObjectEvent -InputObject $fsw -EventName Renamed -Action {
        $arg = $Event.SourceEventArgs
        $msg = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - RENAMED $($arg.OldFullPath) → $($arg.FullPath)"
        Write-Host $msg
        Write-EQ12Log $msg
    }

    Write-Host "Watcher started on $Folder" -ForegroundColor Cyan
}
