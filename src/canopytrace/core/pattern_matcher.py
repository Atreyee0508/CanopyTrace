"""Smuggling Modus Operandi (MO) pattern matching engine."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from canopytrace.db import get_all_smuggling_patterns
from canopytrace.schemas import ShippingManifest, PhysicalInspection


def _check_condition(expr: str, obs_dict: Dict[str, Any]) -> bool:
    """Evaluates an indicator expression like 'schreger_angle_outer > 115'."""
    expr = expr.strip()
    match = re.match(r"^([a-zA-Z0-9_]+)\s*(>|<|>=|<=|==|!=)\s*(.+)$", expr)
    if not match:
        return False
    var, op, raw_val = match.groups()
    var = var.lower()
    if var not in obs_dict:
        return False

    obs_val = obs_dict[var]
    raw_val = raw_val.strip()

    # Boolean values
    if raw_val.lower() in ("true", "false"):
        target_val = raw_val.lower() == "true"
        if op == "==":
            return bool(obs_val) == target_val
        elif op == "!=":
            return bool(obs_val) != target_val
        return False

    # String values
    if not re.match(r"^-?\d+(\.\d+)?$", raw_val):
        target_str = raw_val.strip("\"'").lower()
        obs_str = str(obs_val).strip().lower()
        if op == "==":
            return obs_str == target_str
        elif op == "!=":
            return obs_str != target_str
        return False

    # Numeric comparisons
    try:
        num_obs = float(obs_val)
        num_target = float(raw_val)
        if op == ">":
            return num_obs > num_target
        elif op == "<":
            return num_obs < num_target
        elif op == ">=":
            return num_obs >= num_target
        elif op == "<=":
            return num_obs <= num_target
        elif op == "==":
            return num_obs == num_target
        elif op == "!=":
            return num_obs != num_target
    except (ValueError, TypeError):
        return False

    return False


def match_smuggling_patterns(
    manifest: ShippingManifest,
    inspection: PhysicalInspection,
    db_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Evaluates manifest paperwork and physical measurements against registered
    wildlife trafficking modus operandi (MOs).
    """
    patterns = get_all_smuggling_patterns(db_path=db_path)

    text_to_search = f"{manifest.declared_item_name} {manifest.declared_commercial_form}".lower()
    obs_dict: Dict[str, Any] = {
        m.feature_name.strip().lower(): m.value
        for m in inspection.measurements
    }

    matched_patterns: List[Dict[str, Any]] = []
    accumulated_risk = 0.0

    for p in patterns:
        kw_matches = [
            kw for kw in p["manifest_keywords"]
            if kw.lower() in text_to_search
        ]

        ind_matches = [
            ind for ind in p["physical_indicators"]
            if _check_condition(ind, obs_dict)
        ]

        # Triggered if both manifest keyword and physical indicator are present
        if kw_matches and ind_matches:
            matched_patterns.append({
                "id": p["id"],
                "name": p["name"],
                "category": p["category"],
                "risk_weight": p["risk_weight"],
                "target_contraband": p["target_contraband"],
                "cites_appendix": p["cites_appendix_breach"],
                "matched_keywords": kw_matches,
                "matched_indicators": ind_matches,
                "recommended_lab_assays": p["recommended_lab_assays"],
            })
            accumulated_risk = max(accumulated_risk, p["risk_weight"])

    return {
        "matched_count": len(matched_patterns),
        "patterns": matched_patterns,
        "max_risk_weight": accumulated_risk,
        "matched_ids": [p["id"] for p in matched_patterns],
    }
