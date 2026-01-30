import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# 1. 환경 설정
st.set_page_config(page_title="공장 예산관리 통합 시스템", layout="wide")

# API 키 및 구글 시트 주소 (엑셀 형식)
API_KEY = "AIzaSyAkhIIHXg2XJSBHfrkhxGP_0iW1KZZJlZc"
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6hnNtH_1tBFJoA25lXzFPjKUGpBfu0H313_QVFDPdHOpWDDQSJQvIlOQpUoczNO7z7jyWbE171ApD/pub?output=xlsx"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. 데이터 로드 및 전처리
@st.cache_data(ttl=60)
def load_data_pro():
    try:
        sheets = pd.read_excel(SHEET_URL, sheet_name=None)
        
        # 시트 이름 자동 찾기
        budget_sheet = next((s for s in sheets.keys() if '기준' in s or 'Budget' in s), None)
        expense_sheet = next((s for s in sheets.keys() if '지출' in s or 'Expense' in s), None)
        
        if not budget_sheet or not expense_sheet:
            return "Err", "시트 이름을 찾을 수 없습니다. (기준정보/지출내역 시트 필요)"

        # [A] 예산 데이터 (기준정보)
        df_budget = sheets[budget_sheet].fillna(0)
        # 숫자 정제
        for col in df_budget.columns:
            if col != '팀명':
                df_budget[col] = pd.to_numeric(df_budget[col], errors='coerce').fillna(0)
        
        # 총 예산 계산
        df_budget['총예산'] = df_budget.iloc[:, 1:].sum(axis=1)
        df_base = df_budget[['팀명', '총예산']]

        # [B] 지출 데이터 (지출내역)
        df_expense = sheets[expense_sheet].fillna(0)
        
        # 날짜 컬럼 처리 (필터링을 위해 필수)
        date_col = next((c for c in df_expense.columns if '날짜' in c or 'Date' in c), None)
        if date_col:
            df_expense[date_col] = pd.to_datetime(df_expense[date_col], errors='coerce')
            # '월(Month)' 컬럼 생성 (예: 2026-01)
            df_expense['조회월'] = df_expense[date_col].dt.strftime('%Y-%m')
        else:
            df_expense['조회월'] = '날짜없음'

        if '금액' in df_expense.columns:
            df_expense['금액'] = pd.to_numeric(df_expense['금액'], errors='coerce').fillna(0)

        return df_base, df_expense

    except Exception as e:
        return "Err", str(e)

# 3. UI 렌더링
result = load_data_pro()

if result[0] == "Err":
    st.error(f"데이터 오류: {result[1]}")
    st.stop()

df_budget_base, df_expense_all = result

# --- [사이드바 컨트롤] ---
# 여기서 월을 선택하면 전체 대시보드가 바뀝니다.
st.sidebar.header("🔍 조회 필터")

# 1. 월 선택 콤보박스 (데이터에 있는 월만 추출)
available_months = sorted(list(set(df_expense_all['조회월'].dropna())))
if '날짜없음' in available_months: available_months.remove('날짜없음')

# '전체 누적'을 기본으로 추가
month_options = ["전체 누적"] + available_months
selected_month = st.sidebar.selectbox("📅 조회 기간 (월)", month_options)

# 2. 팀 선택 콤보박스
team_options = ["전체 팀"] + list(df_budget_base['팀명'].unique())
selected_team = st.sidebar.selectbox("🏢 부서 선택", team_options)


# --- [데이터 필터링 로직] ---
# 선택한 월에 해당하는 지출 데이터만 걸러냄
if selected_month == "전체 누적":
    filtered_expense = df_expense_all
    period_title = "전체 누적"
else:
    filtered_expense = df_expense_all[df_expense_all['조회월'] == selected_month]
    period_title = f"{selected_month} 월간"

# 선택한 팀에 해당하는 데이터만 걸러냄 (지출내역용)
if selected_team != "전체 팀":
    filtered_expense_detail = filtered_expense[filtered_expense['팀명'] == selected_team]
else:
    filtered_expense_detail = filtered_expense

# --- [통합 데이터 재계산] ---
# 필터링된 지출 데이터를 팀별로 다시 합산
expense_sum = filtered_expense.groupby('팀명')['금액'].sum().reset_index()
expense_sum.rename(columns={'금액': '기간지출'}, inplace=True)

# 예산 정보와 합치기
df_dashboard = pd.merge(df_budget_base, expense_sum, on='팀명', how='left').fillna(0)

# 잔액 및 집행률 계산
# 주의: '전체 누적'이 아닐 때도 '연간 총예산' 대비 '해당 월 지출' 비율을 보여줄지 고민 필요
# 여기서는 (연간 총예산) - (선택 기간 지출) = (기간 잔액) 개념으로 보여줍니다.
df_dashboard['잔액'] = df_dashboard['총예산'] - df_dashboard['기간지출']
df_dashboard['집행률'] = df_dashboard.apply(lambda x: (x['기간지출'] / x['총예산'] * 100) if x['총예산'] > 0 else 0, axis=1)

# 선택한 팀만 대시보드에 보여주기 (옵션)
if selected_team != "전체 팀":
    df_dashboard = df_dashboard[df_dashboard['팀명'] == selected_team]


# --- [메인 화면 구성] ---
st.title(f"🏭 공장 예산 집행 현황 ({period_title})")
st.markdown("좌측 사이드바(화살표)를 눌러 **월별/팀별 조회 조건**을 변경할 수 있습니다.")

# [상단 요약]
total_b = df_dashboard['총예산'].sum()
total_s = df_dashboard['기간지출'].sum()
total_r = df_dashboard['잔액'].sum()
avg_rate = (total_s / total_b * 100) if total_b > 0 else 0

c1, c2, c3 = st.columns(3)
c1.metric("총 예산 (연간)", f"{total_b:,.0f}원")
c2.metric(f"{period_title} 집행액", f"{total_s:,.0f}원", f"{avg_rate:.1f}% 사용")
c3.metric("현재 잔액", f"{total_r:,.0f}원")

st.divider()

# [팀별 카드 뷰]
st.subheader(f"👥 {period_title} 팀별 집행 현황")

# 카드 그리드 (3열)
rows = st.columns(3)
for i, row in df_dashboard.reset_index().iterrows():
    with rows[i % 3]:
        with st.container(border=True):
            # 상태 아이콘 (월별 조회 시 기준을 좀 낮게 잡을 수도 있지만, 일단 통일)
            icon = "🟢"
            if row['집행률'] >= 80: icon = "⚠️" 
            if row['집행률'] >= 100: icon = "🚨"
            
            st.markdown(f"### {icon} {row['팀명']}")
            st.write(f"**집행률: {row['집행률']:.1f}%**")
            st.progress(min(row['집행률']/100, 1.0))
            
            c_a, c_b = st.columns(2)
            c_a.caption("연간 예산")
            c_a.write(f"{row['총예산']:,.0f}")
            c_b.caption(f"{period_title} 지출")
            c_b.write(f"**{row['기간지출']:,.0f}**")

st.divider()

# [하단 상세 내역]
st.subheader("📝 상세 지출 내역 (필터 적용됨)")

# 컬럼 순서 정리 및 포맷팅
if not filtered_expense_detail.empty:
    # 보기 좋은 컬럼 순서
    cols_to_show = [c for c in ['날짜', '팀명', '대분류', '소분류', '상세내역', '금액'] if c in filtered_expense_detail.columns]
    
    st.dataframe(
        filtered_expense_detail[cols_to_show]
        .sort_values('날짜', ascending=False)
        .style.format({'금액': '{:,.0f}원'}),
        use_container_width=True
    )
else:
    st.info("해당 조건의 지출 내역이 없습니다.")
