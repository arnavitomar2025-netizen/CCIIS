"""
CCIIS — Subject Profiles & Attribution
BLACK / RED / WHITE editorial design.
Forensic target dossiers, communication channels, case attribution.
Role-based CRUD: INVESTIGATOR can add/edit; ADMIN can also delete.
"""

import streamlit as st
from data.mock_db import get_db
from auth import get_current_user, can
from components.ui_elements import render_editorial_header, render_status_tag


def render_suspects_page():
    db = get_db()
    user = get_current_user()
    user_name = user["full_name"] if user else "Officer"

    render_editorial_header(
        title="Subject Profiles & Attribution",
        description="Forensic intelligence dossiers on identified targets — digital aliases, communication channels, mule accounts, and case attribution records.",
        classification="CONFIDENTIAL // LAW ENFORCEMENT SENSITIVE",
    )

    all_suspects = list(db.suspect_entities.values())

    # ── Search & Filter Bar ──
    f1, f2 = st.columns([2, 1])
    with f1:
        search_query = st.text_input(
            "Search Targets",
            placeholder="Search by alias, MSISDN, IP address, mule account, or field notes...",
            label_visibility="collapsed",
            key="suspect_search_input",
        ).strip().lower()
    with f2:
        filter_type = st.selectbox(
            "Target Filter",
            ["All Targets", "With Linked Inquiries", "With Mule Bank Account", "With IP Resolved"],
            label_visibility="collapsed",
            key="suspect_filter_select",
        )

    # Apply search and filters
    filtered_suspects = all_suspects
    if search_query:
        filtered_suspects = [
            s for s in filtered_suspects
            if search_query in s.get("alias", "").lower()
            or (s.get("phone") and search_query in s["phone"].lower())
            or (s.get("ip_addr") and search_query in s["ip_addr"].lower())
            or (s.get("bank_acc") and search_query in s["bank_acc"].lower())
            or (s.get("trace_notes") and search_query in s["trace_notes"].lower())
        ]

    if filter_type == "With Linked Inquiries":
        linked_s_ids = {link["suspect_id"] for link in db.docket_suspect_links}
        filtered_suspects = [s for s in filtered_suspects if s["suspect_id"] in linked_s_ids]
    elif filter_type == "With Mule Bank Account":
        filtered_suspects = [s for s in filtered_suspects if s.get("bank_acc")]
    elif filter_type == "With IP Resolved":
        filtered_suspects = [s for s in filtered_suspects if s.get("ip_addr")]

    suspect_ids = [s["suspect_id"] for s in filtered_suspects]
    default_s_id = st.session_state.get("selected_suspect_id", 1)
    if default_s_id not in suspect_ids and suspect_ids:
        default_s_id = suspect_ids[0]

    col_selector, col_profile = st.columns([1.0, 2.4], gap="large")

    # ── LEFT: Target Pool ──
    with col_selector:
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <div class="section-label">Identified Subject Pool</div>
                <span style="font-family:var(--font-mono); font-size:0.60rem; color:var(--text-dim);">
                    {len(filtered_suspects)} OF {len(all_suspects)} MATCHED
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not filtered_suspects:
            st.info("No targets match the current query.")
        else:
            for s in filtered_suspects:
                is_active = s["suspect_id"] == default_s_id
                border = "#C8102E" if is_active else "var(--border-main)"
                bg = "var(--bg-elevated)" if is_active else "var(--bg-panel)"

                st.markdown(
                    f"""
                    <div style="background:{bg}; border:1px solid {border};
                                border-left:3px solid {'#C8102E' if is_active else 'transparent'};
                                padding:10px 12px; margin-bottom:6px;">
                        <div style="font-family:var(--font-display); font-weight:800; font-size:0.90rem;
                                    color:var(--text-white); text-transform:uppercase; letter-spacing:0.04em;">
                            {s['alias']}
                        </div>
                        <div style="font-family:var(--font-mono); font-size:0.68rem; color:var(--text-dim); margin-top:3px;">
                            TGT #{s['suspect_id']:04d} &bull; {s['ip_addr'] or 'NO IP'}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Examine Dossier →", key=f"btn_pick_s_{s['suspect_id']}", use_container_width=True):
                    st.session_state.selected_suspect_id = s["suspect_id"]
                    st.rerun()

        st.markdown(
            "<hr style='border:none; border-top:1px solid #2A2A2A; margin:14px 0;'>",
            unsafe_allow_html=True,
        )

        if can("can_create"):
            with st.expander("+ Ingest Target Subject Record", expanded=False):
                with st.form("form_add_new_suspect"):
                    new_alias = st.text_input("Alias / Identifier", value="Telegram Syndicate Operative")
                    new_phone = st.text_input("Primary Phone (MSISDN)", value="8555555555")
                    new_ip    = st.text_input("Originating IP Address", value="185.220.102.8")
                    new_bank  = st.text_input("Beneficiary Mule Account", value="ICIC0009988776")
                    new_notes = st.text_area("Field Intelligence Notes", value="Coordinating mule SIM swap transfers for phishing operations.")
                    if st.form_submit_button("Record Target", type="primary"):
                        if hasattr(db, "add_suspect"):
                            new_id = db.add_suspect(new_alias, new_phone, new_ip, new_bank, new_notes, user_name)
                        else:
                            new_id = (max(db.suspect_entities.keys()) + 1) if db.suspect_entities else 1
                            db.suspect_entities[new_id] = {
                                "suspect_id": new_id, "alias": new_alias,
                                "phone": new_phone or None, "ip_addr": new_ip or None,
                                "bank_acc": new_bank or None, "trace_notes": new_notes,
                            }
                            db._log_audit(
                                "ncrp_suspect_entity",
                                "INSERT",
                                str(new_id),
                                None,
                                f"alias={new_alias}",
                                user_name,
                            )
                        st.success(f"Target #{new_id:04d} recorded.")
                        st.session_state.selected_suspect_id = new_id
                        st.rerun()

    # ── RIGHT: Full Target Dossier ──
    with col_profile:
        s = db.suspect_entities.get(default_s_id)
        if not s:
            st.info("Select a target entity from the ledger.")
            return

        # Target Identification Record Header
        st.markdown(
            f"""
            <div class="jacket-header">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <div style="font-family:var(--font-mono); font-size:0.56rem; text-transform:uppercase;
                                    letter-spacing:0.12em; color:var(--text-dim); margin-bottom:4px;">
                            TARGET IDENTIFICATION RECORD // FORENSIC DOSSIER
                        </div>
                        <div class="jacket-case-num">{s['alias']}</div>
                        <div style="font-family:var(--font-mono); font-size:0.70rem; color:var(--text-dim); margin-top:3px;">
                            TGT #{s['suspect_id']:04d}
                        </div>
                    </div>
                    <span class="badge badge-investigation">UNDER INVESTIGATION</span>
                </div>
                <hr style="border:none; border-top:1px solid var(--border-subtle); margin:12px 0;">
                <div style="display:grid; grid-template-columns: repeat(3,1fr); gap:16px;">
                    <div>
                        <div class="jacket-field-label">Primary Phone (MSISDN)</div>
                        <div style="font-family:var(--font-mono); font-size:0.88rem; color:var(--text-white); font-weight:600; margin-top:2px;">
                            {s['phone'] or 'UNIDENTIFIED / SPOOFED'}
                        </div>
                    </div>
                    <div>
                        <div class="jacket-field-label">Originating IP Address</div>
                        <div style="font-family:var(--font-mono); font-size:0.88rem; color:var(--text-white); font-weight:600; margin-top:2px;">
                            {s['ip_addr'] or 'UNRESOLVED'}
                        </div>
                    </div>
                    <div>
                        <div class="jacket-field-label">Beneficiary Mule Account</div>
                        <div style="font-family:var(--font-mono); font-size:0.88rem; color:var(--text-white); font-weight:600; margin-top:2px;">
                            {s['bank_acc'] or 'NONE RECORDED'}
                        </div>
                    </div>
                </div>
                <hr style="border:none; border-top:1px solid var(--border-subtle); margin:12px 0;">
                <div>
                    <div class="jacket-field-label" style="margin-bottom:5px;">Field Intelligence Notes</div>
                    <div style="font-size:0.86rem; color:var(--text-primary); line-height:1.55;">
                        {s['trace_notes'] or 'No intelligence notes recorded for this entity.'}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Linked Case Inquiries
        st.markdown(
            """
            <div style="margin:16px 0 10px;">
                <div class="section-label">Linked Case Inquiries & Attribution Confidence [sp_suspect_cases]</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        associated_cases = db.sp_suspect_cases(s["suspect_id"])

        if not associated_cases:
            st.info("No cases currently linked to this target.")
        else:
            for c in associated_cases:
                conf_pct = int(c["conf_score"] * 100)
                conf_color = "#FF4D6A" if conf_pct > 75 else "#E0824A" if conf_pct > 50 else "var(--text-secondary)"
                st.markdown(
                    f"""
                    <div style="background:var(--bg-panel); border:1px solid var(--border-main);
                                border-left:3px solid var(--red); padding:12px 16px; margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <span style="font-family:var(--font-display); font-weight:800; font-size:1.0rem;
                                             color:var(--text-white); text-transform:uppercase; letter-spacing:0.04em;">
                                    {c['doc_no']}
                                </span>
                                <span style="margin-left:10px; font-size:0.82rem; color:var(--text-secondary);">
                                    {c['crime_type']}
                                </span>
                            </div>
                            {render_status_tag(c['stage_code'])}
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center;
                                    margin-top:8px; font-size:0.80rem;">
                            <span style="color:var(--text-secondary);">
                                Loss: <strong style="color:var(--text-primary);">₹{c['loss_amt']:,.0f}</strong>
                            </span>
                            <span style="font-family:var(--font-mono); font-size:0.70rem;">
                                <span style="color:var(--text-dim);">CONFIDENCE:</span>
                                <strong style="color:{conf_color}; margin-left:4px;">{c['conf_score']:.2f} ({conf_pct}%)</strong>
                            </span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(f"Open Case Jacket: {c['doc_no']}", key=f"s_open_case_{c['doc_no']}"):
                    st.session_state.selected_docket_id = c["doc_no"]
                    st.session_state.current_page = "Cases"
                    st.rerun()

        # ── Link Target to Case Docket [sp_link_suspect] ──
        if can("can_create") or can("can_edit"):
            with st.expander("+ Link Target to Case Docket [sp_link_suspect]", expanded=False):
                with st.form(f"form_link_target_docket_{s['suspect_id']}"):
                    all_doc_keys = list(db.incident_dockets.keys())
                    target_doc = st.selectbox(
                        "Select Case Docket",
                        options=all_doc_keys,
                        format_func=lambda x: f"{x} — {db.incident_dockets[x]['crime_type']} (₹{db.incident_dockets[x]['loss_amt']:,.0f})",
                    )
                    conf_level = st.slider("Attribution Confidence", 0.1, 1.0, 0.85, 0.05)
                    if st.form_submit_button("Link Target to Docket", type="primary"):
                        try:
                            db.sp_link_suspect(target_doc, s["suspect_id"], conf_level)
                            st.success(f"Target #{s['suspect_id']:04d} linked to {target_doc} with confidence {conf_level:.2f}.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

        # ── Correlated Evidence & Pattern Clusters (Case -> Suspect -> Evidence -> Cluster loop) ──
        if associated_cases:
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            with st.expander("◫ Correlated Seized Evidence & Syndicate Infrastructure", expanded=False):
                associated_doc_nos = {c["doc_no"] for c in associated_cases}
                rel_evidence = [ev for ev in db.forensic_evidence.values() if ev["doc_no"] in associated_doc_nos]
                rel_clusters = [
                    db.pattern_clusters[pl["cluster_id"]]
                    for pl in db.docket_pattern_links
                    if pl["doc_no"] in associated_doc_nos and pl["cluster_id"] in db.pattern_clusters
                ]

                col_ce, col_cp = st.columns(2)
                with col_ce:
                    st.markdown("<div class='section-label' style='margin-bottom:6px;'>Associated Evidence Exhibits</div>", unsafe_allow_html=True)
                    if not rel_evidence:
                        st.caption("No evidence items attached to linked cases.")
                    else:
                        for rev in rel_evidence:
                            st.markdown(
                                f"""
                                <div style="background:var(--bg-panel); border:1px solid var(--border-main);
                                            border-left:3px solid #58705A; padding:8px 10px; margin-bottom:6px; font-size:0.78rem;">
                                    <strong>{rev['evidence_id'].upper()}</strong> &bull; {rev['file_name']}
                                    <div style="font-family:var(--font-mono); font-size:0.65rem; color:var(--text-dim); margin-top:2px;">
                                        Case: {rev['doc_no']}
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                            if st.button(f"Inspect Exhibit {rev['evidence_id'].upper()}", key=f"s_rev_{rev['evidence_id']}"):
                                st.session_state.selected_evidence_id = rev["evidence_id"]
                                st.session_state.current_page = "Evidence"
                                st.rerun()

                with col_cp:
                    st.markdown("<div class='section-label' style='margin-bottom:6px;'>Correlated Syndicate Clusters</div>", unsafe_allow_html=True)
                    if not rel_clusters:
                        st.caption("No syndicate clusters attached to linked cases.")
                    else:
                        for i, rcl in enumerate(rel_clusters):
                            st.markdown(
                                f"""
                                <div style="background:var(--bg-panel); border:1px solid var(--border-main);
                                            border-left:3px solid var(--red); padding:8px 10px; margin-bottom:6px; font-size:0.78rem;">
                                    <strong>{rcl['cluster_id'].upper()}</strong> &bull; {rcl['pattern_type']}
                                    <div style="font-family:var(--font-mono); font-size:0.65rem; color:var(--text-dim); margin-top:2px;">
                                        Pivot: {rcl['pivot_val']} &bull; Risk: {rcl['risk_score']}/100
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                            if st.button(f"Inspect Cluster {rcl['cluster_id'].upper()}", key=f"s_rcl_{rcl['cluster_id']}_{i}"):
                                st.session_state.selected_cluster_id = rcl["cluster_id"]
                                st.session_state.current_page = "Patterns"
                                st.rerun()

        # ── EDIT SUSPECT (INVESTIGATOR / ADMIN) ──
        if can("can_edit"):
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            with st.expander("✎ Edit Subject Record", expanded=False):
                with st.form(f"form_edit_suspect_{s['suspect_id']}"):
                    up_alias = st.text_input("Alias / Identifier", value=s["alias"])
                    up_phone = st.text_input("Primary Phone", value=s["phone"] or "")
                    up_ip    = st.text_input("Originating IP",  value=s["ip_addr"] or "")
                    up_bank  = st.text_input("Mule Account",    value=s["bank_acc"] or "")
                    up_notes = st.text_area("Field Intelligence Notes", value=s["trace_notes"] or "")
                    if st.form_submit_button("Update Record", type="primary"):
                        try:
                            db.update_suspect(
                                suspect_id=s["suspect_id"],
                                alias=up_alias, phone=up_phone, ip_addr=up_ip,
                                bank_acc=up_bank, trace_notes=up_notes, changed_by=user_name,
                            )
                            st.success("Subject record updated.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

        # ── DELETE SUSPECT (ADMIN ONLY) ──
        if can("can_delete"):
            st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
            with st.expander("⊠ Delete Subject [ADMIN ONLY]", expanded=False):
                st.warning(
                    f"Remove **{s['alias']}** (TGT #{s['suspect_id']:04d}) and all docket links. "
                    "This cannot be undone during this session."
                )
                confirmed = st.checkbox("Confirm deletion.", key=f"confirm_del_susp_{s['suspect_id']}")
                if confirmed and st.button("Delete Subject", key=f"del_susp_{s['suspect_id']}", type="primary"):
                    db.delete_suspect(s["suspect_id"], changed_by=user_name)
                    st.success("Subject record deleted.")
                    st.session_state.pop("selected_suspect_id", None)
                    st.rerun()
