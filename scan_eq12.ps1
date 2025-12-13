# Scan C:\EQ12 and produce a report
# Run: powershell -ExecutionPolicy Bypass -File C:\EQ12\scan_eq12.ps1
# (Run as Administrator if you need to inspect protected locations)

$folder = 'C:\EQ12'
$report = Join-Path $folder 'scan_report.txt'

if (-not (Test-Path $folder)) {
    Write-Host "Folder $folder not found"
    exit 1
}

"Scan report for $folder - $(Get-Date)" | Out-File $report -Encoding utf8
"" | Out-File $report -Append

# List files with basic metadata
Get-ChildItem -Path $folder -Force | Select-Object Name, Length, @{Name='LastWriteTime';Expression={$_.LastWriteTime}} | Format-Table | Out-String | Out-File -Append $report

"" | Out-File $report -Append
# Compute SHA256 for files (skip directories)
Get-ChildItem -Path $folder -File -Force | ForEach-Object {
    $hash = Get-FileHash -Path $_.FullName -Algorithm SHA256
    "{0}  {1}  {2}" -f $_.Name, $_.Length, $hash.Hash | Out-File -Append $report
}

"" | Out-File $report -Append
# Show heads of common files we expect
$prompt = Join-Path $folder 'EQ12_master_copilot_prompt.txt'
$readme = Join-Path $folder 'README_EQ12_PROMPT.md'

if (Test-Path $prompt) {
    "---- Start: EQ12_master_copilot_prompt.txt (first 40 lines) ----" | Out-File -Append $report
    Get-Content -Path $prompt -TotalCount 40 | Out-File -Append $report
    "---- End: EQ12_master_copilot_prompt.txt ----" | Out-File -Append $report
}

if (Test-Path $readme) {
    "---- Start: README_EQ12_PROMPT.md (first 40 lines) ----" | Out-File -Append $report
    Get-Content -Path $readme -TotalCount 40 | Out-File -Append $report
    "---- End: README_EQ12_PROMPT.md ----" | Out-File -Append $report
}

# Final summary
"" | Out-File -Append $report
"Report generated: $report" | Out-File -Append $report

# Show quick preview on console
Write-Host "Report written to: $report"
Write-Host "Preview (first 30 lines):"
Get-Content -Path $report -TotalCount 30 | ForEach-Object { Write-Host $_ }

exit 0
