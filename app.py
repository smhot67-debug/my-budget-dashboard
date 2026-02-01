import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# -----------------------------------------------------------------------------
# 1. 시스템 설정 및 디자인
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="통합 관리 시스템",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# [CSS] 프리미엄 UI 디자인 (폰트, 카드, 정렬)
st.markdown("""
    <style>
        /* 1. 기본 폰트 설정 (시스템 폰트 우선하여 깨짐 방지) */
        html, body, p, div, span, h1, h2, h3, h4, h5, h6, label, button, input, select, textarea {
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif !important;
        }

        /* 2. 배경색 및 메인 컨테이너 */
        .stApp { background-color: #f8f9fa; }
        .block-container { padding-top: 2rem; }

        /* 3. 카드 박스 스타일 (Shadow Box) */
        div.css-1r6slb0, div.stDataFrame, div[data-testid="stMetric"] {
            background-color: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            border: 1px solid #e2e8f0;
        }

        /* 4. 메트릭 숫자 강조 */
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
            font-weight: 800 !important;
            color: #1e293b;
        }

        /* 5. 커스텀 리스트 행 스타일 (촉진대상자 등) */
        .custom-row {
            background-color: white;
            border-bottom: 1px solid #f1f5f9;
            padding: 12px 0;
            display: flex;
            align-items: center;
            transition: background-color 0.2s;
        }
        .custom-row:hover { background-color: #f8fafc; }
        .custom-header {
            background-color: #f8fafc;
            border-top: 1px solid #e2e8f0;
            border-bottom: 1px solid #e2e8f0;
            padding: 10px 0;
            font-weight: 700;
            color: #64748b;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
        }
        .row-item { flex: 1; text-align: center; font-size: 0.95rem; color: #334155; }
        .row-item-left { flex: 1; text-align: left; padding-left: 20px; font-size: 0.95rem; color: #334155; }
        
        /* 6. 태그 스타일 */
        .badge {
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .badge-red { background-color: #fee2e2; color: #991b1b; }
        .badge-blue { background-color: #dbeafe; color: #1e40af; }
        .badge-gray { background-color: #f1f5f9; color: #475569; }

        /* 7. 합계 박스 스타일 */
        .total-box {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-around;
            align-items: center;
        }
        .total-label { font-size: 0.85rem; color: #64748b; margin-bottom: 4px; display: block; text-align: center;}
        .total-value { font-size: 1.2rem; font-weight: 800; color: #0f172a; display: block; text-align: center;}
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
        sheets = pd.read_excel(SHEET_URL, sheet_name=None)
        return sheets
    except Exception as e:
        return None

def clean_dept_name(name):
    if pd.isna(name): return ""
    # "1. 지원팀" -> "지원팀"
    return re.sub(r'^[\d\.\s]+', '', str(name))

all_sheets = load_all_data()

if not all_sheets:
    st.error("데이터 로드 실패. 구글 시트가 엑셀(xlsx) 형식으로 게시되었는지 확인해주세요.")
    st.stop()

budget_sheet_name = next((s for s in all_sheets.keys() if '기준' in s or 'Budget' in s), None)
expense_sheet_name = next((s for s in all_sheets.keys() if '지출' in s or 'Expense' in s), None)
leave_sheet_name = next((s for s in all_sheets.keys() if '원천' in s or 'Leave' in s), None)

# -----------------------------------------------------------------------------
# 3. 사이드바 및 공통 로직
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("통합 관리 시스템")
    st.markdown("---")
    menu = st.radio("업무 모듈", ["💰 예산 관리", "🏖️ 연차 관리"])
    st.markdown("---")

# =============================================================================
# [PART A] 예산 관리
# =============================================================================
if menu == "💰 예산 관리":
    if not budget_sheet_name or not expense_sheet_name:
        st.error("예산 데이터 시트가 없습니다.")
        st.stop()

    # 데이터 처리
    df_budget = all_sheets[budget_sheet_name].fillna(0)
    for col in df_budget.columns:
        if col != '팀명': df_budget[col] = pd.to_numeric(df_budget[col], errors='coerce').fillna(0)
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
        df_expense['금액'] = pd.to_numeric(df_expense['금액'], errors='coerce').fillna(0)
    
    # 0원 제거 및 문자열 변환
    df_expense = df_expense[df_expense['금액'] != 0]
    if '대분류' not in df_expense.columns: df_expense['대분류'] = '-'
    if '소분류' not in df_expense.columns: df_expense['소분류'] = '-'
    df_expense['대분류'] = df_expense['대분류'].astype(str)
    df_expense['소분류'] = df_expense['소분류'].astype(str)

    # 사이드바 필터
    with st.sidebar:
        st.subheader("예산 필터")
        month_list = sorted([m for m in df_expense['월'].unique() if m != '날짜없음'], reverse=True)
        period_option = st.selectbox("기간", ["전체 누적"] + month_list)
        
        team_list = sorted(df_base['팀명'].unique())
        team_option = st.selectbox("부서", ["전체 부서"] + team_list)
        
        st.caption("항목 필터")
        main_cats = ["전체"] + sorted(df_expense['대분류'].unique())
        cat_main = st.selectbox("대분류", main_cats)
        
        sub_cats = ["전체"]
        if cat_main != "전체":
            sub_cats += sorted(df_expense[df_expense['대분류'] == cat_main]['소분류'].unique())
        else:
            sub_cats += sorted(df_expense['소분류'].unique())
        cat_sub = st.selectbox("소분류", sub_cats)

    # 필터링
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

    # UI
    st.title("💰 예산 관리 대시보드")
    st.caption(f"기준: {team_option} / {period_label}")
    
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
            fig.update_layout(showlegend=True, height=400, margin=dict(t=20, b=20, l=20, r=20))
            fig.add_annotation(text=f"Total\n{tot_s/10000:,.0f}만", x=0.5, y=0.5, font_size=24, showarrow=False, font_weight="bold")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("데이터 없음")

    with col_list:
        st.subheader("🏢 팀별 집행 현황")
        with st.container(height=400):
            if not df_dash.empty:
                for i, row in df_dash.iterrows():
                    pct = min(row['집행률'], 100)
                    status_color = "#2563eb" if pct < 80 else ("#d97706" if pct < 100 else "#dc2626")
                    
                    st.markdown(f"""
                        <div style="background:white; padding:15px; border-radius:10px; border:1px solid #e2e8f0; margin-bottom:10px;">
                            <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                                <span style="font-weight:bold; color:#1e293b;">{row['팀명']}</span>
                                <span style="font-weight:bold; color:{status_color};">{row['집행률']:.1f}%</span>
                            </div>
                            <div style="width:100%; background-color:#f1f5f9; height:8px; border-radius:4px; margin-bottom:8px;">
                                <div style="width:{pct}%; background-color:{status_color}; height:8px; border-radius:4px;"></div>
                            </div>
                            <div style="display:flex; justify-content:space-between; font-size:0.85rem; color:#64748b;">
                                <span>예산: {row['총예산']:,.0f}</span>
                                <span>잔액: <strong>{row['잔액']:,.0f}</strong></span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("데이터 없음")

    st.subheader("📝 상세 지출 내역")
    
    # 합계 박스 (콤마 적용)
    st.markdown(f"""
        <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 10px; padding: 15px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span style="font-weight: bold; color: #1e3a8a;">🧾 조회 내역 합계</span>
            <span style="font-size: 1.4rem; font-weight: 800; color: #2563eb;">{df_filtered['금액'].sum():,.0f} 원</span>
        </div>
    """, unsafe_allow_html=True)

    if not df_filtered.empty:
        # [UI 개선] 엑셀 스타일 대신 깔끔한 리스트 뷰로 표시 (가운데 정렬)
        df_show = df_filtered.sort_values('날짜', ascending=False).reset_index(drop=True)
        
        # 헤더
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
        
        # 데이터 행 반복 출력 (상용 UI 느낌)
        with st.container(height=400):
            for _, row in df_show.iterrows():
                date_str = row['날짜'].strftime('%Y-%m-%d')
                amt_str = f"{int(row['금액']):,}"
                st.markdown(f"""
                    <div class="custom-row">
                        <div class="row-item" style="color:#64748b; font-size:0.85rem;">{date_str}</div>
                        <div class="row-item"><strong>{row['팀명']}</strong></div>
                        <div class="row-item"><span class="badge badge-gray">{row['대분류']}</span></div>
                        <div class="row-item"><span class="badge badge-gray">{row['소분류']}</span></div>
                        <div class="row-item-left" style="flex:2;">{row['상세내역']}</div>
                        <div class="row-item" style="text-align:right; padding-right:20px; font-weight:bold; color:#1e293b;">{amt_str}원</div>
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
    df_leave['소속'] = df_leave['소속'].apply(clean_dept_name) # 소속명 정제 (숫자 제거)

    # 숫자형 변환
    for col in ['합계', '사용일수', '잔여일수', '부채예산', '부채잔액']:
        if col in df_leave.columns:
            df_leave[col] = pd.to_numeric(df_leave[col], errors='coerce').fillna(0)

    # 필터
    with st.sidebar:
        st.subheader("연차 필터")
        dept_list = ["전체"] + sorted(df_leave['소속'].unique())
        leave_dept_option = st.selectbox("소속 부서", dept_list)
        risk_criteria = st.slider("촉진 대상 기준 (잔여일)", 5, 25, 10)

    if leave_dept_option != "전체":
        df_leave = df_leave[df_leave['소속'] == leave_dept_option]

    # 촉진 대상자 (잔여일수 기준 내림차순)
    df_risk = df_leave[df_leave['잔여일수'] >= risk_criteria].sort_values('잔여일수', ascending=False)

    # KPI
    avg_usage = (df_leave['사용일수'].sum() / df_leave['합계'].sum() * 100) if df_leave['합계'].sum() > 0 else 0
    tot_liab = df_leave['부채잔액'].sum()

    st.title("🏖️ 연차 관리 대시보드")
    st.caption(f"기준: {leave_dept_option} / 촉진 {risk_criteria}일 이상")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("전사 소진율", f"{avg_usage:.1f}%", delta="목표 60%")
    k2.metric("미사용 연차 부채", f"{tot_liab/100000000:.2f}억", "예상 비용", delta_color="inverse")
    k3.metric("촉진 대상자", f"{len(df_risk)}명", f"잔여 {risk_criteria}일↑", delta_color="inverse")
    k4.metric("평균 잔여일수", f"{df_leave['잔여일수'].mean():.1f}일")

    st.divider()

    c_chart, c_risk = st.columns([4, 6])
    with c_chart:
        st.subheader("📊 부서별 소진율")
        dept_sum = df_leave.groupby('소속').agg({'사용일수':'sum', '합계':'sum'}).reset_index()
        dept_sum['소진율'] = (dept_sum['사용일수'] / dept_sum['합계'] * 100).fillna(0)
        
        fig = px.bar(dept_sum, x='소속', y='소진율', text=dept_sum['소진율'].apply(lambda x: f"{x:.1f}%"),
                     color='소진율', color_continuous_scale='Bluyl')
        fig.update_layout(xaxis_title=None, yaxis_title="소진율(%)", height=450)
        st.plotly_chart(fig, use_container_width=True)

    with c_risk:
        # [UI 개선] 촉진 대상자 리스트 (이미지 스타일 적용)
        st.subheader(f"🚨 촉진 대상자 (Care Group)")
        
        if not df_risk.empty:
            r_tot = df_risk['합계'].sum()
            r_use = df_risk['사용일수'].sum()
            r_rem = df_risk['잔여일수'].sum()
            r_rate = (r_use / r_tot * 100) if r_tot > 0 else 0
            
            # 요약 박스 (콤마 적용)
            st.markdown(f"""
                <div class="total-box">
                    <div><span class="total-label">대상자 총 연차</span><span class="total-value">{r_tot:,.1f}</span></div>
                    <div><span class="total-label">사용 총계</span><span class="total-value">{r_use:,.1f}</span></div>
                    <div><span class="total-label">잔여 총계</span><span class="total-value" style="color:#ef4444;">{r_rem:,.1f}</span></div>
                    <div><span class="total-label">그룹 소진율</span><span class="total-value">{r_rate:.1f}%</span></div>
                </div>
            """, unsafe_allow_html=True)

            # 리스트 헤더
            st.markdown("""
                <div class="custom-header">
                    <div class="row-item">성명/직급</div>
                    <div class="row-item">소속</div>
                    <div class="row-item">잔여일수</div>
                    <div class="row-item">비고</div>
                </div>
            """, unsafe_allow_html=True)

            # 리스트 바디 (스크롤 가능)
            with st.container(height=320):
                for _, row in df_risk.iterrows():
                    st.markdown(f"""
                        <div class="custom-row">
                            <div class="row-item"><strong>{row['성명']}</strong></div>
                            <div class="row-item" style="color:#64748b;">{row['소속']}</div>
                            <div class="row-item"><span class="badge badge-red">{row['잔여일수']:.1f}일</span></div>
                            <div class="row-item" style="font-size:0.8rem; color:#94a3b8;">잔여 {risk_criteria}일 이상</div>
                        </div>
                    """, unsafe_allow_html=True)
            
            # 독려 버튼
            st.button(f"📧 대상자({len(df_risk)}명) 독려 메일 발송 양식 생성", use_container_width=True)
        else:
            st.success("해당 조건의 촉진 대상자가 없습니다.")

    st.divider()
    st.subheader("👥 전체 임직원 명부")
    
    # 전체 명부 (콤마 적용 및 깔끔한 표)
    df_show = df_leave.copy()
    st.dataframe(
        df_show[['소속', '성명', '합계', '사용일수', '잔여일수', '부채잔액']],
        use_container_width=True,
        column_config={
            "소속": st.column_config.TextColumn("부서", width="small"),
            "성명": st.column_config.TextColumn("이름", width="small"),
            "합계": st.column_config.NumberColumn("총 연차", format="%.1f"),
            "사용일수": st.column_config.ProgressColumn("사용 현황", format="%.1f", min_value=0, max_value=25),
            "잔여일수": st.column_config.NumberColumn("잔여", format="%.1f"),
            "부채잔액": st.column_config.NumberColumn("예상 부채", format="%d원")
        },
        hide_index=True
    )
