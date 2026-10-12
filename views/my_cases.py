"""
CCIIS — My Cases (Victim Portal)
==================================
Restricted view: shows only cases where the logged-in user is the victim.
No suspect intelligence, no officer contact details beyond name, no bank records.
"""

import streamlit as st
from data.mock_db import get_db
from auth import get_current_user
from components.ui_elements import render_editorial_header, render_status_tag
from utils.formatters import fmt_date, fmt_inr


def render_my_cases_page():
    db = get_db()
    user = get_current_user()
    if not user:
        st.error("Session expired. Please log in again.")
        return

    render_editorial_header(
        title="My Registered Complaints",
        description="Cases filed under your identity with the National Cybercrime Reporting Portal.",
        classification="COMPLAINANT PORTAL — VICTIM RESTRICTED VIEW",
    )

    victim_dockets = db.get_victim_dockets(user["reg_id"])
    if not victim_dockets:
        st.info("No complaints are currently registered under your profile.")
        return

    st.markdown(
        f"""
        <div style="background:rgba(200,16,46,0.07); border:1px solid var(--red-muted);
                    border-left:3px solid var(--red); padding:10px 14px; margin-bottom:20px;
                    font-family:var(--font-mono); font-size:0.68rem; color:var(--text-secondary);">
            ⚑ You are viewing your own complaint records only.
            For status queries, contact your assigned investigating officer.
            Sensitive investigation details are restricted to law enforcement personnel.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Case selector ──
    case_keys = [d["doc_no"] for d in victim_dockets]
    selected_key = st.session_state.get("selected_docket_id", case_keys[0] if case_keys else None)
    if selected_key not in case_keys:
        selected_key = case_keys[0]

    col_list, col_detail = st.columns([1, 2.2], gap="large")

    with col_list:
        st.markdown(
            f'<div class="section-label" style="margin-bottom:10px;">Your Complaints ({len(victim_dockets)})</div>',
            unsafe_allow_html=True,
        )
        for d in victim_dockets:
            is_sel = d["doc_no"] == selected_key
            bg = "var(--bg-elevated)" if is_sel else "var(--bg-panel)"
            border = "#C8102E" if is_sel else "var(--border-main)"
            st.markdown(
                f"""
                <div style="background:{bg}; border:1px solid {border};
                            border-left:3px solid {'#C8102E' if is_sel else 'transparent'};
                            padding:10px 12px; margin-bottom:6px;">
                    <div style="font-family:var(--font-display); font-weight:800; font-size:0.90rem;
                                color:var(--text-white); text-transform:uppercase; letter-spacing:0.04em;">
                        {d['doc_no']}
                    </div>
                    <div style="font-size:0.76rem; color:var(--text-secondary); margin-top:3px;">
                        {d['crime_type']}
                    </div>
                    <div style="margin-top:4px;">{render_status_tag(d['stage_code'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("View Details →", key=f"vic_sel_{d['doc_no']}", use_container_width=True):
                st.session_state.selected_docket_id = d["doc_no"]
                st.rerun()

    with col_detail:
        d = db.incident_dockets.get(selected_key)
        if not d:
            st.info("Select a complaint to view details.")
            return

        officer = db.registrant_profiles.get(d["officer_id"], {})
        ev_count = db.fn_evidence_count(d["doc_no"])

        st.markdown(
            f"""
            <div class="jacket-header">
                <div style="font-family:var(--font-mono); font-size:0.56rem; text-transform:uppercase;
                            letter-spacing:0.12em; color:var(--text-dim); margin-bottom:4px;">
                    COMPLAINT RECORD // NCRP
                </div>
                <div class="jacket-case-num">{d['doc_no']}</div>
                <div class="jacket-crime-type">{d['crime_type'].upper()}</div>
                <hr style="border:none; border-top:1px solid var(--border-subtle); margin:12px 0;">
                <div style="display:grid; grid-template-columns: repeat(3,1fr); gap:16px;">
                    <div>
                        <div class="jacket-field-label">Current Stage</div>
                        <div style="margin-top:4px;">{render_status_tag(d['stage_code'])}</div>
                    </div>
                    <div>
                        <div class="jacket-field-label">Reported Loss</div>
                        <div style="font-family:var(--font-mono); font-size:0.92rem; font-weight:700;
                                    color:var(--text-white); margin-top:2px;">{fmt_inr(d['loss_amt'])}</div>
                    </div>
                    <div>
                        <div class="jacket-field-label">Date Filed</div>
                        <div style="font-family:var(--font-mono); font-size:0.82rem;
                                    color:var(--text-secondary); margin-top:2px;">{fmt_date(d['filed_dt'])}</div>
                    </div>
                </div>
                <hr style="border:none; border-top:1px solid var(--border-subtle); margin:12px 0;">
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
                    <div>
                        <div class="jacket-field-label">Investigating Officer</div>
                        <div class="jacket-field-val">{officer.get('full_name', 'Assigned Officer')}</div>
                    </div>
                    <div>
                        <div class="jacket-field-label">Evidence Items Collected</div>
                        <div style="font-family:var(--font-mono); font-size:0.88rem;
                                    color:var(--text-secondary); margin-top:2px;">{ev_count} items</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="section-label" style="margin:16px 0 6px;">Complaint Narrative</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div style="background:var(--bg-secondary); border:1px solid var(--border-main);
                        padding:16px 18px; line-height:1.65; font-size:0.88rem; color:var(--text-primary);">
                {d['details']}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="background:rgba(46,107,48,0.08); border:1px solid #2E6B30;
                        padding:10px 14px; margin-top:16px; font-size:0.76rem; color:var(--text-secondary);">
                If you need to update your complaint or check on its progress, please contact
                the cybercrime helpline at <strong style="color:var(--text-primary);">1930</strong>
                or visit your nearest cybercrime police station.
            </div>
            """,
            unsafe_allow_html=True,
        )
