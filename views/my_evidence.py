"""
CCIIS — My Evidence (Victim Portal)
=====================================
Restricted view: shows only evidence records associated with the
logged-in victim's own dockets. No SHA-256 hash, no storage path exposed.
"""

import streamlit as st
from data.mock_db import get_db
from auth import get_current_user
from components.ui_elements import render_editorial_header
from utils.formatters import fmt_datetime


def render_my_evidence_page():
    db = get_db()
    user = get_current_user()
    if not user:
        st.error("Session expired. Please log in again.")
        return

    render_editorial_header(
        title="My Evidence Records",
        description="Digital exhibits collected in connection with your registered complaints.",
        classification="COMPLAINANT PORTAL — VICTIM RESTRICTED VIEW",
    )

    # Only evidence tied to victim's own dockets
    my_doc_nos = {d["doc_no"] for d in db.get_victim_dockets(user["reg_id"])}
    my_evidence = [ev for ev in db.forensic_evidence.values() if ev["doc_no"] in my_doc_nos]

    if not my_evidence:
        st.info("No digital evidence has been recorded for your complaints yet.")
        return

    st.markdown(
        f"""
        <div style="font-family:var(--font-mono); font-size:0.64rem; color:var(--text-dim);
                    margin-bottom:16px; text-transform:uppercase; letter-spacing:0.08em;">
            {len(my_evidence)} evidence items across {len(my_doc_nos)} complaint(s)
        </div>
        """,
        unsafe_allow_html=True,
    )

    for ev in my_evidence:
        uploader = db.registrant_profiles.get(ev["uploader_id"], {}).get("full_name", "Investigating Officer")
        st.markdown(
            f"""
            <div class="evidence-record" style="margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="evidence-id">{ev['evidence_id'].upper()}</span>
                    <span style="font-size:0.68rem; color:var(--text-dim);">{ev['file_type']}</span>
                </div>
                <div style="font-size:0.88rem; color:var(--text-white); font-weight:600; margin-top:5px;">
                    {ev['file_name']}
                </div>
                <div style="font-family:var(--font-mono); font-size:0.70rem; color:var(--text-secondary); margin-top:4px;">
                    Case: <span style="color:var(--text-primary);">{ev['doc_no']}</span>
                    &nbsp;&bull;&nbsp;
                    Collected by: {uploader}
                    &nbsp;&bull;&nbsp;
                    {fmt_datetime(ev['uploaded_at'])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
