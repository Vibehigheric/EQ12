Imports System
Imports System.IO
Imports System.Net.Http
Imports System.ServiceModel.Syndication
Imports System.Xml
Imports System.Data.SQLite
Imports System.Text.Json
Imports System.Threading.Tasks
Imports System.Security.Cryptography
Imports System.Text

Module Program
    ' Configuration class
    Public Class FeedConfig
        Public Property name As String
        Public Property type As String
        Public Property category As String
        Public Property url As String
        Public Property enabled As Boolean
        Public Property pollMinutes As Integer
    End Class

    Public Class AppConfig
        Public Property databasePath As String
        Public Property feeds As List(Of FeedConfig)
    End Class

    Private configPath As String = "C:\EQ12\WindowsDataSentinel\config\feeds.json"
    Private configuration As AppConfig
    Private httpClient As HttpClient

    Sub Main(args As String())
        Try
            ' Parse command line arguments
            If args.Length > 0 AndAlso args(0).StartsWith("--config=") Then
                configPath = args(0).Substring(9)
            End If

            Console.WriteLine("=" & New String("="c, 59))
            Console.WriteLine("Windows Data Sentinel - VB.NET Data Collector")
            Console.WriteLine("=" & New String("="c, 59))

            ' Load configuration
            LoadConfiguration()

            ' Initialize HTTP client
            httpClient = New HttpClient()
            httpClient.Timeout = TimeSpan.FromSeconds(30)

            ' Initialize database
            InitializeDatabase()

            ' Process all feeds
            ProcessAllFeeds()

            Console.WriteLine("=" & New String("="c, 59))
            Console.WriteLine("Collection complete")
            Console.WriteLine("=" & New String("="c, 59))

        Catch ex As Exception
            Console.Error.WriteLine($"FATAL ERROR: {ex.Message}")
            Console.Error.WriteLine(ex.StackTrace)
            Environment.Exit(1)
        End Try
    End Sub

    Sub LoadConfiguration()
        Try
            Dim jsonText As String = File.ReadAllText(configPath)
            configuration = JsonSerializer.Deserialize(Of AppConfig)(jsonText)
            Console.WriteLine($"Configuration loaded: {configPath}")
        Catch ex As Exception
            Throw New Exception($"Failed to load configuration: {ex.Message}", ex)
        End Try
    End Sub

    Sub InitializeDatabase()
        Try
            Dim dbPath As String = configuration.databasePath
            Dim dbDir As String = Path.GetDirectoryName(dbPath)
            
            ' Create directory if it doesn't exist
            If Not Directory.Exists(dbDir) Then
                Directory.CreateDirectory(dbDir)
            End If

            Using conn As New SQLiteConnection($"Data Source={dbPath};Version=3;")
                conn.Open()

                Using cmd As New SQLiteCommand(conn)
                    ' Create Items table
                    cmd.CommandText = "
                        CREATE TABLE IF NOT EXISTS Items (
                            Id INTEGER PRIMARY KEY AUTOINCREMENT,
                            SourceName TEXT NOT NULL,
                            Category TEXT NOT NULL,
                            ItemId TEXT NOT NULL,
                            Title TEXT,
                            Url TEXT,
                            PublishedUtc TEXT,
                            RawJson TEXT,
                            InsertedUtc TEXT NOT NULL,
                            UNIQUE(SourceName, ItemId)
                        )
                    "
                    cmd.ExecuteNonQuery()

                    ' Create indexes
                    cmd.CommandText = "CREATE INDEX IF NOT EXISTS idx_items_category ON Items(Category)"
                    cmd.ExecuteNonQuery()

                    cmd.CommandText = "CREATE INDEX IF NOT EXISTS idx_items_source ON Items(SourceName)"
                    cmd.ExecuteNonQuery()

                    cmd.CommandText = "CREATE INDEX IF NOT EXISTS idx_items_published ON Items(PublishedUtc DESC)"
                    cmd.ExecuteNonQuery()
                End Using
            End Using

            Console.WriteLine($"Database initialized: {dbPath}")

        Catch ex As Exception
            Throw New Exception($"Database initialization failed: {ex.Message}", ex)
        End Try
    End Sub

    Sub ProcessAllFeeds()
        Dim enabledFeeds = configuration.feeds.Where(Function(f) f.enabled).ToList()
        Console.WriteLine($"Processing {enabledFeeds.Count} enabled feeds (out of {configuration.feeds.Count} total)")

        For Each feed In enabledFeeds
            ProcessFeed(feed)
        Next
    End Sub

    Sub ProcessFeed(feed As FeedConfig)
        Console.WriteLine($"Processing {feed.type}: {feed.name}")

        Try
            If feed.type = "rss" Then
                ProcessRssFeed(feed)
            ElseIf feed.type = "api-json" Then
                ProcessJsonApi(feed)
            Else
                Console.WriteLine($"  [WARN] Unknown feed type: {feed.type}")
            End If
        Catch ex As Exception
            Console.Error.WriteLine($"  [ERROR] {feed.name}: {ex.Message}")
        End Try
    End Sub

    Sub ProcessRssFeed(feed As FeedConfig)
        Try
            Using reader As XmlReader = XmlReader.Create(feed.url)
                Dim syndicationFeed As SyndicationFeed = SyndicationFeed.Load(reader)
                Dim itemsAdded As Integer = 0

                For Each item In syndicationFeed.Items
                    Dim itemId As String = If(item.Id, GetHashId(item.Title.Text & item.PublishDate.ToString()))
                    Dim title As String = item.Title?.Text
                    Dim url As String = item.Links?.FirstOrDefault()?.Uri?.ToString()
                    Dim published As DateTimeOffset? = item.PublishDate

                    If UpsertItem(feed.name, feed.category, itemId, title, url, published, Nothing) Then
                        itemsAdded += 1
                    End If
                Next

                Console.WriteLine($"  → Added {itemsAdded} new items from {feed.name}")
            End Using

        Catch ex As Exception
            Throw New Exception($"RSS parsing error: {ex.Message}", ex)
        End Try
    End Sub

    Sub ProcessJsonApi(feed As FeedConfig)
        Try
            Dim response = httpClient.GetStringAsync(feed.url).Result
            Dim jsonDoc = JsonDocument.Parse(response)
            Dim itemsAdded As Integer = 0

            ' Try to find results array
            Dim itemsArray As JsonElement? = Nothing

            If jsonDoc.RootElement.ValueKind = JsonValueKind.Array Then
                itemsArray = jsonDoc.RootElement
            ElseIf jsonDoc.RootElement.ValueKind = JsonValueKind.Object Then
                ' Try common patterns
                For Each propName In {"results", "data", "items", "hits", "response"}
                    Dim prop As JsonElement
                    If jsonDoc.RootElement.TryGetProperty(propName, prop) AndAlso prop.ValueKind = JsonValueKind.Array Then
                        itemsArray = prop
                        Exit For
                    End If
                Next

                ' If no array found, treat whole object as single item
                If Not itemsArray.HasValue Then
                    itemsArray = New JsonElement() ' Will handle as single object below
                End If
            End If

            ' Process items
            If itemsArray.HasValue AndAlso itemsArray.Value.ValueKind = JsonValueKind.Array Then
                For Each item In itemsArray.Value.EnumerateArray()
                    ProcessJsonItem(feed, item, itemsAdded)
                Next
            Else
                ' Single object
                ProcessJsonItem(feed, jsonDoc.RootElement, itemsAdded)
            End If

            Console.WriteLine($"  → Added {itemsAdded} new items from {feed.name}")

        Catch ex As Exception
            Throw New Exception($"API error: {ex.Message}", ex)
        End Try
    End Sub

    Sub ProcessJsonItem(feed As FeedConfig, item As JsonElement, ByRef itemsAdded As Integer)
        ' Extract common fields (flexible)
        Dim itemId As String = GetJsonValue(item, {"id", "citation", "guid"})
        If String.IsNullOrEmpty(itemId) Then
            itemId = GetHashId(item.GetRawText())
        End If

        Dim title As String = GetJsonValue(item, {"case_name", "title", "name", "headline"})
        Dim url As String = GetJsonValue(item, {"absolute_url", "url", "link", "href"})
        
        ' Parse date
        Dim published As DateTimeOffset? = Nothing
        Dim dateStr As String = GetJsonValue(item, {"date_filed", "date_created", "published", "created_at", "timestamp"})
        If Not String.IsNullOrEmpty(dateStr) Then
            Dim parsedDate As DateTimeOffset
            If DateTimeOffset.TryParse(dateStr, parsedDate) Then
                published = parsedDate
            End If
        End If

        Dim rawJson As String = item.GetRawText()

        If UpsertItem(feed.name, feed.category, itemId, title, url, published, rawJson) Then
            itemsAdded += 1
        End If
    End Sub

    Function GetJsonValue(element As JsonElement, propertyNames As String()) As String
        For Each propName In propertyNames
            Dim prop As JsonElement
            If element.TryGetProperty(propName, prop) Then
                If prop.ValueKind = JsonValueKind.String Then
                    Return prop.GetString()
                ElseIf prop.ValueKind = JsonValueKind.Number Then
                    Return prop.GetInt64().ToString()
                End If
            End If
        Next
        Return Nothing
    End Function

    Function GetHashId(input As String) As String
        Using md5 As MD5 = MD5.Create()
            Dim hash = md5.ComputeHash(Encoding.UTF8.GetBytes(input))
            Return BitConverter.ToString(hash).Replace("-", "").ToLower()
        End Using
    End Function

    Function UpsertItem(
        sourceName As String,
        category As String,
        itemId As String,
        title As String,
        url As String,
        published As DateTimeOffset?,
        rawJson As String
    ) As Boolean
        Using conn As New SQLiteConnection($"Data Source={configuration.databasePath};Version=3;")
            conn.Open()

            Using cmd As New SQLiteCommand(conn)
                cmd.CommandText = "
                    INSERT OR IGNORE INTO Items 
                    (SourceName, Category, ItemId, Title, Url, PublishedUtc, RawJson, InsertedUtc)
                    VALUES (@sourceName, @category, @itemId, @title, @url, @published, @rawJson, @inserted)
                "
                cmd.Parameters.AddWithValue("@sourceName", sourceName)
                cmd.Parameters.AddWithValue("@category", category)
                cmd.Parameters.AddWithValue("@itemId", itemId)
                cmd.Parameters.AddWithValue("@title", If(title, DBNull.Value))
                cmd.Parameters.AddWithValue("@url", If(url, DBNull.Value))
                cmd.Parameters.AddWithValue("@published", If(published?.UtcDateTime.ToString("o"), DBNull.Value))
                cmd.Parameters.AddWithValue("@rawJson", If(rawJson, DBNull.Value))
                cmd.Parameters.AddWithValue("@inserted", DateTimeOffset.UtcNow.ToString("o"))

                Dim rowsAffected = cmd.ExecuteNonQuery()
                Return rowsAffected > 0
            End Using
        End Using
    End Function
End Module
