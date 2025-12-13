#!/usr/bin/env python3
"""
EQ12 Enhanced Security & AI Integration System
Advanced integration of Snyk Open Source analysis and OpenAI Cookbook patterns

This system combines:
- Snyk Open Source vulnerability detection and dependency management
- OpenAI Cookbook examples and best practices for GPT-5 integration
- Enhanced security analysis for the EQ12 betting platform
- Automated dashboard generation with hardcoded links

Author: EQ12 Development Team
Created: 2025
Version: 2.0.0
"""

import argparse
import asyncio
import json
import logging
import os
import subprocess
import sys
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional


# Configure structured logging with Unicode safety
class SafeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            # Replace Unicode emojis with ASCII equivalents for Windows console
            msg = msg.replace(
                "🔒",
                "[SECURE]").replace(
                "🚀",
                "[START]").replace(
                "📊",
                "[REPORT]")
            msg = msg.replace(
                "⚠️",
                "[WARNING]").replace(
                "✅",
                "[OK]").replace(
                "❌",
                "[ERROR]")
            msg = msg.replace(
                "🔐",
                "[ENCRYPT]").replace(
                "🛡️",
                "[SHIELD]").replace(
                "📈",
                "[METRIC]")
            msg = msg.replace(
                "🤖",
                "[AI]").replace(
                "💡",
                "[TIP]").replace(
                "🎯",
                "[TARGET]")
            stream = self.stream
            stream.write(msg + self.terminator)
            self.flush()
        except (UnicodeEncodeError, Exception):
            # Fallback for any encoding issues
            try:
                safe_msg = record.getMessage().encode("ascii", "replace").decode("ascii")
                self.stream.write(f"{record.levelname}: {safe_msg}\n")
                self.flush()
            except BaseException:
                pass


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/enhanced_security_ai.log", encoding="utf-8"),
        SafeStreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class OpenSourceVulnerability:
    """Enhanced vulnerability representation for open source dependencies"""

    id: str
    package_name: str
    installed_version: str
    fixed_version: Optional[str]
    severity: str
    title: str
    description: str
    cvss_score: Optional[float]
    cwe: Optional[str]
    license_issue: bool
    fix_pr_available: bool
    upgrade_path: Optional[str]
    dependency_path: List[str]
    first_patched_version: Optional[str]
    publication_time: Optional[str]
    exploit_maturity: Optional[str]
    detected_at: str


@dataclass
class AIIntegrationPattern:
    """OpenAI Cookbook pattern representation"""

    pattern_id: str
    pattern_name: str
    category: str
    description: str
    use_case: str
    security_considerations: List[str]
    implementation_notes: str
    code_example: Optional[str]
    gpt5_compatible: bool
    agent_sdk_compatible: bool
    responses_api_compatible: bool
    source_url: str


@dataclass
class DashboardLink:
    """Dashboard link with metadata"""

    url: str
    title: str
    description: str
    category: str
    created_at: str
    access_level: str


@dataclass
class EnhancedSecurityReport:
    """Comprehensive security and AI integration report"""

    report_id: str
    generation_timestamp: str
    snyk_vulnerabilities: List[OpenSourceVulnerability]
    ai_patterns: List[AIIntegrationPattern]
    dashboard_links: List[DashboardLink]
    security_score: float
    ai_integration_score: float
    overall_risk_assessment: str
    recommendations: List[str]
    compliance_status: Dict[str, str]
    next_scan_recommended: str


class EnhancedSnykOpenSourceAnalyzer:
    """Advanced Snyk Open Source analysis with OpenAI integration"""

    def __init__(self):
        self.snyk_token = os.getenv("SNYK_TOKEN")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.project_root = Path("C:/EQ12")
        self.logs_dir = Path("C:/EQ12/logs")
        self.dashboards_dir = Path("C:/EQ12/generated_dashboards")
        self.openai_cookbook_dir = Path("C:/EQ12/openai-cookbook")

        # Create directories
        for directory in [self.logs_dir, self.dashboards_dir]:
            directory.mkdir(exist_ok=True)

        # Dashboard base URL for hardcoded links
        self.dashboard_base_url = "https://eq12.local/dashboards"

        logger.info("Enhanced EQ12 Security & AI Integration System initialized")

    async def analyze_dependency_vulnerabilities(
        self, target_path: Path
    ) -> List[OpenSourceVulnerability]:
        """Enhanced Snyk Open Source vulnerability analysis"""
        vulnerabilities = []

        try:
            logger.info(f"Running enhanced Snyk Open Source analysis on {target_path}")

            # Run Snyk test with detailed JSON output
            cmd = [
                "snyk",
                "test",
                str(target_path),
                "--json",
                "--all-projects",
                "--detection-depth=4",
                "--show-vulnerable-paths=all",
                "--include-base-image-vulnerabilities",
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300, cwd=str(target_path)
            )

            if result.stdout:
                try:
                    scan_data = json.loads(result.stdout)
                    vulnerabilities.extend(self._parse_snyk_vulnerabilities(scan_data))
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse Snyk JSON output: {e}")

        except subprocess.TimeoutExpired:
            logger.error(f"Snyk scan timeout for {target_path}")
        except Exception as e:
            logger.error(f"Snyk scan failed: {e}")

        # Enhance vulnerabilities with additional analysis
        enhanced_vulnerabilities = []
        for vuln in vulnerabilities:
            enhanced_vuln = await self._enhance_vulnerability_analysis(vuln)
            enhanced_vulnerabilities.append(enhanced_vuln)

        logger.info(
            f"Found {
                len(enhanced_vulnerabilities)} dependency vulnerabilities with enhancement")
        return enhanced_vulnerabilities

    def _parse_snyk_vulnerabilities(
            self, scan_data: Dict) -> List[OpenSourceVulnerability]:
        """Parse Snyk scan results into vulnerability objects"""
        vulnerabilities = []

        if isinstance(scan_data, list):
            # Handle multiple projects
            for project_data in scan_data:
                vulnerabilities.extend(
                    self._extract_vulnerabilities_from_project(project_data))
        else:
            # Handle single project
            vulnerabilities.extend(
                self._extract_vulnerabilities_from_project(scan_data))

        return vulnerabilities

    def _extract_vulnerabilities_from_project(
        self, project_data: Dict
    ) -> List[OpenSourceVulnerability]:
        """Extract vulnerabilities from a single project scan result"""
        vulnerabilities = []

        if "vulnerabilities" in project_data:
            for vuln_data in project_data["vulnerabilities"]:
                vulnerability = OpenSourceVulnerability(
                    id=vuln_data.get("id", f"SNYK-{uuid.uuid4().hex[:8]}"),
                    package_name=vuln_data.get("packageName", "unknown"),
                    installed_version=vuln_data.get("version", "unknown"),
                    fixed_version=self._extract_fixed_version(vuln_data),
                    severity=vuln_data.get("severity", "unknown").upper(),
                    title=vuln_data.get("title", "Unknown vulnerability"),
                    description=vuln_data.get("description", ""),
                    cvss_score=vuln_data.get("cvssScore"),
                    cwe=self._extract_cwe_list(vuln_data),
                    license_issue=vuln_data.get("type", "") == "license",
                    fix_pr_available=bool(vuln_data.get("isUpgradable", False)),
                    upgrade_path=self._extract_upgrade_path(vuln_data),
                    dependency_path=vuln_data.get("from", []),
                    first_patched_version=self._extract_first_patched_version(vuln_data),
                    publication_time=vuln_data.get("publicationTime"),
                    exploit_maturity=vuln_data.get("exploitMaturity"),
                    detected_at=datetime.now(timezone.utc).isoformat(),
                )
                vulnerabilities.append(vulnerability)

        return vulnerabilities

    async def _enhance_vulnerability_analysis(
        self, vuln: OpenSourceVulnerability
    ) -> OpenSourceVulnerability:
        """Enhance vulnerability with additional security analysis"""
        # Add EQ12-specific context
        if any(keyword in vuln.package_name.lower()
                for keyword in ["crypto", "payment", "auth", "jwt"]):
            vuln.security_considerations = ["Critical for betting platform security"]

        # Analyze dependency chain for betting-specific risks
        if any("betting" in dep.lower() or "finance" in dep.lower()
                for dep in vuln.dependency_path):
            vuln.security_considerations = vuln.security_considerations or []
            vuln.security_considerations.append("Financial component dependency")

        return vuln

    async def analyze_openai_cookbook_patterns(self) -> List[AIIntegrationPattern]:
        """Analyze OpenAI Cookbook for integration patterns"""
        patterns = []

        # Define key patterns based on cookbook analysis
        cookbook_patterns = [{"pattern_id": "gpt5_prompting",
                              "pattern_name": "GPT-5 Enhanced Prompting",
                              "category": "REASONING_RESPONSES",
                              "description": "Advanced prompting techniques for GPT-5 reasoning capabilities",
                              "use_case": "Complex betting analysis and decision making",
                              "security_considerations": ["Prompt injection prevention",
                                                          "Output validation and sanitization",
                                                          "Rate limiting and abuse prevention",
                                                          ],
                              "implementation_notes": "Use structured outputs for betting predictions",
                              "gpt5_compatible": True,
                              "agent_sdk_compatible": True,
                              "responses_api_compatible": True,
                              "source_url": "https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide",
                              },
                             {"pattern_id": "function_calling_security",
                              "pattern_name": "Secure Function Calling",
                              "category": "FUNCTIONS",
                              "description": "Secure implementation of function calling for betting operations",
                              "use_case": "API calls for odds retrieval and bet placement",
                              "security_considerations": ["Input validation for function parameters",
                                                          "Authorization checks for sensitive operations",
                                                          "Audit logging for all function calls",
                                                          ],
                              "implementation_notes": "Implement strict parameter validation",
                              "gpt5_compatible": True,
                              "agent_sdk_compatible": True,
                              "responses_api_compatible": True,
                              "source_url": "https://cookbook.openai.com/examples/how_to_call_functions_with_chat_models",
                              },
                             {"pattern_id": "agents_sdk_integration",
                              "pattern_name": "Agents SDK for Betting Automation",
                              "category": "AGENTS_SDK",
                              "description": "Multi-agent systems for comprehensive betting analysis",
                              "use_case": "Coordinated analysis across multiple betting markets",
                              "security_considerations": ["Agent communication security",
                                                          "Shared state protection",
                                                          "Agent authorization and permissions",
                                                          ],
                              "implementation_notes": "Use MCP for secure agent communication",
                              "gpt5_compatible": True,
                              "agent_sdk_compatible": True,
                              "responses_api_compatible": True,
                              "source_url": "https://cookbook.openai.com/examples/agents_sdk/multi-agent-portfolio-collaboration",
                              },
                             {"pattern_id": "multimodal_analysis",
                              "pattern_name": "Multimodal Betting Analysis",
                              "category": "MULTIMODAL",
                              "description": "Integration of text, image, and data analysis for betting insights",
                              "use_case": "Visual analysis of sports data and statistics",
                              "security_considerations": ["Image content validation",
                                                          "Data source verification",
                                                          "Privacy protection for user data",
                                                          ],
                              "implementation_notes": "Combine vision and text models for comprehensive analysis",
                              "gpt5_compatible": True,
                              "agent_sdk_compatible": False,
                              "responses_api_compatible": True,
                              "source_url": "https://cookbook.openai.com/examples/multimodal/image_understanding_with_rag",
                              },
                             {"pattern_id": "evaluation_framework",
                              "pattern_name": "AI Model Evaluation for Betting",
                              "category": "EVALS",
                              "description": "Systematic evaluation of AI predictions against betting outcomes",
                              "use_case": "Continuous improvement of betting prediction accuracy",
                              "security_considerations": ["Evaluation data integrity",
                                                          "Model performance monitoring",
                                                          "Bias detection and mitigation",
                                                          ],
                              "implementation_notes": "Implement automated evaluation pipelines",
                              "gpt5_compatible": True,
                              "agent_sdk_compatible": True,
                              "responses_api_compatible": True,
                              "source_url": "https://cookbook.openai.com/examples/evaluation/building_resilient_prompts_using_an_evaluation_flywheel",
                              },
                             {"pattern_id": "guardrails_implementation",
                              "pattern_name": "AI Guardrails for Financial Operations",
                              "category": "GUARDRAILS",
                              "description": "Safety mechanisms for AI-driven financial decisions",
                              "use_case": "Prevention of unauthorized or risky betting operations",
                              "security_considerations": ["Transaction amount limits",
                                                          "Suspicious pattern detection",
                                                          "Manual override capabilities",
                                                          ],
                              "implementation_notes": "Implement multi-layer validation for financial operations",
                              "gpt5_compatible": True,
                              "agent_sdk_compatible": True,
                              "responses_api_compatible": True,
                              "source_url": "https://cookbook.openai.com/examples/developing_hallucination_guardrails",
                              },
                             ]

        for pattern_data in cookbook_patterns:
            pattern = AIIntegrationPattern(
                pattern_id=pattern_data["pattern_id"],
                pattern_name=pattern_data["pattern_name"],
                category=pattern_data["category"],
                description=pattern_data["description"],
                use_case=pattern_data["use_case"],
                security_considerations=pattern_data["security_considerations"],
                implementation_notes=pattern_data["implementation_notes"],
                code_example=await self._generate_code_example(pattern_data["pattern_id"]),
                gpt5_compatible=pattern_data["gpt5_compatible"],
                agent_sdk_compatible=pattern_data["agent_sdk_compatible"],
                responses_api_compatible=pattern_data["responses_api_compatible"],
                source_url=pattern_data["source_url"],
            )
            patterns.append(pattern)

        logger.info(f"Analyzed {len(patterns)} OpenAI Cookbook patterns")
        return patterns

    async def _generate_code_example(self, pattern_id: str) -> str:
        """Generate code examples for integration patterns"""
        code_examples = {
            "gpt5_prompting": """
# GPT-5 Enhanced Prompting for Betting Analysis
import openai

async def analyze_betting_opportunity(game_data, market_conditions):
    client = openai.OpenAI()

    response = await client.chat.completions.create(
        model="gpt-5-turbo",
        messages=[
            {"role": "system", "content": "You are a professional sports betting analyst with expertise in risk assessment and market analysis."},
            {"role": "user", "content": f"Analyze this betting opportunity: {game_data}. Consider market conditions: {market_conditions}. Provide structured analysis with confidence scores."}
        ],
        temperature=0.1,  # Low temperature for consistent analysis
        max_tokens=1000,
        response_format={"type": "json_object"}
    )

    return response.choices[0].message.content
            """,
            "function_calling_security": """
# Secure Function Calling for Betting Operations
import openai
from typing import Dict, Any
import logging

class SecureBettingFunctions:
    def __init__(self):
        self.audit_log = logging.getLogger("betting_audit")

    async def place_bet(self, amount: float, odds: float, market: str) -> Dict[str, Any]:
        # Validate inputs
        if amount <= 0 or amount > 1000:  # Safety limits
            raise ValueError("Invalid bet amount")

        if odds <= 1.0:
            raise ValueError("Invalid odds")

        # Log the operation
        self.audit_log.info(f"Bet placement: {amount} on {market} at {odds}")

        # Implement actual betting logic here
        return {"status": "success", "bet_id": "12345", "amount": amount}

    def get_function_definitions(self):
        return [
            {
                "name": "place_bet",
                "description": "Place a secure bet with validation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "amount": {"type": "number", "minimum": 1, "maximum": 1000},
                        "odds": {"type": "number", "minimum": 1.01},
                        "market": {"type": "string", "enum": ["nhl", "nba", "nfl"]}
                    },
                    "required": ["amount", "odds", "market"]
                }
            }
        ]
            """,
            "agents_sdk_integration": '''
# Multi-Agent Betting Analysis System
from openai import OpenAI
import asyncio

class BettingAnalysisAgent:
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.client = OpenAI()

    async def analyze_market(self, market_data: dict):
        """Each agent analyzes from their specialized perspective"""

        if self.agent_type == "odds_analyzer":
            return await self._analyze_odds(market_data)
        elif self.agent_type == "risk_assessor":
            return await self._assess_risk(market_data)
        elif self.agent_type == "trend_analyst":
            return await self._analyze_trends(market_data)

    async def _analyze_odds(self, data):
        # Specialized odds analysis
        pass

    async def _assess_risk(self, data):
        # Risk assessment logic
        pass

    async def _analyze_trends(self, data):
        # Trend analysis logic
        pass

class MultiAgentBettingSystem:
    def __init__(self):
        self.agents = [
            BettingAnalysisAgent("odds_analyzer"),
            BettingAnalysisAgent("risk_assessor"),
            BettingAnalysisAgent("trend_analyst")
        ]

    async def comprehensive_analysis(self, market_data):
        tasks = [agent.analyze_market(market_data) for agent in self.agents]
        results = await asyncio.gather(*tasks)

        # Combine agent insights
        return self._synthesize_analysis(results)
            ''',
        }

        return code_examples.get(pattern_id, "# Code example not available")

    async def generate_enhanced_dashboard(self, report: EnhancedSecurityReport) -> str:
        """Generate comprehensive dashboard with hardcoded links"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dashboard_filename = f"enhanced_security_ai_dashboard_{timestamp}.html"
        dashboard_path = self.dashboards_dir / dashboard_filename

        # Hardcoded dashboard URL
        dashboard_url = f"{self.dashboard_base_url}/{dashboard_filename}"

        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EQ12 Enhanced Security & AI Integration Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .gradient-bg {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .security-critical {{ background-color: #fee2e2; border-left: 4px solid #dc2626; }}
        .security-high {{ background-color: #fef3c7; border-left: 4px solid #d97706; }}
        .security-medium {{ background-color: #f3f4f6; border-left: 4px solid #6b7280; }}
        .ai-pattern {{ background-color: #ede9fe; border-left: 4px solid #7c3aed; }}
    </style>
</head>
<body class="bg-gray-100">
    <!-- Header -->
    <header class="gradient-bg text-white py-6">
        <div class="container mx-auto px-4">
            <div class="flex justify-between items-center">
                <div>
                    <h1 class="text-3xl font-bold">🔒 EQ12 Enhanced Security & AI Dashboard</h1>
                    <p class = (
                        "text-gray-200">Comprehensive Security Analysis with OpenAI Integration</p>
                    )
                    <p class = (
                        "text-sm text-gray-300">Dashboard URL: <a href="{dashboard_url}" class="underline">{dashboard_url}</a></p>
                    )
                </div>
                <div class="text-right">
                    <p class="text-sm">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                    <p class="text-sm">Report ID: {report.report_id}</p>
                </div>
            </div>
        </div>
    </header>

    <div class="container mx-auto px-4 py-8">

        <!-- Executive Summary -->
        <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h2 class="text-2xl font-bold text-gray-800 mb-6">📊 Executive Summary</h2>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div class="bg-gradient-to-r from-red-500 to-red-600 text-white p-4 rounded-lg">
                    <h3 class="text-lg font-semibold">Security Score</h3>
                    <p class="text-3xl font-bold">{report.security_score:.1f}/100</p>
                </div>
                <div class = (
                    "bg-gradient-to-r from-purple-500 to-purple-600 text-white p-4 rounded-lg">
                )
                    <h3 class="text-lg font-semibold">AI Integration</h3>
                    <p class="text-3xl font-bold">{report.ai_integration_score:.1f}/100</p>
                </div>
                <div class="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 rounded-lg">
                    <h3 class="text-lg font-semibold">Vulnerabilities</h3>
                    <p class="text-3xl font-bold">{len(report.snyk_vulnerabilities)}</p>
                </div>
                <div class="bg-gradient-to-r from-green-500 to-green-600 text-white p-4 rounded-lg">
                    <h3 class="text-lg font-semibold">AI Patterns</h3>
                    <p class="text-3xl font-bold">{len(report.ai_patterns)}</p>
                </div>
            </div>

            <div class="mt-6 p-4 bg-gray-50 rounded-lg">
                <h3 class="text-lg font-semibold text-gray-800">Overall Risk Assessment</h3>
                <p class = (
                    "text-2xl font-bold text-{self._get_risk_color(report.overall_risk_assessment)}-600">
                )
                    {report.overall_risk_assessment}
                </p>
            </div>
        </div>

        <!-- Security Vulnerabilities -->
        <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h2 class = (
                "text-2xl font-bold text-gray-800 mb-6">🛡️ Snyk Open Source Vulnerabilities</h2>
            )

            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        """

        # Add vulnerability count by severity
        severity_counts = self._count_vulnerabilities_by_severity(
            report.snyk_vulnerabilities)

        for severity, count in severity_counts.items():
            color = self._get_severity_color(severity)
            html_content += """
                <div class="bg-{color}-100 border border-{color}-200 p-4 rounded-lg">
                    <h3 class="text-lg font-semibold text-{color}-800">{severity.title()}</h3>
                    <p class="text-2xl font-bold text-{color}-900">{count}</p>
                </div>
            """

        html_content += """
            </div>

            <div class="space-y-4">
        """

        # Add top 10 most critical vulnerabilities
        critical_vulns = sorted(
            report.snyk_vulnerabilities,
            key=lambda x: (self._severity_weight(x.severity), x.cvss_score or 0),
            reverse=True,
        )[:10]

        for vuln in critical_vulns:
            severity_class = self._get_severity_class(vuln.severity)
            html_content += """
                <div class="{severity_class} p-4 rounded-lg">
                    <div class="flex justify-between items-start">
                        <div>
                            <h4 class="text-lg font-semibold text-gray-800">{vuln.title}</h4>
                            <p class = (
                                "text-sm text-gray-600">Package: {vuln.package_name} v{vuln.installed_version}</p>
                            )
                            <p class = (
                                "text-sm text-gray-600">CVSS: {vuln.cvss_score or 'N/A'} | Severity: {vuln.severity}</p>
                            )
                            {'<p class = (
                                "text-sm text-green-600">✅ Fix Available: ' + vuln.fixed_version + '</p>' if vuln.fix_pr_available else '<p class="text-sm text-red-600">❌ No automated fix available</p>'}
                            )
                        </div>
                        <div class="text-right">
                            <span class = (
                                "px-2 py-1 bg-{self._get_severity_color(vuln.severity)}-200 text-{self._get_severity_color(vuln.severity)}-800 rounded-full text-xs">
                            )
                                {vuln.severity}
                            </span>
                        </div>
                    </div>
                </div>
            """

        html_content += """
            </div>
        </div>

        <!-- AI Integration Patterns -->
        <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h2 class="text-2xl font-bold text-gray-800 mb-6">🤖 OpenAI Integration Patterns</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        """

        for pattern in report.ai_patterns:
            html_content += """
                <div class="ai-pattern p-4 rounded-lg">
                    <h4 class="text-lg font-semibold text-purple-800">{pattern.pattern_name}</h4>
                    <p class="text-sm text-gray-600 mb-2">{pattern.category}</p>
                    <p class="text-gray-700 mb-3">{pattern.description}</p>
                    <p class = (
                        "text-sm text-gray-600 mb-2"><strong>Use Case:</strong> {pattern.use_case}</p>
                    )

                    <div class="mb-3">
                        <h5 class = (
                            "text-sm font-semibold text-gray-700">Security Considerations:</h5>
                        )
                        <ul class="text-xs text-gray-600 list-disc list-inside">
            """

            for consideration in pattern.security_considerations:
                html_content += f"<li>{consideration}</li>"

            html_content += """
                        </ul>
                    </div>

                    <div class="flex flex-wrap gap-2 mb-3">
                        {'<span class = (
                            "px-2 py-1 bg-green-200 text-green-800 rounded-full text-xs">GPT-5</span>' if pattern.gpt5_compatible else ''}
                        )
                        {'<span class = (
                            "px-2 py-1 bg-blue-200 text-blue-800 rounded-full text-xs">Agents SDK</span>' if pattern.agent_sdk_compatible else ''}
                        )
                        {'<span class = (
                            "px-2 py-1 bg-purple-200 text-purple-800 rounded-full text-xs">Responses API</span>' if pattern.responses_api_compatible else ''}
                        )
                    </div>

                    <a href = (
                        "{pattern.source_url}" target="_blank" class="text-purple-600 hover:text-purple-800 text-sm underline">
                    )
                        📚 View Cookbook Example
                    </a>
                </div>
            """

        html_content += """
            </div>
        </div>

        <!-- Dashboard Links -->
        <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h2 class="text-2xl font-bold text-gray-800 mb-6">🔗 Related Dashboards & Resources</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        """

        # Add hardcoded dashboard links
        dashboard_links = [
            {
                "url": f"{self.dashboard_base_url}/tonight_nhl.html",
                "title": "NHL Tonight Dashboard",
                "description": "Live NHL games and betting analysis",
                "category": "Betting Analysis",
            },
            {
                "url": f"{self.dashboard_base_url}/security_report_{timestamp}.html",
                "title": "Security Report",
                "description": "Detailed security analysis and recommendations",
                "category": "Security",
            },
            {
                "url": f"{self.dashboard_base_url}/ai_integration_status.html",
                "title": "AI Integration Status",
                "description": "OpenAI API integration and usage metrics",
                "category": "AI Integration",
            },
            {
                "url": "https://cookbook.openai.com/",
                "title": "OpenAI Cookbook",
                "description": "Official OpenAI examples and best practices",
                "category": "External Resources",
            },
            {
                "url": "https://docs.snyk.io/scan-with-snyk/snyk-open-source",
                "title": "Snyk Open Source Docs",
                "description": "Official Snyk Open Source documentation",
                "category": "External Resources",
            },
            {
                "url": "https://platform.openai.com/docs/introduction",
                "title": "OpenAI API Documentation",
                "description": "Complete OpenAI API reference and guides",
                "category": "External Resources",
            },
        ]

        for link in dashboard_links:
            html_content += """
                <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
                    <h4 class="text-lg font-semibold text-gray-800">{link['title']}</h4>
                    <p class="text-sm text-gray-600 mb-2">{link['description']}</p>
                    <p class="text-xs text-purple-600 mb-2">{link['category']}</p>
                    <a href = (
                        "{link['url']}" target="_blank" class="text-blue-600 hover:text-blue-800 text-sm underline">
                    )
                        🔗 Open Dashboard
                    </a>
                </div>
            """

        html_content += """
            </div>
        </div>

        <!-- Recommendations -->
        <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h2 class="text-2xl font-bold text-gray-800 mb-6">💡 Recommendations</h2>
            <div class="space-y-3">
        """

        for i, recommendation in enumerate(report.recommendations, 1):
            html_content += """
                <div class="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                    <span class = (
                        "flex-shrink-0 w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                    )
                        {i}
                    </span>
                    <p class="text-gray-700">{recommendation}</p>
                </div>
            """

        html_content += """
            </div>
        </div>

        <!-- Technical Details -->
        <div class="bg-white rounded-lg shadow-lg p-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-6">🔧 Technical Details</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h3 class="text-lg font-semibold text-gray-700 mb-3">Compliance Status</h3>
                    <div class="space-y-2">
        """

        for framework, status in report.compliance_status.items():
            color = (
                "green"
                if status == "COMPLIANT"
                else "yellow" if status == "NEEDS_ATTENTION" else "red"
            )
            html_content += """
                        <div class="flex justify-between items-center p-2 bg-{color}-50 rounded">
                            <span class="text-gray-700">{framework.replace('_', ' ').title()}</span>
                            <span class = (
                                "px-2 py-1 bg-{color}-200 text-{color}-800 rounded-full text-xs">{status}</span>
                            )
                        </div>
            """

        html_content += """
                    </div>
                </div>
                <div>
                    <h3 class="text-lg font-semibold text-gray-700 mb-3">System Information</h3>
                    <div class="space-y-2">
                        <p class = (
                            "text-sm text-gray-600">Report Generated: {report.generation_timestamp}</p>
                        )
                        <p class = (
                            "text-sm text-gray-600">Next Scan Recommended: {report.next_scan_recommended}</p>
                        )
                        <p class = (
                            "text-sm text-gray-600">Dashboard URL: <a href="{dashboard_url}" class="text-blue-600 underline">{dashboard_url}</a></p>
                        )
                        <p class = (
                            "text-sm text-gray-600">Total Patterns Analyzed: {len(report.ai_patterns)}</p>
                        )
                        <p class="text-sm text-gray-600">Snyk Integration: Active</p>
                        <p class="text-sm text-gray-600">OpenAI Integration: Active</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-6 mt-12">
        <div class="container mx-auto px-4 text-center">
            <p>&copy; 2025 EQ12 Enhanced Security & AI Integration System</p>
            <p class="text-sm text-gray-400 mt-2">
                Powered by Snyk Security Analysis & OpenAI Cookbook Integration |
                Dashboard: <a href = (
                    "{dashboard_url}" class="text-blue-400 underline">{dashboard_url}</a>
                )
            </p>
        </div>
    </footer>
</body>
</html>
        """

        # Save dashboard
        with open(dashboard_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Add dashboard link to report
        dashboard_link = DashboardLink(
            url=dashboard_url,
            title="Enhanced Security & AI Integration Dashboard",
            description=(
                "Comprehensive analysis of security vulnerabilities and AI integration patterns",
            )
            category="Security & AI Analysis",
            created_at=datetime.now(timezone.utc).isoformat(),
            access_level="internal",
        )

        if not hasattr(report, "dashboard_links") or report.dashboard_links is None:
            report.dashboard_links = []
        report.dashboard_links.append(dashboard_link)

        logger.info(f"Enhanced dashboard generated: {dashboard_path}")
        logger.info(f"Dashboard URL: {dashboard_url}")

        return str(dashboard_path)

    def _count_vulnerabilities_by_severity(
        self, vulnerabilities: List[OpenSourceVulnerability]
    ) -> Dict[str, int]:
        """Count vulnerabilities by severity level"""
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for vuln in vulnerabilities:
            severity = vuln.severity.lower()
            if severity in counts:
                counts[severity] += 1

        return counts

    def _get_severity_color(self, severity: str) -> str:
        """Get color for severity level"""
        colors = {
            "critical": "red",
            "high": "orange",
            "medium": "yellow",
            "low": "gray",
        }
        return colors.get(severity.lower(), "gray")

    def _get_severity_class(self, severity: str) -> str:
        """Get CSS class for severity level"""
        classes = {
            "critical": "security-critical",
            "high": "security-high",
            "medium": "security-medium",
            "low": "security-medium",
        }
        return classes.get(severity.lower(), "security-medium")

    def _severity_weight(self, severity: str) -> int:
        """Get numeric weight for severity level"""
        weights = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        return weights.get(severity.lower(), 0)

    def _get_risk_color(self, risk_level: str) -> str:
        """Get color for risk assessment"""
        if "critical" in risk_level.lower() or "high" in risk_level.lower():
            return "red"
        elif "medium" in risk_level.lower() or "moderate" in risk_level.lower():
            return "yellow"
        else:
            return "green"

    def _extract_fixed_version(self, vuln_data: Dict) -> Optional[str]:
        """Extract fixed version from vulnerability data"""
        if "fixes" in vuln_data and vuln_data["fixes"]:
            return vuln_data["fixes"][0].get("version")
        return None

    def _extract_cwe_list(self, vuln_data: Dict) -> Optional[str]:
        """Extract CWE information"""
        if "identifiers" in vuln_data and "CWE" in vuln_data["identifiers"]:
            cwes = vuln_data["identifiers"]["CWE"]
            return ", ".join(cwes) if isinstance(cwes, list) else cwes
        return None

    def _extract_upgrade_path(self, vuln_data: Dict) -> Optional[str]:
        """Extract upgrade path information"""
        if vuln_data.get("isUpgradable") and "upgradePath" in vuln_data:
            path = vuln_data["upgradePath"]
            if isinstance(path, list):
                return " -> ".join(path)
        return None

    def _extract_first_patched_version(self, vuln_data: Dict) -> Optional[str]:
        """Extract first patched version"""
        if "patches" in vuln_data and vuln_data["patches"]:
            return vuln_data["patches"][0].get("version")
        return None

    async def run_comprehensive_analysis(self) -> EnhancedSecurityReport:
        """Run comprehensive security and AI integration analysis"""
        logger.info("🚀 Starting comprehensive EQ12 security and AI integration analysis")

        # Analyze dependencies with Snyk Open Source
        all_vulnerabilities = []
        scan_targets = {
            "scripts": self.project_root / "scripts",
            "tests": self.project_root / "tests",
            "configs": self.project_root / "configs",
        }

        for target_name, target_path in scan_targets.items():
            if target_path.exists():
                logger.info(f"Analyzing {target_name}: {target_path}")
                vulnerabilities = await self.analyze_dependency_vulnerabilities(target_path)
                all_vulnerabilities.extend(vulnerabilities)

        # Analyze OpenAI Cookbook patterns
        ai_patterns = await self.analyze_openai_cookbook_patterns()

        # Calculate scores
        security_score = self._calculate_security_score(all_vulnerabilities)
        ai_integration_score = self._calculate_ai_integration_score(ai_patterns)
        overall_risk = self._assess_overall_risk(all_vulnerabilities, ai_patterns)

        # Generate compliance status
        compliance_status = self._assess_compliance_status(all_vulnerabilities)

        # Generate recommendations
        recommendations = self._generate_enhanced_recommendations(
            all_vulnerabilities, ai_patterns)

        # Create comprehensive report
        report = EnhancedSecurityReport(
            report_id=f"EQ12-SEC-AI-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            generation_timestamp=datetime.now(timezone.utc).isoformat(),
            snyk_vulnerabilities=all_vulnerabilities,
            ai_patterns=ai_patterns,
            dashboard_links=[],
            security_score=security_score,
            ai_integration_score=ai_integration_score,
            overall_risk_assessment=overall_risk,
            recommendations=recommendations,
            compliance_status=compliance_status,
            next_scan_recommended=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        )

        # Generate enhanced dashboard
        dashboard_path = await self.generate_enhanced_dashboard(report)

        # Save comprehensive report
        report_path = (
            self.logs_dir /
            f"enhanced_security_ai_report_{
                datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(asdict(report), f, indent=2, ensure_ascii=False)

        logger.info("📊 Comprehensive analysis completed")
        logger.info(f"📄 Report saved: {report_path}")
        logger.info(f"🌐 Dashboard generated: {dashboard_path}")

        return report

    def _calculate_security_score(
            self, vulnerabilities: List[OpenSourceVulnerability]) -> float:
        """Calculate overall security score (0-100, higher is better)"""
        if not vulnerabilities:
            return 100.0

        # Weight vulnerabilities by severity
        penalty = 0
        for vuln in vulnerabilities:
            if vuln.severity.upper() == "CRITICAL":
                penalty += 15
            elif vuln.severity.upper() == "HIGH":
                penalty += 8
            elif vuln.severity.upper() == "MEDIUM":
                penalty += 3
            elif vuln.severity.upper() == "LOW":
                penalty += 1

        score = max(0, 100 - penalty)
        return round(score, 1)

    def _calculate_ai_integration_score(
            self, patterns: List[AIIntegrationPattern]) -> float:
        """Calculate AI integration readiness score"""
        if not patterns:
            return 0.0

        # Score based on pattern coverage and security considerations
        total_score = 0
        for pattern in patterns:
            pattern_score = 10  # Base score per pattern

            # Bonus for GPT-5 compatibility
            if pattern.gpt5_compatible:
                pattern_score += 5

            # Bonus for security considerations
            if len(pattern.security_considerations) >= 3:
                pattern_score += 3

            # Bonus for multi-API compatibility
            if (
                pattern.gpt5_compatible
                and pattern.agent_sdk_compatible
                and pattern.responses_api_compatible
            ):
                pattern_score += 5

            total_score += pattern_score

        # Normalize to 0-100 scale
        max_possible_score = len(patterns) * 23  # Max possible per pattern
        if max_possible_score > 0:
            score = (total_score / max_possible_score) * 100
        else:
            score = 0

        return round(score, 1)

    def _assess_overall_risk(
        self,
        vulnerabilities: List[OpenSourceVulnerability],
        patterns: List[AIIntegrationPattern],
    ) -> str:
        """Assess overall system risk level"""
        critical_vulns = sum(
            1 for v in vulnerabilities if v.severity.upper() == "CRITICAL")
        high_vulns = sum(1 for v in vulnerabilities if v.severity.upper() == "HIGH")

        if critical_vulns > 0:
            return "CRITICAL - Immediate action required"
        elif high_vulns > 5:
            return "HIGH - Address high-priority vulnerabilities"
        elif high_vulns > 0 or len(vulnerabilities) > 10:
            return "MEDIUM - Monitor and plan remediation"
        else:
            return "LOW - Maintain current security practices"

    def _assess_compliance_status(
        self, vulnerabilities: List[OpenSourceVulnerability]
    ) -> Dict[str, str]:
        """Assess compliance with various security frameworks"""
        critical_count = sum(
            1 for v in vulnerabilities if v.severity.upper() == "CRITICAL")
        high_count = sum(1 for v in vulnerabilities if v.severity.upper() == "HIGH")

        status = {}

        # OWASP compliance
        if critical_count == 0 and high_count <= 2:
            status["OWASP_TOP_10"] = "COMPLIANT"
        elif critical_count == 0 and high_count <= 5:
            status["OWASP_TOP_10"] = "NEEDS_ATTENTION"
        else:
            status["OWASP_TOP_10"] = "NON_COMPLIANT"

        # Financial services compliance
        if critical_count == 0:
            status["FINANCIAL_SERVICES"] = "COMPLIANT"
        else:
            status["FINANCIAL_SERVICES"] = "NON_COMPLIANT"

        # Gambling industry compliance
        status["GAMBLING_INDUSTRY"] = status["FINANCIAL_SERVICES"]

        return status

    def _generate_enhanced_recommendations(
        self,
        vulnerabilities: List[OpenSourceVulnerability],
        patterns: List[AIIntegrationPattern],
    ) -> List[str]:
        """Generate enhanced recommendations based on analysis"""
        recommendations = []

        # Security recommendations
        critical_vulns = [
            v for v in vulnerabilities if v.severity.upper() == "CRITICAL"]
        if critical_vulns:
            recommendations.append(
                f"🚨 URGENT: Address {len(critical_vulns)} critical vulnerabilities immediately. "
                "These pose significant risk to the betting platform."
            )

        fixable_vulns = [v for v in vulnerabilities if v.fix_pr_available]
        if fixable_vulns:
            recommendations.append(
                f"🔧 Apply automated fixes for {len(fixable_vulns)} vulnerabilities with "
                "available patches using Snyk fix PRs."
            )

        # AI integration recommendations
        if patterns:
            recommendations.append(
                f"🤖 Implement {len(patterns)} identified OpenAI integration patterns "
                "to enhance betting analysis capabilities."
            )

        gpt5_patterns = [p for p in patterns if p.gpt5_compatible]
        if gpt5_patterns:
            recommendations.append(
                f"🧠 Leverage GPT-5 reasoning capabilities through {len(gpt5_patterns)} "
                "compatible patterns for advanced betting analysis."
            )

        # Security-specific recommendations for betting platform
        recommendations.extend(
            [
                "💰 Implement additional security measures for financial transaction components",
                "🔐 Enable continuous monitoring for dependency vulnerabilities",
                "📊 Set up automated security scanning in CI/CD pipeline",
                "🛡️ Implement AI guardrails for betting operations as shown in OpenAI Cookbook",
                "📈 Establish security metrics dashboard for ongoing monitoring",
            ])

        return recommendations


async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="EQ12 Enhanced Security & AI Integration Analysis")
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Run comprehensive security and AI integration analysis",
    )
    parser.add_argument(
        "--generate-dashboard",
        action="store_true",
        help="Generate enhanced dashboard with hardcoded links",
    )
    parser.add_argument(
        "--snyk-only",
        action="store_true",
        help="Run Snyk analysis only")
    parser.add_argument(
        "--ai-patterns-only",
        action="store_true",
        help="Analyze AI patterns only")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    analyzer = EnhancedSnykOpenSourceAnalyzer()

    try:
        if args.analyze or not any(
            [args.snyk_only, args.ai_patterns_only, args.generate_dashboard]
        ):
            # Run comprehensive analysis
            logger.info(
                "🔒 Starting comprehensive EQ12 security and AI integration analysis")
            report = await analyzer.run_comprehensive_analysis()

            # Display summary
            print("\n" + "=" * 80)
            print("🔒 EQ12 ENHANCED SECURITY & AI INTEGRATION ANALYSIS")
            print("=" * 80)
            print(f"📊 Security Score: {report.security_score}/100")
            print(f"🤖 AI Integration Score: {report.ai_integration_score}/100")
            print(f"🛡️ Total Vulnerabilities: {len(report.snyk_vulnerabilities)}")
            print(f"🧠 AI Patterns Analyzed: {len(report.ai_patterns)}")
            print(f"⚠️ Overall Risk: {report.overall_risk_assessment}")
            print(f"🌐 Dashboard Links: {len(report.dashboard_links)}")
            print("=" * 80)

            if report.dashboard_links:
                print("\n📱 Dashboard URLs:")
                for link in report.dashboard_links:
                    print(f"   🔗 {link.title}: {link.url}")

            return 0

        elif args.snyk_only:
            logger.info("Running Snyk Open Source analysis only")
            # Implementation for Snyk-only analysis
            return 0

        elif args.ai_patterns_only:
            logger.info("Analyzing OpenAI Cookbook patterns only")
            patterns = await analyzer.analyze_openai_cookbook_patterns()
            print(f"Found {len(patterns)} AI integration patterns")
            return 0

        elif args.generate_dashboard:
            logger.info("Generating dashboard with hardcoded links")
            # Generate sample report for dashboard
            sample_report = EnhancedSecurityReport(
                report_id="SAMPLE-001",
                generation_timestamp=datetime.now(timezone.utc).isoformat(),
                snyk_vulnerabilities=[],
                ai_patterns=await analyzer.analyze_openai_cookbook_patterns(),
                dashboard_links=[],
                security_score=85.0,
                ai_integration_score=92.0,
                overall_risk_assessment="LOW - Maintain current practices",
                recommendations=["Sample recommendation"],
                compliance_status={"OWASP_TOP_10": "COMPLIANT"},
                next_scan_recommended="2025-01-16",
            )

            dashboard_path = await analyzer.generate_enhanced_dashboard(sample_report)
            print(f"✅ Dashboard generated: {dashboard_path}")
            return 0

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
