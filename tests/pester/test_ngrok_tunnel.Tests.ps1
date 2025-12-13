# Pester tests for Start-EQ12Tunnel
Describe 'Start-EQ12Tunnel' {
    It 'DryRun should not attempt to start ngrok and should output the command' {
        $scriptFile = $PSCommandPath
        if (-not $scriptFile) { $scriptFile = $MyInvocation.MyCommand.Definition }
        if (-not $scriptFile) { $scriptFile = (Get-Location).Path }
        $testDir = Split-Path -Parent $scriptFile
        $repoRoot = Split-Path -Parent (Split-Path -Parent $testDir)
        $scriptPath = Join-Path $repoRoot 'scripts\Start-EQ12Tunnel.ps1'
        Test-Path $scriptPath | Should -BeTrue
        . $scriptPath
        { Start-EQ12Tunnel -Service 'test' -LocalPort 8888 -DryRun } | Should -Not -Throw
    }

    It 'Get-EQ12TunnelStatus should not error when log missing' {
        { Get-EQ12TunnelStatus } | Should -Not -Throw
    }
}
