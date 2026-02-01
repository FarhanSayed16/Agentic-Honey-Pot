"""
Callback service - POST final result to GUVI endpoint.
"""
import logging
from typing import Any, Dict, Optional

import httpx

from app.config import (
    CALLBACK_URL,
    CALLBACK_RETRY_COUNT,
    CALLBACK_TIMEOUT,
    MIN_TURNS_BEFORE_CALLBACK,
)
from app.models import ExtractedIntelligence
from app.session_store import Session

logger = logging.getLogger(__name__)


def _build_agent_notes(intelligence: ExtractedIntelligence) -> str:
    """Generate short summary for agentNotes."""
    parts = []
    if intelligence.upiIds:
        parts.append(f"UPI IDs shared: {len(intelligence.upiIds)}")
    if intelligence.bankAccounts:
        parts.append(f"Bank accounts shared: {len(intelligence.bankAccounts)}")
    if intelligence.phishingLinks:
        parts.append(f"Links shared: {len(intelligence.phishingLinks)}")
    if intelligence.phoneNumbers:
        parts.append(f"Phone numbers shared: {len(intelligence.phoneNumbers)}")
    if intelligence.suspiciousKeywords:
        parts.append("Urgency/verification tactics used")
    if not parts:
        return "Scam engagement; no financial details extracted yet"
    return "; ".join(parts)


def build_callback_payload(
    session_id: str,
    scam_detected: bool,
    total_messages: int,
    intelligence: ExtractedIntelligence,
    agent_notes: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build callback payload matching GUVI spec exactly.
    """
    if agent_notes is None:
        agent_notes = _build_agent_notes(intelligence)

    return {
        "sessionId": session_id,
        "scamDetected": scam_detected,
        "totalMessagesExchanged": total_messages,
        "extractedIntelligence": {
            "bankAccounts": list(intelligence.bankAccounts),
            "upiIds": list(intelligence.upiIds),
            "phishingLinks": list(intelligence.phishingLinks),
            "phoneNumbers": list(intelligence.phoneNumbers),
            "suspiciousKeywords": list(intelligence.suspiciousKeywords),
        },
        "agentNotes": agent_notes,
    }


def send_callback(payload: Dict[str, Any]) -> bool:
    """
    POST payload to CALLBACK_URL. Retry on failure.
    Returns True if 2xx, False otherwise.
    """
    session_id = payload.get("sessionId", "?")
    logger.info("Callback attempt for sessionId=%s", session_id)

    for attempt in range(1, CALLBACK_RETRY_COUNT + 1):
        try:
            with httpx.Client(timeout=CALLBACK_TIMEOUT) as client:
                resp = client.post(
                    CALLBACK_URL,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
            if 200 <= resp.status_code < 300:
                logger.info("Callback sent successfully for session %s", payload.get("sessionId"))
                return True
            logger.warning(
                "Callback attempt %d failed: %d %s",
                attempt,
                resp.status_code,
                resp.text[:200] if resp.text else "",
            )
        except Exception as e:
            logger.warning("Callback attempt %d error: %s", attempt, str(e))

        if attempt < CALLBACK_RETRY_COUNT:
            import time
            time.sleep(1)

    logger.warning("Callback failed after %d attempts for sessionId=%s", CALLBACK_RETRY_COUNT, session_id)
    return False


def should_send_callback(session: Session) -> bool:
    """
    Return True when conditions met:
    - scam_detected
    - turn_count >= MIN_TURNS_BEFORE_CALLBACK (e.g., 5)
    - Not on turn 1
    """
    if not session.scam_detected:
        return False
    if session.turn_count < MIN_TURNS_BEFORE_CALLBACK:
        return False
    return True
