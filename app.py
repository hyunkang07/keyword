"""
본 프로그램 'RankChecker by L&C'는 Link&Co, Inc.에 의해 개발된 소프트웨어입니다.
해당 소스코드 및 실행 파일의 무단 복제, 배포, 역컴파일, 수정은
저작권법 및 컴퓨터프로그램 보호법에 따라 엄격히 금지됩니다.

무단 유포 및 상업적 이용 시 민형사상 법적 책임을 물을 수 있습니다.

Copyright ⓒ 2025 Link&Co. All rights reserved.
Unauthorized reproduction or redistribution is strictly prohibited. 
"""

import streamlit as st
import json
import urllib.request
import urllib.parse
import re
import hashlib
import hmac
import base64
import time
import pandas as pd
import os
from typing import Optional, Dict, List
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 네이버 쇼핑 검색 API 설정
CLIENT_ID = os.getenv("NAVER_CLIENT_ID", "your_client_id_here")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET", "your_client_secret_here")

# 네이버 광고 API 설정
CUSTOMER_ID = os.getenv("NAVER_CUSTOMER_ID", "your_customer_id_here")
API_KEY = os.getenv("NAVER_API_KEY", "your_api_key_here")
SECRET_KEY = os.getenv("NAVER_SECRET_KEY", "your_secret_key_here")

# 페이지 설정
st.set_page_config(
    page_title="네이버 마케팅 도구",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS 스타일링
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
    .result-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #03C75A;
    }
    .success-result {
        border-left-color: #03C75A;
    }
    .error-result {
        border-left-color: #ff4444;
    }
    .keyword-chip {
        display: inline-block;
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        border-radius: 20px;
        font-size: 0.9rem;
    }
    .keyword-chip:hover {
        background-color: #bbdefb;
        cursor: pointer;
    }
    .footer {
        text-align: center;
        color: #999;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding: 1rem;
        border-top: 1px solid #eee;
    }
    .stButton>button {
        width: 100%;
        background-color: #03C75A;
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 8px;
        border: none;
        font-size: 1.1rem;
    }
    .stButton>button:hover {
        background-color: #02b350;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)


def generate_signature(timestamp, method, uri, secret_key):
    """네이버 광고 API 서명 생성"""
    message = f"{timestamp}.{method}.{uri}"
    signature = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode('utf-8')


def get_related_keywords(keyword: str) -> List[Dict]:
    """
    네이버 검색광고 API를 사용하여 연관 키워드 조회
    
    Args:
        keyword: 검색할 키워드
    
    Returns:
        연관 키워드 리스트
    """
    try:
        timestamp = str(int(time.time() * 1000))
        method = "GET"
        uri = f"/keywordstool"
        
        # 서명 생성
        signature = generate_signature(timestamp, method, uri, SECRET_KEY)
        
        # API 요청
        url = f"https://api.naver.com/keywordstool?hintKeywords={urllib.parse.quote(keyword)}&showDetail=1"
        
        request = urllib.request.Request(url)
        request.add_header("X-Timestamp", timestamp)
        request.add_header("X-API-KEY", API_KEY)
        request.add_header("X-Customer", CUSTOMER_ID)
        request.add_header("X-Signature", signature)
        
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('keywordList', [])
            
    except Exception as e:
        st.error(f"연관 키워드 조회 실패: {str(e)}")
        # 대체 방법: 네이버 쇼핑 검색 결과에서 추출
        return get_keywords_from_search(keyword)


def get_keywords_from_search(keyword: str) -> List[Dict]:
    """
    네이버 쇼핑 검색 결과에서 연관 키워드 추출 (대체 방법)
    
    Args:
        keyword: 검색할 키워드
    
    Returns:
        연관 키워드 리스트
    """
    try:
        encText = urllib.parse.quote(keyword)
        url = f"https://openapi.naver.com/v1/search/shop.json?query={encText}&display=100"
        
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", CLIENT_ID)
        request.add_header("X-Naver-Client-Secret", CLIENT_SECRET)
        
        with urllib.request.urlopen(request) as response:
            result = json.loads(response.read())
            
            # 상품명에서 키워드 추출
            keywords = set()
            for item in result.get("items", []):
                title = re.sub(r"<.*?>", "", item["title"])
                words = title.split()
                for word in words:
                    if len(word) >= 2 and word not in keywords:
                        keywords.add(word)
            
            # 딕셔너리 형태로 변환
            return [{"relKeyword": kw, "monthlyPcQcCnt": "-", "monthlyMobileQcCnt": "-"} 
                    for kw in sorted(list(keywords))[:50]]
                    
    except Exception as e:
        st.error(f"키워드 추출 실패: {str(e)}")
        return []


def get_top_ranked_product_by_mall(keyword: str, mall_name: str, progress_bar, status_text) -> Optional[Dict]:
    """
    네이버 쇼핑에서 특정 키워드와 판매처명으로 최상위 순위 상품을 검색
    
    Args:
        keyword: 검색 키워드
        mall_name: 판매처명
        progress_bar: Streamlit 진행률 바
        status_text: Streamlit 상태 텍스트
    
    Returns:
        최상위 순위 상품 정보 딕셔너리 또는 None
    """
    encText = urllib.parse.quote(keyword)
    seen_titles = set()
    best_product = None
    
    try:
        for page_num, start in enumerate(range(1, 1001, 100), 1):
            progress = page_num / 10
            progress_bar.progress(progress)
            status_text.text(f"🔍 '{keyword}' 검색 중... ({page_num}/10 페이지)")
            
            url = f"https://openapi.naver.com/v1/search/shop.json?query={encText}&display=100&start={start}"
            request = urllib.request.Request(url)
            request.add_header("X-Naver-Client-Id", CLIENT_ID)
            request.add_header("X-Naver-Client-Secret", CLIENT_SECRET)
            
            response = urllib.request.urlopen(request)
            result = json.loads(response.read())
            
            for idx, item in enumerate(result.get("items", []), start=1):
                if item.get("mallName") and mall_name in item["mallName"]:
                    title_clean = re.sub(r"<.*?>", "", item["title"])
                    
                    if title_clean in seen_titles:
                        continue
                    
                    seen_titles.add(title_clean)
                    rank = start + idx - 1
                    
                    product = {
                        "rank": rank,
                        "title": title_clean,
                        "price": item["lprice"],
                        "link": item["link"],
                        "mallName": item["mallName"]
                    }
                    
                    if not best_product or rank < best_product["rank"]:
                        best_product = product
        
        progress_bar.progress(1.0)
        return best_product
        
    except Exception as e:
        st.error(f"❌ 검색 중 오류 발생: {str(e)}")
        return None


def rank_checker_tab():
    """순위 확인 탭"""
    st.markdown("### 📝 검색 정보 입력")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        keywords_input = st.text_area(
            "검색어 (최대 10개, 쉼표로 구분)",
            placeholder="예: 키보드, 마우스, 충전기",
            height=100,
            help="검색할 키워드를 쉼표(,)로 구분하여 입력하세요. 최대 10개까지 입력 가능합니다.",
            key="rank_keywords"
        )
    
    with col2:
        mall_name = st.text_input(
            "판매처명",
            placeholder="예: OO스토어",
            help="순위를 확인할 판매처 이름을 입력하세요.",
            key="rank_mall"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        search_button = st.button("🔍 순위 확인", use_container_width=True, key="rank_search")
    
    if search_button:
        if not keywords_input or not mall_name:
            st.error("⚠️ 검색어와 판매처명을 모두 입력해주세요.")
            return
        
        keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
        
        if not keywords:
            st.error("⚠️ 올바른 검색어를 입력해주세요.")
            return
        
        if len(keywords) > 10:
            st.error("⚠️ 검색어는 최대 10개까지만 입력 가능합니다.")
            return
        
        st.markdown("---")
        st.markdown("### 📊 검색 결과")
        
        results = {}
        overall_progress = st.progress(0)
        overall_status = st.empty()
        
        for idx, keyword in enumerate(keywords, 1):
            overall_status.text(f"⏳ 전체 진행: {idx}/{len(keywords)} 키워드")
            
            keyword_progress = st.progress(0)
            keyword_status = st.empty()
            
            result = get_top_ranked_product_by_mall(keyword, mall_name, keyword_progress, keyword_status)
            
            if result:
                results[keyword] = result
                
                with st.container():
                    st.markdown(f"""
                    <div class="result-box success-result">
                        <h4>✅ {keyword}</h4>
                        <p><strong>순위:</strong> {result['rank']}위</p>
                        <p><strong>상품명:</strong> {result['title']}</p>
                        <p><strong>가격:</strong> {int(result['price']):,}원</p>
                        <p><strong>판매처:</strong> {result['mallName']}</p>
                        <p><strong>링크:</strong> <a href="{result['link']}" target="_blank">상품 보기</a></p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                results[keyword] = None
                
                with st.container():
                    st.markdown(f"""
                    <div class="result-box error-result">
                        <h4>❌ {keyword}</h4>
                        <p style="color: #ff4444;">검색 결과 없음</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            keyword_status.empty()
            keyword_progress.empty()
            overall_progress.progress(idx / len(keywords))
        
        overall_status.text("✅ 모든 검색 완료!")
        
        st.markdown("---")
        st.markdown("### 📈 검색 요약")
        
        found_count = sum(1 for v in results.values() if v is not None)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 검색 키워드", len(keywords))
        with col2:
            st.metric("발견된 상품", found_count)
        with col3:
            st.metric("미발견 상품", len(keywords) - found_count)


def keyword_analysis_tab():
    """키워드 분석 탭"""
    st.markdown("### 🔎 키워드 분석")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        keyword_input = st.text_input(
            "분석할 키워드 입력",
            placeholder="예: 무선키보드",
            help="연관 키워드를 분석할 키워드를 입력하세요.",
            key="analysis_keyword"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_button = st.button("📊 분석하기", use_container_width=True, key="analysis_search")
    
    if analyze_button:
        if not keyword_input:
            st.error("⚠️ 키워드를 입력해주세요.")
            return
        
        st.markdown("---")
        
        with st.spinner(f"'{keyword_input}' 키워드 분석 중..."):
            related_keywords = get_related_keywords(keyword_input)
        
        if related_keywords:
            st.success(f"✅ {len(related_keywords)}개의 연관 키워드를 찾았습니다!")
            
            # 데이터프레임 생성
            df_data = []
            for idx, kw in enumerate(related_keywords, 1):
                keyword_text = kw.get('relKeyword', '')
                
                # 월간검색수
                pc_search = kw.get('monthlyPcQcCnt', '-')
                mobile_search = kw.get('monthlyMobileQcCnt', '-')
                
                # 월평균클릭수
                pc_click = kw.get('monthlyAvePcClkCnt', '-')
                mobile_click = kw.get('monthlyAveMobileClkCnt', '-')
                
                # 월평균클릭률
                pc_ctr = kw.get('monthlyAvePcCtr', '-')
                mobile_ctr = kw.get('monthlyAveMobileCtr', '-')
                
                # 경쟁정도
                comp_idx = kw.get('compIdx', '-')
                
                # 월평균노출광고수
                avg_ads = kw.get('monthlyAveImpsCnt', '-')
                
                # 숫자 변환 (정렬용)
                try:
                    pc_search_num = int(pc_search) if str(pc_search).isdigit() else 0
                    mobile_search_num = int(mobile_search) if str(mobile_search).isdigit() else 0
                    total_search = pc_search_num + mobile_search_num
                except:
                    pc_search_num = 0
                    mobile_search_num = 0
                    total_search = 0
                
                df_data.append({
                    '순번': idx,
                    '연관키워드': keyword_text,
                    'PC 월간검색수': pc_search if pc_search == '-' else f'{pc_search_num:,}',
                    '모바일 월간검색수': mobile_search if mobile_search == '-' else f'{mobile_search_num:,}',
                    'PC 월평균클릭수': pc_click if pc_click == '-' else (f'{int(pc_click):,}' if str(pc_click).replace('.', '').isdigit() else pc_click),
                    '모바일 월평균클릭수': mobile_click if mobile_click == '-' else (f'{int(mobile_click):,}' if str(mobile_click).replace('.', '').isdigit() else mobile_click),
                    'PC 월평균클릭률': pc_ctr if pc_ctr == '-' else f'{float(pc_ctr):.2f}%' if str(pc_ctr).replace('.', '').isdigit() else pc_ctr,
                    '모바일 월평균클릭률': mobile_ctr if mobile_ctr == '-' else f'{float(mobile_ctr):.2f}%' if str(mobile_ctr).replace('.', '').isdigit() else mobile_ctr,
                    '경쟁정도': comp_idx,
                    '월평균노출광고수': avg_ads if avg_ads == '-' else (f'{int(avg_ads):,}' if str(avg_ads).replace('.', '').isdigit() else avg_ads),
                    '_pc_num': pc_search_num,
                    '_mobile_num': mobile_search_num,
                    '_total_num': total_search
                })
            
            df = pd.DataFrame(df_data)
            
            # 필터 및 정렬 옵션
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                sort_option = st.selectbox(
                    "📊 정렬 기준",
                    ["순번", "연관키워드", "PC 월간검색수", "모바일 월간검색수", "전체 검색량"],
                    key="sort_option"
                )
            
            with col2:
                sort_order = st.selectbox(
                    "📈 정렬 방향",
                    ["내림차순 ↓", "오름차순 ↑"],
                    key="sort_order"
                )
            
            with col3:
                search_filter = st.text_input(
                    "🔍 키워드 필터링",
                    placeholder="특정 키워드 검색...",
                    key="keyword_filter"
                )
            
            # 필터링
            if search_filter:
                df = df[df['연관키워드'].str.contains(search_filter, case=False, na=False)]
            
            # 정렬
            ascending = (sort_order == "오름차순 ↑")
            
            if sort_option == "PC 월간검색수":
                df = df.sort_values('_pc_num', ascending=ascending)
            elif sort_option == "모바일 월간검색수":
                df = df.sort_values('_mobile_num', ascending=ascending)
            elif sort_option == "전체 검색량":
                df = df.sort_values('_total_num', ascending=ascending)
            elif sort_option == "연관키워드":
                df = df.sort_values('연관키워드', ascending=ascending)
            else:  # 순번
                df = df.sort_values('순번', ascending=ascending)
            
            # 숨김 컬럼 제거
            display_df = df[[
                '순번', '연관키워드', 
                'PC 월간검색수', '모바일 월간검색수',
                'PC 월평균클릭수', '모바일 월평균클릭수',
                'PC 월평균클릭률', '모바일 월평균클릭률',
                '경쟁정도', '월평균노출광고수'
            ]].reset_index(drop=True)
            
            # 통계 정보
            st.markdown("### 📈 통계 요약")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("전체 키워드", len(display_df))
            
            with col2:
                total_pc = df['_pc_num'].sum()
                st.metric("총 PC 검색량", f"{total_pc:,}" if total_pc > 0 else "-")
            
            with col3:
                total_mobile = df['_mobile_num'].sum()
                st.metric("총 모바일 검색량", f"{total_mobile:,}" if total_mobile > 0 else "-")
            
            with col4:
                total_all = df['_total_num'].sum()
                st.metric("총 검색량", f"{total_all:,}" if total_all > 0 else "-")
            
            # 테이블 표시
            st.markdown("### 📋 연관 키워드 목록")
            
            # HTML 테이블 생성 (헤더 고정)
            table_html = """
            <style>
                .keyword-table-wrapper {
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    margin-bottom: 1rem;
                }
                .keyword-table {
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 0.85rem;
                }
                .keyword-table thead th {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 12px 8px;
                    text-align: center;
                    font-weight: 600;
                    position: sticky;
                    top: 0;
                    z-index: 10;
                    border-right: 1px solid rgba(255,255,255,0.2);
                    font-size: 0.8rem;
                }
                .keyword-table thead th:last-child {
                    border-right: none;
                }
                .keyword-table tbody tr {
                    border-bottom: 1px solid #f0f0f0;
                    transition: background-color 0.2s;
                }
                .keyword-table tbody tr:hover {
                    background-color: #f0f7ff;
                }
                .keyword-table tbody tr:nth-child(even) {
                    background-color: #fafafa;
                }
                .keyword-table td {
                    padding: 10px 8px;
                    border-right: 1px solid #f0f0f0;
                }
                .keyword-table td:last-child {
                    border-right: none;
                }
                .table-container {
                    max-height: 500px;
                    overflow-y: auto;
                    overflow-x: auto;
                }
                .table-container::-webkit-scrollbar {
                    width: 8px;
                    height: 8px;
                }
                .table-container::-webkit-scrollbar-track {
                    background: #f1f1f1;
                }
                .table-container::-webkit-scrollbar-thumb {
                    background: #888;
                    border-radius: 4px;
                }
                .table-container::-webkit-scrollbar-thumb:hover {
                    background: #555;
                }
                .num-col {
                    text-align: center;
                    color: #666;
                    font-weight: 500;
                }
                .keyword-col {
                    font-weight: 600;
                    color: #03C75A;
                    text-align: left;
                }
                .count-col {
                    text-align: right;
                    color: #333;
                }
                .center-col {
                    text-align: center;
                    color: #666;
                }
            </style>
            <div class="keyword-table-wrapper">
                <div class="table-container">
                    <table class="keyword-table">
                        <thead>
                            <tr>
                                <th rowspan="2" style="width: 5%;">순번</th>
                                <th rowspan="2" style="width: 15%;">연관키워드</th>
                                <th colspan="2" style="border-bottom: 1px solid rgba(255,255,255,0.3);">월간검색수</th>
                                <th colspan="2" style="border-bottom: 1px solid rgba(255,255,255,0.3);">월평균클릭수</th>
                                <th colspan="2" style="border-bottom: 1px solid rgba(255,255,255,0.3);">월평균클릭률</th>
                                <th rowspan="2" style="width: 8%;">경쟁<br>정도</th>
                                <th rowspan="2" style="width: 10%;">월평균<br>노출광고수</th>
                            </tr>
                            <tr>
                                <th style="width: 10%;">💻 PC</th>
                                <th style="width: 10%;">📱 모바일</th>
                                <th style="width: 10%;">💻 PC</th>
                                <th style="width: 10%;">📱 모바일</th>
                                <th style="width: 10%;">💻 PC</th>
                                <th style="width: 10%;">📱 모바일</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            for _, row in display_df.iterrows():
                table_html += f"""
                            <tr>
                                <td class="num-col">{row['순번']}</td>
                                <td class="keyword-col">{row['연관키워드']}</td>
                                <td class="count-col">{row['PC 월간검색수']}</td>
                                <td class="count-col">{row['모바일 월간검색수']}</td>
                                <td class="count-col">{row['PC 월평균클릭수']}</td>
                                <td class="count-col">{row['모바일 월평균클릭수']}</td>
                                <td class="count-col">{row['PC 월평균클릭률']}</td>
                                <td class="count-col">{row['모바일 월평균클릭률']}</td>
                                <td class="center-col">{row['경쟁정도']}</td>
                                <td class="count-col">{row['월평균노출광고수']}</td>
                            </tr>
                """
            
            table_html += """
                        </tbody>
                    </table>
                </div>
            </div>
            """
            
            st.markdown(table_html, unsafe_allow_html=True)
            
            # 키워드 클라우드 (선택적 표시)
            with st.expander("🏷️ 키워드 태그 클라우드 보기"):
                keywords_html = "".join([
                    f'<span class="keyword-chip">{row["연관키워드"]}</span>'
                    for _, row in display_df.head(50).iterrows()
                ])
                st.markdown(f'<div style="line-height: 2.5;">{keywords_html}</div>', unsafe_allow_html=True)
            
            # CSV 다운로드
            col1, col2 = st.columns([3, 1])
            with col2:
                csv_data = display_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 CSV 다운로드",
                    data=csv_data,
                    file_name=f"{keyword_input}_연관키워드.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.warning("⚠️ 연관 키워드를 찾을 수 없습니다.")


def shopping_rank_tab():
    """네이버 쇼핑 순위 1~100위 탭"""
    st.markdown("### 🛍️ 네이버 쇼핑 순위 조회")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        keyword_input = st.text_input(
            "검색 키워드",
            placeholder="예: 무선키보드",
            help="네이버 쇼핑에서 순위를 확인할 키워드를 입력하세요.",
            key="shopping_keyword"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_button = st.button("🔍 순위 조회", use_container_width=True, key="shopping_search")
    
    if search_button:
        if not keyword_input:
            st.error("⚠️ 검색 키워드를 입력해주세요.")
            return
        
        st.markdown("---")
        
        with st.spinner(f"'{keyword_input}' 순위 조회 중..."):
            # 1~100위 데이터 가져오기
            encText = urllib.parse.quote(keyword_input)
            products = []
            
            try:
                # 100개 상품 조회 (API는 최대 100개까지 한 번에 조회 가능)
                url = f"https://openapi.naver.com/v1/search/shop.json?query={encText}&display=100&start=1&sort=sim"
                request = urllib.request.Request(url)
                request.add_header("X-Naver-Client-Id", CLIENT_ID)
                request.add_header("X-Naver-Client-Secret", CLIENT_SECRET)
                
                response = urllib.request.urlopen(request)
                result = json.loads(response.read())
                
                # 중복 제거를 위한 set
                seen_titles = set()
                
                for item in result.get("items", []):
                    title_clean = re.sub(r"<.*?>", "", item["title"])
                    
                    # 중복 상품 제거
                    if title_clean in seen_titles:
                        continue
                    seen_titles.add(title_clean)
                    
                    products.append({
                        '상품명': title_clean,
                        '최저가': int(item.get("lprice", 0)),
                        '판매처': item.get("mallName", "-"),
                        '브랜드': item.get("brand", "-"),
                        '카테고리': item.get("category1", "-") + " > " + item.get("category2", "-") if item.get("category2") else item.get("category1", "-"),
                        '링크': item.get("link", ""),
                        '_price_num': int(item.get("lprice", 0))
                    })
                    
                    # 100개가 되면 중단
                    if len(products) >= 100:
                        break
                
                if products:
                    # 데이터프레임 생성
                    df = pd.DataFrame(products)
                    
                    # 원래 순위 추가 (1위부터 시작)
                    df.insert(0, '순위', range(1, len(df) + 1))
                    df['_original_rank'] = df['순위']  # 원래 순위 백업
                    
                    st.success(f"✅ 상위 {len(products)}위까지 상품을 찾았습니다!")
                    
                    # 필터 옵션
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        sort_option = st.selectbox(
                            "📊 정렬 기준",
                            ["네이버 순위", "최저가 낮은순", "최저가 높은순"],
                            key="shopping_sort"
                        )
                    
                    with col2:
                        mall_filter = st.text_input(
                            "🏪 판매처 필터",
                            placeholder="판매처명 검색...",
                            key="mall_filter"
                        )
                    
                    with col3:
                        brand_filter = st.text_input(
                            "🏷️ 브랜드 필터",
                            placeholder="브랜드명 검색...",
                            key="brand_filter"
                        )
                    
                    with col4:
                        product_filter = st.text_input(
                            "🔍 상품명 필터",
                            placeholder="상품명 검색...",
                            key="product_filter"
                        )
                    
                    # 필터링
                    filtered_df = df.copy()
                    if mall_filter:
                        filtered_df = filtered_df[filtered_df['판매처'].str.contains(mall_filter, case=False, na=False)]
                    if brand_filter:
                        filtered_df = filtered_df[filtered_df['브랜드'].str.contains(brand_filter, case=False, na=False)]
                    if product_filter:
                        filtered_df = filtered_df[filtered_df['상품명'].str.contains(product_filter, case=False, na=False)]
                    
                    # 정렬
                    if sort_option == "최저가 낮은순":
                        filtered_df = filtered_df.sort_values('_price_num', ascending=True)
                        # 정렬 후 순위 재지정
                        filtered_df['순위'] = range(1, len(filtered_df) + 1)
                    elif sort_option == "최저가 높은순":
                        filtered_df = filtered_df.sort_values('_price_num', ascending=False)
                        # 정렬 후 순위 재지정
                        filtered_df['순위'] = range(1, len(filtered_df) + 1)
                    else:  # 네이버 순위
                        filtered_df = filtered_df.sort_values('_original_rank', ascending=True)
                        # 네이버 원래 순위 유지
                        filtered_df['순위'] = filtered_df['_original_rank']
                    
                    df = filtered_df.reset_index(drop=True)
                    
                    # 통계 요약
                    st.markdown("### 📈 통계 요약")
                    
                    if len(df) > 0:
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("조회된 상품수", f"{len(df)}개")
                        
                        with col2:
                            avg_price = df['_price_num'].mean()
                            st.metric("평균 가격", f"{int(avg_price):,}원")
                        
                        with col3:
                            min_price = df['_price_num'].min()
                            st.metric("최저 가격", f"{int(min_price):,}원")
                        
                        with col4:
                            max_price = df['_price_num'].max()
                            st.metric("최고 가격", f"{int(max_price):,}원")
                    else:
                        st.warning("⚠️ 필터 조건에 맞는 상품이 없습니다.")
                    
                    # 테이블 표시
                    if len(df) > 0:
                        st.markdown("### 📋 상품 순위 (1~100위)")
                        
                        # HTML 테이블 생성
                        table_html = """
                        <style>
                            .shopping-table-wrapper {
                                border-radius: 8px;
                                overflow: hidden;
                                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                                margin-bottom: 1rem;
                            }
                            .shopping-table {
                                width: 100%;
                                border-collapse: collapse;
                                font-size: 0.85rem;
                            }
                            .shopping-table thead th {
                                background: linear-gradient(135deg, #03C75A 0%, #02b350 100%);
                                color: white;
                                padding: 12px 8px;
                                text-align: center;
                                font-weight: 600;
                                position: sticky;
                                top: 0;
                                z-index: 10;
                                border-right: 1px solid rgba(255,255,255,0.2);
                            }
                            .shopping-table thead th:last-child {
                                border-right: none;
                            }
                            .shopping-table tbody tr {
                                border-bottom: 1px solid #f0f0f0;
                                transition: background-color 0.2s;
                            }
                            .shopping-table tbody tr:hover {
                                background-color: #e8f5e9;
                            }
                            .shopping-table tbody tr:nth-child(even) {
                                background-color: #fafafa;
                            }
                            .shopping-table td {
                                padding: 10px 8px;
                                border-right: 1px solid #f0f0f0;
                            }
                            .shopping-table td:last-child {
                                border-right: none;
                            }
                            .shopping-container {
                                max-height: 600px;
                                overflow-y: auto;
                                overflow-x: auto;
                            }
                            .shopping-container::-webkit-scrollbar {
                                width: 8px;
                                height: 8px;
                            }
                            .shopping-container::-webkit-scrollbar-track {
                                background: #f1f1f1;
                            }
                            .shopping-container::-webkit-scrollbar-thumb {
                                background: #03C75A;
                                border-radius: 4px;
                            }
                            .shopping-container::-webkit-scrollbar-thumb:hover {
                                background: #02b350;
                            }
                            .rank-col {
                                text-align: center;
                                font-weight: bold;
                                color: #666;
                            }
                            .rank-1 { color: #FFD700; font-size: 1.1rem; }
                            .rank-2 { color: #C0C0C0; font-size: 1.05rem; }
                            .rank-3 { color: #CD7F32; font-size: 1.05rem; }
                            .product-col {
                                text-align: left;
                                color: #333;
                            }
                            .price-col {
                                text-align: right;
                                font-weight: 600;
                                color: #03C75A;
                            }
                            .mall-col {
                                text-align: center;
                                color: #666;
                            }
                            .link-btn {
                                display: inline-block;
                                padding: 4px 12px;
                                background: #03C75A;
                                color: white;
                                text-decoration: none;
                                border-radius: 4px;
                                font-size: 0.8rem;
                                transition: background 0.2s;
                            }
                            .link-btn:hover {
                                background: #02b350;
                            }
                        </style>
                        <div class="shopping-table-wrapper">
                            <div class="shopping-container">
                                <table class="shopping-table">
                                    <thead>
                                        <tr>
                                            <th style="width: 6%;">순위</th>
                                            <th style="width: 35%;">상품명</th>
                                            <th style="width: 12%;">최저가</th>
                                            <th style="width: 15%;">판매처</th>
                                            <th style="width: 12%;">브랜드</th>
                                            <th style="width: 15%;">카테고리</th>
                                            <th style="width: 5%;">링크</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                        """
                        
                        for _, row in df.iterrows():
                            rank = row['순위']
                            rank_class = f"rank-{rank}" if rank <= 3 else "rank-col"
                            
                            table_html += f"""
                                        <tr>
                                            <td class="{rank_class}">{rank}</td>
                                            <td class="product-col">{row['상품명']}</td>
                                            <td class="price-col">{row['최저가']:,}원</td>
                                            <td class="mall-col">{row['판매처']}</td>
                                            <td class="mall-col">{row['브랜드']}</td>
                                            <td class="mall-col" style="font-size: 0.75rem;">{row['카테고리']}</td>
                                            <td style="text-align: center;">
                                                <a href="{row['링크']}" target="_blank" class="link-btn">보기</a>
                                            </td>
                                        </tr>
                            """
                        
                        table_html += """
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        """
                    
                        st.markdown(table_html, unsafe_allow_html=True)
                        
                        # CSV 다운로드
                        col1, col2 = st.columns([3, 1])
                        with col2:
                            csv_df = df[['순위', '상품명', '최저가', '판매처', '브랜드', '카테고리', '링크']]
                            csv_data = csv_df.to_csv(index=False, encoding='utf-8-sig')
                            st.download_button(
                                label="📥 CSV 다운로드",
                                data=csv_data,
                                file_name=f"{keyword_input}_쇼핑순위.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                else:
                    st.warning("⚠️ 검색 결과가 없습니다.")
                    
            except Exception as e:
                st.error(f"❌ 검색 중 오류 발생: {str(e)}")


def main():
    """메인 애플리케이션"""
    
    # 헤더
    st.markdown('<h1 class="main-title">🔍 네이버 마케팅 도구</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">by 링크앤코 (Link&Co)</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["🎯 순위 확인", "🛍️ 쇼핑 순위", "📊 키워드 분석"])
    
    with tab1:
        rank_checker_tab()
    
    with tab2:
        shopping_rank_tab()
    
    with tab3:
        keyword_analysis_tab()
    
    # 푸터
    st.markdown("""
    <div class="footer">
        ⓒ 2025 링크앤코. 무단 복제 및 배포 금지. All rights reserved.
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
