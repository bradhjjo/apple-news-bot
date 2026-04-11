#!/usr/bin/env python3
"""Backward-compatible wrapper for `applescout/scripts/collect_news.py`."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from applescout.scripts.collect_news import (
    fetch_apple_newsroom,
    fetch_google_news,
    fetch_tech_news,
    filter_recent,
    main,
    parse_article_timestamp,
    remove_duplicates,
)


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
