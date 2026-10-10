"""FastAPI local server providing REST API and responsive field web dashboard."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from canopytrace.core.pipeline import run_forensic_pipeline
from canopytrace.db import get_all_smuggling_patterns
from canopytrace.escalation import list_pending_escalations, approve_and_ingest_novel_finding
from canopytrace.schemas import ShippingManifest, PhysicalInspection

app = FastAPI(
    title="CanopyTrace Forensic API",
    description="AI Forensic Fingerprinting for Illegal Wildlife & Timber Trade Verification",
    version="0.1.0",
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "output"

STATIC_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/api/health")
def health_check() -> Dict[str, str]:
    return {"status": "healthy", "service": "CanopyTrace"}


@app.get("/api/patterns")
def list_patterns() -> List[Dict[str, Any]]:
    return get_all_smuggling_patterns()


@app.get("/api/escalations")
def get_escalations() -> List[Dict[str, Any]]:
    return list_pending_escalations()


@app.post("/api/escalate/approve")
def approve_escalation(
    case_id: str = Form(...),
    species: str = Form(...),
    appendix: str = Form(...),
    notes: str = Form("Verified by Scientific Authority"),
) -> Dict[str, Any]:
    success = approve_and_ingest_novel_finding(
        case_id=case_id,
        verified_species=species,
        verified_appendix=appendix,
        authority_notes=notes,
    )
    return {"success": success, "case_id": case_id, "species": species}


from canopytrace.core.harness import get_forensic_harness

@app.post("/api/inspect")
async def inspect_cargo(request: Request) -> Dict[str, Any]:
    try:
        body = await request.json()
        manifest_data = body.get("manifest")
        inspection_data = body.get("inspection")
        case_id = body.get("case_id")
        model_name = body.get("model", "gemma4:e2b")

        if not manifest_data or not inspection_data:
            raise HTTPException(status_code=400, detail="Missing 'manifest' or 'inspection' payload.")

        manifest = ShippingManifest.model_validate(manifest_data)
        inspection = PhysicalInspection.model_validate(inspection_data)

        harness = get_forensic_harness(model_name=model_name)
        res = run_forensic_pipeline(manifest, inspection, case_id=case_id, harness=harness)
        # Format for JSON return
        return {
            "case_id": res["case_id"],
            "discrepancy_score": res["discrepancy_score"],
            "suspected_species": res["suspected_species"],
            "cites_appendix": res["cites_appendix"],
            "flagged_indicators": res["flagged_indicators"],
            "smuggling_mos": res["smuggling_mos"],
            "forensic_output": res["forensic_output"].model_dump(),
            "alert_dispatched": res["alert_dispatched"],
            "is_novel_escalation": res["is_novel_escalation"],
            "dossier_package": res["dossier_package"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dossier/{case_id}/pdf")
def download_pdf(case_id: str):
    pdf_path = OUTPUT_DIR / case_id / f"{case_id}_dossier.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Dossier PDF not found.")
    return FileResponse(str(pdf_path), media_type="application/pdf", filename=f"{case_id}_dossier.pdf")


@app.get("/api/dossier/{case_id}/markdown")
def download_markdown(case_id: str):
    md_path = OUTPUT_DIR / case_id / f"{case_id}_dossier.md"
    if not md_path.exists():
        raise HTTPException(status_code=404, detail="Dossier Markdown not found.")
    return FileResponse(str(md_path), media_type="text/markdown", filename=f"{case_id}_dossier.md")


@app.get("/api/dossier/{case_id}/json")
def download_json(case_id: str):
    json_path = OUTPUT_DIR / case_id / f"{case_id}_dossier.json"
    if not json_path.exists():
        raise HTTPException(status_code=404, detail="Dossier JSON not found.")
    return FileResponse(str(json_path), media_type="application/json", filename=f"{case_id}_dossier.json")


@app.get("/", response_class=HTMLResponse)
def dashboard_html() -> str:
    """Returns the single-page responsive customs inspection dashboard."""
    html_file = STATIC_DIR / "index.html"
    if html_file.exists():
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>CanopyTrace Dashboard</h1><p>Static index.html not found.</p>"
