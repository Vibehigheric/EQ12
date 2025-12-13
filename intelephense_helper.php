<?php
/**
 * EQ12 Intelephense Helper - Professional IDE Type Definitions
 * 
 * This file exists to help Intelephense understand concrete types used by EQ12.
 * It is NOT loaded in production. Do not include() it.
 * 
 * According to the master prompt: "tell Intelephense that our functions return concrete types"
 * 
 * @package EQ12
 * @author EQ12 Platform Team
 * @since 1.0.0
 */

// Prevent accidental execution in production
if (defined('EQ12_PRODUCTION_MODE') && EQ12_PRODUCTION_MODE) {
    throw new LogicException('Intelephense helper should not be loaded in production');
}

// ========== EQ12 FRAMEWORK TYPE OVERRIDES ==========

if (!function_exists('eq12_odds_client')) {
    /**
     * Get EQ12 Odds API Client instance
     * 
     * @return \EQ12\Services\OddsApiClient
     */
    function eq12_odds_client(): \EQ12\Services\OddsApiClient {}
}

if (!function_exists('eq12_betting_engine')) {
    /**
     * Get EQ12 Betting Analysis Engine
     * 
     * @return \EQ12\Analytics\BettingEngine
     */
    function eq12_betting_engine(): \EQ12\Analytics\BettingEngine {}
}

if (!function_exists('eq12_sgp_builder')) {
    /**
     * Get EQ12 Same Game Parlay Builder
     * 
     * @return \EQ12\Builders\SgpBuilder
     */
    function eq12_sgp_builder(): \EQ12\Builders\SgpBuilder {}
}

if (!function_exists('eq12_response')) {
    /**
     * Create EQ12 API Response
     * 
     * @param array<string, mixed> $data Response data
     * @param int $status HTTP status code
     * @param array<string, string> $headers Additional headers
     * @return \EQ12\Http\ApiResponse
     */
    function eq12_response(array $data = [], int $status = 200, array $headers = []): \EQ12\Http\ApiResponse {}
}

if (!function_exists('eq12_cache')) {
    /**
     * Get EQ12 Cache Manager
     * 
     * @return \EQ12\Cache\CacheManager
     */
    function eq12_cache(): \EQ12\Cache\CacheManager {}
}

if (!function_exists('eq12_logger')) {
    /**
     * Get EQ12 Logger instance
     * 
     * @return \EQ12\Logging\Logger
     */
    function eq12_logger(): \EQ12\Logging\Logger {}
}

if (!function_exists('eq12_config')) {
    /**
     * Get configuration value with type safety
     * 
     * @param string $key Configuration key
     * @param mixed $default Default value
     * @return mixed Configuration value
     */
    function eq12_config(string $key, $default = null) {}
}

// ========== EQ12 CONCRETE CLASSES FOR INTELEPHENSE ==========

namespace EQ12\Services {
    /**
     * EQ12 Odds API Client with type-safe methods
     */
    class OddsApiClient {
        /**
         * @return array<int, array{id: string, sport_key: string, sport_title: string, commence_time: string, home_team: string, away_team: string, bookmakers: array}>
         */
        public function getOdds(string $sport, string $region = 'us', string $market = 'h2h'): array {}
        
        /**
         * @return array<int, array{key: string, group: string, title: string, description: string, active: bool, has_outrights: bool}>
         */
        public function getSports(): array {}
        
        /**
         * @param array<string> $eventIds
         * @return array<string, array{id: string, home_team: string, away_team: string, commence_time: string, sport_key: string}>
         */
        public function getEventsByIds(array $eventIds): array {}
    }
}

namespace EQ12\Analytics {
    /**
     * EQ12 Betting Analysis Engine
     */
    class BettingEngine {
        /**
         * @param float $probability Win probability (0-1)
         * @param float $odds Decimal odds
         * @param float $bankroll Available bankroll
         * @param float $maxKelly Maximum Kelly fraction
         * @return array{fraction: float, stake: float, expected_value: float, recommended: bool}
         */
        public function calculateKelly(float $probability, float $odds, float $bankroll, float $maxKelly = 0.25): array {}
        
        /**
         * @param array<array{probability: float, odds: float}> $legs
         * @return array{combined_odds: float, win_probability: float, expected_value: float, kelly_fraction: float}
         */
        public function analyzeSgp(array $legs): array {}
        
        /**
         * @return array{games: array, recommendations: array, risk_analysis: array}
         */
        public function nhlAnalysis(): array {}
    }
}

namespace EQ12\Builders {
    /**
     * EQ12 Same Game Parlay Builder
     */
    class SgpBuilder {
        /**
         * @param string $gameId
         * @param array<array{market: string, selection: string, odds: float}> $selections
         * @return array{legs: array, combined_odds: float, stake_recommendation: float, confidence: float}
         */
        public function buildSgp(string $gameId, array $selections): array {}
        
        /**
         * @param array<string> $gameIds
         * @param int $maxLegs
         * @return array<array{game_id: string, legs: array, roi: float, confidence: float}>
         */
        public function buildStackedSgp(array $gameIds, int $maxLegs = 20): array {}
        
        /**
         * @param array<array{game_id: string, legs: array, confidence: float}> $sgps
         * @return array{optimized_legs: array, removed_legs: array, improved_probability: float}
         */
        public function optimizeByConfidence(array $sgps): array {}
    }
}

namespace EQ12\Http {
    /**
     * EQ12 API Response with structured data
     */
    class ApiResponse {
        /**
         * @param array<string, mixed> $data
         */
        public function __construct(array $data = [], int $status = 200, array $headers = []) {}
        
        /**
         * @return array<string, mixed>
         */
        public function getData(): array {}
        
        public function getStatus(): int {}
        
        /**
         * @return array<string, string>
         */
        public function getHeaders(): array {}
        
        public function toJson(): string {}
    }
}

namespace EQ12\Cache {
    /**
     * EQ12 Cache Manager
     */
    class CacheManager {
        /**
         * @param mixed $value
         */
        public function set(string $key, $value, int $ttl = 3600): bool {}
        
        /**
         * @param mixed $default
         * @return mixed
         */
        public function get(string $key, $default = null) {}
        
        public function delete(string $key): bool {}
        
        public function clear(): bool {}
        
        public function has(string $key): bool {}
    }
}

namespace EQ12\Logging {
    /**
     * EQ12 Logger with structured logging
     */
    class Logger {
        /**
         * @param array<string, mixed> $context
         */
        public function info(string $message, array $context = []): void {}
        
        /**
         * @param array<string, mixed> $context
         */
        public function error(string $message, array $context = []): void {}
        
        /**
         * @param array<string, mixed> $context
         */
        public function warning(string $message, array $context = []): void {}
        
        /**
         * @param array<string, mixed> $context
         */
        public function debug(string $message, array $context = []): void {}
        
        /**
         * @param array<string, mixed> $bettingData
         */
        public function logBettingEvent(string $eventType, array $bettingData): void {}
    }
}

// ========== EQ12 UTILITY INTERFACES ==========

/**
 * Interface for EQ12 Odds Providers
 */
interface OddsProvider {
    /**
     * Get best odds for specific event
     * 
     * @param string $eventId Event identifier
     * @return array{home: float, away: float, draw?: float, bookmaker: string, updated_at: string}
     */
    public function bestOddsFor(string $eventId): array;
    
    /**
     * Get historical odds data
     * 
     * @param string $eventId
     * @param \DateTime $from
     * @param \DateTime $to
     * @return array<array{timestamp: string, odds: array, bookmaker: string}>
     */
    public function getHistoricalOdds(string $eventId, \DateTime $from, \DateTime $to): array;
}

/**
 * Interface for EQ12 Risk Managers
 */
interface RiskManager {
    /**
     * Analyze portfolio risk
     * 
     * @param array<array{sport: string, amount: float, odds: float, probability: float}> $positions
     * @return array{total_risk: float, max_loss: float, kelly_violations: int, recommendations: array}
     */
    public function analyzePortfolioRisk(array $positions): array;
    
    /**
     * Check if bet meets risk criteria
     * 
     * @param array{amount: float, odds: float, probability: float, sport: string} $bet
     * @return array{approved: bool, reasons: array<string>, suggested_stake?: float}
     */
    public function validateBet(array $bet): array;
}

// ========== EQ12 MATHEMATICAL UTILITIES ==========

/**
 * EQ12 Betting Mathematics Helper
 */
class EQ12BettingMath {
    /**
     * Calculate correlation between two arrays
     * 
     * @param array<float> $x
     * @param array<float> $y
     */
    public static function calculateCorrelation(array $x, array $y): float {}
    
    /**
     * Convert American odds to decimal
     */
    public static function americanToDecimal(int $americanOdds): float {}
    
    /**
     * Convert decimal odds to implied probability
     */
    public static function oddsToImpliedProbability(float $decimalOdds): float {}
    
    /**
     * Calculate expected value
     */
    public static function expectedValue(float $probability, float $odds, float $stake): float {}
    
    /**
     * Calculate optimal Kelly fraction
     */
    public static function kellyFraction(float $probability, float $odds): float {}
    
    /**
     * Combine multiple probabilities
     * 
     * @param array<float> $probabilities
     */
    public static function combineProbabilities(array $probabilities): float {}
}

// ========== GLOBAL EQ12 HELPER FUNCTIONS ==========

/**
 * Get environment variable with type casting
 * 
 * @param string $key Environment variable name
 * @param mixed $default Default value if not found
 * @return mixed Environment value or default
 */
function eq12_env(string $key, $default = null) {}

/**
 * Format currency for display
 * 
 * @param float $amount Amount to format
 * @param string $currency Currency symbol
 * @return string Formatted currency string
 */
function eq12_format_currency(float $amount, string $currency = '$'): string {}

/**
 * Convert UTC timestamp to local timezone
 * 
 * @param string $utcTimestamp UTC timestamp string
 * @param string $timezone Target timezone (default: America/New_York)
 * @return string Formatted local timestamp
 */
function eq12_utc_to_local(string $utcTimestamp, string $timezone = 'America/New_York'): string {}

/**
 * Log structured data to EQ12 logs directory
 * 
 * @param array<string, mixed> $data Data to log
 * @param string $type Log type (betting, analysis, error)
 * @return bool Success status
 */
function eq12_log_structured(array $data, string $type = 'general'): bool {}

/**
 * Validate EQ12 API key format
 * 
 * @param string $apiKey API key to validate
 * @return bool True if valid format
 */
function eq12_validate_api_key(string $apiKey): bool {}

/**
 * Generate EQ12 correlation matrix for sports
 * 
 * @param array<string> $sports Sport keys
 * @return array<string, array<string, float>> Correlation matrix
 */
function eq12_generate_correlation_matrix(array $sports): array {}

// ========== EQ12 CONSTANTS FOR INTELEPHENSE ==========

/**
 * EQ12 System Constants
 */
const EQ12_VERSION = '2.0.0';
const EQ12_API_BASE_URL = 'https://api.the-odds-api.com/v4';
const EQ12_MAX_KELLY_FRACTION = 0.25;
const EQ12_MIN_ODDS_THRESHOLD = 1.10;
const EQ12_MAX_LEGS_PER_SGP = 20;
const EQ12_CACHE_TTL_ODDS = 300; // 5 minutes
const EQ12_CACHE_TTL_SPORTS = 3600; // 1 hour
const EQ12_LOG_LEVEL_DEBUG = 0;
const EQ12_LOG_LEVEL_INFO = 1;
const EQ12_LOG_LEVEL_WARNING = 2;
const EQ12_LOG_LEVEL_ERROR = 3;