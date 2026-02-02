import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
from io import BytesIO

# -----------------------------------------------------------------------------
# 1. 시스템 설정 및 디자인
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="통합 관리 시스템",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# [CSS] 프리미엄 UI 디자인
st.markdown("""
    <style>
        /* 폰트 설정 (Pretendard) */
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        
        .stApp {
            font-family: 'Pretendard', sans-serif;
            background-color: #f8f9fa;
        }
        
        h1, h2, h3, h4, h5, h6, p, div, span, label, button, input, select, textarea {
            font-family: 'Pretendard', sans-serif;
        }
        
        /* 아이콘 폰트 깨짐 방지 */
        .material-symbols-rounded {
            font-family: 'Material Symbols Rounded' !important;
        }

        /* 컨테이너 여백 */
        .block-container { padding-top: 2rem; }

        /* 카드 박스 스타일 */
        div.css-1r6slb0, div.stDataFrame, div[data-testid="stMetric"] {
            background-color: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            border: 1px solid #e2e8f0;
        }

        /* 메트릭 숫자 강조 */
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
            font-weight: 800 !important;
            color: #1e293b;
        }

        /* 커스텀 리스트 행 스타일 */
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
        
        /* 태그 스타일 */
        .badge { padding: 4px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; }
        .badge-red { background-color: #fee2e2; color: #991b1b; }
        .badge-blue { background-color: #dbeafe; color: #1e40af; }
        .badge-gray { background-color: #f1f5f9; color: #475569; }

        /* 합계 박스 스타일 */
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
    return re.sub(r'^[\d\.\s]+', '', str(name))

all_sheets = load_all_data()

if not all_sheets:
    st.error("데이터 로드 실패. 구글 시트 연결을 확인해주세요.")
    st.stop()

# 시트 이름 매핑
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
    
    # [QR 코드 생성기 - 안전 모드]
    # qrcode 모듈 설치 여부를 확인하여 앱 중단을 방지함
    try:
        import qrcode
        has_qrcode = True
    except ImportError:
        has_qrcode = False

    with st.expander("📱 모바일 접속 QR"):
        if has_qrcode:
            st.caption("아래 QR코드를 스캔하면 로그인 없이 접속됩니다.")
            # [업데이트] 동권님의 새로운 앱 주소 적용
            default_url = "https://my-budget-dashboard-ebrzrzbmslu8xh6dphqtin.streamlit.app/"
            app_url = st.text_input("접속 주소", value=default_url)
            
            if app_url:
                try:
                    qr = qrcode.QRCode(box_size=10, border=2)
                    qr.add_data(app_url)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white")
                    
                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    st.image(buffer, caption="스캔하여 바로 접속", use_container_width=True)
                except Exception as e:
                    st.warning("QR 이미지 생성 중 오류가 발생했습니다.")
        else:
            st.warning("QR 기능 준비 중 (qrcode 모듈 설치 필요)")
            st.info("서버 재부팅 후 활성화됩니다.")

# =============================================================================
# [PART A] 예산 관리
# =============================================================================
if menu == "💰 예산 관리":
    if not budget_sheet_name or not expense_sheet_name:
        st.error("예산 데이터 시트가 없습니다.")
        st.stop()
