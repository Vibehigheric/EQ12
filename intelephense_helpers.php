<?php

/**
 * EQ12 Intelephense Helper File
 *
 * This file provides enhanced type information and stub declarations
 * to improve IDE experience with EQ12 PHP components.
 *
 * This file is for IDE support only and should NOT be included
 * in production code.
 *
 * @package EQ12
 * @author EQ12 Platform
 */

// This file exists solely for Intelephense IDE support
if (false) {

    /**
     * Enhanced EQ12 PHP Odds Client with full type information
     */
    class EQ12PhpOddsClient
    {
        /**
         * @var string The Odds API key
         */
        private string $apiKey;

        /**
         * @var string Base URL for the Odds API
         */
        private string $baseUrl;

        /**
         * Constructor
         * @param string $apiKey The Odds API key from environment
         */
        public function __construct(string $apiKey = '') {}

        /**
         * Get available sports
         * @return array<string, array{key: string, group: string, title: string, description: string, has_outrights: bool}> Array of sports data
         * @throws \Exception When API request fails
         */
        public function getSports(): array {}

        /**
         * Get odds for a specific sport
         * @param string $sport The sport key (e.g., 'americanfootball_nfl')
         * @param array<string> $markets The markets to include (h2h, spreads, totals)
         * @param string $regions The regions to include (us, uk, au)
         * @param string $oddsFormat The odds format (american, decimal, fractional)
         * @return array<int, array{id: string, sport_key: string, sport_title: string, commence_time: string, home_team: string, away_team: string, bookmakers: array}> Odds data
         * @throws \Exception When API request fails
         */
        public function getOdds(string $sport, array $markets = ['h2h'], string $regions = 'us', string $oddsFormat = 'american'): array {}

        /**
         * Get player props for a specific sport
         * @param string $sport The sport key
         * @param string $regions The regions to include
         * @return array<int, array{id: string, sport_key: string, sport_title: string, commence_time: string, home_team: string, away_team: string, bookmakers: array}> Player props data
         * @throws \Exception When API request fails
         */
        public function getPlayerProps(string $sport, string $regions = 'us'): array {}

        /**
         * Find arbitrage opportunities across bookmakers
         * @param string $sport The sport to analyze
         * @return array<int, array{game: string, arbitrage_percentage: float, profit_percentage: float, bets: array}> Arbitrage opportunities
         */
        public function findArbitrageOpportunities(string $sport = 'americanfootball_nfl'): array {}

        /**
         * Calculate implied probability from American odds
         * @param int $americanOdds The American odds (e.g., -110, +150)
         * @return float The implied probability (0.0 to 1.0)
         */
        public function calculateImpliedProbability(int $americanOdds): float {}

        /**
         * Convert American odds to decimal odds
         * @param int $americanOdds The American odds
         * @return float The decimal odds
         */
        public function americanToDecimal(int $americanOdds): float {}

        /**
         * Make HTTP request to Odds API
         * @param string $endpoint The API endpoint
         * @param array<string, mixed> $params Query parameters
         * @return array<string, mixed> The API response data
         * @throws \Exception When request fails
         */
        private function makeRequest(string $endpoint, array $params = []): array {}
    }

    /**
     * Enhanced EQ12 PHP Betting Suite with full type information
     */
    class EQ12PhpBettingSuite
    {
        /**
         * @var EQ12PhpOddsClient The odds client instance
         */
        private EQ12PhpOddsClient $oddsClient;

        /**
         * Constructor
         * @param string|null $apiKey Optional API key override
         */
        public function __construct(?string $apiKey = null) {}

        /**
         * Analyze NFL games for Sunday
         * @return array<string, array{game: string, recommendations: array, expected_value: float, confidence: string}> Analysis results
         */
        public function nflSundayAnalysis(): array {}

        /**
         * Build Same Game Parlays (SGPs)
         * @param string $sport The sport key
         * @param int $minLegs Minimum number of legs
         * @param int $maxLegs Maximum number of legs
         * @param float $minOdds Minimum total odds
         * @return array<int, array{legs: array, total_odds: float, implied_probability: float, expected_value: float}> SGP combinations
         */
        public function buildSGPs(string $sport, int $minLegs = 2, int $maxLegs = 6, float $minOdds = 2.0): array {}

        /**
         * Calculate Kelly Criterion bet sizing
         * @param float $probability Your estimated probability (0.0 to 1.0)
         * @param float $odds The decimal odds offered
         * @param float $bankroll Your total bankroll
         * @param float $maxKelly Maximum Kelly fraction (default 0.25)
         * @return array{kelly_fraction: float, bet_size: float, expected_growth: float} Kelly calculation results
         */
        public function calculateKelly(float $probability, float $odds, float $bankroll, float $maxKelly = 0.25): array {}

        /**
         * Analyze correlations between different bet types
         * @param array<string, mixed> $gameData The game data to analyze
         * @return array<string, array{correlation: float, confidence: string, recommendation: string}> Correlation analysis
         */
        public function analyzeCorrelations(array $gameData): array {}

        /**
         * Generate daily betting report
         * @param string $date The date in Y-m-d format
         * @return array{games_analyzed: int, opportunities: array, total_ev: float, recommendations: array} Daily report
         */
        public function generateDailyReport(string $date): array {}

        /**
         * Validate bet combination for contradictions
         * @param array<string, mixed> $legs Array of bet legs
         * @return array{valid: bool, conflicts: array<string>, recommendations: array<string>} Validation results
         */
        public function validateBetCombination(array $legs): array {}

        /**
         * Calculate expected value for a bet
         * @param float $probability Your estimated win probability
         * @param float $odds The decimal odds
         * @param float $stake The bet amount
         * @return array{ev_dollars: float, ev_percentage: float, roi: float} Expected value calculation
         */
        public function calculateExpectedValue(float $probability, float $odds, float $stake): array {}
    }

    /**
     * EQ12 Betting Math Engine for advanced calculations
     */
    class EQ12BettingMath
    {
        /**
         * Calculate Poisson distribution probability
         * @param float $lambda The expected number of events
         * @param int $k The actual number of events
         * @return float The probability
         */
        public static function poissonProbability(float $lambda, int $k): float {}

        /**
         * Calculate correlation coefficient between two datasets
         * @param array<float> $x First dataset
         * @param array<float> $y Second dataset
         * @return float Correlation coefficient (-1 to 1)
         */
        public static function calculateCorrelation(array $x, array $y): float {}

        /**
         * Simulate Monte Carlo outcomes
         * @param array<array{probability: float, payout: float}> $bets Array of bet scenarios
         * @param int $iterations Number of simulations
         * @return array{mean_outcome: float, std_dev: float, win_rate: float, risk_of_ruin: float} Simulation results
         */
        public static function monteCarlo(array $bets, int $iterations = 10000): array {}
    }

    // Global helper functions for EQ12 ecosystem

    /**
     * Get environment variable with default fallback
     * @param string $key Environment variable name
     * @param string $default Default value if not found
     * @return string The environment value or default
     */
    function eq12_env(string $key, string $default = ''): string {}

    /**
     * Log message to EQ12 logging system
     * @param string $message The message to log
     * @param string $level Log level (info, warning, error, debug)
     * @param array<string, mixed> $context Additional context data
     * @return bool Success status
     */
    function eq12_log(string $message, string $level = 'info', array $context = []): bool {}

    /**
     * Format currency value for display
     * @param float $amount The amount to format
     * @param string $currency Currency symbol
     * @return string Formatted currency string
     */
    function eq12_format_currency(float $amount, string $currency = '$'): string {}

    /**
     * Convert UTC timestamp to local timezone
     * @param string $utcTimestamp UTC timestamp
     * @param string $timezone Target timezone (default: America/New_York)
     * @return string Formatted local time
     */
    function eq12_utc_to_local(string $utcTimestamp, string $timezone = 'America/New_York'): string {}

    /**
     * Validate API response structure
     * @param array<string, mixed> $response API response data
     * @param array<string> $requiredFields Required fields to validate
     * @return array{valid: bool, missing_fields: array<string>, errors: array<string>} Validation result
     */
    function eq12_validate_response(array $response, array $requiredFields): array {}
}

/**
 * Type definitions for common EQ12 data structures
 */

/**
 * @template TBet of array{
 *   id: string,
 *   sport: string,
 *   game: string,
 *   market: string,
 *   selection: string,
 *   odds: float,
 *   probability: float,
 *   stake: float,
 *   expected_value: float
 * }
 */
interface EQ12Bet {}

/**
 * @template TGame of array{
 *   id: string,
 *   sport_key: string,
 *   sport_title: string,
 *   commence_time: string,
 *   home_team: string,
 *   away_team: string,
 *   bookmakers: array<array{
 *     key: string,
 *     title: string,
 *     markets: array<array{
 *       key: string,
 *       outcomes: array<array{
 *         name: string,
 *         price: int|float,
 *         point?: float
 *       }>
 *     }>
 *   }>
 * }
 */
interface EQ12Game {}

/**
 * @template TSGP of array{
 *   game_id: string,
 *   legs: array<TBet>,
 *   total_odds: float,
 *   combined_probability: float,
 *   expected_value: float,
 *   kelly_fraction: float,
 *   confidence_level: string,
 *   correlations: array<string, float>
 * }
 */
interface EQ12SGP {}
