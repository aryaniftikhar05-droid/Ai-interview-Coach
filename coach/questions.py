"""Built-in interview questions, grouped by role and category."""

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
