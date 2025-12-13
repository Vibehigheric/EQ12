Imports System.Diagnostics
Imports System.IO
Imports System.Threading.Tasks
Imports Newtonsoft.Json.Linq

''' <summary>
''' GitHub integration for automated gist creation, repo synchronization, and version control
''' </summary>
Public Class GitHubSync

    ''' <summary>
    ''' Create a public gist with content and return the URL
    ''' </summary>
    Public Shared Async Function CreateGistAsync(title As String, extension As String, content As String, Optional description As String = "") As Task(Of String)
        Try
            Dim filename = $"{title}.{extension}"
            Dim tempFile = Path.Combine(Path.GetTempPath(), filename)

            ' Write content to temporary file
            Await File.WriteAllTextAsync(tempFile, content)

            ' Create gist using GitHub CLI
            Dim startInfo As New ProcessStartInfo With {
                .FileName = "gh",
                .Arguments = $"gist create ""{tempFile}"" --public --desc ""{If(String.IsNullOrEmpty(description), title, description)}""",
                .UseShellExecute = False,
                .RedirectStandardOutput = True,
                .RedirectStandardError = True,
                .CreateNoWindow = True
            }

            Using process = Process.Start(startInfo)
                If process Is Nothing Then
                    Throw New Exception("Failed to start GitHub CLI process")
                End If

                Dim output = Await process.StandardOutput.ReadToEndAsync()
                Dim errors = Await process.StandardError.ReadToEndAsync()

                Await Task.Run(Sub() process.WaitForExit())

                ' Clean up temporary file
                Try
                    File.Delete(tempFile)
                Catch
                    ' Ignore cleanup errors
                End Try

                If process.ExitCode = 0 Then
                    Return output.Trim()
                Else
                    Throw New Exception($"GitHub CLI error: {errors}")
                End If
            End Using

        Catch ex As Exception
            Throw New Exception($"Failed to create gist: {ex.Message}", ex)
        End Try
    End Function

    ''' <summary>
    ''' Create a gist synchronously (wrapper for async method)
    ''' </summary>
    Public Shared Function CreateGist(title As String, extension As String, content As String, Optional description As String = "") As String
        Try
            Return CreateGistAsync(title, extension, content, description).GetAwaiter().GetResult()
        Catch ex As Exception
            Throw New Exception($"Failed to create gist synchronously: {ex.Message}", ex)
        End Try
    End Function

    ''' <summary>
    ''' Push data to a GitHub repository
    ''' </summary>
    Public Shared Async Function PushToRepoAsync(repoPath As String, filename As String, content As String, commitMessage As String, Optional branch As String = "main") As Task(Of String)
        Try
            Dim tempDir = Path.Combine(Path.GetTempPath(), "eq12-sync-" & Guid.NewGuid().ToString("N")(0..7))
            Directory.CreateDirectory(tempDir)

            Try
                ' Clone repository to temp directory
                Await RunGitCommandAsync($"clone https://github.com/{repoPath}.git .", tempDir)

                ' Switch to specified branch
                If branch <> "main" Then
                    Await RunGitCommandAsync($"checkout -b {branch}", tempDir)
                End If

                ' Write file
                Dim filePath = Path.Combine(tempDir, filename)
                Await File.WriteAllTextAsync(filePath, content)

                ' Add, commit, and push
                Await RunGitCommandAsync("add .", tempDir)
                Await RunGitCommandAsync($"commit -m ""{commitMessage}""", tempDir)
                Await RunGitCommandAsync($"push origin {branch}", tempDir)

                Return $"https://github.com/{repoPath}/blob/{branch}/{filename}"

            Finally
                ' Clean up temporary directory
                Try
                    Directory.Delete(tempDir, True)
                Catch
                    ' Ignore cleanup errors
                End Try
            End Try

        Catch ex As Exception
            Throw New Exception($"Failed to push to repository: {ex.Message}", ex)
        End Try
    End Function

    ''' <summary>
    ''' Create a comprehensive betting summary gist
    ''' </summary>
    Public Shared Async Function CreateBettingSummaryGistAsync(Optional days As Integer = 7) As Task(Of String)
        Try
            Dim summary = Await GenerateBettingSummaryAsync(days)
            Dim title = $"EQ12_Betting_Summary_{DateTime.Now:yyyyMMdd}"
            Dim description = $"EQ12 Sports Betting Terminal - {days} Day Performance Summary"

            Return Await CreateGistAsync(title, "md", summary, description)

        Catch ex As Exception
            Throw New Exception($"Failed to create betting summary gist: {ex.Message}", ex)
        End Try
    End Function

    ''' <summary>
    ''' Create an arbitrage opportunities gist
    ''' </summary>
    Public Shared Async Function CreateArbitrageGistAsync() As Task(Of String)
        Try
            Dim opportunities = Await GenerateArbitrageReportAsync()
            Dim title = $"EQ12_Arbitrage_Opportunities_{DateTime.Now:yyyyMMdd_HHmmss}"
            Dim description = "EQ12 Sports Betting Terminal - Current Arbitrage Opportunities"

            Return Await CreateGistAsync(title, "json", opportunities, description)

        Catch ex As Exception
            Throw New Exception($"Failed to create arbitrage gist: {ex.Message}", ex)
        End Try
    End Function

    ''' <summary>
    ''' Backup betting data to GitHub repository
    ''' </summary>
    Public Shared Async Function BackupBettingDataAsync(repoPath As String) As Task(Of String)
        Try
            Dim backupData = Await GenerateBackupDataAsync()
            Dim filename = $"eq12-backup-{DateTime.Now:yyyyMMdd-HHmmss}.json"
            Dim commitMessage = $"EQ12 Betting Data Backup - {DateTime.Now:yyyy-MM-dd HH:mm:ss}"

            Return Await PushToRepoAsync(repoPath, filename, backupData, commitMessage)

        Catch ex As Exception
            Throw New Exception($"Failed to backup betting data: {ex.Message}", ex)
        End Try
    End Function

    ''' <summary>
    ''' Generate comprehensive betting summary in markdown format
    ''' </summary>
    Private Shared Async Function GenerateBettingSummaryAsync(days As Integer) As Task(Of String)
        Return Await Task.Run(Function()
            Dim sb As New Text.StringBuilder()

            sb.AppendLine($"# 📊 EQ12 Betting Terminal - {days} Day Summary")
            sb.AppendLine($"Generated: {DateTime.Now:yyyy-MM-dd HH:mm:ss UTC}")
            sb.AppendLine()

            Try
                ' Get performance metrics
                Using conn As New System.Data.SQLite.SQLiteConnection("Data Source=Data\bankroll.db")
                    conn.Open()

                    ' Overall performance
                    Dim sql = $"SELECT COUNT(*) as total_bets, SUM(stake) as total_wagered, SUM(profit_loss) as net_profit, AVG(CASE WHEN result IN ('Won', 'Lost') THEN CASE WHEN result = 'Won' THEN 1.0 ELSE 0.0 END END) * 100 as win_rate, AVG(odds) as avg_odds FROM bets WHERE bet_date >= date('now', '-{days} days') AND result IN ('Won', 'Lost', 'Push')"

                    Using cmd As New System.Data.SQLite.SQLiteCommand(sql, conn)
                        Using reader = cmd.ExecuteReader()
                            If reader.Read() Then
                                Dim totalBets = If(reader("total_bets") Is DBNull.Value, 0, CInt(reader("total_bets")))
                                Dim totalWagered = If(reader("total_wagered") Is DBNull.Value, 0.0, CDbl(reader("total_wagered")))
                                Dim netProfit = If(reader("net_profit") Is DBNull.Value, 0.0, CDbl(reader("net_profit")))
                                Dim winRate = If(reader("win_rate") Is DBNull.Value, 0.0, CDbl(reader("win_rate")))
                                Dim avgOdds = If(reader("avg_odds") Is DBNull.Value, 0, CInt(reader("avg_odds")))
                                Dim roi = If(totalWagered > 0, (netProfit / totalWagered) * 100, 0.0)

                                sb.AppendLine("## 📈 Performance Overview")
                                sb.AppendLine($"- **Total Bets**: {totalBets}")
                                sb.AppendLine($"- **Total Wagered**: ${totalWagered:F2}")
                                sb.AppendLine($"- **Net Profit**: ${netProfit:F2}")
                                sb.AppendLine($"- **ROI**: {roi:F2}%")
                                sb.AppendLine($"- **Win Rate**: {winRate:F1}%")
                                sb.AppendLine($"- **Avg Odds**: {If(avgOdds > 0, "+" & avgOdds.ToString(), avgOdds.ToString())}")
                                sb.AppendLine()
                            End If
                        End Using
                    End Using

                    ' Sport breakdown
                    sb.AppendLine("## 🏈 Performance by Sport")
                    sql = $"SELECT sport, COUNT(*) as bets, SUM(stake) as wagered, SUM(profit_loss) as profit, AVG(CASE WHEN result IN ('Won', 'Lost') THEN CASE WHEN result = 'Won' THEN 1.0 ELSE 0.0 END END) * 100 as win_rate FROM bets WHERE bet_date >= date('now', '-{days} days') AND result IN ('Won', 'Lost', 'Push') GROUP BY sport ORDER BY profit DESC"

                    Using cmd As New System.Data.SQLite.SQLiteCommand(sql, conn)
                        Using reader = cmd.ExecuteReader()
                            sb.AppendLine("| Sport | Bets | Wagered | Profit | Win Rate | ROI |")
                            sb.AppendLine("|-------|------|---------|--------|----------|-----|")

                            While reader.Read()
                                Dim sport = reader("sport").ToString()
                                Dim bets = CInt(reader("bets"))
                                Dim wagered = CDbl(reader("wagered"))
                                Dim profit = CDbl(reader("profit"))
                                Dim winRate = If(reader("win_rate") Is DBNull.Value, 0.0, CDbl(reader("win_rate")))
                                Dim roi = If(wagered > 0, (profit / wagered) * 100, 0.0)

                                sb.AppendLine($"| {sport} | {bets} | ${wagered:F0} | ${profit:F2} | {winRate:F1}% | {roi:F1}% |")
                            End While
                        End Using
                    End Using

                    sb.AppendLine()

                    ' Recent arbitrage opportunities
                    sb.AppendLine("## ⚡ Recent Arbitrage Opportunities")
                    sql = $"SELECT COUNT(*) as total_arbs, AVG(profit_percentage) as avg_profit, SUM(guaranteed_profit) as total_guaranteed FROM arbitrage_opportunities WHERE detected_at >= datetime('now', '-{days} days')"

                    Using cmd As New System.Data.SQLite.SQLiteCommand(sql, conn)
                        Using reader = cmd.ExecuteReader()
                            If reader.Read() Then
                                Dim totalArbs = If(reader("total_arbs") Is DBNull.Value, 0, CInt(reader("total_arbs")))
                                Dim avgProfit = If(reader("avg_profit") Is DBNull.Value, 0.0, CDbl(reader("avg_profit")))
                                Dim totalGuaranteed = If(reader("total_guaranteed") Is DBNull.Value, 0.0, CDbl(reader("total_guaranteed")))

                                sb.AppendLine($"- **Total Opportunities**: {totalArbs}")
                                sb.AppendLine($"- **Average Profit**: {avgProfit:F2}%")
                                sb.AppendLine($"- **Total Guaranteed Profit**: ${totalGuaranteed:F2}")
                            End If
                        End Using
                    End Using
                End Using

            Catch ex As Exception
                sb.AppendLine($"Error generating summary: {ex.Message}")
            End Try

            sb.AppendLine()
            sb.AppendLine("---")
            sb.AppendLine("*Generated by EQ12 Sports Betting Terminal*")

            Return sb.ToString()
        End Function)
    End Function

    ''' <summary>
    ''' Generate arbitrage opportunities report in JSON format
    ''' </summary>
    Private Shared Async Function GenerateArbitrageReportAsync() As Task(Of String)
        Return Await Task.Run(Function()
            Dim report As New JObject()
            report("generated_at") = DateTime.UtcNow.ToString("o")
            report("opportunities") = New JArray()

            Try
                Using conn As New System.Data.SQLite.SQLiteConnection("Data Source=Data\bankroll.db")
                    conn.Open()

                    Dim sql = "SELECT * FROM arbitrage_opportunities WHERE status = 'detected' AND expires_at > datetime('now') ORDER BY profit_percentage DESC LIMIT 50"

                    Using cmd As New System.Data.SQLite.SQLiteCommand(sql, conn)
                        Using reader = cmd.ExecuteReader()
                            While reader.Read()
                                Dim opp As New JObject()
                                opp("id") = CInt(reader("id"))
                                opp("event_id") = reader("event_id").ToString()
                                opp("sport") = reader("sport").ToString()
                                opp("market") = reader("market").ToString()
                                opp("side_a") = New JObject From {
                                    {"selection", reader("side_a_selection").ToString()},
                                    {"book", reader("side_a_book").ToString()},
                                    {"odds", CInt(reader("side_a_odds"))},
                                    {"stake", CDbl(reader("stake_a"))}
                                }
                                opp("side_b") = New JObject From {
                                    {"selection", reader("side_b_selection").ToString()},
                                    {"book", reader("side_b_book").ToString()},
                                    {"odds", CInt(reader("side_b_odds"))},
                                    {"stake", CDbl(reader("stake_b"))}
                                }
                                opp("profit_percentage") = CDbl(reader("profit_percentage"))
                                opp("guaranteed_profit") = CDbl(reader("guaranteed_profit"))
                                opp("detected_at") = reader("detected_at").ToString()
                                opp("expires_at") = reader("expires_at").ToString()

                                CType(report("opportunities"), JArray).Add(opp)
                            End While
                        End Using
                    End Using
                End Using

            Catch ex As Exception
                report("error") = ex.Message
            End Try

            Return report.ToString(Newtonsoft.Json.Formatting.Indented)
        End Function)
    End Function

    ''' <summary>
    ''' Generate comprehensive backup data in JSON format
    ''' </summary>
    Private Shared Async Function GenerateBackupDataAsync() As Task(Of String)
        Return Await Task.Run(Function()
            Dim backup As New JObject()
            backup("backup_date") = DateTime.UtcNow.ToString("o")
            backup("version") = "1.0"

            Try
                Using conn As New System.Data.SQLite.SQLiteConnection("Data Source=Data\bankroll.db")
                    conn.Open()

                    ' Backup bets
                    backup("bets") = New JArray()
                    Dim sql = "SELECT * FROM bets WHERE bet_date >= date('now', '-30 days') ORDER BY created_at DESC"

                    Using cmd As New System.Data.SQLite.SQLiteCommand(sql, conn)
                        Using reader = cmd.ExecuteReader()
                            While reader.Read()
                                Dim bet As New JObject()
                                For i = 0 To reader.FieldCount - 1
                                    bet(reader.GetName(i)) = If(reader(i) Is DBNull.Value, Nothing, reader(i))
                                Next
                                CType(backup("bets"), JArray).Add(bet)
                            End While
                        End Using
                    End Using

                    ' Backup arbitrage opportunities
                    backup("arbitrage_opportunities") = New JArray()
                    sql = "SELECT * FROM arbitrage_opportunities WHERE detected_at >= datetime('now', '-7 days') ORDER BY detected_at DESC"

                    Using cmd As New System.Data.SQLite.SQLiteCommand(sql, conn)
                        Using reader = cmd.ExecuteReader()
                            While reader.Read()
                                Dim arb As New JObject()
                                For i = 0 To reader.FieldCount - 1
                                    arb(reader.GetName(i)) = If(reader(i) Is DBNull.Value, Nothing, reader(i))
                                Next
                                CType(backup("arbitrage_opportunities"), JArray).Add(arb)
                            End While
                        End Using
                    End Using

                    ' Backup bankroll history
                    backup("bankroll_history") = New JArray()
                    sql = "SELECT * FROM bankroll_history WHERE date >= date('now', '-30 days') ORDER BY date DESC"

                    Using cmd As New System.Data.SQLite.SQLiteCommand(sql, conn)
                        Using reader = cmd.ExecuteReader()
                            While reader.Read()
                                Dim history As New JObject()
                                For i = 0 To reader.FieldCount - 1
                                    history(reader.GetName(i)) = If(reader(i) Is DBNull.Value, Nothing, reader(i))
                                Next
                                CType(backup("bankroll_history"), JArray).Add(history)
                            End While
                        End Using
                    End Using
                End Using

            Catch ex As Exception
                backup("error") = ex.Message
            End Try

            Return backup.ToString(Newtonsoft.Json.Formatting.Indented)
        End Function)
    End Function

    ''' <summary>
    ''' Run a git command in the specified directory
    ''' </summary>
    Private Shared Async Function RunGitCommandAsync(arguments As String, workingDirectory As String) As Task
        Dim startInfo As New ProcessStartInfo With {
            .FileName = "git",
            .Arguments = arguments,
            .WorkingDirectory = workingDirectory,
            .UseShellExecute = False,
            .RedirectStandardOutput = True,
            .RedirectStandardError = True,
            .CreateNoWindow = True
        }

        Using process = Process.Start(startInfo)
            If process Is Nothing Then
                Throw New Exception("Failed to start git process")
            End If

            Dim output = Await process.StandardOutput.ReadToEndAsync()
            Dim errors = Await process.StandardError.ReadToEndAsync()

            Await Task.Run(Sub() process.WaitForExit())

            If process.ExitCode <> 0 Then
                Throw New Exception($"Git command failed: {errors}")
            End If
        End Using
    End Function

End Class
