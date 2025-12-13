Imports Xunit
Imports FluentAssertions
Imports EQ12.Core

Public Class PerformanceMetricsTests
    
    <Fact>
    Public Sub CalculateSharpeRatio_Should_HandleEmptyData()
        ' Arrange
        Dim returns = New Double() {}
        Dim riskFreeRate = 0.02
        
        ' Act
        Dim sharpe = PerformanceMetrics.CalculateSharpeRatio(returns, riskFreeRate)
        
        ' Assert
        sharpe.Should().Be(0.0)
    End Sub
    
    <Fact>
    Public Sub KellyCriterion_Should_CalculateCorrectStake()
        ' Arrange
        Dim winProbability = 0.55
        Dim odds = 2.0 ' -110 moneyline
        Dim bankroll = 1000.0
        
        ' Act
        Dim kellySuggestion = PerformanceMetrics.KellyCriterion(winProbability, odds, bankroll)
        
        ' Assert
        kellySuggestion.Should().BeGreaterThan(0)
        kellySuggestion.Should().BeLessThan(bankroll)
    End Sub
    
    <Fact>
    Public Sub CalculateROI_WithKnownValues()
        ' Arrange
        Dim startValue = 10000.0
        Dim endValue = 11200.0
        
        ' Act
        Dim roi = PerformanceMetrics.CalculateROI(startValue, endValue)
        
        ' Assert
        roi.Should().Be(0.12) ' 12% ROI
    End Sub

End Class
