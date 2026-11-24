"""Local configuration; no credentials belong in source control."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=False)
TOKEN = os.getenv("DISCORD_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MOEDA_EMOJI = os.getenv("MOEDA_EMOJI", "💰")
ID_CARGO_MEMBRO = int(os.getenv("ID_CARGO_MEMBRO", "0"))
ID_CANAL_LOGS = int(os.getenv("ID_CANAL_LOGS", "0"))
DATABASE_PATH = os.getenv("DATABASE_PATH", "emblemas.db")
