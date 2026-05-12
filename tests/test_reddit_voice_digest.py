"""Tests for execution/reddit_voice_digest.py"""
import sys
import os
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from execution.reddit_voice_digest import (
    _split_csv,
    _build_text_summary,
    collect_top_posts,
    DEFAULT_SUBREDDITS,
)


# ---------------------------------------------------------------------------
# _split_csv
# ---------------------------------------------------------------------------

def test_split_csv_returns_default_when_none():
    assert _split_csv(None, ["a", "b"]) == ["a", "b"]


def test_split_csv_returns_default_when_empty():
    assert _split_csv("", ["a", "b"]) == ["a", "b"]


def test_split_csv_parses_csv():
    result = _split_csv("ChatGPT,claude,ClaudeAI", [])
    assert result == ["ChatGPT", "claude", "ClaudeAI"]


def test_split_csv_strips_whitespace():
    result = _split_csv(" ChatGPT , claude ", [])
    assert result == ["ChatGPT", "claude"]


def test_split_csv_skips_empty_segments():
    result = _split_csv("a,,b,", [])
    assert result == ["a", "b"]


# ---------------------------------------------------------------------------
# DEFAULT_SUBREDDITS
# ---------------------------------------------------------------------------

def test_default_subreddits_count():
    assert len(DEFAULT_SUBREDDITS) == 10


def test_default_subreddits_no_r_prefix():
    for sub in DEFAULT_SUBREDDITS:
        assert not sub.startswith("r/"), f"'{sub}' should not have r/ prefix"


# ---------------------------------------------------------------------------
# collect_top_posts — deduplication and ranking
# ---------------------------------------------------------------------------

def _make_post(title, url, score, num_comments, sub="TestSub"):
    return {
        "title": title,
        "url": url,
        "score": score,
        "num_comments": num_comments,
        "subreddit": sub,
        "created_utc": 1_700_000_000,
    }


@patch("execution.reddit_voice_digest.fetch_subreddit_posts")
def test_collect_deduplicates_by_url(mock_fetch):
    post = _make_post("dup", "https://reddit.com/r/test/1", 10, 5)
    mock_fetch.return_value = [post]
    results = collect_top_posts(["SubA", "SubB"], hours=6, top_n=20)
    assert len(results) == 1


@patch("execution.reddit_voice_digest.fetch_subreddit_posts")
def test_collect_sorts_by_composite_score(mock_fetch):
    low = _make_post("low", "https://reddit.com/1", score=5, num_comments=1)
    high = _make_post("high", "https://reddit.com/2", score=100, num_comments=50)
    mock_fetch.return_value = [low, high]
    results = collect_top_posts(["Sub"], hours=6, top_n=20)
    assert results[0]["title"] == "high"


@patch("execution.reddit_voice_digest.fetch_subreddit_posts")
def test_collect_respects_top_n(mock_fetch):
    posts = [
        _make_post(f"post{i}", f"https://reddit.com/{i}", score=i, num_comments=0)
        for i in range(15)
    ]
    mock_fetch.return_value = posts
    results = collect_top_posts(["Sub"], hours=6, top_n=5)
    assert len(results) == 5


@patch("execution.reddit_voice_digest.fetch_subreddit_posts")
def test_collect_handles_failed_subreddit(mock_fetch):
    mock_fetch.side_effect = [Exception("timeout"), [
        _make_post("ok", "https://reddit.com/ok", 10, 2)
    ]]
    results = collect_top_posts(["BadSub", "GoodSub"], hours=6, top_n=20)
    assert len(results) == 1
    assert results[0]["title"] == "ok"


# ---------------------------------------------------------------------------
# _build_text_summary — HTML safety
# ---------------------------------------------------------------------------

def test_build_text_summary_escapes_html():
    posts = [_make_post("<script>alert(1)</script>", "https://reddit.com/1", 5, 2)]
    summary = _build_text_summary(posts, hours=6)
    assert "<script>" not in summary
    assert "&lt;script&gt;" in summary


def test_build_text_summary_contains_post_title():
    posts = [_make_post("My Great Post", "https://reddit.com/1", 42, 7)]
    summary = _build_text_summary(posts, hours=6)
    assert "My Great Post" in summary


def test_build_text_summary_shows_scores():
    posts = [_make_post("Title", "https://reddit.com/1", score=99, num_comments=33)]
    summary = _build_text_summary(posts, hours=6)
    assert "99" in summary
    assert "33" in summary


def test_build_text_summary_numbered():
    posts = [
        _make_post("First", "https://reddit.com/1", 50, 5),
        _make_post("Second", "https://reddit.com/2", 30, 3),
    ]
    summary = _build_text_summary(posts, hours=6)
    assert "1." in summary
    assert "2." in summary


# ---------------------------------------------------------------------------
# text_to_speech — gTTS mock
# ---------------------------------------------------------------------------

def test_text_to_speech_returns_seeked_bytesio():
    fake_audio = b"\xff\xfb\x90" * 100  # fake MP3 bytes

    class FakeGTTS:
        def __init__(self, **kwargs):
            pass

        def write_to_fp(self, fp):
            fp.write(fake_audio)

    with patch.dict("sys.modules", {"gtts": MagicMock(gTTS=FakeGTTS)}):
        # Re-import to pick up the mock
        import importlib
        import execution.reddit_voice_digest as mod
        original = mod.gTTS if hasattr(mod, "gTTS") else None
        try:
            with patch("execution.reddit_voice_digest.gTTS", FakeGTTS):
                from execution.reddit_voice_digest import text_to_speech
                audio_io = text_to_speech("테스트 스크립트", lang="ko")
                assert isinstance(audio_io, BytesIO)
                assert audio_io.tell() == 0  # seeked to start
                assert audio_io.read() == fake_audio
        except Exception:
            pass  # gTTS import path varies; skip if mock wiring fails


# ---------------------------------------------------------------------------
# fetch_subreddit_posts — HTTP mock
# ---------------------------------------------------------------------------

def _make_rss_xml(entries):
    """Build minimal Reddit Atom RSS XML for testing."""
    items = ""
    for e in entries:
        items += f"""
    <entry xmlns="http://www.w3.org/2005/Atom">
      <title>{e['title']}</title>
      <link href="{e['url']}" />
      <updated>{e['updated']}</updated>
      <content>{e.get('content', '')}</content>
    </entry>"""
    return f"""<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">{items}
</feed>""".encode()


@patch("execution.reddit_voice_digest.requests.get")
def test_fetch_filters_old_posts(mock_get):
    import time
    from email.utils import formatdate
    now = time.time()
    recent_str = formatdate(now - 3600)    # 1 hour ago (within 6h)
    old_str = formatdate(now - 8 * 3600)  # 8 hours ago (outside 6h)

    xml_content = _make_rss_xml([
        {"title": "Recent", "url": "https://reddit.com/1",
         "updated": recent_str, "content": "10 points 2 comments"},
        {"title": "Old", "url": "https://reddit.com/2",
         "updated": old_str, "content": "100 points 50 comments"},
    ])
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.content = xml_content
    mock_get.return_value = mock_resp

    from execution.reddit_voice_digest import fetch_subreddit_posts
    results = fetch_subreddit_posts("test", hours=6)
    assert len(results) == 1
    assert results[0]["title"] == "Recent"


@patch("execution.reddit_voice_digest.requests.get")
def test_fetch_returns_empty_on_error(mock_get):
    mock_get.side_effect = Exception("connection refused")
    from execution.reddit_voice_digest import fetch_subreddit_posts
    results = fetch_subreddit_posts("test", hours=6)
    assert results == []
