' EQ12 CLI Main Dispatcher with X Ads API Integration v3.0
' Complete command-line interface with enhanced X API and X Ads API support

Imports System
Imports System.Threading.Tasks
Imports Microsoft.Extensions.Configuration
Imports Microsoft.Extensions.Logging
Imports Microsoft.Extensions.DependencyInjection

Module EQ12CliMainProgram

    Private _logger As ILogger
    Private _config As IConfiguration

    Public Async Function Main(args As String()) As Task(Of Integer)
        Try
            ' Initialize configuration and logging
            SetupConfiguration()
            SetupLogging()

            _logger?.LogInformation("???? EQ12 CLI v3.0 with X Ads API Integration starting...")

            ' Handle empty args
            If args.Length = 0 Then
                ShowMainUsage()
                Return 0
            End If

            ' Get the main command
            Dim mainCommand = args(0).ToLower()

            ' Initialize the CLI extension
            Dim cliExtension As New Eq12CliGitHubExtension()
            cliExtension.Initialize(_logger, _config)

            ' Route to appropriate command handler
            Select Case mainCommand
                ' Enhanced X API Commands
                Case "x-post"
                    Return Await cliExtension.HandleXPostEnhancedCommand(args)
                Case "x-thread"
                    Return Await cliExtension.HandleXThreadEnhancedCommand(args)
                Case "x-search"
                    Return Await cliExtension.HandleXSearchEnhancedCommand(args)
                Case "x-oauth"
                    Return Await cliExtension.HandleXOAuthCommand(args)
                Case "x-monitor"
                    Return Await cliExtension.HandleXMonitorCommand(args)
                Case "x-media"
                    Return Await cliExtension.HandleXMediaCommand(args)

                ' NEW: X Ads API Commands
                Case "xads-campaign"
                    Return Await cliExtension.HandleXAdsCampaignCommand(args)
                Case "xads-creative"
                    Return Await cliExtension.HandleXAdsCreativeCommand(args)
                Case "xads-report"
                    Return Await cliExtension.HandleXAdsReportCommand(args)

                ' Copilot metrics commands
                Case "metrics-sync"
                    Return Await cliExtension.HandleMetricsSyncCommand(args)
                Case "metrics-report"
                    Return Await cliExtension.HandleMetricsReportCommand(args)
                Case "metrics-diff"
                    Return Await cliExtension.HandleMetricsDiffCommand(args)
                ' Convenience shortcuts for X Ads
                Case "xads-create"
                    ' Shortcut for campaign creation
                    Dim newArgs = {"xads-campaign", "create"}.Concat(args.Skip(1)).ToArray()
                    Return Await cliExtension.HandleXAdsCampaignCommand(newArgs)
                Case "xads-upload"
                    ' Shortcut for creative upload
                    Dim newArgs = {"xads-creative", "upload"}.Concat(args.Skip(1)).ToArray()
                    Return Await cliExtension.HandleXAdsCreativeCommand(newArgs)
                Case "xads-stats"
                    ' Shortcut for campaign stats
                    Dim newArgs = {"xads-campaign", "stats"}.Concat(args.Skip(1)).ToArray()
                    Return Await cliExtension.HandleXAdsCampaignCommand(newArgs)

                ' Help and information
                Case "help", "--help", "-h"
                    ShowMainUsage()
                    Return 0
                Case "version", "--version", "-v"
                    ShowVersion()
                    Return 0

                ' Unknown command
                Case Else
                    Console.WriteLine($"??? Unknown command: {mainCommand}")
                    Console.WriteLine("")
                    ShowMainUsage()
                    Return 1
            End Select

        Catch ex As Exception
            _logger?.LogError(ex, "Fatal error in EQ12 CLI")
            Console.WriteLine($"???? Fatal Error: {ex.Message}")
            Console.WriteLine("???? Stack trace has been logged for debugging")
            Return 1
        End Try
    End Function

    Private Sub SetupConfiguration()
        Dim builder = New ConfigurationBuilder()
        builder.AddJsonFile("appsettings.json", optional:=True)
        builder.AddEnvironmentVariables()
        _config = builder.Build()
    End Sub

    Private Sub SetupLogging()
        Dim serviceCollection As New ServiceCollection()
        serviceCollection.AddLogging(Function(builder)
                                         builder.AddConsole()
                                         builder.SetMinimumLevel(LogLevel.Information)
                                         Return builder
                                     End Function)

        Dim serviceProvider = serviceCollection.BuildServiceProvider()
        _logger = serviceProvider.GetService(Of ILogger(Of Object))()
    End Sub

    Private Sub ShowMainUsage()
        Console.WriteLine("???? EQ12 CLI v3.0 - Complete X API and X Ads API Integration")
        Console.WriteLine("================================================================")
        Console.WriteLine("")
        Console.WriteLine("???? X API Commands (Organic Content):")
        Console.WriteLine("  x-post       Post tweets with media, threads, scheduling")
        Console.WriteLine("  x-thread     Create tweet threads")
        Console.WriteLine("  x-search     Search tweets with advanced filters")
        Console.WriteLine("  x-oauth      Manage OAuth tokens")
        Console.WriteLine("  x-monitor    Real-time engagement monitoring")
        Console.WriteLine("  x-media      Media upload and management")
        Console.WriteLine("")
        Console.WriteLine("???? X Ads API Commands (Paid Advertising):")
        Console.WriteLine("  xads-campaign    Campaign management (create, list, update, stats)")
        Console.WriteLine("  xads-creative    Creative management (upload, promote-tweet)")
        Console.WriteLine("  xads-report      Analytics and performance reports")
        Console.WriteLine("")
        Console.WriteLine("??? Quick Shortcuts:")
        Console.WriteLine("  xads-create      Quick campaign creation")
        Console.WriteLine("  xads-upload      Quick creative upload")
        Console.WriteLine("  xads-stats       Quick campaign statistics")
        Console.WriteLine("")
        Console.WriteLine("???? Examples:")
        Console.WriteLine("  eq12 x-post ""Hello World!"" --media ""image.jpg""")
        Console.WriteLine("  eq12 x-search ""#crypto"" --max-results 50")
        Console.WriteLine("  eq12 xads-create ""My Campaign"" --budget 100")
        Console.WriteLine("  eq12 xads-upload ""banner.jpg"" --account-id ""abc123""")
        Console.WriteLine("  eq12 xads-stats --campaign-id ""xyz789"" --days 7")
        Console.WriteLine("")
        Console.WriteLine("??????  For detailed help on any command, use: eq12 <command> --help")
        Console.WriteLine("")
        Console.WriteLine("???? Setup Required:")
        Console.WriteLine("  1. Run 'eq12 x-oauth setup' to configure API access")
        Console.WriteLine("  2. Ensure you have X Ads API access for advertising commands")
        Console.WriteLine("  3. Set environment variables: TELEGRAM_BOT_TOKEN, BITLY_ACCESS_TOKEN (optional)")
        Console.WriteLine("")
        Console.WriteLine("???? Data Location: C:\EQ12\logs")
        Console.WriteLine("???? GitHub: https://github.com/your-org/EQ12")
    End Sub

    Private Sub ShowVersion()
        Console.WriteLine("???? EQ12 CLI Version Information")
        Console.WriteLine("===============================")
        Console.WriteLine("Version: 3.0")
        Console.WriteLine("Build: Enhanced X Ads API Integration")
        Console.WriteLine("Features: X API, X Ads API, OAuth2, Media Upload, Analytics, Reporting")
        Console.WriteLine("Platform: Windows/.NET")
        Console.WriteLine("Data Schema: v3.1 (X API + X Ads API)")
        Console.WriteLine("")
        Console.WriteLine("???? Endpoints:")
        Console.WriteLine("  X API: https://api.x.com/2")
        Console.WriteLine("  X Ads API: https://ads-api.x.com/12")
        Console.WriteLine("  OAuth: https://x.com/i/oauth2")
        Console.WriteLine("")
        Console.WriteLine("???? Supported Operations:")
        Console.WriteLine("  ??? Tweet posting and threading")
        Console.WriteLine("  ??? Advanced search and analytics")
        Console.WriteLine("  ??? Media upload (images, videos, GIFs)")
        Console.WriteLine("  ??? Campaign creation and management")
        Console.WriteLine("  ??? Creative upload and promotion")
        Console.WriteLine("  ??? Audience targeting and management")
        Console.WriteLine("  ??? Comprehensive analytics and reporting")
        Console.WriteLine("  ??? Auto-promotion of high-performing content")
        Console.WriteLine("  ??? A/B testing framework")
        Console.WriteLine("")
    End Sub

End Module

' Extension to support initialization
Partial Public Class Eq12CliGitHubExtension
    Public Sub Initialize(logger As ILogger, config As IConfiguration)
        _logger = logger
        _config = config
    End Sub
End Class


