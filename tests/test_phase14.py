"""
Phase 14: Polish & Submission Preparation — Verification
Run: python tests/test_phase14.py [BASE_URL]
  - Without BASE_URL: unit tests (extractor, detector, agent)
  - With BASE_URL: stability check (20+ requests)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()


def test_scam_detection():
    """14.3 Scam detection tuning."""
    from app.detector import detect_scam

    assert detect_scam("Your account will be blocked. Verify immediately.", []) is True
    assert detect_scam("Share your UPI to avoid suspension.", []) is True
    assert detect_scam("Hi", []) is False
    assert detect_scam("Hello, how are you?", []) is False
    assert detect_scam("", []) is False
    print("14.3 Scam detection: OK")


def test_extraction():
    """14.4 Intelligence extraction completeness."""
    from app.extractor import extract_intelligence

    i = extract_intelligence("Send to xyz@paytm or abc@ybl")
    assert any("paytm" in u.lower() or "ybl" in u.lower() for u in i.upiIds)
    assert len(i.upiIds) >= 2

    i = extract_intelligence("Call +919876543210 or 9876543210")
    assert any("9876543210" in p or "876543210" in p for p in i.phoneNumbers)
    assert len(i.phoneNumbers) >= 1

    i = extract_intelligence("Click https://evil.com/verify")
    assert any("evil.com" in l for l in i.phishingLinks)
    assert len(i.phishingLinks) >= 1

    i = extract_intelligence("Account 1234 5678 9012 3456")
    assert len(i.bankAccounts) >= 1
    print("14.4 Intelligence extraction: OK")


def test_agent_prompt():
    """14.2 Agent quality — prompt instructs never to use forbidden keywords."""
    from app.agent import SYSTEM_PROMPT

    assert "never" in SYSTEM_PROMPT.lower() and "scam" in SYSTEM_PROMPT.lower()
    assert "gradual trust" in SYSTEM_PROMPT.lower()
    assert "ask" in SYSTEM_PROMPT.lower()
    # Agent output must not contain these (verified via generate_reply tests)
    from app.agent import generate_reply
    reply = generate_reply("Verify now", [])
    for w in ["scam", "honeypot", "bot", "detection"]:
        assert w not in reply.lower()
    print("14.2 Agent prompt: OK")


def test_metadata_usage():
    """14.5 Metadata usage — agent accepts metadata."""
    from app.agent import generate_reply
    from app.models import Message, Metadata

    reply = generate_reply("Verify now", [], metadata=Metadata(channel="SMS", locale="IN"))
    assert reply and len(reply) > 0
    reply2 = generate_reply("Verify now", [], metadata=None)
    assert reply2 and len(reply2) > 0
    print("14.5 Metadata usage: OK")


def test_stability(base_url: str, api_key: str, n: int = 25):
    """14.7 Stability check — rapid requests, no 500s."""
    import httpx

    url = base_url.rstrip("/")
    if not url.endswith("/api/honeypot"):
        url = f"{url}/api/honeypot"
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}

    for i in range(n):
        r = httpx.post(
            url,
            json={
                "sessionId": f"phase14-stability-{i}",
                "message": {"sender": "scammer", "text": "Verify now.", "timestamp": "2026-01-21T10:00:00Z"},
                "conversationHistory": [],
            },
            headers=headers,
            timeout=15,
        )
        assert r.status_code == 200, f"Request {i}: {r.status_code}"
        d = r.json()
        assert d.get("status") == "success" and d.get("reply")
    print(f"14.7 Stability: {n} requests OK")


def main():
    print("=== Phase 14: Polish Verification ===\n")

    test_scam_detection()
    test_extraction()
    test_agent_prompt()
    test_metadata_usage()

    base_url = sys.argv[1] if len(sys.argv) > 1 else os.getenv("PHASE14_BASE_URL")
    api_key = os.getenv("API_KEY")
    if base_url and api_key:
        print("\nRunning stability check...")
        test_stability(base_url, api_key)

    print("\n=== Phase 14: All polish checks PASS ===")


if __name__ == "__main__":
    main()
