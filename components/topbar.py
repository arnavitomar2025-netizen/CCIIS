"""
Technical Context Top Bar for Cerberus Case Intelligence Console.
Displays environment, network state, timestamp, and active role telemetry.
"""

import streamlit as st


def render_topbar(current_module_label: str):
    """Renders the technical forensic telemetry strip."""
    clean_label = current_module_label.strip()

    st.markdown(
        f"""
        <div class="top-telemetry-strip">
            <div class="telemetry-item">
                <span class="telemetry-tag">SYSTEM CONTEXT</span>
                <span class="telemetry-val" style="color:var(--text-white);">CCIIS // {clean_label}</span>
            </div>
            <div class="telemetry-item">
                <span class="telemetry-tag">ENVIRONMENT</span>
                <span class="telemetry-val">NCRP PROTOCOL (IN-MEMORY DEMO)</span>
            </div>
            <div class="telemetry-item">
                <span class="telemetry-tag">DATABASE STATE</span>
                <span class="telemetry-val" style="color:#2E6B30;">● ACTIVE</span>
            </div>
            <div class="telemetry-item">
                <span class="telemetry-tag">LAST SYNC</span>
                <span class="telemetry-val">08 OCT 2026 / 14:32:18</span>
            </div>
            <div class="telemetry-item">
                <span class="telemetry-tag">OPERATOR / ROLE</span>
                <span class="telemetry-val">INVESTIGATOR [reg-002]</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
