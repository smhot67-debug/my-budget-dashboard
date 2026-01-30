import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="공장 예산관리 실시간 대시보드", layout="wide")

# 설정 정보 (동권님 시트 주소 적용)
API_KEY = "AIzaSyAkhIIHXg2XJSBHfrkhxGP_0iW1KZZJlZc"
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6hnNtH_1tBFJoA25lXzFPjKUGpBfu0H313_QVFDPdHOpWDDQSJQvIlOQpUoczNO7z7jyWbE171ApD/pub?output=csv"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. 데이터 처리 및 자동 정제
@st.cache_data(ttl=60)
def load_and_clean_data():
    data = pd.read_csv(SHEET_URL)
    data = data.fillna(0)
    
    # 숫자형 변환 (팀명 제외)
    for col in data.columns:
        if col != '팀명':
            data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)
    
    # 전체 지출 및 잔액 계산
    data['총지출'] = data.iloc[:, 2:].sum(axis=1)
    data['집행률(%)'] = (data['총지출'] / data['배정예산'] * 100).round(1)
    data['잔액'] = data['배정예산'] - data['총지출']
    return data

try:
    df = load_and_clean_data()

    # --- 대시보드 화면 구성 ---
    st.title("🏭 공장 팀별 예산 집행 대시보드")
    st.info(f"마지막 업데이트: {pd.Timestamp.now().strftime('%H:%M:%S')} (구글 시트와 실시간 연동 중)")

    # [A] 상단 주요 지표 (숫자 카드)
    t_budget = df['배정예산'].sum()
    t_spent = df['총지출'].sum()
    t_remains = df['잔액'].sum()
    t_pct = (t_spent / t_budget * 100) if t_budget > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("전체 배정예산", f"{t_budget:,.0f}원")
    col2.metric("전체 집행액", f"{t_spent:,.0f}원", f"집행률 {t_pct:.1f}%")
    col3.metric("전체 잔액", f"{t_remains:,.0f}원")
    col4.metric("관리 팀 수", f"{len(df)}개 팀")

    st.divider()

    # [B] 그래프 시각화 (숫자를 눈으로 확인)
    left_chart, right_chart = st.columns([6, 4])

    with left_chart:
        st.subheader("📊 팀별 집행률 (%)")
        # 집행률에 따라 색상이 자동으로 바뀌는 막대 그래프 (초록->노랑->빨강)
        fig = px.bar(df, x='팀명', y='집행률(%)', text='집행률(%)',
                     color='집행률(%)', 
                     color_continuous_scale=['#10b981', '#f59e0b', '#ef4444'],
                     range_color=[0, 100])
        fig.update_traces(texttemplate='%{text}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    with right_chart:
        st.subheader("💰 팀별 예산 비중")
        fig_pie = px.pie(df, values='배정예산', names='팀명', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

    # [C] 실시간 데이터 상세 테이블
    st.subheader("📋 실시간 예산 관리 상세표")
    st.dataframe(df.style.format({
        '배정예산': '{:,.0f}', '총지출': '{:,.0f}', '잔액': '{:,.0f}', '집행률(%)': '{:.1f}%'
    }).background_gradient(subset=['집행률(%)'], cmap='YlOrRd'), width='stretch')

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
