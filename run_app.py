import os
import sys
import subprocess

# 현재 스크립트의 디렉토리로 이동
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print("=" * 50)
print("   🔍 네이버 마케팅 도구 - 실행 중...")
print("=" * 50)
print()
print("🔐 로그인 정보:")
print("   - 아이디: hyune")
print("   - 비밀번호: 123456789qwer")
print()
print("🌐 브라우저에서 http://localhost:8501 접속")
print("=" * 50)
print()

# Streamlit 실행 (통합 앱)
subprocess.run([sys.executable, "-m", "streamlit", "run", "main_app.py"])

