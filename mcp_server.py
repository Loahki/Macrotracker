#!/usr/bin/env python3
"""
Macro Tracker MCP Server — exposes Google Sheets logging tools to Claude Code.

Claude Code configuration (~/.claude/settings.json):
    {
      "mcpServers": {
        "macro-tracker": {
          "command": "python3",
          "args": ["/home/user/Macrotracker/mcp_server.py"]
        }
      }
    }
"""

import sys
import os
import json
import asyncio

# Propagate SPREADSHEET_ID for cloud mode before any lib imports
# (no-op locally since the env var won't be set)


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP

_transport = os.environ.get('MCP_TRANSPORT', 'stdio')
_port = int(os.environ.get('PORT', 8000))
mcp = FastMCP(
    "macro-tracker",
    host='0.0.0.0' if _transport == 'http' else '127.0.0.1',
    port=_port,
)


# ── tools ───────────────────────────────────────────────────────────────────────────────

@mcp.tool()
def log_food(
    name: str,
    calories: float,
    protein: float,
    carbs: float,
    fat: float,
    fiber: float,
    date: str = "",
) -> str:
    """
    Log a food item to the Macro Tracker Google Sheet.

    Use USDA estimates for common foods when exact values are unknown.
    Always log each distinct food as a separate call.

    Args:
        name:     Human-readable food name (e.g. "Apple", "6oz Chicken Breast")
        calories: Total calories
        protein:  Protein in grams
        carbs:    Carbohydrates in grams
        fat:      Total fat in grams
        fiber:    Dietary fiber in grams
        date:     Date in YYYY-MM-DD format (default: today)
    """
    from lib.sheets import log_food as _log, get_day_totals

    row = _log(
        name=name,
        calories=calories,
        protein=protein,
        carbs=carbs,
        fat=fat,
        fiber=fiber,
        meal_date=date or None,
    )

    totals = get_day_totals(date or None)
    t = totals['targets']
    is_high = t['calories'] == 2000

    lines = [
        f"✓ Logged: {name}",
        f"  {calories:.0f} cal | {protein:.0f}g protein | {carbs:.0f}g carbs | {fat:.0f}g fat | {fiber:.0f}g fiber",
        "",
        f"Running totals for {totals['date']} ({('High-Activity' if is_high else 'Standard')} day):",
        f"  Calories: {totals['calories']:.0f} / {t['calories']} kcal",
        f"  Protein:  {totals['protein']:.0f} / {t['protein']}g",
        f"  Carbs:    {totals['carbs']:.0f} / {t['carbs']}g",
        f"  Fat:      {totals['fat']:.0f} / {t['fat']}g",
        f"  Fiber:    {totals['fiber']:.0f} / {t['fiber']}g",
    ]
    return "\n".join(lines)


@mcp.tool()
def get_day_totals(date: str = "") -> str:
    """
    Return macro totals for a specific date and how they compare to daily targets.

    Args:
        date: Date in YYYY-MM-DD format (default: today)
    """
    from lib.sheets import get_day_totals as _get_totals

    totals = _get_totals(date or None)
    t = totals['targets']
    is_high = t['calories'] == 2000
    entries = totals.get('entries', [])

    def pct(v, target):
        return f"{v / target * 100:.0f}%" if target else "—"

    lines = [
        f"Date: {totals['date']}  ({'High-Activity' if is_high else 'Standard'} day)",
        "─" * 44,
        f"  Calories: {totals['calories']:>6.1f} / {t['calories']:>4} kcal  ({pct(totals['calories'], t['calories'])})",
        f"  Protein:  {totals['protein']:>6.1f} / {t['protein']:>4}g    ({pct(totals['protein'], t['protein'])})",
        f"  Carbs:    {totals['carbs']:>6.1f} / {t['carbs']:>4}g    ({pct(totals['carbs'], t['carbs'])})",
        f"  Fat:      {totals['fat']:>6.1f} / {t['fat']:>4}g    ({pct(totals['fat'], t['fat'])})",
        f"  Fiber:    {totals['fiber']:>6.1f} / {t['fiber']:>4}g    ({pct(totals['fiber'], t['fiber'])})",
        "─" * 44,
        f"  Meals logged: {len(entries)}",
    ]

    for e in entries:
        ts = str(e.get('Timestamp', ''))[-8:-3]
        lines.append(
            f"  {ts}  {e.get('Meal Name','')[:30]:<30}  {float(e.get('Calories',0) or 0):.0f} cal"
        )

    return "\n".join(lines)


@mcp.tool()
def log_staple(staple_name: str) -> str:
    """
    Log a pre-configured staple food by name.

    Looks up the staple in config using fuzzy matching (case-insensitive,
    substring). Returns an error if not found.

    Args:
        staple_name: The staple key or partial name (e.g. "super coffee", "apple", "meal prep")
    """
    from lib.config import lookup_staple
    from lib.sheets import log_food as _log, get_day_totals

    staple = lookup_staple(staple_name)
    if not staple:
        from lib.config import load_config
        config = load_config()
        keys = list(config.get('staples', {}).keys())
        return f"Staple '{staple_name}' not found.\nAvailable staples: {', '.join(keys)}"

    row = _log(
        name=staple['name'],
        calories=staple['calories'],
        protein=staple['protein'],
        carbs=staple['carbs'],
        fat=staple['fat'],
        fiber=staple['fiber'],
    )

    totals = get_day_totals()
    t = totals['targets']
    is_high = t['calories'] == 2000

    lines = [
        f"✓ Logged staple: {staple['name']}",
        f"  {staple['calories']} cal | {staple['protein']}g protein | {staple['carbs']}g carbs | {staple['fat']}g fat | {staple['fiber']}g fiber",
        "",
        f"Today's running totals ({('High-Activity' if is_high else 'Standard')} day):",
        f"  Calories: {totals['calories']:.0f} / {t['calories']} kcal",
        f"  Protein:  {totals['protein']:.0f} / {t['protein']}g",
        f"  Carbs:    {totals['carbs']:.0f} / {t['carbs']}g",
        f"  Fat:      {totals['fat']:.0f} / {t['fat']}g",
        f"  Fiber:    {totals['fiber']:.0f} / {t['fiber']}g",
    ]
    return "\n".join(lines)


@mcp.tool()
def get_today_totals() -> str:
    """Return today's macro totals and how they compare to the daily targets."""
    from lib.sheets import get_day_totals

    totals = get_day_totals()
    t = totals['targets']
    is_high = t['calories'] == 2000
    entries = totals.get('entries', [])

    def pct(v, target):
        return f"{v / target * 100:.0f}%" if target else "—"

    lines = [
        f"Today: {totals['date']}  ({'High-Activity' if is_high else 'Standard'} day)",
        "─" * 44,
        f"  Calories: {totals['calories']:>6.0f} / {t['calories']:>4} kcal  ({pct(totals['calories'], t['calories'])})",
        f"  Protein:  {totals['protein']:>6.0f} / {t['protein']:>4}g    ({pct(totals['protein'], t['protein'])})",
        f"  Carbs:    {totals['carbs']:>6.0f} / {t['carbs']:>4}g    ({pct(totals['carbs'], t['carbs'])})",
        f"  Fat:      {totals['fat']:>6.0f} / {t['fat']:>4}g    ({pct(totals['fat'], t['fat'])})",
        f"  Fiber:    {totals['fiber']:>6.0f} / {t['fiber']:>4}g    ({pct(totals['fiber'], t['fiber'])})",
        "─" * 44,
        f"  Meals logged: {len(entries)}",
    ]

    for e in entries:
        ts = str(e.get('Timestamp', ''))[-8:-3]
        lines.append(
            f"  {ts}  {e.get('Meal Name','')[:30]:<30}  {float(e.get('Calories',0) or 0):.0f} cal"
        )

    return "\n".join(lines)


@mcp.tool()
def get_weekly_summary() -> str:
    """Return a 7-day macro summary table."""
    from lib.sheets import get_weekly_summary as _weekly

    summary = _weekly(7)
    lines = ["7-Day Macro Summary", "─" * 70]
    lines.append(f"{'Date':<12} {'Cal':>5} {'Tgt':>5} {'Pro':>5} {'Carb':>5} {'Fat':>5} {'Fib':>5}  Type")
    lines.append("─" * 70)

    for d in summary:
        t = d['targets']
        is_high = t['calories'] == 2000
        lines.append(
            f"{d['date']:<12} {d['calories']:>5.0f} {t['calories']:>5} "
            f"{d['protein']:>4.0f}g {d['carbs']:>4.0f}g {d['fat']:>4.0f}g {d['fiber']:>4.0f}g  "
            f"{'HIGH' if is_high else 'std'}"
        )

    return "\n".join(lines)


@mcp.tool()
def list_staples() -> str:
    """List all configured staple foods with their macro values."""
    from lib.config import load_config

    config = load_config()
    staples = config.get('staples', {})
    if not staples:
        return "No staples configured."

    lines = ["Configured Staples:", "─" * 70]
    lines.append(f"{'Key':<20} {'Name':<35} {'Cal':>4} {'Pro':>4} {'Carb':>4} {'Fat':>4} {'Fib':>4}")
    lines.append("─" * 70)

    for key, s in staples.items():
        lines.append(
            f"{key:<20} {s['name']:<35} {s['calories']:>4} {s['protein']:>3}g "
            f"{s['carbs']:>3}g {s['fat']:>3}g {s['fiber']:>3}g"
        )

    return "\n".join(lines)


@mcp.tool()
def undo_last_entry() -> str:
    """Remove the most recently logged food entry from the sheet."""
    from lib.sheets import undo_last_entry as _undo

    deleted = _undo()
    if deleted:
        name = deleted.get('Meal Name', '?')
        cal  = deleted.get('Calories', '?')
        return f"✓ Removed: {name} ({cal} cal)"
    return "Nothing to undo — log is empty."


@mcp.tool()
def mark_high_activity_day(date: str = "") -> str:
    """
    Mark a day as a high-activity day (2000 cal target instead of 1500).

    Args:
        date: Date in YYYY-MM-DD format. Leave empty for today.
    """
    from lib.config import mark_high_activity

    marked = mark_high_activity(date or None)
    return f"✓ Marked {marked} as a high-activity day (target: 2000 cal)."


# ── entry point ────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if _transport == 'http':
        mcp.run(transport='streamable-http')
    else:
        mcp.run()
