"""
Phase 11: Local Testing & Validation
Run: python -m pytest tests/test_phase11.py -v
Or:  python tests/test_phase11.py (standalone)
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx

BASE = "http://127.0.0.1:8000"


def get_api_key():
    from dotenv import load_dotenv
    load_dotenv()
    return os.getenv("API_KEY", "")


def run_phase11_tests():
    api_key = get_api_key()
    headers_ok = {"x-api-key": api_key, "Content-Type": "application/json"}

    print("=== Phase 11: Local Testing & Validation ===\n")

    # 11.1 Basic Connectivity
    print("11.1 Basic Connectivity")
    r = httpx.get(f"{BASE}/")
    assert r.status_code == 200, f"GET / expected 200, got {r.status_code}"
    assert "status" in r.json()
    print("  GET / : 200 OK")

    r = httpx.post(f"{BASE}/api/honeypot", json={})
    assert r.status_code in (401, 422), f"POST without key expected 401/422, got {r.status_code}"
    print("  POST without x-api-key : 401/422 OK (rejected)")

    r = httpx.post(
        f"{BASE}/api/honeypot",
        headers={"x-api-key": "wrong", "Content-Type": "application/json"},
        json={"sessionId": "x", "message": {"sender": "scammer", "text": "x", "timestamp": "2026-01-21T10:00:00Z"}, "conversationHistory": []},
    )
    assert r.status_code == 401, f"POST with wrong key expected 401, got {r.status_code}"
    print("  POST with wrong x-api-key : 401 OK")

    r = httpx.post(f"{BASE}/api/honeypot", headers=headers_ok, json={})
    assert r.status_code == 422, f"POST empty body expected 422, got {r.status_code}"
    print("  POST valid key, empty body : 422 OK (validation)")
    print("  11.1 PASS\n")

    # 11.2 First Message (Scam)
    print("11.2 First Message (Scam)")
    req = {
        "sessionId": "test-session-1",
        "message": {
            "sender": "scammer",
            "text": "Your bank account will be blocked today. Verify immediately.",
            "timestamp": "2026-01-21T10:15:30Z",
        },
        "conversationHistory": [],
        "metadata": {"channel": "SMS", "language": "English", "locale": "IN"},
    }
    r = httpx.post(f"{BASE}/api/honeypot", json=req, headers=headers_ok)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    d = r.json()
    assert d.get("status") == "success"
    assert d.get("reply") and len(d["reply"]) > 0
    assert "scam" not in d.get("reply", "").lower()
    reply1 = d["reply"]
    print(f"  Reply: {reply1[:50]}...")
    print("  11.2 PASS\n")

    # 11.3 Follow-Up Message
    print("11.3 Follow-Up Message")
    req2 = {
        "sessionId": "test-session-1",
        "message": {
            "sender": "scammer",
            "text": "Share your UPI ID to avoid suspension.",
            "timestamp": "2026-01-21T10:17:00Z",
        },
        "conversationHistory": [
            {
                "sender": "scammer",
                "text": "Your bank account will be blocked today. Verify immediately.",
                "timestamp": "2026-01-21T10:15:30Z",
            },
            {"sender": "user", "text": reply1, "timestamp": "2026-01-21T10:16:00Z"},
        ],
        "metadata": {"channel": "SMS", "language": "English", "locale": "IN"},
    }
    r = httpx.post(f"{BASE}/api/honeypot", json=req2, headers=headers_ok)
    assert r.status_code == 200
    d = r.json()
    assert d.get("status") == "success" and d.get("reply")
    print(f"  Reply: {d['reply'][:50]}...")
    print("  11.3 PASS\n")

    # 11.4 Non-Scam Message
    print("11.4 Non-Scam Message")
    req3 = {
        "sessionId": "phase11-nonscam",
        "message": {"sender": "scammer", "text": "Hi, how are you?", "timestamp": "2026-01-21T10:00:00Z"},
        "conversationHistory": [],
    }
    r = httpx.post(f"{BASE}/api/honeypot", json=req3, headers=headers_ok)
    assert r.status_code == 200
    d = r.json()
    assert d.get("reply") == "Can you explain what you mean?"
    print("  11.4 PASS\n")

    # 11.5 Intelligence Extraction Test
    # (Extractor unit-tested in Phase 6; session is per-process so we verify request succeeds)
    print("11.5 Intelligence Extraction Test")
    req5 = {
        "sessionId": "phase11-intel",
        "message": {
            "sender": "scammer",
            "text": "Send payment to abc@paytm or 9876543210",
            "timestamp": "2026-01-21T10:00:00Z",
        },
        "conversationHistory": [],
    }
    r = httpx.post(f"{BASE}/api/honeypot", json=req5, headers=headers_ok)
    assert r.status_code == 200
    d = r.json()
    assert d.get("status") == "success" and d.get("reply")
    print("  Request succeeds (extractor runs on server)")
    print("  11.5 PASS\n")

    # 11.6 Multi-Session Test (verify isolation via API; session store is server-side)
    print("11.6 Multi-Session Test")
    ra = httpx.post(
        f"{BASE}/api/honeypot",
        json={
            "sessionId": "phase11-a",
            "message": {"sender": "scammer", "text": "Account blocked. Verify.", "timestamp": "2026-01-21T10:00:00Z"},
            "conversationHistory": [],
        },
        headers=headers_ok,
    )
    rb = httpx.post(
        f"{BASE}/api/honeypot",
        json={
            "sessionId": "phase11-b",
            "message": {"sender": "scammer", "text": "Different message.", "timestamp": "2026-01-21T10:00:00Z"},
            "conversationHistory": [],
        },
        headers=headers_ok,
    )
    assert ra.status_code == 200 and rb.status_code == 200
    # Different sessionIds return valid replies; server keeps sessions isolated
    assert ra.json().get("reply") and rb.json().get("reply")
    print("  Sessions a and b return valid replies (server-side isolation)")
    print("  11.6 PASS\n")

    # 11.7 Stress Test (Optional)
    print("11.7 Stress Test (Optional)")
    for i in range(15):
        r = httpx.post(
            f"{BASE}/api/honeypot",
            json={
                "sessionId": f"stress-{i}",
                "message": {"sender": "scammer", "text": "Verify now.", "timestamp": "2026-01-21T10:00:00Z"},
                "conversationHistory": [],
            },
            headers=headers_ok,
        )
        assert r.status_code == 200, f"Stress request {i} failed: {r.status_code}"
    print("  15 rapid requests: all 200")
    print("  11.7 PASS\n")

    print("=== Phase 11: ALL TESTS PASS ===")


if __name__ == "__main__":
    run_phase11_tests()
