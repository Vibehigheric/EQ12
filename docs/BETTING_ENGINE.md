# 🎲 EQ12 Betting Engine Documentation

The **EdgeGod-Omega** Betting Engine is a modular system composed of 10 specialized intelligences.

## 🧠 The 10 Intelligences

### 1. Line Discrepancy Engine (`src/intelligences/line_discrepancy/`)
*   **Goal**: Detect when a specific sportsbook's line deviates significantly from the market consensus or "fair" line.
*   **Inputs**: Odds API feeds, internal "Fair Line" model.
*   **Outputs**: `DiscrepancySignal` (Book, Event, Market, Deviation).

### 2. Arbitrage + Hedging Engine (`src/intelligences/arbitrage/`)
*   **Goal**: Identify risk-free profit opportunities (Arbs) and low-risk hedges (Middles).
*   **Inputs**: Real-time odds from all books.
*   **Outputs**: `ArbitrageOrder` (Bet A, Bet B, Stake A, Stake B, Profit %).

### 3. Player Prop Tensor Engine (`src/intelligences/prop_tensor/`)
*   **Goal**: Predict player performance probabilities (HR, Hits, Ks, etc.).
*   **Inputs**: Statcast data, weather, historical matchups, recent form.
*   **Outputs**: `PropPrediction` (Player, Market, Probability, EV).

### 4. ML Line-Correction Engine (`src/intelligences/line_correction/`)
*   **Goal**: Generate a "True Line" independent of sportsbooks.
*   **Inputs**: Team stats, injuries, advanced metrics.
*   **Outputs**: `TrueLine` (Spread, Total, Moneyline).

### 5. Live Micro-Signal Engine (`src/intelligences/live_signals/`)
*   **Goal**: Exploit latency in live betting markets.
*   **Inputs**: Real-time play-by-play feeds (sub-second latency).
*   **Outputs**: `LiveSignal` (Event, Market, Direction, Urgency).

### 6. Parlay Construction Engine (`src/intelligences/parlay_builder/`)
*   **Goal**: Construct EV+ parlays by combining uncorrelated positive-edge bets.
*   **Inputs**: Outputs from Intelligences 1, 3, and 4.
*   **Outputs**: `ParlayRecommendation` (Legs, Total Odds, EV, Kelly Stake).

### 7. Capital Allocation / Risk Engine (`src/intelligences/risk_manager/`)
*   **Goal**: Determine the optimal bet size for every order.
*   **Inputs**: Bankroll size, current exposure, bet edge, confidence.
*   **Outputs**: `StakeAuthorization` (Amount, Approved/Rejected).

### 8. Anti-Book Behavior Engine (`src/intelligences/anti_book/`)
*   **Goal**: Detect "traps" and dangerous market movements.
*   **Inputs**: Line movement history, public betting percentages.
*   **Outputs**: `DangerSignal` (Event, Reason).

### 9. Self-Training Loop (`src/intelligences/self_trainer/`)
*   **Goal**: Analyze past performance to improve models.
*   **Inputs**: Bet history, game results.
*   **Outputs**: Model updates / weight adjustments.

### 10. Book-Specific Exploitation Engine (`src/intelligences/book_exploit/`)
*   **Goal**: Route bets to the sportsbook with the best odds or known weaknesses.
*   **Inputs**: Bookmaker profiles, current odds.
*   **Outputs**: `RoutingInstruction` (Target Book).

---

## 🔄 Data Flow

1.  **Ingestion**: Scrapers running on M70q fetch data and push to Redis/DB.
2.  **Analysis**: Intelligences 1-5 process data and publish signals.
3.  **Synthesis**: Intelligences 6, 8, and 10 filter and combine signals.
4.  **Risk Check**: Intelligence 7 approves stakes.
5.  **Execution**: Orchestrator logs the bet and notifies the user.
