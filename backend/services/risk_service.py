import re

# -------------------------
# High-risk direct phrases
# -------------------------
HIGH_RISK_PATTERNS = [
    r"\bi want to die\b",
    r"\bkill myself\b",
    r"\bend my life\b",
    r"\bsuicide\b",
    r"\bno reason to live\b",
    r"\bi can't go on\b"
]

# -------------------------
# Moderate distress phrases
# -------------------------
MODERATE_RISK_PATTERNS = [
    r"\bfeel hopeless\b",
    r"\bworthless\b",
    r"\bi hate my life\b",
    r"\bno one cares\b",
    r"\bcompletely alone\b"
]


def detect_risk(text: str):
    """
    Detects crisis risk level from raw text.
    Returns: dict with risk_level and matched patterns
    """

    text = text.lower()

    high_matches = [
        pattern for pattern in HIGH_RISK_PATTERNS
        if re.search(pattern, text)
    ]

    moderate_matches = [
        pattern for pattern in MODERATE_RISK_PATTERNS
        if re.search(pattern, text)
    ]

    if high_matches:
        risk_level = "high"
    elif moderate_matches:
        risk_level = "moderate"
    else:
        risk_level = "low"

    return {
        "risk_level": risk_level,
        "high_matches": high_matches,
        "moderate_matches": moderate_matches
    }