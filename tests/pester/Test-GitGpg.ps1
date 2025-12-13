# Pester stub for Git/GPG setup
# This is a placeholder. If Pester is available in CI, these tests will run.
Describe 'Git/GPG configuration' {
    It 'should have git installed' {
        (Get-Command git -ErrorAction SilentlyContinue) | Should -Not -BeNullOrEmpty
    }
}
