"""
순위 확인 페이지
특정 키워드와 판매처명으로 네이버 쇼핑 순위를 조회하는 기능
"""

import streamlit as st
import json
import urllib.request
import urllib.parse
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 네이버 쇼핑 검색 API 설정
CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "your_client_id_here")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "your_client_secret_here")

def rank_checker_tab():
    """순위 확인 탭"""
    st.markdown("### 🎯 순위 확인")
    st.markdown("특정 키워드와 판매처명으로 네이버 쇼핑 순위를 조회합니다.")
    
    # 입력 폼
    col1, col2 = st.columns(2)
    
    with col1:
        keyword = st.text_input(
            "🔍 검색 키워드",
            placeholder="예: 무선마우스",
            help="순위를 확인하고 싶은 키워드를 입력하세요"
        )
    
    with col2:
        shop_name = st.text_input(
            "🏪 판매처명",
            placeholder="예: 쿠팡",
            help="순위를 확인하고 싶은 판매처명을 입력하세요"
        )
    
    # 검색 옵션
    col3, col4 = st.columns(2)
    
    with col3:
        sort_option = st.selectbox(
            "📊 정렬 기준",
            ["정확도순", "가격낮은순", "가격높은순", "판매량순", "평점순"],
            help="검색 결과 정렬 기준을 선택하세요"
        )
    
    with col4:
        display_count = st.slider(
            "📋 검색 결과 수",
            min_value=10,
            max_value=100,
            value=30,
            step=10,
            help="검색할 상품 수를 선택하세요"
        )
    
    # 검색 버튼
    if st.button("🔍 순위 검색", type="primary", use_container_width=True):
        if not keyword or not shop_name:
            st.warning("⚠️ 키워드와 판매처명을 모두 입력해주세요.")
        else:
            search_rank(keyword, shop_name, sort_option, display_count)

def search_rank(keyword, shop_name, sort_option, display_count):
    """순위 검색 실행"""
    
    # 정렬 옵션 매핑
    sort_mapping = {
        "정확도순": "sim",
        "가격낮은순": "asc",
        "가격높은순": "dsc", 
        "판매량순": "count",
        "평점순": "review"
    }
    
    sort_param = sort_mapping.get(sort_option, "sim")
    
    try:
        with st.spinner("🔍 순위를 검색하는 중..."):
            # 네이버 쇼핑 API 호출
            url = "https://openapi.naver.com/v1/search/shop.json"
            params = {
                "query": keyword,
                "display": min(display_count, 100),
                "sort": sort_param
            }
            
            # URL 인코딩
            query_string = urllib.parse.urlencode(params)
            full_url = f"{url}?{query_string}"
            
            # 요청 헤더
            request = urllib.request.Request(full_url)
            request.add_header("X-Naver-Client-Id", CLIENT_ID)
            request.add_header("X-Naver-Client-Secret", CLIENT_SECRET)
            
            # API 호출
            response = urllib.request.urlopen(request)
            response_data = response.read()
            result = json.loads(response_data.decode('utf-8'))
            
            if result.get('items'):
                display_results(result['items'], shop_name, keyword)
            else:
                st.warning("⚠️ 검색 결과가 없습니다.")
                
    except Exception as e:
        st.error(f"❌ 검색 중 오류 발생: {str(e)}")

def display_results(items, shop_name, keyword):
    """검색 결과 표시"""
    
    found_rank = None
    total_results = len(items)
    
    # 판매처명 매칭 (부분 일치)
    for i, item in enumerate(items, 1):
        item_title = item.get('title', '').replace('<b>', '').replace('</b>', '')
        item_mall = item.get('mallName', '')
        
        # 판매처명이 제목이나 몰명에 포함되어 있는지 확인
        if shop_name.lower() in item_mall.lower() or shop_name.lower() in item_title.lower():
            found_rank = i
            break
    
    # 결과 표시
    if found_rank:
        st.success(f"🎉 **{shop_name}**의 **{keyword}** 순위: **{found_rank}위**")
        
        # 해당 상품 정보 표시
        target_item = items[found_rank - 1]
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**상품명:** {target_item.get('title', '').replace('<b>', '').replace('</b>', '')}")
            st.markdown(f"**판매처:** {target_item.get('mallName', '')}")
            st.markdown(f"**가격:** {target_item.get('lprice', 'N/A')}원")
        
        with col2:
            if target_item.get('image'):
                st.image(target_item['image'], width=150)
        
        # 상위 10개 결과 표시
        st.markdown("### 📊 상위 10개 검색 결과")
        for i, item in enumerate(items[:10], 1):
            item_title = item.get('title', '').replace('<b>', '').replace('</b>', '')
            item_mall = item.get('mallName', '')
            item_price = item.get('lprice', 'N/A')
            
            # 현재 순위 강조
            if i == found_rank:
                st.markdown(f"**{i}위** 🎯 **{item_mall}** - {item_title} ({item_price}원)")
            else:
                st.markdown(f"{i}위 - {item_mall} - {item_title} ({item_price}원)")
    else:
        st.warning(f"⚠️ **{shop_name}**의 **{keyword}** 검색 결과에서 해당 판매처를 찾을 수 없습니다.")
        st.info(f"총 {total_results}개 상품 중에서 검색했습니다.")
        
        # 상위 10개 결과 표시
        st.markdown("### 📊 상위 10개 검색 결과")
        for i, item in enumerate(items[:10], 1):
            item_title = item.get('title', '').replace('<b>', '').replace('</b>', '')
            item_mall = item.get('mallName', '')
            item_price = item.get('lprice', 'N/A')
            st.markdown(f"{i}위 - {item_mall} - {item_title} ({item_price}원)")

# 메인 실행
if __name__ == "__main__":
    rank_checker_tab()
