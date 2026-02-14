#!/usr/bin/env python3
"""
Gemini AI 분석 스크립트
Gemini Pro 2.5를 사용한 고급 뉴스 분석 및 요약
"""

import json
import os
from datetime import datetime
from typing import List, Dict
import google.generativeai as genai
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def configure_gemini():
    """Gemini API 설정"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")
    
    genai.configure(api_key=api_key)
    # gemini-2.5-flash 모델 사용
    return genai.GenerativeModel('gemini-2.5-flash')


def analyze_with_gemini(news_articles: List[Dict], social_posts: List[Dict], stock_data: Dict) -> Dict:
    """Gemini AI로 뉴스 분석 및 요약"""
    
    print("🤖 Starting Gemini AI analysis...")
    
    try:
        model = configure_gemini()
        
        # 프롬프트 구성
        prompt = f"""당신은 애플(Apple Inc.) 전문 애널리스트입니다. 다음 데이터를 분석하여 한국어로 종합 리포트를 작성해주세요.

## 주가 정보
- 현재가: ${stock_data.get('current_price', 'N/A')}
- 변동률: {stock_data.get('change_percent', 'N/A')}%
- 5일 트렌드: {stock_data.get('trend_5day', 'N/A')}

## 최신 뉴스 ({len(news_articles)}개)
"""
        
        # 상위 10개 뉴스 추가
        for i, article in enumerate(news_articles[:10], 1):
            prompt += f"{i}. {article['title']} (출처: {article['source']})\n"
        
        prompt += f"\n## 소셜 미디어 반응 ({len(social_posts)}개)\n"
        
        # 상위 5개 소셜 포스트 추가
        for i, post in enumerate(social_posts[:5], 1):
            prompt += f"{i}. {post['title']} (점수: {post.get('score', 0)})\n"
        
        prompt += """

다음 형식으로 JSON 응답을 작성해주세요:

{
  "overall_sentiment": "긍정적|중립|부정적",
  "sentiment_score": 0.0-1.0 사이의 숫자,
  "key_insights": [
    "핵심 인사이트 1",
    "핵심 인사이트 2",
    "핵심 인사이트 3"
  ],
  "executive_summary": "200자 이내의 전체 요약",
  "detailed_analysis": "500자 이내의 상세 분석",
  "market_outlook": "향후 전망 (100자 이내)",
  "top_topics": ["주요 토픽1", "주요 토픽2", "주요 토픽3"],
  "risk_factors": ["리스크 요인1", "리스크 요인2"],
  "opportunities": ["기회 요인1", "기회 요인2"]
}

JSON만 반환하고 다른 텍스트는 포함하지 마세요."""

        # Gemini API 호출
        response = model.generate_content(prompt)
        
        # JSON 파싱
        response_text = response.text.strip()
        
        # JSON 코드 블록 제거 (있는 경우)
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        analysis = json.loads(response_text.strip())
        
        print("✓ Gemini analysis completed")
        print(f"✓ Sentiment: {analysis.get('overall_sentiment')}")
        print(f"✓ Key insights: {len(analysis.get('key_insights', []))}")
        
        return analysis
        
    except Exception as e:
        print(f"✗ Gemini analysis failed: {e}")
        print("⚠️  Falling back to basic analysis...")
        
        # 폴백: 기본 분석 반환
        return {
            "overall_sentiment": "중립",
            "sentiment_score": 0.5,
            "key_insights": [
                f"{len(news_articles)}개의 뉴스 기사 수집됨",
                f"{len(social_posts)}개의 소셜 미디어 포스트 분석됨",
                "AI 분석을 사용할 수 없어 기본 분석 제공"
            ],
            "executive_summary": f"애플 관련 {len(news_articles)}개 뉴스와 {len(social_posts)}개 소셜 포스트를 수집했습니다.",
            "detailed_analysis": "Gemini API를 사용할 수 없어 상세 분석을 제공할 수 없습니다. API 키를 확인해주세요.",
            "market_outlook": "데이터 부족으로 전망 제공 불가",
            "top_topics": ["Apple", "iPhone", "Technology"],
            "risk_factors": ["API 연결 실패"],
            "opportunities": ["AI 분석 활성화 시 더 나은 인사이트 제공 가능"]
        }

def load_data():
    """수집된 데이터 로드"""
    data = {}
    
    # 뉴스 데이터
    news_file = '.tmp/news_articles.json'
    if os.path.exists(news_file):
        with open(news_file, 'r', encoding='utf-8') as f:
            data['news'] = json.load(f)
    else:
        data['news'] = []
    
    # 소셜 미디어 데이터
    social_file = '.tmp/social_posts.json'
    if os.path.exists(social_file):
        with open(social_file, 'r', encoding='utf-8') as f:
            data['social'] = json.load(f)
    else:
        data['social'] = []
    
    # 주가 데이터
    stock_file = '.tmp/stock_data.json'
    if os.path.exists(stock_file):
        with open(stock_file, 'r', encoding='utf-8') as f:
            data['stock'] = json.load(f)
    else:
        data['stock'] = {}
    
    return data

def main():
    """메인 실행 함수"""
    print("🤖 Starting Gemini AI content analysis...")
    
    # 데이터 로드
    data = load_data()
    
    if not data['news'] and not data['social']:
        print("❌ No data to analyze")
        return False
    
    print(f"✓ Loaded {len(data['news'])} news articles")
    print(f"✓ Loaded {len(data['social'])} social posts")
    
    # Gemini AI 분석
    gemini_analysis = analyze_with_gemini(
        data['news'],
        data['social'],
        data['stock']
    )
    
    # 기존 TextBlob 분석도 유지 (폴백용)
    from analyze_content import analyze_sentiment
    
    textblob_sentiments = []
    for article in data['news'][:10]:
        text = f"{article['title']} {article.get('summary', '')}"
        sentiment, score = analyze_sentiment(text)
        textblob_sentiments.append(score)
    
    textblob_avg = sum(textblob_sentiments) / len(textblob_sentiments) if textblob_sentiments else 0
    
    # 결과 구성
    report = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'stock': data['stock'],
        'gemini_analysis': gemini_analysis,
        'textblob_sentiment_score': round(textblob_avg, 2),
        'news_count': len(data['news']),
        'social_count': len(data['social']),
        'top_news': data['news'][:5],
        'top_social': data['social'][:5]
    }
    
    # 결과 저장
    output_dir = '.tmp'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'gemini_report.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved Gemini analysis report to {output_file}")
    
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
