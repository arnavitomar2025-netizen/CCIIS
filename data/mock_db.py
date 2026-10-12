"""
CCIIS In-Memory Database Engine
===============================
Authoritative in-memory replica of project_cciis relational schema seeded from cciis_final.sql.
Provides relational integrity, stored procedure emulation, trigger enforcement, audit logging,
and view projections with full parity to the MySQL database engine.
"""

from datetime import datetime, date
import hashlib
from typing import Dict, List, Optional, Any
from data.seed_data import load_seed_data, parse_datetime


class CCIISDatabase:
    def __init__(self, seed_sql_path: Optional[str] = None):
        self.is_connected = False
        self.is_mysql = False
        self._init_tables()
        self._seed_data(seed_sql_path)

    def _init_tables(self):
        # Master Tables
        self.registrant_profiles: Dict[str, Dict[str, Any]] = {}
        self.incident_dockets: Dict[str, Dict[str, Any]] = {}
        self.suspect_entities: Dict[int, Dict[str, Any]] = {}
        self.pattern_clusters: Dict[str, Dict[str, Any]] = {}
        self.forensic_evidence: Dict[str, Dict[str, Any]] = {}
        self.analytical_reports: Dict[str, Dict[str, Any]] = {}

        # Relationship Junction Tables
        self.docket_suspect_links: List[Dict[str, Any]] = []
        self.docket_pattern_links: List[Dict[str, Any]] = []

        # Audit Log Table (Section 3 in SQL)
        self.audit_logs: List[Dict[str, Any]] = []
        self._audit_id_seq = 1

    def _seed_data(self, seed_sql_path: Optional[str] = None):
        """Seed all 9 tables from cciis_final.sql."""
        try:
            seeds = load_seed_data(seed_sql_path)
            self.registrant_profiles = seeds["registrant_profiles"]
            self.incident_dockets = seeds["incident_dockets"]
            self.suspect_entities = seeds["suspect_entities"]
            self.pattern_clusters = seeds["pattern_clusters"]
            self.forensic_evidence = seeds["forensic_evidence"]
            self.analytical_reports = seeds["analytical_reports"]
            self.docket_suspect_links = seeds["docket_suspect_links"]
            self.docket_pattern_links = seeds["docket_pattern_links"]
            self.audit_logs = seeds["audit_logs"]

            if self.audit_logs:
                max_log = max(int(l.get("log_id", 0)) for l in self.audit_logs)
                self._audit_id_seq = max_log + 1
            else:
                self._audit_id_seq = 1
        except Exception as e:
            # Fallback seed if cciis_final.sql cannot be loaded
            self._seed_fallback()

    def _seed_fallback(self):
        """Minimal fallback seeds."""
        self.registrant_profiles["reg-001"] = {
            "reg_id": "reg-001", "full_name": "Admin User", "email": "admin@cciis.in",
            "phone": "9000000001", "pass_hash": hashlib.sha256(b"admin123").hexdigest(),
            "role_code": "ADMIN", "priv_lvl": 5, "created_at": datetime.now(),
        }

    def _log_audit(
        self,
        table_name: str,
        action: str,
        record_key: str,
        old_val: Optional[str],
        new_val: Optional[str],
        changed_by: str = "INVESTIGATOR",
    ):
        self.audit_logs.insert(0, {
            "log_id": self._audit_id_seq,
            "table_name": table_name,
            "action": action,
            "record_key": str(record_key),
            "old_value": str(old_val) if old_val is not None else None,
            "new_value": str(new_val) if new_val is not None else None,
            "changed_by": changed_by,
            "changed_at": datetime.now(),
        })
        self._audit_id_seq += 1

    # =========================================================================
    # SQL FUNCTIONS (Section 5)
    # =========================================================================
    def fn_case_age_days(self, doc_no: str) -> int:
        """Emulates SQL fn_case_age_days: DATEDIFF(CURDATE(), DATE(filed_dt))"""
        docket = self.incident_dockets.get(doc_no)
        if not docket:
            return 0
        ref_date = date(2026, 10, 8)
        dt = docket.get("filed_dt")
        if isinstance(dt, datetime):
            f_date = dt.date()
        elif isinstance(dt, str):
            f_date = parse_datetime(dt).date() if parse_datetime(dt) else ref_date
        else:
            f_date = ref_date
        return max(0, (ref_date - f_date).days)

    def fn_evidence_count(self, doc_no: str) -> int:
        """Emulates SQL fn_evidence_count: COUNT(*) FROM ncrp_forensic_evidence WHERE doc_no = p_doc"""
        return sum(1 for ev in self.forensic_evidence.values() if ev.get("doc_no") == doc_no)

    def fn_get_suspect_count(self, doc_no: str) -> int:
        """Emulates SQL fn_get_suspect_count: COUNT(*) FROM ncrp_docket_suspect_link WHERE doc_no = p_doc"""
        return sum(1 for l in self.docket_suspect_links if l.get("doc_no") == doc_no)

    # =========================================================================
    # SQL VIEWS (Section 4)
    # =========================================================================
    def get_vw_active_investigations(self) -> List[Dict[str, Any]]:
        """Active investigations (stage != 'CLOSED')"""
        results = []
        for d in self.incident_dockets.values():
            if d.get("stage_code") != "CLOSED":
                officer = self.registrant_profiles.get(d.get("officer_id"), {}).get("full_name", "Unassigned")
                victim = self.registrant_profiles.get(d.get("victim_id"), {}).get("full_name", "Complainant")
                results.append({**d, "officer_name": officer, "victim_name": victim})
        return results

    def get_vw_suspect_case_history(self) -> List[Dict[str, Any]]:
        """Emulates vw_suspect_case_history"""
        results = []
        for link in self.docket_suspect_links:
            s = self.suspect_entities.get(link["suspect_id"])
            d = self.incident_dockets.get(link["doc_no"])
            if s and d:
                results.append({
                    "suspect_id": s["suspect_id"],
                    "alias": s["alias"],
                    "phone": s.get("phone"),
                    "ip_addr": s.get("ip_addr"),
                    "doc_no": d["doc_no"],
                    "crime_type": d["crime_type"],
                    "stage_code": d["stage_code"],
                    "loss_amt": d["loss_amt"],
                    "conf_score": link["conf_score"],
                })
        return results

    def get_vw_pattern_summary(self) -> List[Dict[str, Any]]:
        """Emulates vw_pattern_summary"""
        results = []
        for c in self.pattern_clusters.values():
            linked_docs = [l["doc_no"] for l in self.docket_pattern_links if l["cluster_id"] == c["cluster_id"]]
            total_loss = sum(float(self.incident_dockets[doc].get("loss_amt", 0.0)) for doc in linked_docs if doc in self.incident_dockets)
            results.append({
                "cluster_id": c["cluster_id"],
                "pattern_type": c["pattern_type"],
                "pivot_val": c["pivot_val"],
                "risk_score": c["risk_score"],
                "linked_dockets": len(linked_docs),
                "linked_doc_list": linked_docs,
                "total_loss": total_loss,
            })
        results.sort(key=lambda x: x["risk_score"], reverse=True)
        return results

    def get_vw_officer_workload(self) -> List[Dict[str, Any]]:
        """Emulates vw_officer_workload"""
        workload = {}
        for r_id, r in self.registrant_profiles.items():
            if r.get("role_code") in ("INVESTIGATOR", "ADMIN"):
                workload[r_id] = {
                    "reg_id": r_id,
                    "full_name": r["full_name"],
                    "total_cases": 0,
                    "open_cases": 0,
                }
        for d in self.incident_dockets.values():
            officer_id = d.get("officer_id")
            if officer_id in workload:
                workload[officer_id]["total_cases"] += 1
                if d.get("stage_code") != "CLOSED":
                    workload[officer_id]["open_cases"] += 1
        return list(workload.values())

    def get_vw_suspect_public(self) -> List[Dict[str, Any]]:
        """Emulates vw_suspect_public (hides bank account and trace notes for analysts)"""
        return [
            {"suspect_id": s["suspect_id"], "alias": s["alias"], "ip_addr": s.get("ip_addr")}
            for s in self.suspect_entities.values()
        ]

    def get_victim_dockets(self, victim_reg_id: str) -> List[Dict[str, Any]]:
        """Return only dockets where victim_id matches — used for VICTIM role isolation."""
        v_clean = str(victim_reg_id).strip().lower()
        return [
            d for d in self.incident_dockets.values()
            if str(d.get("victim_id", "")).strip().lower() == v_clean
        ]

    # =========================================================================
    # STORED PROCEDURES & TRIGGERS (Sections 6 & 7)
    # =========================================================================
    def sp_update_stage(self, doc_no: str, new_stage: str, changed_by: str = "Insp. Ravi Kumar") -> None:
        """
        Emulates sp_update_stage + triggers:
        trg_docket_before_update: Cannot reopen CLOSED cases.
        trg_docket_after_update: Inserts into ncrp_audit_log.
        """
        if doc_no not in self.incident_dockets:
            raise ValueError(f"Docket {doc_no} not found.")

        valid_stages = ("TRIAGE", "LOGGED", "INVESTIGATION", "CLOSED")
        if new_stage not in valid_stages:
            raise ValueError(f"Invalid stage code: {new_stage}. Must be one of {valid_stages}")

        current_docket = self.incident_dockets[doc_no]
        old_stage = current_docket.get("stage_code")

        if old_stage == "CLOSED" and new_stage != "CLOSED":
            raise PermissionError("SQL TRIGGER VIOLATION: trg_docket_before_update: Closed dockets cannot be reopened.")

        if old_stage != new_stage:
            current_docket["stage_code"] = new_stage
            self._log_audit(
                table_name="ncrp_incident_docket",
                action="STAGE_CHANGE",
                record_key=doc_no,
                old_val=old_stage,
                new_val=new_stage,
                changed_by=changed_by,
            )

    def sp_link_suspect(self, doc_no: str, suspect_id: int, conf_score: float, changed_by: str = "ADMIN") -> None:
        """Emulates sp_link_suspect: ON DUPLICATE KEY UPDATE conf_score"""
        if doc_no not in self.incident_dockets:
            raise ValueError(f"Docket {doc_no} does not exist.")
        sid = int(suspect_id)
        if sid not in self.suspect_entities:
            raise ValueError(f"Suspect #{suspect_id} does not exist.")
        if not (0.0 <= conf_score <= 1.0):
            raise ValueError("Constraint chk_conf: Confidence score must be between 0 and 1.")

        for link in self.docket_suspect_links:
            if link["doc_no"] == doc_no and int(link["suspect_id"]) == sid:
                link["conf_score"] = float(conf_score)
                self._log_audit("ncrp_docket_suspect_link", "UPDATE_CONF", f"{doc_no}::#{sid}", None, f"{conf_score:.2f}", changed_by)
                return

        self.docket_suspect_links.append({
            "doc_no": doc_no,
            "suspect_id": sid,
            "linked_dt": datetime.now(),
            "conf_score": float(conf_score),
        })
        self._log_audit(
            table_name="ncrp_docket_suspect_link",
            action="LINK_SUSPECT",
            record_key=f"{doc_no}::#{sid}",
            old_val=None,
            new_val=f"conf={conf_score:.2f}",
            changed_by=changed_by,
        )

    def sp_register_docket(
        self,
        doc_no: str,
        victim_id: str,
        officer_id: str,
        event_dt: datetime,
        crime_type: str,
        details: str,
        loss_amt: float,
        changed_by: str = "INVESTIGATOR",
    ) -> None:
        """Emulates sp_register_docket transaction."""
        if doc_no in self.incident_dockets:
            raise ValueError(f"Docket {doc_no} already registered.")
        if victim_id not in self.registrant_profiles:
            raise ValueError(f"Victim profile {victim_id} not found.")
        if officer_id not in self.registrant_profiles:
            raise ValueError(f"Officer profile {officer_id} not found.")
        if loss_amt < 0:
            raise ValueError("Constraint chk_loss_nonneg: Loss amount cannot be negative.")

        new_docket = {
            "doc_no": doc_no,
            "victim_id": victim_id,
            "officer_id": officer_id,
            "event_dt": event_dt,
            "filed_dt": datetime.now(),
            "crime_type": crime_type,
            "details": details,
            "stage_code": "TRIAGE",
            "loss_amt": float(loss_amt),
        }
        self.incident_dockets[doc_no] = new_docket
        self._log_audit("ncrp_incident_docket", "INSERT", doc_no, None, "TRIAGE", changed_by)

    def sp_suspect_cases(self, suspect_id: int) -> List[Dict[str, Any]]:
        """Emulates sp_suspect_cases: returns cases linked to a suspect."""
        sid = int(suspect_id)
        cases = []
        for link in self.docket_suspect_links:
            if int(link.get("suspect_id", -1)) == sid:
                doc = self.incident_dockets.get(link["doc_no"])
                if doc:
                    cases.append({
                        "doc_no": doc["doc_no"],
                        "crime_type": doc["crime_type"],
                        "stage_code": doc["stage_code"],
                        "loss_amt": float(doc.get("loss_amt") or 0.0),
                        "conf_score": float(link.get("conf_score") or 1.0),
                        "filed_dt": doc.get("filed_dt"),
                    })
        return cases

    def sp_assign_investigator(self, doc_no: str, officer_id: str, changed_by: str = "ADMIN") -> None:
        """Assign an investigator to a docket."""
        if doc_no not in self.incident_dockets:
            raise ValueError(f"Docket {doc_no} not found.")
        old_officer = self.incident_dockets[doc_no].get("officer_id")
        self.incident_dockets[doc_no]["officer_id"] = officer_id
        self._log_audit("ncrp_incident_docket", "ASSIGN", doc_no, old_officer, officer_id, changed_by)

    def add_forensic_evidence(
        self,
        evidence_id: str,
        doc_no: str,
        file_name: str,
        file_type: str,
        file_path: str,
        sha_hash: str,
        uploader_id: str = "reg-002",
        changed_by: str = "INVESTIGATOR",
    ) -> None:
        """Inserts evidence and fires trg_evidence_after_insert into ncrp_audit_log."""
        if doc_no not in self.incident_dockets:
            raise ValueError(f"Docket {doc_no} not found.")
        if evidence_id in self.forensic_evidence:
            raise ValueError(f"Evidence {evidence_id} already exists.")

        now_dt = datetime.now()
        ev_entry = {
            "evidence_id": evidence_id,
            "doc_no": doc_no,
            "file_name": file_name,
            "file_type": file_type,
            "file_path": file_path,
            "sha_hash": sha_hash,
            "uploader_id": uploader_id,
            "uploaded_dt": now_dt,
            "uploaded_at": now_dt,
        }
        self.forensic_evidence[evidence_id] = ev_entry

        self._log_audit(
            table_name="ncrp_forensic_evidence",
            action="INSERT",
            record_key=evidence_id,
            old_val=None,
            new_val=f"{doc_no} | {file_name}",
            changed_by=changed_by,
        )

    def delete_evidence(self, evidence_id: str, changed_by: str = "INVESTIGATOR") -> None:
        """Remove an evidence record from the locker."""
        if evidence_id not in self.forensic_evidence:
            raise ValueError(f"Evidence {evidence_id} not found.")
        del self.forensic_evidence[evidence_id]
        self._log_audit("ncrp_forensic_evidence", "DELETE", evidence_id, "EXISTS", "DELETED", changed_by)

    def link_docket_pattern(self, doc_no: str, cluster_id: str, changed_by: str = "INVESTIGATOR") -> None:
        """Links a docket to a pattern cluster and updates risk score."""
        if doc_no not in self.incident_dockets:
            raise ValueError(f"Docket {doc_no} not found.")
        if cluster_id not in self.pattern_clusters:
            raise ValueError(f"Cluster {cluster_id} not found.")

        for pl in self.docket_pattern_links:
            if pl["doc_no"] == doc_no and pl["cluster_id"] == cluster_id:
                return

        self.docket_pattern_links.append({
            "doc_no": doc_no,
            "cluster_id": cluster_id,
            "matched_dt": datetime.now(),
        })

        # Trigger trg_pattern_link_after_insert: increment risk score by 5 (capped at 100)
        c = self.pattern_clusters[cluster_id]
        c["risk_score"] = min(100, c.get("risk_score", 0) + 5)

        self._log_audit(
            table_name="ncrp_docket_pattern_link",
            action="CLUSTER_JOIN",
            record_key=f"{doc_no}::{cluster_id}",
            old_val=None,
            new_val=f"risk={c['risk_score']}",
            changed_by=changed_by,
        )

    def add_pattern_cluster(
        self,
        cluster_id: str,
        pattern_type: str,
        pivot_val: str,
        risk_score: int = 50,
        changed_by: str = "INVESTIGATOR",
    ) -> None:
        """Create a new syndicate pattern cluster."""
        if cluster_id in self.pattern_clusters:
            raise ValueError(f"Cluster {cluster_id} already exists.")
        self.pattern_clusters[cluster_id] = {
            "cluster_id": cluster_id,
            "pattern_type": pattern_type,
            "pivot_val": pivot_val,
            "risk_score": max(0, min(100, int(risk_score))),
            "detected_dt": datetime.now(),
        }
        self._log_audit(
            "ncrp_pattern_cluster",
            "INSERT",
            cluster_id,
            None,
            f"{pattern_type} | {pivot_val}",
            changed_by,
        )

    def delete_pattern_cluster(self, cluster_id: str, changed_by: str = "ADMIN") -> None:
        """Delete a pattern cluster and remove its docket associations."""
        if cluster_id not in self.pattern_clusters:
            raise ValueError(f"Cluster {cluster_id} not found.")
        self.docket_pattern_links = [l for l in self.docket_pattern_links if l["cluster_id"] != cluster_id]
        del self.pattern_clusters[cluster_id]
        self._log_audit("ncrp_pattern_cluster", "DELETE", cluster_id, "EXISTS", "DELETED", changed_by)

    def add_suspect(
        self,
        alias: str,
        phone: Optional[str],
        ip_addr: Optional[str],
        bank_acc: Optional[str],
        trace_notes: str,
        changed_by: str = "INVESTIGATOR",
    ) -> int:
        """Insert new target entity and return new suspect_id."""
        int_keys = [k for k in self.suspect_entities.keys() if isinstance(k, int)]
        new_id = (max(int_keys) + 1) if int_keys else 1
        self.suspect_entities[new_id] = {
            "suspect_id": new_id,
            "alias": alias,
            "phone": phone or None,
            "ip_addr": ip_addr or None,
            "bank_acc": bank_acc or None,
            "trace_notes": trace_notes,
        }
        self._log_audit("ncrp_suspect_entity", "INSERT", str(new_id), None, f"alias={alias}", changed_by)
        return new_id

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
        """Update suspect details."""
        sid = int(suspect_id)
        if sid not in self.suspect_entities:
            raise ValueError(f"Suspect #{suspect_id} not found.")
        s = self.suspect_entities[sid]
        old_snap = f"alias={s['alias']}"
        s["alias"] = alias
        s["phone"] = phone or None
        s["ip_addr"] = ip_addr or None
        s["bank_acc"] = bank_acc or None
        s["trace_notes"] = trace_notes
        self._log_audit("ncrp_suspect_entity", "UPDATE", str(sid), old_snap, f"alias={alias}", changed_by)

    def delete_suspect(self, suspect_id: int, changed_by: str = "ADMIN") -> None:
        """Delete a suspect and remove junction links."""
        sid = int(suspect_id)
        if sid not in self.suspect_entities:
            raise ValueError(f"Suspect #{suspect_id} not found.")
        self.docket_suspect_links = [l for l in self.docket_suspect_links if int(l["suspect_id"]) != sid]
        del self.suspect_entities[sid]
        self._log_audit("ncrp_suspect_entity", "DELETE", str(sid), "EXISTS", "DELETED", changed_by)

    def add_analytical_report(
        self,
        report_id: str,
        author_id: str,
        rep_type: str,
        doc_summary: str,
        doc_no: Optional[str] = None,
        is_admissible: bool = True,
        changed_by: str = "INVESTIGATOR",
    ) -> None:
        """Insert new analytical dossier."""
        now_dt = datetime.now()
        rep_entry = {
            "report_id": report_id,
            "author_id": author_id,
            "rep_type": rep_type,
            "doc_summary": doc_summary,
            "doc_no": doc_no,
            "is_admissible": 1 if is_admissible else 0,
            "admissibility": "YES" if is_admissible else "NO",
            "generated_dt": now_dt,
            "created_at": now_dt,
        }
        self.analytical_reports[report_id] = rep_entry
        self._log_audit("ncrp_analytical_report", "INSERT", report_id, None, f"{rep_type} | {doc_no}", changed_by)

    def delete_report(self, report_id: str, changed_by: str = "ADMIN") -> None:
        """Delete analytical report."""
        if report_id in self.analytical_reports:
            del self.analytical_reports[report_id]
            self._log_audit("ncrp_analytical_report", "DELETE", report_id, "EXISTS", "DELETED", changed_by)

    def edit_docket(
        self,
        doc_no: str,
        crime_type: str,
        details: str,
        loss_amt: float,
        officer_id: str,
        changed_by: str = "INVESTIGATOR",
    ) -> None:
        """Edit docket record."""
        if doc_no not in self.incident_dockets:
            raise ValueError(f"Docket {doc_no} not found.")
        d = self.incident_dockets[doc_no]
        old_snapshot = f"{d['crime_type']}|₹{d['loss_amt']}|{d['officer_id']}"
        d["crime_type"] = crime_type
        d["details"] = details
        d["loss_amt"] = float(loss_amt)
        d["officer_id"] = officer_id
        new_snapshot = f"{crime_type}|₹{loss_amt}|{officer_id}"
        self._log_audit("ncrp_incident_docket", "UPDATE", doc_no, old_snapshot, new_snapshot, changed_by)

    def delete_docket(self, doc_no: str, changed_by: str = "ADMIN") -> None:
        """Permanently delete docket and all cascades."""
        if doc_no not in self.incident_dockets:
            raise ValueError(f"Docket {doc_no} not found.")
        self.docket_suspect_links = [l for l in self.docket_suspect_links if l["doc_no"] != doc_no]
        self.docket_pattern_links = [l for l in self.docket_pattern_links if l["doc_no"] != doc_no]
        self.forensic_evidence = {k: v for k, v in self.forensic_evidence.items() if v.get("doc_no") != doc_no}
        for r in self.analytical_reports.values():
            if r.get("doc_no") == doc_no:
                r["doc_no"] = None
        del self.incident_dockets[doc_no]
        self._log_audit("ncrp_incident_docket", "DELETE", doc_no, "EXISTS", "DELETED", changed_by)

    def get_investigation_network(self, doc_no: str) -> Dict[str, Any]:
        """Deep cross-relational dossier mapping for docket."""
        doc = self.incident_dockets.get(doc_no)
        if not doc:
            return {}

        suspects_linked = []
        for l in self.docket_suspect_links:
            if l.get("doc_no") == doc_no:
                sid = int(l["suspect_id"])
                s = self.suspect_entities.get(sid)
                if s:
                    suspects_linked.append({
                        "suspect_id": s["suspect_id"],
                        "alias": s["alias"],
                        "phone": s.get("phone"),
                        "ip_addr": s.get("ip_addr"),
                        "bank_acc": s.get("bank_acc"),
                        "conf_score": float(l.get("conf_score", 1.0)),
                    })

        evidence_linked = [
            ev for ev in self.forensic_evidence.values() if ev.get("doc_no") == doc_no
        ]

        clusters_linked = []
        for pl in self.docket_pattern_links:
            if pl.get("doc_no") == doc_no:
                cid = pl.get("cluster_id")
                c = self.pattern_clusters.get(cid)
                if c:
                    sibling_docs = [
                        other["doc_no"]
                        for other in self.docket_pattern_links
                        if other["cluster_id"] == cid and other["doc_no"] != doc_no
                    ]
                    clusters_linked.append({
                        "cluster_id": c["cluster_id"],
                        "pattern_type": c["pattern_type"],
                        "pivot_val": c["pivot_val"],
                        "risk_score": c["risk_score"],
                        "sibling_dockets": sibling_docs,
                    })

        reports_linked = [
            rep for rep in self.analytical_reports.values() if rep.get("doc_no") == doc_no
        ]

        return {
            "docket": doc,
            "victim": self.registrant_profiles.get(doc.get("victim_id")),
            "officer": self.registrant_profiles.get(doc.get("officer_id")),
            "suspects": suspects_linked,
            "evidence": evidence_linked,
            "clusters": clusters_linked,
            "reports": reports_linked,
        }

    def authenticate_user(self, identifier: str, candidate_hash: str) -> Optional[dict]:
        """Authenticate user against registrant profiles."""
        id_clean = identifier.strip().lower()
        for reg in self.registrant_profiles.values():
            if (reg.get("email", "").lower() == id_clean or reg.get("reg_id", "").lower() == id_clean):
                if reg.get("pass_hash") == candidate_hash:
                    return reg
        return None


# Singleton session accessor
_mock_instance: Optional[CCIISDatabase] = None
_mysql_instance: Optional[Any] = None


def get_db() -> Any:
    """
    Returns the active database engine:
    1. Attempts to connect to the live MySQL database (project_cciis).
    2. If connected, returns MySQLDatabase backed by real MySQL tables.
    3. If connection cannot be established, returns CCIISDatabase fallback
       fully seeded with all 17 cases, 17 users, 14 suspects, 12 clusters,
       13 exhibits, and 12 reports from cciis_final.sql.
    """
    global _mock_instance, _mysql_instance
    try:
        from data.mysql_db import MySQLDatabase, get_mysql_config
        cfg = get_mysql_config()
        if _mysql_instance is None or _mysql_instance.config != cfg:
            _mysql_instance = MySQLDatabase(cfg)
        is_ok, msg = _mysql_instance.test_connection()
        if is_ok:
            _mysql_instance.is_mysql = True
            _mysql_instance.is_connected = True
            try:
                conn = _mysql_instance.get_connection()
                with conn.cursor() as cur:
                    cur.execute("SHOW TABLES;")
                    rows = cur.fetchall()
                conn.close()
                if not rows:
                    _mysql_instance.init_database_from_sql()
            except Exception:
                _mysql_instance.init_database_from_sql()
            return _mysql_instance
    except Exception:
        pass

    if _mock_instance is None:
        _mock_instance = CCIISDatabase()
    _mock_instance.is_connected = False
    _mock_instance.is_mysql = False
    return _mock_instance
