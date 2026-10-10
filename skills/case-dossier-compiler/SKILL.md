---
name: case-dossier-compiler
version: 1.0.0
description: Aggregates shipping paperwork, morphology measurements, CITES audit findings, smuggling MO matches, and Gemma AI rationales into tamper-evident multi-format case files (PDF, Markdown, JSON) stamped with cryptographic SHA-256 digests.
inputs:
  - name: case_data
    type: object
    description: Aggregated case payload containing manifest, inspection, forensic_output, and audit metadata.
outputs:
  - name: dossier_package
    type: object
    description: Paths to compiled dossier.md, dossier.json, dossier.pdf, and SHA-256 cryptographic digest.
---

# Case Dossier Compiler Skill (`case-dossier-compiler`)

## 1. Overview
The `case-dossier-compiler` skill aggregates all forensic evidence collected during a customs inspection into court-admissible, tamper-evident case files. Every compiled dossier package includes:
- **Canonical JSON (`dossier.json`):** Strict, verifiable data representation.
- **Auditable Markdown (`dossier.md`):** Human-readable structured report.
- **Customs-Ready PDF (`dossier.pdf`):** High-fidelity printable report with official layout, measurement tables, and legal notices.
- **SHA-256 Digest (`dossier.sha256`):** Cryptographic checksum computed across canonical JSON to guarantee chain-of-custody integrity.

## 2. Mandatory Non-Definitive Legal Disclaimer
All compiled dossiers unconditionally embed the legal disclaimer:
> *"AI findings provide investigative triage and do not constitute certified legal testimony. Formal seizure and prosecution require confirmatory forensic laboratory analysis."*

## 3. Usage

### Command Line Execution
```bash
python skills/case-dossier-compiler/compile_dossier.py --case-file case_bundle.json --outdir ./output/CASE-001/
```

### Programmatic Python Invocation
```python
from compile_dossier import compile_evidentiary_dossier

dossier_meta = compile_evidentiary_dossier(case_data_dict, output_dir=Path("./output"))
print(dossier_meta["sha256_hash"], dossier_meta["pdf_path"])
```
