#!/usr/bin/env python3
"""Backward-compatible wrapper for the skill-oriented AppleScout runner."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from applescout.scripts.run_applescout import main


if __name__ == "__main__":
    raise SystemExit(main())
