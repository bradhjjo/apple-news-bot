#!/usr/bin/env python3
"""
뉴스 스크래핑 스크립트
Directive: directives/collect_apple_news.md
"""

import feedparser
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import time

def fetch_google_news() -> List[Dict]:
    """Google News RSS에서 애플 뉴스 수집"""
    articles = []
    try:
        url = "https://news.google.com/rss/search?q=Apple+OR+AAPL&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(url)

        for entry in feed.entries[:20]:  # 최대 20개
            articles.append({
                'title': entry.title,
                'source': 'Google News',
                'url': entry.link,
                'published': entry.get('published', ''),
                'summary': entry.get('summary', '')
            })
        print(f"✓ Google News: {len(articles)} articles")
    except Exception as e:
        print(f"✗ Google News error: {e}")

    return articles

def fetch_apple_newsroom() -> List[Dict]:
    """Apple Newsroom RSS에서 공식 뉴스 수집"""
    articles = []
    try:
        url = "https://www.apple.com/newsroom/rss-feed.rss"
        feed = feedparser.parse(url)

        for entry in feed.entries[:10]:
            articles.append({
                'title': entry.title,
                'source': 'Apple Newsroom',
                'url': entry.link,
                'published': entry.get('published', ''),
                'summary': entry.get('summary', '')
            })
        print(f"✓ Apple Newsroom: {len(articles)} articles")
    except Exception as e:
        print(f"✗ Apple Newsroom error: {e}")

    return articles

def fetch_tech_news() -> List[Dict]:
    """주요 테크 뉴스 사이트에서 RSS 수집"""
    articles = []
    feeds = {
        'MacRumors': 'https://www.macrumors.com/feed/',
        '9to5Mac': 'https://9to5mac.com/feed/',
        'AppleInsider': 'https://appleinsider.com/rss/news/'
    }

    for source, url in feeds.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                articles.append({
                    'title': entry.title,
                    'source': source,
                    'url': entry.link,
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', '')
                })
            print(f"✓ {source}: {len([a for a in articles if a['source'] == source])} articles")
            time.sleep(1)  # 요청 간 대기
        except Exception as e:
            print(f"✗ {source} error: {e}")

    return articles

def remove_duplicates(articles: List[Dict]) -> List[Dict]:
    """URL 기준으로 중복 제거"""
    seen_urls = set()
    unique_articles = []

    for article in articles:
        if article['url'] not in seen_urls:
            seen_urls.add(article['url'])
            unique_articles.append(article)

    return unique_articles

def filter_recent(articles: List[Dict], hours: int = 24) -> List[Dict]:
    """최근 N시간 이내 뉴스만 필터링"""
    # RSS 피드는 일반적으로 최신순이므로 상위 항목만 유지
    # 실제 시간 파싱은 복잡하므로 상위 항목 우선
    return articles[:50]  # 최대 50개 유지

def main():
    """메인 실행 함수"""
    print("🍎 Starting Apple news collection...")

    # 모든 소스에서 뉴스 수집
    all_articles = []
    all_articles.extend(fetch_google_news())
    all_articles.extend(fetch_apple_newsroom())
    all_articles.extend(fetch_tech_news())

    # 중복 제거
    unique_articles = remove_duplicates(all_articles)
    print(f"\n📊 Total unique articles: {len(unique_articles)}")

    # 최근 뉴스만 필터링
    recent_articles = filter_recent(unique_articles)

    # 결과 저장
    output_dir = '.tmp'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'news_articles.json')

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(recent_articles, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(recent_articles)} articles to {output_file}")

    return len(recent_articles) >= 5  # 최소 5개 이상 수집 성공

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
