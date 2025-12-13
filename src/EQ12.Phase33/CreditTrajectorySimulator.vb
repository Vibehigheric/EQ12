Imports System.IO

''' <summary>
''' Credit score trajectory simulation
''' Projects path to key business milestones
''' 680 (business credit), 700 (merchant), 740 (USDA loans)
''' </summary>
Public Class CreditTrajectorySimulator
    Private _dataRoot As String
    Private _logger As Logger
    
    Public Sub New(dataRoot As String)
        _dataRoot = dataRoot
        _logger = New Logger(dataRoot)
    End Sub
    
    ''' <summary>
    ''' Get current credit trajectory and milestone timeline
    ''' </summary>
    Public Function GetTrajectory(currentScore As Integer, monthlyImprovement As Double) As TrajectoryProjection
        Try
            _logger.Log($"[CREDIT-SIM] Projecting from score {currentScore}")
            
            Dim projection As New TrajectoryProjection With {
                .CurrentScore = currentScore,
                .ProjectionDate = DateTime.UtcNow,
                .MonthlyImprovement = monthlyImprovement
            }
            
            ' Calculate months to each milestone
            projection.MilestoneTimeline = New List(Of MilestoneProjection) From {
                CalculateMilestone(currentScore, 680, monthlyImprovement, "Business Credit"),
                CalculateMilestone(currentScore, 700, monthlyImprovement, "Merchant Services"),
                CalculateMilestone(currentScore, 720, monthlyImprovement, "Premium Cards"),
                CalculateMilestone(currentScore, 740, monthlyImprovement, "USDA Loans"),
                CalculateMilestone(currentScore, 760, monthlyImprovement, "Excellent Rating"),
                CalculateMilestone(currentScore, 800, monthlyImprovement, "Perfect Score")
            }
            
            projection.Success = True
            
            Return projection
        Catch ex As Exception
            _logger.LogError($"[CREDIT-SIM] Trajectory calculation failed: {ex.Message}")
            Return New TrajectoryProjection With {
                .Success = False,
                .Error = ex.Message
            }
        End Try
    End Function
    
    ''' <summary>
    ''' Analyze what factors are hurting credit score
    ''' </summary>
    Public Function AnalyzeCreditFactors(currentScore As Integer) As CreditFactorAnalysis
        Try
            _logger.Log("[CREDIT-SIM] Analyzing credit factors")
            
            Dim analysis As New CreditFactorAnalysis With {
                .CurrentScore = currentScore,
                .Factors = New List(Of CreditFactor)
            }
            
            ' Payment history (35% weight)
            analysis.Factors.Add(New CreditFactor With {
                .Name = "Payment History",
                .Weight = 0.35,
                .Score = 95,
                .Status = "Excellent",
                .Impact = "Positive",
                .Recommendation = "Maintain on-time payments. Zero missed payments in last 12 months."
            })
            
            ' Credit utilization (30% weight)
            analysis.Factors.Add(New CreditFactor With {
                .Name = "Credit Utilization",
                .Weight = 0.30,
                .Score = 72,
                .Status = "Fair",
                .Impact = "Negative",
                .Recommendation = "Current utilization: 45%. Reduce to <30% to gain +15 points."
            })
            
            ' Length of history (15% weight)
            analysis.Factors.Add(New CreditFactor With {
                .Name = "Length of Credit History",
                .Weight = 0.15,
                .Score = 85,
                .Status = "Good",
                .Impact = "Neutral",
                .Recommendation = "Average account age: 6 years. Keep oldest accounts open."
            })
            
            ' Credit mix (10% weight)
            analysis.Factors.Add(New CreditFactor With {
                .Name = "Credit Mix",
                .Weight = 0.10,
                .Score = 80,
                .Status = "Good",
                .Impact = "Neutral",
                .Recommendation = "Have installment and revolving credit. Good diversity."
            })
            
            ' Hard inquiries (10% weight)
            analysis.Factors.Add(New CreditFactor With {
                .Name = "Hard Inquiries",
                .Weight = 0.10,
                .Score = 65,
                .Status = "Fair",
                .Impact = "Negative",
                .Recommendation = "3 hard inquiries in last 6 months. Limit new credit applications."
            })
            
            Return analysis
        Catch ex As Exception
            _logger.LogError($"[CREDIT-SIM] Factor analysis failed: {ex.Message}")
            Return New CreditFactorAnalysis With {
                .Success = False,
                .Error = ex.Message
            }
        End Try
    End Function
    
    ''' <summary>
    ''' Get action plan to reach target score
    ''' </summary>
    Public Function GetActionPlan(currentScore As Integer, targetScore As Integer) As ActionPlan
        Try
            _logger.Log($"[CREDIT-SIM] Building action plan: {currentScore} → {targetScore}")
            
            Dim plan As New ActionPlan With {
                .CurrentScore = currentScore,
                .TargetScore = targetScore,
                .Actions = New List(Of CreditAction)
            }
            
            ' Immediate actions (next 30 days)
            plan.Actions.Add(New CreditAction With {
                .Timeline = "Immediate (0-30 days)",
                .Action = "Pay down credit cards to <30% utilization",
                .ExpectedPointGain = 15,
                .Priority = "HIGH",
                .Difficulty = "Medium"
            })
            
            plan.Actions.Add(New CreditAction With {
                .Timeline = "Immediate (0-30 days)",
                .Action = "Dispute any errors on credit reports",
                .ExpectedPointGain = 5,
                .Priority = "HIGH",
                .Difficulty = "Low"
            })
            
            ' Short-term actions (30-90 days)
            plan.Actions.Add(New CreditAction With {
                .Timeline = "Short-term (30-90 days)",
                .Action = "Apply for 1 new business credit card (builder)",
                .ExpectedPointGain = 8,
                .Priority = "MEDIUM",
                .Difficulty = "Low"
            })
            
            plan.Actions.Add(New CreditAction With {
                .Timeline = "Short-term (30-90 days)",
                .Action = "Request credit limit increases (no hard inquiry)",
                .ExpectedPointGain = 10,
                .Priority = "MEDIUM",
                .Difficulty = "Low"
            })
            
            ' Long-term actions (90-180 days)
            plan.Actions.Add(New CreditAction With {
                .Timeline = "Long-term (90-180 days)",
                .Action = "Maintain perfect payment history",
                .ExpectedPointGain = 20,
                .Priority = "HIGH",
                .Difficulty = "Medium"
            })
            
            plan.Actions.Add(New CreditAction With {
                .Timeline = "Long-term (90-180 days)",
                .Action = "Build business credit profile",
                .ExpectedPointGain = 15,
                .Priority = "MEDIUM",
                .Difficulty = "High"
            })
            
            plan.TotalExpectedGain = plan.Actions.Sum(Function(a) a.ExpectedPointGain)
            plan.ProjectedTargetDate = DateTime.Now.AddDays(
                Math.Ceiling((targetScore - currentScore) / plan.Actions.Average(Function(a) a.ExpectedPointGain) * 30))
            
            Return plan
        Catch ex As Exception
            _logger.LogError($"[CREDIT-SIM] Action plan failed: {ex.Message}")
            Return New ActionPlan With {
                .Success = False,
                .Error = ex.Message
            }
        End Try
    End Function
    
    ''' <summary>
    ''' Get benefit unlock at each milestone score
    ''' </summary>
    Public Function GetMilestoneUnlocks() As List(Of MilestoneUnlock)
        Try
            Return New List(Of MilestoneUnlock) From {
                New MilestoneUnlock With {
                    .Score = 620,
                    .Milestone = "Entry Level",
                    .Benefits = "Basic credit cards, subprime auto loans",
                    .ApprovalRate = 0.40,
                    .AvgApr = 0.18
                },
                New MilestoneUnlock With {
                    .Score = 660,
                    .Milestone = "Fair Credit",
                    .Benefits = "Standard credit cards, FHA mortgage",
                    .ApprovalRate = 0.65,
                    .AvgApr = 0.12
                },
                New MilestoneUnlock With {
                    .Score = 680,
                    .Milestone = "Business Credit",
                    .Benefits = "D&B rating, business credit cards, equipment loans",
                    .ApprovalRate = 0.75,
                    .AvgApr = 0.10
                },
                New MilestoneUnlock With {
                    .Score = 700,
                    .Milestone = "Merchant Services",
                    .Benefits = "Credit card processing, lines of credit, vendor accounts",
                    .ApprovalRate = 0.85,
                    .AvgApr = 0.08
                },
                New MilestoneUnlock With {
                    .Score = 720,
                    .Milestone = "Prime Rate",
                    .Benefits = "Premium cards, investment loans, competitive rates",
                    .ApprovalRate = 0.90,
                    .AvgApr = 0.06
                },
                New MilestoneUnlock With {
                    .Score = 740,
                    .Milestone = "USDA Loans",
                    .Benefits = "USDA rural loans, SBA loans, best mortgage rates",
                    .ApprovalRate = 0.95,
                    .AvgApr = 0.04
                },
                New MilestoneUnlock With {
                    .Score = 760,
                    .Milestone = "Excellent",
                    .Benefits = "Jumbo loans, venture credit, private equity access",
                    .ApprovalRate = 0.98,
                    .AvgApr = 0.03
                },
                New MilestoneUnlock With {
                    .Score = 800,
                    .Milestone = "Perfect Score",
                    .Benefits = "All products available, best possible rates",
                    .ApprovalRate = 1.0,
                    .AvgApr = 0.02
                }
            }
        Catch ex As Exception
            _logger.LogError($"[CREDIT-SIM] Milestone unlocks failed: {ex.Message}")
            Return New List(Of MilestoneUnlock)
        End Try
    End Function
    
    ''' <summary>
    ''' Calculate funding capacity at different score levels
    ''' </summary>
    Public Function CalculateFundingCapacity(currentScore As Integer) As FundingCapacity
        Try
            Dim capacity As New FundingCapacity With {
                .CurrentScore = currentScore,
                .Projections = New List(Of FundingProjection)
            }
            
            ' Map score to borrowing capacity
            Dim scoreMapping = New Dictionary(Of Integer, Double) From {
                {620, 5000},
                {660, 15000},
                {700, 50000},
                {720, 100000},
                {740, 250000},
                {760, 500000},
                {800, 1000000}
            }
            
            For Each kvp In scoreMapping
                capacity.Projections.Add(New FundingProjection With {
                    .TargetScore = kvp.Key,
                    .EstimatedCapacity = kvp.Value,
                    .InterestRate = CalculateInterestRate(kvp.Key),
                    .ApprovalLikelihood = CalculateApproval(kvp.Key)
                })
            Next
            
            Return capacity
        Catch ex As Exception
            _logger.LogError($"[CREDIT-SIM] Funding capacity failed: {ex.Message}")
            Return New FundingCapacity With {
                .Success = False,
                .Error = ex.Message
            }
        End Try
    End Function
    
    Private Function CalculateMilestone(currentScore As Integer, targetScore As Integer, monthlyImprovement As Double, 
                                       name As String) As MilestoneProjection
        If currentScore >= targetScore Then
            Return New MilestoneProjection With {
                .MilestoneName = name,
                .TargetScore = targetScore,
                .MonthsToReach = 0,
                .ProjectedDate = DateTime.Now,
                .Status = "ACHIEVED",
                .IsAchieved = True
            }
        End If
        
        Dim monthsNeeded = Math.Ceiling((targetScore - currentScore) / monthlyImprovement)
        
        Return New MilestoneProjection With {
            .MilestoneName = name,
            .TargetScore = targetScore,
            .MonthsToReach = CInt(monthsNeeded),
            .ProjectedDate = DateTime.Now.AddMonths(CInt(monthsNeeded)),
            .Status = If(monthsNeeded <= 3, "SOON", If(monthsNeeded <= 12, "ATTAINABLE", "LONG-TERM")),
            .IsAchieved = False
        }
    End Function
    
    Private Function CalculateInterestRate(score As Integer) As Double
        ' Inverse relationship: higher score = lower rate
        Select Case score
            Case >= 800 : Return 0.02
            Case >= 760 : Return 0.03
            Case >= 740 : Return 0.04
            Case >= 720 : Return 0.06
            Case >= 700 : Return 0.08
            Case >= 680 : Return 0.10
            Case >= 660 : Return 0.12
            Case Else : Return 0.18
        End Select
    End Function
    
    Private Function CalculateApproval(score As Integer) As Double
        ' Approval likelihood
        Select Case score
            Case >= 800 : Return 1.0
            Case >= 760 : Return 0.98
            Case >= 740 : Return 0.95
            Case >= 720 : Return 0.90
            Case >= 700 : Return 0.85
            Case >= 680 : Return 0.75
            Case >= 660 : Return 0.65
            Case Else : Return 0.40
        End Select
    End Function
End Class

Public Class TrajectoryProjection
    Public Property Success As Boolean
    Public Property CurrentScore As Integer
    Public Property MonthlyImprovement As Double
    Public Property ProjectionDate As DateTime
    Public Property MilestoneTimeline As List(Of MilestoneProjection)
    Public Property Error As String
End Class

Public Class MilestoneProjection
    Public Property MilestoneName As String
    Public Property TargetScore As Integer
    Public Property MonthsToReach As Integer
    Public Property ProjectedDate As DateTime
    Public Property Status As String
    Public Property IsAchieved As Boolean
End Class

Public Class CreditFactorAnalysis
    Public Property Success As Boolean
    Public Property CurrentScore As Integer
    Public Property Factors As List(Of CreditFactor)
    Public Property Error As String
End Class

Public Class CreditFactor
    Public Property Name As String
    Public Property Weight As Double
    Public Property Score As Integer
    Public Property Status As String
    Public Property Impact As String
    Public Property Recommendation As String
End Class

Public Class ActionPlan
    Public Property Success As Boolean
    Public Property CurrentScore As Integer
    Public Property TargetScore As Integer
    Public Property Actions As List(Of CreditAction)
    Public Property TotalExpectedGain As Integer
    Public Property ProjectedTargetDate As DateTime
    Public Property Error As String
End Class

Public Class CreditAction
    Public Property Timeline As String
    Public Property Action As String
    Public Property ExpectedPointGain As Integer
    Public Property Priority As String
    Public Property Difficulty As String
End Class

Public Class MilestoneUnlock
    Public Property Score As Integer
    Public Property Milestone As String
    Public Property Benefits As String
    Public Property ApprovalRate As Double
    Public Property AvgApr As Double
End Class

Public Class FundingCapacity
    Public Property Success As Boolean
    Public Property CurrentScore As Integer
    Public Property Projections As List(Of FundingProjection)
    Public Property Error As String
End Class

Public Class FundingProjection
    Public Property TargetScore As Integer
    Public Property EstimatedCapacity As Double
    Public Property InterestRate As Double
    Public Property ApprovalLikelihood As Double
End Class
