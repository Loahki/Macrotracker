#!/usr/bin/env python3
"""
Macro Tracker Dashboard Server.

Serves the dashboard HTML and exposes a JSON API backed by Google Sheets.

Usage:
    python3 dashboard/server.py
    # then open http://localhost:8080

API:
    GET /              — dashboard HTML
    GET /api/daily     — today's data        ?date=YYYY-MM-DD
    GET /api/weekly    — last 7-day summary  ?days=N
    GET /api/staples   — configured staples
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, timedelta
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder=os.path.dirname(os.path.abspath(__file__)))
CORS(app)


@app.route('/')
def index():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'index.html')


@app.route('/api/daily')
def api_daily():
    target_date = request.args.get('date', date.today().isoformat())
    try:
        from lib.sheets import get_day_totals
        data = get_day_totals(target_date)
        # Serialise entries for JSON
        data['entries'] = [dict(e) for e in data.get('entries', [])]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/weekly')
def api_weekly():
    days = int(request.args.get('days', 7))
    try:
        from lib.sheets import get_weekly_summary
        summary = get_weekly_summary(days)
        for day in summary:
            day['entries'] = [dict(e) for e in day.get('entries', [])]
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/staples')
def api_staples():
    try:
        from lib.config import load_config
        config = load_config()
        return jsonify(config.get('staples', {}))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Macro Tracker Dashboard running at http://localhost:{port}")
    print("Press Ctrl+C to stop.")
    app.run(host='127.0.0.1', port=port, debug=False)
