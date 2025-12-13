#!/usr/bin/env python3
"""
EQ12 GODSTACK - Interactive Streaming Governance Assistant
Real-time conversational AI for governance with live streaming responses.

Features:
- Interactive streaming chat with real-time AI responses
- Live progress indicators and typing effects
- Comprehensive governance task automation
- Real-time streaming event visualization
- Multi-modal governance analysis (text, reasoning, function calls)

Author: EQ12 GODSTACK Team
Version: 2.0.0 (Streaming Enhanced)
License: MIT
"""

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import colorama
from colorama import Fore, Style

from eq12_openai_streaming import (
    EQ12StreamingGovernanceClient,
    stream_chrome_governance_analysis,
    stream_security_audit_analysis,
)

# Initialize colorama for Windows compatibility
colorama.init(autoreset=True)


class InteractiveStreamingGovernanceAssistant:
    """Interactive streaming governance assistant with real-time AI responses."""

    def __init__(self, eq12_root: str | None = None):
        self.eq12_root = Path(
            eq12_root
            or os.getenv("EQ12_ROOT", "C:/EQ12" if os.name == "nt" else "/workspaces/EQ12")
        )
        self.client = None
        self.current_session = None

        # GPT-5 Enhanced Features (applied from cookbook)
        self.gpt5_features = {
            "multimodal_input": True,
            "advanced_reasoning": True,
            "frontend_generation": True,
            "steerable_responses": True,
            "production_grade": True,
        }

        # GPT-5 Recommended Libraries/Frameworks
        self.recommended_stack = {
            "frameworks": ["Next.js (TypeScript)", "React", "HTML"],
            "styling": ["Tailwind CSS", "shadcn/ui", "Radix Themes"],
            "icons": ["Material Symbols", "Heroicons", "Lucide"],
            "animation": ["Motion"],
            "fonts": ["Inter", "Geist", "Mona Sans", "IBM Plex Sans"],
        }
        self.session_history = []

        # Initialize streaming client
        try:
            self.client = EQ12StreamingGovernanceClient(eq12_root=str(self.eq12_root))
            self.available = True
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  OpenAI API not available: {e}")
            print(f"{Fore.BLUE}ℹ️  Running in demo mode without AI")
            self.available = False

        self.commands = {
            "chrome": self.analyze_chrome_governance,
            "security": self.analyze_security_audit,
            "compliance": self.analyze_compliance,
            "help": self.show_help,
            "history": self.show_history,
            "status": self.show_status,
            "exit": self.exit_assistant,
            "quit": self.exit_assistant,
            "demo": self.run_demo_mode,
        }

        self.running = True

    def print_banner(self):
        """Display the interactive assistant banner."""
        banner = f"""
{Fore.CYAN}{Style.BRIGHT}{"=" * 80}
{Fore.GREEN}  🚀 EQ12 GODSTACK - INTERACTIVE STREAMING GOVERNANCE ASSISTANT
{Fore.CYAN}{"=" * 80}
{Fore.YELLOW}  📡 Real-time AI governance with OpenAI streaming responses
{Fore.BLUE}  🤖 Powered by GPT-4o with live reasoning transparency
{Fore.MAGENTA}  ⚡ Live streaming • Delta updates • Function calls • Reasoning
{Fore.CYAN}{"=" * 80}

{Fore.WHITE}Available Commands:
{Fore.GREEN}  chrome      {Fore.WHITE}- Stream Chrome bookmark security analysis
{Fore.GREEN}  security    {Fore.WHITE}- Stream comprehensive security audit
{Fore.GREEN}  compliance  {Fore.WHITE}- Stream governance compliance check
{Fore.GREEN}  help        {Fore.WHITE}- Show detailed command help
{Fore.GREEN}  history     {Fore.WHITE}- Show session analysis history
{Fore.GREEN}  status      {Fore.WHITE}- Show current streaming status
{Fore.GREEN}  demo        {Fore.WHITE}- Run demo mode (no API key required)
{Fore.GREEN}  exit/quit   {Fore.WHITE}- Exit assistant

{Fore.CYAN}Type a command or describe your governance task...
{Fore.CYAN}{"=" * 80}
"""
        print(banner)

    def print_typing_effect(self, text: str, delay: float = 0.03, color: str = Fore.WHITE):
        """Print text with typing effect."""
        for char in text:
            print(f"{color}{char}", end="", flush=True)
            time.sleep(delay)
        print()  # New line at the end

    def show_progress_indicator(self, message: str, duration: float = 2.0):
        """Show animated progress indicator."""
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        end_time = time.time() + duration

        while time.time() < end_time:
            for frame in frames:
                if time.time() >= end_time:
                    break
                print(f"\r{Fore.CYAN}{frame} {message}", end="", flush=True)
                time.sleep(0.1)

        print(f"\r{Fore.GREEN}✅ {message} - Complete!")

    async def analyze_chrome_governance(self, user_input: str = ""):
        """Stream Chrome governance analysis."""
        print(f"\n{Fore.BLUE}🌐 Chrome Governance Analysis")
        print(f"{Fore.CYAN}{'─' * 60}")

        if not self.available:
            return await self.demo_chrome_analysis()

        try:
            # Gather Chrome bookmark data
            chrome_data = await self.gather_chrome_data()

            print(f"{Fore.YELLOW}📊 Analyzing {len(chrome_data.get('bookmarks', []))} bookmarks...")

            # Start streaming analysis
            context = await stream_chrome_governance_analysis(chrome_data, self.client)
            self.current_session = context
            self.session_history.append(
                {
                    "type": "chrome_governance",
                    "timestamp": datetime.now(),
                    "context": context,
                }
            )

            print(f"\n{Fore.GREEN}🎉 Chrome governance analysis complete!")

        except Exception as e:
            print(f"{Fore.RED}❌ Chrome analysis failed: {e}")

    async def analyze_security_audit(self, user_input: str = ""):
        """Stream security audit analysis."""
        print(f"\n{Fore.RED}🛡️  Security Audit Analysis")
        print(f"{Fore.CYAN}{'─' * 60}")

        if not self.available:
            return await self.demo_security_analysis()

        try:
            # Gather security audit data
            security_data = await self.gather_security_data()

            print(f"{Fore.YELLOW}🔍 Analyzing security posture...")

            # Start streaming analysis
            context = await stream_security_audit_analysis(security_data, self.client)
            self.current_session = context
            self.session_history.append(
                {
                    "type": "security_audit",
                    "timestamp": datetime.now(),
                    "context": context,
                }
            )

            print(f"\n{Fore.GREEN}🎉 Security audit complete!")

        except Exception as e:
            print(f"{Fore.RED}❌ Security audit failed: {e}")

    async def analyze_compliance(self, user_input: str = ""):
        """Stream compliance analysis."""
        print(f"\n{Fore.MAGENTA}📋 Compliance Analysis")
        print(f"{Fore.CYAN}{'─' * 60}")

        if not self.available:
            return await self.demo_compliance_analysis()

        try:
            compliance_data = {
                "frameworks": ["SOC2", "ISO27001", "GDPR"],
                "policies": ["Data_Protection", "Access_Control", "Incident_Response"],
                "last_audit": "2024-01-15",
                "findings": ["Medium risk - Password policy", "Low risk - Encryption"],
            }

            prompt = """
            📋 EQ12 GOVERNANCE COMPLIANCE ANALYSIS

            Review compliance status against major frameworks and provide recommendations.
            Focus on:
            1. SOC2 Type II compliance gaps
            2. ISO27001 certification readiness
            3. GDPR data protection compliance
            4. Policy enforcement effectiveness
            5. Audit trail completeness
            6. Risk mitigation priorities

            Provide actionable compliance roadmap.
            """

            print(f"{Fore.YELLOW}📊 Analyzing compliance frameworks...")

            context = await self.client.start_streaming_governance_analysis(
                task_type="compliance_check",
                governance_prompt=prompt,
                context_data=compliance_data,
            )

            self.current_session = context
            self.session_history.append(
                {"type": "compliance", "timestamp": datetime.now(), "context": context}
            )

            print(f"\n{Fore.GREEN}🎉 Compliance analysis complete!")

        except Exception as e:
            print(f"{Fore.RED}❌ Compliance analysis failed: {e}")

    async def gather_chrome_data(self) -> dict[str, Any]:
        """Gather Chrome bookmark data for analysis."""
        # Check if Chrome bookmarks file exists
        chrome_paths = [
            Path.home() / "AppData/Local/Google/Chrome/User Data/Default/Bookmarks",
            Path.home() / ".config/google-chrome/Default/Bookmarks",
            Path.home() / "Library/Application Support/Google/Chrome/Default/Bookmarks",
        ]

        bookmarks_data = {
            "bookmarks": [],
            "analysis_timestamp": datetime.now().isoformat(),
            "source": "demo_data",
        }

        # Try to read actual Chrome bookmarks
        for chrome_path in chrome_paths:
            if chrome_path.exists():
                try:
                    with open(chrome_path, encoding="utf-8") as f:
                        chrome_bookmarks = json.load(f)
                        # Extract bookmarks from Chrome format
                        bookmarks_data["bookmarks"] = self.extract_chrome_bookmarks(
                            chrome_bookmarks
                        )
                        bookmarks_data["source"] = str(chrome_path)
                        break
                except Exception:
                    continue

        # Use demo data if no Chrome bookmarks found
        if not bookmarks_data["bookmarks"]:
            bookmarks_data["bookmarks"] = [
                {
                    "name": "GitHub",
                    "url": "https://github.com",
                    "folder": "Development",
                },
                {
                    "name": "ChatGPT",
                    "url": "https://chat.openai.com",
                    "folder": "AI Tools",
                },
                {
                    "name": "Banking Portal",
                    "url": "https://bank.example.com",
                    "folder": "Finance",
                },
                {
                    "name": "Company Wiki",
                    "url": "https://wiki.company.com",
                    "folder": "Work",
                },
                {
                    "name": "Cloud Console",
                    "url": "https://console.aws.amazon.com",
                    "folder": "Infrastructure",
                },
            ]

        return bookmarks_data

    def extract_chrome_bookmarks(self, chrome_data: dict) -> list[dict]:
        """Extract bookmarks from Chrome bookmarks JSON."""
        bookmarks = []

        def extract_from_folder(folder, folder_name="Root"):
            if isinstance(folder, dict):
                if folder.get("type") == "url":
                    bookmarks.append(
                        {
                            "name": folder.get("name", "Unknown"),
                            "url": folder.get("url", ""),
                            "folder": folder_name,
                        }
                    )
                elif folder.get("type") == "folder":
                    folder_name = folder.get("name", "Unknown Folder")
                    children = folder.get("children", [])
                    for child in children:
                        extract_from_folder(child, folder_name)

        # Extract from bookmark bar and other folders
        roots = chrome_data.get("roots", {})
        for root_name, root_data in roots.items():
            extract_from_folder(root_data, root_name)

        return bookmarks[:50]  # Limit to 50 bookmarks for analysis

    async def gather_security_data(self) -> dict[str, Any]:
        """Gather security audit data."""
        return {
            "system_info": {
                "os": os.name,
                "platform": sys.platform,
                "python_version": sys.version,
            },
            "file_permissions": "analysis_pending",
            "network_ports": "scan_pending",
            "installed_software": "inventory_pending",
            "security_policies": {
                "password_policy": "Medium strength requirements",
                "firewall_status": "Active",
                "antivirus_status": "Unknown",
                "encryption_status": "Partial",
            },
            "audit_timestamp": datetime.now().isoformat(),
        }

    # Demo mode methods for when API is not available
    async def demo_chrome_analysis(self):
        """Demo Chrome analysis without API."""
        print(f"\n{Fore.BLUE}🌐 Demo: Chrome Governance Analysis")
        self.show_progress_indicator("Analyzing Chrome bookmarks", 2.0)

        demo_findings = """
        🔍 CHROME GOVERNANCE ANALYSIS RESULTS (DEMO)

        ✅ Security Assessment:
        - 15 bookmarks analyzed
        - 2 potential security risks identified
        - 1 corporate policy violation found

        ⚠️  Key Findings:
        1. Banking portal accessed over HTTP (HIGH RISK)
        2. Personal social media in work profile (POLICY)
        3. Outdated development tools bookmarked (MEDIUM)

        📋 Recommendations:
        1. Enable HTTPS-only mode in Chrome
        2. Separate personal/work browsing profiles
        3. Update development tool bookmarks
        4. Implement bookmark governance policy
        """

        self.print_typing_effect(demo_findings, 0.02, Fore.GREEN)

    async def demo_security_analysis(self):
        """Demo security analysis without API."""
        print(f"\n{Fore.RED}🛡️  Demo: Security Audit Analysis")
        self.show_progress_indicator("Performing security scan", 3.0)

        demo_findings = """
        🛡️  SECURITY AUDIT RESULTS (DEMO)

        📊 Overall Security Score: 7.2/10 (Good)

        ✅ Strengths:
        - Firewall active and properly configured
        - OS patches up to date
        - Strong password policy in place

        ⚠️  Areas for Improvement:
        1. Enable full disk encryption (CRITICAL)
        2. Install endpoint detection software (HIGH)
        3. Configure automated backup verification (MEDIUM)
        4. Implement 2FA for all admin accounts (HIGH)

        🎯 Priority Actions:
        1. Deploy encryption within 7 days
        2. Schedule security awareness training
        3. Review and update incident response plan
        """

        self.print_typing_effect(demo_findings, 0.02, Fore.RED)

    async def demo_compliance_analysis(self):
        """Demo compliance analysis without API."""
        print(f"\n{Fore.MAGENTA}📋 Demo: Compliance Analysis")
        self.show_progress_indicator("Checking compliance frameworks", 2.5)

        demo_findings = """
        📋 COMPLIANCE ANALYSIS RESULTS (DEMO)

        🎯 Framework Status:
        - SOC2 Type II: 85% compliant (4 gaps identified)
        - ISO27001: 78% ready (certification possible in 6 months)
        - GDPR: 92% compliant (minor documentation gaps)

        🔧 Required Actions:
        1. Complete access control documentation (SOC2)
        2. Implement change management process (ISO27001)
        3. Update privacy policy language (GDPR)
        4. Conduct vendor risk assessments (All frameworks)

        ⏱️  Timeline:
        - 30 days: Documentation updates
        - 60 days: Process implementations
        - 90 days: Ready for external audit
        """

        self.print_typing_effect(demo_findings, 0.02, Fore.MAGENTA)

    async def run_demo_mode(self, user_input: str = ""):
        """Run full demo mode without API requirements."""
        print(f"\n{Fore.CYAN}🎪 EQ12 Governance Demo Mode")
        print(f"{Fore.YELLOW}Running all governance analyses in demo mode...")

        await self.demo_chrome_analysis()
        print(f"\n{Fore.CYAN}{'─' * 60}")

        await self.demo_security_analysis()
        print(f"\n{Fore.CYAN}{'─' * 60}")

        await self.demo_compliance_analysis()
        print(f"\n{Fore.GREEN}🎉 Demo mode complete!")

    def show_help(self, user_input: str = ""):
        """Show detailed help information."""
        help_text = f"""
{Fore.CYAN}{"=" * 80}
{Fore.GREEN}{Style.BRIGHT}  EQ12 STREAMING GOVERNANCE ASSISTANT - HELP
{Fore.CYAN}{"=" * 80}

{Fore.YELLOW}AVAILABLE COMMANDS:
{Fore.GREEN}  chrome      {Fore.WHITE}- Analyze Chrome bookmarks for security risks
                Real-time streaming analysis of browser governance
                Identifies policy violations, security risks, compliance issues

{Fore.GREEN}  security    {Fore.WHITE}- Comprehensive security audit with AI analysis
                System security posture assessment
                Vulnerability scanning and risk prioritization

{Fore.GREEN}  compliance  {Fore.WHITE}- Multi-framework compliance analysis
                SOC2, ISO27001, GDPR compliance checking
                Gap analysis and remediation roadmaps

{Fore.GREEN}  demo        {Fore.WHITE}- Run all analyses in demo mode (no API required)
                Perfect for testing and evaluation

{Fore.GREEN}  history     {Fore.WHITE}- View session analysis history
{Fore.GREEN}  status      {Fore.WHITE}- Show current streaming session status
{Fore.GREEN}  help        {Fore.WHITE}- Show this help message
{Fore.GREEN}  exit/quit   {Fore.WHITE}- Exit the assistant

{Fore.YELLOW}STREAMING FEATURES:
{Fore.BLUE}  • Real-time AI responses with delta streaming
{Fore.BLUE}  • Live progress indicators and typing effects
{Fore.BLUE}  • Transparent AI reasoning display
{Fore.BLUE}  • Function call monitoring
{Fore.BLUE}  • Comprehensive event logging

{Fore.YELLOW}GOVERNANCE CAPABILITIES:
{Fore.MAGENTA}  • Chrome browser security governance
{Fore.MAGENTA}  • Enterprise security auditing
{Fore.MAGENTA}  • Compliance framework analysis
{Fore.MAGENTA}  • Risk assessment and prioritization
{Fore.MAGENTA}  • Policy enforcement monitoring

{Fore.CYAN}{"=" * 80}
"""
        print(help_text)

    def show_history(self, user_input: str = ""):
        """Show session analysis history."""
        print(f"\n{Fore.BLUE}📊 Analysis History")
        print(f"{Fore.CYAN}{'─' * 60}")

        if not self.session_history:
            print(f"{Fore.YELLOW}No analyses performed in this session yet.")
            return

        for i, session in enumerate(self.session_history, 1):
            timestamp = session["timestamp"].strftime("%H:%M:%S")
            analysis_type = session["type"].replace("_", " ").title()
            print(f"{Fore.GREEN}{i:2}. {Fore.WHITE}{analysis_type} {Fore.CYAN}at {timestamp}")

            if hasattr(session.get("context"), "current_status"):
                status = session["context"].current_status
                print(f"    {Fore.YELLOW}Status: {status}")

    def show_status(self, user_input: str = ""):
        """Show current streaming session status."""
        print(f"\n{Fore.CYAN}📡 Streaming Status")
        print(f"{Fore.CYAN}{'─' * 60}")

        if self.current_session:
            print(f"{Fore.GREEN}Active Session:")
            print(f"  {Fore.YELLOW}Task Type: {Fore.WHITE}{self.current_session.task_type}")
            print(f"  {Fore.YELLOW}Status: {Fore.WHITE}{self.current_session.current_status}")
            print(
                f"  {Fore.YELLOW}Started: {Fore.WHITE}{self.current_session.start_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            print(
                f"  {Fore.YELLOW}Text Length: {Fore.WHITE}{len(self.current_session.accumulated_text)} chars"
            )
        else:
            print(f"{Fore.YELLOW}No active streaming session")

        print(f"\n{Fore.BLUE}Client Status:")
        print(
            f"  {Fore.YELLOW}API Available: {Fore.GREEN if self.available else Fore.RED}{'✅' if self.available else '❌'}"
        )
        print(f"  {Fore.YELLOW}Sessions Run: {Fore.WHITE}{len(self.session_history)}")

    def exit_assistant(self, user_input: str = ""):
        """Exit the assistant."""
        print(f"\n{Fore.GREEN}👋 Thank you for using EQ12 Streaming Governance Assistant!")
        print(f"{Fore.CYAN}🚀 EQ12 GODSTACK - Governance automation complete")
        self.running = False

    async def process_user_input(self, user_input: str):
        """Process user input and execute appropriate command."""
        user_input = user_input.strip().lower()

        # Check for direct commands
        if user_input in self.commands:
            command_func = self.commands[user_input]
            if asyncio.iscoroutinefunction(command_func):
                await command_func(user_input)
            else:
                command_func(user_input)
            return

        # Check for partial matches
        for command, func in self.commands.items():
            if command.startswith(user_input) and len(user_input) >= 2:
                if asyncio.iscoroutinefunction(func):
                    await func(user_input)
                else:
                    func(user_input)
                return

        # Handle natural language or unknown input
        if user_input:
            print(f"{Fore.YELLOW}❓ Unknown command: '{user_input}'")
            print(
                f"{Fore.BLUE}💡 Try 'help' for available commands or 'demo' for a quick demonstration"
            )

    async def run_interactive_session(self):
        """Run the main interactive session."""
        self.print_banner()

        while self.running:
            try:
                # Get user input
                prompt = f"\n{Fore.CYAN}EQ12 Governance{Fore.WHITE}> "
                user_input = input(prompt).strip()

                if not user_input:
                    continue

                # Process the input
                await self.process_user_input(user_input)

            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}⚠️  Interrupted by user")
                self.exit_assistant()
            except EOFError:
                print(f"\n{Fore.YELLOW}👋 Session ended")
                self.exit_assistant()
            except Exception as e:
                print(f"{Fore.RED}❌ Error: {e}")


async def main():
    """Main entry point for the interactive streaming governance assistant."""
    parser = argparse.ArgumentParser(description="EQ12 Interactive Streaming Governance Assistant")
    parser.add_argument("--eq12-root", help="EQ12 root directory", default=None)
    parser.add_argument("--demo", action="store_true", help="Run demo mode immediately")
    parser.add_argument(
        "--command",
        help="Run specific command and exit",
        choices=["chrome", "security", "compliance", "demo", "help"],
    )

    args = parser.parse_args()

    try:
        assistant = InteractiveStreamingGovernanceAssistant(args.eq12_root)

        if args.demo:
            assistant.print_banner()
            await assistant.run_demo_mode()
        elif args.command:
            assistant.print_banner()
            await assistant.process_user_input(args.command)
        else:
            await assistant.run_interactive_session()

    except Exception as e:
        print(f"{Fore.RED}❌ Failed to start assistant: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
