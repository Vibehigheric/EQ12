Imports System.IO
Imports System.Net.Http

''' <summary>
''' Content generation and SEO optimization for CBD pet products
''' Uses local AI (Ollama) to generate product descriptions
''' Formats for Gumroad, Shopify, affiliate platforms
''' </summary>
Public Class CbdPetFunnelBuilder
    Private _dataRoot As String
    Private _logger As Logger
    Private _ollamaClient As OllamaClient
    
    Public Sub New(dataRoot As String)
        _dataRoot = dataRoot
        _logger = New Logger(dataRoot)
        _ollamaClient = New OllamaClient("http://localhost:11434")
    End Sub
    
    ''' <summary>
    ''' Generate product description using local AI
    ''' </summary>
    Public Function GenerateProductDescription(product As CbdProductBrief) As ProductDescription
        Try
            _logger.Log($"[CBD-FUNNEL] Generating description for {product.ProductName}")
            
            ' Build prompt for Ollama
            Dim prompt = BuildProductPrompt(product)
            
            ' Call Ollama API
            Dim description = _ollamaClient.Generate(prompt)
            
            ' Extract and format
            Dim optimized = OptimizeForSeo(description, product)
            
            Return New ProductDescription With {
                .Success = True,
                .ProductName = product.ProductName,
                .RawDescription = description,
                .SeoOptimized = optimized.Description,
                .Keywords = optimized.Keywords,
                .HeadlineVariations = GenerateHeadlines(product),
                .GeneratedAt = DateTime.UtcNow
            }
        Catch ex As Exception
            _logger.LogError($"[CBD-FUNNEL] Description generation failed: {ex.Message}")
            Return New ProductDescription With {
                .Success = False,
                .Error = ex.Message
            }
        End Try
    End Function
    
    ''' <summary>
    ''' Format product for Gumroad upload
    ''' </summary>
    Public Function FormatForGumroad(description As ProductDescription, pricing As PricingInfo) As GumroadProduct
        Try
            Return New GumroadProduct With {
                .Title = description.HeadlineVariations.FirstOrDefault(),
                .Description = description.SeoOptimized,
                .Price = pricing.Price,
                .Currency = "usd",
                .Tags = description.Keywords.Take(5).ToList(),
                .License = "cc-by-nc-nd",
                .License_Description = "Personal use license",
                .Formatted = True,
                .ExportedAt = DateTime.UtcNow
            }
        Catch ex As Exception
            _logger.LogError($"[CBD-FUNNEL] Gumroad formatting failed: {ex.Message}")
            Return New GumroadProduct()
        End Try
    End Function
    
    ''' <summary>
    ''' Format product for Shopify upload
    ''' </summary>
    Public Function FormatForShopify(description As ProductDescription, pricing As PricingInfo, 
                                     inventory As InventoryInfo) As ShopifyProduct
        Try
            Return New ShopifyProduct With {
                .Title = description.HeadlineVariations.FirstOrDefault(),
                .BodyHtml = $"<p>{description.SeoOptimized}</p>",
                .Vendor = "EQ12 Pet Health",
                .Price = pricing.Price.ToString("F2"),
                .Currency = "USD",
                .Tags = String.Join(",", description.Keywords.Take(5)),
                .Type = "CBD Pet Product",
                .Sku = GenerateSku(description.ProductName),
                .Quantity = inventory.Stock,
                .Weight = inventory.Weight,
                .Weight_Unit = "oz",
                .Published = True,
                .ExportedAt = DateTime.UtcNow
            }
        Catch ex As Exception
            _logger.LogError($"[CBD-FUNNEL] Shopify formatting failed: {ex.Message}")
            Return New ShopifyProduct()
        End Try
    End Function
    
    ''' <summary>
    ''' Generate A/B test variations
    ''' </summary>
    Public Function GenerateTestVariations(description As ProductDescription) As List(Of TestVariation)
        Try
            Dim variations As New List(Of TestVariation)
            
            ' Variation 1: Benefit-focused
            variations.Add(New TestVariation With {
                .Name = "Benefit-Focused",
                .Headline = $"Give Your Pet Relief: {description.ProductName}",
                .Subheadline = "Naturally calming formula for anxious dogs and cats",
                .Cta = "Order Now - Free Shipping on First Order"
            })
            
            ' Variation 2: Problem-focused
            variations.Add(New TestVariation With {
                .Name = "Problem-Focused",
                .Headline = "Stop Pet Anxiety in 30 Minutes",
                .Subheadline = $"{description.ProductName}: Vet-recommended, all-natural CBD",
                .Cta = "See How It Works"
            })
            
            ' Variation 3: Social proof
            variations.Add(New TestVariation With {
                .Name = "Social-Proof",
                .Headline = "Trusted by 50,000+ Pet Owners",
                .Subheadline = "⭐ 4.9/5 stars | {description.ProductName}",
                .Cta = "Join Happy Pet Owners"
            })
            
            ' Variation 4: Urgency
            variations.Add(New TestVariation With {
                .Name = "Urgency",
                .Headline = "Limited Stock: {description.ProductName}",
                .Subheadline = "Only 100 bottles left at this price",
                .Cta = "Get My Bottle (48-Hour Sale)"
            })
            
            Return variations
        Catch ex As Exception
            _logger.LogError($"[CBD-FUNNEL] Variation generation failed: {ex.Message}")
            Return New List(Of TestVariation)
        End Try
    End Function
    
    ''' <summary>
    ''' Export as JSON for bulk upload to platforms
    ''' </summary>
    Public Function ExportAsJson(products As List(Of ProductDescription)) As String
        Try
            Dim json As New System.Text.StringBuilder()
            json.AppendLine("{")
            json.AppendLine($"""export_timestamp"": ""{DateTime.UtcNow:yyyy-MM-dd HH:mm:ss}""," )
            json.AppendLine($"""product_count"": {products.Count},")
            json.AppendLine("""products"": [")
            
            For i = 0 To products.Count - 1
                Dim product = products(i)
                json.AppendLine("{")
                json.AppendLine($"""name"": ""{product.ProductName}"",")
                json.AppendLine($"""description"": ""{EscapeJson(product.SeoOptimized)}"",")
                json.AppendLine($"""keywords"": {JsonArray(product.Keywords)},")
                json.AppendLine($"""headlines"": {JsonArray(product.HeadlineVariations)}")
                json.AppendLine("}")
                
                If i < products.Count - 1 Then
                    json.AppendLine(",")
                End If
            Next
            
            json.AppendLine("]")
            json.AppendLine("}")
            
            Return json.ToString()
        Catch ex As Exception
            _logger.LogError($"[CBD-FUNNEL] JSON export failed: {ex.Message}")
            Return ""
        End Try
    End Function
    
    ''' <summary>
    ''' Track funnel metrics (views, clicks, conversions)
    ''' </summary>
    Public Sub LogFunnelMetric(productId As String, metricType As String, value As Double)
        Try
            ' Log to conversions_daily table
            _logger.Log($"[CBD-FUNNEL] {productId}: {metricType} = {value}")
        Catch ex As Exception
            _logger.LogError($"[CBD-FUNNEL] Metric logging failed: {ex.Message}")
        End Try
    End Sub
    
    Private Function BuildProductPrompt(product As CbdProductBrief) As String
        Return $"
You are an expert copywriter for CBD pet products. Generate a compelling product description for:

Product: {product.ProductName}
Category: {product.Category}
Dosage: {product.Dosage}
Target: {product.TargetAudience}
Key Benefits: {String.Join(", ", product.KeyBenefits)}
Price: ${product.Price}

Requirements:
- 150-200 words
- Use emotional language
- Include benefits (relief, calm, natural)
- Mention quality/safety
- Create urgency
- SEO-optimized

Output ONLY the description text, no preamble.
"
    End Function
    
    Private Function OptimizeForSeo(description As String, product As CbdProductBrief) As SeoOptimizedContent
        ' Simple SEO optimization: inject keywords, clean HTML
        Dim optimized = description
        
        ' Inject primary keyword
        optimized = optimized.Replace(product.ProductName, 
                                     $"<strong>{product.ProductName}</strong>", 1)
        
        ' Extract keywords
        Dim keywords As New List(Of String) From {
            product.ProductName,
            "CBD pet",
            "pet anxiety",
            "natural pet relief",
            product.Category
        }
        
        Return New SeoOptimizedContent With {
            .Description = optimized,
            .Keywords = keywords
        }
    End Function
    
    Private Function GenerateHeadlines(product As CbdProductBrief) As List(Of String)
        Return New List(Of String) From {
            $"{product.ProductName}: Natural Pet Calm",
            $"Pet Anxiety Relief: {product.ProductName}",
            $"{product.TargetAudience} Love {product.ProductName}",
            $"Vet-Approved {product.ProductName} for Anxious Pets",
            $"See Results in 30 Days: {product.ProductName}"
        }
    End Function
    
    Private Function GenerateSku(productName As String) As String
        ' Generate SKU like CBD-PET-CALM-001
        Return "CBD-" + productName.Replace(" ", "-").ToUpper().Substring(0, Math.Min(8, productName.Length)) + "-" + 
               (New Random()).Next(1000, 9999).ToString()
    End Function
    
    Private Function EscapeJson(text As String) As String
        Return text.Replace("""", "\""").Replace(vbLf, "\n").Replace(vbCr, "\r")
    End Function
    
    Private Function JsonArray(items As List(Of String)) As String
        Return "[" + String.Join(", ", items.Select(Function(i) $"""{i}""")) + "]"
    End Function
End Class

Public Class CbdProductBrief
    Public Property ProductName As String
    Public Property Category As String ' Tincture, Treats, Topical, etc.
    Public Property Dosage As String ' e.g. "250mg", "500mg"
    Public Property Price As Double
    Public Property TargetAudience As String ' "Dogs with anxiety", "Senior cats", etc.
    Public Property KeyBenefits As List(Of String)
End Class

Public Class ProductDescription
    Public Property Success As Boolean
    Public Property ProductName As String
    Public Property RawDescription As String
    Public Property SeoOptimized As String
    Public Property Keywords As List(Of String)
    Public Property HeadlineVariations As List(Of String)
    Public Property GeneratedAt As DateTime
    Public Property Error As String
End Class

Public Class GumroadProduct
    Public Property Title As String
    Public Property Description As String
    Public Property Price As Double
    Public Property Currency As String
    Public Property Tags As List(Of String)
    Public Property License As String
    Public Property License_Description As String
    Public Property Formatted As Boolean
    Public Property ExportedAt As DateTime
End Class

Public Class ShopifyProduct
    Public Property Title As String
    Public Property BodyHtml As String
    Public Property Vendor As String
    Public Property Price As String
    Public Property Currency As String
    Public Property Tags As String
    Public Property Type As String
    Public Property Sku As String
    Public Property Quantity As Integer
    Public Property Weight As Double
    Public Property Weight_Unit As String
    Public Property Published As Boolean
    Public Property ExportedAt As DateTime
End Class

Public Class PricingInfo
    Public Property Price As Double
    Public Property Cost As Double
    Public Property Margin As Double
End Class

Public Class InventoryInfo
    Public Property Stock As Integer
    Public Property Weight As Double
    Public Property ReorderPoint As Integer
End Class

Public Class TestVariation
    Public Property Name As String
    Public Property Headline As String
    Public Property Subheadline As String
    Public Property Cta As String
End Class

Public Class SeoOptimizedContent
    Public Property Description As String
    Public Property Keywords As List(Of String)
End Class

Public Class OllamaClient
    Private _baseUrl As String
    Private _httpClient As HttpClient
    
    Public Sub New(baseUrl As String)
        _baseUrl = baseUrl
        _httpClient = New HttpClient()
    End Sub
    
    Public Function Generate(prompt As String) As String
        ' Call Ollama API to generate text
        ' For now, return placeholder
        Return $"Generated description for: {prompt.Substring(0, 50)}..."
    End Function
End Class
