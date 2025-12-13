#!/usr/bin/env python3
"""
EQ12 Scripts Package
Legacy script compatibility layer and utility functions
"""

# Import commonly used scripts for backwards compatibility
try:
    from .codex_check import main as codex_main
    from .eq12_ai_guardrails import main as guardrails_main
    from .eq12_chatgpt import call_chatgpt
    from .eq12_chatgpt import main as chatgpt_main
except ImportError:
    # Graceful degradation if dependencies are missing
    pass

__all__ = ["call_chatgpt", "chatgpt_main", "codex_main", "guardrails_main"]
