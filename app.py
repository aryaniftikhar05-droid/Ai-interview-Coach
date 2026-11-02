import csv
import io
import json
import os
import random

import requests
import streamlit as st

MODEL = "claude-sonnet-4-20250514"
API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"

st.set_page_config(page_title="AI Interview Coach", page_icon="🎯", layout="wide")

QUESTION_BANK = {
    "ML Engineer": {
        "Technical": [
            "Explain the bias-variance tradeoff and how you would diagnose it in a production model.",
            "You deploy a model and accuracy drops after 2 weeks. Walk me through your debugging process.",
            "What is data leakage and give me a real example of how it could silently destroy a model.",
            "Compare L1 and L2 regularisation. When would you use each?",
            "Explain how gradient boosting works. Why does it often outperform random forests?",
            "You have 10 million training samples and limited RAM. How do you train your model?",
            "What is the difference between bagging and boosting?",
            "How do you handle severely imbalanced classes in a fraud detection problem?",
            "Explain attention mechanisms in transformers in simple terms.",
            "What is RLHF and why does it matter for LLMs?",
        ],
        "System Design": [
            "Design a real-time recommendation system for an e-commerce platform serving 1M users.",
            "How would you build an ML pipeline that automatically retrains when model performance degrades?",
            "Design a feature store for a fintech company processing 100k transactions per second.",
            "Walk me through how you would A/B test two ML models in production.",
            "How would you deploy a large language model to serve 10,000 concurrent users?",
        ],
        "Behavioural": [
            "Tell me about a time your model failed in production. What did you do?",
            "Describe a project where you had to explain a complex ML concept to a non-technical stakeholder.",
            "How do you stay up to date with the latest ML research?",
            "Tell me about a time you had to make a decision with incomplete data.",
        ],
    },
    "Data Scientist": {
        "Technical": [
            "What is the difference between correlation and causation? Give a concrete example.",
            "Explain p-values to a non-statistician. What are their limitations?",
            "You have a dataset with 40% missing values. What do you do?",
            "What is cross-validation and why is k-fold better than a single train-test split?",
            "Explain precision vs recall. When would you optimise for each?",
            "What is the curse of dimensionality and how do you combat it?",
            "How does SHAP work and why is it better than feature importance from a random forest?",
            "Explain the difference between parametric and non-parametric statistical tests.",
        ],
        "Case Study": [
            "A client says their sales dropped 20% last month. How do you investigate this?",
            "You are given a dataset of customer transactions. How would you identify churning customers?",
            "How would you measure the impact of a new product feature on user engagement?",
            "Design an experiment to test whether a new pricing strategy increases revenue.",
        ],
        "Behavioural": [
            "Tell me about the most impactful analysis you have done. What was the business outcome?",
            "Describe a time you disagreed with a stakeholder about data interpretation.",
            "How do you communicate uncertainty in your analysis to business leaders?",
        ],
    },
}

CRITERIA = {
    "structure_score": 0.25,
    "depth_score": 0.30,
    "examples_score": 0.25,
    "communication_score": 0.20,
}
DECISIONS = {"STRONG YES", "YES", "BORDERLINE", "NO"}


class CoachError(Exception):
    """An error that can be shown safely in the app."""


def get_api_key():
    """Read the API key from Streamlit secrets or an environment variable."""
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY")
    except (FileNotFoundError, KeyError):
        key = None
    return key or os.getenv("ANTHROPIC_API_KEY")


def call_claude(system_prompt, user_message):
    api_key = get_api_key()
    if not api_key:
        raise CoachError(
            "Anthropic API key not found. Add ANTHROPIC_API_KEY to "
            ".streamlit/secrets.toml or your environment."
        )

    try:
        response = requests.post(
            API_URL,
            headers={
                "content-type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": API_VERSION,
            },
            json={
                "model": MODEL,
                "max_tokens": 1000,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_message}],
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
    except requests.Timeout as exc:
        raise CoachError("The feedback request timed out. Please try again.") from exc
    except requests.RequestException as exc:
        raise CoachError(
            "Could not reach the Anthropic API. Check your connection and API settings."
        ) from exc
    except ValueError as exc:
        raise CoachError("The API returned a response that could not be read.") from exc

    text_blocks = [
        block.get("text", "")
        for block in data.get("content", [])
        if block.get("type") == "text"
    ]
    if not text_blocks:
        raise CoachError("The API response did not contain interview feedback.")
    return "".join(text_blocks).strip()


def parse_feedback(raw):
    """Parse and validate the model response before displaying it."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```json").removeprefix("```").strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()

    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise CoachError("The model returned invalid feedback. Please try again.") from exc

    if not isinstance(result, dict):
        raise CoachError("The model returned feedback in an unexpected format.")

    validated = {}
    for field in CRITERIA:
        value = result.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 1 <= value <= 10:
            raise CoachError("The model returned an invalid score. Please try again.")
        validated[field] = float(value)

    for field in ("what_was_good", "critical_gap", "model_answer_hint"):
        value = result.get(field)
        if not isinstance(value, str) or not value.strip():
            raise CoachError("The model returned incomplete feedback. Please try again.")
        validated[field] = value.strip()

    decision = result.get("hire_decision")
    if decision not in DECISIONS:
        raise CoachError("The model returned an invalid practice decision. Please try again.")

    validated["overall_score"] = round(
        sum(validated[field] * weight for field, weight in CRITERIA.items()), 1
    )
    validated["hire_decision"] = decision
    return validated


def evaluate_answer(question, answer, role):
    system_prompt = f"""You are a practice interviewer for a {role} candidate.
Evaluate the answer constructively. This is practice feedback, not a real hiring decision.

Score each criterion from 1 to 10:
- Structure (25%): logical flow
- Depth (30%): technical accuracy and depth
- Examples (25%): concrete examples or metrics
- Communication (20%): clarity and conciseness

Return only a JSON object with these exact keys:
{{
  "structure_score": 1,
  "depth_score": 1,
  "examples_score": 1,
  "communication_score": 1,
  "what_was_good": "Specific strengths",
  "critical_gap": "The most important missing point",
  "model_answer_hint": "Two sentences describing a stronger answer",
  "hire_decision": "STRONG YES, YES, BORDERLINE, or NO"
}}"""

    user_message = f"Question: {question}\n\nCandidate answer: {answer}"
    raw = call_claude(system_prompt, user_message)
    return parse_feedback(raw)


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


st.title("🎯 AI Interview Coach")
st.caption("Practice ML Engineer and Data Scientist interview answers with AI feedback.")
st.info(
    "Your answer is sent to Anthropic to generate feedback. Do not enter passwords, "
    "private personal information, or confidential material."
)

for key, default in (
    ("current_question", None),
    ("current_role", "ML Engineer"),
    ("history", []),
    ("latest_feedback", None),
):
    if key not in st.session_state:
        st.session_state[key] = default

practice_tab, dashboard_tab, bank_tab = st.tabs(
    ["Practice", "Progress", "Question bank"]
)

with practice_tab:
    left, right = st.columns([1, 2])
    with left:
        role = st.selectbox("Target role", list(QUESTION_BANK))
        category = st.selectbox("Question type", list(QUESTION_BANK[role]))
        if st.button("Get a random question", type="primary", use_container_width=True):
            st.session_state.current_question = random.choice(QUESTION_BANK[role][category])
            st.session_state.current_role = role
            st.session_state.latest_feedback = None
            st.session_state.pop("answer", None)

    with right:
        if st.session_state.current_question:
            st.markdown(f"### {st.session_state.current_question}")
            answer = st.text_area(
                "Your answer",
                height=200,
                key="answer",
                placeholder="Write a complete answer. For behavioural questions, explain the situation, your action, and the result.",
            )
            submit_column, new_column = st.columns(2)
            submit = submit_column.button(
                "Submit for feedback", type="primary", use_container_width=True
            )
            new_question = new_column.button("Clear question", use_container_width=True)

            if new_question:
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
                            )
                            record = {
                                "question": st.session_state.current_question,
                                "scores": result,
                                "role": st.session_state.current_role,
                            }
                            st.session_state.history.append(record)
                            st.session_state.latest_feedback = result
                        except CoachError as exc:
                            st.error(str(exc))

            if st.session_state.latest_feedback:
                render_feedback(st.session_state.latest_feedback)
        else:
            st.info("Choose a role and question type, then select Get a random question.")

with dashboard_tab:
    st.subheader("Practice history")
    history = st.session_state.history
    if not history:
        st.info("Complete a practice question to see your session history.")
    else:
        output = io.StringIO(newline="")
        columns = [
            "role",
            "question",
            "structure_score",
            "depth_score",
            "examples_score",
            "communication_score",
            "weighted_score",
            "practice_decision",
        ]
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        for item in history:
            scores_for_item = item["scores"]
            writer.writerow({
                "role": item["role"],
                "question": item["question"],
                "structure_score": scores_for_item["structure_score"],
                "depth_score": scores_for_item["depth_score"],
                "examples_score": scores_for_item["examples_score"],
                "communication_score": scores_for_item["communication_score"],
                "weighted_score": scores_for_item["overall_score"],
                "practice_decision": scores_for_item["hire_decision"],
            })
        st.download_button(
            "Download session report (CSV)",
            data=output.getvalue(),
            file_name="interview_practice_history.csv",
            mime="text/csv",
        )

        scores = [item["scores"]["overall_score"] for item in history]
        first, second, third = st.columns(3)
        first.metric("Answers submitted", len(history))
        second.metric("Average weighted score", f"{sum(scores) / len(scores):.1f}/10")
        third.metric("Best weighted score", f"{max(scores):.1f}/10")

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
