"""
CCIIS — Authentication & Session Management
============================================
PROTOTYPE / DEMO AUTHENTICATION ONLY.
This module uses in-memory SHA-256 comparison against mock_db seed passwords.
It does NOT connect to any database, store sessions externally, or perform
production-grade security. Replace this module with a MySQL-backed equivalent
during the database integration phase.

DEMO ACCOUNTS (prototype only):
  admin@cciis.in       /  admin123     →  ADMIN
  ravi@cciis.in        /  officer123   →  INVESTIGATOR
  meena@cciis.in       /  analyst123   →  INVESTIGATOR
  arjun@mail.com       /  victim123    →  VICTIM
  priya@mail.com       /  victim123    →  VICTIM
"""

import hashlib
import streamlit as st
from data.mock_db import get_db


# ---------------------------------------------------------------------------
# Role permission matrix — PROTOTYPE ONLY.
# Will be replaced by MySQL stored-procedure / privilege check during DB phase.
# ---------------------------------------------------------------------------
ROLE_PERMISSIONS: dict[str, dict] = {
    "ADMIN": {
        "pages":         ["Dashboard", "Cases", "Suspects", "Evidence", "Patterns", "Reports", "Audit Log"],
        "can_create":    True,
        "can_edit":      True,
        "can_delete":    True,
        "can_change_stage": True,
        "sees_full_suspect": True,  # phone, bank_acc, trace_notes
        "sees_all_cases":   True,   # all dockets regardless of assigned victim
        "label":         "System Administrator",
    },
    "INVESTIGATOR": {
        "pages":         ["Dashboard", "Cases", "Suspects", "Evidence", "Patterns", "Reports"],
        "can_create":    True,
        "can_edit":      True,
        "can_delete":    False,
        "can_change_stage": True,
        "sees_full_suspect": True,
        "sees_all_cases":   True,
        "label":         "Investigating Officer",
    },
    "VICTIM": {
        "pages":         ["My Cases", "My Evidence"],
        "can_create":    False,
        "can_edit":      False,
        "can_delete":    False,
        "can_change_stage": False,
        "sees_full_suspect": False,
        "sees_all_cases":   False,  # only own dockets
        "label":         "Registered Complainant",
    },
}


def _hash(plaintext: str) -> str:
    """SHA-256 — mirrors mock_db seed hashing."""
    return hashlib.sha256(plaintext.encode()).hexdigest()


def authenticate(identifier: str, password: str) -> dict | None:
    """
    Authenticate against MySQL ncrp_registrant_profile table using parameterized query.
    Falls back to memory dictionary if database is offline.
    """
    db = get_db()
    candidate_hash = _hash(password.strip())
    identifier = identifier.strip().lower()

    if hasattr(db, "authenticate_user"):
        user = db.authenticate_user(identifier, candidate_hash)
        if user:
            return user

    for reg in db.registrant_profiles.values():
        if (reg["email"].lower() == identifier or reg["reg_id"].lower() == identifier):
            if reg["pass_hash"] == candidate_hash:
                return reg  # matched
    return None


def login(identifier: str, password: str) -> bool:
    """Attempt login; populate st.session_state on success."""
    user = authenticate(identifier, password)
    if user:
        st.session_state["authenticated"] = True
        st.session_state["user"] = {
            "reg_id":    user["reg_id"],
            "full_name": user["full_name"],
            "email":     user["email"],
            "role_code": user["role_code"],
            "priv_lvl":  user["priv_lvl"],
        }
        st.session_state["current_page"] = "Dashboard" if user["role_code"] != "VICTIM" else "My Cases"
        return True
    return False


def logout():
    """Clear session state and redirect to login."""
    for key in ["authenticated", "user", "current_page",
                "selected_docket_id", "selected_suspect_id",
                "selected_evidence_id", "selected_cluster_id",
                "selected_report_id"]:
        st.session_state.pop(key, None)


def get_current_user() -> dict | None:
    """Return the currently signed-in user dict, or None."""
    if st.session_state.get("authenticated"):
        return st.session_state.get("user")
    return None


def get_permissions() -> dict:
    """Return the permission set for the current user's role."""
    user = get_current_user()
    if not user:
        return {}
    return ROLE_PERMISSIONS.get(user["role_code"], {})


def require_login():
    """
    Call at the top of every protected page.
    If not authenticated, stop rendering and show the login wall.
    """
    if not st.session_state.get("authenticated"):
        st.stop()


def can(permission: str) -> bool:
    """
    Convenience helper: can("can_create"), can("can_delete"), etc.
    Returns False for unauthenticated users or missing permissions.
    """
    perms = get_permissions()
    return bool(perms.get(permission, False))


def allowed_pages() -> list[str]:
    """Return the list of page names the current user may access."""
    perms = get_permissions()
    return perms.get("pages", [])
