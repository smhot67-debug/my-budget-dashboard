import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. 프로그램 설정 (UI 디자인)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="공장 예산관리 시스템",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# [CSS 스타일링] 프로그램처럼 보이게 만드는 디자인 코드
st.markdown("""
    <style>
        /* 상단 여백 제거 */
        .block-container { padding-top: 1rem; padding-bottom: 2rem; }
        /* 메트릭 카드 스타일 */
        div[data-testid="stMetric"] {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        /* 헤더 스타일 */
        h1, h2, h3 { color: #2c3e50; font-family: 'Suit', sans-serif; }
        /* 데이터프레임 헤더 색상 */
        thead tr th:first-child { display:none }
        tbody th { display:none }
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
            return False, "필수 시트 누락", None

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
            df_expense['날짜'] = df_expense[date_col] # 원본 날짜 유지
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

# --- [사이드바: 컨트롤 패널] ---
with st.sidebar:
    st.title("🎛️ 제어 패널")
    st.markdown("---")
    
    # 필터
    st.subheader("조회 조건")
    month_list = sorted([m for m in df_expense['월'].unique() if m != '날짜없음'], reverse=True)
    period_option = st.selectbox("📅 기간 선택", ["전체 누적"] + month_list)
    
    team_list = sorted(df_base['팀명'].unique())
    team_option = st.selectbox("🏢 부서 선택", ["전체 부서"] + team_list)
    
    st.markdown("---")
    st.caption(f"Ver 2.0 | 공장 관리 시스템")

# --- [데이터 필터링 엔진] ---
if period_option == "전체 누적":
    df_filtered_exp = df_expense
    period_label = "전체 기간"
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

# --- [메인 대시보드 UI] ---
st.title(f"🏭 공장 예산 통합 관리")
st.markdown(f"**{team_option}** / **{period_label}** 현황판")

# [1] KPI 보드 (상단 핵심 지표)
total_b = df_dashboard['총예산'].sum()
total_s = df_dashboard['사용액'].sum()
total_r = df_dashboard['잔액'].sum()
avg_r = (total_s / total_b * 100) if total_b > 0 else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("총 배정 예산", f"{total_b:,.0f}", delta="목표 예산", delta_color="off")
k2.metric("현재 사용액", f"{total_s:,.0f}", delta=f"{avg_r:.1f}% 소진", delta_color="inverse")
k3.metric("현재 잔액", f"{total_r:,.0f}", delta="가용 재원")
k4.metric("지출 건수", f"{len(df_filtered_exp_detail):,}건", delta="처리 완료")

st.markdown("---")

# [2] 시각화 및 상세 분석 (2단 구성)
col_chart, col_detail = st.columns([1, 1])

with col_chart:
    st.subheader("📊 부서별 집행률 분석")
    with st.container(border=True):
        if not df_dashboard.empty:
            # 시각화: 집행률 막대 + 예산 선
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=df_dashboard['팀명'], x=df_dashboard['집행률'],
                orientation='h', name='집행률',
                marker=dict(color=df_dashboard['집행률'], colorscale='RdBu_r'),
                text=df_dashboard['집행률'].apply(lambda x: f"{x:.1f}%"),
                textposition='auto'
            ))
            fig.update_layout(height=400, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("데이터 없음")

with col_detail:
    st.subheader("📋 예산 현황표")
    with st.container(border=True):
        st.dataframe(
            df_dashboard[['팀명', '총예산', '사용액', '잔액', '집행률']].style
            .format({'총예산': '{:,.0f}', '사용액': '{:,.0f}', '잔액': '{:,.0f}', '집행률': '{:.1f}%'})
            .background_gradient(subset=['집행률'], cmap='Reds', vmin=0, vmax=120),
            use_container_width=True,
            height=400
        )

# [3] 상세 지출 내역 (하단)
st.markdown("---")
st.subheader("📝 상세 지출 내역서")

with st.container(border=True):
    # [요청하신 기능] 상세 내역의 합계 표시
    detail_total = df_filtered_exp_detail['금액'].sum()
    
    # 합계 배너
    c_tot1, c_tot2 = st.columns([8, 2])
    with c_tot1:
        st.markdown(f"##### 📑 조회된 내역 ({len(df_filtered_exp_detail)}건)")
    with c_tot2:
        st.markdown(f"<div style='text-align:right; color:#d63031; font-weight:bold; font-size:1.2em;'>합계: {detail_total:,.0f}원</div>", unsafe_allow_html=True)
    
    # 상세 테이블
    if not df_filtered_exp_detail.empty:
        cols_show = [c for c in ['날짜', '팀명', '대분류', '소분류', '상세내역', '금액'] if c in df_filtered_exp_detail.columns]
        
        st.dataframe(
            df_filtered_exp_detail[cols_show]
            .sort_values('날짜', ascending=False)
            .style.format({'금액': '{:,.0f}원', '날짜': '{:%Y-%m-%d}'}),
            use_container_width=True
        )
    else:
        st.warning("해당 기간/부서의 지출 내역이 존재하지 않습니다.")
