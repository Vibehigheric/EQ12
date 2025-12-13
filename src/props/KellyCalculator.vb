''' <summary>
''' Kelly Criterion calculator for optimal bet sizing
''' </summary>
Public Module Kelly
    
    ''' <summary>
    ''' Calculate parlay true probability (assuming independence)
    ''' For correlated legs, use copula-adjusted probabilities
    ''' </summary>
    Public Function ParlayTrueProb(legs As IEnumerable(Of LegCandidate)) As Double
        Return legs.Aggregate(1.0, Function(acc, l) acc * l.TrueProb)
    End Function
    
    ''' <summary>
    ''' Calculate parlay decimal odds
    ''' </summary>
    Public Function ParlayDecimalOdds(legs As IEnumerable(Of LegCandidate)) As Double
        Return legs.Aggregate(1.0, Function(acc, l) acc * Pricing.AmericanToDecimal(l.Odds))
    End Function
    
    ''' <summary>
    ''' Calculate parlay American odds
    ''' </summary>
    Public Function ParlayAmericanOdds(legs As IEnumerable(Of LegCandidate)) As Integer
        Dim decOdds = ParlayDecimalOdds(legs)
        Dim prob = 1.0 / decOdds
        Return Pricing.ProbabilityToAmericanOdds(1.0 - prob)
    End Function
    
    ''' <summary>
    ''' Calculate optimal Kelly stake (full Kelly)
    ''' f* = (bp - q) / b
    ''' where b = decimal odds - 1, p = win prob, q = lose prob
    ''' </summary>
    Public Function FullKellyStake(bankroll As Double, winProb As Double, decimalOdds As Double) As Double
        Dim b = decimalOdds - 1.0
        Dim p = winProb
        Dim q = 1.0 - p
        
        ' Kelly fraction
        Dim k = ((b * p) - q) / b
        
        ' Don't bet if Kelly is negative (no edge)
        If k <= 0 Then Return 0.0
        
        Return k * bankroll
    End Function
    
    ''' <summary>
    ''' Calculate fractional Kelly stake (recommended: 1/4 or 1/2 Kelly)
    ''' More conservative to reduce variance
    ''' </summary>
    Public Function FractionalKellyStake(bankroll As Double, 
                                        winProb As Double, 
                                        decimalOdds As Double, 
                                        fraction As Double) As Double
        Dim fullKelly = FullKellyStake(bankroll, winProb, decimalOdds)
        Return Math.Max(0, fullKelly * fraction)
    End Function
    
    ''' <summary>
    ''' Calculate expected growth rate (for Kelly optimization)
    ''' </summary>
    Public Function ExpectedGrowthRate(winProb As Double, decimalOdds As Double, kellyFraction As Double) As Double
        Dim p = winProb
        Dim b = decimalOdds - 1.0
        Dim f = kellyFraction
        
        ' Expected log growth
        Return (p * Math.Log(1.0 + f * b)) + ((1.0 - p) * Math.Log(1.0 - f))
    End Function
    
    ''' <summary>
    ''' Calculate risk of ruin for given stake size
    ''' </summary>
    Public Function RiskOfRuin(bankroll As Double, 
                               stakeSize As Double, 
                               winProb As Double, 
                               decimalOdds As Double,
                               numBets As Integer) As Double
        Dim p = winProb
        Dim q = 1.0 - p
        Dim f = stakeSize / bankroll
        Dim b = decimalOdds - 1.0
        
        ' Simplified ROR calculation
        If p * (1.0 + b * f) < 1.0 Then
            ' Negative expectancy
            Return 1.0
        End If
        
        ' Approximate ROR for positive expectancy
        Dim a = q / p
        Dim ratio = (1.0 - f) / (1.0 + f * b)
        Return Math.Pow(ratio, numBets)
    End Function
    
    ''' <summary>
    ''' Adjust Kelly for correlation (reduce stake if legs are correlated)
    ''' </summary>
    Public Function CorrelationAdjustedKelly(baseKelly As Double, 
                                            avgCorrelation As Double) As Double
        ' Reduce stake proportionally to average pairwise correlation
        ' If avgRho = 0.4, reduce by 40%
        Dim adjustment = 1.0 - Math.Abs(avgCorrelation)
        Return baseKelly * adjustment
    End Function
    
    ''' <summary>
    ''' Calculate optimal Kelly for parlay with correlation adjustment
    ''' </summary>
    Public Function OptimalParlayStake(bankroll As Double,
                                      legs As IEnumerable(Of LegCandidate),
                                      avgCorrelation As Double,
                                      kellyFraction As Double) As Double
        Dim p = ParlayTrueProb(legs)
        Dim decOdds = ParlayDecimalOdds(legs)
        
        Dim baseStake = FractionalKellyStake(bankroll, p, decOdds, kellyFraction)
        Dim adjustedStake = CorrelationAdjustedKelly(baseStake, avgCorrelation)
        
        ' Never bet more than 5% of bankroll on a parlay (safety cap)
        Dim maxStake = bankroll * 0.05
        Return Math.Min(adjustedStake, maxStake)
    End Function
    
End Module
