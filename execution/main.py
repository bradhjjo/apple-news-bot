#!/usr/bin/env python3
"""
메인 오케스트레이션 스크립트
모든 단계를 순서대로 실행하는 Layer 2 역할
"""

import sys
import os
from datetime import datetime

# 실행 스크립트 임포트
sys.path.insert(0, os.path.dirname(__file__))

def run_step(step_name: str, script_path: str) -> bool:
    """개별 스크립트 실행"""
    print(f"\n{'='*60}")
    print(f"Step: {step_name}")
    print(f"{'='*60}")
    
    try:
        # 스크립트를 서브프로세스로 실행
        import subprocess
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ {step_name} completed successfully")
            return True
        else:
            print(f"❌ {step_name} failed with exit code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ {step_name} failed with error: {e}")
        return False

def main():
    """메인 워크플로우"""
    print("🚀 Starting Apple News Bot Daily Workflow")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 스크립트 디렉토리
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 실행 단계 정의
    steps = [
        ("뉴스 수집", os.path.join(script_dir, "scrape_news.py")),
        ("소셜 미디어 수집", os.path.join(script_dir, "fetch_social_media.py")),
        ("주가 데이터 수집", os.path.join(script_dir, "fetch_stock_data.py")),
        ("Gemini AI 분석", os.path.join(script_dir, "analyze_with_gemini.py")),
        ("텔레그램 전송", os.path.join(script_dir, "send_telegram_message.py"))
    ]

    
    # 각 단계 실행
    results = []
    for step_name, script_path in steps:
        success = run_step(step_name, script_path)
        results.append((step_name, success))
        
        # 중요 단계 실패 시 중단 (텔레그램 전송은 제외)
        if not success and step_name != "텔레그램 전송":
            print(f"\n⚠️  Critical step '{step_name}' failed. Continuing anyway...")
    
    # 결과 요약
    print(f"\n{'='*60}")
    print("📊 Workflow Summary")
    print(f"{'='*60}")
    
    for step_name, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {step_name}")
    
    # 전체 성공 여부
    all_success = all(success for _, success in results)
    
    print(f"\n⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if all_success:
        print("🎉 All steps completed successfully!")
        return 0
    else:
        print("⚠️  Some steps failed. Check logs above.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
