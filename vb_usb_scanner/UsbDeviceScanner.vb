''' <summary>
''' EQ12 USB Device Scanner - Complete USB port and device detection system
''' Integrates with Fetch Engine architecture for automated device discovery
''' </summary>

Imports System.Management
Imports System.Text
Imports System.Collections.Generic

Public Class UsbPortInfo
    Public Property PortNumber As String
    Public Property PortType As String ' USB 2.0, 3.0, 3.1, 3.2, Type-C
    Public Property Speed As String ' Low, Full, High, SuperSpeed, SuperSpeedPlus
    Public Property Status As String ' Connected, Available, Error
    Public Property DevicePath As String
End Class

Public Class UsbDeviceInfo
    Public Property VendorId As String
    Public Property ProductId As String
    Public Property DevicePath As String
    Public Property Manufacturer As String
    Public Property ProductName As String
    Public Property SerialNumber As String
    Public Property DeviceClass As String
    Public Property DriverVersion As String
    Public Property Speed As String
    Public Property PortType As String
    Public Property IsRemovable As Boolean
    Public Property DriveLetters As List(Of String)
End Class

Public NotInheritable Class UsbScanner

    ''' <summary>
    ''' Scan all USB devices on the system
    ''' </summary>
    Public Shared Function ScanAllUsbDevices() As List(Of UsbDeviceInfo)
        Dim devices As New List(Of UsbDeviceInfo)()

        Try
            Dim searcher As New ManagementObjectSearcher(
                "SELECT * FROM Win32_USBControllerDevice")

            For Each device As ManagementObject In searcher.Get()
                Dim dependent As String = device("Dependent").ToString()

                If dependent.Contains("VID_") AndAlso dependent.Contains("PID_") Then
                    Dim info = ParseUsbDeviceInfo(dependent)
                    If info IsNot Nothing Then
                        devices.Add(info)
                    End If
                End If
            Next
        Catch ex As Exception
            Console.WriteLine($"[ERROR] USB scan failed: {ex.Message}")
        End Try

        Return devices
    End Function

    ''' <summary>
    ''' Parse USB device information from WMI path
    ''' </summary>
    Private Shared Function ParseUsbDeviceInfo(dependentPath As String) As UsbDeviceInfo
        Try
            Dim info As New UsbDeviceInfo()

            ' Extract VID/PID
            Dim vidMatch = System.Text.RegularExpressions.Regex.Match(dependentPath, "VID_([0-9A-F]{4})")
            Dim pidMatch = System.Text.RegularExpressions.Regex.Match(dependentPath, "PID_([0-9A-F]{4})")

            If vidMatch.Success Then info.VendorId = vidMatch.Groups(1).Value
            If pidMatch.Success Then info.ProductId = pidMatch.Groups(1).Value

            info.DevicePath = dependentPath

            ' Get detailed device information
            EnrichDeviceInfo(info)

            Return info
        Catch ex As Exception
            Console.WriteLine($"[WARN] Failed to parse device: {ex.Message}")
            Return Nothing
        End Try
    End Function

    ''' <summary>
    ''' Enrich device info with WMI queries
    ''' </summary>
    Private Shared Sub EnrichDeviceInfo(ByRef info As UsbDeviceInfo)
        Try
            ' Query PnP devices for detailed information
            Dim query As String = $"SELECT * FROM Win32_PnPEntity WHERE DeviceID LIKE '%VID_{info.VendorId}%PID_{info.ProductId}%'"
            Dim searcher As New ManagementObjectSearcher(query)

            For Each device As ManagementObject In searcher.Get()
                info.Manufacturer = TryGetProperty(device, "Manufacturer")
                info.ProductName = TryGetProperty(device, "Name")
                info.DeviceClass = TryGetProperty(device, "PNPClass")
                info.DriverVersion = TryGetProperty(device, "DriverVersion")

                ' Detect USB speed from device descriptor
                Dim deviceDesc = TryGetProperty(device, "Description")
                info.Speed = DetectUsbSpeed(deviceDesc)
                info.PortType = DetectPortType(deviceDesc)
                Exit For
            Next

            ' Check if it's a storage device
            If info.DeviceClass = "DiskDrive" OrElse info.DeviceClass = "Volume" Then
                info.DriveLetters = GetDriveLetters(info.VendorId, info.ProductId)
                info.IsRemovable = True
            End If

        Catch ex As Exception
            Console.WriteLine($"[WARN] Failed to enrich device info: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Detect USB speed from device description
    ''' </summary>
    Private Shared Function DetectUsbSpeed(description As String) As String
        If String.IsNullOrEmpty(description) Then Return "Unknown"

        If description.Contains("SuperSpeed USB 20Gbps") OrElse description.Contains("USB 3.2 Gen 2x2") Then
            Return "20 Gbps (USB 3.2 Gen 2x2)"
        ElseIf description.Contains("SuperSpeed USB 10Gbps") OrElse description.Contains("USB 3.2 Gen 2") Then
            Return "10 Gbps (USB 3.2 Gen 2)"
        ElseIf description.Contains("SuperSpeed USB") OrElse description.Contains("USB 3.") Then
            Return "5 Gbps (USB 3.0/3.1 Gen 1)"
        ElseIf description.Contains("High-Speed") OrElse description.Contains("USB 2.0") Then
            Return "480 Mbps (USB 2.0)"
        ElseIf description.Contains("Full-Speed") Then
            Return "12 Mbps (USB 1.1)"
        ElseIf description.Contains("Low-Speed") Then
            Return "1.5 Mbps (USB 1.0)"
        Else
            Return "Unknown"
        End If
    End Function

    ''' <summary>
    ''' Detect port type (Type-A, Type-B, Type-C, Micro, Mini)
    ''' </summary>
    Private Shared Function DetectPortType(description As String) As String
        If String.IsNullOrEmpty(description) Then Return "Unknown"

        If description.Contains("Type-C") OrElse description.Contains("USB-C") Then
            Return "USB Type-C"
        ElseIf description.Contains("Type-B") Then
            Return "USB Type-B"
        ElseIf description.Contains("Micro") Then
            Return "USB Micro"
        ElseIf description.Contains("Mini") Then
            Return "USB Mini"
        Else
            Return "USB Type-A"
        End If
    End Function

    ''' <summary>
    ''' Get drive letters for removable USB storage
    ''' </summary>
    Private Shared Function GetDriveLetters(vid As String, pid As String) As List(Of String)
        Dim letters As New List(Of String)()

        Try
            Dim drives = IO.DriveInfo.GetDrives()
            For Each drive In drives
                If drive.DriveType = IO.DriveType.Removable OrElse drive.DriveType = IO.DriveType.Fixed Then
                    ' Simple detection - would need more sophisticated matching in production
                    If drive.IsReady Then
                        letters.Add(drive.Name)
                    End If
                End If
            Next
        Catch ex As Exception
            Console.WriteLine($"[WARN] Failed to get drive letters: {ex.Message}")
        End Try

        Return letters
    End Function

    ''' <summary>
    ''' Safe property getter for ManagementObject
    ''' </summary>
    Private Shared Function TryGetProperty(obj As ManagementObject, propertyName As String) As String
        Try
            Dim value = obj(propertyName)
            If value IsNot Nothing Then
                Return value.ToString()
            End If
        Catch
            ' Property doesn't exist
        End Try
        Return String.Empty
    End Function

    ''' <summary>
    ''' Monitor USB plug/unplug events (requires elevated permissions)
    ''' </summary>
    Public Shared Sub MonitorUsbEvents(onDeviceChanged As Action(Of String, Boolean))
        Try
            Dim insertQuery As New WqlEventQuery("SELECT * FROM __InstanceCreationEvent WITHIN 2 WHERE TargetInstance ISA 'Win32_USBControllerDevice'")
            Dim removeQuery As New WqlEventQuery("SELECT * FROM __InstanceDeletionEvent WITHIN 2 WHERE TargetInstance ISA 'Win32_USBControllerDevice'")

            Dim insertWatcher As New ManagementEventWatcher(insertQuery)
            Dim removeWatcher As New ManagementEventWatcher(removeQuery)

            AddHandler insertWatcher.EventArrived,
                Sub(sender, e)
                    Console.WriteLine("[USB] Device connected")
                    onDeviceChanged("Connected", True)
                End Sub

            AddHandler removeWatcher.EventArrived,
                Sub(sender, e)
                    Console.WriteLine("[USB] Device disconnected")
                    onDeviceChanged("Disconnected", False)
                End Sub

            insertWatcher.Start()
            removeWatcher.Start()

            Console.WriteLine("[USB] Monitoring started. Press Ctrl+C to stop.")
            Threading.Thread.Sleep(Threading.Timeout.Infinite)
        Catch ex As Exception
            Console.WriteLine($"[ERROR] USB monitoring failed: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Generate detailed USB report
    ''' </summary>
    Public Shared Function GenerateUsbReport() As String
        Dim sb As New StringBuilder()
        sb.AppendLine("=== EQ12 USB DEVICE SCANNER REPORT ===")
        sb.AppendLine($"Scan Time: {DateTime.Now:yyyy-MM-dd HH:mm:ss}")
        sb.AppendLine()

        Dim devices = ScanAllUsbDevices()

        sb.AppendLine($"Total USB Devices Detected: {devices.Count}")
        sb.AppendLine()

        For Each dev In devices
            sb.AppendLine("----------------------------------------")
            sb.AppendLine($"Device: {If(String.IsNullOrEmpty(dev.ProductName), "Unknown Device", dev.ProductName)}")
            sb.AppendLine($"Manufacturer: {If(String.IsNullOrEmpty(dev.Manufacturer), "Unknown", dev.Manufacturer)}")
            sb.AppendLine($"VID: {dev.VendorId}  PID: {dev.ProductId}")
            sb.AppendLine($"Class: {dev.DeviceClass}")
            sb.AppendLine($"Speed: {dev.Speed}")
            sb.AppendLine($"Port Type: {dev.PortType}")
            If dev.DriveLetters IsNot Nothing AndAlso dev.DriveLetters.Count > 0 Then
                sb.AppendLine($"Drive Letters: {String.Join(", ", dev.DriveLetters)}")
            End If
            If Not String.IsNullOrEmpty(dev.DriverVersion) Then
                sb.AppendLine($"Driver Version: {dev.DriverVersion}")
            End If
            sb.AppendLine($"Device Path: {dev.DevicePath}")
            sb.AppendLine()
        Next

        sb.AppendLine("========================================")
        Return sb.ToString()
    End Function

End Class
