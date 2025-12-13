Imports System.Net.Http
Imports System.Text
Imports System.Threading.Tasks
Imports Newtonsoft.Json
Imports Newtonsoft.Json.Linq
Imports System.Data.SQLite
Imports System.IO

''' <summary>
''' Google Apps Script Client for EQ12 Integration
''' Provides signed HTTP communication with GAS Web App endpoints
''' Handles authentication, retries, and comprehensive logging
''' </summary>
Public Class GASClient
    Private ReadOnly _baseUrl As String
    Private ReadOnly _sharedSecret As String
    Private ReadOnly _httpClient As HttpClient
    Private ReadOnly _dbPath As String
    Private ReadOnly _maxRetries As Integer = 3
    Private ReadOnly _timeoutSeconds As Integer = 30

    Public Sub New(baseUrl As String, sharedSecret As String, Optional dbPath As String = "")
        If String.IsNullOrEmpty(baseUrl) Then
            Throw New ArgumentException("Base URL cannot be empty", NameOf(baseUrl))
        End If

        If String.IsNullOrEmpty(sharedSecret) Then
            Throw New ArgumentException("Shared secret cannot be empty", NameOf(sharedSecret))
        End If

        _baseUrl = baseUrl.TrimEnd("/"c)
        _sharedSecret = sharedSecret
        _dbPath = If(String.IsNullOrEmpty(dbPath), "Data/eq12_terminal.db", dbPath)

        ' Configure HTTP client with timeout and headers
        _httpClient = New HttpClient() With {
            .Timeout = TimeSpan.FromSeconds(_timeoutSeconds)
        }
        _httpClient.DefaultRequestHeaders.Add("User-Agent", "EQ12-Terminal/1.0")

        ' Initialize database table if needed
        InitializeDatabase()
    End Sub

    ''' <summary>
    ''' Execute GET request to GAS endpoint with authentication
    ''' </summary>
    ''' <param name="action">Action to perform (pull, status, health)</param>
    ''' <param name="parameters">Query parameters</param>
    ''' <returns>Parsed JSON response</returns>
    Public Async Function GetJsonAsync(action As String, parameters As Dictionary(Of String, String)) As Task(Of JObject)
        If String.IsNullOrEmpty(action) Then
            Throw New ArgumentException("Action cannot be empty", NameOf(action))
        End If

        If parameters Is Nothing Then
            parameters = New Dictionary(Of String, String)()
        End If

        ' Add authentication and action to parameters
        parameters("secret") = _sharedSecret
        parameters("action") = action

        ' Build query string
        Dim queryString = String.Join("&",
            parameters.Select(Function(kv) $"{Uri.EscapeDataString(kv.Key)}={Uri.EscapeDataString(kv.Value)}")
        )

        Dim uri = $"{_baseUrl}?{queryString}"

        ' Execute with retry logic
        For attempt As Integer = 1 To _maxRetries
            Try
                LogGASActivity("GET", action, $"Attempt {attempt}", "started")

                Dim response = Await _httpClient.GetStringAsync(uri)
                Dim jsonResponse = JObject.Parse(response)

                ' Check if GAS returned an error
                If Not jsonResponse.Value(Of Boolean)("ok") Then
                    Dim errorMsg = jsonResponse.Value(Of String)("error")
                    Throw New InvalidOperationException($"GAS Error: {errorMsg}")
                End If

                LogGASActivity("GET", action, $"Success on attempt {attempt}", "success", response.Length)
                Return jsonResponse

            Catch ex As Exception When attempt < _maxRetries
                LogGASActivity("GET", action, $"Attempt {attempt} failed: {ex.Message}", "retry")

                ' Wait before retry with exponential backoff
                Await Task.Delay(1000 * attempt)
            Catch ex As Exception
                LogGASActivity("GET", action, $"Final failure: {ex.Message}", "failed")
                Throw New Exception($"GAS GET failed after {_maxRetries} attempts: {ex.Message}", ex)
            End Try
        Next

        Throw New Exception("Should not reach here")
    End Function

    ''' <summary>
    ''' Execute POST request to GAS endpoint with JSON payload
    ''' </summary>
    ''' <param name="payload">JSON payload to send</param>
    ''' <returns>Parsed JSON response</returns>
    Public Async Function PostJsonAsync(payload As JObject) As Task(Of JObject)
        If payload Is Nothing Then
            Throw New ArgumentNullException(NameOf(payload))
        End If

        ' Add authentication to payload
        payload("secret") = _sharedSecret

        Dim jsonString = payload.ToString(Formatting.None)

        ' Execute with retry logic
        For attempt As Integer = 1 To _maxRetries
            Try
                LogGASActivity("POST", payload.Value(Of String)("action") ?? "unknown", $"Attempt {attempt}", "started")

                Using content As New StringContent(jsonString, Encoding.UTF8, "application/json")
                    ' Add shared secret header as backup auth method
                    content.Headers.Add("X-Shared-Secret", _sharedSecret)

                    Using response = Await _httpClient.PostAsync(_baseUrl, content)
                        response.EnsureSuccessStatusCode()

                        Dim responseString = Await response.Content.ReadAsStringAsync()
                        Dim jsonResponse = JObject.Parse(responseString)

                        ' Check if GAS returned an error
                        If Not jsonResponse.Value(Of Boolean)("ok") Then
                            Dim errorMsg = jsonResponse.Value(Of String)("error")
                            Throw New InvalidOperationException($"GAS Error: {errorMsg}")
                        End If

                        LogGASActivity("POST", payload.Value(Of String)("action") ?? "unknown",
                                     $"Success on attempt {attempt}", "success", responseString.Length)
                        Return jsonResponse
                    End Using
                End Using

            Catch ex As Exception When attempt < _maxRetries
                LogGASActivity("POST", payload.Value(Of String)("action") ?? "unknown",
                             $"Attempt {attempt} failed: {ex.Message}", "retry")

                ' Wait before retry with exponential backoff
                Await Task.Delay(1000 * attempt)
            Catch ex As Exception
                LogGASActivity("POST", payload.Value(Of String)("action") ?? "unknown",
                             $"Final failure: {ex.Message}", "failed")
                Throw New Exception($"GAS POST failed after {_maxRetries} attempts: {ex.Message}", ex)
            End Try
        Next

        Throw New Exception("Should not reach here")
    End Function

    ''' <summary>
    ''' Check GAS endpoint health
    ''' </summary>
    ''' <returns>Health status information</returns>
    Public Async Function CheckHealthAsync() As Task(Of Boolean)
        Try
            Dim healthResponse = Await GetJsonAsync("health", New Dictionary(Of String, String)())
            Return healthResponse.Value(Of String)("status") = "ok"
        Catch
            Return False
        End Try
    End Function

    ''' <summary>
    ''' Get GAS system status with spreadsheet information
    ''' </summary>
    ''' <returns>Status information</returns>
    Public Async Function GetStatusAsync() As Task(Of JObject)
        Return Await GetJsonAsync("status", New Dictionary(Of String, String)())
    End Function

    ''' <summary>
    ''' Initialize database table for logging
    ''' </summary>
    Private Sub InitializeDatabase()
        Try
            If Not File.Exists(_dbPath) Then
                Directory.CreateDirectory(Path.GetDirectoryName(_dbPath))
            End If

            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                Dim createTableSql = "
                CREATE TABLE IF NOT EXISTS gas_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT (datetime('now')),
                    method TEXT NOT NULL,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT,
                    response_size INTEGER DEFAULT 0
                )"

                Using cmd As New SQLiteCommand(createTableSql, conn)
                    cmd.ExecuteNonQuery()
                End Using
            End Using

        Catch ex As Exception
            ' Log to console if database initialization fails
            Console.WriteLine($"GASClient database init failed: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Log GAS activity to database for monetization tracking
    ''' </summary>
    ''' <param name="method">HTTP method (GET/POST)</param>
    ''' <param name="action">GAS action performed</param>
    ''' <param name="details">Detailed information</param>
    ''' <param name="status">Operation status</param>
    ''' <param name="responseSize">Response size in bytes</param>
    Private Sub LogGASActivity(method As String, action As String, details As String,
                              status As String, Optional responseSize As Integer = 0)
        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                Dim insertSql = "
                INSERT INTO gas_logs (method, action, status, details, response_size)
                VALUES (@method, @action, @status, @details, @response_size)"

                Using cmd As New SQLiteCommand(insertSql, conn)
                    cmd.Parameters.AddWithValue("@method", method)
                    cmd.Parameters.AddWithValue("@action", action)
                    cmd.Parameters.AddWithValue("@status", status)
                    cmd.Parameters.AddWithValue("@details", details)
                    cmd.Parameters.AddWithValue("@response_size", responseSize)
                    cmd.ExecuteNonQuery()
                End Using
            End Using

        Catch ex As Exception
            ' Don't throw on logging failure - just write to console
            Console.WriteLine($"GAS logging failed: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Get recent GAS activity logs for monitoring
    ''' </summary>
    ''' <param name="limit">Number of recent logs to retrieve</param>
    ''' <returns>List of log entries</returns>
    Public Function GetRecentLogs(Optional limit As Integer = 50) As List(Of Object)
        Dim logs As New List(Of Object)()

        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                Dim selectSql = $"
                SELECT timestamp, method, action, status, details, response_size
                FROM gas_logs
                ORDER BY timestamp DESC
                LIMIT {limit}"

                Using cmd As New SQLiteCommand(selectSql, conn)
                    Using reader = cmd.ExecuteReader()
                        While reader.Read()
                            logs.Add(New With {
                                .Timestamp = reader("timestamp").ToString(),
                                .Method = reader("method").ToString(),
                                .Action = reader("action").ToString(),
                                .Status = reader("status").ToString(),
                                .Details = reader("details").ToString(),
                                .ResponseSize = Convert.ToInt32(reader("response_size"))
                            })
                        End While
                    End Using
                End Using
            End Using

        Catch ex As Exception
            Console.WriteLine($"Failed to retrieve GAS logs: {ex.Message}")
        End Try

        Return logs
    End Function

    ''' <summary>
    ''' Clean up resources
    ''' </summary>
    Public Sub Dispose()
        _httpClient?.Dispose()
    End Sub

    Protected Overrides Sub Finalize()
        Dispose()
        MyBase.Finalize()
    End Sub
End Class
