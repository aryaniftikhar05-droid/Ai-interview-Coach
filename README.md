# 🎯 AI Interview Coach

A reproducible, production-ready Streamlit application powered by Claude 3.5 Sonnet to simulate senior-level technical, system design, and behavioral interviews — built as a professional portfolio development asset.
   
📌 Project Overview

Most technical candidates fail machine learning and data science interview loops not due to a lack of core technical theory, but because they struggle to articulate complex concepts structurally under pressure. 

This application provides an end-to-end simulated mock interview dashboard. It prompts the user with curated, high-frequency industry questions and runs comprehensive real-time evaluations across standard engineering competency metrics. By processing input text via strict prompt-engineered grading matrices, it outputs an instant scorecard, a definitive hiring decision, an explicit critique of critical gaps, and target model-answer hints.

🗂️ Repository Structure

Ai-interview-Coach/
│
├── .streamlit/
│   └── secrets.toml             ← Local API credentials configuration (git-ignored)
│
├── app.py                       ← Main Streamlit application and UI layout engine
├── requirements.txt             ← Python library production dependencies
└── README.md                    ← Interactive documentation and setup playbook

🔍 Evaluation Criteria & Grading Matrix

CompetencyWeightAssessment FocusTarget Rubric Standard**Structure**25%Logical conversational flow (STAR framework / problem context → solution design)Linear, clear, scannable delivery**Depth**30%Technical accuracy, architectural viability, framework knowledgeDeep domain-specific trade-off analysis**Examples**25%Integration of concrete metrics, production constraints, or hard numbersData-backed claim validation**Communication**20%Brevity, concise phrasing, vocabulary precision, conceptual clarityC-level executive level crispness
⚙️ Application Architecture Pipeline

1. Select Role      → Choose target discipline (ML Engineer / Data Scientist) and topic track
2. Fetch Question   → Extract random, industry-vetted question from internal memory arrays
3. User Submission  → Capture comprehensive, paragraph-length text response from candidate
4. Length Guardrail → Validate string counts to block thin or low-effort submissions
5. JSON Formatting  → Inject responses into strict system prompts demanding raw telemetry objects
6. API Handshake    → Transmit payload securely to the Anthropic Claude 3.5 Sonnet endpoint
7. Response Parsing → Strip Markdown fences and extract structural feedback metadata safely
8. UI Render        → Display conditional, color-coded metric panels and tailored critiques
9. State Caching    → Persist evaluation metrics to persistent log history arrays

📊 Operational Benchmarks

Track RoleAvailable ModulesTotal Core QuestionsTarget Hire Threshold**ML Engineer**Technical Theory, System Design, Behavioral19 Production QuestionsScore $\ge$ 7.0 / 10**Data Scientist**Technical Theory, Case Study, Behavioral15 Analytics QuestionsScore $\ge$ 7.0 / 10

🛠️ Tools & Technologies

* **Python 3.10+** — core language architecture environment
* **Streamlit** — dashboard interface framework and interactive state controls
* **Anthropic Claude API** — (`claude-3-5-sonnet`) underlying analytical validation model
* **Requests** — client-server network protocol communication handler

🚀 How to Run

```bash
# 1. Clone the repository
git clone [https://github.com/aryaniftikhar05-droid/Ai-interview-Coach.git](https://github.com/aryaniftikhar05-droid/Ai-interview-Coach.git)
cd Ai-interview-Coach

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the Streamlit dashboard
python -m streamlit run app.py


💡 What I Learned
LLM Evaluation Matrix: Architecting strict system prompts that force models to reliably output parseable, non-hallucinated structural JSON blocks.
State Preservation: Leveraging temporary cache protocols (session_state) to manage multi-tab execution flow, history retention, and rolling metric aggregations cleanly.
API Secret Isolation: Isolating production API tokens securely using environment variable injection blocks to prevent accidental exposures on public repositories.
UI Customization overrides: Embedding custom CSS classes into boilerplate layouts to build professional, sleek dark-themed dashboards.

📁 Application State Schema
State VariableTypeDescriptionRuntime Scopecurrent_questionstringTracks the currently active interview prompt displayed to the candidateActive interview loop contextcurrent_rolestringIdentifies the active testing career track configurationGlobal runtime execution pathhistorylistNested dictionary logs storing cumulative answers and API feedback payloadsPerformance history visualizationtotal_scorelistFlat integer array storing historical final grades to compute running dashboard metricsAnalytics computation

Author
Aryan Iftikhar Computer Science Student | Aspiring Machine Learning & Software Engineer


