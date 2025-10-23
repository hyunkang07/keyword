@echo off
chcp 65001
cd /d "%~dp0"

echo ===============================================
echo    .... packages installing ....
echo ===============================================
pip install -r requirements.txt

echo.
echo ===============================================
echo    ... Naver Marketing Tool Running ...
echo ===============================================
echo.
echo    - ID: hyune
echo    - PW: 123456789qwer
echo.
echo    >> http://localhost:8501
echo.
echo ===============================================
streamlit run main_app.py
pause

