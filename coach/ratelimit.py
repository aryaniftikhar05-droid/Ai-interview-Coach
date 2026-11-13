"""A small in-memory rate limiter.

It protects the app owner's API key: without a limit, a script could send
thousands of requests to a public demo and spend all of the owner's credit
(a "denial of wallet" attack).
"""
import threading
import time
from collections import deque


class RateLimiter:
    """Allow at most `max_calls` calls in any `window_seconds` period."""

    def __init__(self, max_calls, window_seconds, clock=time.monotonic):
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self._clock = clock
        self._calls = deque()
        # Streamlit runs each visitor in its own thread, so guard shared state.
        self._lock = threading.Lock()

    def allow(self):
        """Record one call and return True, or return False if the limit is reached."""
        now = self._clock()
        with self._lock:
            while self._calls and now - self._calls[0] >= self.window_seconds:
                self._calls.popleft()
            if len(self._calls) >= self.max_calls:
                return False
            self._calls.append(now)
            return True
