---
name: morphology-fingerprint
version: 1.0.0
description: Matches on-site physical measurements and micro-structural observations against verified forensic identification keys (Schreger line angles, wood porosity, keratin dorsal keels, osteon canals).
inputs:
  - name: inspection
    type: object
    description: PhysicalInspection JSON containing observed specimen category and quantitative/qualitative morphology measurements.
outputs:
  - name: fingerprint_result
    type: object
    description: Matched forensic keys, diagnostic taxon matches, confidence ratings, and contradiction alerts.
---

# Morphology Fingerprint Skill (`morphology-fingerprint`)

## 1. Overview
The `morphology-fingerprint` skill evaluates empirical micro-structural metrics gathered during physical customs examinations against laboratory identification keys. It identifies whether physical specimen traits agree with declared paperwork or betray illicit wildlife/timber derivatives.

## 2. Forensic Diagnostic Domains
- **Ivory Triage (Schreger Pattern Analysis):**
  - Modern Elephant Ivory (*Loxodonta* / *Elephas*): Outer Schreger intersection angles > 115° (typically 120°-140°).
  - Extinct Mammoth Ivory (*Mammuthus primigenius*): Outer Schreger intersection angles < 90° (typically 70°-85°).
  - Bone Distinction: Haversian canal osteons present under microscopy (characteristic of mammalian bone, absent in ivory dentine).
  - Synthetic Polymer: Injection mold seams, uniform matrix, or gas bubbles.
- **Pangolin Scales vs Cattle Horn:**
  - Presence of 1 to 3 distinct longitudinal dorsal keels/ridges and imbricated armor plates confirms *Manis* spp.
  - Fibrous hollow laminar sheath confirms domestic bovine horn or hoof core.
- **Timber Anatomy (Rosewood vs Teak):**
  - *Dalbergia* (Rosewood): Diffuse-porous vessel arrangement, storied rays (tangential ripple marks), distinctive extract fluorescence.
  - *Tectona grandis* (Teak): Ring-porous or semi-ring-porous arrangement with wide earlywood pores, absence of storied rays.
- **Marine Reptile Bekko (Hawksbill Turtle Shell):**
  - Layered organic keratin lamellae without synthetic mold seams or poured polymer bubbles.

## 3. Usage

### Command Line Execution
```bash
python skills/morphology-fingerprint/fingerprint.py --inspection tests/data/sample_inspection.json
```

### Programmatic Python Invocation
```python
from canopytrace.schemas import PhysicalInspection
from fingerprint import match_morphology_fingerprint

inspection = PhysicalInspection(...)
result = match_morphology_fingerprint(inspection)
print(result["matched_taxa"], result["diagnostic_confidence"])
```
