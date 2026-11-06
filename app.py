import os
import random

import streamlit as st

from coach.feedback import CoachError, evaluate_answer
from coach.questions import QUESTION_BANK
from coach.report import history_to_csv

st.set_page_config(page_title="AI Interview Coach", page_icon="🎯", layout="wide")


def get_secret(name):
    """Read a value from Streamlit secrets, falling back to an environment variable."""
    try:
        value = st.secrets.get(name)
    except (FileNotFoundError, KeyError):
        value = None
    return value or os.getenv(name)


def set_question(question, role, is_follow_up=False):
    st.session_state.current_question = question
    st.session_state.current_role = role
    st.session_state.is_follow_up = is_follow_up
    st.session_state.latest_feedback = None
    st.session_state.pop("answer", None)


def render_feedback(result):
    st.subheader("Practice feedback")
    columns = st.columns(5)
    labels = [
        ("Structure", "structure_score"),
        ("Depth", "depth_score"),
        ("Examples", "examples_score"),
        ("Communication", "communication_score"),
        ("Weighted overall", "overall_score"),
    ]
    for column, (label, key) in zip(columns, labels):
        column.metric(label, f"{result[key]:g}/10")

    st.caption(
        f"Model-generated practice decision: {result['hire_decision']}. "
        "This is not a real hiring prediction."
    )
    st.markdown("**What went well**")
    st.write(result["what_was_good"])
    st.markdown("**Main gap**")
    st.write(result["critical_gap"])
    st.markdown("**How to improve**")
    st.write(result["model_answer_hint"])
    st.markdown("**Likely follow-up question**")
    st.write(result["follow_up_question"])
    if st.button("Answer this follow-up", key="follow_up"):
        set_question(result["follow_up_question"], st.session_state.current_role, True)
        st.rerun()


st.title("🎯 AI Interview Coach")
st.caption("Practice ML Engineer and Data Scientist interview answers with AI feedback.")
st.info(
    "Your answer is sent to Anthropic to generate feedback. Do not enter passwords, "
    "private personal information, or confidential material."
)

for key, default in (
    ("current_question", None),
    ("current_role", "ML Engineer"),
    ("is_follow_up", False),
    ("history", []),
    ("latest_feedback", None),
):
    if key not in st.session_state:
        st.session_state[key] = default

practice_tab, dashboard_tab, bank_tab = st.tabs(["Practice", "Progress", "Question bank"])

with practice_tab:
    left, right = st.columns([1, 2])
    with left:
        role = st.selectbox("Target role", list(QUESTION_BANK))
        category = st.selectbox("Question type", list(QUESTION_BANK[role]))
        if st.button("Get a random question", type="primary", use_container_width=True):
            set_question(random.choice(QUESTION_BANK[role][category]), role)

        with st.expander("Use your own question"):
            custom = st.text_area(
                "Paste a question from a real job advert or past interview",
                key="custom_question",
                height=100,
            )
            if st.button("Practise this question", use_container_width=True):
                if len(custom.split()) < 4:
                    st.warning("Please enter a full question.")
                else:
                    set_question(custom.strip(), role)

    with right:
        if st.session_state.current_question:
            if st.session_state.is_follow_up:
                st.caption("Follow-up question")
            st.markdown(f"### {st.session_state.current_question}")
            answer = st.text_area(
                "Your answer",
                height=200,
                key="answer",
                placeholder=(
                    "Write a complete answer. For behavioural questions, explain the "
                    "situation, your action, and the result."
                ),
            )
            submit_column, new_column = st.columns(2)
            submit = submit_column.button(
                "Submit for feedback", type="primary", use_container_width=True
            )
            if new_column.button("Clear question", use_container_width=True):
                st.session_state.current_question = None
                st.session_state.latest_feedback = None
                st.rerun()

            if submit:
                if len(answer.split()) < 10:
                    st.warning("Please write at least 10 words so there is enough to evaluate.")
                else:
                    with st.spinner("Generating feedback..."):
                        try:
                            result = evaluate_answer(
                                st.session_state.current_question,
                                answer,
                                st.session_state.current_role,
                                api_key=get_secret("ANTHROPIC_API_KEY"),
                                model=get_secret("ANTHROPIC_MODEL"),
                            )
                            st.session_state.history.append({
                                "question": st.session_state.current_question,
                                "scores": result,
                                "role": st.session_state.current_role,
                            })
                            st.session_state.latest_feedback = result
                        except CoachError as exc:
                            st.error(str(exc))

            if st.session_state.latest_feedback:
                render_feedback(st.session_state.latest_feedback)
        else:
            st.info(
                "Choose a role and question type, then select Get a random question, "
                "or paste your own question."
            )

with dashboard_tab:
    st.subheader("Practice history")
    history = st.session_state.history
    if not history:
        st.info("Complete a practice question to see your session history.")
    else:
        scores = [item["scores"]["overall_score"] for item in history]
        first, second, third = st.columns(3)
        first.metric("Answers submitted", len(history))
        second.metric("Average weighted score", f"{sum(scores) / len(scores):.1f}/10")
        third.metric("Best weighted score", f"{max(scores):.1f}/10")

        if len(history) > 1:
            st.markdown("**Score by criterion over this session**")
            st.line_chart({
                "Structure": [h["scores"]["structure_score"] for h in history],
                "Depth": [h["scores"]["depth_score"] for h in history],
                "Examples": [h["scores"]["examples_score"] for h in history],
                "Communication": [h["scores"]["communication_score"] for h in history],
            })

        st.download_button(
            "Download session report (CSV)",
            data=history_to_csv(history),
            file_name="interview_practice_history.csv",
            mime="text/csv",
        )

        for index, item in enumerate(reversed(history[-5:]), start=1):
            st.markdown(f"**Recent answer {index} · {item['role']}**")
            st.write(item["question"])
            st.write(
                f"Weighted score: {item['scores']['overall_score']:.1f}/10 · "
                f"Practice decision: {item['scores']['hire_decision']}"
            )
    st.caption("History is stored only in this Streamlit session and is not saved permanently.")

with bank_tab:
    st.subheader("Question bank")
    for role_name, categories in QUESTION_BANK.items():
        with st.expander(role_name):
            for category_name, questions in categories.items():
                st.markdown(f"**{category_name}**")
                for question in questions:
                    st.write(f"• {question}")
