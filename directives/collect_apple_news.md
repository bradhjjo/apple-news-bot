# Collect Apple News

## Goal

매일 아침 최신 애플 관련 뉴스를 무료 소스에서 수집합니다.

## Inputs

- 검색 키워드: "Apple", "AAPL", "iPhone", "iPad", "Mac", "Tim Cook"
- 시간 범위: 지난 24시간

## Tools/Scripts

- `execution/scrape_news.py`

## Data Sources

### 1. Google News RSS Feed

- URL: `https://news.google.com/rss/search?q=Apple+OR+AAPL&hl=en-US&gl=US&ceid=US:en`
- 무료, API 키 불필요
- 최신 뉴스 헤드라인 및 링크 제공

### 2. Apple Newsroom

- URL: `https://www.apple.com/newsroom/`
- 공식 애플 보도자료
- RSS 피드: `https://www.apple.com/newsroom/rss-feed.rss`

### 3. Tech News Sites (RSS)

- MacRumors: `https://www.macrumors.com/feed/`
- 9to5Mac: `https://9to5mac.com/feed/`
- AppleInsider: `https://appleinsider.com/rss/news/`

## Output

- 파일: `.tmp/news_articles.json`
- 형식:

```json
[
  {
    "title": "뉴스 제목",
    "source": "출처",
    "url": "링크",
    "published": "발행 시간",
    "summary": "요약 (있는 경우)"
  }
]
```

## Edge Cases

- **RSS 피드 다운**: 다른 소스로 폴백
- **중복 뉴스**: URL 기준으로 중복 제거
- **네트워크 오류**: 3회 재시도 후 실패 시 빈 배열 반환
- **파싱 오류**: 해당 항목 스킵, 로그 기록

## Success Criteria

- 최소 5개 이상의 뉴스 항목 수집
- 24시간 이내 뉴스만 포함
- 중복 제거 완료
