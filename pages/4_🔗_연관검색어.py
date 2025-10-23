"""
연관검색어 페이지
키워드 입력 시 연관 검색어 목록을 추출하는 기능
"""

import streamlit as st
import json
import urllib.request
import urllib.parse
import os
import time
import requests
import hmac
import hashlib
import base64
import pandas as pd
from dotenv import load_dotenv
from collections import Counter
import re

# 환경 변수 로드
load_dotenv()

# 네이버 광고 API 설정
API_KEY = os.getenv("NAVER_API_KEY", "010000000040aefa21fbb0a3769e556d20040963da514e6b3e7ea7589fe278cb2e857ce16e")
SECRET_KEY = os.getenv("NAVER_SECRET_KEY", "AQAAAABArvoh+7Cjdp5VbSAECWPayKfamwuyOYal6veBVythVA==")
CUSTOMER_ID = os.getenv("NAVER_CUSTOMER_ID", "3900043")

# 네이버 쇼핑 API 설정 (대안용)
CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "your_client_id_here")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "your_client_secret_here")

BASE_URL = 'https://api.searchad.naver.com'

def generate_signature(timestamp, method, uri, secret_key):
    """네이버 광고 API 서명 생성 (네이버 공식 문서 샘플 코드 기준)"""
    message = f"{timestamp}.{method}.{uri}"
    hash_obj = hmac.new(
        secret_key.encode('utf-8'), 
        message.encode('utf-8'), 
        hashlib.sha256
    )
    return base64.b64encode(hash_obj.digest()).decode()

def get_header(method, uri, api_key, secret_key, customer_id):
    """네이버 광고 API 헤더 생성 (네이버 공식 문서 기준)"""
    timestamp = str(round(time.time() * 1000))
    signature = generate_signature(timestamp, method, uri, secret_key)
    
    if signature is None:
        return None
    
    return {
        'Content-Type': 'application/json; charset=UTF-8',
        'X-Timestamp': timestamp,
        'X-API-KEY': api_key,
        'X-Customer': str(customer_id),
        'X-Signature': signature
    }

def safe_int_conversion(value):
    """값을 정수로 안전하게 변환하고, 변환 실패 시 0을 반환합니다."""
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

def get_related_keywords_from_ad_api(keyword):
    """네이버 광고 API를 사용하여 연관검색어 추출 (네이버 공식 문서 기준)"""
    try:
        # 키워드 도구 API 호출 (올바른 엔드포인트)
        uri = '/keywordstool'
        method = 'GET'
        
        headers = get_header(method, uri, API_KEY, SECRET_KEY, CUSTOMER_ID)
        
        if headers is None:
            st.error("❌ API 헤더 생성 실패")
            return None
        
        # 키워드 추천 요청 (네이버 공식 문서 기준)
        params = {
            'hintKeywords': keyword,
            'showDetail': '1'
        }
        
        # URL에 파라미터 추가
        query_string = urllib.parse.urlencode(params)
        full_url = f"{BASE_URL}{uri}?{query_string}"
        
        response = requests.get(
            full_url,
            headers=headers
        )
        
        st.info(f"🔍 API 호출 상태: {response.status_code}")
        st.info(f"🔍 요청 URL: {full_url}")
        st.info(f"🔍 요청 헤더: {headers}")
        st.info(f"🔍 응답 내용: {response.text[:500]}...")
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            st.warning("⚠️ 네이버 광고 API 서명 오류입니다.")
            st.info("API 키와 시크릿 키를 확인해주세요.")
            return None
        else:
            st.warning(f"⚠️ API 호출 실패: {response.status_code}")
            st.warning(f"응답: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"❌ API 호출 중 오류: {str(e)}")
        return None

def process_ad_api_response(response_data):
    """네이버 광고 API 응답을 처리하여 데이터프레임으로 변환합니다."""
    keyword_list = response_data.get('keywordList', [])
    if not keyword_list:
        return pd.DataFrame()

    processed_data = []
    for item in keyword_list:
        pc_qc_cnt = safe_int_conversion(item.get('monthlyPcQcCnt', 0))
        mobile_qc_cnt = safe_int_conversion(item.get('monthlyMobileQcCnt', 0))
        pc_click_cnt = safe_int_conversion(item.get('monthlyPcClickCnt', 0))
        mobile_click_cnt = safe_int_conversion(item.get('monthlyMobileClickCnt', 0))

        total_search = pc_qc_cnt + mobile_qc_cnt
        total_clicks = pc_click_cnt + mobile_click_cnt
        
        pc_ctr = (pc_click_cnt / pc_qc_cnt * 100) if pc_qc_cnt > 0 else 0
        mobile_ctr = (mobile_click_cnt / mobile_qc_cnt * 100) if mobile_qc_cnt > 0 else 0

        processed_data.append({
            '연관키워드': item.get('relKeyword', 'N/A'),
            '월간검색수(PC)': pc_qc_cnt,
            '월간검색수(모바일)': mobile_qc_cnt,
            '월간 총 검색수': total_search,
            '월평균클릭수(PC)': pc_click_cnt,
            '월평균클릭수(모바일)': mobile_click_cnt,
            '월평균 총 클릭수': total_clicks,
            '월평균클릭률(PC)': f"{pc_ctr:.2f}%",
            '월평균클릭률(모바일)': f"{mobile_ctr:.2f}%",
            '경쟁정도': item.get('compIdx', 'N/A'),
            '월평균노출광고수': item.get('plAvgDepth', 'N/A')
        })
    
    df = pd.DataFrame(processed_data)
    df = df.sort_values(by='월간 총 검색수', ascending=False).reset_index(drop=True)
    return df

def display_ad_api_results(df, keyword):
    """네이버 광고 API 결과 표시"""
    if df.empty:
        st.warning("⚠️ 분석할 연관검색어 데이터가 없습니다.")
        return

    st.success(f"🎉 **{keyword}** 연관검색어 분석 완료! (총 {len(df)}개)")
    
    # 통계 정보
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 총 연관검색어", f"{len(df):,}개")
    with col2:
        avg_search = df['월간 총 검색수'].mean()
        st.metric("📈 평균 월간 검색량", f"{avg_search:,.0f}")
    with col3:
        avg_clicks = df['월평균 총 클릭수'].mean()
        st.metric("🖱️ 평균 월간 클릭수", f"{avg_clicks:,.0f}")
    with col4:
        # '경쟁정도'가 문자열일 수 있으므로 숫자만 필터링
        numeric_comp = pd.to_numeric(df['경쟁정도'], errors='coerce').dropna()
        avg_comp = numeric_comp.mean() if not numeric_comp.empty else 0
        st.metric("🏆 평균 경쟁정도", f"{avg_comp:.1f}")

    st.markdown("---")
    st.markdown(f"### 📊 '{keyword}' 연관검색어 상세 데이터")
    st.dataframe(df, use_container_width=True)

    # 시각화
    st.markdown("---")
    col1, col2 = st.columns(2)
    chart_data = df.head(15)
    with col1:
        st.markdown("#### 📈 월간 총 검색수 (상위 15개)")
        st.bar_chart(chart_data.set_index('연관키워드')['월간 총 검색수'])
    with col2:
        st.markdown("#### 🏆 경쟁 정도 (상위 15개)")
        st.bar_chart(chart_data.set_index('연관키워드')['경쟁정도'])

def analyze_related_keywords(keyword):
    """연관검색어 분석 실행"""
    try:
        with st.spinner("🔍 네이버 광고 API에서 연관검색어를 조회하는 중..."):
            result = get_related_keywords_from_ad_api(keyword)
            
            if result:
                df = process_ad_api_response(result)
                display_ad_api_results(df, keyword)
            else:
                st.error("❌ 네이버 광고 API에서 데이터를 가져오지 못했습니다.")
                st.info("API 키, 권한 또는 네트워크 상태를 확인해주세요.")
                
    except Exception as e:
        st.error(f"❌ 분석 중 오류 발생: {str(e)}")

def related_keywords_tab():
    """연관검색어 탭 UI 구성"""
    st.markdown("### 🔗 연관검색어 분석 (네이버 광고 API)")
    st.markdown("키워드 입력 시 관련된 검색어들의 상세 데이터를 분석하여 제공합니다.")

    with st.expander("🔑 API 키 로드 상태 확인"):
        st.info(f"CUSTOMER_ID: `{CUSTOMER_ID}`")
        st.info(f"API_KEY: `{API_KEY[:10]}...`")
        if CUSTOMER_ID == "3900043":
             st.success("✅ API 키가 코드에 설정되었습니다.")
        else:
            st.warning("⚠️ `.env` 파일에 올바른 키를 입력했는지 확인해주세요.")

    keyword = st.text_input(
        "🔍 분석할 키워드",
        placeholder="예: 손목보호대, 캠핑의자",
        help="연관검색어를 분석하고 싶은 키워드를 입력하세요."
    )
    
    if st.button("🔍 연관검색어 분석 실행", type="primary", use_container_width=True):
        if not keyword:
            st.warning("⚠️ 분석할 키워드를 입력해주세요.")
        else:
            analyze_related_keywords(keyword)

# 메인 실행
if __name__ == "__main__":
    related_keywords_tab()
