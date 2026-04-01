import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

BOT_TOKEN = os.getenv("BOT_TOKEN")
PROFILES_FILE = DATA_DIR / "profiles.json"
STATE_FILE = DATA_DIR / "state.json"