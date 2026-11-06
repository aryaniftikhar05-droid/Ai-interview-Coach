import pytest
import requests

from coach.feedback import (
    CRITERIA, FEEDBACK_TOOL, CoachError, evaluate_answer, validate_feedback, weighted_score,
)

GOOD = {
    "structure_score": 8,
    "depth_score": 6,
    "examples_score": 4,
    "communication_score": 10,
    "what_was_good": "Clear structure.",
    "critical_gap": "No metrics.",
    "model_answer_hint": "Add a concrete example. Quantify the impact.",
    "follow_up_question": "How would you monitor this in production?",
    "hire_decision": "YES",
}


class FakeResponse:
    def __init__(self, payload, status=200):
        self.payload, self.status_code = payload, status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(response=self)

    def json(self):
        return self.payload


def fake_post(payload, status=200, capture=None):
    def post(url, **kwargs):
        if capture is not None:
            capture.update(kwargs)
        return FakeResponse(payload, status)
    return post


def tool_reply(tool_input):
    return {"content": [{"type": "tool_use", "name": "submit_feedback", "input": tool_input}]}


def test_weights_sum_to_one():
    assert sum(CRITERIA.values()) == pytest.approx(1.0)


def test_weighted_score_is_calculated_locally():
    # 8*.25 + 6*.30 + 4*.25 + 10*.20 = 6.8
    assert validate_feedback(GOOD)["overall_score"] == 6.8
    assert weighted_score({f: 10 for f in CRITERIA}) == 10.0


@pytest.mark.parametrize("bad", [0, 11, "7", True, None])
def test_invalid_scores_are_rejected(bad):
    with pytest.raises(CoachError):
        validate_feedback({**GOOD, "depth_score": bad})


@pytest.mark.parametrize("field", ["what_was_good", "follow_up_question"])
def test_empty_text_is_rejected(field):
    with pytest.raises(CoachError):
        validate_feedback({**GOOD, field: "  "})


def test_unknown_decision_is_rejected():
    with pytest.raises(CoachError):
        validate_feedback({**GOOD, "hire_decision": "MAYBE"})


def test_request_forces_the_feedback_tool():
    sent = {}
    result = evaluate_answer("Q?", "An answer", "ML Engineer", api_key="k",
                             model="test-model", post=fake_post(tool_reply(GOOD), capture=sent))
    body = sent["json"]
    assert body["tool_choice"] == {"type": "tool", "name": FEEDBACK_TOOL["name"]}
    assert body["model"] == "test-model"
    assert sent["headers"]["x-api-key"] == "k"
    assert result["follow_up_question"] == GOOD["follow_up_question"]


def test_missing_api_key_gives_clear_error():
    with pytest.raises(CoachError, match="API key"):
        evaluate_answer("Q?", "A", "ML Engineer", api_key=None, post=fake_post({}))


def test_text_only_reply_is_rejected():
    reply = {"content": [{"type": "text", "text": "Great answer!"}]}
    with pytest.raises(CoachError, match="did not contain"):
        evaluate_answer("Q?", "A", "ML Engineer", api_key="k", post=fake_post(reply))


@pytest.mark.parametrize("status,message", [(401, "rejected"), (429, "Rate limit"), (500, "error")])
def test_http_errors_become_friendly_messages(status, message):
    with pytest.raises(CoachError, match=message):
        evaluate_answer("Q?", "A", "ML Engineer", api_key="k", post=fake_post({}, status))


def test_timeout_is_reported():
    def post(url, **kwargs):
        raise requests.Timeout()
    with pytest.raises(CoachError, match="timed out"):
        evaluate_answer("Q?", "A", "ML Engineer", api_key="k", post=post)
