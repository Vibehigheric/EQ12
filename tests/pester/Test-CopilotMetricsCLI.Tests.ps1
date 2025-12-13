Describe "Copilot Metrics CLI wiring" {
    BeforeAll {
        $repoRoot = (Get-Item -LiteralPath $PSScriptRoot).Parent.Parent.FullName
        $Global:CliFile = Join-Path $repoRoot 'EQ12CliMainProgram.vb'
        $Global:ClientFile = Join-Path $repoRoot 'CopilotMetricsClient.vb'
        $Global:ExtensionFile = Join-Path $repoRoot 'Eq12CliGitHubExtensionEnhanced.vb'
    }

    It "documents metrics commands in the CLI dispatcher" {
        $cliContent = Get-Content -Path $Global:CliFile -Raw
        $cliContent | Should -Match 'metrics-sync'
        $cliContent | Should -Match 'metrics-report'
        $cliContent | Should -Match 'metrics-diff'
    }

    It "includes the CopilotMetricsClient type" {
        (Test-Path $Global:ClientFile) | Should -BeTrue
        $clientContent = Get-Content -Path $Global:ClientFile -Raw
        $clientContent | Should -Match 'Class CopilotMetricsClient'
        $clientContent | Should -Match 'X-GitHub-Api-Version'
    }

    It "writes Copilot metrics output to logs" {
        $extensionContent = Get-Content -Path $Global:ExtensionFile -Raw
        $extensionContent | Should -Match 'Copilot metrics saved to'
        $extensionContent | Should -Match 'Copilot metrics report saved to'
    }
}
