[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$Network = "192.168.1.0/24"
)

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "EQ12 Network Device Discovery & Identification" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Scanning network: $Network" -ForegroundColor Yellow
Write-Host ""

# Run nmap with service detection
$nmap_output = nmap -sV -A $Network 2>$null

# Parse and display results
$devices = @()
$current_device = $null

foreach ($line in $nmap_output) {
    if ($line -match "Nmap scan report for (.+)") {
        $ip = $matches[1]
        $current_device = [PSCustomObject]@{
            IPAddress = $ip
            Hostname = "N/A"
            Ports = @()
            Services = @()
            MACs = @()
            OSGuess = "Unknown"
            Vendor = "Unknown"
        }
        $devices += $current_device
    }
    
    if ($line -match "MAC Address: (.+) \((.+)\)") {
        if ($current_device) {
            $current_device.MACs += @{MAC=$matches[1]; Vendor=$matches[2]}
        }
    }
    
    if ($line -match "^(\d+)/tcp\s+(\w+)\s+(\S+)" -and $current_device) {
        $port = $matches[1]
        $state = $matches[2]
        $service = $matches[3]
        $current_device.Ports += "$port/tcp ($state)"
        $current_device.Services += $service
    }
    
    if ($line -match "OS details: (.+)$") {
        if ($current_device) {
            $current_device.OSGuess = $matches[1]
        }
    }
}

Write-Host "Found $($devices.Count) device(s)" -ForegroundColor Green
Write-Host ""

foreach ($device in $devices) {
    Write-Host "IP: $($device.IPAddress)" -ForegroundColor Cyan
    
    if ($device.MACs.Count -gt 0) {
        foreach ($mac_info in $device.MACs) {
            Write-Host "  MAC: $($mac_info.MAC) - Vendor: $($mac_info.Vendor)" -ForegroundColor Yellow
        }
    }
    
    if ($device.Services.Count -gt 0) {
        Write-Host "  Services: $($device.Services -join ', ')" -ForegroundColor Green
    }
    
    if ($device.OSGuess -ne "Unknown") {
        Write-Host "  OS: $($device.OSGuess)" -ForegroundColor Magenta
    }
    
    Write-Host ""
}

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "Device Type Guide:" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Based on MAC address vendor and services:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Askey Computer (F4:52:46:89:33:EF)" -ForegroundColor Green
Write-Host "  └─ Likely: WiFi Router/Gateway" -ForegroundColor Cyan
Write-Host ""
Write-Host "Raspberry Pi Trading (2C:CF:67:8E:13:5A)" -ForegroundColor Green
Write-Host "  └─ Confirmed: Raspberry Pi (pi-node-1)" -ForegroundColor Cyan
Write-Host ""
Write-Host "LCFC Electronics (98:FA:9B:E9:D6:99)" -ForegroundColor Green
Write-Host "  └─ Likely: Smart Home Device or IoT Device" -ForegroundColor Cyan
Write-Host ""
Write-Host "LG Innotek (A4:36:C7:37:E7:1C)" -ForegroundColor Green
Write-Host "  └─ Likely: LG Smart TV or Home Appliance" -ForegroundColor Cyan
Write-Host ""
Write-Host "TCL Moka (98:7A:9B:41:28:EA)" -ForegroundColor Green
Write-Host "  └─ Likely: TCL Smart TV or Display Device" -ForegroundColor Cyan
Write-Host ""
Write-Host "Unknown (02:0F:B5:90:77:D3)" -ForegroundColor Green
Write-Host "  └─ Could be: Virtual machine, container, or custom device" -ForegroundColor Cyan
Write-Host ""
