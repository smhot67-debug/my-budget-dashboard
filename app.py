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
    page_title="Enterprise Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# [CSS] 프리미엄 모던 UI 디자인
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            background-attachment: fixed;
        }
        
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1400px;
        }

        /* 글래스모피즘 카드 */
        .glass-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 32px;
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.3);
            margin-bottom: 24px;
        }

        /* 헤더 디자인 */
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 45px;
            border-radius: 24px;
            margin-bottom: 32px;
            box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
            position: relative;
            overflow: hidden;
        }
        
        .main-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
            opacity: 0.4;
        }
        
        .main-header h1 {
            margin: 0;
            font-size: 2.5rem;
            color: white;
            font-weight: 800;
            position: relative;
            letter-spacing: -0.5px;
        }
        
        .main-header p {
            margin: 12px 0 0 0;
            color: rgba(255, 255, 255, 0.9);
            font-size: 1.1rem;
            font-weight: 500;
            position: relative;
        }

        /* 메트릭 카드 */
        .metric-card {
            background: white;
            border-radius: 20px;
            padding: 28px 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border: 1px solid rgba(0, 0, 0, 0.05);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            height: 100%;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);
        }
        
        .metric-label {
            color: #8B92A8;
            font-size: 0.875rem;
            font-weight: 600;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .metric-value {
            color: #1A202C;
            font-size: 2.25rem;
            font-weight: 800;
            letter-spacing: -1px;
            margin-bottom: 8px;
        }
        
        .metric-delta {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 700;
            margin-top: 8px;
        }
        
        .metric-delta.positive {
            background: #D1FAE5;
            color: #065F46;
        }
        
        .metric-delta.negative {
            background: #FEE2E2;
            color: #991B1B;
        }
        
        .metric-delta.neutral {
            background: #E0E7FF;
            color: #3730A3;
        }

        /* 섹션 헤더 */
        .section-header {
            font-size: 1.5rem;
            font-weight: 700;
            color: #1A202C;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .section-header::before {
            content: '';
            width: 4px;
            height: 28px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 4px;
        }

        /* 테이블 스타일 */
        .data-table {
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
        }
        
        .table-header {
            background: linear-gradient(135deg, #F7FAFC 0%, #EDF2F7 100%);
            padding: 16px 20px;
            display: flex;
            align-items: center;
            font-weight: 700;
            font-size: 0.875rem;
            color: #4A5568;
            border-bottom: 2px solid #E2E8F0;
        }
        
        .table-row {
            background: white;
            padding: 18px 20px;
            display: flex;
            align-items: center;
            border-bottom: 1px solid #F7FAFC;
            transition: all 0.2s ease;
        }
        
        .table-row:hover {
            background: #F8FAFC;
            transform: translateX(4px);
        }
        
        .table-cell {
            flex: 1;
            text-align: center;
            font-size: 0.9rem;
            color: #2D3748;
            font-weight: 500;
        }
        
        .table-cell-left {
            flex: 1;
            text-align: left;
            font-size: 0.9rem;
            color: #2D3748;
            font-weight: 500;
        }
        
        .table-cell strong {
            color: #1A202C;
            font-weight: 700;
        }

        /* 배지 */
        .badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.3px;
        }
        
        .badge-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .badge-success {
            background: #D1FAE5;
            color: #065F46;
        }
        
        .badge-warning {
            background: #FEF3C7;
            color: #92400E;
        }
        
        .badge-danger {
            background: #FEE2E2;
            color: #991B1B;
        }
        
        .badge-info {
            background: #DBEAFE;
            color: #1E40AF;
        }

        /* 진행바 */
        .progress-container {
            background: #F1F5F9;
            height: 10px;
            border-radius: 10px;
            overflow: hidden;
            margin: 12px 0;
        }
        
        .progress-bar {
            height: 100%;
            border-radius: 10px;
            transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        }
        
        .progress-bar.warning {
            background: linear-gradient(90deg, #F59E0B 0%, #D97706 100%);
        }
        
        .progress-bar.danger {
            background: linear-gradient(90deg, #EF4444 0%, #DC2626 100%);
        }

        /* 요약 카드 */
        .summary-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 24px;
            padding: 32px;
            color: white;
            box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
            margin-bottom: 28px;
        }
        
        .summary-item {
            text-align: center;
            padding: 0 20px;
        }
        
        .summary-label {
            font-size: 0.875rem;
            opacity: 0.9;
            margin-bottom: 8px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .summary-value {
            font-size: 2rem;
            font-weight: 800;
            letter-spacing: -1px;
        }

        /* 사이드바 */
        [data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.98);
            backdrop-filter: blur(20px);
            box-shadow: 4px 0 20px rgba(0, 0, 0, 0.08);
        }
        
        [data-testid="stSidebar"] .sidebar-content {
            padding: 20px;
        }
        
        [data-testid="stSidebar"] h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            font-size: 1.5rem;
            margin-bottom: 24px;
        }

        /* 탭/라디오 버튼 */
        div.row-widget.stRadio > div {
            background: white;
            padding: 8px;
            border-radius: 16px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
            display: flex;
            gap: 8px;
            margin: 20px 0;
        }
        
        div.row-widget.stRadio > div[role="radiogroup"] > label {
            flex: 1;
            background: transparent;
            border-radius: 12px;
            padding: 14px 20px;
            text-align: center;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            border: none;
            margin: 0 !important;
        }
        
        div.row-widget.stRadio > div[role="radiogroup"] > label:hover {
            background: #F8FAFC;
            transform: translateY(-2px);
        }
        
        div.row-widget.stRadio > div[role="radiogroup"] > label[data-checked="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
            transform: translateY(-2px);
        }
        
        div.row-widget.stRadio > div[role="radiogroup"] > label p {
            font-size: 1rem !important;
            font-weight: 700 !important;
            margin: 0 !important;
        }
        
        div.row-widget.stRadio > div[role="radiogroup"] > label[data-checked="false"] p {
            color: #64748B !important;
        }
        
        div.row-widget.stRadio > div[role="radiogroup"] > label[data-checked="true"] p {
            color: white !important;
        }

        /* 스크롤바 */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #F1F5F9;
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #5568d3 0%, #653a8b 100%);
        }

        /* 버튼 */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 12px 24px;
            font-weight: 700;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
        }

        /* 인풋 필드 */
        .stSelectbox > div > div,
        .stTextInput > div > div {
            border-radius: 12px;
            border: 2px solid #E2E8F0;
            transition: all 0.3s ease;
        }
        
        .stSelectbox > div > div:focus-within,
        .stTextInput > div > div:focus-within {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        /* 차트 컨테이너 */
        .chart-container {
            background: white;
            border-radius: 20px;
            padding: 24px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
            margin-bottom: 24px;
        }

        /* 팀 카드 */
        .team-card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 16px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
            border-left: 4px solid #667eea;
            transition: all 0.3s ease;
        }
        
        .team-card:hover {
            transform: translateX(4px);
            box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
        }
        
        .team-name {
            font-weight: 700;
            font-size: 1.1rem;
            color: #1A202C;
            margin-bottom: 12px;
        }
        
        .team-stats {
            display: flex;
            justify-content: space-between;
            font-size: 0.875rem;
            color: #64748B;
            margin-top: 12px;
        }

        /* 구분선 */
        hr {
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, #E2E8F0, transparent);
            margin: 32px 0;
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
    st.error("🔌 데이터 연결 실패. 구글 시트를 확인해주세요.")
    if st.button("🔄 다시 시도"):
        st.cache_data.clear()
        st.rerun()
    st.stop()

# 시트 이름 매핑
sheet_keys = list(all_sheets.keys())
budget_sheet_name = next((s for s in sheet_keys if '기준' in s or 'Budget' in s), None)
expense_sheet_name = next((s for s in sheet_keys if '지출' in s or 'Expense' in s), None)
leave_sheet_name = next((s for s in sheet_keys if '원천' in s or 'Leave' in s), None)
overtime_sheet_name = next((s for s in sheet_keys if '연장' in s or 'Overtime' in s or '근무' in s), None)

# 마스터 데이터
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
# 3. 사이드바
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("# 📊 Analytics")
    st.markdown("---")
    
    menu = st.radio(
        "Navigation",
        ["💰 예산 관리", "🏖️ 연차 관리", "⏰ 연장근무 관리"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    if st.button("🔄 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.caption("💡 시트 수정 후 1~5분 내 반영")
    
    st.markdown("---")
    
    with st.expander("📱 QR 접속"):
        try:
            import qrcode
            default_url = "https://my-budget-dashboard-ebrzrzbmslu8xh6dphqtin.streamlit.app/"
            app_url = st.text_input("URL", value=default_url)
            if app_url:
                qr = qrcode.QRCode(box_size=10, border=1)
                qr.add_data(app_url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                st.image(buffer, use_container_width=True)
        except:
            st.info("QR 코드 라이브러리 필요")

# =============================================================================
# [PART A] 예산 관리
# =============================================================================
if menu == "💰 예산 관리":
    if not budget_sheet_name or not expense_sheet_name:
        st.error("예산 데이터를 찾을 수 없습니다.")
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
        df_expense['월'] = df_expense[date_col].dt.strftime('%Y-%m')
        df_expense['월_숫자'] = df_expense[date_col].dt.month
    else:
        df_expense['월'] = 'Unknown'
        df_expense['월_숫자'] = 0
    
    if '금액' in df_expense.columns:
        df_expense['금액'] = safe_numeric(df_expense['금액'])
    
    df_expense = df_expense[df_expense['금액'] != 0]

    with st.sidebar:
        st.markdown("### 🎯 Filter")
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

    # 헤더
    st.markdown(f"""
        <div class="main-header">
            <h1>💰 Budget Management Dashboard</h1>
            <p>{team_option} · {period_option}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # KPI 메트릭
    if cat_main == "전체":
        tot_b = df_dash['예산'].sum()
        tot_s = df_dash['사용액'].sum()
        tot_r = df_dash['잔액'].sum()
    else:
        tot_b = 0
        tot_s = df_detail_filtered['금액'].sum()
        tot_r = 0

    exec_rate = (tot_s / tot_b * 100) if tot_b > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">총 예산</div>
                <div class="metric-value">{tot_b/10000:,.0f}만</div>
                <div class="metric-delta neutral">Available</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">사용 금액</div>
                <div class="metric-value">{tot_s/10000:,.0f}만</div>
                <div class="metric-delta {'positive' if exec_rate < 80 else 'negative'}">{exec_rate:.1f}%</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">잔여 예산</div>
                <div class="metric-value">{tot_r/10000:,.0f}만</div>
                <div class="metric-delta {'positive' if tot_r > 0 else 'negative'}">Remaining</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">지출 건수</div>
                <div class="metric-value">{len(df_detail_filtered):,}</div>
                <div class="metric-delta neutral">Transactions</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # 차트 섹션
    col_chart, col_teams = st.columns([5, 5])
    
    with col_chart:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📊 예산 분포</div>', unsafe_allow_html=True)
        
        if tot_s > 0:
            fig = px.pie(
                df_dash, 
                values='사용액', 
                names='팀명', 
                hole=0.65,
                color_discrete_sequence=px.colors.sequential.Purples_r
            )
            fig.update_traces(
                textposition='outside',
                textinfo='percent+label',
                marker=dict(line=dict(color='white', width=2))
            )
            fig.update_layout(
                showlegend=False,
                height=400,
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', size=12, color='#1A202C')
            )
            
            fig.add_annotation(
                text=f"<b>{tot_s/10000:,.0f}</b><br><span style='font-size:14px'>만원</span>",
                x=0.5, y=0.5,
                font_size=28,
                showarrow=False,
                font_color="#1A202C"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📭 지출 데이터가 없습니다")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_teams:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">🏢 팀별 현황</div>', unsafe_allow_html=True)
        
        if not df_dash.empty:
            for _, row in df_dash.iterrows():
                pct = min(row['집행률'], 100)
                
                if pct < 70:
                    bar_color = "#10B981"
                    status = "양호"
                elif pct < 90:
                    bar_color = "#F59E0B"
                    status = "주의"
                else:
                    bar_color = "#EF4444"
                    status = "초과 주의"
                
                st.markdown(f"""
                    <div class="team-card">
                        <div class="team-name">{row['팀명']}</div>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <span style="font-size:0.875rem; color:#64748B;">집행률</span>
                            <span style="font-weight:700; font-size:1.1rem; color:{bar_color};">{pct:.1f}%</span>
                        </div>
                        <div class="progress-container">
                            <div class="progress-bar" style="width:{pct}%; background:{bar_color};"></div>
                        </div>
                        <div class="team-stats">
                            <span>예산 <strong>{row['예산']/10000:,.0f}만</strong></span>
                            <span>사용 <strong>{row['사용액']/10000:,.0f}만</strong></span>
                            <span>잔액 <strong>{row['잔액']/10000:,.0f}만</strong></span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📭 데이터 없음")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # 상세 내역
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📋 지출 내역</div>', unsafe_allow_html=True)
    
    if not df_detail_filtered.empty:
        df_show = df_detail_filtered.sort_values('날짜', ascending=False).reset_index(drop=True)
        
        st.markdown("""
            <div class="table-header">
                <div class="table-cell">날짜</div>
                <div class="table-cell">부서</div>
                <div class="table-cell">대분류</div>
                <div class="table-cell">소분류</div>
                <div class="table-cell-left" style="flex:2;">적요</div>
                <div class="table-cell" style="text-align:right;">금액</div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container(height=400):
            for _, row in df_show.iterrows():
                date_str = row['날짜'].strftime('%Y-%m-%d')
                amt_str = f"{int(row['금액']):,}원"
                
                st.markdown(f"""
                    <div class="table-row">
                        <div class="table-cell" style="color:#64748B; font-size:0.85rem;">{date_str}</div>
                        <div class="table-cell"><strong>{row['팀명']}</strong></div>
                        <div class="table-cell"><span class="badge badge-info">{row['대분류']}</span></div>
                        <div class="table-cell"><span class="badge badge-primary">{row['소분류']}</span></div>
                        <div class="table-cell-left" style="flex:2; color:#475569;">{row['상세내역']}</div>
                        <div class="table-cell" style="text-align:right; font-weight:700; color:#1A202C;">{amt_str}</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("📭 지출 내역이 없습니다")
    
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# [PART B] 연차 관리
# =============================================================================
elif menu == "🏖️ 연차 관리":
    if not leave_sheet_name:
        st.error("연차 데이터를 찾을 수 없습니다.")
        st.stop()

    df_leave = all_sheets[leave_sheet_name].fillna(0)
    df_leave['소속'] = df_leave['소속'].apply(clean_dept_name)
    for col in ['합계', '사용일수', '잔여일수', '부채예산', '부채잔액']:
        if col in df_leave.columns: df_leave[col] = safe_numeric(df_leave[col])

    with st.sidebar:
        st.markdown("### 🎯 Filter")
        leave_month_list = ["전체 누적"] + [f"{i}월" for i in range(1, 13)]
        leave_period_option = st.selectbox("기간", leave_month_list)
        
        leave_dept_option = st.selectbox("소속", master_teams)
        risk_criteria = st.slider("촉진 대상 기준", 5, 25, 10)

    if leave_dept_option != "전체 팀":
        df_leave = df_leave[df_leave['소속'] == leave_dept_option]

    if leave_period_option != "전체 누적":
        target_col = leave_period_option
        if target_col in df_leave.columns:
             df_leave['당월사용'] = safe_numeric(df_leave[target_col])
             display_usage_col = '당월사용'
        else:
             st.warning(f"'{target_col}' 데이터가 없습니다. 전체 누적으로 표시합니다.")
             display_usage_col = '사용일수'
    else:
        display_usage_col = '사용일수'

    df_risk = df_leave[df_leave['잔여일수'] >= risk_criteria].sort_values('잔여일수', ascending=False)
    
    total_used = df_leave[display_usage_col].sum()
    total_remain = df_leave['잔여일수'].sum()
    avg_usage = (total_used / df_leave['합계'].sum() * 100) if df_leave['합계'].sum() > 0 else 0
    tot_liab = df_leave['부채잔액'].sum()

    # 헤더
    st.markdown(f"""
        <div class="main-header">
            <h1>🏖️ Annual Leave Management</h1>
            <p>{leave_dept_option} · {leave_period_option}</p>
        </div>
    """, unsafe_allow_html=True)

    # KPI 메트릭
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    
    with k1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">소진율</div>
                <div class="metric-value">{avg_usage:.1f}%</div>
                <div class="metric-delta {'positive' if avg_usage >= 60 else 'negative'}">Target 60%</div>
            </div>
        """, unsafe_allow_html=True)
    
    with k2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">사용 연차</div>
                <div class="metric-value">{total_used:,.0f}</div>
                <div class="metric-delta neutral">일</div>
            </div>
        """, unsafe_allow_html=True)
    
    with k3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">잔여 연차</div>
                <div class="metric-value">{total_remain:,.0f}</div>
                <div class="metric-delta neutral">일</div>
            </div>
        """, unsafe_allow_html=True)
    
    with k4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">부채 예상</div>
                <div class="metric-value">{tot_liab/100000000:.2f}</div>
                <div class="metric-delta negative">억원</div>
            </div>
        """, unsafe_allow_html=True)
    
    with k5:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">촉진 대상</div>
                <div class="metric-value">{len(df_risk)}</div>
                <div class="metric-delta {'negative' if len(df_risk) > 0 else 'positive'}">명</div>
            </div>
        """, unsafe_allow_html=True)
    
    with k6:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">평균 잔여</div>
                <div class="metric-value">{df_leave['잔여일수'].mean():.1f}</div>
                <div class="metric-delta neutral">일</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # 차트 섹션
    c_chart, c_risk = st.columns([5, 5])
    
    with c_chart:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📊 부서별 소진율</div>', unsafe_allow_html=True)
        
        dept_sum = df_leave.groupby('소속').agg({display_usage_col:'sum', '합계':'sum'}).reset_index()
        dept_sum['소진율'] = (dept_sum[display_usage_col] / dept_sum['합계'] * 100).fillna(0)
        
        fig = px.bar(
            dept_sum, 
            x='소속', 
            y='소진율',
            color='소진율',
            color_continuous_scale='Purples'
        )
        fig.update_traces(
            texttemplate='%{y:.1f}%',
            textposition='outside',
            textfont_color='#1A202C'
        )
        fig.update_layout(
            xaxis_title=None,
            yaxis_title=None,
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='#1A202C'),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with c_risk:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">🚨 촉진 대상자</div>', unsafe_allow_html=True)
        
        if not df_risk.empty:
            r_tot = df_risk['합계'].sum()
            r_use = df_risk['사용일수'].sum()
            r_rem = df_risk['잔여일수'].sum()
            r_rate = (r_use / r_tot * 100) if r_tot > 0 else 0
            
            st.markdown(f"""
                <div class="summary-card">
                    <div style="display:flex; justify-content:space-around;">
                        <div class="summary-item">
                            <div class="summary-label">총 연차</div>
                            <div class="summary-value">{r_tot:,.0f}</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-label">사용</div>
                            <div class="summary-value">{r_use:,.0f}</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-label">잔여</div>
                            <div class="summary-value">{r_rem:,.0f}</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-label">소진율</div>
                            <div class="summary-value">{r_rate:.1f}%</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            with st.container(height=250):
                for _, row in df_risk.iterrows():
                    st.markdown(f"""
                        <div class="table-row">
                            <div class="table-cell"><strong>{row['성명']}</strong></div>
                            <div class="table-cell" style="color:#64748B;">{row['소속']}</div>
                            <div class="table-cell"><span class="badge badge-danger">{row['잔여일수']:.0f}일</span></div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.success("✅ 촉진 대상자 없음")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # 전체 명부
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">👥 임직원 현황</div>', unsafe_allow_html=True)
    
    df_show = df_leave.sort_values('소속').copy()
    usage_header = "사용(누적)" if leave_period_option == "전체 누적" else f"사용({leave_period_option})"
    
    st.markdown(f"""
        <div class="table-header">
            <div class="table-cell">소속</div>
            <div class="table-cell">성명</div>
            <div class="table-cell">총 연차</div>
            <div class="table-cell">{usage_header}</div>
            <div class="table-cell">잔여</div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container(height=500):
        for _, row in df_show.iterrows():
            st.markdown(f"""
                <div class="table-row">
                    <div class="table-cell" style="color:#64748B;">{row['소속']}</div>
                    <div class="table-cell"><strong>{row['성명']}</strong></div>
                    <div class="table-cell">{row['합계']:.1f}</div>
                    <div class="table-cell">{row[display_usage_col]:.1f}</div>
                    <div class="table-cell"><span class="badge badge-primary">{row['잔여일수']:.1f}</span></div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# [PART C] 연장근무 관리
# =============================================================================
elif menu == "⏰ 연장근무 관리":
    if not overtime_sheet_name:
        st.error("연장근무 데이터를 찾을 수 없습니다.")
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
        st.markdown("### 🎯 Filter")
        ot_month_opt = st.selectbox("조회 기간", master_months)
        ot_team_opt = st.selectbox("소속 팀", master_teams)
        target_ratio = st.slider("전년 대비 목표", 80, 120, 90)

    df_filtered = df_ot.copy()
    if ot_month_opt != "전체 누적":
        df_filtered = df_filtered[df_filtered['월'] == ot_month_opt]
    if ot_team_opt != "전체 팀":
        df_filtered = df_filtered[df_filtered['팀명'] == ot_team_opt]

    # 헤더
    st.markdown(f"""
        <div class="main-header">
            <h1>⏰ Overtime Management</h1>
            <p>{ot_team_opt} · {ot_month_opt}</p>
        </div>
    """, unsafe_allow_html=True)

    # 뷰 모드
    view_mode = st.radio(
        "VIEW",
        ["📊 통합 현황", "📈 주간 추이"],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    # 통계
    total_sum = df_filtered['총근무'].sum()
    ext_sum = df_filtered[[c for c in df_ot.columns if '연장' in c]].sum().sum()
    night_sum = df_filtered[[c for c in df_ot.columns if '야근' in c]].sum().sum()
    hol_sum = df_filtered[[c for c in df_ot.columns if '휴일' in c]].sum().sum()
    
    ext_ratio = (ext_sum / total_sum * 100) if total_sum > 0 else 0
    night_ratio = (night_sum / total_sum * 100) if total_sum > 0 else 0
    hol_ratio = (hol_sum / total_sum * 100) if total_sum > 0 else 0

    if view_mode == "📊 통합 현황":
        # KPI
        k1, k2, k3, k4 = st.columns(4)
        
        with k1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">총 근무시간</div>
                    <div class="metric-value">{total_sum:,.0f}h</div>
                    <div class="metric-delta neutral">Total</div>
                </div>
            """, unsafe_allow_html=True)
        
        with k2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">연장 근로</div>
                    <div class="metric-value">{ext_sum:,.0f}h</div>
                    <div class="metric-delta neutral">{ext_ratio:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
        
        with k3:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">야간 근로</div>
                    <div class="metric-value">{night_sum:,.0f}h</div>
                    <div class="metric-delta negative">{night_ratio:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)
        
        with k4:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">휴일 근로</div>
                    <div class="metric-value">{hol_sum:,.0f}h</div>
                    <div class="metric-delta neutral">{hol_ratio:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        
        # 차트
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-header">🏢 팀별 비교</div>', unsafe_allow_html=True)
            
            chart_teams = master_teams[1:] if ot_team_opt == "전체 팀" else [ot_team_opt]
            df_agg = df_filtered.groupby('팀명')[valid_num_cols].sum().reset_index()
            df_agg = df_agg.set_index('팀명').reindex(chart_teams).fillna(0).reset_index()
            df_long = df_agg.melt(id_vars='팀명', var_name='유형', value_name='시간')
            
            color_map = {
                '연장시간': '#667eea', '연장근로': '#667eea',
                '야근시간': '#EF4444',
                '휴일시간': '#06B6D4'
            }
            
            fig = px.bar(
                df_long,
                x='시간',
                y='팀명',
                color='유형',
                orientation='h',
                barmode='stack',
                color_discrete_map=color_map
            )
            fig.update_traces(texttemplate='%{x:.0f}', textposition='auto')
            fig.update_layout(
                xaxis_title=None,
                yaxis_title=None,
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter', color='#1A202C')
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with c2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-header">📅 월별 추이</div>', unsafe_allow_html=True)
            
            if '월' in df_ot.columns:
                trend_df = df_ot.groupby('월')['총근무'].sum().reset_index()
                try:
                    trend_df['sort_key'] = trend_df['월'].apply(lambda x: int(re.sub(r'\D', '', str(x))) if re.sub(r'\D', '', str(x)) else 0)
                    trend_df = trend_df.sort_values('sort_key')
                except: pass
                
                fig2 = px.area(trend_df, x='월', y='총근무', markers=True)
                fig2.update_traces(
                    line_color='#667eea',
                    fillcolor='rgba(102, 126, 234, 0.2)',
                    marker=dict(size=8, color='#764ba2')
                )
                fig2.update_layout(
                    xaxis_title=None,
                    yaxis_title=None,
                    height=400,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family='Inter', color='#1A202C')
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("데이터 없음")
            
            st.markdown('</div>', unsafe_allow_html=True)

    elif view_mode == "📈 주간 추이":
        if '주차' in df_filtered.columns:
            c_w1, c_w2 = st.columns(2)
            
            with c_w1:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-header">📊 주차별 합계</div>', unsafe_allow_html=True)
                
                week_chart = df_filtered.groupby(['주차', '팀명'])['총근무'].sum().reset_index()
                if not week_chart.empty:
                    fig3 = px.bar(
                        week_chart,
                        x='주차',
                        y='총근무',
                        color='팀명',
                        barmode='group',
                        color_discrete_sequence=px.colors.sequential.Purples_r
                    )
                    fig3.update_layout(
                        height=400,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family='Inter', color='#1A202C')
                    )
                    st.plotly_chart(fig3, use_container_width=True)
                else:
                    st.info("데이터 없음")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with c_w2:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('<div class="section-header">📉 누적 추이</div>', unsafe_allow_html=True)
                
                if not week_chart.empty:
                    try:
                        week_chart['주차_num'] = week_chart['주차'].apply(lambda x: int(re.sub(r'\D', '', str(x))) if re.sub(r'\D', '', str(x)) else 0)
                        week_chart = week_chart.sort_values('주차_num')
                    except: pass
                    
                    week_chart['누적근무'] = week_chart.groupby('팀명')['총근무'].cumsum()
                    fig4 = px.line(
                        week_chart,
                        x='주차',
                        y='누적근무',
                        color='팀명',
                        markers=True,
                        color_discrete_sequence=px.colors.sequential.Purples_r
                    )
                    fig4.update_layout(
                        height=400,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(family='Inter', color='#1A202C')
                    )
                    st.plotly_chart(fig4, use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("'주차' 데이터가 없습니다")

    # 상세 내역
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-header">🗓️ 상세 내역</div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="table-header">
            <div class="table-cell">월</div>
            <div class="table-cell">팀명</div>
            <div class="table-cell">이름</div>
            <div class="table-cell">연장</div>
            <div class="table-cell">야근</div>
            <div class="table-cell">휴일</div>
            <div class="table-cell">합계</div>
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
                
                st.markdown(f"""
                    <div class="table-row">
                        <div class="table-cell" style="color:#64748B;">{row['월']}</div>
                        <div class="table-cell"><strong>{row['팀명']}</strong></div>
                        <div class="table-cell">{row['이름']}</div>
                        <div class="table-cell" style="color:#667eea; font-weight:600;">{ext:.1f}</div>
                        <div class="table-cell" style="color:#EF4444; font-weight:600;">{night:.1f}</div>
                        <div class="table-cell" style="color:#06B6D4; font-weight:600;">{hol:.1f}</div>
                        <div class="table-cell"><span class="badge badge-primary">{row['총근무']:.1f}h</span></div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("📭 내역이 없습니다")
    
    st.markdown('</div>', unsafe_allow_html=True)
