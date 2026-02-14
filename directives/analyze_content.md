# Analyze Content

## Goal

수집된 뉴스, 소셜 미디어, 주가 데이터를 분석하고 요약합니다.

## Inputs

- `.tmp/news_articles.json`
- `.tmp/social_posts.json`
- `.tmp/stock_data.json`

## Tools/Scripts

- `execution/analyze_content.py`

## Analysis Steps

### 1. 중복 제거

- URL 기준으로 중복 뉴스 제거
- 유사한 제목 병합 (80% 이상 유사도)

### 2. 감성 분석 (TextBlob)

- 각 뉴스/포스트의 감성 점수 계산
- 긍정(positive), 중립(neutral), 부정(negative) 분류
- 전체 감성 트렌드 계산

### 3. 키워드 추출

- 빈도 기반 키워드 추출
- 중요 토픽 식별 (제품 출시, 실적 발표, 법적 이슈 등)

### 4. 중요도 순위

- 소스 신뢰도 (공식 > 주요 언론 > 소셜)
- 소셜 점수 (upvotes, comments)
- 시간 (최신 우선)

### 5. 요약 생성

- 상위 5개 뉴스 요약
- 주요 토픽별 그룹화
- 전체 트렌드 요약

## Output

- 파일: `.tmp/daily_report.json`
- 형식:

```json
{
  "date": "2026-02-08",
  "stock": {
    "price": 185.50,
    "change_percent": 1.26,
    "trend": "상승"
  },
  "sentiment": {
    "overall": "긍정적",
    "score": 0.65,
    "positive_count": 15,
    "neutral_count": 8,
    "negative_count": 3
  },
  "top_news": [
    {
      "title": "...",
      "source": "...",
      "url": "...",
      "sentiment": "긍정적"
    }
  ],
  "top_social": [
    {
      "title": "...",
      "platform": "reddit",
      "score": 234
    }
  ],
  "keywords": ["iPhone 16", "AI", "Vision Pro"],
  "summary": "전체 요약 텍스트"
}
```

## Edge Cases

- **데이터 부족**: 최소 요구사항 미달 시 경고 포함
- **감성 분석 실패**: 중립으로 분류
- **언어 혼합**: 영어 우선, 한글 번역 필요 시 표시

## Success Criteria

- 감성 분석 완료
- 상위 5개 뉴스 선정
- 전체 요약 생성
