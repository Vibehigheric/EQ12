Describe 'eq12_chatgpt wrapper' {
    $script = Join-Path $PSScriptRoot '..\..\scripts\eq12_chatgpt.ps1'
    It 'script exists' {
        Test-Path $script | Should -BeTrue
    }

    It 'prints usage when called with missing params' {
        $out = & $script 2>&1
        # Expect an error about missing mandatory parameter or nothing harmful
        $out | Should -Not -BeNullOrEmpty
    }
}
