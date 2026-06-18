"""
Dream Machine — Interface Mockup Viewer
Renders AI-generated HTML wireframe with mobile/desktop toggle.
"""
import streamlit as st
import streamlit.components.v1 as components
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.styles import inject_styles
from components.db import init_db, get_blueprint, list_blueprints, update_blueprint_mockup
from components.gemini_client import generate_mockup, IDEA_TYPE_ICONS

st.set_page_config(
    page_title="Interface Mockup — Dream Machine",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_styles()
init_db()

# ── Load Blueprint ─────────────────────────────────────────────────────────────
bid = st.session_state.get("current_blueprint_id")
if not bid:
    bps = list_blueprints(limit=1)
    if bps:
        bid = bps[0]["id"]
        st.session_state.current_blueprint_id = bid

if not bid:
    st.markdown("""<div class="empty-state"><div class="empty-state-icon">🎨</div>
    <div class="empty-state-title">No mockup found</div>
    <div class="empty-state-text">Generate a blueprint first to see the mockup.</div>
    </div>""", unsafe_allow_html=True)
    if st.button("← Create Blueprint", type="primary"):
        st.switch_page("app.py")
    st.stop()

bp = get_blueprint(bid)
if not bp:
    st.error("Blueprint not found.")
    st.stop()

idea = bp.get("idea", "")
idea_type = bp.get("idea_type", "Other")
icon = IDEA_TYPE_ICONS.get(idea_type, "💡")
mockup_html = bp.get("mockup_html", "")
answers = bp.get("answers", {})

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-bottom:24px;">
    <div class="section-tag">Interface Mockup</div>
    <h1 style="font-family:'Space Grotesk',sans-serif;font-size:1.8rem;font-weight:700;
               letter-spacing:-0.03em;color:#E8E8F0;margin:8px 0;">
        {icon} {bp.get('title', idea[:50])}
    </h1>
    <div style="font-size:14px;color:#6B6B8A;">
        AI-generated interface preview · {idea_type}
    </div>
</div>
""", unsafe_allow_html=True)

# ── Controls ──────────────────────────────────────────────────────────────────
ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns([2, 1, 1, 1])

with ctrl_col1:
    view_mode = st.radio(
        "VIEW MODE",
        ["🖥️ Desktop", "📱 Mobile"],
        horizontal=True,
        label_visibility="collapsed",
        key="view_mode_radio"
    )
with ctrl_col2:
    style_choice = st.selectbox(
        "STYLE",
        ["modern", "minimal", "colorful"],
        label_visibility="visible",
        key="style_sel"
    )
with ctrl_col3:
    regen_btn = st.button("🔄 Regenerate", use_container_width=True, key="regen_btn")
with ctrl_col4:
    if st.button("← Blueprint", use_container_width=True):
        st.switch_page("pages/3_Blueprint.py")

# ── Regenerate ────────────────────────────────────────────────────────────────
if regen_btn:
    with st.spinner(f"🎨 Regenerating {style_choice} mockup..."):
        mockup_html = generate_mockup(idea, idea_type, answers, style=style_choice)
        update_blueprint_mockup(bid, mockup_html)
        bp["mockup_html"] = mockup_html
    st.success("Mockup regenerated!")
    st.rerun()

if not mockup_html:
    with st.spinner("🎨 Generating your interface mockup..."):
        mockup_html = generate_mockup(idea, idea_type, answers, style="modern")
        update_blueprint_mockup(bid, mockup_html)
        bp["mockup_html"] = mockup_html
    st.rerun()

# ── Mockup Render ─────────────────────────────────────────────────────────────
is_mobile = "Mobile" in view_mode
frame_width = 390 if is_mobile else 1200
frame_height = 700 if is_mobile else 650

st.markdown(f"""
<div style="
    {'max-width:420px;margin:0 auto;' if is_mobile else ''}
    border: 1px solid rgba(92,107,255,0.3);
    border-radius: {'28px' if is_mobile else '12px'};
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 40px rgba(92,107,255,0.1);
    {'padding:8px;background:#1A1A2E;' if is_mobile else ''}
">
""", unsafe_allow_html=True)

if is_mobile:
    # Mobile frame decoration
    st.markdown("""
    <div style="height:24px;background:#1A1A2E;display:flex;align-items:center;justify-content:center;gap:8px;">
        <div style="width:50px;height:4px;background:rgba(255,255,255,0.2);border-radius:2px;"></div>
    </div>
    """, unsafe_allow_html=True)

components.html(mockup_html, height=frame_height, scrolling=True)
st.markdown("</div>", unsafe_allow_html=True)

# ── Annotations ───────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("🔍 Design Annotations & Decisions", expanded=False):
    annotation_cols = st.columns(3)
    annotations = [
        ("🎨 Color System", f"Primary: Electric Indigo (#5C6BFF) for trust and innovation. Accent: Neon Cyan for calls-to-action. Dark background reduces eye strain for {idea_type} users who spend hours in the tool."),
        ("📐 Layout Logic", "Top navigation with core actions visible at a glance. Hero area focuses the user on the single most important action. Grid layout below for scannable feature discovery."),
        ("⚡ UX Principles", "Every click serves a purpose. Primary CTA is impossible to miss. Social proof and trust signals placed strategically. Progressive disclosure hides complexity until needed."),
    ]
    for i, (title, text) in enumerate(annotations):
        with annotation_cols[i]:
            st.markdown(f"""
            <div class="dream-card">
                <div style="font-weight:600;font-size:14px;margin-bottom:8px;color:#E8E8F0;">{title}</div>
                <div style="font-size:13px;color:#6B6B8A;line-height:1.6;">{text}</div>
            </div>
            """, unsafe_allow_html=True)

# ── Download ──────────────────────────────────────────────────────────────────
st.divider()
dl_col1, dl_col2 = st.columns(2)
with dl_col1:
    st.download_button(
        "📥 Download HTML",
        data=mockup_html,
        file_name=f"mockup_{bid[:8]}.html",
        mime="text/html",
        use_container_width=True
    )
with dl_col2:
    if st.button("📊 View Full Blueprint →", type="primary", use_container_width=True):
        st.switch_page("pages/3_Blueprint.py")
