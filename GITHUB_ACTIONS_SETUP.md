# GitHub Actions 자동 배포 가이드

## 🚀 GitHub Actions로 자동 실행 설정하기

이 가이드를 따라하면 **15분 안에** 매일 아침 7시 자동 실행이 완료됩니다!

---

## 1️⃣ GitHub 저장소 생성

### 옵션 A: GitHub 웹사이트에서

1. [GitHub](https://github.com) 로그인
2. 우측 상단 `+` → `New repository` 클릭
3. 저장소 이름: `apple-news-bot` (원하는 이름)
4. **Public** 또는 **Private** 선택 (둘 다 무료)
5. `Create repository` 클릭

### 옵션 B: GitHub CLI로

```bash
gh repo create apple-news-bot --public --source=. --remote=origin --push
```

---

## 2️⃣ 코드를 GitHub에 푸시

```bash
cd c:\appdev\stocknews_bot

# Git 초기화 (아직 안했다면)
git init

# 모든 파일 추가 (.gitignore가 .env 제외함)
git add .

# 커밋
git commit -m "Initial commit: Apple News Bot with Gemini AI"

# GitHub 저장소 연결 (본인의 username으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/apple-news-bot.git

# 푸시
git push -u origin main
```

> **중요**: `.env` 파일은 자동으로 제외됩니다 (`.gitignore`에 포함)

---

## 3️⃣ GitHub Secrets 설정 (API 키 등록)

### 웹사이트에서 설정

1. GitHub 저장소 페이지로 이동
2. `Settings` 탭 클릭
3. 왼쪽 메뉴에서 `Secrets and variables` → `Actions` 클릭
4. `New repository secret` 버튼 클릭

### 다음 3개의 Secret 추가

#### Secret 1: TELEGRAM_BOT_TOKEN

- Name: `TELEGRAM_BOT_TOKEN`
- Value: `YOUR_TELEGRAM_BOT_TOKEN` (BotFather에서 발급받은 토큰)

#### Secret 2: TELEGRAM_CHAT_ID

- Name: `TELEGRAM_CHAT_ID`
- Value: `YOUR_TELEGRAM_CHAT_ID` (본인의 Chat ID)

#### Secret 3: GEMINI_API_KEY

- Name: `GEMINI_API_KEY`
- Value: `YOUR_GEMINI_API_KEY` (Google AI Studio에서 발급받은 키)

---

## 4️⃣ 자동 실행 확인

### GitHub Actions 페이지에서

1. 저장소의 `Actions` 탭 클릭
2. 왼쪽에서 `Daily Apple News Bot` 워크플로우 선택
3. 다음 실행 예정 시간 확인

### 수동으로 테스트 실행

1. `Actions` 탭 → `Daily Apple News Bot` 선택
2. 우측 `Run workflow` 버튼 클릭
3. `Run workflow` 확인
4. 약 1분 후 텔레그램으로 메시지 도착!

---

## 📅 스케줄 설정

현재 설정: **매일 UTC 13:00 (CST 7:00 AM)**

### 시간 변경하려면

`.github/workflows/daily-news.yml` 파일의 cron 수정:

```yaml
schedule:
  - cron: '0 13 * * *'  # UTC 13:00 = CST 7:00 AM
```

#### 다른 시간 예시

- `0 14 * * *` - 오전 8시 (CST)
- `0 12 * * *` - 오전 6시 (CST)
- `0 1 * * *` - 오후 7시 (CST)

> **참고**: GitHub Actions는 UTC 기준입니다. CST는 UTC-6입니다.

---

## ✅ 완료

이제 매일 아침 7시에 자동으로:

1. 🍎 애플 뉴스 50개 수집
2. 💬 소셜 미디어 포스트 수집
3. 📈 주가 데이터 수집
4. 🤖 Gemini AI 분석
5. 📱 텔레그램으로 리포트 전송

---

## 🔍 모니터링

### 실행 로그 확인

1. `Actions` 탭 → 최근 실행 클릭
2. `Run Apple News Bot` 단계 클릭
3. 상세 로그 확인

### 실패 시

- GitHub에서 자동으로 이메일 알림
- `Actions` 탭에서 빨간색 X 표시
- 로그에서 오류 원인 확인
- `Re-run jobs` 버튼으로 재실행

---

## 💰 비용

**완전 무료!**

- GitHub Actions: 무료 (월 2,000분)
- 일일 사용량: ~1분
- 월 사용량: ~30분 (무료 한도의 1.5%)

---

## 🛠️ 문제 해결

### "Secrets not found" 오류

→ GitHub Secrets 설정 확인 (대소문자 정확히)

### 텔레그램 메시지 안옴

→ `Actions` 로그에서 오류 확인

### Gemini API 오류

→ API 키 확인 및 할당량 체크

### 시간이 안맞음

→ UTC 시간대 확인 (CST = UTC-6)

---

## 📝 추가 팁

### 여러 시간대에 실행

```yaml
schedule:
  - cron: '0 13 * * *'  # 오전 7시
  - cron: '0 1 * * *'   # 오후 7시
```

### 주말 제외

```yaml
schedule:
  - cron: '0 13 * * 1-5'  # 월-금만
```

### 알림 끄기

저장소 Settings → Notifications → Actions 체크 해제

---

## 🎉 성공

이제 컴퓨터를 끄고 있어도 매일 아침 애플 뉴스 리포트를 받을 수 있습니다! 🚀
