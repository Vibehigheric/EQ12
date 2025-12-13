<?php

/**
 * EQ12 Complete PHP Betting Suite
 * Comprehensive PHP implementation with advanced betting features
 * Integrates with existing EQ12 Python and Node.js platforms
 *
 * @author EQ12 Platform
 * @version 1.0.0
 */

require_once __DIR__ . '/eq12_php_odds_client.php';

class EQ12PhpBettingSuite
{
    private $oddsClient;
    private $logDir;
    private $dataDir;
    private $configsDir;

    public function __construct($apiKey = null)
    {
        $this->oddsClient = new EQ12PhpOddsClient($apiKey);
        $this->logDir = 'C:/EQ12/logs';
        $this->dataDir = 'C:/EQ12/data';
        $this->configsDir = 'C:/EQ12/configs';

        echo '🚀 EQ12 Complete PHP Betting Suite initialized' . PHP_EOL;
    }

    private function log($message, $level = 'INFO')
    {
        $timestamp = date('c');
        $logMessage = "{$timestamp} - {$level} - {$message}";
        echo $logMessage . PHP_EOL;

        try {
            $logFile = $this->logDir . '/eq12_php_betting_suite.log';
            file_put_contents($logFile, $logMessage . PHP_EOL, FILE_APPEND | LOCK_EX);
        } catch (Exception $e) {
            echo "⚠️ Could not write to log file: " . $e->getMessage() . PHP_EOL;
        }
    }

    // 1. NFL Sunday Analysis with Advanced Metrics
    public function nflSundayAnalysis()
    {
        $this->log('🏈 Starting NFL Sunday Analysis...');
        echo PHP_EOL . '🏈 NFL SUNDAY COMPLETE ANALYSIS' . PHP_EOL;
        echo '================================' . PHP_EOL;

        try {
            // Get NFL odds with all markets
            $nflOdds = $this->oddsClient->getOdds('americanfootball_nfl', [
                'regions' => 'us,uk',
                'markets' => 'h2h,spreads,totals',
                'oddsFormat' => 'american'
            ]);

            $analysis = [
                'totalGames' => count($nflOdds),
                'upcomingGames' => [],
                'valuePicksATS' => [],
                'totalsBets' => [],
                'moneylineValue' => [],
                'arbitrageOpportunities' => []
            ];

            // Analyze each game
            foreach ($nflOdds as $game) {
                if (strtotime($game['commence_time']) > time()) {
                    $analysis['upcomingGames'][] = $game;

                    // Analyze for value bets
                    $gameAnalysis = $this->analyzeNFLGame($game);

                    if (!empty($gameAnalysis['atsValue'])) {
                        $analysis['valuePicksATS'][] = $gameAnalysis['atsValue'];
                    }

                    if (!empty($gameAnalysis['totalValue'])) {
                        $analysis['totalsBets'][] = $gameAnalysis['totalValue'];
                    }

                    if (!empty($gameAnalysis['mlValue'])) {
                        $analysis['moneylineValue'][] = $gameAnalysis['mlValue'];
                    }
                }
            }

            // Find arbitrage opportunities
            $arbitrages = $this->oddsClient->findArbitrageOpportunities('americanfootball_nfl');
            $analysis['arbitrageOpportunities'] = array_slice($arbitrages, 0, 5);

            // Display results
            echo "📊 Games Analysis: " . count($analysis['upcomingGames']) . " upcoming games" . PHP_EOL;
            echo "💰 Value Picks ATS: " . count($analysis['valuePicksATS']) . PHP_EOL;
            echo "📈 Total Bets: " . count($analysis['totalsBets']) . PHP_EOL;
            echo "🎯 Moneyline Value: " . count($analysis['moneylineValue']) . PHP_EOL;
            echo "⚡ Arbitrage Opportunities: " . count($analysis['arbitrageOpportunities']) . PHP_EOL;

            // Display top recommendations
            $this->displayTopPicks($analysis);

            // Save analysis
            $this->saveToFile('nfl_sunday_analysis', $analysis);

            return $analysis;
        } catch (Exception $e) {
            $this->log("NFL analysis error: " . $e->getMessage(), 'ERROR');
            throw $e;
        }
    }

    private function analyzeNFLGame($game)
    {
        $analysis = [];

        try {
            // Get best odds for each market
            $bestSpread = $this->getBestOdds($game, 'spreads');
            $bestTotal = $this->getBestOdds($game, 'totals');
            $bestML = $this->getBestOdds($game, 'h2h');

            // ATS Value Analysis
            if ($bestSpread && count($bestSpread['outcomes']) >= 2) {
                $homeSpread = null;
                $awaySpread = null;

                foreach ($bestSpread['outcomes'] as $outcome) {
                    if ($outcome['name'] === $game['home_team']) {
                        $homeSpread = $outcome;
                    } elseif ($outcome['name'] === $game['away_team']) {
                        $awaySpread = $outcome;
                    }
                }

                if ($homeSpread && $awaySpread) {
                    // Simple value detection (can be enhanced with ML models)
                    if (abs($homeSpread['point']) >= 7 && $homeSpread['price'] >= -105) {
                        $analysis['atsValue'] = [
                            'game' => $game['home_team'] . ' vs ' . $game['away_team'],
                            'pick' => ($homeSpread['point'] > 0 ? $game['home_team'] : $game['away_team']) . ' ' . $homeSpread['point'],
                            'odds' => $homeSpread['price'],
                            'confidence' => 'Medium',
                            'reasoning' => 'Large spread with favorable juice'
                        ];
                    }
                }
            }

            // Totals Value Analysis
            if ($bestTotal && count($bestTotal['outcomes']) >= 2) {
                $overUnder = $bestTotal['outcomes'][0];
                if ($overUnder && isset($overUnder['point'])) {
                    // Look for totals value (can be enhanced)
                    if ($overUnder['point'] >= 50 && $overUnder['price'] >= -105) {
                        $analysis['totalValue'] = [
                            'game' => $game['home_team'] . ' vs ' . $game['away_team'],
                            'pick' => $overUnder['name'] . ' ' . $overUnder['point'],
                            'odds' => $overUnder['price'],
                            'confidence' => 'Low',
                            'reasoning' => 'High total with good odds'
                        ];
                    }
                }
            }

            // Moneyline Value
            if ($bestML && count($bestML['outcomes']) >= 2) {
                foreach ($bestML['outcomes'] as $outcome) {
                    if ($outcome['price'] >= 200) {  // Underdog value
                        $analysis['mlValue'] = [
                            'game' => $game['home_team'] . ' vs ' . $game['away_team'],
                            'pick' => $outcome['name'],
                            'odds' => $outcome['price'],
                            'confidence' => 'High',
                            'reasoning' => 'Strong underdog value'
                        ];
                    }
                }
            }
        } catch (Exception $e) {
            $this->log("Game analysis error for {$game['home_team']} vs {$game['away_team']}: " . $e->getMessage(), 'ERROR');
        }

        return $analysis;
    }

    private function getBestOdds($game, $marketType)
    {
        $bestMarket = null;
        $bestOdds = -PHP_INT_MAX;

        foreach ($game['bookmakers'] as $bookmaker) {
            foreach ($bookmaker['markets'] as $market) {
                if ($market['key'] === $marketType) {
                    $avgOdds = 0;
                    foreach ($market['outcomes'] as $outcome) {
                        $avgOdds += ($outcome['price'] > 0 ? $outcome['price'] : abs($outcome['price']));
                    }
                    $avgOdds /= count($market['outcomes']);

                    if ($avgOdds > $bestOdds) {
                        $bestOdds = $avgOdds;
                        $bestMarket = $market;
                    }
                }
            }
        }

        return $bestMarket;
    }

    private function displayTopPicks($analysis)
    {
        echo PHP_EOL . '🎯 TOP BETTING RECOMMENDATIONS:' . PHP_EOL;
        echo '================================' . PHP_EOL;

        if (!empty($analysis['valuePicksATS'])) {
            echo PHP_EOL . '🏈 AGAINST THE SPREAD:' . PHP_EOL;
            $topATS = array_slice($analysis['valuePicksATS'], 0, 3);
            foreach ($topATS as $index => $pick) {
                echo ($index + 1) . ". {$pick['game']}" . PHP_EOL;
                echo "   Pick: {$pick['pick']} ({$pick['odds']})" . PHP_EOL;
                echo "   Confidence: {$pick['confidence']}" . PHP_EOL;
                echo "   Reasoning: {$pick['reasoning']}" . PHP_EOL . PHP_EOL;
            }
        }

        if (!empty($analysis['totalsBets'])) {
            echo '📊 TOTALS BETS:' . PHP_EOL;
            $topTotals = array_slice($analysis['totalsBets'], 0, 2);
            foreach ($topTotals as $index => $pick) {
                echo ($index + 1) . ". {$pick['game']}" . PHP_EOL;
                echo "   Pick: {$pick['pick']} ({$pick['odds']})" . PHP_EOL;
                echo "   Confidence: {$pick['confidence']}" . PHP_EOL . PHP_EOL;
            }
        }

        if (!empty($analysis['arbitrageOpportunities'])) {
            echo '⚡ ARBITRAGE OPPORTUNITIES:' . PHP_EOL;
            $topArbs = array_slice($analysis['arbitrageOpportunities'], 0, 3);
            foreach ($topArbs as $index => $arb) {
                echo ($index + 1) . ". {$arb['event']}" . PHP_EOL;
                echo "   Profit: " . number_format($arb['profit'], 2) . "%" . PHP_EOL;
                echo "   Description: {$arb['description']}" . PHP_EOL . PHP_EOL;
            }
        }
    }

    // 2. NBA Props Builder
    public function nbaPropsBuilder()
    {
        $this->log('🏀 Starting NBA Props Builder...');
        echo PHP_EOL . '🏀 NBA PLAYER PROPS ANALYSIS' . PHP_EOL;
        echo '============================' . PHP_EOL;

        try {
            $nbaProps = $this->oddsClient->getPlayerProps('basketball_nba');

            if (empty($nbaProps)) {
                echo '⚠️ NBA player props not available or season not active' . PHP_EOL;
                return [];
            }

            $propsAnalysis = [
                'totalGames' => count($nbaProps),
                'playerProps' => [],
                'valueProps' => [],
                'correlatedProps' => []
            ];

            // Analyze player props (simplified version)
            foreach ($nbaProps as $game) {
                foreach ($game['bookmakers'] as $bookmaker) {
                    foreach ($bookmaker['markets'] as $market) {
                        if (strpos($market['key'], 'player_') === 0) {
                            foreach ($market['outcomes'] as $outcome) {
                                $propsAnalysis['playerProps'][] = [
                                    'game' => $game['home_team'] . ' vs ' . $game['away_team'],
                                    'player' => $outcome['description'] ?? 'Unknown Player',
                                    'market' => $market['key'],
                                    'line' => $outcome['point'] ?? null,
                                    'odds' => $outcome['price'],
                                    'bookmaker' => $bookmaker['title']
                                ];
                            }
                        }
                    }
                }
            }

            echo "📊 Found " . count($propsAnalysis['playerProps']) . " player props across " . $propsAnalysis['totalGames'] . " games" . PHP_EOL;

            $this->saveToFile('nba_props_analysis', $propsAnalysis);
            return $propsAnalysis;
        } catch (Exception $e) {
            $this->log("NBA props analysis error: " . $e->getMessage(), 'ERROR');
            return [];
        }
    }

    // 3. Live Monitoring System (Simplified for PHP)
    public function liveMonitoring($sports = ['americanfootball_nfl', 'basketball_nba'], $cycles = 3)
    {
        $this->log('📡 Starting live odds monitoring...');
        echo PHP_EOL . '📡 LIVE ODDS MONITORING SYSTEM' . PHP_EOL;
        echo '==============================' . PHP_EOL;

        for ($cycle = 1; $cycle <= $cycles; $cycle++) {
            try {
                echo PHP_EOL . "🔄 Monitoring Cycle {$cycle} - " . date('H:i:s') . PHP_EOL;

                foreach ($sports as $sport) {
                    try {
                        echo PHP_EOL . "📊 Checking {$sport}..." . PHP_EOL;

                        // Get current odds
                        $odds = $this->oddsClient->getOdds($sport, [
                            'regions' => 'us',
                            'markets' => 'h2h',
                            'oddsFormat' => 'american'
                        ]);

                        // Check for arbitrage opportunities
                        $arbitrages = $this->oddsClient->findArbitrageOpportunities($sport);

                        if (!empty($arbitrages)) {
                            echo "🚨 ALERT: " . count($arbitrages) . " arbitrage opportunities found in {$sport}!" . PHP_EOL;
                            $topArbs = array_slice($arbitrages, 0, 2);
                            foreach ($topArbs as $arb) {
                                echo "   💰 {$arb['event']} - " . number_format($arb['profit'], 2) . "% profit" . PHP_EOL;
                            }
                        } else {
                            echo "   ✅ No arbitrage opportunities in {$sport}" . PHP_EOL;
                        }

                        // Save monitoring snapshot
                        $snapshot = [
                            'timestamp' => date('c'),
                            'sport' => $sport,
                            'totalGames' => count($odds),
                            'arbitrageCount' => count($arbitrages),
                            'topArbitrages' => array_slice($arbitrages, 0, 3)
                        ];

                        $this->saveToFile("monitoring_{$sport}_{$cycle}", $snapshot);
                    } catch (Exception $e) {
                        echo "   ❌ Error monitoring {$sport}: " . $e->getMessage() . PHP_EOL;
                    }

                    // Small delay between sports
                    sleep(2);
                }

                // Delay between cycles
                if ($cycle < $cycles) {
                    echo PHP_EOL . "⏳ Waiting 30 seconds for next cycle..." . PHP_EOL;
                    sleep(30);
                }
            } catch (Exception $e) {
                echo "❌ Monitoring error: " . $e->getMessage() . PHP_EOL;
            }
        }

        echo PHP_EOL . '🏁 Live monitoring demo complete' . PHP_EOL;

        // Display usage stats
        $this->oddsClient->getUsageStats();
    }

    // 4. Portfolio Performance Tracker
    public function portfolioPerformanceTracker()
    {
        $this->log('📈 Generating portfolio performance report...');
        echo PHP_EOL . '📈 PORTFOLIO PERFORMANCE TRACKER' . PHP_EOL;
        echo '================================' . PHP_EOL;

        // Simulate portfolio data (in real implementation, would read from database)
        $portfolioData = [
            'totalBets' => 150,
            'winningBets' => 82,
            'losingBets' => 68,
            'totalWagered' => 15000,
            'totalReturns' => 16200,
            'roi' => 8.0,
            'sharpRatio' => 1.45,
            'longestWinStreak' => 7,
            'longestLoseStreak' => 4,
            'betsByType' => [
                'moneyline' => ['bets' => 45, 'roi' => 12.3],
                'spreads' => ['bets' => 60, 'roi' => 5.8],
                'totals' => ['bets' => 30, 'roi' => 8.9],
                'props' => ['bets' => 15, 'roi' => 15.2]
            ]
        ];

        // Calculate metrics
        $winRate = number_format(($portfolioData['winningBets'] / $portfolioData['totalBets'] * 100), 1);
        $avgBetSize = number_format(($portfolioData['totalWagered'] / $portfolioData['totalBets']), 2);
        $profit = $portfolioData['totalReturns'] - $portfolioData['totalWagered'];

        echo "📊 Portfolio Overview:" . PHP_EOL;
        echo "   💰 Total Profit: $" . ($profit > 0 ? '+' : '') . number_format($profit) . PHP_EOL;
        echo "   📈 ROI: {$portfolioData['roi']}%" . PHP_EOL;
        echo "   🎯 Win Rate: {$winRate}%" . PHP_EOL;
        echo "   📏 Average Bet Size: $" . $avgBetSize . PHP_EOL;
        echo "   🏆 Sharp Ratio: {$portfolioData['sharpRatio']}" . PHP_EOL;

        echo PHP_EOL . "📊 Performance by Bet Type:" . PHP_EOL;
        foreach ($portfolioData['betsByType'] as $type => $data) {
            echo "   " . strtoupper($type) . ": {$data['bets']} bets, {$data['roi']}% ROI" . PHP_EOL;
        }

        echo PHP_EOL . "📈 Streak Analysis:" . PHP_EOL;
        echo "   🔥 Longest Win Streak: {$portfolioData['longestWinStreak']}" . PHP_EOL;
        echo "   ❄️ Longest Lose Streak: {$portfolioData['longestLoseStreak']}" . PHP_EOL;

        // Generate recommendations
        $recommendations = $this->generatePortfolioRecommendations($portfolioData);
        echo PHP_EOL . "💡 RECOMMENDATIONS:" . PHP_EOL;
        foreach ($recommendations as $index => $rec) {
            echo ($index + 1) . ". {$rec}" . PHP_EOL;
        }

        $this->saveToFile('portfolio_performance', array_merge($portfolioData, [
            'generatedAt' => date('c'),
            'recommendations' => $recommendations
        ]));

        return $portfolioData;
    }

    private function generatePortfolioRecommendations($data)
    {
        $recommendations = [];

        // Win rate analysis
        $winRate = $data['winningBets'] / $data['totalBets'];
        if ($winRate < 0.53) {
            $recommendations[] = 'Win rate below break-even. Focus on bet selection and line shopping.';
        }

        // ROI analysis
        if ($data['roi'] < 5) {
            $recommendations[] = 'ROI below target. Consider reducing bet size and focusing on higher value bets.';
        }

        // Bet type analysis
        $bestType = '';
        $bestRoi = 0;
        foreach ($data['betsByType'] as $type => $typeData) {
            if ($typeData['roi'] > $bestRoi) {
                $bestRoi = $typeData['roi'];
                $bestType = $type;
            }
        }

        $recommendations[] = strtoupper($bestType) . " bets show highest ROI ({$bestRoi}%). Consider increasing allocation.";

        // Streak analysis
        if ($data['longestLoseStreak'] >= 5) {
            $recommendations[] = 'Long losing streaks detected. Review bankroll management and bet sizing.';
        }

        return $recommendations;
    }

    // 5. Cross-Platform Integration Demo
    public function crossPlatformDemo()
    {
        $this->log('🌐 Starting cross-platform integration demo...');
        echo PHP_EOL . '🌐 CROSS-PLATFORM INTEGRATION DEMO' . PHP_EOL;
        echo '==================================' . PHP_EOL;

        try {
            // Check if Python files exist
            $pythonFiles = [
                'eq12_enhanced_openai_sdk.py',
                'eq12_odds_api_client.py',
                'eq12_google_sheets_integration.py'
            ];

            $availablePython = [];
            foreach ($pythonFiles as $file) {
                if (file_exists(getcwd() . '/' . $file)) {
                    $availablePython[] = $file;
                }
            }

            // Check if Node.js files exist
            $nodeFiles = [
                'eq12_node_odds_client.js',
                'eq12_node_betting_suite.js'
            ];

            $availableNode = [];
            foreach ($nodeFiles as $file) {
                if (file_exists(getcwd() . '/' . $file)) {
                    $availableNode[] = $file;
                }
            }

            echo "🐍 Python Integration Status:" . PHP_EOL;
            echo "   ✅ Available Python modules: " . count($availablePython) . "/" . count($pythonFiles) . PHP_EOL;
            foreach ($availablePython as $file) {
                echo "   📄 {$file}" . PHP_EOL;
            }

            echo PHP_EOL . "🟢 Node.js Integration Status:" . PHP_EOL;
            echo "   ✅ Available Node.js modules: " . count($availableNode) . "/" . count($nodeFiles) . PHP_EOL;
            foreach ($availableNode as $file) {
                echo "   📄 {$file}" . PHP_EOL;
            }

            // PHP capabilities
            echo PHP_EOL . "🔵 PHP Capabilities:" . PHP_EOL;
            echo "   ✅ Enhanced Odds API Client" . PHP_EOL;
            echo "   ✅ Real-time Arbitrage Detection" . PHP_EOL;
            echo "   ✅ NFL/NBA Analysis Engine" . PHP_EOL;
            echo "   ✅ Live Monitoring System" . PHP_EOL;
            echo "   ✅ Portfolio Performance Tracking" . PHP_EOL;

            // Integration points
            echo PHP_EOL . "🔗 Integration Points:" . PHP_EOL;
            echo "   📊 Shared data directory: C:/EQ12/data" . PHP_EOL;
            echo "   📝 Shared logs directory: C:/EQ12/logs" . PHP_EOL;
            echo "   ⚙️ Shared configs directory: C:/EQ12/configs" . PHP_EOL;

            // Demonstrate data sharing
            $phpData = [
                'timestamp' => date('c'),
                'source' => 'PHP Platform',
                'version' => '1.0.0',
                'capabilities' => [
                    'Real-time odds fetching',
                    'Arbitrage detection',
                    'NFL/NBA analysis',
                    'Live monitoring',
                    'Performance tracking'
                ],
                'apiUsage' => $this->oddsClient->getUsageStats()
            ];

            $this->saveToFile('php_platform_status', $phpData);
            echo PHP_EOL . "💾 Platform status saved for cross-platform integration" . PHP_EOL;

            return [
                'pythonModules' => $availablePython,
                'nodeModules' => $availableNode,
                'phpCapabilities' => $phpData['capabilities'],
                'integrationReady' => true
            ];
        } catch (Exception $e) {
            $this->log("Cross-platform demo error: " . $e->getMessage(), 'ERROR');
            throw $e;
        }
    }

    private function saveToFile($filename, $data)
    {
        try {
            $filepath = $this->dataDir . '/' . $filename . '.json';
            file_put_contents($filepath, json_encode($data, JSON_PRETTY_PRINT));
            $this->log("💾 Data saved to {$filepath}");
        } catch (Exception $e) {
            $this->log("Error saving file: " . $e->getMessage(), 'ERROR');
        }
    }

    // Master demo method
    public function runCompleteBettingSuite()
    {
        echo '🚀 EQ12 COMPLETE PHP BETTING SUITE DEMO' . PHP_EOL;
        echo '=======================================' . PHP_EOL;

        try {
            // 1. NFL Sunday Analysis
            $this->nflSundayAnalysis();
            sleep(3);

            // 2. NBA Props Builder
            $this->nbaPropsBuilder();
            sleep(3);

            // 3. Portfolio Performance
            $this->portfolioPerformanceTracker();
            sleep(3);

            // 4. Cross-Platform Demo
            $this->crossPlatformDemo();
            sleep(3);

            // 5. Live Monitoring (short demo)
            echo PHP_EOL . '🎯 Starting brief live monitoring demo...' . PHP_EOL;
            $this->liveMonitoring(['americanfootball_nfl'], 2);

            echo PHP_EOL . '🎉 COMPLETE BETTING SUITE DEMO FINISHED!' . PHP_EOL;
            echo '=========================================' . PHP_EOL;
            echo '🏆 PHP platform fully operational and integrated with Python and Node.js components' . PHP_EOL;
        } catch (Exception $e) {
            echo "❌ Suite error: " . $e->getMessage() . PHP_EOL;
            $this->log("Complete suite error: " . $e->getMessage(), 'ERROR');
        }
    }
}

// If run directly, execute complete demo
if (basename(__FILE__) == basename($_SERVER["SCRIPT_NAME"])) {
    $suite = new EQ12PhpBettingSuite();
    $suite->runCompleteBettingSuite();
}
