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


def test_off_topic_answer_is_capped():
    question = "How do you handle class imbalance when evaluating a fraud model?"
    on_topic = demo_feedback(question, STRONG)
    off_topic = demo_feedback("What is RLHF and why does it matter for LLMs?", STRONG)
    assert off_topic["depth_score"] <= 3
    assert "does not seem to address" in off_topic["critical_gap"]
    assert on_topic["overall_score"] > off_topic["overall_score"]


def test_relevance_matches_word_forms():
    from coach.demo import relevance
    assert relevance("Explain overfitting in models", "My model was overfitting, so I...") == 1.0


JOB = (
    "ML Engineer. Requirements: Python, SQL, XGBoost, Docker, AWS, A/B testing, "
    "model monitoring for drift, and explaining results to non-technical stakeholders."
)


def test_job_advert_skills_and_questions():
    from coach.questions import questions_for_job, skills_in_job_advert
    skills = skills_in_job_advert(JOB)
    assert {"Python", "SQL", "Gradient boosting", "A/B testing"} <= set(skills)
    picks = questions_for_job(JOB)
    questions = [p[0] for p in picks]
    assert len(questions) == len(set(questions))  # no duplicates
    assert any("gradient boosting" in q.lower() for q in questions)
    assert any("SQL" in q for q in questions)  # skill without a bank question
    assert skills_in_job_advert("We sell shoes and need a cashier.") == []


def test_app_job_advert_flow():
    app = AppTest.from_file(
        str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30
    ).run()
    app.text_area(key="job_text").input(JOB).run()
    next(b for b in app.button if b.key == "job_q_0").click().run()
    assert not app.exception
    assert app.session_state.current_question


def test_checklist_reflects_answer_quality():
    from coach.demo import answer_checklist
    question = "How do you handle class imbalance when evaluating a fraud model?"
    strong = dict((label.split(" (")[0], ok) for label, ok in answer_checklist(question, STRONG))
    weak = answer_checklist(question, WEAK)
    assert all(strong.values())
    assert sum(ok for _, ok in weak) <= 1


def test_job_advert_matches_whole_words_only():
    from coach.questions import skills_in_job_advert
    # "rag" is inside "average", "aws" inside "laws", "demand" inside "demanding".
    assert skills_in_job_advert(
        "We leverage storage to average data, comply with laws and keep a demanding, "
        "asterisk-free schedule."
    ) == []
    found = set(skills_in_job_advert(
        "RAG and LLMs on AWS; A/B tests, pipelines, forecasting, containers, statistical models."
    ))
    assert {"Transformers / LLMs", "a cloud platform (AWS, GCP or Azure)", "A/B testing",
            "Data pipelines", "Forecasting", "Docker / Kubernetes", "Statistics"} <= found


def test_like_is_not_counted_as_a_filler_word():
    plain = "Boosted trees such as XGBoost fit residuals step by step and handle missing values well."
    with_like = plain.replace("such as", "like")
    assert demo_feedback("Q?", with_like)["communication_score"] == \
        demo_feedback("Q?", plain)["communication_score"]


def test_demo_decision_matches_weighted_score():
    from coach.feedback import decision_for
    for answer in (WEAK, STRONG):
        result = demo_feedback("Q?", answer)
        assert result["hire_decision"] == decision_for(result["overall_score"])
