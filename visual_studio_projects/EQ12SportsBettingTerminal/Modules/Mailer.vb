Imports System.Net
Imports System.Net.Mail
Imports System.Text
Imports Newtonsoft.Json.Linq

''' <summary>
''' Final Form SMTP + GitHub Gist Email Integration
''' Sends reports via email with PDF/Excel attachments AND creates GitHub Gists for mobile-friendly viewing
''' </summary>
Public Class Mailer
    ''' <summary>
    ''' Send email with attachments and optionally create GitHub Gist for mobile viewing
    ''' </summary>
    Public Shared Sub SendEmail(cfg As JObject, subject As String, body As String, attachments As List(Of String), Optional gistContent As String = "", Optional gistFilename As String = "")
        Try
            Dim smtpCfg = cfg("smtp")
            If smtpCfg Is Nothing Then
                Console.WriteLine("❌ SMTP configuration not found in config.json")
                Return
            End If

            Dim host = smtpCfg("host")?.ToString()
            Dim port = smtpCfg("port")?.ToObject(Of Integer)()
            Dim user = smtpCfg("user")?.ToString()
            Dim pass = smtpCfg("pass")?.ToString()
            Dim toAddr = smtpCfg("to")?.ToString()

            If String.IsNullOrEmpty(host) OrElse String.IsNullOrEmpty(user) OrElse String.IsNullOrEmpty(pass) OrElse String.IsNullOrEmpty(toAddr) Then
                Console.WriteLine("❌ Incomplete SMTP configuration")
                Return
            End If

            ' Create GitHub Gist if content provided
            Dim gistUrl As String = ""
            If Not String.IsNullOrEmpty(gistContent) AndAlso Not String.IsNullOrEmpty(gistFilename) Then
                Try
                    gistUrl = GitHubSync.CreateGist(gistFilename, "md", gistContent)
                    Console.WriteLine($"✅ GitHub Gist created: {gistUrl}")
                Catch gistEx As Exception
                    Console.WriteLine($"⚠️ Gist creation failed: {gistEx.Message}")
                End Try
            End If

            ' Enhance email body with Gist link if available
            Dim finalBody = body
            If Not String.IsNullOrEmpty(gistUrl) Then
                finalBody += vbCrLf & vbCrLf & $"📱 **Quick Mobile View:** {gistUrl}" & vbCrLf &
                           "Click the link above for instant mobile-friendly report viewing!"
            End If

            ' Send email
            Using msg As New MailMessage()
                msg.From = New MailAddress(user, "EQ12 Sports Betting Terminal")
                msg.To.Add(toAddr)
                msg.Subject = subject
                msg.Body = finalBody
                msg.IsBodyHtml = False

                ' Add attachments
                Dim attachmentCount = 0
                For Each path In attachments
                    If IO.File.Exists(path) Then
                        msg.Attachments.Add(New Attachment(path))
                        attachmentCount += 1
                        Console.WriteLine($"📎 Attached: {IO.Path.GetFileName(path)}")
                    Else
                        Console.WriteLine($"⚠️ Attachment not found: {path}")
                    End If
                Next

                ' Send via SMTP
                Using client As New SmtpClient(host, port.Value)
                    client.Credentials = New NetworkCredential(user, pass)
                    client.EnableSsl = True
                    client.Timeout = 30000 ' 30 seconds
                    client.Send(msg)
                End Using

                Console.WriteLine($"✅ Email sent successfully to {toAddr}")
                Console.WriteLine($"   📧 Subject: {subject}")
                Console.WriteLine($"   📎 Attachments: {attachmentCount}")
                If Not String.IsNullOrEmpty(gistUrl) Then
                    Console.WriteLine($"   🔗 Gist URL: {gistUrl}")
                End If

            End Using

        Catch ex As SmtpException
            Console.WriteLine($"❌ SMTP Error: {ex.Message}")
            If ex.InnerException IsNot Nothing Then
                Console.WriteLine($"   Details: {ex.InnerException.Message}")
            End If
        Catch ex As Exception
            Console.WriteLine($"❌ Email error: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Send simple notification email (no attachments)
    ''' </summary>
    Public Shared Sub SendNotification(cfg As JObject, subject As String, message As String)
        SendEmail(cfg, subject, message, New List(Of String)())
    End Sub

    ''' <summary>
    ''' Send arbitrage alert with Gist link for mobile viewing
    ''' </summary>
    Public Shared Sub SendArbAlert(cfg As JObject, arbData As JObject)
        Try
            Dim subject = $"🔥 EQ12 Arbitrage Alert - {arbData("arb_pct")}%"

            ' Create detailed alert content
            Dim alertContent As New StringBuilder()
            alertContent.AppendLine($"# EQ12 Arbitrage Alert - {arbData("arb_pct")}%")
            alertContent.AppendLine($"**Generated:** {DateTime.Now:yyyy-MM-dd HH:mm:ss}")
            alertContent.AppendLine()
            alertContent.AppendLine($"## Opportunity Details")
            alertContent.AppendLine($"- **Event:** {arbData("event_id")}")
            alertContent.AppendLine($"- **Sport/Market:** {arbData("sport")} {arbData("market")}")
            alertContent.AppendLine($"- **Side A:** {arbData("side_a")} @ {arbData("odds_a")} ({arbData("book_a")})")
            alertContent.AppendLine($"- **Side B:** {arbData("side_b")} @ {arbData("odds_b")} ({arbData("book_b")})")
            alertContent.AppendLine($"- **Arbitrage %:** {arbData("arb_pct")}%")
            alertContent.AppendLine()

            If arbData("mode")?.ToString() = "hedge" Then
                alertContent.AppendLine($"## Hedge Stakes (Risk-Free)")
                alertContent.AppendLine($"- **Stake A:** ${arbData("hedge_stakeA"):F2}")
                alertContent.AppendLine($"- **Stake B:** ${arbData("hedge_stakeB"):F2}")
                alertContent.AppendLine($"- **Total Stake:** ${arbData("total_stake"):F2}")
                alertContent.AppendLine($"- **Guaranteed Profit:** ${arbData("lock_profit"):F2}")
            ElseIf arbData("mode")?.ToString() = "kelly" Then
                alertContent.AppendLine($"## Kelly Stakes (EV Optimal)")
                alertContent.AppendLine($"- **Kelly A:** ${arbData("kelly_stakeA"):F2}")
                alertContent.AppendLine($"- **Kelly B:** ${arbData("kelly_stakeB"):F2}")
                alertContent.AppendLine($"- **Bankroll:** ${arbData("bankroll"):F2}")
                alertContent.AppendLine($"- **Kelly Fraction:** {arbData("kelly_fraction"):P0}")
            End If

            alertContent.AppendLine()
            alertContent.AppendLine($"*Alert generated by EQ12 Sports Betting Terminal at {DateTime.Now:HH:mm:ss}*")

            Dim emailBody = $"🔥 ARBITRAGE OPPORTUNITY DETECTED!" & vbCrLf & vbCrLf &
                           $"Event: {arbData("event_id")}" & vbCrLf &
                           $"Arbitrage: {arbData("arb_pct")}%" & vbCrLf &
                           $"Side A: {arbData("side_a")} @ {arbData("odds_a")} ({arbData("book_a")})" & vbCrLf &
                           $"Side B: {arbData("side_b")} @ {arbData("odds_b")} ({arbData("book_b")})" & vbCrLf &
                           $"Stakes: ${arbData("hedge_stakeA"):F2} / ${arbData("hedge_stakeB"):F2}" & vbCrLf &
                           $"Guaranteed Profit: ${arbData("lock_profit"):F2}"

            Dim gistFilename = $"arb_alert_{DateTime.Now:yyyyMMdd_HHmmss}"

            SendEmail(cfg, subject, emailBody, New List(Of String)(), alertContent.ToString(), gistFilename)

        Catch ex As Exception
            Console.WriteLine($"❌ Failed to send arbitrage alert: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Test SMTP configuration
    ''' </summary>
    Public Shared Function TestSMTP(cfg As JObject) As Boolean
        Try
            Dim testSubject = "EQ12 SMTP Test"
            Dim testBody = $"This is a test email from EQ12 Sports Betting Terminal.{vbCrLf}Sent at: {DateTime.Now}"

            SendEmail(cfg, testSubject, testBody, New List(Of String)())
            Return True

        Catch ex As Exception
            Console.WriteLine($"❌ SMTP test failed: {ex.Message}")
            Return False
        End Try
    End Function
End Class
