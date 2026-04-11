#!/usr/bin/env python3
"""
콘텐츠 분석 스크립트
Directive: directives/analyze_content.md
"""

import json
import os
from datetime import datetime
from typing import List, Dict
from textblob import TextBlob
from collections import Counter
import re

def load_data():
    """수집된 데이터 로드"""
    data = {}

    # 뉴스 데이터
    news_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.tmp', 'news_articles.json')
    if os.path.exists(news_file):
        with open(news_file, 'r', encoding='utf-8') as f:
            data['news'] = json.load(f)
    else:
        data['news'] = []

    # 소셜 미디어 데이터
    social_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.tmp', 'social_posts.json')
    if os.path.exists(social_file):
        with open(social_file, 'r', encoding='utf-8') as f:
            data['social'] = json.load(f)
    else:
        data['social'] = []

    # 주가 데이터
    stock_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.tmp', 'stock_data.json')
    if os.path.exists(stock_file):
        with open(stock_file, 'r', encoding='utf-8') as f:
            data['stock'] = json.load(f)
    else:
        data['stock'] = None

    return data

def analyze_sentiment(text: str) -> tuple:
    """텍스트 감성 분석 (TextBlob 사용)"""
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 (부정) ~ 1 (긍정)

        if polarity > 0.1:
            sentiment = "긍정적"
        elif polarity < -0.1:
            sentiment = "부정적"
        else:
            sentiment = "중립"

        return sentiment, polarity
    except:
        return "중립", 0.0

def analyze_content(data: dict) -> dict:
    """전체 콘텐츠 분석"""
    print("🔍 Analyzing content...")

    # 감성 분석
    sentiments = {'긍정적': 0, '중립': 0, '부정적': 0}
    sentiment_scores = []

    # 뉴스 분석
    analyzed_news = []
    for article in data['news'][:10]:  # 상위 10개
        text = f"{article['title']} {article.get('summary', '')}"
        sentiment, score = analyze_sentiment(text)

        sentiments[sentiment] += 1
        sentiment_scores.append(score)

        analyzed_news.append({
            'title': article['title'],
            'source': article['source'],
            'url': article['url'],
            'sentiment': sentiment,
            'score': round(score, 2)
        })

    # 소셜 미디어 분석
    analyzed_social = []
    for post in data['social'][:10]:  # 상위 10개
        text = f"{post['title']} {post.get('text', '')}"
        sentiment, score = analyze_sentiment(text)

        sentiments[sentiment] += 1
        sentiment_scores.append(score)

        analyzed_social.append({
            'title': post['title'],
            'platform': post['platform'],
            'url': post['url'],
            'score': post['score'],
            'sentiment': sentiment
        })

    # 전체 감성 점수
    overall_score = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0

    if overall_score > 0.1:
        overall_sentiment = "긍정적"
    elif overall_score < -0.1:
        overall_sentiment = "부정적"
    else:
        overall_sentiment = "중립"

    # 키워드 추출
    all_text = ' '.join([a['title'] for a in data['news']] + [p['title'] for p in data['social']])
    keywords = extract_keywords(all_text)

    # 요약 생성
    summary = generate_summary(analyzed_news, analyzed_social, overall_sentiment)

    # 결과 구성
    report = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'stock': data['stock'] if data['stock'] else {
            'price': 0,
            'change_percent': 0,
            'trend': '데이터 없음'
        },
        'sentiment': {
            'overall': overall_sentiment,
            'score': round(overall_score, 2),
            'positive_count': sentiments['긍정적'],
            'neutral_count': sentiments['중립'],
            'negative_count': sentiments['부정적']
        },
        'top_news': analyzed_news[:5],
        'top_social': analyzed_social[:5],
        'keywords': keywords[:10],
        'summary': summary
    }

    print(f"✓ Sentiment: {overall_sentiment} ({overall_score:.2f})")
    print(f"✓ Top keywords: {', '.join(keywords[:5])}")

    return report

def extract_keywords(text: str) -> List[str]:
    """키워드 추출 (빈도 기반)"""
    # 소문자 변환 및 단어 추출
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

    # 불용어 제거
    stopwords = {'the', 'and', 'for', 'with', 'this', 'that', 'from', 'are', 'was', 'has', 'have', 'will', 'can', 'but', 'not', 'you', 'all', 'new', 'more', 'get', 'how', 'out', 'now', 'may'}
    filtered_words = [w for w in words if w not in stopwords and len(w) > 3]

    # 빈도 계산
    word_freq = Counter(filtered_words)

    # 상위 키워드 반환
    return [word.capitalize() for word, count in word_freq.most_common(15)]

def generate_summary(news: List[Dict], social: List[Dict], sentiment: str) -> str:
    """전체 요약 생성"""
    summary_parts = []

    # 뉴스 요약
    if news:
        top_news_titles = [n['title'][:60] + '...' if len(n['title']) > 60 else n['title'] for n in news[:3]]
        summary_parts.append(f"주요 뉴스: {', '.join(top_news_titles)}")

    # 감성 요약
    summary_parts.append(f"전체적으로 {sentiment} 분위기입니다.")

    # 소셜 미디어 요약
    if social:
        summary_parts.append(f"소셜 미디어에서 {len(social)}개의 관련 토론이 활발합니다.")

    return ' '.join(summary_parts)

def main():
    """메인 실행 함수"""
    print("📊 Starting content analysis...")

    # 데이터 로드
    data = load_data()

    if not data['news'] and not data['social']:
        print("❌ No data to analyze")
        return False

    print(f"✓ Loaded {len(data['news'])} news articles")
    print(f"✓ Loaded {len(data['social'])} social posts")

    # 콘텐츠 분석
    report = analyze_content(data)

    # 결과 저장
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.tmp')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'daily_report.json')

    tmp_output_file = output_file + '.tmp'
    with open(tmp_output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    os.replace(tmp_output_file, output_file)

    print(f"✅ Saved analysis report to {output_file}")

    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
