"""
Phase 13: Tester Compliance — Simulates what the Honeypot Endpoint Tester likely sends.
Run against your DEPLOYED URL before using the official tester.

Usage:
  python tests/test_tester_compliance.py https://YOUR-APP.onrender.com/api/honeypot YOUR_API_KEY

Or set env: TESTER_URL and API_KEY
"""
import os
import sys

# Add project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx


# Payload similar to what the tester likely sends
TEST_PAYLOAD = {
    "sessionId": "test-session-123",
    "message": {
        "sender": "scammer",
        "text": "Your bank account will be blocked today. Verify immediately.",
        "timestamp": "2026-01-21T10:15:30Z",
    },
    "conversationHistory": [],
    "metadata": {
        "channel": "SMS",
        "language": "English",
        "locale": "IN",
    },
}


def run_tester_compliance(url: str, api_key: str) -> bool:
    """Run tester compliance checks against deployed URL. Returns True if all pass."""
    from dotenv import load_dotenv
    load_dotenv()

    if not url or not api_key:
        print("Usage: python test_tester_compliance.py <URL> <API_KEY>")
        print("  Or set TESTER_URL and API_KEY in env")
        return False

    url = url.rstrip("/")
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}

    print("=== Phase 13: Tester Compliance Check ===\n")
    print(f"URL: {url}")
    print(f"API Key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '***'}\n")

    # 1. Without key → expect 401 or 422
    print("1. POST without x-api-key...")
    try:
        r = httpx.post(url, json=TEST_PAYLOAD, headers={"Content-Type": "application/json"}, timeout=30)
        assert r.status_code in (401, 422), f"Expected 401/422, got {r.status_code}"
        print(f"   OK (rejected: {r.status_code})\n")
    except Exception as e:
        print(f"   FAIL: {e}\n")
        return False

    # 2. Wrong key → expect 401
    print("2. POST with wrong x-api-key...")
    try:
        r = httpx.post(url, json=TEST_PAYLOAD, headers={"x-api-key": "wrong-key", "Content-Type": "application/json"}, timeout=30)
        assert r.status_code == 401, f"Expected 401, got {r.status_code}"
        print(f"   OK (401)\n")
    except Exception as e:
        print(f"   FAIL: {e}\n")
        return False

    # 3. Valid request → expect 200 + { status, reply }
    print("3. POST with valid x-api-key and payload...")
    try:
        r = httpx.post(url, json=TEST_PAYLOAD, headers=headers, timeout=30)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        d = r.json()
        assert "status" in d, "Response missing 'status'"
        assert "reply" in d, "Response missing 'reply'"
        assert d.get("status") == "success", f"Expected status='success', got {d.get('status')}"
        assert isinstance(d.get("reply"), str) and len(d["reply"]) > 0, "Reply must be non-empty string"
        print(f"   OK (200)")
        print(f"   Response: {d}\n")
    except Exception as e:
        print(f"   FAIL: {e}\n")
        return False

    print("=== All checks PASS — Ready for official tester ===\n")
    return True


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    url = sys.argv[1] if len(sys.argv) > 1 else os.getenv("TESTER_URL")
    api_key = sys.argv[2] if len(sys.argv) > 2 else os.getenv("API_KEY")
    ok = run_tester_compliance(url, api_key)
    sys.exit(0 if ok else 1)
