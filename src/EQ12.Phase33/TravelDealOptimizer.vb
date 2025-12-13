Imports System.IO
Imports System.Net.Http

''' <summary>
''' Travel deal discovery and funnel automation
''' Queries flight/hotel prices, formats deal pages, integrates affiliate links
''' </summary>
Public Class TravelDealOptimizer
    Private _dataRoot As String
    Private _logger As Logger
    Private _httpClient As HttpClient
    
    Public Sub New(dataRoot As String)
        _dataRoot = dataRoot
        _logger = New Logger(dataRoot)
        _httpClient = New HttpClient()
    End Sub
    
    ''' <summary>
    ''' Find top deal opportunities for the day
    ''' </summary>
    Public Function FindDailyDeals() As List(Of TravelDeal)
        Try
            _logger.Log("[TRAVEL-DEALS] Scanning for top deals")
            
            Dim deals As New List(Of TravelDeal)
            
            ' Query flight APIs for deals
            Dim flightDeals = ScanFlightPrices()
            deals.AddRange(flightDeals)
            
            ' Query hotel APIs for deals
            Dim hotelDeals = ScanHotelPrices()
            deals.AddRange(hotelDeals)
            
            ' Score and rank by ROI potential
            Dim scoredDeals = ScoreDeals(deals)
            Dim topDeals = scoredDeals.Take(10).ToList()
            
            _logger.Log($"[TRAVEL-DEALS] Found {topDeals.Count} top deals")
            
            Return topDeals
        Catch ex As Exception
            _logger.LogError($"[TRAVEL-DEALS] Deal scan failed: {ex.Message}")
            Return New List(Of TravelDeal)
        End Try
    End Function
    
    ''' <summary>
    ''' Generate landing page HTML for a deal
    ''' </summary>
    Public Function GenerateDealPage(deal As TravelDeal) As String
        Try
            Dim html As New System.Text.StringBuilder()
            
            html.AppendLine("<!DOCTYPE html>")
            html.AppendLine("<html>")
            html.AppendLine("<head>")
            html.AppendLine($"<title>{deal.Title} - {deal.Discount}% OFF</title>")
            html.AppendLine("<meta charset='utf-8'>")
            html.AppendLine("<meta name='viewport' content='width=device-width, initial-scale=1.0'>")
            html.AppendLine(GetCssStyles())
            html.AppendLine("</head>")
            html.AppendLine("<body>")
            
            ' Hero section
            html.AppendLine("<div class='hero'>")
            html.AppendLine($"<h1>{deal.Title}</h1>")
            html.AppendLine($"<p class='badge'>{deal.Discount}% OFF Today Only</p>")
            html.AppendLine("</div>")
            
            ' Deal details
            html.AppendLine("<div class='content'>")
            html.AppendLine($"<h2>Save ${deal.SavingsAmount} on Your Trip</h2>")
            html.AppendLine($"<p>{deal.Description}</p>")
            
            ' Pricing breakdown
            html.AppendLine("<div class='pricing'>")
            html.AppendLine($"<div class='price-row'>")
            html.AppendLine($"<span>Original Price:</span><span class='strike'>${deal.OriginalPrice:F2}</span>")
            html.AppendLine($"</div>")
            html.AppendLine($"<div class='price-row'>")
            html.AppendLine($"<span>Today's Price:</span><span class='highlight'>${deal.DiscountedPrice:F2}</span>")
            html.AppendLine($"</div>")
            html.AppendLine($"<div class='price-row'>")
            html.AppendLine($"<span><strong>You Save:</strong></span><span class='save'>${deal.SavingsAmount:F2}</span>")
            html.AppendLine($"</div>")
            html.AppendLine("</div>")
            
            ' Itinerary details
            html.AppendLine("<div class='itinerary'>")
            html.AppendLine($"<h3>Trip Details</h3>")
            html.AppendLine($"<p><strong>From:</strong> {deal.Departure}</p>")
            html.AppendLine($"<p><strong>To:</strong> {deal.Destination}</p>")
            html.AppendLine($"<p><strong>Dates:</strong> {deal.StartDate:MMM d, yyyy} - {deal.EndDate:MMM d, yyyy}</p>")
            html.AppendLine($"<p><strong>Duration:</strong> {(deal.EndDate - deal.StartDate).Days} days</p>")
            html.AppendLine("</div>")
            
            ' CTA button with affiliate link
            html.AppendLine("<div class='cta'>")
            html.AppendLine($"<a href='{deal.AffiliateLink}' class='btn btn-primary'>Get Deal Now</a>")
            html.AppendLine("</div>")
            
            ' Social proof
            html.AppendLine("<div class='social-proof'>")
            html.AppendLine($"<p>✓ {deal.BookingRate * 100:F0}% booking rate | Commission: ${deal.ProjectedCommission:F2}</p>")
            html.AppendLine("</div>")
            
            html.AppendLine("</div>")
            html.AppendLine("</body>")
            html.AppendLine("</html>")
            
            Return html.ToString()
        Catch ex As Exception
            _logger.LogError($"[TRAVEL-DEALS] Page generation failed: {ex.Message}")
            Return ""
        End Try
    End Function
    
    ''' <summary>
    ''' Export deal cards as JSON for bulk upload
    ''' </summary>
    Public Function ExportDealsAsJson(deals As List(Of TravelDeal)) As String
        Try
            Dim json As New System.Text.StringBuilder()
            json.AppendLine("{")
            json.AppendLine($"""timestamp"": ""{DateTime.UtcNow:yyyy-MM-dd HH:mm:ss}""," )
            json.AppendLine($"""deal_count"": {deals.Count},")
            json.AppendLine("""deals"": [")
            
            For i = 0 To deals.Count - 1
                Dim deal = deals(i)
                json.AppendLine("{")
                json.AppendLine($"""id"": ""{deal.DealId}"",")
                json.AppendLine($"""title"": ""{deal.Title}"",")
                json.AppendLine($"""destination"": ""{deal.Destination}"",")
                json.AppendLine($"""discount_percent"": {deal.Discount},")
                json.AppendLine($"""original_price"": {deal.OriginalPrice},")
                json.AppendLine($"""discounted_price"": {deal.DiscountedPrice},")
                json.AppendLine($"""savings"": {deal.SavingsAmount},")
                json.AppendLine($"""commission"": {deal.ProjectedCommission},")
                json.AppendLine($"""affiliate_link"": ""{deal.AffiliateLink}"",")
                json.AppendLine($"""booking_rate"": {deal.BookingRate}")
                json.AppendLine("}")
                
                If i < deals.Count - 1 Then
                    json.AppendLine(",")
                End If
            Next
            
            json.AppendLine("]")
            json.AppendLine("}")
            
            Return json.ToString()
        Catch ex As Exception
            _logger.LogError($"[TRAVEL-DEALS] JSON export failed: {ex.Message}")
            Return ""
        End Try
    End Function
    
    ''' <summary>
    ''' Track conversion for a deal
    ''' </summary>
    Public Sub LogDealConversion(dealId As String, visitor As String, converted As Boolean)
        Try
            _logger.Log($"[TRAVEL-DEALS] Deal {dealId}: {If(converted, "CONVERTED", "ABANDONED")} ({visitor})")
            ' Log to conversions_daily table in eq12_memory.db
        Catch ex As Exception
            _logger.LogError($"[TRAVEL-DEALS] Conversion logging failed: {ex.Message}")
        End Try
    End Sub
    
    Private Function ScanFlightPrices() As List(Of TravelDeal)
        Dim deals As New List(Of TravelDeal)
        
        ' Scan popular routes (NYC, LAX, MIA, ORD, DFW, ATL, etc.)
        ' In production, call Skyscanner, Kayak, or ITA API
        
        deals.Add(New TravelDeal With {
            .DealId = "FLIGHT_NYC_LAX_001",
            .Title = "NYC → Los Angeles",
            .Destination = "Los Angeles",
            .Departure = "New York",
            .StartDate = DateTime.Now.AddDays(7),
            .EndDate = DateTime.Now.AddDays(14),
            .OriginalPrice = 450,
            .DiscountedPrice = 285,
            .Discount = 37,
            .SavingsAmount = 165,
            .Description = "Weekend escape to sunny Los Angeles with roundtrip flights included",
            .BookingRate = 0.15,
            .ProjectedCommission = 35,
            .AffiliateLink = "https://affiliate.kayak.com/flights/NYC-LAX?ref=eq12",
            .Type = "Flight"
        })
        
        deals.Add(New TravelDeal With {
            .DealId = "FLIGHT_ORD_MIA_002",
            .Title = "Chicago → Miami",
            .Destination = "Miami",
            .Departure = "Chicago",
            .StartDate = DateTime.Now.AddDays(5),
            .EndDate = DateTime.Now.AddDays(12),
            .OriginalPrice = 380,
            .DiscountedPrice = 215,
            .Discount = 43,
            .SavingsAmount = 165,
            .Description = "Beach getaway to Miami with amazing deals on flights",
            .BookingRate = 0.18,
            .ProjectedCommission = 40,
            .AffiliateLink = "https://affiliate.kayak.com/flights/ORD-MIA?ref=eq12",
            .Type = "Flight"
        })
        
        Return deals
    End Function
    
    Private Function ScanHotelPrices() As List(Of TravelDeal)
        Dim deals As New List(Of TravelDeal)
        
        ' Scan hotel booking sites
        ' In production, call Booking.com, Expedia, Hotels.com API
        
        deals.Add(New TravelDeal With {
            .DealId = "HOTEL_CANCUN_003",
            .Title = "Cancun All-Inclusive Resort",
            .Destination = "Cancun",
            .Departure = "Cancun",
            .StartDate = DateTime.Now.AddDays(10),
            .EndDate = DateTime.Now.AddDays(17),
            .OriginalPrice = 1200,
            .DiscountedPrice = 840,
            .Discount = 30,
            .SavingsAmount = 360,
            .Description = "5-star beachfront resort with all meals and activities included",
            .BookingRate = 0.12,
            .ProjectedCommission = 85,
            .AffiliateLink = "https://affiliate.booking.com/hotels/cancun?ref=eq12",
            .Type = "Hotel"
        })
        
        Return deals
    End Function
    
    Private Function ScoreDeals(deals As List(Of TravelDeal)) As IOrderedEnumerable(Of TravelDeal)
        ' Score deals by commission opportunity + booking conversion potential
        Return deals.OrderByDescending(Function(d) d.ProjectedCommission * d.BookingRate)
    End Function
    
    Private Function GetCssStyles() As String
        Return "
<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f5f5f5;
    color: #333;
    line-height: 1.6;
}
.hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 40px 20px;
    text-align: center;
}
.hero h1 {
    font-size: 2.5em;
    margin-bottom: 10px;
}
.badge {
    display: inline-block;
    background: rgba(255,255,255,0.3);
    padding: 8px 20px;
    border-radius: 20px;
    font-weight: bold;
}
.content {
    max-width: 600px;
    margin: 40px auto;
    background: white;
    padding: 40px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
.content h2 {
    color: #667eea;
    margin-bottom: 20px;
}
.pricing {
    background: #f9f9f9;
    padding: 20px;
    border-radius: 8px;
    margin: 20px 0;
    border-left: 4px solid #667eea;
}
.price-row {
    display: flex;
    justify-content: space-between;
    margin: 10px 0;
    font-size: 1.1em;
}
.strike {
    text-decoration: line-through;
    color: #999;
}
.highlight {
    color: #27ae60;
    font-weight: bold;
    font-size: 1.3em;
}
.save {
    color: #e74c3c;
    font-weight: bold;
    font-size: 1.3em;
}
.itinerary {
    margin: 30px 0;
    padding: 20px;
    background: #f0f7ff;
    border-radius: 8px;
}
.cta {
    text-align: center;
    margin: 30px 0;
}
.btn {
    display: inline-block;
    padding: 15px 40px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: bold;
    font-size: 1.1em;
    transition: all 0.3s ease;
}
.btn-primary {
    background: #667eea;
    color: white;
}
.btn-primary:hover {
    background: #764ba2;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(102,126,234,0.4);
}
.social-proof {
    text-align: center;
    color: #666;
    font-size: 0.95em;
    margin-top: 20px;
}
</style>
"
    End Function
End Class

Public Class TravelDeal
    Public Property DealId As String
    Public Property Title As String
    Public Property Destination As String
    Public Property Departure As String
    Public Property StartDate As DateTime
    Public Property EndDate As DateTime
    Public Property OriginalPrice As Double
    Public Property DiscountedPrice As Double
    Public Property Discount As Integer ' Percentage
    Public Property SavingsAmount As Double
    Public Property Description As String
    Public Property Type As String ' Flight, Hotel, Package
    Public Property BookingRate As Double
    Public Property ProjectedCommission As Double
    Public Property AffiliateLink As String
End Class
