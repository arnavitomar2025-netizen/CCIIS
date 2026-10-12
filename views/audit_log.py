"""
CCIIS — System Audit Trail & Chain of Custody
BLACK / RED / WHITE editorial design.
Cryptographic audit ledger tracking all statutory record modifications.
ADMIN ONLY ACCESS.
"""

import streamlit as st
from data.mock_db import get_db
from auth import get_current_user, can
from components.ui_elements import render_editorial_header


def render_audit_log_page():
    db = get_db()
    user = get_current_user()

    if not can("can_delete"):  # ADMIN role indicator
        st.error("Access Restricted: System Audit Trail is reserved for System Administrators.")
        return

    render_editorial_header(
        title="Statutory System Audit Trail",
        description="Immutable system ledger recording all CRUD transactions, status transitions, forensic property ingestions, and pattern correlations.",
        classification="RESTRICTED // LAW ENFORCEMENT INTERNAL AFFAIRS",
    )

    logs = db.audit_logs

    # ── Summary metrics ──
    total_logs = len(logs)
    inserts = sum(1 for l in logs if l["action"] == "INSERT")
    updates = sum(1 for l in logs if l["action"] in ("UPDATE", "STAGE_CHANGE"))
    deletes = sum(1 for l in logs if l["action"] == "DELETE")

    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Total Audit Events", f"{total_logs:03d}")
    with m2: st.metric("Creation Events", f"{inserts:02d}")
    with m3: st.metric("Modifications", f"{updates:02d}")
    with m4: st.metric("Deletions", f"{deletes:02d}")

    st.markdown("<hr style='border:none; border-top:1px solid #2A2A2A; margin:16px 0;'>", unsafe_allow_html=True)

    # ── Filter controls ──
    f1, f2, f3 = st.columns([1.8, 1, 1])
    with f1:
        search = st.text_input(
            "Search Audit Records",
            placeholder="Search by record key, user, action, or value...",
            label_visibility="collapsed",
            key="audit_search_input",
        ).strip().lower()
    with f2:
        tables = ["All Tables"] + sorted(list({l["table_name"] for l in logs}))
        sel_table = st.selectbox("Target Table", tables, label_visibility="collapsed", key="audit_tbl_select")
    with f3:
        actions = ["All Actions"] + sorted(list({l["action"] for l in logs}))
        sel_action = st.selectbox("Action Type", actions, label_visibility="collapsed", key="audit_act_select")

    filtered = logs
    if search:
        filtered = [
            l for l in filtered
            if search in str(l["log_id"]).lower()
            or search in l["table_name"].lower()
            or search in l["action"].lower()
            or search in l["record_key"].lower()
            or search in l["changed_by"].lower()
            or (l.get("new_value") and search in l["new_value"].lower())
            or (l.get("old_value") and search in l["old_value"].lower())
        ]
    if sel_table != "All Tables":
        filtered = [l for l in filtered if l["table_name"] == sel_table]
    if sel_action != "All Actions":
        filtered = [l for l in filtered if l["action"] == sel_action]

    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <div class="section-label">Audit Log Ledger</div>
            <span style="font-family:var(--font-mono); font-size:0.62rem; color:var(--text-dim);">
                {len(filtered)} OF {total_logs} ENTRIES
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not filtered:
        st.info("No audit log records match the current filter criteria.")
        return

    action_colors = {
        "INSERT":       "#2E6B30",
        "STAGE_CHANGE": "#C8102E",
        "UPDATE":       "#CC5500",
        "DELETE":       "#FF4D6A",
        "CLUSTER_JOIN": "#8F2929",
    }

    for log in filtered:
        act_color = action_colors.get(log["action"], "#8A8480")
        time_str = log["changed_at"].strftime("%d %b %Y &bull; %H:%M:%S")

        old_val_display = f'<span style="color:var(--text-dim);">PREV:</span> {log["old_value"]}' if log.get("old_value") else "N/A"
        new_val_display = f'<span style="color:var(--text-dim);">NEW:</span> <strong style="color:var(--text-white);">{log["new_value"]}</strong>' if log.get("new_value") else "N/A"

        st.markdown(
            f"""
            <div style="background:var(--bg-panel); border:1px solid var(--border-main);
                        border-left:3px solid {act_color}; padding:12px 16px; margin-bottom:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span style="font-family:var(--font-mono); font-size:0.65rem; color:var(--text-dim);">
                            LOG #{log['log_id']:04d} &bull;
                        </span>
                        <span style="font-family:var(--font-mono); font-weight:700; font-size:0.75rem;
                                     color:{act_color}; margin-left:4px;">
                            {log['action']}
                        </span>
                        <span style="font-family:var(--font-mono); font-size:0.75rem; color:var(--text-white); margin-left:10px;">
                            {log['table_name']}
                        </span>
                    </div>
                    <div style="font-family:var(--font-mono); font-size:0.68rem; color:var(--text-dim);">
                        {time_str}
                    </div>
                </div>
                <div style="display:grid; grid-template-columns: 1fr 2fr 1fr; gap:12px; margin-top:8px;
                            font-family:var(--font-mono); font-size:0.72rem; border-top:1px solid var(--border-subtle); padding-top:6px;">
                    <div>
                        <span style="color:var(--text-dim);">TARGET KEY:</span>
                        <strong style="color:var(--text-primary);">{log['record_key']}</strong>
                    </div>
                    <div>
                        {old_val_display} &bull; {new_val_display}
                    </div>
                    <div style="text-align:right;">
                        <span style="color:var(--text-dim);">ACTOR:</span>
                        <strong style="color:var(--text-primary);">{log['changed_by']}</strong>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
