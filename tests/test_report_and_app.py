from pathlib import Path

from streamlit.testing.v1 import AppTest

from coach.feedback import validate_feedback
from coach.questions import QUESTION_BANK
from coach.report import history_to_csv
from tests.test_feedback import GOOD


def test_csv_excludes_answers_and_blocks_formulas():
    history = [{"role": "ML Engineer", "question": "=HYPERLINK(\"x\")",
                "scores": validate_feedback(GOOD)}]
    csv_text = history_to_csv(history)
    assert "'=HYPERLINK" in csv_text
    assert "answer" not in csv_text.splitlines()[0]


def test_question_bank_has_no_empty_categories():
    for categories in QUESTION_BANK.values():
        for questions in categories.values():
            assert questions and all(q.strip() for q in questions)


def test_app_loads_and_shows_a_question():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=30).run()
    assert not app.exception
    app.button[0].click().run()
    assert app.session_state.current_question is not None
