Option Strict On
Option Explicit On

Imports System.Net.Http
Imports System.Text.Json
Imports System.Threading.Tasks

Namespace EQ12.Core.ApiClient

    ''' <summary>
    ''' Client for The Odds API - fetches live odds for sports betting
    ''' </summary>
    Public Class OddsApiClient
        Implements IDisposable

        Private ReadOnly _client As HttpClient
        Private ReadOnly _apiKey As String
        Private Const BASE_URL As String = "https://api.the-odds-api.com/v4"

        Public Sub New(apiKey As String)
            If String.IsNullOrWhiteSpace(apiKey) Then
                Throw New ArgumentException("API key cannot be empty", NameOf(apiKey))
            End If

            _apiKey = apiKey
            _client = New HttpClient() With {
                .BaseAddress = New Uri(BASE_URL)
            }
        End Sub

        ''' <summary>
        ''' Get available sports
        ''' </summary>
        Public Async Function GetSportsAsync() As Task(Of List(Of Sport))
            Dim url = $"/sports/?apiKey={_apiKey}"
            Dim json = Await GetJsonAsync(url)
            Return JsonSerializer.Deserialize(Of List(Of Sport))(json)
        End Function

        ''' <summary>
        ''' Get odds for a specific sport
        ''' </summary>
        Public Async Function GetOddsAsync(sport As String, markets As String, regions As String) As Task(Of List(Of GameOdds))
            If String.IsNullOrWhiteSpace(sport) Then
                Throw New ArgumentException("Sport cannot be empty", NameOf(sport))
            End If

            Dim url = $"/sports/{sport}/odds/?apiKey={_apiKey}&regions={regions}&markets={markets}&oddsFormat=american"
            Dim json = Await GetJsonAsync(url)
            Return JsonSerializer.Deserialize(Of List(Of GameOdds))(json)
        End Function

        ''' <summary>
        ''' Get MLB odds (convenience method)
        ''' </summary>
        Public Async Function GetMlbOddsAsync() As Task(Of List(Of GameOdds))
            Return Await GetOddsAsync("baseball_mlb", "h2h,spreads,totals", "us")
        End Function

        ''' <summary>
        ''' Get NBA odds (convenience method)
        ''' </summary>
        Public Async Function GetNbaOddsAsync() As Task(Of List(Of GameOdds))
            Return Await GetOddsAsync("basketball_nba", "h2h,spreads,totals", "us")
        End Function

        ''' <summary>
        ''' Get NFL odds (convenience method)
        ''' </summary>
        Public Async Function GetNflOddsAsync() As Task(Of List(Of GameOdds))
            Return Await GetOddsAsync("americanfootball_nfl", "h2h,spreads,totals", "us")
        End Function

        Private Async Function GetJsonAsync(url As String) As Task(Of String)
            Dim response = Await _client.GetAsync(url)
            response.EnsureSuccessStatusCode()
            Return Await response.Content.ReadAsStringAsync()
        End Function

        Public Sub Dispose() Implements IDisposable.Dispose
            _client?.Dispose()
        End Sub

    End Class

    ' ============================================================================
    ' DATA MODELS
    ' ============================================================================

    Public Class Sport
        Public Property Key As String
        Public Property Group As String
        Public Property Title As String
        Public Property Description As String
        Public Property Active As Boolean
        Public Property HasOutrights As Boolean
    End Class

    Public Class GameOdds
        Public Property Id As String
        Public Property SportKey As String
        Public Property SportTitle As String
        Public Property CommenceTime As DateTime
        Public Property HomeTeam As String
        Public Property AwayTeam As String
        Public Property Bookmakers As List(Of Bookmaker)
    End Class

    Public Class Bookmaker
        Public Property Key As String
        Public Property Title As String
        Public Property LastUpdate As DateTime
        Public Property Markets As List(Of Market)
    End Class

    Public Class Market
        Public Property Key As String
        Public Property Outcomes As List(Of Outcome)
    End Class

    Public Class Outcome
        Public Property Name As String
        Public Property Price As Integer
        Public Property Point As Double?
    End Class

End Namespace
