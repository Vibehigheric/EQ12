Imports System.Threading.Tasks
Imports System.Data
Imports Newtonsoft.Json
Imports Newtonsoft.Json.Linq
Imports Google.Cloud.BigQuery.V2
Imports System.Collections.Generic

''' <summary>
''' BigQuery Data Warehouse Client for EQ12
''' Handles data synchronization, queries, and analytics for the cloud data warehouse
''' '''
Public Class BigQueryClient
    Private ReadOnly _client As Google.Cloud.BigQuery.V2.BigQueryClient
    Private ReadOnly _projectId As String
    Private ReadOnly _datasetId As String

    Public Sub New(gcpAuth As GCPAuth, datasetId As String)
        _client = gcpAuth.GetBigQueryClient()
        _projectId = gcpAuth.ProjectId
        _datasetId = datasetId
    End Sub

    ''' <summary>
    ''' Ensure dataset and required tables exist
    ''' '''
    Public Sub EnsureDatasetAndTables()
        Try
            ' Create dataset if it doesn't exist
            Dim dataset = _client.GetOrCreateDataset(_datasetId)
            Console.WriteLine($"✅ Dataset {_datasetId} ready")

            ' Create core tables
            CreateCoreTablesIfNotExist()

        Catch ex As Exception
            Console.WriteLine($"❌ Dataset/table creation failed: {ex.Message}")
            Throw
        End Try
    End Sub

    ''' <summary>
    ''' Upsert data from DataTable to BigQuery table
    ''' '''
    Public Sub UpsertFromDataTable(tableName As String, dt As DataTable)
        Try
            If dt Is Nothing OrElse dt.Rows.Count = 0 Then
                Console.WriteLine($"⚠️ No data to upsert for table {tableName}")
                Return
            End If

            Dim tableRef = _client.GetTableReference(_datasetId, tableName)
            Dim table = _client.GetTable(tableRef)

            ' Convert DataTable to BigQuery rows
            Dim rows As New List(Of BigQueryInsertRow)()

            For Each row As DataRow In dt.Rows
                Dim bqRow As New BigQueryInsertRow()

                For Each column As DataColumn In dt.Columns
                    Dim value = row(column)
                    If value IsNot DBNull.Value Then
                        bqRow(column.ColumnName.ToLower()) = value
                    End If
                Next

                rows.Add(bqRow)
            Next

            ' Insert data
            Dim result = _client.InsertRows(table, rows)

            If result.Any() Then
                Console.WriteLine($"⚠️ BigQuery insert errors: {String.Join(", ", result.Select(Function(e) e.Error.Message))}")
            Else
                Console.WriteLine($"✅ Upserted {rows.Count} rows to {tableName}")
            End If

        Catch ex As Exception
            Console.WriteLine($"❌ BigQuery upsert failed: {ex.Message}")
            Throw
        End Try
    End Sub

    ''' <summary>
    ''' Run SQL query and return results as DataTable
    ''' '''
    Public Function RunQuery(sql As String) As DataTable
        Try
            Dim query = _client.CreateQueryJob(sql, Nothing)
            Dim results = query.GetQueryResults()

            ' Convert results to DataTable
            Dim dt As New DataTable()

            ' Add columns
            For Each field In results.Schema.Fields
                Dim columnType = GetSystemType(field.Type)
                dt.Columns.Add(field.Name, columnType)
            Next

            ' Add rows
            For Each row In results
                Dim dataRow = dt.NewRow()

                For i = 0 To row.RawRow.F.Count - 1
                    Dim field = results.Schema.Fields(i)
                    Dim value = row.RawRow.F(i).V

                    If value IsNot Nothing Then
                        dataRow(field.Name) = ConvertBigQueryValue(value, field.Type)
                    End If
                Next

                dt.Rows.Add(dataRow)
            Next

            Console.WriteLine($"✅ Query returned {dt.Rows.Count} rows")
            Return dt

        Catch ex As Exception
            Console.WriteLine($"❌ BigQuery query failed: {ex.Message}")
            Throw
        End Try
    End Function

    ''' <summary>
    ''' Get table row count for monitoring
    ''' '''
    Public Function GetTableRowCount(tableName As String) As Long
        Try
            Dim sql = $"SELECT COUNT(*) as row_count FROM `{_projectId}.{_datasetId}.{tableName}`"
            Dim dt = RunQuery(sql)

            If dt.Rows.Count > 0 Then
                Return Convert.ToInt64(dt.Rows(0)("row_count"))
            End If

            Return 0

        Catch ex As Exception
            Console.WriteLine($"❌ Row count query failed: {ex.Message}")
            Return -1
        End Try
    End Function

    ''' <summary>
    ''' Create core EQ12 tables in BigQuery
    ''' '''
    Private Sub CreateCoreTablesIfNotExist()
        Dim tableDDLs As New Dictionary(Of String, String) From {
            {"odds", "
                CREATE TABLE IF NOT EXISTS `{0}.{1}.odds` (
                  event_id STRING,
                  ts TIMESTAMP,
                  sport STRING,
                  market STRING,
                  selection STRING,
                  book STRING,
                  odds INT64
                )
                PARTITION BY DATE(ts)
                CLUSTER BY sport, event_id
            "},
            {"arb_opportunities", "
                CREATE TABLE IF NOT EXISTS `{0}.{1}.arb_opportunities` (
                  ts TIMESTAMP,
                  event_id STRING,
                  sideA STRING,
                  bookA STRING,
                  oddsA INT64,
                  sideB STRING,
                  bookB STRING,
                  oddsB INT64,
                  arb_pct FLOAT64,
                  bankroll FLOAT64,
                  lock_profit FLOAT64,
                  mode STRING
                )
                PARTITION BY DATE(ts)
                CLUSTER BY event_id
            "},
            {"sports_metrics", "
                CREATE TABLE IF NOT EXISTS `{0}.{1}.sports_metrics` (
                  ts TIMESTAMP,
                  sport STRING,
                  team_or_player STRING,
                  metric_name STRING,
                  metric_value FLOAT64,
                  source STRING
                )
                PARTITION BY DATE(ts)
                CLUSTER BY sport, team_or_player
            "},
            {"staking_log", "
                CREATE TABLE IF NOT EXISTS `{0}.{1}.staking_log` (
                  ts TIMESTAMP,
                  event_id STRING,
                  market STRING,
                  selection STRING,
                  decimal_odds FLOAT64,
                  edge FLOAT64,
                  p FLOAT64,
                  kelly_fraction FLOAT64,
                  stake FLOAT64,
                  mode STRING
                )
                PARTITION BY DATE(ts)
                CLUSTER BY event_id
            "}
        }

        For Each kvp In tableDDLs
            Try
                Dim sql = String.Format(kvp.Value, _projectId, _datasetId)
                _client.CreateQueryJob(sql, Nothing).GetQueryResults()
                Console.WriteLine($"✅ Table {kvp.Key} ready")
            Catch ex As Exception
                Console.WriteLine($"⚠️ Table creation warning for {kvp.Key}: {ex.Message}")
            End Try
        Next
    End Sub

    ' Helper methods for type conversion
    Private Function GetSystemType(bqType As BigQueryDbType) As Type
        Select Case bqType
            Case BigQueryDbType.String : Return GetType(String)
            Case BigQueryDbType.Int64 : Return GetType(Long)
            Case BigQueryDbType.Float64 : Return GetType(Double)
            Case BigQueryDbType.Bool : Return GetType(Boolean)
            Case BigQueryDbType.Timestamp : Return GetType(DateTime)
            Case BigQueryDbType.Date : Return GetType(DateTime)
            Case Else : Return GetType(String)
        End Select
    End Function

    Private Function ConvertBigQueryValue(value As Object, bqType As BigQueryDbType) As Object
        If value Is Nothing Then Return DBNull.Value

        Select Case bqType
            Case BigQueryDbType.Int64 : Return Convert.ToInt64(value)
            Case BigQueryDbType.Float64 : Return Convert.ToDouble(value)
            Case BigQueryDbType.Bool : Return Convert.ToBoolean(value)
            Case BigQueryDbType.Timestamp, BigQueryDbType.Date
                Return DateTime.Parse(value.ToString())
            Case Else : Return value.ToString()
        End Select
    End Function
End Class
