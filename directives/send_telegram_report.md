# Send Telegram Report

## Goal

분석된 리포트를 텔레그램으로 전송합니다.

## Inputs

- `.tmp/daily_report.json`
- 환경 변수: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`

## Tools/Scripts

- `execution/send_telegram_message.py`

## Message Format

### 텔레그램 마크다운 형식

```markdown
🍎 *AppleScout Agent 리포트* - 2026-02-08

📈 *주가 정보*
AAPL: $185.50 (+1.26% ↗️)
5일 트렌드: 상승

😊 *전체 감성*
긍정적 (0.65/1.0)
긍정 15 | 중립 8 | 부정 3

📰 *주요 뉴스*
1. [뉴스 제목](링크) - 출처
   감성: 긍정적

2. [뉴스 제목](링크) - 출처
   감성: 중립

💬 *소셜 미디어 하이라이트*
1. [포스트 제목](링크) - Reddit (👍 234)
2. [포스트 제목](링크) - HackerNews (👍 156)

🔑 *주요 키워드*
#iPhone16 #AI #VisionPro

📝 *요약*
전체 요약 텍스트...
```

## Telegram API

### 메시지 전송

- API: `sendMessage`
- Parse mode: `MarkdownV2`
- 최대 길이: 4096자

### 긴 메시지 처리

- 4096자 초과 시 자동 분할
- 섹션 단위로 분할 (뉴스, 소셜 등)

## Edge Cases

- **메시지 너무 긴 경우**: 섹션별 분할 전송
- **마크다운 파싱 오류**: 특수문자 이스케이프
- **전송 실패**: 3회 재시도 (지수 백오프)
- **봇 토큰 무효**: 오류 로그 및 사용자 알림

## Success Criteria

- 텔레그램 메시지 전송 성공
- 모든 섹션 포함
- 링크 클릭 가능
- 이모지 정상 표시
