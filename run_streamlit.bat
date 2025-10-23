@echo off
chcp 65001
cd /d "%~dp0"
echo ===============================================
echo    🔍 네이버 마케팅 도구 - 실행 중...
echo ===============================================
echo.
echo 🔐 로그인 정보:
echo    - 아이디: hyune
echo    - 비밀번호: 123456789qwer
echo.
echo 🌐 브라우저에서 http://localhost:8501 접속
echo.
echo ===============================================
streamlit run main_app.py
pause

