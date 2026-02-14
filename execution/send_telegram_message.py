#!/usr/bin/env python3
"""
텔레그램 메시지 전송 스크립트 (Gemini AI 버전)
Directive: directives/send_telegram_report.md
"""

import json
import os
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError
import asyncio
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def format_gemini_report(report: dict) -> str:
    """Gemini 분석 리포트를 텔레그램 HTML 형식으로 변환"""
    lines = []
    
    # 헤더
    lines.append("🍎 <b>애플 일일 AI 리포트</b>")
    lines.append(f"📅 {report['date']}")
    lines.append("🤖 <i>Powered by Gemini 2.5 Flash</i>")
    lines.append("")
    
    # 주가 정보
    stock = report.get('stock', {})
    if stock and stock.get('current_price'):
        price = stock['current_price']
        change_pct = stock['change_percent']
        trend_emoji = "📈" if change_pct > 0 else "📉" if change_pct < 0 else "➡️"
        sign = "+" if change_pct > 0 else ""
        
        lines.append("💰 <b>주가 정보</b>")
        lines.append(f"AAPL: ${price} ({sign}{change_pct}% {trend_emoji})")
        lines.append(f"5일 트렌드: {stock.get('trend_5day', 'N/A')}")
        lines.append("")
    
    # Gemini AI 분석
    gemini = report.get('gemini_analysis', {})
    
    # 전체 감성
    sentiment = gemini.get('overall_sentiment', '중립')
    sentiment_score = gemini.get('sentiment_score', 0.5)
    sentiment_emoji = "😊" if sentiment == "긍정적" else "😐" if sentiment == "중립" else "😟"
    
    lines.append(f"{sentiment_emoji} <b>AI 감성 분석</b>")
    lines.append(f"{sentiment} ({sentiment_score}/1.0)")
    lines.append("")
    
    # 핵심 요약
    exec_summary = gemini.get('executive_summary', '')
    if exec_summary:
        lines.append("📊 <b>핵심 요약</b>")
        lines.append(exec_summary)
        lines.append("")
    
    # 주요 인사이트
    insights = gemini.get('key_insights', [])
    if insights:
        lines.append("💡 <b>주요 인사이트</b>")
        for i, insight in enumerate(insights[:5], 1):
            lines.append(f"{i}. {insight}")
        lines.append("")
    
    # 주요 토픽
    topics = gemini.get('top_topics', [])
    if topics:
        topics_str = ' '.join([f"#{t.replace(' ', '_')}" for t in topics[:8]])
        lines.append("🔑 <b>주요 토픽</b>")
        lines.append(topics_str)
        lines.append("")
    
    # 시장 전망
    outlook = gemini.get('market_outlook', '')
    if outlook:
        lines.append("🔮 <b>시장 전망</b>")
        lines.append(outlook)
        lines.append("")
    
    # 기회 요인
    opportunities = gemini.get('opportunities', [])
    if opportunities:
        lines.append("✅ <b>기회 요인</b>")
        for opp in opportunities[:3]:
            lines.append(f"• {opp}")
        lines.append("")
    
    # 리스크 요인
    risks = gemini.get('risk_factors', [])
    if risks:
        lines.append("⚠️ <b>리스크 요인</b>")
        for risk in risks[:3]:
            lines.append(f"• {risk}")
        lines.append("")
    
    # 상세 분석
    detailed = gemini.get('detailed_analysis', '')
    if detailed:
        lines.append("📝 <b>상세 분석</b>")
        lines.append(detailed)
        lines.append("")
    
    # 데이터 출처
    news_count = report.get('news_count', 0)
    social_count = report.get('social_count', 0)
    lines.append("📈 <b>데이터 출처</b>")
    lines.append(f"뉴스: {news_count}개 | 소셜: {social_count}개")
    
    return '\n'.join(lines)

async def send_telegram_message(bot_token: str, chat_id: str, message: str, max_retries: int = 3):
    """텔레그램 메시지 전송 (비동기)"""
    bot = Bot(token=bot_token)
    
    # 메시지가 너무 길면 분할
    max_length = 4096
    if len(message) > max_length:
        # 섹션별로 분할
        parts = message.split('\n\n')
        current_message = ""
        messages = []
        
        for part in parts:
            if len(current_message) + len(part) + 2 < max_length:
                current_message += part + '\n\n'
            else:
                messages.append(current_message)
                current_message = part + '\n\n'
        
        if current_message:
            messages.append(current_message)
    else:
        messages = [message]
    
    # 메시지 전송 (HTML 포맷 사용)
    for i, msg in enumerate(messages):
        for attempt in range(max_retries):
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=msg,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
                print(f"✓ Message part {i+1}/{len(messages)} sent successfully")
                
                if i < len(messages) - 1:
                    await asyncio.sleep(1)
                
                break
            except TelegramError as e:
                print(f"✗ Attempt {attempt+1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise

def main():
    """메인 실행 함수"""
    print("📱 Starting Telegram message send (Gemini version)...")
    
    # 환경 변수 확인
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("❌ Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in .env")
        return False
    
    # Gemini 리포트 로드
    report_file = '.tmp/gemini_report.json'
    if not os.path.exists(report_file):
        print(f"❌ Gemini report file not found: {report_file}")
        print("⚠️  Trying fallback to basic report...")
        
        # 폴백: 기본 리포트 사용
        report_file = '.tmp/daily_report.json'
        if not os.path.exists(report_file):
            print(f"❌ No report file found")
            return False
    
    with open(report_file, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    # 메시지 포맷팅
    message = format_gemini_report(report)
    
    # 메시지 전송
    try:
        asyncio.run(send_telegram_message(bot_token, chat_id, message))
        print("✅ Telegram message sent successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
