import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import qrcode
from io import BytesIO
from datetime import datetime
from dateutil.relativedelta import relativedelta

# -----------------------------------------------------------------------------
# 1. 시스템 설정 및 디자인
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="통합 관리 시스템",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# [CSS] 프리미엄 UI 디자인
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

        .material-symbols-rounded { font-family: 'Material Symbols Rounded' !important; }
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

        /* 모던 헤더 */
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

        /* KPI 카드 */
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
        
        .custom-header {
            background-color: #EEF2FF; 
            border-radius: 12px;
            padding: 16px 10px;
            font-weight: 700;
            color: #4318FF; 
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border: 1px solid #E0E7FF;
        }
        .custom-header .row-item, .custom-header .row-item-left {
            color: #4318FF !important;
            font-weight: 800 !important;
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
# 2. 데이터 로드 및 유틸리티
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

# [Helper] 전월 구하기 (자동 필터용)
def get_default_month_index(options):
    today = datetime.now()
    prev_month = today - relativedelta(months=1)
    prev_month_str = f"2026-{prev_month.strftime('%m')}" 
    
    for i, opt in enumerate(options):
        if prev_month_str in opt:
            return i
    return 0 

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
        teams = [t for t in teams if t != '0' and t != 'nan']
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
    
    df_budget = df_budget[df_budget['팀명'].astype(str) != '0']

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
        st.subheader("Filter")
        default_idx = get_default_month_index(master_months)
        period_option = st.selectbox("기간", master_months, index=default_idx)
        
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
    target_year = master_months[1].split('-')[0] if len(master_months) > 1 else '2026'

    for team in target_teams:
        team_base_monthly = df_budget.loc[df_budget['팀명'] == team, '월기본예산'].sum()
        
        final_budget = 0
        final_spent = 0
        final_balance = 0
        
        if period_option == "전체 누적":
            # [1월 분리 로직] 실적관리는 2월~12월만 합산
            total_budget = team_base_monthly * 11
            total_add = 0
            for m in range(2, 13):
                col_name = f"{m}월_추가"
                if col_name in df_budget.columns:
                    total_add += df_budget.loc[df_budget['팀명'] == team, col_name].sum()
            
            final_budget = total_budget + total_add
            
            months_to_include = [f"{target_year}-{str(x).zfill(2)}" for x in range(2, 13)]
            final_spent = monthly_exp[(monthly_exp['팀명'] == team) & (monthly_exp['월'].isin(months_to_include))]['금액'].sum()
            final_balance = final_budget - final_spent
            
        else:
            try: target_month_idx = int(period_option.split('-')[1])
            except: target_month_idx = 1
            
            if target_month_idx == 1:
                # 1월은 1월 데이터만 계산 (이월 없음)
                col_name = "1월_추가"
                this_add = df_budget.loc[df_budget['팀명'] == team, col_name].sum() if col_name in df_budget.columns else 0
                
                final_budget = team_base_monthly + this_add
                final_spent = monthly_exp[(monthly_exp['팀명'] == team) & (monthly_exp['월'] == period_option)]['금액'].sum()
                final_balance = final_budget - final_spent
            else:
                # 2월부터는 누적 계산 (단, 1월은 제외하고 2월을 베이스캠프로 시작)
                cumulative_balance = 0
                for m in range(2, target_month_idx + 1):
                    month_str = f"{target_year}-{str(m).zfill(2)}"
                    
                    col_name = f"{m}월_추가"
                    this_add = df_budget.loc[df_budget['팀명'] == team, col_name].sum() if col_name in df_budget.columns else 0
                    
                    available = cumulative_balance + team_base_monthly + this_add
                    spent = monthly_exp[(monthly_exp['팀명'] == team) & (monthly_exp['월'] == month_str)]['금액'].sum()
                    
                    current_balance = available - spent
                    cumulative_balance = current_balance

                    if m == target_month_idx:
                        final_budget = available 
                        final_spent = spent
                        final_balance = current_balance

        dashboard_rows.append({
            '팀명': team,
            '예산': final_budget,
            '사용액': final_spent,
            '잔액': final_balance,
            '집행률': (final_spent / final_budget * 100) if final_budget > 0 else 0
        })

    df_dash = pd.DataFrame(dashboard_rows)
    
    df_detail_filtered = df_expense.copy()
    if period_option == "전체 누적":
        # 전체 누적 시 1월 상세 내역 제외
        df_detail_filtered = df_detail_filtered[df_detail_filtered['월_숫자'] >= 2]
    else:
        df_detail_filtered = df_detail_filtered[df_detail_filtered['월'] == period_option]
        
    if team_option != "전체 팀":
        df_detail_filtered = df_detail_filtered[df_detail_filtered['팀명'] == team_option]
    if cat_main != "전체": df_detail_filtered = df_detail_filtered[df_detail_filtered['대분류'] == cat_main]
    if cat_sub != "전체": df_detail_filtered = df_detail_filtered[df_detail_filtered['소분류'] == cat_sub]

    notice_msg = " (※ 실적 관리: 2월~12월 기준)" if period_option == "전체 누적" else ""
    st.markdown(f"""
        <div class="modern-header">
            <h1>💰 예산 관리 대시보드</h1>
            <p>Status: {team_option} / {period_option}{notice_msg}</p>
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

    total_rate = (tot_s / tot_b * 100) if tot_b > 0 else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("가용 예산 (이월포함)", f"{tot_b:,.0f}원")
    c2.metric("총 사용액", f"{tot_s:,.0f}원")
    c3.metric("총 집행률", f"{total_rate:.1f}%", delta="Status")
    c4.metric("현재 잔액", f"{tot_r:,.0f}원", delta="Remain")
    c5.metric("지출 건수", f"{len(df_detail_filtered):,}건")

    st.divider()

    st.subheader("🏢 팀별 집행 현황")
    
    if not df_dash.empty:
        records = df_dash.to_dict('records')
        split_idx = (len(records) + 1) // 2 
        left_data = records[:split_idx]
        right_data = records[split_idx:]
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            for row in left_data:
                pct = min(row['집행률'], 100)
                status_color = "#3B82F6" if pct < 80 else ("#F59E0B" if pct < 100 else "#EF4444")
                
                st.markdown(f"""
                    <div style="background:white; padding:24px; border-radius:16px; margin-bottom:15px; box-shadow: 0px 4px 12px rgba(0,0,0,0.05); border:1px solid #E2E8F0;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                            <span style="font-weight:700; color:#1E293B; font-size:1.1rem;">{row['팀명']}</span>
                            <span style="font-weight:800; color:{status_color}; font-size:1.1rem;">{row['집행률']:.1f}%</span>
                        </div>
                        <div style="width:100%; background-color:#F1F5F9; height:10px; border-radius:5px; margin-bottom:15px;">
                            <div style="width:{pct}%; background-color:{status_color}; height:10px; border-radius:5px;"></div>
                        </div>
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; font-size:0.9rem; color:#64748B;">
                            <div>예산: {row['예산']:,.0f}</div>
                            <div style="text-align:right;">사용: <strong style="color:#1E293B;">{row['사용액']:,.0f}</strong></div>
                            <div style="grid-column: span 2; text-align:right; border-top:1px solid #F1F5F9; padding-top:8px;">
                                잔액: <strong style="color:{status_color}; font-size:1rem;">{row['잔액']:,.0f}</strong>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        with col_right:
            for row in right_data:
                pct = min(row['집행률'], 100)
                status_color = "#3B82F6" if pct < 80 else ("#F59E0B" if pct < 100 else "#EF4444")
                
                st.markdown(f"""
                    <div style="background:white; padding:24px; border-radius:16px; margin-bottom:15px; box-shadow: 0px 4px 12px rgba(0,0,0,0.05); border:1px solid #E2E8F0;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                            <span style="font-weight:700; color:#1E293B; font-size:1.1rem;">{row['팀명']}</span>
                            <span style="font-weight:800; color:{status_color}; font-size:1.1rem;">{row['집행률']:.1f}%</span>
                        </div>
                        <div style="width:100%; background-color:#F1F5F9; height:10px; border-radius:5px; margin-bottom:15px;">
                            <div style="width:{pct}%; background-color:{status_color}; height:10px; border-radius:5px;"></div>
                        </div>
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; font-size:0.9rem; color:#64748B;">
                            <div>예산: {row['예산']:,.0f}</div>
                            <div style="text-align:right;">사용: <strong style="color:#1E293B;">{row['사용액']:,.0f}</strong></div>
                            <div style="grid-column: span 2; text-align:right; border-top:1px solid #F1F5F9; padding-top:8px;">
                                잔액: <strong style="color:{status_color}; font-size:1rem;">{row['잔액']:,.0f}</strong>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("데이터 없음")

    st.subheader("📝 상세 지출 내역 (보안)")
    
    if 'budget_auth' not in st.session_state:
        st.session_state['budget_auth'] = False
        
    if not st.session_state['budget_auth']:
        col_pw1, col_pw2 = st.columns([2, 3])
        with col_pw1:
            pwd = st.text_input("관리자 비밀번호를 입력하세요", type="password")
            if pwd == "7026":
                st.session_state['budget_auth'] = True
                st.rerun()
            elif pwd:
                st.error("비밀번호가 올바르지 않습니다.")
    else:
        if not df_detail_filtered.empty:
            df_show = df_detail_filtered.sort_values('날짜', ascending=False).reset_index(drop=True)
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
    
    df_leave = df_leave[df_leave['소속'] != '대상델리하임']

    for col in ['합계', '사용일수', '잔여일수', '부채예산', '부채잔액']:
        if col in df_leave.columns: df_leave[col] = safe_numeric(df_leave[col])
        
    df_leave['잔여율'] = df_leave.apply(lambda x: (x['잔여일수'] / x['합계'] * 100) if x['합계'] > 0 else 0, axis=1)

    with st.sidebar:
        st.subheader("Filter")
        default_idx = get_default_month_index(master_months)
        leave_period_option = st.selectbox("기간(월)", master_months, index=default_idx)
        
        dept_list = master_teams 
        leave_dept_option = st.selectbox("소속 부서", dept_list)
        risk_criteria = st.slider("촉진 대상 기준 (잔여일)", 5, 25, 10)

    if leave_dept_option != "전체 팀":
        df_leave = df_leave[df_leave['소속'] == leave_dept_option]

    if leave_period_option != "전체 누적":
        target_col = leave_period_option.split('-')[1] + "월"
        if target_col not in df_leave.columns:
             try: target_col = f"{int(leave_period_option.split('-')[1])}월"
             except: pass
             
        if target_col in df_leave.columns:
             df_leave['당월사용'] = safe_numeric(df_leave[target_col])
             display_usage_col = '당월사용'
        else:
             st.warning(f"'{target_col}' 데이터가 없습니다. 누적 사용량으로 표시합니다.")
             display_usage_col = '사용일수'
    else:
        display_usage_col = '사용일수'

    df_risk = df_leave[df_leave['잔여일수'] >= risk_criteria].sort_values('잔여율', ascending=False)
    
    total_used = df_leave[display_usage_col].sum()
    total_remain = df_leave['잔여일수'].sum()
    avg_remain_rate = (total_remain / df_leave['합계'].sum() * 100) if df_leave['합계'].sum() > 0 else 0
    avg_usage = (total_used / df_leave['합계'].sum() * 100) if df_leave['합계'].sum() > 0 else 0

    st.markdown(f"""
        <div class="modern-header">
            <h1>🏖️ 연차 관리 대시보드</h1>
            <p>Status: {leave_dept_option} / {leave_period_option}</p>
        </div>
    """, unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric(f"소진율 ({leave_period_option})", f"{avg_usage:.1f}%", delta="Goal 50%")
    k2.metric("총 사용 연차", f"{total_used:,.1f}일")
    k3.metric("총 잔여 연차", f"{total_remain:,.1f}일")
    k4.metric("전사 평균 잔여율", f"{avg_remain_rate:.1f}%", delta="Down", delta_color="inverse")

    st.divider()

    c_chart, c_risk = st.columns([4, 6])
    with c_chart:
        st.subheader("📊 부서별 소진율")
        dept_sum = df_leave.groupby('소속').agg({display_usage_col:'sum', '합계':'sum'}).reset_index()
        dept_sum['소진율'] = (dept_sum[display_usage_col] / dept_sum['합계'] * 100).fillna(0)
        fig = px.bar(dept_sum, x='소속', y='소진율', text=dept_sum['소진율'].apply(lambda x: f"{x:.1f}%"), color='소진율', color_continuous_scale='Bluyl')
        fig.update_traces(textfont_color='white', textposition='auto')
        fig.update_layout(xaxis_title=None, yaxis_title="소진율(%)", height=450, paper_bgcolor='white', plot_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

    with c_risk:
        st.subheader(f"🚨 촉진 대상자 (High Residual Rate)")
        if not df_risk.empty:
            r_tot = df_risk['합계'].sum()
            r_use = df_risk['사용일수'].sum()
            r_rem = df_risk['잔여일수'].sum()
            r_rate = (r_rem / r_tot * 100) if r_tot > 0 else 0 
            
            st.markdown(f"""
                <div class="total-box">
                    <div><span class="total-label">대상자 총 연차</span><span class="total-value">{r_tot:,.1f}</span></div>
                    <div><span class="total-label">사용 총계</span><span class="total-value">{r_use:,.1f}</span></div>
                    <div><span class="total-label">잔여 총계</span><span class="total-value" style="color:#FCA5A5;">{r_rem:,.1f}</span></div>
                    <div><span class="total-label">평균 잔여율</span><span class="total-value">{r_rate:.1f}%</span></div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
                <div class="custom-header">
                    <div class="row-item">성명/직급</div>
                    <div class="row-item">소속</div>
                    <div class="row-item">잔여율</div>
                    <div class="row-item">비고</div>
                </div>
            """, unsafe_allow_html=True)

            with st.container(height=300):
                for _, row in df_risk.iterrows():
                    st.markdown(f"""
                        <div class="custom-row">
                            <div class="row-item"><strong>{row['성명']}</strong></div>
                            <div class="row-item" style="color:#64748B;">{row['소속']}</div>
                            <div class="row-item"><span class="badge badge-red">{row['잔여율']:.1f}%</span></div>
                            <div class="row-item" style="font-size:0.8rem; color:#94A3B8;">잔여 {row['잔여일수']:.1f}일 이상</div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.success("대상자 없음")

    st.divider()
    st.subheader("👥 전체 임직원 명부")
    df_show = df_leave.sort_values('소속').copy()
    
    st.markdown("""
        <div class="custom-header">
            <div class="row-item">소속</div>
            <div class="row-item">성명</div>
            <div class="row-item">잔여율</div>
        </div>
    """, unsafe_allow_html=True)
    with st.container(height=500):
        for _, row in df_show.iterrows():
            st.markdown(f"""
                <div class="custom-row">
                    <div class="row-item" style="color:#64748B;">{row['소속']}</div>
                    <div class="row-item"><strong>{row['성명']}</strong></div>
                    <div class="row-item"><span class="badge badge-blue">{row['잔여율']:.1f}%</span></div>
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
    
    df_ot['팀명'] = df_ot['팀명'].replace('지원팀', '경영지원팀')
    df_ot = df_ot[~df_ot['팀명'].isin(['생산팀', '대상델리하임'])]
    
    if '팀명' in df_ot.columns:
        df_ot['팀명'] = df_ot['팀명'].astype(str)

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
        default_idx = get_default_month_index(master_months)
        ot_month_opt = st.selectbox("조회 기간", master_months, index=default_idx)

        filtered_teams = sorted(df_ot['팀명'].unique())
        ot_team_opt = st.selectbox("소속 팀", ["전체 팀"] + filtered_teams)
        target_ratio = st.slider("전년 대비 목표 (%)", 80, 120, 90)

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

    view_mode = st.radio("VIEW MODE", ["📊 통합 현황"], horizontal=True, label_visibility="collapsed")
    st.markdown("---")

    total_sum = df_filtered['총근무'].sum()
    ext_sum = df_filtered[[c for c in df_ot.columns if '연장' in c]].sum().sum()
    night_sum = df_filtered[[c for c in df_ot.columns if '야근' in c]].sum().sum()
    hol_sum = df_filtered[[c for c in df_ot.columns if '휴일' in c]].sum().sum()
    
    ext_ratio = (ext_sum / total_sum * 100) if total_sum > 0 else 0
    night_ratio = (night_sum / total_sum * 100) if total_sum > 0 else 0
    hol_ratio = (hol_sum / total_sum * 100) if total_sum > 0 else 0

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
            
            chart_teams = [t for t in filtered_teams] if ot_team_opt == "전체 팀" else [ot_team_opt]
            df_agg = df_filtered.groupby('팀명')[valid_num_cols].sum().reset_index()
            df_agg = df_agg.set_index('팀명').reindex(chart_teams).fillna(0).reset_index()
            
            df_long = df_agg.melt(id_vars='팀명', var_name='유형', value_name='시간')
            
            color_map = {
                '연장시간': '#3B82F6', '연장근로': '#3B82F6', 
                '야근시간': '#EF4444', 
                '휴일시간': '#0EA5E9'
            }
            
            fig = px.bar(df_long, x='시간', y='팀명', color='유형',
                         orientation='h', barmode='stack',
                         color_discrete_map=color_map, text_auto='.0f')
            
            fig.update_traces(textposition='auto', textfont_size=12, textfont_color='white')
            fig.update_layout(xaxis_title=None, yaxis_title=None, height=400, 
                              paper_bgcolor='white', plot_bgcolor='white', font=dict(size=14))
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

    st.divider()
    st.subheader("🗓️ 상세 근무 내역")
    
    st.markdown("""
        <div class="custom-header">
            <div class="row-item">월</div>
            <div class="row-item">팀명</div>
            <div class="row-item">이름</div>
            <div class="row-item" style="color:#3B82F6 !important;">연장</div>
            <div class="row-item" style="color:#EF4444 !important;">야근</div>
            <div class="row-item" style="color:#0EA5E9 !important;">휴일</div>
            <div class="row-item" style="font-weight:bold;">합계</div>
        </div>
    """, unsafe_allow_html=True)

    if not df_filtered.empty:
        df_show_ot = df_filtered.sort_values('총근무', ascending=False).reset_index(drop=True)

        with st.container(height=500):
            for _, row in df_show_ot.iterrows():
                ext = row.get('연장근로', row.get('연장시간', 0))
                night = row.get('야근시간', 0)
                hol = row.get('휴일시간', 0)
                
                st.markdown(f"""
                    <div class="custom-row">
                        <div class="row-item" style="color:#A3AED0;">{row['월']}</div>
                        <div class="row-item"><strong>{row['팀명']}</strong></div>
                        <div class="row-item">{row['이름']}</div>
                        <div class="row-item" style="color:#3B82F6; font-weight:bold;">{ext:.1f}</div>
                        <div class="row-item" style="color:#EF4444; font-weight:bold;">{night:.1f}</div>
                        <div class="row-item" style="color:#0EA5E9; font-weight:bold;">{hol:.1f}</div>
                        <div class="row-item" style="font-weight:bold; background-color:#EFF4FB; border-radius:4px; color:#2B3674;">{row['총근무']:.1f}h</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("내역이 없습니다.")
