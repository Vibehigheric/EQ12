Imports System.IO
Imports System.Net.Http
Imports System.Text
Imports System.Web
Imports Newtonsoft.Json.Linq
Imports Newtonsoft.Json
Imports System.Diagnostics
Imports System.Threading

''' <summary>
''' Google Auth Helper - OAuth2 Authentication for Google APIs
''' Handles authentication for Google Drive, Sheets, and other Google services
''' Features: OAuth2 flow, token management, automatic refresh, secure storage
''' </summary>
Public Class GoogleAuthHelper
    Private Shared ReadOnly client As New HttpClient()

    ''' <summary>
    ''' Generate Google OAuth2 authorization URL for initial setup
    ''' </summary>
    ''' <param name="config">Configuration containing Google API settings</param>
    ''' <param name="service">Service type: 'drive' or 'sheets'</param>
    ''' <returns>Authorization URL for user to visit</returns>
    Public Shared Function GenerateAuthUrl(config As JObject, service As String) As String
        Try
            Dim googleConfig = GetGoogleConfig(config, service)
            If googleConfig Is Nothing Then
                Return "Error: Google configuration not found"
            End If

            Dim clientId = googleConfig("client_id").ToString()
            Dim redirectUri = googleConfig("redirect_uri").ToString()
            Dim scope = googleConfig("scope").ToString()

            Dim authUrl = "https://accounts.google.com/o/oauth2/auth" &
                         "?client_id=" & HttpUtility.UrlEncode(clientId) &
                         "&redirect_uri=" & HttpUtility.UrlEncode(redirectUri) &
                         "&scope=" & HttpUtility.UrlEncode(scope) &
                         "&response_type=code" &
                         "&access_type=offline" &
                         "&prompt=consent"

            Return authUrl

        Catch ex As Exception
            Return $"Error generating auth URL: {ex.Message}"
        End Try
    End Function

    ''' <summary>
    ''' Exchange authorization code for access and refresh tokens
    ''' </summary>
    ''' <param name="config">Configuration containing Google API settings</param>
    ''' <param name="service">Service type: 'drive' or 'sheets'</param>
    ''' <param name="authCode">Authorization code from OAuth callback</param>
    ''' <returns>Success status message</returns>
    Public Shared Function ExchangeCodeForTokens(config As JObject, service As String, authCode As String) As String
        Try
            Dim googleConfig = GetGoogleConfig(config, service)
            If googleConfig Is Nothing Then
                Return "Error: Google configuration not found"
            End If

            Dim clientId = googleConfig("client_id").ToString()
            Dim clientSecret = googleConfig("client_secret").ToString()
            Dim redirectUri = googleConfig("redirect_uri").ToString()
            Dim tokenPath = googleConfig("token_path").ToString()

            ' Prepare token exchange request
            Dim tokenData = New Dictionary(Of String, String) From {
                {"code", authCode},
                {"client_id", clientId},
                {"client_secret", clientSecret},
                {"redirect_uri", redirectUri},
                {"grant_type", "authorization_code"}
            }

            Dim formContent = New FormUrlEncodedContent(tokenData)
            Dim response = client.PostAsync("https://oauth2.googleapis.com/token", formContent).Result

            If response.IsSuccessStatusCode Then
                Dim responseContent = response.Content.ReadAsStringAsync().Result
                Dim tokenResponse = JObject.Parse(responseContent)

                ' Add timestamp for token management
                tokenResponse("created_at") = DateTimeOffset.UtcNow.ToUnixTimeSeconds()
                tokenResponse("service") = service

                ' Ensure token directory exists
                Dim tokenDir = Path.GetDirectoryName(tokenPath)
                If Not Directory.Exists(tokenDir) Then
                    Directory.CreateDirectory(tokenDir)
                End If

                ' Save tokens to file
                File.WriteAllText(tokenPath, tokenResponse.ToString(Formatting.Indented))

                Return $"✅ {service.ToUpper()} tokens saved successfully to {tokenPath}"
            Else
                Dim errorContent = response.Content.ReadAsStringAsync().Result
                Return $"❌ Token exchange failed: {response.StatusCode} - {errorContent}"
            End If

        Catch ex As Exception
            Return $"❌ Token exchange error: {ex.Message}"
        End Try
    End Function

    ''' <summary>
    ''' Get valid access token (refresh if necessary)
    ''' </summary>
    ''' <param name="config">Configuration containing Google API settings</param>
    ''' <param name="service">Service type: 'drive' or 'sheets'</param>
    ''' <returns>Valid access token or error message</returns>
    Public Shared Function GetAccessToken(config As JObject, service As String) As String
        Try
            Dim googleConfig = GetGoogleConfig(config, service)
            If googleConfig Is Nothing Then
                Return "Error: Google configuration not found"
            End If

            Dim tokenPath = googleConfig("token_path").ToString()

            If Not File.Exists(tokenPath) Then
                Return $"Error: Token file not found. Please run authentication first."
            End If

            Dim tokenData = JObject.Parse(File.ReadAllText(tokenPath))

            ' Check if token needs refresh (expires in 1 hour, refresh if older than 50 minutes)
            Dim createdAt = tokenData("created_at")?.ToObject(Of Long)()
            Dim expiresIn = tokenData("expires_in")?.ToObject(Of Integer)()
            Dim currentTime = DateTimeOffset.UtcNow.ToUnixTimeSeconds()

            If createdAt.HasValue AndAlso expiresIn.HasValue Then
                Dim tokenAge = currentTime - createdAt.Value
                If tokenAge >= (expiresIn.Value - 600) Then ' Refresh 10 minutes before expiry
                    Dim refreshResult = RefreshAccessToken(config, service, tokenData)
                    If refreshResult.StartsWith("Error") Then
                        Return refreshResult
                    End If
                    ' Reload refreshed token
                    tokenData = JObject.Parse(File.ReadAllText(tokenPath))
                End If
            End If

            Return tokenData("access_token")?.ToString() ?? "Error: No access token found"

        Catch ex As Exception
            Return $"Error getting access token: {ex.Message}"
        End Try
    End Function

    ''' <summary>
    ''' Refresh access token using refresh token
    ''' </summary>
    Private Shared Function RefreshAccessToken(config As JObject, service As String, tokenData As JObject) As String
        Try
            Dim googleConfig = GetGoogleConfig(config, service)
            Dim refreshToken = tokenData("refresh_token")?.ToString()

            If String.IsNullOrEmpty(refreshToken) Then
                Return "Error: No refresh token available"
            End If

            Dim clientId = googleConfig("client_id").ToString()
            Dim clientSecret = googleConfig("client_secret").ToString()

            Dim refreshData = New Dictionary(Of String, String) From {
                {"refresh_token", refreshToken},
                {"client_id", clientId},
                {"client_secret", clientSecret},
                {"grant_type", "refresh_token"}
            }

            Dim formContent = New FormUrlEncodedContent(refreshData)
            Dim response = client.PostAsync("https://oauth2.googleapis.com/token", formContent).Result

            If response.IsSuccessStatusCode Then
                Dim responseContent = response.Content.ReadAsStringAsync().Result
                Dim refreshResponse = JObject.Parse(responseContent)

                ' Update token data
                tokenData("access_token") = refreshResponse("access_token")
                tokenData("created_at") = DateTimeOffset.UtcNow.ToUnixTimeSeconds()

                If refreshResponse("refresh_token") IsNot Nothing Then
                    tokenData("refresh_token") = refreshResponse("refresh_token")
                End If

                ' Save updated tokens
                Dim tokenPath = googleConfig("token_path").ToString()
                File.WriteAllText(tokenPath, tokenData.ToString(Formatting.Indented))

                Console.WriteLine($"✅ {service.ToUpper()} access token refreshed successfully")
                Return "Success"
            Else
                Return $"Error refreshing token: {response.StatusCode}"
            End If

        Catch ex As Exception
            Return $"Error refreshing token: {ex.Message}"
        End Try
    End Function

    ''' <summary>
    ''' Start OAuth2 authentication flow with local callback server
    ''' </summary>
    ''' <param name="config">Configuration containing Google API settings</param>
    ''' <param name="service">Service type: 'drive' or 'sheets'</param>
    ''' <returns>Success or error message</returns>
    Public Shared Function StartAuthFlow(config As JObject, service As String) As String
        Try
            Dim authUrl = GenerateAuthUrl(config, service)
            If authUrl.StartsWith("Error") Then
                Return authUrl
            End If

            Console.WriteLine($"🔑 Starting {service.ToUpper()} OAuth2 authentication...")
            Console.WriteLine($"Opening browser to: {authUrl}")
            Console.WriteLine("Please authorize the application and copy the authorization code.")
            Console.WriteLine("The browser will redirect to localhost - copy the 'code' parameter from the URL.")

            ' Open browser (optional)
            Try
                Process.Start(New ProcessStartInfo(authUrl) With {.UseShellExecute = True})
            Catch
                Console.WriteLine("Could not open browser automatically. Please visit the URL manually.")
            End Try

            Console.Write("Enter the authorization code: ")
            Dim authCode = Console.ReadLine()?.Trim()

            If String.IsNullOrEmpty(authCode) Then
                Return "Error: No authorization code provided"
            End If

            Return ExchangeCodeForTokens(config, service, authCode)

        Catch ex As Exception
            Return $"Error in auth flow: {ex.Message}"
        End Try
    End Function

    ''' <summary>
    ''' Test Google API connectivity
    ''' </summary>
    ''' <param name="config">Configuration containing Google API settings</param>
    ''' <param name="service">Service type: 'drive' or 'sheets'</param>
    ''' <returns>Test result message</returns>
    Public Shared Function TestConnection(config As JObject, service As String) As String
        Try
            Dim accessToken = GetAccessToken(config, service)
            If accessToken.StartsWith("Error") Then
                Return accessToken
            End If

            ' Test API call based on service
            Dim testUrl As String
            Select Case service.ToLower()
                Case "drive"
                    testUrl = "https://www.googleapis.com/drive/v3/about?fields=user"
                Case "sheets"
                    testUrl = "https://sheets.googleapis.com/v4/spreadsheets/test/values/A1"
                Case Else
                    Return "Error: Unsupported service type"
            End Select

            Using testClient As New HttpClient()
                testClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {accessToken}")

                Dim response = testClient.GetAsync(testUrl).Result

                If response.IsSuccessStatusCode OrElse response.StatusCode = Net.HttpStatusCode.NotFound Then
                    Return $"✅ {service.ToUpper()} API connection successful"
                Else
                    Return $"❌ {service.ToUpper()} API test failed: {response.StatusCode}"
                End If
            End Using

        Catch ex As Exception
            Return $"❌ {service.ToUpper()} connection test error: {ex.Message}"
        End Try
    End Function

    ''' <summary>
    ''' Get Google service configuration from main config
    ''' </summary>
    Private Shared Function GetGoogleConfig(config As JObject, service As String) As JObject
        Try
            Select Case service.ToLower()
                Case "drive"
                    Return config("google_drive")
                Case "sheets"
                    Return config("google_sheets")
                Case Else
                    Return Nothing
            End Select
        Catch
            Return Nothing
        End Try
    End Function

    ''' <summary>
    ''' Validate Google service configuration
    ''' </summary>
    ''' <param name="config">Configuration containing Google API settings</param>
    ''' <param name="service">Service type: 'drive' or 'sheets'</param>
    ''' <returns>True if configuration is valid</returns>
    Public Shared Function ValidateConfig(config As JObject, service As String) As Boolean
        Try
            Dim googleConfig = GetGoogleConfig(config, service)
            If googleConfig Is Nothing Then Return False

            Dim requiredKeys = {"client_id", "client_secret", "redirect_uri", "scope", "token_path"}

            For Each key In requiredKeys
                If Not googleConfig.ContainsKey(key) OrElse String.IsNullOrEmpty(googleConfig(key)?.ToString()) Then
                    Return False
                End If
            Next

            Return True

        Catch
            Return False
        End Try
    End Function

    ''' <summary>
    ''' Get authentication status for service
    ''' </summary>
    ''' <param name="config">Configuration containing Google API settings</param>
    ''' <param name="service">Service type: 'drive' or 'sheets'</param>
    ''' <returns>Authentication status message</returns>
    Public Shared Function GetAuthStatus(config As JObject, service As String) As String
        Try
            If Not ValidateConfig(config, service) Then
                Return $"❌ {service.ToUpper()} configuration incomplete"
            End If

            Dim googleConfig = GetGoogleConfig(config, service)
            Dim tokenPath = googleConfig("token_path").ToString()

            If Not File.Exists(tokenPath) Then
                Return $"⚠️ {service.ToUpper()} not authenticated - run auth flow"
            End If

            Dim tokenData = JObject.Parse(File.ReadAllText(tokenPath))
            Dim createdAt = tokenData("created_at")?.ToObject(Of Long)()

            If createdAt.HasValue Then
                Dim age = DateTimeOffset.UtcNow.ToUnixTimeSeconds() - createdAt.Value
                Dim ageMinutes = Math.Round(age / 60.0, 1)
                Return $"✅ {service.ToUpper()} authenticated ({ageMinutes} minutes ago)"
            Else
                Return $"✅ {service.ToUpper()} authenticated (unknown age)"
            End If

        Catch ex As Exception
            Return $"❌ {service.ToUpper()} auth status error: {ex.Message}"
        End Try
    End Function
End Class
