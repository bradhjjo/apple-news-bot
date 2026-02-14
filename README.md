# 🍎 Apple News Bot with Gemini AI

매일 아침 7시에 애플 관련 뉴스와 소셜 미디어를 분석하여 텔레그램으로 전송하는 자동화 봇입니다.

**🆕 Gemini Pro 2.5 AI 통합**: 전문가 수준의 뉴스 분석, 인사이트 추출, 시장 전망 제공

## 📋 주요 기능

- **🤖 Gemini AI 분석**: 전문가 수준의 뉴스 요약 및 인사이트
- **📰 뉴스 수집**: Google News, Apple Newsroom, 주요 테크 뉴스 사이트
- **💬 소셜 미디어**: Reddit, Hacker News에서 애플 관련 토론 수집
- **📈 주가 정보**: Yahoo Finance에서 AAPL 주가 및 트렌드 분석
- **💡 핵심 인사이트**: AI가 자동으로 중요한 정보 추출
- **🔮 시장 전망**: Gemini AI 기반 시장 예측
- **⚠️ 리스크 분석**: 잠재적 리스크 요인 자동 식별
- **📱 텔레그램 알림**: 분석 결과를 마크다운 형식으로 전송

## 🏗️ 아키텍처

이 프로젝트는 `AGENTS.md`에 정의된 **3계층 아키텍처**를 따릅니다:

- **Layer 1 (Directives)**: `directives/` - 각 작업의 SOP 문서
- **Layer 2 (Orchestration)**: AI 에이전트 - 의사결정 및 워크플로우 관리
- **Layer 3 (Execution)**: `execution/` - 결정론적 Python 스크립트

## 🚀 설치 방법

### 1. 저장소 클론

```bash
cd c:\appdev\stocknews_bot
```

### 2. 가상 환경 생성 (권장)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정

`.env.example`을 `.env`로 복사하고 필요한 값을 입력하세요:

```bash
copy .env.example .env
```

`.env` 파일 편집:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
SCHEDULE_TIME=07:00
```

#### 텔레그램 봇 설정 방법

1. **BotFather로 봇 생성**:
   - 텔레그램에서 [@BotFather](https://t.me/botfather) 검색
   - `/newbot` 명령어 입력
   - 봇 이름과 사용자명 설정
   - 받은 토큰을 `TELEGRAM_BOT_TOKEN`에 입력

2. **Chat ID 확인**:
   - 봇과 대화 시작 (메시지 하나 전송)
   - 브라우저에서 `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` 접속
   - `"chat":{"id":123456789}` 형식에서 ID 확인
   - 해당 ID를 `TELEGRAM_CHAT_ID`에 입력

## 💻 사용 방법

### 수동 실행 (테스트용)

개별 스크립트 테스트:

```bash
python execution/scrape_news.py
python execution/fetch_social_media.py
python execution/fetch_stock_data.py
python execution/analyze_content.py
python execution/send_telegram_message.py
```

전체 워크플로우 실행:

```bash
python execution/main.py
```

### 스케줄러 실행

#### 테스트 모드 (즉시 실행)

```bash
python execution/scheduler.py --test
```

#### 백그라운드 실행

```bash
python execution/scheduler.py
```

스케줄러는 매일 `.env`에 설정된 시간(기본 07:00)에 자동으로 실행됩니다.

### Windows 작업 스케줄러 설정 (선택사항)

Windows에서 부팅 시 자동 실행하려면:

1. **작업 스케줄러** 열기
2. **기본 작업 만들기** 선택
3. 트리거: "컴퓨터를 시작할 때"
4. 작업: "프로그램 시작"
5. 프로그램: `C:\appdev\stocknews_bot\venv\Scripts\python.exe`
6. 인수: `C:\appdev\stocknews_bot\execution\scheduler.py`
7. 시작 위치: `C:\appdev\stocknews_bot`

## 📁 프로젝트 구조

```
stocknews_bot/
├── directives/                    # Layer 1: 지시사항
│   ├── collect_apple_news.md
│   ├── collect_social_media.md
│   ├── fetch_stock_data.md
│   ├── analyze_content.md
│   └── send_telegram_report.md
├── execution/                     # Layer 3: 실행 스크립트
│   ├── scrape_news.py
│   ├── fetch_social_media.py
│   ├── fetch_stock_data.py
│   ├── analyze_content.py
│   ├── send_telegram_message.py
│   ├── main.py
│   └── scheduler.py
├── .tmp/                          # 임시 파일 (자동 생성)
├── .env                           # 환경 변수 (직접 생성)
├── .env.example                   # 환경 변수 템플릿
├── .gitignore
├── requirements.txt
├── AGENTS.md                      # 아키텍처 가이드
└── README.md
```

## 🔧 트러블슈팅

### 텔레그램 메시지가 전송되지 않음

- `.env` 파일의 `TELEGRAM_BOT_TOKEN`과 `TELEGRAM_CHAT_ID` 확인
- 봇과 대화를 시작했는지 확인 (최소 한 번은 메시지 전송 필요)

### Reddit 데이터 수집 실패

- 네트워크 연결 확인
- Reddit API가 일시적으로 다운될 수 있음 (다른 소스는 계속 작동)

### 주가 데이터가 없음

- 시장 휴장일인지 확인
- Yahoo Finance API가 일시적으로 지연될 수 있음

### 감성 분석 오류

- TextBlob 언어 데이터 다운로드:

  ```bash
  python -m textblob.download_corpora
  ```

## 📊 출력 예시

텔레그램으로 전송되는 AI 리포트 예시:

```
🍎 애플 일일 AI 리포트
📅 2026-02-08
🤖 Powered by Gemini Pro 2.5

💰 주가 정보
AAPL: $185.50 (+1.26% 📈)
5일 트렌드: 상승

😊 AI 감성 분석
긍정적 (0.75/1.0)

📊 핵심 요약
애플은 Vision Pro 확장과 iPhone 혁신으로 긍정적 모멘텀을 
유지하고 있습니다. 소셜 미디어 반응도 호의적이며, 주가는 
안정적인 상승세를 보이고 있습니다.

💡 주요 인사이트
1. Vision Pro 글로벌 출시 확대로 공간 컴퓨팅 시장 선점
2. iPhone 18 Pro Max 배터리 개선으로 프리미엄 경쟁력 강화
3. NASA Artemis 미션 iPhone 채택으로 브랜드 가치 상승

🔑 주요 토픽
#VisionPro #iPhone18 #NASA #AI #배터리

🔮 시장 전망
단기적으로 긍정적 전망. Vision Pro 판매 확대와 iPhone 
신제품 기대감이 주가 상승 요인으로 작용할 것으로 예상됩니다.

✅ 기회 요인
• 공간 컴퓨팅 시장 선점 기회
• 프리미엄 제품 라인업 강화

⚠️ 리스크 요인
• Apple News 광고 품질 논란
• 글로벌 경제 불확실성

📈 데이터 출처
뉴스: 50개 | 소셜: 21개
```

## 🚀 클라우드 자동 실행 (GitHub Actions)

**로컬 컴퓨터 없이 매일 자동 실행!**

### 빠른 시작

1. **GitHub 저장소 생성 및 푸시**

   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/apple-news-bot.git
   git push -u origin main
   ```

2. **GitHub Secrets 설정**
   - 저장소 → Settings → Secrets and variables → Actions
   - 다음 3개 Secret 추가:
     - `TELEGRAM_BOT_TOKEN`
     - `TELEGRAM_CHAT_ID`
     - `GEMINI_API_KEY`

3. **완료!**
   - 매일 UTC 13:00 (CST 7:00 AM) 자동 실행
   - Actions 탭에서 수동 실행도 가능

📖 **상세 가이드**: [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)

---

## 🤝 기여

이 프로젝트는 자가 개선(self-annealing) 원칙을 따릅니다:

- 오류 발견 시 스크립트 수정
- 학습한 내용을 `directives/` 문서에 업데이트
- 시스템이 점진적으로 개선됨

## 📄 라이선스

MIT License

## 🙏 감사의 말

- 무료 API 제공: Google News, Reddit, Hacker News, Yahoo Finance
- 라이브러리: python-telegram-bot, feedparser, yfinance, textblob
