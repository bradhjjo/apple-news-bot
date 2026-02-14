# Analyze Content with Gemini AI

## Goal

Gemini Pro 2.5를 사용하여 수집된 뉴스와 소셜 미디어를 고급 AI 분석합니다.

## Inputs

- `.tmp/news_articles.json`
- `.tmp/social_posts.json`
- `.tmp/stock_data.json`
- 환경 변수: `GEMINI_API_KEY`

## Tools/Scripts

- `execution/analyze_with_gemini.py`

## Analysis Features

### 1. AI 기반 감성 분석

- Gemini Pro 2.5의 자연어 이해 능력 활용
- 단순 긍정/부정을 넘어선 뉘앙스 파악
- 시장 심리 분석

### 2. 핵심 인사이트 추출

- 뉴스에서 중요한 정보 자동 추출
- 투자 관점에서의 시사점 도출
- 3-5개의 핵심 인사이트 제공

### 3. 전문가 수준 요약

- 200자 이내 핵심 요약
- 500자 이내 상세 분석
- 맥락을 고려한 종합 분석

### 4. 시장 전망

- 단기 시장 전망 제시
- 주가 트렌드와 뉴스 연관성 분석

### 5. 리스크/기회 분석

- 잠재적 리스크 요인 식별
- 투자 기회 포착

## Output

- 파일: `.tmp/gemini_report.json`
- 형식:

```json
{
  "date": "2026-02-08",
  "stock": {...},
  "gemini_analysis": {
    "overall_sentiment": "긍정적|중립|부정적",
    "sentiment_score": 0.75,
    "key_insights": [
      "인사이트 1",
      "인사이트 2",
      "인사이트 3"
    ],
    "executive_summary": "핵심 요약",
    "detailed_analysis": "상세 분석",
    "market_outlook": "시장 전망",
    "top_topics": ["토픽1", "토픽2"],
    "risk_factors": ["리스크1", "리스크2"],
    "opportunities": ["기회1", "기회2"]
  },
  "news_count": 50,
  "social_count": 21
}
```

## Gemini API Configuration

### API 키 발급

1. [Google AI Studio](https://aistudio.google.com/app/apikey) 방문
2. "Get API key" 클릭
3. 새 프로젝트 생성 또는 기존 프로젝트 선택
4. API 키 복사
5. `.env` 파일에 `GEMINI_API_KEY=your_key_here` 추가

### 모델 선택

- **gemini-2.0-flash-exp**: 빠르고 효율적, 무료 할당량 제공
- 뉴스 분석에 최적화된 성능

### 비용

- 무료 할당량: 분당 15 요청
- 일일 1회 실행 시 완전 무료

## Edge Cases

### API 키 없음

- TextBlob 기반 기본 분석으로 폴백
- 경고 메시지 출력

### API 호출 실패

- 재시도 없이 즉시 폴백
- 기본 분석 결과 반환

### JSON 파싱 오류

- Gemini 응답에서 코드 블록 제거
- 파싱 실패 시 폴백

### 속도 제한

- 일일 1회 실행이므로 문제 없음
- 필요시 재시도 로직 추가 가능

## Success Criteria

- Gemini API 호출 성공
- 3개 이상의 핵심 인사이트 생성
- 전체 요약 및 상세 분석 완료
- 리스크/기회 분석 포함

## Advantages over TextBlob

| 기능 | TextBlob | Gemini Pro 2.5 |
|------|----------|----------------|
| 감성 분석 | 단순 점수 | 맥락 이해 |
| 요약 | 없음 | 전문가 수준 |
| 인사이트 | 없음 | 자동 추출 |
| 시장 전망 | 없음 | AI 예측 |
| 한국어 지원 | 제한적 | 완벽 지원 |
| 비용 | 무료 | 무료 (할당량 내) |
