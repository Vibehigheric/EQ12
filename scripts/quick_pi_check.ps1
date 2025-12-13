# Quick Pi Setup Verification Script

Write-Host " EQ12 Raspberry Pi Setup Verification" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Test connectivity to common Pi addresses
$potentialIPs = @("192.168.1.200", "192.168.1.100", "192.168.1.150", "192.168.1.201")

Write-Host "`n Testing Pi connectivity..." -ForegroundColor Yellow

foreach ($ip in $potentialIPs) {
    Write-Host "Testing $ip..." -NoNewline
    $test = Test-NetConnection -ComputerName $ip -Port 22 -WarningAction SilentlyContinue
    
    if ($test.TcpTestSucceeded) {
        Write-Host "  SSH Available!" -ForegroundColor Green
        Write-Host " Found your Pi at: $ip" -ForegroundColor Green
        
        # Run automated setup
        Write-Host "`n Starting automated integration..." -ForegroundColor Cyan
        & "C:\EQ12\scripts\eq12_pi_integration_setup.ps1" -PiIPAddress $ip -PiPassword "raspberry" -AutoSetup
        break
    } else {
        Write-Host "  Not accessible" -ForegroundColor Red
    }
}

Write-Host "`n If no Pi found, complete these steps on your Pi:" -ForegroundColor Yellow
Write-Host "1. sudo systemctl enable ssh && sudo systemctl start ssh" -ForegroundColor White
Write-Host "2. Set static IP to 192.168.1.200" -ForegroundColor White
Write-Host "3. sudo reboot" -ForegroundColor White
Write-Host "4. Run this script again" -ForegroundColor White

Write-Host "`n Setup Status Dashboard: C:\EQ12\dashboard\raspberry_pi_setup_status.html" -ForegroundColor Cyan
