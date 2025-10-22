import os
import sys
import subprocess

# 현재 스크립트의 디렉토리로 이동
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print(f"현재 디렉토리: {os.getcwd()}")
print(f"app.py 존재 여부: {os.path.exists('app.py')}")

# Streamlit 실행
subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

