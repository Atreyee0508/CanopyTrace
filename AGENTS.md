# AGENTS.md - Agent Operations & Contribution Guide

Welcome to the **CanopyTrace** repository. This document serves as the primary operational instruction manual for autonomous AI agents, coding assistants, and automated multi-agent systems collaborating on this project.

---

## 1. Project Mission & Identity

- **Name:** CanopyTrace (Package: `canopytrace`, CLI: `canopytrace`)
- **Mission:** Open-source AI forensic fingerprinting and investigative decision-support platform for verifying declared shipping manifests against physical morphology, international CITES trade quotas, and known smuggling patterns.
- **Core Stance:** The platform is an **investigative triage assistant**, not a courtroom-certified definitive verdict. AI findings guide on-site customs detention decisions and recommend confirmatory laboratory tests (FTIR, radiocarbon, DNA barcoding).
- **License:** Apache 2.0.

---

## 2. Repository Structure & Key Paths

```
CanopyTrace/
├── PRD.md                           # Product Requirements Document
├── TDD.md                           # Technical Design & Test-Driven Development Plan
├── ARCHITECTURE.md                  # System Architecture & Sequence Diagrams
├── AGENTS.md                        # Instructions for autonomous AI agents (this file)
├── GEMINI.md                        # Project-specific guidelines for Gemini/Antigravity
├── pyproject.toml                   # Project configuration, dependencies, and CLI script entry
│
├── data/                            # Offline Reference Data Sources
│   ├── cites_appendices.json        # CITES Appendices I, II, III taxonomy & trade bans
│   ├── iucn_range_states.json       # Native geographic ranges by ISO country code
│   ├── morphology_keys.yaml         # Identification keys (Schreger angles, timber porosity)
│   ├── smuggling_patterns.yaml      # Documented wildlife trafficking modus operandi (MOs)
│   └── reference.db                 # Compiled offline SQLite 3 database
│
├── skills/                          # agentskills.io Open Standard Skills
│   ├── cites-registry-check/        # Appendix and geographic range audit skill
│   │   ├── SKILL.md                 # Progressive disclosure specification
│   │   └── check_registry.py        # Executable runner script
│   ├── morphology-fingerprint/      # Micro-structural measurement evaluation skill
│   │   ├── SKILL.md                 # Progressive disclosure specification
│   │   └── fingerprint.py           # Executable runner script
│   └── case-dossier-compiler/       # Tamper-evident multi-format dossier compiler
│       ├── SKILL.md                 # Progressive disclosure specification
│       └── compile_dossier.py       # Executable runner script
│
├── src/canopytrace/                 # Python Core Backend Package
│   ├── cli.py                       # Command line interface (`canopytrace ...`)
│   ├── schemas/                     # Pydantic v2 schemas (manifest, inspection, forensic_output)
│   ├── core/                        # Inference harness, GBNF grammar, pattern matcher, pipeline
│   ├── db/                          # SQLite schema, migrations, seed script, FTS5 search
│   ├── escalation/                  # Novel anomaly escalation queue & authority approval hook
│   ├── alerts/                      # Automated local authority alert dispatcher
│   ├── dossier/                     # PDF, Markdown, and JSON compiler with SHA-256 stamps
│   └── web/                         # FastAPI application and responsive field Web UI
│
├── mobile/                          # Flutter Mobile Companion App (Offline-First)
│   ├── lib/                         # Mobile screens, models, Schreger caliper tool, API sync
│   └── test/                        # Flutter widget and unit tests
│
└── tests/                          # Pytest Automated Test Suite
    ├── test_cites_check.py          # Appendix and range tests
    ├── test_morphology.py           # Morphology rule tests
    ├── test_grammar_decoding.py     # GBNF schema compliance tests
    ├── test_smuggling_patterns.py   # Modus operandi detection tests
    ├── test_escalation.py           # Unknown anomaly escalation and DB update
    ├── test_alerts.py               # Authority alert dispatch tests
    ├── test_dossier_integrity.py    # Multi-format compilation and SHA-256 stamps
    └── test_benchmarks.py           # The 6 core realistic smuggling scenarios + escalation
```

---

## 3. Core Development Principles & Invariants

When modifying or extending this codebase, all agents **MUST** respect the following non-negotiable invariants:

### 3.1 Strict Schema Constraints (Zero Hallucinations)
- All LLM interactions must be constrained by Context-Free Grammars (GBNF) derived from `schemas/forensic_output.py`.
- Never bypass schema validation. If `llama-cpp-python` is not available or weights are absent, always utilize the deterministic offline mock engine (`MockForensicHarness`) which enforces the exact same schema.

### 3.2 Non-Definitive Legal Disclaimer
- Every output artifact, screen, CLI summary, and generated PDF/Markdown/JSON dossier must include the mandatory non-definitive legal disclaimer:
  > *"AI findings provide investigative triage and do not constitute certified legal testimony. Formal seizure and prosecution require confirmatory forensic laboratory analysis."*

### 3.3 Cryptographic Integrity (Chain-of-Custody)
- All compiled dossiers must include a SHA-256 digest computed over the canonical JSON representation of the case data.
- Never alter a dossier after hashing; any update creates a new revision with its own cryptographic timestamp.

### 3.4 agentskills.io Compliance
- Skills inside `skills/<skill-name>/` must adhere to the `agentskills.io` standard:
  - Each skill directory must contain a valid `SKILL.md` with YAML frontmatter (`name`, `description`, `version`, `inputs`, `outputs`).
  - Each skill must include a standalone, self-sufficient executable Python script that can be run directly from the shell or imported as a module.

---

## 4. Environment & Tooling Commands

### 4.1 Dependency Management & Virtualenv
Use `uv` or standard Python `venv`:
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies in editable mode
pip install -e ".[dev]"
```

### 4.2 Seed Offline Reference Database
```bash
# Seed or rebuild the SQLite database from YAML/JSON sources
canopytrace db seed
# or
python -m canopytrace.db.seed
```

### 4.3 Running the Test Suite
```bash
# Run all unit tests, integration tests, and benchmarks
pytest -v

# Run the 7 realistic smuggling & compliance benchmarks
pytest tests/test_benchmarks.py -v

# Run with test coverage
pytest --cov=src/canopytrace tests/
```

### 4.4 Running the CLI
```bash
# Inspect a manifest against physical measurements
canopytrace inspect --manifest sample_manifest.json --inspection sample_inspection.json

# Check smuggling patterns
canopytrace patterns list

# Compile an evidentiary case dossier
canopytrace dossier compile --case-id CASE-2026-001 --outdir ./output/

# Launch local Web UI dashboard
canopytrace serve --host 127.0.0.1 --port 8000
```

---

## 5. Adding New Taxa, Morphology Keys, or Smuggling Patterns

Agents tasked with expanding CanopyTrace's forensic scope should follow these guidelines:

1. **Adding CITES Taxa:**
   - Edit `data/cites_appendices.json`.
   - Include: `scientific_name`, `common_names`, `appendix` ("I", "II", "III"), `commercial_status` ("BANNED", "QUOTA_CONTROLLED", "REGULATED"), and `annotations`.
   - Update `data/iucn_range_states.json` with valid ISO 2-letter country codes representing native distribution.
   - Run `canopytrace db seed` to synchronize SQLite tables.

2. **Adding Morphology Identification Keys:**
   - Edit `data/morphology_keys.yaml`.
   - Define diagnostic rules (e.g. Schreger angles, vessel porosity, scale count) with operator (`gt`, `lt`, `eq`, `between`) and threshold values.
   - Add corresponding test cases in `tests/test_morphology.py`.

3. **Adding Smuggling Patterns (Modus Operandi):**
   - Edit `data/smuggling_patterns.yaml`.
   - Define pattern ID (e.g. `MO-TIM-002`), name, description, trigger keywords, physical indicators, risk weight (0.0 to 1.0), and recommended confirmatory lab assays.
   - Add test case in `tests/test_smuggling_patterns.py`.

---

## 6. Novel Anomaly Escalation Protocol

If an inspection presents contradictory measurements or unrecognized morphology:
1. Set triage status to `UNRESOLVED_NOVEL_ANOMALY`.
2. Generate an escalation record in `data/escalations/{case_id}.json`.
3. Higher scientific authorities review and approve via:
   ```bash
   canopytrace escalate approve <case_id> --species "Species name" --appendix "I"
   ```
4. This command automatically writes the verified finding into SQLite so future inspections immediately recognize the pattern.

---

## 7. Automated Local Authority Alert Protocol

When `discrepancy_score >= 0.70`:
1. Dispatcher generates an urgent incident payload (`schemas/alert.py`).
2. Payload contains port location, container ID, suspect taxa, seizure urgency rating, and cryptographic case ID.
3. Automatically writes alert record to `data/alerts/alert_{case_id}.json` and dispatches to configured webhooks.
