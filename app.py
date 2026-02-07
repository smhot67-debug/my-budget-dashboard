import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import qrcode
from io import BytesIO
from datetime import datetime

# -----------------------------------------------------------------------------
# 시스템 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Budget Analytics",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 프리미엄 미니멀 디자인
# -----------------------------------------------------------------------------
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
        
        * {
            font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* 글로벌 배경 */
        .stApp {
            background: #FAFAFA;
        }
        
        /* 메인 컨테이너 */
        .block-container {
            padding: 3rem 4rem;
            max-width: 1600px;
        }
        
        /* 사이드바 */
        [data-testid="stSidebar"] {
            background: #FFFFFF;
            border-right: 1px solid #E8E8E8;
            padding: 2rem 1.5rem;
        }
        
        [data-testid="stSidebar"] .sidebar-content {
            padding: 0;
        }
        
        /* 사이드바 타이틀 */
        [data-testid="stSidebar"] h1 {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1A1A1A;
            margin-bottom: 2rem;
            letter-spacing: -0.3px;
        }
        
        /* 사이드바 섹션 헤더 */
        [data-testid="stSidebar"] h3 {
            font-size: 0.7rem;
            font-weight: 600;
            color: #9B9B9B;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 2rem;
            margin-bottom: 0.75rem;
        }
        
        /* 헤더 - 미니멀 */
        .page-header {
            margin-bottom: 3rem;
            border-bottom: 1px solid #E8E8E8;
            padding-bottom: 1.5rem;
        }
        
        .page-header h1 {
            font-size: 2rem;
            font-weight: 600;
            color: #1A1A1A;
            margin: 0 0 0.5rem 0;
            letter-spacing: -0.5px;
        }
        
        .page-header .meta {
            font-size: 0.875rem;
            color: #6B6B6B;
            font-weight: 400;
        }
        
        /* KPI 그리드 */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }
        
        .kpi-item {
            background: transparent;
            padding: 0;
        }
        
        .kpi-label {
            font-size: 0.75rem;
            font-weight: 500;
            color: #6B6B6B;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }
        
        .kpi-value {
            font-size: 2rem;
            font-weight: 600;
            color: #1A1A1A;
            letter-spacing: -1px;
            margin-bottom: 0.25rem;
        }
        
        .kpi-change {
            font-size: 0.8rem;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
        }
        
        .kpi-change.up {
            color: #00AA5B;
        }
        
        .kpi-change.down {
            color: #E03E3E;
        }
        
        .kpi-change.neutral {
            color: #6B6B6B;
        }
        
        /* 섹션 구분 */
        .section {
            margin-bottom: 4rem;
        }
        
        .section-title {
            font-size: 0.75rem;
            font-weight: 600;
            color: #9B9B9B;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 1.5rem;
        }
        
        /* 차트 컨테이너 */
        .chart-container {
            background: #FFFFFF;
            border: 1px solid #E8E8E8;
            border-radius: 4px;
            padding: 2rem;
            margin-bottom: 2rem;
        }
        
        .chart-header {
            font-size: 0.875rem;
            font-weight: 600;
            color: #1A1A1A;
            margin-bottom: 1.5rem;
        }
        
        /* 팀 프로그레스 */
        .team-progress {
            background: #FFFFFF;
            border: 1px solid #E8E8E8;
            border-radius: 4px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: border-color 0.2s ease;
        }
        
        .team-progress:hover {
            border-color: #1A1A1A;
        }
        
        .team-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 1rem;
        }
        
        .team-name {
            font-size: 0.95rem;
            font-weight: 600;
            color: #1A1A1A;
        }
        
        .team-percent {
            font-size: 0.85rem;
            font-weight: 500;
            font-family: 'JetBrains Mono', monospace;
            color: #6B6B6B;
        }
        
        .progress-track {
            height: 4px;
            background: #F0F0F0;
            border-radius: 2px;
            overflow: hidden;
            margin-bottom: 1rem;
        }
        
        .progress-fill {
            height: 100%;
            background: #1A1A1A;
            transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .progress-fill.warning {
            background: #F5A623;
        }
        
        .progress-fill.danger {
            background: #E03E3E;
        }
        
        .team-stats {
            display: flex;
            gap: 2rem;
            font-size: 0.8rem;
            color: #6B6B6B;
        }
        
        .team-stats span strong {
            color: #1A1A1A;
            font-weight: 500;
        }
        
        /* 테이블 */
        .data-table {
            background: #FFFFFF;
            border: 1px solid #E8E8E8;
            border-radius: 4px;
            overflow: hidden;
        }
        
        .table-header {
            background: #FAFAFA;
            padding: 0.75rem 1.5rem;
            display: flex;
            align-items: center;
            font-size: 0.7rem;
            font-weight: 600;
            color: #9B9B9B;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid #E8E8E8;
        }
        
        .table-row {
            padding: 1rem 1.5rem;
            display: flex;
            align-items: center;
            border-bottom: 1px solid #F0F0F0;
            transition: background-color 0.15s ease;
            font-size: 0.875rem;
        }
        
        .table-row:last-child {
            border-bottom: none;
        }
        
        .table-row:hover {
            background: #FAFAFA;
        }
        
        .table-cell {
            flex: 1;
            text-align: center;
            color: #1A1A1A;
        }
        
        .table-cell-left {
            flex: 1;
            text-align: left;
            color: #1A1A1A;
        }
        
        .table-cell.muted {
            color: #6B6B6B;
            font-size: 0.8rem;
        }
        
        /* 태그/배지 */
        .tag {
            display: inline-block;
            padding: 0.25rem 0.65rem;
            border-radius: 3px;
            font-size: 0.7rem;
            font-weight: 500;
            letter-spacing: 0.3px;
        }
        
        .tag-default {
            background: #F0F0F0;
            color: #1A1A1A;
        }
        
        .tag-primary {
            background: #E8F0FF;
            color: #0066CC;
        }
        
        .tag-success {
            background: #E6F6F0;
            color: #00AA5B;
        }
        
        .tag-warning {
            background: #FFF4E6;
            color: #F5A623;
        }
        
        .tag-danger {
            background: #FFE6E6;
            color: #E03E3E;
        }
        
        /* 탭/라디오 버튼 */
        div.row-widget.stRadio > div {
            background: transparent;
            padding: 0;
            border-radius: 0;
            box-shadow: none;
            display: flex;
            gap: 0.5rem;
            border-bottom: 1px solid #E8E8E8;
            margin-bottom: 2rem;
        }
        
        div.row-widget.stRadio > div[role="radiogroup"] > label {
            flex: none;
            background: transparent;
            border-radius: 0;
            padding: 0.75rem 1rem;
            border: none;
            border-bottom: 2px solid transparent;
            margin: 0 !important;
            transition: all 0.2s ease;
        }
        
        div.row-widget.stRadio > div[role="radiogroup"] > label:hover {
            background: transparent;
            border-bottom-color: #CCCCCC;
        }
        
        div.row-widget.stRadio > div[role="radiogroup"] > label[data-checked="true"] {
            background: transparent;
            border-bottom-color: #1A1A1A;
            box-shadow: none;
            transform: none;
        }
        
        div.row-widget.stRadio > div[role="radiogroup"] > label p {
            font-size: 0.875rem !important;
            font-weight: 600 !important;
            margin: 0 !important;
        }
        
        div.row-widget.stRadio > div[role="radiogroup"] > label[data-checked="false"] p {
            color: #6B6B6B !important;
        }
        
        div.row-widget.stRadio > div[role="radiogroup"] > label[data-checked="true"] p {
            color: #1A1A1A !important;
        }
        
        /* 버튼 */
        .stButton > button {
            background: #1A1A1A;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            font-size: 0.875rem;
            transition: background-color 0.2s ease;
        }
        
        .stButton > button:hover {
            background: #333333;
        }
        
        /* 인풋 */
        .stSelectbox > div > div,
        .stTextInput > div > div,
        .stSlider > div > div {
            border-radius: 4px;
            border: 1px solid #E8E8E8;
            font-size: 0.875rem;
        }
        
        .stSelectbox > div > div:focus-within,
        .stTextInput > div > div:focus-within {
            border-color: #1A1A1A;
            box-shadow: none;
        }
        
        /* 구분선 */
        hr {
            border: none;
            height: 1px;
            background: #E8E8E8;
            margin: 3rem 0;
        }
        
        /* 스크롤바 */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #FAFAFA;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #CCCCCC;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #999999;
        }
        
        /* 요약 카드 */
        .summary-box {
            background: #1A1A1A;
            border-radius: 4px;
            padding: 2rem;
            margin-bottom: 2rem;
            color: white;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 2rem;
        }
        
        .summary-item {
            text-align: left;
        }
        
        .summary-label {
            font-size: 0.7rem;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.6);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }
        
        .summary-value {
            font-size: 1.75rem;
            font-weight: 600;
            letter-spacing: -0.5px;
        }
        
        /* Plotly 차트 스타일 오버라이드 */
        .js-plotly-plot {
            border-radius: 4px;
        }
        
        /* 모바일 */
        @media (max-width: 768px) {
            .block-container {
                padding: 2rem 1.5rem;
            }
            
            .kpi-grid {
                grid-template-columns: 1fr;
            }
            
            .page-header h1 {
                font-size: 1.5rem;
            }
        }
    </style>
""", unsafe_allow_html=True)

# 구글 시트 주소
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6hnNtH_1tBFJoA25lXzFPjKUGpBfu0H313_QVFDPdHOpWDDQSJQvIlOQpUoczNO7z7jyWbE171ApD/pub?output=xlsx"

# -----------------------------------------------------------------------------
# 데이터 로드
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
    st.error("데이터 로드 실패")
    if st.button("재시도"):
        st.cache_data.clear()
        st.rerun()
    st.stop()

# 시트 매핑
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

master_months_list = [f"2026-{str(m).zfill(2)}" for m in range(1, 13)]
master_months = ["전체 누적"] + master_months_list

# -----------------------------------------------------------------------------
# 사이드바
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("◆ Analytics")
    
    menu = st.radio(
        "",
        ["예산 관리", "연차 관리", "연장근무 관리"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    if st.button("새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.caption("시트 수정 후 1~5분 반영")

# =============================================================================
# 예산 관리
# =============================================================================
if menu == "예산 관리":
    if not budget_sheet_name or not expense_sheet_name:
        st.error("예산 데이터 없음")
        st.stop()

    df_budget = all_sheets[budget_sheet_name].fillna(0)
    df_budget.columns = [str(c).strip() for c in df_budget.columns]
    
    for col in df_budget.columns:
        if col != '팀명': df_budget[col] = safe_numeric(df_budget[col])

    base_col = next((c for c in df_budget.columns if '배정' in c or '기본' in c), None)
    df_budget['월기본예산'] = df_budget[base_col] if base_col else 0

    df_expense = all_sheets[expense_sheet_name].fillna(0)
    df_expense.columns = [str(c).strip() for c in df_expense.columns]
    
    date_col = next((c for c in df_expense.columns if '날짜' in c or 'Date' in c), None)
    if date_col:
        df_expense[date_col] = pd.to_datetime(df_expense[date_col], errors='coerce')
        df_expense['월'] = df_expense[date_col].dt.strftime('%Y-%m')
    else:
        df_expense['월'] = 'Unknown'
    
    if '금액' in df_expense.columns:
        df_expense['금액'] = safe_numeric(df_expense['금액'])
    
    df_expense = df_expense[df_expense['금액'] != 0]

    with st.sidebar:
        st.markdown("### Filters")
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
        <div class="page-header">
            <h1>예산 관리</h1>
            <div class="meta">{team_option} · {period_option}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # KPI
    if cat_main == "전체":
        tot_b = df_dash['예산'].sum()
        tot_s = df_dash['사용액'].sum()
        tot_r = df_dash['잔액'].sum()
    else:
        tot_b = 0
        tot_s = df_detail_filtered['금액'].sum()
        tot_r = 0

    exec_rate = (tot_s / tot_b * 100) if tot_b > 0 else 0
    rate_change = "neutral" if exec_rate < 80 else ("up" if exec_rate < 100 else "down")

    st.markdown(f"""
        <div class="kpi-grid">
            <div class="kpi-item">
                <div class="kpi-label">총 예산</div>
                <div class="kpi-value">₩{tot_b/10000:,.0f}M</div>
                <div class="kpi-change neutral">Available</div>
            </div>
            <div class="kpi-item">
                <div class="kpi-label">사용 금액</div>
                <div class="kpi-value">₩{tot_s/10000:,.0f}M</div>
                <div class="kpi-change {rate_change}">{exec_rate:.1f}%</div>
            </div>
            <div class="kpi-item">
                <div class="kpi-label">잔여 예산</div>
                <div class="kpi-value">₩{tot_r/10000:,.0f}M</div>
                <div class="kpi-change {'up' if tot_r > 0 else 'down'}">Remaining</div>
            </div>
            <div class="kpi-item">
                <div class="kpi-label">지출 건수</div>
                <div class="kpi-value">{len(df_detail_filtered):,}</div>
                <div class="kpi-change neutral">Transactions</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # 차트 섹션
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="section-title">예산 분포</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        if tot_s > 0:
            fig = go.Figure(data=[go.Pie(
                labels=df_dash['팀명'],
                values=df_dash['사용액'],
                hole=0.6,
                marker=dict(
                    colors=['#1A1A1A', '#4A4A4A', '#6B6B6B', '#9B9B9B', '#CCCCCC'],
                    line=dict(color='#FFFFFF', width=2)
                ),
                textinfo='label+percent',
                textposition='outside',
                textfont=dict(size=11, family='IBM Plex Sans')
            )])
            
            fig.update_layout(
                showlegend=False,
                height=350,
                margin=dict(t=0, b=0, l=0, r=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='IBM Plex Sans', size=11, color='#1A1A1A')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("지출 데이터 없음")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-title">팀별 집행률</div>', unsafe_allow_html=True)
        
        if not df_dash.empty:
            for _, row in df_dash.iterrows():
                pct = min(row['집행률'], 100)
                bar_class = "" if pct < 70 else ("warning" if pct < 90 else "danger")
                
                st.markdown(f"""
                    <div class="team-progress">
                        <div class="team-header">
                            <span class="team-name">{row['팀명']}</span>
                            <span class="team-percent">{pct:.1f}%</span>
                        </div>
                        <div class="progress-track">
                            <div class="progress-fill {bar_class}" style="width:{pct}%;"></div>
                        </div>
                        <div class="team-stats">
                            <span>예산 <strong>₩{row['예산']/10000:,.0f}M</strong></span>
                            <span>사용 <strong>₩{row['사용액']/10000:,.0f}M</strong></span>
                            <span>잔액 <strong>₩{row['잔액']/10000:,.0f}M</strong></span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("데이터 없음")

    # 지출 내역
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">지출 내역</div>', unsafe_allow_html=True)
    
    if not df_detail_filtered.empty:
        df_show = df_detail_filtered.sort_values('날짜', ascending=False).reset_index(drop=True)
        
        st.markdown("""
            <div class="data-table">
                <div class="table-header">
                    <div class="table-cell">날짜</div>
                    <div class="table-cell">부서</div>
                    <div class="table-cell">대분류</div>
                    <div class="table-cell">소분류</div>
                    <div class="table-cell-left" style="flex:2;">적요</div>
                    <div class="table-cell">금액</div>
                </div>
        """, unsafe_allow_html=True)
        
        for _, row in df_show.head(50).iterrows():
            date_str = row['날짜'].strftime('%Y-%m-%d')
            amt_str = f"₩{int(row['금액']):,}"
            
            st.markdown(f"""
                <div class="table-row">
                    <div class="table-cell muted">{date_str}</div>
                    <div class="table-cell">{row['팀명']}</div>
                    <div class="table-cell"><span class="tag tag-default">{row['대분류']}</span></div>
                    <div class="table-cell"><span class="tag tag-primary">{row['소분류']}</span></div>
                    <div class="table-cell-left" style="flex:2;">{row['상세내역']}</div>
                    <div class="table-cell" style="font-family: 'JetBrains Mono', monospace; font-weight:500;">{amt_str}</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("지출 내역 없음")

# =============================================================================
# 연차 관리
# =============================================================================
elif menu == "연차 관리":
    if not leave_sheet_name:
        st.error("연차 데이터 없음")
        st.stop()

    df_leave = all_sheets[leave_sheet_name].fillna(0)
    df_leave['소속'] = df_leave['소속'].apply(clean_dept_name)
    for col in ['합계', '사용일수', '잔여일수', '부채예산', '부채잔액']:
        if col in df_leave.columns: df_leave[col] = safe_numeric(df_leave[col])

    with st.sidebar:
        st.markdown("### Filters")
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
        <div class="page-header">
            <h1>연차 관리</h1>
            <div class="meta">{leave_dept_option} · {leave_period_option}</div>
        </div>
    """, unsafe_allow_html=True)

    # KPI
    st.markdown(f"""
        <div class="kpi-grid">
            <div class="kpi-item">
                <div class="kpi-label">소진율</div>
                <div class="kpi-value">{avg_usage:.1f}%</div>
                <div class="kpi-change {'up' if avg_usage >= 60 else 'down'}">Target 60%</div>
            </div>
            <div class="kpi-item">
                <div class="kpi-label">사용 연차</div>
                <div class="kpi-value">{total_used:,.0f}</div>
                <div class="kpi-change neutral">일</div>
            </div>
            <div class="kpi-item">
                <div class="kpi-label">잔여 연차</div>
                <div class="kpi-value">{total_remain:,.0f}</div>
                <div class="kpi-change neutral">일</div>
            </div>
            <div class="kpi-item">
                <div class="kpi-label">부채 예상</div>
                <div class="kpi-value">₩{tot_liab/100000000:.2f}B</div>
                <div class="kpi-change down">Liability</div>
            </div>
            <div class="kpi-item">
                <div class="kpi-label">촉진 대상</div>
                <div class="kpi-value">{len(df_risk)}</div>
                <div class="kpi-change {'down' if len(df_risk) > 0 else 'up'}">명</div>
            </div>
            <div class="kpi-item">
                <div class="kpi-label">평균 잔여</div>
                <div class="kpi-value">{df_leave['잔여일수'].mean():.1f}</div>
                <div class="kpi-change neutral">일</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # 차트
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="section-title">부서별 소진율</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        dept_sum = df_leave.groupby('소속').agg({display_usage_col:'sum', '합계':'sum'}).reset_index()
        dept_sum['소진율'] = (dept_sum[display_usage_col] / dept_sum['합계'] * 100).fillna(0)
        
        fig = go.Figure(data=[
            go.Bar(
                x=dept_sum['소속'],
                y=dept_sum['소진율'],
                text=dept_sum['소진율'].apply(lambda x: f'{x:.1f}%'),
                textposition='outside',
                marker=dict(color='#1A1A1A'),
                textfont=dict(size=11, family='IBM Plex Sans')
            )
        ])
        
        fig.update_layout(
            xaxis_title=None,
            yaxis_title=None,
            height=350,
            margin=dict(t=20, b=40, l=40, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='IBM Plex Sans', size=11, color='#1A1A1A'),
            showlegend=False,
            yaxis=dict(gridcolor='#F0F0F0')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-title">촉진 대상자</div>', unsafe_allow_html=True)
        
        if not df_risk.empty:
            r_tot = df_risk['합계'].sum()
            r_use = df_risk['사용일수'].sum()
            r_rem = df_risk['잔여일수'].sum()
            r_rate = (r_use / r_tot * 100) if r_tot > 0 else 0
            
            st.markdown(f"""
                <div class="summary-box">
                    <div class="summary-grid">
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
            
            st.markdown('<div class="data-table">', unsafe_allow_html=True)
            for _, row in df_risk.head(10).iterrows():
                st.markdown(f"""
                    <div class="table-row">
                        <div class="table-cell-left">{row['성명']}</div>
                        <div class="table-cell muted">{row['소속']}</div>
                        <div class="table-cell"><span class="tag tag-danger">{row['잔여일수']:.0f}일</span></div>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.success("촉진 대상자 없음")

    # 전체 명부
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">임직원 현황</div>', unsafe_allow_html=True)
    
    df_show = df_leave.sort_values('소속').copy()
    usage_header = "사용(누적)" if leave_period_option == "전체 누적" else f"사용({leave_period_option})"
    
    st.markdown(f"""
        <div class="data-table">
            <div class="table-header">
                <div class="table-cell">소속</div>
                <div class="table-cell">성명</div>
                <div class="table-cell">총 연차</div>
                <div class="table-cell">{usage_header}</div>
                <div class="table-cell">잔여</div>
            </div>
    """, unsafe_allow_html=True)
    
    for _, row in df_show.iterrows():
        st.markdown(f"""
            <div class="table-row">
                <div class="table-cell muted">{row['소속']}</div>
                <div class="table-cell">{row['성명']}</div>
                <div class="table-cell">{row['합계']:.1f}</div>
                <div class="table-cell">{row[display_usage_col]:.1f}</div>
                <div class="table-cell"><span class="tag tag-default">{row['잔여일수']:.1f}</span></div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================================================
# 연장근무 관리
# =============================================================================
elif menu == "연장근무 관리":
    if not overtime_sheet_name:
        st.error("연장근무 데이터 없음")
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
        st.markdown("### Filters")
        ot_month_opt = st.selectbox("조회 기간", master_months)
        ot_team_opt = st.selectbox("소속 팀", master_teams)

    df_filtered = df_ot.copy()
    if ot_month_opt != "전체 누적":
        df_filtered = df_filtered[df_filtered['월'] == ot_month_opt]
    if ot_team_opt != "전체 팀":
        df_filtered = df_filtered[df_filtered['팀명'] == ot_team_opt]

    # 헤더
    st.markdown(f"""
        <div class="page-header">
            <h1>연장근무 관리</h1>
            <div class="meta">{ot_team_opt} · {ot_month_opt}</div>
        </div>
    """, unsafe_allow_html=True)

    # 뷰 모드
    view_mode = st.radio("", ["통합 현황", "주간 추이"], horizontal=True, label_visibility="collapsed")

    total_sum = df_filtered['총근무'].sum()
    ext_sum = df_filtered[[c for c in df_ot.columns if '연장' in c]].sum().sum()
    night_sum = df_filtered[[c for c in df_ot.columns if '야근' in c]].sum().sum()
    hol_sum = df_filtered[[c for c in df_ot.columns if '휴일' in c]].sum().sum()

    if view_mode == "통합 현황":
        st.markdown(f"""
            <div class="kpi-grid">
                <div class="kpi-item">
                    <div class="kpi-label">총 근무시간</div>
                    <div class="kpi-value">{total_sum:,.0f}h</div>
                    <div class="kpi-change neutral">Total</div>
                </div>
                <div class="kpi-item">
                    <div class="kpi-label">연장 근로</div>
                    <div class="kpi-value">{ext_sum:,.0f}h</div>
                    <div class="kpi-change neutral">{(ext_sum/total_sum*100) if total_sum > 0 else 0:.1f}%</div>
                </div>
                <div class="kpi-item">
                    <div class="kpi-label">야간 근로</div>
                    <div class="kpi-value">{night_sum:,.0f}h</div>
                    <div class="kpi-change down">{(night_sum/total_sum*100) if total_sum > 0 else 0:.1f}%</div>
                </div>
                <div class="kpi-item">
                    <div class="kpi-label">휴일 근로</div>
                    <div class="kpi-value">{hol_sum:,.0f}h</div>
                    <div class="kpi-change neutral">{(hol_sum/total_sum*100) if total_sum > 0 else 0:.1f}%</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-title">팀별 비교</div>', unsafe_allow_html=True)
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            chart_teams = master_teams[1:] if ot_team_opt == "전체 팀" else [ot_team_opt]
            df_agg = df_filtered.groupby('팀명')[valid_num_cols].sum().reset_index()
            df_agg = df_agg.set_index('팀명').reindex(chart_teams).fillna(0).reset_index()
            df_long = df_agg.melt(id_vars='팀명', var_name='유형', value_name='시간')
            
            fig = go.Figure()
            for utype in df_long['유형'].unique():
                df_type = df_long[df_long['유형'] == utype]
                fig.add_trace(go.Bar(
                    x=df_type['시간'],
                    y=df_type['팀명'],
                    name=utype,
                    orientation='h',
                    marker=dict(color='#1A1A1A' if '연장' in utype else ('#6B6B6B' if '야근' in utype else '#9B9B9B'))
                ))
            
            fig.update_layout(
                barmode='stack',
                xaxis_title=None,
                yaxis_title=None,
                height=350,
                margin=dict(t=20, b=40, l=80, r=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family='IBM Plex Sans', size=11, color='#1A1A1A'),
                showlegend=True,
                legend=dict(orientation='h', yanchor='top', y=-0.15, xanchor='center', x=0.5)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="section-title">월별 추이</div>', unsafe_allow_html=True)
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            if '월' in df_ot.columns:
                trend_df = df_ot.groupby('월')['총근무'].sum().reset_index()
                
                fig2 = go.Figure(data=[
                    go.Scatter(
                        x=trend_df['월'],
                        y=trend_df['총근무'],
                        mode='lines+markers',
                        line=dict(color='#1A1A1A', width=2),
                        marker=dict(size=6, color='#1A1A1A'),
                        fill='tozeroy',
                        fillcolor='rgba(26, 26, 26, 0.1)'
                    )
                ])
                
                fig2.update_layout(
                    xaxis_title=None,
                    yaxis_title=None,
                    height=350,
                    margin=dict(t=20, b=40, l=40, r=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(family='IBM Plex Sans', size=11, color='#1A1A1A'),
                    yaxis=dict(gridcolor='#F0F0F0')
                )
                
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("데이터 없음")
            
            st.markdown('</div>', unsafe_allow_html=True)

    # 상세 내역
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">상세 내역</div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="data-table">
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
        df_show_ot = df_filtered.head(50)
        for _, row in df_show_ot.iterrows():
            ext = row.get('연장근로', row.get('연장시간', 0))
            night = row.get('야근시간', 0)
            hol = row.get('휴일시간', 0)
            
            st.markdown(f"""
                <div class="table-row">
                    <div class="table-cell muted">{row['월']}</div>
                    <div class="table-cell">{row['팀명']}</div>
                    <div class="table-cell">{row['이름']}</div>
                    <div class="table-cell">{ext:.1f}</div>
                    <div class="table-cell">{night:.1f}</div>
                    <div class="table-cell">{hol:.1f}</div>
                    <div class="table-cell" style="font-family: 'JetBrains Mono', monospace; font-weight:500;">{row['총근무']:.1f}h</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
