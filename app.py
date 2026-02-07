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

# CSS (변수로 분리 - 안전하게)
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

.stApp { background: var(--bg); font-family: 'Pretendard', sans-serif; color: var(--text); }
.block-container { padding: 1.5rem 2rem; max-width: 1400px; }
h1, h2, h3 { font-weight: 700; color: var(--text); }

[data-testid="stSidebar"] { background: white; border-right: 1px solid var(--border); box-shadow: none; }

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
.modern-header h1 { font-size: 1.6rem; margin: 0; }

.kpi-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem;
    box-shadow: var(--shadow-sm);
    transition: all 0.2s ease;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }

.kpi-title { color: var(--text-muted); font-size: 0.95rem; font-weight: 600; margin-bottom: 0.5rem; }
.kpi-value { font-size: 2.1rem; font-weight: 700; color: var(--text); }

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
.custom-row { transition: all 0.2s; }
.custom-row:hover { background: #F8FAFC; border-color: var(--primary-soft); transform: translateY(-1px); }

.row-item { flex: 1; text-align: center; font-size: 0.95rem; }
.row-item-left { flex: 2; text-align: left; }

.badge { padding: 0.35rem 0.75rem; font-size: 0.875rem; font-weight: 600; border-radius: 9999px; }
.badge-blue  { background: #EFF6FF; color: #2563EB; }
.badge-red   { background: #FEF2F2; color: #DC2626; }
.badge-gray  { background: #F3F4F6
