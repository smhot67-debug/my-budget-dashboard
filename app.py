import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# -----------------------------------------------------------------------------
# 1. 통합 시스템 설정 & 디자인
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="통합 관리 시스템",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# [CSS] 프리미엄 UI 디자인 (공통)
st.markdown("""
    <style>
        /* 폰트 및 기본 스타일 */
        html, body, p, div, span, label, li, h1, h2, h3, h4, h5, h6 {
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif !important;
        }
        .stApp { background-color: #f8f9fa; }
        
        /* 카드 디자인 */
        div.css-1r6slb0, div.stDataFrame, div[data-testid="stMetric"] {
            background-color: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            border: 1px solid #e2e8f0;
        }
        
        /* 메트릭 값 강조 */
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
            font-weight: 800 !important;
            color: #1e293b;
        }
        
        /* 진행바 커스텀 */
        .stProgress > div > div > div > div {
            background-image: linear-gradient(to right, #3b82f6, #60a5fa);
        }
        
        /* 합계 박스 스타일 */
        .summary-box {
            background-color: #eff6ff;
            border-left: 5px solid #3b82f6;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            color: #1e3a8a;
        }
        
        /* 테이블 헤더 */
        th { color: #475569 !important; font-weight: 700 !important; background-color: #f1f5f9 !important; }
    </style>
""", unsafe_allow_html=True)

# 구글 시트 주소 (엑셀 형식)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6hnNtH_1tBFJoA25lXzFPjKUGpBfu0H313_QVFDPdHOpWDDQSJQvIlOQpUoczNO7z7jyWbE171ApD/pub?output=xlsx"

# -----------------------------------------------------------------------------
# 2. 데이터 로드 엔진
# -----------------------------------------------------------------------------
@st.cache_data(ttl=60)
def load_all_data():
    try:
        sheets = pd.read_excel(SHEET_URL, sheet_name=None)
        return sheets
    except Exception as e:
        return None

# 데이터 정제 함수 (부서명 숫자 제거 등)
def clean_dept_name(name):
    if pd.isna(name): return ""
    # "1. 지원팀", "02 생산" 등 앞의 숫자와 특수문자 제거
    return re.sub(r'^[\d\.\s]+', '', str(name))

all_sheets = load_all_data()

if not all_sheets:
    st.error("데이터를 불러올 수 없습니다. 구글 시트 연결을 확인해주세요.")
    st.stop()

# 시트 매핑
budget_sheet_name = next((s for s in all_sheets.keys() if '기준' in s or 'Budget' in s), None)
expense_sheet_name = next((s for s in all_sheets.keys() if '지출' in s or 'Expense' in s), None)
leave_sheet_name = next((s for s in all_sheets.keys() if '원천' in s or 'Leave' in s), None)

# -----------------------------------------------------------------------------
# 3. 메인 UI 및 로직
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("통합 관리 시스템")
    st.markdown("---")
    menu = st.radio("업무 선택", ["💰 예산 관리", "🏖️ 연차 관리"])
    st.markdown("---")

# =============================================================================
# [PART A] 예산 관리
# =============================================================================
if menu == "💰 예산 관리":
    if not budget_sheet_name or not expense_sheet_name:
        st.error("예산 관련 시트가 없습니다.")
        st.stop()

    # 데이터 로드
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

    # 분류 컬럼 확보 (없으면 생성)
    if '대분류' not in df_expense.columns: df_expense['대분류'] = '-'
    if '소분류' not in df_expense.columns: df_expense['소분류'] = '-'
    df_expense['대분류'] = df_expense['대분류'].astype(str)
    df_expense['소분류'] = df_expense['소분류'].astype(str)

    # --- 필터 ---
    with st.sidebar:
        st.subheader("예산 필터")
        month_list = sorted([m for m in df_expense['월'].unique() if m != '날짜없음'], reverse=True)
        period_option = st.selectbox("기간", ["전체 누적"] + month_list)
        team_list = sorted(df_base['팀명'].unique())
        team_option = st.selectbox("부서", ["전체 부서"] + team_list)
        
        # 상세 분류 콤보박스 (대분류 -> 소분류 연동)
        st.markdown("##### 항목 필터")
        main_cats = ["전체"] + sorted(df_expense['대분류'].unique())
        cat_main = st.selectbox("대분류", main_cats)
        
        sub_cats = ["전체"]
        if cat_main != "전체":
            sub_cats += sorted(df_expense[df_expense['대분류'] == cat_main]['소분류'].unique())
        else:
            sub_cats += sorted(df_expense['소분류'].unique())
        cat_sub = st.selectbox("소분류", sub_cats)

    # 필터링 로직
    df_filtered = df_expense.copy()
    period_label = "전체 기간"
    if period_option != "전체 누적":
        df_filtered = df_filtered[df_filtered['월'] == period_option]
        period_label = f"{period_option}"
    
    if cat_main != "전체": df_filtered = df_filtered[df_filtered['대분류'] == cat_main]
    if cat_sub != "전체": df_filtered = df_filtered[df_filtered['소분류'] == cat_sub]

    exp_summary = df_filtered.groupby('팀명')['금액'].sum().reset_index().rename(columns={'금액': '사용액'})
    
    if team_option != "전체 부서":
        df_base = df_base[df_base['팀명'] == team_option]
        df_filtered = df_filtered[df_filtered['팀명'] == team_option]

    df_dash = pd.merge(df_base, exp_summary, on='팀명', how='left').fillna(0)
    df_dash['잔액'] = df_dash['총예산'] - df_dash['사용액']
    df_dash['집행률'] = df_dash.apply(lambda x: (x['사용액'] / x['총예산'] * 100) if x['총예산'] > 0 else 0, axis=1)
    
    # 예산, 사용액 둘 다 0이면 숨김 (단, 필터 없을 때)
    if cat_main == "전체" and cat_sub == "전체":
        df_dash = df_dash[~((df_dash['총예산'] == 0) & (df_dash['사용액'] == 0))]

    # --- UI ---
    st.title("💰 예산 관리 대시보드")
    st.markdown(f"**{team_option}** / **{period_label}**")
    
    # KPI
    tot_b, tot_s, tot_r = df_dash['총예산'].sum(), df_dash['사용액'].sum(), df_dash['잔액'].sum()
    avg_r = (tot_s / tot_b * 100) if tot_b > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총 배정 예산", f"{tot_b:,.0f}원")
    c2.metric("총 지출액", f"{tot_s:,.0f}원", f"{avg_r:.1f}%")
    c3.metric("현재 잔액", f"{tot_r:,.0f}원")
    c4.metric("지출 건수", f"{len(df_filtered):,}건")

    st.divider()

    col_chart, col_list = st.columns([4, 6])
    with col_chart:
        st.subheader("📊 예산 집행률")
        if not df_dash.empty:
            fig = px.pie(df_dash, values='사용액', names='팀명', hole=0.6, color_discrete_sequence=px.colors.qualitative.Prism)
            fig.update_layout(showlegend=True, height=400, margin=dict(t=20, b=20, l=20, r=20))
            fig.add_annotation(text=f"{int(avg_r)}%", x=0.5, y=0.5, font_size=24, showarrow=False, font_weight="bold")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("데이터 없음")

    with col_list:
        st.subheader("🏢 팀별 현황")
        if not df_dash.empty:
            with st.container(height=400):
                for i, row in df_dash.iterrows():
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

    st.subheader("📝 상세 지출 내역")
    
    # 합계 바 (상용화 UI 스타일)
    st.markdown(f"""
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 15px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 10px;">
            <span style="font-weight: bold; color: #475569;">🧾 지출 내역 합계</span>
            <span style="font-size: 1.2rem; font-weight: 800; color: #2563eb;">{df_filtered['금액'].sum():,.0f} 원</span>
        </div>
    """, unsafe_allow_html=True)

    if not df_filtered.empty:
        # 컬럼 순서 및 포맷 정의
        cols_show = [c for c in ['날짜', '팀명', '대분류', '소분류', '상세내역', '금액'] if c in df_filtered.columns]
        
        st.dataframe(
            df_filtered[cols_show].sort_values('날짜', ascending=False),
            column_config={
                "날짜": st.column_config.DateColumn("일자", format="YYYY-MM-DD", width="small"),
                "팀명": st.column_config.TextColumn("부서", width="small"),
                "대분류": st.column_config.TextColumn("대분류", width="small"),
                "소분류": st.column_config.TextColumn("소분류", width="small"),
                "상세내역": st.column_config.TextColumn("적요", width="large"),
                "금액": st.column_config.NumberColumn("금액", format="%d원") # 콤마 포맷
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("해당 조건의 지출 내역이 없습니다.")

# =============================================================================
# [PART B] 연차 관리
# =============================================================================
elif menu == "🏖️ 연차 관리":
    if not leave_sheet_name:
        st.error("연차 데이터 시트('원천' 또는 'Leave' 포함)가 없습니다.")
        st.stop()

    # 데이터 로드 및 전처리
    df_leave = all_sheets[leave_sheet_name].fillna(0)
    
    # 1. 소속명 정제 (숫자 제거)
    df_leave['소속'] = df_leave['소속'].apply(clean_dept_name)

    # 2. 숫자형 변환
    numeric_cols = ['합계', '사용일수', '잔여일수', '부채예산', '부채잔액']
    for col in numeric_cols:
        if col in df_leave.columns:
            df_leave[col] = pd.to_numeric(df_leave[col], errors='coerce').fillna(0)

    # 전체 KPI
    avg_usage_rate = (df_leave['사용일수'].sum() / df_leave['합계'].sum() * 100) if df_leave['합계'].sum() > 0 else 0
    total_liability = df_leave['부채잔액'].sum() if '부채잔액' in df_leave.columns else (df_leave['잔여일수'].sum() * 100000)
    
    # 필터
    with st.sidebar:
        st.subheader("연차 필터")
        dept_list = ["전체"] + sorted(df_leave['소속'].unique())
        leave_dept_option = st.selectbox("소속 부서", dept_list)
        risk_criteria = st.slider("촉진 대상 기준 (잔여일)", 5, 25, 10)

    if leave_dept_option != "전체":
        df_leave = df_leave[df_leave['소속'] == leave_dept_option]

    # 리스크 그룹 (필터 적용 후)
    df_risk_final = df_leave[df_leave['잔여일수'] >= risk_criteria].sort_values('잔여일수', ascending=False)

    # UI 시작
    st.title("🏖️ 연차 관리 대시보드")
    st.markdown(f"**FY 2026** 임직원 휴가 및 부채 현황")
    
    # 1. KPI Cards
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("전사 소진율", f"{avg_usage_rate:.1f}%", delta="목표 60%")
    k2.metric("미사용 연차 부채", f"{total_liability/100000000:.2f}억", "예상 비용", delta_color="inverse")
    k3.metric("촉진 대상자", f"{len(df_risk_final)}명", f"잔여 {risk_criteria}일↑", delta_color="inverse")
    k4.metric("평균 잔여일수", f"{df_leave['잔여일수'].mean():.1f}일")

    st.divider()

    # 2. Charts & Risk Table
    c_chart, c_risk = st.columns([4, 6])
    
    with c_chart:
        st.subheader("📊 부서별 소진율")
        dept_summary = df_leave.groupby('소속').agg({'사용일수':'sum', '합계':'sum'}).reset_index()
        dept_summary['소진율'] = (dept_summary['사용일수'] / dept_summary['합계'] * 100).fillna(0)
        
        fig = px.bar(dept_summary, x='소속', y='소진율', text=dept_summary['소진율'].apply(lambda x: f"{x:.1f}%"),
                     color='소진율', color_continuous_scale='Bluyl')
        fig.update_layout(xaxis_title=None, yaxis_title="소진율(%)", height=380)
        st.plotly_chart(fig, use_container_width=True)

    with c_risk:
        st.subheader(f"🚨 촉진 대상자 (잔여 {risk_criteria}일 이상)")
        
        # [요청 기능] 촉진 대상자 요약 통계 수식
        if not df_risk_final.empty:
            r_total = df_risk_final['합계'].sum()
            r_used = df_risk_final['사용일수'].sum()
            r_rem = df_risk_final['잔여일수'].sum()
            r_rate = (r_used / r_total * 100) if r_total > 0 else 0
            
            # 요약 박스
            st.markdown(f"""
                <div class="summary-box" style="display: flex; justify-content: space-around; text-align: center;">
                    <div><span style="font-size:0.8rem; color:#64748b;">대상자 연차총계</span><br><strong>{r_total:,.1f}</strong></div>
                    <div><span style="font-size:0.8rem; color:#64748b;">사용총계</span><br><strong>{r_used:,.1f}</strong></div>
                    <div><span style="font-size:0.8rem; color:#ef4444;">잔여총계</span><br><strong style="color:#ef4444;">{r_rem:,.1f}</strong></div>
                    <div><span style="font-size:0.8rem; color:#64748b;">그룹 소진율</span><br><strong>{r_rate:.1f}%</strong></div>
                </div>
            """, unsafe_allow_html=True)

            st.dataframe(
                df_risk_final[['소속', '성명', '잔여일수', '사용일수', '합계']],
                use_container_width=True,
                height=300,
                column_config={
                    "소속": st.column_config.TextColumn("부서"),
                    "잔여일수": st.column_config.NumberColumn("잔여", format="%.1f일"),
                    "사용일수": st.column_config.NumberColumn("사용", format="%.1f일"),
                    "합계": st.column_config.NumberColumn("총 연차", format="%.1f일")
                },
                hide_index=True
            )
        else:
            st.success("해당 조건의 촉진 대상자가 없습니다.")

    # 3. 전체 임직원 명부 (상용화 UI)
    st.divider()
    st.subheader("👥 전체 임직원 현황")
    
    st.dataframe(
        df_leave[['소속', '성명', '합계', '사용일수', '잔여일수', '부채잔액']],
        use_container_width=True,
        column_config={
            "소속": st.column_config.TextColumn("부서", width="small"),
            "성명": st.column_config.TextColumn("이름", width="small"),
            "합계": st.column_config.NumberColumn("총 연차", format="%.1f일"),
            "사용일수": st.column_config.ProgressColumn("사용 현황", format="%.1f일", min_value=0, max_value=25),
            "잔여일수": st.column_config.NumberColumn("잔여", format="%.1f일"),
            "부채잔액": st.column_config.NumberColumn("예상 부채", format="%d원") # 콤마 포맷
        },
        hide_index=True
    )
