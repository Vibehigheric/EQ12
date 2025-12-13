#!/usr/bin/env python3
"""
EQ12 GPT-5 URL System Manager
Enhanced management script with GPT-5 integration testing and configuration

Author: EQ12 AI System
Version: 2.0.0 - GPT-5 Enhanced
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

try:
    from eq12_enhanced_ai import EQ12EnhancedAI
    from eq12_url_scanner import EQ12URLScanner

    AI_AVAILABLE = True
except ImportError as e:
    AI_AVAILABLE = False
    print(f"Warning: AI modules not available: {e}")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/gpt5_url_manager.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class GPT5URLSystemManager:
    """Enhanced URL system manager with GPT-5 support"""

    def __init__(self):
        self.config_file = "C:/EQ12/configs/ai_enhanced_config.json"
        self.ai_system = None
        self.url_scanner = None
        self._init_systems()

    def _init_systems(self):
        """Initialize AI systems"""
        if AI_AVAILABLE:
            try:
                self.ai_system = EQ12EnhancedAI(self.config_file)
                self.url_scanner = EQ12URLScanner()
                logger.info("AI systems initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize AI systems: {e}")
        else:
            logger.warning("AI systems not available")

    def test_gpt5_availability(self) -> dict:
        """Test GPT-5 and advanced model availability"""
        print("🧠 Testing GPT-5 and Advanced AI Models...")
        print("=" * 50)

        if not self.ai_system:
            print("❌ AI system not available")
            return {"status": "failed", "reason": "AI system not initialized"}

        try:
            # Test connection and model availability
            test_result = self.ai_system.test_gpt5_connection()

            print("📊 Connection Test Results:")
            print(f"  OpenAI Available: {test_result.get('openai_available', False)}")
            print(
                f"  Client Initialized: {
                    test_result.get(
                        'client_initialized',
                        False)}")
            print(f"  API Key Set: {test_result.get('api_key_set', False)}")
            print(f"  Selected Model: {test_result.get('selected_model', 'unknown')}")
            print(f"  GPT-5 Available: {test_result.get('gpt5_available', False)}")
            print(f"  o1 Models Available: {test_result.get('o1_available', False)}")

            # Display available models
            available_models = test_result.get("available_models", [])
            print(f"\n🎯 Available Models ({len(available_models)}):")
            for model in available_models:
                if "gpt-5" in model:
                    print(f"  🎉 {model} (GPT-5!)")
                elif "o1" in model:
                    print(f"  🧠 {model} (Reasoning Model)")
                elif "gpt-4" in model:
                    print(f"  ✅ {model} (GPT-4)")
                else:
                    print(f"  📝 {model}")

            # API test result
            api_test = test_result.get("api_test", "not tested")
            if api_test == "success":
                print(f"\n✅ API Test: {api_test}")
                print(f"  Response: {test_result.get('test_response', 'N/A')}")
            else:
                print(f"\n⚠️ API Test: {api_test}")

            return test_result

        except Exception as e:
            print(f"❌ GPT-5 test failed: {e}")
            return {"status": "error", "error": str(e)}

    async def enhanced_url_test(self, url: str) -> dict:
        """Test URL scanning with GPT-5 enhanced analysis"""
        print("\n🔍 Enhanced URL Analysis with GPT-5...")
        print(f"URL: {url}")
        print("=" * 50)

        if not self.ai_system:
            print("❌ AI system not available")
            return {"status": "failed", "reason": "AI system not available"}

        try:
            # Simulate content extraction (simplified for demo)
            test_content = """
            This is a test analysis of {url}.
            The system will classify this content using advanced AI models
            including GPT-5 for enhanced understanding and categorization.
            """

            # Use enhanced AI classification
            result = await self.ai_system.enhanced_classify_content(
                content=test_content, url=url, context="GPT-5 URL Manager Test"
            )

            print("📊 Enhanced Analysis Results:")
            print(f"  Category: {result.category}")
            print(f"  Confidence: {result.confidence:.2%}")
            print(f"  Model Used: {result.model_used}")
            print(f"  Processing Time: {result.processing_time:.2f}s")
            print(f"  EQ12 Relevance: {result.eq12_relevance:.2%}")

            print("\n🧠 AI Reasoning:")
            print(f"  {result.reasoning}")

            if result.key_features:
                print("\n🔑 Key Features Identified:")
                for feature in result.key_features:
                    print(f"    - {feature}")

            if result.suggested_actions:
                print("\n💡 Suggested Actions:")
                for action in result.suggested_actions:
                    print(f"    - {action}")

            return {"status": "success", "analysis": result.__dict__}

        except Exception as e:
            print(f"❌ Enhanced URL test failed: {e}")
            return {"status": "error", "error": str(e)}

    def configure_gpt5_settings(self, model: str | None = None):
        """Configure GPT-5 and AI settings"""
        print("⚙️ Configuring GPT-5 Settings...")
        print("=" * 40)

        # Set environment variables
        if model:
            os.environ["EQ12_OPENAI_MODEL"] = model
            print(f"✅ Set preferred model: {model}")

        # Display current configuration
        current_model = os.getenv("EQ12_OPENAI_MODEL", "auto-detect")
        api_key_set = "✅ Set" if os.getenv("OPENAI_API_KEY") else "❌ Not Set"

        print("\n📋 Current Configuration:")
        print(f"  Preferred Model: {current_model}")
        print(f"  OpenAI API Key: {api_key_set}")
        print(f"  Config File: {self.config_file}")

        # Load and display config file settings
        try:
            with open(self.config_file) as f:
                config = json.load(f)
                ai_config = config.get("ai_configuration", {})
                openai_settings = ai_config.get("openai_settings", {})

                print("\n📄 Configuration File Settings:")
                print(
                    f"  Preferred Model: {
                        openai_settings.get(
                            'preferred_model',
                            'N/A')}")
                fallback_models = openai_settings.get("fallback_models", [])
                if fallback_models:
                    print(f"  Fallback Models: {', '.join(fallback_models)}")

        except FileNotFoundError:
            print(f"\n⚠️ Configuration file not found: {self.config_file}")
        except Exception as e:
            print(f"\n❌ Error reading configuration: {e}")

    def show_gpt5_usage_guide(self):
        """Display GPT-5 usage guide and examples"""
        print("📖 GPT-5 Enhanced URL System Usage Guide")
        print("=" * 50)

        print("\n🎯 Available Models (in preference order):")
        models = [
            ("gpt-5", "Latest GPT-5 model (when available)"),
            ("o1-preview", "Advanced reasoning model"),
            ("gpt-4-turbo-preview", "GPT-4 Turbo with latest features"),
            ("gpt-4", "Standard GPT-4 model"),
            ("o1-mini", "Fast reasoning model"),
            ("gpt-3.5-turbo", "Fallback model"),
        ]

        for model, description in models:
            print(f"  {model}: {description}")

        print("\n⚙️ Configuration Options:")
        print("  Environment Variables:")
        print("    EQ12_OPENAI_MODEL     - Override model selection")
        print("    OPENAI_API_KEY        - Required for AI features")
        print("    EQ12_AI_LOG_LEVEL     - Set logging level")

        print("\n📝 Usage Examples:")
        print("  # Test GPT-5 availability")
        print("  python scripts/eq12_gpt5_manager.py --test-gpt5")
        print()
        print("  # Test enhanced URL analysis")
        print("  python scripts/eq12_gpt5_manager.py --enhanced-test https://fastapi.tiangolo.com")
        print()
        print("  # Configure specific model")
        print("  python scripts/eq12_gpt5_manager.py --configure --model gpt-5")
        print()
        print("  # Set environment variable")
        print("  $env:EQ12_OPENAI_MODEL='gpt-5'")

        print("\n💡 Tips:")
        print("  - GPT-5 provides more accurate content classification")
        print("  - o1-preview excels at complex reasoning tasks")
        print("  - System automatically falls back to available models")
        print("  - Enhanced prompting improves classification accuracy")


async def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(
        description="EQ12 GPT-5 Enhanced URL System Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python eq12_gpt5_manager.py --test-gpt5
  python eq12_gpt5_manager.py --enhanced-test https://fastapi.tiangolo.com
  python eq12_gpt5_manager.py --configure --model gpt-5
  python eq12_gpt5_manager.py --usage-guide
        """,
    )

    parser.add_argument(
        "--test-gpt5", action="store_true", help="Test GPT-5 and model availability"
    )
    parser.add_argument(
        "--enhanced-test",
        type=str,
        metavar="URL",
        help="Test enhanced URL analysis with GPT-5",
    )
    parser.add_argument(
        "--configure",
        action="store_true",
        help="Configure GPT-5 settings")
    parser.add_argument(
        "--model",
        type=str,
        help="Set preferred model (use with --configure)")
    parser.add_argument(
        "--usage-guide",
        action="store_true",
        help="Show GPT-5 usage guide")

    args = parser.parse_args()

    # Initialize manager
    manager = GPT5URLSystemManager()

    try:
        if args.test_gpt5:
            result = manager.test_gpt5_availability()
            if result.get("gpt5_available"):
                print("\n🎉 GPT-5 is available and ready to use!")
            elif "gpt-4" in result.get("selected_model", ""):
                print("\n✅ GPT-4 is available as a powerful alternative")
            else:
                print("\n📝 Standard GPT models are available")

        elif args.enhanced_test:
            result = await manager.enhanced_url_test(args.enhanced_test)
            if result["status"] == "success":
                print("\n🎉 Enhanced URL analysis completed successfully!")
            else:
                print(f"\n❌ Analysis failed: {result.get('reason', 'Unknown error')}")

        elif args.configure:
            manager.configure_gpt5_settings(args.model)
            print("\n✅ Configuration updated!")

        elif args.usage_guide:
            manager.show_gpt5_usage_guide()

        else:
            # Default: show status
            print("🧠 EQ12 GPT-5 Enhanced URL System Manager")
            print("=" * 45)

            result = manager.test_gpt5_availability()

            if result.get("openai_available") and result.get("api_key_set"):
                model = result.get("selected_model", "unknown")
                print(f"\n✅ System Ready with model: {model}")

                if result.get("gpt5_available"):
                    print("🎉 GPT-5 is available!")
                elif "gpt-4" in model:
                    print("✅ Using GPT-4 (excellent performance)")

                print("\nTo test enhanced analysis:")
                print(f"  python {__file__} --enhanced-test https://example.com")
            else:
                print("\n⚠️ OpenAI API not configured")
                print("Set OPENAI_API_KEY environment variable to enable AI features")

            print(f"\nFor help: python {__file__} --help")

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
