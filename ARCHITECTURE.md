# Architecture Blueprint (ARCHITECTURE.md)

## Project Title: CanopyTrace
**AI Forensic Fingerprinting for Illegal Wildlife & Protected Timber Trade Verification**

---

## 1. High-Level Architecture Overview

CanopyTrace is structured into four primary logical tiers:
1. **Field & Ingestion Tier:** Captures shipping documents, macro-inspection photos, and morphological measurements across CLI, Local Web UI, and a cross-platform Flutter Mobile companion.
2. **Deterministic Forensic Skills Tier:** Implements modular, reproducible, offline forensic capabilities complying with the `agentskills.io` standard (`cites-registry-check`, `morphology-fingerprint`, `case-dossier-compiler`) backed by an embedded SQLite reference database and a smuggling modus-operandi matching engine.
3. **Schema-Constrained Reasoning Tier:** Open-weight Google Gemma 2 2B Instruct driven by Context-Free Grammars (GBNF) for deterministic forensic JSON synthesis, supported by a dual-engine harness (native GGUF, local server, and offline mock fallback).
4. **Evidentiary & Operational Dispatch Tier:** Multi-format tamper-evident dossier generation (PDF, Markdown, JSON + SHA-256), automated local authority alert dispatching, and a novel anomaly escalation feedback loop for scientific authority review and database enrichment.

---

## 2. Complete Architecture Diagram

```mermaid
graph TB
    subgraph Clients["1. Field Ingestion & Interaction Tier"]
        CLI["CLI: `canopytrace`\n(Click + Rich)"]
        WEB["Local Web Dashboard\n(FastAPI + Tailwind HTML5)"]
        MOBILE["Flutter Mobile Companion\n(Offline Capture + Caliper Overlay)"]
    end

    subgraph Ingestion["2. Ingestion & Validation Gateway"]
        GATEWAY["CanopyTrace Ingestion Gateway"]
        P_SCHEMA["Pydantic Schemas\n(Manifest, Inspection, Measurement)"]
        GATEWAY --> P_SCHEMA
        CLI --> GATEWAY
        WEB --> GATEWAY
        MOBILE -->|REST API Sync| GATEWAY
    end

    subgraph Skills["3. Deterministic Forensic Skills (agentskills.io)"]
        S_CITES["Skill: `cites-registry-check`\n- CITES Appendices I/II/III\n- IUCN Range Verification\n- Export Quota Auditing"]
        S_MORPH["Skill: `morphology-fingerprint`\n- Schreger Angle Evaluator\n- Timber Porosity & Rays\n- Keratin Scale Keel Counts"]
        S_PATT["Smuggling MO Engine\n- Modus Operandi Catalog\n- Camouflage Route Risk"]
        
        DB[("Embedded SQLite 3\n+ FTS5 Fuzzy Taxonomy\n+ YAML/JSON Source Datasets")]
        S_CITES <--> DB
        S_MORPH <--> DB
        S_PATT <--> DB
    end

    GATEWAY --> S_CITES
    GATEWAY --> S_MORPH
    GATEWAY --> S_PATT

    subgraph Reasoning["4. Schema-Constrained Gemma 2 Reasoning Tier"]
        SYNTH["Forensic Synthesis Coordinator"]
        S_CITES --> SYNTH
        S_MORPH --> SYNTH
        S_PATT --> SYNTH
        
        HARNESS["Dual-Engine Inference Harness\n(`canopytrace.core.harness`)"]
        GBNF["Context-Free Grammar\n(GBNF Token Logit Masking)"]
        
        G_NATIVE["Native llama-cpp-python\n(Gemma 2 2B Q4_K_M GGUF)"]
        G_SERVER["Local Server Connection\n(Ollama / vLLM / llama.cpp server)"]
        G_MOCK["Deterministic Mock Fallback\n(Offline CI / Low-RAM Triage)"]
        
        SYNTH --> HARNESS
        HARNESS --> GBNF
        GBNF --> G_NATIVE
        GBNF --> G_SERVER
        GBNF --> G_MOCK
        
        JSON_OUT["Strict ForensicTriageOutput\n(Validated JSON Object)"]
        G_NATIVE --> JSON_OUT
        G_SERVER --> JSON_OUT
        G_MOCK --> JSON_OUT
    end

    subgraph Operational["5. Operational Dispatch & Evidentiary Packaging Tier"]
        EVAL{"Discrepancy Evaluation Engine"}
        JSON_OUT --> EVAL
        
        ALERT["🚨 Local Authority Alert Dispatcher\n(Webhook POST / Urgent JSON / Notice)"]
        ESCALATE["🔬 Novel Anomaly Escalation Queue\n(Higher CITES Authority Portal)"]
        APPROVE["Database Ingestion Hook\n(Admin Verified Taxon / Rule)"]
        
        EVAL -->|"Discrepancy >= 0.70"| ALERT
        EVAL -->|"Unresolved / Unknown Taxon"| ESCALATE
        ESCALATE -->|"Expert Approved"| APPROVE
        APPROVE --> DB
        
        S_COMP["Skill: `case-dossier-compiler`\n- Markdown Generator (`dossier.md`)\n- Canonical JSON (`dossier.json`)\n- ReportLab PDF Generator (`dossier.pdf`)"]
        SHA["Cryptographic Stamp\n(SHA-256 Digest & Audit Log)"]
        
        EVAL --> S_COMP
        S_COMP --> SHA
    end
```

---

## 3. End-to-End Triage Sequence

```mermaid
sequenceDiagram
    autonumber
    actor Inspector as Customs Officer
    participant App as CanopyTrace App / CLI
    participant Core as Forensic Pipeline
    participant Skills as Agent Skills & DB
    participant Gemma as Gemma 2 (CFG Harness)
    participant Dispatch as Alert & Dossier Engine
    actor Authority as Local / CITES Authority

    Inspector->>App: Input Manifest & Inspection Measurements
    App->>Core: Submit Inspection Payload
    
    par Query Offline Databases
        Core->>Skills: cites-registry-check(manifest)
        Skills-->>Core: Appendix status, range validity, quota status
    and Evaluate Morphology
        Core->>Skills: morphology-fingerprint(measurements)
        Skills-->>Core: Diagnostic match (e.g. Elephant outer Schreger >115°)
    and Match Smuggling Patterns
        Core->>Skills: pattern_matcher(manifest, measurements)
        Skills-->>Core: Matched MOs (e.g. MO-IVO-001 "Mammoth Camouflage")
    end
    
    Core->>Gemma: Synthesize Case (Aggregated Evidence + GBNF Grammar)
    Gemma-->>Core: Strict Forensic JSON (Discrepancy, Rationale, Lab Tests)
    
    alt Discrepancy Score >= 0.70
        Core->>Dispatch: Trigger Priority Seizure Alert
        Dispatch->>Authority: 🚨 Dispatch Urgent Alert (Webhook / Notice)
    end
    
    alt Unresolved Unknown Taxon / Anomaly
        Core->>Dispatch: Enqueue for Scientific Authority Review
        Dispatch-->>Authority: Forward Escalation Case File
    end
    
    Core->>Dispatch: Compile Multi-Format Dossier
    Dispatch->>Dispatch: Compute SHA-256 Cryptographic Digest
    Dispatch-->>Inspector: Export PDF, Markdown, and JSON Case Files
```

---

## 4. Component Deep Dive

### 4.1 Ingestion & Data Validation (`canopytrace.schemas`)
- All incoming payloads pass through Pydantic v2 models.
- Rejects malformed numbers, invalid measurement units, and incomplete chain-of-custody metadata.
- Prepares normalized entity dictionaries for downstream rule engines.

### 4.2 Agent Skills Compliance (`agentskills.io`)
Each skill is completely self-contained in `skills/<skill-name>/`:
- **`SKILL.md`:** Contains standardized YAML frontmatter metadata:
  ```yaml
  name: cites-registry-check
  version: 1.0.0
  description: Checks shipping declarations against offline CITES Appendices and IUCN ranges.
  inputs:
    - manifest: ShippingManifest JSON
  outputs:
    - registry_findings: CITESRegistryResult JSON
  ```
  Followed by clear markdown instructions and progressive disclosure documentation.
- **Standalone Python Entry Point:** Can be executed directly from shell or invoked as a Python module:
  `python skills/cites-registry-check/check_registry.py --input manifest.json`

### 4.3 Offline Reference Database (`canopytrace.db`)
- Zero external runtime server required; uses SQLite 3 with WAL mode enabled.
- Tables:
  - `taxa_cites`: Scientific name, common names, Appendix (I/II/III), commercial annotations, active trade bans.
  - `range_states`: Scientific name, ISO country codes of native geographic distribution.
  - `morphology_rules`: Specimen type, diagnostic feature, operator (`gt`, `lt`, `eq`, `between`), threshold value, target species.
  - `smuggling_mos`: Pattern ID, name, trigger keywords, risk score.
  - `escalation_cases`: Pending and verified anomaly cases.
- Full-text search (FTS5) table for common name and trade slang fuzzy matching.

### 4.4 Gemma 2 Schema-Constrained Decoding Harness (`canopytrace.core.harness`)
- Guarantees zero hallucinations and 100% adherence to the forensic JSON schema.
- Uses `llama-cpp-python` with Context-Free Grammar (GBNF) representation of the Pydantic schema.
- **Fail-safe Fallback:** If GGUF weights are not installed or in automated CI runs, the harness switches to a deterministic heuristic mock engine that computes the exact forensic indicators from rule tables, ensuring test suites and pipelines never crash.

### 4.5 Smuggling Modus Operandi (MO) Engine (`canopytrace.core.pattern_matcher`)
- Applies expert-encoded smuggling pattern rules to spot deceptive declarations (e.g. "antique mammoth" disguise, "agricultural keratin" masking, "plantation teak" cover for rosewood).
- Feeds matched pattern IDs and risk weights into Gemma's synthesis prompt.

### 4.6 Automated Alerting & Anomaly Escalation (`canopytrace.alerts` & `canopytrace.escalation`)
- **Alert Dispatcher:** Formats and broadcasts priority seizure alerts when discrepancy threshold is exceeded.
- **Escalation Queue:** Stores unknown specimens and allows Higher CITES Authorities to verify taxonomy and automatically update the local database using `canopytrace escalate approve`.

### 4.7 Multi-Format Dossier Compiler (`canopytrace.dossier`)
- Generates:
  1. `dossier.pdf`: Publication-quality customs enforcement report with official headers, measurement tables, and legal disclaimers.
  2. `dossier.md`: Auditable GitHub-flavored markdown.
  3. `dossier.json`: Verifiable raw machine-readable data.
  4. `dossier.sha256`: Cryptographic checksum ensuring chain-of-custody evidence has not been altered.

### 4.8 Flutter Mobile Field Companion (`mobile/`)
- Cross-platform Flutter application for customs inspectors working in shipping container berths and inspection docks.
- Includes:
  - Offline inspection form.
  - Interactive Schreger angle caliper tool: inspector aligns on-screen protractor arms with cross-section photos to calculate outer angles automatically.
  - Local SQLite storage with background sync to the local CanopyTrace desktop server.

---

## 5. Security & Legal Considerations

1. **Investigative Support Non-Definitive Disclaimer:** Every dossier, screen, and PDF prominently displays the mandatory legal disclaimer:
   > *"AI findings provide preliminary investigative triage and do not constitute certified legal testimony. Formal seizure and prosecution require confirmatory forensic laboratory analysis."*
2. **Chain-of-Custody Integrity:** Every case output is stamped with an immutable SHA-256 hash calculated over the canonical JSON representation.
3. **Air-Gapped Privacy:** All inference and database queries happen on the local machine; no contraband data, port locations, or manifest details leak to third-party cloud APIs.
