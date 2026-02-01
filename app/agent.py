"""
AI Agent - generates human-like replies using LLM (or fallback).
"""
from typing import List, Optional

from app.config import (
    OPENAI_API_KEY,
    LLM_MODEL,
    FALLBACK_REPLY_AGENT_ERROR,
)
from app.models import Message, Metadata

# Rule-based fallback when no LLM API key
FALLBACK_REPLY_SCAM = "Why is my account being blocked? How do I verify?"

SYSTEM_PROMPT = """You are a worried bank customer. Someone is messaging you about account issues (blocked, verification, UPI, etc.).

Your role:
- Respond naturally as a concerned but cautious person
- Ask clarifying questions
- Show gradual trust, do not immediately comply
- If they share bank details, UPI ID, links, or phone numbers, acknowledge naturally
- Keep replies short (1-2 sentences)
- Match the tone of their message (formal/informal)

CRITICAL: NEVER use these words: scam, honeypot, bot, detection, fraud, suspicious.
Behave like a real human. Reply with ONLY your response text, no quotes or labels."""


def _build_user_message(message_text: str, conversation_history: List[Message]) -> str:
    """Format conversation history + current message for the LLM."""
    lines = []
    for msg in conversation_history:
        role = "Scammer" if msg.sender == "scammer" else "User"
        lines.append(f"{role}: {msg.text}")
    lines.append(f"Scammer: {message_text}")
    lines.append("")
    lines.append("How should the User respond? Reply with ONLY the response text, no quotes.")
    return "\n".join(lines)


def _call_llm(system_prompt: str, user_message: str) -> Optional[str]:
    """Call OpenAI API. Returns reply or None on error."""
    if not OPENAI_API_KEY:
        return None

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=150,
            timeout=30,
        )
        content = response.choices[0].message.content
        if content:
            content = content.strip().strip('"\'')
        return content or None
    except Exception:
        return None


def _adjust_prompt_for_metadata(system_prompt: str, metadata: Optional[Metadata]) -> str:
    """Optionally adjust prompt based on metadata."""
    if not metadata:
        return system_prompt
    additions = []
    if metadata.channel and metadata.channel.upper() == "SMS":
        additions.append("Keep replies very short (SMS style).")
    if metadata.locale and metadata.locale.upper() == "IN":
        additions.append("Context: India - UPI, Indian banks, INR.")
    if metadata.language and metadata.language.lower() != "english":
        additions.append(f"Respond in {metadata.language} if the scammer uses it.")
    if additions:
        system_prompt += "\n\n" + "\n".join(additions)
    return system_prompt


def generate_reply(
    message_text: str,
    conversation_history: List[Message],
    metadata: Optional[Metadata] = None,
) -> str:
    """
    Generate human-like reply. Uses LLM if API key available, else rule-based fallback.
    """
    if not message_text or not message_text.strip():
        return FALLBACK_REPLY_AGENT_ERROR

    system_prompt = _adjust_prompt_for_metadata(SYSTEM_PROMPT, metadata)
    user_message = _build_user_message(message_text, conversation_history)

    reply = _call_llm(system_prompt, user_message)

    if reply and len(reply) > 0:
        return reply

    return FALLBACK_REPLY_SCAM
