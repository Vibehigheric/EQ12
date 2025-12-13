[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$JsonPath,
    [Parameter(Mandatory=$false)]
    [string]$CsvPath
)

# Reads a JSON snapshot, validates structure, optionally exports CSV.
Write-Host "Dashboard helper: reading $JsonPath"
$json = Get-Content $JsonPath -Raw | ConvertFrom-Json
if (-not $json.PSObject.Properties.Name -contains 'ok') {
    Write-Error "Snapshot missing 'ok' field"
    return
}

# TODO: export as JSON for dashboard -> ensure consistent path and structure
if ($PSBoundParameters.ContainsKey('CsvPath') -eq $false) {
    $defaultJsonOut = Join-Path -Path (Split-Path -Path $JsonPath -Parent) -ChildPath "dashboard_latest.json"
    try {
        $json | ConvertTo-Json -Depth 6 | Out-File -FilePath $defaultJsonOut -Encoding utf8 -Force
        Write-Host "Wrote dashboard JSON to $defaultJsonOut"
    } catch {
        Write-Warning "Failed to write dashboard JSON: $_"
    }
}

if ($CsvPath) {
    try {
        $data = $json.data | ConvertTo-Json -Depth 5 | ConvertFrom-Json
        $csv = $data | ConvertTo-Csv -NoTypeInformation
        $csv | Out-File -FilePath $CsvPath -Encoding utf8
        Write-Host "Wrote CSV to $CsvPath"
    } catch {
        Write-Warning "Could not export CSV: $_"
    }
}

Write-Host "Dashboard helper finished."