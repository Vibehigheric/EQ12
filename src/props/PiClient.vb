' PiClient.vb - Raspberry Pi REST client for ML predictions
Imports System
Imports System.Net.Http
Imports System.Text
Imports System.Threading.Tasks
Imports Newtonsoft.Json
Imports Renci.SshNet

Namespace EQ12.Props

    ''' <summary>
    ''' Request payload for Pi model inference
    ''' </summary>
    Public Class PredictionRequest
        Public Property PlayerId As String
        Public Property GameId As String
        Public Property Market As String
        Public Property Line As Decimal
        Public Property Features As Dictionary(Of String, Double)
    End Class
    
    ''' <summary>
    ''' Response from Pi model
    ''' </summary>
    Public Class PredictionResponse
        Public Property TrueProb As Double
        Public Property ExpectedValue As Double
        Public Property Confidence As Double
        Public Property ModelVersion As String
        Public Property InferenceTimeMs As Double
    End Class
    
    ''' <summary>
    ''' Client for Raspberry Pi + Coral TPU ML inference service
    ''' </summary>
    Public Class PiClient
        Private ReadOnly _piHost As String
        Private ReadOnly _piPort As Integer
        Private ReadOnly _sshUser As String
        Private ReadOnly _sshKeyPath As String
        Private ReadOnly _httpClient As HttpClient
        
        Public Sub New(piHost As String, 
                      Optional piPort As Integer = 5000, 
                      Optional sshUser As String = "pi", 
                      Optional sshKeyPath As String = "~/.ssh/id_rsa")
            _piHost = piHost
            _piPort = piPort
            _sshUser = sshUser
            _sshKeyPath = sshKeyPath
            
            _httpClient = New HttpClient() With {
                .BaseAddress = New Uri($"http://{_piHost}:{_piPort}/"),
                .Timeout = TimeSpan.FromSeconds(30)
            }
        End Sub
        
        ''' <summary>
        ''' Check if Pi service is healthy and Coral TPU is available
        ''' </summary>
        Public Async Function HealthCheckAsync() As Task(Of Boolean)
            Try
                Dim response = Await _httpClient.GetAsync("/health")
                
                If Not response.IsSuccessStatusCode Then
                    Console.WriteLine($"[PiClient] Health check failed: {response.StatusCode}")
                    Return False
                End If
                
                Dim json = Await response.Content.ReadAsStringAsync()
                Dim health = JsonConvert.DeserializeObject(Of Dictionary(Of String, Object))(json)
                
                Dim tpuAvailable = If(health.ContainsKey("tpu"), Convert.ToBoolean(health("tpu")), False)
                Dim modelLoaded = If(health.ContainsKey("model_loaded"), Convert.ToBoolean(health("model_loaded")), False)
                
                Console.WriteLine($"[PiClient] Health check OK (TPU={tpuAvailable}, Model={modelLoaded})")
                Return tpuAvailable AndAlso modelLoaded
                
            Catch ex As Exception
                Console.WriteLine($"[ERROR] Pi health check failed: {ex.Message}")
                Return False
            End Try
        End Function
        
        ''' <summary>
        ''' Get prediction from Pi model
        ''' </summary>
        Public Async Function PredictAsync(request As PredictionRequest) As Task(Of PredictionResponse)
            Try
                Dim json = JsonConvert.SerializeObject(request)
                Dim content As New StringContent(json, Encoding.UTF8, "application/json")
                
                Dim sw = Diagnostics.Stopwatch.StartNew()
                Dim response = Await _httpClient.PostAsync("/predict", content)
                sw.Stop()
                
                If Not response.IsSuccessStatusCode Then
                    Console.WriteLine($"[ERROR] Pi prediction failed: {response.StatusCode}")
                    Return Nothing
                End If
                
                Dim responseJson = Await response.Content.ReadAsStringAsync()
                Dim prediction = JsonConvert.DeserializeObject(Of PredictionResponse)(responseJson)
                
                Console.WriteLine($"[PiClient] Prediction for {request.PlayerId} {request.Market} {request.Line}: prob={prediction.TrueProb:F3}, EV={prediction.ExpectedValue:F2}, confidence={prediction.Confidence:F2} ({sw.ElapsedMilliseconds}ms)")
                
                Return prediction
                
            Catch ex As HttpRequestException
                Console.WriteLine($"[ERROR] HTTP error during prediction: {ex.Message}")
                Return Nothing
            Catch ex As JsonException
                Console.WriteLine($"[ERROR] JSON error during prediction: {ex.Message}")
                Return Nothing
            End Try
        End Function
        
        ''' <summary>
        ''' Batch prediction for multiple props (more efficient)
        ''' </summary>
        Public Async Function PredictBatchAsync(requests As List(Of PredictionRequest)) As Task(Of List(Of PredictionResponse))
            Try
                Dim json = JsonConvert.SerializeObject(requests)
                Dim content As New StringContent(json, Encoding.UTF8, "application/json")
                
                Dim sw = Diagnostics.Stopwatch.StartNew()
                Dim response = Await _httpClient.PostAsync("/predict/batch", content)
                sw.Stop()
                
                If Not response.IsSuccessStatusCode Then
                    Console.WriteLine($"[ERROR] Pi batch prediction failed: {response.StatusCode}")
                    Return New List(Of PredictionResponse)
                End If
                
                Dim responseJson = Await response.Content.ReadAsStringAsync()
                Dim predictions = JsonConvert.DeserializeObject(Of List(Of PredictionResponse))(responseJson)
                
                Console.WriteLine($"[PiClient] Batch prediction complete: {predictions.Count}/{requests.Count} successful ({sw.ElapsedMilliseconds}ms, {sw.ElapsedMilliseconds / requests.Count}ms avg)")
                
                Return predictions
                
            Catch ex As Exception
                Console.WriteLine($"[ERROR] Batch prediction failed: {ex.Message}")
                Return New List(Of PredictionResponse)
            End Try
        End Function
        
        ''' <summary>
        ''' Execute command on Pi via SSH (for maintenance, model updates)
        ''' </summary>
        Public Function ExecuteSsh(command As String) As String
            Try
                Using client As New SshClient(_piHost, _sshUser, New PrivateKeyFile(_sshKeyPath))
                    client.Connect()
                    
                    If Not client.IsConnected Then
                        Console.WriteLine("[ERROR] SSH connection failed")
                        Return Nothing
                    End If
                    
                    Console.WriteLine($"[PiClient] Executing SSH command: {command}")
                    
                    Using cmd = client.CreateCommand(command)
                        Dim result = cmd.Execute()
                        Dim exitStatus = cmd.ExitStatus
                        
                        If exitStatus <> 0 Then
                            Console.WriteLine($"[WARNING] SSH command exited with status {exitStatus}")
                            Console.WriteLine($"STDERR: {cmd.Error}")
                        End If
                        
                        client.Disconnect()
                        Return result
                    End Using
                End Using
                
            Catch ex As Exception
                Console.WriteLine($"[ERROR] SSH execution failed: {ex.Message}")
                Return Nothing
            End Try
        End Function
        
        ''' <summary>
        ''' Update model on Pi (upload new .tflite file)
        ''' </summary>
        Public Function UpdateModel(localModelPath As String, remoteModelPath As String) As Boolean
            Try
                Using client As New SftpClient(_piHost, _sshUser, New PrivateKeyFile(_sshKeyPath))
                    client.Connect()
                    
                    If Not client.IsConnected Then
                        Console.WriteLine("[ERROR] SFTP connection failed")
                        Return False
                    End If
                    
                    Console.WriteLine($"[PiClient] Uploading model: {localModelPath} → {remoteModelPath}")
                    
                    Using fileStream = System.IO.File.OpenRead(localModelPath)
                        client.UploadFile(fileStream, remoteModelPath, True)
                    End Using
                    
                    client.Disconnect()
                    Console.WriteLine("[PiClient] Model upload complete")
                    
                    ' Restart Pi service to load new model
                    Dim restartResult = ExecuteSsh("sudo systemctl restart eq12-inference")
                    Console.WriteLine($"[PiClient] Service restart: {restartResult}")
                    
                    Return True
                    
                End Using
                
            Catch ex As Exception
                Console.WriteLine($"[ERROR] Model update failed: {ex.Message}")
                Return False
            End Try
        End Function
        
        ''' <summary>
        ''' Get TPU stats from Pi
        ''' </summary>
        Public Async Function GetTpuStatsAsync() As Task(Of Dictionary(Of String, Object))
            Try
                Dim response = Await _httpClient.GetAsync("/stats/tpu")
                
                If Not response.IsSuccessStatusCode Then
                    Return New Dictionary(Of String, Object)
                End If
                
                Dim json = Await response.Content.ReadAsStringAsync()
                Dim stats = JsonConvert.DeserializeObject(Of Dictionary(Of String, Object))(json)
                
                Console.WriteLine($"[PiClient] TPU Stats: Temperature={stats("temperature")}°C, Utilization={stats("utilization")}%")
                
                Return stats
                
            Catch ex As Exception
                Console.WriteLine($"[ERROR] Failed to get TPU stats: {ex.Message}")
                Return New Dictionary(Of String, Object)
            End Try
        End Function
        
    End Class
    
End Namespace
