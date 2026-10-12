"""
CCIIS — Seized Digital Evidence Locker
BLACK / RED / WHITE editorial design.
Forensic property vouchers, chain of custody, SHA-256 hashes.
Role-based: INVESTIGATOR can ingest; ADMIN can also delete.
"""

from datetime import datetime
import hashlib
import streamlit as st
from data.mock_db import get_db
from auth import get_current_user, can
from components.ui_elements import render_editorial_header


def render_evidence_page():
    db = get_db()
    user = get_current_user()
    user_name = user["full_name"] if user else "Officer"

    render_editorial_header(
        title="Seized Digital Evidence Locker",
        description="Forensic property vouchers, statutory chain of custody ledgers, and SHA-256 cryptographic integrity hashes.",
        classification="STATUTORY FORENSIC PROPERTY LEDGER",
    )

    all_evidence = list(db.forensic_evidence.values())

    # ── Filter Bar ──
    f1, f2, f3 = st.columns([1.8, 1, 1])
    with f1:
        search_query = st.text_input(
            "Search Evidence",
            placeholder="Search by Exhibit ID, filename, SHA-256 checksum, or docket...",
            label_visibility="collapsed",
            key="ev_search_input",
        ).strip().lower()
    with f2:
        mime_types = ["All MIME Types"] + sorted(list({ev["file_type"] for ev in all_evidence}))
        filter_mime = st.selectbox("MIME Type", mime_types, label_visibility="collapsed", key="ev_mime_select")
    with f3:
        dockets = ["All Dockets"] + sorted(list({ev["doc_no"] for ev in all_evidence}))
        filter_doc = st.selectbox("Associated Docket", dockets, label_visibility="collapsed", key="ev_doc_select")

    filtered_evidence = all_evidence
    if search_query:
        filtered_evidence = [
            ev for ev in filtered_evidence
            if search_query in ev["evidence_id"].lower()
            or search_query in ev["file_name"].lower()
            or search_query in ev["sha_hash"].lower()
            or search_query in ev["doc_no"].lower()
        ]
    if filter_mime != "All MIME Types":
        filtered_evidence = [ev for ev in filtered_evidence if ev["file_type"] == filter_mime]
    if filter_doc != "All Dockets":
        filtered_evidence = [ev for ev in filtered_evidence if ev["doc_no"] == filter_doc]

    ev_ids = [ev["evidence_id"] for ev in filtered_evidence]
    default_ev_id = st.session_state.get("selected_evidence_id", "ev-001")
    if default_ev_id not in ev_ids and ev_ids:
        default_ev_id = ev_ids[0]

    col_list, col_detail = st.columns([1.0, 2.4], gap="large")

    # ── LEFT: Evidence Locker List ──
    with col_list:
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <div class="section-label">Evidence Locker</div>
                <span style="font-family:var(--font-mono); font-size:0.60rem; color:var(--text-dim);">
                    {len(filtered_evidence)} OF {len(all_evidence)} ITEMS
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not filtered_evidence:
            st.info("No evidence exhibits match the current filter.")
        else:
            for ev in filtered_evidence:
                is_active = ev["evidence_id"] == default_ev_id
                border = "#C8102E" if is_active else "var(--border-main)"
                bg = "var(--bg-elevated)" if is_active else "var(--bg-panel)"

                st.markdown(
                    f"""
                    <div style="background:{bg}; border:1px solid {border};
                                border-left:3px solid {'#2E6B30' if is_active else 'transparent'};
                                padding:10px 12px; margin-bottom:6px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-family:var(--font-mono); font-weight:700; font-size:0.82rem; color:#6AA66C;">
                                {ev['evidence_id'].upper()}
                            </span>
                            <span style="font-size:0.65rem; color:var(--text-dim);">{ev['file_type']}</span>
                        </div>
                        <div style="font-size:0.82rem; color:var(--text-white); font-weight:600; margin-top:3px; letter-spacing:0.01em;">
                            {ev['file_name']}
                        </div>
                        <div style="font-family:var(--font-mono); font-size:0.66rem; color:var(--text-dim); margin-top:2px;">
                            {ev['doc_no']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Inspect Item →", key=f"btn_pick_ev_{ev['evidence_id']}", use_container_width=True):
                    st.session_state.selected_evidence_id = ev["evidence_id"]
                    st.rerun()

        st.markdown(
            "<hr style='border:none; border-top:1px solid #2A2A2A; margin:14px 0;'>",
            unsafe_allow_html=True,
        )

        if can("can_create"):
            with st.expander("+ Ingest Forensic Property Voucher", expanded=False):
                st.markdown(
                    """
                    <div style="background:rgba(200,16,46,0.06); border:1px solid var(--border-main);
                                padding:8px 10px; margin-bottom:12px; font-family:var(--font-mono);
                                font-size:0.64rem; color:var(--text-dim);">
                        ⚠ PROTOTYPE SIMULATION: Uploaded digital evidence files are held in-memory during the running session.
                        Cryptographic SHA-256 hashes are calculated for chain-of-custody simulation. Files are not persisted to physical disk.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Simulated file drop
                uploaded_file = st.file_uploader(
                    "Upload Exhibit File (Simulation)",
                    type=["pdf", "png", "jpg", "txt", "log", "pcap", "csv", "eml"],
                    key="ev_sim_uploader",
                )

                sim_file_name = uploaded_file.name if uploaded_file else "firewall_syslog_0901.log"
                sim_file_mime = uploaded_file.type if (uploaded_file and uploaded_file.type) else "text/plain"
                sim_hash = (
                    hashlib.sha256(uploaded_file.getvalue()).hexdigest()
                    if uploaded_file
                    else "3f786850e387550fdab836ed7e6dc881de23001b70e87038c013622150c3d33e"
                )

                with st.form("form_intake_ev_page"):
                    new_id   = st.text_input("Evidence ID", value=f"ev-{len(db.forensic_evidence)+1:03d}")
                    new_doc  = st.selectbox("Associated Docket", options=list(db.incident_dockets.keys()))
                    new_file = st.text_input("Filename", value=sim_file_name)
                    new_mime = st.selectbox(
                        "MIME Type",
                        ["text/plain", "application/pdf", "message/rfc822", "image/png", "text/csv", "application/octet-stream"],
                        index=["text/plain", "application/pdf", "message/rfc822", "image/png", "text/csv", "application/octet-stream"].index(sim_file_mime)
                        if sim_file_mime in ["text/plain", "application/pdf", "message/rfc822", "image/png", "text/csv", "application/octet-stream"] else 0,
                    )
                    new_hash = st.text_input("SHA-256 Checksum", value=sim_hash)
                    if st.form_submit_button("Commit to Locker", type="primary"):
                        try:
                            db.add_forensic_evidence(
                                evidence_id=new_id, doc_no=new_doc, file_name=new_file,
                                file_type=new_mime, file_path=f"/evidence/{new_doc.split('/')[-1]}/{new_file}",
                                sha_hash=new_hash, uploader_id=user["reg_id"] if user else "reg-002",
                            )
                            st.success("Evidence ingested into locker.")
                            st.session_state.selected_evidence_id = new_id
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

    # ── RIGHT: Evidence Item Detail ──
    with col_detail:
        ev = db.forensic_evidence.get(default_ev_id)
        if not ev:
            st.info("Select an evidence item from the locker.")
            return

        uploader = db.registrant_profiles.get(ev["uploader_id"], {})
        docket_info = db.incident_dockets.get(ev["doc_no"])

        # Property Voucher Card
        st.markdown(
            f"""
            <div style="background:var(--bg-panel); border:1px solid var(--border-main);
                        border-top:3px solid #2E6B30; padding:18px 20px; margin-bottom:16px;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <div style="font-family:var(--font-mono); font-size:0.56rem; text-transform:uppercase;
                                    letter-spacing:0.12em; color:var(--text-dim); margin-bottom:4px;">
                            SEIZED PROPERTY VOUCHER // STATUTORY EVIDENCE
                        </div>
                        <div style="font-family:var(--font-mono); font-size:1.05rem; font-weight:700; color:#6AA66C; margin-bottom:2px;">
                            {ev['evidence_id'].upper()}
                        </div>
                        <div style="font-family:var(--font-display); font-size:1.40rem; font-weight:800;
                                    color:var(--text-white); text-transform:uppercase; letter-spacing:0.02em;">
                            {ev['file_name']}
                        </div>
                        <div style="font-size:0.78rem; color:var(--text-secondary); margin-top:2px;">
                            {ev['file_type']}
                        </div>
                    </div>
                    <span class="badge badge-closed">CRYPTO VERIFIED</span>
                </div>
                <hr style="border:none; border-top:1px solid var(--border-subtle); margin:12px 0;">
                <div style="display:grid; grid-template-columns: repeat(3,1fr); gap:16px;">
                    <div>
                        <div class="jacket-field-label">Affiliated Docket</div>
                        <div style="font-family:var(--font-display); font-size:0.95rem; font-weight:800;
                                    color:var(--text-white); letter-spacing:0.03em; text-transform:uppercase; margin-top:2px;">
                            {ev['doc_no']}
                        </div>
                    </div>
                    <div>
                        <div class="jacket-field-label">Acquiring Officer</div>
                        <div class="jacket-field-val">{uploader.get('full_name', 'Unknown')} ({ev['uploader_id']})</div>
                    </div>
                    <div>
                        <div class="jacket-field-label">Secure Storage Path</div>
                        <div style="font-family:var(--font-mono); font-size:0.76rem; color:var(--text-secondary); margin-top:2px; word-break:break-all;">
                            {ev['file_path']}
                        </div>
                    </div>
                </div>
                <hr style="border:none; border-top:1px solid var(--border-subtle); margin:12px 0;">
                <div>
                    <div class="jacket-field-label" style="margin-bottom:5px;">SHA-256 Checksum Fingerprint (Char-64)</div>
                    <div style="background:var(--bg-secondary); border:1px solid var(--border-main);
                                padding:10px 14px; font-family:var(--font-mono); font-size:0.80rem;
                                color:var(--text-primary); word-break:break-all;">
                        {ev['sha_hash']}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_nav1, col_nav2 = st.columns([1, 1])
        with col_nav1:
            if st.button(f"Open Associated Case Jacket: {ev['doc_no']}", key=f"ev_open_doc_{ev['doc_no']}", use_container_width=True):
                st.session_state.selected_docket_id = ev["doc_no"]
                st.session_state.current_page = "Cases"
                st.rerun()

        # ── Cross-relational context: Suspects and Clusters on this Docket ──
        if docket_info:
            linked_suspect_links = [l for l in db.docket_suspect_links if l["doc_no"] == ev["doc_no"]]
            linked_clusters = [
                db.pattern_clusters[pl["cluster_id"]]
                for pl in db.docket_pattern_links
                if pl["doc_no"] == ev["doc_no"] and pl["cluster_id"] in db.pattern_clusters
            ]

            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            st.markdown(
                """
                <div class="section-label" style="margin-bottom:8px;">
                    Case Context: Attributed Targets &amp; Correlated Clusters
                </div>
                """,
                unsafe_allow_html=True,
            )

            col_cs, col_cp = st.columns(2)
            with col_cs:
                if not linked_suspect_links:
                    st.caption("No target entities linked to this case.")
                else:
                    for l in linked_suspect_links:
                        s = db.suspect_entities.get(l["suspect_id"])
                        if s:
                            st.markdown(
                                f"""
                                <div style="background:var(--bg-panel); border:1px solid var(--border-main);
                                            border-left:3px solid var(--red); padding:8px 10px; margin-bottom:6px; font-size:0.78rem;">
                                    <strong>{s['alias']}</strong> (TGT #{s['suspect_id']:04d})
                                    <div style="font-family:var(--font-mono); font-size:0.66rem; color:var(--text-dim);">
                                        Confidence: {int(l['conf_score']*100)}% &bull; IP: {s['ip_addr'] or 'Unresolved'}
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                            if st.button(f"Examine Target: {s['alias']}", key=f"ev_susp_btn_{s['suspect_id']}"):
                                st.session_state.selected_suspect_id = s["suspect_id"]
                                st.session_state.current_page = "Suspects"
                                st.rerun()

            with col_cp:
                if not linked_clusters:
                    st.caption("No syndicate clusters correlated to this case.")
                else:
                    for c in linked_clusters:
                        st.markdown(
                            f"""
                            <div style="background:var(--bg-panel); border:1px solid var(--border-main);
                                        border-left:3px solid var(--red); padding:8px 10px; margin-bottom:6px; font-size:0.78rem;">
                                <strong>{c['cluster_id'].upper()}</strong> &bull; {c['pattern_type']}
                                <div style="font-family:var(--font-mono); font-size:0.66rem; color:var(--text-dim);">
                                    Pivot: {c['pivot_val']} &bull; Risk: {c['risk_score']}/100
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        if st.button(f"Inspect Cluster: {c['cluster_id'].upper()}", key=f"ev_cl_btn_{c['cluster_id']}"):
                            st.session_state.selected_cluster_id = c["cluster_id"]
                            st.session_state.current_page = "Patterns"
                            st.rerun()

        # ── DELETE EVIDENCE (ADMIN ONLY) ──
        if can("can_delete"):
            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            with st.expander("⊠ Delete Evidence Record [ADMIN ONLY]", expanded=False):
                st.warning(
                    f"Remove exhibit **{ev['evidence_id'].upper()}** ({ev['file_name']}) permanently. "
                    "This cannot be undone during this session."
                )
                confirmed = st.checkbox("Confirm deletion.", key=f"confirm_del_ev_{ev['evidence_id']}")
                if confirmed and st.button("Delete Exhibit", key=f"del_ev_{ev['evidence_id']}", type="primary"):
                    db.delete_evidence(ev["evidence_id"], changed_by=user_name)
                    st.success("Evidence record deleted.")
                    st.session_state.pop("selected_evidence_id", None)
                    st.rerun()

        st.markdown(
            "<hr style='border:none; border-top:1px solid #2A2A2A; margin:16px 0;'>",
            unsafe_allow_html=True,
        )

        # Chain of Custody Audit Trail
        st.markdown(
            """
            <div style="margin-bottom:10px;">
                <div class="section-label">Chain of Custody Event Ledger [trg_evidence_after_insert]</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        custody_logs = [
            a for a in db.audit_logs
            if a["table_name"] == "ncrp_forensic_evidence"
            and (a["record_key"] == ev["evidence_id"] or ev["evidence_id"] in (a["new_value"] or ""))
        ]

        if not custody_logs:
            st.info("Initial intake log recorded in primary repository.")
        else:
            for log in custody_logs:
                time_str = log["changed_at"].strftime("%d %b %Y, %H:%M:%S")
                st.markdown(
                    f"""
                    <div style="background:var(--bg-panel); border:1px solid var(--border-main);
                                border-left:3px solid #2E6B30; padding:10px 14px; margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;
                                    font-family:var(--font-mono); font-size:0.70rem;">
                            <span>EVENT: <strong style="color:var(--text-white);">{log['action']}</strong></span>
                            <span style="color:var(--text-dim);">{time_str}</span>
                        </div>
                        <div style="font-size:0.80rem; color:var(--text-primary); margin-top:4px;">
                            Custodian: <strong>{log['changed_by']}</strong> &bull; Delta: {log['new_value']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
