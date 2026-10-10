"""FastAPI local server providing REST API and responsive field web dashboard."""

import json
import os
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

# In serverless environments like Vercel, the filesystem outside /tmp is read-only
if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    OUTPUT_DIR = Path("/tmp/canopytrace/output")
else:
    OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "output"

try:
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    OUTPUT_DIR = Path("/tmp/canopytrace/output")
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

        cid = case_id or f"CASE-{manifest.manifest_id}"
        case_dir = OUTPUT_DIR / cid
        harness = get_forensic_harness(model_name=model_name)
        res = run_forensic_pipeline(manifest, inspection, case_id=cid, output_dir=case_dir, harness=harness)
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


def get_local_ip() -> str:
    """Finds the local network IP address of the machine."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


@app.get("/api/server-info")
def server_info(request: Request) -> Dict[str, Any]:
    """Returns the server's local LAN address and status for mobile QR pairing."""
    port = request.url.port or 8001
    local_ip = get_local_ip()
    return {
        "status": "online",
        "service": "CanopyTrace Forensic Gateway",
        "local_ip": local_ip,
        "port": port,
        "base_url": f"http://{local_ip}:{port}",
        "active_model": os.environ.get("CANOPYTRACE_LLM_MODEL", "gemma4:e2b"),
    }


from fastapi import UploadFile, File
import shutil
import uuid
from canopytrace.schemas import MorphologyMeasurement

@app.post("/api/mobile/inspect")
async def inspect_mobile_cargo(
    photo: Optional[UploadFile] = File(None),
    category: Optional[str] = Form(None),
    specimen_category: Optional[str] = Form(None),
    declared_item: str = Form(...),
    declared_scientific: Optional[str] = Form(None),
    origin_country: Optional[str] = Form(None),
    country_of_origin: Optional[str] = Form(None),
    checkpoint_location: str = Form("Mobile Port Terminal Unit"),
    caliper_angle: Optional[float] = Form(None),
    schreger_angle: Optional[float] = Form(None),
    model: str = Form("gemma4:e2b"),
    case_id: Optional[str] = Form(None),
) -> Dict[str, Any]:
    """
    Ingests mobile camera photo and field inspection data:
    1. Saves and archives photo permanently in desktop output directory (or generates placeholder if omitted).
    2. Constructs physical measurements.
    3. Runs schema-constrained Gemma 4 e2b triage pipeline.
    4. Automatically dispatches authority alerts if discrepancy threshold is breached.
    5. Returns comprehensive evidentiary dossier package to mobile client.
    """
    try:
        cid = case_id or f"CASE-MOB-{uuid.uuid4().hex[:6].upper()}"
        case_dir = OUTPUT_DIR / cid
        case_dir.mkdir(parents=True, exist_ok=True)

        # 1. Save uploaded photo permanently on desktop (or create clean specimen placeholder)
        photo_path = None
        if photo and photo.filename:
            photo_filename = f"inspection_{photo.filename}"
            photo_path = case_dir / photo_filename
            with open(photo_path, "wb") as buffer:
                shutil.copyfileobj(photo.file, buffer)
        else:
            # Generate clean fallback evidence image
            from PIL import Image, ImageDraw
            photo_filename = f"inspection_placeholder_{cid}.jpg"
            photo_path = case_dir / photo_filename
            img = Image.new("RGB", (400, 300), color=(15, 23, 42))
            draw = ImageDraw.Draw(img)
            draw.text((20, 140), f"Specimen Evidence: {cid}", fill=(16, 185, 129))
            img.save(photo_path, format="JPEG")

        # 2. Build physical measurements based on category and caliper angle
        resolved_category = (category or specimen_category or "unknown").lower().strip()
        resolved_angle = caliper_angle if caliper_angle is not None else schreger_angle
        resolved_origin = (origin_country or country_of_origin or "NG").strip().upper()

        measurements: List[MorphologyMeasurement] = []
        cat_lower = resolved_category

        if "ivory" in cat_lower:
            angle_val = float(resolved_angle) if resolved_angle is not None else 124.0
            measurements = [
                MorphologyMeasurement(feature_name="schreger_angle_outer", value=angle_val, unit="degrees", instrument="mobile_caliper"),
                MorphologyMeasurement(feature_name="haversian_canals_present", value=False),
                MorphologyMeasurement(feature_name="molding_seams_present", value=False),
            ]
        elif "scale" in cat_lower or "keratin" in cat_lower or "pangolin" in cat_lower:
            measurements = [
                MorphologyMeasurement(feature_name="dorsal_keel_count", value=3, instrument="mobile_macro_lens"),
                MorphologyMeasurement(feature_name="imbrication_pattern", value="overlapping_shingle"),
            ]
        elif "timber" in cat_lower or "wood" in cat_lower:
            measurements = [
                MorphologyMeasurement(feature_name="vessel_porosity", value="diffuse_porous", instrument="mobile_lens"),
                MorphologyMeasurement(feature_name="storied_rays_ripple_marks", value=True),
                MorphologyMeasurement(feature_name="uv_water_fluorescence", value="negative"),
            ]
        elif "turtle" in cat_lower or "bekko" in cat_lower or "reptile" in cat_lower:
            measurements = [
                MorphologyMeasurement(feature_name="scute_layering", value="imbricate_keratin"),
                MorphologyMeasurement(feature_name="internal_gas_bubbles", value=False),
                MorphologyMeasurement(feature_name="molding_seams_present", value=False),
            ]
        elif "bone" in cat_lower:
            measurements = [
                MorphologyMeasurement(feature_name="haversian_canals_present", value=True),
                MorphologyMeasurement(feature_name="schreger_pattern_present", value=False),
            ]
        else:
            measurements = [
                MorphologyMeasurement(feature_name="unidentified_morphology_metric", value=1.0),
            ]

        # 3. Build Manifest & Inspection objects
        manifest = ShippingManifest(
            manifest_id=f"MAN-{cid}",
            waybill_number=f"WB-{cid}",
            shipper="Mobile Field Cargo Unit",
            consignee="Customs Detention Hold",
            declared_item_name=declared_item,
            declared_scientific_name=declared_scientific,
            declared_quantity=100.0,
            declared_unit="kg",
            country_of_origin=resolved_origin,
            destination_country="US",
        )

        inspection = PhysicalInspection(
            inspection_id=f"INSP-{cid}",
            inspector_id="FIELD-OFFICER-MOBILE",
            checkpoint_location=checkpoint_location,
            observed_specimen_category=resolved_category,
            measurements=measurements,
            photos=[str(photo_path)],
        )

        # 4. Execute forensic verification pipeline
        harness = get_forensic_harness(model_name=model)
        res = run_forensic_pipeline(manifest, inspection, case_id=cid, output_dir=case_dir, harness=harness)

        return {
            "case_id": cid,
            "discrepancy_score": res["discrepancy_score"],
            "suspected_species": res["suspected_species"],
            "cites_appendix": res["cites_appendix"],
            "flagged_indicators": res["flagged_indicators"],
            "smuggling_mos": res["smuggling_mos"],
            "forensic_output": res["forensic_output"].model_dump(),
            "alert_dispatched": res["alert_dispatched"],
            "is_novel_escalation": res["is_novel_escalation"],
            "photo_archived_path": str(photo_path),
            "pdf_url": f"/api/dossier/{cid}/pdf",
            "markdown_url": f"/api/dossier/{cid}/markdown",
            "json_url": f"/api/dossier/{cid}/json",
            "sha256_hash": res["dossier_package"]["sha256_hash"],
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


@app.get("/api/cases")
def list_archived_cases() -> List[Dict[str, Any]]:
    """Lists all archived cases and dossiers stored in the desktop output directory."""
    cases = []
    if OUTPUT_DIR.exists():
        for case_dir in sorted(OUTPUT_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
            if case_dir.is_dir():
                cid = case_dir.name
                json_file = case_dir / f"{cid}_dossier.json"
                meta: Dict[str, Any] = {
                    "case_id": cid,
                    "timestamp": case_dir.stat().st_mtime,
                    "has_pdf": (case_dir / f"{cid}_dossier.pdf").exists(),
                    "has_json": json_file.exists(),
                    "has_photo": any(case_dir.glob("inspection_*")),
                }
                if json_file.exists():
                    try:
                        with open(json_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            meta["suspected_species"] = data.get("forensic_output", {}).get("suspected_actual_species", "Unknown")
                            meta["discrepancy_score"] = data.get("forensic_output", {}).get("discrepancy_score", 0.0)
                            meta["cites_appendix"] = data.get("forensic_output", {}).get("cites_appendix", "None")
                            meta["declared_item"] = data.get("manifest", {}).get("declared_item_name", cid)
                    except Exception:
                        pass
                cases.append(meta)
    return cases


@app.get("/", response_class=HTMLResponse)
def dashboard_html() -> str:
    """Returns the single-page responsive customs inspection dashboard."""
    html_file = STATIC_DIR / "index.html"
    if html_file.exists():
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>CanopyTrace Dashboard</h1><p>Static index.html not found.</p>"
