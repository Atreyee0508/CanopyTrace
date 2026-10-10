"""Integration tests for CanopyTrace FastAPI Web UI and REST API."""

from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from canopytrace.web.app import app

client = TestClient(app)


def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_patterns():
    response = client.get("/api/patterns")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(p["id"] == "MO-IVO-001" for p in data)


def test_api_dashboard_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "CANOPYTRACE" in response.text
    assert "Schreger Caliper" in response.text


def test_api_inspect_endpoint():
    payload = {
        "case_id": "CASE-API-TEST",
        "manifest": {
            "manifest_id": "MAN-API-01",
            "waybill_number": "WB-API-99",
            "shipper": "Global Traders",
            "consignee": "Artisan Imports",
            "declared_item_name": "Antique Mammoth Carvings",
            "declared_quantity": 200.0,
            "declared_unit": "kg",
            "country_of_origin": "RU",
            "destination_country": "CN",
        },
        "inspection": {
            "inspection_id": "INSP-API-01",
            "inspector_id": "AGENT-42",
            "checkpoint_location": "Port of Shanghai",
            "observed_specimen_category": "ivory",
            "measurements": [
                {"feature_name": "schreger_angle_outer", "value": 125.0, "unit": "degrees"}
            ],
        }
    }

    response = client.post("/api/inspect", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "CASE-API-TEST"
    assert data["discrepancy_score"] >= 0.85
    assert data["alert_dispatched"] is True
    assert "dossier_package" in data


def test_api_server_info():
    response = client.get("/api/server-info")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "local_ip" in data
    assert "port" in data


def test_api_mobile_inspect_multipart(tmp_path):
    import io
    from PIL import Image

    # Create real valid JPEG image bytes
    buf = io.BytesIO()
    img = Image.new("RGB", (100, 100), color=(180, 50, 50))
    img.save(buf, format="JPEG")
    jpeg_bytes = buf.getvalue()

    files = {"photo": ("test_photo.jpg", jpeg_bytes, "image/jpeg")}
    data = {
        "category": "ivory",
        "declared_item": "Antique Mammoth Carvings",
        "origin_country": "NG",
        "checkpoint_location": "Mobile Port Berth 4",
        "caliper_angle": "125.0",
        "case_id": "CASE-TEST-MOB-01",
    }
    response = client.post("/api/mobile/inspect", files=files, data=data)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["case_id"] == "CASE-TEST-MOB-01"
    assert res_data["discrepancy_score"] >= 0.85
    assert res_data["alert_dispatched"] is True
    assert "pdf_url" in res_data
    assert "sha256_hash" in res_data
    assert Path(res_data["photo_archived_path"]).exists()
