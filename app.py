import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# -----------------------------------------------------------------------------
# 1. 시스템 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="통합 관리 시스템",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# [CSS] 디자인 (아이콘 깨짐 방지 및 고급 UI)
st.markdown("""
    <style>
        /* 1. 폰트 적용 (아이콘 클래스 제외) */
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        
        html, body, p, div, span, h1, h2, h3, h4, h5, h6, label, button, input, select, textarea {
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
        }
        
        /* Material Icon 등 아이콘 폰트 침범 방지 */
        .material-icons, .material-symbols-rounded, .st-emotion-cache-1pbq7i6, i {
            font-family: 'Material Icons', 'Material Symbols Rounded', sans-serif !important;
        }

        /* 2. 배경 및 컨테이너 */
        .stApp { background-color: #f8f9fa; }
        
        div.css-1r6slb0, div.stDataFrame, div[data-testid="stMetric"] {
            background-color: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            border: 1px solid #e2e8f0;
        }

        /* 3. 메트릭 값 디자인 */
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
            font-weight: 800 !important;
            color: #1e293b;
        }

        /* 4. 합계/요약 박스 스타일 (반응형 수정) */
        .summary-box {
            background-color: #f1f5f9;
            border-left: 5px solid #3b82f6;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(80px, 1fr)); /* 반응형 그리드 */
            gap: 10px;
            text-align: center;
        }
        .summary-item strong {
            display: block;
            font-size: 1.1rem;
            color: #0f172a;
            margin-top: 5px;
        }
        .summary-item span {
            font-size: 0.85rem;
            color: #64748b;
            font-weight: 600;
        }

        /* 5. 카드 리스트 스타일 */
        .card-container {
            background-color: white;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #e2e8f0;
            margin-bottom: 10px;
            transition: transform 0.2s;
        }
        .card-container:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

# 구글 시트 주소
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6hnNtH_1tBFJoA25lXzFPjKUGpBfu0H313_QVFDPdHOpWDDQSJQvIlOQpUoczNO7z7jyWbE171ApD/pub?output=xlsx"

# -----------------------------------------------------------------------------
# 2. 데이터 로드 및 정제 엔진
# -----------------------------------------------------------------------------
@st.cache_data(ttl=60)
def load_all_data():
    try:
        sheets = pd.read_excel(SHEET_URL, sheet_name=None)
        return sheets
    except Exception as e:
        return None

def clean_dept_name(name):
    if pd.isna(name): return ""
    # "1. 지원팀", "02. 생산" 등 앞의 숫자/특수문자/공백 제거
    return re.sub(r'^[\d\.\s]+', '', str(name))

def format_currency(val):
    """금액을 1,000 단위 콤마 문자열로 변환 (정렬용 원본 데이터는 유지)"""
    try:
        return f"{int(val):,}"
    except:
        return "0"

all_sheets = load_all_data()

if not all_sheets:
    st.error("데이터 로드 실패. 구글 시트 연결 상태를 확인해주세요.")
    st.stop()

# 시트 이름 매핑
budget_sheet_name = next((s for s in all_sheets.keys() if '기준' in s or 'Budget' in s), None)
expense_sheet_name = next((s for s in all_sheets.keys() if '지출' in s or 'Expense' in s), None)
leave_sheet_name = next((s for s in all_sheets.keys() if '원천' in s or 'Leave' in s), None)

# -----------------------------------------------------------------------------
# 3. 메인 UI (사이드바)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("통합 관리 시스템")
    st.markdown("---")
    menu = st.radio("업무 모듈", ["💰 예산 관리", "🏖️ 연차 관리"])
    st.markdown("---")

# =============================================================================
# [MODULE A] 예산 관리
# =============================================================================
if menu == "💰 예산 관리":
    if not budget_sheet_name or not expense_sheet_name:
        st.error("필수 시트('기준정보', '지출내역')가 누락되었습니다.")
        st.stop()

    # 1. 데이터 준비
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

    # 분류 컬럼 처리
    if '대분류' not in df_expense.columns: df_expense['대분류'] = '-'
    if '소분류' not in df_expense.columns: df_expense['소분류'] = '-'
    df_expense['대분류'] = df_expense['대분류'].astype(str)
    df_expense['소분류'] = df_expense['소분류'].astype(str)

    # 2. 필터링 UI
    with st.sidebar:
        st.subheader("상세 필터")
        month_list = sorted([m for m in df_expense['월'].unique() if m != '날짜없음'], reverse=True)
        period_option = st.selectbox("기간", ["전체 누적"] + month_list)
        
        team_list = sorted(df_base['팀명'].unique())
        team_option = st.selectbox("부서", ["전체 부서"] + team_list)
        
        st.caption("항목 필터")
        main_cats = ["전체"] + sorted(df_expense['대분류'].unique())
        cat_main = st.selectbox("대분류", main_cats)
        
        sub_cats = ["전체"]
        if cat_main != "전체":
            sub_cats += sorted(df_expense[df_expense['대분류'] == cat_main]['소분류'].unique())
        else:
            sub_cats += sorted(df_expense['소분류'].unique())
        cat_sub = st.selectbox("소분류", sub_cats)

    # 3. 데이터 필터링 실행
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
    
    if cat_main == "전체" and cat_sub == "전체":
        df_dash = df_dash[~((df_dash['총예산'] == 0) & (df_dash['사용액'] == 0))]

    # 4. 예산 대시보드 화면
    st.title("💰 예산 관리 대시보드")
    st.caption(f"기준: {team_option} / {period_label}")
    st.markdown("<br>", unsafe_allow_html=True)

    # KPI
    tot_b, tot_s, tot_r = df_dash['총예산'].sum(), df_dash['사용액'].sum(), df_dash['잔액'].sum()
    avg_r = (tot_s / tot_b * 100) if tot_b > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총 배정 예산", f"{tot_b:,.0f}원", delta="Budget")
    c2.metric("총 사용액", f"{tot_s:,.0f}원", f"{avg_r:.1f}%", delta_color="inverse")
    c3.metric("현재 잔액", f"{tot_r:,.0f}원", delta="Remain")
    c4.metric("지출 건수", f"{len(df_filtered):,}건")

    st.divider()

    col_chart, col_list = st.columns([4, 6])
    with col_chart:
        st.subheader("📊 예산 집행률")
        if not df_dash.empty:
            fig = px.pie(df_dash, values='사용액', names='팀명', hole=0.6, color_discrete_sequence=px.colors.qualitative.Prism)
            fig.update_layout(showlegend=True, height=400, margin=dict(t=20, b=20, l=20, r=20))
            fig.add_annotation(text=f"Total\n{tot_s/10000:,.0f}만", x=0.5, y=0.5, font_size=24, showarrow=False, font_weight="bold")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("데이터 없음")

    with col_list:
        st.subheader("🏢 팀별 집행 현황")
        if not df_dash.empty:
            # [UI 개선] 엑셀 표 대신 카드 리스트(App-like) 사용
            with st.container(height=400):
                for i, row in df_dash.iterrows():
                    pct = min(row['집행률'], 100)
                    color_bar = "bg-blue-600" if pct < 80 else ("bg-yellow-500" if pct < 100 else "bg-red-600")
                    status_color = "#2563eb" if pct < 80 else ("#d97706" if pct < 100 else "#dc2626")
                    
                    # HTML Card Layout
                    st.markdown(f"""
                        <div class="card-container">
                            <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                                <span style="font-weight:bold; font-size:1.1rem; color:#1e293b;">{row['팀명']}</span>
                                <span style="font-weight:bold; color:{status_color};">{row['집행률']:.1f}%</span>
                            </div>
                            <div style="width:100%; background-color:#e2e8f0; height:8px; border-radius:4px; margin-bottom:8px;">
                                <div style="width:{pct}%; background-color:{status_color}; height:8px; border-radius:4px;"></div>
                            </div>
                            <div style="display:flex; justify-content:space-between; font-size:0.9rem; color:#64748b;">
                                <span>예산: {row['총예산']:,.0f}</span>
                                <span>잔액: <strong>{row['잔액']:,.0f}</strong></span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("데이터 없음")

    st.subheader("📝 상세 지출 내역")
    
    # 합계 박스 (콤마 적용)
    st.markdown(f"""
        <div class="summary-box" style="justify-content: space-between; text-align: left; padding: 15px 30px; display:flex;">
            <div style="font-weight: bold; color: #475569;">🧾 현재 조회 내역 합계</div>
            <div style="font-size: 1.5rem; font-weight: 800; color: #2563eb;">{df_filtered['금액'].sum():,.0f} 원</div>
        </div>
    """, unsafe_allow_html=True)

    if not df_filtered.empty:
        df_display = df_filtered.copy()
        
        # 표시용 컬럼 정리
        cols_show = ['날짜', '팀명', '대분류', '소분류', '상세내역', '금액']
        df_display = df_display[[c for c in cols_show if c in df_display.columns]]
        
        # [UI 개선] Pandas Styler를 사용한 가운데 정렬 (Streamlit 데이터프레임의 한계 극복)
        st.dataframe(
            df_display.sort_values('날짜', ascending=False).style
            .format({'금액': '{:,.0f}원', '날짜': '{:%Y-%m-%d}'}) # 포맷팅
            .set_properties(**{'text-align': 'center'}) # 가운데 정렬 강제
            .set_table_styles([dict(selector='th', props=[('text-align', 'center')])]), # 헤더도 가운데
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("해당 조건의 지출 내역이 없습니다.")

# =============================================================================
# [MODULE B] 연차 관리
# =============================================================================
elif menu == "🏖️ 연차 관리":
    if not leave_sheet_name:
        st.error("연차 데이터 시트가 없습니다.")
        st.stop()

    # 1. 데이터 로드
    df_leave = all_sheets[leave_sheet_name].fillna(0)
    
    # 소속명 정제 (숫자 제거)
    df_leave['소속'] = df_leave['소속'].apply(clean_dept_name)

    # 숫자형 변환
    numeric_cols = ['합계', '사용일수', '잔여일수', '부채예산', '부채잔액']
    for col in numeric_cols:
        if col in df_leave.columns:
            df_leave[col] = pd.to_numeric(df_leave[col], errors='coerce').fillna(0)

    # KPI 계산
    total_emp = len(df_leave)
    avg_usage_rate = (df_leave['사용일수'].sum() / df_leave['합계'].sum() * 100) if df_leave['합계'].sum() > 0 else 0
    total_liability = df_leave['부채잔액'].sum() if '부채잔액' in df_leave.columns else (df_leave['잔여일수'].sum() * 100000)
    
    # 필터 UI
    with st.sidebar:
        st.subheader("연차 필터")
        dept_list = ["전체"] + sorted(df_leave['소속'].unique())
        leave_dept_option = st.selectbox("소속 부서", dept_list)
        risk_criteria = st.slider("촉진 대상 기준 (잔여일)", 5, 25, 10)

    # 필터링 적용
    if leave_dept_option != "전체":
        df_leave = df_leave[df_leave['소속'] == leave_dept_option]

    # 리스크 그룹 (필터 적용 후) & 정렬
    df_risk_final = df_leave[df_leave['잔여일수'] >= risk_criteria].sort_values('잔여일수', ascending=False)

    # 2. 연차 대시보드 화면
    st.title("🏖️ 연차 관리 대시보드")
    st.caption(f"대상: {leave_dept_option} / 촉진기준: {risk_criteria}일 이상")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # KPI Cards
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("전사 소진율", f"{avg_usage_rate:.1f}%", delta="목표 60%")
    k2.metric("미사용 연차 부채", f"{total_liability/100000000:.2f}억", "예상 비용", delta_color="inverse")
    k3.metric("촉진 대상자", f"{len(df_risk_final)}명", f"잔여 {risk_criteria}일↑", delta_color="inverse")
    k4.metric("평균 잔여일수", f"{df_leave['잔여일수'].mean():.1f}일")

    st.divider()

    # 차트 & 대상자 목록
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
        
        if not df_risk_final.empty:
            # 요약 통계 계산
            r_total = df_risk_final['합계'].sum()
            r_used = df_risk_final['사용일수'].sum()
            r_rem = df_risk_final['잔여일수'].sum()
            r_rate = (r_used / r_total * 100) if r_total > 0 else 0
            
            # [수정] 요약 박스 반응형 처리 (화면 넘침 방지)
            st.markdown(f"""
                <div class="summary-box">
                    <div class="summary-item"><span>대상자 총 연차</span><strong>{r_total:,.1f}</strong></div>
                    <div class="summary-item"><span>사용 총계</span><strong>{r_used:,.1f}</strong></div>
                    <div class="summary-item"><span>잔여 총계</span><strong style="color:#ef4444;">{r_rem:,.1f}</strong></div>
                    <div class="summary-item"><span>그룹 소진율</span><strong>{r_rate:.1f}%</strong></div>
                </div>
            """, unsafe_allow_html=True)

            # [수정] 가운데 정렬 및 스타일링 적용
            st.dataframe(
                df_risk_final[['소속', '성명', '잔여일수', '사용일수', '합계']].style
                .format({'잔여일수': '{:.1f}일', '사용일수': '{:.1f}일', '합계': '{:.1f}일'})
                .background_gradient(subset=['잔여일수'], cmap='Reds')
                .set_properties(**{'text-align': 'center'})
                .set_table_styles([dict(selector='th', props=[('text-align', 'center')])]),
                use_container_width=True,
                height=300,
                hide_index=True
            )
        else:
            st.success("관리 대상자가 없습니다.")

    st.divider()
    
    # 3. 전체 임직원 명부
    st.subheader("👥 전체 임직원 현황")
    
    # 표시용 데이터 생성 (콤마 포맷팅)
    df_leave_display = df_leave.copy()
    
    # [수정] 전체 명부도 가운데 정렬 스타일 적용
    # 주의: Progress Bar는 st.column_config로만 가능하므로, 
    # 스타일과 기능 중 하나를 선택해야 할 때가 있습니다. 여기서는 깔끔한 뷰를 위해 스타일 우선 적용 (진행바 대신 숫자로 보여주고 배경색 활용)
    
    st.dataframe(
        df_leave_display[['소속', '성명', '합계', '사용일수', '잔여일수', '부채잔액']].style
        .format({'합계': '{:.1f}', '사용일수': '{:.1f}', '잔여일수': '{:.1f}', '부채잔액': '{:,.0f}원'})
        .background_gradient(subset=['사용일수'], cmap='Blues')
        .set_properties(**{'text-align': 'center'})
        .set_table_styles([dict(selector='th', props=[('text-align', 'center')])]),
        use_container_width=True,
        hide_index=True
    )
