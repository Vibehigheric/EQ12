Imports System.Net.Http
Imports System.Text
Imports System.Threading.Tasks
Imports Newtonsoft.Json.Linq

''' <summary>
''' Comprehensive alerting system for Telegram, Discord, and extensible notification channels
''' </summary>
Public Class Alerts
    Private Shared ReadOnly httpClient As New HttpClient()
    Private Shared lastAlertTimes As New Dictionary(Of String, DateTime)
    Private Shared ReadOnly cooldownMinutes As Integer = 15

    ''' <summary>
    ''' Send Telegram message with advanced formatting and error handling
    ''' </summary>
    Public Shared Async Function TelegramAsync(token As String, chatId As String, text As String, Optional parseMode As String = "Markdown", Optional disableWebPreview As Boolean = True, Optional priority As String = "medium") As Task(Of Boolean)
        Try
            ' Check cooldown for duplicate messages
            Dim messageHash = $"telegram_{chatId}_{text.GetHashCode()}"
            If IsInCooldown(messageHash) AndAlso priority <> "urgent" Then
                Return False
            End If

            ' Prepare message with EQ12 branding
            Dim formattedMessage = FormatTelegramMessage(text, priority)

            ' Build API URL
            Dim url = $"https://api.telegram.org/bot{token}/sendMessage"

            ' Create request payload
            Dim payload = New JObject From {
                {"chat_id", chatId},
                {"text", formattedMessage},
                {"parse_mode", parseMode},
                {"disable_web_page_preview", disableWebPreview}
            }

            ' Send request
            Using content As New StringContent(payload.ToString(), Encoding.UTF8, "application/json")
                Using response = Await httpClient.PostAsync(url, content)
                    If response.IsSuccessStatusCode Then
                        UpdateLastAlertTime(messageHash)
                        LogDelivery("telegram", chatId, "sent", formattedMessage)
                        Return True
                    Else
                        Dim error = Await response.Content.ReadAsStringAsync()
                        LogDelivery("telegram", chatId, "failed", formattedMessage, error)
                        Return False
                    End If
                End Using
            End Using

        Catch ex As Exception
            LogDelivery("telegram", chatId, "error", text, ex.Message)
            Return False
        End Try
    End Function

    ''' <summary>
    ''' Send Telegram message synchronously
    ''' </summary>
    Public Shared Function Telegram(token As String, chatId As String, text As String, Optional parseMode As String = "Markdown", Optional disableWebPreview As Boolean = True, Optional priority As String = "medium") As Boolean
        Return TelegramAsync(token, chatId, text, parseMode, disableWebPreview, priority).GetAwaiter().GetResult()
    End Function

    ''' <summary>
    ''' Send Discord webhook message with rich embeds
    ''' </summary>
    Public Shared Async Function DiscordAsync(webhookUrl As String, text As String, Optional username As String = "EQ12-Terminal", Optional avatarUrl As String = "", Optional priority As String = "medium") As Task(Of Boolean)
        Try
            ' Check cooldown for duplicate messages
            Dim messageHash = $"discord_{webhookUrl.GetHashCode()}_{text.GetHashCode()}"
            If IsInCooldown(messageHash) AndAlso priority <> "urgent" Then
                Return False
            End If

            ' Create rich embed based on priority
            Dim embed = CreateDiscordEmbed(text, priority)

            ' Create webhook payload
            Dim payload = New JObject From {
                {"username", username},
                {"embeds", New JArray From {embed}}
            }

            If Not String.IsNullOrEmpty(avatarUrl) Then
                payload("avatar_url") = avatarUrl
            End If

            ' Send webhook request
            Using content As New StringContent(payload.ToString(), Encoding.UTF8, "application/json")
                Using response = Await httpClient.PostAsync(webhookUrl, content)
                    If response.IsSuccessStatusCode Then
                        UpdateLastAlertTime(messageHash)
                        LogDelivery("discord", webhookUrl, "sent", text)
                        Return True
                    Else
                        Dim error = Await response.Content.ReadAsStringAsync()
                        LogDelivery("discord", webhookUrl, "failed", text, error)
                        Return False
                    End If
                End Using
            End Using

        Catch ex As Exception
            LogDelivery("discord", webhookUrl, "error", text, ex.Message)
            Return False
        End Try
    End Function

    ''' <summary>
    ''' Send Discord message synchronously
    ''' </summary>
    Public Shared Function Discord(webhookUrl As String, text As String, Optional username As String = "EQ12-Terminal", Optional avatarUrl As String = "", Optional priority As String = "medium") As Boolean
        Return DiscordAsync(webhookUrl, text, username, avatarUrl, priority).GetAwaiter().GetResult()
    End Function

    ''' <summary>
    ''' Send multi-channel alert (Telegram + Discord + extensible)
    ''' </summary>
    Public Shared Async Function MultiChannelAlertAsync(config As JObject, alertType As String, title As String, message As String, Optional priority As String = "medium", Optional eventId As String = Nothing, Optional betId As Integer? = Nothing) As Task(Of Boolean)
        Dim success = False
        Dim channels As New List(Of String)

        Try
            ' Format comprehensive alert message
            Dim fullMessage = FormatAlertMessage(alertType, title, message, eventId, betId)

            ' Send to Telegram if configured
            If config("telegram")?("token") IsNot Nothing AndAlso config("telegram")?("chat_id") IsNot Nothing Then
                Dim telegramSuccess = Await TelegramAsync(
                    config("telegram")("token").ToString(),
                    config("telegram")("chat_id").ToString(),
                    fullMessage,
                    config("telegram")?("parse_mode")?.ToString() ?? "Markdown",
                    config("telegram")?("disable_web_page_preview")?.ToObject(Of Boolean)() ?? True,
                    priority
                )
                If telegramSuccess Then
                    channels.Add("telegram")
                    success = True
                End If
            End If

            ' Send to Discord if configured
            If config("discord")?("webhook") IsNot Nothing Then
                Dim discordSuccess = Await DiscordAsync(
                    config("discord")("webhook").ToString(),
                    fullMessage,
                    config("discord")?("username")?.ToString() ?? "EQ12-Terminal",
                    config("discord")?("avatar_url")?.ToString() ?? "",
                    priority
                )
                If discordSuccess Then
                    channels.Add("discord")
                    success = True
                End If
            End If

            ' Log alert to database for tracking
            If success Then
                DBWriter.LogAlert(alertType, title, message, priority, String.Join(",", channels), eventId, betId)
            End If

            Return success

        Catch ex As Exception
            Console.WriteLine($"Multi-channel alert error: {ex.Message}")
            Return False
        End Try
    End Function

    ''' <summary>
    ''' Send arbitrage opportunity alert
    ''' </summary>
    Public Shared Async Function ArbitrageAlertAsync(config As JObject, eventId As String, sport As String, sideABook As String, sideAOdds As Integer, sideBBook As String, sideBOdds As Integer, profitPct As Double, guaranteedProfit As Double) As Task(Of Boolean)
        Dim title = "🔥 Arbitrage Opportunity Detected!"
        Dim message = $"""
**Event**: {eventId}
**Sport**: {sport}
**Side A**: {sideABook} ({If(sideAOdds > 0, "+", "")}{sideAOdds})
**Side B**: {sideBBook} ({If(sideBOdds > 0, "+", "")}{sideBOdds})
**Profit**: {profitPct:F2}% (${guaranteedProfit:F2} guaranteed)

⚡ **Act fast** - opportunities usually last 2-5 minutes!
"""

        Return Await MultiChannelAlertAsync(config, "arbitrage", title, message, "high", eventId)
    End Function

    ''' <summary>
    ''' Send value bet alert
    ''' </summary>
    Public Shared Async Function ValueBetAlertAsync(config As JObject, eventId As String, sport As String, selection As String, book As String, odds As Integer, edge As Double, kellyFraction As Double, suggestedStake As Double) As Task(Of Boolean)
        Dim title = "💰 Value Bet Identified!"
        Dim message = $"""
**Event**: {eventId}
**Sport**: {sport}
**Selection**: {selection}
**Book**: {book}
**Odds**: {If(odds > 0, "+", "")}{odds}
**Edge**: {edge:F2}%
**Kelly Fraction**: {kellyFraction:F3}
**Suggested Stake**: ${suggestedStake:F2}

📊 Based on model predictions and current market prices.
"""

        Return Await MultiChannelAlertAsync(config, "value_bet", title, message, "medium", eventId)
    End Function

    ''' <summary>
    ''' Send line movement alert
    ''' </summary>
    Public Shared Async Function LineMovementAlertAsync(config As JObject, eventId As String, market As String, book As String, oldOdds As Integer, newOdds As Integer, changePercent As Double) As Task(Of Boolean)
        Dim direction = If(newOdds > oldOdds, "📈", "📉")
        Dim title = $"{direction} Significant Line Movement"
        Dim message = $"""
**Event**: {eventId}
**Market**: {market}
**Book**: {book}
**Old Odds**: {If(oldOdds > 0, "+", "")}{oldOdds}
**New Odds**: {If(newOdds > 0, "+", "")}{newOdds}
**Change**: {changePercent:F1}%

🎯 Monitor for potential value or reverse line movement plays.
"""

        Return Await MultiChannelAlertAsync(config, "line_movement", title, message, "low", eventId)
    End Function

    ''' <summary>
    ''' Send bankroll milestone alert
    ''' </summary>
    Public Shared Async Function BankrollMilestoneAlertAsync(config As JObject, currentBalance As Double, milestoneType As String, changeAmount As Double, changePct As Double) As Task(Of Boolean)
        Dim emoji = If(changeAmount > 0, "🚀", "⚠️")
        Dim title = $"{emoji} Bankroll {milestoneType}"
        Dim message = $"""
**Current Balance**: ${currentBalance:F2}
**Change**: {If(changeAmount > 0, "+", "")}${changeAmount:F2} ({If(changePct > 0, "+", "")}{changePct:F1}%)
**Milestone**: {milestoneType}

{If(changeAmount > 0, "Keep up the great work!", "Review recent performance and adjust strategy if needed.")}
"""

        Dim priority = If(Math.Abs(changePct) > 10, "high", "medium")
        Return Await MultiChannelAlertAsync(config, "bankroll", title, message, priority)
    End Function

    ''' <summary>
    ''' Send system status alert
    ''' </summary>
    Public Shared Async Function SystemStatusAlertAsync(config As JObject, status As String, component As String, message As String) As Task(Of Boolean)
        Dim emoji = Select Case status.ToLower()
            Case "online", "success" : "✅"
            Case "warning" : "⚠️"
            Case "error", "offline" : "🚨"
            Case Else : "ℹ️"
        End Select

        Dim title = $"{emoji} System Status: {component}"
        Dim fullMessage = $"""
**Component**: {component}
**Status**: {status}
**Details**: {message}
**Timestamp**: {DateTime.Now:yyyy-MM-dd HH:mm:ss}
"""

        Dim priority = If(status.ToLower() = "error", "high", "low")
        Return Await MultiChannelAlertAsync(config, "system_status", title, fullMessage, priority)
    End Function

    ''' <summary>
    ''' Format Telegram message with EQ12 branding and priority indicators
    ''' </summary>
    Private Shared Function FormatTelegramMessage(text As String, priority As String) As String
        Dim priorityEmoji = Select Case priority.ToLower()
            Case "urgent" : "🚨"
            Case "high" : "🔥"
            Case "medium" : "📊"
            Case "low" : "ℹ️"
            Case Else : "📈"
        End Select

        Return $"{priorityEmoji} **EQ12 Sports Betting Terminal**{vbCrLf}{vbCrLf}{text}{vbCrLf}{vbCrLf}⏰ {DateTime.Now:HH:mm:ss}"
    End Function

    ''' <summary>
    ''' Create Discord embed with color coding based on priority
    ''' </summary>
    Private Shared Function CreateDiscordEmbed(text As String, priority As String) As JObject
        Dim color = Select Case priority.ToLower()
            Case "urgent" : 15158332 ' Red
            Case "high" : 15844367   ' Gold
            Case "medium" : 3447003  ' Blue
            Case "low" : 8359053     ' Gray
            Case Else : 5763719      ' Green
        End Select

        Dim embed As New JObject From {
            {"title", "EQ12 Sports Betting Terminal"},
            {"description", text},
            {"color", color},
            {"timestamp", DateTime.UtcNow.ToString("o")},
            {"footer", New JObject From {
                {"text", $"Priority: {priority.ToUpper()}"}
            }}
        }

        Return embed
    End Function

    ''' <summary>
    ''' Format comprehensive alert message with metadata
    ''' </summary>
    Private Shared Function FormatAlertMessage(alertType As String, title As String, message As String, Optional eventId As String = Nothing, Optional betId As Integer? = Nothing) As String
        Dim sb As New StringBuilder()

        sb.AppendLine(title)
        sb.AppendLine()
        sb.AppendLine(message)

        If Not String.IsNullOrEmpty(eventId) Then
            sb.AppendLine()
            sb.AppendLine($"🎯 **Event ID**: {eventId}")
        End If

        If betId.HasValue Then
            sb.AppendLine($"📊 **Bet ID**: {betId.Value}")
        End If

        Return sb.ToString()
    End Function

    ''' <summary>
    ''' Check if alert is in cooldown period to prevent spam
    ''' </summary>
    Private Shared Function IsInCooldown(messageHash As String) As Boolean
        SyncLock lastAlertTimes
            If lastAlertTimes.ContainsKey(messageHash) Then
                Return DateTime.Now.Subtract(lastAlertTimes(messageHash)).TotalMinutes < cooldownMinutes
            End If
            Return False
        End SyncLock
    End Function

    ''' <summary>
    ''' Update last alert time for cooldown tracking
    ''' </summary>
    Private Shared Sub UpdateLastAlertTime(messageHash As String)
        SyncLock lastAlertTimes
            lastAlertTimes(messageHash) = DateTime.Now
        End SyncLock
    End Sub

    ''' <summary>
    ''' Log alert delivery status to database
    ''' </summary>
    Private Shared Sub LogDelivery(channel As String, destination As String, status As String, message As String, Optional error As String = "")
        Try
            ' Log to performance metrics for monitoring
            DBWriter.LogPerformanceMetric("alert_delivery", $"{channel}_{status}", 1, "count", "Alerts")

            ' Log detailed info for debugging
            If status = "error" OrElse status = "failed" Then
                Console.WriteLine($"Alert delivery {status} - Channel: {channel}, Error: {error}")
            End If

        Catch ex As Exception
            Console.WriteLine($"Failed to log alert delivery: {ex.Message}")
        End Try
    End Sub

End Class
