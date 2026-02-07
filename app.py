import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import qrcode
from io import BytesIO
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="통합 관리 시스템",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ────────────────────────────────────────────────
# 개선된 CSS (변수로 분리 → SyntaxError 방지)
# ────────────────────────────────────────────────

CSS = r"""
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

.kpi-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem;
    box-shadow: var(--shadow-sm);
    transition: all 0.2s ease;
}

.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.kpi-title {
    color: var(--text-muted);
    font-size: 0.95rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.kpi-value {
    font-size: 2.1rem;
    font-weight: 700;
    color: var(--text);
}

.custom-row, .custom-header {
    background: white;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}

.custom-header {
    background: #F8FAFC;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    font-size: 0.875rem;
    letter-spacing: 0.5px;
}

.custom-row {
    transition: all 0.2s;
}

.custom-row:hover {
    background: #F8FAFC;
    border-color: var(--primary-soft);
    transform: translateY(-1px);
}

.row-item {
    flex: 1;
    text-align: center;
    font-size: 0.95rem;
}

.row-item-left {
    flex: 2;
    text-align: left;
}

.badge {
    padding: 0.35rem 0.75rem;
    font-size: 0.875rem;
    font-weight: 600;
    border-radius: 9999px;
}

.badge-blue { background: #EFF6FF; color: #2563EB; }
.badge-red  { background: #FEF2F2; color: #DC2626; }
.badge-gray { background: #F3F4F6; color: #4B5563; }

div.row-widget.stRadio > div {
    background: #F1F5F9;
    border-radius: 9999px !important;
    padding: 0.35rem;
    display: flex;
    gap: 0.35rem;
    border: none;
    box-shadow: none;
    margin: 1rem 0;
}

div.row-widget.stRadio > div label {
    border-radius: 9999px !important;
    padding: 0.6rem 1.4rem !important;
    font-weight: 600;
    font-size: 1rem;
    transition: all 0.2s;
    color: var(--text-muted);
}

div.row-widget.stRadio > div label[data-checked="true"] {
    background: var(--primary) !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
}

div.row-widget.stRadio > div label:hover:not([data-checked="true"]) {
    background: #E0E7FF;
    color: var(--primary);
}

div[data-testid="stMetricValue"] {
    font-size: 2.1rem !important;
    font-weight: 700;
    color: var(--primary);
}

div[data-testid="stMetricLabel"] {
    font-size: 0.95rem;
    color: var(--text-muted);
}
"""

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# 데이터 로드 및 기본 설정
# ────────────────────────────────────────────────

SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6hnNtH_1tBFJoA25lXzFPjKUGpBfu0H313_QVFDPdHOpWDDQSJQvIlOQpUoczNO7z7jyWbE171ApD/pub?output=xlsx"

@st.cache_data(ttl=60)
def load_all_data():
    try:
        return pd.read_excel(SHEET_URL, sheet_name=None, engine='openpyxl')
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return None

def clean_dept_name(name):
    if pd.isna(name): return ""
    return re.sub(r'^[\d.\s]+', '', str(name))

def safe_numeric(series):
    if series.dtype == 'object':
        return pd.to_numeric(series.astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    return pd.to_numeric(series, errors='coerce').fillna(0)

all_sheets = load_all_data()
if not all_sheets:
    st.error("데이터 로드 실패. 구글 시트 연결을 확인해주세요.")
    if st.button("🔄 데이터 다시 불러오기"):
        st.cache_data.clear()
        st.rerun()
    st.stop()

sheet_keys = list(all_sheets.keys())
budget_sheet_name = next((s for s in sheet_keys if '기준' in s or 'Budget' in s), None)
expense_sheet_name = next((s for s in sheet_keys if '지출' in s or 'Expense' in s), None)
leave_sheet_name = next((s for s in sheet_keys if '원천' in s or 'Leave' in s), None)
overtime_sheet_name = next((s for s in sheet_keys if '연장' in s or 'Overtime' in s or '근무' in s), None)

master_teams = ["전체 팀"]
if budget_sheet_name:
    df_bm = all_sheets[budget_sheet_name].fillna(0)
    if '팀명' in df_bm.columns:
        master_teams = ["전체 팀"] + sorted(df_bm['팀명'].astype(str).unique())

master_months = ["전체 누적"] + [f"2026-{str(m).zfill(2)}" for m
