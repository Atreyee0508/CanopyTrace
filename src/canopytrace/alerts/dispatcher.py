"""Automated Local Authority Alert Dispatcher."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import requests

from canopytrace.schemas import AuthorityAlertPayload, ForensicTriageOutput, ShippingManifest, PhysicalInspection

DEFAULT_ALERT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data" / "alerts"
SEIZURE_THRESHOLD = 0.70


def dispatch_authority_alert(
    case_id: str,
    manifest: ShippingManifest,
    inspection: PhysicalInspection,
    forensic: ForensicTriageOutput,
    sha256_hash: str,
    alert_dir: Optional[Path] = None,
    webhook_url: Optional[str] = None,
) -> Optional[AuthorityAlertPayload]:
    """
    Automatically dispatches an urgent incident alert to local customs and law enforcement
    authorities when discrepancy_score >= SEIZURE_THRESHOLD (0.70).
    """
    if forensic.discrepancy_score < SEIZURE_THRESHOLD:
        return None

    target_dir = alert_dir or DEFAULT_ALERT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    alert_id = f"ALT-{case_id}"
    severity = "CRITICAL" if forensic.discrepancy_score >= 0.85 else "HIGH"

    payload = AuthorityAlertPayload(
        alert_id=alert_id,
        case_id=case_id,
        port_location=inspection.checkpoint_location,
        waybill_number=manifest.waybill_number,
        severity=severity,
        discrepancy_score=forensic.discrepancy_score,
        declared_item=manifest.declared_item_name,
        suspected_taxa=forensic.suspected_actual_species,
        cites_appendix=forensic.cites_appendix,
        matched_smuggling_mos=forensic.smuggling_mo_detected,
        recommended_immediate_action="DETAIN_CONTAINER_AND_DISPATCH_CONFIRMATORY_LAB_SAMPLE",
        cryptographic_sha256=sha256_hash,
    )

    # 1. Write local auditable incident spool file
    alert_file = target_dir / f"alert_{case_id}.json"
    with open(alert_file, "w", encoding="utf-8") as f:
        f.write(payload.model_dump_json(indent=2))

    # 2. Dispatch to webhook if configured
    url = webhook_url or os.environ.get("CANOPYTRACE_ALERT_WEBHOOK_URL")
    if url:
        try:
            requests.post(url, json=payload.model_dump(), timeout=5)
        except Exception as e:
            print(f"[CanopyTrace Alerts] Webhook dispatch notice: {e}")

    return payload
