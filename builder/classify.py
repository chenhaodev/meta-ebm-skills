# builder/classify.py
import re

_RULES: list[tuple[str, list[re.Pattern[str]]]] = [
    ("drugs", [re.compile(p) for p in [
        r"drug information",
        r"patient drug information",
        r"pediatric drug information",
    ]]),
    ("overview", [re.compile(p) for p in [
        r"\boverview\b",
        r"\bpathogenesis\b",
        r"\bepidemiolog",
        r"\bgenetics\b",
        r"\bnatural history\b",
        r"\brisk factor",
        r"\bphenotype",
    ]]),
    ("monitoring", [re.compile(p) for p in [
        r"\bmonitoring\b",
        r"\badherence\b",
        r"\bpeak expiratory\b",
        r"what do patients",
        r"trigger control",
    ]]),
    ("diagnosis", [re.compile(p) for p in [
        r"\bdiagnos",
        r"\bevaluat",
        r"pulmonary function",
        r"spirometry",
        r"spirometric",
        r"bronchoprovocation",
        r"flow.volume",
        r"exhaled nitric",
    ]]),
    ("treatment", [re.compile(p) for p in [
        r"\btreatment\b",
        r"\bmanagement\b",
        r"\btherapy\b",
        r"\btherapies\b",
        r"beta agonist",
        r"corticosteroid",
        r"inhaled",
        r"bronchodilator",
        r"mechanical ventilation",
        r"heliox",
        r"theophylline",
    ]]),
]


def classify_topic(title: str) -> str:
    """Assign a clinical bucket to a topic based on its title."""
    lower = title.lower()
    for bucket, patterns in _RULES:
        if any(p.search(lower) for p in patterns):
            return bucket
    return "overview"  # default
