Imports System.IO
Imports System.Data.SQLite
Imports Newtonsoft.Json.Linq
Imports System.Text
Imports System.Text.RegularExpressions
Imports System.Linq

''' <summary>
''' LogManagerHelper: Comprehensive log management and analysis system for EQ12 stack
''' Features: Centralized log analysis, cleanup, archiving, monetizable insights extraction
''' Handles: Error pattern detection, performance analytics, security monitoring, compliance reporting
''' </summary>
Public Class LogManagerHelper

#Region "Core Log Management Functions"

    ''' <summary>
    ''' Analyze all EQ12 logs for patterns, errors, and monetizable insights
    ''' </summary>
    Public Shared Function AnalyzeLogs(cfg As JObject, Optional days As Integer = 7) As JObject
        Try
            Dim analysis As New JObject()
            analysis("timestamp") = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
            analysis("analysis_period_days") = days

            Dim logFiles As List(Of String) = DiscoverLogFiles()
            analysis("total_log_files") = logFiles.Count

            If logFiles.Count = 0 Then
                analysis("success") = False
                analysis("message") = "No log files found"
                Return analysis
            End If

            ' Analyze each category
            analysis("error_analysis") = AnalyzeErrors(logFiles, days)
            analysis("performance_analysis") = AnalyzePerformance(logFiles, days)
            analysis("security_analysis") = AnalyzeSecurity(logFiles, days)
            analysis("monetization_insights") = ExtractMonetizationInsights(logFiles, days)
            analysis("system_health") = AssessSystemHealth(logFiles, days)

            ' Generate recommendations
            analysis("recommendations") = GenerateRecommendations(analysis)

            ' Log the analysis
            LogAnalysisResult(analysis)

            analysis("success") = True
            Return analysis

        Catch ex As Exception
            Console.WriteLine($"❌ Log analysis failed: {ex.Message}")
            Dim errorResult As New JObject()
            errorResult("success") = False
            errorResult("error") = ex.Message
            Return errorResult
        End Try
    End Function

    ''' <summary>
    ''' Clean up old logs based on retention policy
    ''' </summary>
    Public Shared Function CleanupLogs(cfg As JObject) As JObject
        Try
            Dim cleanupResult As New JObject()
            cleanupResult("timestamp") = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")

            Dim retentionDays As Integer = If(cfg("log_manager")?("retention_days")?.ToObject(Of Integer)(), 30)
            Dim cutoffDate As DateTime = DateTime.Now.AddDays(-retentionDays)

            Dim logFiles As List(Of String) = DiscoverLogFiles()
            Dim filesToDelete As New List(Of String)()
            Dim filesToArchive As New List(Of String)()
            Dim totalSizeFreed As Long = 0

            For Each logFile As String In logFiles
                Try
                    Dim fileInfo As New FileInfo(logFile)

                    If fileInfo.LastWriteTime < cutoffDate Then
                        If cfg("log_manager")?("archive_before_delete")?.ToString() = "True" Then
                            ' Archive first, then delete
                            Dim archivePath As String = ArchiveLogFile(logFile, cfg)
                            If Not String.IsNullOrEmpty(archivePath) Then
                                filesToArchive.Add(archivePath)
                            End If
                        End If

                        totalSizeFreed += fileInfo.Length
                        File.Delete(logFile)
                        filesToDelete.Add(logFile)
                    End If

                Catch ex As Exception
                    Console.WriteLine($"Failed to process {logFile}: {ex.Message}")
                End Try
            Next

            cleanupResult("files_deleted") = filesToDelete.Count
            cleanupResult("files_archived") = filesToArchive.Count
            cleanupResult("size_freed_mb") = Math.Round(totalSizeFreed / (1024.0 * 1024.0), 2)
            cleanupResult("retention_days") = retentionDays
            cleanupResult("success") = True

            ' Log the cleanup
            LogCleanupResult(cleanupResult)

            Console.WriteLine($"✅ Log cleanup completed: {filesToDelete.Count} files deleted, {Math.Round(totalSizeFreed / (1024.0 * 1024.0), 2)} MB freed")

            Return cleanupResult

        Catch ex As Exception
            Console.WriteLine($"❌ Log cleanup failed: {ex.Message}")
            Dim errorResult As New JObject()
            errorResult("success") = False
            errorResult("error") = ex.Message
            Return errorResult
        End Try
    End Function

    ''' <summary>
    ''' Archive log files to compressed storage
    ''' </summary>
    Public Shared Function ArchiveLogs(cfg As JObject, Optional forceArchive As Boolean = False) As JObject
        Try
            Dim archiveResult As New JObject()
            archiveResult("timestamp") = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")

            Dim archiveDays As Integer = If(cfg("log_manager")?("archive_after_days")?.ToObject(Of Integer)(), 7)
            Dim cutoffDate As DateTime = DateTime.Now.AddDays(-archiveDays)

            Dim logFiles As List(Of String) = DiscoverLogFiles()
            Dim archivedFiles As New List(Of String)()
            Dim totalSizeArchived As Long = 0

            For Each logFile As String In logFiles
                Try
                    Dim fileInfo As New FileInfo(logFile)

                    If forceArchive OrElse fileInfo.LastWriteTime < cutoffDate Then
                        Dim archivePath As String = ArchiveLogFile(logFile, cfg)
                        If Not String.IsNullOrEmpty(archivePath) Then
                            archivedFiles.Add(archivePath)
                            totalSizeArchived += fileInfo.Length
                        End If
                    End If

                Catch ex As Exception
                    Console.WriteLine($"Failed to archive {logFile}: {ex.Message}")
                End Try
            Next

            archiveResult("files_archived") = archivedFiles.Count
            archiveResult("size_archived_mb") = Math.Round(totalSizeArchived / (1024.0 * 1024.0), 2)
            archiveResult("archive_threshold_days") = archiveDays
            archiveResult("archived_files") = New JArray(archivedFiles)
            archiveResult("success") = True

            Console.WriteLine($"✅ Log archiving completed: {archivedFiles.Count} files archived")

            Return archiveResult

        Catch ex As Exception
            Console.WriteLine($"❌ Log archiving failed: {ex.Message}")
            Dim errorResult As New JObject()
            errorResult("success") = False
            errorResult("error") = ex.Message
            Return errorResult
        End Try
    End Function

#End Region

#Region "Log Analysis Functions"

    ''' <summary>
    ''' Analyze error patterns in logs
    ''' </summary>
    Private Shared Function AnalyzeErrors(logFiles As List(Of String), days As Integer) As JObject
        Try
            Dim errorAnalysis As New JObject()
            Dim errorPatterns As New Dictionary(Of String, Integer)()
            Dim criticalErrors As New JArray()
            Dim totalErrors As Integer = 0

            Dim cutoffDate As DateTime = DateTime.Now.AddDays(-days)

            For Each logFile As String In logFiles
                Try
                    Dim lines As String() = File.ReadAllLines(logFile)

                    For Each line As String In lines
                        If ContainsTimestamp(line, cutoffDate) Then
                            If IsErrorLine(line) Then
                                totalErrors += 1

                                ' Extract error pattern
                                Dim pattern As String = ExtractErrorPattern(line)
                                If Not String.IsNullOrEmpty(pattern) Then
                                    If errorPatterns.ContainsKey(pattern) Then
                                        errorPatterns(pattern) += 1
                                    Else
                                        errorPatterns(pattern) = 1
                                    End If
                                End If

                                ' Check for critical errors
                                If IsCriticalError(line) Then
                                    Dim criticalError As New JObject()
                                    criticalError("timestamp") = ExtractTimestamp(line)
                                    criticalError("message") = line
                                    criticalError("source_file") = Path.GetFileName(logFile)
                                    criticalErrors.Add(criticalError)
                                End If
                            End If
                        End If
                    Next

                Catch ex As Exception
                    Console.WriteLine($"Error analyzing {logFile}: {ex.Message}")
                End Try
            Next

            errorAnalysis("total_errors") = totalErrors
            errorAnalysis("critical_errors_count") = criticalErrors.Count
            errorAnalysis("critical_errors") = criticalErrors

            ' Convert error patterns to JArray
            Dim patternsArray As New JArray()
            For Each kvp In errorPatterns.OrderByDescending(Function(x) x.Value).Take(10)
                Dim patternObj As New JObject()
                patternObj("pattern") = kvp.Key
                patternObj("count") = kvp.Value
                patternsArray.Add(patternObj)
            Next
            errorAnalysis("top_error_patterns") = patternsArray

            Return errorAnalysis

        Catch ex As Exception
            Console.WriteLine($"Error analysis failed: {ex.Message}")
            Return New JObject()
        End Try
    End Function

    ''' <summary>
    ''' Analyze performance metrics from logs
    ''' </summary>
    Private Shared Function AnalyzePerformance(logFiles As List(Of String), days As Integer) As JObject
        Try
            Dim performanceAnalysis As New JObject()
            Dim responseTimes As New List(Of Double)()
            Dim apiCalls As New Dictionary(Of String, Integer)()
            Dim slowOperations As New JArray()

            Dim cutoffDate As DateTime = DateTime.Now.AddDays(-days)

            For Each logFile As String In logFiles
                Try
                    Dim lines As String() = File.ReadAllLines(logFile)

                    For Each line As String In lines
                        If ContainsTimestamp(line, cutoffDate) Then
                            ' Extract response times
                            Dim responseTime As Double = ExtractResponseTime(line)
                            If responseTime > 0 Then
                                responseTimes.Add(responseTime)

                                ' Track slow operations (>5 seconds)
                                If responseTime > 5000 Then
                                    Dim slowOp As New JObject()
                                    slowOp("timestamp") = ExtractTimestamp(line)
                                    slowOp("response_time_ms") = responseTime
                                    slowOp("operation") = ExtractOperation(line)
                                    slowOperations.Add(slowOp)
                                End If
                            End If

                            ' Count API calls
                            Dim apiEndpoint As String = ExtractApiEndpoint(line)
                            If Not String.IsNullOrEmpty(apiEndpoint) Then
                                If apiCalls.ContainsKey(apiEndpoint) Then
                                    apiCalls(apiEndpoint) += 1
                                Else
                                    apiCalls(apiEndpoint) = 1
                                End If
                            End If
                        End If
                    Next

                Catch ex As Exception
                    Console.WriteLine($"Error analyzing performance in {logFile}: {ex.Message}")
                End Try
            Next

            If responseTimes.Count > 0 Then
                performanceAnalysis("avg_response_time_ms") = Math.Round(responseTimes.Average(), 2)
                performanceAnalysis("max_response_time_ms") = responseTimes.Max()
                performanceAnalysis("min_response_time_ms") = responseTimes.Min()
                performanceAnalysis("total_operations") = responseTimes.Count
            End If

            performanceAnalysis("slow_operations_count") = slowOperations.Count
            performanceAnalysis("slow_operations") = slowOperations

            ' Top API endpoints by usage
            Dim apiArray As New JArray()
            For Each kvp In apiCalls.OrderByDescending(Function(x) x.Value).Take(5)
                Dim apiObj As New JObject()
                apiObj("endpoint") = kvp.Key
                apiObj("call_count") = kvp.Value
                apiArray.Add(apiObj)
            Next
            performanceAnalysis("top_api_endpoints") = apiArray

            Return performanceAnalysis

        Catch ex As Exception
            Console.WriteLine($"Performance analysis failed: {ex.Message}")
            Return New JObject()
        End Try
    End Function

    ''' <summary>
    ''' Analyze security-related log entries
    ''' </summary>
    Private Shared Function AnalyzeSecurity(logFiles As List(Of String), days As Integer) As JObject
        Try
            Dim securityAnalysis As New JObject()
            Dim authFailures As Integer = 0
            Dim suspiciousIPs As New Dictionary(Of String, Integer)()
            Dim securityEvents As New JArray()

            Dim cutoffDate As DateTime = DateTime.Now.AddDays(-days)

            For Each logFile As String In logFiles
                Try
                    Dim lines As String() = File.ReadAllLines(logFile)

                    For Each line As String In lines
                        If ContainsTimestamp(line, cutoffDate) Then
                            ' Check for authentication failures
                            If IsAuthFailure(line) Then
                                authFailures += 1

                                Dim ip As String = ExtractIPAddress(line)
                                If Not String.IsNullOrEmpty(ip) Then
                                    If suspiciousIPs.ContainsKey(ip) Then
                                        suspiciousIPs(ip) += 1
                                    Else
                                        suspiciousIPs(ip) = 1
                                    End If
                                End If
                            End If

                            ' Check for other security events
                            If IsSecurityEvent(line) Then
                                Dim secEvent As New JObject()
                                secEvent("timestamp") = ExtractTimestamp(line)
                                secEvent("event_type") = ExtractSecurityEventType(line)
                                secEvent("message") = line
                                secEvent("source_file") = Path.GetFileName(logFile)
                                securityEvents.Add(secEvent)
                            End If
                        End If
                    Next

                Catch ex As Exception
                    Console.WriteLine($"Error analyzing security in {logFile}: {ex.Message}")
                End Try
            Next

            securityAnalysis("auth_failures") = authFailures
            securityAnalysis("security_events_count") = securityEvents.Count
            securityAnalysis("security_events") = securityEvents

            ' Top suspicious IPs
            Dim suspiciousArray As New JArray()
            For Each kvp In suspiciousIPs.OrderByDescending(Function(x) x.Value).Take(5)
                Dim ipObj As New JObject()
                ipObj("ip_address") = kvp.Key
                ipObj("failure_count") = kvp.Value
                suspiciousArray.Add(ipObj)
            Next
            securityAnalysis("suspicious_ips") = suspiciousArray

            Return securityAnalysis

        Catch ex As Exception
            Console.WriteLine($"Security analysis failed: {ex.Message}")
            Return New JObject()
        End Try
    End Function

    ''' <summary>
    ''' Extract monetizable insights from logs
    ''' </summary>
    Private Shared Function ExtractMonetizationInsights(logFiles As List(Of String), days As Integer) As JObject
        Try
            Dim insights As New JObject()
            Dim affiliateClicks As Integer = 0
            Dim telegramJoins As Integer = 0
            Dim reportDownloads As Integer = 0
            Dim apiUsage As New Dictionary(Of String, Integer)()

            Dim cutoffDate As DateTime = DateTime.Now.AddDays(-days)

            For Each logFile As String In logFiles
                Try
                    Dim lines As String() = File.ReadAllLines(logFile)

                    For Each line As String In lines
                        If ContainsTimestamp(line, cutoffDate) Then
                            ' Count affiliate link clicks
                            If line.Contains("affiliate") OrElse line.Contains("bitly") Then
                                affiliateClicks += 1
                            End If

                            ' Count Telegram joins
                            If line.Contains("telegram") AndAlso line.Contains("join") Then
                                telegramJoins += 1
                            End If

                            ' Count report downloads
                            If line.Contains("report") AndAlso (line.Contains("download") OrElse line.Contains("pdf")) Then
                                reportDownloads += 1
                            End If

                            ' Track API usage for billing
                            Dim apiCall As String = ExtractApiProvider(line)
                            If Not String.IsNullOrEmpty(apiCall) Then
                                If apiUsage.ContainsKey(apiCall) Then
                                    apiUsage(apiCall) += 1
                                Else
                                    apiUsage(apiCall) = 1
                                End If
                            End If
                        End If
                    Next

                Catch ex As Exception
                    Console.WriteLine($"Error extracting monetization insights from {logFile}: {ex.Message}")
                End Try
            Next

            insights("affiliate_clicks") = affiliateClicks
            insights("telegram_joins") = telegramJoins
            insights("report_downloads") = reportDownloads
            insights("conversion_rate") = If(affiliateClicks > 0, Math.Round((telegramJoins / affiliateClicks) * 100, 2), 0)

            ' API usage costs (estimated)
            Dim apiCostsArray As New JArray()
            For Each kvp In apiUsage
                Dim apiCost As New JObject()
                apiCost("provider") = kvp.Key
                apiCost("calls") = kvp.Value
                apiCost("estimated_cost_usd") = CalculateApiCost(kvp.Key, kvp.Value)
                apiCostsArray.Add(apiCost)
            Next
            insights("api_usage_costs") = apiCostsArray

            Return insights

        Catch ex As Exception
            Console.WriteLine($"Monetization insights extraction failed: {ex.Message}")
            Return New JObject()
        End Try
    End Function

    ''' <summary>
    ''' Assess overall system health from logs
    ''' </summary>
    Private Shared Function AssessSystemHealth(logFiles As List(Of String), days As Integer) As JObject
        Try
            Dim health As New JObject()
            Dim totalLogs As Integer = 0
            Dim errorLogs As Integer = 0
            Dim warningLogs As Integer = 0
            Dim uptimeSeconds As Double = 0

            Dim cutoffDate As DateTime = DateTime.Now.AddDays(-days)

            For Each logFile As String In logFiles
                Try
                    Dim lines As String() = File.ReadAllLines(logFile)

                    For Each line As String In lines
                        If ContainsTimestamp(line, cutoffDate) Then
                            totalLogs += 1

                            If IsErrorLine(line) Then
                                errorLogs += 1
                            ElseIf IsWarningLine(line) Then
                                warningLogs += 1
                            End If
                        End If
                    Next

                Catch ex As Exception
                    Console.WriteLine($"Error assessing health from {logFile}: {ex.Message}")
                End Try
            Next

            ' Calculate health metrics
            Dim errorRate As Double = If(totalLogs > 0, (errorLogs / totalLogs) * 100, 0)
            Dim warningRate As Double = If(totalLogs > 0, (warningLogs / totalLogs) * 100, 0)

            health("total_log_entries") = totalLogs
            health("error_count") = errorLogs
            health("warning_count") = warningLogs
            health("error_rate_percent") = Math.Round(errorRate, 2)
            health("warning_rate_percent") = Math.Round(warningRate, 2)

            ' Determine health status
            Dim healthStatus As String
            If errorRate > 5 Then
                healthStatus = "Critical"
            ElseIf errorRate > 2 OrElse warningRate > 10 Then
                healthStatus = "Warning"
            ElseIf errorRate > 1 OrElse warningRate > 5 Then
                healthStatus = "Caution"
            Else
                healthStatus = "Healthy"
            End If

            health("health_status") = healthStatus
            health("assessment_period_days") = days

            Return health

        Catch ex As Exception
            Console.WriteLine($"System health assessment failed: {ex.Message}")
            Return New JObject()
        End Try
    End Function

#End Region

#Region "Utility Functions"

    ''' <summary>
    ''' Discover all log files in the EQ12 system
    ''' </summary>
    Private Shared Function DiscoverLogFiles() As List(Of String)
        Dim logFiles As New List(Of String)()

        Try
            ' Main logs directory
            If Directory.Exists("logs") Then
                logFiles.AddRange(Directory.GetFiles("logs", "*.log", SearchOption.AllDirectories))
                logFiles.AddRange(Directory.GetFiles("logs", "*.txt", SearchOption.AllDirectories))
            End If

            ' Check for logs in other common locations
            Dim otherPaths As String() = {
                "C:\EQ12\logs",
                "Data\logs",
                "Exports\logs",
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "EQ12", "logs")
            }

            For Each path As String In otherPaths
                If Directory.Exists(path) Then
                    logFiles.AddRange(Directory.GetFiles(path, "*.log", SearchOption.AllDirectories))
                    logFiles.AddRange(Directory.GetFiles(path, "*.txt", SearchOption.AllDirectories))
                End If
            Next

        Catch ex As Exception
            Console.WriteLine($"Error discovering log files: {ex.Message}")
        End Try

        Return logFiles.Distinct().ToList()
    End Function

    ''' <summary>
    ''' Archive a single log file
    ''' </summary>
    Private Shared Function ArchiveLogFile(logFilePath As String, cfg As JObject) As String
        Try
            Dim archiveDir As String = If(cfg("log_manager")?("archive_directory")?.ToString(), "logs\archive")
            If Not Directory.Exists(archiveDir) Then
                Directory.CreateDirectory(archiveDir)
            End If

            Dim fileName As String = Path.GetFileNameWithoutExtension(logFilePath)
            Dim extension As String = Path.GetExtension(logFilePath)
            Dim timestamp As String = DateTime.Now.ToString("yyyyMMdd_HHmmss")

            Dim archivePath As String = Path.Combine(archiveDir, $"{fileName}_{timestamp}{extension}")

            File.Move(logFilePath, archivePath)

            Return archivePath

        Catch ex As Exception
            Console.WriteLine($"Failed to archive {logFilePath}: {ex.Message}")
            Return ""
        End Try
    End Function

    ''' <summary>
    ''' Generate recommendations based on analysis
    ''' </summary>
    Private Shared Function GenerateRecommendations(analysis As JObject) As JArray
        Dim recommendations As New JArray()

        Try
            ' Error-based recommendations
            Dim errorCount As Integer = analysis("error_analysis")?("total_errors")?.ToObject(Of Integer)() Or 0
            If errorCount > 100 Then
                recommendations.Add("High error count detected. Review error patterns and implement fixes.")
            End If

            ' Performance-based recommendations
            Dim avgResponseTime As Double = analysis("performance_analysis")?("avg_response_time_ms")?.ToObject(Of Double)() Or 0
            If avgResponseTime > 2000 Then
                recommendations.Add("Average response time is high. Consider optimizing slow operations.")
            End If

            ' Security-based recommendations
            Dim authFailures As Integer = analysis("security_analysis")?("auth_failures")?.ToObject(Of Integer)() Or 0
            If authFailures > 10 Then
                recommendations.Add("Multiple authentication failures detected. Review security measures.")
            End If

            ' Monetization recommendations
            Dim conversionRate As Double = analysis("monetization_insights")?("conversion_rate")?.ToObject(Of Double)() Or 0
            If conversionRate < 2 Then
                recommendations.Add("Low conversion rate. Consider improving affiliate link placement and CTAs.")
            End If

            ' Health-based recommendations
            Dim healthStatus As String = analysis("system_health")?("health_status")?.ToString()
            If healthStatus = "Critical" Or healthStatus = "Warning" Then
                recommendations.Add($"System health status: {healthStatus}. Immediate attention required.")
            End If

        Catch ex As Exception
            Console.WriteLine($"Error generating recommendations: {ex.Message}")
        End Try

        Return recommendations
    End Function

    ''' <summary>
    ''' Calculate estimated API cost
    ''' </summary>
    Private Shared Function CalculateApiCost(provider As String, callCount As Integer) As Double
        ' Rough cost estimates per 1000 calls
        Dim costPer1000 As Dictionary(Of String, Double) = New Dictionary(Of String, Double) From {
            {"openai", 0.30},
            {"deepseek", 0.05},
            {"gemini", 0.25},
            {"claude", 0.80},
            {"odds_api", 0.10}
        }

        Dim rate As Double = If(costPer1000.ContainsKey(provider.ToLower()), costPer1000(provider.ToLower()), 0.20)
        Return Math.Round((callCount / 1000.0) * rate, 4)
    End Function

#End Region

#Region "Log Pattern Recognition"

    Private Shared Function ContainsTimestamp(line As String, cutoffDate As DateTime) As Boolean
        ' Simple timestamp check - could be enhanced with regex
        Try
            Dim timestamp As String = ExtractTimestamp(line)
            If Not String.IsNullOrEmpty(timestamp) Then
                Dim logDate As DateTime
                If DateTime.TryParse(timestamp, logDate) Then
                    Return logDate >= cutoffDate
                End If
            End If
            Return True ' Include if can't parse timestamp
        Catch
            Return True
        End Try
    End Function

    Private Shared Function IsErrorLine(line As String) As Boolean
        Return line.Contains("ERROR") OrElse line.Contains("Exception") OrElse line.Contains("FAILED") OrElse line.Contains("❌")
    End Function

    Private Shared Function IsWarningLine(line As String) As Boolean
        Return line.Contains("WARNING") OrElse line.Contains("WARN") OrElse line.Contains("⚠️")
    End Function

    Private Shared Function IsCriticalError(line As String) As Boolean
        Return line.Contains("CRITICAL") OrElse line.Contains("FATAL") OrElse line.Contains("OutOfMemory") OrElse line.Contains("StackOverflow")
    End Function

    Private Shared Function IsAuthFailure(line As String) As Boolean
        Return line.Contains("authentication failed") OrElse line.Contains("login failed") OrElse line.Contains("unauthorized")
    End Function

    Private Shared Function IsSecurityEvent(line As String) As Boolean
        Return line.Contains("security") OrElse line.Contains("breach") OrElse line.Contains("attack") OrElse line.Contains("malware")
    End Function

    Private Shared Function ExtractTimestamp(line As String) As String
        ' Extract timestamp from log line - could be enhanced with better regex
        Dim timestampRegex As New Regex("\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}")
        Dim match = timestampRegex.Match(line)
        Return If(match.Success, match.Value, "")
    End Function

    Private Shared Function ExtractErrorPattern(line As String) As String
        ' Extract meaningful error pattern
        If line.Contains("Exception") Then
            Dim exceptionRegex As New Regex("(\w+Exception)")
            Dim match = exceptionRegex.Match(line)
            Return If(match.Success, match.Value, "General Exception")
        ElseIf line.Contains("ERROR") Then
            Return "General Error"
        ElseIf line.Contains("FAILED") Then
            Return "Operation Failed"
        Else
            Return "Unknown Error"
        End If
    End Function

    Private Shared Function ExtractResponseTime(line As String) As Double
        Dim responseTimeRegex As New Regex("(\d+(?:\.\d+)?)\s*ms")
        Dim match = responseTimeRegex.Match(line)
        If match.Success Then
            Dim responseTime As Double
            If Double.TryParse(match.Groups(1).Value, responseTime) Then
                Return responseTime
            End If
        End If
        Return 0
    End Function

    Private Shared Function ExtractOperation(line As String) As String
        ' Extract operation name from log line
        If line.Contains("API") Then
            Return "API Call"
        ElseIf line.Contains("Database") Then
            Return "Database Operation"
        ElseIf line.Contains("Report") Then
            Return "Report Generation"
        Else
            Return "Unknown Operation"
        End If
    End Function

    Private Shared Function ExtractApiEndpoint(line As String) As String
        Dim apiRegex As New Regex("(https?://[^\s]+)")
        Dim match = apiRegex.Match(line)
        Return If(match.Success, match.Value, "")
    End Function

    Private Shared Function ExtractApiProvider(line As String) As String
        If line.Contains("openai") Then Return "openai"
        If line.Contains("deepseek") Then Return "deepseek"
        If line.Contains("gemini") Then Return "gemini"
        If line.Contains("claude") Then Return "claude"
        If line.Contains("odds-api") Then Return "odds_api"
        Return ""
    End Function

    Private Shared Function ExtractIPAddress(line As String) As String
        Dim ipRegex As New Regex("\b(?:\d{1,3}\.){3}\d{1,3}\b")
        Dim match = ipRegex.Match(line)
        Return If(match.Success, match.Value, "")
    End Function

    Private Shared Function ExtractSecurityEventType(line As String) As String
        If line.Contains("authentication") Then Return "Authentication"
        If line.Contains("authorization") Then Return "Authorization"
        If line.Contains("breach") Then Return "Security Breach"
        If line.Contains("attack") Then Return "Attack Attempt"
        Return "Security Event"
    End Function

#End Region

#Region "Database Logging"

    Private Shared Sub LogAnalysisResult(analysis As JObject)
        Try
            Dim dbPath As String = "Data\eq12_terminal.db"
            Using conn As New SQLiteConnection($"Data Source={dbPath}")
                conn.Open()

                Dim sql As String = "INSERT INTO log_analysis (analysis_type, total_errors, performance_score, security_score, health_status, recommendations_count) VALUES (@analysisType, @totalErrors, @performanceScore, @securityScore, @healthStatus, @recommendationsCount)"
                Using cmd As New SQLiteCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@analysisType", "comprehensive")
                    cmd.Parameters.AddWithValue("@totalErrors", analysis("error_analysis")?("total_errors")?.ToObject(Of Integer)() Or 0)
                    cmd.Parameters.AddWithValue("@performanceScore", CalculatePerformanceScore(analysis))
                    cmd.Parameters.AddWithValue("@securityScore", CalculateSecurityScore(analysis))
                    cmd.Parameters.AddWithValue("@healthStatus", analysis("system_health")?("health_status")?.ToString() Or "Unknown")
                    cmd.Parameters.AddWithValue("@recommendationsCount", analysis("recommendations")?.Count Or 0)

                    cmd.ExecuteNonQuery()
                End Using
            End Using

        Catch ex As Exception
            Console.WriteLine($"Failed to log analysis result: {ex.Message}")
        End Try
    End Sub

    Private Shared Sub LogCleanupResult(cleanupResult As JObject)
        Try
            Dim dbPath As String = "Data\eq12_terminal.db"
            Using conn As New SQLiteConnection($"Data Source={dbPath}")
                conn.Open()

                Dim sql As String = "INSERT INTO log_cleanup (files_deleted, files_archived, size_freed_mb, retention_days) VALUES (@filesDeleted, @filesArchived, @sizeFreed, @retentionDays)"
                Using cmd As New SQLiteCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@filesDeleted", cleanupResult("files_deleted").ToObject(Of Integer)())
                    cmd.Parameters.AddWithValue("@filesArchived", cleanupResult("files_archived").ToObject(Of Integer)())
                    cmd.Parameters.AddWithValue("@sizeFreed", cleanupResult("size_freed_mb").ToObject(Of Double)())
                    cmd.Parameters.AddWithValue("@retentionDays", cleanupResult("retention_days").ToObject(Of Integer)())

                    cmd.ExecuteNonQuery()
                End Using
            End Using

        Catch ex As Exception
            Console.WriteLine($"Failed to log cleanup result: {ex.Message}")
        End Try
    End Sub

    Private Shared Function CalculatePerformanceScore(analysis As JObject) As Integer
        Try
            Dim avgResponseTime As Double = analysis("performance_analysis")?("avg_response_time_ms")?.ToObject(Of Double)() Or 1000
            ' Score from 1-100 based on response time
            Dim score As Integer = Math.Max(1, 100 - CInt(avgResponseTime / 50))
            Return Math.Min(100, score)
        Catch
            Return 50 ' Default score
        End Try
    End Function

    Private Shared Function CalculateSecurityScore(analysis As JObject) As Integer
        Try
            Dim authFailures As Integer = analysis("security_analysis")?("auth_failures")?.ToObject(Of Integer)() Or 0
            Dim securityEvents As Integer = analysis("security_analysis")?("security_events_count")?.ToObject(Of Integer)() Or 0

            ' Score from 1-100 based on security incidents
            Dim score As Integer = 100 - (authFailures * 5) - (securityEvents * 10)
            Return Math.Max(1, Math.Min(100, score))
        Catch
            Return 80 ' Default score
        End Try
    End Function

#End Region

End Class
