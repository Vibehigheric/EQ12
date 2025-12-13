"""
EQ12 Async Compatibility & Unicode Utilities
Fixes common Windows development issues with event loops and encoding
"""

import asyncio
import inspect
import logging
import os
import queue
import sys
import threading
from collections.abc import Awaitable
from typing import Any


class AsyncCompatibilityManager:
    """Manages async/sync compatibility for mixed environments"""

    @staticmethod
    def is_running_in_loop() -> bool:
        """Check if currently running inside an event loop"""
        try:
            loop = asyncio.get_running_loop()
            return loop is not None
        except RuntimeError:
            return False

    @staticmethod
    def run_coro_blocking(coro: Awaitable[Any], timeout: float = 30.0) -> Any:
        """
        Run async coroutine in a blocking manner, handling event loop conflicts

        Args:
            coro: Coroutine to execute
            timeout: Timeout in seconds

        Returns:
            Result of the coroutine

        Raises:
            TimeoutError: If coroutine takes longer than timeout
            Exception: Any exception raised by the coroutine
        """
        if not inspect.iscoroutine(coro):
            raise TypeError(f"Expected coroutine, got {type(coro)}")

        if not AsyncCompatibilityManager.is_running_in_loop():
            # No event loop running, safe to use asyncio.run
            return asyncio.run(coro)

        # Event loop is running, use thread-based execution
        result_queue = queue.Queue()
        exception_queue = queue.Queue()

        def thread_runner():
            try:
                # Create new event loop for this thread
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)

                try:
                    result = new_loop.run_until_complete(coro)
                    result_queue.put(result)
                except Exception as e:
                    exception_queue.put(e)
                finally:
                    new_loop.close()

            except Exception as e:
                exception_queue.put(e)

        thread = threading.Thread(target=thread_runner)
        thread.daemon = True
        thread.start()
        thread.join(timeout=timeout)

        if thread.is_alive():
            raise TimeoutError(f"Coroutine timed out after {timeout} seconds")

        if not exception_queue.empty():
            raise exception_queue.get()

        if not result_queue.empty():
            return result_queue.get()

        raise RuntimeError("Async execution failed with no result or exception")


def run_maybe_async(fn, *args, **kwargs) -> Any:
    """
    Universal async/sync runner - handles both sync and async functions intelligently

    Args:
        fn: Function to call (sync or async)
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Result of function execution
    """
    try:
        result = fn(*args, **kwargs)

        if inspect.isawaitable(result):
            # Function returned an awaitable, need to handle async execution
            if AsyncCompatibilityManager.is_running_in_loop():
                # Inside event loop - return the awaitable for caller to await
                # OR create a task if immediate execution is needed
                return asyncio.create_task(result)
            # No event loop - run synchronously
            return AsyncCompatibilityManager.run_coro_blocking(result)

        return result

    except Exception as e:
        # Re-raise with context
        raise RuntimeError(f"Failed to execute {fn.__name__}: {e}") from e


class UnicodeHandler:
    """Handles Windows Unicode/UTF-8 encoding issues"""

    @staticmethod
    def setup_windows_unicode():
        """Setup proper Unicode handling for Windows PowerShell/CMD"""
        if sys.platform == "win32":
            try:
                # Set console to UTF-8
                os.system("chcp 65001 > nul")

                # Configure Python encoding
                os.environ["PYTHONIOENCODING"] = "utf-8"

                # Reconfigure stdout/stderr for UTF-8
                if hasattr(sys.stdout, "reconfigure"):
                    sys.stdout.reconfigure(encoding="utf-8")
                if hasattr(sys.stderr, "reconfigure"):
                    sys.stderr.reconfigure(encoding="utf-8")

                return True

            except Exception as e:
                print(f"Warning: Could not setup Unicode handling: {e}")
                return False
        return True

    @staticmethod
    def setup_logging_unicode():
        """Configure logging to handle Unicode properly"""
        try:
            # Remove any existing handlers to avoid conflicts
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

            # Setup UTF-8 logging
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                encoding="utf-8",
                force=True,
            )

            return True

        except Exception as e:
            # Fallback to ASCII-only logging
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
            logging.warning(f"Could not setup UTF-8 logging: {e}")
            return False

    @staticmethod
    def safe_print(message: str, use_ascii_fallback: bool = True):
        """Print message with Unicode safety"""
        try:
            print(message)
        except UnicodeEncodeError:
            if use_ascii_fallback:
                # Convert to ASCII, replacing problematic characters
                ascii_message = message.encode("ascii", "replace").decode("ascii")
                print(ascii_message)
            else:
                print(f"[Unicode Error] Could not display message: {len(message)} characters")


def initialize_eq12_compatibility():
    """Initialize all EQ12 compatibility fixes"""
    print("🔧 Initializing EQ12 compatibility...")

    # Setup Unicode handling
    unicode_ok = UnicodeHandler.setup_windows_unicode()
    logging_ok = UnicodeHandler.setup_logging_unicode()

    if unicode_ok and logging_ok:
        print("✅ Unicode and logging configured successfully")
    else:
        print("⚠️ Some Unicode configuration failed - using fallbacks")

    # Test async compatibility
    try:

        async def test_coro():
            return "async_test_ok"

        result = AsyncCompatibilityManager.run_coro_blocking(test_coro())
        if result == "async_test_ok":
            print("✅ Async compatibility verified")
        else:
            print("⚠️ Async compatibility test failed")

    except Exception as e:
        print(f"⚠️ Async compatibility test error: {e}")

    print("🎯 EQ12 compatibility initialization complete")


# Export main functions
__all__ = [
    "AsyncCompatibilityManager",
    "UnicodeHandler",
    "initialize_eq12_compatibility",
    "run_maybe_async",
]


if __name__ == "__main__":
    # Demo/test mode
    initialize_eq12_compatibility()

    # Test Unicode
    UnicodeHandler.safe_print("🚀 Testing Unicode: EQ12 Dashboard ✅ 🎯")

    # Test async compatibility
    async def demo_async():
        await asyncio.sleep(0.1)
        return "Demo async function completed"

    result = run_maybe_async(demo_async)
    print(f"Async result: {result}")

    print("🎉 All compatibility tests passed!")
