"""
Pydantic models - request/response structures.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Single message in a conversation."""
    sender: str = "scammer"
    text: str = ""
    timestamp: str = ""


class Metadata(BaseModel):
    """Optional metadata for the request."""
    channel: Optional[str] = None  # SMS, WhatsApp, Email, Chat
    language: Optional[str] = None
    locale: Optional[str] = None  # e.g., IN


class HoneypotRequest(BaseModel):
    """Incoming request from the platform. Lenient for tester compatibility."""
    sessionId: str
    message: Message
    conversationHistory: Optional[List[Message]] = None  # Accept null from tester
    metadata: Optional[Metadata] = None


class HoneypotResponse(BaseModel):
    """API response format — exactly what GUVI expects."""
    status: str = "success"
    reply: str = "I'm not sure, could you please explain?"

    model_config = {"extra": "forbid"}  # No extra keys


class ExtractedIntelligence(BaseModel):
    """Intelligence extracted from conversation (for callback)."""
    bankAccounts: List[str] = Field(default_factory=list)
    upiIds: List[str] = Field(default_factory=list)
    phishingLinks: List[str] = Field(default_factory=list)
    phoneNumbers: List[str] = Field(default_factory=list)
    suspiciousKeywords: List[str] = Field(default_factory=list)
