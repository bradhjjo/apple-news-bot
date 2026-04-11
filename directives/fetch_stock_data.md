# Fetch Stock Data

## Goal

애플(AAPL) 주가 정보를 무료로 수집합니다.

## Inputs

- 티커: AAPL
- 기간: 지난 5일 (트렌드 파악용)

## Tools/Scripts

- `execution/fetch_stock_data.py`

## Data Source

### 1. Stooq CSV

- 무료, API 키 불필요
- 최근 일별 OHLCV 데이터 제공
- 1차 소스로 사용

### 2. Yahoo Finance Chart API

- 무료, API 키 불필요
- 5일 가격, 거래량, 일부 메타데이터 제공
- Stooq 실패 시 폴백

### 3. Google Finance Page

- 무료, API 키 불필요
- 현재가와 당일 변동률 스크래핑
- 앞선 소스 실패 시 최종 폴백

## Output

- 파일: `.tmp/stock_data.json`
- 형식:

```json
{
  "symbol": "AAPL",
  "current_price": 185.50,
  "change": 2.30,
  "change_percent": 1.26,
  "volume": 52000000,
  "market_cap": 2850000000000,
  "52_week_high": 199.62,
  "52_week_low": 164.08,
  "trend_5day": "상승|하락|보합"
}
```

## Edge Cases

- **시장 휴장**: 최근 거래일 데이터 사용
- **데이터 지연**: 15-20분 지연 가능 (무료 데이터)
- **네트워크 오류**: 다음 데이터 소스로 폴백
- **모든 소스 실패**: `source: "none"` 및 `current_price: 0` placeholder 반환 후 워크플로우 계속 진행

## Success Criteria

- 최신 주가 데이터 수집 완료
- 변동률 계산 완료
- 5일 트렌드 분석 완료
