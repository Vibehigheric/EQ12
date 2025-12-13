#!/usr/bin/env python3
"""
EQ12 Unified AI Integration System v3.0
Complete integration of enhanced OpenAI API, prompt engineering framework,
conversation management, and advanced features for production deployment.

Features:
- Unified interface for all AI operations
- Advanced error handling and retry logic
- Function calling and tool integration
- Performance monitoring and optimization
- Cost tracking and budget management
- Production-ready deployment patterns

Author: EQ12 GODSTACK Team
Version: 3.0.0
License: MIT
"""

import asyncio
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from eq12_conversation_manager import ConversationManager, ConversationRole, MessageType

# Import our enhanced components
from eq12_openai_enhanced_v2 import (
    EQ12OpenAIEnhanced,
    TaskComplexity,
)
from eq12_prompt_engineering_framework import PromptTemplateManager


class EQ12AIOrchestrator:
    """
    Main orchestrator for all EQ12 AI operations.
    Provides unified interface and manages all AI subsystems.
    """

    def __init__(
        self,
        api_key: str | None = None,
        eq12_root: str | None = None,
        budget_limit: float = 100.0,  # Daily budget limit
        enable_memory: bool = True,
    ):
        self.eq12_root = Path(eq12_root or "C:/EQ12")
        self.logs_dir = self.eq12_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)

        self.logger = self._setup_logging()

        # Initialize core components
        self.openai_client = EQ12OpenAIEnhanced(api_key=api_key, eq12_root=eq12_root)
        self.prompt_manager = PromptTemplateManager()
        self.conversation_manager = ConversationManager() if enable_memory else None

        # Budget and cost management
        self.daily_budget = budget_limit
        self.daily_spend = 0.0
        self.budget_reset_date = datetime.now().date()

        # Performance tracking
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "total_tokens": 0,
            "total_cost": 0.0,
        }

        # Active conversations
        self.active_conversations: dict[str, str] = {}  # session_id -> conversation_id

        self.logger.info("🤖 EQ12 AI Orchestrator v3.0 initialized")

    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        log_file = self.logs_dir / f"eq12_ai_orchestrator_{datetime.now().strftime('%Y%m%d')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )

        return logging.getLogger(f"{__name__}.EQ12AIOrchestrator")

    def _check_budget(self, estimated_cost: float) -> bool:
        """Check if request is within budget"""
        # Reset daily budget if new day
        today = datetime.now().date()
        if today > self.budget_reset_date:
            self.daily_spend = 0.0
            self.budget_reset_date = today

        return (self.daily_spend + estimated_cost) <= self.daily_budget

    def _update_metrics(self, success: bool, response_time: float, tokens: int, cost: float):
        """Update performance metrics"""
        self.performance_metrics["total_requests"] += 1

        if success:
            self.performance_metrics["successful_requests"] += 1
        else:
            self.performance_metrics["failed_requests"] += 1

        # Update averages
        total_requests = self.performance_metrics["total_requests"]
        current_avg_time = self.performance_metrics["average_response_time"]
        self.performance_metrics["average_response_time"] = (
            current_avg_time * (total_requests - 1) + response_time
        ) / total_requests

        self.performance_metrics["total_tokens"] += tokens
        self.performance_metrics["total_cost"] += cost
        self.daily_spend += cost

    async def analyze_sports_bet(
        self,
        game_info: str,
        bet_type: str,
        odds: str,
        estimated_probability: float,
        bankroll: float,
        context: str = "",
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Comprehensive sports betting analysis with conversation memory
        """
        start_time = time.time()

        try:
            # Estimate cost first
            estimated_cost = 0.05  # Rough estimate for this operation
            if not self._check_budget(estimated_cost):
                raise ValueError(f"Request would exceed daily budget of ${self.daily_budget}")

            # Use conversation manager if available and session provided
            if self.conversation_manager and session_id:
                # Get or create conversation
                if session_id not in self.active_conversations:
                    conv_id = self.conversation_manager.create_conversation(
                        title=f"Sports Betting Session - {game_info}",
                        metadata={"session_id": session_id, "type": "sports_betting"},
                    )
                    self.active_conversations[session_id] = conv_id
                else:
                    conv_id = self.active_conversations[session_id]

                # Add context to conversation memory
                self.conversation_manager.add_memory(conv_id, "current_bankroll", bankroll)
                self.conversation_manager.add_memory(conv_id, "betting_context", context)

                # Add user query to conversation
                query = f"Analyze: {game_info}, {bet_type}, {odds}, {estimated_probability}% probability"
                self.conversation_manager.add_message(
                    conv_id, ConversationRole.USER, query, MessageType.QUERY
                )

                # Get conversation context for enhanced analysis
                self.conversation_manager.get_conversation_messages(conv_id, limit=10)

            # Perform analysis using enhanced OpenAI client
            analysis = await self.openai_client.analyze_sports_bet(
                game_info=game_info,
                bet_type=bet_type,
                odds=odds,
                estimated_probability=estimated_probability,
                bankroll=bankroll,
                context=context,
            )

            # Add response to conversation if using memory
            if self.conversation_manager and session_id:
                response_text = f"Recommendation: {analysis.recommendation}, EV: {analysis.expected_value:.1f}%, Kelly: {analysis.kelly_fraction:.2%}"
                self.conversation_manager.add_message(
                    conv_id,
                    ConversationRole.ASSISTANT,
                    response_text,
                    MessageType.RESPONSE,
                )

            # Update metrics
            end_time = time.time()
            response_time = end_time - start_time
            tokens_used = 500  # Estimate - would be actual from API response
            actual_cost = 0.025  # Would be actual from API response

            self._update_metrics(True, response_time, tokens_used, actual_cost)

            # Format response
            result = {
                "success": True,
                "analysis": {
                    "recommendation": analysis.recommendation,
                    "confidence": analysis.confidence,
                    "expected_value": analysis.expected_value,
                    "kelly_fraction": analysis.kelly_fraction,
                    "risk_assessment": analysis.risk_assessment,
                    "reasoning": analysis.reasoning,
                    "factors": analysis.factors,
                },
                "metadata": {
                    "response_time": response_time,
                    "tokens_used": tokens_used,
                    "cost": actual_cost,
                    "model_used": "gpt-4o",  # Would be actual model
                    "session_id": session_id,
                },
            }

            self.logger.info(
                f"Sports betting analysis completed: {analysis.recommendation} ({response_time:.2f}s)"
            )
            return result

        except Exception as e:
            # Update error metrics
            end_time = time.time()
            self._update_metrics(False, end_time - start_time, 0, 0)

            self.logger.error(f"Sports betting analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "metadata": {
                    "response_time": end_time - start_time,
                    "session_id": session_id,
                },
            }

    async def review_code(
        self,
        code: str,
        language: str,
        file_path: str = "unknown",
        focus_areas: list[str] | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Comprehensive code review with AI analysis
        """
        start_time = time.time()

        try:
            estimated_cost = 0.03
            if not self._check_budget(estimated_cost):
                raise ValueError(f"Request would exceed daily budget of ${self.daily_budget}")

            # Use enhanced client for code review
            result = await self.openai_client.review_code(
                file_path=file_path,
                language=language,
                code=code,
                context=f"Focus areas: {', '.join(focus_areas or ['general'])}",
            )

            end_time = time.time()
            response_time = end_time - start_time

            self._update_metrics(
                True,
                response_time,
                result["usage"].total_tokens,
                result["usage"].estimated_cost,
            )

            formatted_result = {
                "success": True,
                "review": {
                    "content": result["content"],
                    "model_used": result["model"],
                },
                "metadata": {
                    "response_time": response_time,
                    "tokens_used": result["usage"].total_tokens,
                    "cost": result["usage"].estimated_cost,
                    "file_path": file_path,
                    "language": language,
                    "session_id": session_id,
                },
            }

            self.logger.info(f"Code review completed for {file_path} ({response_time:.2f}s)")
            return formatted_result

        except Exception as e:
            end_time = time.time()
            self._update_metrics(False, end_time - start_time, 0, 0)

            self.logger.error(f"Code review failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "metadata": {
                    "response_time": end_time - start_time,
                    "session_id": session_id,
                },
            }

    async def general_query(
        self,
        query: str,
        context: str = "",
        complexity: TaskComplexity = TaskComplexity.MODERATE,
        session_id: str | None = None,
        response_format: type | None = None,
    ) -> dict[str, Any]:
        """
        General purpose AI query with automatic model selection
        """
        start_time = time.time()

        try:
            estimated_cost = 0.02
            if not self._check_budget(estimated_cost):
                raise ValueError(f"Request would exceed daily budget of ${self.daily_budget}")

            # Prepare messages
            messages = [{"role": "user", "content": f"{query}\n\nContext: {context}"}]

            # Use conversation history if available
            if self.conversation_manager and session_id:
                if session_id not in self.active_conversations:
                    conv_id = self.conversation_manager.create_conversation(
                        title="General Query Session",
                        metadata={"session_id": session_id, "type": "general"},
                    )
                    self.active_conversations[session_id] = conv_id
                else:
                    conv_id = self.active_conversations[session_id]

                # Add to conversation
                self.conversation_manager.add_message(
                    conv_id, ConversationRole.USER, query, MessageType.QUERY
                )

                # Get enriched messages
                messages = self.conversation_manager.get_conversation_messages(conv_id, limit=20)

            # Make API call
            result = await self.openai_client.create_structured_completion(
                messages=messages,
                response_format=response_format,
                complexity=complexity,
            )

            # Add response to conversation
            if self.conversation_manager and session_id:
                self.conversation_manager.add_message(
                    conv_id,
                    ConversationRole.ASSISTANT,
                    str(result["content"]),
                    MessageType.RESPONSE,
                )

            end_time = time.time()
            response_time = end_time - start_time

            self._update_metrics(
                True,
                response_time,
                result["usage"].total_tokens,
                result["usage"].estimated_cost,
            )

            return {
                "success": True,
                "response": result["content"],
                "metadata": {
                    "model_used": result["model"],
                    "response_time": response_time,
                    "tokens_used": result["usage"].total_tokens,
                    "cost": result["usage"].estimated_cost,
                    "session_id": session_id,
                },
            }

        except Exception as e:
            end_time = time.time()
            self._update_metrics(False, end_time - start_time, 0, 0)

            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "metadata": {"session_id": session_id},
            }

    def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status"""
        openai_stats = self.openai_client.get_usage_stats()

        status = {
            "system_info": {
                "version": "3.0.0",
                "uptime": "Active",  # Could track actual uptime
                "eq12_root": str(self.eq12_root),
                "memory_enabled": self.conversation_manager is not None,
            },
            "budget_status": {
                "daily_limit": self.daily_budget,
                "daily_spent": self.daily_spend,
                "remaining_budget": self.daily_budget - self.daily_spend,
                "budget_utilization": (self.daily_spend / self.daily_budget) * 100,
            },
            "performance_metrics": self.performance_metrics,
            "openai_stats": openai_stats,
            "active_conversations": len(self.active_conversations),
            "available_templates": list(self.prompt_manager.templates.keys()),
            "health_status": (
                "healthy" if self.daily_spend < self.daily_budget else "budget_warning"
            ),
        }

        if self.conversation_manager:
            status["conversation_metrics"] = self.conversation_manager.get_metrics()

        return status

    async def test_system_connectivity(self) -> dict[str, Any]:
        """Test all system components"""
        results = {}

        # Test OpenAI connectivity
        try:
            test_results = await self.openai_client.test_models()
            results["openai_models"] = test_results
        except Exception as e:
            results["openai_models"] = {"error": str(e)}

        # Test conversation manager
        if self.conversation_manager:
            try:
                test_conv = self.conversation_manager.create_conversation(title="Test")
                self.conversation_manager.add_message(
                    test_conv, ConversationRole.USER, "Test message", MessageType.QUERY
                )
                results["conversation_manager"] = {"status": "operational"}
            except Exception as e:
                results["conversation_manager"] = {"error": str(e)}

        # Test prompt templates
        try:
            templates = self.prompt_manager.list_templates()
            results["prompt_templates"] = {
                "count": len(templates),
                "status": "operational",
            }
        except Exception as e:
            results["prompt_templates"] = {"error": str(e)}

        return results

    async def shutdown(self):
        """Gracefully shutdown the orchestrator"""
        self.logger.info("Shutting down EQ12 AI Orchestrator...")

        # Save any pending data
        if self.conversation_manager:
            # Conversation data is automatically persisted
            pass

        # Log final statistics
        final_stats = self.get_system_status()
        self.logger.info(f"Final stats: {final_stats['performance_metrics']}")

        self.logger.info("EQ12 AI Orchestrator shutdown complete")


# Production-ready example usage
async def main():
    """Example usage of the unified AI system"""

    # Initialize the orchestrator
    ai = EQ12AIOrchestrator(budget_limit=50.0, enable_memory=True)  # $50 daily budget

    print("🚀 EQ12 Unified AI Integration System v3.0")
    print("=" * 60)

    # System health check
    print("\n🔧 System Status:")
    status = ai.get_system_status()
    print(
        f"Budget: ${status['budget_status']['remaining_budget']:.2f} / ${status['budget_status']['daily_limit']:.2f}"
    )
    print(f"Active conversations: {status['active_conversations']}")
    print(f"Available templates: {len(status['available_templates'])}")

    # Test connectivity
    print("\n📡 Testing connectivity...")
    connectivity = await ai.test_system_connectivity()
    for component, result in connectivity.items():
        if "error" in result:
            print(f"❌ {component}: {result['error']}")
        else:
            print(f"✅ {component}: operational")

    # Example sports betting analysis
    print("\n🎯 Example: Sports Betting Analysis")
    try:
        betting_result = await ai.analyze_sports_bet(
            game_info="Chiefs vs Bills, NFL Week 8",
            bet_type="Moneyline",
            odds="-150",
            estimated_probability=65.0,
            bankroll=1000.0,
            context="Chiefs coming off bye week",
            session_id="demo_session_1",
        )

        if betting_result["success"]:
            analysis = betting_result["analysis"]
            print(f"✅ Recommendation: {analysis['recommendation']}")
            print(f"   Confidence: {analysis['confidence']:.1%}")
            print(f"   Expected Value: {analysis['expected_value']:.1f}%")
            print(f"   Cost: ${betting_result['metadata']['cost']:.4f}")
        else:
            print(f"❌ Analysis failed: {betting_result['error']}")

    except Exception as e:
        print(f"❌ Betting analysis error: {e}")

    # Example code review
    print("\n🔍 Example: Code Review")
    sample_code = """
def calculate_kelly(prob, odds, bankroll):
    if prob <= 0 or prob >= 1:
        return 0
    decimal_odds = abs(odds) / 100 + 1 if odds > 0 else 100 / abs(odds) + 1
    kelly_fraction = (prob * decimal_odds - 1) / (decimal_odds - 1)
    return max(0, min(kelly_fraction * bankroll, bankroll * 0.25))
"""

    try:
        review_result = await ai.review_code(
            code=sample_code,
            language="python",
            file_path="kelly_calculator.py",
            focus_areas=["security", "performance"],
            session_id="demo_session_2",
        )

        if review_result["success"]:
            print("✅ Code review completed")
            print(f"   Cost: ${review_result['metadata']['cost']:.4f}")
            print(f"   Tokens: {review_result['metadata']['tokens_used']}")
        else:
            print(f"❌ Code review failed: {review_result['error']}")

    except Exception as e:
        print(f"❌ Code review error: {e}")

    # Final system status
    print("\n📊 Final System Status:")
    final_status = ai.get_system_status()
    print(f"Total requests: {final_status['performance_metrics']['total_requests']}")
    print(
        f"Success rate: {final_status['performance_metrics']['successful_requests'] / max(1, final_status['performance_metrics']['total_requests']):.1%}"
    )
    print(f"Total cost: ${final_status['performance_metrics']['total_cost']:.4f}")

    # Cleanup
    await ai.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
