# Macro Tracker

Personal nutrition macro tracker backed by Google Sheets. Logs calories, protein, carbs, fat, and fiber. Works from the CLI, via Claude Code natural language, and a local web dashboard.

**Targets (prescribed):**

| Day | Calories | Protein | Carbs | Fat | Fiber |
|---|---|---|---|---|---|
| Standard (5×/wk) | 1500 | 125g | 125g | 32g | 30g |
| High-activity (2×/wk) | 2000 | 125g | 125g | 35g | 30g |

---

## Quick Start (after OAuth setup)

```bash
# 1. Install dependencies
pip3 install --user -r requirements.txt

# 2. Set up Google Sheets (one time)
python3 setup/init_sheet.py

# 3. Install the CLI
bash cli_install.sh

# 4. Start logging
macros log "super coffee"
macros today
```

---

## Setup: Part 1 — Google Cloud Console OAuth

**See the detailed step-by-step guide:** [`setup/google_cloud_setup.md`](setup/google_cloud_setup.md)

Summary:
1. Create a project at console.cloud.google.com
2. Enable **Google Sheets API** and **Google Drive API**
3. Configure **OAuth consent screen** (External, add yourself as a test user)
4. Create **OAuth 2.0 credentials** (Desktop app) → download `credentials.json`
5. Move it: `mv ~/Downloads/credentials.json ~/.macrotracker/credentials.json`
6. Run: `python3 setup/init_sheet.py`

---

## Setup: Part 2 — Claude Code MCP Server

Add the MCP server to your Claude Code config so Claude can log food via natural language.

Edit `~/.claude/settings.json` (create if it doesn't exist):

```json
{
  "mcpServers": {
    "macro-tracker": {
      "command": "python3",
      "args": ["/home/user/Macrotracker/mcp_server.py"]
    }
  }
}
```

**Test the MCP connection** by starting a new Claude Code session in this directory and saying:
> "Show me my macro staples"

Claude should respond using the `list_staples` tool.

---

## CLI Reference

Install once: `bash cli_install.sh`

```bash
# Log a configured staple by name
macros log "super coffee"
macros log "apple"
macros log "meal prep"

# Log any food with explicit macros
macros log "6oz chicken breast" --cal 280 --pro 52 --carb 0 --fat 6 --fiber 0
macros log "Quest bar" --cal 190 --pro 21 --carb 22 --fat 8 --fiber 14

# View today's totals
macros today

# View last N days
macros summary
macros summary --days 14

# Mark today as high-activity (2000 cal target)
macros high
macros high --date 2024-01-15

# Undo last entry
macros undo

# List configured staples
macros staples
```

---

## Configured Staples

| Key | Food | Cal | Pro | Carb | Fat | Fiber |
|---|---|---|---|---|---|---|
| `super coffee` | Super Coffee Protein+ Mocha | 150 | 25g | 8g | 3g | 0g |
| `apple` | Apple | 85 | 0g | 22g | 0g | 4g |
| `meal prep` | Meal Prep (chicken/rice/veg) | 500 | 42g | 52g | 9g | 5g |

To add more staples, edit `~/.macrotracker/config.json`:
```json
"staples": {
  "protein bar": {
    "name": "Quest Bar Chocolate Chip Cookie Dough",
    "calories": 190,
    "protein": 21,
    "carbs": 22,
    "fat": 8,
    "fiber": 14
  }
}
```

---

## Web Dashboard

```bash
python3 dashboard/server.py
# → http://localhost:8080
```

Features:
- Day navigation with prev/next buttons
- 5 macro cards (Calories, Protein, Carbs, Fat, Fiber) with progress bars
- Progress bars turn yellow at 85% and red at 100% (or green for protein/fiber)
- Full meal log for the selected day
- 7-day calorie chart
- Auto-refreshes every 30 seconds

---

## Claude Code Natural Language Logging

With the MCP server configured, just tell Claude what you ate:

> "I just had my morning super coffee and an apple"

> "Had 8oz chicken breast and a cup of brown rice for lunch"

> "Just ate a Quest bar and drank a protein shake"

> "How are my macros today?"

> "Mark today as a high-activity day"

Claude will:
1. Parse each food item separately
2. Look up staples by name or estimate macros from USDA data
3. Call `log_food` or `log_staple` for each item
4. Show confirmation with running daily totals

See [`CLAUDE.md`](CLAUDE.md) for the full reference Claude uses internally.

---

## File Structure

```
Macrotracker/
├── CLAUDE.md              # Claude Code natural language instructions
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── macros.py              # CLI entry point
├── mcp_server.py          # MCP server for Claude Code
├── cli_install.sh         # Installs 'macros' command to ~/.local/bin
├── lib/
│   ├── auth.py            # Google OAuth / gspread auth
│   ├── config.py          # Config file management (~/.macrotracker/config.json)
│   └── sheets.py          # Sheet read/write operations
├── setup/
│   ├── google_cloud_setup.md  # Step-by-step OAuth guide
│   └── init_sheet.py          # Creates the Google Sheet (run once)
└── dashboard/
    ├── server.py          # Flask API server
    └── index.html         # Dashboard UI
```

---

## Config File

After running `setup/init_sheet.py`, your config lives at `~/.macrotracker/config.json`:

```json
{
  "spreadsheet_id": "1abc...",
  "staples": { ... },
  "targets": {
    "standard":      { "calories": 1500, "protein": 125, "carbs": 125, "fat": 32, "fiber": 30 },
    "high_activity": { "calories": 2000, "protein": 125, "carbs": 125, "fat": 35, "fiber": 30 }
  },
  "high_activity_days": []
}
```

---

## Troubleshooting

**`credentials.json not found`**
→ See `setup/google_cloud_setup.md`, Step 5.

**`Config not found — run setup/init_sheet.py`**
→ Run `python3 setup/init_sheet.py` first.

**`macros: command not found`**
→ Run `bash cli_install.sh` and add `~/.local/bin` to your PATH.

**MCP server not responding in Claude Code**
→ Check `~/.claude/settings.json` has the correct path to `mcp_server.py`.
→ Test manually: `python3 mcp_server.py` (should start without errors).

**Token expired**
→ Delete `~/.macrotracker/token.json` and run any `macros` command to re-auth.
