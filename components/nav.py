"""
CCIIS — Role-Aware Sidebar Navigation
BLACK / RED / WHITE institutional identity.
Barlow Condensed bold acronym masthead + clean nav rail.
Dynamically renders pages and user panel based on authenticated role.
"""

import streamlit as st
from datetime import datetime
from auth import get_current_user, allowed_pages, logout, ROLE_PERMISSIONS


NAV_ICONS = {
    "Dashboard":  "◈",
    "Cases":      "◻",
    "Suspects":   "◉",
    "Evidence":   "◫",
    "Patterns":   "◆",
    "Reports":    "◧",
    "Audit Log":  "◎",
    "My Cases":   "◻",
    "My Evidence": "◫",
}

ROLE_COLOR = {
    "ADMIN":        "#FF4D6A",
    "INVESTIGATOR": "#E0824A",
    "VICTIM":       "#6AA66C",
}


def render_sidebar_nav() -> str:
    """Renders the CCIIS institutional sidebar navigation for the authenticated user."""
    user = get_current_user()

    with st.sidebar:
        # ── Agency Masthead ──
        now_str = datetime.now().strftime("%d %b %Y · %H:%M")
        st.markdown(
            f"""
            <div class="agency-masthead">
                <div class="masthead-red-bar"></div>
                <div class="masthead-body">
                    <div class="masthead-dept">Government of India &bull; NCRP &bull; {now_str}</div>
                    <div class="masthead-acronym">CC<span>II</span>S</div>
                    <div class="masthead-fullname">Cyber Crime Investigation<br>&amp; Intelligence System</div>
                    <div class="masthead-classification">RESTRICTED // LAW ENFORCEMENT</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div style='height:1px; background:var(--border-main); margin:0;'></div>",
            unsafe_allow_html=True,
        )

        # ── Navigation based on role ──
        pages = allowed_pages() if user else ["Dashboard"]

        if "current_page" not in st.session_state or st.session_state.current_page not in pages:
            st.session_state.current_page = pages[0]

        current_idx = 0
        if st.session_state.current_page in pages:
            current_idx = pages.index(st.session_state.current_page)

        selected_page = st.radio(
            label="Navigation",
            options=pages,
            index=current_idx,
            label_visibility="collapsed",
            key="main_nav_radio",
            format_func=lambda p: f"{NAV_ICONS.get(p, '▸')}  {p}",
        )

        st.session_state.current_page = selected_page

        # ── Active User Panel ──
        if user:
            role = user.get("role_code") or user.get("role") or st.session_state.get("role", "")
            role_color = ROLE_COLOR.get(role, "var(--text-secondary)")
            role_label = ROLE_PERMISSIONS.get(role, {}).get("label", role or "Authenticated User")
            from data.mock_db import get_db
            db_conn = get_db()
            db_status = '<span style="color:#6AA66C;">DB: MYSQL</span>' if getattr(db_conn, "is_mysql", False) else '<span style="color:#CC5500;">DB: STANDBY</span>'

            full_name = user.get("full_name", "Unknown User")
            reg_id = str(user.get("reg_id", "")).upper()
            priv_lvl = user.get("priv_lvl", 0)

            st.markdown(
                f"""
                <div class="officer-panel">
                    <div class="officer-badge">Active Session</div>
                    <div class="officer-name">{full_name}</div>
                    <div class="officer-rank">{role_label}</div>
                    <div class="officer-id">
                        <span style="color:{role_color}; font-weight:700;">{role}</span>
                        &nbsp;&bull;&nbsp;{reg_id}
                        &nbsp;&bull;&nbsp;PRIV: {priv_lvl}
                        &nbsp;&bull;&nbsp;{db_status}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            if st.button("⊠  Sign Out", use_container_width=True, key="logout_btn"):
                logout()
                st.rerun()

    return st.session_state.current_page
