#!/usr/bin/env python3
"""
Batch import backdated food entries from a JSON file.

Usage:
    python3 setup/batch_import.py entries.json
    python3 setup/batch_import.py entries.json --dry-run

JSON format:
    [
      {"date":"2026-04-17","name":"Food name","cal":300,"pro":25,"carb":30,"fat":8,"fiber":3},
      ...
    ]
    'fiber' is optional (defaults to 0).
"""

import sys
import os
import json
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FIBER_ESTIMATES = {
    "smoothie": 5,
    "muesli": 3,
    "raspberry": 2,
    "banana": 3,
    "pb2": 1,
    "seeds": 2,
    "chipotle": 10,
    "black beans": 8,
    "supergreens": 4,
    "salad": 3,
    "veggies": 3,
    "roasted veg": 4,
    "fries": 2,
    "quest": 14,
    "red bean": 5,
    "kimchi": 1,
    "pineapple": 1,
    "cottage cheese": 0,
    "chips": 1,
    "platter": 3,
    "halal": 2,
}


def estimate_fiber(name: str) -> float:
    name_lower = name.lower()
    for keyword, fiber in FIBER_ESTIMATES.items():
        if keyword in name_lower:
            return float(fiber)
    return 0.0


def main():
    parser = argparse.ArgumentParser(description='Batch import food entries')
    parser.add_argument('file', help='JSON file with entries')
    parser.add_argument('--dry-run', action='store_true', help='Preview without writing')
    args = parser.parse_args()

    with open(args.file) as f:
        entries = json.load(f)

    if args.dry_run:
        print(f"DRY RUN — {len(entries)} entries (nothing will be written)\n")
    else:
        from lib.sheets import log_food
        print(f"Importing {len(entries)} entries...\n")

    by_date: dict[str, list] = {}
    for e in entries:
        by_date.setdefault(e['date'], []).append(e)

    total_logged = 0

    for date in sorted(by_date.keys()):
        day_entries = by_date[date]
        print(f"── {date} ({'DRY RUN' if args.dry_run else 'logging'}) ──")

        day_cal = day_pro = day_carb = day_fat = day_fiber = 0.0

        for e in day_entries:
            fiber = float(e.get('fiber', estimate_fiber(e['name'])))
            cal   = float(e['cal'])
            pro   = float(e['pro'])
            carb  = float(e['carb'])
            fat   = float(e['fat'])

            day_cal   += cal
            day_pro   += pro
            day_carb  += carb
            day_fat   += fat
            day_fiber += fiber

            fiber_note = f"{fiber:.0f}fi" if 'fiber' in e else f"~{fiber:.0f}fi (est)"
            print(f"  {e['name'][:50]:<50}  {cal:>4.0f}cal  {pro:.0f}p/{carb:.0f}c/{fat:.0f}f/{fiber_note}")

            if not args.dry_run:
                log_food(
                    name=e['name'],
                    calories=cal,
                    protein=pro,
                    carbs=carb,
                    fat=fat,
                    fiber=fiber,
                    meal_date=date,
                )
                total_logged += 1

        print(f"  {'TOTAL':<50}  {day_cal:>4.0f}cal  {day_pro:.0f}p/{day_carb:.0f}c/{day_fat:.0f}f/{day_fiber:.0f}fi")
        print()

    if args.dry_run:
        print(f"Would log {len(entries)} entries across {len(by_date)} days.")
        print("Re-run without --dry-run to write to the sheet.")
    else:
        print(f"Done. Logged {total_logged} entries.")


if __name__ == '__main__':
    main()
