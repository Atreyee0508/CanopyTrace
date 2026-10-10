"""4-Stage Deterministic-Agentic Forensic Verification Pipeline Coordinator."""

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Ensure repository root is on sys.path for skills imports
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from canopytrace.alerts.dispatcher import dispatch_authority_alert
from canopytrace.core.harness import get_forensic_harness, BaseForensicHarness
from canopytrace.core.pattern_matcher import match_smuggling_patterns
from canopytrace.dossier.compiler import compile_evidentiary_dossier, compute_canonical_hash
from canopytrace.escalation.queue import enqueue_escalation
from canopytrace.schemas import ShippingManifest, PhysicalInspection, ForensicTriageOutput

# Import skills
from skills.cites_registry_check.check_registry import audit_manifest_registry
from skills.morphology_fingerprint.fingerprint import match_morphology_fingerprint


def run_forensic_pipeline(
    manifest: ShippingManifest,
    inspection: PhysicalInspection,
    case_id: Optional[str] = None,
    output_dir: Optional[Path] = None,
    db_path: Optional[Path] = None,
    harness: Optional[BaseForensicHarness] = None,
) -> Dict[str, Any]:
    """
    Executes the complete CanopyTrace 4-stage forensic triage pipeline:
      Stage 1: CITES Registry Check
      Stage 2: Morphology Fingerprinting
      Stage 3: Smuggling Modus Operandi Matching
      Stage 4: Gemma 2 Schema-Constrained Synthesis & Multi-Format Dossier Compilation
    """
    cid = case_id or f"CASE-{manifest.manifest_id}"
    if output_dir:
        out_dir = output_dir
    elif os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        out_dir = Path("/tmp/canopytrace/output") / cid
    else:
        out_dir = Path(__file__).resolve().parent.parent.parent.parent / "output" / cid

    # Stage 1: CITES Registry Check
    registry_res = audit_manifest_registry(manifest, db_path=db_path)

    # Stage 2: Morphology Fingerprinting
    morph_res = match_morphology_fingerprint(inspection, db_path=db_path)

    # Stage 3: Smuggling Pattern Matching
    pattern_res = match_smuggling_patterns(manifest, inspection, db_path=db_path)

    # Gemma Forensic Reasoning Synthesis
    llm_harness = harness or get_forensic_harness()
    forensic_output: ForensicTriageOutput = llm_harness.synthesize(
        manifest=manifest,
        inspection=inspection,
        registry_res=registry_res,
        morph_res=morph_res,
        pattern_res=pattern_res,
    )

    # Prepare preliminary case data for hashing
    raw_case_data: Dict[str, Any] = {
        "case_id": cid,
        "manifest": manifest.model_dump(),
        "inspection": inspection.model_dump(),
        "registry_audit": registry_res,
        "morphology_fingerprint": morph_res,
        "smuggling_patterns": pattern_res,
        "forensic_output": forensic_output.model_dump(),
    }
    sha256_digest = compute_canonical_hash(raw_case_data)

    # Operational Decision Hook 1: Automated Local Authority Alerting
    alert_payload = None
    if forensic_output.discrepancy_score >= 0.70:
        alert_payload = dispatch_authority_alert(
            case_id=cid,
            manifest=manifest,
            inspection=inspection,
            forensic=forensic_output,
            sha256_hash=sha256_digest,
        )

    # Operational Decision Hook 2: Novel Anomaly Escalation
    escalation_case = None
    if forensic_output.suspected_actual_species == "UNRESOLVED_NOVEL_ANOMALY":
        escalation_case = enqueue_escalation(
            case_id=cid,
            manifest=manifest,
            inspection=inspection,
            reason="Specimen features cannot be identified against known morphology identification keys.",
            db_path=db_path,
        )

    # Stage 4: Compile Multi-Format Evidentiary Dossier Package
    raw_case_data["alert_dispatched"] = alert_payload.model_dump() if alert_payload else None
    raw_case_data["escalation"] = escalation_case.model_dump() if escalation_case else None

    dossier_meta = compile_evidentiary_dossier(raw_case_data, out_dir)

    return {
        "case_id": cid,
        "discrepancy_score": forensic_output.discrepancy_score,
        "suspected_species": forensic_output.suspected_actual_species,
        "cites_appendix": forensic_output.cites_appendix,
        "flagged_indicators": forensic_output.flagged_indicators,
        "smuggling_mos": forensic_output.smuggling_mo_detected,
        "forensic_output": forensic_output,
        "alert_dispatched": alert_payload is not None,
        "alert_payload": alert_payload,
        "is_novel_escalation": escalation_case is not None,
        "dossier_package": dossier_meta,
    }
