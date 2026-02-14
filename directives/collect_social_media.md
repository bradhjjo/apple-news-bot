# Collect Social Media Content

## Goal

애플 관련 소셜 미디어 포스트를 무료로 수집합니다.

## Inputs

- 검색 키워드: "Apple", "AAPL", "iPhone", "iPad", "Mac"
- 시간 범위: 지난 24시간

## Tools/Scripts

- `execution/fetch_social_media.py`

## Data Sources

### 1. Reddit API (PRAW)

- Subreddits: r/apple, r/stocks, r/investing
- 무료, API 키 불필요 (read-only)
- 최신 핫 포스트 및 댓글

### 2. Hacker News API

- URL: `https://hacker-news.firebaseio.com/v0/`
- 무료, API 키 불필요
- 애플 관련 토론 및 링크

## Output

- 파일: `.tmp/social_posts.json`
- 형식:

```json
[
  {
    "platform": "reddit|hackernews",
    "title": "포스트 제목",
    "url": "링크",
    "score": 123,
    "comments": 45,
    "created": "생성 시간",
    "text": "본문 내용"
  }
]
```

## Edge Cases

- **API 속도 제한**: 요청 간 1초 대기
- **관련 없는 포스트**: 키워드 필터링
- **삭제된 포스트**: 스킵
- **네트워크 오류**: 재시도 로직

## Success Criteria

- 최소 10개 이상의 포스트 수집
- 점수(score) 기준 상위 포스트 우선
- 24시간 이내 포스트만 포함
