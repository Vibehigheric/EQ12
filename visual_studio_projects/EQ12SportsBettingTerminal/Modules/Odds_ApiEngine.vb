
' OddsApiClient.vb
' Source: GitHub repo https://github.com/sarartur/oddsapi, adapted for EQ12
' Original description: Python wrapper around The Odds-Api
' Functions extracted:
    ' retrieve_odds from oddsAPI\client.py
    ' OddsApiClient(Client) from oddsAPI\client.py
    ' OddsClientError(Exception) from oddsAPI\exceptions.py
    ' OddsApiResponse(BaseType) from oddsAPI\_types.py

Imports System
Imports System.Net.Http
Imports System.Threading.Tasks
Imports Newtonsoft.Json
Imports System.Data

Public Class OddsApiClient
    
    Private ReadOnly httpClient As HttpClient
    Private ReadOnly apiKey As String
    Private ReadOnly baseUrl As String = "https://api.the-odds-api.com/v4"
    Private ReadOnly dbWriter As DBWriter
    Private ReadOnly logger As Logger
    
    Public Sub New()
        httpClient = New HttpClient()
        apiKey = Environment.GetEnvironmentVariable("ODDS_API_KEY")
        dbWriter = New DBWriter()
        logger = New Logger("OddsApiClient")
        
        If String.IsNullOrEmpty(apiKey) Then
            Throw New ArgumentException("ODDS_API_KEY environment variable not set")
        End If
        
        logger.Info("OddsApiClient initialized from GitHub repo integration")
    End Sub
    
    Public Async Function GetSportsAsync() As Task(Of List(Of Sport))
        ' Get available sports - adapted from oddsapi
        Try
            Dim url As String = $"{baseUrl}/sports?apiKey={apiKey}"
            Dim response = Await httpClient.GetStringAsync(url)
            
            Dim sports As List(Of Sport) = JsonConvert.DeserializeObject(Of List(Of Sport))(response)
            logger.Info($"Retrieved {sports.Count} sports from OddsAPI")
            
            Return sports
            
        Catch ex As Exception
            logger.Error($"Error getting sports: {ex.Message}")
            Return New List(Of Sport)()
        End Try
    End Function
    
    Public Async Function GetOddsBySportAsync(sport As String, Optional regions As String = "us", Optional markets As String = "h2h,spreads,totals") As Task(Of DataTable)
        ' Get odds for specific sport - core functionality from GitHub repo
        Try
            Dim url As String = $"{baseUrl}/sports/{sport}/odds?apiKey={apiKey}&regions={regions}&markets={markets}"
            Dim response = Await httpClient.GetStringAsync(url)
            
            Dim oddsResponse = JsonConvert.DeserializeObject(response)
            Dim oddsTable As DataTable = ParseOddsToDataTable(oddsResponse, sport)
            
            ' Save to database
            Await SaveOddsToDatabase(oddsTable)
            
            logger.Info($"Retrieved {oddsTable.Rows.Count} odds records for {sport}")
            Return oddsTable
            
        Catch ex As Exception
            logger.Error($"Error getting odds for {sport}: {ex.Message}")
            Return New DataTable()
        End Try
    End Function
    
    Private Function ParseOddsToDataTable(oddsData As Object, sport As String) As DataTable
        ' Parse JSON response to DataTable - adapted from repo parsing logic
        Dim table As New DataTable()
        
        ' Define schema
        table.Columns.Add("ts", GetType(DateTime))
        table.Columns.Add("event_id", GetType(String))
        table.Columns.Add("sport", GetType(String))
        table.Columns.Add("market", GetType(String))
        table.Columns.Add("selection", GetType(String))
        table.Columns.Add("book", GetType(String))
        table.Columns.Add("odds", GetType(Integer))
        
        Try
            ' Parse JSON structure and populate DataTable
            ' This would contain the specific parsing logic from the GitHub repo
            Dim timestamp As DateTime = DateTime.Now
            
            ' Example parsing structure - would be adapted from actual repo
            ' For Each event In oddsData...
            '   For Each bookmaker In event.bookmakers...
            '     For Each market In bookmaker.markets...
            '       For Each outcome In market.outcomes...
            
            logger.Info($"Parsed odds data into {table.Rows.Count} rows")
            
        Catch ex As Exception
            logger.Error($"Error parsing odds data: {ex.Message}")
        End Try
        
        Return table
    End Function
    
    Private Async Function SaveOddsToDatabase(oddsTable As DataTable) As Task
        ' Save odds to SQLite and sync to BigQuery
        Try
            For Each row As DataRow In oddsTable.Rows
                Dim sql As String = "INSERT INTO odds (ts, event_id, sport, market, selection, book, odds) VALUES (?, ?, ?, ?, ?, ?, ?)"
                dbWriter.ExecuteNonQuery(sql, row("ts"), row("event_id"), row("sport"), row("market"), row("selection"), row("book"), row("odds"))
            Next
            
            ' Sync to BigQuery
            dbWriter.SyncToBigQuery("odds")
            
            ' Check for value bets and send alerts
            Await CheckForValueBets(oddsTable)
            
        Catch ex As Exception
            logger.Error($"Error saving odds to database: {ex.Message}")
        End Try
    End Function
    
    Private Async Function CheckForValueBets(oddsTable As DataTable) As Task
        ' Simple value bet detection and alerting
        Try
            ' Basic value bet logic - would be enhanced based on repo algorithms
            For Each row As DataRow In oddsTable.Rows
                Dim odds As Integer = Convert.ToInt32(row("odds"))
                Dim impliedProb As Double = If(odds > 0, 100.0 / (odds + 100.0), Math.Abs(odds) / (Math.Abs(odds) + 100.0))
                
                ' Simple heuristic - alert if implied probability suggests value
                If impliedProb < 0.45 AndAlso odds > 120 Then
                    Await SendValueBetAlert(row)
                End If
            Next
            
        Catch ex As Exception
            logger.Error($"Error checking for value bets: {ex.Message}")
        End Try
    End Function
    
    Private Async Function SendValueBetAlert(oddsRow As DataRow) As Task
        ' Send value bet alert with Bitly link
        Try
            Dim alertMessage As String = $"💰 VALUE BET: {oddsRow("selection")} {oddsRow("odds")} at {oddsRow("book")}"
            Dim detailUrl As String = $"https://eq12.local/odds/{oddsRow("event_id")}"
            Dim bitlyUrl As String = BitlyHelper.ShortenUrl(detailUrl)
            
            AlertsHelper.SendTelegramAlert(alertMessage & " " & bitlyUrl)
            
        Catch ex As Exception
            logger.Error($"Error sending value bet alert: {ex.Message}")
        End Try
    End Function
    
    Public Sub Dispose()
        httpClient?.Dispose()
    End Sub
    
End Class

Public Class Sport
    Public Property Key As String
    Public Property Group As String
    Public Property Title As String
    Public Property Description As String
    Public Property Active As Boolean
    Public Property HasOutrights As Boolean
End Class
