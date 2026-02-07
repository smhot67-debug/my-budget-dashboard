import streamlit as st
import pandas as pd
import plotly.express as px
import re
from datetime import datetime
# qrcode, plotly.graph_objects 등은 필요할 때만 import (현재는 주석 처리)

# 페이지 설정
st.set_page_config(
    page_title="통합 관리 시스템",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ────────────────────────────────────────────────
# CSS (완전하게 닫힌 형태)
# ────────────────────────────────────────────────

CSS = """
@import url('https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/static/pretendard.css');

:root {
    --bg: #FAFAFA;
    --card: #FFFFFF;
    --border: #E2E8F0;
    --text: #0F172A;
    --text-muted: #64748B;
    --primary: #6366F1;
    --primary-soft: #818CF8;
    --radius: 0.75rem;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
    --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
}

.stApp {
    background: var(--bg);
    font-family: 'Pretendard', sans-serif;
    color: var(--text);
}

.block-container {
    padding: 1.5rem 2rem;
    max-width: 1400px;
}

h1, h2, h3 {
    font-weight: 700;
    color: var(--text);
}

[data-testid="stSidebar"] {
    background: white;
    border-right: 1px solid var(--border);
    box-shadow: none;
}

.modern-header {
    background: white;
    border-bottom: 1px solid var(--border);
    padding: 1.25rem 2rem;
    margin: -1.5rem -2rem 1.5rem -2rem;
    position: sticky;
    top: 0;
    z-index: 100;
    backdrop-filter: blur(8px);
}

.modern-header h1 {
    font-size: 1.6rem;
    margin: 0;
}
"""

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# 데이터 로드 (기본 뼈대만)
# ────────────────────────────────────────────────

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6hnNtH_1tBFJoA25lXzFPjKUGpBfu0H313_QVFDPdHOpWDDQSJQvIlOQpUoczNO7z7jyWbE171ApD/pub?output=xlsx"

@st.cache_data(ttl=300)
def load_data():
    try:
        return pd.read_excel(SHEET_URL, sheet_name=None)
    except Exception as e:
        st.error("시트 로드 실패")
        st.error(str(e))
        return None

sheets = load_data()
if sheets is None:
    st.stop()

# ────────────────────────────────────────────────
# 사이드바
# ────────────────────────────────────────────────

with st.sidebar:
    st.title("통합 관리 시스템")
    st.markdown("---")

    menu = st.radio(
        "메뉴",
        options=["💰 예산 관리", "🏖️ 연차 관리", "⏰ 연장근무 관리"],
        index=0
    )

    st.markdown("---")
    if st.button("🔄 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ────────────────────────────────────────────────
# 메인 화면
# ────────────────────────────────────────────────

if menu == "💰 예산 관리":
    st.markdown(
        '<div class="modern-header"><h1>💰 예산 관리 대시보드</h1></div>',
        unsafe_allow_html=True
    )
    st.info("여기에 예산 관리 로직을 붙여넣으세요")

elif menu == "🏖️ 연차 관리":
    st.markdown(
        '<div class="modern-header"><h1>🏖️ 연차 관리 대시보드</h1></div>',
        unsafe_allow_html=True
    )
    st.info("여기에 연차 관리 로직을 붙여넣으세요")

elif menu == "⏰ 연장근무 관리":
    st.markdown(
        '<div class="modern-header"><h1>⏰ 연장근무 관리</h1></div>',
        unsafe_allow_html=True
    )
    st.info("여기에 연장근무 관리 로직을 붙여넣으세요")
