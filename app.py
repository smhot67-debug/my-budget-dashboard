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

# [CSS] 디자인 스타일링
st.markdown("""
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        
        .stApp { font-family: 'Pretendard', sans-serif; background-color: #F4F7FE; }
        
        /* 기본 폰트 적용 */
        h1, h2, h3, h4, h5, h6, p, div, span, label, button, input, select, textarea {
            font-family: 'Pretendard', sans-serif;
        }
        
        /* 아이콘 폰트 보호 */
        .material-symbols-rounded { font-family: 'Material Symbols Rounded' !important; }

        /* 컨테이너 여백 */
        .block-container { padding-top: 2rem; padding-bottom: 5rem; }

        /* 카드 박스 스타일 */
        div.css-1r6slb0, div.stDataFrame, div[data-testid="stMetric"] {
            background-color: white;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05);
            border: 1px solid #E2E8F0;
        }

        /* 메트릭 숫자 강조 */
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
            font-weight: 700 !important;
            color: #1E293B;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.9rem !important;
            color: #64748B;
            font-weight: 600;
        }

        /* 커스텀 리스트 행 */
        .custom-row {
            background-color: white;
            border-bottom: 1px solid #F1F5F9;
            padding: 14px 10px;
            display: flex;
            align-items: center;
            transition: all 0.2s ease;
            border-radius: 8px;
        }
        .custom-row:hover { background-color: #F8FAFC; }
        
        .custom-header {
            background-color: #F1F5F9;
            border-radius: 8px;
            padding: 12px 10px;
            font-weight: 700;
            color: #475569;
            font-size: 0.85rem;
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .row-item { flex: 1; text-align: center; font-size: 0.9rem; color: #334155; }
        .row-item-left { flex: 1; text-align: left; padding-left: 15px; font-size: 0.9rem; color: #334155; }
        
        /* 태그 */
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
        .badge-red { background-color: #FEE2E2; color: #991B1B; }
        .badge-blue { background-color: #DBEAFE; color: #1E40AF; }
        .badge-gray { background-color: #F3F4F6; color: #4B5563; }
        
        /* 합계 박스 */
        .total-box {
            background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-around;
            align-items: center;
            color: white;
            box-shadow: 0px 4px 12px rgba(37, 99, 235, 0.2);
        }
        .total-label { font-size: 0.85rem; color: #DBEAFE; margin-bottom: 4px; display: block; text-align: center;}
        .total-value { font-size: 1.3rem; font-weight: 800; color: white; display: block; text-align: center;}
        
        /* 탭 스타일 */
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            background-color: white;
            border-radius: 8px;
            padding: 0 20px;
            font-weight: 600;
            color: #64748B;
            border: 1px solid #E2E8F0;
        }
        .stTabs [aria-selected="true"] {
            background-color: #2563EB !important;
            color: white !important;
            border: none;
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

# [마스터 데이터 생성]
master_teams = ["전체 팀"]
if budget_sheet_name:
    df_bm = all_sheets[budget_sheet_name].fillna(0)
    if '팀명' in df_bm.columns:
        master_teams = ["전체 팀"] + sorted(df_bm['팀명'].astype(str).unique())

current_year = datetime.now().year
# 2026년 기준 1~12월 생성 (실제 운영 시 연도 자동화 가능)
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
    
    # QR 코드
    try:
        import qrcode
        has_qrcode = True
    except ImportError:
        has_qrcode = False

    with st.expander("📱 모바일 접속 QR"):
        if has_qrcode:
            default_url = "https://my-budget-dashboard-ebrzrzbmslu8xh6dphqtin.streamlit.app/"
            qr_url = st.text_input("URL", value=default_url)
            if qr_url:
                try:
                    qr = qrcode.QRCode(box_size=10, border=1)
                    qr.add_data(qr_url)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white")
                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    st.image(buffer, use_container_width=True)
                except: pass

# =============================================================================
# [PART A] 예산 관리 (자동 삭감 로직 적용)
# =============================================================================
if menu == "💰 예산 관리":
    if not budget_sheet_name or not expense_sheet_name:
        st.error("예산 시트가 없습니다.")
        st.stop()

    # 1. 예산 데이터 처리
    df_budget = all_sheets[budget_sheet_name].fillna(0)
    df_budget.columns = [str(c).strip() for c in df_budget.columns]
    
    # 기본/추가 예산 컬럼 식별
    for c in df_budget.columns:
        if c != '팀명': df_budget[c] = safe_numeric(df_budget[c])

    base_col = next((c for c in df_budget.columns if '배정' in c or '기본' in c), None)
    
    # 2. 지출 데이터 처리
    df_expense = all_sheets[expense_sheet_name].fillna(0)
    df_expense.columns = [str(c).strip() for c in df_expense.columns]
    
    date_col = next((c for c in df_expense.columns if '날짜' in c or 'Date' in c), None)
    if date_col:
        df_expense[date_col] = pd.to_datetime(df_expense[date_col], errors='coerce')
        df_expense['월'] = df_expense[date_col].dt.strftime('%Y-%m') # 2026-01 형태
        df_expense['월_숫자'] = df_expense[date_col].dt.month
    else:
        df_expense['월'] = 'Unknown'
        df_expense['월_숫자'] = 0
    
    if '금액' in df_expense.columns:
        df_expense['금액'] = safe_numeric(df_expense['금액'])
    
    df_expense = df_expense[df_expense['금액'] != 0]

    # 3. 필터
    with st.sidebar:
        st.subheader("예산 필터")
        period_option = st.selectbox("기간", master_months)
        team_option = st.selectbox("부서", master_teams)
        
        main_cats = ["전체"] + sorted(df_expense['대분류'].astype(str).unique())
        cat_main = st.selectbox("대분류", main_cats)
        sub_cats = ["전체"]
        if cat_main != "전체":
            sub_cats += sorted(df_expense[df_expense['대분류'] == cat_main]['소분류'].astype(str).unique())
        cat_sub = st.selectbox("소분류", sub_cats)

    # 4. [핵심] 월별 예산 및 이월 계산 로직
    # 팀별/월별 지출 집계
    monthly_exp = df_expense.groupby(['팀명', '월'])['금액'].sum().reset_index()
    
    # 결과 데이터프레임 구성
    dashboard_rows = []
    
    # 조회할 팀 목록
    target_teams = df_budget['팀명'].unique() if team_option == "전체 팀" else [team_option]
    
    for team in target_teams:
        team_base_yearly = df_budget.loc[df_budget['팀명'] == team, base_col].sum() if base_col else 0
        team_base_monthly = team_base_yearly / 12 # 월 기본 예산
        
        # 누적 잔액 계산 (1월부터 순차적으로)
        current_balance = 0
        
        target_month_idx = 0
        if period_option != "전체 누적":
            try:
                target_month_idx = int(period_option.split('-')[1])
            except: target_month_idx = 1
        else:
            target_month_idx = 12 # 전체 누적은 연말 기준

        # 1월부터 조회 월까지 순차 계산
        final_budget = 0
        final_spent = 0
        final_balance = 0
        
        if period_option == "전체 누적":
            # 전체 누적: 총 예산(연간+모든추가) - 총 지출
            annual_add = 0
            for c in df_budget.columns:
                if '추가' in c: annual_add += df_budget.loc[df_budget['팀명'] == team, c].sum()
            
            final_budget = team_base_yearly + annual_add
            final_spent = df_expense[df_expense['팀명'] == team]['금액'].sum()
            final_balance = final_budget - final_spent
            
        else:
            # 월별 이월 로직
            # 잔액 = (전월잔액) + (당월기본) + (당월추가) - (당월지출)
            cumulative_balance = 0
            
            for m in range(1, target_month_idx + 1):
                month_str = f"2026-{str(m).zfill(2)}" # 연도 하드코딩 주의
                
                # 1. 당월 기본
                this_month_budget = team_base_monthly
                
                # 2. 당월 추가 (컬럼명 예: "1월_추가")
                add_col_name = f"{m}월_추가"
                this_month_add = 0
                for c in df_budget.columns:
                    if str(m) in c and '추가' in c: # "1월" 또는 "1" 포함 확인
                        this_month_add += df_budget.loc[df_budget['팀명'] == team, c].sum()
                
                # 3. 당월 지출
                this_month_spent = monthly_exp[(monthly_exp['팀명'] == team) & (monthly_exp['월'] == month_str)]['금액'].sum()
                
                # 4. 당월 가용 예산 (전월 잔액 + 당월 예산)
                this_month_available = cumulative_balance + this_month_budget + this_month_add
                
                # 5. 월말 잔액 갱신
                cumulative_balance = this_month_available - this_month_spent
                
                # 조회 대상 월이면 결과 저장
                if m == target_month_idx:
                    final_budget = this_month_available # 가용 예산 (전월 삭감/이월 반영됨)
                    final_spent = this_month_spent
                    final_balance = cumulative_balance

        # 대시보드 데이터 추가
        dashboard_rows.append({
            '팀명': team,
            '예산': final_budget,
            '사용액': final_spent,
            '잔액': final_balance,
            '집행률': (final_spent / final_budget * 100) if final_budget > 0 else 0
        })

    df_dash = pd.DataFrame(dashboard_rows)
    
    # 분류 필터링 (상세 내역용)
    df_detail_filtered = df_expense.copy()
    if period_option != "전체 누적":
        df_detail_filtered = df_detail_filtered[df_detail_filtered['월'] == period_option]
    if team_option != "전체 팀":
        df_detail_filtered = df_detail_filtered[df_detail_filtered['팀명'] == team_option]
    if cat_main != "전체": df_detail_filtered = df_detail_filtered[df_detail_filtered['대분류'] == cat_main]
    if cat_sub != "전체": df_detail_filtered = df_detail_filtered[df_detail_filtered['소분류'] == cat_sub]

    # 5. UI 출력
    st.title("💰 예산 관리 대시보드")
    st.caption(f"기준: {team_option} / {period_option}")
    
    # KPI
    # 분류 필터가 없을 때만 전체 예산 KPI 표시 (분류 필터 시에는 왜곡됨)
    if cat_main == "전체":
        tot_b = df_dash['예산'].sum()
        tot_s = df_dash['사용액'].sum()
        tot_r = df_dash['잔액'].sum()
    else:
        # 분류 필터 시 예산은 표시하지 않고 지출만 표시
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
            fig.update_layout(showlegend=True, height=400, margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
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
                            <span>예산: {row['예산']:,.0f}</span>
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
        dept_list = master_teams # 마스터 팀 사용
        leave_dept_option = st.selectbox("소속 부서", dept_list)
        risk_criteria = st.slider("촉진 대상 기준 (잔여일)", 5, 25, 10)

    if leave_dept_option != "전체 팀":
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
        fig.update_layout(xaxis_title=None, yaxis_title="소진율(%)", height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
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
            
            # 리스트 뷰
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
# [PART C] 연장근무 관리 (디자인 복구 및 개선)
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

    df_filtered = df_ot.copy()
    if ot_month_opt != "전체 누적":
        df_filtered = df_filtered[df_filtered['월'] == ot_month_opt]
    if ot_team_opt != "전체 팀":
        df_filtered = df_filtered[df_filtered['팀명'] == ot_team_opt]

    # [수정] 탭(Tabs)으로 UI 변경 (고급 스타일)
    tab_monthly, tab_weekly = st.tabs(["📊 통합 현황", "📈 주간 추이"])

    # 1. 통합 현황
    with tab_monthly:
        st.subheader("통합 연장근무 현황")
        
        total_sum = df_filtered['총근무'].sum()
        ext_sum = df_filtered[[c for c in df_ot.columns if '연장' in c]].sum().sum()
        night_sum = df_filtered[[c for c in df_ot.columns if '야근' in c]].sum().sum()
        hol_sum = df_filtered[[c for c in df_ot.columns if '휴일' in c]].sum().sum()
        
        ext_ratio = (ext_sum / total_sum * 100) if total_sum > 0 else 0
        night_ratio = (night_sum / total_sum * 100) if total_sum > 0 else 0
        hol_ratio = (hol_sum / total_sum * 100) if total_sum > 0 else 0
        target_val = total_sum * (target_ratio / 100)

        # [수정] 네이티브 Streamlit Metric 사용 (깨짐 방지)
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("총 근무시간", f"{total_sum:,.1f}h")
        k2.metric("연장 근로 (Blue)", f"{ext_sum:,.1f}h", f"{ext_ratio:.1f}%", delta_color="off")
        k3.metric("야간 근로 (Red)", f"{night_sum:,.1f}h", f"{night_ratio:.1f}%", delta_color="off")
        k4.metric("휴일 근로 (Sky)", f"{hol_sum:,.1f}h", f"{hol_ratio:.1f}%", delta_color="off")

        st.markdown("---")
        
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("##### 🏢 팀별 근무 유형 비교")
            
            chart_teams = master_teams[1:] if ot_team_opt == "전체 팀" else [ot_team_opt]
            df_agg = df_filtered.groupby('팀명')[valid_num_cols].sum().reset_index()
            df_agg = df_agg.set_index('팀명').reindex(chart_teams).fillna(0).reset_index()
            df_long = df_agg.melt(id_vars='팀명', var_name='유형', value_name='시간')
            
            # [수정] 색상 통일 (파랑, 빨강, 하늘색)
            color_map = {
                '연장시간': '#3B82F6', '연장근로': '#3B82F6', # Blue
                '야근시간': '#EF4444', # Red
                '휴일시간': '#0EA5E9'  # Sky Blue
            }
            
            fig = px.bar(df_long, x='팀명', y='시간', color='유형',
                         barmode='group',
                         color_discrete_map=color_map,
                         text_auto='.0f')
            
            fig.update_layout(xaxis_title=None, yaxis_title=None, height=350, 
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.markdown("##### 📅 월별 통합 추이")
            if not df_ot.empty:
                trend_df = df_ot.groupby('월')['총근무'].sum().reset_index()
                trend_df = trend_df.sort_values('월')
                fig2 = px.area(trend_df, x='월', y='총근무', markers=True)
                fig2.update_traces(line_color='#3B82F6', fillcolor='rgba(59, 130, 246, 0.1)')
                fig2.update_layout(xaxis_title=None, yaxis_title=None, height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig2, use_container_width=True)

    # 2. 주간 추이
    with tab_weekly:
        st.subheader("주간 진행 현황")
        # 데이터가 있는 월만 필터
        data_months = sorted([m for m in df_ot['월'].unique() if m != '0' and m != 'Unknown'])
        if data_months:
            target_month = st.selectbox("월 선택", data_months, key="weekly_month")
            df_weekly = df_ot[df_ot['월'] == target_month]
            
            if '주차' in df_weekly.columns:
                c_w1, c_w2 = st.columns([1, 1])
                with c_w1:
                    st.markdown("##### 📊 주차별 합계")
                    week_chart = df_weekly.groupby(['주차', '팀명'])['총근무'].sum().reset_index()
                    fig3 = px.bar(week_chart, x='주차', y='총근무', color='팀명', barmode='group', color_discrete_sequence=px.colors.qualitative.Prism)
                    fig3.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig3, use_container_width=True)
                with c_w2:
                    st.markdown("##### 📉 누적 추이")
                    week_chart['누적근무'] = week_chart.groupby('팀명')['총근무'].cumsum()
                    fig4 = px.line(week_chart, x='주차', y='누적근무', color='팀명', markers=True, color_discrete_sequence=px.colors.qualitative.Prism)
                    fig4.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig4, use_container_width=True)
            else:
                st.warning("'주차' 컬럼이 없습니다.")
        else:
            st.info("데이터가 없습니다.")

    st.divider()
    st.subheader("🗓️ 상세 근무 내역")
    
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
                        <div class="row-item" style="color:#A3AED0;">{row['월']} {week_str}</div>
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
