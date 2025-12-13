Imports System.Data
Imports System.Data.SQLite
Imports System.Drawing
Imports System.IO
Imports System.Net.Http
Imports System.Text.RegularExpressions
Imports System.Windows.Forms
Imports Newtonsoft.Json.Linq

''' <summary>
''' Link Safety Module - Cybersecurity & Link Verification Mastery
''' Provides comprehensive link safety verification, phishing detection, and risk assessment
''' Features: URL resolution, domain reputation, sender verification, safety logging
''' </summary>
Public Class LinkSafetyModule
    Inherits UserControl

    ' UI Components
    Private topPanel As New Panel With {.Height = 160, .Dock = DockStyle.Top}
    Private inputPanel As New Panel With {.Height = 40, .Dock = DockStyle.Top, .Padding = New Padding(10, 5, 10, 5)}
    Private buttonPanel As New Panel With {.Height = 40, .Dock = DockStyle.Top, .Padding = New Padding(10, 5, 10, 5)}
    Private contextPanel As New Panel With {.Height = 40, .Dock = DockStyle.Top, .Padding = New Padding(10, 5, 10, 5)}
    Private checklistPanel As New Panel With {.Height = 40, .Dock = DockStyle.Top, .Padding = New Padding(10, 5, 10, 5)}

    Private urlTextBox As New TextBox With {.Width = 400, .Left = 120, .Top = 8, .PlaceholderText = "Enter shortened URL to verify (bit.ly/xyz, tinyurl.com/abc, etc.)"}
    Private contextTextBox As New TextBox With {.Width = 400, .Left = 120, .Top = 8, .PlaceholderText = "Who sent this link? (email, social media, text message, etc.)"}

    Private verifyBtn As New Button With {.Text = "🔍 Verify Link", .Width = 100, .Left = 530, .Top = 6}
    Private previewBtn As New Button With {.Text = "👁️ Preview (+ Trick)", .Width = 130, .Left = 640, .Top = 6}
    Private clearBtn As New Button With {.Text = "🗑️ Clear", .Width = 70, .Left = 780, .Top = 6}

    Private checklist As New CheckedListBox With {.Left = 10, .Top = 5, .Width = 800, .Height = 30, .CheckOnClick = True}

    Private resultPanel As New Panel With {.Dock = DockStyle.Fill, .Padding = New Padding(10)}
    Private resultTextBox As New TextBox With {.Dock = DockStyle.Fill, .Multiline = True, .ScrollBars = ScrollBars.Vertical, .Font = New Font("Consolas", 9)}

    ' Risk assessment data
    Private trustedDomains As New HashSet(Of String) From {
        "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "buff.ly",
        "github.com", "microsoft.com", "google.com", "amazon.com", "youtube.com",
        "linkedin.com", "facebook.com", "twitter.com", "instagram.com"
    }

    Private suspiciousTlds As New HashSet(Of String) From {
        ".tk", ".ml", ".ga", ".cf", ".click", ".download", ".stream", ".zip"
    }

    Public Sub New()
        InitializeComponents()
        LoadSecurityChecklist()
        LoadRecentChecks()
    End Sub

    ''' <summary>
    ''' Initialize UI components and security features
    ''' </summary>
    Private Sub InitializeComponents()
        ' Setup input panels
        inputPanel.Controls.AddRange({
            New Label With {.Text = "🔗 Short URL:", .Left = 10, .Top = 12, .Width = 100, .Font = New Font("Segoe UI", 9, FontStyle.Bold)},
            urlTextBox
        })

        contextPanel.Controls.AddRange({
            New Label With {.Text = "📤 Sender Info:", .Left = 10, .Top = 12, .Width = 100, .Font = New Font("Segoe UI", 9, FontStyle.Bold)},
            contextTextBox
        })

        buttonPanel.Controls.AddRange({verifyBtn, previewBtn, clearBtn})

        checklistPanel.Controls.Add(checklist)

        topPanel.Controls.AddRange({inputPanel, contextPanel, buttonPanel, checklistPanel})

        ' Setup result area
        resultPanel.Controls.Add(resultTextBox)

        ' Setup main layout
        Me.Controls.AddRange({resultPanel, topPanel})

        ' Wire events
        AddHandler verifyBtn.Click, AddressOf VerifyLink
        AddHandler previewBtn.Click, AddressOf PreviewLink
        AddHandler clearBtn.Click, AddressOf ClearResults
        AddHandler urlTextBox.KeyPress, AddressOf OnUrlKeyPress

        ' Initial instructions
        ShowSecurityInstructions()
    End Sub

    ''' <summary>
    ''' Load cybersecurity verification checklist
    ''' </summary>
    Private Sub LoadSecurityChecklist()
        checklist.Items.Clear()
        checklist.Items.AddRange({
            "✓ I know who sent me this link",
            "✓ The sender context makes sense (expected this type of link)",
            "✓ This link was sent through a secure/trusted channel",
            "✓ The sender's message doesn't use urgent/pressuring language",
            "✓ I'm not being asked to provide sensitive information"
        })

        ' Set all to unchecked by default (security-first approach)
        For i = 0 To checklist.Items.Count - 1
            checklist.SetItemChecked(i, False)
        Next
    End Sub

    ''' <summary>
    ''' Handle Enter key press for quick verification
    ''' </summary>
    Private Sub OnUrlKeyPress(sender As Object, e As KeyPressEventArgs)
        If e.KeyChar = ChrW(Keys.Enter) Then
            VerifyLink(sender, EventArgs.Empty)
            e.Handled = True
        End If
    End Sub

    ''' <summary>
    ''' Comprehensive link verification and safety assessment
    ''' </summary>
    Private Sub VerifyLink(sender As Object, e As EventArgs)
        Try
            Dim shortUrl = urlTextBox.Text.Trim()
            If String.IsNullOrEmpty(shortUrl) Then
                MessageBox.Show("Please enter a shortened URL to verify.", "Input Required", MessageBoxButtons.OK, MessageBoxIcon.Information)
                Return
            End If

            verifyBtn.Text = "🔍 Verifying..."
            verifyBtn.Enabled = False

            resultTextBox.Clear()
            AppendResult("🔐 LINK SECURITY VERIFICATION INITIATED", Color.Blue, True)
            AppendResult($"Target URL: {shortUrl}")
            AppendResult($"Verification Time: {DateTime.Now:yyyy-MM-dd HH:mm:ss} UTC")
            AppendResult(New String("="c, 60))

            ' Step 1: Basic URL analysis
            Dim urlAnalysis = AnalyzeUrlStructure(shortUrl)
            DisplayUrlAnalysis(urlAnalysis)

            ' Step 2: Resolve the actual destination
            Dim resolvedUrl = ResolveShortUrl(shortUrl)
            If Not String.IsNullOrEmpty(resolvedUrl) Then
                DisplayResolutionResults(shortUrl, resolvedUrl)

                ' Step 3: Domain reputation check
                Dim riskAssessment = AssessRisk(resolvedUrl)
                DisplayRiskAssessment(riskAssessment)

                ' Step 4: Context verification
                Dim contextVerification = VerifyContext()
                DisplayContextResults(contextVerification)

                ' Step 5: Final verdict
                Dim finalVerdict = DetermineFinalVerdict(urlAnalysis, riskAssessment, contextVerification)
                DisplayFinalVerdict(finalVerdict)

                ' Step 6: Log to database
                LogSafetyCheck(shortUrl, resolvedUrl, finalVerdict)
            Else
                AppendResult("❌ FAILED TO RESOLVE URL", Color.Red, True)
                AppendResult("The shortened URL could not be resolved. This could indicate:")
                AppendResult("  • Invalid or expired link")
                AppendResult("  • Network connectivity issues")
                AppendResult("  • Link shortener service problems")
                AppendResult("  • Potentially malicious blocking")
            End If

        Catch ex As Exception
            AppendResult($"❌ VERIFICATION ERROR: {ex.Message}", Color.Red, True)
        Finally
            verifyBtn.Text = "🔍 Verify Link"
            verifyBtn.Enabled = True
        End Try
    End Sub

    ''' <summary>
    ''' Preview link using Bitly + trick (add + to see preview)
    ''' </summary>
    Private Sub PreviewLink(sender As Object, e As EventArgs)
        Try
            Dim shortUrl = urlTextBox.Text.Trim()
            If String.IsNullOrEmpty(shortUrl) Then
                MessageBox.Show("Please enter a Bitly link to preview.", "Input Required", MessageBoxButtons.OK, MessageBoxIcon.Information)
                Return
            End If

            ' Check if it's a Bitly link
            If Not shortUrl.ToLower().Contains("bit.ly") Then
                MessageBox.Show("The preview trick (+ method) only works with Bitly links (bit.ly).", "Bitly Links Only", MessageBoxButtons.OK, MessageBoxIcon.Information)
                Return
            End If

            ' Add + to the end for preview
            Dim previewUrl = shortUrl.TrimEnd("+"c) & "+"

            AppendResult("👁️ BITLY PREVIEW TRICK ACTIVATED", Color.Green, True)
            AppendResult($"Original: {shortUrl}")
            AppendResult($"Preview URL: {previewUrl}")
            AppendResult("Opening preview in browser (shows destination + stats without clicking through)...")

            ' Open preview in browser
            Process.Start(New ProcessStartInfo(previewUrl) With {.UseShellExecute = True})

            AppendResult("✅ Preview opened! This shows the destination URL and click statistics safely.")

        Catch ex As Exception
            AppendResult($"Preview failed: {ex.Message}", Color.Red)
        End Try
    End Sub

    ''' <summary>
    ''' Analyze URL structure for initial risk indicators
    ''' </summary>
    Private Function AnalyzeUrlStructure(url As String) As Dictionary(Of String, Object)
        Dim analysis As New Dictionary(Of String, Object)

        Try
            ' Normalize URL
            If Not url.StartsWith("http") Then
                url = "https://" & url
            End If

            Dim uri As New Uri(url)

            analysis("domain") = uri.Host.ToLower()
            analysis("path") = uri.AbsolutePath
            analysis("hasQuery") = Not String.IsNullOrEmpty(uri.Query)
            analysis("scheme") = uri.Scheme
            analysis("isSecure") = uri.Scheme = "https"

            ' Check for suspicious patterns
            Dim suspiciousPatterns As New List(Of String)
            If uri.Host.Contains("xn--") Then suspiciousPatterns.Add("Punycode domain (potential spoofing)")
            If Regex.IsMatch(uri.Host, "\d+\.\d+\.\d+\.\d+") Then suspiciousPatterns.Add("IP address instead of domain")
            If uri.Host.Length > 50 Then suspiciousPatterns.Add("Unusually long domain name")
            If uri.Host.Count("."c) > 3 Then suspiciousPatterns.Add("Multiple subdomains")

            analysis("suspiciousPatterns") = suspiciousPatterns
            analysis("riskLevel") = If(suspiciousPatterns.Any(), "Medium", "Low")

        Catch ex As Exception
            analysis("error") = ex.Message
            analysis("riskLevel") = "High"
        End Try

        Return analysis
    End Function

    ''' <summary>
    ''' Display URL structure analysis results
    ''' </summary>
    Private Sub DisplayUrlAnalysis(analysis As Dictionary(Of String, Object))
        AppendResult("📊 URL STRUCTURE ANALYSIS", Color.Blue, True)

        If analysis.ContainsKey("error") Then
            AppendResult($"❌ Analysis Error: {analysis("error")}", Color.Red)
            Return
        End If

        AppendResult($"Domain: {analysis("domain")}")
        AppendResult($"Scheme: {analysis("scheme")} {If(CBool(analysis("isSecure")), "✅ (Secure)", "⚠️ (Not HTTPS)")}")
        AppendResult($"Path: {analysis("path")}")

        Dim patterns = DirectCast(analysis("suspiciousPatterns"), List(Of String))
        If patterns.Any() Then
            AppendResult("⚠️ SUSPICIOUS PATTERNS DETECTED:", Color.Orange, True)
            For Each pattern In patterns
                AppendResult($"  • {pattern}")
            Next
        Else
            AppendResult("✅ No suspicious URL patterns detected")
        End If

        AppendResult("")
    End Sub

    ''' <summary>
    ''' Resolve shortened URL to actual destination
    ''' </summary>
    Private Function ResolveShortUrl(shortUrl As String) As String
        Try
            If Not shortUrl.StartsWith("http") Then
                shortUrl = "https://" & shortUrl
            End If

            Using client As New HttpClient()
                client.Timeout = TimeSpan.FromSeconds(10)

                ' Don't follow redirects automatically - we want to see the chain
                Dim handler As New HttpClientHandler() With {
                    .AllowAutoRedirect = False
                }

                Using noRedirectClient As New HttpClient(handler)
                    noRedirectClient.Timeout = TimeSpan.FromSeconds(10)

                    Dim response = noRedirectClient.GetAsync(shortUrl).Result

                    If response.Headers.Location IsNot Nothing Then
                        Return response.Headers.Location.ToString()
                    Else
                        ' Try HEAD request
                        Dim headResponse = noRedirectClient.SendAsync(New HttpRequestMessage(HttpMethod.Head, shortUrl)).Result
                        If headResponse.Headers.Location IsNot Nothing Then
                            Return headResponse.Headers.Location.ToString()
                        End If
                    End If
                End Using
            End Using

        Catch ex As Exception
            AppendResult($"Resolution error: {ex.Message}")
        End Try

        Return Nothing
    End Function

    ''' <summary>
    ''' Display URL resolution results
    ''' </summary>
    Private Sub DisplayResolutionResults(shortUrl As String, resolvedUrl As String)
        AppendResult("🎯 URL RESOLUTION RESULTS", Color.Blue, True)
        AppendResult($"Short URL: {shortUrl}")
        AppendResult($"Resolves to: {resolvedUrl}")

        Try
            Dim resolvedUri As New Uri(resolvedUrl)
            AppendResult($"Destination Domain: {resolvedUri.Host}")
            AppendResult($"Destination Path: {resolvedUri.AbsolutePath}")
        Catch
            AppendResult("⚠️ Could not parse resolved URL")
        End Try

        AppendResult("")
    End Sub

    ''' <summary>
    ''' Assess risk based on domain reputation and URL characteristics
    ''' </summary>
    Private Function AssessRisk(resolvedUrl As String) As Dictionary(Of String, Object)
        Dim assessment As New Dictionary(Of String, Object)

        Try
            Dim uri As New Uri(resolvedUrl)
            Dim domain = uri.Host.ToLower()

            ' Check trusted domains
            Dim isTrusted = trustedDomains.Any(Function(d) domain = d OrElse domain.EndsWith("." & d))
            assessment("isTrusted") = isTrusted

            ' Check suspicious TLDs
            Dim hasSuspiciousTld = suspiciousTlds.Any(Function(tld) domain.EndsWith(tld))
            assessment("hasSuspiciousTld") = hasSuspiciousTld

            ' Additional risk factors
            Dim riskFactors As New List(Of String)

            If Not isTrusted AndAlso Not domain.Contains(".") Then
                riskFactors.Add("Single-word domain (potentially suspicious)")
            End If

            If hasSuspiciousTld Then
                riskFactors.Add($"Suspicious top-level domain ({suspiciousTlds.FirstOrDefault(Function(tld) domain.EndsWith(tld))})")
            End If

            If Regex.IsMatch(domain, "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}") Then
                riskFactors.Add("Uses IP address instead of domain name")
            End If

            If domain.Length > 50 Then
                riskFactors.Add("Unusually long domain name")
            End If

            assessment("riskFactors") = riskFactors
            assessment("riskLevel") = If(isTrusted, "Low", If(riskFactors.Any(), "High", "Medium"))

        Catch ex As Exception
            assessment("error") = ex.Message
            assessment("riskLevel") = "Unknown"
        End Try

        Return assessment
    End Function

    ''' <summary>
    ''' Display risk assessment results
    ''' </summary>
    Private Sub DisplayRiskAssessment(assessment As Dictionary(Of String, Object))
        AppendResult("🛡️ SECURITY RISK ASSESSMENT", Color.Blue, True)

        If assessment.ContainsKey("error") Then
            AppendResult($"❌ Assessment Error: {assessment("error")}", Color.Red)
            Return
        End If

        Dim riskLevel = assessment("riskLevel").ToString()
        Dim isTrusted = CBool(assessment("isTrusted"))

        If isTrusted Then
            AppendResult("✅ TRUSTED DOMAIN", Color.Green, True)
            AppendResult("This domain is in our trusted domains list.")
        Else
            AppendResult("⚠️ UNKNOWN DOMAIN", Color.Orange, True)
            AppendResult("This domain is not in our trusted domains list. Exercise caution.")
        End If

        Dim riskFactors = DirectCast(assessment("riskFactors"), List(Of String))
        If riskFactors.Any() Then
            AppendResult("🚨 RISK FACTORS IDENTIFIED:", Color.Red, True)
            For Each factor In riskFactors
                AppendResult($"  • {factor}")
            Next
        End If

        Dim riskColor = If(riskLevel = "Low", Color.Green, If(riskLevel = "Medium", Color.Orange, Color.Red))
        AppendResult($"Risk Level: {riskLevel}", riskColor, True)
        AppendResult("")
    End Sub

    ''' <summary>
    ''' Verify sender context using checklist
    ''' </summary>
    Private Function VerifyContext() As Dictionary(Of String, Object)
        Dim verification As New Dictionary(Of String, Object)

        Dim checkedItems = 0
        For i = 0 To checklist.Items.Count - 1
            If checklist.GetItemChecked(i) Then checkedItems += 1
        Next

        Dim senderContext = contextTextBox.Text.Trim()

        verification("checkedItems") = checkedItems
        verification("totalItems") = checklist.Items.Count
        verification("senderContext") = senderContext
        verification("hasSenderInfo") = Not String.IsNullOrEmpty(senderContext)
        verification("contextScore") = checkedItems / checklist.Items.Count

        Return verification
    End Function

    ''' <summary>
    ''' Display context verification results
    ''' </summary>
    Private Sub DisplayContextResults(verification As Dictionary(Of String, Object))
        AppendResult("👤 SENDER CONTEXT VERIFICATION", Color.Blue, True)

        Dim checkedItems = CInt(verification("checkedItems"))
        Dim totalItems = CInt(verification("totalItems"))
        Dim contextScore = CDbl(verification("contextScore"))
        Dim senderContext = verification("senderContext").ToString()

        AppendResult($"Security Checklist: {checkedItems}/{totalItems} verified ({contextScore:P0})")

        If Not String.IsNullOrEmpty(senderContext) Then
            AppendResult($"Sender Context: {senderContext}")
        Else
            AppendResult("⚠️ No sender context provided", Color.Orange)
        End If

        If contextScore >= 1.0 Then
            AppendResult("✅ All security checks passed", Color.Green)
        ElseIf contextScore >= 0.8 Then
            AppendResult("⚠️ Most security checks passed - proceed with caution", Color.Orange)
        Else
            AppendResult("🚨 Multiple security concerns - high risk", Color.Red)
        End If

        AppendResult("")
    End Function

    ''' <summary>
    ''' Determine final safety verdict
    ''' </summary>
    Private Function DetermineFinalVerdict(urlAnalysis As Dictionary(Of String, Object), riskAssessment As Dictionary(Of String, Object), contextVerification As Dictionary(Of String, Object)) As String
        Try
            Dim urlRisk = urlAnalysis("riskLevel").ToString()
            Dim domainRisk = riskAssessment("riskLevel").ToString()
            Dim contextScore = CDbl(contextVerification("contextScore"))
            Dim isTrusted = CBool(riskAssessment("isTrusted"))

            ' High-risk conditions
            If domainRisk = "High" OrElse contextScore < 0.6 Then
                Return "malicious"
            End If

            ' Safe conditions
            If isTrusted AndAlso contextScore >= 0.8 AndAlso urlRisk = "Low" Then
                Return "safe"
            End If

            ' Default to suspicious for anything in between
            Return "suspicious"

        Catch
            Return "unknown"
        End Try
    End Function

    ''' <summary>
    ''' Display final safety verdict
    ''' </summary>
    Private Sub DisplayFinalVerdict(verdict As String)
        AppendResult("🎯 FINAL SECURITY VERDICT", Color.Blue, True)

        Select Case verdict.ToLower()
            Case "safe"
                AppendResult("✅ SAFE TO PROCEED", Color.Green, True)
                AppendResult("This link appears safe based on our analysis.")
                AppendResult("However, always remain vigilant when clicking links.")

            Case "suspicious"
                AppendResult("⚠️ PROCEED WITH EXTREME CAUTION", Color.Orange, True)
                AppendResult("This link has some concerning characteristics.")
                AppendResult("Consider verifying with the sender before clicking.")

            Case "malicious"
                AppendResult("🚨 DO NOT CLICK - HIGH RISK", Color.Red, True)
                AppendResult("This link shows multiple risk indicators.")
                AppendResult("Contact the sender through a different channel to verify.")

            Case Else
                AppendResult("❓ INSUFFICIENT DATA", Color.Gray, True)
                AppendResult("Unable to determine safety level.")
                AppendResult("Exercise maximum caution.")
        End Select

        AppendResult(New String("="c, 60))
        AppendResult("💡 SECURITY REMINDER: When in doubt, don't click. Verify with sender first.", Color.Blue, True)
    End Sub

    ''' <summary>
    ''' Log safety check to database
    ''' </summary>
    Private Sub LogSafetyCheck(shortUrl As String, resolvedUrl As String, verdict As String)
        Try
            Dim riskFactors = "[]" ' Would include actual risk factors in JSON format
            Dim senderContext = contextTextBox.Text.Trim()

            DBWriter.LogLinkCheck(shortUrl, resolvedUrl, verdict, riskFactors, senderContext)

        Catch ex As Exception
            AppendResult($"Logging failed: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Load recent security checks from database
    ''' </summary>
    Private Sub LoadRecentChecks()
        Try
            Using conn As New SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()
                Using cmd As New SQLiteCommand("
                    SELECT ts, short_url, resolved_url, verdict
                    FROM link_safety_checks
                    ORDER BY ts DESC
                    LIMIT 5", conn)
                    Using rdr = cmd.ExecuteReader()
                        If rdr.HasRows Then
                            AppendResult("📜 RECENT SAFETY CHECKS", Color.Blue, True)
                            While rdr.Read()
                                Dim ts = Convert.ToDateTime(rdr("ts")).ToString("MM-dd HH:mm")
                                Dim shortUrl = rdr("short_url").ToString()
                                Dim verdict = rdr("verdict").ToString()
                                AppendResult($"{ts} | {shortUrl} | {verdict.ToUpper()}")
                            End While
                            AppendResult("")
                        End If
                    End Using
                End Using
            End Using
        Catch ex As Exception
            ' Ignore database errors during initialization
        End Try
    End Sub

    ''' <summary>
    ''' Clear all results and reset form
    ''' </summary>
    Private Sub ClearResults(sender As Object, e As EventArgs)
        resultTextBox.Clear()
        urlTextBox.Clear()
        contextTextBox.Clear()
        LoadSecurityChecklist()
        ShowSecurityInstructions()
    End Sub

    ''' <summary>
    ''' Show initial security instructions
    ''' </summary>
    Private Sub ShowSecurityInstructions()
        AppendResult("🔐 EQ12 LINK SAFETY MODULE - CYBERSECURITY MASTERY", Color.Blue, True)
        AppendResult("Master safe link verification and phishing protection")
        AppendResult("")
        AppendResult("🎯 FEATURES:", Color.Green, True)
        AppendResult("• Comprehensive URL analysis and risk assessment")
        AppendResult("• Bitly preview trick (add + to any bit.ly link)")
        AppendResult("• Domain reputation and trust verification")
        AppendResult("• Sender context validation checklist")
        AppendResult("• Complete safety logging and analytics")
        AppendResult("")
        AppendResult("⚠️ SECURITY BEST PRACTICES:", Color.Orange, True)
        AppendResult("1. Never click suspicious links from unknown senders")
        AppendResult("2. Always verify sender identity through separate channel")
        AppendResult("3. Use preview features before clicking")
        AppendResult("4. Check for urgency/pressure tactics in messages")
        AppendResult("5. When in doubt, don't click - ask the sender directly")
        AppendResult("")
        AppendResult("Enter a shortened URL above to begin security verification...")
    End Sub

    ''' <summary>
    ''' Append formatted text to results
    ''' </summary>
    Private Sub AppendResult(text As String, Optional color As Color = Nothing, Optional bold As Boolean = False)
        If color = Nothing Then color = Color.Black

        Dim currentLength = resultTextBox.TextLength
        resultTextBox.AppendText(text & Environment.NewLine)

        resultTextBox.SelectionStart = currentLength
        resultTextBox.SelectionLength = text.Length
        resultTextBox.SelectionColor = color
        If bold Then
            resultTextBox.SelectionFont = New Font(resultTextBox.Font, FontStyle.Bold)
        End If

        resultTextBox.SelectionStart = resultTextBox.TextLength
        resultTextBox.ScrollToCaret()
    End Sub
End Class
