<#
Pester tests for eq12_firefox_bookmarks.ps1

This test file uses $PSScriptRoot and Join-Path to build absolute paths so
the tests work regardless of the current working directory used by Pester.
#>

Describe 'eq12_firefox_bookmarks script' -Tags 'Integration' {
    # Compute the repository root from the test file location.
    # $PSScriptRoot -> C:\EQ12\tests\pester
    $repoRoot = Split-Path -Parent (Split-Path -Path $PSScriptRoot -Parent)

    # Build an absolute path to the script under test (expected at C:\EQ12\scripts)
    $scriptPathCandidate = Join-Path -Path $repoRoot -ChildPath 'scripts\\eq12_firefox_bookmarks.ps1'
    if (Test-Path -Path $scriptPathCandidate) { $scriptPath = $scriptPathCandidate } else { $scriptPath = $null }

    It 'script file exists in repository scripts folder' {
        Test-Path -Path $scriptPath | Should -Be $true -Because "Test expects the script file to be present at $scriptPathCandidate"
    }

    Context 'When dot-sourced' {
        BeforeAll {
            if (-not $scriptPath) { Throw "Test cannot continue: script not found at $scriptPathCandidate" }
            # Dot-source the script into the current scope so functions become available
            Describe 'eq12_firefox_bookmarks script' -Tags 'Integration' {
                # This block runs once before any tests in this Describe block.
                # It ensures the script path is valid and accessible and dot-sources it.
                BeforeAll {
                    # repo root is parent of the tests folder (two levels up from tests\pester)
                    $repoRoot = [System.IO.Path]::GetDirectoryName([System.IO.Path]::GetDirectoryName($PSScriptRoot))
                    $scriptPath = Join-Path $repoRoot 'scripts\eq12_firefox_bookmarks.ps1'

                    if (-not (Test-Path -Path $scriptPath)) {
                        throw "Test cannot continue: script not found at '$scriptPath'"
                    }

                    # Dot-source the script once for all tests in this Describe block
                    . $scriptPath
                }

                Context 'script file exists' {
                    It 'should be present in repository scripts folder' {
                        Test-Path $scriptPath | Should -Be $true
                    }
                }

                Context 'When dot-sourced' {
                    It 'exports Get-EQ12FirefoxBookmarks function' {
                        (Get-Command -Name Get-EQ12FirefoxBookmarks -CommandType Function -ErrorAction SilentlyContinue) | Should -Not -BeNullOrEmpty
                    }

                    It 'calling function returns a non-empty result in DryRun' {
                        # If the function requires parameters, update this call accordingly.
                        $result = Get-EQ12FirefoxBookmarks -DryRun
                        $result | Should -Not -BeNullOrEmpty
                    }
                }
            }
}
