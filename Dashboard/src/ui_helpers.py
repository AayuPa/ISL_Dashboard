"""
UI Helper functions and Custom CSS injection for Indian Super League Analytics Platform.
Enforces light aesthetics, dark fonts, uncluttered spacing, and palette:
[#815337] [#926a52] [#ab8a76] [#d2b7a7] [#f7e5da]
"""

import streamlit as st
from src.config import PALETTE, PILLAR_CONFIG

def load_custom_css():
    """Inject custom responsive CSS adhering strictly to the warm light aesthetic."""
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    /* Global Typography & Light Aesthetics */
    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: {PALETTE["text_dark"]} !important;
    }}
    
    .stApp {{
        background-color: {PALETTE["bg_main"]};
    }}
    
    /* Top Header Banner */
    .hero-banner {{
        background: linear-gradient(135deg, {PALETTE["light_card"]} 0%, {PALETTE["bg_secondary"]} 100%);
        border: 1px solid {PALETTE["border"]};
        border-radius: 14px;
        padding: 24px 28px;
        margin-bottom: 22px;
        box-shadow: 0 2px 8px rgba(129, 83, 55, 0.05);
    }}
    
    .hero-title {{
        font-size: 1.85rem;
        font-weight: 800;
        color: {PALETTE["primary"]} !important;
        margin: 4px 0 6px 0;
        letter-spacing: -0.02em;
    }}
    
    .hero-subtitle {{
        font-size: 0.95rem;
        color: {PALETTE["text_muted"]} !important;
        line-height: 1.5;
        margin: 0;
    }}
    
    /* Pill Badges */
    .badge-pill {{
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-right: 6px;
        margin-bottom: 4px;
    }}
    
    .badge-primary {{
        background-color: {PALETTE["light_card"]};
        color: {PALETTE["primary"]} !important;
        border: 1px solid {PALETTE["border"]};
    }}
    
    .badge-secondary {{
        background-color: {PALETTE["bg_secondary"]};
        color: {PALETTE["secondary"]} !important;
        border: 1px solid {PALETTE["accent"]};
    }}
    
    /* Executive Metric Card */
    .metric-card {{
        background-color: {PALETTE["white"]};
        border: 1px solid {PALETTE["border"]};
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: 0 1px 4px rgba(129, 83, 55, 0.04);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(129, 83, 55, 0.08);
        border-color: {PALETTE["primary"]};
    }}
    
    .metric-label {{
        font-size: 0.78rem;
        font-weight: 600;
        color: {PALETTE["text_muted"]} !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 4px;
    }}
    
    .metric-value {{
        font-size: 1.65rem;
        font-weight: 800;
        color: {PALETTE["primary"]} !important;
        line-height: 1.1;
    }}
    
    .metric-subtext {{
        font-size: 0.75rem;
        color: {PALETTE["text_muted"]} !important;
        margin-top: 4px;
    }}
    
    /* Pillar Cards */
    .pillar-card {{
        background: {PALETTE["white"]};
        border: 1px solid {PALETTE["border"]};
        border-top: 4px solid {PALETTE["primary"]};
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 12px;
    }}
    
    /* Code and Math blocks */
    code, pre {{
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
    }}
    
    /* Streamlit Sidebar custom styling */
    [data-testid="stSidebar"] {{
        background-color: {PALETTE["bg_secondary"]};
        border-right: 1px solid {PALETTE["border"]};
    }}
    
    /* Streamlit Tabs Customization */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        border-bottom: 1px solid {PALETTE["border"]};
    }}
    
    .stTabs [data-baseweb="tab"] {{
        height: 42px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px 8px 0px 0px;
        color: {PALETTE["text_muted"]};
        font-weight: 600;
        font-size: 0.9rem;
        padding: 0 16px;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {PALETTE["light_card"]} !important;
        color: {PALETTE["primary"]} !important;
        border-bottom: 3px solid {PALETTE["primary"]} !important;
    }}
    
    /* Clean button styling */
    .stButton > button {{
        background-color: {PALETTE["primary"]};
        color: #FFFFFF !important;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        padding: 6px 16px;
        transition: background 0.15s ease;
    }}
    
    .stButton > button:hover {{
        background-color: {PALETTE["secondary"]};
        color: #FFFFFF !important;
    }}
    
    /* Dataframe styling */
    [data-testid="stDataFrame"] {{
        border: 1px solid {PALETTE["border"]};
        border-radius: 8px;
        overflow: hidden;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_hero_banner(title: str, subtitle: str, badge: str = "ISL ANALYTICS"):
    """Render top hero banner with clean warm palette."""
    html = f"""
    <div class="hero-banner">
        <div>
            <span class="badge-pill badge-primary">{badge}</span>
            <span class="badge-pill badge-secondary">SOFASCORE STATS ENGINE</span>
            <div class="hero-title">{title}</div>
            <p class="hero-subtitle">{subtitle}</p>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_sidebar_brand():
    """Render branded ISL Intelligence sidebar title and active 2026/27 campaign badge."""
    st.sidebar.markdown(
        f"""
        <div style="padding: 10px 0 14px 0; border-bottom: 1px solid {PALETTE['border']}; margin-bottom: 14px;">
            <div style="font-size: 0.72rem; font-weight: 800; color: {PALETTE['secondary']}; letter-spacing: 0.08em; text-transform: uppercase;">
                Indian Super League • Official Hub
            </div>
            <div style="font-size: 1.25rem; font-weight: 800; color: {PALETTE['primary']};">
                ISL Analytics Suite
            </div>
            <div style="display:flex; align-items:center; gap:6px; margin-top:6px;">
                <span class="badge-pill badge-primary" style="margin:0;">2026/27 SEASON</span>
                <span style="font-size: 0.75rem; color: {PALETTE['text_muted']};">Matchweeks 1–6 Live</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    return "2026-27"
