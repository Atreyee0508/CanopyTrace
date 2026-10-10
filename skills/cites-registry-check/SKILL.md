---
name: cites-registry-check
version: 1.0.0
description: Audits declared shipping manifests against offline CITES Appendices (I, II, III), IUCN Red List native geographic ranges, and international commercial trade bans.
inputs:
  - name: manifest
    type: object
    description: ShippingManifest JSON containing declared species/item name, origin country, transit routes, and claimed permits.
outputs:
  - name: registry_result
    type: object
    description: Verification findings including CITES appendix, commercial status, range-state validity, and permit red flags.
---

# CITES Registry Check Skill (`cites-registry-check`)

## 1. Overview
The `cites-registry-check` skill cross-references cargo paperwork declarations against local offline copies of the CITES Appendices and IUCN Red List geographic range distribution records. It detects impossible geographic origins (e.g. wild specimens exported from non-range countries), trade ban violations, and counterfeit or invalid CITES permit claims.

## 2. Capabilities
- **Taxon Resolution:** Resolves commercial declared trade names and slang (e.g., "antique mammoth", "cow bone carvings", "teak logs") against CITES scientific binomials using exact and FTS5 full-text matching.
- **Protection Status Assessment:** Returns the applicable CITES Appendix (`I`, `II`, `III`, or `None`) and regulatory status (`BANNED`, `QUOTA_CONTROLLED`, `UNREGULATED`).
- **Geographic Range State Validation:** Verifies whether the declared `country_of_origin` matches the native wild distribution of the suspected species. Flags triangular transshipment anomalies.
- **Permit Red-Flagging:** Flags shipments lacking mandatory CITES export permits for Appendix I/II specimens or claiming permits from non-range states.

## 3. Usage

### Command Line Execution
```bash
python skills/cites-registry-check/check_registry.py --manifest tests/data/sample_manifest.json
```

### Programmatic Python Invocation
```python
from canopytrace.schemas import ShippingManifest
from check_registry import audit_manifest_registry

manifest = ShippingManifest(...)
result = audit_manifest_registry(manifest)
print(result["is_flagged"], result["cites_appendix"])
```

## 4. Output Schema
```json
{
  "declared_item": "Antique Mammoth Carvings",
  "resolved_taxon": "Mammuthus primigenius",
  "cites_appendix": "None",
  "commercial_status": "REGULATED_UNLISTED",
  "origin_country": "NG",
  "is_native_range": false,
  "suspected_camouflage_target": "Loxodonta africana",
  "target_appendix": "I",
  "is_flagged": true,
  "red_flags": [
    "Origin country 'NG' is not a native range state for declared species 'Mammuthus primigenius'.",
    "Declared item frequently used as fraudulent camouflage for CITES Appendix I elephant ivory."
  ]
}
```
