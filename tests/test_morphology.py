"""Unit tests for morphology fingerprinting skill."""

import pytest
from canopytrace.schemas import PhysicalInspection, MorphologyMeasurement
from skills.morphology_fingerprint.fingerprint import match_morphology_fingerprint


def test_elephant_schreger_angle_gt_115():
    inspection = PhysicalInspection(
        inspection_id="INSP-01",
        inspector_id="AGENT-1",
        checkpoint_location="Port of Mombasa",
        observed_specimen_category="ivory",
        measurements=[
            MorphologyMeasurement(feature_name="schreger_angle_outer", value=126.0, unit="degrees"),
            MorphologyMeasurement(feature_name="haversian_canals_present", value=False),
            MorphologyMeasurement(feature_name="molding_seams_present", value=False),
        ]
    )
    res = match_morphology_fingerprint(inspection)
    assert res["primary_key_matched"] == "KEY-IVO-ELEPHANT"
    assert "Loxodonta africana" in res["suspected_taxa"]
    assert res["diagnostic_confidence"] >= 0.90


def test_mammoth_schreger_angle_lt_90():
    inspection = PhysicalInspection(
        inspection_id="INSP-02",
        inspector_id="AGENT-1",
        checkpoint_location="Rotterdam Port",
        observed_specimen_category="ivory",
        measurements=[
            MorphologyMeasurement(feature_name="schreger_angle_outer", value=78.0, unit="degrees"),
            MorphologyMeasurement(feature_name="haversian_canals_present", value=False),
        ]
    )
    res = match_morphology_fingerprint(inspection)
    assert res["primary_key_matched"] == "KEY-IVO-MAMMOTH"
    assert "Mammuthus primigenius" in res["suspected_taxa"]


def test_bovine_bone_haversian_canals():
    inspection = PhysicalInspection(
        inspection_id="INSP-03",
        inspector_id="AGENT-2",
        checkpoint_location="Singapore Customs",
        observed_specimen_category="bone",
        measurements=[
            MorphologyMeasurement(feature_name="haversian_canals_present", value=True),
            MorphologyMeasurement(feature_name="schreger_pattern_present", value=False),
        ]
    )
    res = match_morphology_fingerprint(inspection)
    assert res["primary_key_matched"] == "KEY-BON-BOVINE"
    assert "Bos taurus" in res["suspected_taxa"]


def test_rosewood_diffuse_porosity_and_storied_rays():
    inspection = PhysicalInspection(
        inspection_id="INSP-04",
        inspector_id="AGENT-3",
        checkpoint_location="Hai Phong Port",
        observed_specimen_category="timber",
        measurements=[
            MorphologyMeasurement(feature_name="vessel_porosity", value="diffuse_porous"),
            MorphologyMeasurement(feature_name="storied_rays_ripple_marks", value=True),
            MorphologyMeasurement(feature_name="uv_water_fluorescence", value="negative"),
        ]
    )
    res = match_morphology_fingerprint(inspection)
    assert res["primary_key_matched"] == "KEY-TIM-DALBERGIA"
    assert any("Dalbergia" in t for t in res["suspected_taxa"])


def test_pangolin_scale_keels():
    inspection = PhysicalInspection(
        inspection_id="INSP-05",
        inspector_id="AGENT-4",
        checkpoint_location="Lagos Port",
        observed_specimen_category="keratin_scales",
        measurements=[
            MorphologyMeasurement(feature_name="dorsal_keel_count", value=3),
            MorphologyMeasurement(feature_name="imbrication_pattern", value="overlapping_shingle"),
        ]
    )
    res = match_morphology_fingerprint(inspection)
    assert res["primary_key_matched"] == "KEY-PAN-TRICUSPIS"
    assert "Manis tricuspis" in res["suspected_taxa"]
