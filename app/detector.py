"""
Scam detection logic.
"""
from typing import List

from app.models import Message

# Keyword categories with weights
URGENCY_KEYWORDS = [
    "immediately", "urgent", "today", "now", "blocked", "verify now",
    "act fast", "asap", "suspended", "expire", "deadline"
]
FINANCIAL_KEYWORDS = [
    "bank", "account", "upi", "payment", "transfer", "balance",
    "blocked", "suspended", "verify", "compliance", "fund", "money",
    "transaction", "refund", "reward", "prize", "lottery"
]
AUTHORITY_KEYWORDS = [
    "official", "bank", "verification", "compliance", "department",
    "reserve bank", "rbi", "government", "income tax"
]
ACTION_KEYWORDS = [
    "click", "share", "send", "verify", "link", "otp", "call",
    "register", "update", "confirm", "submit"
]

# Benign greetings - never treat as scam
BENIGN_GREETINGS = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}

SCAM_THRESHOLD = 2


def _score_message(text: str) -> int:
    """Score message for scam signals. Higher = more likely scam."""
    if not text or not text.strip():
        return 0

    text_lower = text.lower().strip()

    # Benign greetings alone → not scam
    if text_lower in BENIGN_GREETINGS:
        return 0
    if len(text_lower) <= 3 and text_lower in ("hi", "hey", "ok"):
        return 0

    score = 0

    # Urgency (weight 2)
    for kw in URGENCY_KEYWORDS:
        if kw in text_lower:
            score += 2
            break

    # Financial (weight 2)
    for kw in FINANCIAL_KEYWORDS:
        if kw in text_lower:
            score += 2
            break

    # Authority (weight 1)
    for kw in AUTHORITY_KEYWORDS:
        if kw in text_lower:
            score += 1
            break

    # Action (weight 1)
    for kw in ACTION_KEYWORDS:
        if kw in text_lower:
            score += 1
            break

    return score


def detect_scam(message_text: str, conversation_history: List[Message]) -> bool:
    """
    Detect if message indicates scam intent.
    Returns True if scam detected, False otherwise.
    """
    if not message_text:
        return False

    score = _score_message(message_text)

    # Boost score if follow-up message escalates (e.g., first vague, second asks for UPI)
    if conversation_history:
        # Check if any previous scammer message had high score
        scammer_texts = [m.text for m in conversation_history if m.sender == "scammer"]
        if scammer_texts:
            prev_score = max(_score_message(t) for t in scammer_texts)
            if prev_score > 0 and score > 0:
                score += 1  # Escalation boost

    return score >= SCAM_THRESHOLD
