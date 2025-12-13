param(
    [string]$ManagerIP = "192.168.100.3",
    [string]$User = "ricoj100"
)

Write-Host "=== [EQ12] Cluster Monitor (Ctrl+C to exit) ===" -ForegroundColor Cyan
Write-Host "Connecting to Manager ($ManagerIP)..." -ForegroundColor Gray

# Use watch command on Linux to refresh every 2 seconds
ssh -t "$User@$ManagerIP" "watch -n 2 'docker service ps eq12 --no-trunc'"
