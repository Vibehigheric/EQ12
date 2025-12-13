# 🏗️ EDGEGOD-OMEGA: System Architecture

## **1. High-Level Overview**

EDGEGOD-OMEGA is a distributed, multi-intelligence betting system designed to run on a hybrid cluster (Windows Master + Linux Workers). It moves beyond simple scraping to **parallel intelligence orchestration**.

### **Cluster Roles**
*   **EQ12 (Windows 11)**: **The Brain**. Runs the Orchestrator, Decision Engine, Database, and VB.NET Control Tower.
*   **M70q (Ubuntu/WSL)**: **The Eyes**. Runs high-volume scraping, real-time ingestion, and heavy ML inference tasks (Docker Swarm).

---

## **2. Core Components**

### **A. The Data Bus (The Nervous System)**
*   **Redis**: Real-time signal bus. Used for "Live Micro-Signals" and inter-agent messaging.
    *   Channel: `edgegod.signals.live`
    *   Channel: `edgegod.orders.new`
*   **PostgreSQL**: Long-term memory. Stores historical odds, player props, and bet history.
*   **JSON Exchange**: `dashboard_data.json` (Legacy/Simple) -> Moving to API-based consumption.

### **B. The Orchestrator (The Conductor)**
*   **Location**: `src/orchestrator/`
*   **Role**:
    *   Loads the **Master System Prompt**.
    *   Spins up/down Intelligence Modules.
    *   Aggregates outputs from all 10 intelligences.
    *   Executes the "Final Action Plan".

### **C. The 10 Intelligence Modules (The Agents)**
Each module is an independent unit (Python Class or Docker Container) located in `src/intelligences/`.

1.  **`line_discrepancy`**: Compares feeds vs. consensus.
2.  **`arbitrage_engine`**: Finds risk-free profit (scans books).
3.  **`prop_tensor`**: ML models for player props.
4.  **`line_correction`**: Predictive models for spreads/totals.
5.  **`live_signals`**: Real-time game flow analysis.
6.  **`parlay_builder`**: Construct EV+ parlays.
7.  **`risk_manager`**: Kelly criterion & bankroll logic.
8.  **`anti_book`**: Detects traps/steam.
9.  **`self_trainer`**: Feedback loop for models.
10. **`book_exploit`**: Routing logic for specific books.

### **D. The Control Tower (The Interface)**
*   **Location**: `src/EQ12.CommandCenter/` (VB.NET)
*   **Role**:
    *   Human-in-the-loop visualization.
    *   System health monitoring.
    *   Network profile management.
    *   "Emergency Stop" button.

---

## **3. Directory Structure**

```text
C:\EQ12_BROKEN_20251122_210342\
├── config/
│   ├── prompts/            # System prompts (Master Prompt)
│   ├── settings/           # API keys, bookmaker config
│   └── models/             # Trained ML models (.pkl, .pt)
├── src/
│   ├── intelligences/      # The 10 Brains
│   │   ├── __init__.py
│   │   ├── base_intelligence.py  # Abstract Base Class
│   │   ├── line_discrepancy/
│   │   ├── arbitrage/
│   │   └── ...
│   ├── orchestrator/       # The Manager
│   │   ├── main.py
│   │   └── aggregator.py
│   ├── shared/             # Common libs
│   │   ├── database.py
│   │   ├── messaging.py    # Redis wrapper
│   │   └── types.py
│   └── EQ12.CommandCenter/ # VB.NET App
├── scripts/                # Deployment & Utility scripts
└── docker/                 # Dockerfiles for M70q workers
```

---

## **4. Data Flow**

1.  **Ingestion**: M70q scrapes odds/stats -> Pushes to **Redis/DB**.
2.  **Analysis**: Intelligences 1-5 wake up, read data, run models, publish **Signals**.
3.  **Refinement**: Intelligences 6-8 (Parlay, Risk, Anti-Book) consume Signals, filter them, and produce **Orders**.
4.  **Execution**: Orchestrator validates Orders -> Logs to DB -> Updates Dashboard.
5.  **Feedback**: Intelligence 9 (Self-Train) analyzes results nightly.

---

## **5. Technology Stack**

*   **Language**: Python 3.12 (Logic), VB.NET 9.0 (UI/Orchestration).
*   **Containerization**: Docker (Linux Workers).
*   **Database**: PostgreSQL (TimescaleDB extension recommended for time-series).
*   **Messaging**: Redis (Pub/Sub).
*   **ML Framework**: PyTorch / Scikit-Learn.
