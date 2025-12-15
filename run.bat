@echo off
title Inner Piece Launcher
echo.
echo ====================================================
echo        Inner Piece : 마음 챙김 도구 실행 중...
echo ====================================================
echo.
echo 필수 구성 요소 확인 및 설치 중... (처음 실행 시 시간이 걸릴 수 있습니다)
pip install -r requirements.txt
echo.
echo 구성 요소 준비 완료!
echo.
echo 잠시 후 브라우저가 자동으로 열립니다.
echo 프로그램을 종료하려면 이 창을 닫거나 Ctrl+C를 누르세요.
echo.

:: 브라우저 열기 (서버가 켜질 시간을 잠시 주기 위해 타임아웃을 쓸 수도 있지만, 보통 먼저 열어도 연결됨)
timeout /t 2 /nobreak >nul
start http://127.0.0.1:5000

:: 파이썬 서버 실행
python app.py

pause
