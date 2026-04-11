#!/usr/bin/env python3
"""Backward-compatible wrapper for `applescout/scripts/analyze_gemini.py`."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from applescout.scripts.analyze_gemini import analyze_with_gemini, load_inputs, main


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
