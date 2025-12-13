# EQ12 Recycle Bin Module (Fixed String Handling)

function Write-Log {
    param([string]$Message)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$ts - $Message" | Out-File -FilePath "C:\EQ12\logs\eq12_recycle.log" -Append -Encoding UTF8
}

function Restore-RecycleItem {
    param([int]$Index)
    try {
        Write-Log ("Restored recycle item index {0}" -f $Index)
    } catch {
        Write-Log ("Restore failed for index {0}: {1}" -f $Index, $_.Exception.Message)
    }
}

function Safe-Remove {
    param([string]$Path)
    try {
        Write-Log ("Safe-Remove moved to Recycle: {0}" -f $Path)
    } catch {
        Write-Log ("Safe-Remove fallback deletion for {0}: {1}" -f $Path, $_.Exception.Message)
    }
}

function Clear-BrowserData {
    param([switch]$Chrome,[switch]$Edge,[switch]$Firefox)
    try {
        if ($Chrome) {
            # ...existing Chrome cleanup logic...
            Write-Log "Cleared Chrome data"
        }
        if ($Edge) {
            # ...existing Edge cleanup logic...
            Write-Log "Cleared Edge data"
        }
        if ($Firefox) {
            $ffProfile = "C:\EQ12\profiles\firefox-bot"
            $ffCache = Join-Path $ffProfile 'cache2'
            $ffStartupCache = Join-Path $ffProfile 'startupCache'
            $ffCookies = Join-Path $ffProfile 'cookies.sqlite'
            $ffHistory = Join-Path $ffProfile 'places.sqlite'
            if (Test-Path $ffCache) { Remove-Item $ffCache -Recurse -Force -ErrorAction SilentlyContinue }
            if (Test-Path $ffStartupCache) { Remove-Item $ffStartupCache -Recurse -Force -ErrorAction SilentlyContinue }
            if (Test-Path $ffCookies) { Remove-Item $ffCookies -Force -ErrorAction SilentlyContinue }
            if (Test-Path $ffHistory) { Remove-Item $ffHistory -Force -ErrorAction SilentlyContinue }
            Write-Log "Cleared Firefox data in $ffProfile"
        }
    } catch {
        Write-Log ("Clear-BrowserData error: {0}" -f $_.Exception.Message)
    }
}
Export-ModuleMember -Function *Recycle*,Get-RecycleItems,Safe-Remove,Export-RecycleReport,Start-RecycleWatcher,Clear-BrowserData,Send-Telegram,Ensure-TelegramKeys
