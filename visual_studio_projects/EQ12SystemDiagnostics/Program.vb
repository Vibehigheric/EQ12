Imports System
Imports System.IO
Imports System.Text
Imports System.Net.Http
Imports System.Text.Json
Imports System.Threading.Tasks
Imports System.Diagnostics
Imports System.Collections.Generic

Module Program
    Public Async Function Main(args As String()) As Task
        Dim options = DiagnosticsOptions.Parse(args)
        Dim runner As New DiagnosticsRunner(options)
        runner.Register(New Eq12StartupCheck())
        runner.Register(New ChromeSetupCheck())
        runner.Register(New ApiConfigurationCheck())
        runner.Register(New ProgramDiscoveryCheck())
        runner.Register(New SystemStatisticsCheck())
        runner.Register(New SyntaxValidationCheck())

        Dim results = Await runner.RunAsync()
        DiagnosticsReporter.Render(results)

        If options.GenerateSportsQueries Then
            Dim sportsCoordinator As New SportsQueryCoordinator()
            Await sportsCoordinator.RunAsync(options)
        End If

        If results.Exists(Function(r) r.Status = DiagnosticStatus.Failed) Then
            Environment.ExitCode = 1
        ElseIf results.Exists(Function(r) r.Status = DiagnosticStatus.Warning) Then
            Environment.ExitCode = 2
        Else
            Environment.ExitCode = 0
        End If
    End Function
End Module

#Region "Options"

Public Class DiagnosticsOptions
    Public Property RepoRoot As String = "C:\EQ12"
    Public Property GenerateSportsQueries As Boolean
    Public Property SportsOutputPath As String = Path.Combine("C:\EQ12", "data", "sports_queries.json")
    Public Property MaxTweetsPerQuery As Integer = 100
    Public Property KeywordsFile As String = Path.Combine("C:\EQ12", "configs", "sports_keywords.txt")

    Public Shared Function Parse(args As String()) As DiagnosticsOptions
        Dim opts As New DiagnosticsOptions()
        Dim i As Integer = 0
        While i < args.Length
            Select Case args(i).ToLowerInvariant()
                Case "--repo-root"
                    If i + 1 < args.Length Then
                        opts.RepoRoot = args(i + 1)
                        i += 1
                    End If
                Case "--sports"
                    opts.GenerateSportsQueries = True
                Case "--sports-output"
                    If i + 1 < args.Length Then
                        opts.SportsOutputPath = args(i + 1)
                        i += 1
                    End If
                Case "--max-tweets"
                    If i + 1 < args.Length AndAlso Integer.TryParse(args(i + 1), opts.MaxTweetsPerQuery) Then
                        i += 1
                    End If
                Case "--keywords"
                    If i + 1 < args.Length Then
                        opts.KeywordsFile = args(i + 1)
                        i += 1
                    End If
            End Select
            i += 1
        End While
        Return opts
    End Function
End Class

#End Region

#Region "Diagnostics Framework"

Public Enum DiagnosticStatus
    Passed
    Warning
    Failed
End Enum

Public Class DiagnosticResult
    Public Property Name As String = String.Empty
    Public Property Status As DiagnosticStatus
    Public Property Messages As New List(Of String)()
    Public Property Suggestions As New List(Of String)()
    Public Property Duration As TimeSpan
End Class

Public Interface IDiagnosticCheck
    ReadOnly Property Name As String
    Function ExecuteAsync(options As DiagnosticsOptions) As Task(Of DiagnosticResult)
End Interface

Public Class DiagnosticsRunner
    Private ReadOnly _checks As New List(Of IDiagnosticCheck)()
    Private ReadOnly _options As DiagnosticsOptions

    Public Sub New(options As DiagnosticsOptions)
        _options = options
    End Sub

    Public Sub Register(check As IDiagnosticCheck)
        _checks.Add(check)
    End Sub

    Public Async Function RunAsync() As Task(Of List(Of DiagnosticResult))
        Dim results As New List(Of DiagnosticResult)
        For Each check In _checks
            Dim sw = Stopwatch.StartNew()
            Try
                Dim result = Await check.ExecuteAsync(_options)
                result.Duration = sw.Elapsed
                results.Add(result)
            Catch ex As Exception
                results.Add(New DiagnosticResult With {
                    .Name = check.Name,
                    .Status = DiagnosticStatus.Failed,
                    .Duration = sw.Elapsed,
                    .Messages = New List(Of String) From { "Unhandled exception: " & ex.Message },
                    .Suggestions = New List(Of String) From { "Check logs and rerun diagnostics with verbose tracing." }
                })
            End Try
        Next
        Return results
    End Function
End Class

Public NotInheritable Class DiagnosticsReporter
    Private Sub New()
    End Sub

    Public Shared Sub Render(results As List(Of DiagnosticResult))
        Console.OutputEncoding = Encoding.UTF8
        Console.WriteLine("EQ12 Diagnostics Summary")
        Console.WriteLine(New String("-"c, 60))
        For Each result In results
            Dim icon = If(result.Status = DiagnosticStatus.Passed, "[OK]", If(result.Status = DiagnosticStatus.Warning, "[WARN]", "[FAIL]"))
            Console.WriteLine($"{icon} {result.Name} [{result.Status}] ({result.Duration.TotalMilliseconds:n0} ms)")
            For Each message In result.Messages
                Console.WriteLine($"    - {message}")
            Next
            If result.Suggestions.Count > 0 Then
                Console.WriteLine("    Suggestions:")
                For Each suggestion In result.Suggestions
                    Console.WriteLine($"      * {suggestion}")
                Next
            End If
            Console.WriteLine()
        Next
    End Sub
End Class

#End Region

#Region "Check Implementations"

Public Class Eq12StartupCheck
    Implements IDiagnosticCheck

    Public ReadOnly Property Name As String Implements IDiagnosticCheck.Name
        Get
            Return "EQ12 Startup Files"
        End Get
    End Property

    Public Async Function ExecuteAsync(options As DiagnosticsOptions) As Task(Of DiagnosticResult) Implements IDiagnosticCheck.ExecuteAsync
        Dim result As New DiagnosticResult With {.Name = Name, .Status = DiagnosticStatus.Passed}
        Await Task.Yield()

        Dim mandatoryPaths = {
            Path.Combine(options.RepoRoot, "Start-EQ12-GODSTACK-Clean.ps1"),
            Path.Combine(options.RepoRoot, "EQ12_Interactive_Launcher.ps1"),
            Path.Combine(options.RepoRoot, "scripts"),
            Path.Combine(options.RepoRoot, "logs"),
            Path.Combine(options.RepoRoot, "tests")
        }

        For Each item In mandatoryPaths
            If Directory.Exists(item) OrElse File.Exists(item) Then
                result.Messages.Add($"Found {item}")
            Else
                result.Status = DiagnosticStatus.Warning
                result.Messages.Add($"Missing {item}")
                result.Suggestions.Add($"Restore {item} from source control or regenerate it before starting the stack.")
            End If
        Next

        Return result
    End Function
End Class

Public Class ChromeSetupCheck
    Implements IDiagnosticCheck

    Public ReadOnly Property Name As String Implements IDiagnosticCheck.Name
        Get
            Return "Chrome Automation Setup"
        End Get
    End Property

    Public Async Function ExecuteAsync(options As DiagnosticsOptions) As Task(Of DiagnosticResult) Implements IDiagnosticCheck.ExecuteAsync
        Dim result As New DiagnosticResult With {.Name = Name, .Status = DiagnosticStatus.Passed}
        Await Task.Yield()

        Dim chromePaths = {
            "C:\Program Files\Google\Chrome\Application\chrome.exe",
            "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        }

        If Array.Exists(chromePaths, AddressOf File.Exists) Then
            result.Messages.Add("Chrome executable located.")
        Else
            result.Status = DiagnosticStatus.Failed
            result.Messages.Add("Chrome executable not found.")
            result.Suggestions.Add("Install Google Chrome or update the path configuration.")
        End If

        Dim governanceScript = Path.Combine(options.RepoRoot, "chrome_governance_automation.py")
        If File.Exists(governanceScript) Then
            result.Messages.Add("Chrome governance automation script available.")
        Else
            result.Status = DiagnosticStatus.Warning
            result.Messages.Add("chrome_governance_automation.py missing.")
            result.Suggestions.Add("Run eq12 governance bootstrap or restore the script from backups.")
        End If

        Return result
    End Function
End Class

Public Class ApiConfigurationCheck
    Implements IDiagnosticCheck

    Public ReadOnly Property Name As String Implements IDiagnosticCheck.Name
        Get
            Return "API Credential Configuration"
        End Get
    End Property

    Private Shared ReadOnly CriticalVars As String() = {
        "X_BEARER_TOKEN", "ODDS_API_KEY", "OPENAI_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"
    }

    Public Async Function ExecuteAsync(options As DiagnosticsOptions) As Task(Of DiagnosticResult) Implements IDiagnosticCheck.ExecuteAsync
        Dim result As New DiagnosticResult With {.Name = Name, .Status = DiagnosticStatus.Passed}
        Await Task.Yield()

        For Each varName In CriticalVars
            Dim value = Environment.GetEnvironmentVariable(varName)
            If String.IsNullOrWhiteSpace(value) Then
                result.Status = DiagnosticStatus.Warning
                result.Messages.Add($"{varName} not configured.")
                result.Suggestions.Add($"Set {varName} in your environment or secrets store.")
            Else
                result.Messages.Add($"{varName} detected.")
            End If
        Next

        Return result
    End Function
End Class

Public Class ProgramDiscoveryCheck
    Implements IDiagnosticCheck

    Public ReadOnly Property Name As String Implements IDiagnosticCheck.Name
        Get
            Return "Program Discovery"
        End Get
    End Property

    Public Async Function ExecuteAsync(options As DiagnosticsOptions) As Task(Of DiagnosticResult) Implements IDiagnosticCheck.ExecuteAsync
        Dim result As New DiagnosticResult With {.Name = Name, .Status = DiagnosticStatus.Passed}
        Await Task.Yield()

        Dim scriptsDir = Path.Combine(options.RepoRoot, "scripts")
        If Directory.Exists(scriptsDir) Then
            Dim topScripts = Directory.GetFiles(scriptsDir, "*.ps1")
            Dim pythonScripts = Directory.GetFiles(scriptsDir, "*.py")
            result.Messages.Add($"PowerShell scripts: {topScripts.Length}")
            result.Messages.Add($"Python automations: {pythonScripts.Length}")
        Else
            result.Status = DiagnosticStatus.Warning
            result.Messages.Add("scripts directory missing.")
            result.Suggestions.Add("Check repository integrity or update RepoRoot setting.")
        End If

        Return result
    End Function
End Class

Public Class SystemStatisticsCheck
    Implements IDiagnosticCheck

    Public ReadOnly Property Name As String Implements IDiagnosticCheck.Name
        Get
            Return "System Statistics"
        End Get
    End Property

    Public Async Function ExecuteAsync(options As DiagnosticsOptions) As Task(Of DiagnosticResult) Implements IDiagnosticCheck.ExecuteAsync
        Dim result As New DiagnosticResult With {.Name = Name, .Status = DiagnosticStatus.Passed}
        Await Task.Yield()

        If Not Directory.Exists(options.RepoRoot) Then
            result.Status = DiagnosticStatus.Failed
            result.Messages.Add($"Repository root {options.RepoRoot} not found.")
            Return result
        End If

        Dim counts = New Dictionary(Of String, Integer)(StringComparer.OrdinalIgnoreCase) From {
            {".py", 0},
            {".ps1", 0},
            {".vb", 0},
            {".json", 0}
        }

        For Each filePath In Directory.EnumerateFiles(options.RepoRoot, "*.*", SearchOption.AllDirectories)
            Dim ext = Path.GetExtension(filePath)
            If counts.ContainsKey(ext) Then
                counts(ext) += 1
            End If
        Next

        For Each kvp In counts
            result.Messages.Add($"{kvp.Key} files: {kvp.Value}")
        Next

        Return result
    End Function
End Class

Public Class SyntaxValidationCheck
    Implements IDiagnosticCheck

    Public ReadOnly Property Name As String Implements IDiagnosticCheck.Name
        Get
            Return "Syntax Validation"
        End Get
    End Property

    Public Async Function ExecuteAsync(options As DiagnosticsOptions) As Task(Of DiagnosticResult) Implements IDiagnosticCheck.ExecuteAsync
        Dim result As New DiagnosticResult With {.Name = Name, .Status = DiagnosticStatus.Passed}
        Await Task.Yield()

        Dim psErrors = RunPowerShellSyntaxScan(options.RepoRoot)
        If psErrors.Count > 0 Then
            result.Status = DiagnosticStatus.Warning
            result.Messages.Add("PowerShell syntax issues detected.")
            result.Messages.AddRange(psErrors)
            result.Suggestions.Add("Run PowerShell Editor Services or VS Code formatter to resolve the listed files.")
        Else
            result.Messages.Add("PowerShell scripts parsed without errors.")
        End If

        Dim pythonErrors = RunPythonSyntaxScan(options.RepoRoot)
        If pythonErrors.Count > 0 Then
            result.Status = DiagnosticStatus.Warning
            result.Messages.Add("Python syntax issues detected.")
            result.Messages.AddRange(pythonErrors)
            result.Suggestions.Add("Execute `python -m compileall` for detailed traces.")
        Else
            result.Messages.Add("Python compile check passed.")
        End If

        Return result
    End Function

    Private Shared Function RunPowerShellSyntaxScan(root As String) As List(Of String)
        Dim messages As New List(Of String)()
        Dim sanitizedRoot = root.Replace("'", "''")
        Dim scriptBuilder As New StringBuilder()
        scriptBuilder.AppendLine("$ErrorActionPreference = 'Stop'")
        scriptBuilder.AppendLine("$issues = @()")
        scriptBuilder.AppendLine("Get-ChildItem -Recurse -Path '" & sanitizedRoot & "' -Filter '*.ps1' | ForEach-Object {")
        scriptBuilder.AppendLine("    $tokens = $null")
        scriptBuilder.AppendLine("    $parseErrors = $null")
        scriptBuilder.AppendLine("    [System.Management.Automation.Language.Parser]::ParseFile($_.FullName, [ref]$tokens, [ref]$parseErrors)")
        scriptBuilder.AppendLine("    if ($parseErrors) {")
        scriptBuilder.AppendLine("        $issues += ($parseErrors | ForEach-Object { $_.Message + ' (' + $_.Extent.File + ':' + $_.Extent.StartLineNumber + ')' })")
        scriptBuilder.AppendLine("    }")
        scriptBuilder.AppendLine("}")
        scriptBuilder.AppendLine("if ($issues.Count -gt 0) {")
        scriptBuilder.AppendLine("    $issues -join '|'")
        scriptBuilder.AppendLine("}")

        Dim tempPath = Path.GetTempFileName() & ".ps1"
        File.WriteAllText(tempPath, scriptBuilder.ToString(), Encoding.UTF8)

        Dim psi As New ProcessStartInfo("powershell.exe", "-NoProfile -ExecutionPolicy Bypass -File \"" & tempPath & "\"") With {
            .RedirectStandardOutput = True,
            .RedirectStandardError = True,
            .UseShellExecute = False,
            .CreateNoWindow = True
        }

        Try
            Using proc = Process.Start(psi)
                Dim output = proc.StandardOutput.ReadToEnd()
                Dim errs = proc.StandardError.ReadToEnd()
                proc.WaitForExit(60000)
                If proc.ExitCode <> 0 AndAlso Not String.IsNullOrWhiteSpace(errs) Then
                    messages.Add("PowerShell parser error: " & errs.Trim())
                ElseIf Not String.IsNullOrWhiteSpace(output) Then
                    For Each item In output.Trim().Split("|"c)
                        If Not String.IsNullOrWhiteSpace(item) Then
                            messages.Add(item.Trim())
                        End If
                    Next
                End If
            End Using
        Catch ex As Exception
            messages.Add("PowerShell parser failed: " & ex.Message)
        Finally
            Try
                If File.Exists(tempPath) Then
                    File.Delete(tempPath)
                End If
            Catch
            End Try
        End Try

        Return messages
    End Function

    Private Shared Function RunPythonSyntaxScan(root As String) As List(Of String)
        Dim messages As New List(Of String)()
        Dim psi As New ProcessStartInfo With {
            .FileName = "python",
            .Arguments = "-m compileall \"" & root & "\"",
            .RedirectStandardOutput = True,
            .RedirectStandardError = True,
            .UseShellExecute = False,
            .CreateNoWindow = True
        }

        Try
            Using proc = Process.Start(psi)
                Dim stderr = proc.StandardError.ReadToEnd()
                proc.WaitForExit(60000)
                If proc.ExitCode <> 0 Then
                    messages.Add("python -m compileall reported errors.")
                    If Not String.IsNullOrWhiteSpace(stderr) Then
                        messages.AddRange(stderr.Split({Environment.NewLine}, StringSplitOptions.RemoveEmptyEntries))
                    End If
                End If
            End Using
        Catch ex As Exception
            messages.Add("Python compiler unavailable: " & ex.Message)
        End Try

        Return messages
    End Function
End Class

#End Region

#Region "Sports Query Builder"

Public Class SportsQueryCoordinator
    Private Shared ReadOnly KeywordsFallback As String() = {
        "NFL", "NBA", "MLB", "NHL", "MLS", "Premier League", "La Liga", "Serie A", "FIFA", "UEFA",
        "Super Bowl", "World Cup", "Manchester United", "FC Barcelona", "Los Angeles Lakers",
        "Golden State Warriors", "New York Yankees", "Dallas Cowboys", "Boston Celtics", "Chicago Bulls",
        "Real Madrid", "Kansas City Chiefs", "Philadelphia Eagles", "Miami Dolphins", "San Francisco 49ers",
        "New England Patriots", "Houston Astros", "Atlanta Braves", "Toronto Maple Leafs"
    }

    Public Async Function RunAsync(options As DiagnosticsOptions) As Task
        Dim keywords = LoadKeywords(options.KeywordsFile)
        Dim client = New HttpClient()
        Dim bearer = Environment.GetEnvironmentVariable("X_BEARER_TOKEN")
        If String.IsNullOrWhiteSpace(bearer) Then
            Console.WriteLine("X_BEARER_TOKEN not configured. Skipping sports query generation.")
            Return
        End If

        client.DefaultRequestHeaders.Authorization = New System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", bearer)

        Dim queries = BuildQueryBatches(keywords)
        Dim aggregated As New List(Of SportsQueryResult)
        For Each query In queries
            Dim search = Await SearchTweetsAsync(client, query, options.MaxTweetsPerQuery)
            aggregated.Add(search)
            Console.WriteLine($"Fetched {search.Tweets.Count} tweets for: {query.Query}")
        Next

        Dim outputDir = Path.GetDirectoryName(options.SportsOutputPath)
        If Not Directory.Exists(outputDir) Then
            Directory.CreateDirectory(outputDir)
        End If

        Dim json = JsonSerializer.Serialize(aggregated, New JsonSerializerOptions With {.WriteIndented = True})
        Await File.WriteAllTextAsync(options.SportsOutputPath, json)
        Console.WriteLine($"Saved sports query results to {options.SportsOutputPath}")
    End Function

    Private Shared Function LoadKeywords(path As String) As List(Of String)
        If File.Exists(path) Then
            Dim filtered As New List(Of String)
            For Each line In File.ReadAllLines(path)
                Dim trimmed = line.Trim()
                If trimmed.Length > 0 AndAlso Not trimmed.StartsWith("#") Then
                    filtered.Add(trimmed)
                End If
            Next
            If filtered.Count > 0 Then
                Return filtered
            End If
        End If
        Return New List(Of String)(KeywordsFallback)
    End Function

    Private Shared Function BuildQueryBatches(keywords As List(Of String)) As List(Of SportsQuery)
        Const maxLength As Integer = 512
        Dim batches As New List(Of SportsQuery)
        Dim current As New List(Of String)
        Dim sb As New StringBuilder()

        For Each keyword In keywords
            Dim normalized = keyword.Replace("\""c, "").Trim()
            If normalized.Length = 0 Then Continue For

            Dim candidate = If(sb.Length = 0, normalized, sb.ToString() & " OR " & normalized)
            If candidate.Length > maxLength AndAlso current.Count > 0 Then
                batches.Add(New SportsQuery(String.Join(" OR ", current)))
                current.Clear()
                sb.Clear()
            End If
            current.Add(normalized)
            If sb.Length = 0 Then
                sb.Append(normalized)
            Else
                sb.Append(" OR ").Append(normalized)
            End If
        Next

        If current.Count > 0 Then
            batches.Add(New SportsQuery(String.Join(" OR ", current)))
        End If

        Return batches
    End Function

    Private Shared Async Function SearchTweetsAsync(client As HttpClient, query As SportsQuery, maxTweets As Integer) As Task(Of SportsQueryResult)
        Dim endpoint As String = "https://api.x.com/2/tweets/search/all"
        Dim collected As New List(Of TweetRecord)
        Dim nextToken As String = Nothing

        Do
            Dim remaining = Math.Max(0, maxTweets - collected.Count)
            If remaining = 0 Then Exit Do

            Dim uriBuilder As New UriBuilder(endpoint)
            Dim urlQuery As New List(Of String) From {
                "query=" & Uri.EscapeDataString(query.Query),
                "max_results=" & Math.Min(500, remaining).ToString()
            }
            If Not String.IsNullOrWhiteSpace(nextToken) Then
                urlQuery.Add("next_token=" & Uri.EscapeDataString(nextToken))
            End If
            uriBuilder.Query = String.Join("&", urlQuery)

            Dim response = Await client.GetAsync(uriBuilder.Uri)
            Dim payload = Await response.Content.ReadAsStringAsync()
            If Not response.IsSuccessStatusCode Then
                Return New SportsQueryResult With {
                    .Query = query,
                    .Tweets = collected,
                    .RawResponse = payload,
                    .[Error] = "HTTP " & CInt(response.StatusCode).ToString() & ": " & response.ReasonPhrase
                }
            End If

            Dim document = JsonDocument.Parse(payload)
            If document.RootElement.TryGetProperty("data", Nothing) Then
                For Each item In document.RootElement.GetProperty("data").EnumerateArray()
                    Dim tweet As New TweetRecord With {
                        .Id = item.GetProperty("id").GetString(),
                        .Text = item.GetProperty("text").GetString(),
                        .AuthorId = If(item.TryGetProperty("author_id", Nothing), item.GetProperty("author_id").GetString(), Nothing),
                        .CreatedAt = If(item.TryGetProperty("created_at", Nothing), item.GetProperty("created_at").GetString(), Nothing)
                    }
                    collected.Add(tweet)
                    If collected.Count >= maxTweets Then Exit For
                Next
            End If

            If collected.Count >= maxTweets Then Exit Do

            If document.RootElement.TryGetProperty("meta", Nothing) AndAlso document.RootElement.GetProperty("meta").TryGetProperty("next_token", Nothing) Then
                nextToken = document.RootElement.GetProperty("meta").GetProperty("next_token").GetString()
            Else
                Exit Do
            End If
        Loop While collected.Count < maxTweets

        Return New SportsQueryResult With {
            .Query = query,
            .Tweets = collected
        }
    End Function
End Class

Public Class SportsQuery
    Public Property Query As String

    Public Sub New(value As String)
        Query = value
    End Sub
End Class

Public Class TweetRecord
    Public Property Id As String
    Public Property Text As String
    Public Property AuthorId As String
    Public Property CreatedAt As String
End Class

Public Class SportsQueryResult
    Public Property Query As SportsQuery
    Public Property Tweets As List(Of TweetRecord) = New List(Of TweetRecord)()
    Public Property RawResponse As String
    Public Property [Error] As String
End Class

#End Region
