import streamlit as st
import requests
import json
import random

# --- 페이지 설정 ---
st.set_page_config(page_title="AI 카피라이터", page_icon="✍️", layout="wide")

# --- Gemini API 설정 ---
API_KEY = "AIzaSyDz-bwrNEpTUmRDzZohuTj4DbwhO9yX_Z0"

# --- UI 디자인 테마 ---
THEMES = [
    {
        "bg_color": "#F0F2F6", "container_bg": "#FFFFFF", "title_color": "#1E3A8A",
        "subtitle_color": "#3B82F6", "text_color": "#1F2937", "font_family": "Georgia, serif",
    },
    {
        "bg_color": "#FDFBFB", "container_bg": "#F7F0EA", "title_color": "#4A2E2A",
        "subtitle_color": "#A0522D", "text_color": "#3D405B", "font_family": "Helvetica, sans-serif",
    },
]

def generate_html_content(text_content, theme):
    """HTML 콘텐츠 생성"""
    html = f"""
    <div style="font-family: {theme['font_family']}; color: {theme['text_color']}; background-color: {theme['container_bg']}; padding: 30px; border-radius: 10px; border-left: 5px solid {theme['subtitle_color']};">
        <h1 style="color: {theme['title_color']}; border-bottom: 2px solid {theme['title_color']}; padding-bottom: 10px;">재작성된 콘텐츠</h1>
        {text_content}
    </div>
    """
    html = html.replace('<p>', f'<p style="line-height: 1.8; font-size: 1.1em; margin-bottom: 1em;">')
    return f'<body style="background-color: {theme["bg_color"]};">{html}</body>'

# --- 함수 정의 ---

def get_available_models():
    """사용 가능한 Gemini 모델 목록을 가져옵니다."""
    try:
        conn = requests.get(f"https://generativelanguage.googleapis.com/v1/models?key={API_KEY}")
        conn.raise_for_status() # HTTP 오류 발생 시 예외 발생
        models_data = conn.json()
        # 'generateContent'를 지원하는 모델만 필터링
        return [m['name'] for m in models_data.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
    except requests.exceptions.HTTPError as http_err:
        st.error(f"모델 목록 조회 실패 (HTTP Status: {http_err.response.status_code}): {http_err.response.text}")
        return []
    except requests.exceptions.RequestException as req_err:
        st.error(f"모델 목록 조회 중 네트워크 또는 요청 오류 발생: {req_err}")
        return []
    except Exception as e:
        st.error(f"모델 목록 조회 중 오류 발생: {e}")
        return []

def rewrite_text_with_gemini(original_text, mode, model_name):
    """Gemini API 직접 호출 (requests 라이브러리 사용으로 변경)"""
    
    # 프롬프트 구성
    if mode == "일반 글 모드":
        prompt = f"""
        당신은 최고의 카피라이터입니다. 아래의 원본 글을 다음 지침에 따라 전문적이고 사람이 작성한 것처럼 자연스러운 형태로 재작성해주세요.
        **지침:**
        1. **분량:** 공백과 이모지를 제외하고 최소 2500자 이상으로 작성해주세요.
        2. **독창성:** 원본 글의 핵심 의미는 유지하되, 문장 구조, 어휘, 표현을 완전히 새롭게 구성하여 유사 문서 문제를 완벽히 회피해야 합니다.
        **[원본 글]**
        {original_text}
        **[재작성된 글]**
        """
    else:  # HTML 코드 모드
        prompt = f"""
        당신은 최고의 카피라이터이자 숙련된 웹 퍼블리셔입니다. 아래의 원본 글을 다음 지침에 따라 HTML 코드로 재작성해주세요.
        **지침:**
        1. **콘텐츠 분량:** 재작성된 글의 텍스트 내용은 공백과 이모지를 제외하고 최소 2500자 이상이어야 합니다.
        2. **독창성:** 원본 글의 핵심 의미는 유지하되, 문장 구조, 어휘, 표현을 완전히 새롭게 구성하여 유사 문서 문제를 완벽히 회피해야 합니다.
        3. **HTML 구조:** `<body>` 태그 안에 들어갈 내용만 작성해주세요.
        4. **CSS 스타일:** 모든 스타일은 반드시 인라인 CSS(예: `<p style="...">`)로 작성해야 합니다.
        **[원본 글]**
        {original_text}
        **[재작성된 HTML 코드 (`<body>` 내부)]**
        """
    
    url = f"https://generativelanguage.googleapis.com/v1/{model_name}:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        with st.spinner(f"`{model_name}` 모델을 사용하여 글을 재작성합니다..."):
            # POST 요청 (120초 타임아웃)
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            # HTTP 오류 발생 시 예외 처리
            response.raise_for_status()

        response_json = response.json()
        return response_json['candidates'][0]['content']['parts'][0]['text']

    except requests.exceptions.HTTPError as http_err:
        st.error(f"API 호출 실패 (HTTP Status: {http_err.response.status_code})")
        try:
            # 오류 응답이 JSON 형식일 경우 예쁘게 출력
            st.json(http_err.response.json())
        except json.JSONDecodeError:
            # JSON이 아닐 경우 텍스트로 출력
            st.code(http_err.response.text)
        return None
    except requests.exceptions.RequestException as req_err:
        st.error(f"네트워크 또는 요청 오류가 발생했습니다: {req_err}")
        return None
    except Exception as e:
        st.error(f"처리 중 심각한 오류가 발생했습니다: {e}")
        # 오류 발생 시 응답 내용이 있다면 출력
        if 'response' in locals() and response.text:
            st.code(response.text)
        return None

# --- UI 구성 ---

st.markdown('<h1 style="text-align: center; color: #4A90E2;">✍️ AI 카피라이터</h1>', unsafe_allow_html=True)
st.markdown("---")

available_models = get_available_models()

if not available_models:
    st.error("사용 가능한 모델을 찾을 수 없습니다. API 키를 확인해주세요.")
else:
    # --- 입력 섹션 ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. 원본 글 입력")
        original_text = st.text_area("재작성할 글을 여기에 붙여넣어 주세요.", height=400)

    with col2:
        st.subheader("2. 재작성 옵션 선택")
        selected_model = st.selectbox("사용할 AI 모델 선택", available_models)
        mode = st.radio("결과물 형태 선택", ("일반 글 모드", "HTML 코드 모드"))

    if st.button("🚀 지금 글 재작성하기", type="primary", use_container_width=True):
        if original_text:
            rewritten_content = rewrite_text_with_gemini(original_text, mode, selected_model)
            if rewritten_content:
                st.session_state.rewritten_content = rewritten_content
                st.session_state.mode = mode
        else:
            st.warning("⚠️ 재작성할 원본 글을 입력해주세요.")

# --- 결과 출력 ---
if 'rewritten_content' in st.session_state:
    st.markdown("---")
    st.subheader("✨ 재작성 결과")

    content = st.session_state.rewritten_content
    output_mode = st.session_state.mode
    
    if output_mode == "일반 글 모드":
        st.text_area("결과물", content, height=500)
    else: # HTML 코드 모드
        theme = random.choice(THEMES)
        final_html = generate_html_content(content, theme)
        
        st.markdown("#### 미리보기")
        st.markdown(final_html, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("#### HTML 코드")
        st.code(final_html, language="html")
