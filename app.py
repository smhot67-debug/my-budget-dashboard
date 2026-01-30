import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. 환경 설정
st.set_page_config(page_title="공장 경영관리 AI 대시보드", layout="wide")
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6hnNtH_1tBFJoA25lXzFPjKUGpBfu0H313_QVFDPdHOpWDDQSJQvIlOQpUoczNO7z7jyWbE171ApD/pubhtml"
API_KEY = "AIzaSyAkhIIHXg2XJSBHfrkhxGP_0iW1KZZJlZc"

# Gemini 설정
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

st.title("📊 실시간 경영관리 & AI 분석 리포트")
st.info("구글 시트의 데이터를 기반으로 Gemini AI가 현재 상황을 분석합니다.")

# 2. 데이터 불러오기 (Pandas)
@st.cache_data(ttl=600)  # 10분마다 데이터 갱신
def load_data():
    # 웹에 게시된 HTML 주소에서 테이블 데이터를 읽어옵니다.
    df = pd.read_html(GOOGLE_SHEET_URL, header=1)[0]
    # 불필요한 인덱스 열 제거 등 전처리 (시트 구조에 맞춰 조정 필요)
    df = df.iloc[:, 1:] 
    return df

try:
    data = load_data()
    
    # 3. 데이터 시각화 섹션
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 현재 데이터 현황")
        st.dataframe(data, use_container_width=True)
        
    with col2:
        st.subheader("🤖 Gemini AI 분석 요약")
        if st.button("AI 분석 실행"):
            prompt = f"다음은 우리 공장의 경영 데이터입니다: {data.to_string()}. 이 데이터를 바탕으로 현재 가장 개선이 필요한 비용 항목이나 생산 효율성 관점에서의 제언을 3가지 핵심 요약해줘."
            response = model.generate_content(prompt)
            st.write(response.text)
        else:
            st.write("버튼을 누르면 분석을 시작합니다.")

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")