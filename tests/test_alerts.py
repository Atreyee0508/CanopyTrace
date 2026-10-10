"""Unit tests for automated local authority alerting."""

import pytest
from pathlib import Path
from canopytrace.alerts.dispatcher import dispatch_authority_alert, SEIZURE_THRESHOLD
from canopytrace.schemas import (
    ShippingManifest,
    PhysicalInspection,
    ForensicTriageOutput,
    UncertaintyBounds,
    LabAction,
)


def test_alert_triggered_above_threshold(tmp_path):
    manifest = ShippingManifest(
        manifest_id="ALT-TEST-01",
        waybill_number="WB-999",
        shipper="Suspect Co",
        consignee="Receiving Co",
        declared_item_name="Antique Mammoth Carvings",
        declared_quantity=100.0,
        declared_unit="kg",
        country_of_origin="NG",
        destination_country="CN",
    )
    inspection = PhysicalInspection(
        inspection_id="INSP-ALT-01",
        inspector_id="OFFICER-9",
        checkpoint_location="Port of Mombasa",
        observed_specimen_category="ivory",
    )
    forensic = ForensicTriageOutput(
        discrepancy_score=0.92,  # >= 0.70 threshold
        flagged_indicators=["Schreger angle exceeds 115 deg."],
        suspected_actual_species="Loxodonta africana",
        cites_appendix="I",
        smuggling_mo_detected=["MO-IVO-001"],
        uncertainty_bounds=UncertaintyBounds(lower_bound=0.88, upper_bound=0.96, confidence_interval="95%"),
        suggested_lab_action=[LabAction(test_type="c14", priority="mandatory", expected_discriminator="bomb pulse")],
        forensic_rationale="Contraband detected.",
    )

    alert = dispatch_authority_alert(
        case_id="CASE-ALT-01",
        manifest=manifest,
        inspection=inspection,
        forensic=forensic,
        sha256_hash="abcdef1234567890",
        alert_dir=tmp_path,
    )

    assert alert is not None
    assert alert.severity == "CRITICAL"
    assert alert.discrepancy_score == 0.92
    assert alert.cites_appendix == "I"
    assert (tmp_path / "alert_CASE-ALT-01.json").exists()


def test_no_alert_below_threshold(tmp_path):
    manifest = ShippingManifest(
        manifest_id="ALT-TEST-02",
        waybill_number="WB-888",
        shipper="Clean Co",
        consignee="Craft Store",
        declared_item_name="Bovine Bone Carvings",
        declared_quantity=50.0,
        declared_unit="kg",
        country_of_origin="IN",
        destination_country="US",
    )
    inspection = PhysicalInspection(
        inspection_id="INSP-ALT-02",
        inspector_id="OFFICER-9",
        checkpoint_location="Singapore Port",
        observed_specimen_category="bone",
    )
    forensic = ForensicTriageOutput(
        discrepancy_score=0.10,  # Below 0.70
        flagged_indicators=[],
        suspected_actual_species="Bos taurus",
        cites_appendix="None",
        smuggling_mo_detected=[],
        uncertainty_bounds=UncertaintyBounds(lower_bound=0.05, upper_bound=0.15, confidence_interval="95%"),
        suggested_lab_action=[],
        forensic_rationale="Routine clearance.",
    )

    alert = dispatch_authority_alert(
        case_id="CASE-ALT-02",
        manifest=manifest,
        inspection=inspection,
        forensic=forensic,
        sha256_hash="123456abcdef",
        alert_dir=tmp_path,
    )

    assert alert is None
    assert not (tmp_path / "alert_CASE-ALT-02.json").exists()
