# Macro Tracker — Claude Code Instructions

This project is a personal nutrition macro tracker backed by Google Sheets.

## Your Role

When the user mentions eating or drinking something, **always log it to the sheet**
using the `macro-tracker` MCP tools. Do not ask for confirmation — just log it and
show the result.

## MCP Tools Available

| Tool | When to use |
|---|---|
| `log_staple` | User mentions a named staple (super coffee, apple, meal prep) |
| `log_food` | User mentions any other food with estimated or provided macros |
| `get_today_totals` | User asks "how am I doing", "what's my count", "totals" |
| `get_weekly_summary` | User asks about the week or recent days |
| `list_staples` | User asks what staples are configured |
| `undo_last_entry` | User says "undo", "remove that", "I didn't eat that" |
| `mark_high_activity_day` | User says "high day", "I worked out", "mark today as active" |

## Logging Rules

1. **Multiple foods in one message → multiple separate `log_food`/`log_staple` calls.**
   "I had an apple and a protein coffee" = two calls, logged in order.

2. **Use `log_staple` for configured staples** (case-insensitive match):
   - "super coffee", "protein coffee", "mocha coffee" → `log_staple("super coffee")`
   - "apple" → `log_staple("apple")`
   - "meal prep", "chicken rice", "my prep" → `log_staple("meal prep")`

3. **Use `log_food` for everything else** with USDA-estimated macros.

4. **After logging, always show the confirmation** returned by the tool.

## USDA Macro Estimates (common foods)

Use these when the user doesn't provide exact values:

| Food | Cal | Pro | Carb | Fat | Fiber |
|---|---|---|---|---|---|
| Banana (medium) | 105 | 1 | 27 | 0 | 3 |
| Orange (medium) | 62 | 1 | 15 | 0 | 3 |
| Greek yogurt, plain (6oz) | 100 | 17 | 6 | 0 | 0 |
| Oatmeal, cooked (1 cup) | 158 | 6 | 27 | 3 | 4 |
| Whole egg (large) | 72 | 6 | 0 | 5 | 0 |
| Egg whites (3) | 51 | 11 | 0 | 0 | 0 |
| Chicken breast, cooked (4oz) | 187 | 35 | 0 | 4 | 0 |
| Chicken breast, cooked (6oz) | 280 | 52 | 0 | 6 | 0 |
| Ground beef 93% lean (4oz cooked) | 197 | 24 | 0 | 10 | 0 |
| Salmon (4oz) | 208 | 28 | 0 | 10 | 0 |
| Tuna, canned in water (3oz) | 73 | 17 | 0 | 1 | 0 |
| White rice, cooked (1 cup) | 206 | 4 | 45 | 0 | 1 |
| Brown rice, cooked (1 cup) | 216 | 5 | 45 | 2 | 4 |
| Sweet potato (medium) | 103 | 2 | 24 | 0 | 4 |
| Broccoli (1 cup) | 55 | 4 | 11 | 1 | 5 |
| Mixed vegetables (1 cup) | 80 | 3 | 15 | 1 | 4 |
| Bread, whole wheat (1 slice) | 81 | 4 | 14 | 1 | 2 |
| Almonds (1oz / ~23) | 164 | 6 | 6 | 14 | 4 |
| Peanut butter (2 tbsp) | 188 | 8 | 6 | 16 | 2 |
| String cheese (1 stick) | 80 | 7 | 1 | 5 | 0 |
| Cottage cheese (1/2 cup) | 110 | 13 | 4 | 5 | 0 |
| Protein shake (typical 1 scoop) | 120 | 25 | 5 | 2 | 1 |
| Protein bar (Quest-style) | 180 | 20 | 21 | 7 | 14 |
| Subway 6" turkey | 280 | 18 | 46 | 3 | 5 |
| Chipotle burrito bowl (chicken, rice, beans, salsa) | 670 | 45 | 70 | 17 | 12 |

For quantities not listed above, scale proportionally (e.g., "8oz chicken" = 6oz × 8/6).

## Example Interactions

**User:** "just had my morning super coffee and an apple"
```
→ log_staple("super coffee")
→ log_staple("apple")
→ Show both confirmations + running total
```

**User:** "I had 8oz of chicken breast and a cup of rice for lunch"
```
→ log_food("Chicken Breast (8oz)", calories=374, protein=69, carbs=0, fat=8, fiber=0)
→ log_food("White Rice (1 cup)", calories=206, protein=4, carbs=45, fat=0, fiber=1)
→ Show both + running total
```

**User:** "had a protein shake and some almonds"
```
→ log_food("Protein Shake (1 scoop)", calories=120, protein=25, carbs=5, fat=2, fiber=1)
→ log_food("Almonds (1oz)", calories=164, protein=6, carbs=6, fat=14, fiber=4)
```

**User:** "how are my macros today?"
```
→ get_today_totals()
→ Show result
```

**User:** "undo that"
```
→ undo_last_entry()
```

**User:** "I'm doing a workout today"
```
→ mark_high_activity_day("")
→ Confirm 2000 cal target is now active
```

## Targets

| Day Type | Calories | Protein | Carbs | Fat | Fiber |
|---|---|---|---|---|---|
| Standard (5x/week) | 1500 | 125g | 125g | 32g | 30g |
| High-activity (2x/week) | 2000 | 125g | 125g | 35g | 30g |

## Project Setup Status

- **CLI:** `macros today`, `macros log "..."`, etc. (see README.md)
- **Dashboard:** `python3 dashboard/server.py` → http://localhost:8080
- **MCP config:** see README.md § "Claude Code MCP Setup"
- **Sheet init:** `python3 setup/init_sheet.py` (run once)
