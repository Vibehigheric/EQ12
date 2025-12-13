Imports System.Net.Http
Imports System.Text
Imports Newtonsoft.Json.Linq
Imports Newtonsoft.Json
Imports System.Web
Imports System.Data.SQLite

''' <summary>
''' Sheets Helper - Google Sheets API Integration
''' Handles data synchronization and AppSheet integration for EQ12 reports
''' Features: Table sync, incremental updates, AppSheet integration, data validation
''' </summary>
Public Class SheetsHelper

    ''' <summary>
    ''' Sync data table to Google Sheets
    ''' </summary>
    ''' <param name="config">Configuration object with Google Sheets settings</param>
    ''' <param name="tableName">Database table name to sync</param>
    ''' <param name="sheetName">Google Sheets tab name (optional)</param>
    ''' <param name="incrementalOnly">Only sync new/updated records</param>
    ''' <returns>Sync result message</returns>
    Public Shared Function SyncTable(config As JObject, tableName As String,
                                    Optional sheetName As String = Nothing,
                                    Optional incrementalOnly As Boolean = True) As String
        Try
            Console.WriteLine($"📊 Syncing {tableName} to Google Sheets...")

            ' Get access token
            Dim accessToken = GoogleAuthHelper.GetAccessToken(config, "sheets")
            If accessToken.StartsWith("Error") Then
                Return accessToken
            End If

            ' Use table name as sheet name if not specified
            If String.IsNullOrEmpty(sheetName) Then
                sheetName = tableName
            End If

            ' Get spreadsheet ID from config
            Dim spreadsheetId = config("google_sheets")("sheet_id")?.ToString()
            If String.IsNullOrEmpty(spreadsheetId) Then
                Return "Error: No spreadsheet ID configured"
            End If

            ' Get data from database
            Dim tableData = GetTableData(tableName, incrementalOnly)
            If tableData.Rows.Count = 0 Then
                Console.WriteLine("ℹ️ No new data to sync")
                Return "No new data to sync"
            End If

            ' Check if sheet exists, create if not
            Dim sheetExists = CheckSheetExists(config, spreadsheetId, sheetName, accessToken)
            If Not sheetExists Then
                Dim createResult = CreateSheet(config, spreadsheetId, sheetName, accessToken)
                If createResult.StartsWith("Error") Then
                    Return createResult
                End If
            End If

            ' Prepare data for sheets
            Dim sheetData = PrepareSheetData(tableData)

            ' Determine update method
            Dim updateResult As String
            If incrementalOnly Then
                updateResult = AppendToSheet(config, spreadsheetId, sheetName, sheetData, accessToken)
            Else
                updateResult = UpdateEntireSheet(config, spreadsheetId, sheetName, sheetData, accessToken)
            End If

            If updateResult.StartsWith("Error") Then
                Return updateResult
            End If

            ' Log sync operation
            LogSheetSync(tableName, sheetName, tableData.Rows.Count, incrementalOnly)

            ' Update AppSheet if configured
            If config("appsheet")?.ContainsKey("app_id") = True Then
                Dim appSheetResult = TriggerAppSheetSync(config, tableName)
                If Not appSheetResult.StartsWith("Error") Then
                    Console.WriteLine($"📱 AppSheet sync triggered: {appSheetResult}")
                End If
            End If

            Console.WriteLine($"✅ Sync completed - {tableData.Rows.Count} records updated")
            Return $"Success: {tableData.Rows.Count} records synced to {sheetName}"

        Catch ex As Exception
            Return $"Error syncing table: {ex.Message}"
        End Try
    End Function

    ''' <summary>
    ''' Get table data from database with optional incremental filtering
    ''' </summary>
    Private Shared Function GetTableData(tableName As String, incrementalOnly As Boolean) As DataTable
        Dim dataTable As New DataTable()

        Try
            Using conn As New SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()

                Dim sql As String
                If incrementalOnly Then
                    ' Get records modified since last sync
                    sql = GetIncrementalQuery(tableName)
                Else
                    ' Get all records
                    sql = $"SELECT * FROM {tableName} ORDER BY id DESC LIMIT 1000"
                End If

                Using cmd As New SQLiteCommand(sql, conn)
                    Using adapter As New SQLiteDataAdapter(cmd)
                        adapter.Fill(dataTable)
                    End Using
                End Using
            End Using

        Catch ex As Exception
            Console.WriteLine($"❌ Error getting table data: {ex.Message}")
        End Try

        Return dataTable
    End Function

    ''' <summary>
    ''' Get incremental query based on table type and last sync time
    ''' </summary>
    Private Shared Function GetIncrementalQuery(tableName As String) As String
        Dim lastSync = GetLastSyncTime(tableName)

        Select Case tableName.ToLower()
            Case "events"
                Return $"SELECT * FROM events WHERE date >= datetime('{lastSync}') ORDER BY date DESC LIMIT 500"
            Case "lines"
                Return $"SELECT * FROM lines WHERE created_at >= datetime('{lastSync}') ORDER BY created_at DESC LIMIT 1000"
            Case "bets"
                Return $"SELECT * FROM bets WHERE created_at >= datetime('{lastSync}') ORDER BY created_at DESC LIMIT 500"
            Case "arbitrage"
                Return $"SELECT * FROM arbitrage WHERE created_at >= datetime('{lastSync}') ORDER BY created_at DESC LIMIT 200"
            Case "deliverables"
                Return $"SELECT * FROM deliverables WHERE created_at >= datetime('{lastSync}') ORDER BY created_at DESC LIMIT 100"
            Case "bitly_stats"
                Return $"SELECT * FROM bitly_stats WHERE created_at >= datetime('{lastSync}') ORDER BY created_at DESC LIMIT 300"
            Case "drive_uploads"
                Return $"SELECT * FROM drive_uploads WHERE created_at >= datetime('{lastSync}') ORDER BY created_at DESC LIMIT 100"
            Case Else
                Return $"SELECT * FROM {tableName} ORDER BY id DESC LIMIT 200"
        End Select
    End Function

    ''' <summary>
    ''' Get last sync time for table from database
    ''' </summary>
    Private Shared Function GetLastSyncTime(tableName As String) As String
        Try
            Using conn As New SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()

                Dim sql = "SELECT MAX(synced_at) FROM sheet_syncs WHERE table_name = @table_name"
                Using cmd As New SQLiteCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@table_name", tableName)

                    Dim result = cmd.ExecuteScalar()
                    If result IsNot Nothing AndAlso result IsNot DBNull.Value Then
                        Return Convert.ToDateTime(result).ToString("yyyy-MM-dd HH:mm:ss")
                    End If
                End Using
            End Using
        Catch ex As Exception
            Console.WriteLine($"⚠️ Could not get last sync time: {ex.Message}")
        End Try

        ' Default to 24 hours ago if no previous sync
        Return DateTime.UtcNow.AddHours(-24).ToString("yyyy-MM-dd HH:mm:ss")
    End Function

    ''' <summary>
    ''' Check if sheet exists in spreadsheet
    ''' </summary>
    Private Shared Function CheckSheetExists(config As JObject, spreadsheetId As String,
                                           sheetName As String, accessToken As String) As Boolean
        Try
            Using client As New HttpClient()
                client.DefaultRequestHeaders.Add("Authorization", $"Bearer {accessToken}")

                Dim getUrl = $"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheetId}"
                Dim response = client.GetAsync(getUrl).Result

                If response.IsSuccessStatusCode Then
                    Dim responseContent = response.Content.ReadAsStringAsync().Result
                    Dim spreadsheetData = JObject.Parse(responseContent)

                    If spreadsheetData("sheets") IsNot Nothing Then
                        For Each sheet In spreadsheetData("sheets")
                            Dim properties = sheet("properties")
                            If properties?.Item("title")?.ToString() = sheetName Then
                                Return True
                            End If
                        Next
                    End If
                End If
            End Using
        Catch ex As Exception
            Console.WriteLine($"⚠️ Error checking sheet existence: {ex.Message}")
        End Try

        Return False
    End Function

    ''' <summary>
    ''' Create new sheet in spreadsheet
    ''' </summary>
    Private Shared Function CreateSheet(config As JObject, spreadsheetId As String,
                                      sheetName As String, accessToken As String) As String
        Try
            Console.WriteLine($"📋 Creating sheet: {sheetName}")

            Dim requestBody As New JObject()
            Dim requests As New JArray()

            Dim addSheetRequest As New JObject()
            addSheetRequest("addSheet") = New JObject() From {
                {"properties", New JObject() From {
                    {"title", sheetName}
                }}
            }
            requests.Add(addSheetRequest)
            requestBody("requests") = requests

            Using client As New HttpClient()
                client.DefaultRequestHeaders.Add("Authorization", $"Bearer {accessToken}")

                Dim content = New StringContent(requestBody.ToString(), Encoding.UTF8, "application/json")
                Dim batchUpdateUrl = $"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheetId}:batchUpdate"
                Dim response = client.PostAsync(batchUpdateUrl, content).Result

                If response.IsSuccessStatusCode Then
                    Console.WriteLine($"✅ Sheet created: {sheetName}")
                    Return "Success"
                Else
                    Dim errorContent = response.Content.ReadAsStringAsync().Result
                    Return $"Error: {response.StatusCode} - {errorContent}"
                End If
            End Using

        Catch ex As Exception
            Return $"Error creating sheet: {ex.Message}"
        End Try
    End Function

    ''' <summary>
    ''' Prepare DataTable data for Google Sheets format
    ''' </summary>
    Private Shared Function PrepareSheetData(dataTable As DataTable) As JArray
        Dim sheetData As New JArray()

        ' Add header row
        Dim headerRow As New JArray()
        For Each column As DataColumn In dataTable.Columns
            headerRow.Add(column.ColumnName)
        Next
        sheetData.Add(headerRow)

        ' Add data rows
        For Each row As DataRow In dataTable.Rows
            Dim dataRow As New JArray()
            For Each item In row.ItemArray
                If item Is DBNull.Value Then
                    dataRow.Add("")
                Else
                    dataRow.Add(item.ToString())
                End If
            Next
            sheetData.Add(dataRow)
        Next

        Return sheetData
    End Function

    ''' <summary>
    ''' Append data to existing sheet
    ''' </summary>
    Private Shared Function AppendToSheet(config As JObject, spreadsheetId As String,
                                        sheetName As String, sheetData As JArray,
                                        accessToken As String) As String
        Try
            ' Skip header row for append operations
            Dim dataOnly As New JArray()
            For i = 1 To sheetData.Count - 1
                dataOnly.Add(sheetData(i))
            Next

            If dataOnly.Count = 0 Then
                Return "No data to append"
            End If

            Dim requestBody As New JObject() From {
                {"values", dataOnly},
                {"majorDimension", "ROWS"}
            }

            Using client As New HttpClient()
                client.DefaultRequestHeaders.Add("Authorization", $"Bearer {accessToken}")

                Dim content = New StringContent(requestBody.ToString(), Encoding.UTF8, "application/json")
                Dim appendUrl = $"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheetId}/values/{HttpUtility.UrlEncode(sheetName)}:append?valueInputOption=RAW"
                Dim response = client.PostAsync(appendUrl, content).Result

                If response.IsSuccessStatusCode Then
                    Return "Success"
                Else
                    Dim errorContent = response.Content.ReadAsStringAsync().Result
                    Return $"Error: {response.StatusCode} - {errorContent}"
                End If
            End Using

        Catch ex As Exception
            Return $"Error appending to sheet: {ex.Message}"
        End Try
    End Function

    ''' <summary>
    ''' Update entire sheet with new data (replaces existing)
    ''' </summary>
    Private Shared Function UpdateEntireSheet(config As JObject, spreadsheetId As String,
                                            sheetName As String, sheetData As JArray,
                                            accessToken As String) As String
        Try
            Dim requestBody As New JObject() From {
                {"values", sheetData},
                {"majorDimension", "ROWS"}
            }

            Using client As New HttpClient()
                client.DefaultRequestHeaders.Add("Authorization", $"Bearer {accessToken}")

                Dim content = New StringContent(requestBody.ToString(), Encoding.UTF8, "application/json")
                Dim updateUrl = $"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheetId}/values/{HttpUtility.UrlEncode(sheetName)}?valueInputOption=RAW"
                Dim response = client.PutAsync(updateUrl, content).Result

                If response.IsSuccessStatusCode Then
                    Return "Success"
                Else
                    Dim errorContent = response.Content.ReadAsStringAsync().Result
                    Return $"Error: {response.StatusCode} - {errorContent}"
                End If
            End Using

        Catch ex As Exception
            Return $"Error updating sheet: {ex.Message}"
        End Try
    End Function

    ''' <summary>
    ''' Trigger AppSheet sync for updated data
    ''' </summary>
    Private Shared Function TriggerAppSheetSync(config As JObject, tableName As String) As String
        Try
            Dim appId = config("appsheet")("app_id")?.ToString()
            If String.IsNullOrEmpty(appId) Then
                Return "Error: No AppSheet app ID configured"
            End If

            ' AppSheet sync methods:
            ' 1. Webhook trigger (if configured)
            ' 2. API call to refresh data
            ' 3. Email notification

            Dim syncMethod = config("appsheet")("sync_method")?.ToString() ?? "webhook"

            Select Case syncMethod.ToLower()
                Case "webhook"
                    Return TriggerAppSheetWebhook(config, tableName)
                Case "api"
                    Return TriggerAppSheetAPI(config, tableName)
                Case Else
                    Return $"AppSheet sync queued for {tableName}"
            End Select

        Catch ex As Exception
            Return $"Error triggering AppSheet sync: {ex.Message}"
        End Try
    End Function

    ''' <summary>
    ''' Trigger AppSheet via webhook
    ''' </summary>
    Private Shared Function TriggerAppSheetWebhook(config As JObject, tableName As String) As String
        Try
            Dim webhookUrl = config("appsheet")("webhook_url")?.ToString()
            If String.IsNullOrEmpty(webhookUrl) Then
                Return "AppSheet webhook not configured"
            End If

            Dim payload As New JObject() From {
                {"table", tableName},
                {"timestamp", DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")},
                {"source", "EQ12"}
            }

            Using client As New HttpClient()
                Dim content = New StringContent(payload.ToString(), Encoding.UTF8, "application/json")
                Dim response = client.PostAsync(webhookUrl, content).Result

                If response.IsSuccessStatusCode Then
                    Return "AppSheet webhook triggered successfully"
                Else
                    Return $"AppSheet webhook failed: {response.StatusCode}"
                End If
            End Using

        Catch ex As Exception
            Return $"AppSheet webhook error: {ex.Message}"
        End Try
    End Function

    ''' <summary>
    ''' Trigger AppSheet via API
    ''' </summary>
    Private Shared Function TriggerAppSheetAPI(config As JObject, tableName As String) As String
        ' AppSheet API integration would go here
        ' This is a placeholder for future AppSheet API implementation
        Return $"AppSheet API sync initiated for {tableName}"
    End Function

    ''' <summary>
    ''' Sync multiple tables in batch
    ''' </summary>
    ''' <param name="config">Configuration object</param>
    ''' <param name="tableNames">List of table names to sync</param>
    ''' <param name="incrementalOnly">Only sync new records</param>
    ''' <returns>Batch sync results</returns>
    Public Shared Function SyncMultipleTables(config As JObject, tableNames As List(Of String),
                                             Optional incrementalOnly As Boolean = True) As Dictionary(Of String, String)
        Dim results As New Dictionary(Of String, String)

        Console.WriteLine($"📊 Starting batch sync for {tableNames.Count} tables...")

        For Each tableName In tableNames
            Try
                Dim result = SyncTable(config, tableName, Nothing, incrementalOnly)
                results(tableName) = result

                ' Small delay between syncs to avoid rate limiting
                Threading.Thread.Sleep(1000)

            Catch ex As Exception
                results(tableName) = $"Error: {ex.Message}"
            End Try
        Next

        Console.WriteLine($"✅ Batch sync completed - {results.Count} tables processed")
        Return results
    End Function

    ''' <summary>
    ''' Log sheet sync operation to database
    ''' </summary>
    Private Shared Sub LogSheetSync(tableName As String, sheetName As String,
                                  recordCount As Integer, isIncremental As Boolean)
        Try
            Using conn As New SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()

                Dim sql = "INSERT INTO sheet_syncs (table_name, sheet_name, record_count, " &
                         "is_incremental, synced_at, created_at) " &
                         "VALUES (@table_name, @sheet_name, @record_count, @is_incremental, @synced_at, @created_at)"

                Using cmd As New SQLiteCommand(sql, conn)
                    cmd.Parameters.AddWithValue("@table_name", tableName)
                    cmd.Parameters.AddWithValue("@sheet_name", sheetName)
                    cmd.Parameters.AddWithValue("@record_count", recordCount)
                    cmd.Parameters.AddWithValue("@is_incremental", isIncremental)
                    cmd.Parameters.AddWithValue("@synced_at", DateTime.UtcNow)
                    cmd.Parameters.AddWithValue("@created_at", DateTime.UtcNow)

                    cmd.ExecuteNonQuery()
                End Using
            End Using
        Catch ex As Exception
            Console.WriteLine($"⚠️ Failed to log sheet sync: {ex.Message}")
        End Try
    End Sub

    ''' <summary>
    ''' Test Google Sheets connectivity and permissions
    ''' </summary>
    ''' <param name="config">Configuration object</param>
    ''' <returns>Test result message</returns>
    Public Shared Function TestSheetsConnection(config As JObject) As String
        Try
            ' Test authentication
            Dim authTest = GoogleAuthHelper.TestConnection(config, "sheets")
            If authTest.StartsWith("❌") Then
                Return authTest
            End If

            ' Test spreadsheet access
            Dim spreadsheetId = config("google_sheets")("sheet_id")?.ToString()
            If String.IsNullOrEmpty(spreadsheetId) Then
                Return "❌ No spreadsheet ID configured in google_sheets.sheet_id"
            End If

            Dim accessToken = GoogleAuthHelper.GetAccessToken(config, "sheets")
            If accessToken.StartsWith("Error") Then
                Return $"❌ {accessToken}"
            End If

            Using client As New HttpClient()
                client.DefaultRequestHeaders.Add("Authorization", $"Bearer {accessToken}")

                Dim getUrl = $"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheetId}"
                Dim response = client.GetAsync(getUrl).Result

                If response.IsSuccessStatusCode Then
                    Dim responseContent = response.Content.ReadAsStringAsync().Result
                    Dim spreadsheetData = JObject.Parse(responseContent)
                    Dim title = spreadsheetData("properties")?.Item("title")?.ToString() ?? "Unknown"
                    Dim sheetCount = spreadsheetData("sheets")?.Count() ?? 0

                    Return $"✅ Google Sheets connection successful - '{title}' ({sheetCount} sheets)"
                Else
                    Return $"❌ Spreadsheet access failed: {response.StatusCode}"
                End If
            End Using

        Catch ex As Exception
            Return $"❌ Google Sheets test failed: {ex.Message}"
        End Try
    End Function

    ''' <summary>
    ''' Get sync statistics from database
    ''' </summary>
    ''' <returns>Sync statistics summary</returns>
    Public Shared Function GetSyncStats() As String
        Try
            Using conn As New SQLiteConnection("Data Source=Data\bankroll.db")
                conn.Open()

                Dim sql = "SELECT table_name, COUNT(*) as sync_count, " &
                         "MAX(synced_at) as last_sync, SUM(record_count) as total_records " &
                         "FROM sheet_syncs GROUP BY table_name ORDER BY last_sync DESC"

                Using cmd As New SQLiteCommand(sql, conn)
                    Using reader = cmd.ExecuteReader()
                        Dim stats As New StringBuilder()
                        stats.AppendLine("📊 Google Sheets Sync Statistics:")
                        stats.AppendLine()

                        While reader.Read()
                            Dim tableName = reader("table_name").ToString()
                            Dim syncCount = reader("sync_count").ToString()
                            Dim lastSync = Convert.ToDateTime(reader("last_sync")).ToString("yyyy-MM-dd HH:mm")
                            Dim totalRecords = reader("total_records").ToString()

                            stats.AppendLine($"  {tableName}: {syncCount} syncs, {totalRecords} records, last: {lastSync}")
                        End While

                        Return stats.ToString()
                    End Using
                End Using
            End Using
        Catch ex As Exception
            Return $"Error getting sync stats: {ex.Message}"
        End Try
    End Function
End Class
