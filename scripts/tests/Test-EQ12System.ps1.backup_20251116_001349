# EQ12 System Integration Test

# Reload profile to ensure all functions are available
. $PROFILE

# Run the full elite process
Write-Host "\n=== Running eq12-elite-run ==="
eq12-elite-run

Write-Host "\n=== Running eq12-build-dashboard ==="
eq12-build-dashboard

Write-Host "\n=== Verifying dashboard content ==="
$dashboardOk = Test-EQ12Dashboard

if ($dashboardOk) {
    Write-Host "\n✅ EQ12 System Test PASSED: All dashboard sections present."
    exit 0
} else {
    Write-Host "\n❌ EQ12 System Test FAILED: Dashboard missing sections."
    exit 1
}
