"""
Automated Forensic Benchmark Suite for CanopyTrace.
Executes the 6 core realistic smuggling & compliance scenarios + 1 novel anomaly escalation case.
"""

import pytest
from pathlib import Path
from canopytrace.core.pipeline import run_forensic_pipeline
from canopytrace.schemas import ShippingManifest, PhysicalInspection, MorphologyMeasurement


def test_bm01_elephant_ivory_mammoth_camouflage(tmp_path):
    """
    BM-01: Elephant Ivory declared as Antique Mammoth Carvings.
    Physical examination shows outer Schreger angles of 124 degrees (> 115 deg),
    identifying modern elephant ivory (CITES Appendix I).
    Expected: Severe discrepancy (>= 0.85), alert dispatched, MO-IVO-001 detected.
    """
    manifest = ShippingManifest(
        manifest_id="BM-01",
        waybill_number="WB-BM01-789",
        shipper="Siberian Artifacts Trading",
        consignee="Global Curio Importers",
        declared_item_name="Antique Mammoth Carvings",
        declared_scientific_name="Mammuthus primigenius",
        declared_quantity=450.0,
        declared_unit="kg",
        country_of_origin="RU",
        destination_country="HK",
    )
    inspection = PhysicalInspection(
        inspection_id="INSP-BM-01",
        inspector_id="CUSTOMS-OFFICER-44",
        checkpoint_location="Hong Kong Maritime Berth 3",
        observed_specimen_category="ivory",
        measurements=[
            MorphologyMeasurement(feature_name="schreger_angle_outer", value=124.0, unit="degrees"),
            MorphologyMeasurement(feature_name="haversian_canals_present", value=False),
            MorphologyMeasurement(feature_name="molding_seams_present", value=False),
        ]
    )

    res = run_forensic_pipeline(manifest, inspection, case_id="CASE-BM01", output_dir=tmp_path)

    assert res["discrepancy_score"] >= 0.85
    assert "Loxodonta africana" in res["suspected_species"] or "Elephant" in res["suspected_species"]
    assert res["cites_appendix"] == "I"
    assert "MO-IVO-001" in res["smuggling_mos"]
    assert res["alert_dispatched"] is True
    assert Path(res["dossier_package"]["pdf_path"]).exists()


def test_bm02_pangolin_scales_keratin_disguise(tmp_path):
    """
    BM-02: Pangolin scales declared as Dried Bovine Horn / Keratin Flakes from Nigeria.
    Physical traits show 3 dorsal keels and imbricated scale armor (Manis tricuspis, CITES App I).
    Expected: Severe discrepancy (>= 0.90), alert dispatched, MO-PAN-001 detected.
    """
    manifest = ShippingManifest(
        manifest_id="BM-02",
        waybill_number="WB-BM02-456",
        shipper="West Africa Agro Byproducts Ltd",
        consignee="Far East Fertilizer Importers",
        declared_item_name="Dried Bovine Horn / Keratin Flakes",
        declared_scientific_name="Bos taurus",
        declared_quantity=2400.0,
        declared_unit="kg",
        country_of_origin="NG",
        destination_country="VN",
    )
    inspection = PhysicalInspection(
        inspection_id="INSP-BM-02",
        inspector_id="CUSTOMS-OFFICER-12",
        checkpoint_location="Lagos Container Terminal",
        observed_specimen_category="keratin_scales",
        measurements=[
            MorphologyMeasurement(feature_name="dorsal_keel_count", value=3),
            MorphologyMeasurement(feature_name="imbrication_pattern", value="overlapping_shingle"),
        ]
    )

    res = run_forensic_pipeline(manifest, inspection, case_id="CASE-BM02", output_dir=tmp_path)

    assert res["discrepancy_score"] >= 0.90
    assert "Manis tricuspis" in res["suspected_species"]
    assert res["cites_appendix"] == "I"
    assert "MO-PAN-001" in res["smuggling_mos"]
    assert res["alert_dispatched"] is True


def test_bm03_rosewood_timber_teak_misdeclaration(tmp_path):
    """
    BM-03: Protected Rosewood (Dalbergia) declared as Plantation Teak.
    Wood anatomy shows diffuse-porous vessels, storied rays (ripple marks), and negative UV fluorescence.
    Expected: Discrepancy >= 0.80, CITES Appendix II/I, MO-TIM-001 detected.
    """
    manifest = ShippingManifest(
        manifest_id="BM-03",
        waybill_number="WB-BM03-123",
        shipper="Mekong Wood Exporters",
        consignee="Oriental Furniture Manufacturers",
        declared_item_name="Plantation Teak Logs (Tectona grandis)",
        declared_scientific_name="Tectona grandis",
        declared_quantity=35.0,
        declared_unit="m3",
        country_of_origin="LA",
        destination_country="CN",
    )
    inspection = PhysicalInspection(
        inspection_id="INSP-BM-03",
        inspector_id="CUSTOMS-OFFICER-89",
        checkpoint_location="Hai Phong Port Container Yard",
        observed_specimen_category="timber",
        measurements=[
            MorphologyMeasurement(feature_name="vessel_porosity", value="diffuse_porous"),
            MorphologyMeasurement(feature_name="storied_rays_ripple_marks", value=True),
            MorphologyMeasurement(feature_name="uv_water_fluorescence", value="negative"),
        ]
    )

    res = run_forensic_pipeline(manifest, inspection, case_id="CASE-BM03", output_dir=tmp_path)

    assert res["discrepancy_score"] >= 0.80
    assert "Dalbergia" in res["suspected_species"]
    assert res["cites_appendix"] in ("I", "II")
    assert "MO-TIM-001" in res["smuggling_mos"]


def test_bm04_hawksbill_turtle_bekko_synthetic_resin(tmp_path):
    """
    BM-04: Hawksbill Sea Turtle Bekko declared as Decorative Synthetic Celluloid Resin.
    Physical analysis shows imbricate organic keratin scutes without gas bubbles or mold seams.
    Expected: Severe discrepancy (>= 0.85), CITES Appendix I, MO-REP-001 detected.
    """
    manifest = ShippingManifest(
        manifest_id="BM-04",
        waybill_number="WB-BM04-987",
        shipper="Coastal Crafts Inc",
        consignee="Luxury Jewelry Artisans",
        declared_item_name="Decorative Synthetic Celluloid Resin Crafts",
        declared_quantity=150.0,
        declared_unit="pieces",
        country_of_origin="ID",
        destination_country="JP",
    )
    inspection = PhysicalInspection(
        inspection_id="INSP-BM-04",
        inspector_id="CUSTOMS-OFFICER-56",
        checkpoint_location="Jakarta Tanjung Priok Port",
        observed_specimen_category="marine_reptile",
        measurements=[
            MorphologyMeasurement(feature_name="scute_layering", value="imbricate_keratin"),
            MorphologyMeasurement(feature_name="internal_gas_bubbles", value=False),
            MorphologyMeasurement(feature_name="molding_seams_present", value=False),
        ]
    )

    res = run_forensic_pipeline(manifest, inspection, case_id="CASE-BM04", output_dir=tmp_path)

    assert res["discrepancy_score"] >= 0.85
    assert "Eretmochelys imbricata" in res["suspected_species"]
    assert res["cites_appendix"] == "I"
    assert "MO-REP-001" in res["smuggling_mos"]
    assert res["alert_dispatched"] is True


def test_bm05_legitimate_bovine_bone_negative_control(tmp_path):
    """
    BM-05: Legitimate Bovine Bone Carvings (Negative Control Baseline).
    Physical analysis confirms Haversian osteon vascular canals and absence of Schreger patterns.
    Expected: Low discrepancy (<= 0.15), CITES Appendix None, cleared for routine release.
    """
    manifest = ShippingManifest(
        manifest_id="BM-05",
        waybill_number="WB-BM05-321",
        shipper="Artisan Bone Novelties Export",
        consignee="Western Craft Store",
        declared_item_name="Handcrafted Bovine Bone Carvings",
        declared_scientific_name="Bos taurus",
        declared_quantity=60.0,
        declared_unit="kg",
        country_of_origin="IN",
        destination_country="US",
    )
    inspection = PhysicalInspection(
        inspection_id="INSP-BM-05",
        inspector_id="CUSTOMS-OFFICER-21",
        checkpoint_location="Mumbai Nhava Sheva Port",
        observed_specimen_category="bone",
        measurements=[
            MorphologyMeasurement(feature_name="haversian_canals_present", value=True),
            MorphologyMeasurement(feature_name="schreger_pattern_present", value=False),
        ]
    )

    res = run_forensic_pipeline(manifest, inspection, case_id="CASE-BM05", output_dir=tmp_path)

    assert res["discrepancy_score"] <= 0.15
    assert "Bos taurus" in res["suspected_species"]
    assert res["cites_appendix"] == "None"
    assert res["alert_dispatched"] is False


def test_bm06_fraudulent_permit_impossible_origin(tmp_path):
    """
    BM-06: Fraudulent CITES Export Permit with impossible geographic origin.
    Declared origin country is not in native range states for the Appendix I species.
    Expected: Discrepancy >= 0.75, flagged indicators include range state red flag.
    """
    manifest = ShippingManifest(
        manifest_id="BM-06",
        waybill_number="WB-BM06-654",
        shipper="Transit Logistics",
        consignee="Foreign Collectors Ltd",
        declared_item_name="African Elephant Carvings",
        declared_scientific_name="Loxodonta africana",
        declared_quantity=80.0,
        declared_unit="kg",
        country_of_origin="NO",  # Norway is not an African elephant range state
        transit_countries=["AE"],
        destination_country="CN",
        permit_numbers=["CITES-EXP-FAKE-999"],
    )
    inspection = PhysicalInspection(
        inspection_id="INSP-BM-06",
        inspector_id="CUSTOMS-OFFICER-33",
        checkpoint_location="Dubai Jebel Ali Port",
        observed_specimen_category="ivory",
        measurements=[
            MorphologyMeasurement(feature_name="schreger_angle_outer", value=125.0, unit="degrees"),
        ]
    )

    res = run_forensic_pipeline(manifest, inspection, case_id="CASE-BM06", output_dir=tmp_path)

    assert res["discrepancy_score"] >= 0.75
    assert any("native IUCN range states" in ind for ind in res["flagged_indicators"])


def test_bm07_novel_unknown_anomaly_escalation(tmp_path):
    """
    BM-07: Rare unidentified specimen fragment exhibiting unknown anatomy.
    Expected: Flagged as UNRESOLVED_NOVEL_ANOMALY and enqueued for Higher Scientific Authority escalation.
    """
    manifest = ShippingManifest(
        manifest_id="BM-07",
        waybill_number="WB-BM07-111",
        shipper="Exotic Expeditions",
        consignee="Private Research Cabinet",
        declared_item_name="Unidentified Biological Sample",
        declared_quantity=10.0,
        declared_unit="kg",
        country_of_origin="BR",
        destination_country="FR",
    )
    inspection = PhysicalInspection(
        inspection_id="INSP-BM-07",
        inspector_id="CUSTOMS-OFFICER-77",
        checkpoint_location="Le Havre Port",
        observed_specimen_category="unknown",
        measurements=[
            MorphologyMeasurement(feature_name="unidentified_crystallinity", value=42.1),
        ]
    )

    res = run_forensic_pipeline(manifest, inspection, case_id="CASE-BM07", output_dir=tmp_path)

    assert res["suspected_species"] == "UNRESOLVED_NOVEL_ANOMALY"
    assert res["is_novel_escalation"] is True
