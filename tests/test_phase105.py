"""
Phase 105: Pre-Submission Checkpoint
Run: python tests/test_phase105.py [BASE_URL]
  - Without BASE_URL: code-level verification only
  - With BASE_URL: full deployment + sanity checks (set API_KEY in env)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()


def run_code_checks():
    """105.1, 105.4 — Code-level verification."""
    print("=== Phase 105: Pre-Submission Checkpoint ===\n")

    # 105.1 — No localhost in app code
    print("105.1 Deployment Verification (code)")
    app_dir = os.path.join(os.path.dirname(__file__), "..", "app")
    for root, _, files in os.walk(app_dir):
        for f in files:
            if not f.endswith(".py"):
                continue
            path = os.path.join(root, f)
            with open(path, encoding="utf-8") as fp:
                content = fp.read()
            assert "localhost" not in content and "127.0.0.1" not in content, (
                f"Found localhost in {path}"
            )
    print("  No localhost in app code: OK")

    # Procfile exists
    procfile = os.path.join(os.path.dirname(__file__), "..", "Procfile")
    assert os.path.exists(procfile), "Procfile missing"
    with open(procfile) as f:
        p = f.read()
    assert "uvicorn" in p and "0.0.0.0" in p
    print("  Procfile correct: OK\n")

    # 105.4 Critical Requirements
    print("105.4 Critical Requirements Re-Check")
    from app.config import CALLBACK_URL
    from app.callback import build_callback_payload
    from app.models import ExtractedIntelligence

    assert CALLBACK_URL == "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
    print("  Callback URL correct: OK")

    p = build_callback_payload("s", True, 10, ExtractedIntelligence(upiIds=["x@upi"]))
    for k in ["sessionId", "scamDetected", "totalMessagesExchanged", "extractedIntelligence", "agentNotes"]:
        assert k in p
    ei = p["extractedIntelligence"]
    for k in ["bankAccounts", "upiIds", "phishingLinks", "phoneNumbers", "suspiciousKeywords"]:
        assert k in ei and isinstance(ei[k], list)
    print("  Callback payload structure: OK")

    from app.models import HoneypotRequest, HoneypotResponse, Message
    req_fields = HoneypotRequest.model_fields if hasattr(HoneypotRequest, "model_fields") else getattr(HoneypotRequest, "__fields__", {})
    assert "sessionId" in req_fields and "message" in req_fields
    resp_fields = HoneypotResponse.model_fields if hasattr(HoneypotResponse, "model_fields") else getattr(HoneypotResponse, "__fields__", {})
    assert "status" in resp_fields and "reply" in resp_fields
    print("  API request/response format: OK\n")


def run_deployment_checks(base_url: str, api_key: str):
    """105.1, 105.3 — Deployment and sanity checks."""
    import httpx

    url = base_url.rstrip("/")
    if not url.endswith("/api/honeypot"):
        url = f"{url}/api/honeypot"
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}

    print("105.1 Deployment Verification (production)")
    try:
        r = httpx.get(url.rsplit("/api", 1)[0] or url, timeout=15)
        print(f"  Root reachable: {r.status_code}")
    except Exception as e:
        print(f"  Root: {e}")

    r = httpx.post(
        url,
        json={
            "sessionId": "c105",
            "message": {"sender": "scammer", "text": "Verify now.", "timestamp": "2026-01-21T10:00:00Z"},
            "conversationHistory": [],
        },
        headers=headers,
        timeout=30,
    )
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    d = r.json()
    assert d.get("status") == "success" and d.get("reply")
    print("  POST returns 200 + valid response: OK\n")

    print("105.3 Post-Tester Sanity Check (5 requests)")
    payloads = [
        ("s1", "Your account blocked. Verify.", True),
        ("s2", "Share UPI to verify", True),
        ("s3", "Hi, how are you?", False),
        ("s4", "Click link to verify", True),
        ("s5", "Random chat", False),
    ]
    for sid, text, is_scam in payloads:
        r = httpx.post(
            url,
            json={"sessionId": sid, "message": {"sender": "scammer", "text": text, "timestamp": "2026-01-21T10:00:00Z"}, "conversationHistory": []},
            headers=headers,
            timeout=30,
        )
        assert r.status_code == 200, f"Session {sid}: {r.status_code}"
        d = r.json()
        assert d.get("status") == "success" and d.get("reply")
    print("  5 requests (scam + non-scam): all 200 OK\n")


def main():
    run_code_checks()

    base_url = sys.argv[1] if len(sys.argv) > 1 else os.getenv("PHASE105_BASE_URL")
    api_key = os.getenv("API_KEY")

    if base_url and api_key:
        print("Running deployment checks against:", base_url)
        run_deployment_checks(base_url, api_key)
    else:
        print("(Skipping deployment checks — set PHASE105_BASE_URL and API_KEY for full verification)\n")

    print("=== Phase 105: Code checks PASS ===\n")
    print("105.2 Endpoint Tester: Run official tester; document URL and key in PHASE13_TESTER_GUIDE.")
    print("105.5 Sign-off: Proceed to Phase 14 when deployment stable and tester passed.")


if __name__ == "__main__":
    main()
