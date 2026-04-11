import pytest
from datetime import datetime, timezone
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from execution.scrape_news import parse_article_timestamp

def test_parse_article_timestamp():
    dt = parse_article_timestamp("2026-03-20T10:00:00Z")
    assert dt is not None
    assert dt.tzinfo == timezone.utc


def test_parse_article_timestamp_rfc2822():
    dt = parse_article_timestamp("Fri, 20 Mar 2026 10:00:00 GMT")
    assert dt is not None
    assert dt.tzinfo == timezone.utc
