import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# 1. 환경 설정
st.set_page_config(page_title="공장 예산관리 통합 시스템", layout="wide")

# API 키
API_KEY = "AIzaSyAkhIIHXg2XJSBHfrkhxGP_0iW1KZZJlZc"

# [중요] 구글 시트 주소 (반드시 'Microsoft Excel(.xlsx)' 형식으로 게시해야 함)
# 아래 주소는 예시입니다. 동권님이 엑셀 형식으로 다시 게시 후 주소를 바꿔주세요.
# 만약 기존 CSV 주소만 있다면, 구글 시트 > 파일 > 공유 > 웹에 게시 > 'Microsoft Excel' 선택 후 주소 복사
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6hnNtH_1tBFJoA25lXzFPjKUGpBfu0H313_QVFDPdHOpWDDQSJQvIlOQpUoczNO7z7jyWbE171ApD/pub?output=xlsx"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. 데이터 로드 및 병합 (핵심 로직)
@st.cache_data(ttl=60)
def load_data_integrated():
    try:
        # 엑셀 파일로 시트 전체를 읽어옵니다 (Sheet1: 기준정보, Sheet2: 지출내역)
        # sheet_name=None을 쓰면 모든 시트를 다 가져옵니다.
        sheets = pd.read_excel(SHEET_URL, sheet_name=None)
        
        # 시트 이름 찾기 (이름이 조금 달라도 찾을 수 있게 처리)
        budget_sheet_name = next((s for s in sheets.keys() if '기준' in s or 'Budget' in s), None)
        expense_sheet_name = next((s for s in sheets.keys() if '지출' in s or 'Expense' in s), None)
        
        if not budget_sheet_name or not expense_sheet_name:
            return "오류: '기준정보' 시트와 '지출내역' 시트가 모두 필요합니다."

        # --- [A] 기준정보(Budget) 처리 ---
        df_budget = sheets[budget_sheet_name].fillna(0)
        
        # 예산 계산: 기본 배정예산 + 월별 추가예산 합계
        # (팀명, 배정예산 컬럼은 고정, 나머지는 월별 추가예산으로 간주)
        # 숫자 정제
        for col in df_budget.columns:
            if col != '팀명':
                df_budget[col] = pd.to_numeric(df_budget[col], errors='coerce').fillna(0)
        
        # 총 예산 = 배정예산 + (나머지 컬럼들의 합)
        df_budget['총예산'] = df_budget.iloc[:, 1:].sum(axis=1)
        df_budget = df_budget[['팀명', '총예산']] # 필요한 컬럼만 남김

        # --- [B] 지출내역(Expense) 처리 ---
        df_expense = sheets[expense_sheet_name].fillna(0)
        
        # 지출 데이터 정제
        if '금액' in df_expense.columns:
            df_expense['금액'] = pd.to_numeric(df_expense['금액'], errors='coerce').fillna(0)
        
        # 팀별로 그룹지어 지출 합계 계산 (여기가 핵심!)
        expense_summary = df_expense.groupby('팀명')['금액'].sum().reset_index()
        expense_summary.rename(columns={'금액': '총지출'}, inplace=True)

        # --- [C] 데이터 병합 (Merge) ---
        # 기준정보(Left)에 지출내역(Right)을 팀명 기준으로 붙이기
        df_final = pd.merge(df_budget, expense_summary, on='팀명', how='left').fillna(0)
        
        # 최종 지표 계산
        df_final['잔액'] = df_final['총예산'] - df_final['총지출']
        df_final['집행률'] = df_final.apply(lambda x: (x['총지출'] / x['총예산'] * 100) if x['총예산'] > 0 else 0, axis=1)
        
        return df_final, df_expense # 요약표와 상세내역 둘 다 반환

    except Exception as e:
        return f"데이터 처리 중 오류 발생: {e}", None

# 3. UI 렌더링
result = load_data_integrated()

if isinstance(result[0], str): # 에러 메시지인 경우
    st.error(result[0])
    st.info("💡 팁: 구글 시트 '웹에 게시' 설정에서 형식을 'Microsoft Excel(.xlsx)'로 선택해야 시트 2개를 모두 읽을 수 있습니다.")
    st.stop()

df_summary, df_detail = result

st.title("🏭 공장 예산 통합 관리 시스템")
st.markdown("기준정보(Plan)와 지출내역(Actual)을 실시간으로 비교 분석합니다.")

# [상단 요약]
total_budget = df_summary['총예산'].sum()
total_spent = df_summary['총지출'].sum()
total_remain = df_summary['잔액'].sum()
total_rate = (total_spent / total_budget * 100) if total_budget > 0 else 0

c1, c2, c3 = st.columns(3)
c1.metric("총 예산 (기본+추가)", f"{total_budget:,.0f}원")
c2.metric("총 지출액 (실시간)", f"{total_spent:,.0f}원", f"{total_rate:.1f}%")
c3.metric("총 잔액", f"{total_remain:,.0f}원")

st.divider()

# [메인: 팀별 현황 카드]
st.subheader("👥 팀별 예산 집행 현황")
cols = st.columns(3)
for i, row in df_summary.iterrows():
    with cols[i % 3]:
        with st.container(border=True):
            status = "🟢"
            if row['집행률'] >= 100: status = "🔴"
            elif row['집행률'] >= 80: status = "🟡"
            
            st.write(f"### {status} {row['팀명']}")
            st.progress(min(row['집행률']/100, 1.0))
            
            c_a, c_b = st.columns(2)
            c_a.caption("총 예산")
            c_a.write(f"{row['총예산']:,.0f}")
            c_b.caption("현재 지출")
            c_b.write(f"{row['총지출']:,.0f}")
            
            st.markdown(f"**잔액: {row['잔액']:,.0f}원** ({row['집행률']:.1f}%)")

st.divider()

# [하단: 상세 분석]
tab1, tab2 = st.tabs(["📊 월별 누계 관리표", "📝 상세 지출 내역"])

with tab1:
    st.dataframe(
        df_summary.style.format({
            '총예산': '{:,.0f}', '총지출': '{:,.0f}', '잔액': '{:,.0f}', '집행률': '{:.1f}%'
        }).background_gradient(subset=['집행률'], cmap='OrRd'),
        use_container_width=True
    )

with tab2:
    st.caption("최근 지출 내역 (지출내역 시트 데이터)")
    # 날짜 기준 내림차순 정렬 (날짜 컬럼이 있다고 가정)
    if '날짜' in df_detail.columns:
        df_detail['날짜'] = pd.to_datetime(df_detail['날짜'], errors='coerce')
        df_detail = df_detail.sort_values('날짜', ascending=False)
        df_detail['날짜'] = df_detail['날짜'].dt.strftime('%Y-%m-%d') # 보기 좋게 포맷팅
    
    st.dataframe(df_detail, use_container_width=True)

# [AI 분석]
with st.expander("🤖 Gemini AI 경영 리포트 생성"):
    if st.button("예산 vs 실적 분석 실행"):
        with st.spinner("데이터 병합 분석 중..."):
            prompt = f"""
            너는 공장 재무 담당자야.
            기준정보(예산)와 지출내역(실적)을 비교한 데이터야.
            
            [데이터 요약]
            {df_summary.to_string()}
            
            1. 예산 대비 초과 지출이 발생한(또는 임박한) 팀을 지목해줘.
            2. 현재 공장의 자금 소진 속도가 적절한지 평가해줘.
            """
            response = model.generate_content(prompt)
            st.markdown(response.text)
