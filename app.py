import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="공장 경영관리 AI 대시보드", layout="wide")
st.title("🏭 공장 비용 관리 대시보드 (AI 통합형)")

# 동권님의 정보 적용
API_KEY = "AIzaSyAkhIIHXg2XJSBHfrkhxGP_0iW1KZZJlZc"
# 동권님이 새로 뽑아주신 CSV 전용 주소입니다.
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6hnNtH_1tBFJoA25lXzFPjKUGpBfu0H313_QVFDPdHOpWDDQSJQvIlOQpUoczNO7z7jyWbE171ApD/pub?output=csv"

# Gemini 설정 (최신 라이브러리에 최적화된 모델명 사용)
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. 데이터 자동 로드 및 정제 함수
@st.cache_data(ttl=60)
def load_data():
    # CSV 주소에서 데이터를 읽어옵니다.
    data = pd.read_csv(SHEET_URL)
    
    # [정제] 'None'이나 빈칸 때문에 생기는 오류를 방지하기 위해 0으로 채웁니다.
    data = data.fillna(0)
    
    # [정제] 숫자가 들어와야 하는 컬럼들을 강제로 숫자형으로 바꿉니다.
    for col in data.columns:
        if col != '팀명': # 팀명(글자)만 제외하고 모두 숫자로 변환
            data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)
            
    return data

try:
    df = load_data()
    
    # 3. 상단 요약 카드 (동권님의 디자인 철학 반영)
    st.info("데이터는 구글 스프레드시트와 실시간 연동 중입니다. 시트에서 숫자를 바꾸면 이곳에 즉시 반영됩니다.")
    
    col1, col2, col3 = st.columns(3)
    
    # 배정예산 합계
    total_budget = df['배정예산'].sum() if '배정예산' in df.columns else 0
    # 1월~12월 모든 지출 합계 (3번째 컬럼부터 끝까지가 월별 데이터라고 가정)
    total_spent = df.iloc[:, 2:].sum().sum() 
    
    with col1:
        st.metric("총 배정 예산", f"{total_budget:,.0f}원")
    with col2:
        pct = (total_spent / total_budget * 100) if total_budget > 0 else 0
        st.metric("현재 총 집행액", f"{total_spent:,.0f}원", delta=f"집행률 {pct:.1f}%")
    with col3:
        st.metric("총 잔여 예산", f"{(total_budget - total_spent):,.0f}원")

    # 4. 월별 누계 관리표 (최신 문법 적용)
    st.subheader("📋 월별 예산 집행 세부 현황")
    st.dataframe(df, width='stretch')

    # 5. AI 분석 섹션
    st.divider()
    st.subheader("🤖 Gemini AI 경영지원 리포트")
    
    if st.button("실시간 집행 현황 분석 실행"):
        with st.spinner('동권님의 공장 데이터를 분석 중입니다...'):
            prompt = f"너는 공장 경영관리 전문가야. 다음 팀별/월별 예산 데이터를 보고 집행률이 비정상적으로 높거나 낮은 팀을 찾아내고, 경영지원팀이 조치해야 할 사항 3가지를 알려줘: {df.to_string()}"
            response = model.generate_content(prompt)
            st.success("분석이 완료되었습니다.")
            st.markdown(response.text)

except Exception as e:
    st.error(f"데이터 연동 과정에서 오류가 발생했습니다: {e}")
