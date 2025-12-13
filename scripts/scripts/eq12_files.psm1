
# eq12_files.psm1 - file explorer helpers
$global:EQ12_FileWatches = @{}

function Start-WatchFolder {
    [CmdletBinding()]
    param([Parameter(Mandatory=$true)][string]$Path,[ScriptBlock]$Action,[string]$Name="EQ12Watch")
    if (-not (Test-Path $Path)) { throw "Path not found: $Path" }
    $fsw = New-Object System.IO.FileSystemWatcher $Path -Property @{ IncludeSubdirectories = $true; NotifyFilter = [System.IO.NotifyFilters]'FileName, LastWrite, Size, DirectoryName' }
    $onCreated = Register-ObjectEvent -InputObject $fsw -EventName Created -SourceIdentifier "$Name-Create" -Action { param($sender,$e) & $Action $e }
    $onChanged = Register-ObjectEvent -InputObject $fsw -EventName Changed -SourceIdentifier "$Name-Change" -Action { param($sender,$e) & $Action $e }
    $onDeleted = Register-ObjectEvent -InputObject $fsw -EventName Deleted -SourceIdentifier "$Name-Delete" -Action { param($sender,$e) & $Action $e }
    $onRenamed = Register-ObjectEvent -InputObject $fsw -EventName Renamed -SourceIdentifier "$Name-Rename" -Action { param($sender,$e) & $Action $e }
    $fsw.EnableRaisingEvents = $true
    $global:EQ12_FileWatches[$Name] = @{ Watcher = $fsw; Events = @($onCreated,$onChanged,$onDeleted,$onRenamed) }
    Write-Output "Started watch '$Name' on $Path"
}

function Stop-WatchFolder { param([Parameter(Mandatory=$true)][string]$Name) if ($global:EQ12_FileWatches.ContainsKey($Name)) { $entry = $global:EQ12_FileWatches[$Name]; foreach ($ev in $entry.Events) { Unregister-Event -SourceIdentifier $ev.Name -ErrorAction SilentlyContinue }; $entry.Watcher.EnableRaisingEvents = $false; $entry.Watcher.Dispose(); $global:EQ12_FileWatches.Remove($Name) | Out-Null; Write-Output "Stopped watch $Name" } else { Write-Warning "Watch not found: $Name" } }

function eq12-files { param([string]$Path="C:\") Get-ChildItem -Path $Path -Force | Select-Object Mode, LastWriteTime, Length, Name }

function eq12-preview { param([Parameter(Mandatory=$true)][string]$File) if (-not (Test-Path $File)) { throw "File not found: $File" } $ext = [io.path]::GetExtension($File).ToLowerInvariant(); switch ($ext) { '.txt' { Get-Content -Path $File -TotalCount 200 } '.log' { Get-Content -Path $File -Tail 200 } '.json' { Get-Content $File -Raw | ConvertFrom-Json | Out-String } default { Write-Output "Preview not supported for $ext." } } }

Export-ModuleMember -Function Start-WatchFolder,Stop-WatchFolder,eq12-files,eq12-preview
