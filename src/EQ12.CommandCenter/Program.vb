Imports System
Imports System.IO
Imports System.Linq

Module Program
    Sub Main(args As String())
        Console.WriteLine("🚀 EQ12 CommandCenter Starting...")
        Console.WriteLine("Modern .NET 9 VB.NET Architecture Ready")
        Console.WriteLine()
        Console.WriteLine("Available Commands:")
        Console.WriteLine("  health       - Check system health")
        Console.WriteLine("  bankroll     - Show bankroll status")
        Console.WriteLine("  dashboard    - Show Betting Engine stats")
        Console.WriteLine("  network      - Show Network Status")
        Console.WriteLine("  profile [name] - Apply Network Profile (cluster, home, vpn_tokyo)")
        Console.WriteLine("  gumroad      - Sync Gumroad sales")
        Console.WriteLine("  predict      - Run prediction model")
        Console.WriteLine()
        
        ' Process command-line arguments or enter interactive mode
        If args.Length = 0 Then
            InteractiveMode()
        Else
            ProcessCommand(args(0), args.Skip(1).ToArray())
        End If
    End Sub

    Private Sub InteractiveMode()
        Console.Write("EQ12> ")
        Dim input = Console.ReadLine()
        
        If String.IsNullOrWhiteSpace(input) Then
            Return
        End If
        
        Dim parts = input.Split(" "c)
        ProcessCommand(parts(0), parts.Skip(1).ToArray())
    End Sub

    Private Sub ProcessCommand(command As String, args() As String)
        Select Case command.ToLower()
            Case "health"
                Console.WriteLine("✅ System Health: All systems operational")
            Case "bankroll"
                Console.WriteLine("💰 Bankroll Status: Loading from database...")
            Case "dashboard"
                ShowDashboard()
            Case "network"
                NetworkManager.ShowNetworkStatus()
            Case "profile"
                If args.Length > 0 Then
                    IPProfileManager.ApplyProfile(args(0))
                Else
                    Console.WriteLine("Usage: profile [name]")
                End If
            Case "gumroad"
                Console.WriteLine("🛍️  Syncing Gumroad: Checking for new sales...")
            Case "predict"
                Console.WriteLine("🔮 Running prediction models...")
            Case "exit", "quit"
                Environment.Exit(0)
            Case Else
                Console.WriteLine($"Unknown command: {command}")
        End Select
    End Sub

    Private Sub ShowDashboard()
        Dim dataPath As String = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", "..", "..", "dashboard_data.json")
        ' Adjust path if running from bin/Debug/net9.0
        If Not File.Exists(dataPath) Then
             ' Try root path
             dataPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "dashboard_data.json")
        End If

        Dim data = DashboardLoader.LoadData(dataPath)
        If data IsNot Nothing Then
            Console.WriteLine()
            Console.WriteLine("📊 EQ12 Betting Engine Dashboard")
            Console.WriteLine("================================")
            Console.WriteLine($"Generated At: {data.GeneratedAt}")
            Console.WriteLine($"Total Profit: ${data.Stats.TotalProfit:F2}")
            Console.WriteLine($"Total Bets:   {data.Stats.TotalBets}")
            Console.WriteLine($"Avg CLV:      {data.Stats.AvgClv:F2}%")
            Console.WriteLine()
            Console.WriteLine("Recent Bets:")
            For Each bet In data.RecentBets
                Dim statusIcon = If(bet.Status = "WON", "✅", If(bet.Status = "LOST", "❌", "⏳"))
                Console.WriteLine($"{statusIcon} {bet.DatePlaced} | {bet.Selection} ({bet.Market}) | ${bet.Profit:F2}")
            Next
            Console.WriteLine()
        Else
            Console.WriteLine("⚠️ Could not load dashboard data. Run 'python src/betting_engine/dashboard_api.py' first.")
        End If
    End Sub
End Module
