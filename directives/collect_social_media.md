# Collect Social Media Content

## Goal

애플 관련 소셜 미디어 포스트를 무료로 수집합니다.

## Inputs

- 검색 키워드: "Apple", "AAPL", "iPhone", "iPad", "Mac"
- 시간 범위: 지난 24시간

## Tools/Scripts

- `execution/fetch_social_media.py`

## Data Sources

### 1. Reddit RSS

- Subreddits: r/apple, r/stocks, r/investing
- 무료, API 키 불필요
- 최신 핫 포스트 및 댓글

### 2. Google News Discussion Queries

- Apple stock analysis, AAPL stock opinion, Apple earnings discussion
- 무료, API 키 불필요
- 투자 관점 기사와 논평성 콘텐츠 수집

### 3. Seeking Alpha RSS

- URL: `https://seekingalpha.com/api/sa/combined/AAPL.xml`
- 무료 RSS 기반 수집
- AAPL 분석성 글 수집

### 4. Hacker News API

- URL: `https://hacker-news.firebaseio.com/v0/`
- 무료, API 키 불필요
- 애플 관련 토론 및 링크

## Output

- 파일: `.tmp/social_posts.json`
- 형식:

```json
[
  {
    "platform": "reddit|google_news|seeking_alpha|hackernews",
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

- **API/RSS 속도 제한**: 요청 간 1-2초 대기
- **관련 없는 포스트**: 키워드 필터링
- **삭제된 포스트**: 스킵
- **네트워크 오류**: 소스 단위로 실패 처리 후 가능한 소스 계속 수집

## Success Criteria

- 소셜 수집 실패가 전체 워크플로우를 중단하지 않음
- 생성 시간 기준 최신 포스트 우선, 동일 시간대에서는 score 참고
- 24시간 이내 포스트만 포함
