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


def fetch_reddit_posts() -> List[Dict]:
    """Reddit에서 애플 관련 포스트 수집 (read-only, 인증 불필요)"""
    posts = []
    
    try:
        # Reddit API 없이 웹 스크래핑 방식으로 변경 (더 안정적)
        import requests
        
        subreddits = ['apple', 'stocks', 'investing']
        keywords = ['apple', 'aapl', 'iphone', 'ipad', 'mac', 'tim cook']
        
        for subreddit_name in subreddits:
            try:
                # Reddit JSON API 사용 (인증 불필요)
                url = f"https://www.reddit.com/r/{subreddit_name}/hot.json?limit=25"
                headers = {'User-Agent': 'AppleNewsBot/1.0'}
                
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code != 200:
                    print(f"✗ Reddit r/{subreddit_name} returned status {response.status_code}")
                    continue
                
                data = response.json()
                
                for post in data['data']['children']:
                    post_data = post['data']
                    title_lower = post_data['title'].lower()
                    
                    # 키워드 필터링
                    if any(keyword in title_lower for keyword in keywords):
                        posts.append({
                            'platform': 'reddit',
                            'title': post_data['title'],
                            'url': f"https://reddit.com{post_data['permalink']}",
                            'score': post_data['score'],
                            'comments': post_data['num_comments'],
                            'created': datetime.fromtimestamp(post_data['created_utc']).isoformat(),
                            'text': post_data.get('selftext', '')[:500]
                        })
                
                print(f"✓ Reddit r/{subreddit_name}: {len([p for p in posts if subreddit_name in p['url']])} posts")
                time.sleep(2)  # Reddit API 속도 제한 준수
                
            except Exception as e:
                print(f"✗ Reddit r/{subreddit_name} error: {e}")
        
    except Exception as e:
        print(f"✗ Reddit API error: {e}")
    
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
    all_posts.extend(fetch_reddit_posts())
    all_posts.extend(fetch_hackernews())
    
    # 정렬 및 필터링
    filtered_posts = filter_and_sort(all_posts)
    print(f"\n📊 Total filtered posts: {len(filtered_posts)}")
    
    # 결과 저장
    output_dir = '.tmp'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'social_posts.json')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_posts, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved {len(filtered_posts)} posts to {output_file}")
    
    return len(filtered_posts) >= 5  # 최소 5개 이상 수집 성공

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
