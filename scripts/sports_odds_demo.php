<?php
/**
 * EQ12 Sports Betting Odds Analysis Demo
 * Demonstrates PHP development environment with Intelephense IntelliSense
 * 
 * @package EQ12\SportsAnalysis
 * @author EQ12 Development Team
 * @since 1.0.0
 */

declare(strict_types=1);

namespace EQ12\SportsAnalysis;

/**
 * Sports odds analyzer with type hints for Intelephense
 */
class OddsAnalyzer
{
    /** @var string */
    private $apiKey;
    
    /** @var array */
    private $supportedSports = ['americanfootball_nfl', 'basketball_nba', 'baseball_mlb'];
    
    public function __construct(?string $apiKey = null)
    {
        $this->apiKey = $apiKey ?? getenv('ODDS_API_KEY') ?: '';
    }
    
    /**
     * Fetch live odds from The Odds API
     * @param string $sport Sport key (e.g., 'americanfootball_nfl')
     * @param string $region Region for odds (us, uk, au, eu)
     * @return array Raw odds data
     * @throws \Exception When API request fails
     */
    public function fetchOdds(string $sport, string $region = 'us'): array
    {
        if (empty($this->apiKey)) {
            throw new \Exception('ODDS_API_KEY environment variable not set');
        }
        
        if (!in_array($sport, $this->supportedSports, true)) {
            throw new \Exception("Unsupported sport: {$sport}");
        }
        
        $url = "https://api.the-odds-api.com/v4/sports/{$sport}/odds/?" . http_build_query([
            'api_key' => $this->apiKey,
            'regions' => $region,
            'markets' => 'h2h,spreads,totals',
            'oddsFormat' => 'american'
        ]);
        
        $response = $this->makeApiRequest($url);
        
        if ($response === false) {
            throw new \Exception('Failed to fetch odds data');
        }
        
        return json_decode($response, true) ?? [];
    }
    
    /**
     * Calculate implied probability from American odds
     * @param int $americanOdds American format odds (e.g., -150, +130)
     * @return float Implied probability (0.0 to 1.0)
     */
    public function calculateImpliedProbability(int $americanOdds): float
    {
        if ($americanOdds > 0) {
            // Positive odds: 100 / (odds + 100)
            return 100 / ($americanOdds + 100);
        }
        
        // Negative odds: |odds| / (|odds| + 100)
        return abs($americanOdds) / (abs($americanOdds) + 100);
    }
    
    /**
     * Find arbitrage opportunities across multiple sportsbooks
     * @param array $oddsData Raw odds data from API
     * @return array Arbitrage opportunities with profit percentages
     */
    public function findArbitrage(array $oddsData): array
    {
        $arbitrageOpportunities = [];
        
        foreach ($oddsData as $game) {
            $gameAnalysis = $this->analyzeGame($game);
            
            if ($gameAnalysis['arbitrage_possible']) {
                $arbitrageOpportunities[] = $gameAnalysis;
            }
        }
        
        // Sort by profit margin (highest first)
        usort($arbitrageOpportunities, function($a, $b) {
            return $b['profit_margin'] <=> $a['profit_margin'];
        });
        
        return $arbitrageOpportunities;
    }
    
    /**
     * Analyze a single game for arbitrage opportunities
     * @param array $game Game data with bookmaker odds
     * @return array Analysis results
     */
    private function analyzeGame(array $game): array
    {
        $bestOdds = $this->findBestOdds($game['bookmakers'] ?? []);
        
        if (empty($bestOdds['home']) || empty($bestOdds['away'])) {
            return [
                'game_id' => $game['id'] ?? 'unknown',
                'arbitrage_possible' => false,
                'reason' => 'Insufficient odds data'
            ];
        }
        
        // Calculate total implied probability
        $homeProb = $this->calculateImpliedProbability($bestOdds['home']['odds']);
        $awayProb = $this->calculateImpliedProbability($bestOdds['away']['odds']);
        $totalProb = $homeProb + $awayProb;
        
        $arbitragePossible = $totalProb < 1.0;
        $profitMargin = $arbitragePossible ? (1.0 - $totalProb) * 100 : 0;
        
        return [
            'game_id' => $game['id'] ?? 'unknown',
            'home_team' => $game['home_team'] ?? 'Unknown',
            'away_team' => $game['away_team'] ?? 'Unknown',
            'game_time' => $game['commence_time'] ?? null,
            'arbitrage_possible' => $arbitragePossible,
            'profit_margin' => round($profitMargin, 2),
            'best_home_odds' => $bestOdds['home'],
            'best_away_odds' => $bestOdds['away'],
            'home_probability' => round($homeProb * 100, 2),
            'away_probability' => round($awayProb * 100, 2),
            'total_probability' => round($totalProb * 100, 2)
        ];
    }
    
    /**
     * Find best odds across all bookmakers for a game
     * @param array $bookmakers Bookmaker odds data
     * @return array Best odds for home/away
     */
    private function findBestOdds(array $bookmakers): array
    {
        $bestOdds = ['home' => null, 'away' => null];
        
        foreach ($bookmakers as $bookmaker) {
            $markets = $bookmaker['markets'] ?? [];
            
            foreach ($markets as $market) {
                if ($market['key'] !== 'h2h') continue;
                
                foreach ($market['outcomes'] as $outcome) {
                    $team = $outcome['name'];
                    $odds = (int)$outcome['price'];
                    $position = $this->getTeamPosition($team, $bookmaker);
                    
                    if ($position && (!$bestOdds[$position] || $odds > $bestOdds[$position]['odds'])) {
                        $bestOdds[$position] = [
                            'team' => $team,
                            'odds' => $odds,
                            'bookmaker' => $bookmaker['title'] ?? 'Unknown'
                        ];
                    }
                }
            }
        }
        
        return $bestOdds;
    }
    
    /**
     * Determine if team is home or away
     * @param string $teamName Team name from outcome
     * @param array $bookmaker Bookmaker data context
     * @return string|null 'home', 'away', or null
     */
    private function getTeamPosition(string $teamName, array $bookmaker): ?string
    {
        // This is a simplified implementation
        // In real use, you'd match against the game's home_team/away_team
        static $teamIndex = 0;
        return $teamIndex++ % 2 === 0 ? 'home' : 'away';
    }
    
    /**
     * Make HTTP API request with error handling
     * @param string $url API endpoint URL
     * @return string|false Response body or false on failure
     */
    private function makeApiRequest(string $url)
    {
        $context = stream_context_create([
            'http' => [
                'timeout' => 30,
                'user_agent' => 'EQ12 Sports Analysis Tool v1.0'
            ]
        ]);
        
        return file_get_contents($url, false, $context);
    }
    
    /**
     * Format analysis results for display
     * @param array $arbitrageOpportunities Analysis results
     * @return string Formatted output
     */
    public function formatResults(array $arbitrageOpportunities): string
    {
        if (empty($arbitrageOpportunities)) {
            return "🚫 No arbitrage opportunities found.\n";
        }
        
        $output = "🎯 Found " . count($arbitrageOpportunities) . " arbitrage opportunities:\n\n";
        
        foreach ($arbitrageOpportunities as $i => $opportunity) {
            $output .= sprintf(
                "%d. %s vs %s\n" .
                "   Profit Margin: %.2f%%\n" .
                "   Best Home Odds: %s (%d) at %s\n" .
                "   Best Away Odds: %s (%d) at %s\n" .
                "   Total Probability: %.2f%%\n\n",
                $i + 1,
                $opportunity['home_team'],
                $opportunity['away_team'],
                $opportunity['profit_margin'],
                $opportunity['best_home_odds']['team'],
                $opportunity['best_home_odds']['odds'],
                $opportunity['best_home_odds']['bookmaker'],
                $opportunity['best_away_odds']['team'],
                $opportunity['best_away_odds']['odds'],
                $opportunity['best_away_odds']['bookmaker'],
                $opportunity['total_probability']
            );
        }
        
        return $output;
    }
}

/**
 * Demo runner for command line testing
 */
function runDemo(): void
{
    echo "🎲 EQ12 Sports Betting Analysis Demo\n";
    echo "=" . str_repeat("=", 40) . "\n\n";
    
    $analyzer = new OddsAnalyzer();
    
    // Demo with sample data (since we may not have API key)
    $sampleOdds = [
        [
            'id' => 'demo_game_1',
            'home_team' => 'Kansas City Chiefs',
            'away_team' => 'Buffalo Bills',
            'commence_time' => '2024-01-15T20:00:00Z',
            'bookmakers' => [
                [
                    'title' => 'DraftKings',
                    'markets' => [
                        [
                            'key' => 'h2h',
                            'outcomes' => [
                                ['name' => 'Kansas City Chiefs', 'price' => -150],
                                ['name' => 'Buffalo Bills', 'price' => 130]
                            ]
                        ]
                    ]
                ],
                [
                    'title' => 'FanDuel', 
                    'markets' => [
                        [
                            'key' => 'h2h',
                            'outcomes' => [
                                ['name' => 'Kansas City Chiefs', 'price' => -140],
                                ['name' => 'Buffalo Bills', 'price' => 135]
                            ]
                        ]
                    ]
                ]
            ]
        ]
    ];
    
    echo "📊 Analyzing sample NFL game...\n";
    
    // Test individual calculations
    echo "\n🧮 Testing odds calculations:\n";
    echo "Kansas City (-150): " . round($analyzer->calculateImpliedProbability(-150) * 100, 2) . "% implied probability\n";
    echo "Buffalo (+130): " . round($analyzer->calculateImpliedProbability(130) * 100, 2) . "% implied probability\n";
    
    // Test arbitrage analysis
    echo "\n🔍 Analyzing for arbitrage opportunities:\n";
    $arbitrageResults = $analyzer->findArbitrage($sampleOdds);
    echo $analyzer->formatResults($arbitrageResults);
    
    echo "✅ Demo completed successfully!\n";
    echo "\n💡 To use with live data:\n";
    echo "   1. Set ODDS_API_KEY environment variable\n";
    echo "   2. Call \$analyzer->fetchOdds('americanfootball_nfl')\n";
    echo "   3. Analyze real-time arbitrage opportunities\n";
}

// Run demo if script is executed directly
if (isset($_SERVER['SCRIPT_FILENAME']) && realpath(__FILE__) === realpath($_SERVER['SCRIPT_FILENAME'])) {
    try {
        runDemo();
    } catch (\Exception $e) {
        echo "❌ Error: " . $e->getMessage() . "\n";
        exit(1);
    }
}
?>