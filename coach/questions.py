"""Built-in interview questions, grouped by role and category."""
import re

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


# Skills recruiters often list, with the words that show them in a job advert.
# Terms match whole words (an optional plural "s" is allowed), so "rag" does not
# match "average" and "aws" does not match "laws". A term ending in "*" matches
# any word that starts with it, e.g. "forecast*" matches "forecasting".
SKILLS = {
    "Python": ["python"],
    "SQL": ["sql", "postgres", "bigquery", "snowflake"],
    "PyTorch": ["pytorch", "torch"],
    "TensorFlow": ["tensorflow", "keras"],
    "scikit-learn": ["scikit-learn", "sklearn", "scikit"],
    "Gradient boosting": ["xgboost", "lightgbm", "catboost", "gradient boosting"],
    "Deep learning": ["deep learning", "neural network", "cnn", "rnn"],
    "Transformers / LLMs": ["transformer", "llm", "large language model", "gpt", "rag", "hugging face", "huggingface"],
    "NLP": ["nlp", "natural language"],
    "Computer vision": ["computer vision", "image classification", "object detection"],
    "Statistics": ["statistic*", "hypothesis test", "p-value", "bayesian", "regression"],
    "A/B testing": ["a/b test*", "ab test*", "experiment*"],
    "Recommender systems": ["recommend*", "personalisation", "personalization", "ranking"],
    "Forecasting": ["forecast*", "time series", "time-series", "demand planning"],
    "Fraud / risk": ["fraud*", "credit risk", "risk model*", "risk scor*", "anomal*"],
    "MLOps": ["mlops", "mlflow", "kubeflow", "model monitoring", "drift", "retrain*"],
    "a cloud platform (AWS, GCP or Azure)": ["aws", "gcp", "azure", "sagemaker", "vertex"],
    "Docker / Kubernetes": ["docker", "kubernetes", "k8s", "container*"],
    "Data pipelines": ["airflow", "spark", "etl", "pipeline", "dbt", "kafka"],
    "Feature engineering": ["feature engineering", "feature store"],
    "Model explainability": ["shap", "explainab*", "interpretab*"],
    "Stakeholder communication": ["stakeholder", "communicat*", "non-technical", "business partner"],
}

# Which built-in questions each skill relates to (matched by words in the question).
SKILL_QUESTION_WORDS = {
    "Gradient boosting": ["gradient boosting", "bagging", "boosting"],
    "Transformers / LLMs": ["attention", "transformer", "rlhf", "language model"],
    "Statistics": ["p-value", "correlation", "parametric", "cross-validation"],
    "A/B testing": ["a/b test", "experiment"],
    "Recommender systems": ["recommendation"],
    "Fraud / risk": ["fraud", "imbalanced"],
    "MLOps": ["retrains", "accuracy drops", "deploy"],
    "Feature engineering": ["feature store", "dimensionality", "missing values"],
    "Model explainability": ["shap"],
    "Stakeholder communication": ["non-technical", "stakeholder", "business leaders"],
    "Data pipelines": ["pipeline", "10 million"],
    "Python": ["limited ram", "data leakage"],
    "scikit-learn": ["regularisation", "cross-validation", "precision vs recall"],
}

MAX_JOB_TEXT = 20_000


def _term_pattern(term):
    if term.endswith("*"):
        body = re.escape(term[:-1]) + r"[a-z0-9\-]*"
    else:
        body = re.escape(term) + r"(?:s|es)?"
    return r"(?<![a-z0-9])" + body.replace(r"\ ", r"[\s\-]+") + r"(?![a-z0-9])"


SKILL_PATTERNS = {
    skill: re.compile("|".join(_term_pattern(t) for t in terms))
    for skill, terms in SKILLS.items()
}


def skills_in_job_advert(text):
    """Return the skills mentioned in a job advert, in a stable order."""
    lowered = text.lower()[:MAX_JOB_TEXT]
    return [skill for skill, pattern in SKILL_PATTERNS.items() if pattern.search(lowered)]


def _all_questions():
    for role, categories in QUESTION_BANK.items():
        for category, questions in categories.items():
            for question in questions:
                yield question, role, category


def search_questions(query):
    """Find built-in questions containing every search word, ignoring case.

    Search the question, role and category together. A blank query returns
    the full bank in its original order.
    """
    terms = query.casefold().split()
    return [
        (question, role, category)
        for question, role, category in _all_questions()
        if all(term in f"{question} {role} {category}".casefold() for term in terms)
    ]


def questions_for_job(text, limit=8):
    """Pick practice questions that match a pasted job advert.

    Returns (question, role, category, reason) tuples: one question per skill
    found. A built-in question is used when one fits (words listed first win);
    otherwise the skill gets a question about the candidate's own project.
    """
    picked, seen = [], set()
    for skill in skills_in_job_advert(text):
        match = None
        for word in SKILL_QUESTION_WORDS.get(skill, []):
            match = next(
                (item for item in _all_questions()
                 if word in item[0].lower() and item[0] not in seen),
                None,
            )
            if match:
                break
        if match is None:
            match = (
                f"Tell me about a project where you used {skill}. "
                "What problem did it solve and what was the result?",
                "ML Engineer", "Behavioural",
            )
        seen.add(match[0])
        picked.append((*match, f"Matches: {skill}"))
    return picked[:limit]
