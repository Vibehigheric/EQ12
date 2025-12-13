# EQ12 MCP Server

This is the **Model Context Protocol (MCP)** server for the EQ12 Cluster.
It allows AI agents (like Kilo Code, Claude, or Copilot) to directly control the EQ12 infrastructure.

## 🛠️ Tools Provided
1.  `read_system_memory`: Reads `EQ12_MEMORY.md`.
2.  `append_system_memory`: Logs events to the memory file.
3.  `run_eq12_script`: Executes any script in `scripts/` (Python or PowerShell).
4.  `check_cluster_health`: Returns the status of the nodes.

## 🚀 How to Run
1.  **Install Dependencies**:
    ```bash
    cd eq12-mcp-server
    npm install
    ```
2.  **Build**:
    ```bash
    npm run build
    ```
3.  **Configure Client**:
    Add this to your MCP Client configuration (e.g., `claude_desktop_config.json` or Kilo settings):
    ```json
    {
      "mcpServers": {
        "eq12-cluster": {
          "command": "node",
          "args": ["C:\\EQ12_BROKEN_20251122_210342\\eq12-mcp-server\\build\\index.js"]
        }
      }
    }
    ```
