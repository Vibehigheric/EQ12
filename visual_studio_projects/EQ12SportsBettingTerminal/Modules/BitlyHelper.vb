Imports System.Net.Http
Imports System.Text
Imports Newtonsoft.Json.Linq

''' <summary>
''' Bitly URL Shortening Helper for EQ12 Sports Betting Terminal
''' Provides URL shortening for GitHub Gist links in reports and alerts
''' </summary>
Public Class BitlyHelper
    ''' <summary>
    ''' Shorten a long URL using Bitly API
    ''' </summary>
    ''' <param name="token">Bitly Generic Access Token</param>
    ''' <param name="longUrl">The URL to shorten</param>
    ''' <returns>Shortened Bitly URL or original URL if failed</returns>
    Public Shared Function Shorten(token As String, longUrl As String) As String
        Try
            ' Validate inputs
            If String.IsNullOrWhiteSpace(token) OrElse String.IsNullOrWhiteSpace(longUrl) Then
                Return longUrl
            End If

            Using client As New HttpClient()
                ' Set authorization header
                client.DefaultRequestHeaders.Add("Authorization", "Bearer " & token)

                ' Create request body
                Dim requestBody = New JObject From {
                    {"long_url", longUrl},
                    {"domain", "bit.ly"}
                }

                ' Make API request
                Dim content = New StringContent(requestBody.ToString(), Encoding.UTF8, "application/json")
                Dim response = client.PostAsync("https://api-ssl.bitly.com/v4/shorten", content).Result

                If response.IsSuccessStatusCode Then
                    Dim responseJson = response.Content.ReadAsStringAsync().Result
                    Dim parsed = JObject.Parse(responseJson)

                    If parsed("link") IsNot Nothing Then
                        Dim shortUrl = parsed("link").ToString()
                        Console.WriteLine($"✅ Shortened URL: {longUrl} → {shortUrl}")
                        Return shortUrl
                    End If
                Else
                    Console.WriteLine($"⚠️ Bitly API error: {response.StatusCode} - {response.ReasonPhrase}")
                End If

            End Using
        Catch ex As Exception
            Console.WriteLine($"⚠️ Bitly shortening failed: {ex.Message}")
        End Try

        ' Return original URL if shortening failed
        Return longUrl
    End Function

    ''' <summary>
    ''' Shorten a long URL using Bitly API with custom domain
    ''' </summary>
    ''' <param name="token">Bitly Generic Access Token</param>
    ''' <param name="longUrl">The URL to shorten</param>
    ''' <param name="domain">Custom Bitly domain (default: bit.ly)</param>
    ''' <returns>Shortened Bitly URL or original URL if failed</returns>
    Public Shared Function Shorten(token As String, longUrl As String, domain As String) As String
        Try
            ' Validate inputs
            If String.IsNullOrWhiteSpace(token) OrElse String.IsNullOrWhiteSpace(longUrl) Then
                Return longUrl
            End If

            If String.IsNullOrWhiteSpace(domain) Then domain = "bit.ly"

            Using client As New HttpClient()
                ' Set authorization header
                client.DefaultRequestHeaders.Add("Authorization", "Bearer " & token)

                ' Create request body with custom domain
                Dim requestBody = New JObject From {
                    {"long_url", longUrl},
                    {"domain", domain}
                }

                ' Make API request
                Dim content = New StringContent(requestBody.ToString(), Encoding.UTF8, "application/json")
                Dim response = client.PostAsync("https://api-ssl.bitly.com/v4/shorten", content).Result

                If response.IsSuccessStatusCode Then
                    Dim responseJson = response.Content.ReadAsStringAsync().Result
                    Dim parsed = JObject.Parse(responseJson)

                    If parsed("link") IsNot Nothing Then
                        Dim shortUrl = parsed("link").ToString()
                        Console.WriteLine($"✅ Shortened URL ({domain}): {longUrl} → {shortUrl}")
                        Return shortUrl
                    End If
                Else
                    Console.WriteLine($"⚠️ Bitly API error ({domain}): {response.StatusCode} - {response.ReasonPhrase}")
                End If

            End Using
        Catch ex As Exception
            Console.WriteLine($"⚠️ Bitly shortening failed ({domain}): {ex.Message}")
        End Try

        ' Return original URL if shortening failed
        Return longUrl
    End Function

    ''' <summary>
    ''' Test Bitly configuration by shortening a test URL
    ''' </summary>
    ''' <param name="token">Bitly Generic Access Token</param>
    ''' <returns>True if test successful, False otherwise</returns>
    Public Shared Function TestConnection(token As String) As Boolean
        Try
            Dim testUrl = "https://github.com"
            Dim shortUrl = Shorten(token, testUrl)

            If shortUrl <> testUrl AndAlso shortUrl.Contains("bit.ly") Then
                Console.WriteLine("✅ Bitly connection test successful")
                Return True
            Else
                Console.WriteLine("⚠️ Bitly connection test failed - no URL transformation")
                Return False
            End If
        Catch ex As Exception
            Console.WriteLine($"❌ Bitly connection test failed: {ex.Message}")
            Return False
        End Try
    End Function

    ''' <summary>
    ''' Get shortened URL with fallback to original URL
    ''' </summary>
    ''' <param name="cfg">Configuration object containing Bitly token</param>
    ''' <param name="longUrl">URL to shorten</param>
    ''' <returns>Shortened URL if available, original URL otherwise</returns>
    Public Shared Function GetShortUrl(cfg As JObject, longUrl As String) As String
        Try
            If cfg("bitly")?("token") IsNot Nothing Then
                Dim token = cfg("bitly")("token").ToString()
                If Not String.IsNullOrWhiteSpace(token) AndAlso token <> "YOUR_BITLY_GENERIC_ACCESS_TOKEN" Then
                    Return Shorten(token, longUrl)
                End If
            End If
        Catch ex As Exception
            Console.WriteLine($"⚠️ Bitly configuration error: {ex.Message}")
        End Try

        ' Return original URL if Bitly not configured or failed
        Return longUrl
    End Function
End Class
