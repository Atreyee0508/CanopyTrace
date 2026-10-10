"""Pydantic schema for automated local authority incident alerts."""

from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field


class AuthorityAlertPayload(BaseModel):
    """Urgent incident alert payload dispatched when discrepancy_score >= threshold."""
    alert_id: str = Field(description="Unique alert identifier (e.g. ALT-2026-001)")
    case_id: str = Field(description="Associated forensic case ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Alert generation timestamp")
    port_location: str = Field(description="Customs port or checkpoint where cargo was intercepted")
    waybill_number: str = Field(description="Waybill or container ID")
    severity: str = Field(default="CRITICAL", description="Incident severity: CRITICAL, HIGH, WARNING")
    discrepancy_score: float = Field(ge=0.0, le=1.0, description="Calculated forensic discrepancy score")
    declared_item: str = Field(description="Declared commercial description on manifest")
    suspected_taxa: str = Field(description="Suspected actual contraband species")
    cites_appendix: str = Field(description="Violated CITES Appendix: I, II, or III")
    matched_smuggling_mos: List[str] = Field(default_factory=list, description="Associated smuggling patterns")
    recommended_immediate_action: str = Field(
        default="DETAIN_CARGO_AND_COLLECT_PHYSICAL_SAMPLE",
        description="Immediate enforcement action recommended for customs officers"
    )
    cryptographic_sha256: str = Field(description="Cryptographic hash of the case payload for evidentiary chain")
