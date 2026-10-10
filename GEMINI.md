# GEMINI.md - Assistant Guidelines for CanopyTrace

## 1. Project Context & Mission

You are working on **CanopyTrace**, an open-source AI forensic fingerprinting and investigative decision-support platform designed to counter illegal wildlife and timber trafficking.

The system empowers customs inspectors and wildlife law enforcement at border checkpoints and shipping container ports to verify physical contraband (elephant ivory, pangolin scales, protected rosewood timber, big cat derivatives, sea turtle bekko) against fraudulent cargo manifests and counterfeit CITES permits.

---

## 2. Technical Stack & Key Technologies

- **Language & Runtime:** Python 3.10+ (managed with `pyproject.toml` and `uv`).
- **Open-Weight LLM:** Google Gemma 2 2B Instruct (Q4_K_M GGUF format).
- **Decoding Engine:** `llama-cpp-python` with Context-Free Grammar (GBNF) logit masking to enforce strict JSON schemas.
- **Embedded Database:** SQLite 3 with WAL mode, FTS5 full-text search, and indexed tables.
- **Data Validation:** Pydantic v2 (`BaseModel`, `Field`, `model_json_schema()`).
- **Web UI & REST API:** FastAPI + Jinja2 + HTML5/Tailwind + Uvicorn.
- **CLI:** Click + Rich for colorful, auditable terminal inspection outputs.
- **Dossier Generation:** ReportLab (customs-grade printable PDF) + Markdown2 + SHA-256 integrity digests.
- **Open Agent Standard:** `agentskills.io` compliant skill directories (`SKILL.md` + standalone runner).
- **Mobile Client:** Flutter / Dart 3.x cross-platform mobile companion with offline-first local capture.

---

## 3. Strict Development Invariants

As a Gemini / Antigravity coding assistant, always adhere to the following principles:

### 3.1 Zero Hallucinations via GBNF Grammars
- Never rely on unconstrained free-form text completions for forensic calculations.
- Gemma 2 outputs must strictly conform to the `ForensicTriageOutput` Pydantic schema via GBNF grammars.
- Maintain the deterministic mock fallback (`MockForensicHarness`) so all unit and integration tests run in seconds without requiring multi-gigabyte GGUF weights.

### 3.2 Mandatory Non-Definitive Legal Disclaimer
- Every user-facing output (CLI, Web UI, PDF, Markdown, JSON) must prominently include:
  > *"AI findings provide investigative triage and do not constitute certified legal testimony. Formal seizure and prosecution require confirmatory forensic laboratory analysis."*

### 3.3 Cryptographic Integrity (SHA-256)
- Every compiled case file must be stamped with a SHA-256 checksum calculated across the canonical JSON representation.
- Never write or modify a case without recalculating or validating its hash.

### 3.4 Automated Authority Alerting
- If `discrepancy_score >= 0.70`, automatically generate and dispatch an emergency alert payload containing port location, container ID, suspect taxa, and seizure urgency.

### 3.5 Novel Anomaly Escalation Loop
- When an item cannot be identified or exhibits conflicting morphology, set status to `UNRESOLVED_NOVEL_ANOMALY` and queue it for Higher Scientific Authority review.
- Provide the database update hook so approved novel taxa automatically enrich the offline SQLite registry.

---

## 4. Coding Standards & Conventions

### 4.1 Python Standards
- Use modern Python 3.10+ syntax: `list[str]`, `dict[str, Any]`, `X | Y` union operators.
- Fully type-annotate all functions and methods.
- Use Pydantic v2 methods (`model_dump()`, `model_validate()`, `model_json_schema()`).
- Maintain clean separation of concerns:
  - `schemas/`: Pure data models.
  - `db/`: Database operations and migrations.
  - `core/`: Business logic, inference, grammars, and pattern matching.
  - `skills/`: `agentskills.io` compliant modular scripts.
  - `dossier/`: Multi-format report compilation and PDF generation.
  - `alerts/`: Notification and webhook dispatchers.
  - `escalation/`: Authority review and database updating.
  - `cli.py`: Click commands.
  - `web/`: FastAPI routes and dashboard.

### 4.2 Error Handling
- Never allow an unhandled exception to crash the CLI or Web UI.
- Wrap external file reads, GGUF invocations, and database queries in descriptive `try...except` blocks with fallback handling.

### 4.3 Clickable Links & Formatting
- Always provide clickable markdown links with `file://` scheme to relevant files and line numbers when summarizing work for the user.

---

## 5. Standard Test Suite Execution

Always verify your changes with pytest:
```bash
# Run all tests
pytest -v

# Run the 6 smuggling benchmarks + escalation test
pytest tests/test_benchmarks.py -v
```
Ensure all 7 benchmark scenarios pass with 100% assertion accuracy.
