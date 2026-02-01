"""
Configuration - environment variables and constants.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Required: API key for honeypot endpoint (must match x-api-key header)
API_KEY = os.getenv("API_KEY", "").strip()
if not API_KEY:
    raise ValueError(
        "API_KEY is required. Set it in .env file or environment. "
        "Example: API_KEY=your-secret-api-key"
    )

# Optional: OpenAI API key for LLM agent
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip() or None

# Callback configuration
CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
CALLBACK_RETRY_COUNT = 3
CALLBACK_TIMEOUT = 5  # seconds
MIN_TURNS_BEFORE_CALLBACK = 5

# LLM configuration
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# Fallback replies
FALLBACK_REPLY_NON_SCAM = "Can you explain what you mean?"
FALLBACK_REPLY_AGENT_ERROR = "I'm not sure, could you please explain?"
