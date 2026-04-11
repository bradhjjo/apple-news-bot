#!/usr/bin/env python3
"""Collect Apple news articles into `.tmp/news_articles.json`."""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
import sys
from typing import Dict, List, Optional

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from applescout.scripts.utils_io import write_json_atomic
from applescout.scripts.utils_paths import tmp_file


def fetch_google_news() -> List[Dict]:
    import feedparser

    articles = []
    try:
        url = "https://news.google.com/rss/search?q=Apple+OR+AAPL&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(url)
        for entry in feed.entries[:20]:
            articles.append(
                {
                    "title": entry.title,
                    "source": "Google News",
                    "url": entry.link,
                    "published": entry.get("published", ""),
                    "summary": entry.get("summary", ""),
                }
            )
        print(f"✓ Google News: {len(articles)} articles")
    except Exception as exc:
        print(f"✗ Google News error: {exc}")
    return articles


def fetch_apple_newsroom() -> List[Dict]:
    import feedparser

    articles = []
    try:
        url = "https://www.apple.com/newsroom/rss-feed.rss"
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            articles.append(
                {
                    "title": entry.title,
                    "source": "Apple Newsroom",
                    "url": entry.link,
                    "published": entry.get("published", ""),
                    "summary": entry.get("summary", ""),
                }
            )
        print(f"✓ Apple Newsroom: {len(articles)} articles")
    except Exception as exc:
        print(f"✗ Apple Newsroom error: {exc}")
    return articles


def fetch_tech_news() -> List[Dict]:
    import feedparser

    articles = []
    feeds = {
        "MacRumors": "https://www.macrumors.com/feed/",
        "9to5Mac": "https://9to5mac.com/feed/",
        "AppleInsider": "https://appleinsider.com/rss/news/",
    }
    for source, url in feeds.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                articles.append(
                    {
                        "title": entry.title,
                        "source": source,
                        "url": entry.link,
                        "published": entry.get("published", ""),
                        "summary": entry.get("summary", ""),
                    }
                )
            count = len([article for article in articles if article["source"] == source])
            print(f"✓ {source}: {count} articles")
            time.sleep(1)
        except Exception as exc:
            print(f"✗ {source} error: {exc}")
    return articles


def remove_duplicates(articles: List[Dict]) -> List[Dict]:
    seen_urls = set()
    unique_articles = []
    for article in articles:
        url = article.get("url")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_articles.append(article)
    return unique_articles


def parse_article_timestamp(value: str) -> Optional[datetime]:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = parsedate_to_datetime(value)
        except (TypeError, ValueError, IndexError):
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def filter_recent(articles: List[Dict], hours: int = 24) -> List[Dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    recent_articles = []
    skipped_without_timestamp = 0
    for article in articles:
        published_at = parse_article_timestamp(article.get("published", ""))
        if not published_at:
            skipped_without_timestamp += 1
            continue
        if published_at >= cutoff:
            item = dict(article)
            item["_parsed_published"] = published_at
            recent_articles.append(item)
    recent_articles.sort(key=lambda article: article["_parsed_published"], reverse=True)
    for article in recent_articles:
        article.pop("_parsed_published", None)
    print(f"✓ Recent news filter: kept {len(recent_articles)} articles from last {hours}h")
    if skipped_without_timestamp:
        print(f"⚠️  Skipped {skipped_without_timestamp} articles without parseable timestamps")
    return recent_articles[:50]


def main() -> bool:
    print("🍎 Starting Apple news collection...")
    all_articles = []
    all_articles.extend(fetch_google_news())
    all_articles.extend(fetch_apple_newsroom())
    all_articles.extend(fetch_tech_news())
    unique_articles = remove_duplicates(all_articles)
    print(f"\n📊 Total unique articles: {len(unique_articles)}")
    recent_articles = filter_recent(unique_articles)
    output_file = tmp_file("news_articles.json")
    write_json_atomic(output_file, recent_articles)
    print(f"✅ Saved {len(recent_articles)} articles to {output_file}")
    return len(recent_articles) >= 5


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
