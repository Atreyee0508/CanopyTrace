#!/usr/bin/env python3
"""
Standalone runner script and module for the cites-registry-check skill.
Complies with agentskills.io standard.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure canopytrace package is resolvable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from canopytrace.db import query_cites_by_name, is_in_range_state, get_range_states
from canopytrace.schemas import ShippingManifest


def audit_manifest_registry(
    manifest: ShippingManifest,
    db_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Audits a shipping manifest against CITES appendices and IUCN range states.
    """
    red_flags: List[str] = []
    declared_query = manifest.declared_scientific_name or manifest.declared_item_name
    origin_country = manifest.country_of_origin.strip().upper()

    # Query offline CITES registry
    cites_match = query_cites_by_name(declared_query, db_path=db_path)

    resolved_taxon = cites_match["scientific_name"] if cites_match else None
    cites_appendix = cites_match["appendix"] if cites_match else "None"
    commercial_status = cites_match["commercial_status"] if cites_match else "UNKNOWN"

    is_native = False
    if resolved_taxon:
        is_native = is_in_range_state(resolved_taxon, origin_country, db_path=db_path)
        if not is_native and origin_country != "ALL":
            ranges = get_range_states(resolved_taxon, db_path=db_path)
            if ranges:
                red_flags.append(
                    f"Declared origin '{origin_country}' is NOT in documented native IUCN range states "
                    f"for {resolved_taxon} (Range: {', '.join(ranges[:6])})."
                )

        # Appendix I total commercial trade ban check
        if cites_appendix == "I":
            red_flags.append(
                f"Specimen '{resolved_taxon}' is listed on CITES Appendix I: Commercial trade is banned."
            )
            if not manifest.permit_numbers:
                red_flags.append("Missing mandatory CITES import/export permits for Appendix I listed species.")

        # Appendix II permit verification check
        elif cites_appendix == "II":
            if not manifest.permit_numbers:
                red_flags.append(
                    f"Specimen '{resolved_taxon}' is listed on CITES Appendix II: Valid export permit required."
                )

    # Check for known camouflage declared terms
    lower_decl = manifest.declared_item_name.lower()
    suspected_target = None
    target_appendix = None

    if any(k in lower_decl for k in ["mammoth", "mammuthus", "antique ivory"]):
        suspected_target = "Loxodonta africana / Elephas maximus"
        target_appendix = "I"
        red_flags.append(
            "Declared item description matches high-risk camouflage pattern for CITES Appendix I Elephant Ivory."
        )

    if any(k in lower_decl for k in ["bovine horn", "cattle horn", "keratin flakes", "cow hoof"]):
        suspected_target = "Manis spp. (Pangolin)"
        target_appendix = "I"
        red_flags.append(
            "Agricultural keratin declarations from West/Central Africa frequently mask CITES Appendix I Pangolin scales."
        )

    if any(k in lower_decl for k in ["teak", "tectona"]):
        suspected_target = "Dalbergia spp. (Rosewood)"
        target_appendix = "II"

    if any(k in lower_decl for k in ["synthetic resin", "plastic craft", "celluloid"]):
        suspected_target = "Eretmochelys imbricata (Hawksbill Sea Turtle Bekko)"
        target_appendix = "I"

    is_flagged = len(red_flags) > 0

    return {
        "manifest_id": manifest.manifest_id,
        "declared_item": manifest.declared_item_name,
        "resolved_taxon": resolved_taxon,
        "cites_appendix": cites_appendix,
        "commercial_status": commercial_status,
        "origin_country": origin_country,
        "is_native_range": is_native,
        "suspected_camouflage_target": suspected_target,
        "target_appendix": target_appendix,
        "is_flagged": is_flagged,
        "red_flags": red_flags,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit shipping manifest against CITES appendices & IUCN ranges.")
    parser.add_argument("--manifest", required=True, help="Path to shipping manifest JSON file.")
    parser.add_argument("--output", help="Optional path to write output JSON.")
    args = parser.parse_args()

    with open(args.manifest, "r", encoding="utf-8") as f:
        data = json.load(f)
        manifest = ShippingManifest.model_validate(data)

    result = audit_manifest_registry(manifest)
    out_json = json.dumps(result, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out_json)
    else:
        print(out_json)


if __name__ == "__main__":
    main()
