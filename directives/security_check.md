# SOP: Security Check

## Goal

Prevent the accidental commitment of sensitive information (API keys, secrets, credentials) to version control.

## When to Run

- Before every `git commit`
- Before every `git push`
- When adding new dependencies or documentation

## Procedure

### 1. Identify Sensitive Patterns

Use the following regex patterns to search for potential secrets:

- **Gemini API Key**: `AIzaSy[A-Za-z0-9_-]{33}`
- **Telegram Bot Token**: `[0-9]{10}:[A-Za-z0-9_-]{35}`
- **Telegram Chat ID**: `[0-9]{10}` (Use caution, may have false positives)
- **Generic Private Key**: `-----BEGIN [A-Z ]+ PRIVATE KEY-----`

### 2. Manual Scan (Agent Workflow)

Run the following commands to inspect the changes:

```powershell
# Check staged changes for patterns
git diff --cached | Select-String -Pattern "AIzaSy|:[A-Za-z0-9_-]{35}|PRIVATE KEY"

# Review the names of staged files
git status
```

### 3. Verify .gitignore

Ensure that `.env`, `*.key`, and other local secret files are NOT tracked.

```powershell
git ls-files --stage | Select-String -Pattern ".env"
```

## Emergency Response

If a secret is detected in a *previous* commit:

1. **Revoke** the token immediately.
2. Follow the "🚨 실수로 커밋한 경우" section in `SECURITY.md`.
