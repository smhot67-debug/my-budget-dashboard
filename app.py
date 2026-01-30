import streamlit as st
import pandas as pd
import google.generativeai as genai
import streamlit.components.v1 as components

# 1. 초기 설정
st.set_page_config(page_title="공장 경영관리 AI 대시보드", layout="wide")

# 동권님의 설정값
API_KEY = "AIzaSyAkhIIHXg2XJSBHfrkhxGP_0iW1KZZJlZc"
# 구글 시트 주소 (CSV 출력 모드)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6hnNtH_1tBFJoA25lXzFPjKUGpBfu0H313_QVFDPdHOpWDDQSJQvIlOQpUoczNO7z7jyWbE171ApD/pub?output=csv"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. 데이터 자동 로드 함수
@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df = df.fillna(0) # 빈칸은 0으로 처리
    return df

# 3. 메인 화면 구성
st.title("🏭 공장 비용 관리 대시보드 (AI 통합형)")
st.info("데이터는 구글 스프레드시트와 실시간 연동 중입니다. 시트에서 숫자를 바꾸면 이곳에 즉시 반영됩니다.")

try:
    df = load_data()

    # 상단 요약 지표 (동권님의 디자인 철학 반영)
    col1, col2, col3 = st.columns(3)
    total_budget = df['배정예산'].sum() if '배정예산' in df.columns else 0
    total_spent = df.iloc[:, 2:].sum().sum() # 1월~12월 모든 지출 합계
    
    with col1:
        st.metric("총 배정 예산", f"{total_budget:,.0f}원")
    with col2:
        st.metric("현재 총 집행액", f"{total_spent:,.0f}원", delta=f"집행률 {round(total_spent/total_budget*100, 1)}%" if total_budget > 0 else "0%")
    with col3:
        st.metric("총 잔여 예산", f"{(total_budget - total_spent):,.0f}원")

    # 월별 누계 관리표 (HTML 폼 스타일로 출력)
    st.subheader("📋 월별 누계 관리표")
    st.dataframe(df, width='stretch')

    # AI 분석 섹션 (동권님의 폼 하단에 추가되는 강력한 도구)
    st.divider()
    st.subheader("🤖 Gemini AI 경영지원 리포트")
    
    if st.button("실시간 집행 현황 분석 실행"):
        with st.spinner('경영관리 관점에서 데이터를 분석 중입니다...'):
            # AI에게 데이터를 텍스트로 전달
            prompt = f"""
            너는 공장 경영관리 전문가야. 아래의 팀별 월별 예산 데이터를 보고 다음 사항을 보고해줘:
            1. 현재 예산 집행 속도가 너무 빠른 팀은 어디인가?
            2. 예산 절감이 시급해 보이는 부분은?
            3. 공장 운영 효율을 위해 경영진이 결정해야 할 점은?
            
            데이터: {df.to_string()}
            """
            response = model.generate_content(prompt)
            st.success("분석이 완료되었습니다.")
            st.markdown(response.text)

except Exception as e:
    st.error(f"시트 연동 실패: {e}. 구글 시트가 '웹에 게시' 되어 있는지 확인해 주세요.")

# 하단에 동권님의 원본 HTML 폼 디자인 가이드 추가 (필요시 참고용)
with st.expander("원본 폼 디자인 가이드 보기"):
    st.write("동권 님이 제작하신 HTML 기반 UI 가이드는 내부 시스템에 저장되어 있으며, 향후 시각화 차트 업데이트 시 참조됩니다.")

