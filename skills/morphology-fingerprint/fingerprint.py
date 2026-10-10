#!/usr/bin/env python3
"""
Standalone runner script and module for the morphology-fingerprint skill.
Complies with agentskills.io standard.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from canopytrace.db import get_morphology_rules
from canopytrace.schemas import PhysicalInspection


def _evaluate_rule(val: Any, op: str, thresh: Any) -> bool:
    """Evaluates a single morphological condition."""
    try:
        if op == "gt":
            return float(val) > float(thresh)
        elif op == "lt":
            return float(val) < float(thresh)
        elif op == "eq":
            if isinstance(val, str) and isinstance(thresh, str):
                return val.strip().lower() == thresh.strip().lower()
            return val == thresh
        elif op == "between" and isinstance(thresh, list) and len(thresh) == 2:
            return float(thresh[0]) <= float(val) <= float(thresh[1])
        elif op == "in" and isinstance(thresh, list):
            if isinstance(val, str):
                return val.strip().lower() in [str(t).strip().lower() for t in thresh]
            return val in thresh
        return False
    except (ValueError, TypeError):
        return False


def match_morphology_fingerprint(
    inspection: PhysicalInspection,
    db_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Evaluates physical inspection measurements against forensic identification keys.
    """
    domain = inspection.observed_specimen_category.strip().lower()
    # Normalize domain aliases
    if "tusk" in domain or "ivory" in domain:
        domain = "ivory"
    elif "wood" in domain or "timber" in domain:
        domain = "timber"
    elif "scale" in domain or "keratin" in domain or "pangolin" in domain:
        domain = "keratin_scales"
    elif "bone" in domain:
        domain = "bone"
    elif "turtle" in domain or "bekko" in domain:
        domain = "marine_reptile"

    rules = get_morphology_rules(db_path=db_path)

    # Index observed measurements by feature_name
    obs: Dict[str, Any] = {
        m.feature_name.strip().lower(): m.value
        for m in inspection.measurements
    }

    # Group rules by key_id
    key_groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in rules:
        kid = r["key_id"]
        key_groups.setdefault(kid, []).append(r)

    best_key = None
    best_taxa = []
    best_score = 0.0
    matched_features: List[str] = []
    recommended_lab = "forensic_stereomicroscopy"
    all_evaluations: List[Dict[str, Any]] = []

    for key_id, group_rules in key_groups.items():
        total_rules = len(group_rules)
        passed_rules = 0
        current_matched_features = []

        for rule in group_rules:
            feat = rule["feature"].strip().lower()
            if feat in obs:
                val = obs[feat]
                if _evaluate_rule(val, rule["operator"], rule["threshold"]):
                    passed_rules += 1
                    current_matched_features.append(f"{feat}={val} ({rule['description']})")

        if passed_rules > 0:
            match_ratio = passed_rules / total_rules
            confidence = group_rules[0]["confidence"] * match_ratio

            eval_entry = {
                "key_id": key_id,
                "domain": group_rules[0]["domain"],
                "passed_rules": passed_rules,
                "total_rules": total_rules,
                "confidence": round(confidence, 3),
                "target_taxa": group_rules[0]["target_taxa"],
            }
            all_evaluations.append(eval_entry)

            if match_ratio == 1.0 and confidence > best_score:
                best_score = confidence
                best_key = key_id
                best_taxa = group_rules[0]["target_taxa"]
                matched_features = current_matched_features
                recommended_lab = group_rules[0]["recommended_lab_test"] or recommended_lab
            elif best_key is None and confidence > best_score:
                best_score = confidence
                best_key = key_id
                best_taxa = group_rules[0]["target_taxa"]
                matched_features = current_matched_features
                recommended_lab = group_rules[0]["recommended_lab_test"] or recommended_lab

    return {
        "inspection_id": inspection.inspection_id,
        "specimen_category": inspection.observed_specimen_category,
        "primary_key_matched": best_key,
        "suspected_taxa": best_taxa,
        "diagnostic_confidence": round(best_score, 3),
        "matched_features": matched_features,
        "recommended_lab_test": recommended_lab,
        "all_key_evaluations": all_evaluations,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Match inspection morphology against forensic keys.")
    parser.add_argument("--inspection", required=True, help="Path to physical inspection JSON file.")
    parser.add_argument("--output", help="Optional path to write output JSON.")
    args = parser.parse_args()

    with open(args.inspection, "r", encoding="utf-8") as f:
        data = json.load(f)
        inspection = PhysicalInspection.model_validate(data)

    result = match_morphology_fingerprint(inspection)
    out_json = json.dumps(result, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_json)
    else:
        print(out_json)


if __name__ == "__main__":
    main()
