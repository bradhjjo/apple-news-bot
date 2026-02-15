# AppleScout Agent with Gemini AI

애플 관련 뉴스, 소셜 미디어 동향 및 주가 데이터를 자동으로 분석하여 텔레그램으로 리포트를 전송하는 시스템입니다. Gemini Pro 2.5를 활용하여 매일 아침 전문가 수준의 인사이트를 제공합니다.

## 주요 기능

- AI 기반 심층 분석: Gemini Pro 2.5를 사용하여 뉴스를 요약하고, 핵심 인사이트 및 시장 전망을 추출합니다.
- 다양한 데이터 수집: Google News, Apple Newsroom 및 주요 테크 뉴스 사이트의 RSS 피드를 통해 정보를 수집합니다.
- 소셜 미디어 모니터링: Reddit과 Hacker News의 커뮤니티 반응을 실시간으로 추적합니다.
- 주가 데이터 연동: Yahoo Finance를 통해 AAPL의 실시간 가격 정보와 최근 트렌드를 분석합니다.
- 리스크 및 기회 식별: 수집된 데이터를 바탕으로 잠재적 리스크 요인과 투자 기회를 자동 분류합니다.
- 보고서 자동 전송: 분석 결과를 마크다운 형식으로 구성하여 텔레그램 메시지로 배달합니다.

## 시스템 아키텍처

이 프로젝트는 안정성과 확장성을 위해 다음과 같은 3계층 아키텍처를 채택하고 있습니다.

1. 지시 계층 (Layer 1): `directives/` 폴더에 위치한 각 작업에 대한 표준 운영 절차(SOP) 정의.
2. 조율 계층 (Layer 2): AI 에이전트를 통한 지시 사항 해석 및 워크플로우 관리.
3. 실행 계층 (Layer 3): `execution/` 폴더의 결정론적 Python 스크립트를 통한 실제 데이터 처리 및 API 연동.

## 설치 및 설정

### 사전 요구 사항

- Python 3.8 이상
- 텔레그램 봇 토큰 및 Chat ID
- Google Gemini API 키

### 설치 방법

1. 저장소 클론:

   ```bash
   cd c:\appdev\apple-scout
   ```

2. 가상 환경 설정:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows 환경: venv\Scripts\activate
   ```

3. 필수 라이브러리 설치:

   ```bash
   pip install -r requirements.txt
   ```

4. 환경 변수 구성:
   `.env.example` 파일을 `.env`로 복사하고 환경에 맞는 값을 설정합니다.

   ```bash
   copy .env.example .env
   ```

   필요한 변수: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `GEMINI_API_KEY`.

### 텔레그램 연동

1. 봇 생성: 텔레그램 [@BotFather](https://t.me/botfather)를 통해 봇을 생성하고 토큰을 발급받습니다.
2. Chat ID 획득: 생성한 봇에 메시지를 보낸 후, `https://api.telegram.org/bot<TOKEN>/getUpdates` 주소를 통해 `chat_id`를 확인합니다.

## 사용법

### 수동 실행

워크플로우를 즉시 실행하여 데이터를 분석하려면 다음 명령어를 사용합니다.

```bash
python execution/main.py
```

### 스케줄러를 통한 자동화

매일 정해진 시간에 자동으로 작동하도록 스케줄러를 실행할 수 있습니다.

```bash
python execution/scheduler.py
```

`--test` 플래그를 추가하면 설정된 시간과 관계없이 즉시 실행 테스트가 가능합니다.

## 프로젝트 구조

- `directives/`: 데이터 수집, 분석, 통보를 위한 SOP 가이드.
- `execution/`: 데이터 획득 및 처리 로직이 담긴 Python 스크립트.
- `.tmp/`: 처리 중 생성되는 중간 데이터 저장소.
- `AGENTS.md`: 아키텍처 및 에이전트 상세 가이드.
- `README.md`: 영문 본문 문서.

## 문제 해결

- 메시지 전송 실패: `.env` 내의 토큰 정보가 정확한지, 봇과 대화가 시작되었는지 확인하십시오.
- 데이터 획득 오류: 네트워크 연결 상태와 각 서비스의 RSS 피드 접근성을 점검하십시오.
- 자연어 처리 오류: 감성 분석용 텍스트 처리를 위해 다음 명령어로 필요한 데이터를 다운로드하십시오.

  ```bash
  python -m textblob.download_corpora
  ```

## 클라우드 실행 가이드 (GitHub Actions)

본 프로젝트는 GitHub Actions를 통해 로컬 서버 없이도 매일 정해진 시간에 자동 실행되도록 설계되었습니다.

1. 코드를 GitHub 저장소에 푸시합니다.
2. 저장소 설정(Settings > Secrets and variables > Actions)에서 `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `GEMINI_API_KEY`를 등록합니다.
3. 매일 한국 시간 기준 오전 7시(UTC 13:00)에 자동으로 워크플로우가 가동됩니다.

더 자세한 설정 방법은 [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)를 참조하십시오.

## 라이선스

이 프로젝트는 MIT 라이선스에 따라 배포됩니다.
