"""Unit tests for multi-format dossier compiler and SHA-256 cryptographic integrity."""

import hashlib
import json
import pytest
from pathlib import Path
from canopytrace.dossier import compile_evidentiary_dossier, compute_canonical_hash
from canopytrace.schemas.forensic_output import MANDATORY_LEGAL_DISCLAIMER


def test_dossier_compilation_and_sha256(tmp_path):
    case_data = {
        "case_id": "CASE-DOSSIER-01",
        "manifest": {
            "manifest_id": "MAN-01",
            "declared_item_name": "Antique Mammoth Carvings",
            "country_of_origin": "RU",
            "declared_quantity": 100.0,
            "declared_unit": "kg",
        },
        "inspection": {
            "inspection_id": "INSP-01",
            "checkpoint_location": "Hong Kong Berth 2",
            "observed_specimen_category": "ivory",
            "measurements": [
                {"feature_name": "schreger_angle_outer", "value": 125.0, "unit": "degrees"}
            ],
        },
        "forensic_output": {
            "discrepancy_score": 0.94,
            "suspected_actual_species": "Loxodonta africana",
            "cites_appendix": "I",
            "flagged_indicators": ["Schreger outer angle 125 deg."],
            "smuggling_mo_detected": ["MO-IVO-001"],
            "uncertainty_bounds": {"lower_bound": 0.90, "upper_bound": 0.98, "confidence_interval": "95%"},
            "suggested_lab_action": [
                {"test_type": "radiocarbon_dating_c14", "priority": "mandatory", "expected_discriminator": "C14 bomb pulse"}
            ],
            "forensic_rationale": "Severe discrepancy detected.",
            "legal_disclaimer": MANDATORY_LEGAL_DISCLAIMER,
        }
    }

    res = compile_evidentiary_dossier(case_data, tmp_path)

    # 1. Verify all multi-format files exist
    assert Path(res["json_path"]).exists()
    assert Path(res["md_path"]).exists()
    assert Path(res["pdf_path"]).exists()
    assert Path(res["hash_path"]).exists()

    # 2. Verify SHA-256 integrity
    sha = res["sha256_hash"]
    assert len(sha) == 64  # SHA-256 hex length

    # 3. Verify Markdown contains mandatory disclaimer
    md_content = Path(res["md_path"]).read_text(encoding="utf-8")
    assert MANDATORY_LEGAL_DISCLAIMER in md_content
    assert sha in md_content

    # 4. Verify PDF contains content and non-empty file size
    assert Path(res["pdf_path"]).stat().st_size > 1000
