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

# [커스텀 CSS] 엑셀 느낌을 지우고 앱처럼 보이게 하는 스타일
st.markdown("""
    <style>
        /* 배경 및 폰트 */
        .stApp { background-color: #f8f9fa; }
        
        /* 카드 스타일 (그림자 효과) */
        .css-1r6slb0, div[data-testid="stMetric"] {
            background-color: white;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            border: none;
        }
        
        /* 팀별 카드 디자인 */
        .team-card {
            background-color: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 15px;
            border-left: 5px solid #3182ce;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        
        /* 진행바 커스텀 */
        .stProgress > div > div > div > div {
            background-image: linear-gradient(to right, #3182ce, #63b3ed);
        }
        
        /* 숫자 강조 */
        .big-number { font-size: 1.2rem; font-weight: 700; color: #2d3748; }
        .sub-text { font-size: 0.9rem; color: #718096; }
        
        /* 합계 박스 */
        .total-floating {
            background: #2c5282;
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
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

        # [자동 필터링] 금액이 0인 무의미한 행 제거 (빈 셀 없애기)
        df_expense = df_expense[df_expense['금액'] != 0]

        return True, df_base, df_expense

    except Exception as e:
        return False, str(e), None

status, data1, data2 = load_data_engine()
if not status: st.stop()

df_base, df_expense = data1, data2

# --- [사이드바] ---
with st.sidebar:
    st.markdown("### ⚙️ 설정")
    month_list = sorted([m for m in df_expense['월'].unique() if m != '날짜없음'], reverse=True)
    period_option = st.selectbox("기간", ["전체 누적"] + month_list)
    
    team_list = sorted(df_base['팀명'].unique())
    team_option = st.selectbox("부서", ["전체 부서"] + team_list)
    st.info("데이터는 실시간 연동됩니다.")

# --- [데이터 가공] ---
if period_option == "전체 누적":
    df_filtered_exp = df_expense
else:
    df_filtered_exp = df_expense[df_expense['월'] == period_option]

if team_option != "전체 부서":
    df_filtered_exp_detail = df_filtered_exp[df_filtered_exp['팀명'] == team_option]
    df_base_view = df_base[df_base['팀명'] == team_option]
else:
    df_filtered_exp_detail = df_filtered_exp
    df_base_view = df_base

# 합계 계산
exp_summary = df_filtered_exp.groupby('팀명')['금액'].sum().reset_index().rename(columns={'금액': '사용액'})
df_dashboard = pd.merge(df_base_view, exp_summary, on='팀명', how='left').fillna(0)
df_dashboard['잔액'] = df_dashboard['총예산'] - df_dashboard['사용액']
df_dashboard['집행률'] = df_dashboard.apply(lambda x: (x['사용액'] / x['총예산'] * 100) if x['총예산'] > 0 else 0, axis=1)

# [빈 팀 숨기기] 예산도 없고 사용액도 없는 팀은 화면에서 제외
df_dashboard = df_dashboard[~((df_dashboard['총예산'] == 0) & (df_dashboard['사용액'] == 0))]

# --- [메인 UI] ---
st.title("Factory Budget Manager")
st.markdown(f"**{team_option} / {period_option}** 현황 리포트")

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

# 2. 팀별 카드 리스트 (엑셀 표 대신 카드 UI 사용)
col_chart, col_list = st.columns([4, 6])

with col_chart:
    st.subheader("📊 집행률 분석")
    if not df_dashboard.empty:
        fig = go.Figure()
        # 원형 차트로 변경 (더 앱스러움)
        fig = px.pie(df_dashboard, values='사용액', names='팀명', hole=0.6, 
                     color_discrete_sequence=px.colors.qualitative.Prism)
        fig.update_layout(showlegend=True, margin=dict(t=20, b=20, l=20, r=20), height=400)
        # 중앙에 총액 표시
        fig.add_annotation(text=f"{int(avg_r)}%", x=0.5, y=0.5, font_size=20, showarrow=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("데이터 없음")

with col_list:
    st.subheader("🏢 팀별 현황")
    # [핵심] 표(DataFrame) 대신 반복문으로 카드(Card) 생성 -> 앱 느낌 물씬
    with st.container(height=400): # 스크롤 가능한 영역
        for i, row in df_dashboard.iterrows():
            with st.container():
                # 카드 HTML 구조 생성
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
                    st.markdown(f"<div style='text-align:right; color:{color}; font-weight:bold;'>{row['잔액']:,.0f}원</div>", unsafe_allow_html=True)
                    st.caption("잔액")
                st.divider()

st.markdown("---")

# 3. 상세 내역 (깔끔한 리스트 뷰)
st.subheader("📝 지출 내역")

# 합계 바
detail_total = df_filtered_exp_detail['금액'].sum()
st.markdown(f"""
    <div class="total-floating">
        <span>🧾 조회 내역 합계</span>
        <span style="font-size: 1.3rem;">{detail_total:,.0f} 원</span>
    </div>
    <br>
""", unsafe_allow_html=True)

if not df_filtered_exp_detail.empty:
    cols_show = [c for c in ['날짜', '팀명', '대분류', '소분류', '상세내역', '금액'] if c in df_filtered_exp_detail.columns]
    
    st.dataframe(
        df_filtered_exp_detail[cols_show].sort_values('날짜', ascending=False),
        column_config={
            "날짜": st.column_config.DateColumn("Date", format="MM-DD"),
            "금액": st.column_config.NumberColumn("Amount", format="%d원"),
            "팀명": st.column_config.TextColumn("Team", width="small"),
            "상세내역": st.column_config.TextColumn("Description", width="large"),
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.info("지출 내역이 없습니다.")
