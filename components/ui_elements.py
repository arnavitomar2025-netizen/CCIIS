"""
CCIIS — UI Element Helpers
BLACK / RED / WHITE visual identity.
Provides consistent badges, page mastheads, and section headers.
"""

from datetime import datetime
import streamlit as st


def render_status_tag(stage_code: str) -> str:
    """Returns HTML for a status badge based on stage_code."""
    map_ = {
        "INVESTIGATION": ("badge badge-investigation", "INVESTIGATION"),
        "TRIAGE":        ("badge badge-triage", "TRIAGE"),
        "LOGGED":        ("badge badge-logged", "LOGGED"),
        "CLOSED":        ("badge badge-closed", "CLOSED"),
    }
    cls, label = map_.get(stage_code, ("badge badge-logged", stage_code))
    return f'<span class="{cls}">{label}</span>'


def render_severity_tag(severity: str) -> str:
    """Returns HTML for a severity badge."""
    map_ = {
        "HIGH":   ("badge badge-high", "HIGH"),
        "MEDIUM": ("badge badge-medium", "MEDIUM"),
        "LOW":    ("badge badge-low", "LOW"),
    }
    cls, label = map_.get(severity.upper(), ("badge badge-low", severity))
    return f'<span class="{cls}">{label}</span>'


def render_editorial_header(title: str, description: str = "", classification: str = "OFFICIAL"):
    """Renders the full page masthead with red bar, classification prefix, bold title."""
    now_str = datetime.now().strftime("%d %b %Y · %H:%M UTC+5:30")
    st.markdown(
        f"""
        <div class="page-masthead">
            <div class="page-masthead-prefix">{classification}</div>
            <h1 class="page-masthead-title">{title}</h1>
            {"<p class='page-masthead-desc'>" + description + "</p>" if description else ""}
            <div class="page-masthead-meta">NCRP DATABASE INTERFACE &bull; SESSION ACTIVE &bull; {now_str}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_head(label: str, title: str, count: str = ""):
    """Renders an inline section subheading."""
    count_html = f'<span style="font-family:var(--font-mono); font-size:0.65rem; color:var(--text-dim);">{count}</span>' if count else ""
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:10px;">
            <div>
                <div class="section-label">{label}</div>
                <div class="section-heading">{title}</div>
            </div>
            {count_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
