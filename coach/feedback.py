"""Ask Claude for interview feedback and validate the result.

The model is forced to answer through a tool with a JSON schema, so the
response is structured data rather than free text that has to be parsed.
Scores are still checked here, and the weighted score is calculated locally
so the model cannot change the weighting.
"""
import os

import requests

API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"
DEFAULT_MODEL = "claude-sonnet-5-5"
TIMEOUT_SECONDS = 45

CRITERIA = {
    "structure_score": 0.25,
    "depth_score": 0.30,
    "examples_score": 0.25,
    "communication_score": 0.20,
}
TEXT_FIELDS = ("what_was_good", "critical_gap", "model_answer_hint", "follow_up_question")
DECISIONS = ("STRONG YES", "YES", "BORDERLINE", "NO")

FEEDBACK_TOOL = {
    "name": "submit_feedback",
    "description": "Submit structured practice feedback for one interview answer.",
    "input_schema": {
        "type": "object",
        "properties": {
            **{
                field: {"type": "integer", "minimum": 1, "maximum": 10}
                for field in CRITERIA
            },
            "what_was_good": {"type": "string", "description": "Specific strengths."},
            "critical_gap": {"type": "string", "description": "The most important missing point."},
            "model_answer_hint": {
                "type": "string",
                "description": "Two sentences describing a stronger answer.",
            },
            "follow_up_question": {
                "type": "string",
                "description": "One probing follow-up an interviewer would ask next.",
            },
            "hire_decision": {"type": "string", "enum": list(DECISIONS)},
        },
        "required": [*CRITERIA, *TEXT_FIELDS, "hire_decision"],
    },
}


class CoachError(Exception):
    """An error message that is safe to show in the app."""


def build_system_prompt(role):
    return f"""You are a practice interviewer for a {role} candidate.
Evaluate the answer constructively. This is practice feedback, not a real hiring decision.

Score each criterion from 1 to 10:
- Structure (25%): logical flow
- Depth (30%): technical accuracy and depth
- Examples (25%): concrete examples or metrics
- Communication (20%): clarity and conciseness

Be specific to the candidate's actual answer. Do not reward length on its own.
Submit your feedback with the submit_feedback tool."""


def request_feedback(question, answer, role, api_key, model=None, post=requests.post):
    """Call the Messages API and return the raw tool input (a dict)."""
    if not api_key:
        raise CoachError(
            "Anthropic API key not found. Add ANTHROPIC_API_KEY to "
            ".streamlit/secrets.toml or your environment."
        )
    try:
        response = post(
            API_URL,
            headers={
                "content-type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": API_VERSION,
            },
            json={
                "model": model or os.getenv("ANTHROPIC_MODEL") or DEFAULT_MODEL,
                "max_tokens": 1200,
                "system": build_system_prompt(role),
                "tools": [FEEDBACK_TOOL],
                "tool_choice": {"type": "tool", "name": FEEDBACK_TOOL["name"]},
                "messages": [
                    {
                        "role": "user",
                        "content": f"Question: {question}\n\nCandidate answer: {answer}",
                    }
                ],
            },
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
    except requests.Timeout as exc:
        raise CoachError("The feedback request timed out. Please try again.") from exc
    except requests.HTTPError as exc:
        status = getattr(exc.response, "status_code", None)
        if status == 401:
            raise CoachError("The API key was rejected. Check ANTHROPIC_API_KEY.") from exc
        if status == 429:
            raise CoachError("Rate limit reached. Wait a moment and try again.") from exc
        raise CoachError("The Anthropic API returned an error. Please try again.") from exc
    except requests.RequestException as exc:
        raise CoachError(
            "Could not reach the Anthropic API. Check your connection and API settings."
        ) from exc
    except ValueError as exc:
        raise CoachError("The API returned a response that could not be read.") from exc

    for block in data.get("content", []):
        if block.get("type") == "tool_use" and block.get("name") == FEEDBACK_TOOL["name"]:
            return block.get("input")
    raise CoachError("The API response did not contain interview feedback.")


def validate_feedback(result):
    """Check every field and add the locally calculated weighted score."""
    if not isinstance(result, dict):
        raise CoachError("The model returned feedback in an unexpected format.")

    validated = {}
    for field in CRITERIA:
        value = result.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 1 <= value <= 10:
            raise CoachError("The model returned an invalid score. Please try again.")
        validated[field] = float(value)

    for field in TEXT_FIELDS:
        value = result.get(field)
        if not isinstance(value, str) or not value.strip():
            raise CoachError("The model returned incomplete feedback. Please try again.")
        validated[field] = value.strip()

    decision = result.get("hire_decision")
    if decision not in DECISIONS:
        raise CoachError("The model returned an invalid practice decision. Please try again.")
    validated["hire_decision"] = decision
    validated["overall_score"] = weighted_score(validated)
    return validated


def weighted_score(scores):
    return round(sum(scores[field] * weight for field, weight in CRITERIA.items()), 1)


def evaluate_answer(question, answer, role, api_key, model=None, post=requests.post):
    raw = request_feedback(question, answer, role, api_key, model=model, post=post)
    return validate_feedback(raw)
