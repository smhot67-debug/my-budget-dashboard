import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import qrcode
from io import BytesIO
from datetime import datetime

# ────────────────────────────────────────────────
# 페이지 설정
# ────────────────────────────────────────────────

st.set_page_config(
    page_title="통합 관리 시스템",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ────────────────────────────────────────────────
# CSS (변수로 분리 → SyntaxError 방지)
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

/* 헤더 - sticky top bar 스타일 */
.modern-header {
    background: white;
    border-bottom: 1px solid var(--border);
    padding: 1.25rem 2rem;
    margin: -1.5rem -2rem 1.5rem -2rem
