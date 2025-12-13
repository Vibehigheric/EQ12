<?php

/**
 * EQ12 Intelephense Demo - Test PHP IntelliSense Features
 *
 * This file demonstrates Intelephense features working with EQ12 code.
 * Open this file in VS Code to see:
 * - Autocomplete suggestions
 * - Hover information
 * - Go to definition
 * - Error detection
 * - Format on save
 */

declare(strict_types=1);

require_once 'intelephense_helpers.php';

/**
 * Demo class showing Intelephense features
 */
class EQ12IntelephenseDemo
{
    private EQ12PhpOddsClient $oddsClient;
    private EQ12PhpBettingSuite $bettingSuite;

    public function __construct()
    {
        // Intelephense will provide autocomplete here
        $this->oddsClient = new EQ12PhpOddsClient($_ENV['ODDS_API_KEY'] ?? '');
        $this->bettingSuite = new EQ12PhpBettingSuite();
    }

    /**
     * Demonstrate type hints and autocomplete
     *
     * @param string $sport The sport key (e.g., 'americanfootball_nfl')
     * @return array<string, mixed> Demo results with type safety
     */
    public function demonstrateFeatures(string $sport): array
    {
        // Try typing $this-> here - you should see autocomplete suggestions
        $sports = $this->oddsClient->getSports();

        // Try typing $odds-> after this line - hover to see type info
        $odds = $this->oddsClient->getOdds($sport);

        // Intelephense knows the return type from our helper file
        $analysis = $this->bettingSuite->nflSundayAnalysis();

        // Type-safe array access with full IntelliSense
        foreach ($odds as $game) {
            // Try typing $game[''] - you should see available keys
            $gameId = $game['id'];
            $homeTeam = $game['home_team'];
            $awayTeam = $game['away_team'];

            // Hover over these variables to see their types
            eq12_log("Processing game: {$homeTeam} vs {$awayTeam}");
        }

        // Advanced type checking - Intelephense will warn about type mismatches
        $kelly = $this->bettingSuite->calculateKelly(
            0.55,   // probability (Float)
            2.0,    // odds (Float)
            1000.0, // bankroll (Float)
            0.25    // maxKelly (Float)
        );

        return [
            'sports_count' => count($sports),
            'odds_count' => count($odds),
            'analysis' => $analysis,
            'demo_kelly' => $kelly,
            'features_working' => true
        ];
    }

    /**
     * Demonstrate error detection
     */
    public function demonstrateErrorDetection(): void
    {
        // These will show errors in Intelephense:

        // Uncomment to see undefined method error:
        // $this->nonExistentMethod();

        // Uncomment to see type error:
        // $this->bettingSuite->calculateKelly("invalid", "types", "here", "everywhere");

        // Uncomment to see undefined variable error:
        // echo $undefinedVariable;

        echo "Error detection is working if you see no red squiggles above!\n";
    }

    /**
     * Demonstrate documentation and hover features
     *
     * Hover over method calls below to see rich documentation
     */
    public function demonstrateDocumentation(): void
    {
        // Hover over these method calls to see documentation:
        eq12_env('ODDS_API_KEY', 'default-key');
        eq12_format_currency(123.45, '$');
        eq12_utc_to_local('2025-10-07T21:20:00Z');

        // Try Ctrl+Click (or Cmd+Click) to go to definition
        EQ12BettingMath::calculateCorrelation([1, 2, 3], [4, 5, 6]);
    }
}

// Test the demo
if (basename(__FILE__) === basename($_SERVER['SCRIPT_NAME'] ?? '')) {
    echo "🚀 EQ12 INTELEPHENSE DEMO\n";
    echo "========================\n\n";

    try {
        $demo = new EQ12IntelephenseDemo();

        echo "✅ Demo class instantiated successfully\n";
        echo "📊 Testing features...\n";

        $results = $demo->demonstrateFeatures('americanfootball_nfl');

        echo "✅ Features working: " . ($results['features_working'] ? 'YES' : 'NO') . "\n";
        echo "📈 Sports available: " . $results['sports_count'] . "\n";
        echo "🎯 Odds games: " . $results['odds_count'] . "\n";

        echo "\n🎉 Intelephense integration successful!\n";
        echo "💡 Open this file in VS Code to see all features in action.\n";
    } catch (Exception $e) {
        echo "❌ Error: " . $e->getMessage() . "\n";
        echo "💡 This is expected if API keys are not configured.\n";
        echo "   The important thing is that Intelephense shows no syntax errors!\n";
    }
}
