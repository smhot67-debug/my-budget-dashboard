import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="공장 경영관리 AI 대시보드", layout="wide")

# 2. 동권님의 정보 설정
API_KEY = "AIzaSyAkhIIHXg2XJSBHfrkhxGP_0iW1KZZJlZc" #
# CSV 출력 형식으로 변경하여 연결 안정성을 높였습니다.
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6hnNtH_1tBFJoA25lXzFPjKUGpBfu0H313_QVFDPdHOpWDDQSJQvIlOQpUoczNO7z7jyWbE171ApD/pub?output=csv" #

# Gemini AI 설정
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("📊 실시간 경영관리 & AI 분석 리포트")

@st.cache_data(ttl=60) # 1분마다 데이터 갱신
def load_data():
    # CSV 방식으로 읽으면 'No tables found' 에러가 해결됩니다.
    return pd.read_csv(SHEET_URL)

try:
    df = load_data()
    st.subheader("📋 실시간 예산 집행 현황")
    # 표를 화면에 출력합니다.
    st.dataframe(df, use_container_width=True)

    # 3. AI 분석 버튼
    if st.button("🤖 Gemini AI에게 분석 요청하기"):
        with st.spinner('데이터 분석 중...'):
            # 동권님의 데이터를 텍스트로 변환하여 AI에게 전달합니다.
            prompt = f"너는 공장 경영관리 전문가야. 다음 데이터를 보고 비용 절감이 필요한 팀이나 운영상 주의할 점을 요약해줘: {df.to_string()}"
            response = model.generate_content(prompt)
            st.markdown(response.text)

except Exception as e:
    st.error(f"데이터 연결 오류: {e}")
