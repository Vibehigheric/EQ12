Imports System.Diagnostics
Imports System.IO

''' <summary>
''' Bridge between VB.NET operator and Python ML system
''' Executes train_model, drift_monitor, promote_model with parameters
''' Captures output and logs results
''' </summary>
Public Class ModelPromotionManager
    Private _dataRoot As String
    Private _scriptRoot As String
    Private _logger As Logger
    
    Public Sub New(dataRoot As String)
        _dataRoot = dataRoot
        _scriptRoot = Path.Combine(dataRoot, "scripts")
        _logger = New Logger(dataRoot)
    End Sub
    
    ''' <summary>
    ''' Execute drift check (drift_monitor.py)
    ''' </summary>
    Public Function CheckDrift() As DriftCheckResult
        Try
            _logger.Log("[MODEL-MGR] Starting drift check")
            
            Dim output = ExecutePython("drift_monitor.py", "--days 7")
            
            Return New DriftCheckResult With {
                .Success = True,
                .Output = output,
                .Timestamp = DateTime.UtcNow,
                .Recommendation = ParseDriftOutput(output)
            }
        Catch ex As Exception
            _logger.LogError($"[MODEL-MGR] Drift check failed: {ex.Message}")
            Return New DriftCheckResult With {
                .Success = False,
                .Error = ex.Message
            }
        End Try
    End Function
    
    ''' <summary>
    ''' Retrain model (train_model_production.py)
    ''' </summary>
    Public Function RetrainModel(config As String) As ModelTrainResult
        Try
            _logger.Log("[MODEL-MGR] Starting model retrain")
            
            Dim args = $"--config {config} --retrain --save-metrics"
            Dim output = ExecutePython("train_model_production.py", args)
            
            Return New ModelTrainResult With {
                .Success = True,
                .Output = output,
                .Timestamp = DateTime.UtcNow,
                .ModelVersion = ExtractModelVersion(output)
            }
        Catch ex As Exception
            _logger.LogError($"[MODEL-MGR] Retrain failed: {ex.Message}")
            Return New ModelTrainResult With {
                .Success = False,
                .Error = ex.Message
            }
        End Try
    End Function
    
    ''' <summary>
    ''' Promote challenger model to champion (promote_model.py)
    ''' </summary>
    Public Function PromoteModel(challengerVersion As String) As ModelPromotionResult
        Try
            _logger.Log($"[MODEL-MGR] Promoting {challengerVersion}")
            
            Dim output = ExecutePython("promote_model.py", $"--challenger {challengerVersion}")
            
            Return New ModelPromotionResult With {
                .Success = True,
                .Output = output,
                .Timestamp = DateTime.UtcNow,
                .Promoted = output.Contains("PROMOTED")
            }
        Catch ex As Exception
            _logger.LogError($"[MODEL-MGR] Promotion failed: {ex.Message}")
            Return New ModelPromotionResult With {
                .Success = False,
                .Error = ex.Message
            }
        End Try
    End Function
    
    ''' <summary>
    ''' Rollback to previous champion
    ''' </summary>
    Public Function RollbackModel() As ModelRollbackResult
        Try
            _logger.Log("[MODEL-MGR] Rolling back to previous champion")
            
            Dim output = ExecutePython("promote_model.py", "--rollback")
            
            Return New ModelRollbackResult With {
                .Success = True,
                .Output = output,
                .Timestamp = DateTime.UtcNow
            }
        Catch ex As Exception
            _logger.LogError($"[MODEL-MGR] Rollback failed: {ex.Message}")
            Return New ModelRollbackResult With {
                .Success = False,
                .Error = ex.Message
            }
        End Try
    End Function
    
    ''' <summary>
    ''' Run backtest on model
    ''' </summary>
    Public Function RunBacktest(days As Integer) As BacktestResult
        Try
            _logger.Log($"[MODEL-MGR] Running backtest for {days} days")
            
            Dim output = ExecutePython("backtester.py", $"--days {days}")
            
            Return New BacktestResult With {
                .Success = True,
                .Output = output,
                .Timestamp = DateTime.UtcNow,
                .ROI = ExtractRoiFromBacktest(output)
            }
        Catch ex As Exception
            _logger.LogError($"[MODEL-MGR] Backtest failed: {ex.Message}")
            Return New BacktestResult With {
                .Success = False,
                .Error = ex.Message
            }
        End Try
    End Function
    
    Private Function ExecutePython(scriptName As String, args As String) As String
        Dim scriptPath = Path.Combine(_scriptRoot, scriptName)
        
        If Not File.Exists(scriptPath) Then
            Throw New FileNotFoundException($"Script not found: {scriptPath}")
        End If
        
        Dim processInfo As New ProcessStartInfo With {
            .FileName = "python",
            .Arguments = $"""{scriptPath}"" {args}",
            .UseShellExecute = False,
            .RedirectStandardOutput = True,
            .RedirectStandardError = True,
            .CreateNoWindow = True,
            .WorkingDirectory = _dataRoot
        }
        
        Using process = Process.Start(processInfo)
            If Not process.WaitForExit(300000) Then ' 5 min timeout
                process.Kill()
                Throw New TimeoutException($"Script execution timeout: {scriptName}")
            End If
            
            Dim output = process.StandardOutput.ReadToEnd()
            Dim errors = process.StandardError.ReadToEnd()
            
            If process.ExitCode <> 0 Then
                Throw New Exception($"Script failed: {errors}")
            End If
            
            Return output
        End Using
    End Function
    
    Private Function ParseDriftOutput(output As String) As String
        If output.Contains("CRITICAL") Then
            Return "RETRAIN_REQUIRED"
        ElseIf output.Contains("MODERATE") Then
            Return "MONITOR_CLOSELY"
        Else
            Return "OK"
        End If
    End Function
    
    Private Function ExtractModelVersion(output As String) As String
        ' Parse version from output (e.g., "v_2025_12_04_1400")
        Dim lines = output.Split(vbLf)
        For Each line In lines
            If line.Contains("model_version") OrElse line.Contains("v_") Then
                Return line.Split(":")(1).Trim()
            End If
        Next
        Return $"v_{DateTime.Now:yyyy_MM_dd_HHmm}"
    End Function
    
    Private Function ExtractRoiFromBacktest(output As String) As Double
        ' Parse ROI percentage from backtest output
        Dim lines = output.Split(vbLf)
        For Each line In lines
            If line.Contains("ROI") OrElse line.Contains("roi") Then
                Dim parts = line.Split(":")
                If parts.Length > 1 Then
                    If Double.TryParse(parts(1).Trim().Replace("%", ""), Nothing) Then
                        Return Double.Parse(parts(1).Trim().Replace("%", "")) / 100
                    End If
                End If
            End If
        Next
        Return 0.0
    End Function
End Class

Public Class DriftCheckResult
    Public Property Success As Boolean
    Public Property Output As String
    Public Property Error As String
    Public Property Timestamp As DateTime
    Public Property Recommendation As String
End Class

Public Class ModelTrainResult
    Public Property Success As Boolean
    Public Property Output As String
    Public Property Error As String
    Public Property Timestamp As DateTime
    Public Property ModelVersion As String
End Class

Public Class ModelPromotionResult
    Public Property Success As Boolean
    Public Property Output As String
    Public Property Error As String
    Public Property Timestamp As DateTime
    Public Property Promoted As Boolean
End Class

Public Class ModelRollbackResult
    Public Property Success As Boolean
    Public Property Output As String
    Public Property Error As String
    Public Property Timestamp As DateTime
End Class

Public Class BacktestResult
    Public Property Success As Boolean
    Public Property Output As String
    Public Property Error As String
    Public Property Timestamp As DateTime
    Public Property ROI As Double
End Class
