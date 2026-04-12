"""Config file management for Macro Tracker."""

import os
import json

CONFIG_DIR = os.path.expanduser('~/.macrotracker')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
CREDS_FILE = os.path.join(CONFIG_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(CONFIG_DIR, 'token.json')

DEFAULT_CONFIG = {
    "spreadsheet_id": "",
    "staples": {
        "super coffee": {
            "name": "Super Coffee Protein+ Mocha",
            "calories": 150,
            "protein": 25,
            "carbs": 8,
            "fat": 3,
            "fiber": 0
        },
        "apple": {
            "name": "Apple",
            "calories": 85,
            "protein": 0,
            "carbs": 22,
            "fat": 0,
            "fiber": 4
        },
        "meal prep": {
            "name": "Meal Prep (chicken/rice/veg)",
            "calories": 500,
            "protein": 42,
            "carbs": 52,
            "fat": 9,
            "fiber": 5
        }
    },
    "targets": {
        "standard": {
            "calories": 1500,
            "protein": 125,
            "carbs": 125,
            "fat": 32,
            "fiber": 30
        },
        "high_activity": {
            "calories": 2000,
            "protein": 125,
            "carbs": 125,
            "fat": 35,
            "fiber": 30
        }
    },
    "high_activity_days": []
}


def load_config() -> dict:
    """Load config from ~/.macrotracker/config.json."""
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(
            f"Config not found at {CONFIG_FILE}\n"
            "Run: python3 setup/init_sheet.py"
        )
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def save_config(config: dict) -> None:
    """Save config to ~/.macrotracker/config.json."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def lookup_staple(query: str) -> dict | None:
    """Find a staple by name using case-insensitive substring matching."""
    config = load_config()
    q = query.lower().strip()

    for key, staple in config.get('staples', {}).items():
        if q in key.lower() or key.lower() in q:
            return staple
        if q in staple['name'].lower():
            return staple

    return None


def get_targets(target_date: str | None = None) -> dict:
    """Return macro targets for a given date (standard or high-activity)."""
    from datetime import date as dt_date
    config = load_config()
    target = target_date or dt_date.today().isoformat()

    if target in config.get('high_activity_days', []):
        return config['targets']['high_activity']
    return config['targets']['standard']


def mark_high_activity(target_date: str | None = None) -> str:
    """Mark a date as a high-activity day."""
    from datetime import date as dt_date
    config = load_config()
    target = target_date or dt_date.today().isoformat()

    if 'high_activity_days' not in config:
        config['high_activity_days'] = []
    if target not in config['high_activity_days']:
        config['high_activity_days'].append(target)
        save_config(config)

    return target
