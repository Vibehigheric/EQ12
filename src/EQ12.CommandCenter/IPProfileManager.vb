Imports System.Diagnostics

Public Class IPProfileManager
    Public Shared Sub ApplyProfile(profileName As String)
        Console.WriteLine($"🔄 Applying Network Profile: {profileName}...")
        
        ' Mock Logic: In a real app, this would use 'netsh' commands
        Select Case profileName.ToLower()
            Case "cluster"
                ' Set static IP for Cluster communication
                RunNetsh("interface ip set address ""Ethernet"" static 192.168.100.2 255.255.255.0 192.168.100.1")
                Console.WriteLine("✅ Switched to Cluster Network (192.168.100.x)")
            
            Case "home"
                ' Set DHCP for Home internet
                RunNetsh("interface ip set address ""Ethernet"" dhcp")
                Console.WriteLine("✅ Switched to Home Network (DHCP)")
            
            Case "vpn_tokyo"
                Console.WriteLine("✅ VPN Profile 'Tokyo' Activated (Mock)")
                
            Case Else
                Console.WriteLine($"❌ Unknown Profile: {profileName}")
        End Select
    End Sub

    Private Shared Sub RunNetsh(arguments As String)
        ' For safety in this demo, we just print the command instead of executing it
        ' preventing accidental network disconnection during dev.
        Console.WriteLine($"[CMD] netsh {arguments}")
        
        ' Real code:
        ' Dim psi As New ProcessStartInfo("netsh", arguments) With {
        '     .Verb = "runas", ' Requires Admin
        '     .UseShellExecute = True,
        '     .WindowStyle = ProcessWindowStyle.Hidden
        ' }
        ' Process.Start(psi)?.WaitForExit()
    End Sub
End Class
