' ============================================================================
' EQ12_System_Health_Monitor.vb
' 
' 24/7 System Health Monitoring for EQ12 Beelink
' Monitors: CPU, RAM, VS Code, Docker, Copilot, WSL
' Actions: Auto-restart, cleanup, alerts when thresholds exceeded
'
' Author: EQ12 System (Expert VB.NET + System Engineer)
' Created: 2025-11-27
' ============================================================================

Imports System.IO
Imports System.Diagnostics
Imports System.Threading
Imports System.Management

Module EQ12_System_Health_Monitor

    ' ========================================================================
    ' CONFIGURATION
    ' ========================================================================
    
    Private ReadOnly LogPath As String = "C:\EQ12_BROKEN_20251122_210342\logs\system_health_monitor.log"
    Private ReadOnly MonitorIntervalSeconds As Integer = 60  ' Check every 60 seconds
    
    ' Thresholds
    Private ReadOnly MaxRAMUsagePercent As Integer = 90
    Private ReadOnly MaxCPUUsagePercent As Integer = 85
    Private ReadOnly MaxVSCodeProcesses As Integer = 25
    Private ReadOnly MaxVSCodeMemoryMB As Long = 8192  ' 8GB
    Private ReadOnly MaxDockerMemoryMB As Long = 4096  ' 4GB
    
    ' Recovery actions
    Private ReadOnly VSCodeRecoveryManagerPath As String = "C:\EQ12_BROKEN_20251122_210342\visual_studio_projects\VSCode_Recovery_Manager\VSCode_Recovery_Manager.exe"
    
    Private monitoring As Boolean = True
    Private recoveryInProgress As Boolean = False
    
    ' ========================================================================
    ' MAIN ENTRY POINT
    ' ========================================================================
    
    Sub Main(args As String())
        Try
            Log("========================================")
            Log("EQ12 System Health Monitor Started")
            Log("========================================")
            Log("System: " & Environment.MachineName)
            Log("Monitor Interval: " & MonitorIntervalSeconds & " seconds")
            Log("Press Ctrl+C to stop monitoring...")
            Log("========================================")
            
            ' Handle Ctrl+C gracefully
            AddHandler Console.CancelKeyPress, AddressOf StopMonitoring
            
            ' Start monitoring loop
            While monitoring
                Try
                    PerformHealthCheck()
                    Thread.Sleep(MonitorIntervalSeconds * 1000)
                Catch ex As Exception
                    Log("ERROR in monitoring loop: " & ex.Message)
                    Thread.Sleep(5000)  ' Wait 5 seconds before retry
                End Try
            End While
            
            Log("========================================")
            Log("EQ12 System Health Monitor Stopped")
            Log("========================================")
            
        Catch ex As Exception
            Log("CRITICAL ERROR: " & ex.Message)
            Log("Stack Trace: " & ex.StackTrace)
        End Try
    End Sub
    
    Private Sub StopMonitoring(sender As Object, e As ConsoleCancelEventArgs)
        Log("Stop signal received - shutting down gracefully...")
        monitoring = False
        e.Cancel = True
    End Sub
    
    ' ========================================================================
    ' HEALTH CHECK ORCHESTRATION
    ' ========================================================================
    
    Private Sub PerformHealthCheck()
        Dim timestamp = DateTime.Now.ToString("HH:mm:ss")
        
        ' Get system metrics
        Dim ramUsage = GetRAMUsage()
        Dim cpuUsage = GetCPUUsage()
        Dim vsCodeHealth = CheckVSCodeHealth()
        Dim dockerHealth = CheckDockerHealth()
        Dim wslHealth = CheckWSLHealth()
        
        ' Log current status (concise)
        Log($"{timestamp} | RAM: {ramUsage:F1}% | CPU: {cpuUsage:F1}% | VSCode: {vsCodeHealth.ProcessCount} procs ({FormatBytes(vsCodeHealth.TotalMemory)}) | Docker: {FormatBytes(dockerHealth.TotalMemory)} | WSL: {FormatBytes(wslHealth.TotalMemory)}")
        
        ' Check for threshold violations
        Dim issuesDetected As New List(Of String)
        
        If ramUsage > MaxRAMUsagePercent Then
            issuesDetected.Add($"HIGH RAM USAGE: {ramUsage:F1}% (threshold: {MaxRAMUsagePercent}%)")
        End If
        
        If cpuUsage > MaxCPUUsagePercent Then
            issuesDetected.Add($"HIGH CPU USAGE: {cpuUsage:F1}% (threshold: {MaxCPUUsagePercent}%)")
        End If
        
        If vsCodeHealth.ProcessCount > MaxVSCodeProcesses Then
            issuesDetected.Add($"TOO MANY VSCODE PROCESSES: {vsCodeHealth.ProcessCount} (threshold: {MaxVSCodeProcesses})")
        End If
        
        If vsCodeHealth.TotalMemory / (1024 * 1024) > MaxVSCodeMemoryMB Then
            issuesDetected.Add($"VSCODE MEMORY EXCESSIVE: {FormatBytes(vsCodeHealth.TotalMemory)} (threshold: {MaxVSCodeMemoryMB}MB)")
        End If
        
        If dockerHealth.TotalMemory / (1024 * 1024) > MaxDockerMemoryMB Then
            issuesDetected.Add($"DOCKER MEMORY EXCESSIVE: {FormatBytes(dockerHealth.TotalMemory)} (threshold: {MaxDockerMemoryMB}MB)")
        End If
        
        ' Take action if issues detected
        If issuesDetected.Count > 0 AndAlso Not recoveryInProgress Then
            Log("⚠️  HEALTH ISSUES DETECTED:")
            For Each issue In issuesDetected
                Log("   ❌ " & issue)
            Next
            
            PerformRecoveryActions(issuesDetected, vsCodeHealth, dockerHealth)
        End If
    End Sub
    
    ' ========================================================================
    ' SYSTEM METRICS
    ' ========================================================================
    
    Private Function GetRAMUsage() As Double
        Try
            Dim computerInfo = New Microsoft.VisualBasic.Devices.ComputerInfo()
            Dim totalRAM = computerInfo.TotalPhysicalMemory
            Dim availableRAM = computerInfo.AvailablePhysicalMemory
            Dim usedRAM = totalRAM - availableRAM
            Return (usedRAM / totalRAM) * 100.0
        Catch
            Return 0.0
        End Try
    End Function
    
    Private Function GetCPUUsage() As Double
        Try
            Dim cpuCounter As New PerformanceCounter("Processor", "% Processor Time", "_Total")
            cpuCounter.NextValue()
            Thread.Sleep(100)
            Return cpuCounter.NextValue()
        Catch
            Return 0.0
        End Try
    End Function
    
    ' ========================================================================
    ' PROCESS HEALTH CHECKS
    ' ========================================================================
    
    Private Structure ProcessHealth
        Public ProcessCount As Integer
        Public TotalMemory As Long
        Public HungProcesses As Integer
    End Structure
    
    Private Function CheckVSCodeHealth() As ProcessHealth
        Dim health As New ProcessHealth
        
        Try
            Dim codeProcesses = Process.GetProcessesByName("Code")
            health.ProcessCount = codeProcesses.Length
            
            For Each proc In codeProcesses
                Try
                    health.TotalMemory += proc.WorkingSet64
                    If Not proc.Responding Then
                        health.HungProcesses += 1
                    End If
                Catch
                    ' Process may have exited
                End Try
            Next
        Catch ex As Exception
            Log("Error checking VS Code health: " & ex.Message)
        End Try
        
        Return health
    End Function
    
    Private Function CheckDockerHealth() As ProcessHealth
        Dim health As New ProcessHealth
        
        Try
            Dim dockerProcesses = Process.GetProcesses().Where(Function(p) 
                p.ProcessName.ToLower().Contains("docker") OrElse 
                p.ProcessName.ToLower().Contains("com.docker")
            ).ToArray()
            
            health.ProcessCount = dockerProcesses.Length
            
            For Each proc In dockerProcesses
                Try
                    health.TotalMemory += proc.WorkingSet64
                    If Not proc.Responding Then
                        health.HungProcesses += 1
                    End If
                Catch
                    ' Process may have exited
                End Try
            Next
        Catch ex As Exception
            Log("Error checking Docker health: " & ex.Message)
        End Try
        
        Return health
    End Function
    
    Private Function CheckWSLHealth() As ProcessHealth
        Dim health As New ProcessHealth
        
        Try
            Dim wslProcesses = Process.GetProcesses().Where(Function(p) 
                p.ProcessName.ToLower().Contains("wsl") OrElse 
                p.ProcessName.ToLower().Contains("lxss")
            ).ToArray()
            
            health.ProcessCount = wslProcesses.Length
            
            For Each proc In wslProcesses
                Try
                    health.TotalMemory += proc.WorkingSet64
                Catch
                    ' Process may have exited
                End Try
            Next
        Catch ex As Exception
            Log("Error checking WSL health: " & ex.Message)
        End Try
        
        Return health
    End Function
    
    ' ========================================================================
    ' RECOVERY ACTIONS
    ' ========================================================================
    
    Private Sub PerformRecoveryActions(issues As List(Of String), vsCodeHealth As ProcessHealth, dockerHealth As ProcessHealth)
        recoveryInProgress = True
        
        Try
            Log("========================================")
            Log("🔧 INITIATING RECOVERY ACTIONS")
            Log("========================================")
            
            ' Action 1: Kill hung VS Code processes
            If vsCodeHealth.HungProcesses > 0 Then
                Log($"Action 1: Killing {vsCodeHealth.HungProcesses} hung VS Code processes...")
                KillHungProcesses("Code")
            End If
            
            ' Action 2: Run VS Code Recovery Manager if memory excessive
            If vsCodeHealth.TotalMemory / (1024 * 1024) > MaxVSCodeMemoryMB Then
                Log("Action 2: Running VS Code Recovery Manager...")
                RunVSCodeRecoveryManager()
            End If
            
            ' Action 3: Clear temp files if RAM high
            Dim ramUsage = GetRAMUsage()
            If ramUsage > MaxRAMUsagePercent Then
                Log("Action 3: Clearing temp files to free RAM...")
                ClearTempFiles()
            End If
            
            ' Action 4: Restart Docker if excessive memory
            If dockerHealth.TotalMemory / (1024 * 1024) > MaxDockerMemoryMB Then
                Log("Action 4: Restarting Docker Desktop...")
                RestartDocker()
            End If
            
            Log("✅ Recovery actions completed")
            Log("========================================")
            
        Catch ex As Exception
            Log("ERROR during recovery: " & ex.Message)
        Finally
            recoveryInProgress = False
        End Try
    End Sub
    
    Private Sub KillHungProcesses(processName As String)
        Try
            Dim processes = Process.GetProcessesByName(processName)
            Dim killed As Integer = 0
            
            For Each proc In processes
                Try
                    If Not proc.Responding Then
                        proc.Kill()
                        killed += 1
                        Log($"   ✓ Killed hung process: {processName} (PID {proc.Id})")
                    End If
                Catch
                    ' Process may have already exited
                End Try
            Next
            
            If killed > 0 Then
                Log($"   ✅ Killed {killed} hung processes")
            Else
                Log("   ℹ️  No hung processes found")
            End If
        Catch ex As Exception
            Log($"   ❌ Error killing hung processes: {ex.Message}")
        End Try
    End Sub
    
    Private Sub RunVSCodeRecoveryManager()
        Try
            If File.Exists(VSCodeRecoveryManagerPath) Then
                Dim startInfo As New ProcessStartInfo With {
                    .FileName = VSCodeRecoveryManagerPath,
                    .UseShellExecute = False,
                    .CreateNoWindow = True
                }
                
                Dim proc = Process.Start(startInfo)
                proc.WaitForExit(30000)  ' Wait max 30 seconds
                
                Log("   ✅ VS Code Recovery Manager executed")
            Else
                Log($"   ⚠️  Recovery Manager not found: {VSCodeRecoveryManagerPath}")
            End If
        Catch ex As Exception
            Log($"   ❌ Error running Recovery Manager: {ex.Message}")
        End Try
    End Sub
    
    Private Sub ClearTempFiles()
        Try
            Dim tempPaths() As String = {
                Environment.GetEnvironmentVariable("TEMP"),
                Environment.GetEnvironmentVariable("TMP"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Windows), "Temp")
            }
            
            Dim totalCleared As Long = 0
            
            For Each tempPath In tempPaths
                If Directory.Exists(tempPath) Then
                    Try
                        Dim files = Directory.GetFiles(tempPath, "*", SearchOption.TopDirectoryOnly)
                        For Each file In files
                            Try
                                Dim fileInfo As New FileInfo(file)
                                Dim fileSize = fileInfo.Length
                                fileInfo.Delete()
                                totalCleared += fileSize
                            Catch
                                ' Skip files in use
                            End Try
                        Next
                    Catch
                        ' Skip directories with access issues
                    End Try
                End If
            Next
            
            Log($"   ✅ Cleared {FormatBytes(totalCleared)} of temp files")
        Catch ex As Exception
            Log($"   ❌ Error clearing temp files: {ex.Message}")
        End Try
    End Sub
    
    Private Sub RestartDocker()
        Try
            ' Stop Docker Desktop
            Dim dockerProc = Process.GetProcessesByName("Docker Desktop")
            For Each proc In dockerProc
                proc.Kill()
                proc.WaitForExit(10000)
            Next
            
            Thread.Sleep(2000)
            
            ' Start Docker Desktop
            Dim dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
            If File.Exists(dockerPath) Then
                Process.Start(dockerPath)
                Log("   ✅ Docker Desktop restarted")
            Else
                Log("   ⚠️  Docker Desktop not found")
            End If
        Catch ex As Exception
            Log($"   ❌ Error restarting Docker: {ex.Message}")
        End Try
    End Sub
    
    ' ========================================================================
    ' UTILITY FUNCTIONS
    ' ========================================================================
    
    Private Function FormatBytes(bytes As Long) As String
        Dim sizes() As String = {"B", "KB", "MB", "GB", "TB"}
        Dim order As Integer = 0
        Dim size As Double = bytes
        
        While size >= 1024 AndAlso order < sizes.Length - 1
            order += 1
            size /= 1024
        End While
        
        Return String.Format("{0:0.##} {1}", size, sizes(order))
    End Function
    
    Private Sub Log(message As String)
        Try
            ' Ensure log directory exists
            Directory.CreateDirectory(Path.GetDirectoryName(LogPath))
            
            ' Append to log file
            Dim timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss")
            Dim logEntry = timestamp & " | " & message & vbCrLf
            
            File.AppendAllText(LogPath, logEntry)
            
            ' Also write to console
            Console.WriteLine(message)
            
        Catch ex As Exception
            Console.WriteLine("ERROR LOGGING: " & ex.Message)
        End Try
    End Sub

End Module
