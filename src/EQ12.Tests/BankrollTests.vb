Imports Xunit
Imports FluentAssertions
Imports EQ12.Core

Public Class BankrollTests
    
    <Fact>
    Public Sub Deposit_Should_IncreaseBalance()
        ' Arrange
        Dim bankroll = New EQ12.Core.BankrollManager(1000.0D)
        
        ' Act
        bankroll.Deposit(500.0, "Test deposit")
        
        ' Assert
        bankroll.CurrentBalance.Should().Be(1500.0)
    End Sub
    
    <Fact>
    Public Sub Withdrawal_Should_DecreaseBalance()
        ' Arrange
        Dim bankroll = New EQ12.Core.BankrollManager(1000.0D)
        
        ' Act
        bankroll.Withdraw(250.0, "Test withdrawal")
        
        ' Assert
        bankroll.CurrentBalance.Should().Be(750.0)
    End Sub
    
    <Fact>
    Public Sub CalculateROI_Should_ReturnCorrectValue()
        ' Arrange
        Dim bankroll = New EQ12.Core.BankrollManager(1000.0D)
        bankroll.RecordWin(100.0)
        
        ' Act
        Dim roi = bankroll.CalculateROI()
        
        ' Assert
        roi.Should().Be(0.1) ' 10% ROI
    End Sub
    
    <Fact>
    Public Sub MaxDrawdown_Should_CalculateCorrectly()
        ' Arrange
        Dim bankroll = New EQ12.Core.BankrollManager(10000.0D)
        bankroll.RecordWin(5000.0)    ' Peak at 15000
        bankroll.RecordLoss(10000.0)  ' Drop to 5000
        
        ' Act
        Dim maxDD = bankroll.CalculateMaxDrawdown()
        
        ' Assert
        maxDD.Should().Be(0.6667, precision:=0.001) ' ~66.67% drawdown
    End Sub

End Class
