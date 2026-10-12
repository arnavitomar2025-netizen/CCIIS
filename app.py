"""
CCIIS — Cyber Crime Investigation & Intelligence System
NCRP Case Investigation Platform
Phase 2: Authentication, Role-Based Access, CRUD, Charts
"""

import os
import streamlit as st

# Configure wide layout and page metadata
st.set_page_config(
    page_title="CCIIS // Cyber Crime Investigation & Intelligence System",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load and inject custom investigation stylesheet
css_file_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
if os.path.exists(css_file_path):
    with open(css_file_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Auth ──
from auth import get_current_user, allowed_pages
from views.login import render_login_page

# ── Navigation ──
from components.nav import render_sidebar_nav

# ── Protected Views ──
from views.command_center import render_dashboard_page
from views.dockets import render_cases_page
from views.suspects import render_suspects_page
from views.evidence import render_evidence_page
from views.patterns import render_patterns_page
from views.reports import render_reports_page
from views.audit_log import render_audit_log_page
from views.my_cases import render_my_cases_page
from views.my_evidence import render_my_evidence_page


_PAGE_ROUTES = {
    "Dashboard":  render_dashboard_page,
    "Cases":      render_cases_page,
    "Suspects":   render_suspects_page,
    "Evidence":   render_evidence_page,
    "Patterns":   render_patterns_page,
    "Reports":    render_reports_page,
    "Audit Log":  render_audit_log_page,
    "My Cases":   render_my_cases_page,
    "My Evidence": render_my_evidence_page,
}


def main():
    user = get_current_user()

    # ── Login Gate ──
    if not user:
        render_login_page()
        return

    # ── Authenticated: render role-aware sidebar ──
    selected_page = render_sidebar_nav()

    # ── Access enforcement: if the page isn't in the user's allowed list, block it ──
    permitted = allowed_pages()
    if selected_page not in permitted:
        st.error(
            f"Access Denied — the page '{selected_page}' is not permitted for your role ({user['role_code']})."
        )
        return

    # ── Route to the correct view ──
    renderer = _PAGE_ROUTES.get(selected_page)
    if renderer:
        renderer()
    else:
        render_dashboard_page()


if __name__ == "__main__":
    main()
