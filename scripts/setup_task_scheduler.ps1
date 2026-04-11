# ============================================
# AppleScout Agent - Windows Task Scheduler 등록
# 관리자 권한으로 실행 필요
# ============================================

$TaskName = "AppleScout Daily Agent"
$Description = "매일 오전 6시에 AppleScout Agent를 실행하여 애플 뉴스를 수집/분석하고 텔레그램으로 전송합니다."
$ScriptPath = "c:\appdev\apple-scout\run_apple_scout.bat"
$WorkingDir = "c:\appdev\apple-scout"

# 기존 작업이 있으면 제거
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "기존 작업 '$TaskName' 제거 중..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# 트리거: 매일 오전 6시
$Trigger = New-ScheduledTaskTrigger -Daily -At "06:00AM"

# 액션: 배치 파일 실행
$Action = New-ScheduledTaskAction -Execute $ScriptPath -WorkingDirectory $WorkingDir

# 설정
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -WakeToRun

# 작업 등록 (현재 사용자로)
Register-ScheduledTask `
    -TaskName $TaskName `
    -Description $Description `
    -Trigger $Trigger `
    -Action $Action `
    -Settings $Settings `
    -RunLevel Highest

Write-Host ""
Write-Host "✅ '$TaskName' 작업이 성공적으로 등록되었습니다!" -ForegroundColor Green
Write-Host "   실행 시간: 매일 오전 6:00" -ForegroundColor Cyan
Write-Host "   스크립트: $ScriptPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "확인하려면: Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
Write-Host "즉시 실행: Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
Write-Host "제거하려면: Unregister-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray
