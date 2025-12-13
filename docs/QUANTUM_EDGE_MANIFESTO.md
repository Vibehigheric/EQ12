# 🌌 EQ12 QUANTUM EDGE MANIFESTO

## 🧠 Philosophy
The **Quantum Edge** architecture treats the EQ12 Cluster not as a collection of servers, but as a **Single Probabilistic Compute Fabric**.
*   **Quantum**: We deal in probabilities, superpositions (arbitrage states), and entanglement (correlated parlays).
*   **Edge**: Computation happens at the source (Pi/TPU), minimizing latency.

## ⚡ Core Principles

### 1. RAM is the Event Horizon
Memory is our scarcest resource.
*   **No Monoliths**: Engines must stream data.
*   **Lazy Evaluation**: Do not compute a parlay until it is needed.
*   **Zero-Copy**: Pass references, not values, between local engines.

### 2. The Swarm is a Superposition
*   **EQ12 (Manager)**: The Observer. Collapses wave functions (probabilities) into reality (bets).
*   **Pi (Worker)**: The Quantum Tunneler. Uses TPU to bypass CPU bottlenecks for inference.
*   **M70q (Worker)**: The Gravity Well. Holds the heavy state (Database, Scrapers).

### 3. Availability is Entanglement
If one node goes offline, its state must be instantly reconstructible by the others.
*   **State**: Stored in Redis/Postgres (M70q).
*   **Logic**: Replicated in Docker Images across all nodes.

## 🛠 Implementation Strategy

### A. Memory Optimization
*   **Generators**: All engines must `yield` results, not `return` lists.
*   **Resource Pinning**: Docker services have strict RAM limits to prevent OOM kills.
*   **Garbage Collection**: Aggressive `gc.collect()` after heavy inference cycles.

### B. Compute Optimization
*   **TPU Offloading**: `prop_tensor` is strictly pinned to the Pi.
*   **Vectorization**: Use `numpy` / `pandas` vector ops instead of Python loops.

### C. The "Quantum" Scheduler
The Orchestrator assigns tasks based on **Probability of Success** vs **Resource Cost**.
*   High EV + Low Cost = **Immediate Execution** (Pi)
*   Low EV + High Cost = **Deferred / Batch** (M70q)
