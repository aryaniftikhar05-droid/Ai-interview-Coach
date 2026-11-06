from pathlib import Path

from streamlit.testing.v1 import AppTest

from coach.demo import demo_feedback
from coach.feedback import CRITERIA

WEAK = "I think you basically use a model and stuff and it kind of works fine."
STRONG = (
    "First, I would define the metric, because accuracy hides class imbalance. "
    "Then I would compare precision and recall on a held-out set. For example, in my "
    "project on fraud detection I used XGBoost and improved recall from 61% to 78% "
    "while keeping precision above 70%. However, there is a trade-off: more alerts "
    "cost analyst time. Finally, I would monitor drift weekly with Evidently and "
    "retrain when the PSI goes above 0.2. In summary, pick the metric the business "
    "pays for, test it honestly, and watch it in production."
)


def test_demo_feedback_is_valid_and_complete():
    result = demo_feedback("Q?", STRONG, "Technical")
    for field in CRITERIA:
        assert 1 <= result[field] <= 10
    assert result["overall_score"] > 0
    assert result["follow_up_question"].endswith("?")


def test_stronger_answer_scores_higher():
    weak = demo_feedback("Q?", WEAK)
    strong = demo_feedback("Q?", STRONG)
    assert strong["overall_score"] > weak["overall_score"]
    assert strong["examples_score"] > weak["examples_score"]


def test_weak_answer_gets_a_useful_gap():
    result = demo_feedback("Q?", WEAK)
    assert result["hire_decision"] in ("NO", "BORDERLINE")
    assert result["critical_gap"]


def test_app_gives_demo_feedback_without_a_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    app = AppTest.from_file(
        str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30
    ).run()
    app.button[0].click().run()
    app.text_area(key="answer").input(STRONG).run()
    next(b for b in app.button if b.label == "Submit for feedback").click().run()
    assert not app.exception
    assert not app.error
    assert app.session_state.latest_feedback["mode"] == "demo"
    assert len(app.session_state.history) == 1
