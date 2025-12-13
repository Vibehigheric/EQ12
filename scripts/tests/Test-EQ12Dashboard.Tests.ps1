# EQ12 Dashboard Pester Tests
Describe "EQ12 Dashboard Generation" {
    $dashboardPath = "C:\EQ12\dashboard\index.html"

    It "Should create the dashboard file" {
        # Run the dashboard builder script
        & "C:\EQ12\scripts\eq12_build_dashboard.ps1"
        Test-Path $dashboardPath | Should -Be $true
    }

    It "Should contain the Stocks section" {
        (Select-String -Path $dashboardPath -Pattern "Stocks").Count | Should -BeGreaterThan 0
    }
    It "Should contain the Crypto section" {
        (Select-String -Path $dashboardPath -Pattern "Crypto").Count | Should -BeGreaterThan 0
    }
    It "Should contain the Sports Odds section" {
        (Select-String -Path $dashboardPath -Pattern "Sports Odds").Count | Should -BeGreaterThan 0
    }
    It "Should contain the Jobs section" {
        (Select-String -Path $dashboardPath -Pattern "Jobs").Count | Should -BeGreaterThan 0
    }
}
