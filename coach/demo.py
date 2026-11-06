"""Free demo mode: rule-based practice feedback that needs no API key.

This is not AI. It checks simple, visible signals in the answer (length,
structure words, numbers, concrete examples) so the app works for anyone
without an Anthropic account. The output uses the same shape as the Claude
feedback and goes through the same validation, so the rest of the app does
not need to know which mode produced it.
"""
import re

from coach.feedback import validate_feedback

STRUCTURE_WORDS = (
    "first", "second", "third", "then", "next", "finally", "because", "therefore",
    "however", "for example", "in summary", "overall", "situation", "task",
    "action", "result", "trade-off", "tradeoff",
)
EXAMPLE_WORDS = (
    "for example", "for instance", "in my project", "i built", "i used", "i worked",
    "we built", "we used", "at my", "in a project", "such as", "e.g.",
)
FILLER_WORDS = ("basically", "like", "kind of", "sort of", "stuff", "things", "very")

STOPWORDS = set("""
a an and are as at be been but by can could did do does for from had has have how
i if in into is it its of on or our should so than that the their them then there
these they this to was we were what when where which while who why will with would
you your about after before between describe explain tell time give example would
""".split())

FOLLOW_UPS = {
    "Technical": "How would you check that this works on real production data?",
    "System Design": "What would you change if traffic grew ten times overnight?",
    "Case Study": "Which single metric would you report to the business, and why?",
    "Behavioural": "What would you do differently if the same situation happened again?",
}
DEFAULT_FOLLOW_UP = "Can you give a concrete example of this from your own work?"


def _count(text, phrases):
    return sum(text.count(phrase) for phrase in phrases)


def _stem(word):
    return word[:5]


def keywords(text):
    """Meaningful words in a text, cut to a short stem so 'models' matches 'model'."""
    words = re.findall(r"[a-z][a-z0-9\-]+", text.lower())
    return {_stem(w) for w in words if len(w) > 2 and w not in STOPWORDS}


def relevance(question, answer):
    """Share of the question's key words that the answer mentions (0 to 1)."""
    wanted = keywords(question)
    if len(wanted) < 2:
        return 1.0
    return len(wanted & keywords(answer)) / len(wanted)


def answer_signals(answer):
    """Simple, visible signals in an answer. Used for scoring and the live checklist."""
    text = answer.lower()
    words = re.findall(r"[a-zA-Z0-9%£$.\-']+", answer)
    sentences = max(1, len(re.findall(r"[.!?](\s|$)", answer)))
    return {
        "word_count": len(words),
        "unique_words": len(set(w.lower() for w in words)),
        "sentences": sentences,
        "numbers": len(re.findall(r"\d", answer)),
        "structure_hits": _count(text, STRUCTURE_WORDS) + answer.count("\n"),
        "example_hits": _count(text, EXAMPLE_WORDS),
        "filler_hits": _count(f" {text} ", tuple(f" {w} " for w in FILLER_WORDS)),
    }


def _clamp(value):
    return int(max(1, min(10, round(value))))


def demo_feedback(question, answer, category=None):
    """Return validated feedback produced by simple, explainable rules."""
    sig = answer_signals(answer)
    word_count, sentences, numbers = sig["word_count"], sig["sentences"], sig["numbers"]
    structure_hits, example_hits = sig["structure_hits"], sig["example_hits"]
    filler_hits = sig["filler_hits"]
    avg_sentence = word_count / sentences
    on_topic = relevance(question, answer)

    structure = 3 + min(structure_hits, 5) + (1 if sentences >= 3 else 0)
    depth = 2 + min(word_count / 30, 5) + min(sig["unique_words"] / 60, 2)
    if on_topic == 0:
        # A long answer that never touches the question should not score well.
        depth = min(depth, 3)
        structure = min(structure, 5)
    examples = 2 + min(example_hits * 2, 5) + min(numbers, 3)
    communication = 8 - min(filler_hits, 4) - (2 if avg_sentence > 35 else 0)
    if word_count < 40:
        communication -= 1

    scores = {
        "structure_score": _clamp(structure),
        "depth_score": _clamp(depth),
        "examples_score": _clamp(examples),
        "communication_score": _clamp(communication),
    }

    strengths = []
    if structure_hits >= 2:
        strengths.append("the answer has a clear order")
    if example_hits:
        strengths.append("it includes a concrete example")
    if numbers:
        strengths.append("it uses numbers, which makes it believable")
    if word_count >= 120:
        strengths.append("it covers the topic in good detail")
    what_was_good = (
        "Good: " + ", ".join(strengths) + "."
        if strengths else "You answered the question directly, which is a good start."
    )

    weakest = min(scores, key=scores.get)
    off_topic = on_topic == 0
    gaps = {
        "structure_score": "The answer has no clear order. Use steps such as first, then, finally.",
        "depth_score": "The answer needs more depth. Explain how and why, not only what.",
        "examples_score": "There is no concrete example or number from your own work.",
        "communication_score": "Some sentences are long or use filler words. Keep it short and clear.",
    }
    hints = {
        "structure_score": "Start with a one-line answer, then explain in 2-3 clear steps, then finish with a short summary.",
        "depth_score": "Add the reason behind each choice and one trade-off you considered.",
        "examples_score": "Add one real project and one number, for example: 'this cut errors by 15%'.",
        "communication_score": "Use short sentences and remove words like 'basically' and 'kind of'.",
    }

    overall = sum(scores.values()) / 4
    if overall >= 8:
        decision = "STRONG YES"
    elif overall >= 6.5:
        decision = "YES"
    elif overall >= 5:
        decision = "BORDERLINE"
    else:
        decision = "NO"

    return validate_feedback({
        **scores,
        "what_was_good": what_was_good,
        "critical_gap": (
            "The answer does not seem to address the question. Use the key terms "
            "from the question and answer it directly first."
            if off_topic else gaps[weakest]
        ),
        "model_answer_hint": (
            "Start by repeating the core of the question in one sentence, then answer it."
            if off_topic else hints[weakest]
        ),
        "follow_up_question": FOLLOW_UPS.get(category, DEFAULT_FOLLOW_UP),
        "hire_decision": decision,
    })


def answer_checklist(question, answer):
    """Quick checks shown under the answer box before it is submitted."""
    sig = answer_signals(answer)
    return [
        (f"Enough detail ({sig['word_count']} words, aim for 80+)", sig["word_count"] >= 80),
        ("Clear order (first, then, finally...)", sig["structure_hits"] >= 2),
        ("A concrete example from your work", sig["example_hits"] >= 1),
        ("At least one number or result", sig["numbers"] >= 1),
        ("Uses the key words of the question", relevance(question, answer) >= 0.3),
    ]
