"""
CCIIS — Dashboard / Central Incident Register
BLACK / RED / WHITE editorial design.
Five Plotly charts + KPI strip + case stream + intel panel.
All chart data derived from the same mock_db dataset as the tables.
"""

from collections import defaultdict
import streamlit as st
import plotly.graph_objects as go
from data.mock_db import get_db
from auth import get_current_user
from components.ui_elements import render_editorial_header, render_status_tag, render_severity_tag
from utils.formatters import fmt_inr, fmt_date, compute_severity

# ── Shared Plotly theme for black/red/white identity ──
PLOT_BG     = "#0A0A0A"
PAPER_BG    = "#111111"
GRID_COLOR  = "#2A2A2A"
TEXT_COLOR  = "#F0EDE8"
RED         = "#C8102E"
RED_MUTED   = "#7A1020"
MUTED_WHITE = "#8A8480"
GREEN       = "#2E6B30"
ORANGE      = "#CC5500"

def _apply_theme(fig: go.Figure, title: str, **kwargs) -> go.Figure:
    """Applies the institutional Black/Red/White Plotly theme without keyword collisions."""
    layout_args = dict(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(family="IBM Plex Mono, monospace", color=TEXT_COLOR, size=11),
        margin=dict(l=10, r=10, t=36, b=10),
        showlegend=False,
        title=dict(text=title, font=dict(size=11, color=MUTED_WHITE), x=0),
    )
    layout_args.update(kwargs)
    fig.update_layout(**layout_args)
    fig.update_xaxes(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    return fig


STAGE_BAR_COLORS = {
    "INVESTIGATION": RED,
    "TRIAGE":        ORANGE,
    "LOGGED":        "#383838",
    "CLOSED":        GREEN,
}


def _chart_cases_by_stage(dockets: list[dict]) -> go.Figure:
    """Chart 1 — Case counts grouped by stage."""
    counts = defaultdict(int)
    for d in dockets:
        counts[d["stage_code"]] += 1
    stage_order = ["TRIAGE", "LOGGED", "INVESTIGATION", "CLOSED"]
    stages = [s for s in stage_order if s in counts]
    if not stages:
        stages = ["NO DATA"]
        values = [0]
        colors = [MUTED_WHITE]
    else:
        values = [counts[s] for s in stages]
        colors = [STAGE_BAR_COLORS.get(s, MUTED_WHITE) for s in stages]

    fig = go.Figure(go.Bar(
        x=stages, y=values, marker_color=colors,
        text=values, textposition="outside", textfont=dict(color=TEXT_COLOR, size=12),
    ))
    return _apply_theme(fig, "CASES BY STAGE", bargap=0.38)


def _chart_loss_by_crime(dockets: list[dict]) -> go.Figure:
    """Chart 2 — Total recorded loss grouped by crime type, sorted highest first."""
    totals = defaultdict(float)
    for d in dockets:
        if d["loss_amt"] > 0:
            totals[d["crime_type"]] += d["loss_amt"]
    if not totals:
        totals["No Data"] = 0
    sorted_items = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    crime_types = [i[0] for i in sorted_items]
    losses = [i[1] for i in sorted_items]

    bar_colors = [RED if i == 0 else RED_MUTED if i == 1 else MUTED_WHITE for i in range(len(crime_types))]

    fig = go.Figure(go.Bar(
        x=crime_types, y=losses, marker_color=bar_colors,
        text=[fmt_inr(v, compact=True) for v in losses],
        textposition="outside", textfont=dict(color=TEXT_COLOR, size=10),
    ))
    _apply_theme(fig, "LOSS BY CRIME TYPE (₹)", bargap=0.38)
    fig.update_yaxes(tickformat=",.0f", tickprefix="₹")
    return fig


def _chart_cases_per_month(dockets: list[dict]) -> go.Figure:
    """Chart 3 — Monthly case counts using actual filing dates. Chronological."""
    from datetime import datetime
    monthly = defaultdict(int)
    for d in dockets:
        dt = d.get("filed_dt")
        if isinstance(dt, str):
            try:
                dt = datetime.strptime(dt[:19], "%Y-%m-%d %H:%M:%S")
            except Exception:
                try:
                    dt = datetime.strptime(dt[:10], "%Y-%m-%d")
                except Exception:
                    dt = None
        if dt and hasattr(dt, "strftime"):
            month_key = dt.strftime("%Y-%m")
            monthly[month_key] += 1
    if not monthly:
        fig = go.Figure()
        return _apply_theme(fig, "CASES PER MONTH")

    sorted_months = sorted(monthly.keys())
    labels = [m[5:] + "/" + m[2:4] for m in sorted_months]  # MM/YY display
    values = [monthly[m] for m in sorted_months]

    fig = go.Figure(go.Scatter(
        x=labels, y=values, mode="lines+markers+text",
        line=dict(color=RED, width=2),
        marker=dict(color=RED, size=8, symbol="square"),
        text=values, textposition="top center",
        textfont=dict(color=TEXT_COLOR, size=11),
    ))
    _apply_theme(fig, "CASES PER MONTH")
    fig.update_yaxes(tickformat="d", dtick=1)
    return fig


def _chart_repeat_suspects(db) -> go.Figure:
    """Chart 4 — Suspects linked to more than one distinct case."""
    case_count = defaultdict(set)
    for link in db.docket_suspect_links:
        sid = link.get("suspect_id")
        doc = link.get("doc_no")
        if sid is not None and doc:
            try:
                case_count[int(sid)].add(doc)
            except Exception:
                case_count[sid].add(doc)

    repeat = {sid: cases for sid, cases in case_count.items() if len(cases) > 1}
    if not repeat:
        repeat = dict(case_count)

    aliases = []
    counts = []
    for sid, cases in repeat.items():
        s = db.suspect_entities.get(sid)
        if not s:
            try:
                s = db.suspect_entities.get(int(sid))
            except Exception:
                pass
        if s:
            aliases.append(s.get("alias", f"TGT #{sid}"))
            counts.append(len(cases))

    colors = [RED if c >= 3 else ORANGE if c == 2 else MUTED_WHITE for c in counts]

    if not aliases:
        fig = go.Figure()
        return _apply_theme(fig, "REPEAT SUSPECTS — CASE COUNT")

    fig = go.Figure(go.Bar(
        y=aliases, x=counts, orientation="h",
        marker_color=colors, text=counts,
        textposition="outside", textfont=dict(color=TEXT_COLOR, size=11),
    ))
    _apply_theme(fig, "REPEAT SUSPECTS — CASE COUNT", bargap=0.30, margin=dict(l=110, r=20, t=36, b=10))
    fig.update_xaxes(tickformat="d", dtick=1)
    fig.update_yaxes(autorange="reversed")
    return fig


def _chart_cluster_risk(db) -> go.Figure:
    """Chart 5 — Pattern cluster risk scores with linked case counts."""
    patterns = db.get_vw_pattern_summary()
    if not patterns:
        fig = go.Figure()
        return _apply_theme(fig, "PATTERN CLUSTER RISK & LINKED CASES")

    labels       = [f"{p['cluster_id'].upper()}<br>{p['pattern_type'].replace('_', ' ')}" for p in patterns]
    risk_scores  = [p["risk_score"] for p in patterns]
    case_counts  = [p["linked_dockets"] for p in patterns]
    bar_colors   = [RED if r >= 70 else ORANGE if r >= 40 else MUTED_WHITE for r in risk_scores]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Risk Score", x=labels, y=risk_scores,
        marker_color=bar_colors, text=[f"{r}/100" for r in risk_scores],
        textposition="inside", textfont=dict(color="white", size=11),
        yaxis="y",
    ))
    fig.add_trace(go.Scatter(
        name="Linked Cases", x=labels, y=case_counts,
        mode="markers+text", marker=dict(color="white", size=14, symbol="diamond"),
        text=case_counts, textposition="top center",
        textfont=dict(color=TEXT_COLOR, size=11), yaxis="y2",
    ))
    max_cases = max(case_counts) if case_counts else 1
    _apply_theme(
        fig,
        "PATTERN CLUSTER RISK & LINKED CASES",
        showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED_WHITE, size=10)),
        bargap=0.40,
        yaxis=dict(
            title="Risk Score", gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
            range=[0, 110], tickformat="d",
        ),
        yaxis2=dict(
            title="Linked Cases", overlaying="y", side="right",
            gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
            range=[0, max_cases + 2], tickformat="d",
        ),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────


def render_dashboard_page():
    db = get_db()
    user = get_current_user()

    render_editorial_header(
        title="Central Incident Register",
        description="Cyber crime docket ledger, digital evidence intake, and syndicate pattern correlation. All inquiry data is classified law enforcement sensitive.",
        classification="CONFIDENTIAL // LAW ENFORCEMENT SENSITIVE",
    )

    all_dockets = list(db.incident_dockets.values())

    # ── Interactive Filter Strip ──
    flt_col1, flt_col2, flt_col3 = st.columns([1.5, 1.5, 1])
    with flt_col1:
        stage_filter = st.selectbox(
            "Filter by Stage",
            ["All Stages", "INVESTIGATION", "TRIAGE", "LOGGED", "CLOSED"],
            label_visibility="collapsed",
            key="dash_stage_flt",
        )
    with flt_col2:
        crime_filter = st.selectbox(
            "Filter by Crime Category",
            ["All Categories"] + sorted(list({d["crime_type"] for d in all_dockets})),
            label_visibility="collapsed",
            key="dash_crime_flt",
        )
    with flt_col3:
        if stage_filter != "All Stages" or crime_filter != "All Categories":
            if st.button("↺ Reset Filters", use_container_width=True):
                st.session_state.dash_stage_flt = "All Stages"
                st.session_state.dash_crime_flt = "All Categories"
                st.rerun()

    # Filtered dockets
    filtered_dockets = all_dockets
    if stage_filter != "All Stages":
        filtered_dockets = [d for d in filtered_dockets if d["stage_code"] == stage_filter]
    if crime_filter != "All Categories":
        filtered_dockets = [d for d in filtered_dockets if d["crime_type"] == crime_filter]

    # ── KPI Strip (Dynamic based on filters) ──
    active_cnt  = sum(1 for d in filtered_dockets if d["stage_code"] == "INVESTIGATION")
    triage_cnt  = sum(1 for d in filtered_dockets if d["stage_code"] == "TRIAGE")
    closed_cnt  = sum(1 for d in filtered_dockets if d["stage_code"] == "CLOSED")
    total_loss  = sum(d["loss_amt"] for d in filtered_dockets)
    filtered_doc_nos = {d["doc_no"] for d in filtered_dockets}
    total_evid  = sum(1 for ev in db.forensic_evidence.values() if ev["doc_no"] in filtered_doc_nos)
    
    # Linked suspects in filtered cases
    filtered_suspect_ids = {
        l["suspect_id"] for l in db.docket_suspect_links if l["doc_no"] in filtered_doc_nos
    }
    total_susp = len(filtered_suspect_ids)

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1: st.metric("Active Inquiries",  f"{active_cnt:02d}")
    with k2: st.metric("Under Triage",      f"{triage_cnt:02d}")
    with k3: st.metric("Disposed",          f"{closed_cnt:02d}")
    with k4: st.metric("Fraud Value",       fmt_inr(total_loss, compact=True))
    with k5: st.metric("Seized Exhibits",   f"{total_evid:02d}")
    with k6: st.metric("Target Entities",   f"{total_susp:02d}")

    st.markdown("<hr style='border:none; border-top:1px solid #2A2A2A; margin:20px 0;'>", unsafe_allow_html=True)

    # ── Row 1: Chart 1 + Chart 2 ──
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.plotly_chart(_chart_cases_by_stage(filtered_dockets), use_container_width=True, config={"displayModeBar": False})
    with c2:
        st.plotly_chart(_chart_loss_by_crime(filtered_dockets), use_container_width=True, config={"displayModeBar": False})

    # ── Row 2: Chart 3 + Chart 4 ──
    c3, c4 = st.columns(2, gap="medium")
    with c3:
        st.plotly_chart(_chart_cases_per_month(filtered_dockets), use_container_width=True, config={"displayModeBar": False})
    with c4:
        st.plotly_chart(_chart_repeat_suspects(db), use_container_width=True, config={"displayModeBar": False})

    # Repeat Suspects Drilldown Drawer
    repeat_map = defaultdict(set)
    for link in db.docket_suspect_links:
        repeat_map[link["suspect_id"]].add(link["doc_no"])
    repeat_ids = [sid for sid, cases in repeat_map.items() if len(cases) > 1 and sid in db.suspect_entities]

    if repeat_ids:
        with st.expander("🔍 Inspect Repeat Target Subjects & Linked Inquiries", expanded=False):
            sel_repeat_sid = st.selectbox(
                "Select Repeat Target Subject",
                options=repeat_ids,
                format_func=lambda sid: f"{db.suspect_entities[sid]['alias']} — {len(repeat_map[sid])} DISTINCT CASES",
                key="dash_repeat_inspect_sel",
            )
            if sel_repeat_sid:
                rs = db.suspect_entities[sel_repeat_sid]
                st.markdown(
                    f"""
                    <div style="font-family:var(--font-mono); font-size:0.75rem; color:var(--text-secondary); margin-bottom:8px;">
                        TGT #{rs['suspect_id']:04d} &bull; MSISDN: {rs['phone'] or 'Unresolved'} &bull; IP: {rs['ip_addr'] or 'Unresolved'}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                col_cases = st.columns(len(repeat_map[sel_repeat_sid]))
                for idx, doc_no in enumerate(sorted(repeat_map[sel_repeat_sid])):
                    doc_obj = db.incident_dockets.get(doc_no)
                    with col_cases[idx]:
                        if doc_obj:
                            st.markdown(
                                f"""
                                <div style="background:var(--bg-panel); border:1px solid var(--border-main);
                                            border-left:3px solid var(--red); padding:8px 10px; margin-bottom:6px; font-size:0.76rem;">
                                    <strong>{doc_no}</strong><br>
                                    {doc_obj['crime_type']}<br>
                                    Loss: ₹{doc_obj['loss_amt']:,.0f}
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                            if st.button(f"Open {doc_no}", key=f"rpt_btn_{sel_repeat_sid}_{doc_no}", use_container_width=True):
                                st.session_state.selected_docket_id = doc_no
                                st.session_state.current_page = "Cases"
                                st.rerun()

                if st.button(f"Examine Full Target Dossier ({rs['alias']})", key=f"rpt_dossier_{sel_repeat_sid}"):
                    st.session_state.selected_suspect_id = sel_repeat_sid
                    st.session_state.current_page = "Suspects"
                    st.rerun()

    # ── Row 3: Chart 5 (full width) ──
    st.plotly_chart(_chart_cluster_risk(db), use_container_width=True, config={"displayModeBar": False})

    # Cluster Relationship Inspector Drawer
    all_clusters = db.get_vw_pattern_summary()
    if all_clusters:
        with st.expander("🔍 Inspect Syndicate Cluster Relationships & Connected Complaints", expanded=False):
            sel_cluster_id = st.selectbox(
                "Select Syndicate Cluster",
                options=[c["cluster_id"] for c in all_clusters],
                format_func=lambda cid: f"{cid.upper()} — {db.pattern_clusters[cid]['pattern_type']} (Pivot: {db.pattern_clusters[cid]['pivot_val']})",
                key="dash_cluster_inspect_sel",
            )
            c_info = next((c for c in all_clusters if c["cluster_id"] == sel_cluster_id), None)
            if c_info:
                st.markdown(
                    f"""
                    <div style="font-family:var(--font-mono); font-size:0.75rem; color:var(--text-secondary); margin-bottom:10px;">
                        Risk Score: <strong style="color:#FF4D6A;">{c_info['risk_score']}/100</strong> &bull;
                        Total Syndicate Loss: <strong style="color:var(--text-white);">₹{c_info['total_loss']:,.0f}</strong> &bull;
                        Connected Complaints: {c_info['linked_dockets']} cases
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if c_info["linked_doc_list"]:
                    cl_cols = st.columns(min(len(c_info["linked_doc_list"]), 4))
                    for idx, cdoc in enumerate(c_info["linked_doc_list"]):
                        with cl_cols[idx % 4]:
                            cdoc_obj = db.incident_dockets.get(cdoc)
                            if cdoc_obj:
                                st.markdown(
                                    f"""
                                    <div style="background:var(--bg-panel); border:1px solid var(--border-main);
                                                border-left:3px solid var(--red); padding:8px 10px; margin-bottom:6px; font-size:0.76rem;">
                                        <strong>{cdoc}</strong><br>
                                        {cdoc_obj['crime_type']}<br>
                                        Loss: ₹{cdoc_obj['loss_amt']:,.0f}
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                                if st.button(f"Inspect {cdoc}", key=f"cl_btn_{sel_cluster_id}_{cdoc}", use_container_width=True):
                                    st.session_state.selected_docket_id = cdoc
                                    st.session_state.current_page = "Cases"
                                    st.rerun()

                if st.button(f"Open Cluster Dossier in Patterns ({c_info['cluster_id'].upper()})", key=f"cl_open_pat_{sel_cluster_id}"):
                    st.session_state.selected_cluster_id = sel_cluster_id
                    st.session_state.current_page = "Patterns"
                    st.rerun()

    st.markdown("<hr style='border:none; border-top:1px solid #2A2A2A; margin:20px 0;'>", unsafe_allow_html=True)

    # ── Bottom: Case Stream + Intel Panel ──
    col_stream, col_intel = st.columns([1.65, 1.0], gap="large")

    with col_stream:
        sorted_dockets = sorted(filtered_dockets, key=lambda x: x["filed_dt"], reverse=True)

        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:14px;">
                <div>
                    <div class="section-label">Incident Docket Register</div>
                    <div class="section-heading">Recent Cases</div>
                </div>
                <span style="font-family:var(--font-mono); font-size:0.62rem; color:var(--text-dim);">
                    {len(filtered_dockets)} DOCKETS ON FILE
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not sorted_dockets:
            st.info("No cases match the selected filter.")
        else:
            for d in sorted_dockets:
                officer_name = db.registrant_profiles.get(d["officer_id"], {}).get("full_name", "Unassigned")
                filed_str    = fmt_date(d["filed_dt"])
                loss_str     = fmt_inr(d["loss_amt"])
                ev_count     = db.fn_evidence_count(d["doc_no"])
                severity     = compute_severity(d["loss_amt"], d["stage_code"])

                st.markdown(
                    f"""
                    <div style="background:var(--bg-panel); border:1px solid var(--border-main);
                                border-left:3px solid var(--red); padding:14px 16px; margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                            <div>
                                <div style="font-family:var(--font-display); font-size:1.10rem; font-weight:800;
                                            color:var(--text-white); letter-spacing:0.04em; text-transform:uppercase;">
                                    {d['doc_no']}
                                </div>
                                <div style="font-size:0.80rem; color:var(--text-secondary); margin-top:2px;">
                                    {d['crime_type']}
                                    &nbsp;<span style="font-family:var(--font-mono); font-size:0.70rem; color:var(--text-dim);">
                                        &bull; {ev_count} EXHIBITS
                                    </span>
                                </div>
                            </div>
                            <div style="text-align:right;">
                                {render_status_tag(d['stage_code'])}
                                <div style="margin-top:4px;">{render_severity_tag(severity)}</div>
                            </div>
                        </div>
                        <div style="display:grid; grid-template-columns: repeat(3,1fr); gap:10px;
                                    margin-top:12px; padding-top:10px; border-top:1px solid var(--border-subtle);">
                            <div>
                                <div style="font-family:var(--font-mono); font-size:0.56rem; text-transform:uppercase;
                                            letter-spacing:0.10em; color:var(--text-dim); margin-bottom:2px;">
                                    DUTY OFFICER
                                </div>
                                <div style="font-size:0.82rem; color:var(--text-primary); font-weight:500;">
                                    {officer_name}
                                </div>
                            </div>
                            <div>
                                <div style="font-family:var(--font-mono); font-size:0.56rem; text-transform:uppercase;
                                            letter-spacing:0.10em; color:var(--text-dim); margin-bottom:2px;">
                                    FRAUD VALUE
                                </div>
                                <div style="font-family:var(--font-mono); font-size:0.90rem; font-weight:700;
                                            color:{'#FF4D6A' if d['loss_amt'] > 40000 else 'var(--text-primary)'};">
                                    {loss_str}
                                </div>
                            </div>
                            <div>
                                <div style="font-family:var(--font-mono); font-size:0.56rem; text-transform:uppercase;
                                            letter-spacing:0.10em; color:var(--text-dim); margin-bottom:2px;">
                                    REGISTERED
                                </div>
                                <div style="font-family:var(--font-mono); font-size:0.78rem; color:var(--text-secondary);">
                                    {filed_str}
                                </div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                col_btn, _ = st.columns([1, 2])
                with col_btn:
                    if st.button(
                        f"Open Jacket — {d['doc_no']}",
                        key=f"dash_btn_{d['doc_no']}",
                        use_container_width=True,
                    ):
                        st.session_state.selected_docket_id = d["doc_no"]
                        st.session_state.current_page = "Cases"
                        st.rerun()

    with col_intel:
        # Syndicate / Pattern Clusters
        st.markdown(
            """
            <div style="margin-bottom:14px;">
                <div class="section-label">Pattern Intelligence</div>
                <div class="section-heading">Syndicate Infrastructure</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        patterns = db.get_vw_pattern_summary()
        for p in patterns:
            linked_docs_str = ", ".join(p["linked_doc_list"])
            st.markdown(
                f"""
                <div class="pattern-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-family:var(--font-display); font-weight:700; color:var(--text-white);
                                     font-size:0.90rem; letter-spacing:0.04em; text-transform:uppercase;">
                            {p['cluster_id'].upper()} &bull; {p['pattern_type'].replace('_', ' ')}
                        </span>
                        <span class="risk-score">RISK {p['risk_score']}/100</span>
                    </div>
                    <div style="font-family:var(--font-mono); font-size:0.72rem; color:var(--text-secondary); margin-top:6px;">
                        Pivot: <span style="color:var(--text-primary);">{p['pivot_val']}</span>
                    </div>
                    <div style="font-family:var(--font-mono); font-size:0.66rem; color:var(--text-dim); margin-top:3px;">
                        Linked ({p['linked_dockets']}): <span style="color:var(--text-secondary);">{linked_docs_str}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Inspect Cluster: {p['cluster_id'].upper()}", key=f"dash_cl_{p['cluster_id']}"):
                st.session_state.selected_cluster_id = p["cluster_id"]
                st.session_state.current_page = "Patterns"
                st.rerun()

        st.markdown("<hr style='border:none; border-top:1px solid #2A2A2A; margin:20px 0;'>", unsafe_allow_html=True)

        # Officer Caseload
        st.markdown(
            """
            <div style="margin-bottom:14px;">
                <div class="section-label">Personnel Management</div>
                <div class="section-heading">Officer Caseload</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        workloads = db.get_vw_officer_workload()
        for w in workloads:
            pct = int((w["open_cases"] / w["total_cases"] * 100)) if w["total_cases"] else 0
            bar_color = "#C8102E" if pct > 60 else "#CC5500" if pct > 30 else "#2E6B30"
            st.markdown(
                f"""
                <div style="background:var(--bg-panel); border:1px solid var(--border-main);
                            padding:10px 14px; margin-bottom:6px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                        <div>
                            <div style="font-family:var(--font-display); font-size:0.92rem; font-weight:700;
                                        color:var(--text-white); text-transform:uppercase; letter-spacing:0.03em;">
                                {w['full_name']}
                            </div>
                            <div style="font-family:var(--font-mono); font-size:0.58rem; color:var(--text-dim); margin-top:1px;">
                                {w['reg_id']}
                            </div>
                        </div>
                        <div style="text-align:right; font-family:var(--font-mono); font-size:0.78rem;">
                            <span style="color:#FF4D6A; font-weight:700;">{w['open_cases']} ACTIVE</span>
                            <span style="color:var(--text-dim); font-size:0.68rem;"> / {w['total_cases']} TOTAL</span>
                        </div>
                    </div>
                    <div style="height:2px; background:var(--border-main); border-radius:0;">
                        <div style="height:2px; width:{pct}%; background:{bar_color};"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
