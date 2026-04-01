import json
from app.config import PROFILES_FILE, STATE_FILE


def load_profiles() -> dict:
    with open(PROFILES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_profiles(data: dict) -> None:
    with open(PROFILES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_state() -> dict:
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
