"""
CCIIS — Syndicate Infrastructure & Patterns
BLACK / RED / WHITE editorial design.
Cross-docket correlation of organized cybercrime infrastructure.
Role-based: INVESTIGATOR can correlate/create; ADMIN can delete.
"""

import streamlit as st
from data.mock_db import get_db
from auth import get_current_user, can
from components.ui_elements import render_editorial_header, render_status_tag


def render_patterns_page():
    db = get_db()
    user = get_current_user()
    user_name = user["full_name"] if user else "Officer"

    render_editorial_header(
        title="Syndicate Infrastructure & Patterns",
        description="Cross-docket correlation of organized cybercrime syndicates sharing common digital and financial infrastructure — IP pivots, mule bank networks, and communication channels.",
        classification="CONFIDENTIAL // LAW ENFORCEMENT SENSITIVE",
    )

    clusters_view = db.get_vw_pattern_summary()

    # ── Filter / Search Bar ──
    f1, f2 = st.columns([2, 1])
    with f1:
        search_query = st.text_input(
            "Search Clusters",
            placeholder="Search by Cluster ID, pattern type, or infrastructure pivot...",
            label_visibility="collapsed",
            key="pattern_search_input",
        ).strip().lower()
    with f2:
        pattern_types = ["All Types"] + sorted(list({c["pattern_type"] for c in clusters_view}))
        filter_type = st.selectbox("Pattern Type", pattern_types, label_visibility="collapsed", key="pat_type_select")

    filtered_clusters = clusters_view
    if search_query:
        filtered_clusters = [
            c for c in filtered_clusters
            if search_query in c["cluster_id"].lower()
            or search_query in c["pattern_type"].lower()
            or search_query in c["pivot_val"].lower()
        ]
    if filter_type != "All Types":
        filtered_clusters = [c for c in filtered_clusters if c["pattern_type"] == filter_type]

    cl_ids = [c["cluster_id"] for c in filtered_clusters]
    default_cl_id = st.session_state.get("selected_cluster_id", "cl-001")
    if default_cl_id not in cl_ids and cl_ids:
        default_cl_id = cl_ids[0]

    col_list, col_detail = st.columns([1.0, 2.4], gap="large")

    # ── LEFT: Cluster List ──
    with col_list:
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <div class="section-label">Identified Clusters</div>
                <span style="font-family:var(--font-mono); font-size:0.60rem; color:var(--text-dim);">
                    {len(filtered_clusters)} OF {len(clusters_view)} ACTIVE
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not filtered_clusters:
            st.info("No clusters match the search query.")
        else:
            for c in filtered_clusters:
                is_active = c["cluster_id"] == default_cl_id
                border = "#C8102E" if is_active else "var(--border-main)"
                bg = "var(--bg-elevated)" if is_active else "var(--bg-panel)"

                st.markdown(
                    f"""
                    <div style="background:{bg}; border:1px solid {border};
                                border-left:3px solid {'#C8102E' if is_active else 'transparent'};
                                padding:10px 12px; margin-bottom:6px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-family:var(--font-mono); font-weight:700; font-size:0.80rem; color:var(--text-white);">
                                {c['cluster_id'].upper()}
                            </span>
                            <span class="risk-score">RISK {c['risk_score']}/100</span>
                        </div>
                        <div style="font-family:var(--font-display); font-size:0.90rem; font-weight:700;
                                    color:var(--text-white); text-transform:uppercase; letter-spacing:0.04em; margin-top:3px;">
                            {c['pattern_type'].replace('_', ' ')}
                        </div>
                        <div style="font-family:var(--font-mono); font-size:0.68rem; color:var(--text-dim); margin-top:3px;">
                            Pivot: {c['pivot_val']} &bull; {c['linked_dockets']} cases
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Inspect Cluster →", key=f"btn_pick_cl_{c['cluster_id']}", use_container_width=True):
                    st.session_state.selected_cluster_id = c["cluster_id"]
                    st.rerun()

        st.markdown(
            "<hr style='border:none; border-top:1px solid #2A2A2A; margin:14px 0;'>",
            unsafe_allow_html=True,
        )

        # Correlate Case to Cluster
        if can("can_create") or can("can_edit"):
            with st.expander("+ Correlate Case Docket [trg_pattern_link]", expanded=False):
                with st.form("form_link_case_cluster_page"):
                    target_doc = st.selectbox("Case Docket", options=list(db.incident_dockets.keys()))
                    all_cl_keys = list(db.pattern_clusters.keys())
                    target_cl = st.selectbox(
                        "Cluster",
                        options=all_cl_keys,
                        format_func=lambda x: f"{x.upper()} ({db.pattern_clusters[x]['pattern_type']} — {db.pattern_clusters[x]['pivot_val']})",
                    )
                    if st.form_submit_button("Correlate Case", type="primary"):
                        db.link_docket_pattern(target_doc, target_cl)
                        st.success("Case correlated to cluster. Risk score incremented.")
                        st.session_state.selected_cluster_id = target_cl
                        st.rerun()

            # Create New Cluster
            with st.expander("+ Register New Infrastructure Pivot", expanded=False):
                with st.form("form_create_cluster"):
                    new_cl_id = st.text_input("Cluster ID", value=f"cl-{len(db.pattern_clusters)+1:03d}")
                    new_cl_type = st.selectbox("Pattern Type", ["SHARED_IP", "SHARED_BANK", "SHARED_TELECOM", "SHARED_DOMAINS"])
                    new_cl_pivot = st.text_input("Infrastructure Pivot Identifier", value="194.26.29.112")
                    new_cl_risk = st.slider("Initial Risk Score", 10, 100, 50, 5)
                    if st.form_submit_button("Register Cluster", type="primary"):
                        try:
                            db.add_pattern_cluster(new_cl_id, new_cl_type, new_cl_pivot, new_cl_risk, user_name)
                            st.success(f"Cluster {new_cl_id.upper()} registered.")
                            st.session_state.selected_cluster_id = new_cl_id
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

    # ── RIGHT: Cluster Detail ──
    with col_detail:
        cluster_info = next((c for c in clusters_view if c["cluster_id"] == default_cl_id), None)
        if not cluster_info:
            st.info("Select a pattern cluster from the left panel.")
            return

        # Cluster Intelligence Card
        risk_color = "#FF4D6A" if cluster_info["risk_score"] > 70 else "#E0824A" if cluster_info["risk_score"] > 40 else "var(--text-secondary)"
        st.markdown(
            f"""
            <div class="jacket-header">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <div style="font-family:var(--font-mono); font-size:0.56rem; text-transform:uppercase;
                                    letter-spacing:0.12em; color:var(--text-dim); margin-bottom:4px;">
                            SYNDICATE PATTERN CLUSTER // INFRASTRUCTURE NODE
                        </div>
                        <div style="font-family:var(--font-mono); font-size:0.75rem; font-weight:700;
                                    color:var(--red); margin-bottom:2px;">
                            {cluster_info['cluster_id'].upper()}
                        </div>
                        <div class="jacket-case-num">{cluster_info['pattern_type'].replace('_', ' ')}</div>
                        <div style="font-family:var(--font-mono); font-size:0.80rem; color:var(--text-secondary); margin-top:4px;">
                            Infrastructure Pivot: <span style="color:var(--text-white); font-weight:600;">
                                {cluster_info['pivot_val']}
                            </span>
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-family:var(--font-mono); font-size:0.65rem; color:var(--text-dim); margin-bottom:3px; text-transform:uppercase;">
                            SEVERITY RISK SCORE
                        </div>
                        <div style="font-family:var(--font-display); font-size:2.2rem; font-weight:900;
                                    color:{risk_color}; line-height:1;">
                            {cluster_info['risk_score']}
                        </div>
                        <div style="font-family:var(--font-mono); font-size:0.58rem; color:var(--text-dim);">/ 100</div>
                    </div>
                </div>
                <hr style="border:none; border-top:1px solid var(--border-subtle); margin:12px 0;">
                <div style="display:grid; grid-template-columns: repeat(2,1fr); gap:16px;">
                    <div>
                        <div class="jacket-field-label">Connected Inquiries</div>
                        <div style="font-family:var(--font-display); font-size:1.40rem; font-weight:800;
                                    color:var(--text-white); letter-spacing:0.02em; margin-top:2px;">
                            {cluster_info['linked_dockets']} CASES
                        </div>
                    </div>
                    <div>
                        <div class="jacket-field-label">Total Syndicate Fraud Value</div>
                        <div style="font-family:var(--font-display); font-size:1.40rem; font-weight:800;
                                    color:var(--text-white); letter-spacing:0.02em; margin-top:2px;">
                            ₹{cluster_info['total_loss']:,.0f}
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Correlated Dockets
        st.markdown(
            """
            <div style="margin:16px 0 10px;">
                <div class="section-label">Correlated Incident Dockets &amp; Cross-Case Attribution [vw_pattern_summary]</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        linked_docs = cluster_info["linked_doc_list"]
        if not linked_docs:
            st.info("No cases currently linked to this cluster.")
        else:
            for doc_no in linked_docs:
                d = db.incident_dockets.get(doc_no)
                if d:
                    # Find suspects attributed to this correlated case
                    case_suspects = [
                        db.suspect_entities[l["suspect_id"]]["alias"]
                        for l in db.docket_suspect_links
                        if l["doc_no"] == doc_no and l["suspect_id"] in db.suspect_entities
                    ]
                    susp_str = ", ".join(case_suspects) if case_suspects else "None attributed yet"

                    st.markdown(
                        f"""
                        <div style="background:var(--bg-panel); border:1px solid var(--border-main);
                                    border-left:3px solid var(--red); padding:12px 16px; margin-bottom:8px;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <div>
                                    <span style="font-family:var(--font-display); font-weight:800; font-size:1.0rem;
                                                 color:var(--text-white); text-transform:uppercase; letter-spacing:0.04em;">
                                        {d['doc_no']}
                                    </span>
                                    <span style="margin-left:10px; font-size:0.80rem; color:var(--text-secondary);">
                                        {d['crime_type']}
                                    </span>
                                </div>
                                {render_status_tag(d['stage_code'])}
                            </div>
                            <div style="font-family:var(--font-mono); font-size:0.72rem; color:var(--text-secondary); margin-top:6px;">
                                Loss: <strong style="color:var(--text-primary);">₹{d['loss_amt']:,.0f}</strong>
                                &bull; Filed: {d['filed_dt'].strftime('%d %b %Y')}
                                &bull; Attributed Targets: <span style="color:var(--text-white);">{susp_str}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button(f"Open Case Jacket: {d['doc_no']}", key=f"pat_open_doc_{d['doc_no']}"):
                        st.session_state.selected_docket_id = d["doc_no"]
                        st.session_state.current_page = "Cases"
                        st.rerun()

        # ── DELETE CLUSTER (ADMIN ONLY) ──
        if can("can_delete"):
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            with st.expander("⊠ Delete Syndicate Cluster [ADMIN ONLY]", expanded=False):
                st.warning(
                    f"Remove cluster **{cluster_info['cluster_id'].upper()}** and disconnect all dockets. "
                    "This cannot be undone during this session."
                )
                confirmed = st.checkbox("Confirm deletion.", key=f"confirm_del_cl_{cluster_info['cluster_id']}")
                if confirmed and st.button("Delete Cluster", key=f"del_cl_{cluster_info['cluster_id']}", type="primary"):
                    db.delete_pattern_cluster(cluster_info["cluster_id"], changed_by=user_name)
                    st.success("Cluster deleted.")
                    st.session_state.pop("selected_cluster_id", None)
                    st.rerun()

        st.markdown(
            "<hr style='border:none; border-top:1px solid #2A2A2A; margin:16px 0;'>",
            unsafe_allow_html=True,
        )

        # Pattern analysis explanation
        st.markdown(
            """
            <div style="margin-bottom:6px;">
                <div class="section-label">Investigative Purpose of Pattern Correlation</div>
            </div>
            <div style="background:var(--bg-secondary); border:1px solid var(--border-main);
                        border-left:3px solid var(--red); padding:14px 18px; line-height:1.6;
                        font-size:0.84rem; color:var(--text-secondary);">
                In high-volume cyber fraud, independent complaints are filed by unrelated victims across
                jurisdictions. The relational junction table
                <code style="color:var(--text-primary); font-size:0.78rem;">ncrp_docket_pattern_link</code>
                detects convergence upon single syndicates by matching originating IP hops and beneficiary
                mule bank accounts. The trigger
                <code style="color:var(--text-primary); font-size:0.78rem;">trg_pattern_link_after_insert</code>
                auto-increments the cluster risk score on each new association.
            </div>
            """,
            unsafe_allow_html=True,
        )
