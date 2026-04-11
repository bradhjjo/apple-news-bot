#!/usr/bin/env python3
"""
Reddit RSS 기반 데일리 다이제스트 수집 + 텔레그램 전송
- 우회/스크래핑 차단 회피 없이 공식 RSS 엔드포인트만 사용
- apple-scout의 텔레그램 전송 방식( python-telegram-bot )을 재사용

필수 환경변수:
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID

선택 환경변수:
- REDDIT_TOPICS: 콤마 구분 주제 (예: "on-device ai,edge ai,agentic coding")
- REDDIT_SUBREDDITS: 콤마 구분 subreddit (예: "MachineLearning,LocalLLaMA,artificial")
- REDDIT_POST_LIMIT: 피드당 최대 포스트 수 (기본 5)
- REDDIT_TIME: day|week|month|year|all (기본 day)
"""

from __future__ import annotations

import asyncio
import html
import os
import re
from datetime import datetime
from typing import Dict, List, Tuple
from urllib.parse import quote_plus

import feedparser
from dotenv import load_dotenv
from telegram import Bot
from telegram.constants import ParseMode

try:
    load_dotenv()
except Exception:
    pass


def _split_csv(value: str | None, default: List[str]) -> List[str]:
    if not value:
        return default
    return [x.strip() for x in value.split(",") if x.strip()]


def _extract_points_comments(summary: str) -> Tuple[int | None, int | None]:
    # RSS summary 예시에서 "123 points" "45 comments" 추출
    points_match = re.search(r"(\d+)\s+points", summary or "", re.IGNORECASE)
    comments_match = re.search(r"(\d+)\s+comments", summary or "", re.IGNORECASE)
    points = int(points_match.group(1)) if points_match else None
    comments = int(comments_match.group(1)) if comments_match else None
    return points, comments


def fetch_feed(url: str, max_items: int) -> List[Dict]:
    feed = feedparser.parse(
        url,
        request_headers={
            "User-Agent": "AppleScoutRedditRSS/1.0 (+https://github.com/)"
        },
    )

    items: List[Dict] = []
    for entry in feed.entries[:max_items]:
        summary = entry.get("summary", "")
        points, comments = _extract_points_comments(summary)
        items.append(
            {
                "title": entry.get("title", "(no title)"),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "source": feed.feed.get("title", "reddit"),
                "points": points,
                "comments": comments,
            }
        )
    return items


def collect_reddit_rss(topics: List[str], subreddits: List[str], t_range: str, per_feed: int) -> List[Dict]:
    collected: List[Dict] = []

    # 1) topic 검색 RSS
    for topic in topics:
        q = quote_plus(topic)
        url = f"https://www.reddit.com/search.rss?q={q}&sort=new&t={t_range}"
        collected.extend(fetch_feed(url, per_feed))

    # 2) subreddit new RSS
    for sub in subreddits:
        sub = sub.replace("r/", "").strip()
        if not sub:
            continue
        url = f"https://www.reddit.com/r/{quote_plus(sub)}/new/.rss"
        collected.extend(fetch_feed(url, per_feed))

    # dedupe by link
    uniq: Dict[str, Dict] = {}
    for item in collected:
        link = item.get("link")
        if link and link not in uniq:
            uniq[link] = item

    # 간단 정렬: points 우선, 없으면 최근순(입력순 유지)
    items = list(uniq.values())
    items.sort(key=lambda x: (x.get("points") is not None, x.get("points") or -1), reverse=True)
    return items


def build_message(items: List[Dict], topics: List[str], subreddits: List[str], top_n: int = 12) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "🧠 <b>Reddit Daily Digest (RSS)</b>",
        f"⏰ {now}",
        f"🏷️ Topics: {', '.join(topics) if topics else '-'}",
        f"📚 Subreddits: {', '.join(subreddits) if subreddits else '-'}",
        "",
    ]

    if not items:
        lines.append("오늘 수집된 포스트가 없어.")
        return "\n".join(lines)

    for i, it in enumerate(items[:top_n], 1):
        title = html.escape(it.get("title", "(no title)"))
        link = html.escape(it.get("link", ""))
        src = html.escape(it.get("source", "reddit"))
        pts = it.get("points")
        cmt = it.get("comments")
        meta = []
        if pts is not None:
            meta.append(f"👍 {pts}")
        if cmt is not None:
            meta.append(f"💬 {cmt}")
        meta_text = " | ".join(meta) if meta else ""

        lines.append(f"{i}. <a href=\"{link}\">{title}</a>")
        lines.append(f"   └ {src}{(' | ' + meta_text) if meta_text else ''}")

    return "\n".join(lines)


async def send_telegram(bot_token: str, chat_id: str, message: str) -> None:
    bot = Bot(token=bot_token)

    max_len = 4096
    chunks: List[str] = []
    if len(message) <= max_len:
        chunks = [message]
    else:
        buf = ""
        for line in message.split("\n"):
            if len(buf) + len(line) + 1 > max_len:
                chunks.append(buf)
                buf = line + "\n"
            else:
                buf += line + "\n"
        if buf:
            chunks.append(buf)

    for idx, chunk in enumerate(chunks, 1):
        await bot.send_message(
            chat_id=chat_id,
            text=chunk,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        print(f"✓ Telegram sent ({idx}/{len(chunks)})")
        if idx < len(chunks):
            await asyncio.sleep(1)


def main() -> int:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        print("❌ TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID 누락")
        return 1

    topics = _split_csv(os.getenv("REDDIT_TOPICS"), ["on-device ai", "edge ai"])
    subreddits = _split_csv(os.getenv("REDDIT_SUBREDDITS"), ["MachineLearning", "LocalLLaMA", "artificial"])
    per_feed = int(os.getenv("REDDIT_POST_LIMIT", "5"))
    t_range = os.getenv("REDDIT_TIME", "day")

    print("📡 Collecting Reddit RSS...")
    items = collect_reddit_rss(topics, subreddits, t_range, per_feed)
    print(f"✓ Collected unique posts: {len(items)}")

    message = build_message(items, topics, subreddits)
    asyncio.run(send_telegram(bot_token, chat_id, message))
    print("✅ Done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
