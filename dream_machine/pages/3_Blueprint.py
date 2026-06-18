"""
Dream Machine — Blueprint Viewer
Full 10-section blueprint with AI Chat sidebar and export.
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.styles import inject_styles
from components.db import (
    init_db, get_blueprint, list_blueprints, toggle_blueprint_public,
    update_blueprint_status, save_chat_message, get_chat_history, clear_chat_history
)
from components.gemini_client import IDEA_TYPE_ICONS, get_smart_suggestions, stream_chat
from components.export import export_pdf_bytes, export_markdown

st.set_page_config(
    page_title="Blueprint — Dream Machine",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_styles()
init_db()

# ── Load Blueprint ─────────────────────────────────────────────────────────────
bid = st.session_state.get("current_blueprint_id")
if not bid:
    # Try to load most recent
    bps = list_blueprints(limit=1)
    if bps:
        bid = bps[0]["id"]
        st.session_state.current_blueprint_id = bid

if not bid:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">📋</div>
        <div class="empty-state-title">Your blueprint canvas is empty.</div>
        <div class="empty-state-text">What are you going to build?</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("✦ Create Your First Blueprint", type="primary"):
        st.switch_page("app.py")
    st.stop()

bp = get_blueprint(bid)
if not bp:
    st.error("Blueprint not found.")
    st.stop()

sections = bp.get("sections", {})
idea = bp.get("idea", "")
idea_type = bp.get("idea_type", "Other")
icon = IDEA_TYPE_ICONS.get(idea_type, "💡")

# ── Sidebar — AI Chat ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:16px 0 8px;">
        <div class="section-tag">AI Blueprint Advisor</div>
        <div style="font-size:13px;color:#6B6B8A;margin-top:8px;line-height:1.5;">
            Ask me anything about your blueprint. I know this idea deeply.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Chat history
    chat_history = get_chat_history(bid, limit=20)
    chat_container = st.container(height=350)

    with chat_container:
        if not chat_history:
            st.markdown("""
            <div style="text-align:center;padding:40px 10px;color:#6B6B8A;font-size:13px;">
                💬 Ask me anything:<br><br>
                "What should my onboarding look like?"<br>
                "How would this scale to 1M users?"<br>
                "What's the biggest risk I'm missing?"
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in chat_history:
                if msg["role"] == "user":
                    st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-bubble-ai">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

    # Chat input
    user_msg = st.chat_input("Ask about your blueprint...", key="chat_input")
    if user_msg:
        save_chat_message(bid, "user", user_msg)
        with st.spinner("🤖 Thinking..."):
            full_response = "".join(stream_chat(
                idea, idea_type, sections,
                get_chat_history(bid, limit=8),
                user_msg
            ))
        save_chat_message(bid, "assistant", full_response)
        st.rerun()

    if chat_history:
        if st.button("🗑️ Clear chat", use_container_width=True):
            clear_chat_history(bid)
            st.rerun()

    st.divider()

    # Smart suggestions
    st.markdown('<div class="section-tag">💡 Smart Suggestions</div>', unsafe_allow_html=True)
    if "smart_suggestions" not in st.session_state:
        with st.spinner("Generating suggestions..."):
            st.session_state.smart_suggestions = get_smart_suggestions(idea, idea_type)

    for sug in st.session_state.get("smart_suggestions", []):
        st.markdown(f"""
        <div class="note-card" style="font-size:13px;line-height:1.5;margin-bottom:8px;">
            {sug}
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Status
    current_status = bp.get("status", "draft")
    new_status = st.selectbox(
        "PROJECT STATUS",
        ["draft", "in_progress", "built", "archived"],
        index=["draft", "in_progress", "built", "archived"].index(current_status),
        key="status_sel"
    )
    if new_status != current_status:
        update_blueprint_status(bid, new_status)
        st.toast(f"Status updated to {new_status} ✓")

    # Public toggle
    is_public = bool(bp.get("is_public", 0))
    new_public = st.toggle("Share to Gallery", value=is_public)
    if new_public != is_public:
        toggle_blueprint_public(bid, new_public)
        st.toast("Gallery visibility updated ✓")

# ── Main Blueprint View ───────────────────────────────────────────────────────

# Header
st.markdown(f"""
<div style="margin-bottom:24px;">
    <div class="idea-type-pill" style="margin-bottom:12px;">{icon} {idea_type}</div>
    <h1 style="font-family:'Space Grotesk',sans-serif;font-size:2rem;font-weight:700;
               letter-spacing:-0.03em;color:#E8E8F0;margin-bottom:8px;">
        {bp.get('title', idea[:60])}
    </h1>
    <div style="font-size:14px;color:#6B6B8A;max-width:600px;line-height:1.6;">
        {idea[:200]}{"..." if len(idea) > 200 else ""}
    </div>
</div>
""", unsafe_allow_html=True)

# Action buttons
btn_col1, btn_col2, btn_col3, btn_col4, btn_col5, btn_col6 = st.columns([1, 1, 1, 1, 1, 1])
with btn_col1:
    pdf_bytes = export_pdf_bytes(bp)
    st.download_button(
        "📄 PDF",
        data=pdf_bytes,
        file_name=f"blueprint_{bid[:8]}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
with btn_col2:
    md_text = export_markdown(bp)
    st.download_button(
        "📝 Markdown",
        data=md_text,
        file_name=f"blueprint_{bid[:8]}.md",
        mime="text/markdown",
        use_container_width=True
    )
with btn_col3:
    if st.button("🎨 Mockup", use_container_width=True):
        st.switch_page("pages/4_Mockup.py")
with btn_col4:
    if st.button("📃 Pitch Deck", use_container_width=True):
        st.switch_page("pages/8_Pitch.py")
with btn_col5:
    if st.button("⚡ Compare", use_container_width=True):
        st.switch_page("pages/9_Compare.py")
with btn_col6:
    if st.button("📓 Notebook", use_container_width=True):
        st.switch_page("pages/7_Notebook.py")

st.divider()

# ── Blueprint Sections ────────────────────────────────────────────────────────
SECTION_META = [
    ("executive_summary", "📋 Executive Summary",
     "The vision, the problem, the why-now."),
    ("user_personas", "👥 User Personas",
     "Who will use this and why they care."),
    ("core_features", "⚡ Core Feature List",
     "MVP vs. Phase 2 — what ships first."),
    ("architecture", "🏗️ Architecture Map",
     "How the system is built under the hood."),
    ("tech_stack", "🔧 Tech Stack",
     "The best tools for this specific product."),
    ("roadmap", "🗓️ Roadmap",
     "Week-by-week plan from idea to scale."),
    ("business_model", "💰 Business Model",
     "How this makes money and reaches $1M ARR."),
    ("risk_analysis", "⚠️ Risk Analysis",
     "The top threats and how to neutralize them."),
    ("competitor_landscape", "🏁 Competitor Landscape",
     "Who's in the market and your unique position."),
    ("success_metrics", "📊 Success Metrics",
     "The KPIs that will tell you you're winning."),
]

# Tabs for sections
tab_labels = [meta[1] for meta in SECTION_META]
tabs = st.tabs(tab_labels)

for i, (key, title, subtitle) in enumerate(SECTION_META):
    with tabs[i]:
        content = sections.get(key, "")

        if not content:
            st.markdown(f"""
            <div class="empty-state" style="padding:40px 0;">
                <div class="empty-state-icon">⏳</div>
                <div class="empty-state-title">Not yet generated</div>
                <div class="empty-state-text">This section will appear after generation.</div>
            </div>
            """, unsafe_allow_html=True)
            continue

        st.markdown(f"""
        <div class="blueprint-section">
            <div class="blueprint-section-title">{title}</div>
            <div style="font-size:13px;color:#6B6B8A;margin-bottom:16px;">{subtitle}</div>
        """, unsafe_allow_html=True)

        # Special rendering for certain sections
        if key == "user_personas":
            # Render as cards
            personas = content.split("**")
            st.markdown(content)

        elif key == "tech_stack":
            st.markdown(content)
            # Extract tech names and render as badges
            import re
            techs = re.findall(r'\*\*([^*]+)\*\*.*?:\s*([^\n]+)', content)
            if techs:
                st.markdown("<div style='margin-top:16px;'>", unsafe_allow_html=True)
                for tech_type, tech_name in techs[:8]:
                    clean_name = tech_name.split("—")[0].strip()[:30]
                    st.markdown(
                        f'<span class="tech-badge">🔧 {tech_type}: {clean_name}</span>',
                        unsafe_allow_html=True
                    )
                st.markdown("</div>", unsafe_allow_html=True)

        elif key == "success_metrics":
            st.markdown(content)
            # Extract any numbers for KPI display
            import re
            numbers = re.findall(r'(\d+[%kKMmx+]*)\s+([^\n.]+)', content)
            if numbers:
                st.markdown("<br>", unsafe_allow_html=True)
                kpi_cols = st.columns(min(len(numbers[:4]), 4))
                for j, (val, label) in enumerate(numbers[:4]):
                    with kpi_cols[j]:
                        st.markdown(f"""
                        <div class="kpi-card">
                            <div class="kpi-value">{val}</div>
                            <div class="kpi-label">{label[:30]}</div>
                        </div>
                        """, unsafe_allow_html=True)

        elif key == "roadmap":
            # Render roadmap as visual timeline
            import re
            phases = re.split(r'\*\*(Week|Month|Phase|Quarter|Stage)s?\s*[\d\-]+[^*]*\*\*', content)
            phase_headers = re.findall(r'\*\*(Week|Month|Phase|Quarter|Stage)s?\s*[\d\-]+[^*]*\*\*', content)

            if phase_headers and len(phases) > 1:
                # Visual timeline
                for pi, (header, body) in enumerate(zip(phase_headers, phases[1:])):
                    items = [l.strip().lstrip('- ').strip() for l in body.strip().split('\n')
                             if l.strip() and not l.strip().startswith('#')]
                    items_html = "".join(f"""
                    <div style="display:flex;align-items:flex-start;gap:8px;margin-bottom:6px;">
                        <div style="width:4px;height:4px;border-radius:50%;background:#5C6BFF;
                                    flex-shrink:0;margin-top:8px;"></div>
                        <div style="font-size:13px;color:#C0C0D8;line-height:1.6;">{item}</div>
                    </div>""" for item in items[:6] if item)
                    colors = ["#5C6BFF", "#00F5D4", "#FFB800", "#FF6450", "#A070FF", "#00D4FF"]
                    c = colors[pi % len(colors)]
                    st.markdown(f"""
                    <div style="display:flex;gap:0;margin-bottom:16px;">
                        <div style="display:flex;flex-direction:column;align-items:center;margin-right:16px;">
                            <div style="width:36px;height:36px;border-radius:50%;background:{c}22;
                                        border:2px solid {c};display:flex;align-items:center;
                                        justify-content:center;font-size:12px;font-weight:700;
                                        color:{c};flex-shrink:0;">{pi+1}</div>
                            {'<div style="width:2px;flex:1;background:rgba(92,107,255,0.15);margin:4px 0;min-height:20px;"></div>' if pi < len(phase_headers)-1 else ''}
                        </div>
                        <div style="flex:1;padding-bottom:8px;">
                            <div style="font-family:\'Space Grotesk\',sans-serif;font-size:13px;font-weight:700;
                                        color:{c};margin-bottom:8px;text-transform:uppercase;
                                        letter-spacing:0.5px;">{header}</div>
                            {items_html}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(content)

        elif key == "risk_analysis":
            # Parse and render risk cards with severity
            import re
            risks_raw = re.split(r'\*\*Risk\s*\d+[^*]*\*\*', content)
            risk_headers = re.findall(r'\*\*Risk\s*\d+[^*]*\*\*', content)
            if risk_headers:
                for rh, rb in zip(risk_headers, risks_raw[1:]):
                    # Detect severity
                    severity = "Medium"
                    sev_color = "#FFB800"
                    rb_lower = rb.lower()
                    if "high" in rb_lower[:200]:
                        severity = "High"; sev_color = "#FF6450"
                    elif "low" in rb_lower[:200]:
                        severity = "Low"; sev_color = "#00F5D4"
                    st.markdown(f"""
                    <div class="risk-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                            <strong style="color:#FF6450;">⚠️ {rh.strip('*').strip()}</strong>
                            <span style="font-size:11px;padding:2px 10px;border-radius:100px;
                                         color:{sev_color};background:{sev_color}22;font-weight:600;
                                         font-family:'JetBrains Mono',monospace;">{severity}</span>
                        </div>
                        <div style="font-size:13px;color:#B0B0C8;line-height:1.6;">{rb[:400]}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(content)

        else:
            st.markdown(content)

        st.markdown("</div>", unsafe_allow_html=True)

# ── Navigation ────────────────────────────────────────────────────────────────
st.divider()
nav_c1, nav_c2, nav_c3 = st.columns(3)
with nav_c1:
    if st.button("⬅️ Back to Ideas", use_container_width=True):
        st.session_state.idea = ""
        st.session_state.idea_type = ""
        st.session_state.generation_done = False
        st.switch_page("app.py")
with nav_c2:
    if st.button("📊 Dashboard", use_container_width=True):
        st.switch_page("pages/5_Dashboard.py")
with nav_c3:
    if st.button("🎨 View Mockup →", type="primary", use_container_width=True):
        st.switch_page("pages/4_Mockup.py")
