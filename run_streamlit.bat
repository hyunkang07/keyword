@echo off
chcp 65001
cd /d "%~dp0"
streamlit run app.py
pause

