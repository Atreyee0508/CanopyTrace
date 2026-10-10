# Technical Design Document & Test-Driven Development Plan (TDD)

## Project Title: CanopyTrace
**AI Forensic Fingerprinting for Illegal Wildlife & Protected Timber Trade Verification**

---

## 1. Technical Stack & Environment

| Component | Technology | Rationale |
|---|---|---|
| **Programming Language** | Python 3.10+ | Standard for scientific computing, C-bindings, and AI ecosystems. |
| **Package / Project Manager** | `uv` / `hatchling` / `pyproject.toml` | High-speed, reproducible virtual environments and modern dependency resolution. |
| **Inference Engine** | `llama-cpp-python` / GGUF | Efficient CPU & edge execution of quantized Google Gemma 2 2B Instruct with Context-Free Grammar (GBNF) support. |
| **Grammar Enforcement** | GBNF (Grammar-Based Normal Form) | Strict token-level logit masking ensuring deterministic JSON schema output. |
| **Database** | SQLite 3 (with FTS5) | Zero-dependency, air-gapped, high-performance embedded database. |
| **Schema Validation** | `pydantic` v2 | Type validation, serialization, and dynamic JSON Schema generation for grammars. |
| **Web UI / REST API** | FastAPI + Uvicorn + Jinja2 / Static HTML5 | Fast, asynchronous, lightweight local server with built-in OpenAPI docs. |
| **CLI Framework** | `click` / `rich` | Ergonomic command-line interface with formatted tables, progress spinners, and colors. |
| **Dossier Generation** | ReportLab + Markdown2 | High-fidelity printable PDF with embedded tables/diagrams + auditable Markdown. |
| **Cryptographic Integrity** | Python standard library `hashlib` (SHA-256) | Tamper-evident digests for chain-of-custody verification. |
| **Testing Framework** | `pytest` + `pytest-asyncio` + `pytest-cov` | Industrial test suite with coverage, mocks, and parameterized benchmarks. |
| **Mobile Client** | Flutter / Dart 3.x | Cross-platform offline-first mobile companion for field customs inspectors. |

---

## 2. Core Data Models & Schemas

### 2.1 Manifest Declaration Schema (`schemas/manifest.py`)
```python
class ShippingManifest(BaseModel):
    manifest_id: str
    waybill_number: str
    shipper: str
    consignee: str
    declared_item_name: str
    declared_scientific_name: Optional[str] = None
    hs_code: Optional[str] = None
    declared_quantity: float
    declared_unit: str  # e.g., "kg", "pieces", "logs"
    country_of_origin: str  # ISO 2-letter or standard name
    transit_countries: List[str] = Field(default_factory=list)
    destination_country: str
    permit_numbers: List[str] = Field(default_factory=list)
    declared_commercial_form: str  # e.g., "antique carvings", "raw timber", "fertilizer"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

### 2.2 Physical Inspection Schema (`schemas/inspection.py`)
```python
class MorphologyMeasurement(BaseModel):
    feature_name: str  # e.g., "schreger_angle_outer", "vessel_porosity", "dorsal_keels"
    value: Union[float, str, bool]
    unit: Optional[str] = None
    instrument: Optional[str] = None  # e.g., "optical_caliper", "microscope_20x", "fluorescence_uv365"
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)

class PhysicalInspection(BaseModel):
    inspection_id: str
    inspector_id: str
    checkpoint_location: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    observed_specimen_category: str  # e.g., "tusk_cross_section", "wood_transverse_section", "keratin_scales"
    measurements: List[MorphologyMeasurement]
    visual_characteristics: List[str]
    photos: List[str] = Field(default_factory=list)  # file paths or hashes
    notes: Optional[str] = None
```

### 2.3 Strict Forensic Output Schema (`schemas/forensic_output.py`)
```python
class LabAction(BaseModel):
    test_type: str  # "FTIR_spectroscopy", "radiocarbon_dating_c14", "dna_barcoding", "wood_anatomy_thin_section"
    priority: str   # "mandatory", "recommended", "optional"
    expected_discriminator: str

class UncertaintyBounds(BaseModel):
    lower_bound: float
    upper_bound: float
    confidence_interval: str  # e.g., "95%"

class ForensicTriageOutput(BaseModel):
    discrepancy_score: float = Field(ge=0.0, le=1.0)
    flagged_indicators: List[str]
    suspected_actual_species: str
    cites_appendix: str  # "I", "II", "III", or "None"
    smuggling_mo_detected: List[str]
    uncertainty_bounds: UncertaintyBounds
    suggested_lab_action: List[LabAction]
    forensic_rationale: str
    legal_disclaimer: str = (
        "AI findings provide investigative triage and do not constitute certified legal testimony. "
        "Formal seizure and prosecution require confirmatory forensic laboratory analysis."
    )
```

---

## 3. Schema-Constrained GBNF Decoding Harness

### 3.1 Grammar Generator Strategy
The system generates GBNF grammars directly from the Pydantic `ForensicTriageOutput` schema:
1. Extract the JSON schema representation from `ForensicTriageOutput.model_json_schema()`.
2. Convert the JSON Schema into a GBNF grammar string using an automated converter (`canopytrace.core.grammar`).
3. Pass the grammar to `llama_cpp.LlamaGrammar.from_string()` during inference.
4. Token generation is strictly constrained at the logit level: tokens violating the JSON grammar are masked out before softmax sampling.

### 3.2 Dual-Engine Execution Architecture
```
                     +---------------------------------------+
                     |       CanopyTrace Inference Request   |
                     +---------------------------------------+
                                         |
                                         v
                    +------------------------------------------+
                    | Check Environment & Model Availability   |
                    +------------------------------------------+
                       /                 |                  \
                      /                  |                   \
            Model Path Exists     Local Server URL      No Weights /
            & llama-cpp Installed    Configured         Test Environment
                   v                     v                    v
         +--------------------+  +---------------+  +------------------+
         | Direct Native GGUF |  | Local Server  |  | Deterministic    |
         | Execution with     |  | (Ollama/vLLM) |  | Offline Mock     |
         | GBNF Logit Masking |  | + JSON Schema |  | Heuristic Engine |
         +--------------------+  +---------------+  +------------------+
                   \                     |                    /
                    \                    |                   /
                     v                   v                  v
                   +------------------------------------------+
                   |  Strict ForensicTriageOutput Validation  |
                   +------------------------------------------+
```

---

## 4. Smuggling Modus Operandi (MO) Matching Engine

The pattern matching engine (`canopytrace.core.pattern_matcher`) cross-references manifest paperwork and physical inspection records against `data/smuggling_patterns.yaml`.

### 4.1 Pattern Rule Structure
```yaml
patterns:
  - id: "MO-IVO-001"
    name: "Antique Mammoth Ivory Camouflage"
    description: "Declaring modern elephant tusk as extinct mammoth ivory to bypass CITES Appendix I."
    triggers:
      declared_keywords: ["mammoth", "antique", "extinct"]
      physical_indicators: ["schreger_angle_outer > 105", "outer_pattern_present"]
    risk_weight: 0.95
    recommended_lab: "radiocarbon_dating_c14"
```

### 4.2 Matching Algorithm
1. Extract normalized tokens and keywords from manifest description and declared commercial form.
2. Evaluate morphology measurements against trigger boundary expressions.
3. If trigger conditions match, accumulate the pattern into `matched_patterns` and add weighted risk to the baseline discrepancy score.

---

## 5. Automated Alerting & Anomaly Escalation

### 5.1 Automated Authority Dispatcher (`canopytrace.alerts.dispatcher`)
- When `discrepancy_score >= SEIZURE_THRESHOLD` (default 0.70):
  - Generate an `AuthorityAlertPayload` containing:
    - `case_id`, `timestamp`, `port_location`
    - `severity`: "CRITICAL" | "HIGH"
    - `discrepancy_score`, `suspected_taxa`, `cites_appendix`
    - `matched_smuggling_mos`
    - `cryptographic_sha256`
  - Dispatch alert to configured endpoints:
    - HTTP Webhook (POST JSON to customs dispatch endpoint)
    - Local alert spool file (`data/alerts/alert_{case_id}.json`)
    - Standard Out / Terminal notification

### 5.2 Novel Anomaly Escalation Workflow (`canopytrace.escalation`)
- If physical traits do not match any known taxon or exhibit contradictory measurements:
  - Label triage status as `UNRESOLVED_NOVEL_ANOMALY`.
  - Add to pending escalation queue (`data/escalations/`).
  - Provide CLI/Web commands:
    - `canopytrace escalate list`: View pending unverified cases.
    - `canopytrace escalate approve <case_id> --species <species> --appendix <appendix>`: Scientific Authority verifies specimen and updates reference SQLite database with new taxonomy entry.

---

## 6. Multi-Format Dossier Compiler & Cryptographic Integrity

### 6.1 Cryptographic Chain-of-Custody
1. Aggregate manifest data, inspection logs, registry findings, pattern matches, and Gemma forensic synthesis.
2. Serialize canonical JSON string.
3. Compute SHA-256 digest: `sha256(canonical_json)`.
4. Embed SHA-256 hash in header of:
   - `dossier.json`
   - `dossier.md`
   - `dossier.pdf`
5. Write tamper-evident checksum file `dossier.sha256`.

### 6.2 Printable PDF Report Generation
- Built with ReportLab:
  - Custom customs enforcement banner & official seal layout.
  - Case metadata & chain-of-custody timestamps.
  - Discrepancy gauge & uncertainty interval chart.
  - Morphology measurement comparison table.
  - Concrete laboratory protocol instructions.
  - Mandatory legal non-definitive disclaimer.

---

## 7. Test-Driven Development (TDD) Strategy

### 7.1 Test Hierarchy & Coverage Goals
- **Unit Tests (`tests/unit/`):**
  - CITES registry queries, range-state checks, and fuzzy matching.
  - Morphology key calculators (Schreger angle validator, wood porosity matcher).
  - GBNF grammar parser and Pydantic validator.
  - Pattern matcher rule triggers.
  - Cryptographic hash computation and integrity checks.
- **Integration Tests (`tests/integration/`):**
  - Full pipeline: Manifest + Inspection -> Registry -> Morphology -> Gemma Harness -> Dossier.
  - CLI command invocations (`canopytrace inspect`, `canopytrace verify`).
  - REST API endpoint requests.
- **Benchmark Suite (`tests/test_benchmarks.py`):**
  - The 6 core realistic smuggling/compliance benchmark scenarios + 1 novel anomaly escalation case.

### 7.2 The 7 Benchmark Test Specifications

| Case ID | Declared Description | Physical Morphology Data | Expected Outcome | Expected Discrepancy |
|---|---|---|---|---|
| **BM-01** | Antique Mammoth Carvings | Schreger outer angle: 124° | Flagged as Modern Elephant (*Loxodonta* / *Elephas*); CITES App I | Discrepancy >= 0.85 |
| **BM-02** | Dried Bovine Horn / Keratin Flakes (Origin: Nigeria) | Curved imbricated scales, 3 dorsal keels | Flagged as Pangolin (*Manis tricuspis*); CITES App I | Discrepancy >= 0.90 |
| **BM-03** | Plantation Teak Logs (*Tectona grandis*) | Diffuse-porous, storied parenchyma, negative UV fluorescence | Flagged as Rosewood (*Dalbergia* spp.); CITES App II | Discrepancy >= 0.80 |
| **BM-04** | Decorative Synthetic Celluloid Crafts | Layered amber keratin scutes, no gas bubbles, no mold seams | Flagged as Hawksbill Sea Turtle (*Eretmochelys imbricata*); CITES App I | Discrepancy >= 0.85 |
| **BM-05** *(Negative Control)* | Handcrafted Bovine Bone Novelties | Haversian osteon canals present, Schreger pattern absent | Cleared as Domestic Bovine (*Bos taurus*); No CITES listing | Discrepancy <= 0.15 |
| **BM-06** | Wild specimen with CITES Export Permit | Origin declared from non-range country with zero quota | Flagged for fraudulent geographic origin & quota breach | Discrepancy >= 0.75 |
| **BM-07** *(Escalation)* | Rare unidentified wood/fauna fragment | Unknown anatomical traits outside reference database | Flagged as UNRESOLVED_NOVEL_ANOMALY; Queued for escalation | Escalation Status = True |

---

## 8. Development Phases & Milestones

1. **Step 1: Scaffolding & Virtual Environment**
   - Setup `pyproject.toml`, dependencies, and directory tree.
2. **Step 2: Reference Databases & Data Models**
   - Create data files (`cites_appendices.json`, `iucn_range_states.json`, `morphology_keys.yaml`, `smuggling_patterns.yaml`).
   - Implement SQLite seed and query module.
   - Implement Pydantic data schemas.
3. **Step 3: Agent Skills (`agentskills.io` Standard)**
   - `skills/cites-registry-check/`
   - `skills/morphology-fingerprint/`
   - `skills/case-dossier-compiler/`
4. **Step 4: Inference Harness & Pattern Matcher**
   - GBNF grammar generation.
   - Dual-engine Gemma harness with deterministic mock fallback.
   - Smuggling pattern matching algorithm.
   - Authority alert dispatcher and novel anomaly escalation workflow.
5. **Step 5: Dossier Compiler & Integrity Engine**
   - Markdown and JSON export with SHA-256 integrity stamp.
   - ReportLab PDF generator.
6. **Step 6: CLI & Local Web UI**
   - Click CLI commands.
   - FastAPI server with web dashboard and Schreger angle tool.
7. **Step 7: Flutter Mobile App**
   - Flutter companion app with offline capture and sync.
8. **Step 8: Automated Test Execution & Verification**
   - Run complete test suite and verify 100% benchmark compliance.
