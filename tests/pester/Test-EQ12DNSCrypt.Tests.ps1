Describe 'EQ12 DNSCrypt' {
    It 'Get-EQ12DNSCryptStatus returns a status object' {
        Import-Module 'C:\EQ12\scripts\eq12_dnscrypt.psm1'
        $res = Get-EQ12DNSCryptStatus
        # Ensure we got a non-empty result and expected properties exist.
        $res | Should -Not -BeNullOrEmpty
        # Accessing properties directly works for both hashtables and PSCustomObjects
        $res.status | Should -Not -BeNullOrEmpty
        $res.ts | Should -Not -BeNullOrEmpty
    }

    It 'Restart-EQ12DNSCrypt is safe when service missing' {
        Import-Module 'C:\EQ12\scripts\eq12_dnscrypt.psm1'
        # The restart function should not throw even if the service is absent.
        { Restart-EQ12DNSCrypt } | Should -Not -Throw
    }
}
