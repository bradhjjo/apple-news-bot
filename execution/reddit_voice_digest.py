#!/usr/bin/env python3
"""
AI 서브레딧 최근 6시간 Top 20 음성 다이제스트

지정된 AI 관련 서브레딧에서 최근 N시간 동안의 게시글을 수집하고,
댓글 수와 upvote를 기준으로 상위 게시글을 선별해 한국어 음성으로
텔레그램에 전달합니다.

필수 환경변수:
    TELEGRAM_BOT_TOKEN
    TELEGRAM_CHAT_ID
    GEMINI_API_KEY

선택 환경변수:
    AI_SUBREDDITS  : 콤마 구분 서브레딧 목록 (기본값: 10개 AI 서브레딧)
    AI_REDDIT_HOURS: 시간 필터 (기본값: 6)
    AI_REDDIT_TOP_N: 상위 N개 (기본값: 20)
    AI_VOICE_LANG  : TTS 언어 코드 (기본값: ko)
    DRY_RUN        : true 시 Telegram 전송 생략
"""

from __future__ import annotations

import asyncio
import html
import os
import sys
import time
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

# Allow running as standalone script
if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from applescout.scripts.utils_io import env_first, env_flag

try:
    load_dotenv()
except Exception:
    pass

DEFAULT_SUBREDDITS = [
    "ChatGPT",
    "claude",
    "ClaudeAI",
    "ClaudeCode",
    "codex",
    "google_antigravity",
    "hermesagent",
    "myclaw",
    "openclaw",
    "PiCodingAgent",
]

_REDDIT_HEADERS = {
    "User-Agent": "AppleScoutAIBot/1.0 (+https://github.com/bradhjjo/apple-news-bot)"
}


# ---------------------------------------------------------------------------
# Reddit data collection
# ---------------------------------------------------------------------------

def fetch_subreddit_posts(sub: str, hours: int = 6) -> List[Dict]:
    """Fetch recent posts from a subreddit using the public JSON API."""
    url = f"https://www.reddit.com/r/{sub}/new.json?limit=100"
    cutoff = time.time() - hours * 3600
    try:
        resp = requests.get(url, headers=_REDDIT_HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        posts = []
        for child in data.get("data", {}).get("children", []):
            p = child.get("data", {})
            created = p.get("created_utc", 0)
            if created < cutoff:
                continue
            posts.append({
                "title": p.get("title", ""),
                "url": f"https://reddit.com{p.get('permalink', '')}",
                "score": p.get("score", 0),
                "num_comments": p.get("num_comments", 0),
                "subreddit": p.get("subreddit", sub),
                "created_utc": created,
            })
        print(f"  ✓ r/{sub}: {len(posts)}개 (최근 {hours}h)")
        return posts
    except Exception as exc:
        print(f"  ✗ r/{sub} 실패: {exc}")
        return []


def collect_top_posts(subreddits: List[str], hours: int, top_n: int) -> List[Dict]:
    """Collect, deduplicate, and rank posts from all subreddits."""
    all_posts: Dict[str, Dict] = {}
    for sub in subreddits:
        for post in fetch_subreddit_posts(sub, hours):
            url = post["url"]
            if url not in all_posts:
                all_posts[url] = post
        time.sleep(1)  # Reddit rate limit 준수

    ranked = sorted(
        all_posts.values(),
        key=lambda p: p["score"] + p["num_comments"] * 2,
        reverse=True,
    )
    return ranked[:top_n]


# ---------------------------------------------------------------------------
# Gemini voice script generation
# ---------------------------------------------------------------------------

def _configure_gemini():
    from google import genai

    api_key = env_first("APPLESCOUT_GEMINI_API_KEY", "GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
    return genai.Client(api_key=api_key)


def _fallback_script(posts: List[Dict]) -> str:
    now = datetime.now().strftime("%Y년 %m월 %d일 %H시")
    lines = [
        f"안녕하세요, {now} 기준 AI 커뮤니티 핫 포스트 다이제스트입니다.",
        "",
    ]
    for i, p in enumerate(posts, 1):
        lines.append(
            f"{i}위. {p['subreddit']} 서브레딧. "
            f"{p['title']}. "
            f"추천 {p['score']}점, 댓글 {p['num_comments']}개."
        )
    lines.append("")
    lines.append("이상으로 오늘의 AI 커뮤니티 소식을 전해드렸습니다.")
    return "\n".join(lines)


def generate_voice_script(posts: List[Dict]) -> str:
    """Use Gemini to produce a Korean podcast-style script from posts."""
    post_lines = "\n".join(
        f"{i}. [{p['subreddit']}] {p['title']} "
        f"(추천 {p['score']}, 댓글 {p['num_comments']})"
        for i, p in enumerate(posts, 1)
    )
    prompt = f"""당신은 AI 기술 뉴스 팟캐스트 앵커입니다.
아래는 AI 관련 Reddit 커뮤니티의 최근 6시간 인기 게시글 Top {len(posts)}입니다.
자연스러운 한국어 구어체 라디오 스크립트로 작성해주세요.

규칙:
- 각 게시글을 1~2문장으로 자연스럽게 소개 (번호 나열 금지)
- 전체 3~4분 분량 (약 600~900자)
- 서브레딧 이름을 함께 언급하여 출처를 알 수 있게 하세요
- 시작 문장: "안녕하세요, 오늘의 AI 커뮤니티 핫 포스트 다이제스트입니다."
- 마무리 문장: "이상으로 오늘의 AI 커뮤니티 소식을 전해드렸습니다."
- 스크립트 텍스트만 반환하고 다른 설명은 포함하지 마세요

게시글 목록:
{post_lines}
"""
    try:
        client = _configure_gemini()
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        script = response.text.strip()
        print(f"✓ Gemini 스크립트 생성 완료 ({len(script)}자)")
        return script
    except Exception as exc:
        print(f"✗ Gemini 실패: {exc} → 기본 스크립트 사용")
        return _fallback_script(posts)


# ---------------------------------------------------------------------------
# Text-to-speech
# ---------------------------------------------------------------------------

def text_to_speech(script: str, lang: str = "ko") -> Optional[BytesIO]:
    """Convert script to MP3 audio in memory using gTTS."""
    try:
        from gtts import gTTS

        tts = gTTS(text=script, lang=lang, slow=False)
        audio_io = BytesIO()
        tts.write_to_fp(audio_io)
        audio_io.seek(0)
        print("✓ TTS 변환 완료")
        return audio_io
    except Exception as exc:
        print(f"✗ TTS 실패: {exc}")
        return None


# ---------------------------------------------------------------------------
# Telegram delivery
# ---------------------------------------------------------------------------

def _build_text_summary(posts: List[Dict], hours: int) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "🤖 <b>AI Reddit 다이제스트</b>",
        f"⏰ {now} | 최근 {hours}시간 Top {len(posts)}",
        "",
    ]
    for i, p in enumerate(posts, 1):
        title = html.escape(p["title"])
        url = html.escape(p["url"])
        sub = html.escape(p["subreddit"])
        lines.append(
            f'{i}. <a href="{url}">{title}</a>\n'
            f'   └ r/{sub} | 👍 {p["score"]} | 💬 {p["num_comments"]}'
        )
    return "\n".join(lines)


async def _send_voice_telegram(
    bot_token: str,
    chat_id: str,
    audio_io: Optional[BytesIO],
    text_summary: str,
    voice_caption: str,
) -> None:
    from telegram import Bot
    from telegram.constants import ParseMode

    bot = Bot(token=bot_token)

    # 음성 메시지 전송
    if audio_io:
        for attempt in range(3):
            try:
                await bot.send_voice(
                    chat_id=chat_id,
                    voice=audio_io,
                    caption=voice_caption,
                )
                print("✓ Telegram 음성 메시지 전송 완료")
                break
            except Exception as exc:
                wait = 2 ** attempt
                print(f"  음성 전송 실패 (시도 {attempt+1}/3): {exc}")
                if attempt < 2:
                    await asyncio.sleep(wait)
        else:
            print("⚠️  음성 전송 3회 실패 → 텍스트만 전송")

    # 텍스트 요약 전송
    max_len = 4096
    chunks = []
    if len(text_summary) <= max_len:
        chunks = [text_summary]
    else:
        buf = ""
        for line in text_summary.split("\n"):
            if len(buf) + len(line) + 1 > max_len:
                chunks.append(buf)
                buf = line + "\n"
            else:
                buf += line + "\n"
        if buf:
            chunks.append(buf)

    for idx, chunk in enumerate(chunks, 1):
        for attempt in range(3):
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=chunk,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
                print(f"✓ Telegram 텍스트 전송 ({idx}/{len(chunks)})")
                break
            except Exception as exc:
                wait = 2 ** attempt
                print(f"  텍스트 전송 실패 (시도 {attempt+1}/3): {exc}")
                if attempt < 2:
                    await asyncio.sleep(wait)
        if idx < len(chunks):
            await asyncio.sleep(1)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def _split_csv(value: str | None, default: List[str]) -> List[str]:
    if not value:
        return default
    return [x.strip() for x in value.split(",") if x.strip()]


def main() -> int:
    bot_token = env_first("APPLESCOUT_TELEGRAM_BOT_TOKEN", "TELEGRAM_BOT_TOKEN")
    chat_id = env_first("APPLESCOUT_TELEGRAM_CHAT_ID", "TELEGRAM_CHAT_ID")
    dry_run = env_flag("APPLESCOUT_DRY_RUN", "DRY_RUN")

    if not bot_token or not chat_id:
        print("❌ TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID 누락")
        return 1

    subreddits = _split_csv(os.getenv("AI_SUBREDDITS"), DEFAULT_SUBREDDITS)
    hours = int(os.getenv("AI_REDDIT_HOURS", "6"))
    top_n = int(os.getenv("AI_REDDIT_TOP_N", "20"))
    lang = os.getenv("AI_VOICE_LANG", "ko")

    print(f"📡 {len(subreddits)}개 서브레딧에서 최근 {hours}시간 게시글 수집 중...")
    posts = collect_top_posts(subreddits, hours, top_n)
    print(f"✓ Top {len(posts)}개 포스트 선별 완료")

    if not posts:
        print("❌ 수집된 포스트 없음 (서브레딧 접근 불가 또는 최근 게시글 없음)")
        return 1

    print("🤖 Gemini 음성 스크립트 생성 중...")
    script = generate_voice_script(posts)

    print("🔊 TTS 변환 중...")
    audio_io = text_to_speech(script, lang=lang)

    text_summary = _build_text_summary(posts, hours)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    voice_caption = f"🤖 AI Reddit Top{len(posts)} | {now_str}"

    if dry_run:
        print("\n--- DRY RUN: Telegram 전송 생략 ---")
        print(f"[캡션] {voice_caption}")
        print(f"[스크립트 미리보기]\n{script[:300]}...")
        print(text_summary[:500])
        return 0

    print("📨 Telegram 전송 중...")
    asyncio.run(
        _send_voice_telegram(bot_token, chat_id, audio_io, text_summary, voice_caption)
    )
    print("✅ 완료")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
