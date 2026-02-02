import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import qrcode
from io import BytesIO

# -----------------------------------------------------------------------------
# 1. 시스템 설정 및 디자인 (Learn.io 스타일 적용)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="통합 관리 시스템",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# [CSS] Soft UI & Glassmorphism 디자인
st.markdown("""
    <style>
        /* 1. 폰트 설정 (Pretendard) */
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        
        .stApp {
            font-family: 'Pretendard', sans-serif;
            background-color: #F4F7FE; /* Learn.io 스타일 배경색 */
        }
        
        h1, h2, h3, h4, h5, h6, p, div, span, label, button, input, select, textarea {
            font-family: 'Pretendard', sans-serif;
        }

        /* 2. 아이콘 폰트 보호 */
        .material-symbols-rounded {
            font-family: 'Material Symbols Rounded' !important;
        }

        /* 3. 컨테이너 여백 */
        .block-container { padding-top: 2rem; padding-bottom: 5rem; }

        /* 4. 카드 박스 스타일 (Soft UI) - 둥근 모서리 강화 */
        div.css-1r6slb0, div.stDataFrame, div[data-testid="stMetric"] {
            background-color: white;
            border-radius: 24px; /* 더 둥글게 */
            padding: 24px;
            box-shadow: 0px 4px 20px rgba(112, 144, 176, 0.08); /* 부드러운 그림자 */
            border: none; /* 테두리 제거 */
        }

        /* 5. 메트릭 숫자 강조 */
        div[data-testid="stMetricValue"] {
            font-size: 2rem !important;
            font-weight: 700 !important;
            color: #2B3674; /* 진한 네이비 */
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.9rem !important;
            color: #A3AED0; /* 연한 회색 */
            font-weight: 500;
        }

        /* 6. 커스텀 리스트 스타일 */
        .custom-row {
            background-color: white;
            border-bottom: 1px solid #F4F7FE;
            padding: 16px 10px;
            display: flex;
            align-items: center;
            transition: all 0.2s ease;
            border-radius: 12px;
        }
        .custom-row:hover { 
            background-color: #F4F7FE; 
            transform: translateX(5px);
        }
        
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
        
        /* 7. 태그 스타일 */
        .badge { padding: 6px 12px; border-radius: 30px; font-size: 0.75rem; font-weight: 700; }
        .badge-red { background-color: #FEE2E2; color: #DC2626; }
        .badge-blue { background-color: #E0E7FF; color: #4318FF; } /* 퍼플 블루 */
        .badge-gray { background-color: #F4F7FE; color: #A3AED0; }

        /* 8. 합계 박스 스타일 (Gradient Card) */
        .total-box {
            background: linear-gradient(135deg, #868CFF 0%, #4318FF 100%); /* Learn.io 퍼플 */
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
        
        /* 사이드바 스타일링 */
        [data-testid="stSidebar"] {
            background-color: white;
            border-right: none;
            box-shadow: 4px 0px 20px rgba(112, 144, 176, 0.05);
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
    if st.button("데이터 새로고침"):
        st.cache_data.clear()
        st.rerun()
    st.stop()

# 시트 이름 매핑
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
    # 라디오 버튼 대신 더 깔끔한 선택지 UI 제공 가능하나 Streamlit 기본 위젯 사용
    menu = st.radio("MAIN MENU", ["💰 예산 관리", "🏖️ 연차 관리", "⏰ 연장근무 관리"])
    st.markdown("---")
    
    # [QR 코드]
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
                    st.warning("QR Error")

# =============================================================================
# [PART A] 예산 관리
# =============================================================================
if menu == "💰 예산 관리":
    if not budget_sheet_name or not expense_sheet_name:
        st.error("예산 데이터 시트를 찾을 수 없습니다.")
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
                # Soft UI Color Palette
                status_color = "#4318FF" if pct < 80 else ("#FFB547" if pct < 100 else "#FF5630") # Indigo, Orange, Red
                bg_bar = "#EFF4FB"
                
                st.markdown(f"""
                    <div style="background:white; padding:20px; border-radius:16px; margin-bottom:15px; box-shadow: 0px 3px 10px rgba(0,0,0,0.03);">
                        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                            <span style="font-weight:700; color:#2B3674; font-size:1.05rem;">{row['팀명']}</span>
                            <span style="font-weight:800; color:{status_color};">{row['집행률']:.1f}%</span>
                        </div>
                        <div style="width:100%; background-color:{bg_bar}; height:10px; border-radius:5px; margin-bottom:12px;">
                            <div style="width:{pct}%; background-color:{status_color}; height:10px; border-radius:5px;"></div>
                        </div>
                        <div style="display:flex; justify-content:space-between; font-size:0.85rem; color:#A3AED0; font-weight:500;">
                            <span>예산: {row['총예산']:,.0f}</span>
                            <span>잔액: <strong style="color:#2B3674;">{row['잔액']:,.0f}</strong></span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("데이터 없음")

    st.subheader("📝 상세 지출 내역")
    st.markdown(f"""
        <div class="total-box">
            <div style="text-align:left; width:100%; display:flex; justify-content:space-between; align-items:center;">
                <span class="total-label" style="color:#E9E3FF; font-size:1.1rem; text-align:left;">🧾 조회 내역 합계</span>
                <span class="total-value" style="font-size:1.6rem;">{df_filtered['금액'].sum():,.0f} 원</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if not df_filtered.empty:
        df_show = df_filtered.sort_values('날짜', ascending=False).reset_index(drop=True)
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
                        <div class="row-item" style="color:#A3AED0; font-size:0.85rem;">{date_str}</div>
                        <div class="row-item"><strong>{row['팀명']}</strong></div>
                        <div class="row-item"><span class="badge badge-gray">{row['대분류']}</span></div>
                        <div class="row-item"><span class="badge badge-gray">{row['소분류']}</span></div>
                        <div class="row-item-left" style="flex:2; color:#2B3674;">{row['상세내역']}</div>
                        <div class="row-item" style="text-align:right; padding-right:20px; font-weight:bold; color:#2B3674;">{amt_str}원</div>
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
            
            st.markdown(f"""
                <div class="total-box">
                    <div><span class="total-label">대상자 총 연차</span><span class="total-value">{r_tot:,.1f}</span></div>
                    <div><span class="total-label">사용 총계</span><span class="total-value">{r_use:,.1f}</span></div>
                    <div><span class="total-label">잔여 총계</span><span class="total-value" style="color:#FFB547;">{r_rem:,.1f}</span></div>
                    <div><span class="total-label">그룹 소진율</span><span class="total-value">{r_rate:.1f}%</span></div>
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
                            <div class="row-item" style="color:#A3AED0;">{row['소속']}</div>
                            <div class="row-item"><span class="badge badge-red">{row['잔여일수']:.1f}일</span></div>
                            <div class="row-item" style="font-size:0.8rem; color:#A3AED0;">잔여 {risk_criteria}일 이상</div>
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
                    <div class="row-item" style="color:#A3AED0;">{row['소속']}</div>
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

    tab_dashboard, tab_weekly = st.tabs(["📊 통합 현황 (Monthly)", "📈 주간 추이 (Weekly)"])

    # 1. 통합 현황
    with tab_dashboard:
        st.subheader("통합 연장근무 현황")
        
        unique_months = [m for m in df_ot['월'].unique() if m != '0' and m != 'Unknown']
        try:
            sorted_months = sorted(unique_months, key=lambda x: int(re.sub(r'\D', '', str(x))) if re.sub(r'\D', '', str(x)) else 0)
        except:
            sorted_months = sorted(unique_months)

        month_list = ["전체 누적"] + sorted_months
        
        c_filter, c_ratio = st.columns([2, 4])
        with c_filter:
            ot_month_opt = st.selectbox("조회 기간", month_list)
        
        df_filtered = df_ot.copy()
        if ot_month_opt != "전체 누적":
            df_filtered = df_filtered[df_filtered['월'] == ot_month_opt]
        
        total_sum = df_filtered['총근무'].sum()
        ext_sum = df_filtered[[c for c in df_ot.columns if '연장' in c]].sum().sum()
        night_sum = df_filtered[[c for c in df_ot.columns if '야근' in c]].sum().sum()
        hol_sum = df_filtered[[c for c in df_ot.columns if '휴일' in c]].sum().sum()
        
        ext_ratio = (ext_sum / total_sum * 100) if total_sum > 0 else 0
        night_ratio = (night_sum / total_sum * 100) if total_sum > 0 else 0
        hol_ratio = (hol_sum / total_sum * 100) if total_sum > 0 else 0

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("총 근무시간", f"{total_sum:,.1f}h")
        k2.metric("연장 근로", f"{ext_sum:,.1f}h", f"{ext_ratio:.1f}%", delta_color="off")
        k3.metric("야간 근로", f"{night_sum:,.1f}h", f"{night_ratio:.1f}%", delta_color="off")
        k4.metric("휴일 근로", f"{hol_sum:,.1f}h", f"{hol_ratio:.1f}%", delta_color="off")

        st.markdown("---")
        
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("##### 🏢 팀별 근무 유형 비교")
            if not df_filtered.empty:
                df_chart = df_filtered.groupby('팀명')[valid_num_cols].sum().reset_index()
                df_long = df_chart.melt(id_vars='팀명', var_name='유형', value_name='시간')
                
                # Soft UI Colors: Indigo, Pink, Light Blue
                fig = px.bar(df_long, x='팀명', y='시간', color='유형',
                             color_discrete_map={'연장시간':'#4318FF', '연장근로':'#4318FF', '야근시간':'#FF5630', '휴일시간':'#33C5FF'},
                             text_auto='.0f')
                fig.update_layout(xaxis_title=None, yaxis_title=None, height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("데이터 없음")
            
        with c2:
            st.markdown("##### 📅 월별 통합 추이")
            if '월' in df_ot.columns and not df_ot.empty:
                trend_df = df_ot.groupby('월')['총근무'].sum().reset_index()
                try:
                    trend_df['sort_key'] = trend_df['월'].apply(lambda x: int(re.sub(r'\D', '', str(x))) if re.sub(r'\D', '', str(x)) else 0)
                    trend_df = trend_df.sort_values('sort_key')
                except:
                    pass
                
                # [수정완료] fill_color -> fillcolor (오류 해결)
                fig2 = px.area(trend_df, x='월', y='총근무', markers=True)
                fig2.update_traces(line_color='#4318FF', fillcolor='rgba(67, 24, 255, 0.1)')
                fig2.update_layout(xaxis_title=None, yaxis_title=None, height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("데이터 없음")

    # 2. 주간 추이
    with tab_weekly:
        st.subheader("주간 진행 현황 (Weekly)")
        
        if sorted_months:
            target_month = st.selectbox("월 선택", sorted_months, key="weekly_month")
            df_weekly = df_ot[df_ot['월'] == target_month]
            
            if '주차' in df_weekly.columns:
                c_w1, c_w2 = st.columns([1, 1])
                
                with c_w1:
                    st.markdown("##### 📊 주차별 팀 합계")
                    week_chart = df_weekly.groupby(['주차', '팀명'])['총근무'].sum().reset_index()
                    if not week_chart.empty:
                        fig3 = px.bar(week_chart, x='주차', y='총근무', color='팀명', barmode='group', color_discrete_sequence=px.colors.qualitative.Prism)
                        fig3.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                        st.plotly_chart(fig3, use_container_width=True)
                    else:
                        st.info("해당 월의 데이터가 없습니다.")
                    
                with c_w2:
                    st.markdown("##### 📉 팀별 누적 추이")
                    if not week_chart.empty:
                        try:
                            week_chart['주차_num'] = week_chart['주차'].apply(lambda x: int(re.sub(r'\D', '', str(x))) if re.sub(r'\D', '', str(x)) else 0)
                            week_chart = week_chart.sort_values('주차_num')
                        except:
                            pass
                        week_chart['누적근무'] = week_chart.groupby('팀명')['총근무'].cumsum()
                        
                        fig4 = px.line(week_chart, x='주차', y='누적근무', color='팀명', markers=True, color_discrete_sequence=px.colors.qualitative.Prism)
                        fig4.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                        st.plotly_chart(fig4, use_container_width=True)
            else:
                st.warning("'주차' 컬럼이 데이터에 없습니다.")
        else:
            st.info("데이터가 없습니다.")

    st.divider()
    st.subheader("🗓️ 상세 근무 내역")
    
    st.markdown("""
        <div class="custom-header">
            <div class="row-item">월/주차</div>
            <div class="row-item">팀명</div>
            <div class="row-item">이름</div>
            <div class="row-item" style="color:#4318FF;">연장</div>
            <div class="row-item" style="color:#FF5630;">야근</div>
            <div class="row-item" style="color:#33C5FF;">휴일</div>
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
                        <div class="row-item" style="color:#4318FF;">{ext:.1f}</div>
                        <div class="row-item" style="color:#FF5630;">{night:.1f}</div>
                        <div class="row-item" style="color:#33C5FF;">{hol:.1f}</div>
                        <div class="row-item" style="font-weight:bold; background-color:#EFF4FB; border-radius:4px; color:#2B3674;">{row['총근무']:.1f}h</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("내역이 없습니다.")
