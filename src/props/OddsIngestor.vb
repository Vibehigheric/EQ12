Imports System.Net.Http
Imports System.Text.Json
Imports System.Data.SqlClient
Imports System.Threading.Tasks

''' <summary>
''' NBA Props Odds Ingestor - Fetches and stores betting lines
''' </summary>
Public Class OddsIngestor
    Private Shared ReadOnly _http As New HttpClient()
    Private ReadOnly _connStr As String
    Private ReadOnly _apiKey As String
    
    Public Sub New(connectionString As String, apiKey As String)
        _connStr = connectionString
        _apiKey = apiKey
        _http.Timeout = TimeSpan.FromSeconds(30)
    End Sub

    ''' <summary>
    ''' Fetch current NBA props from OddsAPI or similar endpoint
    ''' </summary>
    Public Async Function FetchBookLinesAsync(endpoint As String) As Task(Of List(Of PropLine))
        Try
            Dim req = New HttpRequestMessage(HttpMethod.Get, endpoint)
            req.Headers.Add("Authorization", $"Bearer {_apiKey}")
            req.Headers.Add("User-Agent", "EQ12-PropsEngine/1.0")
            
            Dim res = Await _http.SendAsync(req)
            res.EnsureSuccessStatusCode()
            
            Dim json = Await res.Content.ReadAsStringAsync()
            Dim opts = New JsonSerializerOptions With {
                .PropertyNameCaseInsensitive = True,
                .AllowTrailingCommas = True
            }
            
            Dim lines = JsonSerializer.Deserialize(Of List(Of PropLine))(json, opts)
            
            Console.WriteLine($"[{DateTime.UtcNow:HH:mm:ss}] Fetched {lines.Count} prop lines")
            Return lines
            
        Catch ex As HttpRequestException
            Console.WriteLine($"[ERROR] HTTP fetch failed: {ex.Message}")
            Return New List(Of PropLine)()
        Catch ex As JsonException
            Console.WriteLine($"[ERROR] JSON parse failed: {ex.Message}")
            Return New List(Of PropLine)()
        End Try
    End Function

    ''' <summary>
    ''' Upsert prop lines into database with MERGE for efficiency
    ''' </summary>
    Public Sub UpsertLines(lines As IEnumerable(Of PropLine))
        If Not lines.Any() Then Return
        
        Dim sw = Diagnostics.Stopwatch.StartNew()
        Dim inserted = 0
        Dim updated = 0
        
        Using cn = New SqlConnection(_connStr)
            cn.Open()
            Using tx = cn.BeginTransaction()
                Try
                    For Each l In lines
                        Using cmd = New SqlCommand("
MERGE dbo.PropLines AS t
USING (SELECT @GameId AS GameId, @PlayerId AS PlayerId, @Market AS Market, @Book AS Book, @Line AS Line) s
ON (t.GameId = s.GameId AND t.PlayerId = s.PlayerId AND t.Market = s.Market AND t.Book = s.Book AND t.Line = s.Line)
WHEN MATCHED THEN 
    UPDATE SET Price = @Price, FetchedAt = SYSUTCDATETIME(), LineMovement = (Price - @Price)
WHEN NOT MATCHED THEN 
    INSERT (GameId, PlayerId, Market, Line, Price, Book, FetchedAt, LineMovement)
    VALUES (@GameId, @PlayerId, @Market, @Line, @Price, @Book, SYSUTCDATETIME(), 0)
OUTPUT $action;", cn, tx)
                            
                            cmd.Parameters.AddWithValue("@GameId", l.GameId)
                            cmd.Parameters.AddWithValue("@PlayerId", l.PlayerId)
                            cmd.Parameters.AddWithValue("@Market", l.Market)
                            cmd.Parameters.AddWithValue("@Line", l.Line)
                            cmd.Parameters.AddWithValue("@Price", l.Price)
                            cmd.Parameters.AddWithValue("@Book", l.Book)
                            
                            Dim action = DirectCast(cmd.ExecuteScalar(), String)
                            If action = "INSERT" Then inserted += 1 Else updated += 1
                        End Using
                    Next
                    
                    tx.Commit()
                    sw.Stop()
                    
                    Console.WriteLine($"[{DateTime.UtcNow:HH:mm:ss}] Upserted {lines.Count()} lines (I:{inserted}, U:{updated}) in {sw.ElapsedMilliseconds}ms")
                    
                Catch ex As Exception
                    tx.Rollback()
                    Console.WriteLine($"[ERROR] Upsert failed: {ex.Message}")
                    Throw
                End Try
            End Using
        End Using
    End Sub
    
    ''' <summary>
    ''' Snapshot current lines for historical analysis
    ''' </summary>
    Public Sub SnapshotLines(lines As IEnumerable(Of PropLine))
        Using cn = New SqlConnection(_connStr)
            cn.Open()
            Using cmd = New SqlCommand("
INSERT INTO dbo.PropLinesSnapshot (GameId, PlayerId, Market, Line, Price, Book, SnapshotAt)
SELECT @GameId, @PlayerId, @Market, @Line, @Price, @Book, SYSUTCDATETIME()", cn)
                
                For Each l In lines
                    cmd.Parameters.Clear()
                    cmd.Parameters.AddWithValue("@GameId", l.GameId)
                    cmd.Parameters.AddWithValue("@PlayerId", l.PlayerId)
                    cmd.Parameters.AddWithValue("@Market", l.Market)
                    cmd.Parameters.AddWithValue("@Line", l.Line)
                    cmd.Parameters.AddWithValue("@Price", l.Price)
                    cmd.Parameters.AddWithValue("@Book", l.Book)
                    cmd.ExecuteNonQuery()
                Next
            End Using
        End Using
    End Sub
End Class

''' <summary>
''' Prop line data model
''' </summary>
Public Class PropLine
    Public Property GameId As String
    Public Property PlayerId As String
    Public Property PlayerName As String
    Public Property Market As String        ' PTS, AST, REB, 3PM, PRA, STL, BLK, etc.
    Public Property Line As Decimal
    Public Property Price As Integer        ' American odds
    Public Property Book As String
    Public Property GameDate As DateTime
    Public Property Opponent As String
End Class
