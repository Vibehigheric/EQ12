<?php

/**
 * EQ12 Enhanced PHP Odds API Client
 * Advanced PHP integration for The Odds API with EQ12 platform capabilities
 *
 * @author EQ12 Platform
 * @version 1.0.0
 */

require_once __DIR__ . '/vendor/autoload.php';

use GuzzleHttp\Client;
use GuzzleHttp\Exception\RequestException;

class EQ12PhpOddsClient
{
    private $apiKey;
    private $baseUrl;
    private $logDir;
    private $dataDir;
    private $client;
    private $requestCount;
    private $remainingRequests;

    public function __construct($apiKey = null)
    {
        $this->apiKey = $apiKey ?? $_ENV['ODDS_API_KEY'] ?? $GLOBALS['argv'][1] ?? null;
        $this->baseUrl = 'https://api.the-odds-api.com/v4';
        $this->logDir = 'C:/EQ12/logs';
        $this->dataDir = 'C:/EQ12/data';

        // Ensure directories exist
        $this->ensureDirectories();

        // Initialize HTTP client
        $this->client = new Client([
            'timeout' => 30,
            'http_errors' => false
        ]);

        // Request tracking
        $this->requestCount = 0;
        $this->remainingRequests = null;

        echo "🏆 EQ12 Enhanced PHP Odds API Client initialized" . PHP_EOL;

        if (empty($this->apiKey) || $this->apiKey === 'YOUR_API_KEY') {
            echo "⚠️ API key required. Set ODDS_API_KEY environment variable or pass as argument" . PHP_EOL;
        }
    }

    private function ensureDirectories()
    {
        try {
            if (!is_dir($this->logDir)) {
                mkdir($this->logDir, 0777, true);
            }
            if (!is_dir($this->dataDir)) {
                mkdir($this->dataDir, 0777, true);
            }
        } catch (Exception $e) {
            echo "⚠️ Could not create directories: " . $e->getMessage() . PHP_EOL;
        }
    }

    private function log($message, $level = 'INFO')
    {
        $timestamp = date('c');
        $logMessage = "{$timestamp} - {$level} - {$message}";
        echo $logMessage . PHP_EOL;

        try {
            $logFile = $this->logDir . '/eq12_php_odds.log';
            file_put_contents($logFile, $logMessage . PHP_EOL, FILE_APPEND | LOCK_EX);
        } catch (Exception $e) {
            echo "⚠️ Could not write to log file: " . $e->getMessage() . PHP_EOL;
        }
    }

    private function makeRequest($endpoint, $params = [])
    {
        if (empty($this->apiKey) || $this->apiKey === 'YOUR_API_KEY') {
            throw new Exception('Valid API key required');
        }

        try {
            $this->requestCount++;
            $params['api_key'] = $this->apiKey;

            $response = $this->client->request('GET', $this->baseUrl . $endpoint, [
                'query' => $params
            ]);

            // Track usage
            $remainingHeader = $response->getHeader('x-requests-remaining');
            $usedHeader = $response->getHeader('x-requests-used');

            $this->remainingRequests = !empty($remainingHeader) ? $remainingHeader[0] : null;
            $usedRequests = !empty($usedHeader) ? $usedHeader[0] : null;

            $this->log("API Request: {$endpoint} | Used: {$usedRequests} | Remaining: {$this->remainingRequests}");

            if ($response->getStatusCode() !== 200) {
                throw new Exception("API Error: " . $response->getStatusCode() . " - " . $response->getBody());
            }

            return json_decode($response->getBody(), true);
        } catch (RequestException $e) {
            $this->log("API Error: " . $e->getMessage(), 'ERROR');
            throw $e;
        }
    }

    public function getSports()
    {
        $this->log('🏈 Fetching available sports...');
        $sports = $this->makeRequest('/sports');

        // Save to file
        $this->saveToFile('sports', $sports);

        echo "📊 Found " . count($sports) . " available sports" . PHP_EOL;
        foreach ($sports as $sport) {
            echo "  - {$sport['title']} ({$sport['key']})" . PHP_EOL;
        }

        return $sports;
    }

    public function getOdds($sportKey = 'upcoming', $options = [])
    {
        $defaultOptions = [
            'regions' => 'us',
            'markets' => 'h2h',
            'oddsFormat' => 'american',
            'dateFormat' => 'iso'
        ];

        $params = array_merge($defaultOptions, $options);

        $this->log("🎯 Fetching odds for {$sportKey} with markets: {$params['markets']}");

        $odds = $this->makeRequest("/sports/{$sportKey}/odds", $params);

        // Save to file with timestamp
        $filename = 'odds_' . $sportKey . '_' . date('Y-m-d_H-i-s');
        $this->saveToFile($filename, $odds);

        echo "📊 Found " . count($odds) . " events with odds" . PHP_EOL;

        return $odds;
    }

    public function findArbitrageOpportunities($sportKey = 'upcoming')
    {
        $this->log("🔍 Scanning for arbitrage opportunities in {$sportKey}...");

        $odds = $this->getOdds($sportKey, [
            'regions' => 'us,uk,eu',
            'markets' => 'h2h',
            'oddsFormat' => 'american'
        ]);

        $arbitrages = [];

        foreach ($odds as $event) {
            if (!empty($event['bookmakers']) && count($event['bookmakers']) >= 2) {
                $arb = $this->calculateArbitrage($event);
                if ($arb && $arb['profit'] > 0) {
                    $arbitrages[] = $arb;
                }
            }
        }

        // Sort by profit margin
        usort($arbitrages, function ($a, $b) {
            return $b['profit'] <=> $a['profit'];
        });

        $this->log("💰 Found " . count($arbitrages) . " arbitrage opportunities");

        $topArbitrages = array_slice($arbitrages, 0, 10);
        foreach ($topArbitrages as $index => $arb) {
            $profitFormatted = number_format($arb['profit'], 2);
            echo ($index + 1) . ". {$arb['event']} | Profit: {$profitFormatted}% | {$arb['description']}" . PHP_EOL;
        }

        // Save arbitrage opportunities
        $this->saveToFile('arbitrage_opportunities', $arbitrages);

        return $arbitrages;
    }

    private function calculateArbitrage($event)
    {
        try {
            $bestOdds = [];

            // Find best odds for each outcome
            foreach ($event['bookmakers'] as $bookmaker) {
                foreach ($bookmaker['markets'] as $market) {
                    if ($market['key'] === 'h2h') {
                        foreach ($market['outcomes'] as $outcome) {
                            $impliedProb = $this->americanToImpliedProbability($outcome['price']);

                            if (
                                !isset($bestOdds[$outcome['name']]) ||
                                $impliedProb < $bestOdds[$outcome['name']]['impliedProb']
                            ) {
                                $bestOdds[$outcome['name']] = [
                                    'price' => $outcome['price'],
                                    'impliedProb' => $impliedProb,
                                    'bookmaker' => $bookmaker['title']
                                ];
                            }
                        }
                    }
                }
            }

            // Calculate total implied probability
            $totalImpliedProb = array_sum(array_column($bestOdds, 'impliedProb'));

            if ($totalImpliedProb < 1.0) {
                $profitMargin = ((1 / $totalImpliedProb) - 1) * 100;

                return [
                    'event' => $event['home_team'] . ' vs ' . $event['away_team'],
                    'sport' => $event['sport_title'],
                    'commence_time' => $event['commence_time'],
                    'profit' => $profitMargin,
                    'bestOdds' => $bestOdds,
                    'totalImpliedProb' => $totalImpliedProb,
                    'description' => count($bestOdds) . ' outcomes across multiple bookmakers'
                ];
            }

            return null;
        } catch (Exception $e) {
            $this->log("Error calculating arbitrage for {$event['home_team']} vs {$event['away_team']}: " . $e->getMessage(), 'ERROR');
            return null;
        }
    }

    private function americanToImpliedProbability($americanOdds)
    {
        if ($americanOdds > 0) {
            return 100 / ($americanOdds + 100);
        } else {
            return abs($americanOdds) / (abs($americanOdds) + 100);
        }
    }

    public function getNFLAnalysis()
    {
        $this->log('🏈 Performing NFL analysis...');

        $nflOdds = $this->getOdds('americanfootball_nfl', [
            'regions' => 'us',
            'markets' => 'h2h,spreads,totals',
            'oddsFormat' => 'american'
        ]);

        $analysis = [
            'totalGames' => count($nflOdds),
            'upcomingGames' => 0,
            'averageTotal' => 0,
            'highestFavorite' => null,
            'biggestSpread' => 0,
            'biggestSpreadGame' => null
        ];

        // Analyze each game
        foreach ($nflOdds as $game) {
            if (strtotime($game['commence_time']) > time()) {
                $analysis['upcomingGames']++;
            }

            foreach ($game['bookmakers'] as $bookmaker) {
                foreach ($bookmaker['markets'] as $market) {
                    if ($market['key'] === 'totals') {
                        $total = $market['outcomes'][0]['point'] ?? 0;
                        if ($total > $analysis['averageTotal']) {
                            $analysis['averageTotal'] = $total;
                        }
                    }

                    if ($market['key'] === 'spreads') {
                        foreach ($market['outcomes'] as $outcome) {
                            $spread = abs($outcome['point'] ?? 0);
                            if ($spread > $analysis['biggestSpread']) {
                                $analysis['biggestSpread'] = $spread;
                                $analysis['biggestSpreadGame'] = $game['home_team'] . ' vs ' . $game['away_team'];
                            }
                        }
                    }
                }
            }
        }

        echo '🏈 NFL Analysis Results:' . PHP_EOL;
        echo "  📊 Total Games: {$analysis['totalGames']}" . PHP_EOL;
        echo "  ⏰ Upcoming Games: {$analysis['upcomingGames']}" . PHP_EOL;
        echo "  📈 Biggest Spread: {$analysis['biggestSpread']} ({$analysis['biggestSpreadGame']})" . PHP_EOL;

        $this->saveToFile('nfl_analysis', $analysis);
        return $analysis;
    }

    public function getPlayerProps($sportKey = 'americanfootball_nfl')
    {
        $this->log("🎯 Fetching player props for {$sportKey}...");

        try {
            $props = $this->getOdds($sportKey, [
                'regions' => 'us',
                'markets' => 'player_pass_tds,player_pass_yds,player_rush_yds,player_receptions',
                'oddsFormat' => 'american'
            ]);

            echo "🎲 Found " . count($props) . " events with player props" . PHP_EOL;

            $this->saveToFile('player_props', $props);
            return $props;
        } catch (Exception $e) {
            $this->log("Player props not available for {$sportKey}: " . $e->getMessage(), 'WARNING');
            return [];
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

    public function getUsageStats()
    {
        if ($this->remainingRequests !== null) {
            echo "📊 API Usage Statistics:" . PHP_EOL;
            echo "  🔢 Requests made this session: {$this->requestCount}" . PHP_EOL;
            echo "  ⏳ Remaining requests: {$this->remainingRequests}" . PHP_EOL;

            return [
                'sessionRequests' => $this->requestCount,
                'remainingRequests' => intval($this->remainingRequests)
            ];
        }

        return null;
    }

    // Demo method that showcases all capabilities
    public function runDemo()
    {
        echo '🚀 EQ12 PHP Odds API Demo Starting...' . PHP_EOL;
        echo '====================================' . PHP_EOL;

        try {
            // Get available sports
            $this->getSports();
            echo PHP_EOL;

            // Get NFL odds and analysis
            $this->getNFLAnalysis();
            echo PHP_EOL;

            // Find arbitrage opportunities
            $this->findArbitrageOpportunities('americanfootball_nfl');
            echo PHP_EOL;

            // Get player props
            $this->getPlayerProps();
            echo PHP_EOL;

            // Show usage stats
            $this->getUsageStats();

            echo PHP_EOL . '🎉 EQ12 PHP Demo Complete!' . PHP_EOL;
        } catch (Exception $e) {
            echo "❌ Demo error: " . $e->getMessage() . PHP_EOL;
        }
    }
}

// If run directly, execute demo
if (basename(__FILE__) == basename($_SERVER["SCRIPT_NAME"])) {
    $client = new EQ12PhpOddsClient();
    $client->runDemo();
}
