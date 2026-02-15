# Security Scan Script
# Based on SECURITY.md guidelines

$patterns = @(
    "AIzaSy[A-Za-z0-9_-]{33}", # Gemini
    "[0-9]{10}:[A-Za-z0-9_-]{35}", # Telegram
    "sk-[A-Za-z0-9]{48}" # OpenAI/Other
)

$foundSecrets = $false

Write-Host "🔍 Starting security scan..." -ForegroundColor Cyan

# Check staged changes
$diff = git diff --cached

foreach ($pattern in $patterns) {
    if ($diff -match $pattern) {
        Write-Host "❌ ALERT: Potential secret found matching pattern: $pattern" -ForegroundColor Red
        $foundSecrets = $true
    }
}

if ($foundSecrets) {
    Write-Host "⚠️  Scan failed. Please remove secrets before committing." -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "✅ Scan passed. No obvious secrets detected in staged changes." -ForegroundColor Green
    exit 0
}
