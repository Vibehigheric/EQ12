# Sports API Type Packs
## Professional Type Libraries for Sports Betting APIs

**Perfect IntelliSense for every major sports betting API. Never guess data structures again.**

---

## 🎯 **What You Get**

### **The Odds API v4 Complete Types**
- ✅ **5,000+ lines** of professional type definitions
- ✅ **Perfect autocompletion** for all API responses
- ✅ **Sport-specific extensions** (NFL, NBA, NHL, MLB)
- ✅ **Advanced betting calculations** built-in
- ✅ **Arbitrage detection** helper functions
- ✅ **Kelly criterion** stake calculations

### **Major Sportsbook APIs**
- ✅ **DraftKings** API types
- ✅ **FanDuel** API types  
- ✅ **BetMGM** API types
- ✅ **Caesars** API types
- ✅ **PointsBet** API types

### **Data Provider APIs**
- ✅ **ESPN** sports data types
- ✅ **Yahoo Sports** API types
- ✅ **The Athletic** data types
- ✅ **SportsReference** API types

---

## 🚀 **Before vs After**

### **Before: Generic Arrays, No IntelliSense**
```php
// ❌ No autocompletion, no type safety
function processOdds($apiResponse) {
    foreach ($apiResponse as $game) {
        $homeTeam = $game['home_team']; // No autocomplete
        $bookmakers = $game['bookmakers']; // Unknown structure
        
        foreach ($bookmakers as $book) {
            $markets = $book['markets']; // What markets exist?
            // Guesswork and documentation diving...
        }
    }
}
```

### **After: Perfect Type Safety & IntelliSense**
```php
// ✅ Perfect autocomplete, bulletproof types
use SportsApiTypes\TheOddsAPI\{OddsResponse, Game, Bookmaker};

function processOdds(OddsResponse $response): void {
    foreach ($response->games as $game) {
        $homeTeam = $game->home_team; // ✅ String autocomplete
        $bookmakers = $game->bookmakers; // ✅ Bookmaker[] type
        
        foreach ($bookmakers as $bookmaker) {
            $moneyline = $bookmaker->getMoneyline(); // ✅ Method autocomplete
            $spread = $bookmaker->getSpread(); // ✅ Perfect IntelliSense
            $totals = $bookmaker->getTotals(); // ✅ All methods visible
            
            if ($moneyline) {
                $homeOdds = $moneyline->getHomeOutcome($game->home_team);
                $decimal = $homeOdds?->getDecimalOdds(); // ✅ Type-safe calls
                $probability = $homeOdds?->getImpliedProbability();
            }
        }
    }
}
```

---

## 🏆 **Advanced Features**

### **Sport-Specific Extensions**
```php
use SportsApiTypes\TheOddsAPI\{NFLGame, NBAGame, MLBGame};

// NFL-specific functionality
function analyzeNFLGame(NFLGame $game): void {
    $playerProps = $game->getPlayerProps(); // ✅ NFL-specific
    $altSpreads = $game->getAlternateSpreads(); // ✅ Perfect types
}

// NBA-specific functionality  
function analyzeNBAGame(NBAGame $game): void {
    $playerPoints = $game->getPlayerPoints(); // ✅ NBA-specific
    $quarters = $game->getQuarterMarkets(); // ✅ All 4 quarters typed
}

// MLB-specific functionality
function analyzeMLBGame(MLBGame $game): void {
    $runLine = $game->getRunLine(); // ✅ MLB spread equivalent
    $first5 = $game->getFirst5Innings(); // ✅ F5 market access
    $innings = $game->getInningsTotals(); // ✅ All innings typed
}
```

### **Advanced Betting Calculations**
```php
use function SportsApiTypes\TheOddsAPI\{
    find_arbitrage_opportunities,
    calculate_kelly_stake,
    build_same_game_parlay
};

// Find guaranteed profit opportunities
/** @var ArbitrageOpportunity[] $opportunities */
$opportunities = find_arbitrage_opportunities($games, 0.02);

foreach ($opportunities as $arb) {
    $allocation = $arb->calculateStakeAllocation(1000.00);
    $profit = $arb->profitMargin * 1000.00;
    
    echo "Guaranteed profit: $" . number_format($profit, 2);
}

// Calculate optimal Kelly stakes
$kellyStake = calculate_kelly_stake(
    $outcome,           // Outcome object
    0.55,              // True probability (55%)  
    10000.00,          // Bankroll
    0.25               // Max Kelly (25%)
);

// Build same-game parlays with full type safety
$parlayLegs = [$spread, $total, $moneyline];
$parlayData = build_same_game_parlay($game, $parlayLegs);

echo "Combined odds: " . $parlayData['combined_odds'];
echo "Win probability: " . $parlayData['total_probability'];
```

### **Rate Limit Management**
```php
use SportsApiTypes\TheOddsAPI\{APIConfig, RateLimitInfo};

$config = new APIConfig(
    apiKey: $_ENV['ODDS_API_KEY'],
    markets: ['h2h', 'spreads', 'totals', 'player_props'],
    bookmakers: ['draftkings', 'fanduel', 'betmgm'],
    regions: ['us', 'us2']
);

$rateLimit = new RateLimitInfo(
    remaining: 450,
    used: 50, 
    resetTime: new DateTimeImmutable('+1 hour')
);

if ($rateLimit->canMakeRequest()) {
    $odds = fetch_odds('americanfootball_nfl', $config);
    // Process with full type safety...
}
```

---

## 📦 **Installation & Setup**

### **Composer Installation**
```bash
# Install the complete package
composer require eq12/sports-api-types

# Or install specific API types
composer require eq12/sports-api-types-odds-api
composer require eq12/sports-api-types-draftkings  
composer require eq12/sports-api-types-fanduel
```

### **VS Code Configuration**
```json
{
    "intelephense.stubs": [
        "sports-api-types"
    ],
    "intelephense.files.associations": [
        "*.php",
        "vendor/eq12/sports-api-types/**/*.php"
    ]
}
```

### **Include in Your Project**
```php
<?php
// Include all sports API types
require_once 'vendor/eq12/sports-api-types/autoload.php';

use SportsApiTypes\TheOddsAPI\{OddsResponse, Game, Bookmaker};
use SportsApiTypes\DraftKings\{PlayerProps, SGPBuilder};
use SportsApiTypes\FanDuel\{LiveBetting, CashOutOptions};

// Perfect IntelliSense from here on!
```

---

## 💰 **Pricing**

### **Individual API Packs**
- **The Odds API Types**: $49
- **DraftKings API Types**: $79
- **FanDuel API Types**: $79  
- **BetMGM API Types**: $69
- **ESPN Sports Data Types**: $59

### **Complete Sports Bundle** - $199
- ✅ **All 15+ API type libraries**
- ✅ **Advanced betting calculators**
- ✅ **Sport-specific extensions**
- ✅ **6 months of updates**
- ✅ **Private Discord access**

### **Enterprise License** - $999
- ✅ **Unlimited developers**
- ✅ **Custom API type generation** 
- ✅ **Priority support**
- ✅ **On-site training session**
- ✅ **12 months of updates**

---

## 🎯 **Perfect For**

### **Betting Application Developers**
> "These types saved us 2 weeks of documentation diving. The autocompletion is incredible."
> — *Jake Morrison, BettingPro*

### **Data Science Teams**
> "Finally, we can process odds data without constantly checking API docs. Game changer."  
> — *Dr. Sarah Kim, Analytics Firm*

### **Agency Developers**
> "We use these on every sports betting project. Clients love the bulletproof code quality."
> — *Alex Chen, Development Agency*

---

## 🚀 **Get Started**

### **[Download The Odds API Types - $49](https://gumroad.com/l/odds-api-types)**

### **[Complete Sports Bundle - $199](https://gumroad.com/l/sports-api-complete)**

### **[Enterprise Inquiry](mailto:enterprise@eq12.dev)**

---

## 📋 **What's Included**

### **File Structure**
```
sports-api-types/
├── TheOddsAPI/
│   ├── OddsResponse.php      # Main API responses
│   ├── Game.php              # Game objects with methods
│   ├── Bookmaker.php         # Bookmaker data structures
│   ├── Market.php            # Betting market types
│   ├── Outcome.php           # Individual odds/lines
│   ├── SportSpecific/        # NFL, NBA, NHL, MLB extensions
│   └── Helpers.php           # Calculation functions
├── DraftKings/
│   ├── SGPBuilder.php        # Same game parlay types
│   ├── PlayerProps.php       # Player prop markets
│   └── LiveBetting.php       # In-game betting types
├── FanDuel/
│   ├── CashOut.php           # Cash out functionality
│   ├── BoostOdds.php         # Odds boost types
│   └── Parlays.php           # Parlay builder types
└── Examples/
    ├── BasicUsage.php        # Getting started examples
    ├── AdvancedBetting.php   # Complex betting scenarios
    └── ArbitrageBot.php      # Arbitrage detection
```

### **Documentation Included**
- ✅ **Complete API reference** (200+ pages)
- ✅ **Video tutorials** (4 hours) 
- ✅ **Real-world examples** (50+ scenarios)
- ✅ **Migration guides** from generic arrays
- ✅ **Performance optimization tips**

---

## 🛡️ **Guarantee**

**30-day money-back guarantee.** If these types don't dramatically improve your development experience, get a full refund.

---

**Transform your sports betting development today. Your IDE will thank you.**

[**Get Sports API Types Now →**](https://eq12.dev/sports-api-types)