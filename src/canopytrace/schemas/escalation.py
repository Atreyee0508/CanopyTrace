"""Pydantic schema for novel anomaly escalation cases and authority review."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EscalationCase(BaseModel):
    """Represents a specimen exhibiting unknown, contradictory, or novel morphology."""
    case_id: str = Field(description="Unique case ID")
    escalation_id: str = Field(description="Escalation tracking number (e.g. ESC-2026-001)")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    checkpoint_location: str = Field(description="Port or checkpoint where specimen was intercepted")
    manifest_summary: Dict[str, Any] = Field(description="Summary of declared cargo details")
    observed_measurements: List[Dict[str, Any]] = Field(description="Unresolved physical morphology measurements")
    reason_for_escalation: str = Field(
        description="Detailed explanation of why existing forensic keys could not definitively classify the specimen"
    )
    status: str = Field(
        default="PENDING_AUTHORITY_REVIEW",
        description="Status: PENDING_AUTHORITY_REVIEW, APPROVED, REJECTED"
    )
    authority_review_notes: Optional[str] = Field(default=None, description="Higher scientific authority feedback")
    verified_species: Optional[str] = Field(default=None, description="Species verified by scientific authority")
    verified_appendix: Optional[str] = Field(default=None, description="Assigned CITES appendix (I, II, III, or None)")
    updated_database: bool = Field(default=False, description="Flag indicating if finding was ingested into offline DB")
