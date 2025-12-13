Imports System.Diagnostics
Imports System.IO
Imports System.Threading

''' <summary>
''' EQ12 Docker Desktop Auto-Launch and Self-Healing Manager
''' ASC II Expert Edition - Production-Ready Docker Orchestration
''' </summary>
Public Module DockerManager

    Private ReadOnly DockerPath As String = 
        Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), 
                     "Docker", "Docker", "Docker Desktop.exe")
    
    Private ReadOnly MaxStartupWaitSeconds As Integer = 30
    Private ReadOnly HealthCheckIntervalMs As Integer = 5000

    ''' <summary>
    ''' Ensures Docker Desktop is running and healthy before continuing
    ''' </summary>
    Public Sub EnsureDockerRunning()
        Try
            EQ12.Core.LogManager.Info("Docker Manager: Starting health check...")
            
            ' Step 1: Check if Docker Desktop process is running
            If Not IsDockerDesktopRunning() Then
                EQ12.Core.LogManager.Warning("Docker Desktop not detected. Launching...")
                StartDockerDesktop()
                WaitForDockerEngine()
            End If
            
            ' Step 2: Verify Docker Engine is responsive
            If Not IsDockerEngineHealthy() Then
                EQ12.Core.LogManager.Warning("Docker Engine not responding. Attempting restart...")
                RestartDocker()
                WaitForDockerEngine()
            End If
            
            ' Step 3: Final health confirmation
            If IsDockerEngineHealthy() Then
                EQ12.Core.LogManager.Info("✅ Docker Engine is ready and healthy.")
                
                ' Send Telegram notification
                Try
                    Dim msg = "🐳 Docker Engine verified healthy" & vbCrLf & 
                             "Containers ready for EQ12 stack operations"
                    EQ12.TelegramBot.AlertManager.SendAlert(msg).Wait()
                Catch
                    ' Telegram optional - don't fail on notification error
                End Try
            Else
                Throw New Exception("Docker Engine failed to become healthy after restart")
            End If
            
        Catch ex As Exception
            EQ12.Core.LogManager.Error($"Docker startup failed: {ex.Message}")
            
            ' Send critical alert
            Try
                EQ12.TelegramBot.AlertManager.SendAlert(
                    $"❌ CRITICAL: Docker Engine startup failed{vbCrLf}{ex.Message}"
                ).Wait()
            Catch
            End Try
            
            Throw
        End Try
    End Sub

    ''' <summary>
    ''' Check if Docker Desktop process is running
    ''' </summary>
    Private Function IsDockerDesktopRunning() As Boolean
        Dim processes = Process.GetProcessesByName("Docker Desktop")
        Return processes.Length > 0
    End Function

    ''' <summary>
    ''' Launch Docker Desktop executable
    ''' </summary>
    Private Sub StartDockerDesktop()
        If Not File.Exists(DockerPath) Then
            Throw New FileNotFoundException($"Docker Desktop not found at: {DockerPath}")
        End If
        
        Dim psi As New ProcessStartInfo With {
            .FileName = DockerPath,
            .UseShellExecute = True,
            .WindowStyle = ProcessWindowStyle.Minimized,
            .Verb = "runas"
        }
        
        Process.Start(psi)
        EQ12.Core.LogManager.Info("Docker Desktop process started. Waiting for engine initialization...")
    End Sub

    ''' <summary>
    ''' Wait for Docker Engine to become responsive
    ''' </summary>
    Private Sub WaitForDockerEngine()
        Dim elapsed = 0
        Dim maxWaitMs = MaxStartupWaitSeconds * 1000
        
        While elapsed < maxWaitMs
            If IsDockerEngineHealthy() Then
                EQ12.Core.LogManager.Info($"Docker Engine ready after {elapsed / 1000} seconds")
                Return
            End If
            
            Thread.Sleep(HealthCheckIntervalMs)
            elapsed += HealthCheckIntervalMs
            
            If elapsed Mod 10000 = 0 Then
                EQ12.Core.LogManager.Info($"Still waiting for Docker Engine... ({elapsed / 1000}s)")
            End If
        End While
        
        Throw New TimeoutException($"Docker Engine did not respond after {MaxStartupWaitSeconds} seconds")
    End Sub

    ''' <summary>
    ''' Check Docker Engine health via docker info command
    ''' </summary>
    Public Function IsDockerEngineHealthy() As Boolean
        Try
            Dim result = RunCommand("docker info")
            Return result.Contains("Server Version") AndAlso result.Contains("Operating System")
        Catch
            Return False
        End Try
    End Function

    ''' <summary>
    ''' Restart Docker Desktop (kill and relaunch)
    ''' </summary>
    Private Sub RestartDocker()
        EQ12.Core.LogManager.Warning("Executing Docker Desktop restart...")
        
        ' Kill Docker Desktop process
        Try
            RunCommand("taskkill /IM ""Docker Desktop.exe"" /F")
            Thread.Sleep(3000)
        Catch ex As Exception
            EQ12.Core.LogManager.Warning($"Docker kill command error (may be expected): {ex.Message}")
        End Try
        
        ' Wait for cleanup
        Thread.Sleep(2000)
        
        ' Restart
        StartDockerDesktop()
    End Sub

    ''' <summary>
    ''' Run command and return output
    ''' </summary>
    Private Function RunCommand(cmd As String) As String
        Dim psi As New ProcessStartInfo("cmd.exe", "/c " & cmd) With {
            .RedirectStandardOutput = True,
            .RedirectStandardError = True,
            .UseShellExecute = False,
            .CreateNoWindow = True
        }
        
        Dim proc = Process.Start(psi)
        Dim output = proc.StandardOutput.ReadToEnd()
        Dim errorOutput = proc.StandardError.ReadToEnd()
        proc.WaitForExit()
        
        If proc.ExitCode <> 0 AndAlso Not String.IsNullOrEmpty(errorOutput) Then
            Throw New Exception($"Command failed: {errorOutput}")
        End If
        
        Return output
    End Function

    ''' <summary>
    ''' Ensure specific EQ12 container is running
    ''' </summary>
    Public Sub EnsureContainerRunning(containerName As String, Optional imageName As String = Nothing)
        Try
            Dim psOutput = RunCommand($"docker ps -a --filter name={containerName} --format ""{{{{.Names}}}}|{{{{.Status}}}}""")
            
            If String.IsNullOrEmpty(psOutput) Then
                ' Container doesn't exist - create and start
                If String.IsNullOrEmpty(imageName) Then
                    Throw New ArgumentException($"Container {containerName} not found and no image specified")
                End If
                
                EQ12.Core.LogManager.Info($"Creating container: {containerName} from {imageName}")
                RunCommand($"docker run -d --name {containerName} {imageName}")
                
            ElseIf psOutput.Contains("Exited") OrElse psOutput.Contains("Created") Then
                ' Container exists but stopped - start it
                EQ12.Core.LogManager.Info($"Starting existing container: {containerName}")
                RunCommand($"docker start {containerName}")
                
            Else
                EQ12.Core.LogManager.Info($"Container {containerName} already running")
            End If
            
        Catch ex As Exception
            EQ12.Core.LogManager.Error($"Failed to ensure container {containerName}: {ex.Message}")
            Throw
        End Try
    End Sub

    ''' <summary>
    ''' Start all EQ12 stack containers via docker-compose
    ''' </summary>
    Public Sub StartEQ12Stack()
        Try
            EQ12.Core.LogManager.Info("Starting EQ12 Docker stack (godstack, redis, grafana, prometheus, jupyter)...")
            
            Dim composePath = "C:\EQ12_BROKEN_20251122_210342"
            Dim composeFile = Path.Combine(composePath, "docker-compose.yml")
            
            If Not File.Exists(composeFile) Then
                Throw New FileNotFoundException($"docker-compose.yml not found at {composeFile}")
            End If
            
            ' Change to compose directory and run
            Dim psi As New ProcessStartInfo("cmd.exe", 
                $"/c cd /d ""{composePath}"" && docker-compose up -d") With {
                .RedirectStandardOutput = True,
                .RedirectStandardError = True,
                .UseShellExecute = False,
                .CreateNoWindow = True
            }
            
            Dim proc = Process.Start(psi)
            Dim output = proc.StandardOutput.ReadToEnd()
            Dim errors = proc.StandardError.ReadToEnd()
            proc.WaitForExit()
            
            If proc.ExitCode = 0 Then
                EQ12.Core.LogManager.Info("✅ EQ12 Docker stack started successfully")
                EQ12.Core.LogManager.Info(output)
                
                ' Send success notification
                Try
                    EQ12.TelegramBot.AlertManager.SendAlert(
                        "🚀 EQ12 Stack Launched" & vbCrLf & 
                        "✅ godstack, redis, grafana, prometheus, jupyter" & vbCrLf &
                        "All containers operational"
                    ).Wait()
                Catch
                End Try
            Else
                Throw New Exception($"docker-compose failed: {errors}")
            End If
            
        Catch ex As Exception
            EQ12.Core.LogManager.Error($"Failed to start EQ12 stack: {ex.Message}")
            Throw
        End Try
    End Sub

    ''' <summary>
    ''' Auto-heal failed containers
    ''' </summary>
    Public Sub AutoHealContainers()
        Try
            EQ12.Core.LogManager.Info("Running auto-heal check for exited containers...")
            
            Dim exitedContainers = RunCommand(
                "docker ps -a --filter ""status=exited"" --format ""{{.Names}}"""
            ).Split(New String() {vbCrLf, vbLf}, StringSplitOptions.RemoveEmptyEntries)
            
            If exitedContainers.Length = 0 Then
                EQ12.Core.LogManager.Info("No exited containers found - all healthy")
                Return
            End If
            
            For Each container In exitedContainers
                If Not String.IsNullOrWhiteSpace(container) Then
                    EQ12.Core.LogManager.Warning($"Auto-healing exited container: {container}")
                    
                    Try
                        RunCommand($"docker start {container}")
                        EQ12.Core.LogManager.Info($"✅ Restarted: {container}")
                        
                        ' Send alert
                        EQ12.TelegramBot.AlertManager.SendAlert(
                            $"🔧 Auto-Heal: Restarted container '{container}'"
                        ).Wait()
                    Catch ex As Exception
                        EQ12.Core.LogManager.Error($"Failed to restart {container}: {ex.Message}")
                    End Try
                End If
            Next
            
        Catch ex As Exception
            EQ12.Core.LogManager.Error($"Auto-heal failed: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Get Docker system information
    ''' </summary>
    Public Function GetDockerSystemInfo() As String
        Return RunCommand("docker info")
    End Function

    ''' <summary>
    ''' List all running containers
    ''' </summary>
    Public Function GetRunningContainers() As String
        Return RunCommand("docker ps --format ""table {{.Names}}\t{{.Status}}\t{{.Ports}}""")
    End Function

End Module
