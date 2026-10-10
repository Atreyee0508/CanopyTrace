"""Unit tests for smuggling modus operandi matching engine."""

import pytest
from canopytrace.core.pattern_matcher import match_smuggling_patterns
from canopytrace.schemas import ShippingManifest, PhysicalInspection, MorphologyMeasurement


def test_mammoth_ivory_camouflage_mo():
    manifest = ShippingManifest(
        manifest_id="TEST-MO-01",
        waybill_number="WB-001",
        shipper="Export Co",
        consignee="Import Co",
        declared_item_name="Antique Mammoth Carvings",
        declared_quantity=150.0,
        declared_unit="kg",
        country_of_origin="RU",
        destination_country="HK",
    )
    inspection = PhysicalInspection(
        inspection_id="INSP-MO-01",
        inspector_id="AGENT-1",
        checkpoint_location="Hong Kong Berth 3",
        observed_specimen_category="ivory",
        measurements=[
            MorphologyMeasurement(feature_name="schreger_angle_outer", value=122.0, unit="degrees"),
            MorphologyMeasurement(feature_name="haversian_canals_present", value=False),
        ]
    )
    res = match_smuggling_patterns(manifest, inspection)
    assert res["matched_count"] >= 1
    assert "MO-IVO-001" in res["matched_ids"]
    assert res["max_risk_weight"] >= 0.90


def test_pangolin_keratin_concealment_mo():
    manifest = ShippingManifest(
        manifest_id="TEST-MO-02",
        waybill_number="WB-002",
        shipper="Agro Co",
        consignee="Fertilizer Corp",
        declared_item_name="Dried Bovine Horn / Keratin Flakes",
        declared_quantity=5000.0,
        declared_unit="kg",
        country_of_origin="NG",
        destination_country="VN",
    )
    inspection = PhysicalInspection(
        inspection_id="INSP-MO-02",
        inspector_id="AGENT-2",
        checkpoint_location="Lagos Port",
        observed_specimen_category="keratin_scales",
        measurements=[
            MorphologyMeasurement(feature_name="dorsal_keel_count", value=3),
            MorphologyMeasurement(feature_name="imbrication_pattern", value="overlapping_shingle"),
        ]
    )
    res = match_smuggling_patterns(manifest, inspection)
    assert "MO-PAN-001" in res["matched_ids"]
    assert res["max_risk_weight"] >= 0.95


def test_teak_rosewood_misdeclaration_mo():
    manifest = ShippingManifest(
        manifest_id="TEST-MO-03",
        waybill_number="WB-003",
        shipper="Timber Co",
        consignee="Flooring Co",
        declared_item_name="Plantation Teak Logs (Tectona grandis)",
        declared_quantity=20.0,
        declared_unit="m3",
        country_of_origin="LA",
        destination_country="CN",
    )
    inspection = PhysicalInspection(
        inspection_id="INSP-MO-03",
        inspector_id="AGENT-3",
        checkpoint_location="Hai Phong",
        observed_specimen_category="timber",
        measurements=[
            MorphologyMeasurement(feature_name="vessel_porosity", value="diffuse_porous"),
            MorphologyMeasurement(feature_name="storied_rays_ripple_marks", value=True),
        ]
    )
    res = match_smuggling_patterns(manifest, inspection)
    assert "MO-TIM-001" in res["matched_ids"]
