#!/usr/bin/env python3
"""
EQ12 GODSTACK - Conversational AI Governance Assistant
Interactive AI assistant for governance tasks, code reviews, security audits,
compliance checks, and dashboard analysis using OpenAI's Responses API.

Author: EQ12 GODSTACK Team
Version: 1.0.0
License: MIT
"""

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path

from eq12_openai_governance import EQ12GovernanceAI, EQ12OpenAIClient


class EQ12GovernanceAssistant:
    """Interactive conversational AI for EQ12 governance operations."""

    def __init__(self):
        self.client = EQ12OpenAIClient()
        self.governance_ai = EQ12GovernanceAI(self.client)
        self.active_conversations: dict[str, str] = {}

    async def start_governance_session(self, task_type: str = "general") -> str:
        """Start a new conversational governance session."""
        context = {
            "session_type": task_type,
            "eq12_root": str(self.client.eq12_root),
            "timestamp": datetime.now().isoformat(),
            "capabilities": [
                "code_review",
                "security_audit",
                "compliance_check",
                "dashboard_analysis",
            ],
        }

        conversation_id = await self.client.create_governance_conversation(task_type, context)
        self.active_conversations[task_type] = conversation_id

        return conversation_id

    async def ask_governance_question(self, question: str, task_type: str = "general") -> str:
        """Ask the AI assistant a governance-related question."""

        # Get or create conversation
        if task_type not in self.active_conversations:
            await self.start_governance_session(task_type)

        conversation_id = self.active_conversations[task_type]

        # Analyze with context
        context_data = {
            "question": question,
            "task_type": task_type,
            "conversation_id": conversation_id,
            "eq12_context": self._gather_eq12_context(),
        }

        insight = await self.client.analyze_governance_data(
            task_type, context_data, conversation_id
        )

        return self._format_ai_response(insight)

    def _gather_eq12_context(self) -> dict:
        """Gather current EQ12 system context."""
        context = {}

        # Check key directories
        eq12_dirs = ["scripts", "logs", "configs", "tasks", "reports"]
        for dir_name in eq12_dirs:
            dir_path = self.client.eq12_root / dir_name
            context[f"{dir_name}_exists"] = dir_path.exists()
            if dir_path.exists():
                context[f"{dir_name}_files"] = len(list(dir_path.glob("*")))

        # Check Chrome governance status
        chrome_profile = Path.home() / "AppData/Local/Google/Chrome/User Data/EQ12Governance"
        context["chrome_profile_exists"] = chrome_profile.exists()

        if chrome_profile.exists():
            bookmarks_file = chrome_profile / "Default/Bookmarks"
            context["chrome_bookmarks_exist"] = bookmarks_file.exists()

        return context

    def _format_ai_response(self, insight) -> str:
        """Format AI insight for conversational display."""
        response = f"🤖 **{insight.title}**\n\n"
        response += f"{insight.description}\n\n"

        if insight.recommendations:
            response += "💡 **Recommendations:**\n"
            for i, rec in enumerate(insight.recommendations, 1):
                response += f"{i}. {rec}\n"

        response += f"\n📊 Confidence: {insight.confidence:.1%}"
        response += f" | ⚠️ Severity: {insight.severity.upper()}"

        return response


def main():
    """Interactive governance assistant CLI."""
    parser = argparse.ArgumentParser(
        description="EQ12 GODSTACK Conversational AI Governance Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python eq12_governance_assistant.py --interactive
  python eq12_governance_assistant.py --question "How secure is my Chrome profile?"
  python eq12_governance_assistant.py --code-review --file "chrome_governance_automation.py"
        """,
    )

    parser.add_argument(
        "--interactive", action="store_true", help="Start interactive conversation mode"
    )
    parser.add_argument("--question", type=str, help="Ask a specific governance question")
    parser.add_argument(
        "--task-type",
        type=str,
        default="general",
        choices=[
            "general",
            "security_audit",
            "code_review",
            "compliance_check",
            "daily_governance",
        ],
        help="Type of governance task",
    )
    parser.add_argument("--code-review", action="store_true", help="Perform AI code review")
    parser.add_argument("--file", type=str, help="File to analyze for code review")

    args = parser.parse_args()

    async def run_assistant():
        try:
            assistant = EQ12GovernanceAssistant()

            if args.interactive:
                print("🤖 EQ12 Governance Assistant - Interactive Mode")
                print("Type 'exit' to quit, 'help' for commands")
                print("=" * 50)

                while True:
                    try:
                        question = input("\n🎯 Governance Question: ").strip()

                        if question.lower() in ["exit", "quit", "q"]:
                            break
                        if question.lower() == "help":
                            print("\n📋 Available Commands:")
                            print("- Ask any governance question")
                            print(
                                "- 'switch <task_type>' - Change context (security_audit, code_review, etc.)"
                            )
                            print("- 'status' - Show EQ12 system status")
                            print("- 'exit' - Quit assistant")
                            continue
                        if question.lower().startswith("switch "):
                            new_task = question.split(" ", 1)[1]
                            if new_task in [
                                "security_audit",
                                "code_review",
                                "compliance_check",
                                "daily_governance",
                            ]:
                                args.task_type = new_task
                                print(f"✅ Switched to {new_task} mode")
                            else:
                                print(
                                    "❌ Invalid task type. Use: security_audit, code_review, compliance_check, daily_governance"
                                )
                            continue
                        if question.lower() == "status":
                            context = assistant._gather_eq12_context()
                            print("\n📊 EQ12 System Status:")
                            for key, value in context.items():
                                print(f"  {key}: {value}")
                            continue

                        if question:
                            print("\n🤔 Analyzing...")
                            response = await assistant.ask_governance_question(
                                question, args.task_type
                            )
                            print(f"\n{response}")

                    except KeyboardInterrupt:
                        break
                    except Exception as e:
                        print(f"\n❌ Error: {e}")

                print("\n👋 Governance Assistant session ended")

            elif args.question:
                print("🤖 EQ12 Governance Assistant - Single Question Mode")
                print(f"📝 Question: {args.question}")
                print(f"🎯 Task Type: {args.task_type}")
                print("=" * 50)

                response = await assistant.ask_governance_question(args.question, args.task_type)
                print(f"\n{response}")

            elif args.code_review:
                print("🤖 EQ12 Governance Assistant - Code Review Mode")

                if not args.file:
                    print("❌ Please specify a file to review with --file")
                    return 1

                file_path = Path(args.file)
                if not file_path.exists():
                    print(f"❌ File not found: {file_path}")
                    return 1

                # Read file content for review
                with open(file_path, encoding="utf-8") as f:
                    file_content = f.read()

                review_question = f"Please perform a comprehensive code review of this EQ12 file:\n\nFile: {file_path}\nContent:\n{file_content[:2000]}..."

                response = await assistant.ask_governance_question(review_question, "code_review")
                print(f"\n{response}")

            else:
                print("❌ Please specify --interactive, --question, or --code-review")
                return 1

        except Exception as e:
            print(f"❌ Governance Assistant failed: {e}")
            return 1

        return 0

    return asyncio.run(run_assistant())


if __name__ == "__main__":
    sys.exit(main())
