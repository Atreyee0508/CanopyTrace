"""Pydantic schemas for on-site physical inspection observations and forensic measurements."""

from datetime import datetime, timezone
from typing import Any, List, Optional, Union
from pydantic import BaseModel, Field


class MorphologyMeasurement(BaseModel):
    """A discrete physical or micro-structural measurement taken on-site."""
    feature_name: str = Field(
        description="Name of the observed morphological feature (e.g. 'schreger_angle_outer', 'vessel_porosity', 'dorsal_keel_count')"
    )
    value: Union[float, int, str, bool] = Field(description="Recorded observation or measurement value")
    unit: Optional[str] = Field(default=None, description="Measurement unit (e.g. degrees, count, mm)")
    instrument: Optional[str] = Field(
        default=None,
        description="Tool used (e.g. 'optical_caliper', 'polarizing_microscope', 'uv_lamp_365nm')"
    )
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Inspector measurement confidence")


class PhysicalInspection(BaseModel):
    """Represents a border customs physical inspection report."""
    inspection_id: str = Field(description="Unique inspection log identifier")
    inspector_id: str = Field(description="Customs officer badge or inspector ID")
    checkpoint_location: str = Field(description="Port of entry or checkpoint code (e.g. 'Port of Mombasa', 'Rotterdam')")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Physical examination timestamp")
    observed_specimen_category: str = Field(
        description="General classification: ivory, timber, keratin_scales, bone, marine_reptile, felid, etc."
    )
    measurements: List[MorphologyMeasurement] = Field(default_factory=list, description="Quantitative or qualitative measurement entries")
    visual_characteristics: List[str] = Field(
        default_factory=list,
        description="Qualitative field observations (e.g. 'curved tusk cross section with visible intersecting lines')"
    )
    photos: List[str] = Field(default_factory=list, description="Paths, URLs, or SHA-256 hashes of inspection macro-photos")
    notes: Optional[str] = Field(default=None, description="Freeform inspector field notes")
