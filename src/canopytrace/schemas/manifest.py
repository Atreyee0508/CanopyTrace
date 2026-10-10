"""Pydantic schemas for shipping manifests and customs paperwork declarations."""

from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field


class ShippingManifest(BaseModel):
    """Represents an ingested customs shipping declaration or cargo manifest."""
    manifest_id: str = Field(description="Unique shipping manifest identifier (e.g. MAN-2026-001)")
    waybill_number: str = Field(description="Air waybill or maritime bill of lading number")
    shipper: str = Field(description="Exporter or shipping entity name")
    consignee: str = Field(description="Importer or receiving entity name")
    declared_item_name: str = Field(description="Declared commercial description (e.g. 'Antique Mammoth Carvings')")
    declared_scientific_name: Optional[str] = Field(default=None, description="Declared scientific binomial if stated")
    hs_code: Optional[str] = Field(default=None, description="Harmonized System tariff code")
    declared_quantity: float = Field(gt=0.0, description="Quantity declared on paperwork")
    declared_unit: str = Field(default="kg", description="Unit of measurement (e.g. kg, pieces, logs)")
    country_of_origin: str = Field(description="Declared country of origin (ISO-2 code or name)")
    transit_countries: List[str] = Field(default_factory=list, description="List of transit ports or countries")
    destination_country: str = Field(description="Final destination country")
    permit_numbers: List[str] = Field(default_factory=list, description="Claimed CITES or national export permit numbers")
    declared_commercial_form: str = Field(
        default="raw",
        description="Declared physical state: raw, carved, sawn_timber, flakes, byproduct, etc."
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Filing timestamp")
