''' <summary>
''' EQ12 COMMIT EXPERT TRAINING MODULE
''' VB.NET Transaction Management - Complete Reference
''' </summary>
''' <remarks>
''' This module demonstrates:
''' 1. Database transaction commit/rollback patterns
''' 2. Multi-step atomic operations
''' 3. Error handling and recovery
''' 4. Transaction logging for audit trails
''' 5. Performance monitoring
''' </remarks>

Imports System
Imports System.Data.SqlClient
Imports System.Data.SQLite
Imports System.IO
Imports System.Text

Namespace EQ12.CommitExpert

    ''' <summary>
    ''' Transaction result with detailed metrics
    ''' </summary>
    Public Class TransactionResult
        Public Property Success As Boolean
        Public Property OperationsCompleted As Integer
        Public Property DurationMs As Long
        Public Property ErrorMessage As String
        Public Property RollbackReason As String
        Public Property Timestamp As DateTime

        Public Sub New()
            Timestamp = DateTime.UtcNow
        End Sub
    End Class

    ''' <summary>
    ''' LESSON 1: Basic SQLite Transaction with Commit/Rollback
    ''' </summary>
    Public Class BasicTransactionExample

        Private ReadOnly _connString As String

        Public Sub New(dbPath As String)
            _connString = $"Data Source={dbPath};Version=3;"
        End Sub

        ''' <summary>
        ''' Demonstrates the fundamental commit pattern:
        ''' 1. BeginTransaction
        ''' 2. Execute operations
        ''' 3. Commit on success OR Rollback on error
        ''' </summary>
        Public Function TransferMoney(fromAccountId As Integer, toAccountId As Integer, amount As Decimal) As TransactionResult
            Dim result As New TransactionResult()
            Dim sw = Diagnostics.Stopwatch.StartNew()

            Using conn As New SQLiteConnection(_connString)
                conn.Open()

                ' ✅ CRITICAL: BeginTransaction creates transaction scope
                Using transaction As SQLiteTransaction = conn.BeginTransaction()
                    Try
                        ' Step 1: Debit from source account
                        Using cmd As New SQLiteCommand("UPDATE Accounts SET Balance = Balance - @Amount WHERE AccountId = @AccountId", conn, transaction)
                            cmd.Parameters.AddWithValue("@Amount", amount)
                            cmd.Parameters.AddWithValue("@AccountId", fromAccountId)
                            
                            Dim rowsAffected = cmd.ExecuteNonQuery()
                            If rowsAffected = 0 Then
                                Throw New Exception($"Account {fromAccountId} not found")
                            End If

                            result.OperationsCompleted += 1
                        End Using

                        ' Step 2: Verify sufficient balance (business logic validation)
                        Using cmd As New SQLiteCommand("SELECT Balance FROM Accounts WHERE AccountId = @AccountId", conn, transaction)
                            cmd.Parameters.AddWithValue("@AccountId", fromAccountId)
                            Dim balance = Convert.ToDecimal(cmd.ExecuteScalar())
                            
                            If balance < 0 Then
                                Throw New InvalidOperationException($"Insufficient funds: balance = {balance}")
                            End If
                        End Using

                        ' Step 3: Credit to destination account
                        Using cmd As New SQLiteCommand("UPDATE Accounts SET Balance = Balance + @Amount WHERE AccountId = @AccountId", conn, transaction)
                            cmd.Parameters.AddWithValue("@Amount", amount)
                            cmd.Parameters.AddWithValue("@AccountId", toAccountId)
                            
                            Dim rowsAffected = cmd.ExecuteNonQuery()
                            If rowsAffected = 0 Then
                                Throw New Exception($"Account {toAccountId} not found")
                            End If

                            result.OperationsCompleted += 1
                        End Using

                        ' Step 4: Log transaction (audit trail)
                        Using cmd As New SQLiteCommand("INSERT INTO TransactionLog (FromAccount, ToAccount, Amount, Timestamp) VALUES (@From, @To, @Amount, @Timestamp)", conn, transaction)
                            cmd.Parameters.AddWithValue("@From", fromAccountId)
                            cmd.Parameters.AddWithValue("@To", toAccountId)
                            cmd.Parameters.AddWithValue("@Amount", amount)
                            cmd.Parameters.AddWithValue("@Timestamp", DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss"))
                            cmd.ExecuteNonQuery()

                            result.OperationsCompleted += 1
                        End Using

                        ' ✅ COMMIT: All operations succeeded - make changes permanent
                        transaction.Commit()
                        result.Success = True

                        sw.Stop()
                        result.DurationMs = sw.ElapsedMilliseconds

                        Console.WriteLine($"[COMMIT] Transfer ${amount} from Account {fromAccountId} to {toAccountId} succeeded ({result.OperationsCompleted} operations, {result.DurationMs}ms)")

                    Catch ex As Exception
                        ' ❌ ROLLBACK: Any error reverts ALL changes
                        transaction.Rollback()
                        result.Success = False
                        result.ErrorMessage = ex.Message
                        result.RollbackReason = "Exception during transaction"

                        sw.Stop()
                        result.DurationMs = sw.ElapsedMilliseconds

                        Console.WriteLine($"[ROLLBACK] Transfer failed: {ex.Message} (all changes reverted, {result.DurationMs}ms)")
                    End Try
                End Using
            End Using

            Return result
        End Function

    End Class

    ''' <summary>
    ''' LESSON 2: Advanced Transaction Patterns - Nested Operations
    ''' </summary>
    Public Class AdvancedTransactionExample

        Private ReadOnly _connString As String

        Public Sub New(dbPath As String)
            _connString = $"Data Source={dbPath};Version=3;"
        End Sub

        ''' <summary>
        ''' Demonstrates complex multi-table atomic operations
        ''' Scenario: Process a bet slip with multiple legs
        ''' </summary>
        Public Function ProcessBetSlip(betSlipId As Integer, legs As List(Of BetLeg)) As TransactionResult
            Dim result As New TransactionResult()
            Dim sw = Diagnostics.Stopwatch.StartNew()

            Using conn As New SQLiteConnection(_connString)
                conn.Open()

                Using transaction As SQLiteTransaction = conn.BeginTransaction()
                    Try
                        ' Operation 1: Validate bet slip exists and is open
                        Using cmd As New SQLiteCommand("SELECT Status FROM BetSlips WHERE BetSlipId = @Id", conn, transaction)
                            cmd.Parameters.AddWithValue("@Id", betSlipId)
                            Dim status = cmd.ExecuteScalar()?.ToString()
                            
                            If status Is Nothing Then
                                Throw New Exception($"BetSlip {betSlipId} not found")
                            End If

                            If status <> "OPEN" Then
                                Throw New Exception($"BetSlip {betSlipId} is {status}, cannot process")
                            End If
                        End Using

                        ' Operation 2: Insert all bet legs (multi-row insert)
                        Dim totalStake As Decimal = 0
                        For Each leg In legs
                            Using cmd As New SQLiteCommand("INSERT INTO BetLegs (BetSlipId, Team, Odds, Stake) VALUES (@SlipId, @Team, @Odds, @Stake)", conn, transaction)
                                cmd.Parameters.AddWithValue("@SlipId", betSlipId)
                                cmd.Parameters.AddWithValue("@Team", leg.Team)
                                cmd.Parameters.AddWithValue("@Odds", leg.Odds)
                                cmd.Parameters.AddWithValue("@Stake", leg.Stake)
                                cmd.ExecuteNonQuery()

                                totalStake += leg.Stake
                                result.OperationsCompleted += 1
                            End Using
                        Next

                        ' Operation 3: Calculate parlay odds
                        Dim parlayOdds As Decimal = 1.0
                        For Each leg In legs
                            parlayOdds *= leg.DecimalOdds
                        Next

                        Dim potentialPayout = totalStake * parlayOdds

                        ' Operation 4: Update bet slip with totals
                        Using cmd As New SQLiteCommand("UPDATE BetSlips SET TotalStake = @Stake, ParlayOdds = @Odds, PotentialPayout = @Payout, ProcessedAt = @ProcessedAt, Status = 'PENDING' WHERE BetSlipId = @Id", conn, transaction)
                            cmd.Parameters.AddWithValue("@Stake", totalStake)
                            cmd.Parameters.AddWithValue("@Odds", parlayOdds)
                            cmd.Parameters.AddWithValue("@Payout", potentialPayout)
                            cmd.Parameters.AddWithValue("@ProcessedAt", DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss"))
                            cmd.Parameters.AddWithValue("@Id", betSlipId)
                            cmd.ExecuteNonQuery()

                            result.OperationsCompleted += 1
                        End Using

                        ' Operation 5: Deduct stake from user balance (financial operation)
                        Using cmd As New SQLiteCommand("UPDATE UserBalances SET Balance = Balance - @Stake WHERE UserId = (SELECT UserId FROM BetSlips WHERE BetSlipId = @Id)", conn, transaction)
                            cmd.Parameters.AddWithValue("@Stake", totalStake)
                            cmd.Parameters.AddWithValue("@Id", betSlipId)
                            
                            Dim rowsAffected = cmd.ExecuteNonQuery()
                            If rowsAffected = 0 Then
                                Throw New Exception("User not found or balance update failed")
                            End If

                            result.OperationsCompleted += 1
                        End Using

                        ' Operation 6: Verify user still has positive balance
                        Using cmd As New SQLiteCommand("SELECT Balance FROM UserBalances WHERE UserId = (SELECT UserId FROM BetSlips WHERE BetSlipId = @Id)", conn, transaction)
                            cmd.Parameters.AddWithValue("@Id", betSlipId)
                            Dim balance = Convert.ToDecimal(cmd.ExecuteScalar())
                            
                            If balance < 0 Then
                                Throw New InvalidOperationException($"Insufficient funds: balance would be {balance}")
                            End If
                        End Using

                        ' ✅ COMMIT: All 6 operations succeeded atomically
                        transaction.Commit()
                        result.Success = True

                        sw.Stop()
                        result.DurationMs = sw.ElapsedMilliseconds

                        Console.WriteLine($"[COMMIT] BetSlip {betSlipId} processed: {legs.Count} legs, ${totalStake} stake, ${potentialPayout:F2} potential payout ({result.OperationsCompleted} operations, {result.DurationMs}ms)")

                    Catch ex As Exception
                        ' ❌ ROLLBACK: Any validation or operation failure reverts everything
                        transaction.Rollback()
                        result.Success = False
                        result.ErrorMessage = ex.Message
                        result.RollbackReason = "Business logic validation failed or operation error"

                        sw.Stop()
                        result.DurationMs = sw.ElapsedMilliseconds

                        Console.WriteLine($"[ROLLBACK] BetSlip {betSlipId} processing failed: {ex.Message} (all changes reverted, {result.DurationMs}ms)")
                    End Try
                End Using
            End Using

            Return result
        End Function

    End Class

    ''' <summary>
    ''' LESSON 3: Transaction Isolation Levels
    ''' </summary>
    Public Class IsolationLevelExample

        Private ReadOnly _connString As String

        Public Sub New(connString As String)
            _connString = connString
        End Sub

        ''' <summary>
        ''' Demonstrates different transaction isolation levels
        ''' </summary>
        Public Sub DemonstrateIsolationLevels()
            Using conn As New SqlConnection(_connString)
                conn.Open()

                ' READ UNCOMMITTED - Allows dirty reads (fastest, least safe)
                Using trans = conn.BeginTransaction(IsolationLevel.ReadUncommitted)
                    Console.WriteLine("Isolation Level: READ UNCOMMITTED (can see uncommitted changes from other transactions)")
                    trans.Commit()
                End Using

                ' READ COMMITTED - Default, prevents dirty reads
                Using trans = conn.BeginTransaction(IsolationLevel.ReadCommitted)
                    Console.WriteLine("Isolation Level: READ COMMITTED (only sees committed data)")
                    trans.Commit()
                End Using

                ' REPEATABLE READ - Prevents dirty reads and non-repeatable reads
                Using trans = conn.BeginTransaction(IsolationLevel.RepeatableRead)
                    Console.WriteLine("Isolation Level: REPEATABLE READ (data read cannot be changed by others)")
                    trans.Commit()
                End Using

                ' SERIALIZABLE - Highest isolation, prevents phantom reads
                Using trans = conn.BeginTransaction(IsolationLevel.Serializable)
                    Console.WriteLine("Isolation Level: SERIALIZABLE (full isolation, slowest)")
                    trans.Commit()
                End Using
            End Using
        End Sub

    End Class

    ''' <summary>
    ''' LESSON 4: Commit Logging and Audit Trail
    ''' </summary>
    Public Class CommitLogger

        Private ReadOnly _logPath As String

        Public Sub New(logPath As String)
            _logPath = logPath
        End Sub

        ''' <summary>
        ''' Log commit event with full context
        ''' </summary>
        Public Sub LogCommit(result As TransactionResult, operationName As String)
            Dim logEntry = New StringBuilder()
            logEntry.AppendLine($"[{result.Timestamp:yyyy-MM-dd HH:mm:ss}] COMMIT AUDIT LOG")
            logEntry.AppendLine($"Operation: {operationName}")
            logEntry.AppendLine($"Success: {result.Success}")
            logEntry.AppendLine($"Operations Completed: {result.OperationsCompleted}")
            logEntry.AppendLine($"Duration: {result.DurationMs}ms")

            If Not result.Success Then
                logEntry.AppendLine($"Error: {result.ErrorMessage}")
                logEntry.AppendLine($"Rollback Reason: {result.RollbackReason}")
            End If

            logEntry.AppendLine(New String("-"c, 80))

            File.AppendAllText(_logPath, logEntry.ToString())
        End Sub

    End Class

    ''' <summary>
    ''' Supporting class for bet leg data
    ''' </summary>
    Public Class BetLeg
        Public Property Team As String
        Public Property Odds As Decimal ' American odds
        Public Property Stake As Decimal

        Public ReadOnly Property DecimalOdds As Decimal
            Get
                ' Convert American odds to decimal
                If Odds > 0 Then
                    Return (Odds / 100) + 1
                Else
                    Return (100 / Math.Abs(Odds)) + 1
                End If
            End Get
        End Property
    End Class

    ''' <summary>
    ''' MAIN PROGRAM: Run all transaction examples
    ''' </summary>
    Module CommitTrainingProgram

        Sub Main()
            Console.WriteLine("=== EQ12 COMMIT EXPERT TRAINING ===")
            Console.WriteLine()

            Dim dbPath = "C:\EQ12\data\commit_training.db"
            InitializeDatabase(dbPath)

            ' Lesson 1: Basic Transaction
            Console.WriteLine("--- LESSON 1: Basic Transaction ---")
            Dim basic As New BasicTransactionExample(dbPath)
            
            ' Test successful commit
            Dim result1 = basic.TransferMoney(1, 2, 100D)
            
            ' Test rollback (insufficient funds)
            Dim result2 = basic.TransferMoney(1, 2, 10000D)
            Console.WriteLine()

            ' Lesson 2: Advanced Transaction
            Console.WriteLine("--- LESSON 2: Advanced Transaction ---")
            Dim advanced As New AdvancedTransactionExample(dbPath)
            
            Dim legs As New List(Of BetLeg) From {
                New BetLeg With {.Team = "Lakers", .Odds = -110, .Stake = 50},
                New BetLeg With {.Team = "Warriors", .Odds = +150, .Stake = 50},
                New BetLeg With {.Team = "Celtics", .Odds = -200, .Stake = 50}
            }
            
            Dim result3 = advanced.ProcessBetSlip(1, legs)
            Console.WriteLine()

            ' Lesson 3: Commit Logging
            Console.WriteLine("--- LESSON 3: Commit Logging ---")
            Dim logger As New CommitLogger("C:\EQ12\logs\commit_audit.log")
            logger.LogCommit(result1, "MoneyTransfer")
            logger.LogCommit(result2, "MoneyTransfer_Failed")
            logger.LogCommit(result3, "BetSlipProcessing")
            Console.WriteLine($"Audit log written to: C:\EQ12\logs\commit_audit.log")

            Console.WriteLine()
            Console.WriteLine("Training complete. Review the audit log for commit history.")
        End Sub

        Sub InitializeDatabase(dbPath As String)
            ' Create test database schema
            If Not File.Exists(dbPath) Then
                Directory.CreateDirectory(Path.GetDirectoryName(dbPath))
                SQLiteConnection.CreateFile(dbPath)

                Using conn As New SQLiteConnection($"Data Source={dbPath};Version=3;")
                    conn.Open()

                    Dim schema = "
                    CREATE TABLE Accounts (
                        AccountId INTEGER PRIMARY KEY,
                        Balance DECIMAL(18,2) NOT NULL
                    );

                    CREATE TABLE TransactionLog (
                        LogId INTEGER PRIMARY KEY AUTOINCREMENT,
                        FromAccount INTEGER,
                        ToAccount INTEGER,
                        Amount DECIMAL(18,2),
                        Timestamp TEXT
                    );

                    CREATE TABLE BetSlips (
                        BetSlipId INTEGER PRIMARY KEY,
                        UserId INTEGER,
                        Status TEXT,
                        TotalStake DECIMAL(18,2),
                        ParlayOdds DECIMAL(18,4),
                        PotentialPayout DECIMAL(18,2),
                        ProcessedAt TEXT
                    );

                    CREATE TABLE BetLegs (
                        LegId INTEGER PRIMARY KEY AUTOINCREMENT,
                        BetSlipId INTEGER,
                        Team TEXT,
                        Odds DECIMAL(18,2),
                        Stake DECIMAL(18,2)
                    );

                    CREATE TABLE UserBalances (
                        UserId INTEGER PRIMARY KEY,
                        Balance DECIMAL(18,2) NOT NULL
                    );

                    INSERT INTO Accounts VALUES (1, 1000.00);
                    INSERT INTO Accounts VALUES (2, 500.00);

                    INSERT INTO UserBalances VALUES (1, 5000.00);

                    INSERT INTO BetSlips VALUES (1, 1, 'OPEN', NULL, NULL, NULL, NULL);
                    "

                    Using cmd As New SQLiteCommand(schema, conn)
                        cmd.ExecuteNonQuery()
                    End Using
                End Using

                Console.WriteLine($"Test database initialized: {dbPath}")
            End If
        End Sub

    End Module

End Namespace
