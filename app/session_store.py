"""
In-memory session state per conversation.
"""
from typing import Dict

from app.models import ExtractedIntelligence


def _merge_intelligence(a: ExtractedIntelligence, b: ExtractedIntelligence) -> ExtractedIntelligence:
    """Merge two ExtractedIntelligence objects, deduplicating."""
    def merge_lists(la: list, lb: list) -> list:
        seen = set()
        result = []
        for x in la + lb:
            if x not in seen:
                seen.add(x)
                result.append(x)
        return result

    return ExtractedIntelligence(
        bankAccounts=merge_lists(a.bankAccounts, b.bankAccounts),
        upiIds=merge_lists(a.upiIds, b.upiIds),
        phishingLinks=merge_lists(a.phishingLinks, b.phishingLinks),
        phoneNumbers=merge_lists(a.phoneNumbers, b.phoneNumbers),
        suspiciousKeywords=merge_lists(a.suspiciousKeywords, b.suspiciousKeywords),
    )


class Session:
    """Session state for a single conversation."""
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.turn_count = 0
        self.scam_detected = False
        self.intelligence = ExtractedIntelligence()

    def to_dict(self) -> dict:
        """For callback payload compatibility."""
        return {
            "session_id": self.session_id,
            "turn_count": self.turn_count,
            "scam_detected": self.scam_detected,
            "intelligence": self.intelligence,
        }


_sessions: Dict[str, Session] = {}


def get_or_create(session_id: str) -> Session:
    """
    Get existing session or create new one.
    """
    if session_id in _sessions:
        return _sessions[session_id]
    session = Session(session_id)
    _sessions[session_id] = session
    return session


def update_intelligence(session_id: str, intel: ExtractedIntelligence) -> None:
    """
    Merge new intelligence into session, deduplicating.
    """
    session = get_or_create(session_id)
    session.intelligence = _merge_intelligence(session.intelligence, intel)


def increment_turn(session_id: str) -> None:
    """Increment turn count for session."""
    session = get_or_create(session_id)
    session.turn_count += 1


def mark_scam_detected(session_id: str) -> None:
    """Mark session as scam detected."""
    session = get_or_create(session_id)
    session.scam_detected = True
