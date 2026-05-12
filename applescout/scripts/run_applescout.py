#!/usr/bin/env python3
"""Run the AppleScout pipeline in skill-oriented order."""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from applescout.scripts.utils_paths import tmp_dir


def clean_tmp_dir() -> None:
    tmp_path = tmp_dir()
    print(f"🧹 Cleaning temporary directory: {tmp_path}")
    for item in tmp_path.iterdir():
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)


def run_step(step_name: str, func, critical: bool, *args) -> bool:
    print(f"\n{'=' * 60}")
    print(f"Step: {step_name}")
    print(f"{'=' * 60}")
    try:
        success = bool(func(*args))
    except Exception as exc:
        print(f"❌ {step_name} failed with error: {exc}")
        success = False
    if success:
        print(f"✅ {step_name} completed successfully")
    else:
        print(f"❌ {step_name} failed")
        if critical:
            print(f"\n🛑 Critical step '{step_name}' failed. Stopping workflow.")
    return success


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the AppleScout workflow.")
    parser.add_argument("--dry-run", action="store_true", help="Skip Telegram delivery and write a preview instead.")
    parser.add_argument("--keep-tmp", action="store_true", help="Do not delete existing .tmp artifacts before running.")
    parser.add_argument("--skip-reddit-voice", action="store_true", help="Skip Reddit AI voice digest step.")
    args = parser.parse_args(argv)

    print("🚀 Starting AppleScout Agent Daily Workflow")
    if not args.keep_tmp:
        clean_tmp_dir()
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    from applescout.scripts.analyze_gemini import main as analyze_gemini_main
    from applescout.scripts.collect_news import main as collect_news_main
    from applescout.scripts.collect_social import main as collect_social_main
    from applescout.scripts.collect_stock import main as collect_stock_main
    from applescout.scripts.send_report import main as send_report_main
    from execution.reddit_voice_digest import main as reddit_voice_main

    steps = [
        ("뉴스 수집", collect_news_main, True, None),
        ("소셜 미디어 수집", collect_social_main, False, None),
        ("주가 데이터 수집", collect_stock_main, False, None),
        ("Gemini AI 분석", analyze_gemini_main, True, None),
        ("텔레그램 전송", send_report_main, True, ["--dry-run"] if args.dry_run else None),
    ]
    if not args.skip_reddit_voice:
        steps.append(("Reddit AI 음성 다이제스트", reddit_voice_main, False, None))

    results = []
    critical_failure = None
    for step_name, func, critical, extra_args in steps:
        success = run_step(step_name, func, critical, *(extra_args or ()))
        results.append((step_name, success))
        if critical and not success:
            critical_failure = step_name
            break

    print(f"\n{'=' * 60}")
    print("📊 Workflow Summary")
    print(f"{'=' * 60}")
    for step_name, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {step_name}")
    print(f"\n⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if all(success for _, success in results):
        print("🎉 All steps completed successfully!")
        return 0
    if critical_failure:
        print(f"🛑 Workflow stopped due to critical failure: {critical_failure}")
    print("⚠️  Some steps failed. Check logs above.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
