"""
CCIIS — Formatting & Validation Utilities
==========================================
Shared helpers used across all views. No business logic here — only
formatting, validation, and display utilities that are UI-framework agnostic.
Replace or extend during MySQL integration without touching view files.
"""

from datetime import datetime


# ---------------------------------------------------------------------------
# Currency
# ---------------------------------------------------------------------------

def _to_dt(val):
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    if hasattr(val, "year") and hasattr(val, "month") and hasattr(val, "day"):
        return datetime(val.year, val.month, val.day)
    if isinstance(val, str):
        val = val.strip()
        for fmt in (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d",
            "%d-%m-%Y %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            "%d %b %Y, %H:%M",
            "%d %b %Y",
        ):
            try:
                return datetime.strptime(val, fmt)
            except ValueError:
                pass
    return None


# ---------------------------------------------------------------------------
# Currency
# ---------------------------------------------------------------------------

def fmt_inr(amount: float, compact: bool = False) -> str:
    """Format a value as Indian Rupees."""
    if amount is None:
        return "NIL"
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return "₹0.00"
    if amount == 0:
        return "NIL"
    if compact:
        if amount >= 1_00_00_000:
            return f"₹{amount/1_00_00_000:.1f}Cr"
        if amount >= 1_00_000:
            return f"₹{amount/1_00_000:.1f}L"
        if amount >= 1_000:
            return f"₹{amount/1_000:.0f}K"
    return f"₹{amount:,.2f}"


# ---------------------------------------------------------------------------
# Date / Time
# ---------------------------------------------------------------------------

def fmt_date(dt) -> str:
    parsed = _to_dt(dt)
    if parsed:
        return parsed.strftime("%d %b %Y")
    return str(dt) if dt is not None else "—"


def fmt_datetime(dt) -> str:
    parsed = _to_dt(dt)
    if parsed:
        return parsed.strftime("%d %b %Y, %H:%M")
    return str(dt) if dt is not None else "—"


def fmt_datetime_full(dt) -> str:
    parsed = _to_dt(dt)
    if parsed:
        return parsed.strftime("%d %b %Y • %H:%M HRS")
    return str(dt) if dt is not None else "—"


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_doc_no(doc_no: str, existing_keys: list[str]) -> str | None:
    """Return an error string or None if valid."""
    doc_no = doc_no.strip()
    if not doc_no:
        return "Docket number is required."
    if doc_no in existing_keys:
        return f"Docket {doc_no} already exists."
    return None


def validate_loss(amount: float) -> str | None:
    if amount < 0:
        return "Loss amount cannot be negative."
    return None


def validate_conf_score(score: float) -> str | None:
    if not (0.0 <= score <= 1.0):
        return "Confidence score must be between 0.0 and 1.0."
    return None


def validate_sha256(hash_str: str) -> str | None:
    import re
    hash_str = hash_str.strip()
    if not hash_str:
        return "SHA-256 hash is required."
    if not re.fullmatch(r"[0-9a-fA-F]{64}", hash_str):
        return "SHA-256 must be exactly 64 hexadecimal characters."
    return None


# ---------------------------------------------------------------------------
# Severity helper
# ---------------------------------------------------------------------------

def compute_severity(loss_amt: float, stage_code: str) -> str:
    if loss_amt > 40_000 or stage_code == "INVESTIGATION":
        return "HIGH"
    if loss_amt > 0:
        return "MEDIUM"
    return "LOW"


# ---------------------------------------------------------------------------
# Stage ordering for display
# ---------------------------------------------------------------------------

STAGE_ORDER = ["TRIAGE", "LOGGED", "INVESTIGATION", "CLOSED"]

STAGE_COLORS = {
    "INVESTIGATION": "#C8102E",
    "TRIAGE":        "#CC5500",
    "LOGGED":        "#383838",
    "CLOSED":        "#2E6B30",
}
