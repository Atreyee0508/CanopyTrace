"""Unit tests for CITES registry check skill."""

import pytest
from canopytrace.schemas import ShippingManifest
from skills.cites_registry_check.check_registry import audit_manifest_registry


def test_elephant_cites_appendix_i():
    manifest = ShippingManifest(
        manifest_id="TEST-CITES-01",
        waybill_number="WB-001",
        shipper="Exporter Ltd",
        consignee="Importer Ltd",
        declared_item_name="African Elephant Tusk Souvenirs",
        declared_scientific_name="Loxodonta africana",
        declared_quantity=50.0,
        declared_unit="kg",
        country_of_origin="KE",
        destination_country="CN",
    )
    res = audit_manifest_registry(manifest)
    assert res["resolved_taxon"] == "Loxodonta africana"
    assert res["cites_appendix"] == "I"
    assert res["commercial_status"] == "BANNED"
    assert res["is_native_range"] is True
    assert res["is_flagged"] is True


def test_impossible_geographic_origin():
    # Declaring African elephant tusk from Norway (NO)
    manifest = ShippingManifest(
        manifest_id="TEST-CITES-02",
        waybill_number="WB-002",
        shipper="Nordic Freight",
        consignee="Asian Imports",
        declared_item_name="African Elephant Raw Ivory",
        declared_scientific_name="Loxodonta africana",
        declared_quantity=100.0,
        declared_unit="kg",
        country_of_origin="NO",  # Norway is not in IUCN African elephant range
        destination_country="VN",
    )
    res = audit_manifest_registry(manifest)
    assert res["is_native_range"] is False
    assert any("native IUCN range states" in rf for rf in res["red_flags"])


def test_mammoth_camouflage_detection():
    manifest = ShippingManifest(
        manifest_id="TEST-CITES-03",
        waybill_number="WB-003",
        shipper="Siberia Crafts",
        consignee="Hong Kong Antiques",
        declared_item_name="Antique Mammoth Carvings",
        declared_quantity=200.0,
        declared_unit="kg",
        country_of_origin="RU",
        destination_country="HK",
    )
    res = audit_manifest_registry(manifest)
    assert res["resolved_taxon"] == "Mammuthus primigenius"
    assert res["is_flagged"] is True
    assert res["target_appendix"] == "I"
