#!/usr/bin/env python3
"""Backward-compatible wrapper for `applescout/scripts/collect_social.py`."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from applescout.scripts.collect_social import (
    fetch_google_news_discussions,
    fetch_hackernews,
    fetch_reddit_rss,
    fetch_seeking_alpha_rss,
    filter_and_sort,
    main,
    parse_post_timestamp,
)


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
