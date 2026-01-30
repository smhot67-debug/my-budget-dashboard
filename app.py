import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. 앱 디자인 설정 (UI/UX)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Factory Budget Pro",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# [커스텀 CSS] 폰트 크기 확대 및 고급 디자인 적용
st.markdown("""
    <style>
        /* 1. 전체 기본 폰트 사이즈 확대 (가독성 UP) */
        html, body, p, div, span, label, li {
            font-size: 18px !important; 
            font-family: 'Pretendard', sans-serif;
        }
        
        /* 2. 배경 및 컨테이너 스타일 */
        .stApp { background-color: #f8f9fa; }
        
        .css-1r6slb0, div[data-testid="stMetric"], .stDataFrame {
            background-color: white;
            border-radius: 15px; /* 둥근 모서리 강화 */
            padding: 25px; /* 내부 여백 확대 */
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); /* 부드러운 그림자 */
            border: 1px solid #edf2f7;
        }
        
        /* 3. 팀별 카드 디자인 (더 크게) */
        .team-card {
            background-color: white;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 20px;
            border-left: 8px solid #3182ce;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }
        
        /* 4. 진행바 두께 조절 */
        .stProgress > div > div > div > div {
            height: 12px; /* 바 두께 키움 */
            border-radius: 6px;
            background-image: linear-gradient(to right, #3182ce, #63b3ed);
        }
        
        /* 5. 폰트 계층 구조 강화 */
        h1 { font-size: 3rem !important; font-weight: 800; color: #1a202c; letter-spacing: -1px; }
        h2 { font-size: 2.2rem !important; font-weight: 700; color: #2d3748; }
        h3 { font-size: 1.6rem !important; font-weight: 600; color: #4a5568; margin-bottom: 15px !important; }
        
        /* 메트릭(숫자) 아주 크게 */
        div[data-testid="stMetricValue"] {
            font-size: 2.8rem !important;
            font-weight: 800 !important;
            color: #2b6cb0;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 1.2rem !important;
            color: #718096;
        }
        
        /* 6. [지출내역] 합계 박스 디자인 개선 */
        .total-floating {
            background: linear-gradient(135deg, #2c5282 0%, #2b6cb0 100%);
            color: white;
            padding: 25px 35px;
            border-radius: 12px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 10px 25px rgba(44, 82, 130, 0.25);
            margin-bottom: 25px;
            font-size: 1.4rem !important; /* 텍스트 큼직하게 */
        }
    </style>
""", unsafe_allow_html=True)

# 구글 시트 주소 (엑셀 형식)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6hnNtH_1tBFJoA25lXzFPjKUGpBfu0H313_QVFDPdHOpWDDQSJQvIlOQpUoczNO7z7jyWbE171ApD/pub?output=xlsx"

# -----------------------------------------------------------------------------
# 2. 데이터 엔진
# -----------------------------------------------------------------------------
@st.cache_data(ttl=60)
def load_data_engine():
    try:
        sheets = pd.read_excel(SHEET_URL, sheet_name=None)
        
        budget_sheet = next((s for s in sheets.keys() if '기준' in s or 'Budget' in s), None)
        expense_sheet = next((s for s in sheets.keys() if '지출' in s or 'Expense' in s), None)
        
        if not budget_sheet or not expense_sheet:
            return False, "시트 누락", None

        # [A] 예산 데이터
        df_budget = sheets[budget_sheet].fillna(0)
        for col in df_budget.columns:
            if col != '팀명':
                df_budget[col] = pd.to_numeric(df_budget[col], errors='coerce').fillna(0)
        
        df_budget['총예산'] = df_budget.iloc[:, 1:].sum(axis=1)
        df_base = df_budget[['팀명', '총예산']]

        # [B] 지출 데이터
        df_expense = sheets[expense_sheet].fillna(0)
        
        date_col = next((c for c in df_expense.columns if '날짜' in c or 'Date' in c), None)
        if date_col:
            df_expense[date_col] = pd.to_datetime(df_expense[date_col], errors='coerce')
            df_expense['월'] = df_expense[date_col].dt.strftime('%Y-%m')
            df_expense['날짜'] = df_expense[date_col]
        else:
            df_expense['월'] = '날짜없음'

        if '금액' in df_expense.columns:
            df_expense['금액'] = pd.to_numeric(df_expense['금액'], errors='coerce').fillna(0)

        # [자동 필터링] 금액이 0인 무의미한 행 제거
        df_expense = df_expense[df_expense['금액'] != 0]
        
        # [데이터 전처리] 대분류/소분류가 없는 경우 '기타'로 처리 (필터 오류 방지)
        if '대분류' not in df_expense.columns: df_expense['대분류'] = '기타'
        if '소분류' not in df_expense.columns: df_expense['소분류'] = '-'
        
        df_expense['대분류'] = df_expense['대분류'].astype(str).replace('0', '기타').replace('nan', '기타')
        df_expense['소분류'] = df_expense['소분류'].astype(str).replace('0', '-').replace('nan', '-')

        return True, df_base, df_expense

    except Exception as e:
        return False, str(e), None

status, data1, data2 = load_data_engine()
if not status: st.stop()

df_base, df_expense = data1, data2

# --- [사이드바] ---
with st.sidebar:
    st.markdown("### ⚙️ 설정")
    
    # 1. 기간 선택
    month_list = sorted([m for m in df_expense['월'].unique() if m != '날짜없음'], reverse=True)
    period_option = st.selectbox("기간", ["전체 누적"] + month_list)
    
    # 2. 부서 선택
    team_list = sorted(df_base['팀명'].unique())
    team_option = st.selectbox("부서", ["전체 부서"] + team_list)
    
    st.markdown("---")
    st.markdown("### 🏷️ 분류 필터")
    
    # 3. 대분류 선택 (데이터에 있는 항목만)
    main_cats = sorted(df_expense['대분류'].unique())
    cat_main_option = st.selectbox("대분류", ["전체"] + main_cats)
    
    # 4. 소분류 선택 (대분류 선택에 따라 동적 변경)
    if cat_main_option != "전체":
        sub_cats = sorted(df_expense[df_expense['대분류'] == cat_main_option]['소분류'].unique())
    else:
        sub_cats = sorted(df_expense['소분류'].unique())
        
    cat_sub_option = st.selectbox("소분류", ["전체"] + sub_cats)
    
    st.markdown("---")
    st.info("데이터는 실시간 연동됩니다.")

# --- [데이터 가공 및 필터링 엔진] ---
# 1. 기간 필터
if period_option == "전체 누적":
    df_filtered_exp = df_expense
else:
    df_filtered_exp = df_expense[df_expense['월'] == period_option]

# 2. 대분류/소분류 필터 (지출 내역 필터링)
if cat_main_option != "전체":
    df_filtered_exp = df_filtered_exp[df_filtered_exp['대분류'] == cat_main_option]

if cat_sub_option != "전체":
    df_filtered_exp = df_filtered_exp[df_filtered_exp['소분류'] == cat_sub_option]

# 3. 부서 필터 & 합산용 데이터 준비
if team_option != "전체 부서":
    df_filtered_exp_detail = df_filtered_exp[df_filtered_exp['팀명'] == team_option]
    df_base_view = df_base[df_base['팀명'] == team_option]
else:
    df_filtered_exp_detail = df_filtered_exp
    df_base_view = df_base

# 4. 합계 재계산 (대시보드 KPI용)
# 주의: 분류 필터를 걸면 예산 대비 집행률이 왜곡될 수 있으므로, 
# 분류 필터는 '상세 내역'과 '지출액'에만 영향을 주고, 예산(분모)은 유지하는 것이 일반적임.
exp_summary = df_filtered_exp.groupby('팀명')['금액'].sum().reset_index().rename(columns={'금액': '사용액'})
df_dashboard = pd.merge(df_base_view, exp_summary, on='팀명', how='left').fillna(0)
df_dashboard['잔액'] = df_dashboard['총예산'] - df_dashboard['사용액']
df_dashboard['집행률'] = df_dashboard.apply(lambda x: (x['사용액'] / x['총예산'] * 100) if x['총예산'] > 0 else 0, axis=1)

# [빈 팀 숨기기] 필터 결과 지출도 없고 예산도 0인 팀은 숨김 (깔끔한 뷰를 위해)
# 단, 분류 필터를 걸었을 때는 지출이 0이어도 예산이 있는 팀은 보여주는 게 좋을 수 있음.
if cat_main_option == "전체" and cat_sub_option == "전체":
    df_dashboard = df_dashboard[~((df_dashboard['총예산'] == 0) & (df_dashboard['사용액'] == 0))]
else:
    # 분류 필터 적용 시, 해당 분류 지출이 있는 팀만 보는 게 직관적일 수 있음
    df_dashboard = df_dashboard[df_dashboard['사용액'] > 0] 
    if df_dashboard.empty: # 다 걸러져서 아무것도 없으면 기본 예산 정보라도 보여주기 (선택사항)
         pass 

# --- [메인 UI] ---
st.title("Factory Budget Manager")
filter_info = f"**{team_option} / {period_option}**"
if cat_main_option != "전체": filter_info += f" / {cat_main_option}"
st.markdown(f"### {filter_info} 현황 리포트")
st.markdown("<br>", unsafe_allow_html=True) 

# 1. KPI Cards
total_b = df_dashboard['총예산'].sum()
total_s = df_dashboard['사용액'].sum()
total_r = df_dashboard['잔액'].sum()
avg_r = (total_s / total_b * 100) if total_b > 0 else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("총 예산", f"{total_b:,.0f}")
c2.metric("총 지출", f"{total_s:,.0f}", f"{avg_r:.1f}%")
c3.metric("잔액", f"{total_r:,.0f}")
c4.metric("건수", f"{len(df_filtered_exp_detail):,}건")

st.markdown("---")

# 2. 팀별 카드 리스트 & 차트
col_chart, col_list = st.columns([4, 6])

with col_chart:
    st.subheader("📊 집행률 분석")
    if not df_dashboard.empty:
        fig = go.Figure()
        fig = px.pie(df_dashboard, values='사용액', names='팀명', hole=0.6, 
                     color_discrete_sequence=px.colors.qualitative.Prism)
        fig.update_layout(showlegend=True, margin=dict(t=20, b=20, l=20, r=20), height=450,
                          legend=dict(font=dict(size=14))) 
        # 중앙 텍스트: 필터링된 지출 총액 표시
        fig.add_annotation(text=f"Total\n{total_s/10000:,.0f}만", x=0.5, y=0.5, font_size=20, showarrow=False, font_weight="bold")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("데이터 없음")

with col_list:
    st.subheader("🏢 팀별 현황")
    # [수정됨] height 제한을 제거하여 스크롤 없이 전체 표시
    # with st.container(height=450):  <-- 이 부분을 제거함
    if not df_dashboard.empty:
        for i, row in df_dashboard.iterrows():
            with st.container():
                pct = min(row['집행률'], 100)
                color = "#3182ce" if pct < 80 else ("#dd6b20" if pct < 100 else "#e53e3e")
                
                c_a, c_b, c_c = st.columns([3, 4, 3])
                with c_a:
                    st.markdown(f"**{row['팀명']}**")
                    st.caption(f"예산: {row['총예산']:,.0f}")
                with c_b:
                    st.progress(pct / 100)
                    st.caption(f"지출: {row['사용액']:,.0f} ({row['집행률']:.1f}%)")
                with c_c:
                    st.markdown(f"<div style='text-align:right; color:{color}; font-weight:bold; font-size:1.1rem;'>{row['잔액']:,.0f}원</div>", unsafe_allow_html=True)
                    st.caption("잔액")
                st.divider()
    else:
        st.info("조건에 맞는 팀 데이터가 없습니다.")

st.markdown("---")

# 3. 상세 내역
st.subheader("📝 상세 지출 내역")

# 합계 바
detail_total = df_filtered_exp_detail['금액'].sum()
st.markdown(f"""
    <div class="total-floating">
        <span>🧾 조회 내역 총 합계</span>
        <span style="font-size: 1.8rem; letter-spacing: 1px;">{detail_total:,.0f} 원</span>
    </div>
    <br>
""", unsafe_allow_html=True)

if not df_filtered_exp_detail.empty:
    cols_show = [c for c in ['날짜', '팀명', '대분류', '소분류', '상세내역', '금액'] if c in df_filtered_exp_detail.columns]
    
    st.dataframe(
        df_filtered_exp_detail[cols_show].sort_values('날짜', ascending=False),
        column_config={
            "날짜": st.column_config.DateColumn("Date", format="MM-DD", width="small"),
            "금액": st.column_config.NumberColumn("Amount", format="%d원"),
            "팀명": st.column_config.TextColumn("Team", width="small"),
            "상세내역": st.column_config.TextColumn("Description", width="large"),
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.info("지출 내역이 없습니다.")
