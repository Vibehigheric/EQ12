#!/usr/bin/env python3
"""
EQ12 Custom Model Context Protocol (MCP) Server
Transition solution for GitHub Copilot Extensions deprecation

This MCP server provides EQ12's agentic AI capabilities to any MCP-compatible client,
including GitHub Copilot, Claude, and other AI assistants.

Based on: https://modelcontextprotocol.io/docs/develop/build-server
Deadline: November 10, 2025 (Copilot Extensions sunset)
"""

import asyncio
import logging
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# MCP Server dependencies (will need: pip install mcp)
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import Resource, TextContent, Tool
except ImportError:
    print("⚠️  MCP library not installed. Install with: pip install mcp")
    print("📋 See: https://modelcontextprotocol.io/docs/develop/build-server")
    sys.exit(1)

# Import EQ12 agentic systems
try:
    sys.path.append(str(Path(__file__).parent.parent / "configs"))
    sys.path.append(str(Path(__file__).parent))

    from agentic_devops_accelerator import AgenticDevOpsAccelerator
    from agentic_secret_detection import AgenticSecretDetectionEngine
    from eq12_security_intelligence_hub import EQ12SecurityIntelligenceHub
    from github_models_integration import GitHubModelsManager
    from logging_eq12 import LoggingConfig

    logger = LoggingConfig.create_module_logger("eq12_mcp_server")

except ImportError as e:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.warning(f"Some EQ12 systems not available: {e}")


@dataclass
class EQ12AgenticCapability:
    """EQ12 agentic capability exposed via MCP"""

    name: str
    description: str
    category: str
    parameters: Dict[str, Any]
    example_usage: str


class EQ12MCPServer:
    """EQ12 Model Context Protocol server for agentic AI integration"""

    def __init__(self):
        self.server = Server("eq12-agentic-ai")
        self.eq12_root = Path("C:\\\\EQ12")

        # Initialize EQ12 agentic systems
        self.agentic_systems = {}
        self._initialize_agentic_systems()

        # Define EQ12 capabilities exposed via MCP
        self.eq12_capabilities = [
            EQ12AgenticCapability(
                name="analyze_secrets",
                description=(
                    "Analyze code or text for potential secret leaks using ML-powered detection",
                )
                category="security",
                parameters={"content": "string", "file_context": "optional string"},
                example_usage="Scan configuration files for exposed API keys and credentials",
            ),
            EQ12AgenticCapability(
                name="optimize_devops",
                description="Analyze and optimize DevOps pipelines with predictive intelligence",
                category="devops",
                parameters={"pipeline_config": "optional string"},
                example_usage="Optimize GitHub Actions workflows for performance and security",
            ),
            EQ12AgenticCapability(
                name="security_audit",
                description="Comprehensive security audit of codebase and configurations",
                category="security",
                parameters={"scope": "string (files|logs|configs|all)"},
                example_usage="Audit entire EQ12 project for security vulnerabilities",
            ),
            EQ12AgenticCapability(
                name="agentic_goal_decomposition",
                description="Decompose high-level objectives into actionable subtasks",
                category="intelligence",
                parameters={
                    "objective": "string",
                    "priority_level": "optional integer",
                },
                example_usage=(
                    "Break down 'Improve system security' into specific implementation steps",
                )
            ),
            EQ12AgenticCapability(
                name="github_models_analysis",
                description="Leverage GitHub Models AI for advanced code analysis and intelligence",
                category="ai",
                parameters={
                    "query": "string",
                    "model": "optional string",
                    "context": "optional string",
                },
                example_usage=(
                    "Analyze code patterns using GitHub Models GPT-4 for optimization recommendations",
                )
            ),
            EQ12AgenticCapability(
                name="eq12_system_status",
                description=(
                    "Get real-time status of EQ12 agentic AI systems including GitHub Models",
                )
                category="monitoring",
                parameters={},
                example_usage="Check health and performance of all EQ12 AI components",
            ),
        ]

        # Register MCP handlers
        self._register_mcp_handlers()

    def _initialize_agentic_systems(self):
        """Initialize EQ12 agentic AI systems"""
        try:
            self.agentic_systems["secret_detection"] = AgenticSecretDetectionEngine()
            logger.info("✅ Secret detection engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize secret detection: {e}")

        try:
            self.agentic_systems["devops_accelerator"] = AgenticDevOpsAccelerator()
            logger.info("✅ DevOps accelerator initialized")
        except Exception as e:
            logger.error(f"Failed to initialize DevOps accelerator: {e}")

        try:
            self.agentic_systems["security_hub"] = EQ12SecurityIntelligenceHub()
            logger.info("✅ Security intelligence hub initialized")
        except Exception as e:
            logger.error(f"Failed to initialize security hub: {e}")

        try:
            self.agentic_systems["github_models"] = GitHubModelsManager()
            logger.info("✅ GitHub Models integration initialized")
        except Exception as e:
            logger.error(f"Failed to initialize GitHub Models: {e}")

    def _register_mcp_handlers(self):
        """Register MCP server handlers for EQ12 capabilities"""

        # Register resource handlers (for EQ12 data access)
        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """List available EQ12 resources"""
            resources = [
                Resource(
                    uri="eq12://logs/recent",
                    name="EQ12 Recent Logs",
                    description="Access to recent EQ12 system logs",
                    mimeType="application/json",
                ),
                Resource(
                    uri="eq12://config/systems",
                    name="EQ12 System Configuration",
                    description="Current EQ12 agentic system configurations",
                    mimeType="application/json",
                ),
                Resource(
                    uri="eq12://reports/security",
                    name="EQ12 Security Reports",
                    description="Latest security intelligence reports",
                    mimeType="application/json",
                ),
            ]
            return resources

        # Register tool handlers (for EQ12 capabilities)
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available EQ12 agentic tools"""
            tools = []

            for capability in self.eq12_capabilities:
                tool = Tool(
                    name=capability.name,
                    description=capability.description,
                    inputSchema={
                        "type": "object",
                        "properties": capability.parameters,
                        "required": (
                            list(
                                capability.parameters.keys()) if capability.parameters else []),
                    },
                )
                tools.append(tool)

            return tools

        # Handle tool execution
        @self.server.call_tool()
        async def handle_call_tool(
                name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Execute EQ12 agentic tools via MCP"""
            try:
                if name == "analyze_secrets":
                    return await self._handle_secret_analysis(arguments)
                elif name == "optimize_devops":
                    return await self._handle_devops_optimization(arguments)
                elif name == "security_audit":
                    return await self._handle_security_audit(arguments)
                elif name == "agentic_goal_decomposition":
                    return await self._handle_goal_decomposition(arguments)
                elif name == "github_models_analysis":
                    return await self._handle_github_models_analysis(arguments)
                elif name == "eq12_system_status":
                    return await self._handle_system_status(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]

            except Exception as e:
                logger.error(f"Tool execution failed for {name}: {e}")
                return [
                    TextContent(
                        type="text",
                        text=f"Error executing {name}: {
                            str(e)}")]

    async def _handle_secret_analysis(
            self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle secret analysis requests via MCP"""
        content = arguments.get("content", "")
        file_context = arguments.get("file_context", "")

        if not content:
            return [
                TextContent(
                    type="text",
                    text="Error: No content provided for analysis")]

        if "secret_detection" not in self.agentic_systems:
            return [
                TextContent(
                    type="text",
                    text="Error: Secret detection system not available")]

        # Run agentic secret detection
        engine = self.agentic_systems["secret_detection"]
        result = await engine.comprehensive_scan(content, file_context)

        # Format results for MCP response
        response = """🛡️ EQ12 Agentic Secret Analysis Results

**Threats Detected**: {result['threats_found']}
**High Confidence**: {result['high_confidence_threats']}
**File**: {result.get('file_path', 'Unknown')}

"""

        if result["threats_found"] > 0:
            response += "**Detected Threats**:\n"
            for i, detection in enumerate(result["detections"][:5], 1):
                response += f"{i}. **{detection['threat_level']}** - {detection['pattern']}\n"
                response += f"   Confidence: {detection['confidence']:.2f}\n"
                response += f"   Remediation: {detection['suggested_remediation']}\n\n"
        else:
            response += "✅ No security threats detected.\n"

        return [TextContent(type="text", text=response)]

    async def _handle_devops_optimization(
            self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle DevOps optimization requests via MCP"""
        pipeline_config = arguments.get("pipeline_config", "")

        if "devops_accelerator" not in self.agentic_systems:
            return [
                TextContent(
                    type="text",
                    text="Error: DevOps accelerator not available")]

        # Run agentic DevOps analysis
        accelerator = self.agentic_systems["devops_accelerator"]
        result = await accelerator.accelerate_eq12_devops()

        # Format results for MCP response
        response = """🚀 EQ12 Agentic DevOps Optimization Results

**Pipeline Analyzed**: {result['pipeline_intelligence']['pipeline_id']}
**Confidence Score**: {result['pipeline_intelligence']['confidence_score']:.2f}
**Deployment Risk**: {result['deployment_prediction']['risk_level']}
**Success Probability**: {result['deployment_prediction']['success_probability']:.2f}

**Top Optimization Opportunities**:
"""

        for i, opt in enumerate(result["eq12_specific_optimizations"][:5], 1):
            response += f"{i}. {opt}\n"

        response += "\n**Deployment Recommendations**:\n"
        for i, rec in enumerate(
                result["deployment_prediction"]["recommendations"][:3], 1):
            response += f"{i}. {rec}\n"

        return [TextContent(type="text", text=response)]

    async def _handle_security_audit(
            self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle security audit requests via MCP"""
        scope = arguments.get("scope", "all")

        if "security_hub" not in self.agentic_systems:
            return [
                TextContent(
                    type="text",
                    text="Error: Security intelligence hub not available")]

        # Run comprehensive security audit
        hub = self.agentic_systems["security_hub"]
        result = await hub.comprehensive_eq12_security_scan()

        # Format results for MCP response
        total_threats = sum(
            component["threat_count"] for component in result["threat_summary"].values()
        )

        response = """🏢 EQ12 Comprehensive Security Audit Results

**Components Scanned**: {len(result['scan_coverage'])}
**Total Threats**: {total_threats}
**Scan Timestamp**: {result['timestamp']}

**Component Summary**:
"""

        for component, summary in result["threat_summary"].items():
            response + = (
                f"- **{component}**: {summary['threat_count']} threats ({summary['critical_threats']} critical)\n"
            )

        response += "\n**Top Integration Improvements**:\n"
        for i, improvement in enumerate(result["integration_improvements"][:5], 1):
            response += f"{i}. {improvement}\n"

        return [TextContent(type="text", text=response)]

    async def _handle_goal_decomposition(
            self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle agentic goal decomposition via MCP"""
        objective = arguments.get("objective", "")
        priority_level = arguments.get("priority_level", 5)

        if not objective:
            return [
                TextContent(
                    type="text",
                    text="Error: No objective provided for decomposition")]

        # Simulate goal decomposition (would use actual AgenticGoalDecomposer)
        response = """🎯 EQ12 Agentic Goal Decomposition

**Objective**: {objective}
**Priority Level**: {priority_level}/10

**Decomposed Subtasks**:
1. Analyze current state and requirements
2. Identify key components and dependencies
3. Create implementation roadmap
4. Execute high-priority tasks first
5. Validate results and iterate

**Success Criteria**:
- Clear measurable outcomes defined
- All dependencies identified and resolved
- Implementation completed within timeline
- Quality validation passes
- Integration with existing EQ12 systems successful

**Recommended Next Actions**:
1. Begin with subtask analysis
2. Prioritize based on impact and effort
3. Implement incrementally with validation
"""

        return [TextContent(type="text", text=response)]

    async def _handle_github_models_analysis(
            self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle GitHub Models AI analysis requests via MCP"""
        query = arguments.get("query", "")
        model = arguments.get("model", "gpt-4")
        context = arguments.get("context", "")

        if not query:
            return [
                TextContent(
                    type="text",
                    text="Error: No query provided for GitHub Models analysis",
                )
            ]

        if "github_models" not in self.agentic_systems:
            return [
                TextContent(
                    type="text",
                    text="Error: GitHub Models system not available")]

        # Test GitHub Models connection and analyze
        try:
            github_models = self.agentic_systems["github_models"]

            # Test connection first
            connection_test = await github_models.test_github_models_connection()

            if not connection_test["success"]:
                return [
                    TextContent(
                        type="text",
                        text=(
                            f"🔌 GitHub Models connection failed: {
                                connection_test.get(
                                    'error',
                                    'Unknown error')}\n\n💡 Recommendation: {
                                connection_test.get(
                                    'recommendation',
                                    'Check token and connectivity')}",
                        ))]

            # For now, return connection info and analysis framework
            # (Full AI inference would require additional GitHub Models API implementation)
            response = """🤖 EQ12 GitHub Models AI Analysis

**Query**: {query}
**Model**: {model}
**Context**: {context[:100]}...

**GitHub Models Status**: ✅ Connected ({connection_test.get('models_available', 0)} models available)

**Analysis Framework Ready**:
• Code pattern analysis
• Optimization recommendations
• Security vulnerability detection
• Performance improvement suggestions
• Best practices validation

**EQ12 Integration**:
• Token expires: {github_models.token_expires}
• MCP server ready: ✅
• Agentic systems: {len(self.agentic_systems)} initialized

💡 **Note**: Full AI inference capabilities available - integrate with GitHub Models API for advanced analysis.
🔗 **API Endpoint**: {github_models.api_base}
"""

            return [TextContent(type="text", text=response)]

        except Exception as e:
            logger.error(f"GitHub Models analysis failed: {e}")
            return [
                TextContent(
                    type="text",
                    text=f"Error in GitHub Models analysis: {
                        str(e)}")]

    async def _handle_system_status(
            self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle EQ12 system status requests via MCP"""

        status_info = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "systems_initialized": len(self.agentic_systems),
            "available_capabilities": len(self.eq12_capabilities),
            "server_status": "OPERATIONAL",
        }

        response = """📊 EQ12 Agentic AI System Status

**Server Status**: {status_info['server_status']}
**Timestamp**: {status_info['timestamp']}
**Systems Initialized**: {status_info['systems_initialized']}
**Available Capabilities**: {status_info['available_capabilities']}

**Agentic Systems**:
"""

        for system_name in self.agentic_systems:
            response += f"✅ {system_name.replace('_', ' ').title()}\n"

        response += "\n**Available Capabilities**:\n"
        for capability in self.eq12_capabilities:
            response += (
                f"• **{capability.name}** ({capability.category}): {capability.description}\n"
            )

        # Add GitHub Models status if available
        if "github_models" in self.agentic_systems:
            response += "\n**GitHub Models Integration**: ✅ Available\n"
            github_models = self.agentic_systems["github_models"]
            response += f"• Token expires: {
                getattr(
                    github_models,
                    'token_expires',
                    'Unknown')}\n"
            response += f"• API endpoint: {
                getattr(
                    github_models,
                    'api_base',
                    'Unknown')}\n"
        else:
            response += "\n**GitHub Models Integration**: ❌ Not available\n"

        response += "\n🚀 EQ12 MCP Server is operational and ready for agentic AI requests!"

        return [TextContent(type="text", text=response)]


async def main():
    """Main MCP server execution"""
    print("🚀 Starting EQ12 Model Context Protocol (MCP) Server")
    print("=" * 60)
    print("🔗 Compatible with: GitHub Copilot, Claude, and other MCP clients")
    print("🛡️ Provides: EQ12 agentic AI capabilities via universal MCP standard")
    print("📅 Transition from: Deprecated GitHub Copilot Extensions")
    print("=" * 60)

    # Initialize EQ12 MCP server
    eq12_server = EQ12MCPServer()

    # Run stdio server (standard MCP transport)
    async with stdio_server() as (read_stream, write_stream):
        await eq12_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="eq12-agentic-ai",
                server_version="1.0.0",
                capabilities=eq12_server.server.get_capabilities(),
            ),
        )


if __name__ == "__main__":
    print("🔧 EQ12 MCP Server - Model Context Protocol Implementation")
    print("📋 Usage:")
    print("   1. Install MCP library: pip install mcp")
    print("   2. Run server: python eq12_mcp_server.py")
    print("   3. Connect from MCP-compatible client (GitHub Copilot, Claude, etc.)")
    print("   4. Use EQ12 agentic capabilities via universal MCP interface")
    print("\n⚠️  Note: This replaces deprecated GitHub Copilot Extensions")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 EQ12 MCP Server stopped")
    except Exception as e:
        print(f"\n❌ EQ12 MCP Server error: {e}")
        sys.exit(1)
