"""Session history export."""
import csv
import io

from .feedback import CRITERIA

COLUMNS = ["role", "question", *CRITERIA, "weighted_score", "practice_decision"]


def history_to_csv(history):
    """Return the session history as CSV text. Answer text is not included."""
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=COLUMNS)
    writer.writeheader()
    for item in history:
        scores = item["scores"]
        writer.writerow({
            "role": item["role"],
            "question": _safe_cell(item["question"]),
            **{field: scores[field] for field in CRITERIA},
            "weighted_score": scores["overall_score"],
            "practice_decision": scores["hire_decision"],
        })
    return output.getvalue()


def _safe_cell(value):
    """Stop spreadsheet apps from treating user text as a formula."""
    text = str(value)
    return "'" + text if text[:1] in ("=", "+", "-", "@") else text
