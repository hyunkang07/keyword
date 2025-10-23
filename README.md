# 🔍 네이버 마케팅 도구

네이버 쇼핑 및 광고 API를 활용한 마케팅 도구입니다.

## 📁 파일 구조

### 🚀 **실행 파일**
- `main_app.py` - **메인 애플리케이션** (로그인 + 마케팅 도구 통합)
- `run_app.py` - Python 실행 스크립트
- `run_streamlit.bat` - Windows 배치 실행 파일

### 🔧 **핵심 기능**
- `app.py` - 마케팅 도구 핵심 로직 (순위 확인, 쇼핑 순위, 키워드 분석)

### ⚙️ **설정 파일**
- `requirements.txt` - Python 패키지 의존성
- `env_example.txt` - 환경변수 설정 예시 파일
- `.env` - 실제 API 키 설정 (생성 필요)

### 🎨 **리소스**
- `logo.ico` - 메인 로고
- `logo_inner.ico` - 내부 로고

### 📖 **문서**
- `실행방법.txt` - 실행 가이드

## 🔐 로그인 정보
- **아이디**: `hyune`
- **비밀번호**: `123456789qwer`

## 🚀 실행 방법

### 방법 1: 배치 파일 (가장 간단)
```bash
run_streamlit.bat 더블클릭
```

### 방법 2: Python 스크립트
```bash
python run_app.py
```

### 방법 3: 직접 실행
```bash
streamlit run main_app.py
```

## ⚙️ 환경 설정

1. `.env` 파일 생성
2. `env_example.txt` 참고하여 API 키 설정
3. `pip install -r requirements.txt` 실행

## 🎯 주요 기능

1. **순위 확인**: 특정 키워드와 판매처명으로 네이버 쇼핑 순위 조회
2. **쇼핑 순위**: 카테고리별 상위 상품 순위 조회
3. **키워드 분석**: 연관 키워드 분석 및 검색량 데이터

## 📞 문의
99monster (99monster)