#!/usr/bin/env python3
"""
EQ12 Async Compatibility Helper
Fixes asyncio.run() issues in mixed sync/async contexts
"""

import asyncio
import builtins
import contextlib
import queue
import threading
from collections.abc import Coroutine
from typing import Any, TypeVar

T = TypeVar("T")


def in_running_loop() -> bool:
    """Check if we're currently inside a running event loop"""
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


def run_coro_blocking[T](coro: Coroutine[Any, Any, T], timeout: float | None = None) -> T:
    """
    Run an async coroutine from synchronous code even if an event loop
    is already running elsewhere (by using a dedicated thread).
    """
    result_queue: queue.Queue[tuple[bool, Any]] = queue.Queue(maxsize=1)

    def _worker():
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(coro)
            result_queue.put((True, result))
        except BaseException as e:
            result_queue.put((False, e))
        finally:
            with contextlib.suppress(builtins.BaseException):
                loop.close()

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()

    try:
        success, value = result_queue.get(timeout=timeout)
        if success:
            return value
        raise value
    finally:
        thread.join(timeout=1.0)  # Give thread time to cleanup


def ensure_future_compat(coro_or_future):
    """Compatibility wrapper for ensure_future across Python versions"""
    try:
        return asyncio.ensure_future(coro_or_future)
    except AttributeError:
        return asyncio.create_task(coro_or_future)


async def run_with_timeout[T](coro: Coroutine[Any, Any, T], timeout: float) -> T:
    """Run coroutine with timeout, compatible across asyncio versions"""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except TimeoutError:
        raise TimeoutError(f"Operation timed out after {timeout} seconds")
