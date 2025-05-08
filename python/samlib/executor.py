"""Executor implementation for Python SAMLib.

This module provides the Executor class which manages the execution of agent tasks.
"""
from __future__ import annotations

import asyncio
from typing import Callable, Optional
from concurrent.futures import ThreadPoolExecutor

class Executor:
    """Manages execution of agent tasks in separate threads."""
    
    def __init__(self):
        self._task: Optional[asyncio.Task] = None
        self._thread_pool = ThreadPoolExecutor(max_workers=1)
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        
    def start(self, coro_func: Callable) -> None:
        """Start executing the given coroutine function."""
        def run_loop(loop: asyncio.AbstractEventLoop) -> None:
            asyncio.set_event_loop(loop)
            loop.run_forever()
            
        self._loop = asyncio.new_event_loop()
        self._thread_pool.submit(run_loop, self._loop)
        self._task = asyncio.run_coroutine_threadsafe(coro_func(), self._loop)
    
    def stop(self) -> None:
        """Stop the executor."""
        if self._task:
            self._task.cancel()
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
            
    def join(self) -> None:
        """Wait for the executor to finish."""
        if self._task:
            self._task.result()  # This will raise any exceptions from the task
        self._thread_pool.shutdown(wait=True)
        if self._loop:
            self._loop.close()
