' EQ12 Sports Betting Terminal - Telegram Bot Integration
' Full integration with EQ12 Telegram systems and automated alert management

Imports System.Collections.Generic
Imports System.Threading.Tasks
Imports System.Net.Http
Imports System.Text
Imports Newtonsoft.Json
Imports Newtonsoft.Json.Linq

Public Class TelegramBot

    Private httpClient As HttpClient
    Private config As Dictionary(Of String, Object)
    Private logger As Action(Of String, String)

    ' Telegram configuration
    Private botToken As String = ""
    Private chatId As String = ""
    Private botUsername As String = ""
    Private isEnabled As Boolean = False

    ' Message templates
    Private alertTemplates As Dictionary(Of String, String)

    Public Event MessageSent(message As String, success As Boolean)
    Public Event BotStatusChanged(isOnline As Boolean)

    Public Sub New()
        httpClient = New HttpClient()
        httpClient.Timeout = TimeSpan.FromSeconds(30)

        InitializeTelegramBot()

        ' Set up logging
        logger = Sub(message As String, level As String)
                     Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] [{level}] TelegramBot: {message}")
                 End Sub

        logger("Telegram Bot initialized", "INFO")
    End Sub

    Private Sub InitializeTelegramBot()
        Try
            ' Load configuration from multiple sources (EQ12 standard)
            LoadConfiguration()

            ' Initialize message templates
            InitializeMessageTemplates()

            ' Test bot connection if enabled
            If isEnabled Then
                Task.Run(Sub() TestBotConnection())
            End If

        Catch ex As Exception
            logger($"Error initializing Telegram bot: {ex.Message}", "ERROR")
        End Try
    End Sub

    Public Sub LoadConfiguration(Optional configData As Dictionary(Of String, Object) = Nothing)
        Try
            ' Load from provided config first
            If configData IsNot Nothing AndAlso configData.ContainsKey("telegram") Then
                Dim telegramConfig = TryCast(configData("telegram"), JObject)
                If telegramConfig IsNot Nothing Then
                    If telegramConfig.ContainsKey("token") Then
                        botToken = telegramConfig("token").ToString()
                    End If
                    If telegramConfig.ContainsKey("chat_id") Then
                        chatId = telegramConfig("chat_id").ToString()
                    End If
                End If
            End If

            ' Load from environment variables (EQ12 standard)
            If String.IsNullOrEmpty(botToken) Then
                botToken = Environment.GetEnvironmentVariable("TELEGRAM_BOT_TOKEN")
            End If

            If String.IsNullOrEmpty(chatId) Then
                chatId = Environment.GetEnvironmentVariable("TELEGRAM_CHAT_ID")
            End If

            ' Load from EQ12 config files
            If String.IsNullOrEmpty(botToken) OrElse String.IsNullOrEmpty(chatId) Then
                LoadFromEQ12Config()
            End If

            ' Validate configuration
            If Not String.IsNullOrEmpty(botToken) AndAlso Not String.IsNullOrEmpty(chatId) Then
                isEnabled = True
                logger($"Telegram bot configured: {botToken.Substring(0, Math.Min(8, botToken.Length))}... -> {chatId}", "SUCCESS")
            Else
                isEnabled = False
                logger("Telegram bot disabled: missing credentials", "WARNING")
            End If

        Catch ex As Exception
            logger($"Error loading Telegram configuration: {ex.Message}", "ERROR")
            isEnabled = False
        End Try
    End Sub

    Private Sub LoadFromEQ12Config()
        Try
            ' Check multiple EQ12 config locations
            Dim configPaths = New String() {
                "C:\EQ12\configs\api_credentials.json",
                "C:\EQ12\keys\telegram_credentials.json",
                "C:\EQ12\EdgeGodParlays\config.json"
            }

            For Each configPath In configPaths
                If IO.File.Exists(configPath) Then
                    Try
                        Dim configJson = IO.File.ReadAllText(configPath)
                        Dim configObj = JsonConvert.DeserializeObject(Of Dictionary(Of String, Object))(configJson)

                        ' Try different key patterns used in EQ12 systems
                        If configObj.ContainsKey("telegram") Then
                            Dim telegramConfig = TryCast(configObj("telegram"), JObject)
                            If telegramConfig IsNot Nothing Then
                                If telegramConfig.ContainsKey("bot_token") AndAlso String.IsNullOrEmpty(botToken) Then
                                    botToken = telegramConfig("bot_token").ToString()
                                End If
                                If telegramConfig.ContainsKey("chat_id") AndAlso String.IsNullOrEmpty(chatId) Then
                                    chatId = telegramConfig("chat_id").ToString()
                                End If
                            End If
                        End If

                        ' Direct keys
                        If configObj.ContainsKey("TELEGRAM_BOT_TOKEN") AndAlso String.IsNullOrEmpty(botToken) Then
                            botToken = configObj("TELEGRAM_BOT_TOKEN").ToString()
                        End If
                        If configObj.ContainsKey("TELEGRAM_CHAT_ID") AndAlso String.IsNullOrEmpty(chatId) Then
                            chatId = configObj("TELEGRAM_CHAT_ID").ToString()
                        End If

                        If Not String.IsNullOrEmpty(botToken) AndAlso Not String.IsNullOrEmpty(chatId) Then
                            logger($"Loaded Telegram config from: {configPath}", "SUCCESS")
                            Exit For
                        End If

                    Catch ex As Exception
                        logger($"Error reading config from {configPath}: {ex.Message}", "WARNING")
                    End Try
                End If
            Next

        Catch ex As Exception
            logger($"Error loading from EQ12 config: {ex.Message}", "ERROR")
        End Try
    End Sub

    Private Sub InitializeMessageTemplates()
        Try
            alertTemplates = New Dictionary(Of String, String) From {
                {"arbitrage", "🔥 **ARBITRAGE ALERT** 🔥" + vbCrLf + "{sport} - {teams}" + vbCrLf + "💰 Profit: {profit}" + vbCrLf + "📊 {details}"},
                {"value_bet", "💰 **VALUE BET ALERT** 💰" + vbCrLf + "{sport} - {teams}" + vbCrLf + "📈 Edge: {edge}" + vbCrLf + "💵 Kelly Size: {kelly_size}" + vbCrLf + "🎯 {details}"},
                {"bankroll_update", "📊 **BANKROLL UPDATE** 📊" + vbCrLf + "💰 Current: {current}" + vbCrLf + "📈 P&L: {pnl}" + vbCrLf + "🎲 Win Rate: {win_rate}" + vbCrLf + "📉 ROI: {roi}"},
                {"risk_alert", "⚠️ **RISK ALERT** ⚠️" + vbCrLf + "🚨 {risk_type}" + vbCrLf + "📊 Current: {current_value}" + vbCrLf + "🛑 Limit: {limit_value}" + vbCrLf + "⚡ Action: {action}"},
                {"system_status", "🤖 **EQ12 SYSTEM STATUS** 🤖" + vbCrLf + "📡 Status: {status}" + vbCrLf + "⏰ Uptime: {uptime}" + vbCrLf + "📊 Active Bets: {active_bets}" + vbCrLf + "💻 {details}"},
                {"bet_placed", "🎯 **BET PLACED** 🎯" + vbCrLf + "{sport} - {selection}" + vbCrLf + "💵 Stake: {stake}" + vbCrLf + "📈 Odds: {odds}" + vbCrLf + "🔮 Expected: {expected}"},
                {"bet_result", "🏆 **BET RESULT** 🏆" + vbCrLf + "{sport} - {selection}" + vbCrLf + "✅ Result: {result}" + vbCrLf + "💰 P&L: {profit}" + vbCrLf + "📊 New Balance: {balance}"},
                {"injury_alert", "🏥 **INJURY ALERT** 🏥" + vbCrLf + "⚠️ {player} - {team}" + vbCrLf + "🩹 Status: {status}" + vbCrLf + "📅 Impact: {impact}" + vbCrLf + "📊 Line Movement Expected"}
            }

            logger("Message templates initialized", "SUCCESS")

        Catch ex As Exception
            logger($"Error initializing message templates: {ex.Message}", "ERROR")
        End Try
    End Sub

    Private Async Sub TestBotConnection()
        Try
            If Not isEnabled Then Return

            Dim url = $"https://api.telegram.org/bot{botToken}/getMe"
            Dim response = Await httpClient.GetStringAsync(url)
            Dim result = JsonConvert.DeserializeObject(Of JObject)(response)

            If result("ok").ToObject(Of Boolean)() Then
                Dim botInfo = result("result")
                botUsername = botInfo("username").ToString()
                logger($"Bot connection successful: @{botUsername}", "SUCCESS")
                RaiseEvent BotStatusChanged(True)
            Else
                logger("Bot connection failed: invalid response", "ERROR")
                isEnabled = False
                RaiseEvent BotStatusChanged(False)
            End If

        Catch ex As Exception
            logger($"Bot connection test failed: {ex.Message}", "ERROR")
            isEnabled = False
            RaiseEvent BotStatusChanged(False)
        End Try
    End Sub

    Public Sub Initialize()
        Try
            If isEnabled Then
                Task.Run(Sub() TestBotConnection())
            End If

            logger("Telegram bot initialization complete", "SUCCESS")

        Catch ex As Exception
            logger($"Error during initialization: {ex.Message}", "ERROR")
            Throw
        End Try
    End Sub

    Public Async Function SendAlert(message As String, Optional messageType As String = "general") As Task(Of Boolean)
        Try
            If Not isEnabled Then
                logger("Cannot send alert: bot disabled", "WARNING")
                Return False
            End If

            ' Format message with timestamp and EQ12 branding
            Dim formattedMessage = $"🎯 **EQ12 SPORTS BETTING TERMINAL** 🎯{vbCrLf}{vbCrLf}{message}{vbCrLf}{vbCrLf}⏰ {DateTime.Now:yyyy-MM-dd HH:mm:ss} EST"

            ' Send message
            Dim success = Await SendTelegramMessage(formattedMessage, chatId)

            ' Raise event
            RaiseEvent MessageSent(message, success)

            Return success

        Catch ex As Exception
            logger($"Error sending alert: {ex.Message}", "ERROR")
            RaiseEvent MessageSent(message, False)
            Return False
        End Try
    End Function

    Public Async Function SendArbitrageAlert(opportunity As Dictionary(Of String, Object)) As Task(Of Boolean)
        Try
            If Not isEnabled Then Return False

            Dim sport = If(opportunity.ContainsKey("sport"), opportunity("sport").ToString(), "Unknown")
            Dim teams = If(opportunity.ContainsKey("teams"), opportunity("teams").ToString(), "Unknown vs Unknown")
            Dim profit = If(opportunity.ContainsKey("profit_percentage"), $"{CDbl(opportunity("profit_percentage")):P2}", "Unknown")

            Dim message = alertTemplates("arbitrage").
                Replace("{sport}", sport).
                Replace("{teams}", teams).
                Replace("{profit}", profit).
                Replace("{details}", "Check terminal for full details")

            Return Await SendAlert(message, "arbitrage")

        Catch ex As Exception
            logger($"Error sending arbitrage alert: {ex.Message}", "ERROR")
            Return False
        End Try
    End Function

    Public Async Function SendValueBetAlert(bet As Dictionary(Of String, Object)) As Task(Of Boolean)
        Try
            If Not isEnabled Then Return False

            Dim sport = If(bet.ContainsKey("sport"), bet("sport").ToString(), "Unknown")
            Dim teams = If(bet.ContainsKey("teams"), bet("teams").ToString(), "Unknown vs Unknown")
            Dim edge = If(bet.ContainsKey("expected_value"), $"{CDbl(bet("expected_value")):P2}", "Unknown")
            Dim kellySize = If(bet.ContainsKey("kelly_size"), $"${CDec(bet("kelly_size")):F2}", "TBD")

            Dim message = alertTemplates("value_bet").
                Replace("{sport}", sport).
                Replace("{teams}", teams).
                Replace("{edge}", edge).
                Replace("{kelly_size}", kellySize).
                Replace("{details}", "Auto-bet consideration")

            Return Await SendAlert(message, "value_bet")

        Catch ex As Exception
            logger($"Error sending value bet alert: {ex.Message}", "ERROR")
            Return False
        End Try
    End Function

    Public Async Function SendBankrollUpdate(bankrollData As Dictionary(Of String, Decimal)) As Task(Of Boolean)
        Try
            If Not isEnabled Then Return False

            Dim current = If(bankrollData.ContainsKey("current_bankroll"), $"${bankrollData("current_bankroll"):F2}", "$0.00")
            Dim pnl = If(bankrollData.ContainsKey("total_profit"), $"{bankrollData("total_profit"):+$#,##0.00;-$#,##0.00;$0.00}", "$0.00")
            Dim winRate = If(bankrollData.ContainsKey("win_rate"), $"{bankrollData("win_rate"):P1}", "0%")
            Dim roi = If(bankrollData.ContainsKey("roi"), $"{bankrollData("roi"):P2}", "0%")

            Dim message = alertTemplates("bankroll_update").
                Replace("{current}", current).
                Replace("{pnl}", pnl).
                Replace("{win_rate}", winRate).
                Replace("{roi}", roi)

            Return Await SendAlert(message, "bankroll")

        Catch ex As Exception
            logger($"Error sending bankroll update: {ex.Message}", "ERROR")
            Return False
        End Try
    End Function

    Public Async Function SendRiskAlert(riskType As String, currentValue As Decimal, limitValue As Decimal, action As String) As Task(Of Boolean)
        Try
            If Not isEnabled Then Return False

            Dim message = alertTemplates("risk_alert").
                Replace("{risk_type}", riskType).
                Replace("{current_value}", $"${currentValue:F2}").
                Replace("{limit_value}", $"${limitValue:F2}").
                Replace("{action}", action)

            Return Await SendAlert(message, "risk")

        Catch ex As Exception
            logger($"Error sending risk alert: {ex.Message}", "ERROR")
            Return False
        End Try
    End Function

    Public Async Function SendSystemStatus(status As String, uptime As String, activeBets As Integer, details As String) As Task(Of Boolean)
        Try
            If Not isEnabled Then Return False

            Dim message = alertTemplates("system_status").
                Replace("{status}", status).
                Replace("{uptime}", uptime).
                Replace("{active_bets}", activeBets.ToString()).
                Replace("{details}", details)

            Return Await SendAlert(message, "system")

        Catch ex As Exception
            logger($"Error sending system status: {ex.Message}", "ERROR")
            Return False
        End Try
    End Function

    Public Async Function SendBetPlaced(sport As String, selection As String, stake As Decimal, odds As String, expectedValue As Double) As Task(Of Boolean)
        Try
            If Not isEnabled Then Return False

            Dim message = alertTemplates("bet_placed").
                Replace("{sport}", sport).
                Replace("{selection}", selection).
                Replace("{stake}", $"${stake:F2}").
                Replace("{odds}", odds).
                Replace("{expected}", $"{expectedValue:P2} EV")

            Return Await SendAlert(message, "bet_placed")

        Catch ex As Exception
            logger($"Error sending bet placed alert: {ex.Message}", "ERROR")
            Return False
        End Try
    End Function

    Public Async Function SendBetResult(sport As String, selection As String, result As String, profit As Decimal, newBalance As Decimal) As Task(Of Boolean)
        Try
            If Not isEnabled Then Return False

            Dim resultEmoji = If(result.ToLower().Contains("won"), "✅ WON", If(result.ToLower().Contains("lost"), "❌ LOST", "⏳ PENDING"))

            Dim message = alertTemplates("bet_result").
                Replace("{sport}", sport).
                Replace("{selection}", selection).
                Replace("{result}", resultEmoji).
                Replace("{profit}", $"{profit:+$#,##0.00;-$#,##0.00;$0.00}").
                Replace("{balance}", $"${newBalance:F2}")

            Return Await SendAlert(message, "bet_result")

        Catch ex As Exception
            logger($"Error sending bet result: {ex.Message}", "ERROR")
            Return False
        End Try
    End Function

    Private Async Function SendTelegramMessage(message As String, targetChatId As String) As Task(Of Boolean)
        Try
            Dim url = $"https://api.telegram.org/bot{botToken}/sendMessage"

            Dim payload = New Dictionary(Of String, Object) From {
                {"chat_id", targetChatId},
                {"text", message},
                {"parse_mode", "Markdown"},
                {"disable_web_page_preview", True}
            }

            Dim jsonPayload = JsonConvert.SerializeObject(payload)
            Dim content = New StringContent(jsonPayload, Encoding.UTF8, "application/json")

            Dim response = Await httpClient.PostAsync(url, content)
            Dim responseText = Await response.Content.ReadAsStringAsync()

            If response.IsSuccessStatusCode Then
                Dim result = JsonConvert.DeserializeObject(Of JObject)(responseText)
                If result("ok").ToObject(Of Boolean)() Then
                    logger($"Message sent successfully to {targetChatId}", "SUCCESS")
                    Return True
                Else
                    logger($"Message send failed: {result("description")}", "ERROR")
                    Return False
                End If
            Else
                logger($"HTTP error sending message: {response.StatusCode}", "ERROR")
                Return False
            End If

        Catch ex As Exception
            logger($"Error sending Telegram message: {ex.Message}", "ERROR")
            Return False
        End Try
    End Function

    Public Function IsEnabled() As Boolean
        Return isEnabled
    End Function

    Public Function GetBotUsername() As String
        Return botUsername
    End Function

    Public Function GetChatId() As String
        Return chatId
    End Function

    Public Sub Dispose()
        Try
            httpClient?.Dispose()
            logger("Telegram Bot disposed", "INFO")
        Catch ex As Exception
            logger($"Error disposing Telegram Bot: {ex.Message}", "ERROR")
        End Try
    End Sub

End Class
