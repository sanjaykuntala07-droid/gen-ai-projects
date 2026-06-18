"""
Dream Machine — Dashboard
All saved blueprints in a premium card grid.
"""
import streamlit as st
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.styles import inject_styles
from components.db import init_db, list_blueprints, delete_blueprint, update_blueprint_status
from components.gemini_client import IDEA_TYPE_ICONS

st.set_page_config(
    page_title="Dashboard — Dream Machine",
    page_icon="✦",
    layout="wide",
)
inject_styles()
init_db()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:32px;">
    <div class="section-tag">Your Workspace</div>
    <h1 style="font-family:'Space Grotesk',sans-serif;font-size:2rem;font-weight:700;
               letter-spacing:-0.03em;color:#E8E8F0;margin:8px 0;">
        Blueprint Dashboard
    </h1>
    <div style="font-size:14px;color:#6B6B8A;">All your ideas, fully engineered.</div>
</div>
""", unsafe_allow_html=True)

# ── New Idea CTA ──────────────────────────────────────────────────────────────
cta_col, search_col = st.columns([1, 2])
with cta_col:
    if st.button("✦ New Blueprint", type="primary", use_container_width=True):
        st.session_state.idea = ""
        st.session_state.idea_type = ""
        st.session_state.generation_done = False
        st.switch_page("app.py")

with search_col:
    search_query = st.text_input(
        "SEARCH",
        placeholder="Search your blueprints...",
        label_visibility="collapsed",
        key="dashboard_search"
    )

# ── Filters ───────────────────────────────────────────────────────────────────
filter_col1, filter_col2, filter_col3 = st.columns(3)
with filter_col1:
    status_filter = st.selectbox(
        "STATUS",
        ["All", "draft", "in_progress", "built", "archived"],
        key="status_filter"
    )
with filter_col2:
    sort_by = st.selectbox(
        "SORT BY",
        ["Newest first", "Oldest first"],
        key="sort_filter"
    )
with filter_col3:
    type_filter = st.selectbox(
        "TYPE",
        ["All Types", "SaaS Platform", "Mobile App", "AI Tool", "Business Concept",
         "Physical Product", "Game", "Other"],
        key="type_filter"
    )

st.divider()

# ── Load Blueprints ────────────────────────────────────────────────────────────
all_blueprints = list_blueprints(limit=200)

# Apply filters
filtered = all_blueprints
if status_filter != "All":
    filtered = [b for b in filtered if b.get("status") == status_filter]
if type_filter != "All Types":
    filtered = [b for b in filtered if b.get("idea_type") == type_filter]
if search_query:
    q = search_query.lower()
    filtered = [b for b in filtered if q in b.get("title", "").lower() or q in b.get("idea", "").lower()]
if sort_by == "Oldest first":
    filtered = list(reversed(filtered))

# ── Stats ─────────────────────────────────────────────────────────────────────
stat_cols = st.columns(4)
with stat_cols[0]:
    st.metric("Total Blueprints", len(all_blueprints))
with stat_cols[1]:
    built = sum(1 for b in all_blueprints if b.get("status") == "built")
    st.metric("Built", built)
with stat_cols[2]:
    in_prog = sum(1 for b in all_blueprints if b.get("status") == "in_progress")
    st.metric("In Progress", in_prog)
with stat_cols[3]:
    public = sum(1 for b in all_blueprints if b.get("is_public"))
    st.metric("Shared", public)

st.markdown("<br>", unsafe_allow_html=True)

# ── Blueprint Grid ─────────────────────────────────────────────────────────────
if not filtered:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">📋</div>
        <div class="empty-state-title">No blueprints found</div>
        <div class="empty-state-text">Your blueprint canvas is empty. What are you going to build?</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("✦ Create Your First Blueprint", type="primary"):
        st.switch_page("app.py")
else:
    # Grid: 3 columns
    num_cols = 3
    rows = [filtered[i:i+num_cols] for i in range(0, len(filtered), num_cols)]

    for row in rows:
        cols = st.columns(num_cols, gap="medium")
        for j, bp in enumerate(row):
            with cols[j]:
                bid = bp["id"]
                icon = IDEA_TYPE_ICONS.get(bp.get("idea_type", ""), "💡")
                title = bp.get("title", bp.get("idea", "Untitled")[:50])
                idea = bp.get("idea", "")
                status = bp.get("status", "draft")
                idea_type = bp.get("idea_type", "Unknown")
                created = bp.get("created_at", "")[:10]

                status_colors = {
                    "draft": ("#6B6B8A", "rgba(107,107,138,0.15)"),
                    "in_progress": ("#FFB800", "rgba(255,184,0,0.12)"),
                    "built": ("#00F5D4", "rgba(0,245,212,0.12)"),
                    "archived": ("#444466", "rgba(68,68,102,0.15)"),
                }
                s_color, s_bg = status_colors.get(status, ("#6B6B8A", "rgba(107,107,138,0.15)"))

                # Check if sections are generated
                has_sections = bool(bp.get("sections"))
                section_count = len(bp.get("sections", {}))

                st.markdown(f"""
                <div class="blueprint-card">
                    <div class="blueprint-card-type">{icon} {idea_type}</div>
                    <div class="blueprint-card-title">{title}</div>
                    <div style="font-size:12px;color:#6B6B8A;line-height:1.5;margin-bottom:14px;">
                        {idea[:100]}{"..." if len(idea) > 100 else ""}
                    </div>
                    <div style="display:flex;align-items:center;justify-content:space-between;">
                        <span style="font-size:11px;padding:3px 10px;border-radius:100px;
                                     color:{s_color};background:{s_bg};font-weight:600;
                                     text-transform:uppercase;letter-spacing:0.5px;">
                            {status.replace("_"," ")}
                        </span>
                        <span style="font-size:11px;color:#6B6B8A;">{section_count}/10 sections · {created}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Action buttons
                action_col1, action_col2, action_col3 = st.columns(3)
                with action_col1:
                    if st.button("View", key=f"view_{bid}", use_container_width=True):
                        st.session_state.current_blueprint_id = bid
                        st.switch_page("pages/3_Blueprint.py")
                with action_col2:
                    if st.button("Mockup", key=f"mock_{bid}", use_container_width=True):
                        st.session_state.current_blueprint_id = bid
                        st.switch_page("pages/4_Mockup.py")
                with action_col3:
                    if st.button("🗑️", key=f"del_{bid}", use_container_width=True,
                                  help="Delete this blueprint"):
                        delete_blueprint(bid)
                        if st.session_state.get("current_blueprint_id") == bid:
                            st.session_state.current_blueprint_id = None
                        st.toast("Blueprint deleted")
                        st.rerun()
