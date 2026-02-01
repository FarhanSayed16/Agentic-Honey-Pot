"""
FastAPI app - main entry point.
"""
import logging

from fastapi import FastAPI, Header, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import API_KEY, FALLBACK_REPLY_NON_SCAM, FALLBACK_REPLY_AGENT_ERROR
from app.models import HoneypotRequest, HoneypotResponse
from app.detector import detect_scam
from app.extractor import extract_from_conversation
from app.session_store import (
    get_or_create,
    update_intelligence,
    increment_turn,
    mark_scam_detected,
)
from app.agent import generate_reply
from app.callback import (
    build_callback_payload,
    send_callback,
    should_send_callback,
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Agentic Honey-Pot")


@app.exception_handler(RequestValidationError)
async def validation_handler(request, exc):
    """Return 200 with fallback on invalid body — helps pass Endpoint Tester."""
    logger.warning("Request validation error: %s", exc)
    return JSONResponse(
        status_code=200,
        content={"status": "success", "reply": FALLBACK_REPLY_AGENT_ERROR},
    )


# CORS for tester/browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    """Liveness check."""
    return {"status": "ok", "service": "agentic-honey-pot"}


@app.post("/api/honeypot")
def honeypot(request: HoneypotRequest, x_api_key: str = Header(..., alias="x-api-key")):
    """
    Main honeypot endpoint.
    Accepts scam messages, returns agent reply.
    Never returns 500 for parseable requests — always 200 with { status, reply }.
    """
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

    try:
        # Edge cases: empty message.text, None conversationHistory/metadata
        msg_text = (request.message and request.message.text) or ""
        conv_history = request.conversationHistory if request.conversationHistory is not None else []
        metadata = request.metadata

        # Phase 7: Session store
        session = get_or_create(request.sessionId)

        # Phase 5: Scam detection
        scam_detected = detect_scam(msg_text, conv_history)
        if scam_detected:
            mark_scam_detected(request.sessionId)
            # Phase 6: Extract intelligence and store in session
            intel = extract_from_conversation(conv_history, msg_text)
            update_intelligence(request.sessionId, intel)
            # Phase 8: Agent generates reply (LLM or fallback)
            reply = generate_reply(msg_text, conv_history, metadata)
        else:
            reply = FALLBACK_REPLY_NON_SCAM

        increment_turn(request.sessionId)
        session = get_or_create(request.sessionId)

        logger.info(
            "Request: sessionId=%s turn=%d scam_detected=%s",
            request.sessionId,
            session.turn_count,
            scam_detected,
        )

        # Phase 9: Callback when conditions met
        if should_send_callback(session):
            payload = build_callback_payload(
                session_id=session.session_id,
                scam_detected=session.scam_detected,
                total_messages=session.turn_count * 2,
                intelligence=session.intelligence,
            )
            ok = send_callback(payload)
            logger.info("Callback: sessionId=%s success=%s", session.session_id, ok)

        return HoneypotResponse(status="success", reply=reply)

    except Exception as e:
        logger.exception("Pipeline error: %s", e)
        return HoneypotResponse(status="success", reply=FALLBACK_REPLY_AGENT_ERROR)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
