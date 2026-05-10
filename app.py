import streamlit as st
import pandas as pd
import io
import json
import re
import os
import base64
import google.generativeai as genai
import plotly.express as px
import pandasql as psql

from llm_integration import get_bi_response, generate_dashboard_overview
from visualization import execute_and_plot
from admin_test import render_admin_dashboard

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Jive Analytics",
    page_icon="logo.png" if os.path.exists("logo.png") else "📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design System ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ── Global reset ── */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #0D0D0D !important;
        color: #E8E8E8;
    }

    /* ── Hide Streamlit chrome ── */
    #MainMenu, footer { visibility: hidden; }
    header { background: transparent !important; }
    .block-container {
        padding: 1.5rem 2rem 2rem 2rem !important;
        max-width: 100% !important;
    }

    /* ══════════════════════════════════════════
       SIDEBAR
    ══════════════════════════════════════════ */
    section[data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 1px solid #2A2A2A !important;
        padding-top: 0 !important;
    }
    section[data-testid="stSidebar"] > div {
        padding-top: 0 !important;
    }

    /* Sidebar top brand bar */
    .brand-bar {
        background: #1A1A1A;
        border-bottom: 1px solid #2A2A2A;
        padding: 1.6rem 1.4rem 1.4rem 1.4rem;
        margin: -4rem -1.2rem 1.8rem -1.2rem;
        display: flex;
        align-items: center;
        gap: 0.9rem;
    }
    .brand-icon {
        width: 38px; height: 38px;
        background: linear-gradient(135deg, #F97316, #FB923C);
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.1rem; font-weight: 800; color: #000;
        flex-shrink: 0;
        box-shadow: 0 4px 15px rgba(249, 115, 22, 0.3);
    }
    .brand-text { line-height: 1.1; }
    .brand-name {
        font-size: 0.95rem; font-weight: 800;
        color: #FFFFFF; letter-spacing: 1px;
        text-transform: uppercase;
    }
    .brand-sub {
        font-size: 0.62rem; font-weight: 500;
        color: #F97316; letter-spacing: 1.2px;
        text-transform: uppercase;
        opacity: 0.8;
    }

    /* Sidebar section labels */
    .sidebar-section {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.62rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #555;
        margin: 1.2rem 0 0.5rem 0;
        padding-left: 0.1rem;
    }

    /* Nav items */
    .nav-item {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        padding: 0.5rem 0.7rem;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 500;
        color: #888;
        cursor: pointer;
        margin-bottom: 2px;
        transition: all 0.15s;
    }
    .nav-item:hover { background: #1E1E1E; color: #DDD; }
    .nav-item.active {
        background: rgba(249,115,22,0.15);
        color: #F97316;
        border-left: 2px solid #F97316;
    }
    .nav-icon { font-size: 0.95rem; }

    /* ══════════════════════════════════════════
       TOP HEADER STRIP
    ══════════════════════════════════════════ */
    .page-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1.6rem;
        border-bottom: 1px solid #1E1E1E;
        padding-bottom: 1rem;
    }
    .page-title {
        font-size: 1.55rem;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.3px;
    }
    .breadcrumb {
        font-size: 0.72rem;
        color: #555;
        margin-bottom: 0.15rem;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.5px;
    }
    .orange-badge {
        background: #F97316;
        color: #000;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 0.35rem 0.85rem;
        border-radius: 6px;
        letter-spacing: 0.3px;
        cursor: pointer;
    }

    /* ══════════════════════════════════════════
       METRIC CARDS
    ══════════════════════════════════════════ */
    .metric-card {
        background: #1A1A1A;
        border: 1px solid #262626;
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
        position: relative;
        overflow: hidden;
        height: 100%;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, #F97316, #FB923C);
    }
    .metric-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.62rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #666;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 1.65rem;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.5px;
        line-height: 1;
    }
    .metric-sub {
        font-size: 0.72rem;
        color: #555;
        margin-top: 0.25rem;
    }
    .metric-delta {
        font-size: 0.7rem;
        color: #22C55E;
        font-weight: 600;
        margin-top: 0.4rem;
    }
    .metric-delta.neg { color: #EF4444; }

    /* ══════════════════════════════════════════
       PANEL CARDS (charts, table, etc.)
    ══════════════════════════════════════════ */
    .panel {
        background: #1A1A1A;
        border: 1px solid #262626;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1.2rem;
    }
    .panel-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.9rem;
    }
    .panel-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 2.5px;
        text-transform: uppercase;
        color: #999;
    }

    /* ══════════════════════════════════════════
       SUCCESS / STATUS BANNER
    ══════════════════════════════════════════ */
    .status-banner {
        background: rgba(249,115,22,0.08);
        border: 1px solid rgba(249,115,22,0.3);
        border-left: 3px solid #F97316;
        border-radius: 8px;
        padding: 0.75rem 1.1rem;
        margin-bottom: 1.4rem;
        font-size: 0.82rem;
        color: #CCC;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .status-dot {
        width: 7px; height: 7px;
        background: #F97316;
        border-radius: 50%;
        flex-shrink: 0;
        box-shadow: 0 0 8px #F97316;
    }

    /* ══════════════════════════════════════════
       FILE UPLOADER
    ══════════════════════════════════════════ */
    div[data-testid="stFileUploader"] {
        background: #141414;
        border: 1.5px dashed #333;
        border-radius: 10px;
        padding: 0.3rem;
        transition: border-color 0.2s;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #F97316;
    }
    div[data-testid="stFileUploader"] label {
        color: #888 !important;
        font-size: 0.8rem !important;
    }
    div[data-testid="stFileUploader"] button {
        background: #F97316 !important;
        color: #000 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 6px !important;
    }

    /* ══════════════════════════════════════════
       DATAFRAME
    ══════════════════════════════════════════ */
    .stDataFrame {
        border-radius: 10px !important;
        overflow: hidden !important;
        border: 1px solid #2A2A2A !important;
    }
    .stDataFrame th {
        background: #1E1E1E !important;
        color: #F97316 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.65rem !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        border-bottom: 1px solid #333 !important;
    }
    .stDataFrame td {
        background: #161616 !important;
        color: #CCC !important;
        font-size: 0.8rem !important;
        border-bottom: 1px solid #222 !important;
    }
    .stDataFrame tr:hover td {
        background: #1E1E1E !important;
    }

    /* ══════════════════════════════════════════
       EXPANDER
    ══════════════════════════════════════════ */
    .streamlit-expanderHeader {
        background: #1A1A1A !important;
        border: 1px solid #262626 !important;
        border-radius: 8px !important;
        color: #888 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.72rem !important;
        letter-spacing: 1px !important;
    }
    .streamlit-expanderContent {
        background: #141414 !important;
        border: 1px solid #222 !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
        color: #999 !important;
        font-size: 0.8rem !important;
    }

    /* ══════════════════════════════════════════
       EMPTY STATE
    ══════════════════════════════════════════ */
    .empty-state {
        background: #141414;
        border: 1px solid #222;
        border-radius: 16px;
        padding: 3rem;
        text-align: center;
        margin-top: 2rem;
    }
    .empty-icon {
        font-size: 3.5rem;
        margin-bottom: 1rem;
        filter: grayscale(0.3);
    }
    .empty-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #CCC;
        margin-bottom: 0.5rem;
    }
    .empty-sub {
        font-size: 0.82rem;
        color: #555;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.7rem;
        margin-top: 1.2rem;
    }
    .feature-tile {
        background: #1A1A1A;
        border: 1px solid #262626;
        border-radius: 10px;
        padding: 0.9rem 1rem;
        text-align: left;
        display: flex;
        align-items: flex-start;
        gap: 0.6rem;
    }
    .feature-tile-icon { font-size: 1.1rem; margin-top: 1px; }
    .feature-tile-text { font-size: 0.77rem; color: #888; line-height: 1.4; }
    .feature-tile-title { font-size: 0.82rem; font-weight: 600; color: #DDD; margin-bottom: 0.15rem; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: #111; }
    ::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #F97316; }

    /* Override st.info box */
    div[data-testid="stAlert"] {
        background: #1A1A1A !important;
        border: 1px solid #2A2A2A !important;
        border-left: 3px solid #F97316 !important;
        border-radius: 8px !important;
        color: #AAA !important;
    }

    /* Donezo-inspired minimalist business theme override */
    html, body, [class*="css"], .stApp {
        background: #E9EAEC !important;
        color: #0B0F0E !important;
    }
    .stApp * {
        color: inherit;
    }
    p, span, label, div[data-testid="stMarkdownContainer"], div[data-testid="stMarkdownContainer"] p {
        color: #0B0F0E !important;
    }
    header { background: transparent !important; }
    .block-container {
        background: #F6F6F4;
        border: 12px solid #FFFFFF;
        border-radius: 28px;
        box-shadow: 0 22px 60px rgba(15, 23, 42, 0.12);
        margin: 1.3rem auto 1.8rem auto;
        max-width: 1420px !important;
        padding: 1.2rem 1.35rem 1.5rem 1.35rem !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #F2F3F1 !important;
        border-right: 1px solid #E6E8E4 !important;
    }
    .brand-bar {
        background: transparent;
        border-bottom: 0;
        padding: 1.5rem 1.25rem 1.1rem 1.25rem;
    }
    .brand-icon {
        background: #0C7A43 !important;
        color: #FFFFFF !important;
        border-radius: 50%;
        box-shadow: none;
    }
    .brand-name {
        color: #050505;
        font-size: 1rem;
        letter-spacing: 0;
        text-transform: none;
    }
    .brand-sub {
        color: #7C8580;
        letter-spacing: 0;
        text-transform: none;
    }
    .sidebar-section {
        color: #7C8580;
        letter-spacing: 0.8px;
        margin-top: 2rem;
    }
    .page-header {
        background: #FFFFFF;
        border: 0;
        border-radius: 18px;
        margin-bottom: 1rem;
        padding: 1.35rem 1.45rem;
    }
    .page-title {
        color: #050505;
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: 0;
    }
    .breadcrumb {
        color: #8A918E;
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        letter-spacing: 0;
        margin-top: 0.35rem;
    }
    .orange-badge {
        background: #0B7A43;
        color: #FFFFFF !important;
        border: 1px solid #0B7A43;
        border-radius: 999px;
        padding: 0.75rem 1.2rem;
        cursor: default;
    }
    .jive-topbar {
        background: #FFFFFF;
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 0.8rem;
        padding: 0.8rem 1rem;
    }
    .jive-search {
        align-items: center;
        background: #F6F6F4;
        border-radius: 999px;
        color: #89918D !important;
        display: flex;
        flex: 1;
        gap: 0.55rem;
        max-width: 380px;
        padding: 0.75rem 1rem;
    }
    .jive-profile {
        align-items: center;
        display: flex;
        gap: 0.75rem;
    }
    .jive-avatar {
        align-items: center;
        background: #F2C6BC;
        border-radius: 50%;
        color: #103C27 !important;
        display: flex;
        font-weight: 800;
        height: 42px;
        justify-content: center;
        width: 42px;
    }
    .metric-card, .panel, .empty-state, .feature-tile {
        background: #FFFFFF;
        border: 0;
        border-radius: 18px;
        box-shadow: none;
    }
    .metric-card::before {
        display: none;
    }
    .metric-card {
        min-height: 150px;
        padding: 1.5rem 1.35rem;
    }
    .metric-card.primary-card {
        background: linear-gradient(145deg, #0E6F3D 0%, #1C8F55 100%);
    }
    .metric-card.primary-card .metric-label,
    .metric-card.primary-card .metric-value,
    .metric-card.primary-card .metric-sub,
    .metric-card.primary-card .metric-delta {
        color: #FFFFFF !important;
    }
    .metric-label, .panel-title {
        color: #050505;
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        letter-spacing: 0;
        text-transform: none;
    }
    .metric-value {
        color: #050505;
        font-size: 2.7rem;
        font-weight: 800;
        margin-top: 0.8rem;
    }
    .metric-sub, .empty-sub, .feature-tile-text { color: #7C8580 !important; }
    .metric-delta { color: #3F7A52 !important; }
    .metric-delta.neg { color: #B42318 !important; }
    .empty-title, .feature-tile-title { color: #050505 !important; }
    .status-banner {
        background: #FFFFFF;
        border: 0;
        border-radius: 18px;
        color: #15211A;
    }
    .status-dot {
        background: #0B7A43;
        box-shadow: none;
    }
    div[data-testid="stFileUploader"] {
        background: #FFFFFF;
        border-color: #DDE2DE;
        border-radius: 18px;
    }
    div[data-testid="stFileUploader"]:hover { border-color: #0B7A43; }
    div[data-testid="stFileUploader"] button {
        background: #0B7A43 !important;
        color: #FFFFFF !important;
        border-radius: 999px !important;
    }
    .stDataFrame { border: 1px solid #E5E7EB !important; }
    .stDataFrame th {
        background: #F6F6F4 !important;
        color: #0B0F0E !important;
        border-bottom: 1px solid #E5E7EB !important;
    }
    .stDataFrame td {
        background: #FFFFFF !important;
        color: #0B0F0E !important;
        border-bottom: 1px solid #F3F4F6 !important;
    }
    .stDataFrame tr:hover td { background: #F9FAFB !important; }
    div[data-testid="stAlert"] {
        background: #FFFFFF !important;
        border: 1px solid #DDE2DE !important;
        border-left: 3px solid #0B7A43 !important;
        color: #15211A !important;
    }
    div[data-testid="stButton"] button {
        background: #FFFFFF !important;
        border: 1px solid #0B3D2E !important;
        border-radius: 999px !important;
        color: #0B3D2E !important;
        font-weight: 600 !important;
    }
    div[data-testid="stButton"] button:hover {
        background: #0B7A43 !important;
        color: #FFFFFF !important;
    }
    input, textarea, [contenteditable="true"] {
        color: #0B0F0E !important;
        -webkit-text-fill-color: #0B0F0E !important;
    }
    .stChatMessage {
        background: #FFFFFF !important;
        border-radius: 18px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # Brand
    import base64
    import os
    if os.path.exists("logo.png"):
        with open("logo.png", "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        brand_icon_html = f'<img class="brand-icon" src="data:image/png;base64,{logo_b64}" style="object-fit: contain; background: transparent; padding: 2px;" />'
    else:
        brand_icon_html = '<div class="brand-icon">JR</div>'

    st.markdown(
        f"""
        <div class="brand-bar">
            {brand_icon_html}
            <div class="brand-text">
                <div class="brand-name">Jive Analytics</div>
                <div class="brand-sub">Jairamm Reddi workspace</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Navigation
    st.markdown('<div class="sidebar-section">Main Menu</div>', unsafe_allow_html=True)
    
    # Custom Radio styling to make it look like Nav
    st.markdown("""
        <style>
        /* Hide the radio button input itself */
        div.row-widget.stRadio > div[role="radiogroup"] > label > div:first-child {
            display: none !important;
        }
        
        /* Style the labels as nav items */
        div.row-widget.stRadio > div[role="radiogroup"] > label {
            display: flex !important;
            align-items: center !important;
            padding: 0.65rem 1rem !important;
            border-radius: 8px !important;
            margin-bottom: 4px !important;
            background: transparent !important;
            cursor: pointer !important;
            transition: all 0.2s !important;
            border: 1px solid transparent !important;
            width: 100% !important;
        }
        
        /* Hover state */
        div.row-widget.stRadio > div[role="radiogroup"] > label:hover {
            background: #F3F4F6 !important;
            border-color: #E5E7EB !important;
        }
        
        /* Selected/Active state */
        div.row-widget.stRadio > div[role="radiogroup"] > label[data-active="true"] {
            background: #E8F4EE !important;
            border-left: 3px solid #0B7A43 !important;
        }
        
        /* Target the text inside the radio */
        div.row-widget.stRadio [data-testid="stMarkdownContainer"] p {
            color: #4B5563 !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            margin: 0 !important;
        }
        
        /* Highlight text for active radio */
        div.row-widget.stRadio > div[role="radiogroup"] > label[data-active="true"] p {
            color: #0B7A43 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    menu = st.radio(
        "Navigation",
        ["📊 Dashboard", "💬 Talk to Data", "🧪 Admin Test"],
        label_visibility="collapsed"
    )
    
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section">Actions</div>', unsafe_allow_html=True)
    
    # Custom styling for native streamlit buttons in sidebar
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] button {
            background-color: #FFFFFF !important;
            border: 1px solid #D1D5DB !important;
            color: #374151 !important;
            border-radius: 8px !important;
        }
        section[data-testid="stSidebar"] button:hover {
            border-color: #0B7A43 !important;
            color: #0B7A43 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        if "messages" in st.session_state:
            st.session_state.messages = []
            st.rerun()

    if st.button("🔌 Disconnect Dataset", use_container_width=True):
        if "df" in st.session_state:
            del st.session_state["df"]
            del st.session_state["dataset_context"]
            if "dashboard_overview" in st.session_state:
                del st.session_state["dashboard_overview"]
            st.rerun()

# ── Main Dashboard (Only if data loaded) ──────────────────────────────────────
if "df" in st.session_state:
    df = st.session_state["df"]
    dataset_context = st.session_state["dataset_context"]

    # ── Auto-generate AI Overview if missing ──
    if "dashboard_overview" not in st.session_state:
        with st.spinner("Generating AI Data Overview..."):
            st.session_state["dashboard_overview"] = generate_dashboard_overview(dataset_context)

    # ── Main Header ───────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="jive-topbar">
            <div class="jive-search">Search dataset or ask a question</div>
            <div class="jive-profile">
                <div style="text-align:right;">
                    <div style="font-weight:700; color:#050505;">Jairamm Reddi</div>
                    <div style="font-size:0.82rem; color:#7C8580;">AI Business Intelligence</div>
                </div>
                <div class="jive-avatar">JR</div>
            </div>
        </div>
        <div class="page-header">
            <div>
                <div class="breadcrumb">BI Analytics &nbsp;›&nbsp; {menu.split()[-1]}</div>
                <div class="page-title">Dashboard</div>
            </div>
            <span class="orange-badge">⬡ &nbsp;AI Ready</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if menu == "📊 Dashboard":
        # Status banner
        num_rows, num_cols = df.shape
        st.markdown(
            f"""
            <div class="status-banner">
                <div class="status-dot"></div>
                <div>
                    <strong style="color:#0B7A43;">Dataset Status:</strong>
                    &nbsp;active &amp; ready —&nbsp;
                    <strong style="color:#111827;">{num_rows:,}</strong> rows,&nbsp;
                    <strong style="color:#111827;">{num_cols}</strong> columns detected
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Metric tiles ──────────────────────────────────────────────────────────
        overview = st.session_state.get("dashboard_overview", {})
        metrics_data = overview.get("metrics", [])

        if metrics_data:
            # Display dynamic AI metrics
            cols = st.columns(len(metrics_data))
            for i, m in enumerate(metrics_data):
                try:
                    res = psql.sqldf(m["sql"], {"df": df})
                    val = res.iloc[0, 0]
                    # Format value if numeric
                    if isinstance(val, (int, float)):
                        if val >= 1_000_000:
                            display_val = f"{val/1_000_000:.1f}M"
                        elif val >= 1_000:
                            display_val = f"{val/1_000:.1f}K"
                        else:
                            display_val = f"{val}"
                    else:
                        display_val = str(val)
                    
                    prefix = m.get("prefix", "")
                    suffix = m.get("suffix", "")
                    
                    cols[i].markdown(
                        f"""
                        <div class="metric-card {'primary-card' if i == 0 else ''}">
                            <div class="metric-label">{m['label']}</div>
                            <div class="metric-value">{prefix}{display_val}{suffix}</div>
                            <div class="metric-sub">AI Calculated</div>
                            <div class="metric-delta">▲ Live</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                except Exception as e:
                    cols[i].error(f"Error calculation {m['label']}")
        else:
            # Fallback to default metrics if missing
            c1, c2, c3, c4 = st.columns(4)

            numeric_cols = df.select_dtypes("number").shape[1]
            text_cols    = df.select_dtypes("object").shape[1]
            missing_pct  = round(df.isnull().mean().mean() * 100, 1)

            for idx, (col, label, val, sub) in enumerate([
                (c1, "TOTAL ROWS",     f"{num_rows:,}",    "Records in dataset"),
                (c2, "COLUMNS",        str(num_cols),       "Dataset dimensions"),
                (c3, "NUMERIC COLS",   str(numeric_cols),   f"{text_cols} text columns"),
                (c4, "MISSING DATA",   f"{missing_pct}%",   "Null value rate"),
            ]):
                delta_cls = "neg" if label == "MISSING DATA" and missing_pct > 5 else ""
                delta_sym = "▲" if label != "MISSING DATA" else ("▼" if missing_pct > 0 else "✔")
                col.markdown(
                    f"""
                    <div class="metric-card {'primary-card' if idx == 0 else ''}">
                        <div class="metric-label">{label}</div>
                        <div class="metric-value">{val}</div>
                        <div class="metric-sub">{sub}</div>
                        <div class="metric-delta {delta_cls}">{delta_sym} Live</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── AI Data Summary ────────────────────────────────────────────────────────
        if "dashboard_overview" in st.session_state:
            st.markdown(
                f"""
                <div style="background: #FFFFFF; border: 0; border-left: 3px solid #0B7A43; padding: 1.25rem; border-radius: 18px; margin-bottom: 2rem;">
                    <h4 style="color: #0B7A43; margin-top: 0; margin-bottom: 0.5rem; font-size: 1.1rem;">AI Data Summary</h4>
                    <p style="color: #374151; margin: 0; font-size: 0.95rem; line-height: 1.5;">{st.session_state["dashboard_overview"].get("summary", "")}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        # ── Data Preview Panel ────────────────────────────────────────────────────
        st.markdown(
            """
            <div class="panel-header">
                <span class="panel-title">◈ &nbsp; Data Preview</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.dataframe(df.head(5), width="stretch", height=220)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Interactive Charts ────────────────────────────────────────────────────
        if "dashboard_overview" in st.session_state:
            overview = st.session_state["dashboard_overview"]
            if overview.get("chart1") or overview.get("chart2"):
                st.markdown(
                    """
                    <div class="panel-header">
                        <span class="panel-title">📈 &nbsp; AI Recommended Charts</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                c1, c2 = st.columns(2)
                with c1:
                    if overview.get("chart1"):
                        fig1, _info1, _df1 = execute_and_plot(overview["chart1"], df)
                        if fig1:
                            st.plotly_chart(fig1, use_container_width=True)
                        else:
                            st.info("Chart 1 could not be visualized.")
                with c2:
                    if overview.get("chart2"):
                        fig2, _info2, _df2 = execute_and_plot(overview["chart2"], df)
                        if fig2:
                            st.plotly_chart(fig2, use_container_width=True)
                        else:
                            st.info("Chart 2 could not be visualized.")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Schema Panel ──────────────────────────────────────────────────────────
        with st.expander("◉  Dataset Schema & AI Context  ·  Click to expand", expanded=True):
            st.markdown(dataset_context)

    elif menu == "💬 Talk to Data":
        st.markdown(
            """
            <div class="panel-header">
                <span class="panel-title">💬 &nbsp; Talk to your Data</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ══════════════════════════════════════════════════════════════════════════════
        # PHASE 4 — Streamlit Chat UI & Session State
        # ══════════════════════════════════════════════════════════════════════════════
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # 1. New Default Greeting + Recommendation Chips (only if empty)
        if not st.session_state.messages:
            st.markdown(
                """
                <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px; padding: 2rem; text-align: center; margin-top: 1rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">👋</div>
                    <h2 style="color: #111827; margin-bottom: 0.5rem; font-weight: 600;">Hello, Jairamm Reddi</h2>
                    <p style="color: #4B5563; font-size: 1.1rem; max-width: 500px; margin: 0 auto; margin-bottom: 1.5rem;">
                        I'm your AI Data Assistant. Ask me anything about your dataset, 
                        and I'll write the SQL and build the charts for you.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("<br>", unsafe_allow_html=True)
            st.write("💡 **Try one of these to get started:**")
            
            # Determine 3 recommendations
            recs = ["Show me the total revenue over time", "Which category has the most leads?", "What is the conversion rate by channel?"]
            if "dashboard_overview" in st.session_state:
                overview = st.session_state["dashboard_overview"]
                if overview.get("chart1") and overview["chart1"].get("x_axis"):
                    recs[0] = f"Analyze {overview['chart1']['x_axis']} performance"
                if overview.get("chart2") and overview["chart2"].get("x_axis"):
                    recs[1] = f"Breakdown by {overview['chart2']['x_axis']}"

            cols = st.columns(3)
            suggestion = None
            for i, rec in enumerate(recs):
                if cols[i].button(rec, use_container_width=True, key=f"rec_{i}"):
                    suggestion = rec
        else:
            suggestion = None

        # 1. Render existing messages from session_state
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
                # If the assistant message has a figure or dataframe stored, render them
                if msg["role"] == "assistant":
                    if msg.get("fig") is not None:
                        st.plotly_chart(msg["fig"], width="stretch")
                    
                    if msg.get("df") is not None and not msg["df"].empty:
                        with st.expander("◉ View Raw SQL Data Used for Analysis"):
                            st.dataframe(msg["df"], width="stretch")
                            if msg.get("sql"):
                                st.code(msg["sql"], language="sql")

        # 2. Chat Input
        input_prompt = st.chat_input("Ask a question about your data...")
        prompt = input_prompt if input_prompt else suggestion

        # 3. Handle new user prompt
        if prompt:
            # a. Append and show user prompt
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # b. Assistant response block
            with st.chat_message("assistant"):
                with st.spinner("Analyzing data and generating dashboard..."):
                    
                    # Retrieve last 3 interactions for history context
                    history_subset = st.session_state.messages[-4:-1]  # exclude the current prompt from history
                    chat_history_str = "\n".join(
                        f"{m['role'].upper()}: {m['content']}" for m in history_subset
                    )

                    # Call Gemini (Phase 2)
                    json_config = get_bi_response(prompt, dataset_context, chat_history_str)
                    
                    # Execute SQL and Plot (Phase 3)
                    fig, insight, result_df = execute_and_plot(json_config, df)

                    # Display Results
                    st.markdown(insight)
                    if fig is not None:
                        st.plotly_chart(fig, width="stretch")
                    
                    if result_df is not None and not result_df.empty:
                        with st.expander("◉ View Raw SQL Data Used for Analysis"):
                            st.dataframe(result_df, width="stretch")
                            sql_query = json_config.get("sql", "")
                            if sql_query and sql_query != "ERROR":
                                st.code(sql_query, language="sql")

                    # c. Append assistant response to state
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": insight,
                        "fig": fig,
                        "df": result_df,
                        "sql": json_config.get("sql", "")
                    })

    elif menu == "🧪 Admin Test":
        render_admin_dashboard(df, dataset_context)

    # Store in session state
    st.session_state["df"] = df
    st.session_state["dataset_context"] = dataset_context

    st.markdown("<br><hr>", unsafe_allow_html=True)


else:
    # ── Main Header (Original style for empty state) ──────────────────────────
    st.markdown(
        """
        <div class="page-header">
            <div>
                <div class="breadcrumb">Dashboard &nbsp;›&nbsp; Overview</div>
                <div class="page-title">Welcome back, Jairamm Reddi</div>
            </div>
            <span class="orange-badge">⬡ &nbsp;AI Ready</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Move Uploader Here (Inside Empty State) ───────────────────────────────
    uploaded_file = st.file_uploader(
        label="Drop your CSV dataset here to begin",
        type=["csv"],
        help="Drag and drop your .csv file here for AI-powered analysis."
    )

    if uploaded_file is not None:
        def _smart_read_csv(raw: bytes) -> pd.DataFrame:
            for enc in ("utf-8", "latin-1", "cp1252"):
                try:
                    text = raw.decode(enc, errors="replace")
                    break
                except Exception:
                    continue
            else:
                return None

            lines = text.splitlines()
            start_idx = 0
            for i, line in enumerate(lines):
                stripped = line.strip()
                if not stripped:
                    continue
                printable = sum(1 for c in stripped if c.isprintable() and c != "\ufffd")
                ratio = printable / len(stripped) if stripped else 0
                has_delimiter = "," in stripped or "\t" in stripped
                if ratio >= 0.90 and has_delimiter:
                    start_idx = i
                    break

            clean_text = "\n".join(lines[start_idx:])
            try:
                return pd.read_csv(io.StringIO(clean_text))
            except Exception:
                return None

        _raw = uploaded_file.read()
        df = _smart_read_csv(_raw)

        if df is None:
            st.error("❌ Could not parse the CSV. Please re-save as UTF-8 and try again.")
            st.stop()

        clean_cols = {
            col: col for col in df.columns
            if all(c.isprintable() and c != "\ufffd" for c in str(col))
        }
        df = df[[c for c in df.columns if c in clean_cols]]

        schema_lines = ["### DataFrame Schema\n"]
        for col, dtype in df.dtypes.items():
            schema_lines.append(f"  - `{col}` : {dtype}")
        schema_str = "\n".join(schema_lines)
        sample_str = df.head(3).to_string(index=False)
        dataset_context = (
            f"{schema_str}\n\n"
            f"### First 3 Rows (sample)\n\n"
            f"```\n{sample_str}\n```"
        )
        
        st.session_state["df"] = df
        st.session_state["dataset_context"] = dataset_context

        # dashboard_overview will be generated by the auto-check logic at the top of the 'if df in state' block
        st.rerun()

    # ── Empty State 

    # The actual Empty Content
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-icon">📊</div>
            <div class="empty-title">No dataset loaded</div>
            <div class="empty-sub">
                Upload a <strong style="color:#0B7A43;">.csv file</strong> from the sidebar<br>
                to unlock AI-powered business intelligence.
            </div>
            <div class="feature-grid">
                <div class="feature-tile">
                    <div class="feature-tile-icon">📈</div>
                    <div>
                        <div class="feature-tile-title">Visual Analytics</div>
                        <div class="feature-tile-text">Interactive charts powered by Plotly</div>
                    </div>
                </div>
                <div class="feature-tile">
                    <div class="feature-tile-icon">🤖</div>
                    <div>
                        <div class="feature-tile-title">AI Insights</div>
                        <div class="feature-tile-text">Gemini-powered business summaries</div>
                    </div>
                </div>
                <div class="feature-tile">
                    <div class="feature-tile-icon">🔍</div>
                    <div>
                        <div class="feature-tile-title">Natural Language Query</div>
                        <div class="feature-tile-text">Ask questions in plain English</div>
                    </div>
                </div>
                <div class="feature-tile">
                    <div class="feature-tile-icon">⚡</div>
                    <div>
                        <div class="feature-tile-title">SQL Engine</div>
                        <div class="feature-tile-text">Run SQL queries on your dataset</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
