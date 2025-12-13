' KellyCalculator.vb
' Manually created Kelly Criterion calculator for EQ12
' Implements standard Kelly Criterion formulas for optimal betting stakes

Imports System
Imports System.Data
Imports System.Data.SQLite

Public Class KellyCalculator

    Private ReadOnly dbWriter As DBWriter
    Private ReadOnly logger As Logger

    Public Sub New()
        dbWriter = New DBWriter()
        logger = New Logger("KellyCalculator")
        logger.Info("KellyCalculator initialized")
    End Sub

    Public Function CalculateKellyStake(bankroll As Double, americanOdds As Integer, winProbability As Double, fraction As Double) As KellyResult
        ' Kelly Criterion implementation: k = (b*p - (1-p)) / b
        Try
            Dim decimalOdds As Double = DecimalFromAmerican(americanOdds)
            Dim b As Double = decimalOdds - 1.0  ' Net odds (profit per unit staked)

            ' Full Kelly formula
            Dim kellyFull As Double = ((b * winProbability) - (1.0 - winProbability)) / b

            ' Apply fraction (quarter-kelly = 0.25, half-kelly = 0.5, etc)
            Dim kellyFraction As Double = kellyFull * fraction

            ' Calculate stake amount (never bet more than bankroll or negative amounts)
            Dim stakeAmount As Double = bankroll * Math.Max(0, Math.Min(kellyFraction, 1.0))

            ' Calculate edge
            Dim impliedProb As Double = 1.0 / decimalOdds
            Dim edge As Double = winProbability - impliedProb

            Dim result As New KellyResult With {
                .Bankroll = bankroll,
                .AmericanOdds = americanOdds,
                .DecimalOdds = decimalOdds,
                .WinProbability = winProbability,
                .ImpliedProbability = impliedProb,
                .Edge = edge,
                .KellyFull = kellyFull,
                .KellyFraction = kellyFraction,
                .Fraction = fraction,
                .StakeAmount = stakeAmount,
                .StakePercent = (stakeAmount / bankroll) * 100,
                .ExpectedValue = stakeAmount * edge,
                .Timestamp = DateTime.Now
            }

            ' Log to database
            LogKellyCalculation(result)

            logger.Info($"Kelly calculation: {stakeAmount:C} ({result.StakePercent:F2}%) for odds {americanOdds}, EV: {result.ExpectedValue:C}")
            Return result

        Catch ex As Exception
            logger.Error($"Error calculating Kelly stake: {ex.Message}")
            Return New KellyResult()
        End Try
    End Function

    Public Function CalculateUnitStake(bankroll As Double, unitPercent As Double, units As Double) As Double
        ' Unit-based staking system (alternative to Kelly)
        Try
            Dim unitSize As Double = bankroll * (unitPercent / 100.0)
            Dim stakeAmount As Double = unitSize * units

            ' Don't stake more than 10% of bankroll on any single bet
            Dim maxStake As Double = bankroll * 0.1
            stakeAmount = Math.Min(stakeAmount, maxStake)

            logger.Info($"Unit stake: {stakeAmount:C} ({units} units at {unitPercent:F1}%)")
            Return stakeAmount

        Catch ex As Exception
            logger.Error($"Error calculating unit stake: {ex.Message}")
            Return 0.0
        End Try
    End Function

    Public Function CalculateOptimalFraction(edge As Double, variance As Double, riskTolerance As Double) As Double
        ' Calculate optimal Kelly fraction based on edge, variance, and risk tolerance
        ' More conservative approach for real-world betting
        Try
            If edge <= 0 Then Return 0.0

            ' Base Kelly fraction
            Dim baseKelly As Double = edge / variance

            ' Apply risk tolerance (0.1 = very conservative, 1.0 = full Kelly)
            Dim adjustedKelly As Double = baseKelly * riskTolerance

            ' Cap at reasonable maximum (25% of bankroll)
            Return Math.Min(adjustedKelly, 0.25)

        Catch ex As Exception
            logger.Error($"Error calculating optimal fraction: {ex.Message}")
            Return 0.0
        End Try
    End Function

    Public Function ConvertOddsFormats(americanOdds As Integer) As OddsConversion
        ' Convert between different odds formats
        Try
            Dim decimal_odds As Double = DecimalFromAmerican(americanOdds)
            Dim fractional As String = DecimalToFractional(decimal_odds)
            Dim impliedProb As Double = 1.0 / decimal_odds

            Return New OddsConversion With {
                .American = americanOdds,
                .Decimal = decimal_odds,
                .Fractional = fractional,
                .ImpliedProbability = impliedProb,
                .ImpliedPercentage = impliedProb * 100
            }

        Catch ex As Exception
            logger.Error($"Error converting odds: {ex.Message}")
            Return New OddsConversion()
        End Try
    End Function

    Private Function DecimalFromAmerican(americanOdds As Integer) As Double
        ' Convert American odds to decimal odds
        If americanOdds > 0 Then
            Return (americanOdds / 100.0) + 1.0
        Else
            Return (100.0 / Math.Abs(americanOdds)) + 1.0
        End If
    End Function

    Private Function DecimalToFractional(decimalOdds As Double) As String
        ' Convert decimal odds to fractional (approximate)
        Try
            Dim numerator As Integer = CInt((decimalOdds - 1.0) * 100)
            Dim denominator As Integer = 100

            ' Simplify fraction
            Dim gcd As Integer = FindGCD(numerator, denominator)
            numerator \= gcd
            denominator \= gcd

            Return $"{numerator}/{denominator}"

        Catch
            Return "N/A"
        End Try
    End Function

    Private Function FindGCD(a As Integer, b As Integer) As Integer
        ' Find Greatest Common Divisor
        While b <> 0
            Dim temp As Integer = b
            b = a Mod b
            a = temp
        End While
        Return a
    End Function

    Private Sub LogKellyCalculation(result As KellyResult)
        ' Log to staking_log table
        Try
            Dim sql As String = "INSERT INTO staking_log (decimal_odds, american_odds, edge, p, kelly_full, kelly_fraction, stake, mode, bankroll_name, notes, github_source) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

            Dim notes As String = $"EV: {result.ExpectedValue:C}, Fraction: {result.Fraction}"

            dbWriter.ExecuteNonQuery(sql,
                result.DecimalOdds,
                result.AmericanOdds,
                result.Edge,
                result.WinProbability,
                result.KellyFull,
                result.KellyFraction,
                result.StakeAmount,
                "kelly",
                "Main",
                notes,
                "manual_kelly_calculator")

            ' Sync to BigQuery
            dbWriter.SyncToBigQuery("staking_log")

        Catch ex As Exception
            logger.Error($"Error logging Kelly calculation: {ex.Message}")
        End Try
    End Sub

    Public Function GetBankrollRecommendations(currentBalance As Double, recentPerformance As List(Of Double)) As BankrollAdvice
        ' Provide bankroll management recommendations
        Try
            Dim advice As New BankrollAdvice With {
                .CurrentBalance = currentBalance,
                .RecommendedUnitSize = currentBalance * 0.01, ' 1% units
                .MaxBetSize = currentBalance * 0.05, ' 5% max bet
                .StopLossLevel = currentBalance * 0.8, ' Stop at 20% loss
                .TargetBalance = currentBalance * 1.2 ' Target 20% growth
            }

            ' Adjust based on recent performance
            If recentPerformance.Count > 0 Then
                Dim avgReturn As Double = recentPerformance.Average()
                Dim volatility As Double = CalculateVolatility(recentPerformance)

                If volatility > 0.1 Then ' High volatility
                    advice.RecommendedUnitSize *= 0.5 ' Reduce unit size
                    advice.RiskAssessment = "High volatility detected - reduce unit sizes"
                ElseIf avgReturn > 0.05 Then ' Good performance
                    advice.RecommendedUnitSize *= 1.2 ' Slightly increase
                    advice.RiskAssessment = "Strong performance - slight increase in unit size"
                Else
                    advice.RiskAssessment = "Maintain current strategy"
                End If
            End If

            Return advice

        Catch ex As Exception
            logger.Error($"Error generating bankroll recommendations: {ex.Message}")
            Return New BankrollAdvice()
        End Try
    End Function

    Private Function CalculateVolatility(returns As List(Of Double)) As Double
        ' Calculate standard deviation of returns
        Try
            If returns.Count < 2 Then Return 0.0

            Dim mean As Double = returns.Average()
            Dim sumSquaredDiffs As Double = returns.Sum(Function(r) Math.Pow(r - mean, 2))

            Return Math.Sqrt(sumSquaredDiffs / (returns.Count - 1))

        Catch
            Return 0.0
        End Try
    End Function

End Class

Public Class KellyResult
    Public Property Bankroll As Double
    Public Property AmericanOdds As Integer
    Public Property DecimalOdds As Double
    Public Property WinProbability As Double
    Public Property ImpliedProbability As Double
    Public Property Edge As Double
    Public Property KellyFull As Double
    Public Property KellyFraction As Double
    Public Property Fraction As Double
    Public Property StakeAmount As Double
    Public Property StakePercent As Double
    Public Property ExpectedValue As Double
    Public Property Timestamp As DateTime

    Public ReadOnly Property IsPositiveEV As Boolean
        Get
            Return Edge > 0 AndAlso StakeAmount > 0
        End Get
    End Property

    Public ReadOnly Property RiskLevel As String
        Get
            If StakePercent > 10 Then Return "High"
            If StakePercent > 5 Then Return "Medium"
            Return "Low"
        End Get
    End Property
End Class

Public Class OddsConversion
    Public Property American As Integer
    Public Property Decimal As Double
    Public Property Fractional As String
    Public Property ImpliedProbability As Double
    Public Property ImpliedPercentage As Double
End Class

Public Class BankrollAdvice
    Public Property CurrentBalance As Double
    Public Property RecommendedUnitSize As Double
    Public Property MaxBetSize As Double
    Public Property StopLossLevel As Double
    Public Property TargetBalance As Double
    Public Property RiskAssessment As String
End Class
