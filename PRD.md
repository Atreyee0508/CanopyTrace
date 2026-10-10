# Product Requirements Document (PRD)

## Project Title: CanopyTrace
**AI Forensic Fingerprinting for Illegal Wildlife & Protected Timber Trade Verification**  
*Open-Weight Google Gemma 2 + Schema-Constrained CFG Harness + Agent Skills Standard*

---

## 1. Problem Statement & Background

Illegal wildlife and protected timber trafficking is a multi-billion dollar illicit transnational enterprise. Smugglers exploit complex maritime logistics, cargo volume backlogs, and limited on-site forensic expertise at customs ports, land borders, and container terminals.

Smugglers frequently disguise high-value, strictly prohibited items under legal commercial declarations:
- **Elephant Ivory** (*Loxodonta africana*, *Elephas maximus*, CITES Appendix I) declared as legal antique Mammoth tusk (*Mammuthus primigenius*, extinct) or modern domestic bovine bone carvings.
- **Pangolin Scales** (*Manis* spp., CITES Appendix I) crushed or packaged as bovine/equine keratin fertilizer, fish scales, or oyster shells.
- **Protected Rosewood & Exotic Timber** (*Dalbergia* spp., CITES Appendix II/I) misdeclared as legal plantation teak (*Tectona grandis*), common eucalyptus, or non-regulated sawn wood.
- **Sea Turtle Shell / Bekko** (*Eretmochelys imbricata*, CITES Appendix I) disguised as synthetic decorative resin or celluloid crafts.
- **Big Cat derivatives** (pantherines) declared as generic livestock bone crafts or domestic leather.

Customs officers and wildlife crime control agencies face a dual dilemma:
1. **High False Negatives:** Lack of immediate forensic verification leads to illegal shipments being cleared through ports.
2. **Evidentiary Bottlenecks:** Suspect shipments detained without clear, actionable preliminary proof create port congestion and legal liabilities.

---

## 2. Product Vision & Value Proposition

**CanopyTrace** is an open-source, investigative decision-support platform designed to inspect cargo manifests, evaluate physical and micro-structural observations, cross-reference international CITES trade quotas and known smuggling patterns, and generate tamper-evident forensic dossiers for customs officers and wildlife crime control bureaus.

The system acts strictly as an **investigative decision-support and evidentiary triage assistant**:
- **Triage, Not Final Verdict:** AI outputs do not replace courtroom-certified laboratory genomics or radiocarbon testing; they deliver rapid on-site probabilistic triage and indicate which precise confirmatory assays (FTIR spectroscopy, DNA barcoding, radiocarbon dating) must be ordered.
- **Deterministic Schema-Constrained Reasoning:** Leverages open-weight **Google Gemma 2 2B Instruct** constrained by Context-Free Grammars (GBNF) to eliminate hallucinations and produce structured, auditable outputs.
- **Standardized Interoperability:** Adheres to the open `agentskills.io` standard for pluggable forensic capabilities.

---

## 3. Target User Personas

| Persona | Role | Key Needs & Pain Points | Primary Interface |
|---|---|---|---|
| **Border Customs Officer** | Port of entry cargo inspection | Rapid physical verification against shipping manifests; non-technical guidance on what to check; instant red-flagging. | Local Web UI / Mobile App |
| **Field Wildlife Enforcement Agent** | Seaport container yards, border checkpoints | Offline capture of photos and caliper measurements; Schreger angle calculation tool; chain-of-custody logging. | Flutter Mobile App / CLI |
| **Forensic Triage Specialist** | Customs scientific triage laboratory | Rigorous morphology analysis; discrepancy scoring; recommended laboratory assays; formal dossier generation. | Local Web UI / CLI |
| **Higher CITES / Scientific Authority** | National scientific authority / CITES Secretariat | Review of novel anomalous specimens; approving and ingesting newly identified smuggling patterns into the registry. | Escalation Portal in Web UI |

---

## 4. Key Functional Requirements (FR)

### FR-1: Manifest & Inspection Data Ingestion
- Ingest shipping paperwork declarations: declared species/common name, Harmonized System (HS) tariff code, declared quantity, declared commercial form, country of origin, transit ports, destination, and permit numbers.
- Ingest field physical inspection logs: physical specimen type, dimensions, micro-structural measurements (Schreger pattern angles, vessel porosity type, scale keel count), fluorescence test results, and inspection macro-photographs.
- Support JSON, manual web form inputs, CLI arguments, and mobile sync payloads.

### FR-2: Offline Registry Cross-Referencing (`skills/cites-registry-check`)
- Query local offline SQLite database containing:
  - CITES Appendices I, II, and III listings with commercial annotations and exemptions.
  - IUCN Red List native range distributions and known range-state exclusions.
  - National export quotas and regional trade bans.
- Detect permit invalidity, impossible transit origins (e.g. wild pangolin exported from non-range country), or unauthorized commercial transit of Appendix I species.
- Provide fuzzy/semantic name resolution for misspelled manifest terms and trade trade-slang.

### FR-3: Morphology & Forensic Fingerprinting (`skills/morphology-fingerprint`)
- Implement deterministic forensic morphology identification keys:
  - **Ivory Triage:** Evaluate Schreger outer intersection angles. Elephant outer angles (> 115°, typically 120°-140°) vs. Mammoth outer angles (< 90°, typically 70°-85°). Differentiate bone via Haversian osteon canals and synthetic resin via mold seams / uniform matrix.
  - **Pangolin Scale Triage:** Check imbrication patterns, dorsal ridge/keel count (3 keels for *Manis tricuspis*), scale thickness, and keratin density versus cattle horn and turtle shell.
  - **Timber Triage:** Vessel arrangement (diffuse-porous vs. ring-porous), storied rays, ripple marks, and water/ethanol fluorescence extraction to differentiate *Dalbergia* (Rosewood) from *Tectona* (Teak).
  - **Big Cat & Reptile Triage:** Canine grooves, scute patterns, and epidermal metrics.
- Support pluggable, user-defined morphology keys through external YAML definition files.

### FR-4: Smuggling Modus Operandi (MO) Pattern Matching
- Maintain an offline database of documented wildlife smuggling patterns:
  - Camouflage declarations (e.g. "antique carving", "cow horn", "plantation teak", "plastic resin").
  - High-risk transit routes (triangular routing through non-CITES enforcement hubs).
  - Volume/weight anomalies compared to declared item category.
- Cross-reference inspection inputs against the pattern database to calculate a Modus Operandi Risk Index and flag matching historical precedents.

### FR-5: Schema-Constrained Google Gemma 2 Synthesis
- Feed aggregated registry checks, morphology metrics, and pattern risks into Google Gemma 2 2B Instruct.
- Utilize Context-Free Grammars (GBNF) via `llama-cpp-python` to enforce an immutable JSON schema output:
  - `discrepancy_score` (float: 0.00 to 1.00)
  - `flagged_indicators` (list of specific contradictions)
  - `cites_appendix` (string: "I", "II", "III", or "None")
  - `smuggling_mo_detected` (list of matched smuggling patterns)
  - `uncertainty_bounds` (lower_bound, upper_bound, confidence_interval)
  - `suggested_lab_action` (concrete confirmatory laboratory tests: DNA barcoding, FTIR, radiocarbon)
  - `forensic_rationale` (objective natural-language justification)
- Dual-engine architecture: Native `llama-cpp-python` GGUF, local server connection (Ollama/vLLM), with deterministic offline mock fallback for CI and low-resource environments.

### FR-6: Automated Local Authority Alerting
- If `discrepancy_score` meets or exceeds the configured seizure threshold (default >= 0.70):
  - Automatically dispatch an urgent alert payload (webhook, emergency email notice, incident log).
  - Include port location, container ID, suspect taxa, seizure urgency rating, and cryptographic case ID.
  - Maintain an auditable incident log for all triggered alerts.

### FR-7: Novel Anomaly Escalation & Continuous Learning Loop
- If the system detects a specimen with anomalous physical traits or unknown taxa that cannot be confidently identified:
  - Flag the case as an `Unresolved Novel Anomaly`.
  - Compile an Escalation Case Dossier routed to the Higher Scientific / CITES Authority review queue.
  - Provide an administrative approval interface to verify the specimen and automatically ingest the verified identification rule back into the local offline SQLite database.

### FR-8: Case Dossier Compilation & Evidentiary Packaging (`skills/case-dossier-compiler`)
- Package findings into a complete multi-format dossier:
  - **Printable PDF Dossier:** Official customs layout with agency header, inspection photos, morphology diagrams, discrepancy breakdown, recommended lab tests, and non-definitive legal disclaimer.
  - **Markdown Dossier (`dossier.md`):** Complete structured text report.
  - **Machine-Readable JSON (`dossier.json`):** Full raw case data.
- Stamp all generated files with a cryptographic SHA-256 digest to ensure chain-of-custody integrity and tamper detection.

### FR-9: Triple-Interface Access
- **CLI (`canopytrace`):** Terminal commands for batch inspection, database management, and dossier export.
- **Local Web UI:** Responsive browser-based interface running locally with interactive Schreger angle calculator, photo upload, and live dossier viewer.
- **Flutter Mobile App:** Cross-platform mobile companion with offline-first camera capture, visual angle caliper tool, and local checkpoint synchronization.

---

## 5. Non-Functional Requirements (NFR)

1. **Air-Gapped / Offline Capability:** The entire verification pipeline, database queries, and inference engine must function 100% offline without requiring internet access.
2. **Deterministic Reproducibility:** Given identical manifest and inspection inputs, the deterministic grammar harness and rule engines must produce consistent, reproducible triage outputs.
3. **Low Latency on Edge Hardware:**
   - Full pipeline execution on modern consumer CPU (x86_64 or ARM64) under 10 seconds per item using Gemma 2 2B Q4_K_M GGUF.
   - Offline database queries under 100 milliseconds.
4. **Evidentiary Integrity:** All exported dossiers must incorporate verifiable SHA-256 hashes and timestamped chain-of-custody metadata.
5. **Open Source & Extensible:** Apache 2.0 license; modular Python architecture with standard `agentskills.io` compliance.
6. **Robust Fallbacks:** Graceful degradation to deterministic mock inference if model weights are not loaded.

---

## 6. Success Metrics & Validation Targets

- **Benchmark Suite:** 100% pass rate across the 6 core smuggling/compliance benchmark cases + 1 novel anomaly escalation case.
- **False Negative Prevention:** Flag 100% of high-risk disguises (Elephant ivory disguised as Mammoth; Pangolin scales disguised as cow horn).
- **False Positive Control:** Maintain a discrepancy score < 0.20 on legitimate negative controls (e.g. domestic bovine bone carvings).
- **Format Compliance:** 100% JSON schema conformity through CFG decoding without runtime JSON parse exceptions.
