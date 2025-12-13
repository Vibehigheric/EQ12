Imports System.Net.NetworkInformation
Imports System.Net.Sockets

Public Class NetworkManager
    Public Class AdapterInfo
        Public Property Name As String
        Public Property Description As String
        Public Property Status As String
        Public Property IPAddresses As List(Of String)
        Public Property Gateway As String
    End Class

    Public Shared Function GetAdapters() As List(Of AdapterInfo)
        Dim adapters As New List(Of AdapterInfo)
        
        For Each nic As NetworkInterface In NetworkInterface.GetAllNetworkInterfaces()
            Dim info As New AdapterInfo With {
                .Name = nic.Name,
                .Description = nic.Description,
                .Status = nic.OperationalStatus.ToString(),
                .IPAddresses = New List(Of String)()
            }

            Dim ipProps = nic.GetIPProperties()
            
            ' Get IPs
            For Each ip In ipProps.UnicastAddresses
                If ip.Address.AddressFamily = AddressFamily.InterNetwork Then
                    info.IPAddresses.Add(ip.Address.ToString())
                End If
            Next

            ' Get Gateway
            If ipProps.GatewayAddresses.Count > 0 Then
                info.Gateway = ipProps.GatewayAddresses(0).Address.ToString()
            Else
                info.Gateway = "N/A"
            End If

            adapters.Add(info)
        Next
        
        Return adapters
    End Function

    Public Shared Sub ShowNetworkStatus()
        Console.WriteLine()
        Console.WriteLine("🌐 EQ12 Network Status")
        Console.WriteLine("======================")
        
        Dim adapters = GetAdapters()
        For Each adapter In adapters
            Dim statusIcon = If(adapter.Status = "Up", "🟢", "🔴")
            Console.WriteLine($"{statusIcon} {adapter.Name} ({adapter.Description})")
            Console.WriteLine($"   Status:  {adapter.Status}")
            Console.WriteLine($"   IPs:     {String.Join(", ", adapter.IPAddresses)}")
            Console.WriteLine($"   Gateway: {adapter.Gateway}")
            Console.WriteLine()
        Next
    End Sub
End Class
