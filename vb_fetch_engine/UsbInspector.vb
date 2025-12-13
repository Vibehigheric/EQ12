''' <summary>
''' EQ12 USB Drive Inspector - D:, E:, Ventoy, Bootable Drive Detection
''' Programmatic inspection of removable drives
''' </summary>
Imports System
Imports System.IO
Imports System.Collections.Generic

Namespace EQ12.Core.Hardware

    Public Class UsbDriveInfo
        Public Property DriveLetter As String
        Public Property VolumeLabel As String
        Public Property SizeGb As Double
        Public Property FreeGb As Double
        Public Property UsedGb As Double
        Public Property FileSystem As String
        Public Property IsReady As Boolean
        Public Property DriveType As String

        Public Overrides Function ToString() As String
            Return $"{DriveLetter} | {VolumeLabel} | {SizeGb:F2} GB | {FileSystem}"
        End Function
    End Class

    Public Class UsbInspector
        ''' <summary>
        ''' Get all removable drives (USB, SD cards, etc.)
        ''' </summary>
        Public Shared Function GetRemovableDrives() As List(Of UsbDriveInfo)
            Dim result As New List(Of UsbDriveInfo)()

            For Each d In DriveInfo.GetDrives()
                If d.DriveType = DriveType.Removable Then
                    Dim info As New UsbDriveInfo() With {
                        .DriveLetter = d.Name,
                        .IsReady = d.IsReady,
                        .DriveType = d.DriveType.ToString()
                    }

                    If d.IsReady Then
                        Try
                            info.VolumeLabel = d.VolumeLabel
                            info.SizeGb = Math.Round(d.TotalSize / 1024.0 / 1024.0 / 1024.0, 2)
                            info.FreeGb = Math.Round(d.TotalFreeSpace / 1024.0 / 1024.0 / 1024.0, 2)
                            info.UsedGb = Math.Round((d.TotalSize - d.TotalFreeSpace) / 1024.0 / 1024.0 / 1024.0, 2)
                            info.FileSystem = d.DriveFormat
                        Catch ex As Exception
                            info.VolumeLabel = "Error reading drive"
                        End Try
                    End If

                    result.Add(info)
                End If
            Next

            Return result
        End Function

        ''' <summary>
        ''' Check if drive is Ventoy bootable
        ''' </summary>
        Public Shared Function IsVentoyDrive(driveLetter As String) As Boolean
            Try
                Dim ventoyPath = Path.Combine(driveLetter, "ventoy")
                Dim ventoyDir = Path.Combine(driveLetter, "Ventoy")

                Return Directory.Exists(ventoyPath) OrElse Directory.Exists(ventoyDir)
            Catch ex As Exception
                Return False
            End Try
        End Function

        ''' <summary>
        ''' Get detailed drive report
        ''' </summary>
        Public Shared Function GetDriveReport() As String
            Dim sb As New System.Text.StringBuilder()
            sb.AppendLine("=== EQ12 USB DRIVE INVENTORY ===")
            sb.AppendLine()

            Dim drives = GetRemovableDrives()

            If drives.Count = 0 Then
                sb.AppendLine("No removable drives detected.")
                Return sb.ToString()
            End If

            For Each drive In drives
                sb.AppendLine($"Drive: {drive.DriveLetter}")
                sb.AppendLine($"  Label: {drive.VolumeLabel}")
                sb.AppendLine($"  Size: {drive.SizeGb} GB")
                sb.AppendLine($"  Used: {drive.UsedGb} GB")
                sb.AppendLine($"  Free: {drive.FreeGb} GB")
                sb.AppendLine($"  File System: {drive.FileSystem}")
                sb.AppendLine($"  Ready: {drive.IsReady}")

                If drive.IsReady Then
                    Dim isVentoy = IsVentoyDrive(drive.DriveLetter)
                    sb.AppendLine($"  Ventoy: {isVentoy}")
                End If

                sb.AppendLine()
            Next

            Return sb.ToString()
        End Function

    End Class

End Namespace
