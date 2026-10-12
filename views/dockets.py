"""
CCIIS — Case Files & Investigation Jackets
BLACK / RED / WHITE editorial design.
Two-panel: docket ledger left, full case jacket right.
Role-based CRUD: ADMIN/INVESTIGATOR can edit and change stage; ADMIN can delete.
"""

from datetime import datetime
import streamlit as st
from data.mock_db import get_db
from auth import get_current_user, can
from components.ui_elements import render_editorial_header, render_status_tag, render_severity_tag
from components.network_graph import render_case_relationship_graph
from utils.formatters import fmt_inr, compute_severity, fmt_datetime_full, fmt_date


def render_cases_page():
    db = get_db()
    user = get_current_user()
    user_name = user["full_name"] if user else "Officer"

    render_editorial_header(
        title="Case Files & Investigation Jackets",
        description="Statutory crime dockets, forensic chronologies, evidentiary chain of custody, and cross-docket relational mapping.",
        classification="OFFICIAL POLICE INQUIRY FILE",
    )

    all_dockets = list(db.incident_dockets.values())

    # ── Filter Bar ──
    f1, f2, f3 = st.columns([1.5, 1, 1])
    with f1:
        search_query = st.text_input(
            "Search",
            placeholder="Docket number, crime type, narrative...",
            label_visibility="collapsed",
        ).strip().lower()
    with f2:
        stage_opts = ["All Stages", "INVESTIGATION", "TRIAGE", "LOGGED", "CLOSED"]
        filter_stage = st.selectbox("Stage", stage_opts, label_visibility="collapsed")
    with f3:
        crime_opts = ["All Categories"] + sorted(set(d["crime_type"] for d in all_dockets))
        filter_crime = st.selectbox("Category", crime_opts, label_visibility="collapsed")

    filtered = all_dockets
    if search_query:
        filtered = [
            d for d in filtered
            if search_query in d["doc_no"].lower()
            or search_query in d["crime_type"].lower()
            or search_query in d["details"].lower()
        ]
    if filter_stage != "All Stages":
        filtered = [d for d in filtered if d["stage_code"] == filter_stage]
    if filter_crime != "All Categories":
        filtered = [d for d in filtered if d["crime_type"] == filter_crime]

    # ── Two-panel layout ──
    col_list, col_dossier = st.columns([1.0, 2.4], gap="large")

    doc_keys = [d["doc_no"] for d in filtered]
    selected_doc = st.session_state.get("selected_docket_id", "NCRP/2026/0001")
    if selected_doc not in doc_keys and doc_keys:
        selected_doc = doc_keys[0]

    # ── LEFT: Docket Ledger ──
    with col_list:
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <div class="section-label">Docket Register</div>
                <span style="font-family:var(--font-mono); font-size:0.60rem; color:var(--text-dim);">
                    {len(filtered)} MATCHED
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not filtered:
            st.info("No dockets match the current filter.")
        else:
            for d in filtered:
                is_sel = d["doc_no"] == selected_doc
                border = "#C8102E" if is_sel else "var(--border-main)"
                bg = "var(--bg-elevated)" if is_sel else "var(--bg-panel)"

                st.markdown(
                    f"""
                    <div style="background:{bg}; border:1px solid {border};
                                border-left:3px solid {'#C8102E' if is_sel else 'transparent'};
                                padding:10px 12px; margin-bottom:6px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-family:var(--font-display); font-weight:800; font-size:0.90rem;
                                         color:var(--text-white); letter-spacing:0.04em; text-transform:uppercase;">
                                {d['doc_no']}
                            </span>
                            {render_status_tag(d['stage_code'])}
                        </div>
                        <div style="font-size:0.76rem; color:var(--text-secondary); margin-top:3px;">
                            {d['crime_type']}
                            <span style="font-family:var(--font-mono); color:var(--text-dim); font-size:0.70rem;">
                             &bull; ₹{d['loss_amt']:,.0f}
                            </span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if st.button("Inspect →", key=f"sel_d_{d['doc_no']}", use_container_width=True):
                    st.session_state.selected_docket_id = d["doc_no"]
                    st.rerun()

        st.markdown(
            "<hr style='border:none; border-top:1px solid #2A2A2A; margin:14px 0;'>",
            unsafe_allow_html=True,
        )

        with st.expander("+ Register New Docket [sp_register_docket]", expanded=False):
            with st.form("form_register_new_case"):
                new_doc_no = st.text_input("Docket Number", value=f"NCRP/2026/000{len(db.incident_dockets)+1:01d}")
                new_crime = st.selectbox("Crime Category", ["Phishing", "Investment Fraud", "UPI Fraud", "Identity Theft", "Ransomware"])
                new_loss = st.number_input("Reported Loss (INR)", min_value=0.0, value=35000.0, step=1000.0)
                new_victim = st.selectbox(
                    "Complainant",
                    options=list(db.registrant_profiles.keys()),
                    format_func=lambda x: f"{db.registrant_profiles[x]['full_name']} ({x})",
                )
                new_officer = st.selectbox(
                    "Investigating Officer",
                    options=[k for k, v in db.registrant_profiles.items() if v["role_code"] == "INVESTIGATOR"],
                    format_func=lambda x: f"{db.registrant_profiles[x]['full_name']} ({x})",
                )
                new_narrative = st.text_area("Narrative", value="Complainant alleged unauthorized electronic fund transfers.")
                if st.form_submit_button("Submit Registration", type="primary"):
                    try:
                        db.sp_register_docket(
                            doc_no=new_doc_no,
                            victim_id=new_victim,
                            officer_id=new_officer,
                            event_dt=datetime.now(),
                            crime_type=new_crime,
                            details=new_narrative,
                            loss_amt=new_loss,
                        )
                        st.success(f"Docket {new_doc_no} registered.")
                        st.session_state.selected_docket_id = new_doc_no
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ── RIGHT: Full Case Jacket Dossier ──
    with col_dossier:
        if not selected_doc or selected_doc not in db.incident_dockets:
            st.markdown(
                """
                <div style="background:var(--bg-panel); border:1px solid var(--border-main);
                            border-top:3px solid var(--red); padding:40px; text-align:center;">
                    <div style="font-family:var(--font-display); font-size:1.20rem; font-weight:700;
                                color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.06em;">
                        Select a docket from the ledger
                    </div>
                    <div style="font-size:0.80rem; color:var(--text-dim); margin-top:8px;">
                        Choose a case file to open the full investigation jacket.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            return

        doc = db.incident_dockets[selected_doc]
        officer = db.registrant_profiles.get(doc["officer_id"], {})
        victim = db.registrant_profiles.get(doc["victim_id"], {})
        age_days = db.fn_case_age_days(selected_doc)
        ev_count = db.fn_evidence_count(selected_doc)
        severity = (
            "HIGH" if doc["loss_amt"] > 40000 or doc["stage_code"] == "INVESTIGATION"
            else ("MEDIUM" if doc["loss_amt"] > 0 else "LOW")
        )

        # ── Case Jacket Header ──
        st.markdown(
            f"""
            <div class="jacket-header">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <div style="font-family:var(--font-mono); font-size:0.56rem; text-transform:uppercase;
                                    letter-spacing:0.12em; color:var(--text-dim); margin-bottom:4px;">
                            CENTRAL DOCKET JACKET // DIGITAL FRAUD INQUIRY
                        </div>
                        <div class="jacket-case-num">{doc['doc_no']}</div>
                        <div class="jacket-crime-type">{doc['crime_type'].upper()}</div>
                    </div>
                    <div style="text-align:right;">
                        {render_status_tag(doc['stage_code'])}
                        <div style="margin-top:5px;">{render_severity_tag(severity)}</div>
                    </div>
                </div>
                <hr style="border:none; border-top:1px solid var(--border-subtle); margin:12px 0;">
                <div style="display:grid; grid-template-columns: repeat(4,1fr); gap:16px;">
                    <div>
                        <div class="jacket-field-label">Financial Loss</div>
                        <div style="font-family:var(--font-mono); font-size:1.0rem; font-weight:800;
                                    color:{'#FF4D6A' if doc['loss_amt'] > 40000 else 'var(--text-white)'};">
                            ₹{doc['loss_amt']:,.2f}
                        </div>
                    </div>
                    <div>
                        <div class="jacket-field-label">Investigating Officer</div>
                        <div class="jacket-field-val">{officer.get('full_name', 'Unassigned')}</div>
                    </div>
                    <div>
                        <div class="jacket-field-label">Complainant / Victim</div>
                        <div class="jacket-field-val">{victim.get('full_name', 'Anonymous')}</div>
                    </div>
                    <div>
                        <div class="jacket-field-label">Days on File / Exhibits</div>
                        <div style="font-family:var(--font-mono); font-size:0.88rem; color:var(--text-secondary);">
                            {age_days}d &bull; {ev_count} items
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_rel, tab_narrative, tab_timeline, tab_suspects, tab_evidence, tab_patterns, tab_reports = st.tabs([
            "Relationship Analysis",
            "Statement & Details",
            "Investigation Timeline",
            "Attributed Targets",
            "Evidence Locker",
            "Pattern Clusters",
            "Statutory Reports",
        ])

        net_data = db.get_investigation_network(selected_doc)

        # ── TAB 1: RELATIONSHIP ANALYSIS ──
        with tab_rel:
            st.caption("Forensic relational network linking primary docket to target subjects, infrastructure pivots, and correlated complaints.")
            render_case_relationship_graph(net_data)

        # ── TAB 2: STATEMENT & DETAILS ──
        with tab_narrative:
            st.markdown(
                "<div class='section-label' style='margin-bottom:6px;'>Complainant Statement & First Information Summary</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div style="background:var(--bg-secondary); border:1px solid var(--border-main);
                            padding:16px 18px; line-height:1.65; font-size:0.88rem;
                            color:var(--text-primary); margin-bottom:18px;">
                    {doc['details']}
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                "<div class='section-label' style='margin-bottom:6px;'>Status Workflow Transition [sp_update_stage]</div>",
                unsafe_allow_html=True,
            )
            col_sel, col_btn = st.columns([1.5, 1])
            with col_sel:
                new_status = st.selectbox(
                    "Update Stage",
                    options=["TRIAGE", "LOGGED", "INVESTIGATION", "CLOSED"],
                    index=["TRIAGE", "LOGGED", "INVESTIGATION", "CLOSED"].index(doc["stage_code"]),
                    key="select_stage_update",
                    label_visibility="collapsed",
                )
            with col_btn:
                if can("can_change_stage") and st.button("Commit Status Change", type="primary", use_container_width=True):
                    try:
                        db.sp_update_stage(doc["doc_no"], new_status, changed_by=user_name)
                        st.success(f"Stage transitioned to {new_status}.")
                        st.rerun()
                    except PermissionError as pe:
                        st.error(f"Action Restricted: {pe}")
                    except Exception as ex:
                        st.error(f"Error: {ex}")

        # ── EDIT DOCKET (ADMIN / INVESTIGATOR) ──
        if can("can_edit"):
            with st.expander("✎ Edit Docket Fields", expanded=False):
                with st.form(f"form_edit_docket_{selected_doc}"):
                    ed_crime = st.selectbox(
                        "Crime Category",
                        ["Phishing", "Investment Fraud", "UPI Fraud", "Identity Theft", "Ransomware"],
                        index=["Phishing", "Investment Fraud", "UPI Fraud", "Identity Theft", "Ransomware"].index(doc["crime_type"])
                        if doc["crime_type"] in ["Phishing", "Investment Fraud", "UPI Fraud", "Identity Theft", "Ransomware"] else 0,
                    )
                    ed_loss = st.number_input(
                        "Reported Loss (INR)", min_value=0.0, value=float(doc["loss_amt"]), step=1000.0
                    )
                    ed_officer = st.selectbox(
                        "Investigating Officer",
                        options=[k for k, v in db.registrant_profiles.items() if v["role_code"] == "INVESTIGATOR"],
                        format_func=lambda x: f"{db.registrant_profiles[x]['full_name']} ({x})",
                        index=list(k for k, v in db.registrant_profiles.items() if v["role_code"] == "INVESTIGATOR").index(doc["officer_id"])
                        if doc["officer_id"] in [k for k, v in db.registrant_profiles.items() if v["role_code"] == "INVESTIGATOR"] else 0,
                    )
                    ed_narrative = st.text_area("Narrative", value=doc["details"])
                    if st.form_submit_button("Save Changes", type="primary"):
                        try:
                            db.edit_docket(
                                doc_no=selected_doc, crime_type=ed_crime, details=ed_narrative,
                                loss_amt=ed_loss, officer_id=ed_officer, changed_by=user_name,
                            )
                            st.success("Docket updated.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

        # ── DELETE DOCKET (ADMIN ONLY) ──
        if can("can_delete"):
            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            with st.expander("⊠ Delete This Docket [ADMIN ONLY]", expanded=False):
                st.warning(
                    f"Permanently remove **{selected_doc}** and all linked evidence, suspect links, and pattern links. "
                    "This action cannot be undone during this session."
                )
                confirm_key = f"confirm_delete_{selected_doc}"
                confirmed = st.checkbox("I confirm deletion of this docket and all related records.", key=confirm_key)
                if confirmed and st.button("Delete Docket", key=f"del_doc_{selected_doc}", type="primary"):
                    db.delete_docket(selected_doc, changed_by=user_name)
                    st.success(f"Docket {selected_doc} deleted.")
                    st.session_state.pop("selected_docket_id", None)
                    st.rerun()

        # ── TAB 3: INVESTIGATION TIMELINE ──
        with tab_timeline:
            st.markdown(
                "<div class='section-label' style='margin-bottom:12px;'>Chronological Evidentiary Log</div>",
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="timeline-entry">
                    <div class="timeline-ts">{fmt_datetime_full(doc.get('event_dt'))}</div>
                    <div class="timeline-desc"><strong>Incident Occurrence</strong> — Complainant encountered fraudulent vector ({doc.get('crime_type')}).</div>
                </div>
                <div class="timeline-entry">
                    <div class="timeline-ts">{fmt_datetime_full(doc.get('filed_dt'))}</div>
                    <div class="timeline-desc"><strong>Docket Registered</strong> — Formally logged into NCRP database. Loss recorded: ₹{float(doc.get('loss_amt') or 0.0):,.2f}. Assigned to {officer.get('full_name', 'Investigator')}.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            for ev in net_data.get("evidence", []):
                up_time = fmt_datetime_full(ev.get("uploaded_at") or ev.get("uploaded_dt") or doc.get("filed_dt"))
                st.markdown(
                    f"""
                    <div class="timeline-entry">
                        <div class="timeline-ts">{up_time}</div>
                        <div class="timeline-desc"><strong>Evidence Seized</strong> — Exhibit {ev['evidence_id'].upper()} ({ev.get('file_name', 'Unnamed Exhibit')}) entered into secure forensic locker. SHA-256 hash committed.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            for rep in net_data.get("reports", []):
                rep_time = fmt_datetime_full(rep.get("created_at") or rep.get("generated_dt") or doc.get("filed_dt"))
                st.markdown(
                    f"""
                    <div class="timeline-entry">
                        <div class="timeline-ts">{rep_time}</div>
                        <div class="timeline-desc"><strong>Statutory Dossier Compiled</strong> — Report {rep['report_id'].upper()} ({rep.get('rep_type', 'Analytical Dossier')}) prepared for statutory admissibility.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # ── TAB 4: ATTRIBUTED TARGETS ──
        with tab_suspects:
            suspects = net_data.get("suspects", [])
            if not suspects:
                st.info("No suspects currently linked to this docket.")
            else:
                for s in suspects:
                    st.markdown(
                        f"""
                        <div class="suspect-card">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <div class="suspect-alias">{s['alias']}</div>
                                <span style="font-family:var(--font-mono); color:#FF4D6A; font-size:0.72rem; font-weight:700;">
                                    CONFIDENCE: {int(s['conf_score']*100)}%
                                </span>
                            </div>
                            <div style="font-family:var(--font-mono); font-size:0.72rem; color:var(--text-secondary);
                                        margin-top:8px; line-height:1.5;">
                                PHONE: <span style="color:var(--text-primary);">{s['phone'] or 'UNRESOLVED'}</span>
                                &nbsp;&bull;&nbsp;
                                IP: <span style="color:var(--text-primary);">{s['ip_addr'] or 'UNRESOLVED'}</span>
                                &nbsp;&bull;&nbsp;
                                BANK: <span style="color:var(--text-primary);">{s['bank_acc'] or 'NONE'}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button(f"Examine Target: {s['alias']}", key=f"d_susp_btn_{s['suspect_id']}"):
                        st.session_state.selected_suspect_id = s["suspect_id"]
                        st.session_state.current_page = "Suspects"
                        st.rerun()

            with st.expander("+ Link Target Entity [sp_link_suspect]", expanded=False):
                with st.form(f"form_link_s_{selected_doc}"):
                    s_id = st.selectbox(
                        "Target Entity",
                        options=list(db.suspect_entities.keys()),
                        format_func=lambda x: f"{db.suspect_entities[x]['alias']} (#{x:04d})",
                    )
                    conf = st.slider("Attribution Confidence", 0.0, 1.0, 0.85, 0.05)
                    if st.form_submit_button("Execute Link", type="primary"):
                        db.sp_link_suspect(selected_doc, s_id, conf)
                        st.success("Target entity linked.")
                        st.rerun()

        # ── TAB 5: EVIDENCE LOCKER ──
        with tab_evidence:
            evidence_items = net_data.get("evidence", [])
            if not evidence_items:
                st.info("No digital evidence records attached.")
            else:
                for ev in evidence_items:
                    uploader = db.registrant_profiles.get(ev["uploader_id"], {}).get("full_name", ev["uploader_id"])
                    st.markdown(
                        f"""
                        <div class="evidence-record">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span class="evidence-id">{ev['evidence_id'].upper()}</span>
                                <span style="font-size:0.68rem; color:var(--text-dim);">{ev['file_type']}</span>
                            </div>
                            <div style="font-size:0.86rem; color:var(--text-white); font-weight:600; margin-top:5px;">
                                {ev['file_name']}
                            </div>
                            <div style="font-family:var(--font-mono); font-size:0.68rem; color:var(--text-secondary); margin-top:4px;">
                                SHA-256: <span style="color:var(--text-primary);">{ev['sha_hash']}</span>
                            </div>
                            <div style="font-size:0.68rem; color:var(--text-dim); margin-top:3px;">
                                Seized by: {uploader} &bull; Path: {ev['file_path']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button(f"Open Record: {ev['evidence_id'].upper()}", key=f"d_ev_btn_{ev['evidence_id']}"):
                        st.session_state.selected_evidence_id = ev["evidence_id"]
                        st.session_state.current_page = "Evidence"
                        st.rerun()

            with st.expander("+ Ingest Forensic Property Voucher", expanded=False):
                with st.form(f"form_ingest_ev_{selected_doc}"):
                    ev_id = st.text_input("Evidence ID", value=f"ev-{len(db.forensic_evidence)+1:03d}")
                    ev_name = st.text_input("Filename", value="server_access_log.txt")
                    ev_type = st.selectbox("MIME Type", ["text/plain", "application/pdf", "message/rfc822", "image/png", "text/csv"])
                    ev_hash = st.text_input("SHA-256 Checksum", value="a1b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef0")
                    if st.form_submit_button("Commit to Evidence Vault", type="primary"):
                        db.add_forensic_evidence(
                            evidence_id=ev_id, doc_no=selected_doc, file_name=ev_name,
                            file_type=ev_type, file_path=f"/evidence/{selected_doc.split('/')[-1]}/{ev_name}",
                            sha_hash=ev_hash, uploader_id="reg-002",
                        )
                        st.success("Evidence committed to vault.")
                        st.rerun()

        # ── TAB 6: PATTERN CLUSTERS ──
        with tab_patterns:
            clusters = net_data.get("clusters", [])
            if not clusters:
                st.info("No syndicate pattern matches recorded.")
            else:
                for c in clusters:
                    st.markdown(
                        f"""
                        <div class="pattern-card">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-family:var(--font-display); font-size:0.92rem; font-weight:700;
                                             color:var(--text-white); text-transform:uppercase; letter-spacing:0.04em;">
                                    {c['pattern_type'].replace('_', ' ')}
                                </span>
                                <span class="risk-score">RISK: {c['risk_score']}/100</span>
                            </div>
                            <div style="font-family:var(--font-mono); font-size:0.74rem; color:var(--text-secondary); margin-top:5px;">
                                Pivot: <span style="color:var(--text-primary);">{c['pivot_val']}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    for sib in c.get("sibling_dockets", []):
                        if st.button(f"Open Connected Docket: {sib}", key=f"d_pat_sib_{sib}"):
                            st.session_state.selected_docket_id = sib
                            st.rerun()

            with st.expander("+ Correlate Docket to Cluster [trg_pattern_link]", expanded=False):
                with st.form(f"form_cluster_d_{selected_doc}"):
                    c_id = st.selectbox(
                        "Pattern Cluster",
                        options=list(db.pattern_clusters.keys()),
                        format_func=lambda x: f"{db.pattern_clusters[x]['pattern_type']} ({db.pattern_clusters[x]['pivot_val']})",
                    )
                    if st.form_submit_button("Correlate Docket", type="primary"):
                        db.link_docket_pattern(selected_doc, c_id)
                        st.success("Docket correlated to cluster.")
                        st.rerun()

        # ── TAB 7: STATUTORY REPORTS ──
        with tab_reports:
            reports = net_data.get("reports", [])
            if not reports:
                st.info("No analytical reports compiled for this case.")
            else:
                for rep in reports:
                    author = db.registrant_profiles.get(rep["author_id"], {}).get("full_name", rep["author_id"])
                    st.markdown(
                        f"""
                        <div style="background:var(--bg-panel); border:1px solid var(--border-main);
                                    padding:14px 16px; margin-bottom:8px;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-family:var(--font-display); font-size:0.95rem; font-weight:700;
                                             color:var(--text-white); text-transform:uppercase; letter-spacing:0.04em;">
                                    {rep['rep_type'].replace('_', ' ')}
                                </span>
                                <span style="font-family:var(--font-mono); color:#6AA66C; font-size:0.66rem; font-weight:700;">
                                    STATUTORY ADMISSIBLE
                                </span>
                            </div>
                            <div style="font-family:var(--font-mono); font-size:0.70rem; color:var(--text-dim); margin-top:5px;">
                                Author: {author} &bull; ID: {rep['report_id'].upper()}
                            </div>
                            <div style="font-size:0.84rem; color:var(--text-primary); margin-top:8px; line-height:1.5;">
                                {rep['doc_summary']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button(f"View Dossier: {rep['report_id'].upper()}", key=f"d_rep_btn_{rep['report_id']}"):
                        st.session_state.selected_report_id = rep["report_id"]
                        st.session_state.current_page = "Reports"
                        st.rerun()
