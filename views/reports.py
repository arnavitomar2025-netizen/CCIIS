"""
CCIIS — Analytical Reports & Legal Dossiers
BLACK / RED / WHITE editorial design.
Formal digital evidence briefs, statutory affidavits, prosecution documents.
Role-based: INVESTIGATOR/ADMIN can compile; ADMIN can delete.
"""

from datetime import datetime
import streamlit as st
from data.mock_db import get_db
from auth import get_current_user, can
from components.ui_elements import render_editorial_header


def render_reports_page():
    db = get_db()
    user = get_current_user()
    user_name = user["full_name"] if user else "Analyst"

    render_editorial_header(
        title="Analytical Reports & Legal Dossiers",
        description="Formal digital evidence briefs, link analysis summaries, and affidavits prepared for statutory prosecution under the IT Act and IPC.",
        classification="STATUTORY ADMISSIBILITY DOSSIER",
    )

    all_reports = list(db.analytical_reports.values())

    # ── Search & Filter Bar ──
    f1, f2 = st.columns([2, 1])
    with f1:
        search_query = st.text_input(
            "Search Dossiers",
            placeholder="Search by Report ID, category, docket, or narrative...",
            label_visibility="collapsed",
            key="rep_search_input",
        ).strip().lower()
    with f2:
        categories = ["All Categories"] + sorted(list({r["rep_type"] for r in all_reports}))
        filter_cat = st.selectbox("Category Filter", categories, label_visibility="collapsed", key="rep_cat_select")

    filtered_reports = all_reports
    if search_query:
        filtered_reports = [
            r for r in filtered_reports
            if search_query in r["report_id"].lower()
            or search_query in r["rep_type"].lower()
            or search_query in r.get("doc_no", "").lower()
            or search_query in r["doc_summary"].lower()
        ]
    if filter_cat != "All Categories":
        filtered_reports = [r for r in filtered_reports if r["rep_type"] == filter_cat]

    rep_ids = [r["report_id"] for r in filtered_reports]
    default_rep_id = st.session_state.get("selected_report_id", "rep-001")
    if default_rep_id not in rep_ids and rep_ids:
        default_rep_id = rep_ids[0]

    col_list, col_doc = st.columns([1.0, 2.4], gap="large")

    # ── LEFT: Report Index ──
    with col_list:
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <div class="section-label">Filed Reports</div>
                <span style="font-family:var(--font-mono); font-size:0.60rem; color:var(--text-dim);">
                    {len(filtered_reports)} OF {len(all_reports)} DOSSIERS
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not filtered_reports:
            st.info("No dossiers match the search criteria.")
        else:
            for r in filtered_reports:
                is_active = r["report_id"] == default_rep_id
                border = "#C8102E" if is_active else "var(--border-main)"
                bg = "var(--bg-elevated)" if is_active else "var(--bg-panel)"

                st.markdown(
                    f"""
                    <div style="background:{bg}; border:1px solid {border};
                                border-left:3px solid {'#C8102E' if is_active else 'transparent'};
                                padding:10px 12px; margin-bottom:6px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-family:var(--font-mono); font-weight:700; font-size:0.80rem; color:var(--text-white);">
                                {r['report_id'].upper()}
                            </span>
                            <span style="font-family:var(--font-mono); font-size:0.60rem; color:#6AA66C; font-weight:700;">
                                ADMISSIBLE
                            </span>
                        </div>
                        <div style="font-family:var(--font-display); font-size:0.88rem; font-weight:700;
                                    color:var(--text-white); text-transform:uppercase; letter-spacing:0.03em; margin-top:3px;">
                            {r['rep_type'].replace('_', ' ')}
                        </div>
                        <div style="font-family:var(--font-mono); font-size:0.66rem; color:var(--text-dim); margin-top:2px;">
                            {r.get('doc_no', 'Unlinked')}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Open Document →", key=f"btn_pick_r_{r['report_id']}", use_container_width=True):
                    st.session_state.selected_report_id = r["report_id"]
                    st.rerun()

        st.markdown(
            "<hr style='border:none; border-top:1px solid #2A2A2A; margin:14px 0;'>",
            unsafe_allow_html=True,
        )

        if can("can_create"):
            with st.expander("+ Compile New Analytical Report", expanded=False):
                with st.form("form_compile_report_page"):
                    new_id   = st.text_input("Report ID", value=f"rep-{len(db.analytical_reports)+1:03d}")
                    new_doc  = st.selectbox("Associated Docket", options=list(db.incident_dockets.keys()))
                    new_type = st.selectbox("Report Category", ["LINK_ANALYSIS", "FINANCIAL_TRACE", "FORENSIC_SUMMARY", "TIMELINE_ANALYSIS"])
                    new_auth = st.selectbox(
                        "Authoring Analyst",
                        options=[k for k, v in db.registrant_profiles.items() if v["role_code"] in ("INVESTIGATOR", "ADMIN")],
                        format_func=lambda x: f"{db.registrant_profiles[x]['full_name']} ({x})",
                    )
                    new_sum = st.text_area("Analytical Summary", value="Multi-source correlation confirms centralized coordination across victim complaints.")
                    if st.form_submit_button("Submit Document", type="primary"):
                        try:
                            if hasattr(db, "add_analytical_report"):
                                db.add_analytical_report(
                                    report_id=new_id, author_id=new_auth, rep_type=new_type,
                                    doc_summary=new_sum, doc_no=new_doc, is_admissible=True, changed_by=user_name,
                                )
                            else:
                                db.analytical_reports[new_id] = {
                                    "report_id": new_id, "author_id": new_auth,
                                    "rep_type": new_type, "doc_summary": new_sum,
                                    "doc_no": new_doc, "created_at": datetime.now(), "admissibility": "YES",
                                }
                                db._log_audit("ncrp_analytical_report", "INSERT", new_id, None, f"{new_type} | {new_doc}", user_name)
                            st.success("Report filed and committed to legal ledger.")
                            st.session_state.selected_report_id = new_id
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

    # ── RIGHT: Report Document ──
    with col_doc:
        r = db.analytical_reports.get(default_rep_id)
        if not r:
            st.info("Select a report from the filed index.")
            return

        author = db.registrant_profiles.get(r["author_id"], {})
        docket_obj = db.incident_dockets.get(r.get("doc_no"))

        # Formal Document Header
        st.markdown(
            f"""
            <div style="background:var(--bg-panel); border:1px solid var(--border-main);
                        border-top:3px solid var(--red); padding:18px 20px; margin-bottom:16px;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <div style="font-family:var(--font-mono); font-size:0.56rem; text-transform:uppercase;
                                    letter-spacing:0.12em; color:var(--text-dim); margin-bottom:4px;">
                            ANALYTICAL REPORT &amp; STATUTORY DOSSIER
                        </div>
                        <div style="font-family:var(--font-mono); font-size:0.75rem; font-weight:700;
                                    color:var(--red); margin-bottom:3px;">
                            {r['report_id'].upper()}
                        </div>
                        <div class="jacket-case-num">{r['rep_type'].replace('_', ' ')}</div>
                    </div>
                    <span class="badge badge-closed">COURT ADMISSIBLE</span>
                </div>
                <hr style="border:none; border-top:1px solid var(--border-subtle); margin:12px 0;">
                <div style="display:grid; grid-template-columns: repeat(3,1fr); gap:16px;">
                    <div>
                        <div class="jacket-field-label">Authoring Analyst</div>
                        <div class="jacket-field-val">{author.get('full_name', 'Analyst')}</div>
                        <div style="font-family:var(--font-mono); font-size:0.60rem; color:var(--text-dim); margin-top:1px;">
                            {r['author_id']}
                        </div>
                    </div>
                    <div>
                        <div class="jacket-field-label">Affiliated Inquiry Docket</div>
                        <div style="font-family:var(--font-display); font-size:0.95rem; font-weight:800;
                                    color:var(--text-white); text-transform:uppercase; letter-spacing:0.03em; margin-top:2px;">
                            {r.get('doc_no', 'UNLINKED')}
                        </div>
                    </div>
                    <div>
                        <div class="jacket-field-label">Filing Timestamp</div>
                        <div style="font-family:var(--font-mono); font-size:0.82rem; color:var(--text-secondary); margin-top:2px;">
                            {r['created_at'].strftime('%d %b %Y, %H:%M')}
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Document Body
        st.markdown(
            f"""
            <div style="background:var(--bg-secondary); border:1px solid var(--border-main);
                        padding:22px 24px; margin-bottom:16px; position:relative;">
                <div style="font-family:var(--font-mono); font-size:0.56rem; text-transform:uppercase;
                            letter-spacing:0.14em; color:var(--text-dim); border-bottom:1px solid var(--border-subtle);
                            padding-bottom:10px; margin-bottom:16px;">
                    GOVERNMENT OF INDIA &bull; NATIONAL CYBERCRIME REPORTING PORTAL &bull; FORMAL INVESTIGATION REPORT &bull; CONFIDENTIAL
                </div>
                <div style="font-family:var(--font-mono); font-size:0.60rem; text-transform:uppercase;
                            letter-spacing:0.10em; color:var(--text-dim); margin-bottom:8px;">
                    Analytical Findings &amp; Summary
                </div>
                <div style="font-size:0.88rem; color:var(--text-primary); line-height:1.70;
                            border-left:3px solid var(--red); padding-left:16px;">
                    {r['doc_summary']}
                </div>
                <hr style="border:none; border-top:1px dashed var(--border-main); margin:18px 0;">
                <div style="display:flex; justify-content:space-between; align-items:center;
                            font-family:var(--font-mono); font-size:0.60rem; color:var(--text-dim);">
                    <span>VERIFICATION HASH: CRYPTOGRAPHICALLY COMMITTED</span>
                    <span>STATUTORY ADMISSIBILITY: CERTIFIED UNDER EVIDENCE ACT</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if r.get("doc_no") and docket_obj:
            col_d_info, col_d_btn = st.columns([2, 1])
            with col_d_info:
                st.markdown(
                    f"""
                    <div style="font-family:var(--font-mono); font-size:0.75rem; color:var(--text-secondary);">
                        Linked Case: <strong style="color:var(--text-white);">{r['doc_no']}</strong>
                        &bull; {docket_obj['crime_type']}
                        &bull; Loss: ₹{docket_obj['loss_amt']:,.0f}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_d_btn:
                if st.button(f"Open Case Jacket: {r['doc_no']}", key=f"rep_open_d_{r['doc_no']}", use_container_width=True):
                    st.session_state.selected_docket_id = r["doc_no"]
                    st.session_state.current_page = "Cases"
                    st.rerun()

        # ── DELETE REPORT (ADMIN ONLY) ──
        if can("can_delete"):
            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
            with st.expander("⊠ Delete Report [ADMIN ONLY]", expanded=False):
                st.warning(
                    f"Permanently remove report **{r['report_id'].upper()}**. "
                    "This cannot be undone during this session."
                )
                confirmed = st.checkbox("Confirm deletion.", key=f"confirm_del_rep_{r['report_id']}")
                if confirmed and st.button("Delete Report", key=f"del_rep_{r['report_id']}", type="primary"):
                    db.delete_report(r["report_id"], changed_by=user_name)
                    st.success("Report deleted.")
                    st.session_state.pop("selected_report_id", None)
                    st.rerun()
