Describe 'EQ12 GPG integration' {
    It 'can run gpg --version' {
        $gpg = Get-Command gpg.exe -ErrorAction SilentlyContinue
        $gpg | Should -Not -BeNullOrEmpty
    }
}
