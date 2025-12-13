Option Strict On
Option Explicit On

Imports System.IO
Imports System.Text.Json

Namespace EQ12.Core.FileScanner

    ''' <summary>
    ''' Scans EQ12 workspace for all betting automation files, scripts, configs, and APIs.
    ''' Generates a comprehensive manifest JSON for the dashboard to consume.
    ''' </summary>
    Public Class Eq12Scanner

        Private ReadOnly _rootPath As String
        Private ReadOnly _manifest As Manifest

        Public Sub New(rootPath As String)
            If String.IsNullOrWhiteSpace(rootPath) Then
                Throw New ArgumentException("Root path cannot be empty", NameOf(rootPath))
            End If

            If Not Directory.Exists(rootPath) Then
                Throw New DirectoryNotFoundException($"Root path not found: {rootPath}")
            End If

            _rootPath = rootPath
            _manifest = New Manifest() With {
                .Projects = New List(Of ProjectInfo)(),
                .Apis = New List(Of ApiInfo)(),
                .Configs = New List(Of ConfigInfo)(),
                .Databases = New List(Of DatabaseInfo)(),
                .Logs = New List(Of LogInfo)()
            }
        End Sub

        ''' <summary>
        ''' Perform full workspace scan and generate manifest
        ''' </summary>
        Public Function Scan() As Manifest
            Console.WriteLine($"🔍 Scanning EQ12 workspace: {_rootPath}")

            ' Scan for different file types
            ScanPythonScripts()
            ScanPowerShellScripts()
            ScanVBNETProjects()
            ScanConfigurations()
            ScanDatabases()
            ScanLogFiles()
            ScanApiConfigs()

            Console.WriteLine($"✅ Scan complete:")
            Console.WriteLine($"   - Projects: {_manifest.Projects.Count}")
            Console.WriteLine($"   - APIs: {_manifest.Apis.Count}")
            Console.WriteLine($"   - Configs: {_manifest.Configs.Count}")
            Console.WriteLine($"   - Databases: {_manifest.Databases.Count}")
            Console.WriteLine($"   - Logs: {_manifest.Logs.Count}")

            Return _manifest
        End Function

        Private Sub ScanPythonScripts()
            Dim searchPattern As String = "*.py"
            Dim pythonFiles = Directory.EnumerateFiles(_rootPath, searchPattern, SearchOption.AllDirectories) _
                .Where(Function(f) Not f.Contains("\venv\") AndAlso _
                                   Not f.Contains("\.venv\") AndAlso _
                                   Not f.Contains("\__pycache__\") AndAlso _
                                   Not f.Contains("\site-packages\"))

            For Each file In pythonFiles
                Dim fileName = Path.GetFileNameWithoutExtension(file)
                Dim relativePath = file.Replace(_rootPath, "").TrimStart("\"c)

                ' Classify Python script by name patterns
                Dim tags As New List(Of String)()
                Dim scriptType As String = "python_script"

                If fileName.Contains("parlay", StringComparison.OrdinalIgnoreCase) Then
                    tags.Add("parlay")
                    tags.Add("betting")
                    scriptType = "betting_engine"
                End If

                If fileName.Contains("odds", StringComparison.OrdinalIgnoreCase) Then
                    tags.Add("odds")
                    tags.Add("api")
                    scriptType = "odds_connector"
                End If

                If fileName.Contains("weather", StringComparison.OrdinalIgnoreCase) Then
                    tags.Add("weather")
                    tags.Add("api")
                    scriptType = "weather_connector"
                End If

                If fileName.Contains("telegram", StringComparison.OrdinalIgnoreCase) OrElse _
                   fileName.Contains("bot", StringComparison.OrdinalIgnoreCase) Then
                    tags.Add("telegram")
                    tags.Add("alerts")
                    scriptType = "telegram_bot"
                End If

                If fileName.Contains("sec_13f", StringComparison.OrdinalIgnoreCase) OrElse _
                   fileName.Contains("scraper", StringComparison.OrdinalIgnoreCase) Then
                    tags.Add("scraper")
                    tags.Add("data_ingestion")
                    scriptType = "scraper"
                End If

                If fileName.Contains("prompt", StringComparison.OrdinalIgnoreCase) Then
                    tags.Add("ai")
                    tags.Add("prompts")
                    scriptType = "ai_executor"
                End If

                _manifest.Projects.Add(New ProjectInfo With {
                    .Name = fileName,
                    .Type = scriptType,
                    .Path = file,
                    .RelativePath = relativePath,
                    .Tags = tags,
                    .Language = "Python",
                    .LastModified = File.GetLastWriteTime(file),
                    .SizeBytes = New FileInfo(file).Length
                })
            Next
        End Sub

        Private Sub ScanPowerShellScripts()
            Dim searchPattern As String = "*.ps1"
            Dim psFiles = Directory.EnumerateFiles(_rootPath, searchPattern, SearchOption.AllDirectories)

            For Each file In psFiles
                Dim fileName = Path.GetFileNameWithoutExtension(file)
                Dim relativePath = file.Replace(_rootPath, "").TrimStart("\"c)

                Dim tags As New List(Of String)()
                Dim scriptType As String = "powershell_script"

                If fileName.Contains("PROMPT", StringComparison.OrdinalIgnoreCase) Then
                    tags.Add("ai")
                    tags.Add("automation")
                    scriptType = "automation_wrapper"
                End If

                If fileName.Contains("SCAN", StringComparison.OrdinalIgnoreCase) OrElse _
                   fileName.Contains("SYSTEM", StringComparison.OrdinalIgnoreCase) Then
                    tags.Add("system")
                    tags.Add("monitoring")
                    scriptType = "system_monitor"
                End If

                If fileName.Contains("SEC_13F", StringComparison.OrdinalIgnoreCase) Then
                    tags.Add("scraper")
                    tags.Add("finance")
                    scriptType = "scraper_wrapper"
                End If

                _manifest.Projects.Add(New ProjectInfo With {
                    .Name = fileName,
                    .Type = scriptType,
                    .Path = file,
                    .RelativePath = relativePath,
                    .Tags = tags,
                    .Language = "PowerShell",
                    .LastModified = File.GetLastWriteTime(file),
                    .SizeBytes = New FileInfo(file).Length
                })
            Next
        End Sub

        Private Sub ScanVBNETProjects()
            Dim searchPattern As String = "*.vbproj"
            Dim vbprojFiles = Directory.EnumerateFiles(_rootPath, searchPattern, SearchOption.AllDirectories) _
                .Where(Function(f) Not f.Contains("\obj\") AndAlso Not f.Contains("\bin\"))

            For Each file In vbprojFiles
                Dim projectName = Path.GetFileNameWithoutExtension(file)
                Dim relativePath = file.Replace(_rootPath, "").TrimStart("\"c)

                _manifest.Projects.Add(New ProjectInfo With {
                    .Name = projectName,
                    .Type = "vbnet_project",
                    .Path = file,
                    .RelativePath = relativePath,
                    .Tags = New List(Of String) From {"vbnet", "windows"},
                    .Language = "VB.NET",
                    .LastModified = File.GetLastWriteTime(file),
                    .SizeBytes = New FileInfo(file).Length
                })
            Next
        End Sub

        Private Sub ScanConfigurations()
            ' Scan for .json config files
            Dim jsonFiles = Directory.EnumerateFiles(_rootPath, "*.json", SearchOption.AllDirectories) _
                .Where(Function(f) Not f.Contains("\node_modules\") AndAlso _
                                   Not f.Contains("\bin\") AndAlso _
                                   Not f.Contains("\obj\"))

            For Each file In jsonFiles
                Dim fileName = Path.GetFileName(file)
                If fileName.Equals("data_sources_registry.json", StringComparison.OrdinalIgnoreCase) OrElse _
                   fileName.Contains("config", StringComparison.OrdinalIgnoreCase) Then

                    _manifest.Configs.Add(New ConfigInfo With {
                        .Name = Path.GetFileNameWithoutExtension(file),
                        .Path = file,
                        .Type = "json",
                        .LastModified = File.GetLastWriteTime(file)
                    })
                End If
            Next

            ' Scan for .env files
            Dim envFiles = Directory.EnumerateFiles(_rootPath, ".env*", SearchOption.AllDirectories)
            For Each file In envFiles
                _manifest.Configs.Add(New ConfigInfo With {
                    .Name = Path.GetFileName(file),
                    .Path = file,
                    .Type = "env",
                    .LastModified = File.GetLastWriteTime(file)
                })
            Next
        End Sub

        Private Sub ScanDatabases()
            ' Scan for SQLite databases
            Dim dbFiles = Directory.EnumerateFiles(_rootPath, "*.db", SearchOption.AllDirectories)

            For Each file In dbFiles
                Dim dbName = Path.GetFileNameWithoutExtension(file)
                Dim sizeBytes = New FileInfo(file).Length

                _manifest.Databases.Add(New DatabaseInfo With {
                    .Name = dbName,
                    .Path = file,
                    .Type = "sqlite",
                    .SizeBytes = sizeBytes,
                    .SizeMB = Math.Round(sizeBytes / 1024.0 / 1024.0, 2),
                    .LastModified = File.GetLastWriteTime(file)
                })
            Next
        End Sub

        Private Sub ScanLogFiles()
            If Not Directory.Exists(Path.Combine(_rootPath, "logs")) Then
                Return
            End If

            Dim logFiles = Directory.EnumerateFiles(Path.Combine(_rootPath, "logs"), "*.*", SearchOption.AllDirectories) _
                .Where(Function(f) f.EndsWith(".log") OrElse f.EndsWith(".txt") OrElse f.EndsWith(".json"))

            For Each file In logFiles
                Dim sizeBytes = New FileInfo(file).Length

                _manifest.Logs.Add(New LogInfo With {
                    .Name = Path.GetFileName(file),
                    .Path = file,
                    .SizeBytes = sizeBytes,
                    .SizeMB = Math.Round(sizeBytes / 1024.0 / 1024.0, 2),
                    .LastModified = File.GetLastWriteTime(file)
                })
            Next
        End Sub

        Private Sub ScanApiConfigs()
            ' Load data_sources_registry.json if it exists
            Dim registryPath = Path.Combine(_rootPath, "data", "data_sources_registry.json")
            If File.Exists(registryPath) Then
                Try
                    Dim jsonContent = File.ReadAllText(registryPath)
                    Dim registry = JsonSerializer.Deserialize(Of DataSourceRegistry)(jsonContent)

                    If registry IsNot Nothing AndAlso registry.DataSources IsNot Nothing Then
                        For Each source In registry.DataSources
                            If source.Enabled Then
                                _manifest.Apis.Add(New ApiInfo With {
                                    .Name = source.Name,
                                    .Category = source.Category,
                                    .BaseUrl = source.BaseUrl,
                                    .RequiresAuth = source.RequiresAuth,
                                    .IsFree = source.Cost = "FREE",
                                    .Reliability = source.Reliability,
                                    .ConfigFile = registryPath
                                })
                            End If
                        Next
                    End If
                Catch ex As Exception
                    Console.WriteLine($"⚠️  Failed to parse data sources registry: {ex.Message}")
                End Try
            End If
        End Sub

        ''' <summary>
        ''' Save manifest to JSON file
        ''' </summary>
        Public Sub SaveManifest(manifest As Manifest, outputPath As String)
            Dim options = New JsonSerializerOptions With {
                .WriteIndented = True,
                .PropertyNamingPolicy = JsonNamingPolicy.CamelCase
            }

            Dim json = JsonSerializer.Serialize(manifest, options)
            File.WriteAllText(outputPath, json)

            Console.WriteLine($"💾 Manifest saved: {outputPath}")
        End Sub

    End Class

    ' ============================================================================
    ' DATA MODELS
    ' ============================================================================

    Public Class Manifest
        Public Property Projects As List(Of ProjectInfo)
        Public Property Apis As List(Of ApiInfo)
        Public Property Configs As List(Of ConfigInfo)
        Public Property Databases As List(Of DatabaseInfo)
        Public Property Logs As List(Of LogInfo)
        Public Property ScanTimestamp As DateTime = DateTime.UtcNow
    End Class

    Public Class ProjectInfo
        Public Property Name As String
        Public Property Type As String
        Public Property Path As String
        Public Property RelativePath As String
        Public Property Tags As List(Of String)
        Public Property Language As String
        Public Property LastModified As DateTime
        Public Property SizeBytes As Long
    End Class

    Public Class ApiInfo
        Public Property Name As String
        Public Property Category As String
        Public Property BaseUrl As String
        Public Property RequiresAuth As Boolean
        Public Property IsFree As Boolean
        Public Property Reliability As Double
        Public Property ConfigFile As String
    End Class

    Public Class ConfigInfo
        Public Property Name As String
        Public Property Path As String
        Public Property Type As String
        Public Property LastModified As DateTime
    End Class

    Public Class DatabaseInfo
        Public Property Name As String
        Public Property Path As String
        Public Property Type As String
        Public Property SizeBytes As Long
        Public Property SizeMB As Double
        Public Property LastModified As DateTime
    End Class

    Public Class LogInfo
        Public Property Name As String
        Public Property Path As String
        Public Property SizeBytes As Long
        Public Property SizeMB As Double
        Public Property LastModified As DateTime
    End Class

    ' Helper class for parsing data_sources_registry.json
    Public Class DataSourceRegistry
        Public Property DataSources As List(Of DataSource)
    End Class

    Public Class DataSource
        Public Property Name As String
        Public Property Category As String
        Public Property BaseUrl As String
        Public Property RequiresAuth As Boolean
        Public Property Cost As String
        Public Property Enabled As Boolean
        Public Property Reliability As Double
    End Class

End Namespace
