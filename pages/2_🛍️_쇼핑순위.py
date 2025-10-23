"""
쇼핑 순위 페이지
카테고리별 상위 상품 순위를 조회하는 기능
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

def shopping_rank_tab():
    """쇼핑 순위 탭"""
    st.markdown("### 🛍️ 쇼핑 순위")
    st.markdown("키워드 검색으로 1위부터 100위까지 상품 순위를 조회합니다.")
    
    # 키워드 입력
    keyword = st.text_input(
        "🔍 검색 키워드",
        placeholder="예: 무선마우스, 스마트폰, 노트북",
        help="순위를 확인하고 싶은 키워드를 입력하세요"
    )
    
    # 검색 옵션
    col1, col2 = st.columns(2)
    
    with col1:
        sort_option = st.selectbox(
            "📊 정렬 기준",
            ["정확도순", "가격낮은순", "가격높은순", "판매량순", "평점순"],
            help="검색 결과 정렬 기준을 선택하세요"
        )
    
    with col2:
        display_count = st.slider(
            "📋 표시할 상품 수",
            min_value=10,
            max_value=100,
            value=50,
            step=10,
            help="표시할 상품 수를 선택하세요 (최대 100개)"
        )
    
    # 검색 버튼
    if st.button("🔍 순위 조회", type="primary", use_container_width=True):
        if not keyword:
            st.warning("⚠️ 검색할 키워드를 입력해주세요.")
        else:
            search_shopping_rank(keyword, sort_option, display_count)

def search_shopping_rank(keyword, sort_option, display_count):
    """쇼핑 순위 검색 실행"""
    
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
        with st.spinner("🔍 순위를 조회하는 중..."):
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
                display_shopping_results(result['items'], keyword, sort_option)
            else:
                st.warning("⚠️ 검색 결과가 없습니다.")
                
    except Exception as e:
        st.error(f"❌ 검색 중 오류 발생: {str(e)}")

def display_shopping_results(items, keyword, sort_option):
    """쇼핑 순위 결과 표시"""
    
    st.success(f"🎉 **{keyword}** 키워드 순위 조회 완료!")
    
    # 통계 정보
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 총 상품 수", len(items))
    
    with col2:
        prices = [int(item.get('lprice', 0)) for item in items if item.get('lprice', '').isdigit()]
        if prices:
            avg_price = sum(prices) / len(prices)
            st.metric("💰 평균 가격", f"{avg_price:,.0f}원")
        else:
            st.metric("💰 평균 가격", "N/A")
    
    with col3:
        unique_malls = len(set([item.get('mallName', '') for item in items]))
        st.metric("🏪 판매처 수", unique_malls)
    
    with col4:
        st.metric("📈 정렬 기준", sort_option)
    
    st.markdown("---")
    
    # 순위별 상품 표시
    st.markdown(f"### 🏆 {keyword} 순위 ({sort_option})")
    
    # 페이지네이션을 위한 설정
    items_per_page = 20
    total_pages = (len(items) + items_per_page - 1) // items_per_page
    
    if total_pages > 1:
        page = st.selectbox("📄 페이지 선택", range(1, total_pages + 1), format_func=lambda x: f"페이지 {x}")
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, len(items))
        page_items = items[start_idx:end_idx]
    else:
        page_items = items
    
    # 상품 목록 표시
    for i, item in enumerate(page_items, start_idx + 1):
        with st.container():
            col1, col2, col3 = st.columns([1, 4, 1])
            
            with col1:
                # 순위 표시
                if i <= 3:
                    rank_icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                    st.markdown(f"### {rank_icon} {i}위")
                else:
                    st.markdown(f"### {i}위")
            
            with col2:
                item_title = item.get('title', '').replace('<b>', '').replace('</b>', '')
                item_mall = item.get('mallName', '')
                item_price = item.get('lprice', 'N/A')
                item_brand = item.get('brand', '')
                
                st.markdown(f"**{item_title}**")
                st.markdown(f"🏪 {item_mall}")
                if item_brand:
                    st.markdown(f"🏷️ {item_brand}")
                st.markdown(f"💰 {item_price}원")
            
            with col3:
                if item.get('image'):
                    st.image(item['image'], width=100)
                else:
                    st.markdown("📷 이미지 없음")
            
            st.markdown("---")
    
    # 페이지 정보
    if total_pages > 1:
        st.info(f"📄 현재 페이지: {page}/{total_pages} (총 {len(items)}개 상품)")

# 메인 실행
if __name__ == "__main__":
    shopping_rank_tab()
