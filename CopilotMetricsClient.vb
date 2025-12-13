' Copilot Metrics client and report helpers for EQ12 CLI
' Provides GitHub Copilot usage retrieval, summary, and diff utilities.

Imports System
Imports System.IO
Imports System.Net.Http
Imports System.Net.Http.Headers
Imports System.Text
Imports System.Text.Json
Imports System.Globalization
Imports System.Threading.Tasks
Imports System.Collections.Generic
Imports System.Linq
Imports Microsoft.Extensions.Logging
Imports Microsoft.Extensions.Configuration

Public Enum CopilotMetricsScope
    Enterprise
    Organization
    Team
End Enum

Public Class CopilotMetricsRequest
    Public Property Scope As CopilotMetricsScope = CopilotMetricsScope.Organization
    Public Property EnterpriseSlug As String
    Public Property Organization As String
    Public Property TeamSlug As String
    Public Property AccessToken As String
    Public Property Since As DateTime?

    Public Function DescribeScope() As String
        Select Case Scope
            Case CopilotMetricsScope.Enterprise
                Return $"enterprise:{EnterpriseSlug}"
            Case CopilotMetricsScope.Organization
                Return $"org:{Organization}"
            Case CopilotMetricsScope.Team
                Return $"team:{Organization}/{TeamSlug}"
            Case Else
                Return "unknown"
        End Select
    End Function
End Class

Public Class CopilotMetricsSummary
    Public Property TotalSuggestions As Double?
    Public Property AcceptedSuggestions As Double?
    Public Property AcceptanceRate As Double?
    Public Property TotalChats As Double?
    Public Property AcceptedChatSuggestions As Double?
    Public Property PullRequestSummaries As Double?
    Public Property SummariesViewed As Double?
    Public Property ActiveUsers As Double?
    Public Property LicensedUsers As Double?
    Public Property PercentActive As Double?
End Class

Public Class CopilotMetricsDailyPoint
    Public Property Day As DateTime
    Public Property TotalSuggestions As Double?
    Public Property AcceptedSuggestions As Double?
    Public Property AcceptanceRate As Double?
    Public Property TotalChats As Double?
    Public Property ActiveUsers As Double?
    Public Property LicensedUsers As Double?
End Class

Public Class CopilotMetricDelta
    Public Property MetricName As String
    Public Property RecentAverage As Double?
    Public Property BaselineAverage As Double?

    Public ReadOnly Property Difference As Double?
        Get
            If RecentAverage.HasValue AndAlso BaselineAverage.HasValue Then
                Return RecentAverage.Value - BaselineAverage.Value
            End If
            Return Nothing
        End Get
    End Property
End Class

Public Class CopilotMetricsDiff
    Public Property PeriodDays As Integer
    Public Property Deltas As List(Of CopilotMetricDelta) = New List(Of CopilotMetricDelta)()
End Class

Public Class CopilotMetricsSnapshot
    Public Property Scope As CopilotMetricsScope
    Public Property Identifier As String
    Public Property RetrievedAt As DateTime
    Public Property RawJson As String
    Public Property Summary As CopilotMetricsSummary
    Public Property DailyBuckets As List(Of CopilotMetricsDailyPoint)

    Public Shared Function FromJson(rawJson As String, scope As CopilotMetricsScope, identifier As String) As CopilotMetricsSnapshot
        Dim summary As CopilotMetricsSummary = Nothing
        Dim buckets As List(Of CopilotMetricsDailyPoint) = Nothing

        Using document = JsonDocument.Parse(rawJson)
            Dim root = document.RootElement
            summary = CopilotMetricsParser.ExtractSummary(root)
            buckets = CopilotMetricsParser.ExtractDailyBuckets(root)
        End Using

        Return New CopilotMetricsSnapshot With {
            .Scope = scope,
            .Identifier = identifier,
            .RetrievedAt = DateTime.UtcNow,
            .RawJson = rawJson,
            .Summary = summary,
            .DailyBuckets = buckets
        }
    End Function

    Public Function SaveRawJson(logsRoot As String) As String
        If String.IsNullOrWhiteSpace(logsRoot) Then
            Throw New ArgumentException("logsRoot is required", NameOf(logsRoot))
        End If

        Directory.CreateDirectory(logsRoot)
        Dim safeIdentifier = New String(Identifier.Select(Function(ch) If(Char.IsLetterOrDigit(ch), ch, "_"c)).ToArray())
        Dim filename = $"copilot_metrics_{safeIdentifier}_{RetrievedAt:yyyyMMddHHmmss}.json"
        Dim fullPath = Path.Combine(logsRoot, filename)
        File.WriteAllText(fullPath, RawJson, Encoding.UTF8)
        Return fullPath
    End Function

    Public Function SaveReport(reportContent As String, logsRoot As String, suffix As String) As String
        If String.IsNullOrWhiteSpace(reportContent) Then
            Throw New ArgumentException("Report content is required", NameOf(reportContent))
        End If

        Directory.CreateDirectory(logsRoot)
        Dim safeIdentifier = New String(Identifier.Select(Function(ch) If(Char.IsLetterOrDigit(ch), ch, "_"c)).ToArray())
        Dim filename = $"copilot_metrics_{safeIdentifier}_{suffix}_{RetrievedAt:yyyyMMddHHmmss}.md"
        Dim fullPath = Path.Combine(logsRoot, filename)
        File.WriteAllText(fullPath, reportContent, Encoding.UTF8)
        Return fullPath
    End Function
End Class

Public Class CopilotMetricsClient
    Private ReadOnly _httpClient As HttpClient
    Private ReadOnly _logger As ILogger
    Private ReadOnly _config As IConfiguration

    Private Const BaseUrl As String = "https://api.github.com"
    Private Const ApiVersion As String = "2022-11-28"

    Public Sub New(Optional logger As ILogger = Nothing, Optional config As IConfiguration = Nothing, Optional httpClient As HttpClient = Nothing)
        _logger = logger
        _config = config
        _httpClient = If(httpClient, New HttpClient())
        _httpClient.DefaultRequestHeaders.UserAgent.Clear()
        _httpClient.DefaultRequestHeaders.UserAgent.ParseAdd("EQ12-CopilotMetricsClient/1.0")
    End Sub

    Public Async Function FetchMetricsAsync(request As CopilotMetricsRequest) As Task(Of CopilotMetricsSnapshot)
        If request Is Nothing Then
            Throw New ArgumentNullException(NameOf(request))
        End If

        ValidateRequest(request)
        Dim token = ResolveAccessToken(request)
        Dim endpoint = BuildEndpoint(request)

        Dim uriBuilder = New UriBuilder(endpoint)
        If request.Since.HasValue Then
            Dim query = $"since={request.Since.Value.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture)}"
            If Not String.IsNullOrEmpty(uriBuilder.Query) Then
                uriBuilder.Query = uriBuilder.Query.TrimStart("?"c) + "&" + query
            Else
                uriBuilder.Query = query
            End If
        End If

        Using httpRequest As New HttpRequestMessage(HttpMethod.Get, uriBuilder.Uri)
            httpRequest.Headers.Accept.Clear()
            httpRequest.Headers.Accept.Add(New MediaTypeWithQualityHeaderValue("application/vnd.github+json"))
            httpRequest.Headers.Add("X-GitHub-Api-Version", ApiVersion)
            httpRequest.Headers.Authorization = New AuthenticationHeaderValue("Bearer", token)

            Dim response = Await _httpClient.SendAsync(httpRequest)
            Dim content = Await response.Content.ReadAsStringAsync()

            If Not response.IsSuccessStatusCode Then
                _logger?.LogError("Copilot metrics request failed: {StatusCode} - {Content}", response.StatusCode, content)
                Throw New InvalidOperationException($"Failed to fetch Copilot metrics: {response.StatusCode} {response.ReasonPhrase}")
            End If

            _logger?.LogInformation("Retrieved Copilot metrics for {Identifier}", request.DescribeScope())
            Return CopilotMetricsSnapshot.FromJson(content, request.Scope, request.DescribeScope())
        End Using
    End Function

    Private Sub ValidateRequest(request As CopilotMetricsRequest)
        Select Case request.Scope
            Case CopilotMetricsScope.Enterprise
                If String.IsNullOrWhiteSpace(request.EnterpriseSlug) Then
                    Throw New ArgumentException("Enterprise slug is required for enterprise scope.")
                End If
            Case CopilotMetricsScope.Organization
                If String.IsNullOrWhiteSpace(request.Organization) Then
                    Throw New ArgumentException("Organization name is required for organization scope.")
                End If
            Case CopilotMetricsScope.Team
                If String.IsNullOrWhiteSpace(request.Organization) OrElse String.IsNullOrWhiteSpace(request.TeamSlug) Then
                    Throw New ArgumentException("Organization and team slug are required for team scope.")
                End If
        End Select
    End Sub

    Private Function ResolveAccessToken(request As CopilotMetricsRequest) As String
        Dim candidates = New List(Of String)()

        If Not String.IsNullOrWhiteSpace(request.AccessToken) Then
            candidates.Add(request.AccessToken)
        End If

        If _config IsNot Nothing Then
            candidates.Add(_config("GitHub:Copilot:Token"))
            candidates.Add(_config("GitHub:Pat"))
            candidates.Add(_config("GitHub:AccessToken"))
            candidates.Add(_config("Copilot:Token"))
        End If

        candidates.Add(Environment.GetEnvironmentVariable("GITHUB_PAT"))
        candidates.Add(Environment.GetEnvironmentVariable("GITHUB_TOKEN"))
        candidates.Add(Environment.GetEnvironmentVariable("COPILOT_METRICS_TOKEN"))

        Dim token = candidates.FirstOrDefault(Function(value) Not String.IsNullOrWhiteSpace(value))

        If String.IsNullOrWhiteSpace(token) Then
            Throw New InvalidOperationException("GitHub access token is required. Set GITHUB_PAT or configure GitHub:Copilot:Token.")
        End If

        Return token
    End Function

    Private Function BuildEndpoint(request As CopilotMetricsRequest) As String
        Select Case request.Scope
            Case CopilotMetricsScope.Enterprise
                Return $"{BaseUrl}/enterprises/{request.EnterpriseSlug}/copilot/metrics"
            Case CopilotMetricsScope.Organization
                Return $"{BaseUrl}/orgs/{request.Organization}/copilot/metrics"
            Case CopilotMetricsScope.Team
                Return $"{BaseUrl}/orgs/{request.Organization}/teams/{request.TeamSlug}/copilot/metrics"
            Case Else
                Throw New ArgumentOutOfRangeException(NameOf(request.Scope), "Unsupported Copilot metrics scope.")
        End Select
    End Function
End Class

Public Class CopilotMetricsReportBuilder
    Public Shared Function BuildMarkdownReport(snapshot As CopilotMetricsSnapshot, periodLabel As String) As String
        Dim sb As New StringBuilder()
        Dim summary = snapshot?.Summary
        Dim orderedBuckets = snapshot?.DailyBuckets?.OrderBy(Function(b) b.Day).ToList()

        sb.AppendLine("# EQ12 Copilot Metrics Report")
        sb.AppendLine($"- Scope: {snapshot.Scope}")
        sb.AppendLine($"- Identifier: {snapshot.Identifier}")
        sb.AppendLine($"- Generated: {snapshot.RetrievedAt:yyyy-MM-dd HH:mm:ss} UTC")
        sb.AppendLine($"- Period: {periodLabel}")
        sb.AppendLine("")
        sb.AppendLine("## Key Metrics")

        If summary IsNot Nothing Then
            AppendMetricLine(sb, "Total Suggestions", summary.TotalSuggestions)
            AppendMetricLine(sb, "Accepted Suggestions", summary.AcceptedSuggestions)
            AppendMetricLine(sb, "Acceptance Rate (%)", If(summary.AcceptanceRate.HasValue, summary.AcceptanceRate.Value * 100.0, Nothing))
            AppendMetricLine(sb, "Total Chats", summary.TotalChats)
            AppendMetricLine(sb, "Accepted Chat Suggestions", summary.AcceptedChatSuggestions)
            AppendMetricLine(sb, "PR Summaries", summary.PullRequestSummaries)
            AppendMetricLine(sb, "Summaries Viewed", summary.SummariesViewed)
            AppendMetricLine(sb, "Active Users", summary.ActiveUsers)
            AppendMetricLine(sb, "Licensed Users", summary.LicensedUsers)
            AppendMetricLine(sb, "Percent Active (%)", summary.PercentActive)
        Else
            sb.AppendLine("No summary metrics available.")
        End If

        sb.AppendLine("")
        sb.AppendLine("## Recent Daily Activity")

        If orderedBuckets IsNot Nothing AndAlso orderedBuckets.Count > 0 Then
            Dim recent = orderedBuckets.TakeLast(Math.Min(7, orderedBuckets.Count)).ToList()
            sb.AppendLine("| Day | Suggestions | Accepted | Acceptance % | Active Users | Chats |")
            sb.AppendLine("| --- | ----------- | -------- | ------------ | ------------ | ----- |")

            For Each bucket In recent
                Dim acceptanceValue = bucket.AcceptanceRate
                If Not acceptanceValue.HasValue AndAlso bucket.TotalSuggestions.HasValue AndAlso bucket.AcceptedSuggestions.HasValue AndAlso bucket.TotalSuggestions.Value > 0 Then
                    acceptanceValue = bucket.AcceptedSuggestions.Value / bucket.TotalSuggestions.Value
                End If

                sb.AppendLine($"| {bucket.Day:yyyy-MM-dd} | {FormatNumber(bucket.TotalSuggestions)} | {FormatNumber(bucket.AcceptedSuggestions)} | {FormatPercent(acceptanceValue)} | {FormatNumber(bucket.ActiveUsers)} | {FormatNumber(bucket.TotalChats)} |")
            Next

            Dim totalSuggestions = recent.Sum(Function(b) b.TotalSuggestions.GetValueOrDefault())
            Dim totalAccepted = recent.Sum(Function(b) b.AcceptedSuggestions.GetValueOrDefault())
            Dim avgActive = If(recent.Count > 0, recent.Average(Function(b) b.ActiveUsers.GetValueOrDefault()), 0)

            sb.AppendLine("")
            sb.AppendLine($"Seven-day suggestions total: {totalSuggestions:0.##}")
            sb.AppendLine($"Seven-day acceptance rate: {ComputeAcceptanceRate(totalAccepted, totalSuggestions):0.##}%")
            sb.AppendLine($"Average active users: {avgActive:0.##}")
        Else
            sb.AppendLine("No daily breakdown data returned from the API.")
        End If

        sb.AppendLine("")
        sb.AppendLine("## Notes")
        sb.AppendLine("- Data retrieved via GitHub Copilot Metrics API.")
        sb.AppendLine("- Ensure tokens include `copilot` and `organization_read` scopes.")

        Return sb.ToString()
    End Function

    Public Shared Function CalculateDiff(snapshot As CopilotMetricsSnapshot, days As Integer) As CopilotMetricsDiff
        If snapshot Is Nothing Then
            Throw New ArgumentNullException(NameOf(snapshot))
        End If

        Dim diff As New CopilotMetricsDiff With {
            .PeriodDays = days
        }

        Dim ordered = snapshot.DailyBuckets?.OrderBy(Function(b) b.Day).ToList()
        If ordered Is Nothing OrElse ordered.Count = 0 Then
            Return diff
        End If

        Dim recent = ordered.TakeLast(Math.Min(days, ordered.Count)).ToList()
        Dim baselineCount = Math.Min(days, Math.Max(0, ordered.Count - recent.Count))
        Dim baseline = ordered.Take(Math.Max(0, ordered.Count - recent.Count)).TakeLast(baselineCount).ToList()

        If baseline.Count = 0 Then
            baseline = New List(Of CopilotMetricsDailyPoint) From {ordered.First()}
        End If

        diff.Deltas.Add(BuildDelta("Total Suggestions", recent, baseline, Function(p) p.TotalSuggestions))
        diff.Deltas.Add(BuildDelta("Accepted Suggestions", recent, baseline, Function(p) p.AcceptedSuggestions))
        diff.Deltas.Add(BuildDelta("Acceptance Rate", recent, baseline, Function(p)
                                                                            If(p.AcceptanceRate.HasValue, p.AcceptanceRate,
                                                                               ComputeAcceptanceRateNullable(p.AcceptedSuggestions, p.TotalSuggestions))
                                                                        End Function))
        diff.Deltas.Add(BuildDelta("Active Users", recent, baseline, Function(p) p.ActiveUsers))
        diff.Deltas.Add(BuildDelta("Licensed Users", recent, baseline, Function(p) p.LicensedUsers))
        diff.Deltas.Add(BuildDelta("Total Chats", recent, baseline, Function(p) p.TotalChats))

        diff.Deltas = diff.Deltas.Where(Function(delta) delta IsNot Nothing).ToList()
        Return diff
    End Function

    Private Shared Function BuildDelta(name As String, recent As List(Of CopilotMetricsDailyPoint), baseline As List(Of CopilotMetricsDailyPoint), selector As Func(Of CopilotMetricsDailyPoint, Double?)) As CopilotMetricDelta
        Dim recentValues = recent.Select(Function(p) selector(p)).Where(Function(v) v.HasValue).Select(Function(v) v.Value).ToList()
        Dim baselineValues = baseline.Select(Function(p) selector(p)).Where(Function(v) v.HasValue).Select(Function(v) v.Value).ToList()

        If recentValues.Count = 0 Then
            Return Nothing
        End If

        Dim delta As New CopilotMetricDelta With {
            .MetricName = name,
            .RecentAverage = recentValues.Average()
        }

        If baselineValues.Count > 0 Then
            delta.BaselineAverage = baselineValues.Average()
        End If

        Return delta
    End Function

    Private Shared Sub AppendMetricLine(sb As StringBuilder, label As String, value As Double?)
        If value.HasValue Then
            sb.AppendLine($"- {label}: {value.Value:0.##}")
        End If
    End Sub

    Private Shared Function FormatNumber(value As Double?) As String
        If Not value.HasValue Then
            Return "-"
        End If
        Return value.Value.ToString("0.##")
    End Function

    Private Shared Function FormatPercent(value As Double?) As String
        If Not value.HasValue Then
            Return "-"
        End If
        Return (value.Value * 100.0).ToString("0.##") & "%"
    End Function

    Private Shared Function ComputeAcceptanceRate(accepted As Double, total As Double) As Double
        If total <= 0 Then
            Return 0
        End If
        Return (accepted / total) * 100.0
    End Function

    Private Shared Function ComputeAcceptanceRateNullable(accepted As Double?, total As Double?) As Double?
        If Not accepted.HasValue OrElse Not total.HasValue OrElse total.Value <= 0 Then
            Return Nothing
        End If
        Return accepted.Value / total.Value
    End Function
End Class

Friend Module CopilotMetricsParser
    Public Function ExtractSummary(root As JsonElement) As CopilotMetricsSummary
        Dim summaryElement As JsonElement
        If root.ValueKind = JsonValueKind.Object AndAlso root.TryGetProperty("summary", summaryElement) Then
            Return BuildSummary(summaryElement)
        End If

        Return BuildSummary(root)
    End Function

    Public Function ExtractDailyBuckets(root As JsonElement) As List(Of CopilotMetricsDailyPoint)
        Dim buckets As New List(Of CopilotMetricsDailyPoint)()
        ExtractBucketsRecursive(root, buckets)
        Return buckets.OrderBy(Function(b) b.Day).GroupBy(Function(b) b.Day).Select(Function(g) MergeBuckets(g.ToList())).ToList()
    End Function

    Private Sub ExtractBucketsRecursive(element As JsonElement, buckets As List(Of CopilotMetricsDailyPoint))
        Select Case element.ValueKind
            Case JsonValueKind.Array
                For Each item In element.EnumerateArray()
                    ExtractBucketsRecursive(item, buckets)
                Next
            Case JsonValueKind.Object
                Dim day As DateTime? = Nothing
                Dim hasDay = False

                For Each prop In element.EnumerateObject()
                    If prop.Name.Equals("day", StringComparison.OrdinalIgnoreCase) OrElse prop.Name.Equals("date", StringComparison.OrdinalIgnoreCase) Then
                        Dim parsedDay As DateTime
                        If DateTime.TryParse(prop.Value.GetString(), CultureInfo.InvariantCulture, DateTimeStyles.AdjustToUniversal, parsedDay) Then
                            day = parsedDay.Date
                            hasDay = True
                        End If
                    End If
                Next

                If hasDay AndAlso day.HasValue Then
                    Dim bucket As New CopilotMetricsDailyPoint With {
                        .Day = day.Value
                    }

                    bucket.TotalSuggestions = TryFindNumber(element, "total_suggestions")
                    bucket.AcceptedSuggestions = TryFindNumber(element, "accepted_suggestions")
                    bucket.AcceptanceRate = TryFindNumber(element, "acceptance_rate")
                    bucket.TotalChats = TryFindNumber(element, "total_chats")
                    bucket.ActiveUsers = TryFindNumber(element, "active_users")
                    bucket.LicensedUsers = TryFindNumber(element, "licensed_users")

                    buckets.Add(bucket)
                End If

                For Each prop In element.EnumerateObject()
                    ExtractBucketsRecursive(prop.Value, buckets)
                Next
        End Select
    End Sub

    Private Function MergeBuckets(items As List(Of CopilotMetricsDailyPoint)) As CopilotMetricsDailyPoint
        Dim merged As New CopilotMetricsDailyPoint With {
            .Day = items.First().Day,
            .TotalSuggestions = AverageNullable(items.Select(Function(i) i.TotalSuggestions)),
            .AcceptedSuggestions = AverageNullable(items.Select(Function(i) i.AcceptedSuggestions)),
            .AcceptanceRate = AverageNullable(items.Select(Function(i) i.AcceptanceRate)),
            .TotalChats = AverageNullable(items.Select(Function(i) i.TotalChats)),
            .ActiveUsers = AverageNullable(items.Select(Function(i) i.ActiveUsers)),
            .LicensedUsers = AverageNullable(items.Select(Function(i) i.LicensedUsers))
        }

        Return merged
    End Function

    Private Function AverageNullable(values As IEnumerable(Of Double?)) As Double?
        Dim numericValues = values.Where(Function(v) v.HasValue).Select(Function(v) v.Value).ToList()
        If numericValues.Count = 0 Then
            Return Nothing
        End If
        Return numericValues.Average()
    End Function

    Private Function BuildSummary(element As JsonElement) As CopilotMetricsSummary
        Dim summary As New CopilotMetricsSummary With {
            .TotalSuggestions = TryFindNumber(element, "total_suggestions"),
            .AcceptedSuggestions = TryFindNumber(element, "accepted_suggestions"),
            .AcceptanceRate = TryFindNumber(element, "acceptance_rate"),
            .TotalChats = TryFindNumber(element, "total_chats"),
            .AcceptedChatSuggestions = TryFindNumber(element, "accepted_chat_suggestions"),
            .PullRequestSummaries = TryFindNumber(element, "prs_summarized"),
            .SummariesViewed = TryFindNumber(element, "summaries_viewed"),
            .ActiveUsers = TryFindNumber(element, "active_users"),
            .LicensedUsers = TryFindNumber(element, "licensed_users"),
            .PercentActive = TryFindNumber(element, "percent_active")
        }

        If Not summary.AcceptanceRate.HasValue AndAlso summary.TotalSuggestions.HasValue AndAlso summary.AcceptedSuggestions.HasValue AndAlso summary.TotalSuggestions.Value > 0 Then
            summary.AcceptanceRate = summary.AcceptedSuggestions.Value / summary.TotalSuggestions.Value
        End If

        Return summary
    End Function

    Private Function TryFindNumber(element As JsonElement, fieldName As String) As Double?
        Dim result As Double?
        If TryFindNumberInternal(element, fieldName, result) Then
            Return result
        End If
        Return Nothing
    End Function

    Private Function TryFindNumberInternal(element As JsonElement, fieldName As String, ByRef result As Double?) As Boolean
        Select Case element.ValueKind
            Case JsonValueKind.Object
                For Each prop In element.EnumerateObject()
                    If prop.Name.Equals(fieldName, StringComparison.OrdinalIgnoreCase) Then
                        Dim numberValue As Double
                        If TryConvertToDouble(prop.Value, numberValue) Then
                            result = numberValue
                            Return True
                        End If
                    End If

                    If TryFindNumberInternal(prop.Value, fieldName, result) Then
                        Return True
                    End If
                Next
            Case JsonValueKind.Array
                For Each item In element.EnumerateArray()
                    If TryFindNumberInternal(item, fieldName, result) Then
                        Return True
                    End If
                Next
        End Select

        Return False
    End Function

    Private Function TryConvertToDouble(element As JsonElement, ByRef value As Double) As Boolean
        Select Case element.ValueKind
            Case JsonValueKind.Number
                value = element.GetDouble()
                Return True
            Case JsonValueKind.String
                Dim text = element.GetString()
                If Double.TryParse(text, NumberStyles.Any, CultureInfo.InvariantCulture, value) Then
                    Return True
                End If
        End Select

        Return False
    End Function
End Module
