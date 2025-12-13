''' <summary>
''' EQ12 USB Scanner - Console Application Entry Point
''' Detects all USB devices, identifies port types, and monitors connections
''' </summary>

Imports System

Module Program
    Sub Main(args As String())
        Console.OutputEncoding = Text.Encoding.UTF8
        Console.WriteLine("=== EQ12 USB DEVICE SCANNER ===")
        Console.WriteLine()

        If args.Length > 0 AndAlso args(0) = "--monitor" Then
            MonitorMode()
        ElseIf args.Length > 0 AndAlso args(0) = "--json" Then
            JsonMode()
        Else
            ScanMode()
        End If
    End Sub

    ''' <summary>
    ''' Standard scan mode - print report to console
    ''' </summary>
    Private Sub ScanMode()
        Dim report = UsbScanner.GenerateUsbReport()
        Console.WriteLine(report)

        Console.WriteLine()
        Console.WriteLine("Options:")
        Console.WriteLine("  --monitor   Monitor USB plug/unplug events")
        Console.WriteLine("  --json      Output as JSON")
    End Sub

    ''' <summary>
    ''' Monitor mode - watch for USB events
    ''' </summary>
    Private Sub MonitorMode()
        Console.WriteLine("[Monitor Mode] Watching for USB device changes...")
        Console.WriteLine("Press Ctrl+C to stop.")
        Console.WriteLine()

        UsbScanner.MonitorUsbEvents(
            Sub(eventType, isConnected)
                Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] {eventType}")
                If isConnected Then
                    Threading.Thread.Sleep(1000) ' Wait for device enumeration
                    Dim devices = UsbScanner.ScanAllUsbDevices()
                    If devices.Count > 0 Then
                        Dim latest = devices(devices.Count - 1)
                        Console.WriteLine($"  → {latest.ProductName} ({latest.VendorId}:{latest.ProductId})")
                    End If
                End If
            End Sub
        )
    End Sub

    ''' <summary>
    ''' JSON mode - output structured data for automation
    ''' </summary>
    Private Sub JsonMode()
        Dim devices = UsbScanner.ScanAllUsbDevices()
        Dim json = Text.Json.JsonSerializer.Serialize(devices, New Text.Json.JsonSerializerOptions With {
            .WriteIndented = True,
            .PropertyNamingPolicy = Text.Json.JsonNamingPolicy.CamelCase
        })
        Console.WriteLine(json)
    End Sub
End Module
