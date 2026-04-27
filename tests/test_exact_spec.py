"""
Test deployed API with EXACT request format from Problem Statement 2 (Section 6.1).
Run: python tests/test_exact_spec.py <URL> [API_KEY]
  URL: https://agentic-honey-pot-4g3y.onrender.com/api/honeypot
  API_KEY: from .env if not provided
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()


# EXACT format from Problem Statement 2, Section 6.1 — First Message
EXACT_REQUEST_BODY = {
    "sessionId": "wertyu-dfghj-ertyui",
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


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else None
    api_key = sys.argv[2] if len(sys.argv) > 2 else os.getenv("API_KEY")

    if not url or not api_key:
        print("Usage: python tests/test_exact_spec.py <URL> [API_KEY]")
        print("Example: python tests/test_exact_spec.py https://agentic-honey-pot-4g3y.onrender.com/api/honeypot")
        sys.exit(1)

    url = url.rstrip("/")
    if not url.endswith("/api/honeypot"):
        url = f"{url}/api/honeypot" if "/api/honeypot" not in url else url

    import httpx

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }

    print("Sending EXACT spec request (Problem Statement 2, Section 6.1)...")
    print(f"URL: {url}")
    print(f"Body: {EXACT_REQUEST_BODY}")
    print()

    try:
        r = httpx.post(url, json=EXACT_REQUEST_BODY, headers=headers, timeout=60)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")

        if r.status_code != 200:
            print("\nFAIL: Expected 200")
            sys.exit(1)

        d = r.json()
        if "status" not in d or "reply" not in d:
            print("\nFAIL: Response must have 'status' and 'reply'")
            sys.exit(1)
        if d.get("status") != "success":
            print("\nFAIL: status must be 'success'")
            sys.exit(1)
        if not isinstance(d.get("reply"), str) or len(d["reply"]) == 0:
            print("\nFAIL: reply must be non-empty string")
            sys.exit(1)

        print("\nPASS: API responds correctly to exact spec format")
    except httpx.TimeoutException:
        print("FAIL: Request timed out (Render may be sleeping — wait 60s and retry)")
        sys.exit(1)
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
