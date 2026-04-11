#!/usr/bin/env python3
"""Backward-compatible wrapper for `applescout/scripts/send_report.py`."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from applescout.scripts.format_report import format_gemini_report
from applescout.scripts.send_report import main, send_telegram_message


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
