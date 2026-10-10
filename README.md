# CanopyTrace 🌿🔍

**Open-Source AI Forensic Fingerprinting & Decision Support for Illegal Wildlife and Timber Trade Verification**

[![License: Apache 2.0 / MIT](https://img.shields.io/badge/License-Apache_2.0_/_MIT-blue.svg)](LICENSE)
[![Vercel Deployment](https://img.shields.io/badge/Vercel-Live%20App-000000?logo=vercel&logoColor=white)](https://canopytrace.vercel.app)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Google Gemma 4](https://img.shields.io/badge/Google%20Gemma%204-e2b--IT-purple.svg)](https://ollama.com)
[![agentskills.io](https://img.shields.io/badge/agentskills.io-compliant-green.svg)](https://agentskills.io)
[![Flutter 3.x](https://img.shields.io/badge/Flutter-Android_%7C_Linux-02569B.svg)](https://flutter.dev)

> 🌐 **Live Cloud Dashboard:** [**https://canopytrace.vercel.app**](https://canopytrace.vercel.app) — Explore interactive forensic triage, CITES quotas, and tamper-evident dossier generation in the browser.

---

## 📌 Mission & Overview

**CanopyTrace** is an open-source, investigative decision-support platform designed to counter transnational illegal wildlife and timber trafficking ($20B+ annual illicit trade). It empowers customs inspectors, border enforcement, and wildlife crime control bureaus at seaports and checkpoints to rapidly verify physical cargo against declared shipping paperwork, international CITES trade quotas, and documented smuggling modus operandi (MOs).

Traffickers routinely exploit administrative backlogs by camouflaging high-value banned contraband under legal commercial labels:
- **Elephant Ivory** declared as antique *Mammoth ivory* or modern *Bovine bone*.
- **Pangolin Scales** declared as *Bovine keratin flakes* or *Dried horn fragments*.
- **Protected Rosewood Timber (*Dalbergia*)** declared as plantation *Teak (*Tectona grandis*)*.
- **Hawksbill Sea Turtle Bekko** declared as decorative *Synthetic resin*.

CanopyTrace cross-references shipping manifests and physical micro-measurements using offline reference databases and local **Google Gemma 4 (`gemma4:e2b`)** reasoning under strict schema constraints. It compiles tamper-evident multi-format dossiers (PDF, Markdown, JSON) stamped with cryptographic SHA-256 digests and triggers automated emergency alerts to port authorities when contraband is detected.

> [!IMPORTANT]
> **Investigative Triage Legal Disclaimer:**
> *AI findings provide investigative triage and do not constitute certified legal testimony. Formal seizure and prosecution require confirmatory forensic laboratory analysis (FTIR spectroscopy, radiocarbon C14 bomb-pulse dating, or DNA barcoding).*

---

## 🏛️ System Architecture

CanopyTrace connects on-site mobile field inspection with desktop forensic computation:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             ON-SITE FIELD INSPECTION                             │
│                                                                                  │
│   📱 Flutter Mobile Field Companion         📷 Presentation Photo Evidence       │
│   • Contraband category selector            • High-resolution camera / gallery   │
│   • Interactive Schreger Caliper overlay    • Live macro-structural preview      │
│   • Offline inspection vault                • LAN Sync / USB ADB Port Forwarding │
└─────────────────────────────────────────┬────────────────────────────────────────┘
                                          │  Multipart HTTP Upload (/api/mobile/inspect)
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   CANOPYTRACE FORENSIC GATEWAY (DESKTOP SERVER)                  │
├──────────────────────────────────────────────────────────────────────────────────┤
│ 1. OFFLINE FORENSIC SKILLS (agentskills.io Open Standard):                       │
│    • skills/cites-registry-check/   -> CITES Appendices I/II/III & native ranges │
│    • skills/morphology-fingerprint/ -> Schreger angles (>115° vs <90°), vessels  │
│    • skills/case-dossier-compiler/  -> SHA-256 stamped evidentiary package       │
│                                                                                  │
│ 2. SCHEMA-CONSTRAINED GEMMA 4 REASONING ENGINE (gemma4:e2b):                     │
│    • Zero-hallucination JSON schema logit-masking                                │
│    • Discrepancy scoring (0.00 to 1.00) with 95% uncertainty bounds              │
│    • Contradiction detection & confirmatory laboratory test protocols (FTIR/C14) │
│                                                                                  │
│ 3. EVACUATION & DISPATCH:                                                        │
│    • If discrepancy >= 0.70 -> 🚨 Automated Local Authority Alert Dispatch       │
│    • If anomaly unrecognized -> 🔬 Higher Scientific Authority Escalation Queue   │
│    • Archival -> Permanent ReportLab PDF with embedded field photo & SHA-256     │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📸 Presentation Showcase: Mock Photos & Demos for Judges

When demonstrating CanopyTrace to judges or evaluators, use the following sample photos and benchmark scenarios to showcase each forensic capability:

| Scenario / Contraband | What Mock Photo to Download & Show | What to Set in App / Dashboard | Expected Forensic Finding |
|---|---|---|---|
| **1. Elephant Ivory Camouflage** | Cross-section cut of a tusk showing clear **criss-cross Schreger pattern lines** (lines intersecting near the outer dentine edge). | Declared: *Antique Mammoth Carvings*<br>Origin: `NG`<br>Category: `ivory`<br>Caliper Angle: `124°` | 🚨 **Discrepancy: 0.95 (Appendix I)**<br>Elephant ivory outer angle exceeds 115°, contradicting declared mammoth (<90°). Mandates **Radiocarbon C14** dating. Triggers **Local Authority Alert**. |
| **2. Pangolin Scales Concealment** | Macro close-up of brown keratin scales showing **3 dorsal keels** (raised parallel ridges) and overlapping shingle pattern. | Declared: *Dried Bovine Horn Flakes*<br>Origin: `NG`<br>Category: `keratin_scales` | 🚨 **Discrepancy: 0.95 (Appendix I)**<br>Multi-keeled keratin imbrication identifies *Manis tricuspis* (White-bellied pangolin), contradicting bovine cattle origin. |
| **3. Protected Rosewood Timber** | Microscopic end-grain wood pore photograph showing **diffuse porous vessels** and ripple marks on tangential face. | Declared: *Plantation Teak Logs*<br>Origin: `LA`<br>Category: `timber` | 🚨 **Discrepancy: 0.88 (Appendix I)**<br>Diffuse porosity and storied ripple rays match Brazilian / Siamese Rosewood (*Dalbergia*), contradicting ring-porous teak (*Tectona grandis*). |
| **4. Hawksbill Bekko Turtle Shell** | Polished translucent amber-brown mottled plate with **distinct overlapping scute layers** and no air bubbles. | Declared: *Decorative Synthetic Resin*<br>Origin: `ID`<br>Category: `marine_reptile` | 🚨 **Discrepancy: 0.90 (Appendix I)**<br>Keratin scute layering identifies *Eretmochelys imbricata* (Hawksbill sea turtle). Synthetic resin imitation debunked. |
| **5. Bovine Bone (Negative Control)** | Cross-section of carved ornament showing **microscopic Haversian canals (osteons)** with dark pinpoint vascular dots. | Declared: *Bovine Bone Handicrafts*<br>Origin: `IN`<br>Category: `bone` | 🟢 **Discrepancy: 0.08 (Cleared)**<br>Haversian canal morphology confirms domestic cattle (*Bos taurus*). Cleared for routine customs release without alarm. |
| **6. Unresolved Novel Anomaly** | Unfamiliar crystalline/organic fiber sample with atypical micro-structural measurements. | Declared: *Exotic Mineral Specimen*<br>Origin: `BR`<br>Category: `unknown` | 🔬 **Novel Anomaly Escalation**<br>Flagged as `UNRESOLVED_NOVEL_ANOMALY`. Queued into Higher Scientific Authority portal for species verification and database learning loop. |

> [!TIP]
> **Judge Presentation Flow:**
> 1. Show the **Mobile Phone App** taking or picking a photo of ivory with the **interactive Schreger protractor overlay** set to 124°.
> 2. Tap **"Upload & Run Gemma 4 Triage"**.
> 3. Watch the desktop dashboard instantly receive the photo, evaluate it with Gemma 4, pop the red **🚨 Local Authority Alert**, and generate a printable ReportLab PDF with the photo embedded inside.
> 4. Click **📁 Archived Dossiers** on the desktop to demonstrate full evidentiary chain-of-custody with SHA-256 hashes.

---

## 🚀 Quickstart & Setup

### 1. Prerequisites
- **Python 3.10+** (Linux / macOS / Windows WSL)
- **Ollama** running locally with **Google Gemma 4**:
  ```bash
  ollama run gemma4:e2b
  ```
- *(Optional)* **Flutter 3.x** for the mobile companion app.

### 2. Desktop Server Installation
```bash
# Clone repository
git clone https://github.com/Atreyee0508/CanopyTrace.git
cd CanopyTrace

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in editable mode
pip install -e ".[dev]"

# Seed the offline SQLite forensic reference database
canopytrace db seed
```

### 3. Launch Desktop Server & Web Dashboard
```bash
# Run server on port 8001 (accessible across local network)
canopytrace serve --host 0.0.0.0 --port 8001
```
Open **`http://localhost:8001`** in your browser:
- **Interactive Triage:** Select any benchmark or upload a downloaded photo.
- **Schreger Caliper:** Real-time proboscidean dentine classification slider.
- **Archived Dossiers Vault:** Click the top button to browse all saved case files.
- **Mobile Pairing Modal:** Click `Mobile Link` to view the pairing QR code.

---

## 📱 Running the Mobile Companion App

The Flutter mobile companion app lives in `mobile/`. It runs on Android phones or as a native Linux desktop window.

### Running on a Connected Android Phone (via USB ADB):
```bash
# 1. Reverse port 8001 over USB (zero network configuration required!)
adb reverse tcp:8001 tcp:8001

# 2. Run app on your connected device
cd ~/CanopyTrace/mobile
flutter run
```

### Running on Linux Desktop (No phone required):
```bash
cd ~/CanopyTrace/mobile
flutter run -d linux
```

### In-App Pairing Settings:
- If connected via **USB (`adb reverse`)** or running on **Linux Desktop**: Enter `http://127.0.0.1:8001`.
- If connected over **Physical Wi-Fi**: Enter your computer's LAN IP, e.g., `http://192.168.x.x:8001`.
- Tap **Test Connection & Save** to verify `Model: gemma4:e2b`.

---

## 🧪 Automated Test Suite & Benchmarks

CanopyTrace includes a comprehensive automated test suite verifying 100% of forensic invariants, schema constraints, and realistic smuggling scenarios:

```bash
# Run all unit and integration tests
pytest -v

# Run the 7 realistic smuggling & compliance benchmarks
pytest tests/test_benchmarks.py -v

# Test with coverage
pytest --cov=src/canopytrace tests/
```
*Current test suite: **35 passing tests in ~1.5s** (including end-to-end mobile photo multipart upload, authority alert triggers, and GBNF grammar validation).*

---

## 📂 Project Repository Structure

```
CanopyTrace/
├── PRD.md                           # Product Requirements Document
├── TDD.md                           # Technical Design & Test-Driven Development Plan
├── ARCHITECTURE.md                  # Architectural Sequence Diagrams & Data Flows
├── AGENTS.md                        # Instructions for autonomous AI agents
├── GEMINI.md                        # Gemini / Antigravity development guidelines
├── pyproject.toml                   # Project configuration and CLI entrypoint
│
├── data/                            # Offline Forensic Reference Data
│   ├── cites_appendices.json        # CITES Appendices I, II, III taxonomy & trade bans
│   ├── iucn_range_states.json       # Native species distribution by ISO country code
│   ├── morphology_keys.yaml         # Physical diagnostic rules (Schreger lines, porosity)
│   ├── smuggling_patterns.yaml      # Documented wildlife trafficking modus operandi
│   ├── reference.db                 # Compiled offline SQLite 3 database
│   └── alerts/                      # Dispatched local authority alert incident records
│
├── skills/                          # agentskills.io Open Standard Skills
│   ├── cites-registry-check/        # Appendix and geographic range audit skill
│   ├── morphology-fingerprint/      # Micro-structural measurement evaluation skill
│   └── case-dossier-compiler/       # Tamper-evident multi-format dossier compiler
│
├── src/canopytrace/                 # Python Core Backend Package
│   ├── cli.py                       # CLI interface (`canopytrace inspect`, `serve`)
│   ├── schemas/                     # Pydantic v2 schemas (manifest, inspection, forensic_output)
│   ├── core/                        # Gemma 4 harness, GBNF grammar, pipeline orchestrator
│   ├── db/                          # SQLite engine, migrations, FTS5 full-text search
│   ├── alerts/                      # Automated local authority alert dispatcher
│   ├── escalation/                  # Novel anomaly escalation queue & learning loop
│   ├── dossier/                     # ReportLab PDF, Markdown, and JSON compiler
│   └── web/                         # FastAPI gateway and dark glassmorphic dashboard
│
├── mobile/                          # Flutter Mobile Companion App (Offline-First)
│   ├── lib/screens/                 # Camera capture, Schreger overlay, Dossier view, Vault
│   ├── lib/services/api_service.dart# Multipart photo upload, health check, local caching
│   ├── android/                     # Android platform runner with camera/network permissions
│   └── linux/                       # Linux desktop runner
│
├── output/                          # Evidentiary Dossier Archive (PDF, JSON, MD, SHA-256)
│   └── CASE-MOB-XXXXXX/             # Archived case folders with embedded field photos
│
└── tests/                          # Automated Pytest Suite (35 tests)
    ├── test_benchmarks.py           # The 7 core smuggling and compliance scenarios
    ├── test_cites_check.py          # Appendices and geographic range tests
    ├── test_morphology.py           # Morphology rule and angle tests
    ├── test_grammar_decoding.py     # Schema validation and GBNF tests
    ├── test_alerts.py               # Authority alert dispatch tests
    ├── test_dossier_integrity.py    # Multi-format compilation and SHA-256 stamps
    └── test_web.py                  # Web dashboard and mobile multipart upload tests
```

---

## ⚖️ Open Source License & Compliance

CanopyTrace is open source software dual-licensed under the **Apache 2.0** and **MIT** licenses. Built in compliance with **CITES Article VIII** enforcement guidelines and the **agentskills.io** open agent interoperability standard.