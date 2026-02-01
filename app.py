import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. 통합 시스템 설정 & 디자인
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Factory ERP System",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# [CSS] 프리미엄 UI 디자인 (예산/연차 공통 적용)
st.markdown("""
    <style>
        /* 기본 폰트 설정 */
        html, body, p, div, span, label, li, h1, h2, h3, h4, h5, h6 {
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif !important;
        }
        
        /* 앱 배경 */
        .stApp { background-color: #f1f5f9; }
        
        /* 카드 디자인 (공통) */
        div.css-1r6slb0, div.stDataFrame, div[data-testid="stMetric"] {
            background-color: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            border: 1px solid #e2e8f0;
        }
        
        /* 탭 디자인 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: transparent;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            padding: 0 20px;
            font-weight: 700;
            border: 1px solid #e2e8f0;
        }
        .stTabs [aria-selected="true"] {
            background-color: #2563eb !important;
            color: white !important;
            border-color: #2563eb !important;
        }
        
        /* 메트릭 값 디자인 */
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
            font-weight: 800 !important;
        }
        
        /* 진행바 스타일 */
        .stProgress > div > div > div > div {
            background-image: linear-gradient(to right, #3b82f6, #60a5fa);
        }
    </style>
""", unsafe_allow_html=True)

# 구글 시트 주소 (엑셀 형식)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6hnNtH_1tBFJoA25lXzFPjKUGpBfu0H313_QVFDPdHOpWDDQSJQvIlOQpUoczNO7z7jyWbE171ApD/pub?output=xlsx"

# -----------------------------------------------------------------------------
# 2. 데이터 로드 엔진 (예산 & 연차 통합)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=60)
def load_all_data():
    try:
        sheets = pd.read_excel(SHEET_URL, sheet_name=None)
        return sheets
    except Exception as e:
        return None

all_sheets = load_all_data()

if not all_sheets:
    st.error("데이터를 불러올 수 없습니다. 구글 시트 연결을 확인해주세요.")
    st.stop()

# 시트 매핑
budget_sheet_name = next((s for s in all_sheets.keys() if '기준' in s or 'Budget' in s), None)
expense_sheet_name = next((s for s in all_sheets.keys() if '지출' in s or 'Expense' in s), None)
leave_sheet_name = next((s for s in all_sheets.keys() if '원천' in s or 'Leave' in s), None) # 연차 데이터 시트

# -----------------------------------------------------------------------------
# 3. 메인 UI 구조 (사이드바 메뉴)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("🏭 Factory ERP")
    st.caption(f"통합 관리 시스템 v3.0")
    st.markdown("---")
    
    # [메뉴 선택] 탭 대신 사이드바 메뉴로 깔끔하게 분리
    menu = st.radio(
        "업무 선택",
        ["💰 예산 관리", "🏖️ 연차 관리"],
        captions=["팀별 예산 및 비용 통제", "연차 소진율 및 부채 관리"]
    )
    st.markdown("---")

# =============================================================================
# [PART A] 예산 관리 모듈
# =============================================================================
if menu == "💰 예산 관리":
    if not budget_sheet_name or not expense_sheet_name:
        st.error("예산 관련 시트('기준정보', '지출내역')가 없습니다.")
        st.stop()

    # --- [예산 데이터 처리] ---
    df_budget = all_sheets[budget_sheet_name].fillna(0)
    for col in df_budget.columns:
        if col != '팀명': df_budget[col] = pd.to_numeric(df_budget[col], errors='coerce').fillna(0)
    df_budget['총예산'] = df_budget.iloc[:, 1:].sum(axis=1)
    df_base = df_budget[['팀명', '총예산']]

    df_expense = all_sheets[expense_sheet_name].fillna(0)
    date_col = next((c for c in df_expense.columns if '날짜' in c or 'Date' in c), None)
    if date_col:
        df_expense[date_col] = pd.to_datetime(df_expense[date_col], errors='coerce')
        df_expense['월'] = df_expense[date_col].dt.strftime('%Y-%m')
        df_expense['날짜'] = df_expense[date_col]
    else:
        df_expense['월'] = '날짜없음'
    if '금액' in df_expense.columns:
        df_expense['금액'] = pd.to_numeric(df_expense['금액'], errors='coerce').fillna(0)
    df_expense = df_expense[df_expense['금액'] != 0]

    # --- [사이드바 필터] ---
    with st.sidebar:
        st.subheader("검색 조건")
        month_list = sorted([m for m in df_expense['월'].unique() if m != '날짜없음'], reverse=True)
        period_option = st.selectbox("기간", ["전체 누적"] + month_list)
        team_list = sorted(df_base['팀명'].unique())
        team_option = st.selectbox("부서", ["전체 부서"] + team_list)
        
        # 분류 필터
        if '대분류' in df_expense.columns:
            main_cats = sorted(df_expense['대분류'].astype(str).unique())
            cat_main = st.selectbox("대분류", ["전체"] + main_cats)
        else:
            cat_main = "전체"

    # --- [데이터 필터링 로직] ---
    df_filtered = df_expense.copy()
    period_label = "전체 기간"
    if period_option != "전체 누적":
        df_filtered = df_filtered[df_filtered['월'] == period_option]
        period_label = f"{period_option} 월간"
    
    if cat_main != "전체":
        df_filtered = df_filtered[df_filtered['대분류'].astype(str) == cat_main]

    # 팀별 합계 계산 및 병합
    exp_summary = df_filtered.groupby('팀명')['금액'].sum().reset_index().rename(columns={'금액': '사용액'})
    
    if team_option != "전체 부서":
        df_base = df_base[df_base['팀명'] == team_option]
        df_filtered = df_filtered[df_filtered['팀명'] == team_option]

    df_dash = pd.merge(df_base, exp_summary, on='팀명', how='left').fillna(0)
    df_dash['잔액'] = df_dash['총예산'] - df_dash['사용액']
    df_dash['집행률'] = df_dash.apply(lambda x: (x['사용액'] / x['총예산'] * 100) if x['총예산'] > 0 else 0, axis=1)
    
    if cat_main == "전체": # 분류 필터 없을 때만 빈 팀 숨김
        df_dash = df_dash[~((df_dash['총예산'] == 0) & (df_dash['사용액'] == 0))]

    # --- [예산 대시보드 UI] ---
    st.title("Budget Dashboard")
    st.markdown(f"**{team_option} / {period_label}** 재무 현황")
    st.markdown("<br>", unsafe_allow_html=True)

    # KPI
    tot_b = df_dash['총예산'].sum()
    tot_s = df_dash['사용액'].sum()
    tot_r = df_dash['잔액'].sum()
    avg_r = (tot_s / tot_b * 100) if tot_b > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총 배정 예산", f"{tot_b:,.0f}", delta="Budget")
    c2.metric("총 지출액", f"{tot_s:,.0f}", f"{avg_r:.1f}%", delta_color="inverse")
    c3.metric("현재 잔액", f"{tot_r:,.0f}", delta="Remain")
    c4.metric("지출 건수", f"{len(df_filtered):,}건")

    st.markdown("---")

    col_chart, col_list = st.columns([4, 6])
    with col_chart:
        st.subheader("📊 예산 집행률")
        if not df_dash.empty:
            fig = px.pie(df_dash, values='사용액', names='팀명', hole=0.6, color_discrete_sequence=px.colors.qualitative.Prism)
            fig.update_layout(showlegend=True, height=400, margin=dict(t=20, b=20, l=20, r=20))
            fig.add_annotation(text=f"Total\n{tot_s/10000:,.0f}만", x=0.5, y=0.5, font_size=20, showarrow=False, font_weight="bold")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("데이터 없음")

    with col_list:
        st.subheader("🏢 팀별 현황")
        if not df_dash.empty:
            for i, row in df_dash.iterrows():
                with st.container():
                    pct = min(row['집행률'], 100)
                    color = "#2563eb" if pct < 80 else ("#d97706" if pct < 100 else "#dc2626")
                    c_a, c_b, c_c = st.columns([3, 4, 3])
                    with c_a:
                        st.markdown(f"**{row['팀명']}**")
                        st.caption(f"예산 {row['총예산']:,.0f}")
                    with c_b:
                        st.progress(pct/100)
                        st.caption(f"지출 {row['사용액']:,.0f} ({row['집행률']:.1f}%)")
                    with c_c:
                        st.markdown(f"<div style='text-align:right; color:{color}; font-weight:bold;'>{row['잔액']:,.0f}</div>", unsafe_allow_html=True)
                    st.divider()
        else:
            st.info("데이터 없음")

    st.subheader("📝 지출 상세 내역")
    st.markdown(f"<div style='background:#f1f5f9; padding:15px; border-radius:10px; text-align:right; font-weight:bold; color:#0f172a;'>💰 총 합계: {df_filtered['금액'].sum():,.0f} 원</div><br>", unsafe_allow_html=True)
    
    if not df_filtered.empty:
        cols_show = [c for c in ['날짜', '팀명', '대분류', '소분류', '상세내역', '금액'] if c in df_filtered.columns]
        st.dataframe(
            df_filtered[cols_show].sort_values('날짜', ascending=False),
            column_config={"금액": st.column_config.NumberColumn(format="%d원"), "날짜": st.column_config.DateColumn(format="YYYY-MM-DD")},
            hide_index=True, use_container_width=True
        )

# =============================================================================
# [PART B] 연차 관리 모듈 (New!)
# =============================================================================
elif menu == "🏖️ 연차 관리":
    if not leave_sheet_name:
        st.error("'원천데이터' 시트가 없습니다. 구글 시트를 확인해주세요.")
        st.stop()

    # --- [연차 데이터 처리] ---
    df_leave = all_sheets[leave_sheet_name].fillna(0)
    
    # 숫자형 변환
    numeric_cols = ['합계', '사용일수', '잔여일수', '부채예산', '부채잔액']
    for col in numeric_cols:
        if col in df_leave.columns:
            df_leave[col] = pd.to_numeric(df_leave[col], errors='coerce').fillna(0)
            
    # KPI 계산
    total_emp = len(df_leave)
    avg_usage_rate = (df_leave['사용일수'].sum() / df_leave['합계'].sum() * 100) if df_leave['합계'].sum() > 0 else 0
    total_liability = df_leave['부채잔액'].sum() if '부채잔액' in df_leave.columns else (df_leave['잔여일수'].sum() * 100000) # 없으면 일당 10만원 가정
    
    # 리스크 그룹 (잔여 10일 이상)
    df_risk = df_leave[df_leave['잔여일수'] >= 10].sort_values('잔여일수', ascending=False)

    # --- [사이드바 필터] ---
    with st.sidebar:
        st.subheader("연차 필터")
        dept_list = ["전체"] + sorted(df_leave['소속'].astype(str).unique())
        leave_dept_option = st.selectbox("소속 부서", dept_list)
        
        risk_criteria = st.slider("촉진 대상 기준 (잔여일)", 5, 20, 10)

    # 데이터 필터링
    if leave_dept_option != "전체":
        df_leave = df_leave[df_leave['소속'] == leave_dept_option]
        df_risk = df_risk[df_risk['소속'] == leave_dept_option]
    
    df_risk_final = df_risk[df_risk['잔여일수'] >= risk_criteria]

    # --- [연차 대시보드 UI] ---
    st.title("Leave Management Dashboard")
    st.markdown(f"**FY 2026** 연차 사용 현황 및 부채 관리")
    st.markdown("<br>", unsafe_allow_html=True)

    # 1. KPI Cards
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("전사 소진율", f"{avg_usage_rate:.1f}%", delta="목표 60%")
    k2.metric("미사용 연차 부채", f"{total_liability/100000000:.2f}억", "예상 비용", delta_color="inverse")
    k3.metric("촉진 대상자", f"{len(df_risk_final)}명", f"잔여 {risk_criteria}일↑", delta_color="inverse")
    k4.metric("평균 잔여일수", f"{df_leave['잔여일수'].mean():.1f}일")

    st.markdown("---")

    # 2. Charts & Risk Table
    c_chart, c_risk = st.columns([1, 1])
    
    with c_chart:
        st.subheader("📊 부서별 연차 소진율")
        # 부서별 집계
        dept_summary = df_leave.groupby('소속').agg({'사용일수':'sum', '합계':'sum'}).reset_index()
        dept_summary['소진율'] = (dept_summary['사용일수'] / dept_summary['합계'] * 100).fillna(0)
        
        fig = px.bar(dept_summary, x='소속', y='소진율', text=dept_summary['소진율'].apply(lambda x: f"{x:.1f}%"),
                     color='소진율', color_continuous_scale='Bluyl')
        fig.update_layout(xaxis_title=None, yaxis_title="소진율(%)", height=400)
        st.plotly_chart(fig, use_container_width=True)

    with c_risk:
        st.subheader(f"🚨 촉진 대상자 (잔여 {risk_criteria}일 이상)")
        if not df_risk_final.empty:
            st.dataframe(
                df_risk_final[['소속', '성명', '잔여일수', '사용일수']].style.background_gradient(subset=['잔여일수'], cmap='Reds'),
                use_container_width=True,
                height=400,
                column_config={
                    "잔여일수": st.column_config.NumberColumn(format="%d일"),
                    "사용일수": st.column_config.NumberColumn(format="%d일")
                }
            )
        else:
            st.success("해당 조건의 촉진 대상자가 없습니다.")

    # 3. 전체 명부
    st.markdown("---")
    st.subheader("👥 전체 임직원 연차 현황")
    st.dataframe(
        df_leave[['소속', '성명', '합계', '사용일수', '잔여일수', '부채잔액']],
        use_container_width=True,
        column_config={
            "합계": st.column_config.NumberColumn("발생 연차", format="%d일"),
            "사용일수": st.column_config.ProgressColumn("사용", format="%d일", min_value=0, max_value=25),
            "잔여일수": st.column_config.NumberColumn(format="%d일"),
            "부채잔액": st.column_config.NumberColumn(format="%d원")
        }
    )
