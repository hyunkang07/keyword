"""
키워드 분석 페이지
연관 키워드 분석 및 검색량 데이터를 제공하는 기능
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

def keyword_analysis_tab():
    """키워드 분석 탭"""
    st.markdown("### 📊 키워드 분석")
    st.markdown("연관 키워드 분석 및 검색량 데이터를 제공합니다.")
    
    # 분석 옵션
    analysis_type = st.radio(
        "🔍 분석 유형 선택",
        ["연관 키워드 분석", "경쟁 키워드 분석", "트렌드 키워드 분석"],
        help="원하는 키워드 분석 유형을 선택하세요"
    )
    
    # 키워드 입력
    keyword = st.text_input(
        "🔍 분석할 키워드",
        placeholder="예: 무선마우스",
        help="분석하고 싶은 키워드를 입력하세요"
    )
    
    # 분석 옵션
    col1, col2 = st.columns(2)
    
    with col1:
        max_keywords = st.slider(
            "📋 최대 키워드 수",
            min_value=5,
            max_value=30,
            value=15,
            step=5,
            help="분석할 최대 키워드 수를 선택하세요"
        )
    
    with col2:
        min_search_volume = st.slider(
            "📈 최소 검색량",
            min_value=100,
            max_value=10000,
            value=1000,
            step=100,
            help="최소 검색량 기준을 설정하세요"
        )
    
    # 분석 버튼
    if st.button("📊 키워드 분석", type="primary", use_container_width=True):
        if not keyword:
            st.warning("⚠️ 분석할 키워드를 입력해주세요.")
        else:
            analyze_keywords(keyword, analysis_type, max_keywords, min_search_volume)

def analyze_keywords(keyword, analysis_type, max_keywords, min_search_volume):
    """키워드 분석 실행"""
    
    try:
        with st.spinner("📊 키워드를 분석하는 중..."):
            # 네이버 쇼핑 API 호출
            url = "https://openapi.naver.com/v1/search/shop.json"
            params = {
                "query": keyword,
                "display": 100,
                "sort": "sim"
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
                display_keyword_analysis(result['items'], keyword, analysis_type, max_keywords, min_search_volume)
            else:
                st.warning("⚠️ 분석할 데이터가 없습니다.")
                
    except Exception as e:
        st.error(f"❌ 분석 중 오류 발생: {str(e)}")

def display_keyword_analysis(items, keyword, analysis_type, max_keywords, min_search_volume):
    """키워드 분석 결과 표시"""
    
    st.success(f"🎉 **{keyword}** 키워드 분석 완료!")
    
    # 기본 통계
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 총 상품 수", len(items))
    
    with col2:
        unique_brands = len(set([item.get('brand', '') for item in items if item.get('brand')]))
        st.metric("🏷️ 브랜드 수", unique_brands)
    
    with col3:
        unique_malls = len(set([item.get('mallName', '') for item in items]))
        st.metric("🏪 판매처 수", unique_malls)
    
    with col4:
        avg_price = sum([int(item.get('lprice', 0)) for item in items if item.get('lprice', '').isdigit()]) / len(items)
        st.metric("💰 평균 가격", f"{avg_price:,.0f}원")
    
    st.markdown("---")
    
    # 분석 유형별 결과 표시
    if analysis_type == "연관 키워드 분석":
        display_related_keywords(items, keyword, max_keywords)
    elif analysis_type == "경쟁 키워드 분석":
        display_competitor_keywords(items, keyword, max_keywords)
    else:  # 트렌드 키워드 분석
        display_trend_keywords(items, keyword, max_keywords)

def display_related_keywords(items, keyword, max_keywords):
    """연관 키워드 분석 결과"""
    st.markdown("### 🔗 연관 키워드 분석")
    
    # 상품명에서 키워드 추출
    keywords = {}
    for item in items:
        title = item.get('title', '').replace('<b>', '').replace('</b>', '').lower()
        words = title.split()
        
        for word in words:
            if len(word) > 1 and word not in ['의', '를', '을', '에', '에서', '로', '으로']:
                keywords[word] = keywords.get(word, 0) + 1
    
    # 상위 키워드 정렬
    sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:max_keywords]
    
    # 키워드 클라우드 형태로 표시
    st.markdown("#### 📈 키워드 빈도 분석")
    for i, (word, count) in enumerate(sorted_keywords, 1):
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.markdown(f"**{i}위**")
        with col2:
            st.markdown(f"**{word}** (출현 {count}회)")
        with col3:
            st.progress(min(count / max([c for _, c in sorted_keywords]), 1.0))

def display_competitor_keywords(items, keyword, max_keywords):
    """경쟁 키워드 분석 결과"""
    st.markdown("### ⚔️ 경쟁 키워드 분석")
    
    # 브랜드별 분석
    brand_analysis = {}
    for item in items:
        brand = item.get('brand', '')
        if brand:
            if brand not in brand_analysis:
                brand_analysis[brand] = {'count': 0, 'avg_price': 0, 'items': []}
            brand_analysis[brand]['count'] += 1
            brand_analysis[brand]['items'].append(item)
    
    # 브랜드별 평균 가격 계산
    for brand, data in brand_analysis.items():
        prices = [int(item.get('lprice', 0)) for item in data['items'] if item.get('lprice', '').isdigit()]
        if prices:
            data['avg_price'] = sum(prices) / len(prices)
    
    # 브랜드별 경쟁력 분석
    st.markdown("#### 🏆 브랜드별 경쟁력 분석")
    sorted_brands = sorted(brand_analysis.items(), key=lambda x: x[1]['count'], reverse=True)[:max_keywords]
    
    for i, (brand, data) in enumerate(sorted_brands, 1):
        col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
        with col1:
            st.markdown(f"**{i}위**")
        with col2:
            st.markdown(f"**{brand}**")
        with col3:
            st.metric("상품 수", data['count'])
        with col4:
            st.metric("평균가", f"{data['avg_price']:,.0f}원")

def display_trend_keywords(items, keyword, max_keywords):
    """트렌드 키워드 분석 결과"""
    st.markdown("### 📈 트렌드 키워드 분석")
    
    # 가격대별 분석
    price_ranges = {
        "1만원 미만": 0,
        "1-5만원": 0,
        "5-10만원": 0,
        "10-20만원": 0,
        "20만원 이상": 0
    }
    
    for item in items:
        price = int(item.get('lprice', 0)) if item.get('lprice', '').isdigit() else 0
        if price < 10000:
            price_ranges["1만원 미만"] += 1
        elif price < 50000:
            price_ranges["1-5만원"] += 1
        elif price < 100000:
            price_ranges["5-10만원"] += 1
        elif price < 200000:
            price_ranges["10-20만원"] += 1
        else:
            price_ranges["20만원 이상"] += 1
    
    # 가격대별 트렌드 표시
    st.markdown("#### 💰 가격대별 트렌드")
    for range_name, count in price_ranges.items():
        if count > 0:
            col1, col2 = st.columns([2, 3])
            with col1:
                st.markdown(f"**{range_name}**")
            with col2:
                st.progress(count / max(price_ranges.values()))
                st.markdown(f"{count}개 상품")

# 메인 실행
if __name__ == "__main__":
    keyword_analysis_tab()
