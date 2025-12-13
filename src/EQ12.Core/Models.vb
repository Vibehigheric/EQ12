Imports System.Data

Namespace EQ12.Core
    ''' <summary>Represents a bankroll snapshot at a point in time</summary>
    Public Class BankrollSnapshot
        Public Property Timestamp As DateTime
        Public Property Balance As Decimal
        Public Property DailyRevenue As Decimal
        Public Property Source As String
    End Class

    ''' <summary>Full-featured bankroll manager with transaction history and analytics</summary>
    Public Class BankrollManager
        Private _initialBalance As Decimal
        Private _currentBalance As Decimal
        Private _transactions As New List(Of Transaction)
        Private _peakBalance As Decimal
        
        Public Sub New(initialBalance As Decimal)
            _initialBalance = initialBalance
            _currentBalance = initialBalance
            _peakBalance = initialBalance
        End Sub
        
        Public ReadOnly Property CurrentBalance As Decimal
            Get
                Return _currentBalance
            End Get
        End Property
        
        Public Sub Deposit(amount As Decimal, note As String)
            _currentBalance += amount
            _transactions.Add(New Transaction With {
                .Amount = amount,
                .Type = "Deposit",
                .Note = note,
                .Timestamp = DateTime.UtcNow,
                .BalanceAfter = _currentBalance
            })
            If _currentBalance > _peakBalance Then _peakBalance = _currentBalance
        End Sub
        
        Public Sub Withdraw(amount As Decimal, note As String)
            _currentBalance -= amount
            _transactions.Add(New Transaction With {
                .Amount = -amount,
                .Type = "Withdrawal",
                .Note = note,
                .Timestamp = DateTime.UtcNow,
                .BalanceAfter = _currentBalance
            })
        End Sub
        
        Public Sub RecordWin(amount As Decimal)
            Deposit(amount, "Betting win")
        End Sub
        
        Public Sub RecordLoss(amount As Decimal)
            Withdraw(amount, "Betting loss")
        End Sub
        
        Public Function CalculateROI() As Decimal
            If _initialBalance = 0 Then Return 0
            Return (_currentBalance - _initialBalance) / _initialBalance
        End Function
        
        Public Function CalculateMaxDrawdown() As Decimal
            If _peakBalance = 0 Then Return 0
            Return (_peakBalance - _currentBalance) / _peakBalance
        End Function
        
        Public Function GetTransactionHistory() As List(Of Transaction)
            Return _transactions
        End Function
    End Class
    
    ''' <summary>Transaction record for bankroll tracking</summary>
    Public Class Transaction
        Public Property Amount As Decimal
        Public Property Type As String
        Public Property Note As String
        Public Property Timestamp As DateTime
        Public Property BalanceAfter As Decimal
    End Class
    
    ''' <summary>Performance metrics calculator</summary>
    Public Class PerformanceMetrics
        Public Shared Function CalculateSharpeRatio(returns As Double(), riskFreeRate As Double) As Double
            If returns Is Nothing OrElse returns.Length = 0 Then Return 0.0
            
            Dim avgReturn = returns.Average()
            Dim stdDev = CalculateStdDev(returns)
            
            If stdDev = 0 Then Return 0.0
            Return (avgReturn - riskFreeRate) / stdDev
        End Function
        
        Public Shared Function KellyCriterion(winProbability As Double, odds As Double, bankroll As Double) As Double
            If odds <= 1 Then Return 0.0
            Dim kellyFraction = (winProbability * odds - (1 - winProbability)) / (odds - 1)
            If kellyFraction < 0 Then Return 0.0
            Return kellyFraction * bankroll
        End Function
        
        Public Shared Function CalculateROI(startValue As Double, endValue As Double) As Double
            If startValue = 0 Then Return 0.0
            Return (endValue - startValue) / startValue
        End Function
        
        Private Shared Function CalculateStdDev(values As Double()) As Double
            If values.Length <= 1 Then Return 0.0
            Dim avg = values.Average()
            Dim sumSquares = values.Sum(Function(x) (x - avg) * (x - avg))
            Return Math.Sqrt(sumSquares / (values.Length - 1))
        End Function
    End Class

    ''' <summary>Core logger interface for diagnostic output</summary>
    Public Interface IEQ12Logger
        Sub Log(level As String, message As String)
        Sub LogError(ex As Exception, context As String)
    End Interface

    ''' <summary>Environment configuration holder</summary>
    Public Class EQ12Config
        Public Property GumroadToken As String
        Public Property TelegramBotToken As String
        Public Property OddsApiKey As String
        Public Property DatabasePath As String
        Public Property AzureMLWorkspace As String
        Public Property AzureSubscriptionId As String
        Public Property DockerEnabled As Boolean
    End Class
    
    ''' <summary>Simple database connection info holder</summary>
    Public Class DatabaseConnection
        Public Property ConnectionString As String
        Public Property Provider As String
        Public Property IsActive As Boolean
        
        Public Sub New(path As String)
            ConnectionString = $"Data Source={path};Version=3;"
            Provider = "SQLite"
            IsActive = System.IO.File.Exists(path)
        End Sub
    End Class
End Namespace
