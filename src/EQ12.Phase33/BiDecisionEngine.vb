Imports System.Data.SQLite
Imports System.IO

''' <summary>
''' BI DECISION ENGINE - Intelligent opportunity ranking
''' Analyzes KPIs, conversions, drift, market conditions
''' Generates ranked top 10 daily moves with confidence scores
''' </summary>
Public Class BiDecisionEngine
    Private _dataRoot As String
    Private _dbPath As String
    Private _logger As Logger
    
    Public Sub New(dataRoot As String)
        _dataRoot = dataRoot
        _dbPath = Path.Combine(dataRoot, "logs", "eq12_memory.db")
        _logger = New Logger(dataRoot)
    End Sub
    
    ''' <summary>
    ''' MAIN DECISION ENGINE - Generate top 10 moves for today
    ''' </summary>
    Public Function GenerateTopMoves(kpi As KpiSnapshot, conversions As ConversionAnalysis, drift As DriftStatus) As List(Of NextMove)
        Try
            _logger.Log("[BI-ENGINE] Analyzing all data sources...")
            
            Dim opportunities As New List(Of Opportunity)
            
            ' Analyze ML opportunities
            opportunities.AddRange(AnalyzeMlOpportunities(drift))
            
            ' Analyze conversion opportunities
            opportunities.AddRange(AnalyzeConversionOpportunities(conversions))
            
            ' Analyze pricing opportunities (Turo)
            opportunities.AddRange(AnalyzePricingOpportunities())
            
            ' Analyze content opportunities (CBD, Travel)
            opportunities.AddRange(AnalyzeContentOpportunities())
            
            ' Analyze sports betting opportunities
            opportunities.AddRange(AnalyzeSportsOpportunities(kpi))
            
            ' Analyze credit opportunities
            opportunities.AddRange(AnalyzeCreditOpportunities())
            
            ' Analyze affiliate opportunities
            opportunities.AddRange(AnalyzeAffiliateOpportunities())
            
            ' Score and rank all opportunities
            Dim ranked = ScoreAndRankOpportunities(opportunities)
            
            ' Convert to NextMove objects
            Dim moves = ConvertToNextMoves(ranked.Take(10).ToList())
            
            ' Persist to database
            PersistNextMoves(moves)
            
            _logger.Log($"[BI-ENGINE] Generated {moves.Count} top moves | #1: {moves.FirstOrDefault()?.Title}")
            
            Return moves
        Catch ex As Exception
            _logger.LogError($"[BI-ENGINE] Failed: {ex.Message}")
            Return New List(Of NextMove)
        End Try
    End Function
    
    ' ═══════════════════════════════════════════════════════════
    ' OPPORTUNITY ANALYSIS BY CATEGORY
    ' ═══════════════════════════════════════════════════════════
    
    Private Function AnalyzeMlOpportunities(drift As DriftStatus) As List(Of Opportunity)
        Dim opps As New List(Of Opportunity)
        
        If drift.MaxPsi >= 0.25 Then
            opps.Add(New Opportunity With {
                .Category = "ML",
                .Title = "CRITICAL: Retrain model (high drift)",
                .Description = $"PSI at {drift.MaxPsi:F3} - model accuracy degrading",
                .Action = "RUN train_model_production.py --retrain",
                .ProjectedRevenue = 0,
                .ProjectedCostSavings = 2500,
                .ConfidenceScore = 0.98,
                .AutoExecutable = True,
                .ImpactScore = 9.5,
                .UrgencyScore = 10.0
            })
        ElseIf drift.MaxPsi >= 0.10 Then
            opps.Add(New Opportunity With {
                .Category = "ML",
                .Title = "Moderate drift detected - schedule retrain",
                .Description = $"PSI at {drift.MaxPsi:F3} - monitor closely",
                .Action = "SCHEDULE train_model_production.py +3 days",
                .ProjectedRevenue = 0,
                .ProjectedCostSavings = 1200,
                .ConfidenceScore = 0.75,
                .AutoExecutable = False,
                .ImpactScore = 6.0,
                .UrgencyScore = 5.0
            })
        End If
        
        Return opps
    End Function
    
    Private Function AnalyzeConversionOpportunities(conversions As ConversionAnalysis) As List(Of Opportunity)
        Dim opps As New List(Of Opportunity)
        
        For Each funnel In conversions.FunnelMetrics.OrderByDescending(Function(f) f.ROI).Take(3)
            If funnel.ROI > 0.15 Then
                opps.Add(New Opportunity With {
                    .Category = funnel.Funnel,
                    .Title = $"Scale {funnel.Funnel} funnel (high ROI)",
                    .Description = $"ROI: {funnel.ROI:P1}, Conversion: {funnel.ConversionRate:P1}",
                    .Action = $"INCREASE {funnel.Funnel} budget +25%",
                    .ProjectedRevenue = 1250 * funnel.ROI,
                    .ProjectedCostSavings = 0,
                    .ConfidenceScore = 0.82,
                    .AutoExecutable = False,
                    .ImpactScore = 7.5,
                    .UrgencyScore = 6.0
                })
            ElseIf funnel.ROI < 0.05 Then
                opps.Add(New Opportunity With {
                    .Category = funnel.Funnel,
                    .Title = $"Optimize {funnel.Funnel} funnel (low ROI)",
                    .Description = $"ROI: {funnel.ROI:P1}, CPA too high: ${funnel.CPA:F0}",
                    .Action = $"AUDIT {funnel.Funnel} CTA, landing page, pricing",
                    .ProjectedRevenue = 0,
                    .ProjectedCostSavings = 800,
                    .ConfidenceScore = 0.65,
                    .AutoExecutable = False,
                    .ImpactScore = 5.5,
                    .UrgencyScore = 4.0
                })
            End If
        Next
        
        Return opps
    End Function
    
    Private Function AnalyzePricingOpportunities() As List(Of Opportunity)
        Dim opps As New List(Of Opportunity)
        
        ' Check Turo pricing engine recommendations
        Dim turoEngine As New TuroPricingEngine(_dataRoot)
        Dim vehicles = turoEngine.GetAllVehiclePrices()
        
        For Each vehicle In vehicles.Where(Function(v) Math.Abs(v.PriceChange) > 5).Take(2)
            Dim direction = If(vehicle.PriceChange > 0, "increase", "decrease")
            opps.Add(New Opportunity With {
                .Category = "Turo",
                .Title = $"{direction} {vehicle.Make} {vehicle.Model} price {Math.Abs(vehicle.PriceChange):P0}",
                .Description = $"Current: ${vehicle.CurrentPrice}, Optimal: ${vehicle.RecommendedPrice}",
                .Action = $"UPDATE turo_pricing SET daily_rate = {vehicle.RecommendedPrice} WHERE vehicle_id = '{vehicle.VehicleId}'",
                .ProjectedRevenue = vehicle.PriceChange * 22, ' 22 days/month booking
                .ProjectedCostSavings = 0,
                .ConfidenceScore = 0.78,
                .AutoExecutable = True,
                .ImpactScore = 6.8,
                .UrgencyScore = 7.0
            })
        Next
        
        Return opps
    End Function
    
    Private Function AnalyzeContentOpportunities() As List(Of Opportunity)
        Dim opps As New List(Of Opportunity)
        
        ' Check travel deals
        Dim travelEngine As New TravelDealOptimizer(_dataRoot)
        Dim deals = travelEngine.FindDailyDeals()
        
        If deals.Count > 0 Then
            Dim topDeal = deals.First()
            opps.Add(New Opportunity With {
                .Category = "Travel",
                .Title = $"Generate landing page: {topDeal.Title}",
                .Description = $"{topDeal.Discount}% off, ${topDeal.SavingsAmount} savings",
                .Action = $"RUN TravelDealOptimizer.GenerateDealPage('{topDeal.DealId}')",
                .ProjectedRevenue = topDeal.ProjectedCommission,
                .ProjectedCostSavings = 0,
                .ConfidenceScore = topDeal.BookingRate,
                .AutoExecutable = True,
                .ImpactScore = 5.2,
                .UrgencyScore = 8.0
            })
        End If
        
        ' Check CBD content needs
        opps.Add(New Opportunity With {
            .Category = "CBD",
            .Title = "Generate 3 new CBD pet product descriptions",
            .Description = "Inventory updated, need fresh SEO content",
            .Action = "RUN CbdPetFunnelBuilder.GenerateProductDescription(product_list)",
            .ProjectedRevenue = 450,
            .ProjectedCostSavings = 0,
            .ConfidenceScore = 0.68,
            .AutoExecutable = True,
            .ImpactScore = 4.5,
            .UrgencyScore = 3.0
        })
        
        Return opps
    End Function
    
    Private Function AnalyzeSportsOpportunities(kpi As KpiSnapshot) As List(Of Opportunity)
        Dim opps As New List(Of Opportunity)
        
        ' Check sports intelligence
        Dim sportsEngine As New SportsIntelligencePanel(_dataRoot)
        Dim performance = sportsEngine.GetPerformanceSummary()
        
        If performance.Success AndAlso performance.WinRate > 0.60 Then
            opps.Add(New Opportunity With {
                .Category = "Sports",
                .Title = "Increase bankroll allocation (high win rate)",
                .Description = $"Win rate: {performance.WinRate:P1}, ROI: {performance.Roi:P1}",
                .Action = "INCREASE bankroll allocation +15%",
                .ProjectedRevenue = kpi.BankrollBalance * 0.15 * performance.Roi,
                .ProjectedCostSavings = 0,
                .ConfidenceScore = 0.85,
                .AutoExecutable = False,
                .ImpactScore = 8.2,
                .UrgencyScore = 6.5
            })
        End If
        
        ' Check parlay opportunities
        Dim parlays = sportsEngine.OptimizeParlayConstruction(10.0, 4)
        If parlays.Success AndAlso parlays.AverageConfidence > 0.70 Then
            opps.Add(New Opportunity With {
                .Category = "Sports",
                .Title = $"Place {parlays.Legs.Count}-leg parlay (high confidence)",
                .Description = $"Total odds: {parlays.TotalOdds:F2}, Avg confidence: {parlays.AverageConfidence:P0}",
                .Action = $"PLACE parlay bet: {String.Join(", ", parlays.Legs.Select(Function(l) l.Selection))}",
                .ProjectedRevenue = parlays.PotentialProfit,
                .ProjectedCostSavings = 0,
                .ConfidenceScore = parlays.AverageConfidence,
                .AutoExecutable = False,
                .ImpactScore = 6.5,
                .UrgencyScore = 9.0
            })
        End If
        
        Return opps
    End Function
    
    Private Function AnalyzeCreditOpportunities() As List(Of Opportunity)
        Dim opps As New List(Of Opportunity)
        
        ' Check credit trajectory
        Dim creditEngine As New CreditTrajectorySimulator(_dataRoot)
        Dim trajectory = creditEngine.GetTrajectory(675, 3.5)
        
        If trajectory.Success Then
            Dim nextMilestone = trajectory.MilestoneTimeline.FirstOrDefault(Function(m) Not m.IsAchieved)
            If nextMilestone IsNot Nothing AndAlso nextMilestone.MonthsToReach <= 3 Then
                opps.Add(New Opportunity With {
                    .Category = "Credit",
                    .Title = $"Reach {nextMilestone.MilestoneName} in {nextMilestone.MonthsToReach} months",
                    .Description = $"Target score: {nextMilestone.TargetScore}, unlocks: business credit, merchant services",
                    .Action = "EXECUTE credit improvement plan (pay down utilization <30%)",
                    .ProjectedRevenue = 0,
                    .ProjectedCostSavings = 0,
                    .ConfidenceScore = 0.72,
                    .AutoExecutable = False,
                    .ImpactScore = 7.0,
                    .UrgencyScore = 5.0
                })
            End If
        End If
        
        Return opps
    End Function
    
    Private Function AnalyzeAffiliateOpportunities() As List(Of Opportunity)
        Dim opps As New List(Of Opportunity)
        
        ' Check attribution engine
        Dim attributionEngine As New ConversionAttributionEngine(_dataRoot)
        Dim channelRoi = attributionEngine.GetChannelRoi()
        
        For Each channel In channelRoi.Where(Function(c) c.Roi > 3.0).Take(2)
            opps.Add(New Opportunity With {
                .Category = "Affiliate",
                .Title = $"Scale {channel.Channel} channel (ROI: {channel.Roi:F1}x)",
                .Description = $"Revenue: ${channel.Revenue:F0}, Spend: ${channel.Spend:F0}",
                .Action = $"INCREASE {channel.Channel} budget +30%",
                .ProjectedRevenue = channel.Spend * 0.30 * channel.Roi,
                .ProjectedCostSavings = 0,
                .ConfidenceScore = 0.80,
                .AutoExecutable = False,
                .ImpactScore = 7.8,
                .UrgencyScore = 6.0
            })
        Next
        
        Return opps
    End Function
    
    ' ═══════════════════════════════════════════════════════════
    ' SCORING & RANKING
    ' ═══════════════════════════════════════════════════════════
    
    Private Function ScoreAndRankOpportunities(opportunities As List(Of Opportunity)) As IOrderedEnumerable(Of Opportunity)
        For Each opp In opportunities
            ' Composite score = (Impact × Urgency × Confidence) + Revenue weight
            Dim revenueWeight = Math.Min(opp.ProjectedRevenue / 1000.0, 5.0) ' Cap at +5 points
            Dim savingsWeight = Math.Min(opp.ProjectedCostSavings / 500.0, 3.0) ' Cap at +3 points
            
            opp.CompositeScore = (opp.ImpactScore * opp.UrgencyScore * opp.ConfidenceScore) + revenueWeight + savingsWeight
        Next
        
        Return opportunities.OrderByDescending(Function(o) o.CompositeScore)
    End Function
    
    Private Function ConvertToNextMoves(opportunities As List(Of Opportunity)) As List(Of NextMove)
        Dim moves As New List(Of NextMove)
        Dim priority = 1
        
        For Each opp In opportunities
            moves.Add(New NextMove With {
                .Priority = priority,
                .Category = opp.Category,
                .Title = opp.Title,
                .Description = opp.Description,
                .Action = opp.Action,
                .AutoExecutable = opp.AutoExecutable,
                .ProjectedRevenue = opp.ProjectedRevenue,
                .ConfidenceScore = opp.ConfidenceScore
            })
            priority += 1
        Next
        
        Return moves
    End Function
    
    Private Sub PersistNextMoves(moves As List(Of NextMove))
        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()
                
                ' Clear existing moves for today
                Dim delCmd = conn.CreateCommand()
                delCmd.CommandText = "DELETE FROM next_moves WHERE move_date = date('now')"
                delCmd.ExecuteNonQuery()
                
                ' Insert new moves
                For Each move In moves
                    Dim insCmd = conn.CreateCommand()
                    insCmd.CommandText = "INSERT INTO next_moves (move_date, priority, category, title, description, action, auto_executable, projected_revenue, confidence_score) VALUES (date('now'), @priority, @category, @title, @description, @action, @auto, @revenue, @confidence)"
                    
                    insCmd.Parameters.AddWithValue("@priority", move.Priority)
                    insCmd.Parameters.AddWithValue("@category", move.Category)
                    insCmd.Parameters.AddWithValue("@title", move.Title)
                    insCmd.Parameters.AddWithValue("@description", move.Description)
                    insCmd.Parameters.AddWithValue("@action", move.Action)
                    insCmd.Parameters.AddWithValue("@auto", move.AutoExecutable)
                    insCmd.Parameters.AddWithValue("@revenue", move.ProjectedRevenue)
                    insCmd.Parameters.AddWithValue("@confidence", move.ConfidenceScore)
                    
                    insCmd.ExecuteNonQuery()
                Next
            End Using
        Catch ex As Exception
            _logger.LogError($"[BI-ENGINE] PersistNextMoves failed: {ex.Message}")
        End Try
    End Sub
End Class

''' <summary>
''' Internal opportunity class (before converting to NextMove)
''' </summary>
Public Class Opportunity
    Public Property Category As String
    Public Property Title As String
    Public Property Description As String
    Public Property Action As String
    Public Property ProjectedRevenue As Double
    Public Property ProjectedCostSavings As Double
    Public Property ConfidenceScore As Double
    Public Property AutoExecutable As Boolean
    Public Property ImpactScore As Double ' 0-10
    Public Property UrgencyScore As Double ' 0-10
    Public Property CompositeScore As Double ' Calculated
End Class
