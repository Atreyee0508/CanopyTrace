"""Evidentiary multi-format dossier compiler with SHA-256 integrity digests."""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict

from canopytrace.dossier.pdf_generator import generate_pdf_dossier
from canopytrace.schemas.forensic_output import MANDATORY_LEGAL_DISCLAIMER


def compute_canonical_hash(data: Dict[str, Any]) -> str:
    """Computes SHA-256 hash across canonical sorted JSON string."""
    canonical_str = json.dumps(data, sort_keys=True, indent=2, default=str)
    return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()


def generate_markdown_dossier(case_data: Dict[str, Any], sha256_hash: str) -> str:
    """Compiles auditable Markdown report from case findings."""
    case_id = case_data.get("case_id", "CASE-UNKNOWN")
    manifest = case_data.get("manifest", {})
    inspection = case_data.get("inspection", {})
    forensic = case_data.get("forensic_output", {})

    discrepancy = forensic.get("discrepancy_score", 0.0)
    status_emoji = "🚨 CRITICAL SEIZURE" if discrepancy >= 0.70 else (
        "⚠️ ELEVATED UNCERTAINTY" if discrepancy >= 0.30 else "✅ CLEARED"
    )

    md = f"""# CanopyTrace Forensic Triage Dossier
**Case ID:** `{case_id}`  
**Triage Status:** {status_emoji} (Discrepancy Score: `{discrepancy:.2f}`)  
**Cryptographic Integrity Stamp:** `{sha256_hash}`  

---

## 1. Shipping Manifest Declaration
| Attribute | Declared Value |
|---|---|
| **Declared Commercial Item** | {manifest.get('declared_item_name', 'N/A')} |
| **Declared Binomial** | *{manifest.get('declared_scientific_name', 'N/A')}* |
| **Harmonized System Code** | `{manifest.get('hs_code', 'N/A')}` |
| **Declared Origin** | `{manifest.get('country_of_origin', 'N/A')}` |
| **Shipper / Consignee** | {manifest.get('shipper', 'N/A')} ➔ {manifest.get('consignee', 'N/A')} |
| **Claimed Permits** | {', '.join(manifest.get('permit_numbers', [])) or 'None Provided'} |

---

## 2. Physical Inspection & Empirical Morphology
- **Examined Specimen Category:** `{inspection.get('observed_specimen_category', 'N/A')}`
- **Checkpoint Location:** `{inspection.get('checkpoint_location', 'N/A')}`

### Quantitative & Qualitative Measurements
| Feature | Value | Unit | Instrument |
|---|---|---|---|
"""
    for m in inspection.get("measurements", []):
        md += f"| `{m.get('feature_name')}` | **{m.get('value')}** | {m.get('unit') or '-'} | {m.get('instrument') or '-'} |\n"

    md += f"""
---

## 3. Forensic Contradictions & Modus Operandi
- **Suspected True Taxon:** **{forensic.get('suspected_actual_species', 'N/A')}**
- **CITES Appendix Violated:** **Appendix {forensic.get('cites_appendix', 'None')}**
- **Uncertainty Bounds:** Lower: `{forensic.get('uncertainty_bounds', {}).get('lower_bound', 0.0)}` | Upper: `{forensic.get('uncertainty_bounds', {}).get('upper_bound', 1.0)}` ({forensic.get('uncertainty_bounds', {}).get('confidence_interval', '95%')})

### Flagged Empirical Contradictions
"""
    for flag in forensic.get("flagged_indicators", []):
        md += f"- ❌ **Contradiction:** {flag}\n"

    mos = forensic.get("smuggling_mo_detected", [])
    if mos:
        md += f"\n### Matched Trafficking Modus Operandi (MO)\n"
        for mo in mos:
            md += f"- 🕵️ **{mo}**\n"

    md += f"""
---

## 4. Gemma 2 Forensic Rationale
> {forensic.get('forensic_rationale', 'No rationale generated.')}

---

## 5. Recommended Confirmatory Laboratory Protocol
| Assay / Test Type | Priority | Target Discriminator |
|---|---|---|
"""
    for lab in forensic.get("suggested_lab_action", []):
        md += f"| **{lab.get('test_type')}** | `{lab.get('priority', '').upper()}` | {lab.get('expected_discriminator')} |\n"

    md += f"""
---

## 6. Chain-of-Custody & Statutory Notice
> [!WARNING]
> **MANDATORY LEGAL DISCLAIMER:**  
> *{MANDATORY_LEGAL_DISCLAIMER}*

**Canonical SHA-256 Integrity Digest:**  
`{sha256_hash}`
"""
    return md


def compile_evidentiary_dossier(
    case_data: Dict[str, Any],
    output_dir: Path,
) -> Dict[str, Any]:
    """
    Compiles full multi-format dossier package (JSON, Markdown, PDF, SHA-256).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    case_id = case_data.get("case_id", "CASE-UNKNOWN")

    # 1. Compute canonical SHA-256 hash
    sha256_hash = compute_canonical_hash(case_data)
    case_data["_cryptographic_hash"] = sha256_hash

    # 2. Write dossier.json
    json_path = output_dir / f"{case_id}_dossier.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(case_data, f, indent=2, default=str)

    # 3. Write dossier.md
    md_content = generate_markdown_dossier(case_data, sha256_hash)
    md_path = output_dir / f"{case_id}_dossier.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    # 4. Generate dossier.pdf
    pdf_path = output_dir / f"{case_id}_dossier.pdf"
    generate_pdf_dossier(case_data, pdf_path, sha256_hash)

    # 5. Write dossier.sha256
    hash_path = output_dir / f"{case_id}_dossier.sha256"
    with open(hash_path, "w", encoding="utf-8") as f:
        f.write(f"{sha256_hash}  {pdf_path.name}\n")

    return {
        "case_id": case_id,
        "sha256_hash": sha256_hash,
        "json_path": str(json_path),
        "md_path": str(md_path),
        "pdf_path": str(pdf_path),
        "hash_path": str(hash_path),
    }
