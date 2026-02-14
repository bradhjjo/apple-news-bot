#!/usr/bin/env python3
"""
스케줄러 스크립트
매일 지정된 시간에 메인 워크플로우 실행
"""

import schedule
import time
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import subprocess

# 환경 변수 로드
load_dotenv()

def run_daily_workflow():
    """일일 워크플로우 실행"""
    print(f"\n{'='*60}")
    print(f"🍎 Running Daily Apple News Bot")
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
    # 환경 변수에서 스케줄 시간 가져오기 (기본값: 07:00)
    schedule_time = os.getenv('SCHEDULE_TIME', '07:00')
    
    print("🤖 Apple News Bot Scheduler Started")
    print(f"📅 Scheduled to run daily at {schedule_time}")
    print(f"⏰ Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nPress Ctrl+C to stop the scheduler\n")
    
    # 스케줄 등록
    schedule.every().day.at(schedule_time).do(run_daily_workflow)
    
    # 테스트 모드: 즉시 한 번 실행 (선택사항)
    if '--test' in sys.argv:
        print("🧪 Test mode: Running workflow immediately...\n")
        run_daily_workflow()
    
    # 스케줄러 루프
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크
    except KeyboardInterrupt:
        print("\n\n👋 Scheduler stopped by user")
        sys.exit(0)

if __name__ == '__main__':
    main()
