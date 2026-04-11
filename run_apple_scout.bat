@echo off
REM ============================================
REM AppleScout Agent - Daily Runner
REM Windows Task Scheduler에서 매일 06:00에 실행
REM ============================================

cd /d "c:\appdev\apple-scout"

REM 로그 디렉토리 생성
if not exist "logs" mkdir logs

REM 날짜 기반 로그 파일명
for /f "tokens=1-3 delims=/" %%a in ("%date%") do set TODAY=%%c-%%a-%%b
set LOGFILE=logs\applescout_%TODAY%.log

echo ============================================ >> "%LOGFILE%"
echo AppleScout Agent Started: %date% %time% >> "%LOGFILE%"
echo ============================================ >> "%LOGFILE%"

REM Python 실행 (시스템 Python 사용)
python execution\main.py >> "%LOGFILE%" 2>&1

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Workflow completed at %time% >> "%LOGFILE%"
) else (
    echo [FAILED] Workflow failed with code %ERRORLEVEL% at %time% >> "%LOGFILE%"
)

REM 30일 이상 된 로그 삭제
forfiles /p "logs" /m "applescout_*.log" /d -30 /c "cmd /c del @path" 2>nul

echo ============================================ >> "%LOGFILE%"
echo Finished: %date% %time% >> "%LOGFILE%"
echo ============================================ >> "%LOGFILE%"
