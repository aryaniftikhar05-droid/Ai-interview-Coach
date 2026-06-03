import streamlit as st
import requests
import json
import random

st.set_page_config(page_title="AI Interview Coach", page_icon="🎯", layout="wide")

st.markdown("""
<style>
.question-box { background:#1a1a2e; border-left:4px solid #00d4ff; padding:16px; border-radius:8px; margin:10px 0; color:#fff; }
.feedback-good { background:#E1F5EE; border-left:4px solid #27AE60; padding:14px; border-radius:6px; margin:8px 0; }
.feedback-warn { background:#FAEEDA; border-left:4px solid #E67E22; padding:14px; border-radius:6px; margin:8px 0; }
.feedback-bad  { background:#FCEBEB; border-left:4px solid #C0392B; padding:14px; border-radius:6px; margin:8px 0; }
.score-pill    { display:inline-block; padding:4px 14px; border-radius:20px; font-weight:600; font-size:14px; }
</style>
""", unsafe_allow_html=True)

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
        ]
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
        ]
    }
}

EVALUATION_CRITERIA = {
    "structure":    {"weight": 0.25, "desc": "Clear, logical structure (problem → approach → solution → result)"},
    "depth":        {"weight": 0.30, "desc": "Technical depth and accuracy"},
    "examples":     {"weight": 0.25, "desc": "Concrete examples or numbers to back up claims"},
    "communication":{"weight": 0.20, "desc": "Clarity and conciseness — would a hiring manager follow this?"},
}

def call_claude(system_prompt: str, user_message: str) -> str:
    """Call Claude API for interview feedback."""
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={"Content-Type": "application/json"},
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1000,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_message}]
        }
    )
    data = response.json()
    return data["content"][0]["text"] if data.get("content") else "Error getting feedback."

def evaluate_answer(question: str, answer: str, role: str) -> dict:
    system = f"""You are a senior {role} interviewer at a top tech company (Google, Meta, or a leading fintech).
You are evaluating a candidate's interview answer. Be brutally honest but constructive.

Evaluate on exactly these 4 criteria, score each 1-10:
1. Structure (25%) - Clear logical flow
2. Depth (30%) - Technical accuracy and depth  
3. Examples (25%) - Concrete examples or metrics
4. Communication (20%) - Clarity and conciseness

Respond ONLY in this exact JSON format, nothing else:
{{
  "structure_score": <1-10>,
  "depth_score": <1-10>,
  "examples_score": <1-10>,
  "communication_score": <1-10>,
  "overall_score": <1-10>,
  "what_was_good": "<2-3 specific things done well>",
  "critical_gap": "<the single most important thing missing>",
  "model_answer_hint": "<in 2 sentences, what a perfect answer would include>",
  "hire_decision": "<STRONG YES / YES / BORDERLINE / NO>"
}}"""
    
    user_msg = f"Question: {question}\n\nCandidate Answer: {answer}"
    
    try:
        raw = call_claude(system, user_msg)
        # strip markdown fences if present
        clean = raw.strip().replace("```json","").replace("```","").strip()
        return json.loads(clean)
    except Exception:
        return {
            "structure_score": 5, "depth_score": 5, "examples_score": 5,
            "communication_score": 5, "overall_score": 5,
            "what_was_good": "Could not parse feedback.",
            "critical_gap": "Please try again.",
            "model_answer_hint": "N/A",
            "hire_decision": "BORDERLINE"
        }

# ── UI ────────────────────────────────────────────────────────────────────────

st.title("🎯 AI Interview Coach")
st.caption("Real-time interview feedback powered by Claude · ML Engineer & Data Scientist prep")

st.markdown("""
> **Problem**: Most candidates fail ML interviews not because they lack knowledge — but because they can't
> articulate it clearly under pressure. This coach gives you instant, brutally honest feedback
> on every answer — just like a senior engineer would in a real debrief.
""")

# initialise session state
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "history" not in st.session_state:
    st.session_state.history = []
if "total_score" not in st.session_state:
    st.session_state.total_score = []

tab1, tab2, tab3 = st.tabs(["🎤 Practice Mode", "📊 Performance Dashboard", "📚 Question Bank"])

with tab1:
    col1, col2 = st.columns([1, 2])

    with col1:
        role     = st.selectbox("Target role", ["ML Engineer", "Data Scientist"])
        category = st.selectbox("Question type", list(QUESTION_BANK[role].keys()))
        
        if st.button("🎲 Get Random Question", type="primary", use_container_width=True):
            questions = QUESTION_BANK[role][category]
            st.session_state.current_question = random.choice(questions)
            st.session_state.current_role     = role

        st.divider()
        st.markdown("**Scoring criteria**")
        for name, data in EVALUATION_CRITERIA.items():
            st.markdown(f"• **{name.title()}** ({data['weight']:.0%}) — {data['desc']}")

    with col2:
        if st.session_state.current_question:
            st.markdown(f'<div class="question-box"><h3>❓ {st.session_state.current_question}</h3></div>',
                        unsafe_allow_html=True)
            
            answer = st.text_area("Your answer", height=200,
                                   placeholder="Type your answer here. Aim for 3-5 minutes of spoken response. Use the STAR method for behavioural questions.")
            
            col_a, col_b = st.columns(2)
            submit = col_a.button("📤 Submit for Feedback", type="primary", use_container_width=True)
            clear  = col_b.button("🔄 New Question", use_container_width=True)
            
            if clear:
                st.session_state.current_question = None
                st.rerun()

            if submit and answer.strip():
                if len(answer.split()) < 10:
                    st.warning("Answer is too short. Give at least a paragraph.")
                else:
                    with st.spinner("Evaluating your answer..."):
                        result = evaluate_answer(
                            st.session_state.current_question,
                            answer,
                            st.session_state.get("current_role", "ML Engineer")
                        )

                    # store in history
                    st.session_state.history.append({
                        "question": st.session_state.current_question,
                        "answer":   answer,
                        "scores":   result,
                        "role":     role
                    })
                    st.session_state.total_score.append(result.get("overall_score", 5))

                    # overall score
                    score = result.get("overall_score", 5)
                    decision = result.get("hire_decision", "BORDERLINE")
                    dec_color = {"STRONG YES":"#27AE60","YES":"#2E86AB",
                                 "BORDERLINE":"#E67E22","NO":"#C0392B"}.get(decision,"#666")

                    st.divider()
                    s1, s2, s3, s4, s5 = st.columns(5)
                    s1.metric("Structure",      f"{result.get('structure_score',5)}/10")
                    s2.metric("Depth",          f"{result.get('depth_score',5)}/10")
                    s3.metric("Examples",       f"{result.get('examples_score',5)}/10")
                    s4.metric("Communication",  f"{result.get('communication_score',5)}/10")
                    s5.metric("Overall",        f"{score}/10")

                    st.markdown(f"""<div style="background:#F8F9FA;border-radius:8px;padding:16px;text-align:center;margin:10px 0">
                        <h2 style="color:{dec_color}">{decision}</h2>
                        <p style="color:#666">Hire decision</p></div>""", unsafe_allow_html=True)

                    css = "feedback-good" if score >= 7 else "feedback-warn" if score >= 5 else "feedback-bad"
                    st.markdown(f"""<div class="{css}">
                        <strong>✅ What you did well:</strong><br>{result.get('what_was_good','')}
                    </div>""", unsafe_allow_html=True)
                    st.markdown(f"""<div class="feedback-bad">
                        <strong>🚨 Critical gap:</strong><br>{result.get('critical_gap','')}
                    </div>""", unsafe_allow_html=True)
                    st.markdown(f"""<div class="feedback-warn">
                        <strong>💡 What a perfect answer includes:</strong><br>{result.get('model_answer_hint','')}
                    </div>""", unsafe_allow_html=True)
        else:
            st.info("👈 Select a role and question type, then click 'Get Random Question'")

with tab2:
    st.subheader("Your performance over time")
    if not st.session_state.history:
        st.info("Complete at least one practice question to see your dashboard.")
    else:
        avg = sum(st.session_state.total_score) / len(st.session_state.total_score)
        c1, c2, c3 = st.columns(3)
        c1.metric("Questions answered", len(st.session_state.history))
        c2.metric("Average score",      f"{avg:.1f}/10")
        c3.metric("Best score",         f"{max(st.session_state.total_score)}/10")

        st.divider()
        for i, item in enumerate(reversed(st.session_state.history[-5:])):
            score = item["scores"].get("overall_score", 5)
            css   = "feedback-good" if score >= 7 else "feedback-warn" if score >= 5 else "feedback-bad"
            st.markdown(f"""<div class="{css}">
                <strong>Q{len(st.session_state.history)-i}: {item['question'][:80]}...</strong><br>
                Score: {score}/10 · Decision: {item['scores'].get('hire_decision','N/A')}
            </div>""", unsafe_allow_html=True)

with tab3:
    st.subheader("Full question bank")
    for role_name, categories in QUESTION_BANK.items():
        with st.expander(f"**{role_name}** — {sum(len(q) for q in categories.values())} questions"):
            for cat, questions in categories.items():
                st.markdown(f"**{cat}**")
                for q in questions:
                    st.markdown(f"• {q}")
