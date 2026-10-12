"""
CCIIS — Seed Data Loader from cciis_final.sql
=============================================
Parses authoritative SQL dump from cciis_final.sql and produces Python data structures
used by both CCIISDatabase (in-memory engine) and MySQLDatabase validation.
"""

import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional


def _parse_sql_values(val_str: str) -> List[List[Any]]:
    """Parse comma-separated tuples from SQL VALUES clause."""
    rows = []
    i = 0
    n = len(val_str)

    while i < n:
        while i < n and val_str[i] != "(":
            i += 1
        if i >= n:
            break
        i += 1  # skip '('

        row = []
        curr = []
        in_quote = False
        quote_char = None
        escaped = False

        while i < n:
            ch = val_str[i]
            if in_quote:
                if escaped:
                    curr.append(ch)
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == quote_char:
                    if i + 1 < n and val_str[i + 1] == quote_char:
                        curr.append(ch)
                        i += 1
                    else:
                        in_quote = False
                else:
                    curr.append(ch)
            else:
                if ch in ("'", '"'):
                    in_quote = True
                    quote_char = ch
                elif ch == ",":
                    val = "".join(curr).strip()
                    row.append(_clean_val(val))
                    curr = []
                elif ch == ")":
                    val = "".join(curr).strip()
                    row.append(_clean_val(val))
                    curr = []
                    i += 1
                    break
                else:
                    curr.append(ch)
            i += 1
        rows.append(row)
    return rows


def _clean_val(val: str) -> Any:
    if val == "NULL" or val == "":
        return None
    if (val.startswith("'") and val.endswith("'")) or (val.startswith('"') and val.endswith('"')):
        inner = val[1:-1]
        return inner.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")
    try:
        return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except ValueError:
        pass
    return val


def parse_datetime(val: Any) -> Optional[datetime]:
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    if isinstance(val, str):
        val = val.strip()
        for fmt in (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d",
            "%d-%m-%Y %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
        ):
            try:
                return datetime.strptime(val, fmt)
            except ValueError:
                pass
    return None


def load_seed_data(sql_file_path: Optional[str] = None) -> Dict[str, Any]:
    """Parse cciis_final.sql and return dictionary of tables with enriched types."""
    if not sql_file_path:
        sql_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cciis_final.sql")

    if not os.path.exists(sql_file_path):
        raise FileNotFoundError(f"SQL seed file not found at: {sql_file_path}")

    with open(sql_file_path, "r", encoding="utf-8") as f:
        sql = f.read()

    col_map = {
        "ncrp_registrant_profile": [
            "reg_id", "full_name", "email", "phone", "pass_hash", "role_code", "priv_lvl", "created_at",
        ],
        "ncrp_incident_docket": [
            "doc_no", "victim_id", "officer_id", "event_dt", "filed_dt", "crime_type", "details", "stage_code", "loss_amt",
        ],
        "ncrp_suspect_entity": [
            "suspect_id", "alias", "phone", "bank_acc", "ip_addr", "trace_notes",
        ],
        "ncrp_pattern_cluster": [
            "cluster_id", "pattern_type", "pivot_val", "risk_score", "detected_dt",
        ],
        "ncrp_forensic_evidence": [
            "evidence_id", "doc_no", "file_name", "file_type", "file_path", "sha_hash", "uploaded_dt", "uploader_id",
        ],
        "ncrp_analytical_report": [
            "report_id", "author_id", "rep_type", "generated_dt", "is_admissible", "doc_summary", "doc_no",
        ],
        "ncrp_docket_suspect_link": [
            "doc_no", "suspect_id", "linked_dt", "conf_score",
        ],
        "ncrp_docket_pattern_link": [
            "doc_no", "cluster_id", "matched_dt",
        ],
        "ncrp_audit_log": [
            "log_id", "table_name", "action", "record_key", "old_value", "new_value", "changed_by", "changed_at",
        ],
    }

    raw_tables: Dict[str, List[Dict[str, Any]]] = {}
    for tname, cols in col_map.items():
        pattern = rf"INSERT INTO \x60{tname}\x60 VALUES\s*(.*?);\s*(?:\n|\r|/\*!40000)"
        m = re.search(pattern, sql, re.DOTALL)
        if not m:
            pattern2 = rf"INSERT INTO \x60{tname}\x60 VALUES\s*(.*?);\s*\n"
            m = re.search(pattern2, sql, re.DOTALL)
        if not m:
            raw_tables[tname] = []
            continue

        tuples = _parse_sql_values(m.group(1).strip())
        table_rows = []
        for tup in tuples:
            if len(tup) == len(cols):
                table_rows.append(dict(zip(cols, tup)))
            else:
                # Handle potential mismatch safely
                padded = list(tup) + [None] * max(0, len(cols) - len(tup))
                table_rows.append(dict(zip(cols, padded[:len(cols)])))
        raw_tables[tname] = table_rows

    # Process and build typed structures
    # 1. Registrants: reg_id -> dict
    registrants: Dict[str, Dict[str, Any]] = {}
    for r in raw_tables.get("ncrp_registrant_profile", []):
        r_copy = dict(r)
        r_copy["phone"] = str(r_copy["phone"]) if r_copy.get("phone") is not None else ""
        r_copy["priv_lvl"] = int(r_copy.get("priv_lvl") or 1)
        r_copy["created_at"] = parse_datetime(r_copy.get("created_at")) or datetime(2026, 9, 10, 17, 0, 0)
        registrants[r_copy["reg_id"]] = r_copy

    # 2. Dockets: doc_no -> dict
    dockets: Dict[str, Dict[str, Any]] = {}
    for d in raw_tables.get("ncrp_incident_docket", []):
        d_copy = dict(d)
        d_copy["loss_amt"] = float(d_copy.get("loss_amt") or 0.0)
        d_copy["event_dt"] = parse_datetime(d_copy.get("event_dt")) or datetime(2026, 9, 1, 10, 0, 0)
        d_copy["filed_dt"] = parse_datetime(d_copy.get("filed_dt")) or datetime(2026, 9, 10, 17, 0, 0)
        dockets[d_copy["doc_no"]] = d_copy

    # 3. Suspects: suspect_id (int) -> dict
    suspects: Dict[int, Dict[str, Any]] = {}
    for s in raw_tables.get("ncrp_suspect_entity", []):
        s_copy = dict(s)
        s_id = int(s_copy["suspect_id"])
        s_copy["suspect_id"] = s_id
        s_copy["phone"] = str(s_copy["phone"]) if s_copy.get("phone") is not None else None
        s_copy["bank_acc"] = str(s_copy["bank_acc"]) if s_copy.get("bank_acc") is not None else None
        suspects[s_id] = s_copy

    # 4. Pattern Clusters: cluster_id -> dict
    clusters: Dict[str, Dict[str, Any]] = {}
    for c in raw_tables.get("ncrp_pattern_cluster", []):
        c_copy = dict(c)
        c_copy["risk_score"] = int(c_copy.get("risk_score") or 50)
        c_copy["detected_dt"] = parse_datetime(c_copy.get("detected_dt")) or datetime(2026, 9, 10, 17, 0, 0)
        clusters[c_copy["cluster_id"]] = c_copy

    # 5. Evidence: evidence_id -> dict
    evidence: Dict[str, Dict[str, Any]] = {}
    for ev in raw_tables.get("ncrp_forensic_evidence", []):
        ev_copy = dict(ev)
        up_dt = parse_datetime(ev_copy.get("uploaded_dt")) or datetime(2026, 9, 10, 17, 0, 0)
        ev_copy["uploaded_dt"] = up_dt
        ev_copy["uploaded_at"] = up_dt  # alias for views
        evidence[ev_copy["evidence_id"]] = ev_copy

    # 6. Reports: report_id -> dict
    reports: Dict[str, Dict[str, Any]] = {}
    for rep in raw_tables.get("ncrp_analytical_report", []):
        rep_copy = dict(rep)
        gen_dt = parse_datetime(rep_copy.get("generated_dt")) or datetime(2026, 9, 10, 17, 0, 0)
        rep_copy["generated_dt"] = gen_dt
        rep_copy["created_at"] = gen_dt  # alias for views
        is_adm = bool(rep_copy.get("is_admissible", 1))
        rep_copy["is_admissible"] = 1 if is_adm else 0
        rep_copy["admissibility"] = "YES" if is_adm else "NO"
        reports[rep_copy["report_id"]] = rep_copy

    # 7. Docket Suspect Links: list
    suspect_links: List[Dict[str, Any]] = []
    for sl in raw_tables.get("ncrp_docket_suspect_link", []):
        sl_copy = dict(sl)
        sl_copy["suspect_id"] = int(sl_copy["suspect_id"])
        sl_copy["conf_score"] = float(sl_copy.get("conf_score") or 1.0)
        sl_copy["linked_dt"] = parse_datetime(sl_copy.get("linked_dt")) or datetime(2026, 9, 10, 17, 0, 0)
        suspect_links.append(sl_copy)

    # 8. Docket Pattern Links: list
    pattern_links: List[Dict[str, Any]] = []
    for pl in raw_tables.get("ncrp_docket_pattern_link", []):
        pl_copy = dict(pl)
        pl_copy["matched_dt"] = parse_datetime(pl_copy.get("matched_dt")) or datetime(2026, 9, 10, 17, 0, 0)
        pattern_links.append(pl_copy)

    # 9. Audit Logs: list
    audit_logs: List[Dict[str, Any]] = []
    for al in raw_tables.get("ncrp_audit_log", []):
        al_copy = dict(al)
        al_copy["log_id"] = int(al_copy["log_id"])
        al_copy["changed_at"] = parse_datetime(al_copy.get("changed_at")) or datetime(2026, 10, 8, 18, 30, 44)
        audit_logs.append(al_copy)

    return {
        "registrant_profiles": registrants,
        "incident_dockets": dockets,
        "suspect_entities": suspects,
        "pattern_clusters": clusters,
        "forensic_evidence": evidence,
        "analytical_reports": reports,
        "docket_suspect_links": suspect_links,
        "docket_pattern_links": pattern_links,
        "audit_logs": audit_logs,
    }
