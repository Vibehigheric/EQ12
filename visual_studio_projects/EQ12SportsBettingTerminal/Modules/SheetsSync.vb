Imports System.Data
Imports System.Data.SQLite
Imports System.Threading.Tasks
Imports Newtonsoft.Json
Imports Newtonsoft.Json.Linq

''' <summary>
''' Google Sheets Synchronization Module for EQ12
''' Provides bi-directional DataTable ↔ Google Sheets synchronization via GAS
''' Handles push/pull operations with comprehensive logging and error handling
''' </summary>
Public Class SheetsSync
    Private ReadOnly _gasClient As GASClient
    Private ReadOnly _dbPath As String

    Public Sub New(gasClient As GASClient, Optional dbPath As String = "")
        _gasClient = gasClient ?? Throw New ArgumentNullException(NameOf(gasClient))
        _dbPath = If(String.IsNullOrEmpty(dbPath), "Data/eq12_terminal.db", dbPath)

        ' Initialize sync tracking table
        InitializeSyncTable()
    End Sub

    ''' <summary>
    ''' Push DataTable to Google Sheets (replaces all content)
    ''' </summary>
    ''' <param name="sheetName">Target sheet name</param>
    ''' <param name="dataTable">DataTable to push</param>
    ''' <returns>Synchronization result</returns>
    Public Async Function PushTableAsync(sheetName As String, dataTable As DataTable) As Task(Of SyncResult)
        If String.IsNullOrEmpty(sheetName) Then
            Throw New ArgumentException("Sheet name cannot be empty", NameOf(sheetName))
        End If

        If dataTable Is Nothing Then
            Throw New ArgumentNullException(NameOf(dataTable))
        End If

        Dim syncId As Integer = 0

        Try
            ' Log sync start
            syncId = LogSyncStart(sheetName, "push", dataTable.Rows.Count)

            ' Convert DataTable to JSON array
            Dim rows As New JArray()

            For Each row As DataRow In dataTable.Rows
                Dim rowObj As New JObject()
                For Each column As DataColumn In dataTable.Columns
                    Dim value = If(row(column) Is DBNull.Value, String.Empty, row(column).ToString())
                    rowObj(column.ColumnName) = value
                Next
                rows.Add(rowObj)
            Next

            ' Create payload for GAS
            Dim payload As New JObject() From {
                {"action", "push"},
                {"sheet", sheetName},
                {"rows", rows}
            }

            ' Send to GAS
            Dim response = Await _gasClient.PostJsonAsync(payload)

            ' Parse response
            Dim success = response.Value(Of Boolean)("ok")
            Dim rowCount = response.Value(Of Integer)("count")

            If success Then
                LogSyncComplete(syncId, "success", $"Pushed {rowCount} rows successfully")
                Return New SyncResult With {
                    .Success = True,
                    .SheetName = sheetName,
                    .Direction = SyncDirection.Push,
                    .RowCount = rowCount,
                    .Message = $"Successfully pushed {rowCount} rows to {sheetName}"
                }
            Else
                Dim errorMsg = response.Value(Of String)("error")
                LogSyncComplete(syncId, "failed", errorMsg)
                Return New SyncResult With {
                    .Success = False,
                    .SheetName = sheetName,
                    .Direction = SyncDirection.Push,
                    .RowCount = 0,
                    .ErrorMessage = errorMsg
                }
            End If

        Catch ex As Exception
            LogSyncComplete(syncId, "error", ex.Message)
            Return New SyncResult With {
                .Success = False,
                .SheetName = sheetName,
                .Direction = SyncDirection.Push,
                .RowCount = 0,
                .ErrorMessage = ex.Message
            }
        End Try
    End Function

    ''' <summary>
    ''' Pull data from Google Sheets to DataTable
    ''' </summary>
    ''' <param name="sheetName">Source sheet name</param>
    ''' <param name="limit">Maximum rows to retrieve (0 for all)</param>
    ''' <param name="offset">Number of rows to skip</param>
    ''' <returns>DataTable with sheet data and sync result</returns>
    Public Async Function PullTableAsync(sheetName As String, Optional limit As Integer = 0,
                                        Optional offset As Integer = 0) As Task(Of (DataTable, SyncResult))
        If String.IsNullOrEmpty(sheetName) Then
            Throw New ArgumentException("Sheet name cannot be empty", NameOf(sheetName))
        End If

        Dim syncId As Integer = 0
        Dim dataTable As New DataTable(sheetName)

        Try
            ' Log sync start
            syncId = LogSyncStart(sheetName, "pull", 0)

            ' Build parameters
            Dim parameters As New Dictionary(Of String, String) From {
                {"sheet", sheetName}
            }

            If limit > 0 Then parameters("limit") = limit.ToString()
            If offset > 0 Then parameters("offset") = offset.ToString()

            ' Get data from GAS
            Dim response = Await _gasClient.GetJsonAsync("pull", parameters)

            ' Parse response
            Dim success = response.Value(Of Boolean)("ok")

            If Not success Then
                Dim errorMsg = response.Value(Of String)("error")
                LogSyncComplete(syncId, "failed", errorMsg)

                Dim failResult = New SyncResult With {
                    .Success = False,
                    .SheetName = sheetName,
                    .Direction = SyncDirection.Pull,
                    .RowCount = 0,
                    .ErrorMessage = errorMsg
                }

                Return (dataTable, failResult)
            End If

            ' Extract data
            Dim rows = response.Value(Of JArray)("rows")
            Dim rowCount = response.Value(Of Integer)("count")

            ' Build DataTable structure from first row if available
            If rows.Count > 0 Then
                Dim firstRow = DirectCast(rows(0), JObject)

                ' Add columns based on first row properties
                For Each prop As JProperty In firstRow.Properties()
                    dataTable.Columns.Add(prop.Name, GetType(String))
                Next

                ' Add data rows
                For Each rowToken As JToken In rows
                    Dim row = DirectCast(rowToken, JObject)
                    Dim dataRow = dataTable.NewRow()

                    For Each column As DataColumn In dataTable.Columns
                        Dim value = row.Value(Of String)(column.ColumnName)
                        dataRow(column.ColumnName) = If(value, String.Empty)
                    Next

                    dataTable.Rows.Add(dataRow)
                Next
            End If

            LogSyncComplete(syncId, "success", $"Pulled {rowCount} rows successfully")

            Dim successResult = New SyncResult With {
                .Success = True,
                .SheetName = sheetName,
                .Direction = SyncDirection.Pull,
                .RowCount = rowCount,
                .Message = $"Successfully pulled {rowCount} rows from {sheetName}"
            }

            Return (dataTable, successResult)

        Catch ex As Exception
            LogSyncComplete(syncId, "error", ex.Message)

            Dim errorResult = New SyncResult With {
                .Success = False,
                .SheetName = sheetName,
                .Direction = SyncDirection.Pull,
                .RowCount = 0,
                .ErrorMessage = ex.Message
            }

            Return (dataTable, errorResult)
        End Try
    End Function

    ''' <summary>
    ''' Append rows to existing Google Sheet
    ''' </summary>
    ''' <param name="sheetName">Target sheet name</param>
    ''' <param name="dataTable">DataTable with rows to append</param>
    ''' <returns>Synchronization result</returns>
    Public Async Function AppendTableAsync(sheetName As String, dataTable As DataTable) As Task(Of SyncResult)
        If String.IsNullOrEmpty(sheetName) Then
            Throw New ArgumentException("Sheet name cannot be empty", NameOf(sheetName))
        End If

        If dataTable Is Nothing Then
            Throw New ArgumentNullException(NameOf(dataTable))
        End If

        Dim syncId As Integer = 0

        Try
            ' Log sync start
            syncId = LogSyncStart(sheetName, "append", dataTable.Rows.Count)

            ' Convert DataTable to JSON array
            Dim rows As New JArray()

            For Each row As DataRow In dataTable.Rows
                Dim rowObj As New JObject()
                For Each column As DataColumn In dataTable.Columns
                    Dim value = If(row(column) Is DBNull.Value, String.Empty, row(column).ToString())
                    rowObj(column.ColumnName) = value
                Next
                rows.Add(rowObj)
            Next

            ' Create payload for GAS
            Dim payload As New JObject() From {
                {"action", "append"},
                {"sheet", sheetName},
                {"rows", rows}
            }

            ' Send to GAS
            Dim response = Await _gasClient.PostJsonAsync(payload)

            ' Parse response
            Dim success = response.Value(Of Boolean)("ok")

            If success Then
                Dim appendedCount = response.Value(Of Integer)("appended")
                LogSyncComplete(syncId, "success", $"Appended {appendedCount} rows successfully")

                Return New SyncResult With {
                    .Success = True,
                    .SheetName = sheetName,
                    .Direction = SyncDirection.Append,
                    .RowCount = appendedCount,
                    .Message = $"Successfully appended {appendedCount} rows to {sheetName}"
                }
            Else
                Dim errorMsg = response.Value(Of String)("error")
                LogSyncComplete(syncId, "failed", errorMsg)

                Return New SyncResult With {
                    .Success = False,
                    .SheetName = sheetName,
                    .Direction = SyncDirection.Append,
                    .RowCount = 0,
                    .ErrorMessage = errorMsg
                }
            End If

        Catch ex As Exception
            LogSyncComplete(syncId, "error", ex.Message)

            Return New SyncResult With {
                .Success = False,
                .SheetName = sheetName,
                .Direction = SyncDirection.Append,
                .RowCount = 0,
                .ErrorMessage = ex.Message
            }
        End Try
    End Function

    ''' <summary>
    ''' Sync database table to Google Sheets
    ''' </summary>
    ''' <param name="sheetName">Target sheet name</param>
    ''' <param name="tableName">Source database table name</param>
    ''' <param name="whereClause">Optional WHERE clause for filtering</param>
    ''' <returns>Synchronization result</returns>
    Public Async Function SyncDatabaseTableAsync(sheetName As String, tableName As String,
                                                Optional whereClause As String = "") As Task(Of SyncResult)
        Try
            ' Load data from database
            Dim dataTable = LoadDatabaseTable(tableName, whereClause)

            ' Push to Google Sheets
            Return Await PushTableAsync(sheetName, dataTable)

        Catch ex As Exception
            Return New SyncResult With {
                .Success = False,
                .SheetName = sheetName,
                .Direction = SyncDirection.Push,
                .RowCount = 0,
                .ErrorMessage = $"Database sync failed: {ex.Message}"
            }
        End Try
    End Function

    ''' <summary>
    ''' Get sync history and statistics
    ''' </summary>
    ''' <param name="limit">Number of recent syncs to retrieve</param>
    ''' <returns>List of sync records</returns>
    Public Function GetSyncHistory(Optional limit As Integer = 50) As List(Of Object)
        Dim history As New List(Of Object)()

        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                Dim sql = $"
                SELECT timestamp, sheet_name, direction, rows_processed, status, message
                FROM sheet_syncs
                ORDER BY timestamp DESC
                LIMIT {limit}"

                Using cmd As New SQLiteCommand(sql, conn)
                    Using reader = cmd.ExecuteReader()
                        While reader.Read()
                            history.Add(New With {
                                .Timestamp = reader("timestamp").ToString(),
                                .SheetName = reader("sheet_name").ToString(),
                                .Direction = reader("direction").ToString(),
                                .RowsProcessed = Convert.ToInt32(reader("rows_processed")),
                                .Status = reader("status").ToString(),
                                .Message = reader("message")?.ToString()
                            })
                        End While
                    End Using
                End Using
            End Using

        Catch ex As Exception
            Console.WriteLine($"Failed to retrieve sync history: {ex.Message}")
        End Try

        Return history
    End Function

    ''' <summary>
    ''' Initialize sync tracking database table
    ''' </summary>
    Private Sub InitializeSyncTable()
        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                Dim createTableSql = "
                CREATE TABLE IF NOT EXISTS sheet_syncs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT (datetime('now')),
                    sheet_name TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    rows_processed INTEGER DEFAULT 0,
                    status TEXT NOT NULL,
                    message TEXT
                )"

                Using cmd As New SQLiteCommand(createTableSql, conn)
                    cmd.ExecuteNonQuery()
                End Using
            End Using

        Catch ex As Exception
            Console.WriteLine($"SheetsSync database init failed: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Log sync operation start
    ''' </summary>
    ''' <param name="sheetName">Sheet name</param>
    ''' <param name="direction">Sync direction</param>
    ''' <param name="rowCount">Expected row count</param>
    ''' <returns>Sync record ID</returns>
    Private Function LogSyncStart(sheetName As String, direction As String, rowCount As Integer) As Integer
        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                Dim insertSql = "
                INSERT INTO sheet_syncs (sheet_name, direction, rows_processed, status, message)
                VALUES (@sheet, @direction, @rows, 'started', 'Sync operation started')
                "

                Using cmd As New SQLiteCommand(insertSql, conn)
                    cmd.Parameters.AddWithValue("@sheet", sheetName)
                    cmd.Parameters.AddWithValue("@direction", direction)
                    cmd.Parameters.AddWithValue("@rows", rowCount)
                    cmd.ExecuteNonQuery()

                    Return Convert.ToInt32(conn.LastInsertRowId)
                End Using
            End Using

        Catch ex As Exception
            Console.WriteLine($"Sync logging failed: {ex.Message}")
            Return 0
        End Try
    End Function

    ''' <summary>
    ''' Update sync operation completion
    ''' </summary>
    ''' <param name="syncId">Sync record ID</param>
    ''' <param name="status">Final status</param>
    ''' <param name="message">Completion message</param>
    Private Sub LogSyncComplete(syncId As Integer, status As String, message As String)
        If syncId = 0 Then Return

        Try
            Using conn As New SQLiteConnection($"Data Source={_dbPath}")
                conn.Open()

                Dim updateSql = "
                UPDATE sheet_syncs
                SET status = @status, message = @message
                WHERE id = @id"

                Using cmd As New SQLiteCommand(updateSql, conn)
                    cmd.Parameters.AddWithValue("@status", status)
                    cmd.Parameters.AddWithValue("@message", message)
                    cmd.Parameters.AddWithValue("@id", syncId)
                    cmd.ExecuteNonQuery()
                End Using
            End Using

        Catch ex As Exception
            Console.WriteLine($"Sync completion logging failed: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Load data from database table
    ''' </summary>
    ''' <param name="tableName">Table name</param>
    ''' <param name="whereClause">Optional WHERE clause</param>
    ''' <returns>DataTable with database data</returns>
    Private Function LoadDatabaseTable(tableName As String, Optional whereClause As String = "") As DataTable
        Dim dataTable As New DataTable(tableName)

        Using conn As New SQLiteConnection($"Data Source={_dbPath}")
            conn.Open()

            Dim sql = $"SELECT * FROM {tableName}"
            If Not String.IsNullOrEmpty(whereClause) Then
                sql &= $" WHERE {whereClause}"
            End If

            Using adapter As New SQLiteDataAdapter(sql, conn)
                adapter.Fill(dataTable)
            End Using
        End Using

        Return dataTable
    End Function
End Class

''' <summary>
''' Synchronization result information
''' </summary>
Public Class SyncResult
    Public Property Success As Boolean
    Public Property SheetName As String
    Public Property Direction As SyncDirection
    Public Property RowCount As Integer
    Public Property Message As String
    Public Property ErrorMessage As String

    Public ReadOnly Property IsError As Boolean
        Get
            Return Not Success
        End Get
    End Property

    Public Overrides Function ToString() As String
        If Success Then
            Return $"{Direction} to {SheetName}: {RowCount} rows - {Message}"
        Else
            Return $"{Direction} to {SheetName}: FAILED - {ErrorMessage}"
        End If
    End Function
End Class

''' <summary>
''' Synchronization direction enumeration
''' </summary>
Public Enum SyncDirection
    Push
    Pull
    Append
End Enum
