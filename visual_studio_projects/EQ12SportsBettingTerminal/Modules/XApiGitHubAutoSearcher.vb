' ===============================================================================
' XApiGitHubAutoSearcher.vb - Automated GitHub Search System for X/Twitter API
' Pulls official Twitter repositories and community implementations
' Integrates them automatically into EQ12's XClient system
' ===============================================================================

Imports System.Net.Http
Imports Newtonsoft.Json.Linq
Imports System.IO
Imports System.Threading.Tasks

Public Class XApiGitHubAutoSearcher
    Inherits BaseIntegrator

    Private Shared ReadOnly HttpClient As New HttpClient()
    Private ReadOnly _logger As Logger
    Private ReadOnly _config As JObject

    Public Sub New()
        _logger = New Logger("XApiGitHubAutoSearcher")
        LoadSearchConfiguration()

        ' Configure GitHub API client
        If Not String.IsNullOrEmpty(Config("github")("token")?.ToString()) Then
            HttpClient.DefaultRequestHeaders.Add("Authorization", $"token {Config("github")("token")}")
        End If
        HttpClient.DefaultRequestHeaders.Add("User-Agent", "EQ12-XApiSearcher/1.0")
    End Sub

    Private Sub LoadSearchConfiguration()
        Try
            Dim configPath = "C:\EQ12\configs\x_api_search_queries.json"
            If File.Exists(configPath) Then
                _config = JObject.Parse(File.ReadAllText(configPath))
                _logger.Info($"Loaded X API search configuration from {configPath}")
            Else
                _logger.Error($"X API search configuration not found at {configPath}")
                Throw New FileNotFoundException($"Configuration file not found: {configPath}")
            End If
        Catch ex As Exception
            _logger.Error($"Failed to load X API search configuration: {ex.Message}")
            Throw
        End Try
    End Sub

    ''' <summary>
    ''' Execute all configured GitHub searches for X API repositories
    ''' </summary>
    Public Function ExecuteAutoSearch() As XApiSearchReport
        Dim report As New XApiSearchReport With {
            .SearchStartTime = DateTime.UtcNow,
            .TotalRepositoriesFound = 0,
            .SuccessfulIntegrations = 0,
            .FailedIntegrations = 0
        }

        Try
            _logger.Info("🚀 Starting automated X API GitHub search...")

            ' Search official Twitter repositories
            report.OfficialRepos = SearchOfficialRepositories()

            ' Search community betting repositories
            report.CommunityRepos = SearchCommunityBettingRepositories()

            ' Search SDK implementations
            report.SdkRepos = SearchSdkImplementations()

            report.TotalRepositoriesFound = report.OfficialRepos.Count + report.CommunityRepos.Count + report.SdkRepos.Count

            ' Integrate found repositories
            Dim integrationResults = IntegrateFoundRepositories(report)
            report.SuccessfulIntegrations = integrationResults.Where(Function(r) r.Success).Count()
            report.FailedIntegrations = integrationResults.Where(Function(r) Not r.Success).Count()

            report.SearchEndTime = DateTime.UtcNow
            report.Success = True

            ' Generate integration report
            GenerateSearchReport(report)

            ' Send notifications
            SendSearchNotifications(report)

            _logger.Info($"✅ X API search completed: {report.SuccessfulIntegrations} integrations successful")

        Catch ex As Exception
            report.Success = False
            report.ErrorMessage = ex.Message
            _logger.Error($"❌ X API search failed: {ex.Message}")
        End Try

        Return report
    End Function

    Private Function SearchOfficialRepositories() As List(Of GitHubRepository)
        Dim repos As New List(Of GitHubRepository)

        Try
            Dim officialQueries = _config("x_api_github_queries")("search_categories")("official_repos")

            For Each queryConfig In officialQueries
                Dim query = queryConfig("query").ToString()
                Dim foundRepos = ExecuteGitHubSearch(query, "official")
                repos.AddRange(foundRepos)

                _logger.Info($"Official search '{query}': {foundRepos.Count} repositories found")

                ' Rate limiting
                Threading.Thread.Sleep(1000)
            Next

        Catch ex As Exception
            _logger.Error($"Failed to search official repositories: {ex.Message}")
        End Try

        Return repos
    End Function

    Private Function SearchCommunityBettingRepositories() As List(Of GitHubRepository)
        Dim repos As New List(Of GitHubRepository)

        Try
            Dim communityQueries = _config("x_api_github_queries")("search_categories")("community_betting_repos")

            For Each queryConfig In communityQueries
                Dim query = queryConfig("query").ToString()
                Dim foundRepos = ExecuteGitHubSearch(query, "community_betting")
                repos.AddRange(foundRepos)

                _logger.Info($"Community betting search '{query}': {foundRepos.Count} repositories found")

                ' Rate limiting
                Threading.Thread.Sleep(1000)
            Next

        Catch ex As Exception
            _logger.Error($"Failed to search community betting repositories: {ex.Message}")
        End Try

        Return repos
    End Function

    Private Function SearchSdkImplementations() As List(Of GitHubRepository)
        Dim repos As New List(Of GitHubRepository)

        Try
            Dim sdkQueries = _config("x_api_github_queries")("search_categories")("sdk_implementations")

            For Each queryConfig In sdkQueries
                Dim query = queryConfig("query").ToString()
                Dim foundRepos = ExecuteGitHubSearch(query, "sdk_implementation")
                repos.AddRange(foundRepos)

                _logger.Info($"SDK implementation search '{query}': {foundRepos.Count} repositories found")

                ' Rate limiting
                Threading.Thread.Sleep(1000)
            Next

        Catch ex As Exception
            _logger.Error($"Failed to search SDK implementations: {ex.Message}")
        End Try

        Return repos
    End Function

    Private Function ExecuteGitHubSearch(query As String, category As String) As List(Of GitHubRepository)
        Dim repos As New List(Of GitHubRepository)

        Try
            Dim encodedQuery = Uri.EscapeDataString(query)
            Dim url = $"https://api.github.com/search/repositories?q={encodedQuery}&sort=stars&order=desc&per_page=25"

            Dim response = HttpClient.GetStringAsync(url).Result
            Dim searchResult = JObject.Parse(response)

            If searchResult("items") IsNot Nothing Then
                For Each item In searchResult("items")
                    Dim repo As New GitHubRepository With {
                        .Name = item("name").ToString(),
                        .FullName = item("full_name").ToString(),
                        .Description = item("description")?.ToString() ?? "",
                        .HtmlUrl = item("html_url").ToString(),
                        .CloneUrl = item("clone_url").ToString(),
                        .Stars = Convert.ToInt32(item("stargazers_count")),
                        .Language = item("language")?.ToString() ?? "",
                        .Category = category,
                        .LastUpdated = DateTime.Parse(item("updated_at").ToString())
                    }
                    repos.Add(repo)
                Next
            End If

            ' Log search to integration_log
            DBWriter.LogIntegration("XApiGitHubAutoSearcher", url, $"Found {repos.Count} repositories", "search", "success")

        Catch ex As Exception
            _logger.Error($"GitHub search failed for query '{query}': {ex.Message}")
            DBWriter.LogIntegration("XApiGitHubAutoSearcher", query, $"Search failed: {ex.Message}", "search", "fail")
        End Try

        Return repos
    End Function

    Private Function IntegrateFoundRepositories(report As XApiSearchReport) As List(Of IntegrationResult)
        Dim results As New List(Of IntegrationResult)

        Dim allRepos = New List(Of GitHubRepository)()
        allRepos.AddRange(report.OfficialRepos)
        allRepos.AddRange(report.CommunityRepos)
        allRepos.AddRange(report.SdkRepos)

        For Each repo In allRepos.OrderByDescending(Function(r) r.Stars).Take(10) ' Top 10 by stars
            Try
                _logger.Info($"🔧 Integrating repository: {repo.FullName}")

                Dim integrationResult = XApiGitHubIntegrator.IntegrateSpecificRepository(repo)
                results.Add(integrationResult)

                If integrationResult.Success Then
                    _logger.Info($"✅ Successfully integrated {repo.FullName}")
                Else
                    _logger.Warning($"⚠️ Failed to integrate {repo.FullName}: {integrationResult.ErrorMessage}")
                End If

            Catch ex As Exception
                _logger.Error($"❌ Integration error for {repo.FullName}: {ex.Message}")
                results.Add(New IntegrationResult With {
                    .Success = False,
                    .Repository = repo,
                    .ErrorMessage = ex.Message
                })
            End Try
        Next

        Return results
    End Function

    Private Sub GenerateSearchReport(report As XApiSearchReport)
        Try
            Dim reportPath = $"C:\EQ12\Reports\XApiSearch_{DateTime.UtcNow:yyyyMMdd_HHmmss}.json"
            Directory.CreateDirectory(Path.GetDirectoryName(reportPath))

            Dim reportJson = JObject.FromObject(report)
            File.WriteAllText(reportPath, reportJson.ToString(Formatting.Indented))

            _logger.Info($"📄 Search report generated: {reportPath}")

        Catch ex As Exception
            _logger.Error($"Failed to generate search report: {ex.Message}")
        End Try
    End Sub

    Private Sub SendSearchNotifications(report As XApiSearchReport)
        Try
            Dim message = $"🐦 X API GitHub Auto-Search Complete{vbNewLine}" &
                         $"📊 Total Repositories: {report.TotalRepositoriesFound}{vbNewLine}" &
                         $"✅ Successful Integrations: {report.SuccessfulIntegrations}{vbNewLine}" &
                         $"❌ Failed Integrations: {report.FailedIntegrations}{vbNewLine}" &
                         $"⏱️ Duration: {(report.SearchEndTime - report.SearchStartTime).TotalMinutes:F1} minutes{vbNewLine}" &
                         $"#EQ12 #XAPI #GitHub #Integration"

            ' Send to Telegram
            If Not String.IsNullOrEmpty(Config("telegram")("token")?.ToString()) Then
                Alerts.Telegram(Config("telegram")("token"), Config("telegram")("chat_id"), message)
            End If

            ' Send to Discord
            If Not String.IsNullOrEmpty(Config("discord")("webhook")?.ToString()) Then
                Alerts.Discord(Config("discord")("webhook"), message)
            End If

        Catch ex As Exception
            _logger.Error($"Failed to send search notifications: {ex.Message}")
        End Try
    End Sub
End Class

' ===============================================================================
' Data Structures for X API GitHub Search System
' ===============================================================================

Public Class XApiSearchReport
    Public Property SearchStartTime As DateTime
    Public Property SearchEndTime As DateTime
    Public Property Success As Boolean
    Public Property ErrorMessage As String
    Public Property TotalRepositoriesFound As Integer
    Public Property SuccessfulIntegrations As Integer
    Public Property FailedIntegrations As Integer
    Public Property OfficialRepos As New List(Of GitHubRepository)()
    Public Property CommunityRepos As New List(Of GitHubRepository)()
    Public Property SdkRepos As New List(Of GitHubRepository)()
End Class

Public Class GitHubRepository
    Public Property Name As String
    Public Property FullName As String
    Public Property Description As String
    Public Property HtmlUrl As String
    Public Property CloneUrl As String
    Public Property Stars As Integer
    Public Property Language As String
    Public Property Category As String
    Public Property LastUpdated As DateTime
End Class

Public Class IntegrationResult
    Public Property Success As Boolean
    Public Property Repository As GitHubRepository
    Public Property ErrorMessage As String
    Public Property GeneratedModules As New List(Of String)()
    Public Property ExtractedPatterns As New List(Of String)()
End Class
