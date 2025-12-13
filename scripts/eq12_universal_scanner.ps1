
param(
    [string[]]$Paths = @(
        "C:\EQ12",
        "C:\EQ12_BACKUP_20251127_110157",
        "C:\EQ12_BROKEN_20251122_210342",
        "C:\EQ12_v2",
        "C:\llama_test",
        "C:\scripts",
        "C:\Power_On_and_WOL",
        "C:\logs",
        "C:\local",
        "C:\.github"
    )
)

$report = @()
$interestingPatterns = @("*.py", "*.ps1", "*.json", "*.yaml", "*.yml", "*.bat", "*.sh", "*.db")

foreach ($path in $Paths) {
    if (Test-Path $path) {
        Write-Host "Scanning $path..." -ForegroundColor Cyan
        
        # Get interesting files
        $files = Get-ChildItem -Path $path -Recurse -Depth 2 -Include $interestingPatterns -ErrorAction SilentlyContinue
        
        foreach ($file in $files) {
            # Categorize based on name/content hints
            $category = "Misc"
            if ($file.Name -match "orchestrat|manage|control") { $category = "Orchestration" }
            elseif ($file.Name -match "nba|nfl|bet|parlay|odds") { $category = "Betting" }
            elseif ($file.Name -match "wol|wake|power|boot") { $category = "Infrastructure" }
            elseif ($file.Name -match "llama|gpt|ai|model|infer") { $category = "AI/LLM" }
            elseif ($file.Name -match "deploy|setup|install|config") { $category = "Deployment" }
            elseif ($file.Name -match "monitor|log|watch") { $category = "Monitoring" }
            elseif ($file.Name -match "inventory|stock|sales") { $category = "Business" }

            $report += [PSCustomObject]@{
                SourcePath   = $path
                FileName     = $file.Name
                FullPath     = $file.FullName
                Category     = $category
                SizeKB       = [math]::Round($file.Length / 1KB, 2)
                LastModified = $file.LastWriteTime
            }
        }
    }
    else {
        Write-Host "Path not found: $path" -ForegroundColor Yellow
    }
}

# Group by Category and select top items
$grouped = $report | Group-Object Category
foreach ($g in $grouped) {
    Write-Host "`n=== $($g.Name) ($($g.Count) files) ===" -ForegroundColor Green
    $g.Group | Sort-Object LastModified -Descending | Select-Object -First 5 | Format-Table FileName, SourcePath, SizeKB
}

# Export full list for analysis
$report | Export-Csv -Path "C:\EQ12_BROKEN_20251122_210342\reports\universal_scan_results.csv" -NoTypeInformation
Write-Host "`nFull report saved to C:\EQ12_BROKEN_20251122_210342\reports\universal_scan_results.csv"
