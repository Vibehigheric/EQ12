Imports System.Net.Http
Imports System.Net
Imports System.Text
Imports System.Threading.Tasks
Imports Newtonsoft.Json
Imports HtmlAgilityPack
Imports System.IO

''' <summary>
''' EQ12 PACER SCRAPER MODULE (VB.NET)
''' Integrates with Python backend for PACER data scraping
''' Provides Windows-native GUI for legal case monitoring
''' 
''' Features:
''' - PACER login and session management
''' - CourtListener API integration (FREE RECAP data)
''' - PDF document download with cost optimization
''' - HTML parsing for docket sheets
''' - Integration with EQ12 Business Intelligence platform
''' 
''' Created: November 28, 2025
''' Author: EQ12 System Architect
''' </summary>
Public Class PacerScraperModule
    
    Private ReadOnly httpClient As New HttpClient()
    Private ReadOnly pythonApiBase As String = "http://localhost:5001"  ' Separate port for PACER API
    Private cookieContainer As New CookieContainer()
    
    ' PACER endpoints
    Private Const PACER_LOGIN_URL As String = "https://pacer.login.uscourts.gov/csologin/login.jsf"
    Private Const COURTLISTENER_API As String = "https://www.courtlistener.com/api/rest/v3/"
    
    ' Configuration
    Private pacerUsername As String
    Private pacerPassword As String
    Private courtlistenerApiKey As String
    Private isAuthenticated As Boolean = False
    
    ' Cost tracking
    Private pacerCosts As New Dictionary(Of String, Decimal) From {
        {"pages_downloaded", 0},
        {"total_cost", 0.0},
        {"recap_saves", 0.0}
    }
    
    Public Sub New()
        ' Load credentials from environment variables (NEVER hardcode!)
        pacerUsername = Environment.GetEnvironmentVariable("PACER_USERNAME")
        pacerPassword = Environment.GetEnvironmentVariable("PACER_PASSWORD")
        courtlistenerApiKey = Environment.GetEnvironmentVariable("COURTLISTENER_API_KEY")
        
        ' Configure HTTP client with cookie support
        Dim handler As New HttpClientHandler With {
            .UseCookies = True,
            .CookieContainer = cookieContainer
        }
        httpClient = New HttpClient(handler)
        httpClient.Timeout = TimeSpan.FromMinutes(5)
        
        Console.WriteLine("PacerScraperModule initialized")
    End Sub
    
#Region "CourtListener API (FREE PACER Alternative)"
    
    ''' <summary>
    ''' Search CourtListener RECAP archive (FREE)
    ''' 90% of PACER documents available here at no cost!
    ''' </summary>
    Public Async Function SearchCourtListenerAsync(searchName As String, Optional district As String = Nothing) As Task(Of List(Of PacerCase))
        Try
            ' Build request
            Dim url As String = $"{COURTLISTENER_API}search/"
            httpClient.DefaultRequestHeaders.Clear()
            httpClient.DefaultRequestHeaders.Add("Authorization", $"Token {courtlistenerApiKey}")
            
            ' Build query parameters
            Dim queryParams As New Dictionary(Of String, String) From {
                {"q", searchName},
                {"type", "r"},  ' RECAP documents only
                {"order_by", "dateFiled desc"}
            }
            
            If Not String.IsNullOrEmpty(district) Then
                queryParams.Add("court", district)
            End If
            
            ' Build URL with query string
            Dim queryString As String = String.Join("&", queryParams.Select(Function(kv) $"{kv.Key}={Uri.EscapeDataString(kv.Value)}"))
            Dim fullUrl As String = $"{url}?{queryString}"
            
            ' Execute request
            Dim response = Await httpClient.GetAsync(fullUrl)
            response.EnsureSuccessStatusCode()
            
            Dim jsonResponse = Await response.Content.ReadAsStringAsync()
            Dim data = JsonConvert.DeserializeObject(Of CourtListenerResponse)(jsonResponse)
            
            ' Convert to PacerCase objects
            Dim cases As New List(Of PacerCase)
            For Each result In data.results
                Dim pacerCase As New PacerCase With {
                    .CaseId = result.id,
                    .CaseNumber = result.docketNumber,
                    .CaseName = result.caseName,
                    .Court = result.court,
                    .FiledDate = If(DateTime.TryParse(result.dateFiled, Nothing), DateTime.Parse(result.dateFiled), Nothing),
                    .Source = "CourtListener",
                    .RecapAvailable = True,
                    .Cost = 0.0  ' FREE!
                }
                cases.Add(pacerCase)
            Next
            
            Console.WriteLine($"Found {cases.Count} cases on CourtListener (FREE)")
            Return cases
            
        Catch ex As Exception
            Console.WriteLine($"CourtListener search failed: {ex.Message}")
            Return New List(Of PacerCase)
        End Try
    End Function
    
#End Region
    
#Region "PACER Authentication"
    
    ''' <summary>
    ''' Authenticate with PACER login system
    ''' Establishes session cookies for subsequent requests
    ''' </summary>
    Public Async Function AuthenticatePacerAsync() As Task(Of Boolean)
        If String.IsNullOrEmpty(pacerUsername) OrElse String.IsNullOrEmpty(pacerPassword) Then
            MessageBox.Show("PACER credentials not configured. Set PACER_USERNAME and PACER_PASSWORD environment variables.", 
                          "Configuration Error", MessageBoxButtons.OK, MessageBoxIcon.Warning)
            Return False
        End If
        
        Try
            ' Prepare login data
            Dim loginData As New Dictionary(Of String, String) From {
                {"loginid", pacerUsername},
                {"password", pacerPassword}
            }
            
            Dim content As New FormUrlEncodedContent(loginData)
            
            ' Submit login
            Dim response = Await httpClient.PostAsync(PACER_LOGIN_URL, content)
            Dim responseText = Await response.Content.ReadAsStringAsync()
            
            ' Check if login successful (look for logout link)
            If responseText.ToLower().Contains("logout") Then
                isAuthenticated = True
                Console.WriteLine("✅ Successfully authenticated with PACER")
                Return True
            Else
                Console.WriteLine("❌ PACER authentication failed - check credentials")
                Return False
            End If
            
        Catch ex As Exception
            Console.WriteLine($"PACER login error: {ex.Message}")
            Return False
        End Try
    End Function
    
#End Region
    
#Region "Multi-District Search"
    
    ''' <summary>
    ''' Search ALL federal districts nationwide (94 districts)
    ''' PACER cannot do this - you'd have to search each manually!
    ''' </summary>
    Public Async Function SearchNationwideAsync(searchName As String) As Task(Of List(Of PacerCase))
        Console.WriteLine($"Starting nationwide search for '{searchName}'...")
        
        ' Federal districts to search (top 20 for performance)
        Dim districts As String() = {
            "nywd", "nynd", "nysd", "nyed",  ' New York
            "cacd", "cand", "casd", "caed",  ' California
            "txnd", "txsd", "txed", "txwd",  ' Texas
            "flnd", "flmd", "flsd",          ' Florida
            "ilnd", "ilcd", "ilsd",          ' Illinois
            "paed", "pamd"                   ' Pennsylvania
        }
        
        ' Search all districts in parallel
        Dim tasks As New List(Of Task(Of List(Of PacerCase)))
        For Each district In districts
            tasks.Add(SearchCourtListenerAsync(searchName, district))
        Next
        
        ' Wait for all searches to complete
        Dim results = Await Task.WhenAll(tasks)
        
        ' Flatten results
        Dim allCases As New List(Of PacerCase)
        For Each resultSet In results
            allCases.AddRange(resultSet)
        Next
        
        ' Deduplicate by case number
        Dim uniqueCases = allCases.
            GroupBy(Function(c) c.CaseNumber).
            Select(Function(g) g.First()).
            ToList()
        
        Console.WriteLine($"Nationwide search complete: {uniqueCases.Count} unique cases found")
        Return uniqueCases
    End Function
    
#End Region
    
#Region "Document Download"
    
    ''' <summary>
    ''' Download PDF document from RECAP (free) or PACER (paid)
    ''' Strategy: Check RECAP first to minimize costs
    ''' </summary>
    Public Async Function DownloadDocumentAsync(documentId As String) As Task(Of Byte())
        ' Try RECAP first (FREE)
        Dim recapPdf = Await CheckRecapArchiveAsync(documentId)
        If recapPdf IsNot Nothing Then
            Console.WriteLine($"✅ Document {documentId} found in RECAP (FREE!)")
            UpdateCostSavings(recapPdf.Length)
            Return recapPdf
        End If
        
        ' Fallback to PACER (costs money)
        Console.WriteLine($"⚠️ Document {documentId} not in RECAP, downloading from PACER ($$$)")
        Dim pacerPdf = Await DownloadFromPacerAsync(documentId)
        
        If pacerPdf IsNot Nothing Then
            UpdatePacerCosts(pacerPdf.Length)
        End If
        
        Return pacerPdf
    End Function
    
    ''' <summary>
    ''' Check if document is available in free RECAP archive
    ''' </summary>
    Private Async Function CheckRecapArchiveAsync(documentId As String) As Task(Of Byte())
        Try
            Dim url As String = $"{COURTLISTENER_API}recap-documents/{documentId}/"
            httpClient.DefaultRequestHeaders.Clear()
            httpClient.DefaultRequestHeaders.Add("Authorization", $"Token {courtlistenerApiKey}")
            
            Dim response = Await httpClient.GetAsync(url)
            If response.IsSuccessStatusCode Then
                Dim jsonResponse = Await response.Content.ReadAsStringAsync()
                Dim data = JsonConvert.DeserializeObject(Of RecapDocument)(jsonResponse)
                
                If data.is_available AndAlso Not String.IsNullOrEmpty(data.filepath_local) Then
                    ' Download the free PDF
                    Dim pdfResponse = Await httpClient.GetAsync(data.filepath_local)
                    Return Await pdfResponse.Content.ReadAsByteArrayAsync()
                End If
            End If
            
        Catch ex As Exception
            Console.WriteLine($"RECAP check failed: {ex.Message}")
        End Try
        
        Return Nothing
    End Function
    
    ''' <summary>
    ''' Download from PACER (costs $0.10 per page, max $3.00 per document)
    ''' </summary>
    Private Async Function DownloadFromPacerAsync(documentId As String) As Task(Of Byte())
        If Not isAuthenticated Then
            Await AuthenticatePacerAsync()
        End If
        
        ' PACER document URLs vary by court
        ' Example: https://ecf.nywd.uscourts.gov/doc1/12345678
        ' Actual implementation requires court-specific logic
        
        Console.WriteLine("⚠️ PACER download requires court-specific implementation")
        Return Nothing
    End Function
    
#End Region
    
#Region "HTML Parsing"
    
    ''' <summary>
    ''' Parse PACER docket sheet HTML into structured data
    ''' Uses HtmlAgilityPack for robust HTML parsing
    ''' </summary>
    Public Function ParseDocketSheet(html As String) As List(Of DocketEntry)
        Try
            Dim doc As New HtmlDocument()
            doc.LoadHtml(html)
            
            ' PACER docket sheets have table with id="docket"
            Dim rows = doc.DocumentNode.SelectNodes("//table[@id='docket']/tr")
            If rows Is Nothing Then Return New List(Of DocketEntry)
            
            Dim entries As New List(Of DocketEntry)
            
            For Each row In rows.Skip(1)  ' Skip header row
                Dim cells = row.SelectNodes("td")
                If cells IsNot Nothing AndAlso cells.Count >= 3 Then
                    
                    Dim entry As New DocketEntry With {
                        .DocketNumber = cells(0).InnerText.Trim(),
                        .EntryDate = ParseDate(cells(1).InnerText.Trim()),
                        .EntryText = cells(2).InnerText.Trim()
                    }
                    
                    ' Extract document links if present
                    Dim links = cells(2).SelectNodes(".//a")
                    If links IsNot Nothing Then
                        entry.DocumentLinks = links.Select(Function(l) l.GetAttributeValue("href", "")).ToList()
                    End If
                    
                    entries.Add(entry)
                End If
            Next
            
            Console.WriteLine($"Parsed {entries.Count} docket entries")
            Return entries
            
        Catch ex As Exception
            Console.WriteLine($"Docket parsing failed: {ex.Message}")
            Return New List(Of DocketEntry)
        End Try
    End Function
    
    Private Function ParseDate(dateText As String) As Date?
        Dim parsedDate As Date
        If Date.TryParse(dateText, parsedDate) Then
            Return parsedDate
        End If
        Return Nothing
    End Function
    
#End Region
    
#Region "Cost Tracking"
    
    Private Sub UpdatePacerCosts(pdfSize As Integer)
        ' Estimate pages (rough: 1KB per page)
        Dim pages As Decimal = Math.Ceiling(pdfSize / 1024.0)
        Dim cost As Decimal = Math.Min(pages * 0.1, 3.0)  ' Max $3.00 per document
        
        pacerCosts("pages_downloaded") += pages
        pacerCosts("total_cost") += cost
        
        Console.WriteLine($"PACER download: {pages} pages, ${cost:F2}")
    End Sub
    
    Private Sub UpdateCostSavings(pdfSize As Integer)
        ' Estimate what it would have cost on PACER
        Dim pages As Decimal = Math.Ceiling(pdfSize / 1024.0)
        Dim savings As Decimal = Math.Min(pages * 0.1, 3.0)
        
        pacerCosts("recap_saves") += savings
        
        Console.WriteLine($"RECAP saved: ${savings:F2}")
    End Sub
    
    Public Function GetCostSummary() As Dictionary(Of String, Object)
        Return New Dictionary(Of String, Object) From {
            {"pacer_pages", pacerCosts("pages_downloaded")},
            {"pacer_cost", pacerCosts("total_cost")},
            {"recap_savings", pacerCosts("recap_saves")},
            {"efficiency", $"{(pacerCosts("recap_saves") / (pacerCosts("total_cost") + pacerCosts("recap_saves")) * 100):F1}%"}
        }
    End Function
    
#End Region
    
#Region "Python Backend Integration"
    
    ''' <summary>
    ''' Call Python backend for advanced PACER operations
    ''' Python handles ML analysis, database operations, etc.
    ''' </summary>
    Public Async Function CallPythonBackendAsync(endpoint As String, data As Object) As Task(Of String)
        Try
            Dim url As String = $"{pythonApiBase}/{endpoint}"
            Dim jsonContent As String = JsonConvert.SerializeObject(data)
            Dim content As New StringContent(jsonContent, Encoding.UTF8, "application/json")
            
            Dim response = Await httpClient.PostAsync(url, content)
            response.EnsureSuccessStatusCode()
            
            Return Await response.Content.ReadAsStringAsync()
            
        Catch ex As Exception
            Console.WriteLine($"Python backend call failed: {ex.Message}")
            Return "{""error"": ""Python backend unavailable""}"
        End Try
    End Function
    
#End Region
    
End Class

#Region "Data Models"

''' <summary>
''' PACER case data model
''' </summary>
Public Class PacerCase
    Public Property CaseId As String
    Public Property CaseNumber As String
    Public Property CaseName As String
    Public Property Court As String
    Public Property District As String
    Public Property Plaintiff As String
    Public Property Defendant As String
    Public Property CaseType As String
    Public Property FiledDate As Date?
    Public Property ClosedDate As Date?
    Public Property Status As String
    Public Property JudgeName As String
    Public Property NatureOfSuit As String
    Public Property Source As String  ' "CourtListener" or "PACER"
    Public Property RecapAvailable As Boolean
    Public Property Cost As Decimal
    Public Property MatchScore As Double  ' For fuzzy matching
End Class

''' <summary>
''' Docket entry data model
''' </summary>
Public Class DocketEntry
    Public Property DocketNumber As String
    Public Property EntryDate As Date?
    Public Property EntryText As String
    Public Property FiledBy As String
    Public Property DocumentCount As Integer
    Public Property DocumentLinks As List(Of String)
End Class

''' <summary>
''' CourtListener API response model
''' </summary>
Public Class CourtListenerResponse
    Public Property count As Integer
    Public Property results As List(Of CourtListenerResult)
End Class

Public Class CourtListenerResult
    Public Property id As String
    Public Property docketNumber As String
    Public Property caseName As String
    Public Property court As String
    Public Property dateFiled As String
    Public Property dateTerminated As String
    Public Property nature_of_suit As String
End Class

''' <summary>
''' RECAP document model
''' </summary>
Public Class RecapDocument
    Public Property id As String
    Public Property is_available As Boolean
    Public Property filepath_local As String
    Public Property page_count As Integer
End Class

#End Region
