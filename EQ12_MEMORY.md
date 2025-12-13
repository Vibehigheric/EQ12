# 🧠 EQ12 SYSTEM MEMORY
> **DO NOT DELETE**. This file serves as the persistent long-term memory for GitHub Copilot in this workspace.
> **XML UPGRADE**: See `EQ12_MEMORY.xml` for the machine-readable Source of Truth.

## 📅 Current Context (Updated: 2025-12-12)
- **Active Phase**: "Quantum Edge" Optimization & Swarm Deployment
- **Primary Goal**: Deploy the "GodStack" across EQ12 (Manager), M70q (Worker/DB), and Pi (TPU).
- **Critical Constraint**: RAM is the scarcest resource. All engines must use generators/streaming.

## 🏗️ Architecture State: "The GodStack" (LOCKED & VERIFIED)
- **Cluster Master**: Lenovo M70q (Ubuntu) - Swarm Leader.
    - IP (Cluster): `192.168.100.3`
    - Gateway: `192.168.100.1` (Pi)
    - Role: Orchestration, Database, Heavy Scraping, Image Building.
- **Cluster Worker 1**: EQ12 (Windows 11) - Swarm Worker.
    - IP (Cluster): `192.168.100.2`
    - Role: Control Plane CLI, Monitoring. **NO SWARM MANAGEMENT.**
- **Cluster Worker 2**: Raspberry Pi 5 - Swarm Worker / Network Gateway.
    - IP (Home/Mgmt): `192.168.1.80`
    - IP (Cluster Gateway): `192.168.100.1`
    - Role: Gateway, TPU Inference. **NO IMAGE BUILDING.**
- **Orchestration**: Docker Swarm with `eq12_stack.yml`.

## 🔒 HARD RULES (INVARIANTS)
1.  **Swarm Commands**: ALWAYS run on M70q (`192.168.100.3`). NEVER on Windows.
2.  **Image Builds**: ALWAYS build on M70q (Native Linux). NEVER on Windows (Context/EOF issues).
3.  **Deployment**: `docker stack deploy` must originate from M70q.
4.  **Pi Role**: Pure execution & routing. No builds.
- **Networking**: Overlay Network `eq12_net` (Encrypted).
- **Optimization Philosophy**: "Quantum Edge"
    - **Generators**: All heavy compute (Parlay Construction) uses `yield` to minimize RAM.
    - **Limits**: Strict Docker resource limits (512MB for Manager, 2GB for Workers).
    - **Profiling**: `scripts/profile_memory.py` tracks RSS/VMS usage.

## 💰 Monetization Strategy (Active)
- **Primary Model**: Whitelabel B2B ("Sell the Bot").
- **Secondary Model**: SaaS B2C ("Sell the Picks").
- **Inventory**: 32 pre-generated n8n workflows for NFL, NBA, EPL, etc.

## 🌶️ New Venture: Operation Spice Route
- **Goal**: Launch private label seasoning brand (Taco + Burger).
- **Status**: Phase 1 (Sourcing & Recon).
- **Strategy**: Hybrid (High Volume Taco + High Margin Burger).

## ✅ Recent Accomplishments
1.  **Quantum Edge Optimization**: Refactored `ParlayConstructionEngine` to use Python Generators, reducing RAM footprint to ~20MB.
2.  **Memory Profiling**: Created and verified `scripts/profile_memory.py`.
3.  **Swarm Definition**: Created `eq12_stack.yml` with node constraints and resource limits.
4.  **Cluster Join**: M70q successfully joined `192.168.100.x` subnet.
5.  **Internet Bridge**: Established SSH Reverse Tunnel to pipe internet from Windows to M70q.
6.  **Docker Swarm**: Initialized Swarm on M70q.
7.  **Portainer Deployment**: Pulled and deployed Portainer CE via the tunnel.

## 🚧 Active Tasks
- [ ] **Deploy GodStack**: Run `docker stack deploy -c eq12_stack.yml eq12`.
- [ ] **Verify M70q Workload**: Confirm Scraper/DB services land on the M70q.
- [ ] **Verify Pi Workload**: Confirm TPU services land on the Pi.
- [ ] **Full End-to-End Test**: Run a betting simulation using the full cluster stack.
- [ ] **Dashboard**: Finalize the Unified Dashboard to visualize cluster health.

## 🧠 BI Core Philosophy (The "Magnificent Seven" Doctrine)
- **Verdict**: Do not compete with Tech Giants. Exploit their infrastructure.
- **Strategy**: "Platform Parasite". Use Amazon/Google/Microsoft rails to build cash-flow businesses.
- **Directive**: View big tech as *utilities*, not just stocks.

- [ ] **New Venture**: "Operation Spice Route" (Seasoning Business) - Strategy defined in `reports/bi_seasoning_strategy_2026.md`.
- [x] **Strategic Signal**: "Google Electrician Army" (Infrastructure Bottleneck) - Analysis in `reports/bi_ai_labor_market_2025.md`.
- [ ] **Entertainment**: "Steam Deck Killer" Setup - Defined in `reports/eq12_entertainment_expansion.md`.
- [x] **AI Upgrade**: Deployed `eq12-mcp-server` (Node.js/TypeScript) to enable autonomous control.
- [x] **Market Strategy**: Adopted "Platform Parasite" doctrine (Exploit Big Tech infrastructure).
- [x] **Financial Logic**: Defined "W2 vs. Business" tax efficiency strategy (`reports/bi_tax_efficiency.md`).
- [x] **Swarm Architecture**: Defined the "Unlimited Assistant" hierarchy (`reports/eq12_agent_swarm_architecture.md`).
- [x] **GPT Prompts**: Created System Instructions for the Master and Core Agents (`config/gpt_system_prompts.md`).
- [x] **Industry Strategy**: Ranked top sectors for EQ12 (`reports/industry_targeting_matrix.md`).
- [x] **Product Roadmap**: Selected Top 3 Products to build (`reports/eq12_product_roadmap_2026.md`).

## ### 4. AI Super-Cluster (Evolution)
- [ ] **The Post-Mortem Engine** (Self-Learning):
    - Script that compares `gpt_picks.json` vs `actual_results`.
    - Calculates ROI.
    - If ROI < 0, auto-updates `system_prompt` in `gpt_analyzer.py`.
- [x] **Meta-Prompter**: Tool to generate perfect system prompts from vague goals.
- [x] **Code-Genesis**: "SaaS-in-a-Box" generator (Folder structure + Code).

### 5. Creation & Prompting Engines (Active)
- [x] **Meta-Prompter** (`src/meta_prompter.py`): Generates perfect system prompts from vague goals.
- [x] **Code-Genesis** (`src/code_genesis.py`): Generates full software projects (files + code) from descriptions.

## 🧠 Active Tasks (Prioritized)
1. **Deploy Betting Engine V1.5** (Wednesday Hardware).
2. **Build "Post-Mortem" Self-Learning Loop** (Completed).
3. **Execute Whitelabel Sales Strategy** (High Priority - Cash).
4. **Scaffold "LeadMiner" Engine** (Next Product).
5. **Build TubeTycoon**: Python -> TTS -> FFMpeg (Passive Ad Revenue).
6. **Build Master Dashboard**: Web UI to control the cluster (Streamlit/Next.js).

## 📝 Coding Standards & Rules
- **Scripts**: PowerShell for Windows, Bash for Linux.
- **Secrets**: NEVER hardcode. Use Environment Variables.
- **Logs**: Always write structured logs to `logs/`.
- **Memory**: Update this file when completing major milestones.
