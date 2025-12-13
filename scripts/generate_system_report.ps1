
$root = "C:\EQ12_BROKEN_20251122_210342"
$reportPath = Join-Path $root "reports\eq12_system_scan_20251212.md"

$sb = New-Object System.Text.StringBuilder
[void]$sb.AppendLine("# EQ12 System Scan Report - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
[void]$sb.AppendLine("")

# Active System
[void]$sb.AppendLine("## 🚀 Active System (scripts/)")
$scripts = Get-ChildItem -Path "$root\scripts" -File
[void]$sb.AppendLine("Total Scripts: $($scripts.Count)")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("| Script Name | Size (KB) | Last Modified |")
[void]$sb.AppendLine("|---|---|---|")
foreach ($s in $scripts | Sort-Object LastWriteTime -Descending | Select-Object -First 10) {
    $size = [math]::Round($s.Length / 1KB, 2)
    [void]$sb.AppendLine("| $($s.Name) | $size | $($s.LastWriteTime) |")
}
[void]$sb.AppendLine("*(Top 10 most recently modified)*")
[void]$sb.AppendLine("")

# Legacy Swarm
[void]$sb.AppendLine("## 🏛️ Legacy Swarm (legacy_swarm/)")
if (Test-Path "$root\legacy_swarm") {
    $categories = Get-ChildItem -Path "$root\legacy_swarm" -Directory
    foreach ($cat in $categories) {
        $count = (Get-ChildItem -Path $cat.FullName -Recurse -File).Count
        [void]$sb.AppendLine("- **$($cat.Name)**: $count files")
    }
}
else {
    [void]$sb.AppendLine("Legacy Swarm folder not found.")
}
[void]$sb.AppendLine("")

# Key Components Status
[void]$sb.AppendLine("## 🛠️ Key Components Status")
$components = @(
    @{ Name = "Master Orchestrator"; Path = "scripts\eq12_master_orchestrator.py" },
    @{ Name = "NBA Power Slip Generator"; Path = "scripts\nba_power_slip_generator.py" },
    @{ Name = "Inventory Manager"; Path = "scripts\loganberry_inventory_manager.py" },
    @{ Name = "Legacy NBA Intelligence"; Path = "scripts\eq12_master_nba_intelligence.py" }
)

[void]$sb.AppendLine("| Component | Status | Path |")
[void]$sb.AppendLine("|---|---|---|")
foreach ($comp in $components) {
    $fullPath = Join-Path $root $comp.Path
    $status = if (Test-Path $fullPath) { "✅ Present" } else { "❌ Missing" }
    [void]$sb.AppendLine("| $($comp.Name) | $status | $($comp.Path) |")
}

[void]$sb.AppendLine("")

# Root Directory Inventory
[void]$sb.AppendLine("## 📂 Root Directory Inventory")
[void]$sb.AppendLine("| Folder Name | Files | Size (MB) | Last Modified |")
[void]$sb.AppendLine("|---|---|---|---|")

$rootItems = Get-ChildItem -Path $root -Directory | Where-Object { $_.Name -notin @("scripts", "legacy_swarm", ".git", ".vs") }
foreach ($item in $rootItems) {
    try {
        $stats = Get-ChildItem -Path $item.FullName -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum
        $count = $stats.Count
        $sizeMB = if ($stats.Sum) { [math]::Round($stats.Sum / 1MB, 2) } else { 0 }
        [void]$sb.AppendLine("| $($item.Name) | $count | $sizeMB | $($item.LastWriteTime.ToString('yyyy-MM-dd')) |")
    }
    catch {
        [void]$sb.AppendLine("| $($item.Name) | Error | - | - |")
    }
}

[void]$sb.AppendLine("")
[void]$sb.AppendLine("## 📝 Summary")
[void]$sb.AppendLine("The system is currently operating in a hybrid mode. The `scripts/` directory contains the active, orchestrated components, while `legacy_swarm/` serves as a rich library of historical tools. The root directory contains significant other projects including `sports-betting-optimizer`, `stable-diffusion-webui`, and `web3_repos` that are currently outside the main orchestration loop.")

$sb.ToString() | Out-File -FilePath $reportPath -Encoding utf8
Write-Host "Report generated at $reportPath"
