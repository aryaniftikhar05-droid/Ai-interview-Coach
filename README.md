# 🎯 AI Interview Coach

Real-time ML interview feedback powered by Claude API. Covers ML Engineer and Data Scientist roles across technical, system design, and behavioural questions.

## What it does
- Random question generator across 30+ real interview questions
- Claude evaluates your answer on 4 criteria: Structure, Depth, Examples, Communication
- Hire/No-hire decision with specific gap analysis
- Performance dashboard tracking improvement over time

## Run locally
```bash
pip3 install -r requirements.txt
python3 -m streamlit run app.py
```



* **Python 3.10+** — core language
* **Streamlit** — frontend dashboard UI
* **Anthropic Claude API** — LLM evaluation layer
* **Requests** — synchronous endpoint handler

---

## 🚀 How to Run

```bash
# 1. Clone the repository
git clone [https://github.com/aryaniftikhar05-droid/Ai-interview-Coach.git](https://github.com/aryaniftikhar05-droid/Ai-interview-Coach.git)
cd Ai-interview-Coach

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the pipeline dashboard
python -m streamlit run app.py

What I Learned
LLM Evaluation Matrix: How to build strict system prompts forcing models to output parseable structural JSON data.
State Preservation: Handling active interview data and history navigation loops smoothly utilizing Streamlit session states.
API Secret Isolation: Safeguarding operational credentials securely via cloud environment variables to prevent accidental code leaks.
UI Customization: Overriding boilerplate library layouts with targeted HTML style embeddings for custom visual dashboard cues.

## 📁 Repository Structure

```text
Ai-interview-Coach/
├── app.py               # The main application script (Streamlit app)
├── requirements.txt     # List of external Python packages to install
├── .gitignore           # Tells Git which files/folders to hide or ignore
└── README.md            # Project documentation and setup instructions
