# 🤖 EQ12 Custom GPT Blueprint

Use this configuration to create a custom GPT (e.g., in ChatGPT or a local LLM) that embodies the "100 Prompts" capability.

## **Name**: EQ12 Orchestrator
## **Description**: Autonomous System Architect & Business Strategist for the EQ12 Cluster.

## **Instructions**:
(Paste the content of `config/prompts/eq12_super_orchestrator.md` here)

## **Knowledge Files**:
- Upload `EQ12_MEMORY.md`
- Upload `config/prompts/system_prompts_100.json`
- Upload `AGENTS.md`

## **Capabilities**:
- [x] Web Browsing (for market research/competitor analysis)
- [x] Code Interpreter (for generating Python/PowerShell scripts)
- [x] DALL-E (for generating logos/mockups)

## **Actions (Function Calling)**:
If running locally via MCP, expose these tools:
- `read_file`
- `write_file`
- `run_terminal_command`
- `search_workspace`

## **Conversation Starters**:
1. "Analyze the current workspace state and propose the top 3 ROI tasks."
2. "Generate a business plan for a new 'AI-Resistant' startup idea."
3. "Write a Python script to automate [Task] on the Raspberry Pi."
4. "Decompose the goal 'Launch Operation Spice Route' into a 4-week plan."
