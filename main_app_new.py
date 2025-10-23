"""
네이버 마케팅 도구 - 통합 애플리케이션
로그인부터 마케팅 도구까지 모든 기능을 포함한 단일 앱
"""

import streamlit as st
import hashlib
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 사용자 정보 (실제 앱에서는 DB 또는 안전한 곳에서 관리)
VALID_USERNAME = "hyune"
VALID_PASSWORD_HASH = hashlib.sha256("123456789qwer".encode('utf-8')).hexdigest()

def verify_login(username, password):
    """사용자 아이디와 비밀번호 확인"""
    if username == VALID_USERNAME and hashlib.sha256(password.encode('utf-8')).hexdigest() == VALID_PASSWORD_HASH:
        return True
    return False

def show_login_page():
    """로그인 페이지 표시"""
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # 로고 및 제목
    st.markdown('<div class="logo">🔍</div>', unsafe_allow_html=True)
    st.markdown('<div class="title">네이버 마케팅 도구</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">로그인이 필요합니다</div>', unsafe_allow_html=True)
    
    # 로그인 폼
    with st.form("login_form"):
        username = st.text_input(
            "아이디",
            placeholder="아이디를 입력하세요",
            help="사용자 아이디를 입력해주세요"
        )
        
        password = st.text_input(
            "비밀번호",
            type="password",
            placeholder="비밀번호를 입력하세요",
            help="비밀번호를 입력해주세요"
        )
        
        submitted = st.form_submit_button("🔐 로그인", use_container_width=True)
        
        if submitted:
            if not username or not password:
                st.markdown('<div class="error-message">⚠️ 아이디와 비밀번호를 모두 입력해주세요.</div>', unsafe_allow_html=True)
            else:
                if verify_login(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.markdown('<div class="success-message">✅ 로그인 성공! 마케팅 도구로 이동합니다...</div>', unsafe_allow_html=True)
                    st.rerun()
                else:
                    st.markdown('<div class="error-message">❌ 아이디 또는 비밀번호가 올바르지 않습니다.</div>', unsafe_allow_html=True)
    
    # 도움말
    st.markdown("""
    <div style="margin-top: 2rem; padding: 1rem; background-color: #f8f9fa; border-radius: 8px; font-size: 0.9rem; color: #666;">
        <strong>💡 로그인 정보:</strong><br>
        • 아이디: hyune<br>
        • 비밀번호: 123456789qwer
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_marketing_tool():
    """마케팅 도구 메인 페이지"""
    # 헤더
    st.markdown('<h1 class="main-title">🔍 네이버 마케팅 도구</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">by 99monster</p>', unsafe_allow_html=True)
    
    # 사용자 정보 표시
    col1, col2, col3 = st.columns([3, 1, 1])
    with col2:
        st.info(f"👤 {st.session_state.username}님")
    with col3:
        if st.button("🚪 로그아웃"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()
    
    st.markdown("---")
    
    # 메인 대시보드
    st.markdown("## 🏠 메인 대시보드")
    st.markdown("네이버 마케팅 도구에 오신 것을 환영합니다! 아래 메뉴에서 원하는 기능을 선택하세요.")
    
    # 기능별 카드 메뉴
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 15px; color: white; text-align: center; margin: 1rem 0;">
            <h3>🎯 순위 확인</h3>
            <p>특정 키워드와 판매처명으로<br>네이버 쇼핑 순위 조회</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="padding: 2rem; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    border-radius: 15px; color: white; text-align: center; margin: 1rem 0;">
            <h3>🛍️ 쇼핑 순위</h3>
            <p>카테고리별 상위 상품<br>순위 조회</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="padding: 2rem; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    border-radius: 15px; color: white; text-align: center; margin: 1rem 0;">
            <h3>📊 키워드 분석</h3>
            <p>연관 키워드 분석 및<br>검색량 데이터</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 사용 가이드
    st.markdown("## 📖 사용 가이드")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🚀 빠른 시작
        1. **순위 확인**: 특정 키워드로 내 상품 순위 확인
        2. **쇼핑 순위**: 카테고리별 인기 상품 파악
        3. **키워드 분석**: 경쟁사 분석 및 트렌드 파악
        """)
    
    with col2:
        st.markdown("""
        ### 💡 활용 팁
        - **정기적 모니터링**: 주기적으로 순위 변화 확인
        - **경쟁사 분석**: 상위 판매처들의 전략 분석
        - **키워드 최적화**: 검색량 높은 키워드 활용
        """)
    
    # 최근 활동 (예시)
    st.markdown("## 📈 최근 활동")
    st.info("💡 각 기능 페이지에서 상세한 분석을 진행하세요!")

def main():
    """메인 애플리케이션 (로그인 및 마케팅 도구 통합)"""
    
    # 세션 상태 초기화
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None

    if not st.session_state.authenticated:
        # 로그인 페이지
        st.set_page_config(
            page_title="로그인 - 네이버 마케팅 도구",
            page_icon="🔐",
            layout="centered",
            initial_sidebar_state="collapsed"
        )

        st.markdown("""
        <style>
            .main-container {
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                background: linear-gradient(135deg, #e0f7fa 0%, #e8f5e9 100%);
            }
            .logo {
                font-size: 2.5rem;
                color: #03C75A;
                margin-bottom: 0.5rem;
            }
            .title {
                color: #333;
                font-size: 1.5rem;
                font-weight: bold;
                margin-bottom: 2rem;
            }
            .subtitle {
                color: #666;
                font-size: 1rem;
                margin-bottom: 2rem;
            }
            .stTextInput > div > div > input {
                border-radius: 8px;
                border: 2px solid #e0e0e0;
                padding: 12px;
                font-size: 1rem;
            }
            .stTextInput > div > div > input:focus {
                border-color: #03C75A;
                box-shadow: 0 0 0 3px rgba(3, 199, 90, 0.1);
            }
            .stButton > button {
                width: 100%;
                background: linear-gradient(135deg, #03C75A 0%, #02b350 100%);
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 8px;
                border: none;
                font-size: 1.1rem;
                margin-top: 1rem;
            }
            .stButton > button:hover {
                background: linear-gradient(135deg, #02b350 0%, #019d47 100%);
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(3, 199, 90, 0.3);
            }
            .error-message {
                background-color: #ffebee;
                color: #c62828;
                padding: 1rem;
                border-radius: 8px;
                margin: 1rem 0;
                border-left: 4px solid #c62828;
            }
            .success-message {
                background-color: #e8f5e9;
                color: #2e7d32;
                padding: 1rem;
                border-radius: 8px;
                margin: 1rem 0;
                border-left: 4px solid #2e7d32;
            }
            .main-title {
                text-align: center;
                color: #03C75A;
                font-size: 2.5rem;
                font-weight: bold;
                margin-bottom: 0.5rem;
            }
            .sub-title {
                text-align: center;
                color: #666;
                font-size: 1rem;
                margin-bottom: 2rem;
            }
        </style>
        """, unsafe_allow_html=True)

        show_login_page()
    else:
        # 마케팅 도구 페이지
        st.set_page_config(
            page_title="네이버 마케팅 도구",
            page_icon="🔍",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        st.markdown("""
        <style>
            .main-title {
                text-align: center;
                color: #03C75A;
                font-size: 2.5rem;
                font-weight: bold;
                margin-bottom: 0.5rem;
            }
            .sub-title {
                text-align: center;
                color: #666;
                font-size: 1rem;
                margin-bottom: 2rem;
            }
        </style>
        """, unsafe_allow_html=True)

        show_marketing_tool()

if __name__ == "__main__":
    main()
