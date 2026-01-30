import streamlit as st
import pandas as pd
import google.generativeai as genai

# 페이지 설정
st.set_page_config(page_title="공장 경영관리 AI 대시보드", layout="wide")

# API 및 시트 정보 (동권님 정보 적용)
API_KEY = "AIzaSyAkhIIHXg2XJSBHfrkhxGP_0iW1KZZJlZc"
# 주소를 CSV 형식으로 고정하여 'No tables found' 에러를 원천 차단합니다.
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6hnNtH_1tBFJoA25lXzFPjKUGpBfu0H313_QVFDPdHOpWDDQSJQvIlOQpUoczNO7z7jyWbE171ApD/pub?output=csv"

# Gemini 설정
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("📊 실시간 경영관리 & AI 분석 리포트")

@st.cache_data(ttl=60)
def load_data():
    # CSV로 읽어야 오류 없이 표가 즉시 나타납니다.
    return pd.read_csv(SHEET_URL)

try:
    df = load_data()
    st.subheader("📋 실시간 예산 집행 현황")
    st.dataframe(df, use_container_width=True)

    if st.button("🤖 Gemini AI 분석 실행"):
        with st.spinner('데이터 분석 중...'):
            prompt = f"너는 공장 경영관리 전문가야. 다음 데이터를 보고 예산 절감 포인트 3가지만 제안해줘: {df.to_string()}"
            response = model.generate_content(prompt)
            st.markdown(response.text)

except Exception as e:
    st.error(f"데이터 연동 실패: {e}")
