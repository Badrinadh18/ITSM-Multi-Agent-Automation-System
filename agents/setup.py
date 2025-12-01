# agents/setup.py
# -------------------------------------------------------------
# ADK Setup: loads .env, configures logging, and initializes LLM
# -------------------------------------------------------------

import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

from google.genai import types
from google.adk.models.google_llm import Gemini


# Load API Key
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("❌ GOOGLE_API_KEY missing in .env")

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
print("🔐 GOOGLE_API_KEY loaded.")

# Logging
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")

handler = RotatingFileHandler(LOG_FILE, maxBytes=2_000_000, backupCount=5)
logging.basicConfig(
    level=logging.INFO,
    handlers=[handler],
    format="%(asctime)s [%(levelname)s] %(message)s",
)

print("📝 Logging configured → logs/app.log")


# Retry config
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)


# LLM Factory
def LLM():
    return Gemini(
        model="gemini-2.5-flash-lite",
        retry_options=retry_config,
    )


print("✨ ADK Setup complete.")
