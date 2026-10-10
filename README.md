# CanopyTrace 🌿🔍

**AI Forensic Fingerprinting & Decision Support for Illegal Wildlife and Timber Trade Verification**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![agentskills.io](https://img.shields.io/badge/agentskills.io-compliant-green.svg)](https://agentskills.io)
[![Gemma 2](https://img.shields.io/badge/Google%20Gemma%202-2B--IT%20GGUF-purple.svg)](https://huggingface.co/google/gemma-2-2b-it)

---

## 📌 Overview

**CanopyTrace** is an open-source, investigative decision-support platform that empowers customs officers, border control authorities, and wildlife crime control bureaus to verify physical cargo against shipping paperwork, international CITES trade quotas, and known smuggling patterns.

Traffickers routinely disguise high-value contraband (such as elephant ivory, pangolin scales, protected rosewood, and sea turtle bekko) under legal declarations (such as antique mammoth carvings, bovine bone crafts, synthetic resin, or plantation teak). CanopyTrace performs rapid on-site forensic triage to flag contradictions, calculate uncertainty bounds, detect smuggling modus operandi, and compile tamper-evident case dossiers with SHA-256 integrity digests.

> [!IMPORTANT]
> **Investigative Support Non-Definitive Legal Disclaimer:**
> *AI findings provide preliminary investigative triage and do not constitute certified legal testimony. Formal seizure and prosecution require confirmatory forensic laboratory analysis (e.g. FTIR spectroscopy, radiocarbon dating, or DNA barcoding).*

---

## 🏛️ System Architecture

CanopyTrace operates across four integrated tiers:
1. **Field Ingestion Tier:** Captures shipping manifests and physical macro-inspection data via CLI (`canopytrace`), local responsive Web UI, and a cross-platform Flutter mobile field companion.
2. **Deterministic Forensic Skills (`agentskills.io`):** Modular, reproducible offline skills querying local SQLite reference databases and matching documented smuggling patterns.
3. **Schema-Constrained Gemma 2 Reasoning Tier:** Quantized Google Gemma 2 2B Instruct GGUF executing under Context-Free Grammars (GBNF) for zero-hallucination JSON schema output, backed by an offline mock fallback for CI and low-resource laptops.
4. **Evidentiary Dispatch Tier:** Multi-format tamper-evident dossiers (PDF, Markdown, JSON + SHA-256), automated local authority alert dispatch, and a novel anomaly escalation queue for Higher CITES Scientific Authority review and continuous database enrichment.

```
                              [ Customs Shipping Manifest + Physical Inspection ]
                                                      │
                                                      ▼
                            ┌───────────────────────────────────────────────────┐
                            │      CanopyTrace Forensic Verification Gateway    │
                            └───────────────────────────────────────────────────┘
                                  │                     │                   │
                                  ▼                     ▼                   ▼
                      [ CITES Registry Check ] [ Morphology Key ] [ Smuggling MO ]
                       (Appendices & Ranges)    (Schreger/Porosity)  (Trafficking Patterns)
                                  │                     │                   │
                                  └─────────────────────┼───────────────────┘
                                                        │
                                                        ▼
                                       ┌────────────────────────────────┐
                                       │ Google Gemma 2 2B GGUF Engine  │
                                       │   (GBNF Schema-Constrained)    │
                                       └────────────────────────────────┘
                                                        │
                                                        ▼
                                       ┌────────────────────────────────┐
                                       │     Forensic Triage Output     │
                                       │ (Discrepancy Score, Lab Action)│
                                       └────────────────────────────────┘
                                          │                          │
                 ┌────────────────────────┴────────┐                 ▼
                 ▼                                 ▼       [ Multi-Format Dossier ]
     [ Discrepancy >= 0.70 ]             [ Novel Anomaly ]  • Printable Customs PDF
     🚨 Automated Authority Alert        🔬 CITES Authority • Tamper-evident Markdown
     (Emergency Seizure Dispatch)           Escalation Queue • Cryptographic JSON (SHA-256)
```

---

## 📂 Documentation & Specifications

- 📄 [PRD.md](PRD.md) — Product Requirements Document, user personas, functional specifications.
- 📐 [TDD.md](TDD.md) — Technical Design Document, data models, GBNF grammar specs, and 7 benchmark cases.
- 🏗️ [ARCHITECTURE.md](ARCHITECTURE.md) — Architectural sequence diagrams and component deep dives.
- 🤖 [AGENTS.md](AGENTS.md) — Operational manual and contribution guide for autonomous AI agents.
- 💎 [GEMINI.md](GEMINI.md) — Coding conventions and assistant guidelines.

---

## 🛠️ Quickstart

### 1. Installation
```bash
git clone https://github.com/Atreyee0508/CanopyTrace.git
cd CanopyTrace

# Setup Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

### 2. Seed Offline Reference Database
```bash
canopytrace db seed
```

### 3. Run Benchmark Test Suite
```bash
pytest -v
```

### 4. Start Local Web Dashboard
```bash
canopytrace serve --host 127.0.0.1 --port 8000
```

---

## 📜 License

Licensed under the [MIT License](LICENSE).