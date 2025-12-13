' QuickStart.vb - One-shot example for EQ12 Props system
' Run with: dotnet fsi QuickStart.vb
' Or compile: vbc QuickStart.vb /r:System.Data.dll

Imports System
Imports System.Data.SqlClient

Module QuickStart
    
    Sub Main()
        Console.WriteLine("═══════════════════════════════════════════")
        Console.WriteLine("  EQ12 Props - Quick Start Example")
        Console.WriteLine("═══════════════════════════════════════════")
        Console.WriteLine()
        
        ' Example 1: Convert American odds to probability
        Console.WriteLine("Example 1: Odds Conversion")
        Console.WriteLine("───────────────────────────────────────────")
        Dim odds1 = -110  ' Typical favorite
        Dim odds2 = +150  ' Typical underdog
        
        Dim prob1 = AmericanToImplProb(odds1)
        Dim prob2 = AmericanToImplProb(odds2)
        
        Console.WriteLine($"Odds {odds1:+0;-0} → Implied Prob: {prob1*100:F2}%")
        Console.WriteLine($"Odds {odds2:+0;-0} → Implied Prob: {prob2*100:F2}%")
        Console.WriteLine()
        
        ' Example 2: Calculate expected value
        Console.WriteLine("Example 2: Expected Value Calculation")
        Console.WriteLine("───────────────────────────────────────────")
        Dim trueProb = 0.60       ' We think 60% chance
        Dim impliedProb = prob1   ' Book implies 52.4%
        Dim stake = 100.0
        
        Dim ev = EVPerLeg(trueProb, odds1, stake)
        Dim edge = EdgePercent(trueProb, impliedProb)
        
        Console.WriteLine($"True Probability: {trueProb*100:F1}%")
        Console.WriteLine($"Implied Probability: {impliedProb*100:F1}%")
        Console.WriteLine($"Expected Value: ${ev:F2}")
        Console.WriteLine($"Edge: {edge:F2}%")
        Console.WriteLine()
        
        ' Example 3: Calculate parlay probability and odds
        Console.WriteLine("Example 3: Parlay Calculation")
        Console.WriteLine("───────────────────────────────────────────")
        Dim leg1Prob = 0.60
        Dim leg2Prob = 0.62
        Dim leg3Prob = 0.58
        Dim leg4Prob = 0.61
        
        Dim leg1Odds = -110
        Dim leg2Odds = -115
        Dim leg3Odds = +105
        Dim leg4Odds = -108
        
        Dim parlayProb = leg1Prob * leg2Prob * leg3Prob * leg4Prob
        Dim parlayDecOdds = AmericanToDecimal(leg1Odds) * AmericanToDecimal(leg2Odds) * _
                           AmericanToDecimal(leg3Odds) * AmericanToDecimal(leg4Odds)
        Dim parlayAmericanOdds = DecimalToAmericanOdds(parlayDecOdds)
        
        Console.WriteLine("4-Leg Parlay:")
        Console.WriteLine($"  Leg 1: {leg1Odds:+0;-0} ({leg1Prob*100:F1}%)")
        Console.WriteLine($"  Leg 2: {leg2Odds:+0;-0} ({leg2Prob*100:F1}%)")
        Console.WriteLine($"  Leg 3: {leg3Odds:+0;-0} ({leg3Prob*100:F1}%)")
        Console.WriteLine($"  Leg 4: {leg4Odds:+0;-0} ({leg4Prob*100:F1}%)")
        Console.WriteLine()
        Console.WriteLine($"Combined True Probability: {parlayProb*100:F2}%")
        Console.WriteLine($"Parlay Odds: {parlayAmericanOdds:+0;-0} (Decimal: {parlayDecOdds:F2})")
        Console.WriteLine()
        
        ' Example 4: Kelly Criterion stake sizing
        Console.WriteLine("Example 4: Kelly Stake Sizing")
        Console.WriteLine("───────────────────────────────────────────")
        Dim bankroll = 10000.0
        Dim kellyFraction = 0.25  ' Fractional Kelly (conservative)
        Dim avgCorrelation = 0.20  ' 20% average correlation
        
        Dim fullKelly = FullKellyStake(bankroll, parlayProb, parlayDecOdds)
        Dim fractionalKelly = FractionalKellyStake(bankroll, parlayProb, parlayDecOdds, kellyFraction)
        Dim corrAdjusted = CorrelationAdjustedKelly(fractionalKelly, avgCorrelation)
        Dim finalStake = Math.Min(corrAdjusted, bankroll * 0.05)  ' 5% cap
        
        Console.WriteLine($"Bankroll: ${bankroll:F2}")
        Console.WriteLine($"Full Kelly: ${fullKelly:F2} ({fullKelly/bankroll*100:F2}%)")
        Console.WriteLine($"Fractional Kelly (1/4): ${fractionalKelly:F2} ({fractionalKelly/bankroll*100:F2}%)")
        Console.WriteLine($"Correlation Adjusted: ${corrAdjusted:F2} ({corrAdjusted/bankroll*100:F2}%)")
        Console.WriteLine($"Final Stake (with 5% cap): ${finalStake:F2} ({finalStake/bankroll*100:F2}%)")
        Console.WriteLine()
        
        Dim potentialWin = finalStake * (parlayDecOdds - 1)
        Dim potentialPayout = finalStake * parlayDecOdds
        
        Console.WriteLine($"Risk: ${finalStake:F2}")
        Console.WriteLine($"Potential Win: ${potentialWin:F2}")
        Console.WriteLine($"Potential Payout: ${potentialPayout:F2}")
        Console.WriteLine()
        
        ' Example 5: Poisson probability for counting stats
        Console.WriteLine("Example 5: Poisson Probability (PTS)")
        Console.WriteLine("───────────────────────────────────────────")
        Dim avgPts = 24.5          ' Player averages 24.5 PPG
        Dim line = 26.5            ' Over/Under line
        
        Dim probOver = PoissonCumulativeOver(avgPts, line)
        Dim probUnder = 1.0 - probOver
        
        Console.WriteLine($"Player Average: {avgPts} PPG")
        Console.WriteLine($"Line: {line}")
        Console.WriteLine($"P(Over {line}): {probOver*100:F2}%")
        Console.WriteLine($"P(Under {line}): {probUnder*100:F2}%")
        Console.WriteLine()
        
        ' Example 6: No-vig odds calculation
        Console.WriteLine("Example 6: Remove Bookmaker Vig")
        Console.WriteLine("───────────────────────────────────────────")
        Dim overOdds = -115
        Dim underOdds = -105
        
        Dim overImplied = AmericanToImplProb(overOdds)
        Dim underImplied = AmericanToImplProb(underOdds)
        Dim totalImplied = overImplied + underImplied
        Dim vigPercent = (totalImplied - 1.0) * 100
        
        Dim noVigOver = overImplied / totalImplied
        Dim noVigUnder = underImplied / totalImplied
        
        Console.WriteLine($"Over {overOdds:+0;-0}: {overImplied*100:F2}% → No-Vig: {noVigOver*100:F2}%")
        Console.WriteLine($"Under {underOdds:+0;-0}: {underImplied*100:F2}% → No-Vig: {noVigUnder*100:F2}%")
        Console.WriteLine($"Bookmaker Vig: {vigPercent:F2}%")
        Console.WriteLine()
        
        Console.WriteLine("═══════════════════════════════════════════")
        Console.WriteLine("  All Examples Complete!")
        Console.WriteLine("═══════════════════════════════════════════")
        
    End Sub
    
    ' ═══════════════════════════════════════════════════════════
    ' Helper Functions (Simplified from PricingUtils.vb)
    ' ═══════════════════════════════════════════════════════════
    
    Function AmericanToImplProb(odds As Integer) As Double
        If odds > 0 Then
            Return 100.0 / (odds + 100.0)
        Else
            Return -odds / (-odds + 100.0)
        End If
    End Function
    
    Function AmericanToDecimal(odds As Integer) As Double
        If odds > 0 Then
            Return (odds / 100.0) + 1.0
        Else
            Return (100.0 / -odds) + 1.0
        End If
    End Function
    
    Function DecimalToAmericanOdds(decimalOdds As Double) As Integer
        If decimalOdds >= 2.0 Then
            Return CInt((decimalOdds - 1.0) * 100)
        Else
            Return CInt(-100 / (decimalOdds - 1.0))
        End If
    End Function
    
    Function EVPerLeg(trueProb As Double, americanOdds As Integer, stake As Double) As Double
        Dim decOdds = AmericanToDecimal(americanOdds)
        Dim profit = stake * (decOdds - 1)
        Dim lossProb = 1.0 - trueProb
        Return (trueProb * profit) - (lossProb * stake)
    End Function
    
    Function EdgePercent(trueProb As Double, impliedProb As Double) As Double
        Return ((trueProb - impliedProb) / impliedProb) * 100
    End Function
    
    Function FullKellyStake(bankroll As Double, trueProb As Double, decimalOdds As Double) As Double
        Dim b = decimalOdds - 1.0
        Dim p = trueProb
        Dim q = 1.0 - p
        Dim f = (b * p - q) / b
        Return Math.Max(0, bankroll * f)
    End Function
    
    Function FractionalKellyStake(bankroll As Double, trueProb As Double, decimalOdds As Double, fraction As Double) As Double
        Dim fullKelly = FullKellyStake(bankroll, trueProb, decimalOdds)
        Return fullKelly * fraction
    End Function
    
    Function CorrelationAdjustedKelly(baseStake As Double, avgCorrelation As Double) As Double
        ' Reduce stake proportionally to correlation
        ' Example: 20% correlation → 80% of base stake
        Return baseStake * (1.0 - avgCorrelation)
    End Function
    
    Function PoissonProbability(lambda As Double, k As Integer) As Double
        ' P(X = k) = (λ^k × e^(-λ)) / k!
        Dim numerator = Math.Pow(lambda, k) * Math.Exp(-lambda)
        Dim denominator = Factorial(k)
        Return numerator / denominator
    End Function
    
    Function PoissonCumulativeOver(lambda As Double, threshold As Double) As Double
        Dim k = CInt(Math.Floor(threshold))
        Dim cumulative = 0.0
        
        For i = 0 To k
            cumulative += PoissonProbability(lambda, i)
        Next
        
        Return 1.0 - cumulative  ' P(X > k)
    End Function
    
    Function Factorial(n As Integer) As Double
        If n <= 1 Then Return 1.0
        Dim result = 1.0
        For i = 2 To n
            result *= i
        Next
        Return result
    End Function
    
End Module
