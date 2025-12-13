# eq12_recycle.psm1 — Polished, warning-free

function Get-RecycleItems {
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

function Get-RecycleOverview {
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

function Remove-Safely {
    param([Parameter(Mandatory=$true,ValueFromPipeline=$true)][string[]]$Path)
    process {
        foreach ($p in $Path) {
            try {
                # Move to Recycle Bin
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
                if ($ret -eq 0) { Write-Output "Moved to Recycle: $p" } else { Write-Warning "Recycle move returned $ret for $p" }
            } catch {
                Write-Warning "Fallback: deleting $p"
                Remove-Item -LiteralPath $p -Recurse -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

function Send-TelegramMessage {
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
    param([string]$Token,[string]$ChatId)
    if (-not (Test-Path "C:\EQ12\keys")) { New-Item -ItemType Directory -Path "C:\EQ12\keys" -Force | Out-Null }
    $Token | Out-File "C:\EQ12\keys\tg_token.txt" -Encoding ascii
    $ChatId | Out-File "C:\EQ12\keys\tg_chatid.txt" -Encoding ascii
    Write-Output "Saved Telegram keys."
}

function Clear-BrowserData {
    param([switch]$Chrome,[switch]$Edge,[switch]$Firefox)
    Write-Output "=== EQ12 Browser Clear Start ==="
    if ($Chrome) {
        $c="$env:LOCALAPPDATA\Google\Chrome\User Data\Default"
        if (Test-Path $c) {
            Remove-Item "$c\History","$c\Cookies" -ErrorAction SilentlyContinue
            Write-Output "Chrome data cleared"
        }
    }
    if ($Edge) {
        $e="$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default"
        if (Test-Path $e) {
            Remove-Item "$e\History","$e\Cookies" -ErrorAction SilentlyContinue
            Write-Output "Edge data cleared"
        }
    }
    if ($Firefox) {
        $f="$env:APPDATA\Mozilla\Firefox\Profiles"
        if (Test-Path $f) {
            Get-ChildItem $f -Directory | ForEach-Object {
                Remove-Item "$($_.FullName)\places.sqlite","$($_.FullName)\cookies.sqlite" -ErrorAction SilentlyContinue
            }
            Write-Output "Firefox data cleared"
        }
    }
    Write-Output "=== EQ12 Browser Clear Done ==="
}

Export-ModuleMember -Function Get-RecycleItems,Get-RecycleOverview,Export-RecycleReport,Remove-Safely,Send-TelegramMessage,Save-TelegramKeys,Clear-BrowserData
