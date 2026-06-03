🎯 AI Interview Coach
An AI-powered interview simulation system that evaluates Machine Learning and Data Science interview responses in real time using Claude 3.5 Sonnet.
The system provides structured scoring, behavioural feedback, and performance tracking across sessions.
🚀 Problem It Solves
Most candidates practice interviews without structured feedback or measurable improvement.
This system replicates a real technical interview loop:

Ask realistic industry-level questions
Evaluate answers using an LLM-based scoring rubric
Provide strict hiring-style decisions (Hire / No Hire)
Track performance over time
⚙️ System Architecture
User Input (Answer)
        ↓
Streamlit UI (Frontend)
        ↓
Claude 3.5 Sonnet (Evaluation Engine)
        ↓
Structured JSON Scoring Output
        ↓
Feedback + Decision Layer
        ↓
Session State Storage (Progress Tracking)
🧠 Core Features
🎯 Interview Question Engine (30+ ML + DS questions)
🧾 Structured LLM Evaluation (rubric-based scoring)
📊 Hire / No-Hire decision system
📈 Performance tracking across sessions
🧠 Behavioural + technical feedback breakdown
💾 Persistent session state using Streamlit
🛠️ Tech Stack
Python 3.10+
Streamlit (UI layer)
Anthropic Claude 3.5 Sonnet (LLM evaluation)
Requests (API handling)
📁 Project Structure
Ai-interview-Coach/
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
🚀 How to Run
git clone https://github.com/aryaniftikhar05-droid/Ai-interview-Coach.git
cd Ai-interview-Coach
pip install -r requirements.txt
python -m streamlit run app.py
🧠 Key Engineering Design Decisions
Used structured prompting to force deterministic evaluation output
Implemented session-based memory for interview tracking
Designed a rubric scoring system (structure, depth, clarity, examples)
Isolated API keys using environment variables for security
Built a lightweight frontend using Streamlit instead of heavy frameworks
📊 Why This Project Matters
This is not just a Q&A bot.
It simulates an interview loop with:

Consistent evaluation logic
Repeatable scoring framework
Progress tracking over time
It demonstrates applied understanding of:
LLM orchestration
Evaluation system design
Lightweight full-stack AI applications
👤 Author
Aryan Iftikhar
BSc Computer Science | Keele University
Aspiring AI / ML Engineer


