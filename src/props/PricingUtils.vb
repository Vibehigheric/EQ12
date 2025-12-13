''' <summary>
''' Pricing utilities for odds conversion and EV calculation
''' </summary>
Public Module Pricing
    
    ''' <summary>
    ''' Convert American odds to implied probability
    ''' </summary>
    Public Function AmericanToImplProb(odds As Integer) As Double
        If odds > 0 Then
            Return 100.0 / (odds + 100.0)
        Else
            Return -odds / (-odds + 100.0)
        End If
    End Function
    
    ''' <summary>
    ''' Convert American odds to decimal odds
    ''' </summary>
    Public Function AmericanToDecimal(odds As Integer) As Double
        If odds > 0 Then
            Return 1.0 + (odds / 100.0)
        Else
            Return 1.0 + (100.0 / -odds)
        End If
    End Function
    
    ''' <summary>
    ''' Calculate Expected Value per leg
    ''' EV = (trueProb × profit) - (loseProb × stake)
    ''' </summary>
    Public Function EVPerLeg(trueProb As Double, odds As Integer) As Double
        Dim p = trueProb
        Dim q = 1.0 - p
        Dim decOdds = AmericanToDecimal(odds)
        
        ' Expected return per $1 stake
        Return (p * (decOdds - 1.0)) - (q * 1.0)
    End Function
    
    ''' <summary>
    ''' Calculate edge percentage
    ''' Edge = (trueProb - impliedProb) / impliedProb
    ''' </summary>
    Public Function EdgePercent(trueProb As Double, odds As Integer) As Double
        Dim implied = AmericanToImplProb(odds)
        If implied = 0 Then Return 0
        Return ((trueProb - implied) / implied) * 100.0
    End Function
    
    ''' <summary>
    ''' Check if bet has minimum required edge
    ''' </summary>
    Public Function HasMinEdge(trueProb As Double, odds As Integer, minEdgePct As Double) As Boolean
        Return EdgePercent(trueProb, odds) >= minEdgePct
    End Function
    
    ''' <summary>
    ''' Calculate no-vig (fair) odds from multiple books
    ''' </summary>
    Public Function CalculateNoVigOdds(overOdds As Integer, underOdds As Integer) As (Double, Double)
        Dim overProb = AmericanToImplProb(overOdds)
        Dim underProb = AmericanToImplProb(underOdds)
        Dim totalProb = overProb + underProb
        
        ' Remove vig and normalize
        Dim noVigOver = overProb / totalProb
        Dim noVigUnder = underProb / totalProb
        
        Return (noVigOver, noVigUnder)
    End Function
    
    ''' <summary>
    ''' Convert probability to American odds
    ''' </summary>
    Public Function ProbabilityToAmericanOdds(prob As Double) As Integer
        If prob >= 0.5 Then
            ' Favorite
            Return CInt(Math.Round(-100.0 * (prob / (1.0 - prob))))
        Else
            ' Underdog
            Return CInt(Math.Round(100.0 * ((1.0 - prob) / prob)))
        End If
    End Function
    
    ''' <summary>
    ''' Calculate Poisson probability for player props
    ''' Useful for counting stats (PTS, AST, REB, etc.)
    ''' </summary>
    Public Function PoissonProbability(lambda As Double, k As Integer) As Double
        Dim prob = Math.Exp(-lambda) * Math.Pow(lambda, k) / Factorial(k)
        Return prob
    End Function
    
    ''' <summary>
    ''' Calculate cumulative Poisson probability (for Over bets)
    ''' P(X > k) = 1 - P(X <= k)
    ''' </summary>
    Public Function PoissonCumulativeOver(lambda As Double, threshold As Double) As Double
        Dim k = CInt(Math.Floor(threshold))
        Dim cumulative = 0.0
        
        For i = 0 To k
            cumulative += PoissonProbability(lambda, i)
        Next
        
        Return 1.0 - cumulative
    End Function
    
    Private Function Factorial(n As Integer) As Long
        If n <= 1 Then Return 1
        Dim result As Long = 1
        For i = 2 To n
            result *= i
        Next
        Return result
    End Function
    
End Module
