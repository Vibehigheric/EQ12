# 📅 EQ12 Daily Automation Routine

This routine utilizes the "100 Prompts" to ensure maximum productivity and system health.

## 🌅 Morning (08:00 - 09:00) - Strategy & Health
1.  **System Health Check** (Prompt #80, #39):
    - Run `scripts/EQ12_SYSTEM_SCAN.ps1`.
    - Check logs for errors.
    - *Prompt*: "Audit this system for security flaws and propose fixes." (if errors found).
2.  **Daily Planning** (Prompt #6, #92):
    - Review `EQ12_MEMORY.md`.
    - *Prompt*: "Generate a dynamic operations plan that updates itself after every message."
    - *Prompt*: "Turn my goals into weekly execution plans."

## ☀️ Mid-Day (12:00 - 13:00) - Business & Execution
3.  **Revenue Ops** (Prompt #11, #25):
    - Check sales/leads (if applicable).
    - *Prompt*: "Analyze my monetization options and output a ranked list with revenue estimates."
    - *Prompt*: "Build a fully automated lead-generation machine using free tools."
4.  **Coding & Build** (Prompt #41, #56):
    - Work on active sprints (e.g., Top 3 Products).
    - *Prompt*: "Write production-ready Python code with comments and error handling."
    - *Prompt*: "Write the automated testing suite for this project."

## 🌙 Evening (18:00 - 19:00) - Review & Optimization
5.  **Data Pipeline** (Prompt #82, #68):
    - Process collected data.
    - *Prompt*: "Turn this into a dashboard with key metrics."
6.  **Retrospective** (Prompt #61, #100):
    - *Prompt*: "Perform full SWOT analysis on this business." (Weekly).
    - *Prompt*: "Show me how to eliminate low-value tasks permanently."
    - Update `EQ12_MEMORY.md`.

## 🔄 Always-On Background Agents
- **Watchdog**: Monitors container health (Prompt #80).
- **Scraper**: Gathers market data (Prompt #47).
- **Inference**: Pi + Coral running local models (Prompt #90).
