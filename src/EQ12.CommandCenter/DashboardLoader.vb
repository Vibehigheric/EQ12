Imports System.IO
Imports System.Text.Json
Imports System.Text.Json.Serialization

Public Class DashboardLoader
    Public Class DashboardData
        <JsonPropertyName("generated_at")>
        Public Property GeneratedAt As String
        <JsonPropertyName("stats")>
        Public Property Stats As StatsData
        <JsonPropertyName("recent_bets")>
        Public Property RecentBets As List(Of BetData)
        <JsonPropertyName("alerts")>
        Public Property Alerts As List(Of AlertData)
    End Class

    Public Class StatsData
        <JsonPropertyName("total_profit")>
        Public Property TotalProfit As Double
        <JsonPropertyName("total_bets")>
        Public Property TotalBets As Integer
        <JsonPropertyName("avg_clv")>
        Public Property AvgClv As Double
    End Class

    Public Class BetData
        <JsonPropertyName("id")>
        Public Property Id As Integer
        <JsonPropertyName("date")>
        Public Property DatePlaced As String
        <JsonPropertyName("selection")>
        Public Property Selection As String
        <JsonPropertyName("market")>
        Public Property Market As String
        <JsonPropertyName("odds")>
        Public Property Odds As Double
        <JsonPropertyName("stake")>
        Public Property Stake As Double
        <JsonPropertyName("status")>
        Public Property Status As String
        <JsonPropertyName("profit")>
        Public Property Profit As Double
    End Class

    Public Class AlertData
        <JsonPropertyName("type")>
        Public Property Type As String
        <JsonPropertyName("message")>
        Public Property Message As String
    End Class

    Public Shared Function LoadData(filePath As String) As DashboardData
        If Not File.Exists(filePath) Then
            Console.WriteLine($"❌ Error: Dashboard data file not found at {filePath}")
            Return Nothing
        End If

        Try
            Dim jsonString As String = File.ReadAllText(filePath)
            Dim options As New JsonSerializerOptions With {
                .PropertyNameCaseInsensitive = True
            }
            Return JsonSerializer.Deserialize(Of DashboardData)(jsonString, options)
        Catch ex As Exception
            Console.WriteLine($"❌ Error parsing dashboard data: {ex.Message}")
            Return Nothing
        End Try
    End Function
End Class
