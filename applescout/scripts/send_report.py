#!/usr/bin/env python3
"""Send or dry-run the AppleScout Telegram report."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from applescout.scripts.format_report import format_gemini_report
from applescout.scripts.utils_io import env_first, env_flag, load_json
from applescout.scripts.utils_paths import tmp_file


def split_message(message: str, max_length: int = 4096) -> list[str]:
    if len(message) <= max_length:
        return [message]

    def split_oversized_part(part: str) -> list[str]:
        if len(part) <= max_length:
            return [part]
        chunks = []
        for start in range(0, len(part), max_length):
            chunks.append(part[start : start + max_length])
        return chunks

    parts = message.split("\n\n")
    messages = []
    current = ""
    for part in parts:
        if len(part) > max_length:
            if current:
                messages.append(current.rstrip())
                current = ""
            messages.extend(split_oversized_part(part))
            continue
        candidate = f"{current}{part}\n\n"
        if current and len(candidate.rstrip()) > max_length:
            messages.append(current.rstrip())
            current = f"{part}\n\n"
        else:
            current = candidate
    if current:
        messages.append(current.rstrip())
    return messages


async def send_telegram_message(bot_token: str, chat_id: str, message: str, max_retries: int = 3) -> None:
    from telegram import Bot
    from telegram.constants import ParseMode
    from telegram.error import TelegramError

    bot = Bot(token=bot_token)
    messages = split_message(message)
    for index, chunk in enumerate(messages, 1):
        for attempt in range(max_retries):
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=chunk,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
                print(f"✓ Message part {index}/{len(messages)} sent successfully")
                if index < len(messages):
                    await asyncio.sleep(1)
                break
            except TelegramError as exc:
                print(f"✗ Attempt {attempt + 1}/{max_retries} failed: {exc}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise


def resolve_dry_run(cli_dry_run: bool = False) -> bool:
    return cli_dry_run or env_flag("APPLESCOUT_DRY_RUN", "DRY_RUN", default=False)


def load_report(report_path: Path | None = None) -> dict:
    path = report_path or tmp_file("gemini_report.json")
    if not path.exists():
        path = tmp_file("daily_report.json")
    if not path.exists():
        raise FileNotFoundError("No report file found in .tmp/")
    return load_json(path, {})


def main(argv: list[str] | None = None) -> bool:
    parser = argparse.ArgumentParser(description="Send AppleScout report to Telegram.")
    parser.add_argument("--dry-run", action="store_true", help="Format the report but do not send it.")
    parser.add_argument("--report-file", type=Path, help="Optional report JSON path.")
    args = parser.parse_args(argv)

    print("📱 Starting Telegram report delivery...")
    try:
        report = load_report(args.report_file)
    except FileNotFoundError as exc:
        print(f"❌ {exc}")
        return False
    message = format_gemini_report(report)

    if resolve_dry_run(args.dry_run):
        preview_path = tmp_file("telegram_message_preview.txt")
        preview_path.write_text(message, encoding="utf-8")
        print(f"🧪 Dry run enabled. Wrote preview to {preview_path}")
        return True

    bot_token = env_first("APPLESCOUT_TELEGRAM_BOT_TOKEN", "TELEGRAM_BOT_TOKEN")
    chat_id = env_first("APPLESCOUT_TELEGRAM_CHAT_ID", "TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        print("❌ Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID environment variables")
        return False
    try:
        asyncio.run(send_telegram_message(bot_token, chat_id, message))
        print("✅ Telegram message sent successfully")
        return True
    except Exception as exc:
        print(f"❌ Failed to send Telegram message: {exc}")
        return False


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
