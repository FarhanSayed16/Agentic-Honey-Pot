"""
Pydantic models - request/response structures.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Single message in a conversation."""
    sender: str  # "scammer" or "user"
    text: str
    timestamp: str  # ISO-8601 format


class Metadata(BaseModel):
    """Optional metadata for the request."""
    channel: Optional[str] = None  # SMS, WhatsApp, Email, Chat
    language: Optional[str] = None
    locale: Optional[str] = None  # e.g., IN


class HoneypotRequest(BaseModel):
    """Incoming request from the platform."""
    sessionId: str
    message: Message
    conversationHistory: List[Message] = Field(default_factory=list)
    metadata: Optional[Metadata] = None


class HoneypotResponse(BaseModel):
    """API response format."""
    status: str = "success"
    reply: str


class ExtractedIntelligence(BaseModel):
    """Intelligence extracted from conversation (for callback)."""
    bankAccounts: List[str] = Field(default_factory=list)
    upiIds: List[str] = Field(default_factory=list)
    phishingLinks: List[str] = Field(default_factory=list)
    phoneNumbers: List[str] = Field(default_factory=list)
    suspiciousKeywords: List[str] = Field(default_factory=list)
