<#
eq12_analyze.ps1
Analyzes C:\EQ12 for large files, venvs, node_modules, git repos and produces analysis_report.txt.
Run:
  powershell -ExecutionPolicy Bypass -File C:\EQ12\eq12_analyze.ps1
No destructive actions are taken. Use eq12_cleanup.ps1 (not created unless you ask) for removals/archiving.
#>

$ErrorActionPreference = 'Stop'
$folder = 'C:\EQ12'
$report = Join-Path $folder 'analysis_report.txt'

if (-not (Test-Path $folder)) {
    Write-Host "Folder $folder not found"
    exit 1
}

"EQ12 Analysis Report - $(Get-Date)" | Out-File $report -Encoding utf8
"Folder: $folder" | Out-File -Append $report
"" | Out-File -Append $report

# Summary counts
$totalFiles = (Get-ChildItem -Path $folder -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object).Count
$totalSize = (Get-ChildItem -Path $folder -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
"Total files: $totalFiles" | Out-File -Append $report
"Total size (MB): $([math]::Round($totalSize/1MB,2))" | Out-File -Append $report
"" | Out-File -Append $report

# Top 50 largest files
"Top 50 largest files:" | Out-File -Append $report
Get-ChildItem -Path $folder -Recurse -File -Force -ErrorAction SilentlyContinue |
    Sort-Object Length -Descending |
    Select-Object -First 50 | ForEach-Object {
        $mb = [math]::Round($_.Length/1MB,2)
        "{0,-8} MB  {1}  {2}" -f $mb, $_.FullName, $_.LastWriteTime | Out-File -Append $report
    }

"" | Out-File -Append $report
# Top-level directory sizes (non-recursive list of directories)
"Top-level directory sizes (MB):" | Out-File -Append $report
Get-ChildItem -Path $folder -Directory -Force | ForEach-Object {
    $size = (Get-ChildItem -Path $_.FullName -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    "{0,-8} MB  {1}" -f ([math]::Round($size/1MB,2)), $_.FullName | Out-File -Append $report
}

"" | Out-File -Append $report
# Virtualenv detection and sizes
"Virtual environments (.ven* folders) and sizes:" | Out-File -Append $report
Get-ChildItem -Path $folder -Force -Directory -Filter ".ven*" | ForEach-Object {
    $size = (Get-ChildItem -Path $_.FullName -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    "{0,-8} MB  {1}" -f ([math]::Round($size/1MB,2)), $_.FullName | Out-File -Append $report
}

"" | Out-File -Append $report
# node_modules detection
"Top node_modules directories (by size):" | Out-File -Append $report
Get-ChildItem -Path $folder -Recurse -Directory -Force -ErrorAction SilentlyContinue | Where-Object { $_.Name -ieq 'node_modules' } | ForEach-Object {
    $size = (Get-ChildItem -Path $_.FullName -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    "{0,-8} MB  {1}" -f ([math]::Round($size/1MB,2)), $_.FullName | Out-File -Append $report
}

"" | Out-File -Append $report
# Git repository checks (if git available)
"Git repo size hints (top 5 largest objects) - requires git on PATH:" | Out-File -Append $report
if (Get-Command git -ErrorAction SilentlyContinue) {
    Get-ChildItem -Path $folder -Recurse -Directory -Force -ErrorAction SilentlyContinue | Where-Object { Test-Path (Join-Path $_.FullName '.git') } | ForEach-Object {
        $repo = $_.FullName
        "-- Repo: $repo" | Out-File -Append $report
        try {
            Push-Location $repo
            # best-effort: list 10 largest objects in history
            $gitLarge = git rev-list --objects --all 2>$null | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' 2>$null | Where-Object { $_ -match '\d' } | Sort-Object {[int]($_ -split '\s+' | Select-Object -Last 2 | Select -First 1)} -Descending
            if ($gitLarge) {
                $gitLarge | Select-Object -First 5 | Out-File -Append $report
            } else {
                "  (git listing unavailable or repository small)" | Out-File -Append $report
            }
        } catch {
            "  (error running git: $_)" | Out-File -Append $report
        } finally {
            Pop-Location
        }
    }
} else {
    "git not found on PATH - skipping git object analysis" | Out-File -Append $report
}

"" | Out-File -Append $report
# Duplicate file detection by SHA256 (best-effort, may be slow) - limited to files > 1MB and top 100 by size
"Duplicate large files (SHA256) - best-effort (files >1MB):" | Out-File -Append $report
$largeFiles = Get-ChildItem -Path $folder -Recurse -File -Force -ErrorAction SilentlyContinue | Where-Object { $_.Length -gt 1MB } | Sort-Object Length -Descending | Select-Object -First 100
if ($largeFiles.Count -gt 0) {
    $hashMap = @{}
    foreach ($f in $largeFiles) {
        try {
            $h = (Get-FileHash -Path $f.FullName -Algorithm SHA256 -ErrorAction SilentlyContinue).Hash
            if ($h) {
                if (-not $hashMap.ContainsKey($h)) { $hashMap[$h] = @() }
                $hashMap[$h] += $f.FullName
            }
        } catch {
            # skip
        }
    }
    foreach ($k in $hashMap.Keys) {
        if ($hashMap[$k].Count -gt 1) {
            "Duplicate set (SHA256: $k):" | Out-File -Append $report
            $hashMap[$k] | ForEach-Object { "  $_" | Out-File -Append $report }
        }
    }
} else {
    "No large files found for duplicate check." | Out-File -Append $report
}

"" | Out-File -Append $report
# Recommendations
"Recommendations:" | Out-File -Append $report
"- Consider archiving or removing unused virtual envs (.venv, .venv_new) if they are not needed." | Out-File -Append $report
"- Check large files listed above and remove or archive any build artifacts, installers (e.g., large .zip/.exe), or duplicates." | Out-File -Append $report
"- If node_modules found and not needed, consider running 'npm prune' or removing them for archival." | Out-File -Append $report
"- If git repos are large, consider using 'git gc' and 'git filter-repo' to remove big historical files (careful - backup first)." | Out-File -Append $report
"- If you want, I can generate a non-destructive cleanup plan (archive to zip, move to D:\archive, or safely remove)." | Out-File -Append $report

"" | Out-File -Append $report
"Analysis complete. Report: $report" | Out-File -Append $report

Write-Host "Analysis written to: $report"
Get-Content -Path $report -TotalCount 40 | ForEach-Object { Write-Host $_ }

exit 0
