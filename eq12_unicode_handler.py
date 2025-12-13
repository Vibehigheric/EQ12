#!/usr/bin/env python3
"""
EQ12 Unicode Handler - Windows terminal compatible emoji display
Handles Windows terminal Unicode display issues for the EQ12 system.
"""

import logging
import sys


class EQ12UnicodeHandler:
    """Windows-compatible Unicode handler for EQ12 display"""

    def __init__(self):
        self.is_windows = sys.platform.startswith("win")
        self.emoji_map = {
            # Sports emojis
            "🏈": "[FB]",
            "🎯": "[TARGET]",
            "💰": "[MONEY]",
            "📊": "[CHART]",
            "🎰": "[SLOT]",
            "⚡": "[BOLT]",
            "⏰": "[CLOCK]",
            "🏪": "[SHOP]",
            "🎫": "[TICKET]",
            "📅": "[CAL]",
            # Analysis emojis
            "🔍": "[SEARCH]",
            "🤖": "[AI]",
            "🧠": "[BRAIN]",
            "💡": "[IDEA]",
            "🛡️": "[SHIELD]",
            "📝": "[NOTE]",
            "⚠️": "[WARN]",
            "✅": "[PASS]",
            "❌": "[FAIL]",
            "📈": "[UP]",
            "📉": "[DOWN]",
            "🚀": "[ROCKET]",
            "💎": "[GEM]",
            # Status emojis
            "🔄": "[REFRESH]",
            "💾": "[SAVE]",
            "🎉": "[PARTY]",
        }

    def clean_text(self, text: str) -> str:
        """Clean text for Windows terminal display"""
        if not self.is_windows:
            return text

        # Replace emojis with Windows-safe alternatives
        for emoji, replacement in self.emoji_map.items():
            text = text.replace(emoji, replacement)

        return text

    def setup_logging(self, logger: logging.Logger) -> None:
        """Setup Windows-compatible logging"""
        if self.is_windows:
            # Create a custom formatter that handles Unicode
            class WindowsFormatter(logging.Formatter):
                def format(self, record):
                    msg = super().format(record)
                    return EQ12UnicodeHandler().clean_text(msg)

            # Apply to all handlers
            for handler in logger.handlers:
                if hasattr(handler, "setFormatter"):
                    handler.setFormatter(
                        WindowsFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
                    )


def safe_print(text: str) -> None:
    """Windows-safe print function"""
    handler = EQ12UnicodeHandler()
    cleaned_text = handler.clean_text(text)

    try:
        print(cleaned_text)
    except UnicodeEncodeError:
        # Fallback to ASCII-only
        ascii_text = cleaned_text.encode("ascii", errors="replace").decode("ascii")
        print(ascii_text)


if __name__ == "__main__":
    # Test the handler
    test_text = "🏈 PARLAY 🎯 TARGET 💰 MONEY 📊 ANALYSIS 🤖 AI READY! ✅"
    print("Original:", test_text)
    print("Cleaned:", EQ12UnicodeHandler().clean_text(test_text))
    safe_print(test_text)
