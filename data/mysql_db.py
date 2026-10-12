"""
CCIIS — MySQL Database Engine
=============================
Real MySQL integration connecting the CCIIS frontend to the relational database
defined in cciis_final.sql (Database: project_cciis).

Implements:
- Parameterized SQL queries for security
- Real Stored Procedures: sp_register_docket, sp_update_stage, sp_link_suspect, sp_suspect_cases, sp_assign_investigator
- Real Functions: fn_case_age_days, fn_evidence_count, fn_get_suspect_count
- Real Views: vw_active_investigations, vw_officer_workload, vw_pattern_summary, vw_suspect_case_history, vw_suspect_public
- Real Triggers: trg_evidence_after_insert, trg_pattern_link_after_insert, trg_docket_before_update, trg_docket_after_update, trg_docket_after_delete
- Connection pooling and auto-schema initialization from cciis_final.sql
"""

import os
from datetime import datetime
import pymysql
import pymysql.cursors
import streamlit as st
from typing import Dict, List, Optional, Any, Tuple


def get_mysql_config() -> dict:
    """Retrieve MySQL credentials with priority order."""
    cfg = {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "",
        "database": "project_cciis",
    }

    # 1. Check Streamlit session state overrides
    if "mysql_config_override" in st.session_state:
        cfg.update(st.session_state["mysql_config_override"])
        return cfg

    # 2. Check Streamlit secrets
    try:
        if hasattr(st, "secrets") and "mysql" in st.secrets:
            sec = dict(st.secrets["mysql"])
            cfg.update({k: v for k, v in sec.items() if v is not None})
            return cfg
    except Exception:
        pass

    # 3. Check .env file in workspace
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip().upper()
                        v = v.strip().strip('"').strip("'")
                        if k == "MYSQL_HOST": cfg["host"] = v
                        elif k == "MYSQL_PORT": cfg["port"] = int(v) if v.isdigit() else 3306
                        elif k == "MYSQL_USER": cfg["user"] = v
                        elif k == "MYSQL_PASSWORD": cfg["password"] = v
                        elif k == "MYSQL_DATABASE": cfg["database"] = v
        except Exception:
            pass

    # 4. Check OS environment variables
    if os.getenv("MYSQL_HOST"): cfg["host"] = os.getenv("MYSQL_HOST")
    if os.getenv("MYSQL_PORT"): cfg["port"] = int(os.getenv("MYSQL_PORT"))
    if os.getenv("MYSQL_USER"): cfg["user"] = os.getenv("MYSQL_USER")
    if os.getenv("MYSQL_PASSWORD") is not None: cfg["password"] = os.getenv("MYSQL_PASSWORD")
    if os.getenv("MYSQL_DATABASE"): cfg["database"] = os.getenv("MYSQL_DATABASE")

    return cfg


class MySQLDatabase:
    def __init__(self, config: Optional[dict] = None):
        self.config = config or get_mysql_config()
        self.is_connected = False
        self.last_error = ""

    def get_connection(self, use_db: bool = True):
        """Establish a live PyMySQL connection."""
        conn_kwargs = {
            "host": self.config["host"],
            "port": int(self.config["port"]),
            "user": self.config["user"],
            "password": self.config["password"],
            "charset": "utf8mb4",
            "cursorclass": pymysql.cursors.DictCursor,
            "autocommit": True,
            "connect_timeout": 3,
        }
        if use_db and self.config.get("database"):
            conn_kwargs["database"] = self.config["database"]
        return pymysql.connect(**conn_kwargs)

    def test_connection(self) -> Tuple[bool, str]:
        """Test the connection without throwing exceptions."""
        try:
            conn = self.get_connection(use_db=False)
            with conn.cursor() as cur:
                cur.execute("SELECT VERSION() AS ver;")
                res = cur.fetchone()
            conn.close()
            self.is_connected = True
            self.last_error = ""
            return True, f"Connected to MySQL {res.get('ver', '')}"
        except Exception as e:
            self.is_connected = False
            self.last_error = str(e)
            return False, str(e)

    def init_database_from_sql(self, sql_file_path: Optional[str] = None) -> Tuple[bool, str]:
        """Execute cciis_final.sql against the MySQL instance."""
        if not sql_file_path:
            sql_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cciis_final.sql")

        if not os.path.exists(sql_file_path):
            return False, f"SQL file not found at {sql_file_path}"

        try:
            conn = self.get_connection(use_db=False)
            with conn.cursor() as cur:
                # Ensure database exists
                cur.execute(f"CREATE DATABASE IF NOT EXISTS `{self.config['database']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;")
                cur.execute(f"USE `{self.config['database']}`;")
                cur.execute("SET FOREIGN_KEY_CHECKS = 0;")

                with open(sql_file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Process SQL content respecting DELIMITER blocks
                lines = content.splitlines()
                delimiter = ";"
                current_stmt = []

                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith("DELIMITER"):
                        parts = stripped.split()
                        if len(parts) >= 2:
                            delimiter = parts[1]
                        continue

                    if not stripped or stripped.startswith("--"):
                        continue

                    current_stmt.append(line)
                    combined = "\n".join(current_stmt).strip()
                    if combined.endswith(delimiter):
                        clean_sql = combined[:-len(delimiter)].strip()
                        if clean_sql.startswith("/*!") and clean_sql.endswith("*/"):
                            clean_sql = re.sub(r"^/\*!\d+\s*", "", clean_sql)
                            clean_sql = re.sub(r"\*/$", "", clean_sql).strip()
                        if clean_sql:
                            try:
                                cur.execute(clean_sql)
                            except Exception:
                                pass
                        current_stmt = []

                cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
            conn.close()
            return True, f"Database `{self.config['database']}` initialized from {os.path.basename(sql_file_path)}."
        except Exception as e:
            return False, f"Initialization error: {e}"

    def authenticate_user(self, identifier: str, candidate_hash: str) -> Optional[dict]:
        """Direct parameterized credential verification against ncrp_registrant_profile."""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT reg_id, full_name, email, phone, pass_hash, role_code, priv_lvl
                    FROM ncrp_registrant_profile
                    WHERE LOWER(email) = %s OR LOWER(reg_id) = %s;
                    """,
                    (identifier.lower(), identifier.lower()),
                )
                user = cur.fetchone()
            conn.close()
            if user and user.get("pass_hash") == candidate_hash:
                return user
        except Exception:
            pass
        return None

    # =========================================================================
    # Compatibility Properties for Frontend Views
    # =========================================================================

    @property
    def registrant_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Maps reg_id -> dict for views."""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM ncrp_registrant_profile;")
                rows = cur.fetchall()
            conn.close()
            return {r["reg_id"]: r for r in rows}
        except Exception:
            return {}

    @property
    def incident_dockets(self) -> Dict[str, Dict[str, Any]]:
        """Maps doc_no -> dict."""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM ncrp_incident_docket ORDER BY filed_dt DESC;")
                rows = cur.fetchall()
            conn.close()
            # Convert decimal loss_amt to float for UI calculations
            for r in rows:
                if r.get("loss_amt") is not None:
                    r["loss_amt"] = float(r["loss_amt"])
            return {r["doc_no"]: r for r in rows}
        except Exception:
            return {}

    @property
    def suspect_entities(self) -> Dict[int, Dict[str, Any]]:
        """Maps suspect_id -> dict."""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM ncrp_suspect_entity ORDER BY suspect_id ASC;")
                rows = cur.fetchall()
            conn.close()
            return {r["suspect_id"]: r for r in rows}
        except Exception:
            return {}

    @property
    def pattern_clusters(self) -> Dict[str, Dict[str, Any]]:
        """Maps cluster_id -> dict."""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM ncrp_pattern_cluster ORDER BY risk_score DESC;")
                rows = cur.fetchall()
            conn.close()
            return {r["cluster_id"]: r for r in rows}
        except Exception:
            return {}

    @property
    def forensic_evidence(self) -> Dict[str, Dict[str, Any]]:
        """Maps evidence_id -> dict."""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM ncrp_forensic_evidence ORDER BY uploaded_dt DESC;")
                rows = cur.fetchall()
            conn.close()
            for r in rows:
                r["uploaded_at"] = r.get("uploaded_dt")
            return {r["evidence_id"]: r for r in rows}
        except Exception:
            return {}

    @property
    def analytical_reports(self) -> Dict[str, Dict[str, Any]]:
        """Maps report_id -> dict."""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM ncrp_analytical_report ORDER BY generated_dt DESC;")
                rows = cur.fetchall()
            conn.close()
            for r in rows:
                r["created_at"] = r.get("generated_dt")
                r["admissibility"] = "YES" if r.get("is_admissible") else "NO"
            return {r["report_id"]: r for r in rows}
        except Exception:
            return {}

    @property
    def docket_suspect_links(self) -> List[Dict[str, Any]]:
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM ncrp_docket_suspect_link;")
                rows = cur.fetchall()
            conn.close()
            for r in rows:
                if r.get("conf_score") is not None:
                    r["conf_score"] = float(r["conf_score"])
            return rows
        except Exception:
            return []

    @property
    def docket_pattern_links(self) -> List[Dict[str, Any]]:
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM ncrp_docket_pattern_link;")
                rows = cur.fetchall()
            conn.close()
            return rows
        except Exception:
            return []

    @property
    def audit_logs(self) -> List[Dict[str, Any]]:
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM ncrp_audit_log ORDER BY log_id DESC;")
                rows = cur.fetchall()
            conn.close()
            return rows
        except Exception:
            return []

    # =========================================================================
    # SQL Functions (Section 5)
    # =========================================================================

    def fn_case_age_days(self, doc_no: str) -> int:
        """Call MySQL fn_case_age_days(doc_no)."""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT fn_case_age_days(%s) AS days;", (doc_no,))
                row = cur.fetchone()
            conn.close()
            return int(row["days"]) if row and row.get("days") is not None else 0
        except Exception:
            # Fallback calculation if function not created
            d = self.incident_dockets.get(doc_no)
            if not d: return 0
            return (datetime.now().date() - d["filed_dt"].date()).days

    def fn_evidence_count(self, doc_no: str) -> int:
        """Call MySQL fn_evidence_count(doc_no)."""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT fn_evidence_count(%s) AS cnt;", (doc_no,))
                row = cur.fetchone()
            conn.close()
            return int(row["cnt"]) if row and row.get("cnt") is not None else 0
        except Exception:
            return sum(1 for ev in self.forensic_evidence.values() if ev.get("doc_no") == doc_no)

    def fn_get_suspect_count(self, doc_no: str) -> int:
        """Call MySQL fn_get_suspect_count(doc_no)."""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT fn_get_suspect_count(%s) AS cnt;", (doc_no,))
                row = cur.fetchone()
            conn.close()
            return int(row["cnt"]) if row and row.get("cnt") is not None else 0
        except Exception:
            return sum(1 for l in self.docket_suspect_links if l.get("doc_no") == doc_no)

    # =========================================================================
    # SQL Views (Section 4)
    # =========================================================================

    def get_vw_active_investigations(self) -> List[Dict[str, Any]]:
        """Query vw_active_investigations view."""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM vw_active_investigations;")
                rows = cur.fetchall()
            conn.close()
            return rows
        except Exception:
            return []

    def get_vw_officer_workload(self) -> List[Dict[str, Any]]:
        """Query vw_officer_workload view."""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM vw_officer_workload;")
                rows = cur.fetchall()
            conn.close()
            for r in rows:
                r["total_cases"] = int(r.get("total_cases", 0))
                r["open_cases"] = int(r.get("open_cases", 0))
            return rows
        except Exception:
            return []

    def get_vw_pattern_summary(self) -> List[Dict[str, Any]]:
        """Query vw_pattern_summary view and enrich with linked dockets."""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM vw_pattern_summary ORDER BY risk_score DESC;")
                patterns = cur.fetchall()
                cur.execute("SELECT cluster_id, doc_no FROM ncrp_docket_pattern_link;")
                links = cur.fetchall()
            conn.close()

            cluster_docs: Dict[str, List[str]] = {}
            for l in links:
                cid = l["cluster_id"]
                cluster_docs.setdefault(cid, []).append(l["doc_no"])

            for p in patterns:
                cid = p["cluster_id"]
                p["linked_doc_list"] = cluster_docs.get(cid, [])
                p["linked_dockets"] = len(p["linked_doc_list"])
                p["total_loss"] = float(p.get("total_loss") or 0.0)
            return patterns
        except Exception:
            return []

    def get_vw_suspect_case_history(self) -> List[Dict[str, Any]]:
        """Query vw_suspect_case_history view."""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM vw_suspect_case_history;")
                rows = cur.fetchall()
            conn.close()
            for r in rows:
                if r.get("loss_amt") is not None: r["loss_amt"] = float(r["loss_amt"])
                if r.get("conf_score") is not None: r["conf_score"] = float(r["conf_score"])
            return rows
        except Exception:
            return []

    def get_vw_suspect_public(self) -> List[Dict[str, Any]]:
        """Query vw_suspect_public view."""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM vw_suspect_public;")
                rows = cur.fetchall()
            conn.close()
            return rows
        except Exception:
            return [
                {"suspect_id": s["suspect_id"], "alias": s["alias"], "ip_addr": s.get("ip_addr")}
                for s in self.suspect_entities.values()
            ]

    def get_victim_dockets(self, victim_reg_id: str) -> List[Dict[str, Any]]:
        """Return dockets where victim_id matches for victim role."""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM ncrp_incident_docket WHERE LOWER(victim_id) = %s ORDER BY filed_dt DESC;",
                    (str(victim_reg_id).lower(),)
                )
                rows = cur.fetchall()
            conn.close()
            for r in rows:
                if r.get("loss_amt") is not None:
                    r["loss_amt"] = float(r["loss_amt"])
            return rows
        except Exception:
            v_clean = str(victim_reg_id).lower()
            return [
                d for d in self.incident_dockets.values()
                if str(d.get("victim_id", "")).lower() == v_clean
            ]

    def _log_audit(
        self,
        table_name: str,
        action: str,
        record_key: str,
        old_val: Optional[str] = None,
        new_val: Optional[str] = None,
        changed_by: str = "INVESTIGATOR",
    ) -> None:
        """Manual audit logger for frontend actions."""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO ncrp_audit_log (table_name, action, record_key, old_value, new_value, changed_by)
                    VALUES (%s, %s, %s, %s, %s, %s);
                    """,
                    (
                        table_name,
                        action,
                        str(record_key),
                        str(old_val) if old_val is not None else None,
                        str(new_val) if new_val is not None else None,
                        changed_by,
                    ),
                )
            conn.close()
        except Exception:
            pass

    # =========================================================================
    # Stored Procedures (Section 6) & CRUD Operations
    # =========================================================================

    def sp_register_docket(
        self,
        doc_no: str,
        victim_id: str,
        officer_id: str,
        event_dt: datetime,
        crime_type: str,
        details: str,
        loss_amt: float,
    ) -> None:
        """Execute real Stored Procedure: sp_register_docket."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "CALL sp_register_docket(%s, %s, %s, %s, %s, %s, %s);",
                    (doc_no, victim_id, officer_id, event_dt, crime_type, details, loss_amt),
                )
        finally:
            conn.close()

    def sp_update_stage(self, doc_no: str, stage_code: str, changed_by: str = "OFFICER") -> None:
        """
        Execute real Stored Procedure: sp_update_stage.
        Fires triggers:
        - trg_docket_before_update (prevents reopening closed dockets)
        - trg_docket_after_update (writes to ncrp_audit_log)
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("CALL sp_update_stage(%s, %s);", (doc_no, stage_code))
        finally:
            conn.close()

    def sp_link_suspect(self, doc_no: str, suspect_id: int, conf_score: float) -> None:
        """Execute real Stored Procedure: sp_link_suspect."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("CALL sp_link_suspect(%s, %s, %s);", (doc_no, suspect_id, conf_score))
        finally:
            conn.close()

    def sp_suspect_cases(self, suspect_id: int) -> List[Dict[str, Any]]:
        """Execute real Stored Procedure: sp_suspect_cases."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("CALL sp_suspect_cases(%s);", (suspect_id,))
                rows = cur.fetchall()
            for r in rows:
                if r.get("loss_amt") is not None: r["loss_amt"] = float(r["loss_amt"])
                if r.get("conf_score") is not None: r["conf_score"] = float(r["conf_score"])
            return rows
        except Exception:
            return []
        finally:
            conn.close()

    def sp_assign_investigator(self, doc_no: str, officer_id: str) -> None:
        """Execute real Stored Procedure: sp_assign_investigator."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("CALL sp_assign_investigator(%s, %s);", (doc_no, officer_id))
        finally:
            conn.close()

    def edit_docket(
        self,
        doc_no: str,
        crime_type: str,
        details: str,
        loss_amt: float,
        officer_id: str,
        changed_by: str = "INVESTIGATOR",
    ) -> None:
        """Update permitted fields with trigger-validated UPDATE."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE ncrp_incident_docket
                    SET crime_type = %s, details = %s, loss_amt = %s, officer_id = %s
                    WHERE doc_no = %s;
                    """,
                    (crime_type, details, loss_amt, officer_id, doc_no),
                )
                cur.execute(
                    """
                    INSERT INTO ncrp_audit_log (table_name, action, record_key, old_value, new_value, changed_by)
                    VALUES ('ncrp_incident_docket', 'UPDATE', %s, NULL, %s, %s);
                    """,
                    (doc_no, f"crime={crime_type}, loss={loss_amt}", changed_by),
                )
        finally:
            conn.close()

    def delete_docket(self, doc_no: str, changed_by: str = "ADMIN") -> None:
        """Delete docket; cascades to links and exhibits, fires trg_docket_after_delete."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM ncrp_docket_suspect_link WHERE doc_no = %s;", (doc_no,))
                cur.execute("DELETE FROM ncrp_docket_pattern_link WHERE doc_no = %s;", (doc_no,))
                cur.execute("DELETE FROM ncrp_forensic_evidence WHERE doc_no = %s;", (doc_no,))
                cur.execute("DELETE FROM ncrp_incident_docket WHERE doc_no = %s;", (doc_no,))
        finally:
            conn.close()

    def add_suspect(
        self,
        alias: str,
        phone: Optional[str],
        ip_addr: Optional[str],
        bank_acc: Optional[str],
        trace_notes: str,
        changed_by: str = "INVESTIGATOR",
    ) -> int:
        """Insert suspect into ncrp_suspect_entity."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO ncrp_suspect_entity (alias, phone, ip_addr, bank_acc, trace_notes)
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    (alias, phone or None, ip_addr or None, bank_acc or None, trace_notes),
                )
                new_id = cur.lastrowid
                cur.execute(
                    """
                    INSERT INTO ncrp_audit_log (table_name, action, record_key, old_value, new_value, changed_by)
                    VALUES ('ncrp_suspect_entity', 'INSERT', %s, NULL, %s, %s);
                    """,
                    (str(new_id), f"alias={alias}", changed_by),
                )
            return new_id
        finally:
            conn.close()

    def update_suspect(
        self,
        suspect_id: int,
        alias: str,
        phone: Optional[str],
        ip_addr: Optional[str],
        bank_acc: Optional[str],
        trace_notes: str,
        changed_by: str = "INVESTIGATOR",
    ) -> None:
        """Update suspect fields."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE ncrp_suspect_entity
                    SET alias = %s, phone = %s, ip_addr = %s, bank_acc = %s, trace_notes = %s
                    WHERE suspect_id = %s;
                    """,
                    (alias, phone or None, ip_addr or None, bank_acc or None, trace_notes, suspect_id),
                )
                cur.execute(
                    """
                    INSERT INTO ncrp_audit_log (table_name, action, record_key, old_value, new_value, changed_by)
                    VALUES ('ncrp_suspect_entity', 'UPDATE', %s, NULL, %s, %s);
                    """,
                    (str(suspect_id), f"alias={alias}", changed_by),
                )
        finally:
            conn.close()

    def delete_suspect(self, suspect_id: int, changed_by: str = "ADMIN") -> None:
        """Remove suspect and links."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM ncrp_docket_suspect_link WHERE suspect_id = %s;", (suspect_id,))
                cur.execute("DELETE FROM ncrp_suspect_entity WHERE suspect_id = %s;", (suspect_id,))
                cur.execute(
                    """
                    INSERT INTO ncrp_audit_log (table_name, action, record_key, old_value, new_value, changed_by)
                    VALUES ('ncrp_suspect_entity', 'DELETE', %s, 'EXISTS', 'DELETED', %s);
                    """,
                    (str(suspect_id), changed_by),
                )
        finally:
            conn.close()

    def add_forensic_evidence(
        self,
        evidence_id: str,
        doc_no: str,
        file_name: str,
        file_type: str,
        file_path: str,
        sha_hash: str,
        uploader_id: str,
    ) -> None:
        """Insert exhibit; fires trigger trg_evidence_after_insert into ncrp_audit_log."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO ncrp_forensic_evidence (evidence_id, doc_no, file_name, file_type, file_path, sha_hash, uploader_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """,
                    (evidence_id, doc_no, file_name, file_type, file_path, sha_hash, uploader_id),
                )
        finally:
            conn.close()

    def delete_evidence(self, evidence_id: str, changed_by: str = "INVESTIGATOR") -> None:
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM ncrp_forensic_evidence WHERE evidence_id = %s;", (evidence_id,))
                cur.execute(
                    """
                    INSERT INTO ncrp_audit_log (table_name, action, record_key, old_value, new_value, changed_by)
                    VALUES ('ncrp_forensic_evidence', 'DELETE', %s, 'EXISTS', 'DELETED', %s);
                    """,
                    (evidence_id, changed_by),
                )
        finally:
            conn.close()

    def add_pattern_cluster(
        self,
        cluster_id: str,
        pattern_type: str,
        pivot_val: str,
        risk_score: int = 50,
        changed_by: str = "INVESTIGATOR",
    ) -> None:
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO ncrp_pattern_cluster (cluster_id, pattern_type, pivot_val, risk_score)
                    VALUES (%s, %s, %s, %s);
                    """,
                    (cluster_id, pattern_type, pivot_val, int(risk_score)),
                )
                cur.execute(
                    """
                    INSERT INTO ncrp_audit_log (table_name, action, record_key, old_value, new_value, changed_by)
                    VALUES ('ncrp_pattern_cluster', 'INSERT', %s, NULL, %s, %s);
                    """,
                    (cluster_id, f"{pattern_type} | {pivot_val}", changed_by),
                )
        finally:
            conn.close()

    def delete_pattern_cluster(self, cluster_id: str, changed_by: str = "ADMIN") -> None:
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM ncrp_docket_pattern_link WHERE cluster_id = %s;", (cluster_id,))
                cur.execute("DELETE FROM ncrp_pattern_cluster WHERE cluster_id = %s;", (cluster_id,))
                cur.execute(
                    """
                    INSERT INTO ncrp_audit_log (table_name, action, record_key, old_value, new_value, changed_by)
                    VALUES ('ncrp_pattern_cluster', 'DELETE', %s, 'EXISTS', 'DELETED', %s);
                    """,
                    (cluster_id, changed_by),
                )
        finally:
            conn.close()

    def link_docket_pattern(self, doc_no: str, cluster_id: str) -> None:
        """Fires trigger trg_pattern_link_after_insert: increments cluster risk score."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO ncrp_docket_pattern_link (doc_no, cluster_id)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE matched_dt = CURRENT_TIMESTAMP;
                    """,
                    (doc_no, cluster_id),
                )
        finally:
            conn.close()

    def add_analytical_report(
        self,
        report_id: str,
        author_id: str,
        rep_type: str,
        doc_summary: str,
        doc_no: Optional[str],
        is_admissible: bool = True,
        changed_by: str = "ANALYST",
    ) -> None:
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO ncrp_analytical_report (report_id, author_id, rep_type, doc_summary, doc_no, is_admissible)
                    VALUES (%s, %s, %s, %s, %s, %s);
                    """,
                    (report_id, author_id, rep_type, doc_summary, doc_no or None, 1 if is_admissible else 0),
                )
                cur.execute(
                    """
                    INSERT INTO ncrp_audit_log (table_name, action, record_key, old_value, new_value, changed_by)
                    VALUES ('ncrp_analytical_report', 'INSERT', %s, NULL, %s, %s);
                    """,
                    (report_id, f"{rep_type} | {doc_no}", changed_by),
                )
        finally:
            conn.close()

    def delete_report(self, report_id: str, changed_by: str = "ADMIN") -> None:
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM ncrp_analytical_report WHERE report_id = %s;", (report_id,))
                cur.execute(
                    """
                    INSERT INTO ncrp_audit_log (table_name, action, record_key, old_value, new_value, changed_by)
                    VALUES ('ncrp_analytical_report', 'DELETE', %s, 'EXISTS', 'DELETED', %s);
                    """,
                    (report_id, changed_by),
                )
        finally:
            conn.close()

    def get_victim_dockets(self, victim_reg_id: str) -> List[Dict[str, Any]]:
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM ncrp_incident_docket WHERE victim_id = %s ORDER BY filed_dt DESC;",
                    (victim_reg_id,),
                )
                rows = cur.fetchall()
            conn.close()
            for r in rows:
                if r.get("loss_amt") is not None: r["loss_amt"] = float(r["loss_amt"])
            return rows
        except Exception:
            return []

    # =========================================================================
    # Relational Investigation Network Mapping
    # =========================================================================

    def get_investigation_network(self, doc_no: str) -> Dict[str, Any]:
        """Builds relational intelligence graph for a docket from live MySQL tables."""
        dockets = self.incident_dockets
        doc = dockets.get(doc_no)
        if not doc:
            return {}

        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # 1. Attributed suspects
                cur.execute(
                    """
                    SELECT s.suspect_id, s.alias, s.phone, s.ip_addr, s.bank_acc, l.conf_score
                    FROM ncrp_docket_suspect_link l
                    JOIN ncrp_suspect_entity s ON s.suspect_id = l.suspect_id
                    WHERE l.doc_no = %s;
                    """,
                    (doc_no,),
                )
                suspects = cur.fetchall()
                for s in suspects:
                    if s.get("conf_score") is not None: s["conf_score"] = float(s["conf_score"])

                # 2. Exhibits
                cur.execute(
                    """
                    SELECT evidence_id, doc_no, file_name, file_type, file_path, sha_hash, uploaded_dt as uploaded_at, uploader_id
                    FROM ncrp_forensic_evidence
                    WHERE doc_no = %s;
                    """,
                    (doc_no,),
                )
                evidence = cur.fetchall()

                # 3. Correlated pattern clusters and sibling dockets
                cur.execute(
                    """
                    SELECT c.cluster_id, c.pattern_type, c.pivot_val, c.risk_score
                    FROM ncrp_docket_pattern_link pl
                    JOIN ncrp_pattern_cluster c ON c.cluster_id = pl.cluster_id
                    WHERE pl.doc_no = %s;
                    """,
                    (doc_no,),
                )
                clusters = cur.fetchall()

                for c in clusters:
                    cur.execute(
                        """
                        SELECT doc_no FROM ncrp_docket_pattern_link
                        WHERE cluster_id = %s AND doc_no <> %s;
                        """,
                        (c["cluster_id"], doc_no),
                    )
                    siblings = [r["doc_no"] for r in cur.fetchall()]
                    c["sibling_dockets"] = siblings

                # 4. Reports
                cur.execute(
                    """
                    SELECT report_id, author_id, rep_type, generated_dt as created_at, is_admissible, doc_summary, doc_no
                    FROM ncrp_analytical_report
                    WHERE doc_no = %s;
                    """,
                    (doc_no,),
                )
                reports = cur.fetchall()

            profiles = self.registrant_profiles
            return {
                "docket": doc,
                "victim": profiles.get(doc.get("victim_id")),
                "officer": profiles.get(doc.get("officer_id")),
                "suspects": suspects,
                "evidence": evidence,
                "clusters": clusters,
                "reports": reports,
            }
        except Exception:
            return {}
        finally:
            conn.close()
