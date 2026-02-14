#!/usr/bin/env python3
"""
소셜 미디어 수집 스크립트
Directive: directives/collect_social_media.md
"""

import json
import os
import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict


def fetch_google_news_discussions() -> List[Dict]:
    """Google News에서 애플 관련 토론/의견 기사 수집"""
    posts = []
    
    try:
        import feedparser
        
        # Google News RSS - 의견/분석 기사
        queries = [
            'Apple stock analysis',
            'AAPL stock opinion',
            'Apple earnings discussion'
        ]
        
        for query in queries:
            try:
                url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-US&gl=US&ceid=US:en"
                feed = feedparser.parse(url)
                
                for entry in feed.entries[:10]:
                    posts.append({
                        'platform': 'google_news',
                        'title': entry.title,
                        'url': entry.link,
                        'score': 0,  # Google News doesn't have scores
                        'comments': 0,
                        'created': entry.get('published', datetime.now().isoformat()),
                        'text': entry.get('summary', '')[:500]
                    })
                
                print(f"✓ Google News ({query}): {len([p for p in posts if query.split()[0].lower() in p['title'].lower()])} articles")
                time.sleep(1)
                
            except Exception as e:
                print(f"✗ Google News ({query}) error: {e}")
        
    except Exception as e:
        print(f"✗ Google News error: {e}")
    
    return posts


def fetch_seeking_alpha_rss() -> List[Dict]:
    """Seeking Alpha RSS에서 애플 관련 분석 수집"""
    posts = []
    
    try:
        import feedparser
        
        # Seeking Alpha Apple 피드
        url = "https://seekingalpha.com/api/sa/combined/AAPL.xml"
        
        try:
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:15]:
                posts.append({
                    'platform': 'seeking_alpha',
                    'title': entry.title,
                    'url': entry.link,
                    'score': 0,
                    'comments': 0,
                    'created': entry.get('published', datetime.now().isoformat()),
                    'text': entry.get('summary', '')[:500]
                })
            
            print(f"✓ Seeking Alpha: {len(posts)} articles")
            
        except Exception as e:
            print(f"✗ Seeking Alpha error: {e}")
        
    except Exception as e:
        print(f"✗ Seeking Alpha RSS error: {e}")
    
    return posts


def fetch_hackernews() -> List[Dict]:
    """Hacker News에서 애플 관련 포스트 수집"""
    posts = []
    
    try:
        # 최신 스토리 ID 가져오기
        top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        response = requests.get(top_stories_url, timeout=10)
        story_ids = response.json()[:100]  # 상위 100개
        
        keywords = ['apple', 'aapl', 'iphone', 'ipad', 'mac', 'ios']
        
        for story_id in story_ids[:50]:  # 최대 50개 확인
            try:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                story_response = requests.get(story_url, timeout=5)
                story = story_response.json()
                
                if story and 'title' in story:
                    title_lower = story['title'].lower()
                    if any(keyword in title_lower for keyword in keywords):
                        posts.append({
                            'platform': 'hackernews',
                            'title': story['title'],
                            'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                            'score': story.get('score', 0),
                            'comments': story.get('descendants', 0),
                            'created': datetime.fromtimestamp(story.get('time', 0)).isoformat(),
                            'text': story.get('text', '')[:500]
                        })
            except Exception as e:
                continue  # 개별 스토리 오류는 스킵
        
        print(f"✓ Hacker News: {len(posts)} posts")
        
    except Exception as e:
        print(f"✗ Hacker News error: {e}")
    
    return posts

def filter_and_sort(posts: List[Dict]) -> List[Dict]:
    """점수 기준으로 정렬 및 필터링"""
    # 점수 기준 내림차순 정렬
    sorted_posts = sorted(posts, key=lambda x: x['score'], reverse=True)
    
    # 24시간 이내 포스트만 (간단한 필터링)
    # 실제로는 created 시간 파싱 필요하지만 여기서는 상위 항목 유지
    return sorted_posts[:30]  # 상위 30개

def main():
    """메인 실행 함수"""
    print("💬 Starting social media collection...")
    
    # 모든 플랫폼에서 포스트 수집
    all_posts = []
    
    try:
        google_posts = fetch_google_news_discussions()
        all_posts.extend(google_posts)
    except Exception as e:
        print(f"⚠️  Google News collection failed: {e}")
    
    try:
        sa_posts = fetch_seeking_alpha_rss()
        all_posts.extend(sa_posts)
    except Exception as e:
        print(f"⚠️  Seeking Alpha collection failed: {e}")
    
    try:
        hn_posts = fetch_hackernews()
        all_posts.extend(hn_posts)
    except Exception as e:
        print(f"⚠️  Hacker News collection failed: {e}")
    
    # 정렬 및 필터링
    filtered_posts = filter_and_sort(all_posts)
    print(f"\n📊 Total filtered posts: {len(filtered_posts)}")
    
    # 결과 저장 (빈 리스트라도 저장)
    output_dir = '.tmp'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'social_posts.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_posts, f, ensure_ascii=False, indent=2)
    
    if len(filtered_posts) == 0:
        print("⚠️  No social media posts collected, but continuing workflow...")
        print(f"✅ Saved empty posts list to {output_file}")
    else:
        print(f"✅ Saved {len(filtered_posts)} posts to {output_file}")
    
    # 항상 성공 반환 (소셜 미디어 수집 실패가 전체 워크플로우를 중단하지 않도록)
    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
