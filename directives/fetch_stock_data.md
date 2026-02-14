# Fetch Stock Data

## Goal

애플(AAPL) 주가 정보를 무료로 수집합니다.

## Inputs

- 티커: AAPL
- 기간: 지난 5일 (트렌드 파악용)

## Tools/Scripts

- `execution/fetch_stock_data.py`

## Data Source

### Yahoo Finance (yfinance)

- 무료, API 키 불필요
- 실시간에 가까운 주가 데이터
- 거래량, 시가총액 등 포함

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
- **네트워크 오류**: 재시도 후 실패 시 null 반환

## Success Criteria

- 최신 주가 데이터 수집 완료
- 변동률 계산 완료
- 5일 트렌드 분석 완료
