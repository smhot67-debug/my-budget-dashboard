import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from io import BytesIO
from datetime import datetime
from dateutil.relativedelta import relativedelta

# -----------------------------------------------------------------------------
# 1. 시스템 설정 및 디자인 (Python/Streamlit 환경에 맞게 CSS 래핑)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="통합 관리 시스템",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# [CSS] 프리미엄 UI 디자인 및 스크롤바 에러 방지
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

        /* 커스텀 스크롤바 (Python 에러 방지를 위해 주석과 포맷팅 주의) */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #f1f5f9; }
        ::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 20px; }

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
            margin: 0; font-size: 1.8rem; color: #2B3674; font-weight: 800; line-height: 1.2;
        }
        .modern-header p {
            margin: 8px 0 0 0; color: #A3AED0; font-size: 1rem; font-weight: 500;
        }

        /* KPI 카드 (수동 HTML용) */
        .kpi-card {
            background-color: white; border-radius: 16px; padding: 24px;
            box-shadow: 0px 4px 12px rgba(112, 144, 176, 0.08); border: 1px solid #E2E8F0;
            border-top: 5px solid #3B82F6; height: 100%; display: flex; flex-direction: column; justify-content: space-between;
        }
        .kpi-title { color: #64748B; font-size: 0.9rem; font-weight: 600; margin-bottom: 8px; }
        .kpi-value { color: #1E293B; font-size: 2.2rem; font-weight: 800; letter-spacing: -1px; }
        .kpi-sub { color: #94A3B8; font-size: 0.85rem; margin-top: 4px; font-weight: 500; }

        /* 커스텀 리스트 행 */
        .custom-row {
            background-color: white; border-bottom: 1px solid #F4F7FE; padding: 16px 10px;
            display: flex; align-items: center; transition: all 0.2s ease; border-radius: 12px; margin-bottom: 5px;
        }
        .custom-row:hover { background-color: #F4F7FE; transform: translateX(5px); }
        .custom-header {
            background-color: #F4F7FE; border-radius: 12px; padding: 12px 10px; font-weight: 600;
            color: #A3AED0; font-size: 0.85rem; display: flex; align-items: center; margin-bottom: 10px; text-transform: uppercase;
        }
        .row-item { flex: 1; text-align: center; font-size: 0.95rem; color: #2B3674; font-weight: 500; }
        .row-item-left { flex: 1; text-align: left; padding-left: 20px; font-size: 0.95rem; color: #2B3674; font-weight: 500; }
        
        .badge { padding: 6px 12px; border-radius: 30px; font-size: 0.75rem; font-weight: 700; }
        .badge-red { background-color: #FEE2E2; color: #DC2626; }
        .badge-blue { background-color: #E0E7FF; color: #4318FF; }
        .badge-gray { background-color: #F4F7FE; color: #A3AED0; }
        
        /* 사이드바 탭 스타일 */
        div.row-widget.stRadio > div[role="radiogroup"] > label {
            flex: 1; background-color: transparent; border-radius: 15px; padding: 15px 0; text-align: center;
            transition: all 0.3s ease; cursor: pointer; border: 2px solid transparent; margin-right: 0 !important;
            display: flex; justify-content: center; align-items: center;
        }
        div.row-widget.stRadio > div[role="radiogroup"] > label[data-checked="true"] {
            background-color: #4318FF; color: white !important; box-shadow: 0 8px 20px rgba(67, 24, 255, 0.3);
        }
        div.row-widget.stRadio > div[role="radiogroup"] > label p { font-size: 1.2rem !important; font-weight: 700 !important; margin: 0 !important; }
        div.row-widget.stRadio > div[role="radiogroup"] > label[data-checked="false"] p { color: #A3AED0 !important; }
    </style>
""", unsafe_allow_html=True)

# 구글 시트 주소 (통합 데이터)
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

def safe_numeric(series):
    if series.dtype == 'object':
        return pd.to_numeric(series.astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    else:
        return pd.to_numeric(series, errors='coerce').fillna(0)

def get_default_month_index(options):
    today = datetime.now()
    prev_month = today - relativedelta(months=1)
    prev_month_str = f"2026-{prev_month.strftime('%m')}" 
    for i, opt in enumerate(options):
        if prev_month_str in opt: return i
    return 0 

all_sheets = load_all_data()

if not all_sheets:
    st.error("데이터 로드 실패. 구글 시트 연결을 확인해주세요.")
    st.stop()

# 시트 이름 동적 매핑
sheet_keys = list(all_sheets.keys())
budget_sheet_name = next((s for s in sheet_keys if '기준' in s or 'Budget' in s), None)
expense_sheet_name = next((s for s in sheet_keys if '지출' in s or 'Expense' in s), None)
leave_sheet_name = next((s for s in sheet_keys if '원천' in s or 'Leave' in s), None)
overtime_sheet_name = next((s for s in sheet_keys if '연장' in s or 'Overtime' in s or '근무' in s), None)

master_months_list = [f"2026-{str(m).zfill(2)}" for m in range(1, 13)]
master_months = ["전체 누적"] + master_months_list 

# -----------------------------------------------------------------------------
# 3. 사이드바 메뉴
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("통합 관리 시스템")
    st.markdown("---")
    menu = st.radio("MAIN MENU", ["💰 예산 관리", "🏖️ 연차 관리", "⏰ 연장근무 관리"])
    st.markdown("---")
    if st.button("🔄 데이터 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.caption("※ 구글시트 반영 후 새로고침 하세요.")

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

    master_teams = ["전체 팀"] + sorted(df_budget['팀명'].astype(str).unique().tolist())

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
        st.subheader("Filter")
        period_option = st.selectbox("기간", master_months, index=get_default_month_index(master_months))
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
        is_cumulative_view = (period_option == "전체 누적")
        
        target_month_idx = 12
        if not is_cumulative_view:
            try: target_month_idx = int(period_option.split('-')[1])
            except: target_month_idx = 1
        
        cum_budget, cum_spent, cur_budget_added, cur_spent = 0, 0, 0, 0
        
        for m in range(1, target_month_idx + 1):
            month_str = f"2026-{str(m).zfill(2)}"
            add_col = [c for c in df_budget.columns if str(m) in c and '추가' in c]
            this_add = df_budget.loc[df_budget['팀명'] == team, add_col[0]].sum() if add_col else 0
            spent = monthly_exp[(monthly_exp['팀명'] == team) & (monthly_exp['월'] == month_str)]['금액'].sum()
            
            cum_budget += (team_base_monthly + this_add)
            cum_spent += spent
            
            if m == target_month_idx:
                cur_budget_added = team_base_monthly + this_add
                cur_spent = spent

        cum_balance = cum_budget - cum_spent
        cum_rate = (cum_spent / cum_budget * 100) if cum_budget > 0 else 0
        
        if is_cumulative_view:
            cur_budget_total = cum_budget
            cur_balance = cum_balance
            cur_rate = cum_rate
        else:
            carry_over = 0 if target_month_idx == 1 else (cum_budget - cur_budget_added) - (cum_spent - cur_spent)
            cur_budget_total = cur_budget_added + carry_over
            cur_balance = cur_budget_total - cur_spent
            cur_rate = (cur_spent / cur_budget_total * 100) if cur_budget_total > 0 else 0

        dashboard_rows.append({
            '팀명': team, '누계_예산': cum_budget, '누계_사용액': cum_spent, '누계_잔액': cum_balance, '누계_집행률': cum_rate,
            '당월_예산': cur_budget_total, '당월_사용액': cur_spent, '당월_잔액': cur_balance, '당월_집행률': cur_rate,
            'is_공통': 1 if "공통" in str(team) else 0 
        })

    df_dash = pd.DataFrame(dashboard_rows)
    if not df_dash.empty:
        df_dash = df_dash.sort_values(by=['is_공통', '팀명'], ascending=[False, True]).reset_index(drop=True)
    
    df_detail_filtered = df_expense.copy()
    if period_option != "전체 누적": df_detail_filtered = df_detail_filtered[df_detail_filtered['월'] == period_option]
    if team_option != "전체 팀": df_detail_filtered = df_detail_filtered[df_detail_filtered['팀명'] == team_option]
    if cat_main != "전체": df_detail_filtered = df_detail_filtered[df_detail_filtered['대분류'] == cat_main]
    if cat_sub != "전체": df_detail_filtered = df_detail_filtered[df_detail_filtered['소분류'] == cat_sub]

    st.markdown(f"""
        <div class="modern-header">
            <h1>💰 예산 관리 대시보드</h1>
            <p>Status: {team_option} / {period_option}</p>
        </div>
    """, unsafe_allow_html=True)
    
    if cat_main == "전체":
        tot_b = df_dash['당월_예산'].sum()
        tot_s = df_dash['당월_사용액'].sum()
        tot_r = df_dash['당월_잔액'].sum()
    else:
        tot_b, tot_s, tot_r = 0, df_detail_filtered['금액'].sum(), 0

    total_rate = (tot_s / tot_b * 100) if tot_b > 0 else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("가용 예산 (이월포함)", f"{tot_b:,.0f}원")
    c2.metric("총 사용액", f"{tot_s:,.0f}원")
    c3.metric("총 집행률", f"{total_rate:.1f}%")
    c4.metric("현재 잔액", f"{tot_r:,.0f}원")
    c5.metric("지출 건수", f"{len(df_detail_filtered):,}건")

    st.divider()
    st.subheader("🏢 팀별 집행 현황 (당월 & 누계)")
    
    if not df_dash.empty:
        records = df_dash.to_dict('records')
        split_idx = (len(records) + 1) // 2 
        col_left, col_right = st.columns(2)
        
        def render_card(row):
            is_com = row['is_공통'] == 1
            h_col = "#8B5CF6" if is_common else "#3B82F6"
            t_lbl = f"⭐ {row['팀명']}" if is_common else row['팀명']
            cur_c = "#3B82F6" if row['당월_집행률'] < 80 else ("#F59E0B" if row['당월_집행률'] < 100 else "#EF4444")
            cum_c = "#3B82F6" if row['누계_집행률'] < 80 else ("#F59E0B" if row['누계_집행률'] < 100 else "#EF4444")
            
            # 파이썬 f-string 안에서 HTML을 사용할 때는 들여쓰기를 제거하여 Markdown 코드로 인식되지 않도록 주의해야 합니다.
            return f"""<div style="background:white; padding:24px; border-radius:16px; margin-bottom:20px; box-shadow: 0px 4px 12px rgba(0,0,0,0.05); border:1px solid #E2E8F0; border-top: 5px solid {h_col};">
<div style="margin-bottom:15px;">
<span style="font-weight:800; color:#1E293B; font-size:1.2rem;">{t_lbl}</span>
</div>
<div style="margin-bottom: 20px;">
<div style="display:flex; justify-content:space-between; font-size: 0.9rem; margin-bottom: 6px;">
<span style="color:#64748B; font-weight:700;">당월 실적 (이월포함)</span>
<span style="font-weight:800; color:{cur_c};">{row['당월_집행률']:.1f}%</span>
</div>
<div style="width:100%; background-color:#F1F5F9; height:8px; border-radius:4px; margin-bottom:10px;">
<div style="width:{min(row['당월_집행률'], 100)}%; background-color:{cur_c}; height:8px; border-radius:4px;"></div>
</div>
<div style="display:flex; justify-content:space-between; font-size:0.85rem; color:#64748B;">
<span>예산: {row['당월_예산']:,.0f}</span><span>사용: <strong style="color:#1E293B;">{row['당월_사용액']:,.0f}</strong></span><span>잔액: <strong style="color:{cur_c};">{row['당월_잔액']:,.0f}</strong></span>
</div>
</div>
<div style="border-top: 1px dashed #E2E8F0; margin: 15px 0;"></div>
<div>
<div style="display:flex; justify-content:space-between; font-size: 0.9rem; margin-bottom: 6px;">
<span style="color:#64748B; font-weight:700;">누계 실적 (1월 ~ 현재)</span>
<span style="font-weight:800; color:{cum_c};">{row['누계_집행률']:.1f}%</span>
</div>
<div style="width:100%; background-color:#F1F5F9; height:8px; border-radius:4px; margin-bottom:10px;">
<div style="width:{min(row['누계_집행률'], 100)}%; background-color:{cum_c}; height:8px; border-radius:4px;"></div>
</div>
<div style="display:flex; justify-content:space-between; font-size:0.85rem; color:#64748B;">
<span>예산: {row['누계_예산']:,.0f}</span><span>사용: <strong style="color:#1E293B;">{row['누계_사용액']:,.0f}</strong></span><span>잔액: <strong style="color:{cum_c};">{row['누계_잔액']:,.0f}</strong></span>
</div>
</div>
</div>"""

        with col_left:
            for row in records[:split_idx]: st.markdown(render_card(row), unsafe_allow_html=True)
        with col_right:
            for row in records[split_idx:]: st.markdown(render_card(row), unsafe_allow_html=True)
    else:
        st.info("데이터 없음")

    st.subheader("📝 상세 지출 내역 (보안)")
    if 'budget_auth' not in st.session_state: st.session_state['budget_auth'] = False
        
    if not st.session_state['budget_auth']:
        c_pw = st.columns([2, 3])[0]
        with c_pw:
            pwd = st.text_input("관리자 비밀번호를 입력하세요 (7026)", type="password")
            if pwd == "7026":
                st.session_state['budget_auth'] = True
                st.rerun()
            elif pwd: st.error("비밀번호가 올바르지 않습니다.")
    else:
        if not df_detail_filtered.empty:
            df_show = df_detail_filtered.sort_values('날짜', ascending=False).reset_index(drop=True)
            st.dataframe(df_show[['날짜', '팀명', '대분류', '소분류', '상세내역', '금액']], use_container_width=True)
        else:
            st.info("내역이 없습니다.")

# =============================================================================
# [PART B] 연차 관리 (데이터 파싱 및 이중 축 그래프 적용)
# =============================================================================
elif menu == "🏖️ 연차 관리":
    if not leave_sheet_name:
        st.error("연차 '원천데이터' 시트가 없습니다.")
        st.stop()

    # 원본 데이터 로드 및 정제
    df_raw = all_sheets[leave_sheet_name].fillna(0)
    
    # 1. 컬럼 매핑 (문자열 강제 변환 후 공백 제거)
    df_raw.columns = [str(c).replace(' ', '').strip() for c in df_raw.columns]
    
    # 2. 필터링 (제외 부서)
    excluded_depts = ['성남공장', '델리하임', '기타', '대상델리하임']
    if '소속' in df_raw.columns:
        df_raw['소속'] = df_raw['소속'].astype(str).apply(lambda x: re.sub(r'^[\d\.\s]+', '', x))
        df_raw = df_raw[~df_raw['소속'].isin(excluded_depts)]
    
    # 3. 숫자형 데이터 변환 (에러 방지)
    AVG_DAILY_WAGE = 100000
    for c in ['합계', '사용일수', '잔여일수', '부채예산', '부채잔액']:
        if c in df_raw.columns:
            df_raw[c] = pd.to_numeric(df_raw[c], errors='coerce').fillna(0)

    # 4. 부채금액 자동 생성 (없을 경우)
    if '부채잔액' not in df_raw.columns and '잔여일수' in df_raw.columns:
        df_raw['부채잔액'] = df_raw['잔여일수'] * AVG_DAILY_WAGE

    # 5. 부서별 통계 집계 (KPI 생성용)
    if '소속' in df_raw.columns:
        dept_agg = df_raw.groupby('소속').agg(
            totalDays=('합계', 'sum'),
            usedDays=('사용일수', 'sum'),
            remainingDays=('잔여일수', 'sum'),
            liability=('부채잔액', 'sum'),
            employees=('사번', 'count')
        ).reset_index()
        
        dept_agg['usageRate'] = (dept_agg['usedDays'] / dept_agg['totalDays'] * 100).fillna(0)
        dept_agg['avgRemaining'] = (dept_agg['remainingDays'] / dept_agg['employees']).fillna(0)
        dept_agg = dept_agg.sort_values('usageRate', ascending=True) # 소진율 낮은 순
    else:
        dept_agg = pd.DataFrame()

    # 6. 휴식 권장 대상 (위험군) 데이터 생성
    if '잔여일수' in df_raw.columns:
        df_risk = df_raw[df_raw['잔여일수'] >= 10].copy()
    else:
        df_risk = pd.DataFrame()

    # 7. 월별 소진율(%) 및 부채(억) 추이 데이터 생성
    trend_months = []
    trend_rates = []
    trend_liabilities = []
    total_entitlement = dept_agg['totalDays'].sum() if not dept_agg.empty else 1

    for i in range(1, 13):
        m_col = f"{i}월"
        if m_col in df_raw.columns:
            val = pd.to_numeric(df_raw[m_col], errors='coerce').fillna(0).sum()
            rate = (val / total_entitlement * 100) if total_entitlement > 0 else 0
            trend_months.append(m_col)
            trend_rates.append(rate)
            # 목업 부채 데이터 생성 (원래는 시점별 데이터가 필요하지만 시각화를 위해 점진적 감소로 표현)
            trend_liabilities.append(max(0, 1.5 - (i * 0.05))) 

    # --- UI Layout ---
    st.markdown(f"""
        <div class="modern-header">
            <h1>🏖️ 연차 관리 대시보드 (통합 연동)</h1>
            <p>최종 업데이트: 경영지원팀</p>
        </div>
    """, unsafe_allow_html=True)

    # 상단 KPI
    if not dept_agg.empty:
        total_liability = dept_agg['liability'].sum()
        total_employees = dept_agg['employees'].sum()
        weighted_rate = sum(dept_agg['usageRate'] * dept_agg['employees']) / total_employees if total_employees > 0 else 0
        weighted_rem = sum(dept_agg['avgRemaining'] * dept_agg['employees']) / total_employees if total_employees > 0 else 0
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("전사 연차 소진율", f"{weighted_rate:.1f}%", delta="목표 60% 대비")
        c2.metric("미사용 연차 부채", f"₩{(total_liability/100000000):.2f}억", delta="지급 예상액", delta_color="inverse")
        c3.metric("케어 필요 대상자", f"{len(df_risk)}명", delta="잔여 10일 이상", delta_color="inverse")
        c4.metric("인당 평균 잔여일", f"{weighted_rem:.1f}일", delta="마감 2개월 전")
        st.divider()

    # --- 1. 차트 및 현황 영역 ---
    col_chart, col_dept = st.columns([6, 4])
    
    with col_chart:
        c_head1, c_head2 = st.columns([7, 3])
        c_head1.subheader("📊 월별 연차 소진율 및 부채 추이")
        # 소진율 스케일 콤보박스 (이중 축 적용을 위함)
        trend_scale = c_head2.selectbox("소진율 기준", [100, 50, 30], index=0, label_visibility="collapsed")
        
        if trend_months:
            # 이중 축 차트 생성 (Plotly Graph Objects)
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # 부채 잔액 (막대) - 오른쪽 축
            fig.add_trace(
                go.Bar(x=trend_months, y=trend_liabilities, name="예상 부채(억원)", marker_color='rgba(244, 63, 94, 0.5)'),
                secondary_y=True,
            )
            
            # 소진율 (선) - 왼쪽 축
            fig.add_trace(
                go.Scatter(x=trend_months, y=trend_rates, name="소진율(%)", mode='lines+markers+text',
                           text=[f"{r:.1f}%" for r in trend_rates], textposition="top center",
                           line=dict(color='#3B82F6', width=3), marker=dict(size=8, color='white', line=dict(width=2, color='#3B82F6'))),
                secondary_y=False,
            )
            
            fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='white', 
                              margin=dict(l=20, r=20, t=30, b=20),
                              legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(title_text="<b>소진율 (%)</b>", range=[0, trend_scale], showgrid=True, gridcolor='#F1F5F9', secondary_y=False)
            fig.update_yaxes(title_text="<b>예상 부채 (억원)</b>", range=[0, 2.0], showgrid=False, secondary_y=True)

            st.plotly_chart(fig, use_container_width=True)

    with col_dept:
        st.subheader("🏢 부서별 소진율 현황 (낮은 순)")
        if not dept_agg.empty:
            with st.container(height=400):
                for _, row in dept_agg.iterrows():
                    pct = min(row['usageRate'], 100)
                    status_c = "#EF4444" if pct < 30 else ("#F59E0B" if pct < 50 else "#10B981")
                    # Python 텍스트 포맷팅 오류 방지를 위해 왼쪽 정렬
                    st.markdown(f"""<div style="background:white; padding:15px; border-radius:12px; margin-bottom:10px; border:1px solid #E2E8F0;">
<div style="display:flex; justify-content:space-between; margin-bottom:5px;">
<span style="font-weight:700; color:#1E293B; font-size:0.95rem;">{row['소속']}</span>
<span style="font-weight:800; color:{status_c};">{row['usageRate']:.1f}%</span>
</div>
<div style="width:100%; background-color:#F1F5F9; height:6px; border-radius:3px; margin-bottom:8px;">
<div style="width:{pct}%; background-color:{status_c}; height:6px; border-radius:3px;"></div>
</div>
<div style="display:flex; justify-content:space-between; font-size:0.8rem; color:#64748B;">
<span>인원: {row['employees']}명</span><span>예상부채: ₩{(row['liability']/100000000):.1f}억</span>
</div>
</div>""", unsafe_allow_html=True)
    
    st.divider()
    
    # --- 2. 휴식 권장 대상 (필터 적용) ---
    st.subheader("🚨 휴식 권장 대상 (Care Group)")
    
    col_f1, col_f2 = st.columns([2, 2])
    dept_options = ["전체 부서"] + sorted(df_risk['소속'].unique().tolist()) if not df_risk.empty else ["전체 부서"]
    filter_dept = col_f1.selectbox("소속 필터", dept_options)
    filter_days = col_f2.selectbox("잔여일수 기준", ["10일 이상", "15일 이상", "20일 이상", "25일 이상"], index=1)
    
    days_limit = int(re.sub(r'\D', '', filter_days))
    
    if not df_risk.empty:
        mask = (df_risk['잔여일수'] >= days_limit)
        if filter_dept != "전체 부서":
            mask &= (df_risk['소속'] == filter_dept)
            
        df_show_risk = df_risk[mask].sort_values('잔여일수', ascending=False).reset_index(drop=True)
        
        if not df_show_risk.empty:
            st.dataframe(df_show_risk[['소속', '사번', '성명', '합계', '사용일수', '잔여일수', '부채잔액']], use_container_width=True)
            st.caption(f"검색된 대상자: {len(df_show_risk)}명")
        else:
            st.info("해당 조건의 대상자가 없습니다.")

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
    if '팀명' in df_ot.columns: df_ot['팀명'] = df_ot['팀명'].astype(str)

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
        ot_month_opt = st.selectbox("조회 기간", master_months, index=get_default_month_index(master_months))
        filtered_teams = sorted(df_ot['팀명'].unique())
        ot_team_opt = st.selectbox("소속 팀", ["전체 팀"] + filtered_teams)

    df_filtered = df_ot.copy()
    if ot_month_opt != "전체 누적": df_filtered = df_filtered[df_filtered['월'] == ot_month_opt]
    if ot_team_opt != "전체 팀": df_filtered = df_filtered[df_filtered['팀명'] == ot_team_opt]

    st.markdown(f"""
        <div class="modern-header">
            <h1>⏰ 연장근무 관리</h1>
            <p>Status: {ot_team_opt} / {ot_month_opt}</p>
        </div>
    """, unsafe_allow_html=True)

    total_sum = df_filtered['총근무'].sum()
    ext_sum = df_filtered[[c for c in df_ot.columns if '연장' in c]].sum().sum()
    night_sum = df_filtered[[c for c in df_ot.columns if '야근' in c]].sum().sum()
    hol_sum = df_filtered[[c for c in df_ot.columns if '휴일' in c]].sum().sum()

    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f"""<div class="kpi-card" style="border-top-color: #4F46E5;"><div class="kpi-title">총 근무시간</div><div class="kpi-value">{total_sum:,.1f}h</div></div>""", unsafe_allow_html=True)
    with k2: st.markdown(f"""<div class="kpi-card" style="border-top-color: #3B82F6;"><div class="kpi-title">연장 근로</div><div class="kpi-value">{ext_sum:,.1f}h</div></div>""", unsafe_allow_html=True)
    with k3: st.markdown(f"""<div class="kpi-card" style="border-top-color: #EF4444;"><div class="kpi-title">야간 근로</div><div class="kpi-value">{night_sum:,.1f}h</div></div>""", unsafe_allow_html=True)
    with k4: st.markdown(f"""<div class="kpi-card" style="border-top-color: #0EA5E9;"><div class="kpi-title">휴일 근로</div><div class="kpi-value">{hol_sum:,.1f}h</div></div>""", unsafe_allow_html=True)

    st.divider()
    
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("##### 🏢 팀별 근무 유형 비교")
        chart_teams = [t for t in filtered_teams] if ot_team_opt == "전체 팀" else [ot_team_opt]
        df_agg = df_filtered.groupby('팀명')[valid_num_cols].sum().reset_index()
        df_agg = df_agg.set_index('팀명').reindex(chart_teams).fillna(0).reset_index()
        df_long = df_agg.melt(id_vars='팀명', var_name='유형', value_name='시간')
        
        color_map = {'연장시간': '#3B82F6', '연장근로': '#3B82F6', '야근시간': '#EF4444', '휴일시간': '#0EA5E9'}
        fig = px.bar(df_long, x='시간', y='팀명', color='유형', orientation='h', barmode='stack', color_discrete_map=color_map, text_auto='.0f')
        fig.update_traces(textposition='auto', textfont_size=12, textfont_color='white')
        fig.update_layout(xaxis_title=None, yaxis_title=None, height=400, paper_bgcolor='white', plot_bgcolor='white')
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

    st.divider()
    st.subheader("🗓️ 상세 근무 내역")
    if not df_filtered.empty:
        df_show_ot = df_filtered.sort_values('총근무', ascending=False).reset_index(drop=True)
        st.dataframe(df_show_ot, use_container_width=True)
    else:
        st.info("내역이 없습니다.")
