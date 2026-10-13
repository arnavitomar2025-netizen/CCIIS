"""
CCIIS — Login Screen
====================
Polished institutional login gate with CCIIS branding.
Show/hide password, validation, loading state, and demo account hints.
PROTOTYPE ONLY — not production authentication.
"""

import os
import streamlit as st
from auth import login


def render_login_page():
    """Render the full-screen login wall."""

    # ── Scoped login page styling ──
    st.markdown(
        """
        <style>
        /* Hide default streamlit chrome during login */
        [data-testid="stSidebar"] { display: none !important; }
        header[data-testid="stHeader"] { display: none !important; }

        .login-outer {
            display: flex; justify-content: center; align-items: flex-start;
            min-height: 90vh; padding-top: 6vh;
        }
        .login-card {
            background: var(--bg-panel);
            border: 1px solid var(--border-main);
            border-top: 4px solid var(--red);
            padding: 40px 44px 36px;
            width: 100%; max-width: 440px;
        }
        .login-red-bar  { background: var(--red); height: 4px; width: 100%; margin-bottom: 0; }
        .login-gov-tag  {
            font-family: var(--font-mono); font-size: 0.55rem;
            letter-spacing: 0.14em; text-transform: uppercase;
            color: var(--text-dim); margin-bottom: 12px;
        }
        .login-acronym  {
            font-family: var(--font-display); font-size: 3.2rem; font-weight: 900;
            color: var(--text-white); letter-spacing: 0.04em; line-height: 1;
        }
        .login-acronym span { color: var(--red); }
        .login-subtitle {
            font-family: var(--font-body); font-size: 0.75rem; font-weight: 500;
            color: var(--text-secondary); letter-spacing: 0.01em;
            line-height: 1.3; margin-top: 4px; margin-bottom: 20px;
        }
        .login-classification {
            display: inline-block; font-family: var(--font-mono); font-size: 0.52rem;
            font-weight: 600; letter-spacing: 0.10em; color: var(--red);
            border: 1px solid var(--red-muted); padding: 2px 6px; margin-bottom: 28px;
            text-transform: uppercase; background: rgba(200,16,46,0.06);
        }
        .login-field-label {
            font-family: var(--font-mono); font-size: 0.60rem; text-transform: uppercase;
            letter-spacing: 0.10em; color: var(--text-dim); margin-bottom: 4px;
        }
        .login-demo-panel {
            background: var(--bg-secondary); border: 1px solid var(--border-main);
            border-left: 3px solid var(--red); padding: 12px 16px; margin-top: 24px;
            font-family: var(--font-mono); font-size: 0.64rem; color: var(--text-dim);
            line-height: 1.8;
        }
        .login-demo-title {
            font-size: 0.58rem; text-transform: uppercase; letter-spacing: 0.12em;
            color: var(--red); margin-bottom: 8px; font-weight: 700;
        }
        .login-error {
            background: rgba(200,16,46,0.10); border: 1px solid var(--red-muted);
            border-left: 3px solid var(--red); color: #FF4D6A;
            font-family: var(--font-mono); font-size: 0.72rem; padding: 10px 14px;
            margin-bottom: 14px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ── Centered card ──
    lcol, mcol, rcol = st.columns([1, 1.6, 1])
    with mcol:
        st.markdown(
            """
            <div class="login-gov-tag">Government of India &bull; NCRP &bull; Law Enforcement Portal</div>
            <div class="login-acronym">CC<span>II</span>S</div>
            <div class="login-subtitle">Cyber Crime Investigation<br>&amp; Intelligence System</div>
            <div class="login-classification">RESTRICTED // LAW ENFORCEMENT ACCESS ONLY</div>
            """,
            unsafe_allow_html=True,
        )

        # ── Error display ──
        error_msg = st.session_state.pop("login_error", None)
        if error_msg:
            st.markdown(
                f'<div class="login-error">⚠ {error_msg}</div>',
                unsafe_allow_html=True,
            )

        # ── Credential fields ──
        st.markdown('<div class="login-field-label">Email Address / User ID</div>', unsafe_allow_html=True)
        identifier = st.text_input(
            "Identifier",
            placeholder="e.g. admin@cciis.in",
            label_visibility="collapsed",
            key="login_identifier",
        )

        st.markdown('<div class="login-field-label" style="margin-top:14px;">Password</div>', unsafe_allow_html=True)
        show_pw = st.checkbox("Show password", key="login_show_pw", value=False)
        password = st.text_input(
            "Password",
            type="default" if show_pw else "password",
            placeholder="Enter your password",
            label_visibility="collapsed",
            key="login_password",
        )

        st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

        col_btn, col_loading = st.columns([1, 0.5])
        with col_btn:
            submitted = st.button("AUTHENTICATE →", type="primary", use_container_width=True, key="login_btn")

        if submitted:
            if not identifier.strip():
                st.session_state["login_error"] = "Email / User ID is required."
                st.rerun()
            elif not password.strip():
                st.session_state["login_error"] = "Password is required."
                st.rerun()
            else:
                with st.spinner("Verifying credentials…"):
                    import time
                    time.sleep(0.4)   # brief loading state for UX
                    success = login(identifier, password)
                if success:
                    st.rerun()
                else:
                    st.session_state["login_error"] = (
                        "Invalid credentials. Access denied. Contact your system administrator."
                    )
                    st.rerun()


