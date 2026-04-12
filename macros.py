#!/usr/bin/env python3
"""
macros — CLI for the Macro Tracker Google Sheet.

Commands:
  macros log "Super Coffee"                       # log staple by name
  macros log "6oz chicken" --cal 280 --pro 52 --carb 0 --fat 6 --fiber 0
  macros today                                    # today's totals vs targets
  macros summary [--days N]                       # last 7 days (default)
  macros high [--date YYYY-MM-DD]                 # mark day as high-activity
  macros undo                                     # remove last log entry
  macros staples                                  # list all configured staples
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from colorama import Fore, Style, init as colorama_init
from tabulate import tabulate

colorama_init(autoreset=True)


# ── formatting helpers ────────────────────────────────────────────────────────

BAR_WIDTH = 20

def _bar(value: float, target: float, reverse: bool = False) -> str:
    """Return a coloured ASCII progress bar."""
    pct = value / target if target else 0
    filled = min(int(pct * BAR_WIDTH), BAR_WIDTH)
    bar = '█' * filled + '░' * (BAR_WIDTH - filled)

    if reverse:                          # higher is better (e.g. fiber)
        if pct >= 0.85:
            colour = Fore.GREEN
        elif pct >= 0.50:
            colour = Fore.YELLOW
        else:
            colour = Fore.RED
    else:                                # lower-or-equal is better
        if pct > 1.0:
            colour = Fore.RED
        elif pct >= 0.85:
            colour = Fore.YELLOW
        else:
            colour = Fore.GREEN

    return colour + bar + Style.RESET_ALL + f' {pct*100:.0f}%'


def _print_totals(day_data: dict, label: str = '') -> None:
    t = day_data['targets']
    is_high = t['calories'] == 2000
    day_type = Fore.CYAN + 'High-Activity Day' + Style.RESET_ALL if is_high else 'Standard Day'

    print(f"\n{Style.BRIGHT}{label or day_data['date']}  ({day_type})")
    print('─' * 56)

    rows = [
        ('Calories', day_data['calories'], t['calories'], 'kcal', False),
        ('Protein',  day_data['protein'],  t['protein'],  'g',    True),
        ('Carbs',    day_data['carbs'],    t['carbs'],    'g',    False),
        ('Fat',      day_data['fat'],      t['fat'],      'g',    False),
        ('Fiber',    day_data['fiber'],    t['fiber'],    'g',    True),
    ]
    for name, val, tgt, unit, rev in rows:
        progress = _bar(val, tgt, reverse=rev)
        print(f"  {name:<10} {val:>6.0f} / {tgt:<4.0f}{unit}  {progress}")

    print('─' * 56)
    entries = day_data.get('entries', [])
    if entries:
        print(f"\n  {Style.BRIGHT}Meals logged today ({len(entries)}){Style.RESET_ALL}")
        for e in entries:
            ts = str(e.get('Timestamp', ''))[-8:-3]   # HH:MM
            name = e.get('Meal Name', '')[:32]
            cal = float(e.get('Calories', 0) or 0)
            pro = float(e.get('Protein',  0) or 0)
            carb = float(e.get('Carbs',   0) or 0)
            fat  = float(e.get('Fat',     0) or 0)
            fib  = float(e.get('Fiber',   0) or 0)
            print(f"  {ts}  {name:<32}  {cal:>4.0f}cal  {pro:.0f}p/{carb:.0f}c/{fat:.0f}f/{fib:.0f}fi")
    print()


# ── command implementations ───────────────────────────────────────────────────

def cmd_log(args):
    from lib.config import lookup_staple
    from lib.sheets import log_food, get_day_totals

    name = args.name
    staple = lookup_staple(name) if not any([args.cal, args.pro, args.carb, args.fat is not None, args.fiber is not None]) else None

    if staple:
        item = staple
        display_name = staple['name']
    else:
        # Require all macros when not a known staple
        missing = [f for f, v in [('--cal', args.cal), ('--pro', args.pro),
                                   ('--carb', args.carb), ('--fat', args.fat),
                                   ('--fiber', args.fiber)] if v is None]
        if missing:
            print(Fore.RED + f"Unknown staple '{name}'. Provide macros: {', '.join(missing)}")
            print("Usage: macros log \"food name\" --cal 200 --pro 30 --carb 20 --fat 5 --fiber 2")
            sys.exit(1)
        item = {
            'calories': args.cal,
            'protein':  args.pro,
            'carbs':    args.carb,
            'fat':      args.fat,
            'fiber':    args.fiber,
        }
        display_name = name

    row = log_food(
        name=display_name,
        calories=item['calories'],
        protein=item['protein'],
        carbs=item['carbs'],
        fat=item['fat'],
        fiber=item['fiber'],
    )
    print(Fore.GREEN + f"Logged: {display_name}")
    print(f"  {row['Calories']}cal  {row['Protein']}p / {row['Carbs']}c / {row['Fat']}f / {row['Fiber']}fi")

    # Print running daily totals
    totals = get_day_totals()
    _print_totals(totals, label='Running totals for today')


def cmd_today(args):
    from lib.sheets import get_day_totals
    totals = get_day_totals()
    _print_totals(totals)


def cmd_summary(args):
    from lib.sheets import get_weekly_summary
    days = getattr(args, 'days', 7) or 7
    summary = get_weekly_summary(days)

    headers = ['Date', 'Cal', 'Tgt', 'Pro', 'Carb', 'Fat', 'Fib', 'Type']
    rows = []
    for d in summary:
        t = d['targets']
        is_high = t['calories'] == 2000
        rows.append([
            d['date'],
            f"{d['calories']:.0f}",
            f"{t['calories']}",
            f"{d['protein']:.0f}g",
            f"{d['carbs']:.0f}g",
            f"{d['fat']:.0f}g",
            f"{d['fiber']:.0f}g",
            'HIGH' if is_high else 'std',
        ])

    print()
    print(tabulate(rows, headers=headers, tablefmt='rounded_outline'))
    print()


def cmd_high(args):
    from lib.config import mark_high_activity
    target_date = getattr(args, 'date', None)
    marked = mark_high_activity(target_date)
    print(Fore.CYAN + f"Marked {marked} as a high-activity day (2000 cal target).")


def cmd_undo(args):
    from lib.sheets import undo_last_entry
    deleted = undo_last_entry()
    if deleted:
        name = deleted.get('Meal Name', '?')
        cal  = deleted.get('Calories', '?')
        print(Fore.YELLOW + f"Removed: {name} ({cal} cal)")
    else:
        print(Fore.RED + "Nothing to undo — log is empty.")


def cmd_staples(args):
    from lib.config import load_config
    config = load_config()
    staples = config.get('staples', {})
    if not staples:
        print("No staples configured.")
        return

    headers = ['Key', 'Name', 'Cal', 'Pro', 'Carb', 'Fat', 'Fiber']
    rows = [
        [k, v['name'], v['calories'], f"{v['protein']}g", f"{v['carbs']}g", f"{v['fat']}g", f"{v['fiber']}g"]
        for k, v in staples.items()
    ]
    print()
    print(tabulate(rows, headers=headers, tablefmt='rounded_outline'))
    print()


# ── argument parser ───────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='macros',
        description='Macro Tracker CLI — log food to Google Sheets',
    )
    sub = parser.add_subparsers(dest='command', required=True)

    # log
    p_log = sub.add_parser('log', help='Log a food item')
    p_log.add_argument('name', help='Food name or staple key')
    p_log.add_argument('--cal',   type=float, default=None, help='Calories')
    p_log.add_argument('--pro',   type=float, default=None, help='Protein (g)')
    p_log.add_argument('--carb',  type=float, default=None, help='Carbs (g)')
    p_log.add_argument('--fat',   type=float, default=None, help='Fat (g)')
    p_log.add_argument('--fiber', type=float, default=None, help='Fiber (g)')

    # today
    sub.add_parser('today', help="Show today's macro totals vs targets")

    # summary
    p_sum = sub.add_parser('summary', help='Show multi-day summary')
    p_sum.add_argument('--days', type=int, default=7, help='Number of days (default: 7)')

    # high
    p_high = sub.add_parser('high', help='Mark a day as high-activity')
    p_high.add_argument('--date', default=None, help='Date (YYYY-MM-DD); defaults to today')

    # undo
    sub.add_parser('undo', help='Remove last logged entry')

    # staples
    sub.add_parser('staples', help='List all configured staples')

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {
        'log':     cmd_log,
        'today':   cmd_today,
        'summary': cmd_summary,
        'high':    cmd_high,
        'undo':    cmd_undo,
        'staples': cmd_staples,
    }
    try:
        dispatch[args.command](args)
    except FileNotFoundError as e:
        print(Fore.RED + str(e))
        sys.exit(1)
    except Exception as e:
        print(Fore.RED + f"Error: {e}")
        raise


if __name__ == '__main__':
    main()
