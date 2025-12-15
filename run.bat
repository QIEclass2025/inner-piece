@echo off
title Inner Piece Launcher
echo.
echo ====================================================
echo        Inner Piece : 마음 챙김 도구 실행 중...
echo ====================================================
echo.
echo 필수 구성 요소 확인 및 실행 중... (uv)
echo 처음 실행 시 환경 설정에 시간이 걸릴 수 있습니다.
echo.

:: 브라우저 열기
timeout /t 2 /nobreak >nul
start http://127.0.0.1:5000

:: UV를 사용하여 앱 실행
uv run app.py

pause
