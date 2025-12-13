Option Strict On
Option Explicit On

Imports System.Net.Http
Imports System.Net.Http.Headers
Imports System.Threading.Tasks

Namespace EQ12.Core.ApiClient

    ''' <summary>
    ''' Base class for all EQ12 API clients
    ''' Provides shared HTTP functionality, error handling, and retry logic
    ''' </summary>
    Public MustInherit Class ApiClientBase
        Implements IDisposable

        Protected ReadOnly Http As HttpClient
        Protected ReadOnly ApiInfo As ApiInfo
        
        Private _disposed As Boolean = False

        Protected Sub New(apiInfo As ApiInfo, Optional authToken As String = Nothing)
            If apiInfo Is Nothing Then
                Throw New ArgumentNullException(NameOf(apiInfo))
            End If

            Me.ApiInfo = apiInfo
            Http = New HttpClient() With {
                .BaseAddress = New Uri(apiInfo.BaseUrl),
                .Timeout = TimeSpan.FromSeconds(30)
            }

            ' Configure authentication based on API type
            ConfigureAuthentication(authToken)
            
            ' Set default headers
            Http.DefaultRequestHeaders.Add("User-Agent", "EQ12-Sports-Betting-Orchestrator/1.0")
        End Sub

        Private Sub ConfigureAuthentication(authToken As String)
            If String.IsNullOrWhiteSpace(authToken) Then
                ' Try to load from environment variable
                If Not String.IsNullOrWhiteSpace(ApiInfo.EnvironmentVariableName) Then
                    authToken = Environment.GetEnvironmentVariable(ApiInfo.EnvironmentVariableName)
                End If
            End If

            If String.IsNullOrWhiteSpace(authToken) AndAlso ApiInfo.AuthType <> "None" Then
                Console.WriteLine($"⚠️  Warning: No auth token for {ApiInfo.Name} (expected: {ApiInfo.EnvironmentVariableName})")
            End If

            Select Case ApiInfo.AuthType
                Case "Bearer token"
                    If Not String.IsNullOrWhiteSpace(authToken) Then
                        Http.DefaultRequestHeaders.Authorization = New AuthenticationHeaderValue("Bearer", authToken)
                    End If
                    
                Case "API Key (header: x-rapidapi-key)"
                    If Not String.IsNullOrWhiteSpace(authToken) Then
                        Http.DefaultRequestHeaders.Add("x-rapidapi-key", authToken)
                    End If
                    
                Case "API Key (header: x-apisports-key)"
                    If Not String.IsNullOrWhiteSpace(authToken) Then
                        Http.DefaultRequestHeaders.Add("x-apisports-key", authToken)
                    End If
                    
                ' Querystring auth handled per-request in child classes
                ' User-Agent auth (SEC EDGAR) already set above
            End Select
        End Sub

        ''' <summary>
        ''' Execute GET request with automatic retry and error handling
        ''' </summary>
        Protected Async Function GetAsync(url As String, Optional maxRetries As Integer = 3) As Task(Of String)
            Dim attempt As Integer = 0
            Dim lastException As Exception = Nothing

            While attempt < maxRetries
                Try
                    attempt += 1
                    
                    Dim response = Await Http.GetAsync(url)
                    
                    If response.IsSuccessStatusCode Then
                        ApiInfo.SuccessCount += 1
                        ApiInfo.IsHealthy = True
                        ApiInfo.LastChecked = DateTime.UtcNow
                        Return Await response.Content.ReadAsStringAsync()
                    Else
                        ApiInfo.ErrorCount += 1
                        Throw New HttpRequestException($"HTTP {CInt(response.StatusCode)}: {response.ReasonPhrase}")
                    End If
                    
                Catch ex As Exception
                    lastException = ex
                    ApiInfo.ErrorCount += 1
                    
                    If attempt < maxRetries Then
                        ' Exponential backoff: 1s, 2s, 4s
                        Dim delayMs = CInt(Math.Pow(2, attempt - 1) * 1000)
                        Console.WriteLine($"⚠️  {ApiInfo.Name} attempt {attempt} failed, retrying in {delayMs}ms...")
                        Await Task.Delay(delayMs)
                    End If
                End Try
            End While

            ' All retries failed
            ApiInfo.IsHealthy = False
            ApiInfo.LastChecked = DateTime.UtcNow
            Throw New Exception($"{ApiInfo.Name} failed after {maxRetries} attempts", lastException)
        End Function

        ''' <summary>
        ''' Execute POST request with automatic retry
        ''' </summary>
        Protected Async Function PostAsync(url As String, content As HttpContent, Optional maxRetries As Integer = 3) As Task(Of String)
            Dim attempt As Integer = 0
            Dim lastException As Exception = Nothing

            While attempt < maxRetries
                Try
                    attempt += 1
                    
                    Dim response = Await Http.PostAsync(url, content)
                    
                    If response.IsSuccessStatusCode Then
                        ApiInfo.SuccessCount += 1
                        ApiInfo.IsHealthy = True
                        ApiInfo.LastChecked = DateTime.UtcNow
                        Return Await response.Content.ReadAsStringAsync()
                    Else
                        ApiInfo.ErrorCount += 1
                        Throw New HttpRequestException($"HTTP {CInt(response.StatusCode)}: {response.ReasonPhrase}")
                    End If
                    
                Catch ex As Exception
                    lastException = ex
                    ApiInfo.ErrorCount += 1
                    
                    If attempt < maxRetries Then
                        Dim delayMs = CInt(Math.Pow(2, attempt - 1) * 1000)
                        Await Task.Delay(delayMs)
                    End If
                End Try
            End While

            ApiInfo.IsHealthy = False
            ApiInfo.LastChecked = DateTime.UtcNow
            Throw New Exception($"{ApiInfo.Name} POST failed after {maxRetries} attempts", lastException)
        End Function

        ''' <summary>
        ''' Test API connectivity (override in child classes)
        ''' </summary>
        Public MustOverride Function TestConnectionAsync() As Task(Of String)

        Protected Overridable Sub Dispose(disposing As Boolean)
            If Not _disposed Then
                If disposing Then
                    Http?.Dispose()
                End If
                _disposed = True
            End If
        End Sub

        Public Sub Dispose() Implements IDisposable.Dispose
            Dispose(True)
            GC.SuppressFinalize(Me)
        End Sub

    End Class

End Namespace
