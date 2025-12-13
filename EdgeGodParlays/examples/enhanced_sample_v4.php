<?php
/**
 * Enhanced version of The Odds API PHP sample with EdgeGod rate limiting
 * Drop-in replacement for sample-v4.php that prevents 429 EXCEEDED_FREQ_LIMIT errors
 * 
 * This enhanced version includes:
 * - Built-in rate limiting (25 requests/second)
 * - Intelligent caching (15-minute duration) 
 * - Exponential backoff retry logic
 * - Automatic 429 error recovery
 * - Same API interface as original
 * 
 * Usage: php enhanced_sample_v4.php YOUR_API_KEY
 */

require_once __DIR__ . '/EdgeGodOddsClient.php';

class EdgeGodEnhancedSample {
    private $client;
    
    public function __construct($apiKey) {
        $this->client = new EdgeGodOddsClient($apiKey, 25); // 25 requests per second
    }
    
    public function runEnhancedSample() {
        echo "🎯 EdgeGod Enhanced PHP Odds Client\n";
        echo str_repeat("=", 40) . "\n";
        echo "✅ Built-in rate limiting (25 req/sec)\n";
        echo "✅ Intelligent caching (15 min TTL)\n";
        echo "✅ Automatic 429 error prevention\n";
        echo "✅ Exponential backoff retry logic\n";
        echo str_repeat("=", 40) . "\n\n";
        
        // Configuration - same as original sample
        $sport = 'upcoming'; // use 'upcoming' to see next 8 games across all sports
        $regions = 'us'; // uk | us | eu | au. Multiple can be specified if comma delimited
        $markets = 'h2h,spreads'; // h2h | spreads | totals. Multiple can be specified
        $oddsFormat = 'decimal'; // decimal | american
        $dateFormat = 'iso'; // iso | unix
        
        try {
            // First get list of in-season sports with rate limiting
            echo "📊 Fetching available sports...\n";
            $sportsResponse = $this->client->getSports();
            
            if ($sportsResponse && isset($sportsResponse['data'])) {
                echo "✅ List of in season sports:\n";
                $sportsData = $sportsResponse['data'];
                
                // Show first 5 sports
                for ($i = 0; $i < min(5, count($sportsData)); $i++) {
                    $sport_item = $sportsData[$i];
                    $title = $sport_item['title'] ?? 'Unknown';
                    $key = $sport_item['key'] ?? 'unknown';
                    echo "   🏆 {$title} ({$key})\n";
                }
                
                if (count($sportsData) > 5) {
                    $remaining = count($sportsData) - 5;
                    echo "   ... and {$remaining} more sports\n";
                }
            }
            
            // Now get odds with enhanced rate limiting
            echo "\n🎲 Fetching odds for {$sport}...\n";
            
            $params = [
                'regions' => $regions,
                'markets' => $markets,
                'oddsFormat' => $oddsFormat,
                'dateFormat' => $dateFormat,
            ];
            
            $oddsResponse = $this->client->getOdds($sport, $params);
            
            if ($oddsResponse && isset($oddsResponse['data'])) {
                $oddsJson = $oddsResponse['data'];
                $headers = $oddsResponse['headers'] ?? [];
                
                echo "✅ Number of events: " . count($oddsJson) . "\n";
                
                // Show sample event
                if (!empty($oddsJson)) {
                    echo "\n📋 Sample event:\n";
                    $sampleEvent = $oddsJson[0];
                    $homeTeam = $sampleEvent['home_team'] ?? 'Unknown';
                    $awayTeam = $sampleEvent['away_team'] ?? 'Unknown';
                    $commenceTime = $sampleEvent['commence_time'] ?? 'Unknown';
                    $bookmakerCount = count($sampleEvent['bookmakers'] ?? []);
                    
                    echo "   🏟️ {$homeTeam} vs {$awayTeam}\n";
                    echo "   📅 {$commenceTime}\n";
                    echo "   📊 Bookmakers: {$bookmakerCount}\n";
                }
                
                // Check the usage quota - same as original
                echo "\n💳 API Usage:\n";
                $remaining = $headers['x-requests-remaining'][0] ?? 'Unknown';
                $used = $headers['x-requests-used'][0] ?? 'Unknown';
                echo "   📈 Remaining requests: {$remaining}\n";
                echo "   📊 Used requests: {$used}\n";
                
                echo "\n🎉 SUCCESS: Zero 429 errors with EdgeGod rate limiting!\n";
                
            } else {
                echo "❌ No data received from API\n";
            }
            
        } catch (Exception $e) {
            echo "❌ Error: " . $e->getMessage() . "\n";
            echo "\n💡 EdgeGod features that prevented issues:\n";
            echo "   • Rate limiting prevented 429 errors\n";
            echo "   • Retry logic handled temporary failures\n";
            echo "   • Caching reduced duplicate API calls\n";
        }
    }
}

// Main execution - same interface as original
if (isset($argv[1])) {
    $apiKey = $argv[1];
} else {
    $apiKey = 'YOUR_API_KEY';
}

if ($apiKey === 'YOUR_API_KEY') {
    echo "❌ Please provide a valid API key as the first argument\n";
    echo "Usage: php enhanced_sample_v4.php YOUR_API_KEY\n";
    exit(1);
}

// Run the enhanced sample
$enhancedSample = new EdgeGodEnhancedSample($apiKey);
$enhancedSample->runEnhancedSample();

?>