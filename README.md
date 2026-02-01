# Agentic Honey-Pot — Scam Detection & Intelligence Extraction

AI-powered honeypot API that detects scam messages, engages scammers autonomously, and extracts actionable intelligence.

## Project Structure

```
agentic-honey-pot/
├── app/                 # Application code
│   ├── main.py          # FastAPI app, routes
│   ├── config.py        # Configuration
│   ├── models.py        # Pydantic models
│   ├── detector.py      # Scam detection
│   ├── agent.py         # AI agent (LLM)
│   ├── extractor.py     # Intelligence extraction
│   ├── callback.py      # GUVI callback
│   └── session_store.py # Session state
├── docs/                # All documentation
├── tests/               # Test scripts
├── requirements.txt
├── .env.example
├── Procfile             # For Render/Railway
└── README.md
```

## Setup

1. Create virtual environment: `python -m venv venv`
2. Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
3. Install: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and set `API_KEY` (see [docs/MANUAL_SETUP_GUIDE.md](docs/MANUAL_SETUP_GUIDE.md))
5. Run: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

## Testing

Run local tests (requires server running):

```bash
# Terminal 1: Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Run tests
python tests/test_phase11.py
```

### Manual curl test

```bash
curl -X POST http://localhost:8000/api/honeypot \
  -H "x-api-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"sessionId":"test-1","message":{"sender":"scammer","text":"Your account will be blocked. Verify now.","timestamp":"2026-01-21T10:15:30Z"},"conversationHistory":[],"metadata":{"channel":"SMS","language":"English","locale":"IN"}}'
```

## Deployment

See **[docs/DEPLOYMENT_FULL_GUIDE.md](docs/DEPLOYMENT_FULL_GUIDE.md)** for the full guide: deploy → **Step 1 (API Endpoint Tester)** → **Step 2 (Submission Form)**. Short reference: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

Quick: Push to GitHub → Connect to Render/Railway → Set `API_KEY` env var → Deploy.

---

## Documentation

All docs are in **[docs/](docs/)**. Index: [docs/README.md](docs/README.md).

## Hackathon

Built for GUVI Hackathon — Agentic Honey-Pot for Scam Detection & Intelligence Extraction.
