import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from applescout.scripts.format_report import format_gemini_report, sanitize_hashtag
from applescout.scripts.send_report import resolve_dry_run, split_message


def test_sanitize_hashtag_normalizes_spacing_and_symbols():
    assert sanitize_hashtag("Vision Pro 2!") == "#Vision_Pro_2"


def test_split_message_splits_large_payload():
    message = "Section 1\n\n" + ("A" * 4100) + "\n\nSection 2"
    parts = split_message(message, max_length=4096)
    assert len(parts) >= 2
    assert all(len(part) <= 4096 for part in parts)


def test_split_message_preserves_short_message():
    message = "Short report"
    assert split_message(message, max_length=4096) == [message]


def test_resolve_dry_run_prefers_env(monkeypatch):
    monkeypatch.setenv("APPLESCOUT_DRY_RUN", "true")
    assert resolve_dry_run(False) is True


def test_format_gemini_report_escapes_html():
    report = {
        "date": "2026-03-22",
        "stock": {"current_price": 200, "change_percent": 1.2, "trend_5day": "상승"},
        "gemini_analysis": {
            "overall_sentiment": "긍정적",
            "sentiment_score": 0.8,
            "executive_summary": "<b>unsafe</b>",
            "key_insights": ["Insight"],
            "top_topics": ["Vision Pro"],
            "market_outlook": "Good",
            "opportunities": ["Upside"],
            "risk_factors": ["Risk"],
            "detailed_analysis": "Details",
        },
        "news_count": 3,
        "social_count": 2,
    }

    formatted = format_gemini_report(report)

    assert "&lt;b&gt;unsafe&lt;/b&gt;" in formatted
    assert "#Vision_Pro" in formatted
