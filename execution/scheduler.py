#!/usr/bin/env python3
"""
Deprecated local scheduler.

Prefer OpenClaw cron or another external scheduler calling
`applescout/scripts/run_applescout.py`.
"""

import time
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import subprocess

# 환경 변수 로드 (.env 파일이 있으면 로드, 없으면 시스템 환경 변수 사용)
try:
    load_dotenv()
except:
    pass  # GitHub Actions 등에서는 .env 파일이 없을 수 있음

def run_daily_workflow():
    """일일 워크플로우 실행"""
    print(f"\n{'='*60}")
    print(f"🍎 Running Daily AppleScout Agent")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    # main.py 실행
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(script_dir, "main.py")

    try:
        result = subprocess.run(
            [sys.executable, main_script],
            capture_output=False,
            text=True
        )

        if result.returncode == 0:
            print("\n✅ Daily workflow completed successfully")
        else:
            print(f"\n❌ Daily workflow failed with exit code {result.returncode}")

    except Exception as e:
        print(f"\n❌ Error running daily workflow: {e}")

def main():
    """메인 스케줄러"""
    # 환경 변수에서 스케줄 시간 가져오기 (기본값: 06:00)
    schedule_time = os.getenv('SCHEDULE_TIME', '06:00')
    try:
        scheduled_hour, scheduled_minute = [int(part) for part in schedule_time.split(":", 1)]
    except ValueError:
        print(f"❌ Invalid SCHEDULE_TIME: {schedule_time}. Expected HH:MM.")
        return 1

    print("🤖 AppleScout Agent Scheduler Started")
    print("⚠️  Deprecated: prefer OpenClaw cron with applescout/scripts/run_applescout.py")
    print(f"📅 Scheduled to run daily at {schedule_time}")
    print(f"⏰ Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nPress Ctrl+C to stop the scheduler\n")

    # 테스트 모드: 즉시 한 번 실행 (선택사항)
    if '--test' in sys.argv:
        print("🧪 Test mode: Running workflow immediately...\n")
        run_daily_workflow()

    # 스케줄러 루프
    last_run_date = None
    try:
        while True:
            now = datetime.now()
            should_run = (
                now.hour == scheduled_hour
                and now.minute == scheduled_minute
                and last_run_date != now.date()
            )
            if should_run:
                run_daily_workflow()
                last_run_date = now.date()
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n\n👋 Scheduler stopped by user")
        sys.exit(0)

if __name__ == '__main__':
    raise SystemExit(main() or 0)
