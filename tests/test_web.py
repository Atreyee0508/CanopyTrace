"""Integration tests for CanopyTrace FastAPI Web UI and REST API."""

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
