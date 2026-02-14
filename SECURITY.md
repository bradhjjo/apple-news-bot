# 보안 가이드

## ⚠️ 절대 커밋하면 안되는 파일

다음 파일들은 **절대로** Git에 커밋하면 안됩니다:

- `.env` - 실제 API 키가 포함된 환경 변수 파일
- `*.key` - 개인 키 파일
- `secrets.json` - 민감 정보가 포함된 설정 파일
- `credentials.txt` - 인증 정보

## ✅ 안전한 관리 방법

### 로컬 개발

- `.env` 파일에 실제 키 저장
- `.gitignore`에 `.env` 포함 (이미 설정됨)
- `.env.example`에는 예시 값만 포함

### GitHub Actions

- GitHub Secrets에 API 키 저장
- 코드에는 `${{ secrets.KEY_NAME }}` 형식으로만 참조

### 문서화

- 실제 키 값 대신 `YOUR_API_KEY` 같은 플레이스홀더 사용
- 키 발급 방법만 안내

## 🔍 커밋 전 체크리스트

커밋하기 전에 다음을 확인하세요:

```powershell
# 변경된 파일 확인
git status

# 파일 내용 확인
git diff

# API 키 패턴 검색
git diff | Select-String -Pattern "AIza|[0-9]{10}:[A-Za-z0-9_-]{35}|sk-[A-Za-z0-9]{48}"
```

## 🚨 실수로 커밋한 경우

1. **즉시 API 키 무효화**
2. **Git 히스토리에서 제거** (BFG Repo-Cleaner 사용)
3. **새 키 발급 및 GitHub Secrets 업데이트**
4. **강제 푸시로 원격 저장소 덮어쓰기**

## 📚 참고 자료

- [GitHub Secrets 사용법](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
- [Git 민감 정보 제거](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
