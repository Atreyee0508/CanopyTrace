"""Unit tests for novel anomaly escalation and continuous learning loop."""

import pytest
from canopytrace.db import query_cites_by_name
from canopytrace.escalation.queue import enqueue_escalation, list_pending_escalations
from canopytrace.escalation.approval import approve_and_ingest_novel_finding
from canopytrace.schemas import ShippingManifest, PhysicalInspection, MorphologyMeasurement


def test_escalation_lifecycle_and_db_ingestion(tmp_path):
    db_file = tmp_path / "test_ref.db"
    from canopytrace.db.database import init_db
    init_db(db_file)

    manifest = ShippingManifest(
        manifest_id="ESC-TEST-01",
        waybill_number="WB-777",
        shipper="Amazonia Exporters",
        consignee="Botanic Importers",
        declared_item_name="Unidentified Sawn Timber",
        declared_quantity=30.0,
        declared_unit="m3",
        country_of_origin="BR",
        destination_country="EU",
    )
    inspection = PhysicalInspection(
        inspection_id="INSP-ESC-01",
        inspector_id="AGENT-7",
        checkpoint_location="Santos Port",
        observed_specimen_category="timber",
        measurements=[
            MorphologyMeasurement(feature_name="novel_fibrovascular_ratio", value=88.5),
        ]
    )

    # 1. Enqueue novel anomaly
    esc_case = enqueue_escalation(
        case_id="CASE-ESC-01",
        manifest=manifest,
        inspection=inspection,
        reason="Unknown timber anatomy outside standard reference keys.",
        escalation_dir=tmp_path,
        db_path=db_file,
    )
    assert esc_case.status == "PENDING_AUTHORITY_REVIEW"
    assert (tmp_path / "CASE-ESC-01.json").exists()

    # Verify present in pending list
    pending = list_pending_escalations(db_path=db_file)
    assert any(p["case_id"] == "CASE-ESC-01" for p in pending)

    # Verify taxon is NOT yet in database
    prior = query_cites_by_name("Cedrela fissilis", db_path=db_file)
    assert prior is None

    # 2. Authority Approves and Ingests Novel Taxon
    success = approve_and_ingest_novel_finding(
        case_id="CASE-ESC-01",
        verified_species="Cedrela fissilis",
        verified_appendix="II",
        authority_notes="Verified by CITES Scientific Authority as Brazilian Cedar.",
        common_names=["Brazilian Cedar", "Cedro"],
        commercial_status="QUOTA_CONTROLLED",
        range_countries=["BR", "AR", "BO"],
        escalation_dir=tmp_path,
        db_path=db_file,
    )
    assert success is True

    # 3. Verify future queries now immediately recognize the new taxon!
    updated = query_cites_by_name("Cedrela fissilis", db_path=db_file)
    assert updated is not None
    assert updated["scientific_name"] == "Cedrela fissilis"
    assert updated["appendix"] == "II"
    assert updated["commercial_status"] == "QUOTA_CONTROLLED"
