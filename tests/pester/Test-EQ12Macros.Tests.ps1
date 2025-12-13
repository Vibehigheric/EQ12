Describe 'EQ12 Macros' {
    It 'should have the EQ12Macros.xml file' {
        $macro = 'C:\EQ12\macros\EQ12Macros.xml'
        Test-Path $macro | Should -BeTrue
    }

    It 'should contain required macros' {
        $xml = [xml](Get-Content 'C:\EQ12\macros\EQ12Macros.xml')
        $names = $xml.JAMSMacros.Macro | ForEach-Object { $_.Name }
        $names | Should -Contain 'EQ12LogParameters'
        $names | Should -Contain 'EQ12RetryCommand'
        $names | Should -Contain 'EQ12BuildDashboard'
    }

}
