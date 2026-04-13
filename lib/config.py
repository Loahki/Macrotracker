"""Config file management for Macro Tracker.

Local mode:  reads ~/.macrotracker/config.json
Cloud mode:  reads SPREADSHEET_ID env var + uses built-in defaults
             high_activity_days are stored in the Google Sheet Config tab
"""

import json
import os

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


def _is_cloud_mode() -> bool:
    return bool(os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON'))


def load_config() -> dict:
    """Load config. Uses env vars in cloud mode, config file locally."""
    # Start with defaults
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    else:
        config = DEFAULT_CONFIG.copy()

    # SPREADSHEET_ID env var always wins
    spreadsheet_id = os.environ.get('SPREADSHEET_ID')
    if spreadsheet_id:
        config['spreadsheet_id'] = spreadsheet_id

    if not config.get('spreadsheet_id'):
        raise ValueError(
            "spreadsheet_id not set.\n"
            "Local: run python3 setup/init_sheet.py\n"
            "Cloud: set the SPREADSHEET_ID environment variable"
        )

    return config


def save_config(config: dict) -> None:
    """Save config to ~/.macrotracker/config.json (local only)."""
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

    if _is_cloud_mode():
        from lib.sheets import get_high_activity_days
        high_activity_days = get_high_activity_days()
    else:
        high_activity_days = config.get('high_activity_days', [])

    if target in high_activity_days:
        return config['targets']['high_activity']
    return config['targets']['standard']


def mark_high_activity(target_date: str | None = None) -> str:
    """Mark a date as a high-activity day."""
    from datetime import date as dt_date
    target = target_date or dt_date.today().isoformat()

    if _is_cloud_mode():
        from lib.sheets import add_high_activity_day
        add_high_activity_day(target)
    else:
        config = load_config()
        if 'high_activity_days' not in config:
            config['high_activity_days'] = []
        if target not in config['high_activity_days']:
            config['high_activity_days'].append(target)
            save_config(config)

    return target
