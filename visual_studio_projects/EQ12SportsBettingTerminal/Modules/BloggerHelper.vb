Imports System.Net.Http
Imports System.Text
Imports System.Data.SQLite
Imports Newtonsoft.Json.Linq
Imports System.Text.RegularExpressions
Imports System.IO
Imports System.Threading.Tasks

''' <summary>
''' BloggerHelper: Comprehensive Google Blogger API integration for EQ12 stack
''' Enables auto-publishing of betting reports, arbitrage insights, and monetizable content
''' Features: SEO-optimized posts, affiliate link integration, monetization hooks
''' </summary>
Public Class BloggerHelper

#Region "Core Publishing Functions"

    ''' <summary>
    ''' Publish content to Google Blogger with full monetization integration
    ''' </summary>
    ''' <param name="cfg">Configuration JObject with blogger settings</param>
    ''' <param name="title">Blog post title (SEO optimized)</param>
    ''' <param name="contentHtml">HTML content with tables, affiliate CTAs</param>
    ''' <param name="labels">Optional blog labels/tags for SEO</param>
    ''' <returns>Blogger post ID or error message</returns>
    Public Shared Function PublishPost(cfg As JObject, title As String, contentHtml As String, Optional labels As String() = Nothing) As String
        Try
            ' Validate configuration
            If Not ValidateBloggerConfig(cfg) Then
                Return "ERROR: Invalid Blogger configuration"
            End If

            Dim apiKey As String = cfg("blogger")("api_key").ToString()
            Dim blogId As String = cfg("blogger")("blog_id").ToString()
            Dim enhancedContent As String = EnhanceContentForMonetization(contentHtml, cfg)

            ' Build Blogger API request
            Dim postData As New JObject()
            postData("title") = title
            postData("content") = enhancedContent

            ' Add SEO labels if provided
            If labels IsNot Nothing AndAlso labels.Length > 0 Then
                postData("labels") = New JArray(labels)
            End If

            ' Call Blogger API
            Using client As New HttpClient()
                client.Timeout = TimeSpan.FromSeconds(30)

                Dim apiUrl As String = $"https://www.googleapis.com/blogger/v3/blogs/{blogId}/posts?key={apiKey}"
                Dim jsonContent As New StringContent(postData.ToString(), Encoding.UTF8, "application/json")

                Dim response = client.PostAsync(apiUrl, jsonContent).Result
                Dim responseContent = response.Content.ReadAsStringAsync().Result

                If response.IsSuccessStatusCode Then
                    Dim result = JObject.Parse(responseContent)
                    Dim postId As String = result("id").ToString()
                    Dim postUrl As String = result("url").ToString()

                    ' Create Bitly shortlink for monetization tracking
                    Dim bitlyUrl As String = CreateBitlyShortlink(postUrl, cfg)

                    ' Log successful post
                    LogPost(title, postId, bitlyUrl, "published", "")

                    ' Send monetization alerts
                    SendMonetizationAlert(title, postUrl, bitlyUrl, cfg)

                    Return postId
                Else
                    Dim errorMsg As String = $"Blogger API Error: {response.StatusCode} - {responseContent}"
                    LogPost(title, "", "", "failed", errorMsg)
                    Return $"ERROR: {errorMsg}"
                End If
            End Using

        Catch ex As Exception
            Dim errorMsg As String = $"BloggerHelper.PublishPost failed: {ex.Message}"
            LogPost(title, "", "", "error", errorMsg)
            Return $"ERROR: {errorMsg}"
        End Try
    End Function

    ''' <summary>
    ''' Enhance HTML content with monetization elements
    ''' </summary>
    Private Shared Function EnhanceContentForMonetization(contentHtml As String, cfg As JObject) As String
        Try
            Dim enhanced As String = contentHtml

            ' Add affiliate disclaimer at top
            enhanced = AddAffiliateDisclaimer(enhanced, cfg)

            ' Enhance tables with betting context
            enhanced = EnhanceTables(enhanced)

            ' Add strategic CTAs throughout content
            enhanced = AddStrategicCTAs(enhanced, cfg)

            ' Add SEO footer with links
            enhanced = AddSeoFooter(enhanced, cfg)

            Return enhanced

        Catch ex As Exception
            Console.WriteLine($"Content enhancement error: {ex.Message}")
            Return contentHtml ' Return original on error
        End Try
    End Function

    ''' <summary>
    ''' Add compliance-focused affiliate disclaimer
    ''' </summary>
    Private Shared Function AddAffiliateDisclaimer(content As String, cfg As JObject) As String
        Dim disclaimer As String = "<div class='affiliate-disclaimer' style='background: #f0f8ff; padding: 10px; border-left: 4px solid #007cba; margin-bottom: 20px;'>" &
                                   "<strong>📊 EQ12 Sports Analytics</strong><br>" &
                                   "This analysis contains affiliate links. We may earn a commission at no extra cost to you. " &
                                   "All recommendations are based on quantitative analysis and data-driven insights." &
                                   "</div>"

        Return disclaimer & content
    End Function

    ''' <summary>
    ''' Enhance tables with betting context and styling
    ''' </summary>
    Private Shared Function EnhanceTables(content As String) As String
        ' Add CSS styling to tables for better readability
        Dim tableStyle As String = "style='width:100%; border-collapse: collapse; margin: 15px 0;'"
        Dim thStyle As String = "style='background: #007cba; color: white; padding: 8px; text-align: left;'"
        Dim tdStyle As String = "style='padding: 8px; border: 1px solid #ddd;'"

        content = content.Replace("<table>", $"<table {tableStyle}>")
        content = content.Replace("<th>", $"<th {thStyle}>")
        content = content.Replace("<td>", $"<td {tdStyle}>")

        Return content
    End Function

    ''' <summary>
    ''' Add strategic CTAs throughout content
    ''' </summary>
    Private Shared Function AddStrategicCTAs(content As String, cfg As JObject) As String
        Try
            Dim telegramUrl As String = If(cfg("telegram")?("channel_url")?.ToString(), "https://t.me/eq12alerts")

            Dim midCta As String = "<div class='cta-box' style='background: #fff3cd; border: 2px solid #ffc107; padding: 15px; margin: 20px 0; text-align: center;'>" &
                                   "<h3 style='color: #856404; margin-top: 0;'>📈 Get Real-Time Alerts</h3>" &
                                   "<p>Join our premium Telegram channel for instant arbitrage opportunities and value bet alerts.</p>" &
                                   $"<a href='{telegramUrl}' style='background: #007cba; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;'>Join Premium Feed</a>" &
                                   "</div>"

            ' Insert CTA after first paragraph or at 1/3 content length
            Dim insertPos As Integer = Math.Max(content.IndexOf("</p>"), content.Length \ 3)
            If insertPos > 0 AndAlso insertPos < content.Length Then
                content = content.Insert(insertPos + 4, midCta)
            Else
                content &= midCta
            End If

            Return content

        Catch ex As Exception
            Return content ' Return original on error
        End Try
    End Function

    ''' <summary>
    ''' Add SEO footer with backlinks and social proof
    ''' </summary>
    Private Shared Function AddSeoFooter(content As String, cfg As JObject) As String
        Dim footer As String = "<hr style='margin: 30px 0;'>" &
                               "<div class='seo-footer' style='background: #f8f9fa; padding: 20px; border-radius: 5px;'>" &
                               "<h4 style='color: #007cba; margin-top: 0;'>🚀 About EQ12 Sports Analytics</h4>" &
                               "<p>We provide data-driven sports betting insights using advanced algorithms and real-time analysis. " &
                               "Our quantitative approach helps bettors identify arbitrage opportunities and value bets.</p>" &
                               "<p><strong>Follow us:</strong> " &
                               "<a href='https://github.com/Vibehigheric/edgegod-parlay'>GitHub</a> | " &
                               "<a href='https://t.me/eq12alerts'>Telegram</a> | " &
                               "<a href='mailto:contact@eq12.com'>Contact</a></p>" &
                               "<p style='font-size: 0.9em; color: #666;'>Generated by EQ12 SportsBetting Terminal v2.0</p>" &
                               "</div>"

        Return content & footer
    End Function

#End Region

#Region "Logging and Tracking"

    ''' <summary>
    ''' Log blog post to database for tracking and analytics
    ''' </summary>
    Public Shared Sub LogPost(title As String, postId As String, bitlyUrl As String, status As String, errorMsg As String)
        Try
            Dim dbPath As String = "Data\eq12_terminal.db"
            Using conn As New SQLiteConnection($"Data Source={dbPath}")
                conn.Open()

                Dim sql As String = "INSERT INTO blogger_posts (post_id, title, bitly_url, status, error_msg) VALUES (@postId, @title, @bitlyUrl, @status, @errorMsg)"
                Using cmd As New SQLiteCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@postId", If(String.IsNullOrEmpty(postId), DBNull.Value, postId))
                    cmd.Parameters.AddWithValue("@title", title)
                    cmd.Parameters.AddWithValue("@bitlyUrl", If(String.IsNullOrEmpty(bitlyUrl), DBNull.Value, bitlyUrl))
                    cmd.Parameters.AddWithValue("@status", status)
                    cmd.Parameters.AddWithValue("@errorMsg", If(String.IsNullOrEmpty(errorMsg), DBNull.Value, errorMsg))

                    cmd.ExecuteNonQuery()
                End Using
            End Using

        Catch ex As Exception
            Console.WriteLine($"Failed to log blog post: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Get blog post statistics for ROI analysis
    ''' </summary>
    Public Shared Function GetBlogStats(days As Integer) As JObject
        Try
            Dim dbPath As String = "Data\eq12_terminal.db"
            Dim stats As New JObject()

            Using conn As New SQLiteConnection($"Data Source={dbPath}")
                conn.Open()

                ' Total posts published
                Dim sql As String = "SELECT COUNT(*) FROM blogger_posts WHERE status = 'published' AND ts >= datetime('now', '-{0} days')"
                Using cmd As New SQLiteCommand(String.Format(sql, days), conn)
                    stats("total_posts") = Convert.ToInt32(cmd.ExecuteScalar())
                End Using

                ' Success rate
                sql = "SELECT ROUND(CAST(SUM(CASE WHEN status = 'published' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 2) FROM blogger_posts WHERE ts >= datetime('now', '-{0} days')"
                Using cmd As New SQLiteCommand(String.Format(sql, days), conn)
                    Dim successRate = cmd.ExecuteScalar()
                    stats("success_rate") = If(successRate Is DBNull.Value, 0, Convert.ToDouble(successRate))
                End Using

                ' Recent posts
                sql = "SELECT title, post_id, bitly_url, status, ts FROM blogger_posts WHERE ts >= datetime('now', '-{0} days') ORDER BY ts DESC LIMIT 10"
                Using cmd As New SQLiteCommand(String.Format(sql, days), conn)
                    Using reader = cmd.ExecuteReader()
                        Dim recentPosts As New JArray()
                        While reader.Read()
                            Dim post As New JObject()
                            post("title") = reader("title").ToString()
                            post("post_id") = If(reader("post_id") Is DBNull.Value, "", reader("post_id").ToString())
                            post("bitly_url") = If(reader("bitly_url") Is DBNull.Value, "", reader("bitly_url").ToString())
                            post("status") = reader("status").ToString()
                            post("timestamp") = reader("ts").ToString()
                            recentPosts.Add(post)
                        End While
                        stats("recent_posts") = recentPosts
                    End Using
                End Using
            End Using

            Return stats

        Catch ex As Exception
            Console.WriteLine($"Failed to get blog stats: {ex.Message}")
            Return New JObject()
        End Try
    End Function

#End Region

#Region "Content Generation and Monetization"

    ''' <summary>
    ''' Convert betting report summary to SEO-optimized blog post
    ''' </summary>
    Public Shared Function ConvertReportToBlog(reportSummary As String, reportType As String, cfg As JObject) As Tuple(Of String, String)
        Try
            Dim title As String = GenerateSeoTitle(reportType, DateTime.Now)
            Dim content As String = FormatReportForBlog(reportSummary, reportType)

            Return New Tuple(Of String, String)(title, content)

        Catch ex As Exception
            Console.WriteLine($"Failed to convert report to blog: {ex.Message}")
            Return New Tuple(Of String, String)("", "")
        End Try
    End Function

    ''' <summary>
    ''' Generate SEO-optimized title based on report type and date
    ''' </summary>
    Private Shared Function GenerateSeoTitle(reportType As String, reportDate As DateTime) As String
        Dim dateStr As String = reportDate.ToString("MMMM dd, yyyy")

        Select Case reportType.ToLower()
            Case "daily"
                Return $"Daily Sports Betting Report - {dateStr} | EQ12 Analytics"
            Case "weekly"
                Return $"Weekly Arbitrage Digest - Week of {dateStr} | EQ12"
            Case "arbitrage"
                Return $"Live Arbitrage Opportunities - {dateStr} | EQ12 Sports"
            Case "value"
                Return $"Value Bet Analysis - {dateStr} | Data-Driven Picks"
            Case Else
                Return $"Sports Betting Analysis - {dateStr} | EQ12 Terminal"
        End Select
    End Function

    ''' <summary>
    ''' Format report content for blog with HTML enhancements
    ''' </summary>
    Private Shared Function FormatReportForBlog(reportSummary As String, reportType As String) As String
        Dim content As New StringBuilder()

        ' Add introduction with hook
        content.AppendLine("<h2>📊 Executive Summary</h2>")
        content.AppendLine("<p>Today's quantitative analysis reveals key opportunities in the sports betting markets. Our algorithms have identified the following insights:</p>")

        ' Format the main content
        content.AppendLine("<div class='report-content'>")
        content.AppendLine(ConvertTextToHtml(reportSummary))
        content.AppendLine("</div>")

        ' Add methodology section for credibility
        content.AppendLine("<h3>🔬 Methodology</h3>")
        content.AppendLine("<p>Our analysis uses real-time odds data from multiple sportsbooks, statistical models, and machine learning algorithms to identify market inefficiencies and value opportunities.</p>")

        ' Add risk disclaimer
        content.AppendLine("<h3>⚠️ Risk Management</h3>")
        content.AppendLine("<p>Sports betting involves risk. Never bet more than you can afford to lose. These analyses are for informational purposes and should not be considered guaranteed profits.</p>")

        Return content.ToString()
    End Function

    ''' <summary>
    ''' Convert plain text to formatted HTML
    ''' </summary>
    Private Shared Function ConvertTextToHtml(text As String) As String
        ' Basic text to HTML conversion
        Dim html As String = text
        html = html.Replace(vbCrLf, "<br>")
        html = html.Replace(vbLf, "<br>")

        ' Convert headers (lines starting with #)
        html = Regex.Replace(html, "^# (.+)$", "<h3>$1</h3>", RegexOptions.Multiline)
        html = Regex.Replace(html, "^## (.+)$", "<h4>$1</h4>", RegexOptions.Multiline)

        ' Convert bullet points
        html = Regex.Replace(html, "^- (.+)$", "<li>$1</li>", RegexOptions.Multiline)
        html = html.Replace("<li>", "<ul><li>").Replace("</li><br><li>", "</li><li>")
        html = Regex.Replace(html, "</li><br>(?!<li>)", "</li></ul><br>")

        Return html
    End Function

    ''' <summary>
    ''' Create Bitly shortlink for tracking
    ''' </summary>
    Private Shared Function CreateBitlyShortlink(longUrl As String, cfg As JObject) As String
        Try
            ' Check if Bitly is configured
            If cfg("bitly") Is Nothing OrElse cfg("bitly")("access_token") Is Nothing Then
                Return longUrl ' Return original URL if Bitly not configured
            End If

            Dim accessToken As String = cfg("bitly")("access_token").ToString()

            Using client As New HttpClient()
                client.DefaultRequestHeaders.Add("Authorization", $"Bearer {accessToken}")

                Dim postData As New JObject()
                postData("long_url") = longUrl
                postData("group_guid") = cfg("bitly")("group_guid")?.ToString()

                Dim jsonContent As New StringContent(postData.ToString(), Encoding.UTF8, "application/json")
                Dim response = client.PostAsync("https://api-ssl.bitly.com/v4/shorten", jsonContent).Result

                If response.IsSuccessStatusCode Then
                    Dim result = JObject.Parse(response.Content.ReadAsStringAsync().Result)
                    Return result("link").ToString()
                Else
                    Return longUrl
                End If
            End Using

        Catch ex As Exception
            Console.WriteLine($"Bitly shortlink creation failed: {ex.Message}")
            Return longUrl
        End Try
    End Function

#End Region

#Region "Validation and Utilities"

    ''' <summary>
    ''' Validate Blogger configuration
    ''' </summary>
    Private Shared Function ValidateBloggerConfig(cfg As JObject) As Boolean
        Try
            If cfg("blogger") Is Nothing Then Return False
            If String.IsNullOrEmpty(cfg("blogger")("api_key")?.ToString()) Then Return False
            If String.IsNullOrEmpty(cfg("blogger")("blog_id")?.ToString()) Then Return False
            If Not Convert.ToBoolean(cfg("blogger")("enabled")?.ToString()) Then Return False

            Return True

        Catch ex As Exception
            Return False
        End Try
    End Function

    ''' <summary>
    ''' Send monetization alert to Telegram when new blog post is published
    ''' </summary>
    Private Shared Sub SendMonetizationAlert(title As String, blogUrl As String, bitlyUrl As String, cfg As JObject)
        Try
            If cfg("telegram") Is Nothing Then Return

            Dim message As String = $"📝 NEW BLOG POST PUBLISHED{vbCrLf}" &
                                   $"Title: {title}{vbCrLf}" &
                                   $"URL: {bitlyUrl}{vbCrLf}" &
                                   $"Ready for SEO traffic and monetization! 🚀"

            ' Use existing TelegramHelper if available
            ' TelegramHelper.SendMessage(cfg, message)

        Catch ex As Exception
            Console.WriteLine($"Failed to send monetization alert: {ex.Message}")
        End Try
    End Sub

#End Region

End Class
