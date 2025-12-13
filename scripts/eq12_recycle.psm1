
# eq12_recycle.psm1 - EQ12 Recycle Bin + Browser/Data Hygiene
$RecycleLog = "C:\EQ12\logs\recycle.log"
function Write-RecycleLog {
    param([string]$Message)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$ts - $Message" | Out-File -FilePath $RecycleLog -Append -Encoding UTF8
}

function Get-RecycleItems {
    [CmdletBinding()]
    $shell = New-Object -ComObject Shell.Application
    $recycle = $shell.Namespace(0xA)
    if (-not $recycle) { throw "Cannot access Recycle Bin" }
    $i = 0
    $recycle.Items() | ForEach-Object {
        [PSCustomObject]@{
            Index        = $i
            Name         = $recycle.GetDetailsOf($_,0)
            OriginalPath = $recycle.GetDetailsOf($_,1)
            DeletionDate = $recycle.GetDetailsOf($_,2)
            Size         = $recycle.GetDetailsOf($_,3)
        }
        $i++
    }
}

function Show-Recycle {
    [CmdletBinding()]
    param([int]$RecentDays = 0)
    $items = Get-RecycleItems
    if ($RecentDays -gt 0) {
        $cutoff = (Get-Date).AddDays(-$RecentDays)
        $items = $items | Where-Object {
            try { [datetime]$_.DeletionDate -ge $cutoff } catch { $true }
        }
    }
    if ($items) { $items | Format-Table -AutoSize } else { Write-Output "Recycle Bin empty." }
}

function Export-RecycleReport {
    [CmdletBinding()]
    param(
        [ValidateSet('json','csv','text')] [string]$Format='json',
        [string]$Path="C:\EQ12\logs\recycle_report.$Format"
    )
    if (-not (Test-Path (Split-Path $Path))) { New-Item -ItemType Directory -Path (Split-Path $Path) -Force | Out-Null }
    $items = Get-RecycleItems
    switch ($Format) {
        'json' { $items | ConvertTo-Json -Depth 5 | Out-File $Path -Encoding UTF8 }
        'csv'  { $items | Export-Csv -Path $Path -NoTypeInformation -Force }
        'text' { $items | Out-String | Out-File $Path -Encoding UTF8 }
    }
    return $Path
}

function Remove-SafeItem {
    [CmdletBinding()]
    param([Parameter(Mandatory=$true,ValueFromPipeline=$true)][string[]]$Path)
    process {
        foreach ($p in $Path) {
            try {
                $code = @"
using System;
using System.Runtime.InteropServices;
public class RecycleHelper {
  [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)]
  public struct SHFILEOPSTRUCT {
    public IntPtr hwnd; public UInt32 wFunc; public string pFrom; public string pTo;
    public UInt16 fFlags; public bool fAnyOperationsAborted; public IntPtr hNameMappings;
    public string lpszProgressTitle;
  }
  [DllImport("shell32.dll", CharSet=CharSet.Unicode)]
  public static extern int SHFileOperation(ref SHFILEOPSTRUCT lpFileOp);
  public static int DeleteToRecycle(string path) {
    SHFILEOPSTRUCT fs = new SHFILEOPSTRUCT();
    fs.wFunc = 3; fs.pFrom = path + char.MinValue + char.MinValue; fs.fFlags = 0x0004 + 0x0010;
    return SHFileOperation(ref fs);
  }
}
"@
                Add-Type -TypeDefinition $code -ErrorAction SilentlyContinue
                $ret = [RecycleHelper]::DeleteToRecycle($p)
                if ($ret -eq 0) { Write-Output "Moved to Recycle: $p" }
                else { Write-Warning "Recycle move returned $ret for $p" }
            } catch {
                Write-Warning "Safe-Remove fallback: deleting $p"
                Remove-Item -LiteralPath $p -Recurse -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

function Send-Telegram {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)] [string]$Message,
        [string]$TokenPath="C:\EQ12\keys\tg_token.txt",
        [string]$ChatIdPath="C:\EQ12\keys\tg_chatid.txt"
    )
    if (-not (Test-Path $TokenPath) -or -not (Test-Path $ChatIdPath)) { Write-Warning "Telegram keys missing"; return $false }
    $token=(Get-Content $TokenPath).Trim(); $chat=(Get-Content $ChatIdPath).Trim()
    $uri="https://api.telegram.org/bot$token/sendMessage"
    try {
        Invoke-RestMethod -Method Post -Uri $uri -Body @{chat_id=$chat;text=$Message}
        return $true
    } catch { Write-Warning "Telegram send failed: $($_.Exception.Message)"; return $false }
}

function Save-TelegramKeys {
    [CmdletBinding()]
    param([string]$Token,[string]$ChatId)
    if (-not (Test-Path "C:\EQ12\keys")) { New-Item -ItemType Directory -Path "C:\EQ12\keys" -Force | Out-Null }
    $Token | Out-File "C:\EQ12\keys\tg_token.txt" -Encoding ascii
    $ChatId | Out-File "C:\EQ12\keys\tg_chatid.txt" -Encoding ascii
    Write-Output "Saved Telegram keys."
}

function Clear-BrowserData {
    [CmdletBinding()]
    param([switch]$Chrome,[switch]$Edge,[switch]$Firefox)
    Write-RecycleLog "=== EQ12 Browser Clear Start ==="
    if ($Chrome) {
        try {
            $c="$env:LOCALAPPDATA\Google\Chrome\User Data\Default"
            if (Test-Path $c) {
                Remove-Item "$c\History","$c\Cookies" -ErrorAction SilentlyContinue
                Write-RecycleLog "Chrome data cleared"
            }
        } catch { Write-RecycleLog "Chrome clear error: $($_.Exception.Message)" }
    }
    if ($Edge) {
        try {
            $e="$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default"
            if (Test-Path $e) {
                Remove-Item "$e\History","$e\Cookies" -ErrorAction SilentlyContinue
                Write-RecycleLog "Edge data cleared"
            }
        } catch { Write-RecycleLog "Edge clear error: $($_.Exception.Message)" }
    }
    if ($Firefox) {
        try {
            $ffProfile = "C:\EQ12\profiles\firefox-bot"
            $ffCache = Join-Path $ffProfile 'cache2'
            $ffStartupCache = Join-Path $ffProfile 'startupCache'
            $ffCookies = Join-Path $ffProfile 'cookies.sqlite'
            $ffHistory = Join-Path $ffProfile 'places.sqlite'
            if (Test-Path $ffCache) { Remove-Item $ffCache -Recurse -Force -ErrorAction SilentlyContinue }
            if (Test-Path $ffStartupCache) { Remove-Item $ffStartupCache -Recurse -Force -ErrorAction SilentlyContinue }
            if (Test-Path $ffCookies) { Remove-Item $ffCookies -Force -ErrorAction SilentlyContinue }
            if (Test-Path $ffHistory) { Remove-Item $ffHistory -Force -ErrorAction SilentlyContinue }
            Write-RecycleLog "Firefox data cleared in $ffProfile"
        } catch { Write-RecycleLog "Firefox clear error: $($_.Exception.Message)" }
    }
    Write-RecycleLog "=== EQ12 Browser Clear Done ==="
}

Export-ModuleMember -Function Show-Recycle,Export-RecycleReport,Remove-SafeItem,Send-Telegram,Save-TelegramKeys,Clear-BrowserData,Get-RecycleItems
