#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import { exec } from "child_process";
import { promisify } from "util";
import * as fs from "fs/promises";
import * as path from "path";

const execAsync = promisify(exec);

// Define the EQ12 Workspace Root
const WORKSPACE_ROOT = path.resolve(__dirname, "../../");
const MEMORY_FILE = path.join(WORKSPACE_ROOT, "EQ12_MEMORY.md");

class Eq12Server {
  private server: Server;

  constructor() {
    this.server = new Server(
      {
        name: "eq12-mcp-server",
        version: "1.0.0",
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
    
    // Error handling
    this.server.onerror = (error) => console.error("[MCP Error]", error);
    process.on("SIGINT", async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  private setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: "read_system_memory",
          description: "Reads the persistent EQ12_MEMORY.md file to understand current context and architecture.",
          inputSchema: {
            type: "object",
            properties: {},
          },
        },
        {
          name: "append_system_memory",
          description: "Appends a new entry or log to the EQ12_MEMORY.md file.",
          inputSchema: {
            type: "object",
            properties: {
              content: {
                type: "string",
                description: "The markdown content to append.",
              },
            },
            required: ["content"],
          },
        },
        {
          name: "run_eq12_script",
          description: "Executes a Python or PowerShell script from the scripts/ directory.",
          inputSchema: {
            type: "object",
            properties: {
              scriptName: {
                type: "string",
                description: "The name of the script (e.g., 'shop_nike_xl.py' or 'EQ12_CLUSTER_OPS.ps1').",
              },
              args: {
                type: "string",
                description: "Optional arguments to pass to the script.",
              },
            },
            required: ["scriptName"],
          },
        },
        {
          name: "check_cluster_health",
          description: "Checks the status of the EQ12 Cluster nodes (Windows, Pi, TPU).",
          inputSchema: {
            type: "object",
            properties: {},
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      switch (request.params.name) {
        case "read_system_memory":
          return await this.handleReadMemory();
        case "append_system_memory":
          return await this.handleAppendMemory(request.params.arguments);
        case "run_eq12_script":
          return await this.handleRunScript(request.params.arguments);
        case "check_cluster_health":
          return await this.handleCheckHealth();
        default:
          throw new McpError(
            ErrorCode.MethodNotFound,
            `Unknown tool: ${request.params.name}`
          );
      }
    });
  }

  private async handleReadMemory() {
    try {
      const content = await fs.readFile(MEMORY_FILE, "utf-8");
      return {
        content: [
          {
            type: "text",
            text: content,
          },
        ],
      };
    } catch (error: any) {
      return {
        content: [
          {
            type: "text",
            text: `Error reading memory: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }

  private async handleAppendMemory(args: any) {
    const { content } = z.object({ content: z.string() }).parse(args);
    try {
      const timestamp = new Date().toISOString();
      const entry = `\n\n## 📝 Log Entry (${timestamp})\n${content}`;
      await fs.appendFile(MEMORY_FILE, entry, "utf-8");
      return {
        content: [
          {
            type: "text",
            text: "Successfully appended to EQ12_MEMORY.md",
          },
        ],
      };
    } catch (error: any) {
      return {
        content: [
          {
            type: "text",
            text: `Error appending memory: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }

  private async handleRunScript(args: any) {
    const { scriptName, args: scriptArgs } = z.object({ 
      scriptName: z.string(),
      args: z.string().optional() 
    }).parse(args);

    const scriptPath = path.join(WORKSPACE_ROOT, "scripts", scriptName);
    
    // Determine interpreter
    let command = "";
    if (scriptName.endsWith(".py")) {
      command = `python "${scriptPath}" ${scriptArgs || ""}`;
    } else if (scriptName.endsWith(".ps1")) {
      command = `powershell -ExecutionPolicy Bypass -File "${scriptPath}" ${scriptArgs || ""}`;
    } else {
      throw new McpError(ErrorCode.InvalidParams, "Unsupported script type. Use .py or .ps1");
    }

    try {
      const { stdout, stderr } = await execAsync(command);
      return {
        content: [
          {
            type: "text",
            text: `STDOUT:\n${stdout}\n\nSTDERR:\n${stderr}`,
          },
        ],
      };
    } catch (error: any) {
      return {
        content: [
          {
            type: "text",
            text: `Execution failed: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }

  private async handleCheckHealth() {
    // In a real scenario, this would ping IPs or check API endpoints.
    // For now, we return the known architectural state.
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({
            status: "active",
            nodes: [
              { name: "EQ12-Main", role: "Master", os: "Windows 11", status: "Online" },
              { name: "EQ12-Edge", role: "Edge", os: "Raspberry Pi OS", ip: "192.168.1.80", status: "Unknown (Ping required)" },
              { name: "EQ12-Worker", role: "Worker", os: "Windows 10", model: "Lenovo 10T8", status: "Pending Join" }
            ],
            services: ["Sourcing Agent", "Cluster Ops", "Memory"]
          }, null, 2),
        },
      ],
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("EQ12 MCP Server running on stdio");
  }
}

const server = new Eq12Server();
server.run().catch(console.error);
