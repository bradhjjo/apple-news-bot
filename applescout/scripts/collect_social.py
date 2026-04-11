#!/usr/bin/env python3
"""Collect Apple-related social content into `.tmp/social_posts.json`."""

from __future__ import annotations

import re
import sys
import time
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from applescout.scripts.utils_io import write_json_atomic
from applescout.scripts.utils_paths import tmp_file


def fetch_reddit_rss() -> List[Dict]:
    posts = []
    try:
        import feedparser

        subreddits = ["apple", "stocks", "investing", "wallstreetbets"]
        keywords = ["apple", "aapl", "iphone", "ipad", "mac", "tim cook"]
        for subreddit_name in subreddits:
            try:
                url = f"https://www.reddit.com/r/{subreddit_name}/hot.rss?limit=50"
                feed = feedparser.parse(url)
                if not feed.entries:
                    print(f"✗ Reddit r/{subreddit_name} RSS returned no entries")
                    continue
                for entry in feed.entries:
                    title_lower = entry.title.lower()
                    if any(keyword in title_lower for keyword in keywords):
                        score = 0
                        comments = 0
                        if hasattr(entry, "summary"):
                            score_match = re.search(r"(\d+)\s+points?", entry.summary)
                            comments_match = re.search(r"(\d+)\s+comments?", entry.summary)
                            if score_match:
                                score = int(score_match.group(1))
                            if comments_match:
                                comments = int(comments_match.group(1))
                        posts.append(
                            {
                                "platform": "reddit",
                                "title": entry.title,
                                "url": entry.link,
                                "score": score,
                                "comments": comments,
                                "created": entry.get("published", datetime.now().isoformat()),
                                "text": entry.get("summary", "")[:500],
                            }
                        )
                count = len([post for post in posts if subreddit_name in post["url"]])
                print(f"✓ Reddit r/{subreddit_name} RSS: {count} posts")
                time.sleep(2)
            except Exception as exc:
                print(f"✗ Reddit r/{subreddit_name} RSS error: {exc}")
    except Exception as exc:
        print(f"✗ Reddit RSS error: {exc}")
    return posts


def fetch_google_news_discussions() -> List[Dict]:
    posts = []
    try:
        import feedparser

        queries = ["Apple stock analysis", "AAPL stock opinion", "Apple earnings discussion"]
        for query in queries:
            try:
                url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-US&gl=US&ceid=US:en"
                feed = feedparser.parse(url)
                for entry in feed.entries[:10]:
                    posts.append(
                        {
                            "platform": "google_news",
                            "title": entry.title,
                            "url": entry.link,
                            "score": 0,
                            "comments": 0,
                            "created": entry.get("published", datetime.now().isoformat()),
                            "text": entry.get("summary", "")[:500],
                        }
                    )
                count = len([post for post in posts if query.split()[0].lower() in post["title"].lower()])
                print(f"✓ Google News ({query}): {count} articles")
                time.sleep(1)
            except Exception as exc:
                print(f"✗ Google News ({query}) error: {exc}")
    except Exception as exc:
        print(f"✗ Google News error: {exc}")
    return posts


def fetch_seeking_alpha_rss() -> List[Dict]:
    posts = []
    try:
        import feedparser

        url = "https://seekingalpha.com/api/sa/combined/AAPL.xml"
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]:
                posts.append(
                    {
                        "platform": "seeking_alpha",
                        "title": entry.title,
                        "url": entry.link,
                        "score": 0,
                        "comments": 0,
                        "created": entry.get("published", datetime.now().isoformat()),
                        "text": entry.get("summary", "")[:500],
                    }
                )
            print(f"✓ Seeking Alpha: {len(posts)} articles")
        except Exception as exc:
            print(f"✗ Seeking Alpha error: {exc}")
    except Exception as exc:
        print(f"✗ Seeking Alpha RSS error: {exc}")
    return posts


def fetch_hackernews() -> List[Dict]:
    posts = []
    try:
        top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        response = requests.get(top_stories_url, timeout=10)
        story_ids = response.json()[:100]
        keywords = ["apple", "aapl", "iphone", "ipad", "mac", "ios"]
        for story_id in story_ids[:50]:
            try:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                story_response = requests.get(story_url, timeout=5)
                story = story_response.json()
                if story and "title" in story:
                    title_lower = story["title"].lower()
                    if any(keyword in title_lower for keyword in keywords):
                        posts.append(
                            {
                                "platform": "hackernews",
                                "title": story["title"],
                                "url": story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                                "score": story.get("score", 0),
                                "comments": story.get("descendants", 0),
                                "created": datetime.fromtimestamp(story.get("time", 0)).isoformat(),
                                "text": story.get("text", "")[:500],
                            }
                        )
            except Exception:
                continue
        print(f"✓ Hacker News: {len(posts)} posts")
    except Exception as exc:
        print(f"✗ Hacker News error: {exc}")
    return posts


def parse_post_timestamp(value: str) -> Optional[datetime]:
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


def filter_and_sort(posts: List[Dict], hours: int = 24) -> List[Dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    recent_posts = []
    skipped_without_timestamp = 0
    for post in posts:
        created_at = parse_post_timestamp(post.get("created", ""))
        if not created_at:
            skipped_without_timestamp += 1
            continue
        if created_at >= cutoff:
            item = dict(post)
            item["_parsed_created"] = created_at
            recent_posts.append(item)
    recent_posts.sort(key=lambda post: (post["_parsed_created"], post.get("score", 0)), reverse=True)
    for post in recent_posts:
        post.pop("_parsed_created", None)
    print(f"✓ Recent social filter: kept {len(recent_posts)} posts from last {hours}h")
    if skipped_without_timestamp:
        print(f"⚠️  Skipped {skipped_without_timestamp} posts without parseable timestamps")
    return recent_posts[:30]


def main() -> bool:
    print("💬 Starting social media collection...")
    all_posts = []
    for fetcher in (
        fetch_reddit_rss,
        fetch_google_news_discussions,
        fetch_seeking_alpha_rss,
        fetch_hackernews,
    ):
        try:
            all_posts.extend(fetcher())
        except Exception as exc:
            print(f"⚠️  {fetcher.__name__} failed: {exc}")
    filtered_posts = filter_and_sort(all_posts)
    print(f"\n📊 Total filtered posts: {len(filtered_posts)}")
    output_file = tmp_file("social_posts.json")
    write_json_atomic(output_file, filtered_posts)
    if filtered_posts:
        print(f"✅ Saved {len(filtered_posts)} posts to {output_file}")
    else:
        print("⚠️  No social media posts collected, but continuing workflow...")
        print(f"✅ Saved empty posts list to {output_file}")
    return True


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
