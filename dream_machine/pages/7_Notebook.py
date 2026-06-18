"""
Dream Machine — Idea Notebook
Personal notes and annotations for blueprints.
"""
import streamlit as st
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.styles import inject_styles
from components.db import init_db, get_blueprint, list_blueprints, get_notes, save_notes
from components.gemini_client import IDEA_TYPE_ICONS

st.set_page_config(
    page_title="Notebook — Dream Machine",
    page_icon="✦",
    layout="wide",
)
inject_styles()
init_db()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:24px;">
    <div class="section-tag">Personal Workspace</div>
    <h1 style="font-family:'Space Grotesk',sans-serif;font-size:2rem;font-weight:700;
               letter-spacing:-0.03em;color:#E8E8F0;margin:8px 0;">
        Idea Notebook
    </h1>
    <div style="font-size:14px;color:#6B6B8A;">
        Annotate blueprints, capture insights, track your thinking.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Blueprint Selector ────────────────────────────────────────────────────────
all_bps = list_blueprints(limit=100)
if not all_bps:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">📓</div>
        <div class="empty-state-title">No blueprints yet</div>
        <div class="empty-state-text">Create a blueprint to start taking notes.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("✦ Create a Blueprint", type="primary"):
        st.switch_page("app.py")
    st.stop()

# Select blueprint
bp_options = {f"{IDEA_TYPE_ICONS.get(b['idea_type'],'💡')} {b['title'][:50]}": b["id"] for b in all_bps}
sel_col, action_col = st.columns([3, 1])

with sel_col:
    selected_label = st.selectbox(
        "SELECT BLUEPRINT",
        list(bp_options.keys()),
        key="notebook_bp_select"
    )
with action_col:
    if st.button("View Blueprint →", use_container_width=True):
        bid = bp_options[selected_label]
        st.session_state.current_blueprint_id = bid
        st.switch_page("pages/3_Blueprint.py")

bid = bp_options[selected_label]
bp = get_blueprint(bid)
notes_data = get_notes(bid)

st.divider()

# ── Two-column layout ─────────────────────────────────────────────────────────
note_col, context_col = st.columns([2, 1], gap="large")

with note_col:
    st.markdown('<div class="section-tag">Your Notes</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="font-size:13px;color:#6B6B8A;margin-bottom:16px;">
        {bp.get('title', '')} · {bp.get('idea_type', '')} · Last updated: {notes_data.get('updated_at', 'Never')[:10] if notes_data.get('updated_at') else 'Never'}
    </div>
    """, unsafe_allow_html=True)

    notes_content = st.text_area(
        "NOTES",
        value=notes_data.get("notes", ""),
        height=400,
        label_visibility="collapsed",
        placeholder="""Start your notes here... Some ideas to get you started:

## Key Insights
- What excites me most about this idea?
- What's the #1 risk I haven't solved?

## Next Steps
1. [ ] Research competitors
2. [ ] Talk to 5 potential users
3. [ ] Build a landing page

## Open Questions
- Who is the real decision maker?
- What's the pricing sweet spot?

## Resources & Links
- [Link to research]
- [Competitor URL]""",
        key="notes_editor"
    )

    save_col1, save_col2 = st.columns([1, 3])
    with save_col1:
        if st.button("💾 Save Notes", type="primary", use_container_width=True):
            save_notes(bid, notes_content)
            st.toast("Notes saved! ✓")

    if notes_content:
        word_count = len(notes_content.split())
        st.markdown(f'<div style="font-size:12px;color:#6B6B8A;margin-top:8px;">{word_count} words</div>',
                    unsafe_allow_html=True)

with context_col:
    st.markdown('<div class="section-tag">Blueprint Context</div>', unsafe_allow_html=True)

    sections = bp.get("sections", {})
    icon = IDEA_TYPE_ICONS.get(bp.get("idea_type", ""), "💡")

    st.markdown(f"""
    <div class="dream-card">
        <div style="font-size:11px;color:#00F5D4;text-transform:uppercase;letter-spacing:1.5px;font-family:'JetBrains Mono',monospace;margin-bottom:8px;">{icon} {bp.get('idea_type','')}</div>
        <div style="font-weight:600;font-size:15px;color:#E8E8F0;margin-bottom:12px;line-height:1.4;">{bp.get('title','')}</div>
        <div style="font-size:13px;color:#6B6B8A;line-height:1.6;">{bp.get('idea','')[:200]}{"..." if len(bp.get('idea','')) > 200 else ""}</div>
    </div>
    """, unsafe_allow_html=True)

    # Section quick-view
    if sections:
        st.markdown('<div class="section-tag" style="margin-top:20px;">Quick Reference</div>', unsafe_allow_html=True)
        section_opts = {k.replace("_", " ").title(): v for k, v in sections.items() if v}
        if section_opts:
            selected_section = st.selectbox(
                "Browse sections",
                list(section_opts.keys()),
                key="nb_section_sel"
            )
            content = section_opts[selected_section]
            with st.container(height=300):
                st.markdown(content[:1000] + ("..." if len(content) > 1000 else ""))

    # Highlights
    st.markdown('<div class="section-tag" style="margin-top:20px;">Quick Notes</div>', unsafe_allow_html=True)
    highlights = notes_data.get("highlights", [])

    new_highlight = st.text_input(
        "ADD HIGHLIGHT",
        placeholder="Key insight to remember...",
        key="new_highlight"
    )
    if st.button("+ Add", key="add_highlight_btn") and new_highlight:
        highlights.append({
            "text": new_highlight,
            "time": datetime.now().strftime("%H:%M")
        })
        save_notes(bid, notes_content, highlights)
        st.toast("Added! ✓")
        st.rerun()

    if highlights:
        for i, hl in enumerate(reversed(highlights[-8:])):
            text = hl.get("text", hl) if isinstance(hl, dict) else hl
            time_str = hl.get("time", "") if isinstance(hl, dict) else ""
            st.markdown(f"""
            <div class="note-card">
                <div style="font-size:13px;color:#E8E8F0;margin-bottom:4px;">✦ {text}</div>
                <div style="font-size:11px;color:#6B6B8A;">{time_str}</div>
            </div>
            """, unsafe_allow_html=True)

# ── Export Notes ──────────────────────────────────────────────────────────────
st.divider()
exp_col1, exp_col2 = st.columns(2)
with exp_col1:
    if notes_content:
        export_text = f"# Notes: {bp.get('title', '')}\n\nIdea: {bp.get('idea', '')}\n\n---\n\n{notes_content}"
        st.download_button(
            "📥 Export Notes",
            data=export_text,
            file_name=f"notes_{bid[:8]}.md",
            mime="text/markdown",
            use_container_width=True
        )
with exp_col2:
    if st.button("📊 View Full Blueprint →", type="primary", use_container_width=True):
        st.session_state.current_blueprint_id = bid
        st.switch_page("pages/3_Blueprint.py")
