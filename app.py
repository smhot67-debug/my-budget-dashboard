import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. 페이지 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="공장 예산관리 프로",
    page_icon="🏭",
    layout="wide"
)

# 구글 시트 주소 (엑셀 형식)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6hnNtH_1tBFJoA25lXzFPjKUGpBfu0H313_QVFDPdHOpWDDQSJQvIlOQpUoczNO7z7jyWbE171ApD/pub?output=xlsx"

# -----------------------------------------------------------------------------
# 2. 데이터 로드 함수 (오류 수정됨)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=60)
def load_data_visual():
    try:
        # 엑셀 파일 로드
        sheets = pd.read_excel(SHEET_URL, sheet_name=None)
        
        # 시트 찾기
        budget_sheet = next((s for s in sheets.keys() if '기준' in s or 'Budget' in s), None)
        expense_sheet = next((s for s in sheets.keys() if '지출' in s or 'Expense' in s), None)
        
        if not budget_sheet or not expense_sheet:
            return False, "시트 이름 오류: '기준정보'와 '지출내역' 시트가 필요합니다.", None

        # [A] 기준정보 (예산)
        df_budget = sheets[budget_sheet].fillna(0)
        # 숫자 정제
        for col in df_budget.columns:
            if col != '팀명':
                df_budget[col] = pd.to_numeric(df_budget[col], errors='coerce').fillna(0)
        
        # 총 예산 계산
        df_budget['총예산'] = df_budget.iloc[:, 1:].sum(axis=1)
        df_base = df_budget[['팀명', '총예산']]

        # [B] 지출내역
        df_expense = sheets[expense_sheet].fillna(0)
        
        # 날짜 컬럼 처리
        date_col = next((c for c in df_expense.columns if '날짜' in c or 'Date' in c), None)
        if date_col:
            df_expense[date_col] = pd.to_datetime(df_expense[date_col], errors='coerce')
            df_expense['월'] = df_expense[date_col].dt.strftime('%Y-%m')
        else:
            df_expense['월'] = '날짜없음'

        if '금액' in df_expense.columns:
            df_expense['금액'] = pd.to_numeric(df_expense['금액'], errors='coerce').fillna(0)

        return True, df_base, df_expense

    except Exception as e:
        return False, str(e), None

# -----------------------------------------------------------------------------
# 3. UI 렌더링
# -----------------------------------------------------------------------------
status, data1, data2 = load_data_visual()

if not status:
    st.error(f"데이터 로드 실패: {data1}")
    st.stop()

df_base = data1     # 팀별 예산 기준정보
df_expense = data2  # 전체 지출 내역

# --- [사이드바 필터] ---
with st.sidebar:
    st.header("🔍 조회 조건 설정")
    
    # 1. 월 선택
    month_list = sorted([m for m in df_expense['월'].unique() if m != '날짜없음'])
    period_option = st.selectbox("📅 조회 기간", ["전체 누적"] + month_list, index=0)
    
    # 2. 팀 선택
    team_list = sorted(df_base['팀명'].unique())
    team_option = st.selectbox("🏢 부서 선택", ["전체 부서"] + team_list, index=0)
    
    st.divider()
    st.info("💡 '전체 누적' 선택 시 연간 총 예산 대비 사용량을 보여줍니다.")

# --- [데이터 필터링] ---
# 1. 기간 필터
if period_option == "전체 누적":
    df_filtered_exp = df_expense
    period_label = "전체 기간"
else:
    df_filtered_exp = df_expense[df_expense['월'] == period_option]
    period_label = f"{period_option} 월간"

# 2. 팀 필터 (지출내역용)
if team_option != "전체 부서":
    df_filtered_exp_detail = df_filtered_exp[df_filtered_exp['팀명'] == team_option]
    # 기준정보도 해당 팀만 남김
    df_base_filtered = df_base[df_base['팀명'] == team_option]
else:
    df_filtered_exp_detail = df_filtered_exp
    df_base_filtered = df_base

# 3. 데이터 합산 (대시보드용)
exp_summary = df_filtered_exp.groupby('팀명')['금액'].sum().reset_index().rename(columns={'금액': '사용액'})
df_main = pd.merge(df_base_filtered, exp_summary, on='팀명', how='left').fillna(0)

# 지표 계산
df_main['잔액'] = df_main['총예산'] - df_main['사용액']
df_main['집행률'] = df_main.apply(lambda x: (x['사용액'] / x['총예산'] * 100) if x['총예산'] > 0 else 0, axis=1)

# --- [메인 화면] ---
st.title(f"📊 공장 예산 집행 현황")
st.markdown(f"**{period_label}** 기준 / **{team_option}** 조회 결과입니다.")

# [1. KPI 요약 카드]
total_budget = df_main['총예산'].sum()
total_spent = df_main['사용액'].sum()
total_remain = df_main['잔액'].sum()
avg_rate = (total_spent / total_budget * 100) if total_budget > 0 else 0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("총 배정 예산", f"{total_budget:,.0f}원")
kpi2.metric(f"현재 사용액 ({period_label})", f"{total_spent:,.0f}원", f"{avg_rate:.1f}%")
kpi3.metric("현재 잔액", f"{total_remain:,.0f}원")
kpi4.metric("지출 건수", f"{len(df_filtered_exp_detail):,}건")

st.divider()

# [2. 시각화 차트 영역]
c1, c2 = st.columns([6, 4])

with c1:
    st.subheader("📈 팀별 예산 vs 사용액 비교")
    if not df_main.empty:
        # 막대 그래프 (Budget vs Actual)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_main['팀명'], y=df_main['총예산'],
            name='배정예산', marker_color='#e2e8f0'
        ))
        fig.add_trace(go.Bar(
            x=df_main['팀명'], y=df_main['사용액'],
            name='사용액', marker_color='#3b82f6',
            text=df_main['집행률'].apply(lambda x: f'{x:.1f}%'),
            textposition='auto'
        ))
        fig.update_layout(barmode='group', margin=dict(t=0, b=0, l=0, r=0), height=350)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("표시할 데이터가 없습니다.")

with c2:
    st.subheader(f"💰 {period_label} 지출 비중")
    if total_spent > 0:
        fig_pie = px.pie(df_main, values='사용액', names='팀명', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=350)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("지출 내역이 없어 차트를 표시할 수 없습니다.")

st.divider()

# [3. 상세 내역 (카드뷰 & 테이블)]
tab_card, tab_table = st.tabs(["🗂️ 팀별 현황 카드", "📝 상세 지출 내역서"])

with tab_card:
    # 3열 카드 배치
    rows = st.columns(3)
    for i, row in df_main.reset_index().iterrows():
        with rows[i % 3]:
            with st.container(border=True):
                # 아이콘 상태 로직
                state_icon = "🟢"
                bar_color = "blue"
                if row['집행률'] >= 80: 
                    state_icon = "⚠️"
                    bar_color = "orange"
                if row['집행률'] >= 100: 
                    state_icon = "🚨"
                    bar_color = "red"
                
                st.markdown(f"#### {state_icon} {row['팀명']}")
                st.progress(min(row['집행률']/100, 1.0))
                
                c_left, c_right = st.columns(2)
                with c_left:
                    st.caption("예산")
                    st.write(f"**{row['총예산']:,.0f}**")
                with c_right:
                    st.caption("사용")
                    st.write(f"**{row['사용액']:,.0f}**")
                
                st.markdown("---")
                st.markdown(f"**잔액: {row['잔액']:,.0f}원**")

with tab_table:
    st.markdown(f"##### 📑 {team_option} - {period_label} 지출 상세")
    
    if not df_filtered_exp_detail.empty:
        # 보기 좋은 컬럼만 선택
        display_cols = [c for c in ['날짜', '팀명', '대분류', '소분류', '상세내역', '금액'] if c in df_filtered_exp_detail.columns]
        
        st.dataframe(
            df_filtered_exp_detail[display_cols]
            .sort_values('날짜', ascending=False)
            .style.format({'금액': '{:,.0f}원', '날짜': '{:%Y-%m-%d}'}),
            use_container_width=True,
            height=400
        )
    else:
        st.warning("해당 조건의 상세 지출 내역이 없습니다.")
