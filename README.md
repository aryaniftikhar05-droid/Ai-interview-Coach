# AI Interview Coach

A small Streamlit project for practising machine learning engineer and data scientist interview questions. It sends an answer to the Anthropic Messages API and displays model-generated feedback.

This is a learning project. The scores and practice decision are not a validated hiring assessment and should not be treated as a real prediction.

## Features

- Technical, system design, case study, and behavioural question categories
- Feedback on structure, technical depth, examples, and communication
- A weighted overall score calculated by the application
- A short history held in the current Streamlit session
- CSV download of session scores and questions (answer text is not included)

## Requirements

- Python 3.10 or later
- An Anthropic API key

## Run locally

1. Clone the repository and enter the project directory.
2. Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Create `.streamlit/secrets.toml` with this content:

   ```toml
   ANTHROPIC_API_KEY = "your-api-key"
   ```

   Keep this file private. It is excluded by `.gitignore`. You can instead set an `ANTHROPIC_API_KEY` environment variable.

5. Start the app:

   ```bash
   python -m streamlit run app.py
   ```

For Streamlit Community Cloud, add `ANTHROPIC_API_KEY` in the app's Secrets settings. Do not put the key in source code or commit it to GitHub.

## How it works

1. Choose a role and question category.
2. Generate a question and write an answer.
3. The app sends the question and answer to Anthropic.
4. The app parses the response, checks its fields and score ranges, and calculates the weighted score locally.
5. Feedback and recent scores are displayed in the browser session.
6. Optionally download the session score report as a CSV file.

## Data and limitations

- Answers are sent to Anthropic's API for processing. Do not submit passwords, sensitive personal data, or confidential information.
- History exists only in Streamlit session state. It is not a database and is not saved permanently.
- Model feedback can be inaccurate, inconsistent, or biased. The scores and practice decision are prompts for reflection, not objective measurements.
- The app requires a working API key and internet access. API errors are shown to the user; the app does not substitute a fake score when a request fails.

## Technologies

Python, Streamlit, Requests, and the Anthropic Messages API.
