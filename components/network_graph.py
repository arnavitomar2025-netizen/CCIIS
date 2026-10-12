"""
Case Relationship Analysis visualizer for CCIIS.
Renders an authentic, police intelligence link chart connecting:
Primary Docket -> Subject Profile -> Infrastructure Pivot -> Syndicate Cluster -> Sibling Complaints -> Seized Property.
Strictly restrained palette: #121212, #1A1A1A, #202020, #343434, #8F2929, #E2DED8, #96918B, #B54A32, #58705A.
ZERO blue / ZERO neon.
"""

from typing import Dict, Any
import streamlit as st


def render_case_relationship_graph(net: Dict[str, Any]):
    """Renders a restrained, forensic relationship map with interactive exploration links."""
    if not net or "docket" not in net:
        st.info("No relational links recorded for this case.")
        return

    doc = net["docket"]
    doc_no = doc["doc_no"]
    suspects = net.get("suspects", [])
    evidence = net.get("evidence", [])
    clusters = net.get("clusters", [])

    st.markdown(
        f"""
        <div style="background:#1A1A1A; border:1px solid #343434; border-left:4px solid #8F2929; border-radius:1px; padding:14px 18px; margin-bottom:16px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <span class="mono-tag" style="font-size:0.62rem; color:#96918B; text-transform:uppercase; letter-spacing:0.08em;">
                        Core Docket Under Inquiry
                    </span>
                    <div class="mono-tag" style="font-size:1.15rem; font-weight:700; color:#E2DED8; margin-top:2px;">
                        CASE #{doc_no} &bull; <span style="font-weight:500; color:#96918B;">{doc['crime_type'].upper()}</span>
                    </div>
                </div>
                <div style="text-align:right; font-size:0.78rem; color:#96918B;">
                    <div>Financial Loss: <strong style="color:#E2DED8;">₹{doc['loss_amt']:,.0f}</strong></div>
                    <div>Stage: <span style="color:#D67A7A; font-weight:600;">{doc['stage_code']}</span></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3 Column Structured Editorial Layout
    col_s, col_p, col_e = st.columns([1, 1, 1], gap="medium")

    # Column 1: Attributed Subjects
    with col_s:
        st.markdown(
            """
            <div style="font-family:'IBM Plex Mono',monospace; font-size:0.68rem; font-weight:600; color:#96918B; text-transform:uppercase; letter-spacing:0.08em; padding-bottom:5px; border-bottom:1px solid #343434; margin-bottom:12px;">
                &bull; Attributed Target Subjects
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not suspects:
            st.markdown("<div style='color:#64605C; font-size:0.78rem;'>No suspect entities linked to this incident.</div>", unsafe_allow_html=True)
        else:
            for s in suspects:
                conf_pct = int(s["conf_score"] * 100)
                st.markdown(
                    f"""
                    <div style="background:#202020; border:1px solid #343434; border-left:3px solid #B54A32; border-radius:1px; padding:12px 14px; margin-bottom:10px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:600; color:#E2DED8; font-size:0.88rem;">{s['alias']}</span>
                            <span class="mono-tag" style="font-size:0.68rem; color:#E28874; font-weight:600;">{conf_pct}% CONF</span>
                        </div>
                        <div class="mono-tag" style="font-size:0.75rem; color:#96918B; margin-top:6px; line-height:1.45;">
                            <div>IP: <span style="color:#E2DED8;">{s['ip_addr'] or 'Unresolved'}</span></div>
                            <div>MSISDN: <span>{s['phone'] or 'Unresolved'}</span></div>
                            <div>Bank: <span>{s['bank_acc'] or 'None'}</span></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(f"Examine Target: {s['alias']}", key=f"btn_rel_s_{s['suspect_id']}", use_container_width=True):
                    st.session_state.selected_suspect_id = s["suspect_id"]
                    st.session_state.current_page = "Suspects"
                    st.rerun()

    # Column 2: Infrastructure Clusters & Connected Complaints
    with col_p:
        st.markdown(
            """
            <div style="font-family:'IBM Plex Mono',monospace; font-size:0.68rem; font-weight:600; color:#96918B; text-transform:uppercase; letter-spacing:0.08em; padding-bottom:5px; border-bottom:1px solid #343434; margin-bottom:12px;">
                &bull; Infrastructure &amp; Cross-Cases
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not clusters:
            st.markdown("<div style='color:#64605C; font-size:0.78rem;'>No syndicate clusters matched.</div>", unsafe_allow_html=True)
        else:
            for c in clusters:
                siblings = c.get("sibling_dockets", [])
                st.markdown(
                    f"""
                    <div style="background:#202020; border:1px solid #343434; border-left:3px solid #8F2929; border-radius:1px; padding:12px 14px; margin-bottom:10px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:600; color:#E2DED8; font-size:0.88rem;">{c['pattern_type'].replace('_', ' ')}</span>
                            <span class="mono-tag" style="font-size:0.68rem; color:#D67A7A; font-weight:600;">RISK: {c['risk_score']}/100</span>
                        </div>
                        <div class="mono-tag" style="font-size:0.75rem; color:#96918B; margin-top:6px;">
                            Pivot Identifier: <span style="color:#E2DED8;">{c['pivot_val']}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if siblings:
                    st.markdown("<div class='mono-tag' style='font-size:0.68rem; color:#96918B; margin-top:2px; margin-bottom:4px;'>CROSS-LINKED COMPLAINTS:</div>", unsafe_allow_html=True)
                    for sib in siblings:
                        if st.button(f"Inspect Case: {sib}", key=f"btn_rel_sib_{sib}", use_container_width=True):
                            st.session_state.selected_docket_id = sib
                            st.session_state.current_page = "Cases"
                            st.rerun()
                else:
                    st.markdown("<div style='font-size:0.75rem; color:#64605C;'>No other complaints share this pivot.</div>", unsafe_allow_html=True)

    # Column 3: Seized Digital Evidence
    with col_e:
        st.markdown(
            """
            <div style="font-family:'IBM Plex Mono',monospace; font-size:0.68rem; font-weight:600; color:#96918B; text-transform:uppercase; letter-spacing:0.08em; padding-bottom:5px; border-bottom:1px solid #343434; margin-bottom:12px;">
                &bull; Seized Digital Evidence Locker
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not evidence:
            st.markdown("<div style='color:#64605C; font-size:0.78rem;'>No forensic files in locker.</div>", unsafe_allow_html=True)
        else:
            for ev in evidence:
                st.markdown(
                    f"""
                    <div style="background:#202020; border:1px solid #343434; border-left:3px solid #58705A; border-radius:1px; padding:12px 14px; margin-bottom:10px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span class="mono-tag" style="font-weight:700; color:#8EAC90; font-size:0.80rem;">{ev['evidence_id'].upper()}</span>
                            <span style="font-size:0.68rem; color:#96918B;">{ev['file_type']}</span>
                        </div>
                        <div style="font-size:0.85rem; color:#E2DED8; font-weight:500; margin-top:4px;">
                            {ev['file_name']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(f"Locker Item: {ev['evidence_id'].upper()}", key=f"btn_rel_ev_{ev['evidence_id']}", use_container_width=True):
                    st.session_state.selected_evidence_id = ev["evidence_id"]
                    st.session_state.current_page = "Evidence"
                    st.rerun()
