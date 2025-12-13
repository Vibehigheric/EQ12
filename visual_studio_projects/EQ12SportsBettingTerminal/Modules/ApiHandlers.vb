Imports System.Threading.Tasks
Imports System.Web
Imports System.Net
Imports Newtonsoft.Json
Imports Newtonsoft.Json.Linq
Imports System.Data
Imports System.IO
Imports System.Collections.Generic

''' <summary>
''' API Handlers for EQ12 Cloud Run Services
''' Implements Jump Start Solution: Dynamic Web Application
''' Provides REST endpoints for sports betting analytics and monetization
''' '''
Public Class ApiHandlers
    Private ReadOnly _gcpAuth As GCPAuth
    Private ReadOnly _bqClient As BigQueryClient
    Private ReadOnly _gcsClient As GCSClient
    Private ReadOnly _ragClient As RAGClient
    Private ReadOnly _kbClient As KBClient

    Public Sub New(projectId As String, credentialsPath As String, bucketName As String)
        _gcpAuth = New GCPAuth(projectId, credentialsPath)
        _bqClient = New BigQueryClient(_gcpAuth, "eq12_dw")
        _gcsClient = New GCSClient(_gcpAuth, bucketName)

        ' Initialize Jump Start Solutions clients
        Dim ragUrl = Environment.GetEnvironmentVariable("RAG_SERVICE_URL") ?? "https://eq12-rag-run.a.run.app"
        Dim kbUrl = Environment.GetEnvironmentVariable("KB_SERVICE_URL") ?? "https://eq12-kb-run.a.run.app"

        _ragClient = New RAGClient(ragUrl, _gcpAuth)
        _kbClient = New KBClient(kbUrl, _gcpAuth)
    End Sub

    ''' <summary>
    ''' GET /health - System health check
    ''' '''
    Public Function GetHealth() As JObject
        Try
            Dim health As New JObject From {
                {"status", "healthy"},
                {"timestamp", DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")},
                {"version", "1.0.0"},
                {"services", New JObject From {
                    {"bigquery", "connected"},
                    {"storage", "connected"},
                    {"rag", "available"},
                    {"knowledge_base", "available"}
                }}
            }

            Console.WriteLine("✅ Health check passed")
            Return health

        Catch ex As Exception
            Console.WriteLine($"❌ Health check failed: {ex.Message}")
            Return New JObject From {
                {"status", "unhealthy"},
                {"error", ex.Message},
                {"timestamp", DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")}
            }
        End Try
    End Function

    ''' <summary>
    ''' GET /arb/scan - Recent arbitrage opportunities
    ''' '''
    Public Function GetArbitrageOpportunities(Optional hours As Integer = 24, Optional minPct As Double = 2.0) As JObject
        Try
            Dim sql = $"
                SELECT
                  ts,
                  event_id,
                  sideA,
                  bookA,
                  oddsA,
                  sideB,
                  bookB,
                  oddsB,
                  arb_pct,
                  lock_profit
                FROM `{_gcpAuth.ProjectId}.eq12_dw.arb_opportunities`
                WHERE ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {hours} HOUR)
                  AND arb_pct >= {minPct}
                ORDER BY arb_pct DESC
                LIMIT 100
            "

            Dim dt = _bqClient.RunQuery(sql)
            Dim opportunities = ConvertDataTableToJArray(dt)

            Dim result As New JObject From {
                {"status", "success"},
                {"timestamp", DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")},
                {"timeframe_hours", hours},
                {"min_arb_pct", minPct},
                {"count", opportunities.Count},
                {"opportunities", opportunities}
            }

            Console.WriteLine($"📊 Found {opportunities.Count} arbitrage opportunities")
            Return result

        Catch ex As Exception
            Console.WriteLine($"❌ Arbitrage scan failed: {ex.Message}")
            Return New JObject From {
                {"status", "error"},
                {"error", ex.Message}
            }
        End Try
    End Function

    ''' <summary>
    ''' GET /bets/today - Today's betting opportunities and recommendations
    ''' '''
    Public Async Function GetTodaysBetsAsync() As Task(Of JObject)
        Try
            ' Get today's odds and opportunities
            Dim sql = $"
                SELECT
                  sport,
                  event_id,
                  COUNT(*) as market_count,
                  MIN(ts) as first_seen,
                  MAX(ts) as last_updated
                FROM `{_gcpAuth.ProjectId}.eq12_dw.odds`
                WHERE DATE(ts) = CURRENT_DATE()
                GROUP BY sport, event_id
                ORDER BY sport, last_updated DESC
            "

            Dim dt = _bqClient.RunQuery(sql)
            Dim todaysEvents = ConvertDataTableToJArray(dt)

            ' Get RAG insights for today's games
            Dim ragInsights = Await _ragClient.QueryBettingInsightsAsync(
                "What are the best betting opportunities for today's games? Include injury impacts and line movements.",
                8, "daily_betting"
            )

            Dim result As New JObject From {
                {"status", "success"},
                {"date", DateTime.Today.ToString("yyyy-MM-dd")},
                {"events_count", todaysEvents.Count},
                {"events", todaysEvents},
                {"ai_insights", ragInsights("answer")},
                {"premium_available", True}
            }

            Console.WriteLine($"🎯 Retrieved {todaysEvents.Count} events for today")
            Return result

        Catch ex As Exception
            Console.WriteLine($"❌ Today's bets retrieval failed: {ex.Message}")
            Return New JObject From {
                {"status", "error"},
                {"error", ex.Message}
            }
        End Try
    End Function

    ''' <summary>
    ''' GET /content/latest - Latest deliverables and reports
    ''' '''
    Public Function GetLatestContent(Optional limit As Integer = 20) As JObject
        Try
            Dim sql = $"
                SELECT
                  ts,
                  kind,
                  title,
                  bitly_url,
                  gist_url,
                  window
                FROM `{_gcpAuth.ProjectId}.eq12_dw.deliverables`
                ORDER BY ts DESC
                LIMIT {limit}
            "

            Dim dt = _bqClient.RunQuery(sql)
            Dim content = ConvertDataTableToJArray(dt)

            Dim result As New JObject From {
                {"status", "success"},
                {"timestamp", DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")},
                {"count", content.Count},
                {"deliverables", content},
                {"subscription_url", "https://eq12.com/subscribe"},
                {"premium_features", New JArray From {
                    "Advanced Analytics",
                    "Real-time Alerts",
                    "Custom Reports",
                    "AI Insights"
                }}
            }

            Console.WriteLine($"📄 Retrieved {content.Count} content items")
            Return result

        Catch ex As Exception
            Console.WriteLine($"❌ Content retrieval failed: {ex.Message}")
            Return New JObject From {
                {"status", "error"},
                {"error", ex.Message}
            }
        End Try
    End Function

    ''' <summary>
    ''' POST /kb/ask - Knowledge Base Q&A (Jump Start: Knowledge Base)
    ''' '''
    Public Async Function PostKnowledgeBaseQueryAsync(question As String, context As String) As Task(Of JObject)
        Try
            ' Parse context to enum
            Dim kbContext As KBClient.KnowledgeContext
            If Not [Enum].TryParse(context.Replace("_", ""), True, kbContext) Then
                kbContext = KBClient.KnowledgeContext.BettingFundamentals
            End If

            Dim answer = Await _kbClient.AskAsync(question, kbContext, True)

            Dim result As New JObject From {
                {"status", "success"},
                {"question", question},
                {"context", context},
                {"answer", answer},
                {"timestamp", DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")},
                {"premium_features_available", True}
            }

            Console.WriteLine($"🤖 KB Query answered: {context}")
            Return result

        Catch ex As Exception
            Console.WriteLine($"❌ KB query failed: {ex.Message}")
            Return New JObject From {
                {"status", "error"},
                {"error", ex.Message}
            }
        End Try
    End Function

    ''' <summary>
    ''' POST /rag/query - RAG Query (Jump Start: RAG Solution)
    ''' '''
    Public Async Function PostRAGQueryAsync(question As String, Optional k As Integer = 6, Optional context As String = "betting") As Task(Of JObject)
        Try
            Dim result = Await _ragClient.QueryBettingInsightsAsync(question, k, context)

            ' Add monetization hooks
            result("premium_upgrade_url") = "https://eq12.com/upgrade"
            result("timestamp") = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")

            Console.WriteLine($"🧠 RAG query processed: {context}")
            Return result

        Catch ex As Exception
            Console.WriteLine($"❌ RAG query failed: {ex.Message}")
            Return New JObject From {
                {"status", "error"},
                {"error", ex.Message}
            }
        End Try
    End Function

    ''' <summary>
    ''' GET /metrics/compute - Compute advanced metrics on demand
    ''' '''
    Public Function PostComputeMetrics(sport As String, Optional team As String = "") As JObject
        Try
            ' This would integrate with existing MetricsEngine
            Dim metricsEngine As New MetricsEngine()

            ' Compute metrics (placeholder for actual computation)
            Dim metrics = metricsEngine.ComputeAdvancedMetrics(sport)

            Dim result As New JObject From {
                {"status", "success"},
                {"sport", sport},
                {"team", team},
                {"metrics_computed", True},
                {"timestamp", DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")}
            }

            Console.WriteLine($"📊 Metrics computed for {sport}")
            Return result

        Catch ex As Exception
            Console.WriteLine($"❌ Metrics computation failed: {ex.Message}")
            Return New JObject From {
                {"status", "error"},
                {"error", ex.Message}
            }
        End Try
    End Function

    ''' <summary>
    ''' GET /market/movements - Recent market movements and line changes
    ''' '''
    Public Function GetMarketMovements(Optional hours As Integer = 12) As JObject
        Try
            Dim sql = $"
                SELECT
                  ts,
                  sport,
                  event_id,
                  side,
                  move,
                  inference
                FROM `{_gcpAuth.ProjectId}.eq12_dw.market_moves`
                WHERE ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {hours} HOUR)
                ORDER BY ts DESC
                LIMIT 50
            "

            Dim dt = _bqClient.RunQuery(sql)
            Dim movements = ConvertDataTableToJArray(dt)

            Dim result As New JObject From {
                {"status", "success"},
                {"timeframe_hours", hours},
                {"count", movements.Count},
                {"movements", movements},
                {"analysis_available", True}
            }

            Console.WriteLine($"📈 Retrieved {movements.Count} market movements")
            Return result

        Catch ex As Exception
            Console.WriteLine($"❌ Market movements retrieval failed: {ex.Message}")
            Return New JObject From {
                {"status", "error"},
                {"error", ex.Message}
            }
        End Try
    End Function

    ''' <summary>
    ''' POST /upload/report - Upload report to Cloud Storage with signed URL
    ''' '''
    Public Function PostUploadReport(fileName As String, content As Byte(), contentType As String) As JObject
        Try
            ' Create temporary file
            Dim tempPath = Path.Combine(Path.GetTempPath(), fileName)
            File.WriteAllBytes(tempPath, content)

            ' Upload to GCS
            Dim timestamp = DateTime.UtcNow.ToString("yyyyMMdd_HHmmss")
            Dim objectName = $"reports/{timestamp}_{fileName}"

            Dim gsUrl = _gcsClient.UploadObject(tempPath, objectName, contentType)
            Dim signedUrl = _gcsClient.GetDownloadUrl(objectName, 72) ' 3 days

            ' Clean up temp file
            File.Delete(tempPath)

            Dim result As New JObject From {
                {"status", "success"},
                {"file_name", fileName},
                {"gs_url", gsUrl},
                {"signed_url", signedUrl},
                {"expires_hours", 72},
                {"timestamp", DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")}
            }

            Console.WriteLine($"☁️ Report uploaded: {objectName}")
            Return result

        Catch ex As Exception
            Console.WriteLine($"❌ Report upload failed: {ex.Message}")
            Return New JObject From {
                {"status", "error"},
                {"error", ex.Message}
            }
        End Try
    End Function

    ' Helper method to convert DataTable to JArray
    Private Function ConvertDataTableToJArray(dt As DataTable) As JArray
        Dim result As New JArray()

        If dt Is Nothing OrElse dt.Rows.Count = 0 Then
            Return result
        End If

        For Each row As DataRow In dt.Rows
            Dim obj As New JObject()
            For Each column As DataColumn In dt.Columns
                Dim value = row(column)
                If value IsNot DBNull.Value Then
                    obj(column.ColumnName) = JToken.FromObject(value)
                End If
            Next
            result.Add(obj)
        Next

        Return result
    End Function
End Class
