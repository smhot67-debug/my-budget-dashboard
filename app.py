import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import qrcode
from io import BytesIO
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. 시스템 설정 및 디자인
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="통합 관리 시스템",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# [CSS] 프리미엄 UI 디자인 (헤더 스타일 강화)
st.markdown("""
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        
        .stApp {
            font-family: 'Pretendard', sans-serif;
            background-color: #F4F7FE;
        }
        
        h1, h2, h3, h4, h5, h6, p, div, span, label, button, input, select, textarea {
            font-family: 'Pretendard', sans-serif;
        }

        /* 아이콘 폰트 보호 */
        .material-symbols-rounded { font-family: 'Material Symbols Rounded' !important; }

        /* 컨테이너 여백 */
        .block-container { padding-top: 1.5rem; padding-bottom: 5rem; }

        /* 카드 박스 스타일 */
        div.css-1r6slb0, div.stDataFrame, div[data-testid="stMetric"] {
            background-color: white;
            border-radius: 20px;
            padding: 24px;
            box-shadow: 0px 4px 20px rgba(112, 144, 176, 0.08);
            border: none;
        }

        /* 메트릭 숫자 */
        div[data-testid="stMetricValue"] {
            font-size: 2rem !important;
            font-weight: 700 !important;
            color: #2B3674;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.95rem !important;
            color: #A3AED0;
            font-weight: 500;
        }

        /* [NEW] 모던 헤더 디자인 */
        .modern-header {
            background: white;
            padding: 25px 30px;
            border-radius: 20px;
            box-shadow: 0px 4px 20px rgba(112, 144, 176, 0.08);
            margin-bottom: 25px;
            border-left: 10px solid #4318FF;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .modern-header h1 {
            margin: 0;
            font-size: 1.8rem;
            color: #2B3674;
            font-weight: 800;
            line-height: 1.2;
        }
        .modern-header p {
            margin: 8px 0 0 0;
            color: #A3AED0;
            font-size: 1rem;
            font-weight: 500;
        }

        /* 커스텀 KPI 카드 */
        .kpi-card {
            background-color: white;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0px 4px 12px rgba(112, 144, 176, 0.08);
            border: 1px solid #E2E8F0;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .kpi-title { color: #64748B; font-size: 0.9rem; font-weight: 600; margin-bottom: 8px; }
        .kpi-value { color: #1E293B; font-size: 2.2rem; font-weight: 800; letter-spacing: -1px; }
        .kpi-sub { color: #94A3B8; font-size: 0.85rem; margin-top: 4px; font-weight: 500; }

        /* 커스텀 리스트 행 */
        .custom-row {
            background-color: white;
            border-bottom: 1px solid #F4F7FE;
            padding: 16px 10px;
            display: flex;
            align-items: center;
            transition: all 0.2s ease;
            border-radius: 12px;
            margin-bottom: 5px;
        }
        .custom-row:hover { background-color: #F4F7FE; transform: translateX(5px); }
        
        /* [NEW] 헤더 디자인 강화 (배경색 & 폰트 컬러 적용) */
        .custom-header {
            background-color: #EEF2FF; /* 연한 인디고 배경 */
            border-radius: 16px;
            padding: 18px 10px;
            font-weight: 700;
            color: #4318FF; /* 브랜드 컬러 텍스트 */
            font-size: 0.95rem;
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.03);
            border: 1px solid #E0E7FF;
        }
        
        .row-item { flex: 1; text-align: center; font-size: 0.95rem; color: #2B3674; font-weight: 500; }
        .row-item-left { flex: 1; text-align: left; padding-left: 20px; font-size: 0.95rem; color: #2B3674; font-weight: 500; }
        
        /* 헤더 내부 아이템 컬러 오버라이드 */
        .custom-header .row-item, .custom-header .row-item-left {
            color: #4318FF; 
            font-weight: 800;
        }

        /* 태그 */
        .badge { padding: 6px 12px; border-radius: 30px; font-size: 0.75rem; font-weight: 700; }
        .badge-red { background-color: #FEE2E2; color: #DC2626; }
        .badge-blue { background-color: #E0E7FF; color: #4318FF; }
        .badge-gray { background-color: #F4F7FE; color: #A3AED0; }
        
        /* 합계 박스 */
        .total-box {
            background: linear-gradient(135deg, #868CFF 0%, #4318FF 100%);
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 25px;
            display: flex;
            justify-content: space-around;
            align-items: center;
            color: white;
            box-shadow: 0px 10px 20px rgba(67, 24, 255, 0.2);
        }
        .total-label { font-size: 0.9rem; color: #E9E3FF; margin-bottom: 5px; display: block; text-align: center; font-weight: 500;}
        .total-value { font-size: 1.5rem; font-weight: 700; color: white; display: block; text-align: center;}
        
        /* 사이드바 */
        [data-testid="stSidebar"] {
            background-color: white;
            box-shadow: 4px 0px 20px rgba(112, 144, 176, 0.05);
            border-right: none;
        }

        /* 탭 버튼 스타일 */
        div.row-widget.stRadio > div {
            background-color: white;
            padding: 10px;
            border-radius: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            display: flex;
            justify-content: center;
            gap: 15px;
            border: 1px solid #E2E8F0;
            margin-bottom: 20px;
            margin-top: 10px;
        }
        div.row-widget.stRadio > div[role="radiogroup"] > label {
            flex: 1;
            background-color: transparent;
            border-radius: 15px;
            padding: 15px 0;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
            border: 2px solid transparent;
            margin-right: 0 !important;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        div.row-widget.stRadio > div[role="radiogroup"] > label:hover {
            background-color: #F8FAFC;
            color: #4318FF;
            transform: translateY(-2px);
        }
        div.row-widget.stRadio > div[role="radiogroup"] > label[data-checked="true"] {
            background-color: #4318FF;
            color: white !important;
            box-shadow: 0 8px 20px rgba(67, 24, 255, 0.3);
            transform: translateY(-2px);
        }
        div.row-widget.stRadio > div[role="radiogroup"] > label p {
            font-size: 1.2rem !important;
            font-weight: 700 !important;
            margin: 0 !important;
        }
        div.row-widget.stRadio > div[role="radiogroup"] > label[data-checked="false"] p {
            color: #A3AED0 !important;
        }
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
    if st.button("🔄 데이터 다시 불러오기"):
        st.cache_data.clear()
        st.rerun()
    st.stop()

# 시트 이름 매핑
sheet_keys = list(all_sheets.keys())
budget_sheet_name = next((s for s in sheet_keys if '기준' in s or 'Budget' in s), None)
expense_sheet_name = next((s for s in sheet_keys if '지출' in s or 'Expense' in s), None)
leave_sheet_name = next((s for s in sheet_keys if '원천' in s or 'Leave' in s), None)
overtime_sheet_name = next((s for s in sheet_keys if '연장' in s or 'Overtime' in s or '근무' in s), None)

# [마스터 데이터]
master_teams = ["전체 팀"]
if budget_sheet_name:
    df_bm = all_sheets[budget_sheet_name].fillna(0)
    if '팀명' in df_bm.columns:
        teams = sorted(df_bm['팀명'].astype(str).unique())
        master_teams = ["전체 팀"] + teams

current_year = datetime.now().year
master_months_list = [f"2026-{str(m).zfill(2)}" for m in range(1, 13)]
master_months = ["전체 누적"] + master_months_list

# -----------------------------------------------------------------------------
# 3. 사이드바 및 공통
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("통합 관리 시스템")
    st.markdown("---")
    menu = st.radio("MAIN MENU", ["💰 예산 관리", "🏖️ 연차 관리", "⏰ 연장근무 관리"])
    st.markdown("---")
    
    if st.button("🔄 데이터 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.caption("※ 시트 수정 후 1~5분 뒤 반영됩니다.")
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
                    qr = qrcode.QRCode(box_size=10, border=1)
                    qr.add_data(app_url)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white")
                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    st.image(buffer, use_container_width=True)
                except: pass

# =============================================================================
# [PART A] 예산 관리
# =============================================================================
if menu == "💰 예산 관리":
    if not budget_sheet_name or not expense_sheet_name:
        st.error("예산 시트가 없습니다.")
        st.stop()

    df_budget = all_sheets[budget_sheet_name].fillna(0)
    df_budget.columns = [str(c).strip() for c in df_budget.columns]
    
    for col in df_budget.columns:
        if col != '팀명': df_budget[col] = safe_numeric(df_budget[col])

    base_col = next((c for c in df_budget.columns if '배정' in c or '기본' in c), None)
    
    if base_col:
        df_budget['월기본예산'] = df_budget[base_col]
    else:
        num_cols = df_budget.select_dtypes(include=['number']).columns
        df_budget['월기본예산'] = df_budget[num_cols[0]] if len(num_cols) > 0 else 0

    df_expense = all_sheets[expense_sheet_name].fillna(0)
    df_expense.columns = [str(c).strip() for c in df_expense.columns]
    
    date_col = next((c for c in df_expense.columns if '날짜' in c or 'Date' in c), None)
    if date_col:
        df_expense[date_col] = pd.to_datetime(df_expense[date_col], errors='coerce')
        df_expense['월'] = df_expense[date_col].dt.strftime('%Y-%m') # 2026-01
        df_expense['월_숫자'] = df_expense[date_col].dt.month
    else:
        df_expense['월'] = 'Unknown'
        df_expense['월_숫자'] = 0
    
    if '금액' in df_expense.columns:
        df_expense['금액'] = safe_numeric(df_expense['금액'])
    
    df_expense = df_expense[df_expense['금액'] != 0]

    with st.sidebar:
        st.subheader("Filter")
        period_option = st.selectbox("기간", master_months)
        team_option = st.selectbox("부서", master_teams)
        
        main_cats = ["전체"] + sorted(df_expense['대분류'].astype(str).unique())
        cat_main = st.selectbox("대분류", main_cats)
        sub_cats = ["전체"]
        if cat_main != "전체":
            sub_cats += sorted(df_expense[df_expense['대분류'] == cat_main]['소분류'].astype(str).unique())
        cat_sub = st.selectbox("소분류", sub_cats)

    monthly_exp = df_expense.groupby(['팀명', '월'])['금액'].sum().reset_index()
    dashboard_rows = []
    
    target_teams = df_budget['팀명'].unique() if team_option == "전체 팀" else [team_option]
    
    for team in target_teams:
        team_base_monthly = df_budget.loc[df_budget['팀명'] == team, '월기본예산'].sum()
        
        cumulative_balance = 0
        final_budget = 0
        final_spent = 0
        final_balance = 0
        
        target_month_idx = 12
        if period_option != "전체 누적":
            try: target_month_idx = int(period_option.split('-')[1])
            except: target_month_idx = 1
        
        if period_option == "전체 누적":
            total_base = team_base_monthly * 12
            total_add = 0
            for c in df_budget.columns:
                if '추가' in c: total_add += df_budget.loc[df_budget['팀명'] == team, c].sum()
            
            final_budget = total_base + total_add
            final_spent = df_expense[df_expense['팀명'] == team]['금액'].sum()
            final_balance = final_budget - final_spent
            
        else:
            for m in range(1, target_month_idx + 1):
                month_str = f"2026-{str(m).zfill(2)}"
                
                add_col = [c for c in df_budget.columns if str(m) in c and '추가' in c]
                this_add = df_budget.loc[df_budget['팀명'] == team, add_col[0]].sum() if add_col else 0
                
                available = cumulative_balance + team_base_monthly + this_add
                spent = monthly_exp[(monthly_exp['팀명'] == team) & (monthly_exp['월'] == month_str)]['금액'].sum()
                cumulative_balance = available - spent
                
                if m == target_month_idx:
                    final_budget = available 
                    final_spent = spent
                    final_balance = cumulative_balance

        dashboard_rows.append({
            '팀명': team,
            '예산': final_budget,
            '사용액': final_spent,
            '잔액': final_balance,
            '집행률': (final_spent / final_budget * 100) if final_budget > 0 else 0
        })

    df_dash = pd.DataFrame(dashboard_rows)
    
    df_detail_filtered = df_expense.copy()
    if period_option != "전체 누적":
        df_detail_filtered = df_detail_filtered[df_detail_filtered['월'] == period_option]
    if team_option != "전체 팀":
        df_detail_filtered = df_detail_filtered[df_detail_filtered['팀명'] == team_option]
    if cat_main != "전체": df_detail_filtered = df_detail_filtered[df_detail_filtered['대분류'] == cat_main]
    if cat_sub != "전체": df_detail_filtered = df_detail_filtered[df_detail_filtered['소분류'] == cat_sub]

    st.markdown(f"""
        <div class="modern-header">
            <h1>💰 예산 관리 대시보드</h1>
            <p>Status: {team_option} / {period_option}</p>
        </div>
    """, unsafe_allow_html=True)
    
    if cat_main == "전체":
        tot_b = df_dash['예산'].sum()
        tot_s = df_dash['사용액'].sum()
        tot_r = df_dash['잔액'].sum()
    else:
        tot_b = 0
        tot_s = df_detail_filtered['금액'].sum()
        tot_r = 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("가용 예산 (이월포함)", f"{tot_b:,.0f}원")
    c2.metric("총 사용액", f"{tot_s:,.0f}원")
    c3.metric("현재 잔액", f"{tot_r:,.0f}원", delta="Remain")
    c4.metric("지출 건수", f"{len(df_detail_filtered):,}건")

    st.divider()

    col_chart, col_list = st.columns([4, 6])
    with col_chart:
        st.subheader("📊 예산 집행률")
        if tot_s > 0:
            fig = px.pie(df_dash, values='사용액', names='팀명', hole=0.6, color_discrete_sequence=px.colors.qualitative.Prism)
            fig.update_layout(showlegend=True, height=400, margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor='white', plot_bgcolor='white')
            fig.add_annotation(text=f"Total\n{tot_s/10000:,.0f}만", x=0.5, y=0.5, font_size=20, showarrow=False, font_weight="bold", font_color="#2B3674")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("지출 데이터가 없습니다.")

    with col_list:
        st.subheader("🏢 팀별 집행 현황")
        if not df_dash.empty:
            for i, row in df_dash.iterrows():
                pct = min(row['집행률'], 100)
                status_color = "#3B82F6" if pct < 80 else ("#F59E0B" if pct < 100 else "#EF4444")
                
                st.markdown(f"""
                    <div style="background:white; padding:20px; border-radius:12px; margin-bottom:12px; box-shadow: 0px 2px 8px rgba(0,0,0,0.05); border:1px solid #E2E8F0;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                            <span style="font-weight:700; color:#1E293B;">{row['팀명']}</span>
                            <span style="font-weight:700; color:{status_color};">{row['집행률']:.1f}%</span>
                        </div>
                        <div style="width:100%; background-color:#F1F5F9; height:8px; border-radius:4px; margin-bottom:10px;">
                            <div style="width:{pct}%; background-color:{status_color}; height:8px; border-radius:4px;"></div>
                        </div>
                        <div style="display:flex; justify-content:space-between; font-size:0.9rem; color:#64748B;">
                            <span>가용: {row['예산']:,.0f}</span>
                            <span>사용: {row['사용액']:,.0f}</span>
                            <span>잔액: <strong>{row['잔액']:,.0f}</strong></span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("데이터 없음")

    st.subheader("📝 상세 지출 내역")
    if not df_detail_filtered.empty:
        df_show = df_detail_filtered.sort_values('날짜', ascending=False).reset_index(drop=True)
        # [수정] 헤더 UI 적용
        st.markdown("""
            <div class="custom-header">
                <div class="row-item">날짜</div>
                <div class="row-item">부서</div>
                <div class="row-item">대분류</div>
                <div class="row-item">소분류</div>
                <div class="row-item-left" style="flex:2;">적요</div>
                <div class="row-item" style="text-align:right; padding-right:20px;">금액</div>
            </div>
        """, unsafe_allow_html=True)
        with st.container(height=400):
            for _, row in df_show.iterrows():
                date_str = row['날짜'].strftime('%Y-%m-%d')
                amt_str = f"{int(row['금액']):,}"
                st.markdown(f"""
                    <div class="custom-row">
                        <div class="row-item" style="color:#64748B; font-size:0.85rem;">{date_str}</div>
                        <div class="row-item"><strong>{row['팀명']}</strong></div>
                        <div class="row-item"><span class="badge badge-gray">{row['대분류']}</span></div>
                        <div class="row-item"><span class="badge badge-gray">{row['소분류']}</span></div>
                        <div class="row-item-left" style="flex:2; color:#334155;">{row['상세내역']}</div>
                        <div class="row-item" style="text-align:right; padding-right:20px; font-weight:bold; color:#1E293B;">{amt_str}원</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("내역이 없습니다.")

# =============================================================================
# [PART B] 연차 관리
# =============================================================================
elif menu == "🏖️ 연차 관리":
    if not leave_sheet_name:
        st.error("연차 데이터 시트가 없습니다.")
        st.stop()

    df_leave = all_sheets[leave_sheet_name].fillna(0)
    df_leave['소속'] = df_leave['소속'].apply(clean_dept_name)
    for col in ['합계', '사용일수', '잔여일수', '부채예산', '부채잔액']:
        if col in df_leave.columns: df_leave[col] = safe_numeric(df_leave[col])

    with st.sidebar:
        st.subheader("Filter")
        dept_list = master_teams 
        leave_dept_option = st.selectbox("소속 부서", dept_list)
        risk_criteria = st.slider("촉진 대상 기준 (잔여일)", 5, 25, 10)

    if leave_dept_option != "전체 팀":
        df_leave = df_leave[df_leave['소속'] == leave_dept_option]

    df_risk = df_leave[df_leave['잔여일수'] >= risk_criteria].sort_values('잔여일수', ascending=False)
    avg_usage = (df_leave['사용일수'].sum() / df_leave['합계'].sum() * 100) if df_leave['합계'].sum() > 0 else 0
    tot_liab = df_leave['부채잔액'].sum()

    st.markdown(f"""
        <div class="modern-header">
            <h1>🏖️ 연차 관리 대시보드</h1>
            <p>Status: {leave_dept_option}</p>
        </div>
    """, unsafe_allow_html=True)

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
        fig.update_traces(textfont_color='white', textposition='auto')
        fig.update_layout(xaxis_title=None, yaxis_title="소진율(%)", height=450, paper_bgcolor='white', plot_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    with c_risk:
        st.subheader(f"🚨 촉진 대상자 (Care Group)")
        if not df_risk.empty:
            r_tot = df_risk['합계'].sum()
            r_use = df_risk['사용일수'].sum()
            r_rem = df_risk['잔여일수'].sum()
            r_rate = (r_use / r_tot * 100) if r_tot > 0 else 0
            
            st.markdown(f"""
                <div class="total-box">
                    <div><span class="total-label">대상자 총 연차</span><span class="total-value">{r_tot:,.1f}</span></div>
                    <div><span class="total-label">사용 총계</span><span class="total-value">{r_use:,.1f}</span></div>
                    <div><span class="total-label">잔여 총계</span><span class="total-value" style="color:#FCA5A5;">{r_rem:,.1f}</span></div>
                    <div><span class="total-label">그룹 소진율</span><span class="total-value">{r_rate:.1f}%</span></div>
                </div>
            """, unsafe_allow_html=True)
            
            # [수정] 헤더 UI 적용
            st.markdown("""
                <div class="custom-header">
                    <div class="row-item">성명/직급</div>
                    <div class="row-item">소속</div>
                    <div class="row-item">잔여일수</div>
                    <div class="row-item">비고</div>
                </div>
            """, unsafe_allow_html=True)

            with st.container(height=300):
                for _, row in df_risk.iterrows():
                    st.markdown(f"""
                        <div class="custom-row">
                            <div class="row-item"><strong>{row['성명']}</strong></div>
                            <div class="row-item" style="color:#64748B;">{row['소속']}</div>
                            <div class="row-item"><span class="badge badge-red">{row['잔여일수']:.1f}일</span></div>
                            <div class="row-item" style="font-size:0.8rem; color:#94A3B8;">잔여 {risk_criteria}일 이상</div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.success("대상자 없음")

    st.divider()
    st.subheader("👥 전체 임직원 명부")
    df_show = df_leave.sort_values('소속').copy()
    
    # [수정] 헤더 UI 적용
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
                    <div class="row-item" style="color:#64748B;">{row['소속']}</div>
                    <div class="row-item"><strong>{row['성명']}</strong></div>
                    <div class="row-item">{row['합계']:.1f}</div>
                    <div class="row-item">{row['사용일수']:.1f}</div>
                    <div class="row-item"><span class="badge badge-blue">{row['잔여일수']:.1f}</span></div>
                </div>
            """, unsafe_allow_html=True)

# =============================================================================
# [PART C] 연장근무 관리
# =============================================================================
elif menu == "⏰ 연장근무 관리":
    if not overtime_sheet_name:
        st.error("연장근무 시트를 찾을 수 없습니다.")
        st.stop()

    df_ot = all_sheets[overtime_sheet_name].fillna(0)
    df_ot.columns = [str(c).replace(' ','').strip() for c in df_ot.columns]
    
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

    with st.sidebar:
        st.subheader("Filter")
        ot_month_opt = st.selectbox("조회 기간", master_months)
        ot_team_opt = st.selectbox("소속 팀", master_teams)
        target_ratio = st.slider("전년 대비 목표 (%)", 80, 120, 90)

    # 데이터 필터링
    df_filtered = df_ot.copy()
    if ot_month_opt != "전체 누적":
        df_filtered = df_filtered[df_filtered['월'] == ot_month_opt]
    if ot_team_opt != "전체 팀":
        df_filtered = df_filtered[df_filtered['팀명'] == ot_team_opt]

    st.markdown(f"""
        <div class="modern-header">
            <h1>⏰ 연장근무 관리</h1>
            <p>Status: {ot_team_opt} / {ot_month_opt}</p>
        </div>
    """, unsafe_allow_html=True)

    view_mode = st.radio("VIEW MODE", ["📊 통합 현황", "📈 주간 추이"], horizontal=True, label_visibility="collapsed")
    st.markdown("---")

    # [통합 로직]
    total_sum = df_filtered['총근무'].sum()
    ext_sum = df_filtered[[c for c in df_ot.columns if '연장' in c]].sum().sum()
    night_sum = df_filtered[[c for c in df_ot.columns if '야근' in c]].sum().sum()
    hol_sum = df_filtered[[c for c in df_ot.columns if '휴일' in c]].sum().sum()
    
    ext_ratio = (ext_sum / total_sum * 100) if total_sum > 0 else 0
    night_ratio = (night_sum / total_sum * 100) if total_sum > 0 else 0
    hol_ratio = (hol_sum / total_sum * 100) if total_sum > 0 else 0

    target_val = total_sum * (target_ratio / 100)

    # 1. 통합 현황
    if view_mode == "📊 통합 현황":
        st.subheader("통합 연장근무 현황")
        
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f"""<div class="kpi-card" style="border-top-color: #4F46E5;"><div class="kpi-title">총 근무시간</div><div class="kpi-value">{total_sum:,.1f}h</div><div class="kpi-sub">Total Overtime</div></div>""", unsafe_allow_html=True)
        with k2:
            st.markdown(f"""<div class="kpi-card" style="border-top-color: #3B82F6;"><div class="kpi-title">연장 근로</div><div class="kpi-value">{ext_sum:,.1f}h</div><div class="kpi-sub">{ext_ratio:.1f}% (Blue)</div></div>""", unsafe_allow_html=True)
        with k3:
            st.markdown(f"""<div class="kpi-card" style="border-top-color: #EF4444;"><div class="kpi-title">야간 근로</div><div class="kpi-value">{night_sum:,.1f}h</div><div class="kpi-sub">{night_ratio:.1f}% (Red)</div></div>""", unsafe_allow_html=True)
        with k4:
            st.markdown(f"""<div class="kpi-card" style="border-top-color: #0EA5E9;"><div class="kpi-title">휴일 근로</div><div class="kpi-value">{hol_sum:,.1f}h</div><div class="kpi-sub">{hol_ratio:.1f}% (Sky)</div></div>""", unsafe_allow_html=True)

        st.markdown("---")
        
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("##### 🏢 팀별 근무 유형 비교")
            
            chart_teams = master_teams[1:] if ot_team_opt == "전체 팀" else [ot_team_opt]
            df_agg = df_filtered.groupby('팀명')[valid_num_cols].sum().reset_index()
            df_agg = df_agg.set_index('팀명').reindex(chart_teams).fillna(0).reset_index()
            
            df_long = df_agg.melt(id_vars='팀명', var_name='유형', value_name='시간')
            
            color_map = {
                '연장시간': '#3B82F6', '연장근로': '#3B82F6', # Blue
                '야근시간': '#EF4444', # Red
                '휴일시간': '#0EA5E9'  # Sky
            }
            
            fig = px.bar(df_long, x='시간', y='팀명', color='유형',
                         orientation='h', # 가로형
                         barmode='stack', # 누적형
                         color_discrete_map=color_map,
                         text_auto='.0f')
            
            fig.update_traces(textposition='auto', textfont_size=12, textfont_color='white')
            fig.update_layout(xaxis_title=None, yaxis_title=None, height=400, 
                              paper_bgcolor='white', plot_bgcolor='white',
                              font=dict(size=14))
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.markdown("##### 📅 월별 통합 추이")
            if '월' in df_ot.columns and not df_ot.empty:
                trend_df = df_ot.groupby('월')['총근무'].sum().reset_index()
                try:
                    trend_df['sort_key'] = trend_df['월'].apply(lambda x: int(re.sub(r'\D', '', str(x))) if re.sub(r'\D', '', str(x)) else 0)
                    trend_df = trend_df.sort_values('sort_key')
                except: pass
                
                fig2 = px.area(trend_df, x='월', y='총근무', markers=True)
                fig2.update_traces(line_color='#4318FF', fillcolor='rgba(67, 24, 255, 0.1)')
                fig2.update_layout(xaxis_title=None, yaxis_title=None, height=400, paper_bgcolor='white', plot_bgcolor='white')
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("데이터 없음")

    # 2. 주간 추이
    elif view_mode == "📈 주간 추이":
        st.subheader("주간 진행 현황")
        
        if '주차' in df_filtered.columns:
            c_w1, c_w2 = st.columns([1, 1])
            with c_w1:
                st.markdown("##### 📊 주차별 합계")
                week_chart = df_filtered.groupby(['주차', '팀명'])['총근무'].sum().reset_index()
                if not week_chart.empty:
                    fig3 = px.bar(week_chart, x='주차', y='총근무', color='팀명', barmode='group', color_discrete_sequence=px.colors.qualitative.Prism)
                    fig3.update_traces(textfont_color='white')
                    fig3.update_layout(height=400, paper_bgcolor='white', plot_bgcolor='white')
                    st.plotly_chart(fig3, use_container_width=True)
                else:
                    st.info("데이터가 없습니다.")
            with c_w2:
                st.markdown("##### 📉 누적 추이")
                if not week_chart.empty:
                    try:
                        week_chart['주차_num'] = week_chart['주차'].apply(lambda x: int(re.sub(r'\D', '', str(x))) if re.sub(r'\D', '', str(x)) else 0)
                        week_chart = week_chart.sort_values('주차_num')
                    except: pass
                    
                    week_chart['누적근무'] = week_chart.groupby('팀명')['총근무'].cumsum()
                    fig4 = px.line(week_chart, x='주차', y='누적근무', color='팀명', markers=True, color_discrete_sequence=px.colors.qualitative.Prism)
                    fig4.update_layout(height=400, paper_bgcolor='white', plot_bgcolor='white')
                    st.plotly_chart(fig4, use_container_width=True)
        else:
            st.warning("'주차' 컬럼이 없어 주간 추이를 표시할 수 없습니다.")

    st.divider()
    st.subheader("🗓️ 상세 근무 내역")
    
    # [수정] 헤더 UI 적용
    st.markdown("""
        <div class="custom-header">
            <div class="row-item">월/주차</div>
            <div class="row-item">팀명</div>
            <div class="row-item">이름</div>
            <div class="row-item" style="color:#3B82F6;">연장</div>
            <div class="row-item" style="color:#EF4444;">야근</div>
            <div class="row-item" style="color:#0EA5E9;">휴일</div>
            <div class="row-item" style="font-weight:bold;">합계</div>
        </div>
    """, unsafe_allow_html=True)

    if not df_filtered.empty:
        sort_cols = [c for c in ['월', '주차', '팀명'] if c in df_filtered.columns]
        df_show_ot = df_filtered.sort_values(sort_cols).reset_index(drop=True)

        with st.container(height=500):
            for _, row in df_show_ot.iterrows():
                ext = row.get('연장근로', row.get('연장시간', 0))
                night = row.get('야근시간', 0)
                hol = row.get('휴일시간', 0)
                week_str = row.get('주차', '')
                
                st.markdown(f"""
                    <div class="custom-row">
                        <div class="row-item" style="color:#64748B;">{row['월']} {week_str}</div>
                        <div class="row-item"><strong>{row['팀명']}</strong></div>
                        <div class="row-item">{row['이름']}</div>
                        <div class="row-item" style="color:#3B82F6;">{ext:.1f}</div>
                        <div class="row-item" style="color:#EF4444;">{night:.1f}</div>
                        <div class="row-item" style="color:#0EA5E9;">{hol:.1f}</div>
                        <div class="row-item" style="font-weight:bold; background-color:#EFF4FB; border-radius:4px; color:#2B3674;">{row['총근무']:.1f}h</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("내역이 없습니다.")
