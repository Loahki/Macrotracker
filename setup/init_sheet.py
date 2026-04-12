#!/usr/bin/env python3
"""
One-time setup: creates the 'Macro Tracker' Google Sheet with Log and Config tabs,
then writes the spreadsheet ID and default staples into ~/.macrotracker/config.json.

Run once after completing Google Cloud Console OAuth setup:
    python3 setup/init_sheet.py
"""

import sys
import os

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from lib.auth import get_client
from lib.config import DEFAULT_CONFIG, CONFIG_DIR, CONFIG_FILE, save_config

LOG_HEADERS = ['Date', 'Timestamp', 'Meal Name', 'Calories', 'Protein', 'Carbs', 'Fat', 'Fiber']

CONFIG_SECTION_STAPLES = [
    ['--- STAPLES ---', '', '', '', '', '', ''],
    ['Key', 'Name', 'Calories', 'Protein', 'Carbs', 'Fat', 'Fiber'],
    ['super coffee', 'Super Coffee Protein+ Mocha', 150, 25, 8, 3, 0],
    ['apple',        'Apple',                        85,  0, 22, 0, 4],
    ['meal prep',    'Meal Prep (chicken/rice/veg)', 500, 42, 52, 9, 5],
]

CONFIG_SECTION_TARGETS = [
    [''],
    ['--- TARGETS ---', '', ''],
    ['Type', 'Calories', 'Protein', 'Carbs', 'Fat', 'Fiber'],
    ['standard',      1500, 125, 125, 32, 30],
    ['high_activity', 2000, 125, 125, 35, 30],
]


def main():
    print("Macro Tracker — Sheet Initializer")
    print("=" * 40)

    print("\nAuthenticating with Google...")
    print("A browser window will open for OAuth consent.\n")
    client = get_client()
    print("Authentication successful!")

    # Check for existing sheet
    existing_id = ""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            existing = json.load(f)
        existing_id = existing.get('spreadsheet_id', '')

    if existing_id:
        print(f"\nExisting spreadsheet_id found: {existing_id}")
        answer = input("Re-use existing sheet? [Y/n]: ").strip().lower()
        if answer not in ('n', 'no'):
            print("Using existing sheet. Config unchanged.")
            _verify_worksheets(client, existing_id)
            return

    print("\nCreating 'Macro Tracker' Google Sheet...")
    spreadsheet = client.create('Macro Tracker')
    spreadsheet_id = spreadsheet.id
    print(f"Created: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")

    # Rename default sheet to 'Log'
    sheet1 = spreadsheet.sheet1
    sheet1.update_title('Log')

    # Set up Log tab headers
    sheet1.append_row(LOG_HEADERS, value_input_option='USER_ENTERED')
    sheet1.format('A1:H1', {
        'textFormat': {'bold': True},
        'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
    })

    # Create Config tab
    config_ws = spreadsheet.add_worksheet(title='Config', rows=50, cols=10)

    for row in CONFIG_SECTION_STAPLES:
        config_ws.append_row(row, value_input_option='USER_ENTERED')
    for row in CONFIG_SECTION_TARGETS:
        config_ws.append_row(row, value_input_option='USER_ENTERED')

    print("Worksheets created: Log, Config")

    # Save config
    config = DEFAULT_CONFIG.copy()
    config['spreadsheet_id'] = spreadsheet_id

    os.makedirs(CONFIG_DIR, exist_ok=True)
    save_config(config)
    print(f"\nConfig saved to: {CONFIG_FILE}")

    print("\n" + "=" * 40)
    print("Setup complete!")
    print(f"\nSheet URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
    print("\nNext steps:")
    print("  1. Test CLI:        macros today")
    print("  2. Log a meal:      macros log 'super coffee'")
    print("  3. Start dashboard: python3 dashboard/server.py")


def _verify_worksheets(client, spreadsheet_id: str):
    """Verify Log and Config worksheets exist; create them if missing."""
    spreadsheet = client.open_by_key(spreadsheet_id)
    titles = [ws.title for ws in spreadsheet.worksheets()]

    if 'Log' not in titles:
        ws = spreadsheet.add_worksheet(title='Log', rows=5000, cols=10)
        ws.append_row(LOG_HEADERS, value_input_option='USER_ENTERED')
        print("Created missing 'Log' worksheet.")

    if 'Config' not in titles:
        config_ws = spreadsheet.add_worksheet(title='Config', rows=50, cols=10)
        for row in CONFIG_SECTION_STAPLES + CONFIG_SECTION_TARGETS:
            config_ws.append_row(row, value_input_option='USER_ENTERED')
        print("Created missing 'Config' worksheet.")

    print("Sheet structure verified.")


if __name__ == '__main__':
    main()
