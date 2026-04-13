"""Core Google Sheets read/write operations for Macro Tracker."""

from datetime import date, datetime, timedelta
from typing import Optional

import gspread

from lib.auth import get_client
from lib.config import load_config, get_targets

LOG_HEADERS = ['Date', 'Timestamp', 'Meal Name', 'Calories', 'Protein', 'Carbs', 'Fat', 'Fiber']
_HIGH_ACTIVITY_KEY = 'HIGH_ACTIVITY_DAYS'


def _get_worksheets(client: gspread.Client) -> tuple[gspread.Spreadsheet, gspread.Worksheet, gspread.Worksheet]:
    config = load_config()
    if not config.get('spreadsheet_id'):
        raise ValueError(
            "spreadsheet_id not set in config.\n"
            "Run: python3 setup/init_sheet.py"
        )
    spreadsheet = client.open_by_key(config['spreadsheet_id'])
    log_ws = spreadsheet.worksheet('Log')
    config_ws = spreadsheet.worksheet('Config')
    return spreadsheet, log_ws, config_ws


def log_food(
    name: str,
    calories: float,
    protein: float,
    carbs: float,
    fat: float,
    fiber: float,
    meal_date: Optional[str] = None,
) -> dict:
    """Append one food entry to the Log sheet. Returns the logged row as a dict."""
    client = get_client()
    _, log_ws, _ = _get_worksheets(client)

    now = datetime.now()
    entry_date = meal_date or date.today().isoformat()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

    row = [entry_date, timestamp, name,
           round(calories, 1), round(protein, 1),
           round(carbs, 1), round(fat, 1), round(fiber, 1)]
    log_ws.append_row(row, value_input_option='USER_ENTERED')

    return dict(zip(LOG_HEADERS, row))


def get_day_entries(target_date: Optional[str] = None) -> list[dict]:
    """Return all log rows for a given date."""
    client = get_client()
    _, log_ws, _ = _get_worksheets(client)

    target = target_date or date.today().isoformat()
    all_rows = log_ws.get_all_records()
    return [r for r in all_rows if str(r.get('Date', '')).strip() == target]


def get_day_totals(target_date: Optional[str] = None) -> dict:
    """Sum macros for a given date and return totals alongside targets."""
    entries = get_day_entries(target_date)
    target = target_date or date.today().isoformat()
    targets = get_targets(target)

    totals = {
        'date': target,
        'calories': 0.0,
        'protein': 0.0,
        'carbs': 0.0,
        'fat': 0.0,
        'fiber': 0.0,
        'entries': entries,
        'targets': targets,
    }
    for entry in entries:
        totals['calories'] += float(entry.get('Calories', 0) or 0)
        totals['protein'] += float(entry.get('Protein', 0) or 0)
        totals['carbs'] += float(entry.get('Carbs', 0) or 0)
        totals['fat'] += float(entry.get('Fat', 0) or 0)
        totals['fiber'] += float(entry.get('Fiber', 0) or 0)

    # Round totals
    for key in ('calories', 'protein', 'carbs', 'fat', 'fiber'):
        totals[key] = round(totals[key], 1)

    return totals


def get_weekly_summary(days: int = 7) -> list[dict]:
    """Return daily totals for the last N days."""
    today = date.today()
    summary = []
    for i in range(days - 1, -1, -1):
        d = (today - timedelta(days=i)).isoformat()
        summary.append(get_day_totals(d))
    return summary


def get_high_activity_days() -> list[str]:
    """Read high-activity days from the Config sheet (cloud-safe storage)."""
    client = get_client()
    _, _, config_ws = _get_worksheets(client)

    for row in config_ws.get_all_values():
        if row and row[0] == _HIGH_ACTIVITY_KEY:
            raw = row[1] if len(row) > 1 else ''
            return [d.strip() for d in raw.split(',') if d.strip()]
    return []


def add_high_activity_day(date_str: str) -> None:
    """Persist a high-activity day in the Config sheet."""
    client = get_client()
    _, _, config_ws = _get_worksheets(client)

    all_values = config_ws.get_all_values()
    for i, row in enumerate(all_values):
        if row and row[0] == _HIGH_ACTIVITY_KEY:
            existing_raw = row[1] if len(row) > 1 else ''
            existing = [d.strip() for d in existing_raw.split(',') if d.strip()]
            if date_str not in existing:
                existing.append(date_str)
            config_ws.update_cell(i + 1, 2, ','.join(existing))
            return

    # Key row doesn't exist yet — append it
    config_ws.append_row([_HIGH_ACTIVITY_KEY, date_str], value_input_option='USER_ENTERED')


def undo_last_entry() -> Optional[dict]:
    """Delete the last row in the Log sheet. Returns the deleted row or None."""
    client = get_client()
    _, log_ws, _ = _get_worksheets(client)

    all_values = log_ws.get_all_values()
    if len(all_values) <= 1:
        return None

    last_row_data = dict(zip(LOG_HEADERS, all_values[-1]))
    log_ws.delete_rows(len(all_values))
    return last_row_data
