import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. 설정
st.set_page_config(page_title="공장 경영관리 AI 대시보드", layout="wide")
API_KEY = "AIzaSyAkhIIHXg2XJSBHfrkhxGP_0iW1KZZJlZc"
# 데이터를 더 정확히 가져오기 위해 주소를 CSV 출력 형식으로 변경했습니다.
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6hnNtH_1tBFJoA25lXzFPjKUGpBfu0H313_QVFDPdHOpWDDQSJQvIlOQpUoczNO7z7jyWbE171ApD/pub?output=csv"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("📊 실시간 경영관리 & AI 분석 리포트")

@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv(SHEET_URL)

try:
    df = load_data()
    st.subheader("📋 실시간 예산 집행 현황")
    st.dataframe(df, use_container_width=True)

    if st.button("🤖 Gemini AI에게 분석 요청하기"):
        with st.spinner('데이터 분석 중...'):
            prompt = f"너는 공장 경영관리 전문가야. 다음 데이터를 보고 비용 절감이 필요한 팀이나 주의할 점을 요약해줘: {df.to_string()}"
            response = model.generate_content(prompt)
            st.markdown(response.text)

except Exception as e:
    st.error(f"데이터 연결 오류: {e}")
