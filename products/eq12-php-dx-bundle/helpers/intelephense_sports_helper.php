<?php

/**
 * EQ12 Sports Betting Intelephense Helper
 * 
 * Professional type definitions for sports betting applications
 * Provides IntelliSense for odds calculations, betting models, and portfolio management
 * 
 * @package EQ12\SportsHelper
 * @version 1.0.0
 * @author EQ12 Development Team
 */

// Prevent execution in production
if (!defined('INTELEPHENSE_HELPER') && !class_exists('IntelephenseHelper')) {
    return;
}

/**
 * ==========================================================================
 * CORE BETTING TYPES
 * ==========================================================================
 */

/**
 * @template T of numeric
 */
class AmericanOdds
{
    /** @param T $value */
    public function __construct(public readonly mixed $value) {}

    /** @return DecimalOdds<float> */
    public function toDecimal(): DecimalOdds
    {
        return new DecimalOdds(0.0);
    }

    /** @return float */
    public function toImpliedProbability(): float
    {
        return 0.0;
    }

    /** @return bool */
    public function isFavorite(): bool
    {
        return $this->value < 0;
    }
}

/**
 * @template T of numeric
 */
class DecimalOdds
{
    /** @param T $value */
    public function __construct(public readonly mixed $value) {}

    /** @return AmericanOdds<int> */
    public function toAmerican(): AmericanOdds
    {
        return new AmericanOdds(0);
    }

    /** @return float */
    public function toImpliedProbability(): float
    {
        return 1.0 / $this->value;
    }
}

/**
 * @template T of numeric
 */
class Stake
{
    /** @param T $amount */
    public function __construct(
        public readonly mixed $amount,
        public readonly string $currency = 'USD'
    ) {}

    /**
     * @param DecimalOdds<float> $odds
     * @return Payout<T>
     */
    public function calculatePayout(DecimalOdds $odds): Payout
    {
        return new Payout($this->amount * $odds->value, $this->currency);
    }
}

/**
 * @template T of numeric
 */
class Payout
{
    /** @param T $amount */
    public function __construct(
        public readonly mixed $amount,
        public readonly string $currency = 'USD'
    ) {}

    /** @return float */
    public function getROI(): float
    {
        return ($this->amount - 100) / 100;
    }
}

/**
 * ==========================================================================
 * ADVANCED BETTING STRUCTURES
 * ==========================================================================
 */

/**
 * Same Game Parlay (SGP) Leg
 * @psalm-immutable
 */
class SGPLeg
{
    public function __construct(
        public readonly string $market,
        public readonly string $selection,
        public readonly AmericanOdds $odds,
        public readonly float $probability,
        public readonly float $confidence,
        public readonly string $reasoning = ''
    ) {}

    /** @return array{market: string, selection: string, odds: int, probability: float, confidence: float} */
    public function toArray(): array
    {
        return [
            'market' => $this->market,
            'selection' => $this->selection,
            'odds' => $this->odds->value,
            'probability' => $this->probability,
            'confidence' => $this->confidence
        ];
    }
}

/**
 * Complete SGP Recommendation
 * @psalm-immutable
 */
class SGPRecommendation
{
    /**
     * @param SGPLeg[] $legs
     * @param Stake<numeric> $recommendedStake
     */
    public function __construct(
        public readonly array $legs,
        public readonly float $combinedOdds,
        public readonly float $winProbability,
        public readonly Stake $recommendedStake,
        public readonly float $expectedValue,
        public readonly string $gameId,
        public readonly string $sport
    ) {}

    /** @return float */
    public function getROI(): float
    {
        return ($this->combinedOdds - 1) * $this->winProbability - (1 - $this->winProbability);
    }

    /** @return bool */
    public function meetsKellyCriterion(): bool
    {
        return $this->expectedValue > 0;
    }

    /** @return array{legs: array, combined_odds: float, win_probability: float, expected_value: float, kelly_bet: float} */
    public function toArray(): array
    {
        return [
            'legs' => array_map(fn($leg) => $leg->toArray(), $this->legs),
            'combined_odds' => $this->combinedOdds,
            'win_probability' => $this->winProbability,
            'expected_value' => $this->expectedValue,
            'kelly_bet' => $this->recommendedStake->amount
        ];
    }
}

/**
 * ==========================================================================
 * ODDS API INTEGRATION TYPES
 * ==========================================================================
 */

/**
 * The Odds API v4 Response Structure
 * @psalm-immutable
 */
class OddsApiGame
{
    /**
     * @param array{
     *   home_team: string,
     *   away_team: string,
     *   commence_time: string,
     *   bookmakers: OddsApiBookmaker[]
     * } $gameData
     */
    public function __construct(
        public readonly string $id,
        public readonly string $sport_key,
        public readonly string $home_team,
        public readonly string $away_team,
        public readonly \DateTimeImmutable $commence_time,
        public readonly array $bookmakers
    ) {}

    /** @return bool */
    public function isToday(): bool
    {
        return $this->commence_time->format('Y-m-d') === date('Y-m-d');
    }

    /**
     * @param string $bookmaker
     * @return OddsApiBookmaker|null
     */
    public function getBookmaker(string $bookmaker): ?OddsApiBookmaker
    {
        foreach ($this->bookmakers as $book) {
            if ($book->key === $bookmaker) {
                return $book;
            }
        }
        return null;
    }
}

/**
 * @psalm-immutable
 */
class OddsApiBookmaker
{
    /**
     * @param OddsApiMarket[] $markets
     */
    public function __construct(
        public readonly string $key,
        public readonly string $title,
        public readonly \DateTimeImmutable $last_update,
        public readonly array $markets
    ) {}

    /**
     * @param string $marketKey
     * @return OddsApiMarket|null
     */
    public function getMarket(string $marketKey): ?OddsApiMarket
    {
        foreach ($this->markets as $market) {
            if ($market->key === $marketKey) {
                return $market;
            }
        }
        return null;
    }
}

/**
 * @psalm-immutable
 */
class OddsApiMarket
{
    /**
     * @param OddsApiOutcome[] $outcomes
     */
    public function __construct(
        public readonly string $key,
        public readonly array $outcomes,
        public readonly ?float $point = null
    ) {}

    /**
     * @param string $name
     * @return OddsApiOutcome|null
     */
    public function getOutcome(string $name): ?OddsApiOutcome
    {
        foreach ($this->outcomes as $outcome) {
            if ($outcome->name === $name) {
                return $outcome;
            }
        }
        return null;
    }
}

/**
 * @psalm-immutable
 */
class OddsApiOutcome
{
    public function __construct(
        public readonly string $name,
        public readonly AmericanOdds $price,
        public readonly ?float $point = null
    ) {}

    /** @return DecimalOdds<float> */
    public function getDecimalOdds(): DecimalOdds
    {
        return $this->price->toDecimal();
    }

    /** @return float */
    public function getImpliedProbability(): float
    {
        return $this->price->toImpliedProbability();
    }
}

/**
 * ==========================================================================
 * PORTFOLIO & RISK MANAGEMENT
 * ==========================================================================
 */

/**
 * Kelly Criterion Calculator
 */
class KellyCalculator
{
    /**
     * @param float $winProbability
     * @param DecimalOdds<float> $odds
     * @param float $maxBankrollPercent
     * @return float
     */
    public static function calculate(
        float $winProbability,
        DecimalOdds $odds,
        float $maxBankrollPercent = 0.25
    ): float {
        $b = $odds->value - 1;
        $p = $winProbability;
        $q = 1 - $p;

        $kelly = ($b * $p - $q) / $b;

        return min($kelly, $maxBankrollPercent);
    }

    /**
     * @param SGPRecommendation $sgp
     * @param float $bankroll
     * @return Stake<float>
     */
    public static function recommendStake(SGPRecommendation $sgp, float $bankroll): Stake
    {
        $kellyPercent = self::calculate(
            $sgp->winProbability,
            new DecimalOdds($sgp->combinedOdds)
        );

        return new Stake($bankroll * $kellyPercent);
    }
}

/**
 * Betting Portfolio Management
 */
class BettingPortfolio
{
    /**
     * @param SGPRecommendation[] $activeBets
     * @param float $totalBankroll
     */
    public function __construct(
        public readonly array $activeBets,
        public readonly float $totalBankroll,
        public readonly float $riskTolerance = 0.02
    ) {}

    /** @return float */
    public function getTotalRisk(): float
    {
        return array_sum(array_map(
            fn($bet) => $bet->recommendedStake->amount,
            $this->activeBets
        )) / $this->totalBankroll;
    }

    /** @return float */
    public function getExpectedReturn(): float
    {
        return array_sum(array_map(
            fn($bet) => $bet->expectedValue * $bet->recommendedStake->amount,
            $this->activeBets
        ));
    }

    /** @return bool */
    public function canAddBet(SGPRecommendation $newBet): bool
    {
        $newRisk = ($this->getTotalRisk() * $this->totalBankroll + $newBet->recommendedStake->amount) / $this->totalBankroll;
        return $newRisk <= $this->riskTolerance;
    }
}

/**
 * ==========================================================================
 * CORRELATION & ADVANCED ANALYTICS
 * ==========================================================================
 */

/**
 * Market Correlation Matrix for SGP Building
 */
class CorrelationMatrix
{
    /**
     * @param array<string, array<string, float>> $correlations
     */
    public function __construct(
        public readonly array $correlations,
        public readonly string $sport
    ) {}

    /**
     * @param string $market1
     * @param string $market2
     * @return float
     */
    public function getCorrelation(string $market1, string $market2): float
    {
        return $this->correlations[$market1][$market2] ?? 0.0;
    }

    /**
     * @param SGPLeg[] $legs
     * @return bool
     */
    public function hasContradictoryLegs(array $legs): bool
    {
        for ($i = 0; $i < count($legs); $i++) {
            for ($j = $i + 1; $j < count($legs); $j++) {
                $correlation = $this->getCorrelation($legs[$i]->market, $legs[$j]->market);
                if ($correlation < -0.5) {
                    return true;
                }
            }
        }
        return false;
    }
}

/**
 * Machine Learning Enhanced Probability Calculator
 */
class MLProbabilityEnhancer
{
    /**
     * @param array<string, mixed> $gameFeatures
     * @param string $model
     * @return float
     */
    public static function enhanceProbability(
        array $gameFeatures,
        string $model = 'xgboost'
    ): float {
        // Stub for ML model integration
        return 0.5;
    }

    /**
     * @param OddsApiGame $game
     * @param SGPLeg[] $legs
     * @return array<string, float>
     */
    public static function calculateEnhancedProbabilities(
        OddsApiGame $game,
        array $legs
    ): array {
        $probabilities = [];
        foreach ($legs as $leg) {
            $features = self::extractFeatures($game, $leg);
            $probabilities[$leg->market] = self::enhanceProbability($features);
        }
        return $probabilities;
    }

    /**
     * @param OddsApiGame $game
     * @param SGPLeg $leg
     * @return array<string, mixed>
     */
    private static function extractFeatures(OddsApiGame $game, SGPLeg $leg): array
    {
        return [
            'sport' => $game->sport_key,
            'market' => $leg->market,
            'home_team' => $game->home_team,
            'away_team' => $game->away_team,
            'commence_time' => $game->commence_time->format('H:i'),
            'odds' => $leg->odds->value
        ];
    }
}

/**
 * ==========================================================================
 * HELPER FUNCTIONS FOR INTELEPHENSE
 * ==========================================================================
 */

/**
 * Build an SGP recommendation with full type safety
 *
 * @param OddsApiGame $game
 * @param SGPLeg[] $legs  
 * @param float $bankroll
 * @return SGPRecommendation
 */
function build_sgp_recommendation(OddsApiGame $game, array $legs, float $bankroll): SGPRecommendation
{
    $combinedOdds = 1.0;
    $winProbability = 1.0;

    foreach ($legs as $leg) {
        $combinedOdds *= $leg->odds->toDecimal()->value;
        $winProbability *= $leg->probability;
    }

    $expectedValue = ($combinedOdds - 1) * $winProbability - (1 - $winProbability);
    $kellyStake = KellyCalculator::calculate($winProbability, new DecimalOdds($combinedOdds));

    return new SGPRecommendation(
        $legs,
        $combinedOdds,
        $winProbability,
        new Stake($bankroll * $kellyStake),
        $expectedValue,
        $game->id,
        $game->sport_key
    );
}

/**
 * Fetch odds from The Odds API with proper typing
 *
 * @param string $sport
 * @param string $apiKey
 * @param string[] $markets
 * @return OddsApiGame[]
 */
function fetch_odds_api_games(string $sport, string $apiKey, array $markets = ['h2h', 'spreads', 'totals']): array
{
    // Implementation would go here
    return [];
}

/**
 * Calculate optimal portfolio allocation
 *
 * @param SGPRecommendation[] $recommendations
 * @param float $totalBankroll
 * @param float $maxRisk
 * @return array{
 *   allocation: array<string, float>,
 *   total_risk: float,
 *   expected_return: float,
 *   sharpe_ratio: float
 * }
 */
function optimize_portfolio_allocation(
    array $recommendations,
    float $totalBankroll,
    float $maxRisk = 0.02
): array {
    return [
        'allocation' => [],
        'total_risk' => 0.0,
        'expected_return' => 0.0,
        'sharpe_ratio' => 0.0
    ];
}

/**
 * Generate correlation matrix for sport
 *
 * @param string $sport
 * @return CorrelationMatrix
 */
function get_sport_correlation_matrix(string $sport): CorrelationMatrix
{
    $correlations = [];

    switch ($sport) {
        case 'americanfootball_nfl':
            $correlations = [
                'h2h' => ['spreads' => 0.85, 'totals' => -0.1],
                'spreads' => ['h2h' => 0.85, 'totals' => -0.1],
                'totals' => ['h2h' => -0.1, 'spreads' => -0.1]
            ];
            break;
        case 'basketball_nba':
            $correlations = [
                'h2h' => ['spreads' => 0.90, 'totals' => 0.2],
                'spreads' => ['h2h' => 0.90, 'totals' => 0.2],
                'totals' => ['h2h' => 0.2, 'spreads' => 0.2]
            ];
            break;
        default:
            $correlations = [];
    }

    return new CorrelationMatrix($correlations, $sport);
}

/**
 * ==========================================================================
 * RUNTIME SAFETY GUARDS
 * ==========================================================================
 */

// Prevent any actual execution of this helper file
if (function_exists('header')) {
    header('HTTP/1.0 403 Forbidden');
    exit('This file is for IDE assistance only');
}

if (PHP_SAPI !== 'cli' && !defined('PHPUNIT_COMPOSER_INSTALL')) {
    die('This file is for IDE assistance only');
}
