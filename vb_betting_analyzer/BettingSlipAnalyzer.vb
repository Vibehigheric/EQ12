Imports System
Imports System.Collections.Generic
Imports System.Linq

' ============================================================================
' EQ12 BETTING SLIP ANALYZER - VB.NET CONSOLE APPLICATION
' ============================================================================
' Purpose: Analyze DraftKings/FanDuel SGP betting slips for risk and correlation
' Author: EQ12 Copilot Workspace Architect
' Date: 2025-11-27
' 
' Features:
'   - Risk scoring (leg count × variance × sport mixing penalty)
'   - Correlation scoring (same-game stacking rewards)
'   - Variance tagging (1.0 low → 3.0 high)
'   - Automated recommendation engine
'   - Multi-slip comparison
' ============================================================================

' Simple enums to keep things clean
Public Enum SportType
    NFL
    NCAAF
    NCAAB
End Enum

Public Enum MarketType
    Moneyline
    Spread
    AlternateSpread
    Receptions
    ReceivingYards
    RushingAttempts
    FieldGoals
End Enum

' Represents a single leg of a bet slip
Public Class BetLeg
    Public Property Description As String       ' e.g. "Noah Fant 2+ Receptions"
    Public Property Sport As SportType          ' NFL / NCAAF / NCAAB
    Public Property Market As MarketType        ' Moneyline, Receptions, etc.
    Public Property GameKey As String           ' e.g. "CIN@BAL 8:20PM"
    Public Property BaseVariance As Double      ' 1 = low, 3 = high

    Public Sub New(desc As String,
                   sport As SportType,
                   market As MarketType,
                   gameKey As String,
                   baseVariance As Double)
        Description = desc
        Sport = sport
        Market = market
        GameKey = gameKey
        BaseVariance = baseVariance
    End Sub
End Class

' Represents an entire SGP / slip
Public Class BetSlip
    Public Property Name As String
    Public Property Legs As List(Of BetLeg)

    Public Sub New(name As String)
        Me.Name = name
        Me.Legs = New List(Of BetLeg)()
    End Sub

    ' [Inference] Simple heuristic risk score:
    '   - More legs = higher risk
    '   - Higher average variance = higher risk
    '   - Mixing many sports = penalty
    Public Function RiskScore() As Double
        If Legs.Count = 0 Then Return Double.MaxValue

        Dim legCount As Integer = Legs.Count
        Dim avgVariance As Double = Legs.Average(Function(l) l.BaseVariance)

        ' sports used in this slip
        Dim sportCount As Integer = Legs.Select(Function(l) l.Sport).Distinct().Count()

        ' risk from legs and variance
        Dim score As Double = legCount * avgVariance

        ' penalty if multiple sports
        If sportCount > 1 Then
            score += (sportCount - 1) * 2.0
        End If

        Return score
    End Function

    ' [Inference] Correlation score:
    '   - More legs from same game = better correlation
    '   - Fewer unique games = higher score
    Public Function CorrelationScore() As Double
        If Legs.Count = 0 Then Return 0

        Dim groups = Legs.GroupBy(Function(l) l.GameKey)
        Dim uniqueGames As Integer = groups.Count()

        ' sum of (legs in game)^2 encourages stacking
        Dim stackScore As Double = groups.Sum(Function(g) Math.Pow(g.Count(), 2))

        ' normalize by total legs
        Dim normalized As Double = stackScore / Legs.Count

        ' small bonus if everything is from one sport
        Dim singleSport As Boolean = (Legs.Select(Function(l) l.Sport).Distinct().Count() = 1)
        If singleSport Then
            normalized += 1.0
        End If

        Return normalized
    End Function

    ' Get high variance legs (>= 2.5)
    Public Function HighVarianceLegs() As List(Of BetLeg)
        Return Legs.Where(Function(l) l.BaseVariance >= 2.5).ToList()
    End Function

    ' Calculate sport mixing penalty
    Public Function SportMixPenalty() As Double
        Dim sportCount As Integer = Legs.Select(Function(l) l.Sport).Distinct().Count()
        If sportCount > 1 Then Return (sportCount - 1) * 2.0 Else Return 0
    End Function
End Class

Module Program

    Sub Main()
        Console.WriteLine("=============================================================================")
        Console.WriteLine("EQ12 BETTING SLIP ANALYZER - VB.NET Edition")
        Console.WriteLine("=============================================================================")
        Console.WriteLine()

        ' ------------------------------------------------------------------
        ' Build Slip #1  (mixed NFL + NCAAF + NCAAB, 10 legs)
        ' ------------------------------------------------------------------
        Dim slip1 As New BetSlip("Slip 1 - Mixed Multi-Sport SGPx")

        ' NFL - CIN @ BAL
        slip1.Legs.Add(New BetLeg("Noah Fant 2+ Receptions",
                                  SportType.NFL,
                                  MarketType.Receptions,
                                  "CIN@BAL 8:20PM",
                                  2.0))

        ' NFL - KC @ DAL
        slip1.Legs.Add(New BetLeg("George Pickens 7+ Receptions",
                                  SportType.NFL,
                                  MarketType.Receptions,
                                  "KC@DAL 4:30PM",
                                  2.4))

        ' NCAAF - Navy @ Memphis (alt spread)
        slip1.Legs.Add(New BetLeg("Navy +14.5 Alternate Spread",
                                  SportType.NCAAF,
                                  MarketType.AlternateSpread,
                                  "NAVY@MEM 7:30PM",
                                  3.0))

        ' NCAAF - Michigan State ML
        slip1.Legs.Add(New BetLeg("Michigan State Moneyline",
                                  SportType.NCAAF,
                                  MarketType.Moneyline,
                                  "MSU@UNC 4:30PM",
                                  2.6))

        ' NCAAF - BYU ML
        slip1.Legs.Add(New BetLeg("BYU Moneyline",
                                  SportType.NCAAF,
                                  MarketType.Moneyline,
                                  "BYU@MIA 5:00PM",
                                  2.6))

        ' NCAAB - Santa Clara ML
        slip1.Legs.Add(New BetLeg("Santa Clara Moneyline",
                                  SportType.NCAAB,
                                  MarketType.Moneyline,
                                  "STL@SANTACLARA 7:00PM",
                                  2.8))

        ' NCAAB - Arkansas +10.5
        slip1.Legs.Add(New BetLeg("Arkansas +10.5 Spread",
                                  SportType.NCAAB,
                                  MarketType.Spread,
                                  "DUKE@ARK 8:00PM",
                                  2.9))

        ' NCAAB - Dayton ML
        slip1.Legs.Add(New BetLeg("Dayton Moneyline",
                                  SportType.NCAAB,
                                  MarketType.Moneyline,
                                  "GTOWN@DAYTON 7:30PM",
                                  2.5))

        ' NFL - GB @ DET player props
        slip1.Legs.Add(New BetLeg("Jameson Williams 60+ Receiving Yards",
                                  SportType.NFL,
                                  MarketType.ReceivingYards,
                                  "GB@DET 1:00PM",
                                  2.5))

        slip1.Legs.Add(New BetLeg("Christian Watson 4+ Receptions",
                                  SportType.NFL,
                                  MarketType.Receptions,
                                  "GB@DET 1:00PM",
                                  2.4))

        ' ------------------------------------------------------------------
        ' Build Slip #2  (NFL-only, 2 games, 8 legs - CORRELATED)
        ' ------------------------------------------------------------------
        Dim slip2 As New BetSlip("Slip 2 - NFL Correlated SGP")

        ' CIN @ BAL (4 legs stacked)
        slip2.Legs.Add(New BetLeg("Andrei Iosivas 3+ Receptions",
                                  SportType.NFL,
                                  MarketType.Receptions,
                                  "CIN@BAL 8:20PM",
                                  2.3))

        slip2.Legs.Add(New BetLeg("Zay Flowers 4+ Receptions",
                                  SportType.NFL,
                                  MarketType.Receptions,
                                  "CIN@BAL 8:20PM",
                                  2.0))

        slip2.Legs.Add(New BetLeg("Derrick Henry 16+ Rushing Attempts",
                                  SportType.NFL,
                                  MarketType.RushingAttempts,
                                  "CIN@BAL 8:20PM",
                                  1.8))

        slip2.Legs.Add(New BetLeg("Over 2 First-Half Field Goals (CIN@BAL)",
                                  SportType.NFL,
                                  MarketType.FieldGoals,
                                  "CIN@BAL 8:20PM",
                                  1.7))

        ' GB @ DET (4 legs stacked)
        slip2.Legs.Add(New BetLeg("Christian Watson 3+ Receptions",
                                  SportType.NFL,
                                  MarketType.Receptions,
                                  "GB@DET 1:00PM",
                                  2.0))

        slip2.Legs.Add(New BetLeg("Jameson Williams 3+ Receptions",
                                  SportType.NFL,
                                  MarketType.Receptions,
                                  "GB@DET 1:00PM",
                                  2.0))

        slip2.Legs.Add(New BetLeg("Jahmyr Gibbs 50+ Rushing Yards",
                                  SportType.NFL,
                                  MarketType.RushingAttempts,
                                  "GB@DET 1:00PM",
                                  1.9))

        slip2.Legs.Add(New BetLeg("Over 2 First-Half Field Goals (GB@DET)",
                                  SportType.NFL,
                                  MarketType.FieldGoals,
                                  "GB@DET 1:00PM",
                                  1.7))

        ' ------------------------------------------------------------------
        ' Compare slips
        ' ------------------------------------------------------------------
        Dim slips = New List(Of BetSlip) From {slip1, slip2}

        For Each s In slips
            Console.WriteLine("=============================================================================")
            Console.WriteLine(s.Name)
            Console.WriteLine("=============================================================================")
            Console.WriteLine("Total Legs: " & s.Legs.Count)
            Console.WriteLine("Risk Score (lower is better): " & s.RiskScore().ToString("0.00"))
            Console.WriteLine("Correlation Score (higher is better): " & s.CorrelationScore().ToString("0.00"))
            Console.WriteLine("Sport Mix Penalty: " & s.SportMixPenalty().ToString("0.00"))
            Console.WriteLine()

            ' Show high variance legs
            Dim hvLegs = s.HighVarianceLegs()
            If hvLegs.Count > 0 Then
                Console.WriteLine("HIGH VARIANCE LEGS (>= 2.5):")
                For Each leg In hvLegs
                    Console.WriteLine("  [!] " & leg.Description & " (Variance: " & leg.BaseVariance & ")")
                Next
                Console.WriteLine()
            End If

            Console.WriteLine("LEG BREAKDOWN:")
            For Each leg In s.Legs
                Dim riskIndicator As String = ""
                If leg.BaseVariance >= 2.5 Then
                    riskIndicator = " [HIGH RISK]"
                ElseIf leg.BaseVariance >= 2.0 Then
                    riskIndicator = " [MEDIUM]"
                Else
                    riskIndicator = " [SAFE]"
                End If

                Console.WriteLine("  - " & leg.Description & "  [" & leg.GameKey & "]" & riskIndicator)
            Next
            Console.WriteLine()
        Next

        ' ------------------------------------------------------------------
        ' RECOMMENDATION ENGINE
        ' ------------------------------------------------------------------
        Console.WriteLine("=============================================================================")
        Console.WriteLine("RECOMMENDATION ENGINE")
        Console.WriteLine("=============================================================================")
        Console.WriteLine()

        ' choose a winner using a simple combined metric
        ' [Inference] We reward correlation and penalize risk.
        Dim bestSlip As BetSlip = slips _
            .OrderByDescending(Function(s) s.CorrelationScore() - (s.RiskScore() / 10.0)) _
            .First()

        Console.WriteLine("RECOMMENDED SLIP TO PLAY TODAY:")
        Console.WriteLine(">>> " & bestSlip.Name)
        Console.WriteLine()
        Console.WriteLine("WHY THIS SLIP?")
        Console.WriteLine("  - Risk Score: " & bestSlip.RiskScore().ToString("0.00") & " (lower is better)")
        Console.WriteLine("  - Correlation Score: " & bestSlip.CorrelationScore().ToString("0.00") & " (higher is better)")
        Console.WriteLine("  - Sport Mix Penalty: " & bestSlip.SportMixPenalty().ToString("0.00"))
        Console.WriteLine()

        ' Final verdict
        Dim totalRisk = bestSlip.RiskScore() + bestSlip.SportMixPenalty()
        If totalRisk > 25 Then
            Console.WriteLine("[VERDICT] DO NOT PLAY - Too much variance. Consider removing high-risk legs.")
        ElseIf totalRisk > 18 Then
            Console.WriteLine("[VERDICT] RISKY - Playable but remove at least 2 high-variance legs.")
        Else
            Console.WriteLine("[VERDICT] GOOD BET - Well-correlated, acceptable risk profile.")
        End If

        Console.WriteLine()
        Console.WriteLine("=============================================================================")
        Console.WriteLine("Press any key to exit...")
        Console.ReadKey()
    End Sub

End Module
