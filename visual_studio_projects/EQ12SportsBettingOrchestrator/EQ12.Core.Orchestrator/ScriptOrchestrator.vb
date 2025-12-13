Option Strict On
Option Explicit On

Imports System.Diagnostics
Imports System.IO
Imports System.Text

Namespace EQ12.Core.Orchestrator

    ''' <summary>
    ''' Orchestrates execution of Python and PowerShell scripts
    ''' Captures output, parses results, and manages background processes
    ''' </summary>
    Public Class ScriptOrchestrator

        Private ReadOnly _workspaceRoot As String
        Private ReadOnly _pythonPath As String
        Private ReadOnly _powerShellPath As String

        Public Sub New(workspaceRoot As String, Optional pythonPath As String = "python", Optional powerShellPath As String = "powershell.exe")
            If String.IsNullOrWhiteSpace(workspaceRoot) Then
                Throw New ArgumentException("Workspace root cannot be empty", NameOf(workspaceRoot))
            End If

            _workspaceRoot = workspaceRoot
            _pythonPath = pythonPath
            _powerShellPath = powerShellPath
        End Sub

        ''' <summary>
        ''' Execute a Python script and return output
        ''' </summary>
        Public Function RunPythonScript(scriptPath As String, arguments As String, Optional waitForExit As Boolean = True) As ScriptResult
            If Not File.Exists(scriptPath) Then
                Throw New FileNotFoundException($"Python script not found: {scriptPath}")
            End If

            Dim fullArgs = $"""{scriptPath}"" {arguments}"
            Return RunProcess(_pythonPath, fullArgs, waitForExit)
        End Function

        ''' <summary>
        ''' Execute a PowerShell script and return output
        ''' </summary>
        Public Function RunPowerShellScript(scriptPath As String, arguments As String, Optional waitForExit As Boolean = True) As ScriptResult
            If Not File.Exists(scriptPath) Then
                Throw New FileNotFoundException($"PowerShell script not found: {scriptPath}")
            End If

            Dim fullArgs = $"-NoProfile -ExecutionPolicy Bypass -File ""{scriptPath}"" {arguments}"
            Return RunProcess(_powerShellPath, fullArgs, waitForExit)
        End Function

        ''' <summary>
        ''' Run HR Parlay Builder (convenience method)
        ''' </summary>
        Public Function RunHrParlayBuilder() As ScriptResult
            Dim scriptPath = Path.Combine(_workspaceRoot, "scripts", "eq12_parlay_builder.py")
            Return RunPythonScript(scriptPath, "--type hr --legs 10")
        End Function

        ''' <summary>
        ''' Run odds update (convenience method)
        ''' </summary>
        Public Function RunOddsUpdate() As ScriptResult
            Dim scriptPath = Path.Combine(_workspaceRoot, "scripts", "run-odds")
            Return RunPowerShellScript(scriptPath, "")
        End Function

        ''' <summary>
        ''' Run SEC 13F scraper (convenience method)
        ''' </summary>
        Public Function RunSec13FScraper(maxFilings As Integer) As ScriptResult
            Dim scriptPath = Path.Combine(_workspaceRoot, "scripts", "EQ12_SEC_13F_SCRAPER.ps1")
            Return RunPowerShellScript(scriptPath, $"-Action scrape -MaxFilings {maxFilings}")
        End Function

        ''' <summary>
        ''' Run VB.NET scan orchestrator (convenience method)
        ''' </summary>
        Public Function RunVBNETScan() As ScriptResult
            Dim scriptPath = Path.Combine(_workspaceRoot, "scripts", "EQ12_VBNET_SCAN_ORCHESTRATOR.ps1")
            Return RunPowerShellScript(scriptPath, "-Action scan")
        End Function

        ''' <summary>
        ''' Run system scan (convenience method)
        ''' </summary>
        Public Function RunSystemScan() As ScriptResult
            Dim scriptPath = Path.Combine(_workspaceRoot, "scripts", "EQ12_SYSTEM_SCAN.ps1")
            Return RunPowerShellScript(scriptPath, "-Verbose")
        End Function

        ''' <summary>
        ''' Check if prompt execution is running
        ''' </summary>
        Public Function IsPromptExecutionRunning() As Boolean
            Dim pythonProcs = Process.GetProcessesByName("python")
            For Each proc In pythonProcs
                Try
                    If proc.MainModule IsNot Nothing AndAlso _
                       proc.MainModule.FileName.Contains("eq12_prompt_executor") Then
                        Return True
                    End If
                Catch
                    ' Access denied - skip
                End Try
            Next

            Return False
        End Function

        Private Function RunProcess(fileName As String, arguments As String, waitForExit As Boolean) As ScriptResult
            Dim result As New ScriptResult() With {
                .StartTime = DateTime.UtcNow,
                .Success = False
            }

            Dim output As New StringBuilder()
            Dim errorOutput As New StringBuilder()

            Try
                Dim startInfo As New ProcessStartInfo() With {
                    .FileName = fileName,
                    .Arguments = arguments,
                    .UseShellExecute = False,
                    .RedirectStandardOutput = True,
                    .RedirectStandardError = True,
                    .CreateNoWindow = True,
                    .WorkingDirectory = _workspaceRoot
                }

                Using proc As Process = Process.Start(startInfo)
                    If proc Is Nothing Then
                        Throw New InvalidOperationException("Failed to start process")
                    End If

                    result.ProcessId = proc.Id

                    If waitForExit Then
                        ' Capture output asynchronously
                        AddHandler proc.OutputDataReceived, Sub(sender, e)
                                                                 If e.Data IsNot Nothing Then
                                                                     output.AppendLine(e.Data)
                                                                 End If
                                                             End Sub

                        AddHandler proc.ErrorDataReceived, Sub(sender, e)
                                                                If e.Data IsNot Nothing Then
                                                                    errorOutput.AppendLine(e.Data)
                                                                End If
                                                            End Sub

                        proc.BeginOutputReadLine()
                        proc.BeginErrorReadLine()

                        proc.WaitForExit()

                        result.ExitCode = proc.ExitCode
                        result.Output = output.ToString()
                        result.ErrorOutput = errorOutput.ToString()
                        result.Success = (proc.ExitCode = 0)
                    Else
                        ' Background process - don't wait
                        result.Success = True
                        result.Output = $"Process started in background (PID: {proc.Id})"
                    End If
                End Using

                result.EndTime = DateTime.UtcNow
                result.ExecutionTimeMs = (result.EndTime.Value - result.StartTime).TotalMilliseconds

            Catch ex As Exception
                result.Success = False
                result.ErrorOutput = ex.Message
                result.EndTime = DateTime.UtcNow
            End Try

            Return result
        End Function

    End Class

    ''' <summary>
    ''' Result of script execution
    ''' </summary>
    Public Class ScriptResult
        Public Property ProcessId As Integer
        Public Property ExitCode As Integer
        Public Property Output As String
        Public Property ErrorOutput As String
        Public Property Success As Boolean
        Public Property StartTime As DateTime
        Public Property EndTime As DateTime?
        Public Property ExecutionTimeMs As Double

        Public ReadOnly Property HasOutput As Boolean
            Get
                Return Not String.IsNullOrWhiteSpace(Output)
            End Get
        End Property

        Public ReadOnly Property HasErrors As Boolean
            Get
                Return Not String.IsNullOrWhiteSpace(ErrorOutput)
            End Get
        End Property
    End Class

End Namespace
