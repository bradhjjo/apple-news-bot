# Send Telegram Report

## Goal

분석된 리포트를 텔레그램으로 전송합니다.

## Inputs

- `.tmp/gemini_report.json` 우선, 없으면 `.tmp/daily_report.json`
- 환경 변수: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`

## Tools/Scripts

- `execution/send_telegram_message.py`

## Message Format

### 텔레그램 HTML 형식

```html
🍎 <b>AppleScout Agent AI 리포트</b>
📅 2026-02-08

💰 <b>주가 정보</b>
AAPL: $185.50 (+1.26% ↗️)
5일 트렌드: 상승

😊 <b>AI 감성 분석</b>
긍정적 (0.65/1.0)

🔑 *주요 키워드*
#iPhone16 #AI #VisionPro
```

## Telegram API

### 메시지 전송

- API: `sendMessage`
- Parse mode: `HTML`
- 최대 길이: 4096자

### 긴 메시지 처리

- 4096자 초과 시 자동 분할
- 섹션 단위로 먼저 분할하고, 섹션 하나가 4096자를 넘으면 내부 텍스트도 추가 분할

## Edge Cases

- **메시지 너무 긴 경우**: 섹션별 분할 전송
- **HTML 파싱 오류**: 사용자/모델 출력 텍스트는 HTML escape 처리
- **전송 실패**: 3회 재시도 (지수 백오프)
- **봇 토큰 무효**: 오류 로그 및 사용자 알림

## Success Criteria

- 텔레그램 메시지 전송 성공
- 모든 섹션 포함
- 링크 클릭 가능
- 이모지 정상 표시
