"""
Dream Machine — Professional Design System v2
Mobile-first, PWA-ready, premium dark UI.
"""
import streamlit as st


def inject_pwa_tags():
    """Inject PWA manifest + mobile meta tags. Call once from app.py."""
    st.markdown("""
    <link rel="manifest" href="data:application/json;base64,eyJuYW1lIjoiRHJlYW0gTWFjaGluZSIsInNob3J0X25hbWUiOiJEcmVhbSIsInN0YXJ0X3VybCI6Ii8iLCJkaXNwbGF5Ijoic3RhbmRhbG9uZSIsImJhY2tncm91bmRfY29sb3IiOiIjMEEwQTEyIiwidGhlbWVfY29sb3IiOiIjNUM2QkZGIiwiaWNvbnMiOlt7InNyYyI6ImRhdGE6aW1hZ2UvcG5nO2Jhc2U2NCxpVkJPUncwS0dnb0FBQUFOU1VoRVVnQUFBQ0FBQUFBZkNBWUFBQUJMTitGM0FBQUFBVWxFUVZSSVMyTmdBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBPT0iLCJzaXplcyI6IjE5MngxOTIiLCJ0eXBlIjoiaW1hZ2UvcG5nIn1dfQ==">
    <meta name="theme-color" content="#5C6BFF">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Dream Machine">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    """, unsafe_allow_html=True)


def inject_styles():
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

    <style>
    /* =============================================
       ROOT VARIABLES
    ============================================= */
    :root {
        --bg-primary: #07070F;
        --bg-secondary: #0C0C1A;
        --bg-surface: #111124;
        --bg-card: rgba(255,255,255,0.035);
        --bg-card-hover: rgba(255,255,255,0.065);
        --color-primary: #5C6BFF;
        --color-primary-dark: #4050E8;
        --color-primary-light: #7B88FF;
        --color-accent: #00F5D4;
        --color-accent-dim: rgba(0,245,212,0.12);
        --color-warning: #FFB800;
        --color-danger: #FF6450;
        --color-success: #00F5D4;
        --color-text: #EEEEF6;
        --color-text-secondary: #A0A0BC;
        --color-muted: #5A5A78;
        --color-border: rgba(92,107,255,0.18);
        --color-border-bright: rgba(92,107,255,0.45);
        --color-border-subtle: rgba(255,255,255,0.06);
        --glow-primary: 0 0 24px rgba(92,107,255,0.28);
        --glow-accent: 0 0 24px rgba(0,245,212,0.28);
        --shadow-card: 0 4px 24px rgba(0,0,0,0.35), 0 1px 0 rgba(255,255,255,0.04) inset;
        --shadow-elevated: 0 12px 48px rgba(0,0,0,0.5), 0 1px 0 rgba(255,255,255,0.06) inset;
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 24px;
        --radius-2xl: 32px;
        --font-display: 'Space Grotesk', -apple-system, sans-serif;
        --font-body: 'Inter', -apple-system, sans-serif;
        --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
        --nav-height: 56px;
        --bottom-nav-height: 64px;
    }

    /* =============================================
       GLOBAL BASE
    ============================================= */
    *, *::before, *::after { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }

    html, body {
        font-family: var(--font-body) !important;
        background: var(--bg-primary) !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    [data-testid="stAppViewContainer"] {
        background: var(--bg-primary) !important;
        min-height: 100vh;
    }

    /* Subtle grid background */
    [data-testid="stAppViewContainer"]::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image:
            linear-gradient(rgba(92,107,255,0.035) 1px, transparent 1px),
            linear-gradient(90deg, rgba(92,107,255,0.035) 1px, transparent 1px);
        background-size: 52px 52px;
        pointer-events: none;
        z-index: 0;
    }

    /* Ambient glow top */
    [data-testid="stAppViewContainer"]::after {
        content: '';
        position: fixed;
        top: -200px; left: 50%;
        transform: translateX(-50%);
        width: 800px; height: 400px;
        background: radial-gradient(ellipse, rgba(92,107,255,0.08) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
    }

    [data-testid="stMain"], [data-testid="block-container"] {
        position: relative;
        z-index: 1;
    }

    /* Block container padding */
    [data-testid="block-container"] {
        padding-top: 1.5rem !important;
        padding-bottom: 5rem !important;
    }

    /* Hide Streamlit chrome */
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    [data-testid="stToolbar"] { display: none !important; }
    .stDeployButton { display: none !important; }
    [data-testid="stDecoration"] { display: none !important; }
    [data-testid="stHeader"] { display: none !important; }

    /* =============================================
       SIDEBAR — Professional
    ============================================= */
    [data-testid="stSidebar"] {
        background: rgba(7,7,15,0.98) !important;
        border-right: 1px solid var(--color-border) !important;
        backdrop-filter: blur(24px);
    }
    [data-testid="stSidebar"] [data-testid="stMarkdown"] p {
        color: var(--color-text-secondary);
        font-size: 13px;
        line-height: 1.6;
    }
    [data-testid="stSidebarNav"] {
        padding: 8px !important;
    }
    [data-testid="stSidebarNav"] a {
        color: var(--color-muted) !important;
        font-family: var(--font-display) !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        border-radius: var(--radius-md) !important;
        padding: 10px 14px !important;
        transition: all 0.2s ease !important;
        margin-bottom: 2px !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
    }
    [data-testid="stSidebarNav"] a:hover {
        color: var(--color-text) !important;
        background: rgba(92,107,255,0.1) !important;
    }
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        color: var(--color-primary) !important;
        background: rgba(92,107,255,0.15) !important;
        font-weight: 600 !important;
    }

    /* =============================================
       TYPOGRAPHY
    ============================================= */
    h1, h2, h3, h4, h5, h6 {
        font-family: var(--font-display) !important;
        color: var(--color-text) !important;
        letter-spacing: -0.025em;
        line-height: 1.2;
    }

    p { color: var(--color-text); line-height: 1.7; }
    li { color: var(--color-text); }
    a { color: var(--color-primary); }

    /* Markdown content */
    [data-testid="stMarkdown"] h1 { font-size: 1.5rem; margin-bottom: 0.5rem; }
    [data-testid="stMarkdown"] h2 { font-size: 1.2rem; margin-bottom: 0.5rem; }
    [data-testid="stMarkdown"] h3 { font-size: 1rem; margin-bottom: 0.4rem; }
    [data-testid="stMarkdown"] p { font-size: 14px; margin-bottom: 0.6rem; }
    [data-testid="stMarkdown"] li { font-size: 14px; margin-bottom: 4px; }
    [data-testid="stMarkdown"] strong { color: var(--color-text); font-weight: 600; }
    [data-testid="stMarkdown"] code {
        background: rgba(92,107,255,0.12) !important;
        border: 1px solid rgba(92,107,255,0.2) !important;
        border-radius: 4px !important;
        font-family: var(--font-mono) !important;
        font-size: 12px !important;
        padding: 1px 6px !important;
        color: var(--color-primary-light) !important;
    }
    [data-testid="stMarkdown"] table {
        border-collapse: collapse;
        width: 100%;
        font-size: 13px;
        margin-bottom: 1rem;
    }
    [data-testid="stMarkdown"] th {
        background: rgba(92,107,255,0.1);
        color: var(--color-primary-light);
        padding: 10px 14px;
        text-align: left;
        font-family: var(--font-display);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-bottom: 1px solid var(--color-border);
    }
    [data-testid="stMarkdown"] td {
        padding: 10px 14px;
        border-bottom: 1px solid var(--color-border-subtle);
        color: var(--color-text-secondary);
    }
    [data-testid="stMarkdown"] tr:hover td {
        background: rgba(255,255,255,0.02);
    }

    /* =============================================
       BUTTONS — Professional Touch-Friendly
    ============================================= */
    .stButton > button {
        font-family: var(--font-display) !important;
        font-weight: 600 !important;
        border-radius: var(--radius-md) !important;
        transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
        letter-spacing: -0.01em !important;
        min-height: 44px !important;  /* Touch-friendly */
        font-size: 14px !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--color-primary) 0%, #4858EE 100%) !important;
        border: none !important;
        color: white !important;
        padding: 12px 24px !important;
        box-shadow: 0 4px 20px rgba(92,107,255,0.3), 0 1px 0 rgba(255,255,255,0.15) inset !important;
        position: relative !important;
        overflow: hidden !important;
    }
    .stButton > button[kind="primary"]::before {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
        transition: left 0.5s ease;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 8px 32px rgba(92,107,255,0.5), 0 1px 0 rgba(255,255,255,0.2) inset !important;
        transform: translateY(-2px) !important;
    }
    .stButton > button[kind="primary"]:hover::before { left: 100%; }
    .stButton > button[kind="primary"]:active { transform: translateY(0) !important; }
    .stButton > button[kind="secondary"] {
        background: rgba(92,107,255,0.07) !important;
        border: 1px solid var(--color-border) !important;
        color: var(--color-text-secondary) !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: rgba(92,107,255,0.14) !important;
        border-color: var(--color-border-bright) !important;
        color: var(--color-text) !important;
        transform: translateY(-1px) !important;
    }

    /* Download button */
    .stDownloadButton > button {
        font-family: var(--font-display) !important;
        font-weight: 600 !important;
        border-radius: var(--radius-md) !important;
        min-height: 44px !important;
        font-size: 14px !important;
        transition: all 0.25s ease !important;
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid var(--color-border) !important;
        color: var(--color-text-secondary) !important;
    }
    .stDownloadButton > button:hover {
        border-color: var(--color-border-bright) !important;
        color: var(--color-text) !important;
        transform: translateY(-1px) !important;
    }

    /* =============================================
       INPUTS — Professional
    ============================================= */
    .stTextArea textarea, .stTextInput input {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: var(--radius-md) !important;
        color: var(--color-text) !important;
        font-family: var(--font-body) !important;
        font-size: 15px !important;
        line-height: 1.65 !important;
        transition: all 0.25s ease !important;
        caret-color: var(--color-accent) !important;
        min-height: 44px !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: var(--color-primary) !important;
        box-shadow: 0 0 0 3px rgba(92,107,255,0.14), var(--glow-primary) !important;
        outline: none !important;
    }
    .stTextArea textarea::placeholder, .stTextInput input::placeholder {
        color: var(--color-muted) !important;
        font-size: 14px !important;
    }

    /* Chat input */
    [data-testid="stChatInput"] {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: var(--radius-lg) !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: var(--color-primary) !important;
        box-shadow: 0 0 0 3px rgba(92,107,255,0.12) !important;
    }

    label[data-testid="stWidgetLabel"] p {
        color: var(--color-muted) !important;
        font-family: var(--font-display) !important;
        font-size: 11px !important;
        text-transform: uppercase !important;
        letter-spacing: 1.2px !important;
        font-weight: 700 !important;
        margin-bottom: 6px !important;
    }

    /* =============================================
       SELECT / MULTISELECT
    ============================================= */
    [data-baseweb="select"] > div {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: var(--radius-md) !important;
        color: var(--color-text) !important;
        min-height: 44px !important;
    }
    [data-baseweb="select"] > div:focus-within {
        border-color: var(--color-primary) !important;
        box-shadow: 0 0 0 3px rgba(92,107,255,0.12) !important;
    }
    [data-baseweb="popover"] > div {
        background: #141428 !important;
        border: 1px solid var(--color-border) !important;
        border-radius: var(--radius-md) !important;
        box-shadow: var(--shadow-elevated) !important;
    }
    [data-baseweb="menu"] li {
        font-family: var(--font-body) !important;
        font-size: 14px !important;
        border-radius: var(--radius-sm) !important;
        margin: 2px 4px !important;
        min-height: 40px !important;
    }

    /* Radio */
    .stRadio [data-testid="stWidgetLabel"] + div {
        gap: 8px !important;
    }
    .stRadio label {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: var(--radius-md) !important;
        padding: 10px 16px !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        min-height: 44px !important;
    }
    .stRadio label:hover {
        border-color: var(--color-border-bright) !important;
        background: rgba(92,107,255,0.08) !important;
    }

    /* Toggle */
    .stToggle > label { min-height: 44px !important; }

    /* =============================================
       PROGRESS BAR
    ============================================= */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--color-primary), var(--color-accent)) !important;
        border-radius: 4px !important;
        box-shadow: 0 0 12px rgba(92,107,255,0.4) !important;
        transition: width 0.4s cubic-bezier(0.4,0,0.2,1) !important;
    }
    .stProgress > div {
        background: rgba(255,255,255,0.06) !important;
        border-radius: 4px !important;
        height: 5px !important;
    }

    /* =============================================
       TABS — Professional
    ============================================= */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.025) !important;
        border-radius: var(--radius-md) !important;
        padding: 4px !important;
        border: 1px solid var(--color-border) !important;
        gap: 2px !important;
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: var(--radius-sm) !important;
        color: var(--color-muted) !important;
        font-family: var(--font-display) !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        border: none !important;
        white-space: nowrap !important;
        min-height: 36px !important;
        padding: 0 12px !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--color-text) !important;
        background: rgba(92,107,255,0.1) !important;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(92,107,255,0.18) !important;
        color: var(--color-primary-light) !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 0 rgba(92,107,255,0.3) !important;
    }

    /* =============================================
       METRICS — Professional Cards
    ============================================= */
    [data-testid="stMetric"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: var(--radius-lg) !important;
        padding: 20px !important;
        transition: all 0.25s ease !important;
        box-shadow: var(--shadow-card) !important;
    }
    [data-testid="stMetric"]:hover {
        border-color: var(--color-border-bright) !important;
        box-shadow: var(--glow-primary), var(--shadow-card) !important;
        transform: translateY(-2px);
    }
    [data-testid="stMetricValue"] {
        color: var(--color-primary) !important;
        font-family: var(--font-display) !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em !important;
    }
    [data-testid="stMetricLabel"] {
        color: var(--color-muted) !important;
        font-size: 11px !important;
        text-transform: uppercase !important;
        letter-spacing: 1.2px !important;
        font-family: var(--font-display) !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricDelta"] { font-size: 12px !important; }

    /* =============================================
       DIVIDER
    ============================================= */
    hr {
        border: none !important;
        border-top: 1px solid rgba(255,255,255,0.06) !important;
        margin: 24px 0 !important;
    }

    /* =============================================
       ALERTS
    ============================================= */
    [data-testid="stAlert"] {
        border-radius: var(--radius-md) !important;
        border: 1px solid rgba(0,245,212,0.2) !important;
        background: rgba(0,245,212,0.05) !important;
        font-size: 14px !important;
    }
    [data-testid="stAlert"][data-baseweb="notification"] {
        background: rgba(92,107,255,0.06) !important;
        border-color: rgba(92,107,255,0.2) !important;
    }

    /* Expander */
    [data-testid="stExpander"] {
        border: 1px solid var(--color-border) !important;
        border-radius: var(--radius-lg) !important;
        background: var(--bg-card) !important;
        overflow: hidden !important;
    }
    [data-testid="stExpander"] summary {
        font-family: var(--font-display) !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 16px 20px !important;
        min-height: 48px !important;
    }

    /* =============================================
       SCROLLBAR
    ============================================= */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(92,107,255,0.3);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: var(--color-primary); }

    /* =============================================
       ANIMATIONS
    ============================================= */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to   { opacity: 1; }
    }
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(20px); }
        to   { opacity: 1; transform: translateX(0); }
    }
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 8px rgba(92,107,255,0.2); }
        50% { box-shadow: 0 0 24px rgba(92,107,255,0.5), 0 0 48px rgba(92,107,255,0.15); }
    }
    @keyframes shimmer {
        0%   { background-position: -800px 0; }
        100% { background-position: 800px 0; }
    }
    @keyframes spin {
        from { transform: rotate(0deg); }
        to   { transform: rotate(360deg); }
    }
    @keyframes gradientShift {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes recordingPulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.08); opacity: 0.8; }
    }

    .animate-fade-in-up { animation: fadeInUp 0.6s cubic-bezier(0.4,0,0.2,1) forwards; }
    .animate-fade-in { animation: fadeIn 0.4s ease forwards; }
    .animate-slide-right { animation: slideInRight 0.5s cubic-bezier(0.4,0,0.2,1) forwards; }

    /* =============================================
       HERO SECTION
    ============================================= */
    .hero-section {
        text-align: center;
        padding: 64px 0 48px;
        animation: fadeInUp 0.7s ease forwards;
    }
    .hero-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(92,107,255,0.1);
        border: 1px solid rgba(92,107,255,0.22);
        border-radius: 100px;
        padding: 6px 16px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: var(--color-primary-light);
        margin-bottom: 24px;
        font-family: var(--font-display);
    }
    .hero-title {
        font-family: var(--font-display);
        font-size: clamp(2rem, 5vw, 4.5rem);
        font-weight: 700;
        letter-spacing: -0.04em;
        line-height: 1.06;
        color: var(--color-text);
        margin-bottom: 20px;
    }
    .hero-gradient {
        background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        background-size: 200% 200%;
        animation: gradientShift 4s ease infinite;
    }
    .hero-subtitle {
        font-size: clamp(1rem, 2vw, 1.15rem);
        color: var(--color-text-secondary);
        line-height: 1.7;
        max-width: 560px;
        margin: 0 auto 44px;
    }

    /* Stats bar */
    .stats-bar {
        display: flex;
        justify-content: center;
        gap: 32px;
        flex-wrap: wrap;
        padding: 20px 0;
        border-top: 1px solid var(--color-border-subtle);
        border-bottom: 1px solid var(--color-border-subtle);
        margin: 36px 0;
    }
    .stat-item { text-align: center; }
    .stat-value {
        font-family: var(--font-display);
        font-size: 1.7rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        display: block;
        letter-spacing: -0.03em;
    }
    .stat-label {
        font-size: 11px;
        color: var(--color-muted);
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-family: var(--font-display);
        font-weight: 600;
    }

    /* =============================================
       CARDS
    ============================================= */
    .dream-card {
        background: var(--bg-card);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-lg);
        padding: 22px;
        backdrop-filter: blur(8px);
        margin-bottom: 14px;
        transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-card);
    }
    .dream-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(92,107,255,0.4), transparent);
        opacity: 0;
        transition: opacity 0.3s;
    }
    .dream-card:hover {
        border-color: var(--color-border-bright);
        box-shadow: 0 8px 32px rgba(92,107,255,0.1), var(--shadow-card);
        transform: translateY(-2px);
    }
    .dream-card:hover::before { opacity: 1; }

    /* Premium card variant */
    .dream-card-premium {
        background: linear-gradient(135deg, rgba(92,107,255,0.06), rgba(0,245,212,0.03));
        border-color: rgba(92,107,255,0.22);
    }

    /* Section tag */
    .section-tag {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-family: var(--font-display);
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2.5px;
        color: var(--color-primary);
        margin-bottom: 10px;
    }
    .section-tag::before {
        content: '';
        width: 18px;
        height: 2px;
        background: linear-gradient(90deg, var(--color-primary), var(--color-accent));
        border-radius: 1px;
        flex-shrink: 0;
    }

    /* Blueprint sections */
    .blueprint-section {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(92,107,255,0.1);
        border-left: 3px solid var(--color-primary);
        border-radius: 0 var(--radius-md) var(--radius-md) 0;
        padding: 22px 24px;
        margin-bottom: 16px;
        animation: fadeInUp 0.5s ease forwards;
    }
    .blueprint-section-title {
        font-family: var(--font-display);
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: var(--color-primary);
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 3px 10px;
        border-radius: 100px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-family: var(--font-display);
    }
    .badge-primary {
        background: rgba(92,107,255,0.12);
        border: 1px solid rgba(92,107,255,0.28);
        color: var(--color-primary-light);
    }
    .badge-accent {
        background: rgba(0,245,212,0.1);
        border: 1px solid rgba(0,245,212,0.25);
        color: var(--color-accent);
    }
    .badge-orange {
        background: rgba(255,140,0,0.1);
        border: 1px solid rgba(255,140,0,0.28);
        color: #FF8C00;
    }
    .badge-pink {
        background: rgba(255,80,160,0.1);
        border: 1px solid rgba(255,80,160,0.28);
        color: #FF50A0;
    }

    /* Idea type pill */
    .idea-type-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 16px;
        background: rgba(0,245,212,0.07);
        border: 1px solid rgba(0,245,212,0.22);
        border-radius: 100px;
        color: var(--color-accent);
        font-family: var(--font-display);
        font-size: 12px;
        font-weight: 700;
        animation: fadeIn 0.4s ease;
        letter-spacing: 0.3px;
    }

    /* Question card */
    .question-card {
        background: rgba(92,107,255,0.045);
        border: 1px solid rgba(92,107,255,0.18);
        border-radius: var(--radius-xl);
        padding: 36px;
        animation: fadeInUp 0.5s ease forwards;
        text-align: center;
        max-width: 680px;
        margin: 0 auto;
        box-shadow: var(--shadow-card);
    }
    .question-number {
        font-family: var(--font-mono);
        font-size: 11px;
        color: var(--color-accent);
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 18px;
    }
    .question-text {
        font-family: var(--font-display);
        font-size: clamp(1.2rem, 3vw, 1.5rem);
        font-weight: 600;
        color: var(--color-text);
        line-height: 1.4;
        margin-bottom: 28px;
    }

    /* Option chips */
    .option-chip {
        display: inline-block;
        padding: 10px 20px;
        background: rgba(255,255,255,0.04);
        border: 1px solid var(--color-border);
        border-radius: 100px;
        font-size: 14px;
        color: var(--color-text-secondary);
        cursor: pointer;
        transition: all 0.2s ease;
        margin: 5px;
        font-family: var(--font-body);
        min-height: 44px;
    }
    .option-chip:hover, .option-chip.selected {
        background: rgba(92,107,255,0.14);
        border-color: var(--color-primary);
        color: var(--color-primary-light);
    }

    /* Dashboard cards */
    .blueprint-card {
        background: var(--bg-card);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-lg);
        padding: 18px;
        cursor: pointer;
        transition: all 0.25s ease;
        height: 100%;
        box-shadow: var(--shadow-card);
    }
    .blueprint-card:hover {
        border-color: var(--color-border-bright);
        box-shadow: 0 8px 32px rgba(92,107,255,0.12), var(--shadow-card);
        transform: translateY(-3px);
    }
    .blueprint-card-type {
        font-family: var(--font-mono);
        font-size: 10px;
        color: var(--color-accent);
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 8px;
    }
    .blueprint-card-title {
        font-family: var(--font-display);
        font-size: 1rem;
        font-weight: 600;
        color: var(--color-text);
        line-height: 1.4;
        margin-bottom: 10px;
    }
    .blueprint-card-meta {
        font-size: 12px;
        color: var(--color-muted);
    }

    /* Status badges */
    .status-draft { color: #5A5A78; background: rgba(90,90,120,0.1); border: 1px solid rgba(90,90,120,0.2); }
    .status-progress { color: #FFB800; background: rgba(255,184,0,0.1); border: 1px solid rgba(255,184,0,0.22); }
    .status-built { color: #00F5D4; background: rgba(0,245,212,0.1); border: 1px solid rgba(0,245,212,0.22); }

    /* Generation checklist */
    .gen-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 11px 0;
        border-bottom: 1px solid rgba(92,107,255,0.06);
        font-family: var(--font-body);
        font-size: 13px;
        color: var(--color-muted);
        transition: all 0.3s ease;
    }
    .gen-item.active { color: var(--color-text); }
    .gen-item.done { color: var(--color-accent); }
    .gen-dot {
        width: 7px; height: 7px;
        border-radius: 50%;
        background: rgba(90,90,120,0.4);
        flex-shrink: 0;
        transition: all 0.3s ease;
    }
    .gen-dot.active {
        background: var(--color-primary);
        box-shadow: 0 0 8px rgba(92,107,255,0.6);
        animation: pulseGlow 1.5s ease infinite;
    }
    .gen-dot.done {
        background: var(--color-accent);
        box-shadow: 0 0 6px rgba(0,245,212,0.4);
    }

    /* AI Chat */
    .chat-bubble-user {
        background: rgba(92,107,255,0.1);
        border: 1px solid rgba(92,107,255,0.18);
        border-radius: 16px 16px 4px 16px;
        padding: 11px 15px;
        font-size: 14px;
        color: var(--color-text);
        margin-bottom: 10px;
        margin-left: 15%;
        animation: fadeInUp 0.3s ease;
        line-height: 1.6;
    }
    .chat-bubble-ai {
        background: rgba(255,255,255,0.035);
        border: 1px solid var(--color-border);
        border-radius: 16px 16px 16px 4px;
        padding: 11px 15px;
        font-size: 14px;
        color: var(--color-text);
        margin-bottom: 10px;
        margin-right: 15%;
        animation: fadeInUp 0.3s ease;
        line-height: 1.6;
    }

    /* Tech badge */
    .tech-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 5px 12px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: var(--radius-sm);
        font-family: var(--font-mono);
        font-size: 12px;
        color: var(--color-text-secondary);
        margin: 3px;
        transition: all 0.2s ease;
    }
    .tech-badge:hover {
        border-color: var(--color-primary);
        color: var(--color-primary-light);
    }

    /* Persona card */
    .persona-card {
        background: rgba(92,107,255,0.04);
        border: 1px solid rgba(92,107,255,0.14);
        border-radius: var(--radius-lg);
        padding: 18px;
        transition: all 0.25s ease;
    }
    .persona-card:hover {
        border-color: rgba(92,107,255,0.32);
        box-shadow: var(--glow-primary);
    }
    .persona-avatar {
        width: 44px; height: 44px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        margin-bottom: 10px;
    }

    /* KPI card */
    .kpi-card {
        background: rgba(0,245,212,0.04);
        border: 1px solid rgba(0,245,212,0.14);
        border-radius: var(--radius-md);
        padding: 14px;
        text-align: center;
    }
    .kpi-value {
        font-family: var(--font-display);
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--color-accent);
        letter-spacing: -0.02em;
    }
    .kpi-label {
        font-size: 11px;
        color: var(--color-muted);
        margin-top: 3px;
        font-family: var(--font-display);
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Risk card */
    .risk-card {
        background: rgba(255,100,80,0.03);
        border: 1px solid rgba(255,100,80,0.16);
        border-left: 3px solid #FF6450;
        border-radius: 0 var(--radius-md) var(--radius-md) 0;
        padding: 14px 18px;
        margin-bottom: 10px;
    }

    /* Competitor card */
    .competitor-card {
        background: rgba(255,255,255,0.02);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-md);
        padding: 14px;
        margin-bottom: 10px;
    }

    /* Timeline */
    .timeline-item {
        display: flex;
        gap: 16px;
        padding-bottom: 18px;
        position: relative;
    }
    .timeline-dot {
        width: 10px; height: 10px;
        border-radius: 50%;
        background: var(--color-primary);
        box-shadow: 0 0 8px rgba(92,107,255,0.5);
        flex-shrink: 0;
        margin-top: 4px;
    }
    .timeline-line {
        position: absolute;
        left: 4px; top: 14px;
        width: 2px;
        bottom: 0;
        background: linear-gradient(180deg, var(--color-primary), transparent);
    }

    /* Gallery card */
    .gallery-card {
        background: var(--bg-card);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-lg);
        padding: 18px;
        cursor: pointer;
        transition: all 0.25s ease;
        box-shadow: var(--shadow-card);
    }
    .gallery-card:hover {
        border-color: var(--color-border-bright);
        box-shadow: 0 8px 32px rgba(92,107,255,0.12), var(--shadow-card);
        transform: translateY(-3px);
    }

    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 72px 20px;
        color: var(--color-muted);
    }
    .empty-state-icon { font-size: 44px; margin-bottom: 14px; opacity: 0.7; }
    .empty-state-title {
        font-family: var(--font-display);
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--color-text-secondary);
        margin-bottom: 8px;
    }
    .empty-state-text { font-size: 14px; line-height: 1.6; color: var(--color-muted); }

    /* Notebook */
    .note-card {
        background: rgba(255,184,0,0.04);
        border: 1px solid rgba(255,184,0,0.13);
        border-radius: var(--radius-md);
        padding: 14px;
        margin-bottom: 10px;
    }

    /* Floating CTA */
    .floating-cta {
        position: fixed;
        bottom: 80px;   /* Above bottom nav on mobile */
        right: 24px;
        z-index: 1000;
    }

    /* Voice button */
    .voice-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        width: 64px; height: 64px;
        background: linear-gradient(135deg, #FF4060, #FF2040);
        border-radius: 50%;
        color: white;
        font-size: 24px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(255,64,96,0.4);
        border: none;
        animation: recordingPulse 2s ease infinite;
    }
    .voice-btn:hover {
        transform: scale(1.08);
        box-shadow: 0 8px 32px rgba(255,64,96,0.6);
    }

    /* Recording indicator */
    .recording-dot {
        display: inline-block;
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #FF4060;
        animation: recordingPulse 1s ease infinite;
    }

    /* Mini blueprint cards */
    .mini-bp-card {
        background: rgba(92,107,255,0.05);
        border: 1px solid rgba(92,107,255,0.18);
        border-radius: var(--radius-xl);
        padding: 28px;
        animation: fadeInUp 0.6s ease forwards;
    }

    /* Mindmap container */
    .mindmap-container {
        background: rgba(255,255,255,0.02);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-lg);
        padding: 24px;
        overflow: hidden;
    }

    /* =============================================
       MOBILE-FIRST RESPONSIVE
    ============================================= */

    /* Bottom navigation bar (mobile) */
    .mobile-bottom-nav {
        display: none;
        position: fixed;
        bottom: 0; left: 0; right: 0;
        height: var(--bottom-nav-height);
        background: rgba(7,7,15,0.97);
        border-top: 1px solid var(--color-border);
        backdrop-filter: blur(20px);
        z-index: 999;
        padding: 0 4px;
        align-items: center;
        justify-content: space-around;
    }
    .mobile-nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 3px;
        padding: 8px 12px;
        border-radius: var(--radius-md);
        text-decoration: none;
        color: var(--color-muted);
        font-size: 10px;
        font-family: var(--font-display);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: all 0.2s ease;
        cursor: pointer;
        min-width: 56px;
        text-align: center;
    }
    .mobile-nav-item:hover, .mobile-nav-item.active {
        color: var(--color-primary);
        background: rgba(92,107,255,0.1);
    }
    .mobile-nav-item .nav-icon { font-size: 20px; }

    /* Page header (mobile) */
    .page-header {
        padding: 0 0 20px 0;
        border-bottom: 1px solid var(--color-border-subtle);
        margin-bottom: 24px;
    }
    .page-header h1 {
        font-size: clamp(1.4rem, 4vw, 2rem);
        margin: 0;
    }

    @media (max-width: 768px) {
        /* Show bottom nav */
        .mobile-bottom-nav { display: flex; }

        /* Adjust body padding for bottom nav */
        [data-testid="block-container"] {
            padding-bottom: 80px !important;
            padding-left: 12px !important;
            padding-right: 12px !important;
        }

        /* Single column cards */
        .blueprint-card, .gallery-card { margin-bottom: 12px; }

        /* Larger touch targets */
        .stButton > button { min-height: 48px !important; font-size: 15px !important; }

        /* Hero adjustments */
        .hero-section { padding: 32px 0 24px; }
        .hero-subtitle { font-size: 1rem; }

        /* Tab scrolling */
        .stTabs [data-baseweb="tab-list"] {
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
        }

        /* Full-width selects */
        [data-baseweb="select"] { width: 100% !important; }

        /* Question card */
        .question-card { padding: 24px 18px; }
        .question-text { font-size: 1.15rem; }

        /* Chat bubbles */
        .chat-bubble-user { margin-left: 10%; }
        .chat-bubble-ai { margin-right: 10%; }

        /* Stats bar */
        .stats-bar { gap: 20px; }
        .stat-value { font-size: 1.4rem; }

        /* Floating CTA above bottom nav */
        .floating-cta { bottom: 80px; }

        /* Hide sidebar toggle area */
        [data-testid="stSidebarNav"] { display: none; }
    }

    @media (max-width: 480px) {
        [data-testid="block-container"] {
            padding-left: 10px !important;
            padding-right: 10px !important;
        }
        .dream-card { padding: 16px; }
        .blueprint-section { padding: 16px; }
        .question-card { padding: 20px 14px; }
        .hero-title { font-size: 1.8rem; }
    }

    /* =============================================
       SPINNER / LOADING
    ============================================= */
    [data-testid="stSpinner"] {
        text-align: center;
    }
    [data-testid="stSpinner"] > div {
        color: var(--color-primary) !important;
        font-family: var(--font-display) !important;
        font-size: 14px !important;
    }

    /* =============================================
       TOAST / NOTIFICATIONS
    ============================================= */
    [data-testid="stToast"] {
        background: rgba(20,20,36,0.97) !important;
        border: 1px solid var(--color-border-bright) !important;
        border-radius: var(--radius-md) !important;
        backdrop-filter: blur(16px) !important;
        font-family: var(--font-display) !important;
        font-size: 14px !important;
        box-shadow: var(--shadow-elevated) !important;
    }

    </style>
    """, unsafe_allow_html=True)


def render_mobile_bottom_nav(active_page: str = ""):
    """Render a bottom navigation bar for mobile users."""
    nav_items = [
        ("🏠", "Home", "app"),
        ("✦", "Capture", "0_Capture"),
        ("📊", "Dashboard", "5_Dashboard"),
        ("🎭", "Gallery", "6_Gallery"),
        ("📓", "Notebook", "7_Notebook"),
    ]
    items_html = ""
    for icon, label, page in nav_items:
        is_active = active_page == page
        items_html += f"""
        <a class="mobile-nav-item {'active' if is_active else ''}"
           href="/{page.replace('_', '_')}" target="_self">
            <span class="nav-icon">{icon}</span>
            <span>{label}</span>
        </a>"""

    st.markdown(f"""
    <div class="mobile-bottom-nav">
        {items_html}
    </div>
    """, unsafe_allow_html=True)
