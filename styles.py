"""
Custom CSS Styles for Dark Theme
"""

CUSTOM_CSS = """
<style>
/* ===== Root Variables ===== */
:root {
    --bg-primary: #0e1117;
    --bg-secondary: #1a1d24;
    --bg-card: #262730;
    --accent-primary: #06b6d4;
    --accent-secondary: #0891b2;
    --accent-success: #10b981;
    --accent-warning: #f59e0b;
    --accent-error: #ef4444;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --border-color: #374151;
}

/* ===== Global Styles ===== */
.stApp {
    background: linear-gradient(180deg, #0e1117 0%, #1a1d24 100%);
}

/* Remove top padding from main content */
.stMainBlockContainer, .block-container {
    padding-top: 0.5rem !important;
}

header[data-testid="stHeader"] {
    display: none !important;
}

/* ===== Header Styles ===== */
.main-header {
    background: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%);
    padding: 10px 20px;
    border-radius: 8px;
    margin-bottom: 15px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(6, 182, 212, 0.2);
}

.main-header h1 {
    color: white;
    font-size: 1.4rem;
    font-weight: 700;
    margin: 0;
}

.main-header p {
    color: rgba(255,255,255,0.9);
    font-size: 0.8rem;
    margin-top: 2px;
    margin-bottom: 0;
}

/* ===== Card Styles ===== */
.card {
    background: var(--bg-card);
    border-radius: 10px;
    padding: 15px 20px;
    margin-bottom: 15px;
    border: 1px solid var(--border-color);
}

.card-header {
    display: flex;
    align-items: center;
}

.card-header h3 {
    margin: 0;
    color: var(--text-primary);
    font-size: 1.1rem;
}

/* ===== Section Title ===== */
.section-title {
    background: var(--bg-card);
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 12px;
    border: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    gap: 10px;
}

.section-title h3 {
    margin: 0;
    color: var(--text-primary);
    font-size: 1rem;
    font-weight: 600;
}

/* ===== Text Area Styles ===== */
.stTextArea textarea {
    background-color: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    font-size: 14px !important;
    min-height: 280px !important;
}

.stTextArea textarea:focus {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.2) !important;
}

.stTextArea textarea::placeholder {
    color: var(--text-secondary) !important;
}

/* ===== Button Styles ===== */
.stButton > button {
    background: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    min-height: 42px !important;
    white-space: nowrap !important;
    box-shadow: 0 4px 12px rgba(6, 182, 212, 0.25) !important;
}

.stButton > button:hover {
    box-shadow: 0 6px 16px rgba(6, 182, 212, 0.35) !important;
    transform: translateY(-1px) !important;
}

/* ===== Select Box Styles ===== */
.stSelectbox > div > div {
    background-color: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
}

.stSelectbox > div > div:hover {
    border-color: var(--accent-primary) !important;
}

/* ===== File Uploader Styles ===== */
.stFileUploader > div {
    background: var(--bg-secondary) !important;
    border: 2px dashed var(--border-color) !important;
    border-radius: 8px !important;
    padding: 20px !important;
}

.stFileUploader > div:hover {
    border-color: var(--accent-primary) !important;
}

/* ===== Expander Styles ===== */
.streamlit-expanderHeader {
    background-color: var(--bg-card) !important;
    border-radius: 8px !important;
    border: 1px solid var(--border-color) !important;
}

.streamlit-expanderContent {
    background-color: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
}

/* ===== Metric Styles ===== */
.stMetric {
    background: var(--bg-card) !important;
    padding: 12px !important;
    border-radius: 8px !important;
    border: 1px solid var(--border-color) !important;
}

/* ===== Sidebar Styles ===== */
[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border-color) !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 0.5rem !important;
}

[data-testid="stSidebar"] .stMarkdown h3 {
    color: var(--accent-primary) !important;
    font-size: 0.7rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    margin-top: 4px !important;
    margin-bottom: 2px !important;
}

[data-testid="stSidebar"] .stMarkdown h2 {
    font-size: 1.1rem !important;
    margin-bottom: 0 !important;
}

[data-testid="stSidebar"] .stMarkdown p {
    margin-bottom: 0 !important;
}

[data-testid="stSidebar"] .stSelectbox {
    margin-bottom: 0 !important;
    margin-top: 0 !important;
}

[data-testid="stSidebar"] .stSelectbox > div {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}

[data-testid="stSidebar"] hr {
    margin: 4px 0 !important;
}

[data-testid="stSidebar"] .stMarkdown {
    margin-bottom: 0 !important;
}

[data-testid="stSidebar"] .element-container {
    margin-bottom: 0 !important;
}

/* ===== Progress Bar Styles ===== */
.stProgress > div > div {
    background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary)) !important;
    border-radius: 8px !important;
}

.stProgress {
    background-color: var(--bg-card) !important;
    border-radius: 8px !important;
}

/* ===== Alert Styles ===== */
.stAlert {
    border-radius: 8px !important;
}

/* ===== Tabs Styles ===== */
.stTabs [data-baseweb="tab-list"] {
    background-color: var(--bg-card) !important;
    border-radius: 8px !important;
    padding: 4px !important;
    gap: 4px !important;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 6px !important;
    color: var(--text-secondary) !important;
    background-color: transparent !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary)) !important;
    color: white !important;
}

/* ===== Divider ===== */
hr {
    border-color: var(--border-color) !important;
    margin: 20px 0 !important;
}

/* ===== Radio Button Styles ===== */
.stRadio > div {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

.stRadio > div > div {
    gap: 15px !important;
}

/* ===== Download Button ===== */
.stDownloadButton > button {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25) !important;
}

.stDownloadButton > button:hover {
    box-shadow: 0 6px 16px rgba(16, 185, 129, 0.35) !important;
}

/* ===== Caption/Help Text ===== */
.stCaption, small {
    color: var(--text-secondary) !important;
}

/* ===== Scrollbar Styles ===== */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}

::-webkit-scrollbar-track {
    background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--accent-primary);
}

/* ===== History Card Styles ===== */
.history-card {
    background: var(--bg-card);
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 12px;
    border: 1px solid var(--border-color);
}

.history-card:hover {
    border-color: var(--accent-primary);
}

.history-card-title {
    font-weight: 600;
    color: var(--text-primary);
    font-size: 0.95rem;
}

.history-card-meta {
    color: var(--text-secondary);
    font-size: 0.8rem;
}

/* ===== Animation ===== */
.fade-in {
    animation: fadeIn 0.4s ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ===== AI Feedback Content Styles ===== */
.feedback-container {
    background: transparent;
    padding: 0;
    margin-top: 8px;
}

/* Section headers as cards */
.feedback-container h2 {
    background: linear-gradient(135deg, #0f1419 0%, #151b23 100%);
    color: #06b6d4 !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    padding: 16px 20px !important;
    margin: 0 0 2px 0 !important;
    border-left: 4px solid #06b6d4;
    border-radius: 8px 8px 0 0;
    letter-spacing: 0.3px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.feedback-container h2::before {
    content: '';
    width: 8px;
    height: 8px;
    background: #06b6d4;
    border-radius: 50%;
    box-shadow: 0 0 8px rgba(6, 182, 212, 0.5);
}

/* Content sections after h2 */
.feedback-container h2 + p,
.feedback-container h2 + ul,
.feedback-container h2 + ol,
.feedback-container h2 + table {
    background: linear-gradient(135deg, #12171d 0%, #171d25 100%);
    border: 1px solid #1e2530;
    border-top: none;
    border-radius: 0 0 8px 8px;
    margin-top: 0 !important;
    margin-bottom: 16px !important;
}

.feedback-container h2 + p {
    padding: 20px 24px !important;
}

/* Regular paragraphs */
.feedback-container p {
    color: #d1d5db !important;
    font-size: 14.5px !important;
    line-height: 1.85 !important;
    margin-bottom: 12px !important;
}

/* Lists */
.feedback-container ul,
.feedback-container ol {
    padding: 16px 24px 16px 44px !important;
    margin: 0 !important;
}

.feedback-container li {
    color: #c9d1d9 !important;
    font-size: 14px !important;
    line-height: 1.75 !important;
    margin-bottom: 10px !important;
    padding: 8px 12px !important;
    background: rgba(6, 182, 212, 0.03);
    border-radius: 6px;
    border-left: 3px solid #252d3a;
}

.feedback-container li:hover {
    background: rgba(6, 182, 212, 0.06);
    border-left-color: #06b6d4;
}

.feedback-container ol li {
    list-style-type: decimal;
}

.feedback-container ul li {
    list-style-type: disc;
}

.feedback-container li::marker {
    color: #06b6d4 !important;
    font-weight: 600;
}

/* Bold text */
.feedback-container strong {
    color: #f8fafc !important;
    font-weight: 600 !important;
}

/* Emphasis */
.feedback-container em {
    color: #94a3b8 !important;
    font-style: italic !important;
}

/* Code */
.feedback-container code {
    background: rgba(6, 182, 212, 0.12) !important;
    color: #22d3ee !important;
    padding: 3px 8px !important;
    border-radius: 4px !important;
    font-size: 13px !important;
    font-family: 'Consolas', 'Monaco', monospace !important;
}

/* Table styling */
.feedback-container table {
    width: 100% !important;
    border-collapse: collapse !important;
    background: transparent !important;
    border-radius: 0 0 8px 8px !important;
    overflow: hidden !important;
}

.feedback-container th {
    background: rgba(6, 182, 212, 0.1) !important;
    color: #06b6d4 !important;
    padding: 14px 20px !important;
    text-align: left !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    border-bottom: 2px solid #06b6d4 !important;
}

.feedback-container td {
    padding: 14px 20px !important;
    color: #d1d5db !important;
    border-bottom: 1px solid #1e2530 !important;
    font-size: 14px !important;
}

.feedback-container tr:last-child td {
    border-bottom: none !important;
}

.feedback-container tr:hover td {
    background: rgba(6, 182, 212, 0.04) !important;
}

/* Status colors in table */
.feedback-container td:last-child {
    font-weight: 600;
}

/* Horizontal rules */
.feedback-container hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, #252d3a, transparent) !important;
    margin: 24px 0 !important;
}

/* Blockquote */
.feedback-container blockquote {
    border-left: 4px solid #f59e0b !important;
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(245, 158, 11, 0.03) 100%) !important;
    padding: 16px 20px !important;
    margin: 16px 0 !important;
    border-radius: 0 10px 10px 0 !important;
    color: #fcd34d !important;
}

/* Nested content styling */
.feedback-container h2 ~ p,
.feedback-container h2 ~ ul,
.feedback-container h2 ~ ol {
    background: linear-gradient(135deg, #12171d 0%, #171d25 100%);
    border: 1px solid #1e2530;
    border-radius: 8px;
    margin-bottom: 16px !important;
}

.feedback-container h2 ~ p {
    padding: 20px 24px !important;
}
</style>
"""


def inject_custom_css():
    """Inject custom CSS into Streamlit app"""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_header():
    """Render the main header"""
    import streamlit as st
    st.markdown("""
    <div class="main-header">
        <h1>CV Feedback Assistant</h1>
        <p>AI-powered resume analysis to help you land your dream job</p>
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    """Render the footer"""
    import streamlit as st
    st.markdown("""
    <div style="text-align: center; padding: 20px; color: #64748b; font-size: 0.8rem;">
        <p style="margin: 0;">Powered by <a href="https://ramazankartal.com/" target="_blank" style="color: #64748b; text-decoration: underline; text-underline-offset: 2px;">Ramazan Kartal</a></p>
    </div>
    """, unsafe_allow_html=True)
