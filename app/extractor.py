"""
Intelligence extraction - UPI, bank accounts, links, phone numbers, keywords.
"""
import re
from typing import List

from app.models import Message, ExtractedIntelligence

# UPI: xxx@paytm, xxx@ybl, xxx@okaxis, etc. or generic xxx@xxx
UPI_PATTERN = re.compile(
    r"\b[\w][\w.-]*@(?:paytm|ybl|okaxis|phonepe|paypal|bank|upi|axl|ibl|icici|kotak|"
    r"okbizaxis|fam|jupiteraxis|indus|federal|postbank|sbi|hdfc|pnb|payzapp|[\w.-]+)\b",
    re.IGNORECASE
)
# Fallback: any email-like for UPI (xxx@xxx)
UPI_FALLBACK_PATTERN = re.compile(r"\b[\w][\w.-]*@[\w.-]+\b")

# Bank account: 9-18 digits, optionally with spaces/dashes
BANK_PATTERN = re.compile(
    r"\b(?:(?:\d{4}[\s-]?){2,4}\d{0,6}|\d{9,18})\b"
)
# Filter: exclude pure years (4 digits only), timestamps
YEAR_PATTERN = re.compile(r"^\d{4}$")

# URLs
URL_PATTERN = re.compile(r"https?://[^\s<>\"']+")

# Indian phone: +91 followed by 6-9 and 9 digits, or 10 digits starting with 6-9
PHONE_PATTERN = re.compile(
    r"(?:\+91[-\s]?)?[6-9]\d{9}\b|"
    r"\+91[6-9]\d{9}\b"
)

# Suspicious keywords to extract
SUSPICIOUS_KEYWORDS = [
    "urgent", "immediately", "blocked", "verify", "suspended", "account",
    "upi", "bank", "payment", "transfer", "click", "link", "otp",
    "compliance", "official", "verification"
]


def _extract_upi(text: str) -> List[str]:
    """Extract UPI IDs from text."""
    matches = UPI_PATTERN.findall(text)
    if not matches:
        matches = UPI_FALLBACK_PATTERN.findall(text)
    return list(dict.fromkeys(matches))


def _extract_bank_accounts(text: str) -> List[str]:
    """Extract bank account-like sequences."""
    results = []
    for match in BANK_PATTERN.finditer(text):
        val = match.group().replace(" ", "").replace("-", "")
        if len(val) < 9:
            continue
        if YEAR_PATTERN.match(val):
            continue
        results.append(val)
    return list(dict.fromkeys(results))


def _extract_links(text: str) -> List[str]:
    """Extract URLs from text."""
    matches = URL_PATTERN.findall(text)
    return list(dict.fromkeys(matches))


def _extract_phones(text: str) -> List[str]:
    """Extract Indian phone numbers."""
    results = []
    for match in PHONE_PATTERN.finditer(text):
        val = re.sub(r"[-\s]", "", match.group())
        if val.startswith("+91"):
            val = val
        elif len(val) == 10:
            val = "+91" + val
        if len(val) >= 12:
            results.append(val)
    return list(dict.fromkeys(results))


def _extract_suspicious_keywords(text: str) -> List[str]:
    """Extract suspicious keywords present in text."""
    text_lower = text.lower()
    found = [kw for kw in SUSPICIOUS_KEYWORDS if kw in text_lower]
    return list(dict.fromkeys(found))


def extract_intelligence(text: str) -> ExtractedIntelligence:
    """Extract all intelligence from a single text."""
    if not text:
        return ExtractedIntelligence()

    return ExtractedIntelligence(
        bankAccounts=_extract_bank_accounts(text),
        upiIds=_extract_upi(text),
        phishingLinks=_extract_links(text),
        phoneNumbers=_extract_phones(text),
        suspiciousKeywords=_extract_suspicious_keywords(text),
    )


def _merge_intelligence(a: ExtractedIntelligence, b: ExtractedIntelligence) -> ExtractedIntelligence:
    """Merge two ExtractedIntelligence objects, deduplicating."""
    def merge_lists(la: List[str], lb: List[str]) -> List[str]:
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


def extract_from_conversation(
    conversation_history: List[Message],
    current_message: str
) -> ExtractedIntelligence:
    """
    Extract intelligence from full conversation.
    Combines scammer messages + current message.
    """
    texts = []
    for msg in conversation_history:
        if msg.sender == "scammer" and msg.text:
            texts.append(msg.text)
    if current_message:
        texts.append(current_message)
    combined = " ".join(texts)
    return extract_intelligence(combined)
