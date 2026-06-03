# 🎯 AI Interview Coach

Real-time ML interview feedback powered by Claude API. Covers ML Engineer and Data Scientist roles across technical, system design, and behavioural questions.

## 📺 What It Does
* **Random Question Generator:** Pulls from a bank of 30+ realistic tech industry interview questions.
* **Granular Evaluation:** Claude 3.5 Sonnet evaluates answers on Structure, Depth, Examples, and Communication.
* **Actionable Feedback:** Outputs a definitive Hire/No-Hire decision accompanied by a critical gap analysis.
* **Performance Dashboard:** Tracks historical scoring improvement over time using persistent session states.

## 🛠️ Built With
* **Python 3.10+** — Core programming language
* **Streamlit** — Frontend dashboard UI implementation
* **Anthropic Claude API** — LLM evaluation layer
* **Requests** — Synchronous endpoint handling

---

💡 What I Learned
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


# 1. Clone the repository
git clone https://github.com/aryaniftikhar05-droid/Ai-interview-Coach.git
cd Ai-interview-Coach

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the Streamlit dashboard
python -m streamlit run app.py


