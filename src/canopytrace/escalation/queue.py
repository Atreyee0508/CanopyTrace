"""Novel Anomaly Escalation Queue for Higher Scientific / CITES Authority Review."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from canopytrace.db import get_db_connection
from canopytrace.schemas import EscalationCase, ShippingManifest, PhysicalInspection

import os

if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    DEFAULT_ESCALATION_DIR = Path("/tmp/canopytrace/data/escalations")
else:
    DEFAULT_ESCALATION_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "escalations"


def enqueue_escalation(
    case_id: str,
    manifest: ShippingManifest,
    inspection: PhysicalInspection,
    reason: str,
    escalation_dir: Optional[Path] = None,
    db_path: Optional[Path] = None,
) -> EscalationCase:
    """
    Enqueues an unrecognized or ambiguous specimen for Higher Scientific Authority review.
    """
    target_dir = escalation_dir or DEFAULT_ESCALATION_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    escalation_id = f"ESC-{case_id}"
    esc_case = EscalationCase(
        case_id=case_id,
        escalation_id=escalation_id,
        checkpoint_location=inspection.checkpoint_location,
        manifest_summary=manifest.model_dump(mode="json"),
        observed_measurements=[m.model_dump(mode="json") for m in inspection.measurements],
        reason_for_escalation=reason,
        status="PENDING_AUTHORITY_REVIEW",
    )

    # 1. Write file
    file_path = target_dir / f"{case_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(esc_case.model_dump_json(indent=2))

    # 2. Record in SQLite
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO escalation_records (
            case_id, escalation_id, created_at, checkpoint_location,
            manifest_summary, observed_measurements, reason, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        case_id,
        escalation_id,
        esc_case.created_at.isoformat(),
        inspection.checkpoint_location,
        json.dumps(esc_case.manifest_summary, default=str),
        json.dumps(esc_case.observed_measurements, default=str),
        reason,
        "PENDING_AUTHORITY_REVIEW",
    ))
    conn.commit()
    conn.close()

    return esc_case


def list_pending_escalations(
    escalation_dir: Optional[Path] = None,
    db_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Lists all pending escalation cases."""
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM escalation_records WHERE status = 'PENDING_AUTHORITY_REVIEW'")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]
