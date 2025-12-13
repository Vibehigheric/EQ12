<?php

/**
 * The Odds API v4 - Complete Type Definitions
 * 
 * Professional type definitions for The Odds API v4
 * Provides perfect IntelliSense for all API responses and data structures
 * 
 * @package SportsApiTypes\TheOddsAPI
 * @version 4.0.0
 * @author EQ12 Sports Development Team
 * @link https://the-odds-api.com/
 */

declare(strict_types=1);

namespace SportsApiTypes\TheOddsAPI;

/**
 * ==========================================================================
 * CORE API RESPONSE TYPES
 * ==========================================================================
 */

/**
 * Sports List Response
 * GET /v4/sports
 * 
 * @psalm-immutable
 */
class SportsResponse
{
    /**
     * @param Sport[] $sports
     */
    public function __construct(
        public readonly array $sports
    ) {}

    /**
     * @return array<string, Sport>
     */
    public function getSportsByKey(): array
    {
        $result = [];
        foreach ($this->sports as $sport) {
            $result[$sport->key] = $sport;
        }
        return $result;
    }
}

/**
 * Individual Sport Information
 * 
 * @psalm-immutable
 */
class Sport
{
    public function __construct(
        public readonly string $key,
        public readonly string $group,
        public readonly string $title,
        public readonly string $description,
        public readonly bool $active,
        public readonly bool $has_outrights
    ) {}

    /**
     * @return array{
     *   key: string,
     *   group: string,
     *   title: string,
     *   description: string,
     *   active: bool,
     *   has_outrights: bool
     * }
     */
    public function toArray(): array
    {
        return [
            'key' => $this->key,
            'group' => $this->group,
            'title' => $this->title,
            'description' => $this->description,
            'active' => $this->active,
            'has_outrights' => $this->has_outrights
        ];
    }
}

/**
 * Odds Response 
 * GET /v4/sports/{sport}/odds
 * 
 * @psalm-immutable
 */
class OddsResponse
{
    /**
     * @param Game[] $games
     */
    public function __construct(
        public readonly array $games
    ) {}

    /**
     * Get games starting today
     * 
     * @return Game[]
     */
    public function getTodaysGames(): array
    {
        $today = date('Y-m-d');
        return array_filter(
            $this->games,
            fn(Game $game) => $game->commence_time->format('Y-m-d') === $today
        );
    }

    /**
     * Get games by team
     * 
     * @param string $teamName
     * @return Game[]
     */
    public function getGamesByTeam(string $teamName): array
    {
        return array_filter(
            $this->games,
            fn(Game $game) => $game->home_team === $teamName || $game->away_team === $teamName
        );
    }
}

/**
 * Individual Game with Odds
 * 
 * @psalm-immutable
 */
class Game
{
    /**
     * @param Bookmaker[] $bookmakers
     */
    public function __construct(
        public readonly string $id,
        public readonly string $sport_key,
        public readonly string $sport_title,
        public readonly \DateTimeImmutable $commence_time,
        public readonly string $home_team,
        public readonly string $away_team,
        public readonly array $bookmakers
    ) {}

    /**
     * Get specific bookmaker odds
     * 
     * @param string $bookmakerId
     * @return Bookmaker|null
     */
    public function getBookmaker(string $bookmakerId): ?Bookmaker
    {
        foreach ($this->bookmakers as $bookmaker) {
            if ($bookmaker->key === $bookmakerId) {
                return $bookmaker;
            }
        }
        return null;
    }

    /**
     * Get best odds for each market across all bookmakers
     * 
     * @return array<string, BestOdds>
     */
    public function getBestOdds(): array
    {
        $bestOdds = [];

        foreach ($this->bookmakers as $bookmaker) {
            foreach ($bookmaker->markets as $market) {
                $marketKey = $market->key;

                if (!isset($bestOdds[$marketKey])) {
                    $bestOdds[$marketKey] = new BestOdds($marketKey, []);
                }

                foreach ($market->outcomes as $outcome) {
                    $bestOdds[$marketKey]->addOutcome($outcome, $bookmaker->key);
                }
            }
        }

        return $bestOdds;
    }

    /**
     * @return array{
     *   id: string,
     *   sport_key: string,
     *   sport_title: string,
     *   commence_time: string,
     *   home_team: string,
     *   away_team: string,
     *   bookmakers_count: int
     * }
     */
    public function toArray(): array
    {
        return [
            'id' => $this->id,
            'sport_key' => $this->sport_key,
            'sport_title' => $this->sport_title,
            'commence_time' => $this->commence_time->format('c'),
            'home_team' => $this->home_team,
            'away_team' => $this->away_team,
            'bookmakers_count' => count($this->bookmakers)
        ];
    }
}

/**
 * Bookmaker with Markets and Odds
 * 
 * @psalm-immutable
 */
class Bookmaker
{
    /**
     * @param Market[] $markets
     */
    public function __construct(
        public readonly string $key,
        public readonly string $title,
        public readonly \DateTimeImmutable $last_update,
        public readonly array $markets
    ) {}

    /**
     * Get specific market
     * 
     * @param string $marketKey
     * @return Market|null
     */
    public function getMarket(string $marketKey): ?Market
    {
        foreach ($this->markets as $market) {
            if ($market->key === $marketKey) {
                return $market;
            }
        }
        return null;
    }

    /**
     * Get moneyline market (h2h)
     * 
     * @return Market|null
     */
    public function getMoneyline(): ?Market
    {
        return $this->getMarket('h2h');
    }

    /**
     * Get spread market
     * 
     * @return Market|null
     */
    public function getSpread(): ?Market
    {
        return $this->getMarket('spreads');
    }

    /**
     * Get totals market
     * 
     * @return Market|null
     */
    public function getTotals(): ?Market
    {
        return $this->getMarket('totals');
    }
}

/**
 * Individual Betting Market (h2h, spreads, totals, etc.)
 * 
 * @psalm-immutable
 */
class Market
{
    /**
     * @param Outcome[] $outcomes
     */
    public function __construct(
        public readonly string $key,
        public readonly array $outcomes,
        public readonly ?\DateTimeImmutable $last_update = null
    ) {}

    /**
     * Get outcome by name
     * 
     * @param string $name
     * @return Outcome|null
     */
    public function getOutcome(string $name): ?Outcome
    {
        foreach ($this->outcomes as $outcome) {
            if ($outcome->name === $name) {
                return $outcome;
            }
        }
        return null;
    }

    /**
     * Get home team outcome
     * 
     * @param string $homeTeam
     * @return Outcome|null
     */
    public function getHomeOutcome(string $homeTeam): ?Outcome
    {
        return $this->getOutcome($homeTeam);
    }

    /**
     * Get away team outcome
     * 
     * @param string $awayTeam
     * @return Outcome|null
     */
    public function getAwayOutcome(string $awayTeam): ?Outcome
    {
        return $this->getOutcome($awayTeam);
    }

    /**
     * Get over outcome (for totals)
     * 
     * @return Outcome|null
     */
    public function getOverOutcome(): ?Outcome
    {
        return $this->getOutcome('Over');
    }

    /**
     * Get under outcome (for totals)
     * 
     * @return Outcome|null
     */
    public function getUnderOutcome(): ?Outcome
    {
        return $this->getOutcome('Under');
    }
}

/**
 * Individual Betting Outcome/Line
 * 
 * @psalm-immutable
 */
class Outcome
{
    public function __construct(
        public readonly string $name,
        public readonly float $price,
        public readonly ?float $point = null
    ) {}

    /**
     * Convert American odds to decimal
     * 
     * @return float
     */
    public function getDecimalOdds(): float
    {
        if ($this->price > 0) {
            return ($this->price / 100) + 1;
        } else {
            return (100 / abs($this->price)) + 1;
        }
    }

    /**
     * Calculate implied probability
     * 
     * @return float
     */
    public function getImpliedProbability(): float
    {
        if ($this->price > 0) {
            return 100 / ($this->price + 100);
        } else {
            return abs($this->price) / (abs($this->price) + 100);
        }
    }

    /**
     * Check if this is a favorite (negative odds)
     * 
     * @return bool
     */
    public function isFavorite(): bool
    {
        return $this->price < 0;
    }

    /**
     * Calculate payout for a given stake
     * 
     * @param float $stake
     * @return float
     */
    public function calculatePayout(float $stake): float
    {
        $decimal = $this->getDecimalOdds();
        return $stake * $decimal;
    }

    /**
     * @return array{
     *   name: string,
     *   price: float,
     *   point: float|null,
     *   decimal_odds: float,
     *   implied_probability: float,
     *   is_favorite: bool
     * }
     */
    public function toArray(): array
    {
        return [
            'name' => $this->name,
            'price' => $this->price,
            'point' => $this->point,
            'decimal_odds' => $this->getDecimalOdds(),
            'implied_probability' => $this->getImpliedProbability(),
            'is_favorite' => $this->isFavorite()
        ];
    }
}

/**
 * ==========================================================================
 * ENHANCED BETTING ANALYSIS TYPES
 * ==========================================================================
 */

/**
 * Best Odds Aggregator
 */
class BestOdds
{
    /**
     * @param array<string, BestOutcome> $outcomes
     */
    public function __construct(
        public readonly string $marketKey,
        private array $outcomes = []
    ) {}

    public function addOutcome(Outcome $outcome, string $bookmakerKey): void
    {
        $name = $outcome->name;

        if (
            !isset($this->outcomes[$name]) ||
            $this->outcomes[$name]->outcome->price < $outcome->price
        ) {

            $this->outcomes[$name] = new BestOutcome(
                $outcome,
                $bookmakerKey
            );
        }
    }

    /**
     * @return array<string, BestOutcome>
     */
    public function getOutcomes(): array
    {
        return $this->outcomes;
    }
}

/**
 * Best outcome for a specific selection
 * 
 * @psalm-immutable
 */
class BestOutcome
{
    public function __construct(
        public readonly Outcome $outcome,
        public readonly string $bookmakerKey
    ) {}
}

/**
 * Arbitrage Opportunity
 * 
 * @psalm-immutable
 */
class ArbitrageOpportunity
{
    /**
     * @param BestOutcome[] $legs
     */
    public function __construct(
        public readonly string $gameId,
        public readonly string $marketKey,
        public readonly array $legs,
        public readonly float $totalImpliedProbability,
        public readonly float $profitMargin
    ) {}

    /**
     * Calculate stake allocation for guaranteed profit
     * 
     * @param float $totalStake
     * @return array<string, float>
     */
    public function calculateStakeAllocation(float $totalStake): array
    {
        $allocation = [];

        foreach ($this->legs as $name => $leg) {
            $impliedProb = $leg->outcome->getImpliedProbability();
            $allocation[$name] = ($totalStake * $impliedProb) / $this->totalImpliedProbability;
        }

        return $allocation;
    }
}

/**
 * ==========================================================================
 * SPORT-SPECIFIC TYPE EXTENSIONS
 * ==========================================================================
 */

/**
 * NFL-specific game data
 * 
 * @psalm-immutable
 */
class NFLGame extends Game
{
    /**
     * Get player props market
     * 
     * @return Market|null
     */
    public function getPlayerProps(): ?Market
    {
        return $this->getBookmaker('draftkings')?->getMarket('player_props');
    }

    /**
     * Get alternate spreads
     * 
     * @return Market|null
     */
    public function getAlternateSpreads(): ?Market
    {
        return $this->getBookmaker('draftkings')?->getMarket('alternate_spreads');
    }
}

/**
 * NBA-specific game data
 * 
 * @psalm-immutable
 */
class NBAGame extends Game
{
    /**
     * Get player points market
     * 
     * @return Market|null
     */
    public function getPlayerPoints(): ?Market
    {
        return $this->getBookmaker('draftkings')?->getMarket('player_points');
    }

    /**
     * Get quarter betting markets
     * 
     * @return Market[]
     */
    public function getQuarterMarkets(): array
    {
        $quarters = [];
        foreach (['q1', 'q2', 'q3', 'q4'] as $quarter) {
            $market = $this->getBookmaker('draftkings')?->getMarket("{$quarter}_h2h");
            if ($market) {
                $quarters[$quarter] = $market;
            }
        }
        return $quarters;
    }
}

/**
 * NHL-specific game data
 * 
 * @psalm-immutable  
 */
class NHLGame extends Game
{
    /**
     * Get regulation time market (excludes overtime)
     * 
     * @return Market|null
     */
    public function getRegulationTime(): ?Market
    {
        return $this->getBookmaker('draftkings')?->getMarket('h2h_regulation');
    }

    /**
     * Get puck line (NHL spread equivalent)
     * 
     * @return Market|null
     */
    public function getPuckLine(): ?Market
    {
        return $this->getSpread();
    }
}

/**
 * MLB-specific game data
 * 
 * @psalm-immutable
 */
class MLBGame extends Game
{
    /**
     * Get run line (MLB spread equivalent)
     * 
     * @return Market|null
     */
    public function getRunLine(): ?Market
    {
        return $this->getSpread();
    }

    /**
     * Get first 5 innings market
     * 
     * @return Market|null
     */
    public function getFirst5Innings(): ?Market
    {
        return $this->getBookmaker('draftkings')?->getMarket('h2h_f5');
    }

    /**
     * Get innings totals
     * 
     * @return Market[]
     */
    public function getInningsTotals(): array
    {
        $innings = [];
        for ($i = 1; $i <= 9; $i++) {
            $market = $this->getBookmaker('draftkings')?->getMarket("inning_{$i}_total");
            if ($market) {
                $innings["inning_{$i}"] = $market;
            }
        }
        return $innings;
    }
}

/**
 * ==========================================================================
 * API CLIENT HELPER TYPES
 * ==========================================================================
 */

/**
 * API Configuration
 * 
 * @psalm-immutable
 */
class APIConfig
{
    /**
     * @param string[] $markets
     * @param string[] $bookmakers
     * @param string[] $regions
     */
    public function __construct(
        public readonly string $apiKey,
        public readonly string $baseUrl = 'https://api.the-odds-api.com',
        public readonly array $markets = ['h2h', 'spreads', 'totals'],
        public readonly array $bookmakers = [],
        public readonly array $regions = ['us'],
        public readonly string $dateFormat = 'iso',
        public readonly string $oddsFormat = 'american'
    ) {}

    /**
     * Build query parameters for API request
     * 
     * @return array<string, string>
     */
    public function buildQueryParams(): array
    {
        $params = [
            'apiKey' => $this->apiKey,
            'regions' => implode(',', $this->regions),
            'markets' => implode(',', $this->markets),
            'dateFormat' => $this->dateFormat,
            'oddsFormat' => $this->oddsFormat
        ];

        if (!empty($this->bookmakers)) {
            $params['bookmakers'] = implode(',', $this->bookmakers);
        }

        return $params;
    }
}

/**
 * API Rate Limit Information
 * 
 * @psalm-immutable
 */
class RateLimitInfo
{
    public function __construct(
        public readonly int $remaining,
        public readonly int $used,
        public readonly \DateTimeImmutable $resetTime
    ) {}

    /**
     * Check if rate limit allows another request
     * 
     * @return bool
     */
    public function canMakeRequest(): bool
    {
        return $this->remaining > 0;
    }

    /**
     * Get seconds until rate limit resets
     * 
     * @return int
     */
    public function getSecondsUntilReset(): int
    {
        $now = new \DateTimeImmutable();
        return max(0, $this->resetTime->getTimestamp() - $now->getTimestamp());
    }
}

/**
 * ==========================================================================
 * HELPER FUNCTIONS FOR PERFECT INTELEPHENSE SUPPORT
 * ==========================================================================
 */

/**
 * Fetch sports list with full type safety
 * 
 * @param APIConfig $config
 * @return SportsResponse
 */
function fetch_sports(APIConfig $config): SportsResponse
{
    // Implementation would make HTTP request
    return new SportsResponse([]);
}

/**
 * Fetch odds for a sport with full type safety
 * 
 * @param string $sport
 * @param APIConfig $config
 * @return OddsResponse
 */
function fetch_odds(string $sport, APIConfig $config): OddsResponse
{
    // Implementation would make HTTP request
    return new OddsResponse([]);
}

/**
 * Find arbitrage opportunities across bookmakers
 * 
 * @param Game[] $games
 * @param float $minProfitMargin
 * @return ArbitrageOpportunity[]
 */
function find_arbitrage_opportunities(array $games, float $minProfitMargin = 0.01): array
{
    $opportunities = [];

    foreach ($games as $game) {
        $bestOdds = $game->getBestOdds();

        foreach ($bestOdds as $marketKey => $market) {
            $outcomes = $market->getOutcomes();
            $totalImpliedProb = array_sum(
                array_map(
                    fn(BestOutcome $outcome) => $outcome->outcome->getImpliedProbability(),
                    $outcomes
                )
            );

            if ($totalImpliedProb < (1 - $minProfitMargin)) {
                $opportunities[] = new ArbitrageOpportunity(
                    $game->id,
                    $marketKey,
                    $outcomes,
                    $totalImpliedProb,
                    1 - $totalImpliedProb
                );
            }
        }
    }

    return $opportunities;
}

/**
 * Calculate optimal Kelly criterion stakes
 * 
 * @param Outcome $outcome
 * @param float $trueProbability
 * @param float $bankroll
 * @param float $maxKelly
 * @return float
 */
function calculate_kelly_stake(
    Outcome $outcome,
    float $trueProbability,
    float $bankroll,
    float $maxKelly = 0.25
): float {
    $decimalOdds = $outcome->getDecimalOdds();
    $b = $decimalOdds - 1;
    $p = $trueProbability;
    $q = 1 - $p;

    $kelly = ($b * $p - $q) / $b;
    $kellyPercent = min($kelly, $maxKelly);

    return max(0, $bankroll * $kellyPercent);
}

/**
 * Build same-game parlay from multiple outcomes
 * 
 * @param Game $game
 * @param Outcome[] $legs
 * @return array{
 *   combined_odds: float,
 *   total_probability: float,
 *   expected_payout: float,
 *   kelly_stake: float
 * }
 */
function build_same_game_parlay(Game $game, array $legs): array
{
    $combinedOdds = 1.0;
    $totalProbability = 1.0;

    foreach ($legs as $leg) {
        $combinedOdds *= $leg->getDecimalOdds();
        $totalProbability *= $leg->getImpliedProbability();
    }

    return [
        'combined_odds' => $combinedOdds,
        'total_probability' => $totalProbability,
        'expected_payout' => $combinedOdds,
        'kelly_stake' => calculate_kelly_stake(
            new Outcome('Parlay', ($combinedOdds - 1) * 100),
            $totalProbability,
            1000.0
        )
    ];
}
