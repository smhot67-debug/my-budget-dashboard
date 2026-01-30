import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. 프리미엄 디자인 설정 (CSS Injection)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Factory Budget Pro",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# [커스텀 CSS] UI를 고급스럽게 만드는 스타일 코드
st.markdown("""
    <style>
        /* 전체 배경색 은은한 회색으로 변경 */
        .stApp {
            background-color: #f5f7f9;
        }
        
        /* 상단 여백 제거 및 헤더 스타일 */
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }
        
        /* 카드 디자인 (Metric, Chart 컨테이너) */
        div.css-1r6slb0, div.stDataFrame, div[data-testid="stMetric"] {
            background-color: white;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.03);
            border: 1px solid #e1e4e8;
        }
        
        /* 텍스트 스타일 */
        h1, h2, h3 { font-family: 'Helvetica', sans-serif; color: #2d3748; }
        
        /* 메트릭(숫자) 스타일 강조 */
        [data-testid="stMetricValue"] {
            font-size: 1.6rem !important;
            font-weight: 700 !important;
            color: #2b6cb0 !important;
        }
        
        /* 사이드바 스타일 */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
        }
        
        /* 합계 표시 박스 스타일 (그라데이션) */
        .total-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 25px;
            border-radius: 10px;
            text-align: right;
            font-size: 1.2rem;
            font-weight: bold;
            box-shadow: 0 4px 10px rgba(118, 75, 162, 0.3);
            margin-bottom: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# 구글 시트 주소 (엑셀 형식)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6hnNtH_1tBFJoA25lXzFPjKUGpBfu0H313_QVFDPdHOpWDDQSJQvIlOQpUoczNO7z7jyWbE171ApD/pub?output=xlsx"

# -----------------------------------------------------------------------------
# 2. 데이터 엔진 (로딩 및 정제)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=60)
def load_data_engine():
    try:
        sheets = pd.read_excel(SHEET_URL, sheet_name=None)
        
        budget_sheet = next((s for s in sheets.keys() if '기준' in s or 'Budget' in s), None)
        expense_sheet = next((s for s in sheets.keys() if '지출' in s or 'Expense' in s), None)
        
        if not budget_sheet or not expense_sheet:
            return False, "필수 시트가 누락되었습니다.", None

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

        return True, df_base, df_expense

    except Exception as e:
        return False, str(e), None

# -----------------------------------------------------------------------------
# 3. 메인 프로그램 로직
# -----------------------------------------------------------------------------
status, data1, data2 = load_data_engine()

if not status:
    st.error(f"시스템 오류: {data1}")
    st.stop()

df_base = data1
df_expense = data2

# --- [사이드바] ---
with st.sidebar:
    st.markdown("### 🎛️ Dashboard Control")
    
    # 필터 디자인
    month_list = sorted([m for m in df_expense['월'].unique() if m != '날짜없음'], reverse=True)
    period_option = st.selectbox("📅 기간 선택", ["전체 누적"] + month_list)
    
    team_list = sorted(df_base['팀명'].unique())
    team_option = st.selectbox("🏢 부서 선택", ["전체 부서"] + team_list)
    
    st.markdown("---")
    st.info("데이터는 실시간으로 연동됩니다.")

# --- [데이터 필터링] ---
if period_option == "전체 누적":
    df_filtered_exp = df_expense
    period_label = "2026 연간 누적"
else:
    df_filtered_exp = df_expense[df_expense['월'] == period_option]
    period_label = f"{period_option} 월간"

if team_option != "전체 부서":
    df_filtered_exp_detail = df_filtered_exp[df_filtered_exp['팀명'] == team_option]
    df_base_view = df_base[df_base['팀명'] == team_option]
else:
    df_filtered_exp_detail = df_filtered_exp
    df_base_view = df_base

# 합계 재계산
exp_summary = df_filtered_exp.groupby('팀명')['금액'].sum().reset_index().rename(columns={'금액': '사용액'})
df_dashboard = pd.merge(df_base_view, exp_summary, on='팀명', how='left').fillna(0)
df_dashboard['잔액'] = df_dashboard['총예산'] - df_dashboard['사용액']
df_dashboard['집행률'] = df_dashboard.apply(lambda x: (x['사용액'] / x['총예산'] * 100) if x['총예산'] > 0 else 0, axis=1)

# --- [메인 대시보드] ---
st.title("Factory Budget Manager")
st.markdown(f"**{period_label}** / **{team_option}** 재무 현황")
st.markdown("<br>", unsafe_allow_html=True) 

# [1] KPI Cards
total_b = df_dashboard['총예산'].sum()
total_s = df_dashboard['사용액'].sum()
total_r = df_dashboard['잔액'].sum()
avg_r = (total_s / total_b * 100) if total_b > 0 else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Budget (배정)", f"{total_b:,.0f}", delta="목표")
with col2:
    st.metric("Actual (지출)", f"{total_s:,.0f}", f"{avg_r:.1f}%", delta_color="inverse")
with col3:
    st.metric("Remain (잔액)", f"{total_r:,.0f}")
with col4:
    st.metric("Count (건수)", f"{len(df_filtered_exp_detail):,}건")

st.markdown("<br>", unsafe_allow_html=True)

# [2] Chart & Advanced Table (프로그램 스타일 적용)
c_left, c_right = st.columns([1, 1])

with c_left:
    st.subheader("📊 부서별 집행 분석")
    if not df_dashboard.empty:
        fig = go.Figure()
        # 배경바 (회색)
        fig.add_trace(go.Bar(
            y=df_dashboard['팀명'], x=df_dashboard['총예산'],
            orientation='h', name='총 예산',
            marker_color='#edf2f7', hoverinfo='none'
        ))
        # 실적바 (그라데이션)
        colors = ['#5a67d8' if r < 100 else '#e53e3e' for r in df_dashboard['집행률']]
        fig.add_trace(go.Bar(
            y=df_dashboard['팀명'], x=df_dashboard['사용액'],
            orientation='h', name='지출액',
            marker_color=colors,
            text=df_dashboard['집행률'].apply(lambda x: f"{x:.1f}%"),
            textposition='auto'
        ))
        fig.update_layout(
            barmode='overlay', 
            plot_bgcolor='white',
            margin=dict(l=10, r=10, t=10, b=10),
            height=350,
            showlegend=False,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("데이터 없음")

with c_right:
    st.subheader("📋 예산 현황 리포트")
    # [핵심] column_config를 사용하여 앱 같은 표 만들기
    st.dataframe(
        df_dashboard,
        column_config={
            "팀명": st.column_config.TextColumn("부서명", width="medium"),
            "총예산": st.column_config.NumberColumn("배정 예산", format="%d원"),
            "사용액": st.column_config.NumberColumn("지출액", format="%d원"),
            "잔액": st.column_config.NumberColumn("잔액", format="%d원"),
            "집행률": st.column_config.ProgressColumn(
                "집행률 (%)",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            ),
        },
        hide_index=True,  # 0, 1, 2 인덱스 숨기기
        use_container_width=True,
        height=350
    )

st.markdown("---")

# [3] Detail Section (상세 내역)
st.subheader("📝 상세 지출 내역서")

# 합계 박스 (보라색 그라데이션)
detail_total = df_filtered_exp_detail['금액'].sum()
st.markdown(f"""
    <div class="total-box">
        <span>Total Expense : </span>
        <span style="font-size: 1.5rem; margin-left: 10px;">{detail_total:,.0f} 원</span>
    </div>
""", unsafe_allow_html=True)

if not df_filtered_exp_detail.empty:
    cols_show = [c for c in ['날짜', '팀명', '대분류', '소분류', '상세내역', '금액'] if c in df_filtered_exp_detail.columns]
    
    # 여기서도 column_config로 깔끔하게 처리
    st.dataframe(
        df_filtered_exp_detail[cols_show].sort_values('날짜', ascending=False),
        column_config={
            "날짜": st.column_config.DateColumn("일자", format="YYYY-MM-DD"),
            "금액": st.column_config.NumberColumn("금액", format="%d원"),
            "팀명": st.column_config.TextColumn("부서"),
            "대분류": st.column_config.TextColumn("항목(대)"),
            "소분류": st.column_config.TextColumn("항목(소)"),
            "상세내역": st.column_config.TextColumn("적요", width="large"),
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.info("조회된 지출 내역이 없습니다.")
