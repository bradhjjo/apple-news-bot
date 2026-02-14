#!/usr/bin/env python3
"""
주가 데이터 수집 스크립트
Directive: directives/fetch_stock_data.md
"""

import json
import os
import yfinance as yf
from datetime import datetime, timedelta

def fetch_stock_data(symbol: str = 'AAPL') -> dict:
    """Yahoo Finance에서 주가 데이터 수집"""
    print(f"📈 Fetching stock data for {symbol}...")
    
    try:
        # 티커 객체 생성
        ticker = yf.Ticker(symbol)
        
        # 현재 정보
        info = ticker.info
        
        # 최근 5일 히스토리
        hist = ticker.history(period='5d')
        
        if hist.empty:
            print("✗ No historical data available")
            return None
        
        # 최신 가격
        current_price = hist['Close'].iloc[-1]
        
        # 전일 대비 변동
        if len(hist) > 1:
            prev_price = hist['Close'].iloc[-2]
            change = current_price - prev_price
            change_percent = (change / prev_price) * 100
        else:
            change = 0
            change_percent = 0
        
        # 5일 트렌드 계산
        if len(hist) >= 5:
            first_price = hist['Close'].iloc[0]
            trend_change = ((current_price - first_price) / first_price) * 100
            if trend_change > 1:
                trend = "상승"
            elif trend_change < -1:
                trend = "하락"
            else:
                trend = "보합"
        else:
            trend = "데이터 부족"
        
        # 결과 구성
        stock_data = {
            'symbol': symbol,
            'current_price': round(float(current_price), 2),
            'change': round(float(change), 2),
            'change_percent': round(float(change_percent), 2),
            'volume': int(hist['Volume'].iloc[-1]) if 'Volume' in hist else 0,
            'market_cap': info.get('marketCap', 0),
            '52_week_high': info.get('fiftyTwoWeekHigh', 0),
            '52_week_low': info.get('fiftyTwoWeekLow', 0),
            'trend_5day': trend,
            'last_updated': datetime.now().isoformat()
        }
        
        print(f"✓ Current price: ${stock_data['current_price']} ({stock_data['change_percent']:+.2f}%)")
        print(f"✓ 5-day trend: {trend}")
        
        return stock_data
        
    except Exception as e:
        print(f"✗ Error fetching stock data: {e}")
        print("⚠️  Returning placeholder data...")
        # 오류 시 기본 데이터 반환 (워크플로우 계속 진행)
        return {
            'symbol': symbol,
            'current_price': 0,
            'change': 0,
            'change_percent': 0,
            'volume': 0,
            'market_cap': 0,
            '52_week_high': 0,
            '52_week_low': 0,
            'trend_5day': '데이터 없음',
            'last_updated': datetime.now().isoformat(),
            'error': str(e)
        }


def main():
    """메인 실행 함수"""
    print("💰 Starting stock data collection...")
    
    # AAPL 주가 데이터 수집
    stock_data = fetch_stock_data('AAPL')
    
    if not stock_data:
        print("❌ Failed to fetch stock data")
        # 빈 데이터라도 파일 생성
        stock_data = {
            'symbol': 'AAPL',
            'current_price': 0,
            'change': 0,
            'change_percent': 0,
            'volume': 0,
            'market_cap': 0,
            '52_week_high': 0,
            '52_week_low': 0,
            'trend_5day': '데이터 없음',
            'last_updated': datetime.now().isoformat()
        }

    
    # 결과 저장
    output_dir = '.tmp'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'stock_data.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(stock_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved stock data to {output_file}")
    
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
