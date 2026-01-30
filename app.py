import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="공장 예산관리 실시간 대시보드", layout="wide")

# 동권님의 설정 정보
API_KEY = "AIzaSyAkhIIHXg2XJSBHfrkhxGP_0iW1KZZJlZc"
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6hnNtH_1tBFJoA25lXzFPjKUGpBfu0H313_QVFDPdHOpWDDQSJQvIlOQpUoczNO7z7jyWbE171ApD/pub?output=csv"

# AI 설정 (필요할 때만 호출)
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. 데이터 처리 함수 (오류 방지 및 숫자 정제)
@st.cache_data(ttl=60)
def load_and_clean_data():
    data = pd.read_csv(SHEET_URL)
    data = data.fillna(0)
    
    # 숫자형으로 변환 (팀명 제외)
    for col in data.columns:
        if col != '팀명':
            data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)
    
    # 집행률 계산 (배정예산 대비 모든 월의 합계)
    # 3번째 컬럼(1월_추가 등)부터 마지막까지가 지출액이라고 가정
    data['총지출'] = data.iloc[:, 2:].sum(axis=1)
    data['집행률(%)'] = (data['총지출'] / data['배정예산'] * 100).round(1).fillna(0)
    data['잔액'] = data['배정예산'] - data['총지출']
    
    return data

try:
    df = load_and_clean_data()

    # --- 화면 구성 시작 ---
    st.title("🏭 공장 팀별 예산 집행 대시보드")
    st.caption(f"데이터 갱신 시간: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # [A] 상단 요약 카드 (동권님의 HTML 폼 스타일)
    total_b = df['배정예산'].sum()
    total_s = df['총지출'].sum()
    total_r = df['잔액'].sum()
    total_p = (total_s / total_b * 100) if total_b > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("전체 배정예산", f"{total_b:,.0f}원")
    m2.metric("전체 집행액", f"{total_s:,.0f}원", f"{total_p:.1f}% 집행")
    m3.metric("전체 잔액", f"{total_r:,.0f}원", delta_color="normal")
    m4.metric("대상 팀 수", f"{len(df)}개 팀")

    st.divider()

    # [B] 시각화 영역 (숫자를 그래프로!)
    col_left, col_right = st.columns([6, 4])

    with col_left:
        st.subheader("📊 팀별 예산 집행률 (%)")
        # 집행률에 따라 색상이 변하는 막대 그래프
        fig = px.bar(df, x='팀명', y='집행률(%)', 
                     text='집행률(%)',
                     color='집행률(%)',
                     color_continuous_scale=['#10b981', '#f59e0b', '#ef4444'], # 초록 -> 주황 -> 빨강
                     range_color=[0, 100])
        fig.update_traces(texttemplate='%{text}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("💰 팀별 예산 비중 (배정액 기준)")
        fig_pie = px.pie(df, values='배정예산', names='팀명', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

    # [C] 상세 데이터 표
    st.subheader("📋 실시간 예산 관리 상세표")
    # 집행률이 90% 넘는 팀은 빨간색으로 강조하는 스타일 적용 가능 (간략화)
    st.dataframe(df.style.format({
        '배정예산': '{:,.0f}', '총지출': '{:,.0f}', '잔액': '{:,.0f}', '집행률(%)': '{:.1f}%'
    }).background_gradient(subset=['집행률(%)'], cmap='YlOrRd'), width='stretch')

    # [D] AI 분석 (필요할 때만 펼쳐서 보기)
    with st.expander("🤖 Gemini AI에게 경영관리 조언 구하기"):
        if st.button("데이터 기반 리포트 생성"):
            with st.spinner('분석 중...'):
                prompt = f"너는 경영관리 전문가야. 다음 팀별 예산 데이터를 보고 집행률이 위험한 팀을 지목하고 대책을 알려줘: {df[['팀명', '배정예산', '총지출', '집행률(%)']].to_string()}"
                response = model.generate_content(prompt)
                st.markdown(response.text)

except Exception as e:
    st.error(f"대시보드 로딩 중 오류 발생: {e}")
