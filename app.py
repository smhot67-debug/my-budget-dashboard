import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import qrcode
from io import BytesIO

# -----------------------------------------------------------------------------
# 1. 시스템 설정 및 디자인
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="통합 관리 시스템",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# [CSS] Shiftee Style & Premium UI
st.markdown("""
    <style>
        /* 폰트 설정 */
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        .stApp { font-family: 'Pretendard', sans-serif; background-color: #F7F8FA; } /* 배경색 변경 */
        
        h1, h2, h3, h4, h5, h6, p, div, span, label, button, input, select, textarea {
            font-family: 'Pretendard', sans-serif;
        }

        /* 아이콘 폰트 보호 */
        .material-symbols-rounded { font-family: 'Material Symbols Rounded' !important; }

        /* 컨테이너 여백 */
        .block-container { padding-top: 1.5rem; padding-bottom: 5rem; }

        /* 공통 카드 스타일 */
        div.css-1r6slb0, div.stDataFrame, div[data-testid="stMetric"] {
            background-color: white;
            border-radius: 8px; /* 각진 둥글기 */
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05); /* 얕은 그림자 */
            border: 1px solid #E1E2E6;
        }

        /* Shiftee 스타일 KPI 카드 커스텀 */
        .kpi-card {
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            border: 1px solid #E1E2E6;
            border-top-width: 4px; /* 상단 컬러 라인 */
            height: 100%;
        }
        .kpi-title { color: #6B7280; font-size: 0.9rem; font-weight: 600; margin-bottom: 8px; }
        .kpi-value { color: #111827; font-size: 2.2rem; font-weight: 800; }
        .kpi-sub { color: #9CA3AF; font-size: 0.8rem; margin-top: 5px; }

        /* 테이블 스타일 */
        .custom-row {
            background-color: white;
            border-bottom: 1px solid #F3F4F6;
            padding: 14px 10px;
            display: flex;
            align-items: center;
            font-size: 0.9rem;
        }
        .custom-row:hover { background-color: #F9FAFB; }
        
        .custom-header {
            background-color: #F9FAFB;
            border-top: 1px solid #E5E7EB;
            border-bottom: 1px solid #E5E7EB;
            padding: 10px 10px;
            font-weight: 700;
            color: #4B5563;
            font-size: 0.85rem;
            display: flex;
            align-items: center;
        }

        /* 배지 스타일 */
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
        .badge-blue { background-color: #DBEAFE; color: #1E40AF; }
        .badge-red { background-color: #FEE2E2; color: #991B1B; }
        .badge-gray { background-color: #F3F4F6; color: #4B5563; }
        
        /* 섹션 타이틀 */
        .section-title { font-size: 1.1rem; font-weight: 700; color: #1F2937; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# 구글 시트 주소
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6hnNtH_1tBFJoA25lXzFPjKUGpBfu0H313_QVFDPdHOpWDDQSJQvIlOQpUoczNO7z7jyWbE171ApD/pub?output=xlsx"

# -----------------------------------------------------------------------------
# 2. 데이터 로드 엔진
# -----------------------------------------------------------------------------
@st.cache_data(ttl=60)
def load_all_data():
    try:
        sheets = pd.read_excel(SHEET_URL, sheet_name=None, engine='openpyxl')
        return sheets
    except Exception as e:
        return None

def clean_dept_name(name):
    if pd.isna(name): return ""
    return re.sub(r'^[\d\.\s]+', '', str(name))

def safe_numeric(series):
    if series.dtype == 'object':
        return pd.to_numeric(series.astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    else:
        return pd.to_numeric(series, errors='coerce').fillna(0)

all_sheets = load_all_data()

if not all_sheets:
    st.error("데이터 로드 실패. 구글 시트 연결을 확인해주세요.")
    if st.button("데이터 새로고침"):
        st.cache_data.clear()
        st.rerun()
    st.stop()

# 시트 매핑
sheet_keys = list(all_sheets.keys())
budget_sheet_name = next((s for s in sheet_keys if '기준' in s or 'Budget' in s), None)
expense_sheet_name = next((s for s in sheet_keys if '지출' in s or 'Expense' in s), None)
leave_sheet_name = next((s for s in sheet_keys if '원천' in s or 'Leave' in s), None)
overtime_sheet_name = next((s for s in sheet_keys if '연장' in s or 'Overtime' in s or '근무' in s), None)

# -----------------------------------------------------------------------------
# 3. 사이드바 및 공통 로직
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("통합 관리 시스템")
    st.markdown("---")
    menu = st.radio("MAIN MENU", ["💰 예산 관리", "🏖️ 연차 관리", "⏰ 연장근무 관리"])
    st.markdown("---")
    
    try:
        import qrcode
        has_qrcode = True
    except ImportError:
        has_qrcode = False

    with st.expander("📱 모바일 접속 QR"):
        if has_qrcode:
            st.caption("Scan to access")
            default_url = "https://my-budget-dashboard-ebrzrzbmslu8xh6dphqtin.streamlit.app/"
            app_url = st.text_input("URL", value=default_url)
            if app_url:
                try:
                    qr = qrcode.QRCode(box_size=10, border=2)
                    qr.add_data(app_url)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white")
                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    st.image(buffer, caption="Mobile Access", use_container_width=True)
                except:
                    pass

# =============================================================================
# [PART A] 예산 관리
# =============================================================================
if menu == "💰 예산 관리":
    if not budget_sheet_name or not expense_sheet_name:
        st.error("예산 데이터 시트가 없습니다.")
        st.stop()

    df_budget = all_sheets[budget_sheet_name].fillna(0)
    for col in df_budget.columns:
        if col != '팀명': df_budget[col] = safe_numeric(df_budget[col])
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
        df_expense['금액'] = safe_numeric(df_expense['금액'])
    
    df_expense = df_expense[df_expense['금액'] != 0]
    if '대분류' not in df_expense.columns: df_expense['대분류'] = '-'
    if '소분류' not in df_expense.columns: df_expense['소분류'] = '-'
    df_expense['대분류'] = df_expense['대분류'].astype(str)
    df_expense['소분류'] = df_expense['소분류'].astype(str)

    with st.sidebar:
        st.subheader("Filter")
        month_list = sorted([m for m in df_expense['월'].unique() if m != '날짜없음'], reverse=True)
        period_option = st.selectbox("기간", ["전체 누적"] + month_list)
        team_list = sorted(df_base['팀명'].unique())
        team_option = st.selectbox("부서", ["전체 부서"] + team_list)
        
        st.caption("Category")
        main_cats = ["전체"] + sorted(df_expense['대분류'].unique())
        cat_main = st.selectbox("대분류", main_cats)
        sub_cats = ["전체"]
        if cat_main != "전체":
            sub_cats += sorted(df_expense[df_expense['대분류'] == cat_main]['소분류'].unique())
        else:
            sub_cats += sorted(df_expense['소분류'].unique())
        cat_sub = st.selectbox("소분류", sub_cats)

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

    st.title("💰 예산 관리 대시보드")
    st.caption(f"Status: {team_option} / {period_label}")
    
    tot_b, tot_s, tot_r = df_dash['총예산'].sum(), df_dash['사용액'].sum(), df_dash['잔액'].sum()
    avg_r = (tot_s / tot_b * 100) if tot_b > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총 배정 예산", f"{tot_b:,.0f}원")
    c2.metric("총 사용액", f"{tot_s:,.0f}원", f"{avg_r:.1f}%", delta_color="inverse")
    c3.metric("현재 잔액", f"{tot_r:,.0f}원")
    c4.metric("지출 건수", f"{len(df_filtered):,}건")

    st.divider()

    col_chart, col_list = st.columns([4, 6])
    with col_chart:
        st.subheader("📊 예산 집행률")
        if not df_dash.empty:
            fig = px.pie(df_dash, values='사용액', names='팀명', hole=0.6, color_discrete_sequence=px.colors.qualitative.Prism)
            fig.update_layout(showlegend=True, height=400, margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            if tot_s > 0:
                fig.add_annotation(text=f"Total\n{tot_s/10000:,.0f}만", x=0.5, y=0.5, font_size=24, showarrow=False, font_weight="bold", font_color="#2B3674")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("데이터 없음")

    with col_list:
        st.subheader("🏢 팀별 집행 현황")
        if not df_dash.empty:
            for i, row in df_dash.iterrows():
                pct = min(row['집행률'], 100)
                status_color = "#4318FF" if pct < 80 else ("#FFB547" if pct < 100 else "#FF5630")
                bg_bar = "#EFF4FB"
                
                st.markdown(f"""
                    <div style="background:white; padding:20px; border-radius:8px; margin-bottom:15px; border:1px solid #E1E2E6; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                            <span style="font-weight:700; color:#111827; font-size:1.0rem;">{row['팀명']}</span>
                            <span style="font-weight:800; color:{status_color};">{row['집행률']:.1f}%</span>
                        </div>
                        <div style="width:100%; background-color:{bg_bar}; height:8px; border-radius:4px; margin-bottom:12px;">
                            <div style="width:{pct}%; background-color:{status_color}; height:8px; border-radius:4px;"></div>
                        </div>
                        <div style="display:flex; justify-content:space-between; font-size:0.85rem; color:#6B7280; font-weight:500;">
                            <span>예산: {row['총예산']:,.0f}</span>
                            <span>잔액: <strong style="color:#111827;">{row['잔액']:,.0f}</strong></span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("데이터 없음")

    st.subheader("📝 상세 지출 내역")
    if not df_filtered.empty:
        df_show = df_filtered.sort_values('날짜', ascending=False).reset_index(drop=True)
        st.markdown("""
            <div class="custom-header">
                <div style="flex:1;">날짜</div>
                <div style="flex:1;">부서</div>
                <div style="flex:1;">분류</div>
                <div style="flex:2;">적요</div>
                <div style="flex:1; text-align:right;">금액</div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container(height=400):
            for _, row in df_show.iterrows():
                date_str = row['날짜'].strftime('%Y-%m-%d')
                amt_str = f"{int(row['금액']):,}"
                st.markdown(f"""
                    <div class="custom-row">
                        <div style="flex:1; color:#6B7280;">{date_str}</div>
                        <div style="flex:1;"><strong>{row['팀명']}</strong></div>
                        <div style="flex:1;"><span class="badge badge-gray">{row['소분류']}</span></div>
                        <div style="flex:2; color:#374151;">{row['상세내역']}</div>
                        <div style="flex:1; text-align:right; font-weight:bold; color:#1F2937;">{amt_str}원</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("내역이 없습니다.")

# =============================================================================
# [PART B] 연차 관리
# =============================================================================
elif menu == "🏖️ 연차 관리":
    if not leave_sheet_name:
        st.error("연차 데이터 시트를 찾을 수 없습니다.")
        st.stop()

    df_leave = all_sheets[leave_sheet_name].fillna(0)
    df_leave['소속'] = df_leave['소속'].apply(clean_dept_name)
    for col in ['합계', '사용일수', '잔여일수', '부채예산', '부채잔액']:
        if col in df_leave.columns: df_leave[col] = safe_numeric(df_leave[col])

    with st.sidebar:
        st.subheader("Filter")
        dept_list = ["전체"] + sorted(df_leave['소속'].unique())
        leave_dept_option = st.selectbox("소속 부서", dept_list)
        risk_criteria = st.slider("촉진 대상 기준 (잔여일)", 5, 25, 10)

    if leave_dept_option != "전체":
        df_leave = df_leave[df_leave['소속'] == leave_dept_option]

    df_risk = df_leave[df_leave['잔여일수'] >= risk_criteria].sort_values('잔여일수', ascending=False)
    avg_usage = (df_leave['사용일수'].sum() / df_leave['합계'].sum() * 100) if df_leave['합계'].sum() > 0 else 0
    tot_liab = df_leave['부채잔액'].sum()

    st.title("🏖️ 연차 관리 대시보드")
    st.caption(f"Status: {leave_dept_option}")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("전사 소진율", f"{avg_usage:.1f}%", delta="Goal 60%")
    k2.metric("미사용 연차 부채", f"{tot_liab/100000000:.2f}억", "Estimated", delta_color="inverse")
    k3.metric("촉진 대상자", f"{len(df_risk)}명", f"> {risk_criteria} days", delta_color="inverse")
    k4.metric("평균 잔여일수", f"{df_leave['잔여일수'].mean():.1f}일")

    st.divider()

    c_chart, c_risk = st.columns([4, 6])
    with c_chart:
        st.subheader("📊 부서별 소진율")
        dept_sum = df_leave.groupby('소속').agg({'사용일수':'sum', '합계':'sum'}).reset_index()
        dept_sum['소진율'] = (dept_sum['사용일수'] / dept_sum['합계'] * 100).fillna(0)
        fig = px.bar(dept_sum, x='소속', y='소진율', text=dept_sum['소진율'].apply(lambda x: f"{x:.1f}%"), color='소진율', color_continuous_scale='Bluyl')
        fig.update_layout(xaxis_title=None, yaxis_title="소진율(%)", height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with c_risk:
        st.subheader(f"🚨 촉진 대상자 (Care Group)")
        if not df_risk.empty:
            r_tot = df_risk['합계'].sum()
            r_use = df_risk['사용일수'].sum()
            r_rem = df_risk['잔여일수'].sum()
            r_rate = (r_use / r_tot * 100) if r_tot > 0 else 0
            
            # 요약 박스 (Shiftee Style)
            st.markdown(f"""
                <div style="background-color: #FEF2F2; border: 1px solid #FECACA; border-radius: 8px; padding: 15px; display: flex; justify-content: space-around; margin-bottom: 20px;">
                    <div style="text-align:center;"><span style="font-size:0.8rem; color:#991B1B;">대상자 총 연차</span><br><strong>{r_tot:,.1f}</strong></div>
                    <div style="text-align:center;"><span style="font-size:0.8rem; color:#991B1B;">사용 총계</span><br><strong>{r_use:,.1f}</strong></div>
                    <div style="text-align:center;"><span style="font-size:0.8rem; color:#DC2626;">잔여 총계</span><br><strong style="font-size:1.1rem; color:#DC2626;">{r_rem:,.1f}</strong></div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("""
                <div class="custom-header">
                    <div class="row-item">성명/직급</div>
                    <div class="row-item">소속</div>
                    <div class="row-item">잔여일수</div>
                    <div class="row-item">비고</div>
                </div>
            """, unsafe_allow_html=True)

            with st.container(height=320):
                for _, row in df_risk.iterrows():
                    st.markdown(f"""
                        <div class="custom-row">
                            <div class="row-item"><strong>{row['성명']}</strong></div>
                            <div class="row-item" style="color:#6B7280;">{row['소속']}</div>
                            <div class="row-item"><span class="badge badge-red">{row['잔여일수']:.1f}일</span></div>
                            <div class="row-item" style="font-size:0.8rem; color:#9CA3AF;">잔여 {risk_criteria}일 이상</div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.success("해당 조건의 촉진 대상자가 없습니다.")

    st.divider()
    st.subheader("👥 전체 임직원 명부")
    df_show = df_leave.sort_values('소속').copy()
    st.markdown("""
        <div class="custom-header">
            <div class="row-item">소속</div>
            <div class="row-item">성명</div>
            <div class="row-item">총 연차</div>
            <div class="row-item">사용</div>
            <div class="row-item">잔여</div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container(height=500):
        for _, row in df_show.iterrows():
            st.markdown(f"""
                <div class="custom-row">
                    <div class="row-item" style="color:#6B7280;">{row['소속']}</div>
                    <div class="row-item"><strong>{row['성명']}</strong></div>
                    <div class="row-item">{row['합계']:.1f}</div>
                    <div class="row-item">{row['사용일수']:.1f}</div>
                    <div class="row-item"><span class="badge badge-blue">{row['잔여일수']:.1f}</span></div>
                </div>
            """, unsafe_allow_html=True)

# =============================================================================
# [PART C] 연장근무 관리 (Shiftee Style Redesign)
# =============================================================================
elif menu == "⏰ 연장근무 관리":
    if not overtime_sheet_name:
        st.error("연장근무 데이터 시트('연장' 포함)를 찾을 수 없습니다.")
        st.stop()

    df_ot = all_sheets[overtime_sheet_name].fillna(0)
    df_ot.columns = [c.replace(' ','').strip() for c in df_ot.columns]
    
    month_col = next((c for c in df_ot.columns if c == '월' or c == 'Month'), None)
    if month_col:
        df_ot.rename(columns={month_col: '월'}, inplace=True)
        df_ot['월'] = df_ot['월'].astype(str)
    else:
        df_ot['월'] = 'Unknown'

    num_cols = ['연장시간', '연장근로', '야근시간', '휴일시간']
    valid_num_cols = []
    for c in df_ot.columns:
        if any(x in c for x in num_cols):
            df_ot[c] = safe_numeric(df_ot[c])
            valid_num_cols.append(c)
    
    df_ot['총근무'] = df_ot[valid_num_cols].sum(axis=1)

    # Shiftee Layout Implementation
    st.title("근태/연장근무 리포트")
    st.caption("실시간 근무 현황 및 통계")

    # 필터 (사이드바 유지)
    with st.sidebar:
        st.subheader("연장근무 필터")
        unique_months = [m for m in df_ot['월'].unique() if m != '0' and m != 'Unknown']
        try:
            sorted_months = sorted(unique_months, key=lambda x: int(re.sub(r'\D', '', str(x))) if re.sub(r'\D', '', str(x)) else 0)
        except:
            sorted_months = sorted(unique_months)
        month_list = ["전체 누적"] + sorted_months
        ot_month_opt = st.selectbox("조회 기간", month_list)

        team_list = ["전체"] + sorted(df_ot['팀명'].unique())
        ot_team_opt = st.selectbox("소속 팀", team_list)

    # 데이터 필터링
    df_filtered = df_ot.copy()
    if ot_month_opt != "전체 누적":
        df_filtered = df_filtered[df_filtered['월'] == ot_month_opt]
    if ot_team_opt != "전체":
        df_filtered = df_filtered[df_filtered['팀명'] == ot_team_opt]

    # 1. Top KPI Cards (Shiftee Style with Colored Borders)
    total_sum = df_filtered['총근무'].sum()
    ext_sum = df_filtered[[c for c in df_ot.columns if '연장' in c]].sum().sum()
    night_sum = df_filtered[[c for c in df_ot.columns if '야근' in c]].sum().sum()
    hol_sum = df_filtered[[c for c in df_ot.columns if '휴일' in c]].sum().sum()
    
    # 인원수 계산
    emp_count = df_filtered['이름'].nunique()

    k1, k2, k3, k4 = st.columns(4)
    
    with k1:
        st.markdown(f"""
            <div class="kpi-card" style="border-top-color: #3B82F6;">
                <div class="kpi-title">총 연장근로</div>
                <div class="kpi-value">{ext_sum:,.1f}</div>
                <div class="kpi-sub">연장 근무 합계 (시간)</div>
            </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
            <div class="kpi-card" style="border-top-color: #EF4444;">
                <div class="kpi-title">야간 근로</div>
                <div class="kpi-value">{night_sum:,.1f}</div>
                <div class="kpi-sub">22시~06시 근무 (시간)</div>
            </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
            <div class="kpi-card" style="border-top-color: #10B981;">
                <div class="kpi-title">휴일 근로</div>
                <div class="kpi-value">{hol_sum:,.1f}</div>
                <div class="kpi-sub">휴일 근무 합계 (시간)</div>
            </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
            <div class="kpi-card" style="border-top-color: #6B7280;">
                <div class="kpi-title">대상 인원</div>
                <div class="kpi-value">{emp_count}</div>
                <div class="kpi-sub">근무 기록 발생 인원 (명)</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Middle Section (Chart & List)
    c_chart, c_list = st.columns([7, 3])
    
    with c_chart:
        st.markdown('<div class="section-title">📊 팀별 근무 유형 비교</div>', unsafe_allow_html=True)
        if not df_filtered.empty:
            df_chart = df_filtered.groupby('팀명')[valid_num_cols].sum().reset_index()
            df_long = df_chart.melt(id_vars='팀명', var_name='유형', value_name='시간')
            
            fig = px.bar(df_long, x='팀명', y='시간', color='유형', barmode='group',
                         color_discrete_map={'연장시간':'#3B82F6', '연장근로':'#3B82F6', '야근시간':'#EF4444', '휴일시간':'#10B981'},
                         text_auto='.0f')
            fig.update_layout(
                xaxis_title=None, 
                yaxis_title=None, 
                height=350, 
                paper_bgcolor='white', 
                plot_bgcolor='white',
                margin=dict(t=20, b=20, l=20, r=20),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("데이터가 없습니다.")

    with c_list:
        st.markdown('<div class="section-title">🚨 관리 필요 (Top 5)</div>', unsafe_allow_html=True)
        # 상위 근무자 추출
        top_users = df_filtered.groupby(['이름', '팀명'])['총근무'].sum().reset_index().sort_values('총근무', ascending=False).head(5)
        
        if not top_users.empty:
            with st.container():
                for i, row in top_users.iterrows():
                    st.markdown(f"""
                        <div style="background:white; border:1px solid #E5E7EB; border-radius:8px; padding:12px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <div style="font-weight:700; color:#1F2937;">{row['이름']}</div>
                                <div style="font-size:0.75rem; color:#6B7280;">{row['팀명']}</div>
                            </div>
                            <div style="text-align:right;">
                                <div style="font-weight:800; color:#EF4444;">{row['총근무']:.1f}h</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("데이터 없음")

    # 3. Bottom Section (Detail Table)
    st.markdown('<div class="section-title">🗓️ 리포트 현황 (상세)</div>', unsafe_allow_html=True)

    if not df_filtered.empty:
        sort_cols = [c for c in ['월', '주차', '팀명'] if c in df_filtered.columns]
        df_show_ot = df_filtered.sort_values(sort_cols).reset_index(drop=True)

        # 테이블 헤더
        st.markdown("""
            <div class="custom-header">
                <div style="flex:1;">월/주차</div>
                <div style="flex:1;">팀명</div>
                <div style="flex:1;">이름</div>
                <div style="flex:1; text-align:right; color:#3B82F6;">연장</div>
                <div style="flex:1; text-align:right; color:#EF4444;">야근</div>
                <div style="flex:1; text-align:right; color:#10B981;">휴일</div>
                <div style="flex:1.5; text-align:right;">총 합계</div>
            </div>
        """, unsafe_allow_html=True)

        with st.container(height=500):
            for _, row in df_show_ot.iterrows():
                ext = row.get('연장근로', row.get('연장시간', 0))
                night = row.get('야근시간', 0)
                hol = row.get('휴일시간', 0)
                week_str = row.get('주차', '')
                total = row['총근무']
                
                # 프로그레스 바 시각화 (최대 52시간 기준)
                prog_width = min(total / 52 * 100, 100)
                prog_color = "#EF4444" if total > 12 else "#3B82F6"

                st.markdown(f"""
                    <div class="custom-row">
                        <div style="flex:1; color:#6B7280;">{row['월']} {week_str}</div>
                        <div style="flex:1; font-weight:600;">{row['팀명']}</div>
                        <div style="flex:1;">{row['이름']}</div>
                        <div style="flex:1; text-align:right; font-family:monospace;">{ext:.1f}</div>
                        <div style="flex:1; text-align:right; font-family:monospace;">{night:.1f}</div>
                        <div style="flex:1; text-align:right; font-family:monospace;">{hol:.1f}</div>
                        <div style="flex:1.5; padding-left:20px;">
                            <div style="display:flex; align-items:center; gap:8px;">
                                <div style="flex:1; height:6px; background:#E5E7EB; border-radius:3px; overflow:hidden;">
                                    <div style="width:{prog_width}%; height:100%; background:{prog_color};"></div>
                                </div>
                                <span style="font-weight:700; width:40px; text-align:right;">{total:.1f}h</span>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("표시할 상세 내역이 없습니다.")
