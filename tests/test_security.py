import pytest

from coach.feedback import MAX_QUESTION_CHARS, CoachError, request_feedback
from coach.ratelimit import RateLimiter


def test_rate_limiter_blocks_then_recovers_after_the_window():
    now = [0.0]
    limiter = RateLimiter(max_calls=2, window_seconds=60, clock=lambda: now[0])
    assert limiter.allow() and limiter.allow()
    assert not limiter.allow()
    now[0] = 61
    assert limiter.allow()


def test_overlong_question_is_rejected_before_any_api_call():
    def post(*args, **kwargs):
        raise AssertionError("the API must not be called")

    with pytest.raises(CoachError, match="question is too long"):
        request_feedback("x" * (MAX_QUESTION_CHARS + 1), "an answer", "ML Engineer",
                         api_key="test-key", post=post)
