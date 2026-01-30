import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="공장 경영관리 AI 대시보드", layout="wide")
st.title("📊 실시간 경영관리 & AI 분석 리포트")

# 동권님의 정보 적용
API_KEY = "AIzaSyAkhIIHXg2XJSBHfrkhxGP_0iW1KZZJlZc"
# CSV 출력 형식으로 고정하여 안정성을 극대화했습니다.
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6hnNtH_1tBFJoA25lXzFPjKUGpBfu0H313_QVFDPdHOpWDDQSJQvIlOQpUoczNO7z7jyWbE171ApD/pub?output=csv"

# Gemini 설정
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. 데이터 불러오기
@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv(SHEET_URL)

try:
    df = load_data()
    
    # 3. 데이터 시각화
    st.subheader("📋 실시간 예산 집행 현황")
    # 최신 문법(width='stretch') 적용하여 오류를 방지합니다.
    st.dataframe(df, width='stretch')

    # 4. AI 분석 버튼
    if st.button("🤖 Gemini AI 분석 실행"):
        with st.spinner('데이터 분석 중...'):
            prompt = f"너는 공장 경영관리 전문가야. 다음 데이터를 보고 예산 절감 포인트 3가지만 제안해줘: {df.to_string()}"
            response = model.generate_content(prompt)
            st.markdown(response.text)

except Exception as e:
    st.error(f"데이터 연결 실패: {e}")
