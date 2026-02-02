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

# [CSS] 프리미엄 UI 디자인 (제목 디자인 개선 & 메뉴 폰트 확대)
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

        /* 커스텀 KPI 카드 (Shiftee Style) */
        .kpi-card {
            background-color: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0px 4px 12px rgba(112, 144, 176, 0.08);
            border: 1px solid #E2E8F0;
            border-top: 5px solid #3B82F6;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .kpi-title { color: #64748B; font-size: 0.9rem; font-weight: 600; margin-bottom: 8px; }
        .kpi-value { color: #1E293B; font-size: 2.2rem; font-weight: 800; letter-spacing: -1px; }
        .kpi-sub { color: #94A3B8; font-size: 0.85rem; margin-top: 4px; font-weight: 500; }

        /* [NEW] 모던 헤더 디자인 (이미지 없이 CSS로 구현) */
        .modern-header {
            background: white;
            padding: 20px 30px;
            border-radius: 16px;
            box-shadow: 0px 2px 10px rgba(0,0,0,0.03);
            margin-bottom: 20px;
            border-left: 8px solid #4318FF;
            display: flex;
            flex-direction: column;
        }
        .modern-header h1 {
            margin: 0;
            font-size: 1.8rem;
            color: #2B3674;
            font-weight: 800;
        }
        .modern-header p {
            margin: 5px 0 0 0;
            color: #A3AED0;
            font-size: 0.9rem;
            font-weight: 500;
        }

        /* 커스텀 리스트 행 */
        .custom-row {
            background-color: white;
            border-bottom: 1px solid #F4F7FE;
            padding: 16px 10px;
            display: flex;
            align-items: center;
            transition: all 0.2s ease;
            border-radius: 12px;
        }
        .custom-row:hover { background-color: #F4F7FE; transform: translateX(5px); }
        
        .custom-header {
            background-color: #F4F7FE;
            border-radius: 12px;
            padding: 12px 10px;
            font-weight: 600;
            color: #A3AED0;
            font-size: 0.85rem;
            display: flex;
            align-items: center;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .row-item { flex: 1; text-align: center; font-size: 0.95rem; color: #2B3674; font-weight: 500; }
        .row-item-left { flex: 1; text-align: left; padding-left: 20px; font-size: 0.95rem; color: #2B3674; font-weight: 500; }
        
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

        /* [NEW] 메뉴 스타일 개선 (간격 및 폰트 확대) */
        div.row-widget.stRadio > div {
            gap: 15px; /* 메뉴 간격 확대 */
        }
        div.row-widget.stRadio > div[role="radiogroup"] > label {
            border-radius: 12px;
            padding: 15px 20px; /* 패딩 확대 */
            text-align: center;
            font-weight: 600;
            color: #64748B;
            border: 1px solid transparent;
            transition: all 0.2s;
            box-shadow: 0 2px 5px rgba(0,0,0,0.02);
            background-color: white;
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
        }
        div.row-widget.stRadio > div[role="radiogroup"] > label p {
            font-size: 1.15rem !important; /* 폰트 확대 (+2px 느낌) */
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

    # [UI] 모던 헤더 적용
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
        tot_b =
