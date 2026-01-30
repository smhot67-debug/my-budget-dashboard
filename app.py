import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai

# -----------------------------------------------------------------------------
# 1. 환경 설정 (Pro Version)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="공장 예산관리 프로 대시보드",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 동권님의 설정 정보
API_KEY = "AIzaSyAkhIIHXg2XJSBHfrkhxGP_0iW1KZZJlZc"
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6hnNtH_1tBFJoA25lXzFPjKUGpBfu0H313_QVFDPdHOpWDDQSJQvIlOQpUoczNO7z7jyWbE171ApD/pub?output=csv"

# AI 설정
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# -----------------------------------------------------------------------------
# 2. 스마트 데이터 로딩 및 전처리 함수
# -----------------------------------------------------------------------------
@st.cache_data(ttl=60) # 60초마다 데이터 자동 갱신
def load_data_pro():
    try:
        # CSV 로드
        df = pd.read_csv(SHEET_URL)
        
        # [스마트 정제] 팀명을 제외한 모든 컬럼의 콤마(,) 제거 및 숫자로 변환
        for col in df.columns:
            if col != '팀명':
                # 문자열인 경우 콤마 제거 후 변환, 이미 숫자면 그대로 둠
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.replace(',', '').str.replace('None', '0')
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        df = df.fillna(0) # 남은 빈칸 0 처리
        
        # [자동 계산] 배정예산과 지출 합계 계산
        # 가정: '팀명', '배정예산' 컬럼이 있고, 3번째 컬럼부터는 월별 지출/추가예산 데이터임
        # 만약 컬럼명이 명확하다면 df['총지출'] = df['1월'] + df['2월']... 처럼도 가능하지만
        # 여기서는 범용성을 위해 3번째 컬럼부터 끝까지 더함
        if '배정예산' in df.columns:
            # 3번째 컬럼부터 끝까지를 모두 더해서 '총지출'로 간주 (상황에 맞게 조정 가능)
            # 동권님의 시트 구조상 3열부터가 월별 데이터라고 판단됨
            expense_cols = df.columns[2:] 
            df['총지출'] = df[expense_cols].sum(axis=1)
            df['잔액'] = df['배정예산'] - df['총지출']
            
            # 집행률 계산 (0으로 나누기 방지)
            df['집행률'] = df.apply(lambda x: (x['총지출'] / x['배정예산'] * 100) if x['배정예산'] > 0 else 0, axis=1)
        
        return df
    except Exception as e:
        return str(e)

# -----------------------------------------------------------------------------
# 3. UI 렌더링 시작
# -----------------------------------------------------------------------------
data_result = load_data_pro()

# 데이터 로드 실패 시 에러 표시
if isinstance(data_result, str):
    st.error(f"데이터 로드 실패: {data_result}")
    st.stop()
else:
    df = data_result

# [헤더 섹션]
st.title("🏭 공장 비용 관리 대시보드")
st.markdown(f"""
<style>
div.block-container {{padding-top: 2rem;}}
</style>
<div style='background-color:#f8f9fa; padding:15px; border-radius:10px; margin-bottom:20px;'>
    <span style='color:#6c757d;'>기준정보(월별 예산)와 지출내역을 실시간으로 통합 관리합니다.</span>
    <br>
    <span style='font-size:0.8em; color:#adb5bd;'>마지막 동기화: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
</div>
""", unsafe_allow_html=True)

# [상단 KPI 요약 카드]
total_budget = df['배정예산'].sum()
total_spent = df['총지출'].sum()
total_remain = df['잔액'].sum()
total_rate = (total_spent / total_budget * 100) if total_budget > 0 else 0

kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.metric("총 배정 예산", f"{total_budget:,.0f}원", delta="연간 기준", delta_color="off")
with kpi2:
    st.metric("현재 총 집행액", f"{total_spent:,.0f}원", delta=f"{total_rate:.1f}% 집행중", delta_color="inverse")
with kpi3:
    st.metric("총 잔여 예산", f"{total_remain:,.0f}원", delta="가용 예산")

st.divider()

# [메인 섹션: 팀별 카드 뷰]
st.subheader("👥 팀별 집행 현황")

# 3열 그리드 생성
cols = st.columns(3)

for idx, row in df.iterrows():
    # 3개씩 줄바꿈
    with cols[idx % 3]:
        # 카드 스타일 컨테이너
        with st.container(border=True):
            # 1. 헤더 (팀명 + 상태 아이콘)
            status_icon = "✅"
            status_color = "green"
            if row['집행률'] >= 100:
                status_icon = "🚨"
                status_color = "red"
            elif row['집행률'] >= 80:
                status_icon = "⚠️"
                status_color = "orange"
                
            st.markdown(f"### {status_icon} {row['팀명']}")
            
            # 2. 진행바 (집행률)
            # Streamlit 프로그레스바는 0.0 ~ 1.0 사이 값
            progress_val = min(row['집행률'] / 100, 1.0)
            st.progress(progress_val)
            
            # 3. 상세 수치
            c1, c2 = st.columns(2)
            with c1:
                st.caption("배정 예산")
                st.write(f"**{row['배정예산']:,.0f}**")
            with c2:
                st.caption("현재 지출")
                st.write(f"**{row['총지출']:,.0f}**")
            
            # 4. 잔액 강조
            st.markdown("---")
            st.markdown(f"**잔액: :{'red' if row['잔액'] < 0 else 'blue'}[{row['잔액']:,.0f}원]** ({row['집행률']:.1f}%)")

st.divider()

# [하단 섹션: 월별 상세 테이블 & 차트]
tab1, tab2 = st.tabs(["📋 상세 데이터 (월별)", "📊 시각화 분석"])

with tab1:
    # 데이터프레임 스타일링 (Pro 기능: 히트맵 적용)
    st.subheader("월별 누계 관리표")
    
    # 표시할 컬럼 정리 (팀명, 배정, 지출, 잔액, 집행률 순서로)
    display_cols = ['팀명', '배정예산', '총지출', '잔액', '집행률']
    # 나머지 월별 데이터 컬럼도 뒤에 붙임
    monthly_cols = [c for c in df.columns if c not in display_cols]
    final_cols = display_cols + monthly_cols
    
    # 포맷팅 설정
    format_dict = {'배정예산': '{:,.0f}', '총지출': '{:,.0f}', '잔액': '{:,.0f}', '집행률': '{:.1f}%'}
    for col in monthly_cols:
        format_dict[col] = '{:,.0f}' # 월별 데이터도 천단위 콤마

    # 스타일 적용하여 출력
    st.dataframe(
        df[final_cols].style
        .format(format_dict)
        .background_gradient(subset=['집행률'], cmap='Reds', vmin=0, vmax=120)  # 집행률 높으면 빨갛게
        , use_container_width=True
    )

with tab2:
    st.subheader("예산 점유율 분석")
    fig = px.pie(df, values='배정예산', names='팀명', title='팀별 예산 비중', hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

# [AI 리포트 섹션]
with st.expander("🤖 Gemini AI 경영 컨설팅 (클릭하여 열기)"):
    if st.button("AI 심층 분석 실행"):
        with st.spinner("경영 데이터를 분석하고 있습니다..."):
            prompt = f"""
            너는 노련한 공장 경영관리 전문가야. 
            다음 데이터를 보고 경영진에게 보고할 '비용 절감 및 효율화 보고서'를 작성해줘.
            
            데이터: {df.to_string()}
            
            [보고서 양식]
            1. **총평**: 현재 공장의 전반적인 예산 운영 상태 (양호/주의/위험)
            2. **주요 이슈**: 예산 초과가 우려되는 팀과 그 원인 추정
            3. **제언**: 남은 기간 동안의 자금 운용 가이드라인
            """
            try:
                response = model.generate_content(prompt)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"AI 분석 중 오류: {e}")
