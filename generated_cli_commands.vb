
        Case "ingest-oddsapi"
            Dim sport As String = GetArgValue(args, "--sport", "nfl")
            Dim oddsClient As New OddsApiClient()
            Dim oddsData = Await oddsClient.GetOddsBySportAsync(sport)
            Console.WriteLine($"Retrieved {oddsData.Rows.Count} odds records for {sport}")
            
        Case "run-arb-bot"
            Dim window As String = GetArgValue(args, "--window", "60m")
            Dim minArb As Double = Convert.ToDouble(GetArgValue(args, "--min-arb", "1.0"))
            
            Dim arbBot As New ArbitrageBotEngine()
            Dim recentOdds = GetRecentOdds(window)
            Dim opportunities = arbBot.DetectArbitrageOpportunities(recentOdds)
            Console.WriteLine($"Found {opportunities.Count} arbitrage opportunities")
            
        Case "calc-kelly"
            Dim odds As Integer = Convert.ToInt32(GetArgValue(args, "--odds", "+150"))
            Dim probability As Double = Convert.ToDouble(GetArgValue(args, "--p", "0.55"))
            Dim fraction As Double = Convert.ToDouble(GetArgValue(args, "--fraction", "0.5"))
            Dim bankroll As Double = GetCurrentBankroll()
            
            Dim kelly As New KellyCalculator()
            Dim result = kelly.CalculateKellyStake(bankroll, odds, probability, fraction)
            Console.WriteLine($"Recommended stake: {result.StakeAmount:C} ({result.StakePercent:F2}%)")
        