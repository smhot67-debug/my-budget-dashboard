import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="공장 경영관리 AI 대시보드", layout="wide")
st.title("📊 실시간 경영관리 & AI 분석 리포트")

# 동권님의 정보 적용 (수정된 구글 시트 및 API 정보)
API_KEY = "AIzaSyAkhIIHXg2XJSBHfrkhxGP_0iW1KZZJlZc"
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6hnNtH_1tBFJoA25lXzFPjKUGpBfu0H313_QVFDPdHOpWDDQSJQvIlOQpUoczNO7z7jyWbE171ApD/pub?output=csv"

# Gemini 설정 (가장 안정적인 'gemini-1.5-flash' 모델 사용)
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. 데이터 불러오기 및 전처리
@st.cache_data(ttl=60)
def load_data():
    data = pd.read_csv(SHEET_URL)
    # 빈 값(None)을 0으로 채워서 표를 깔끔하게 만듭니다.
    data = data.fillna(0)
    return data

try:
    df = load_data()
    
    # 3. 데이터 시각화 (표 출력)
    st.subheader("📋 실시간 예산 집행 현황")
    st.dataframe(df, width='stretch')

    # 4. AI 분석 버튼
    st.divider()
    if st.button("🤖 Gemini AI 분석 실행"):
        with st.spinner('동권님의 데이터를 분석 중입니다...'):
            # 분석을 위한 프롬프트 구성
            prompt = f"너는 공장 경영관리 전문가야. 다음 팀별 예산 데이터를 보고 집행률이 높거나 낮은 팀을 분석해서 관리 포인트를 알려줘: {df.to_string()}"
            response = model.generate_content(prompt)
            st.markdown("### 💡 AI 분석 결과")
            st.markdown(response.text)

except Exception as e:
    st.error(f"데이터 연결 중 오류가 발생했습니다: {e}")
