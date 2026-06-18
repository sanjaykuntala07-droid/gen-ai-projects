"""
Dream Machine — AI Pitch Deck Generator
Generates investor-ready pitch slides from the blueprint.
"""
import streamlit as st
import streamlit.components.v1 as components
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.styles import inject_styles
from components.db import init_db, get_blueprint, list_blueprints
from components.gemini_client import IDEA_TYPE_ICONS, generate_pitch_deck

st.set_page_config(
    page_title="Pitch Deck — Dream Machine",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_styles()
init_db()

# ── Load Blueprint ──────────────────────────────────────────────────────────────
bid = st.session_state.get("current_blueprint_id")
if not bid:
    bps = list_blueprints(limit=1)
    if bps:
        bid = bps[0]["id"]
        st.session_state.current_blueprint_id = bid

if not bid:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">🎯</div>
        <div class="empty-state-title">No blueprint found</div>
        <div class="empty-state-text">Generate a blueprint first to create your pitch deck.</div>
    </div>
    """, unsafe_allow_html=True)
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
sections = bp.get("sections", {})

# ── Header ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-bottom:24px;">
    <div class="section-tag">Investor Ready</div>
    <h1 style="font-family:'Space Grotesk',sans-serif;font-size:2rem;font-weight:700;
               letter-spacing:-0.03em;color:#E8E8F0;margin:8px 0;">
        {icon} Pitch Deck Generator
    </h1>
    <div style="font-size:14px;color:#6B6B8A;">
        AI-crafted investor slides from your blueprint · {idea_type}
    </div>
</div>
""", unsafe_allow_html=True)

# ── Controls ──────────────────────────────────────────────────────────────────
ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([2, 1, 1, 1])

with ctrl1:
    deck_style = st.selectbox(
        "PITCH STYLE",
        ["Seed / Angel", "Series A", "Demo Day", "Corporate / Enterprise"],
        key="pitch_style_sel"
    )

with ctrl2:
    num_slides = st.selectbox(
        "SLIDE COUNT",
        [10, 12, 15],
        key="pitch_slides_sel"
    )

with ctrl3:
    gen_btn = st.button("✦ Generate Deck", type="primary", use_container_width=True, key="gen_pitch_btn")

with ctrl4:
    if st.button("← Blueprint", use_container_width=True, key="back_to_bp_btn"):
        st.switch_page("pages/3_Blueprint.py")

st.divider()

# ── Session cache key ─────────────────────────────────────────────────────────
cache_key = f"pitch_slides_{bid}_{deck_style}_{num_slides}"

if gen_btn or cache_key not in st.session_state:
    if not sections:
        st.warning("⚠️ This blueprint has no sections yet. Please generate it first.")
        if st.button("Go to Blueprint →", type="primary"):
            st.switch_page("pages/3_Blueprint.py")
        st.stop()

    with st.spinner("🎯 Crafting your investor-ready pitch deck..."):
        slides = generate_pitch_deck(idea, idea_type, sections, deck_style, int(num_slides))
        st.session_state[cache_key] = slides
    st.toast("Pitch deck ready! ✦")

slides = st.session_state.get(cache_key, [])

if not slides:
    st.info("Click **✦ Generate Deck** to create your pitch deck.")
    st.stop()

# ── Slide Navigation ──────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;">
    <div class="section-tag">{len(slides)} Slides Generated</div>
    <div style="font-size:13px;color:#6B6B8A;">
        {deck_style} · {idea_type}
    </div>
</div>
""", unsafe_allow_html=True)

# Slide selector
slide_idx = st.session_state.get("pitch_slide_idx", 0)
slide_idx = max(0, min(slide_idx, len(slides) - 1))

# Slide thumbnails row
thumb_cols = st.columns(min(len(slides), 10))
for i, slide in enumerate(slides):
    with thumb_cols[i % 10]:
        is_active = i == slide_idx
        st.markdown(f"""
        <div style="
            text-align:center;
            padding:8px 4px;
            border-radius:8px;
            background:{'rgba(92,107,255,0.2)' if is_active else 'rgba(255,255,255,0.03)'};
            border:1px solid {'rgba(92,107,255,0.5)' if is_active else 'rgba(92,107,255,0.12)'};
            cursor:pointer;
            font-size:11px;
            color:{'#5C6BFF' if is_active else '#6B6B8A'};
            font-family:'JetBrains Mono',monospace;
            margin-bottom:4px;
        ">
            {i + 1}
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"", key=f"thumb_{i}", help=slide.get("title", f"Slide {i+1}"),
                     use_container_width=True):
            st.session_state.pitch_slide_idx = i
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ── Main Slide Display ─────────────────────────────────────────────────────────
slide = slides[slide_idx]
slide_type = slide.get("type", "content")

# Slide type color map
type_colors = {
    "title": ("#5C6BFF", "rgba(92,107,255,0.08)"),
    "problem": ("#FF6450", "rgba(255,100,80,0.06)"),
    "solution": ("#00F5D4", "rgba(0,245,212,0.06)"),
    "market": ("#FFB800", "rgba(255,184,0,0.06)"),
    "product": ("#5C6BFF", "rgba(92,107,255,0.06)"),
    "traction": ("#00F5D4", "rgba(0,245,212,0.06)"),
    "business_model": ("#FFB800", "rgba(255,184,0,0.06)"),
    "team": ("#5C6BFF", "rgba(92,107,255,0.06)"),
    "financials": ("#FF6450", "rgba(255,100,80,0.06)"),
    "ask": ("#00F5D4", "rgba(0,245,212,0.08)"),
    "content": ("#5C6BFF", "rgba(92,107,255,0.06)"),
}
accent_color, bg_color = type_colors.get(slide_type, type_colors["content"])

# Main slide view + speaker notes side by side
slide_col, notes_col = st.columns([3, 1], gap="large")

with slide_col:
    # Slide card
    bullet_html = ""
    for bullet in slide.get("bullets", []):
        bullet_html += f"""
        <div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:14px;animation:fadeInUp 0.4s ease;">
            <div style="width:6px;height:6px;border-radius:50%;background:{accent_color};
                        flex-shrink:0;margin-top:8px;box-shadow:0 0 8px {accent_color}66;"></div>
            <div style="font-size:15px;color:#D0D0E0;line-height:1.6;font-family:'Inter',sans-serif;">{bullet}</div>
        </div>"""

    stat_html = ""
    for stat in slide.get("stats", []):
        val = stat.get("value", "")
        label = stat.get("label", "")
        stat_html += f"""
        <div style="text-align:center;padding:20px;background:rgba(255,255,255,0.04);
                    border:1px solid {accent_color}33;border-radius:12px;flex:1;">
            <div style="font-family:'Space Grotesk',sans-serif;font-size:2rem;font-weight:700;
                        color:{accent_color};letter-spacing:-0.02em;">{val}</div>
            <div style="font-size:12px;color:#6B6B8A;margin-top:4px;text-transform:uppercase;
                        letter-spacing:1px;font-family:'JetBrains Mono',monospace;">{label}</div>
        </div>"""

    if stat_html:
        stat_html = f'<div style="display:flex;gap:16px;margin-bottom:24px;">{stat_html}</div>'

    st.markdown(f"""
    <div style="
        background:linear-gradient(135deg,{bg_color},{bg_color.replace('0.06','0.02')});
        border:1px solid {accent_color}33;
        border-left:4px solid {accent_color};
        border-radius:16px;
        padding:40px 48px;
        min-height:420px;
        position:relative;
        overflow:hidden;
    ">
        <!-- Slide number badge -->
        <div style="position:absolute;top:20px;right:24px;font-family:'JetBrains Mono',monospace;
                    font-size:11px;color:#3A3A5A;text-transform:uppercase;letter-spacing:1px;">
            {slide_idx + 1} / {len(slides)}
        </div>

        <!-- Slide type tag -->
        <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:{accent_color};
                    text-transform:uppercase;letter-spacing:2px;margin-bottom:16px;">
            ◆ {slide_type.replace('_', ' ').title()}
        </div>

        <!-- Title -->
        <div style="font-family:'Space Grotesk',sans-serif;font-size:1.9rem;font-weight:700;
                    color:#E8E8F0;margin-bottom:8px;letter-spacing:-0.03em;line-height:1.2;">
            {slide.get('title', '')}
        </div>

        <!-- Subtitle -->
        <div style="font-size:14px;color:#6B6B8A;margin-bottom:28px;line-height:1.5;">
            {slide.get('subtitle', '')}
        </div>

        <!-- Stats row -->
        {stat_html}

        <!-- Bullets -->
        {bullet_html}
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    st.markdown("<br>", unsafe_allow_html=True)
    nav1, nav2, nav3, nav4, nav5 = st.columns([1, 1, 2, 1, 1])
    with nav1:
        if st.button("⏮ First", use_container_width=True, disabled=slide_idx == 0):
            st.session_state.pitch_slide_idx = 0
            st.rerun()
    with nav2:
        if st.button("← Prev", use_container_width=True, disabled=slide_idx == 0):
            st.session_state.pitch_slide_idx = slide_idx - 1
            st.rerun()
    with nav3:
        st.markdown(f"""
        <div style="text-align:center;font-family:'JetBrains Mono',monospace;font-size:13px;
                    color:#6B6B8A;padding:12px;">
            Slide {slide_idx + 1} of {len(slides)}
        </div>
        """, unsafe_allow_html=True)
    with nav4:
        if st.button("Next →", use_container_width=True, disabled=slide_idx == len(slides) - 1,
                     type="primary"):
            st.session_state.pitch_slide_idx = slide_idx + 1
            st.rerun()
    with nav5:
        if st.button("Last ⏭", use_container_width=True, disabled=slide_idx == len(slides) - 1):
            st.session_state.pitch_slide_idx = len(slides) - 1
            st.rerun()

with notes_col:
    # Speaker notes
    st.markdown('<div class="section-tag">Speaker Notes</div>', unsafe_allow_html=True)
    notes = slide.get("speaker_notes", "")
    if notes:
        st.markdown(f"""
        <div class="dream-card" style="font-size:13px;line-height:1.7;color:#B0B0C8;">
            {notes}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="font-size:13px;color:#6B6B8A;font-style:italic;padding:16px;">
            No speaker notes for this slide.
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-tag" style="margin-top:20px;">Slide Type</div>',
                unsafe_allow_html=True)
    st.markdown(f"""
    <div style="padding:12px;background:rgba(255,255,255,0.03);border-radius:8px;
                border:1px solid {accent_color}33;font-size:13px;color:{accent_color};
                font-family:'JetBrains Mono',monospace;text-transform:uppercase;
                letter-spacing:1px;">
        {slide_type.replace('_', ' ').title()}
    </div>
    """, unsafe_allow_html=True)

    # Tips
    tips_map = {
        "title": "Lead with your name, the company name, and one power sentence. Eye contact!",
        "problem": "Make them FEEL the pain. Use a story or shocking statistic.",
        "solution": "Demo if possible. Show, don't just tell.",
        "market": "TAM/SAM/SOM — but focus on why YOU can win the SAM.",
        "business_model": "Be specific about pricing. Show you understand unit economics.",
        "traction": "Nothing speaks louder than numbers. Show growth trajectory.",
        "team": "Why is THIS team uniquely positioned to win?",
        "ask": "Be specific. Tell them exactly what you'll do with the money.",
    }
    tip = tips_map.get(slide_type, "Tell a story. Data + emotion = memorable pitch.")
    st.markdown(f"""
    <div style="margin-top:16px;padding:12px;background:rgba(255,184,0,0.06);
                border:1px solid rgba(255,184,0,0.2);border-radius:8px;">
        <div style="font-size:11px;color:#FFB800;text-transform:uppercase;letter-spacing:1px;
                    font-family:'JetBrains Mono',monospace;margin-bottom:6px;">💡 Tip</div>
        <div style="font-size:12px;color:#C0B090;line-height:1.6;">{tip}</div>
    </div>
    """, unsafe_allow_html=True)

# ── All Slides Overview ───────────────────────────────────────────────────────
st.divider()
with st.expander("📋 All Slides Overview", expanded=False):
    overview_cols = st.columns(3)
    for i, s in enumerate(slides):
        s_type = s.get("type", "content")
        _, bg = type_colors.get(s_type, type_colors["content"])
        with overview_cols[i % 3]:
            is_cur = i == slide_idx
            st.markdown(f"""
            <div style="background:{bg};border:1px solid {'rgba(92,107,255,0.4)' if is_cur else 'rgba(92,107,255,0.12)'};
                        border-radius:10px;padding:14px;margin-bottom:12px;cursor:pointer;">
                <div style="font-size:10px;color:#6B6B8A;font-family:'JetBrains Mono',monospace;
                            text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">
                    {i + 1} · {s_type.replace('_', ' ').title()}
                </div>
                <div style="font-size:13px;font-weight:600;color:#E8E8F0;font-family:'Space Grotesk',sans-serif;">
                    {s.get('title', '')[:50]}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Jump to slide {i+1}", key=f"jump_{i}", use_container_width=True):
                st.session_state.pitch_slide_idx = i
                st.rerun()

# ── Export ────────────────────────────────────────────────────────────────────
st.divider()
exp1, exp2, exp3 = st.columns(3)

with exp1:
    # Export as formatted text
    export_lines = [
        f"# PITCH DECK: {bp.get('title', idea[:50])}",
        f"Style: {deck_style} | Type: {idea_type}",
        f"Generated by Dream Machine\n",
        "---\n",
    ]
    for i, s in enumerate(slides):
        export_lines.append(f"## Slide {i+1}: {s.get('title', '')}")
        export_lines.append(f"*{s.get('subtitle', '')}*\n")
        for b in s.get("bullets", []):
            export_lines.append(f"- {b}")
        for st_item in s.get("stats", []):
            export_lines.append(f"**{st_item.get('value','')}** — {st_item.get('label','')}")
        if s.get("speaker_notes"):
            export_lines.append(f"\n> **Speaker Notes:** {s.get('speaker_notes', '')}")
        export_lines.append("\n---\n")

    export_text = "\n".join(export_lines)
    st.download_button(
        "📥 Export as Markdown",
        data=export_text,
        file_name=f"pitch_{bid[:8]}.md",
        mime="text/markdown",
        use_container_width=True
    )

with exp2:
    if st.button("🔄 Regenerate Deck", use_container_width=True, key="regen_deck_btn"):
        if cache_key in st.session_state:
            del st.session_state[cache_key]
        st.rerun()

with exp3:
    if st.button("📊 View Blueprint →", type="primary", use_container_width=True):
        st.switch_page("pages/3_Blueprint.py")
