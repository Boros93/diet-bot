# AGENTS.md

## Project overview

This repository contains a personal Telegram bot for food-equivalence calculations.

Primary goals:
- manage two fixed profiles: `A` and `Y`
- store food tables locally in JSON
- allow selecting the active profile
- convert quantities between equivalent foods in the same group
- compute remaining quota after eating part of a food
- keep the implementation simple, local-first, and easy to run

Tech constraints:
- Python 3.10+
- aiogram 3.x
- long polling
- local JSON files for configuration/state
- no database unless explicitly requested later

---

## Product rules

The bot is for personal use only.

There are only two supported profiles:
- `A`
- `Y`

Do not introduce:
- Telegram user-based identity
- authentication
- multi-user database logic
- admin panels
- unnecessary cloud infrastructure

The bot must work with a single active profile stored locally.

Core commands:
- `/start`
- `/help`
- `/profili`
- `/profilo <A|Y>`
- `/tabella`
- `/converti <qty> <from_food> <to_food>`
- `/residuo <qty> <food>`

Examples:
- `/profilo A`
- `/converti 20 pane patate`
- `/residuo 20 pane`

---

## Data model

Profiles are stored in `data/profiles.json`.

Expected structure:

```json
{
  "profiles": {
    "A": {
      "groups": {
        "carboidrati": {
          "items": {
            "pane":   { "qty": 60, "unit": "g" },
            "patate": { "qty": 220, "unit": "g" },
            "pasta":  { "qty": 80, "unit": "g" },
            "riso":   { "qty": 70, "unit": "g" }
          }
        }
      }
    },
    "Y": {
      "groups": {
        "carboidrati": {
          "items": {
            "pane":   { "qty": 80, "unit": "g" },
            "patate": { "qty": 300, "unit": "g" },
            "pasta":  { "qty": 100, "unit": "g" },
            "riso":   { "qty": 90, "unit": "g" }
          }
        }
      }
    }
  }
}