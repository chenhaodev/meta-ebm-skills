# builder/classify.py
import re

_RULES = [
    ("drugs",      [r"drug information", r"patient drug information", r"pediatric drug information"]),
    ("overview",   [r"\boverview\b", r"\bpathogenesis\b", r"\bepidemiolog", r"\bgenetics\b",
                    r"\bnatural history\b", r"\brisk factor", r"\bphenotype"]),
    ("monitoring", [r"\bmonitoring\b", r"\badherence\b", r"\bpeak expiratory\b",
                    r"what do patients", r"trigger control"]),
    ("diagnosis",  [r"\bdiagnos", r"\bevaluat", r"pulmonary function", r"spirometry", r"spirometric",
                    r"bronchoprovocation", r"flow.volume", r"exhaled nitric"]),
    ("treatment",  [r"\btreatment\b", r"\bmanagement\b", r"\btherapy\b", r"\btherapies\b",
                    r"beta agonist", r"corticosteroid", r"inhaled", r"bronchodilator",
                    r"mechanical ventilation", r"heliox", r"theophylline"]),
]

def classify_topic(title: str) -> str:
    """Assign a clinical bucket to a topic based on its title."""
    lower = title.lower()
    for bucket, patterns in _RULES:
        if any(re.search(p, lower) for p in patterns):
            return bucket
    return "overview"  # default
