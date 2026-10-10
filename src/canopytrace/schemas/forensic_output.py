"""Strict Pydantic schema for schema-constrained Gemma 2 forensic triage outputs."""

from typing import List
from pydantic import BaseModel, Field

MANDATORY_LEGAL_DISCLAIMER: str = (
    "AI findings provide investigative triage and do not constitute certified legal testimony. "
    "Formal seizure and prosecution require confirmatory forensic laboratory analysis."
)


class LabAction(BaseModel):
    """Recommended laboratory assay required for courtroom-admissible evidence."""
    test_type: str = Field(
        description="Assay type (e.g. 'radiocarbon_dating_c14', 'dna_barcoding_cytochrome_b', 'ftir_spectroscopy', 'wood_anatomy_thin_section')"
    )
    priority: str = Field(
        description="Urgency: 'mandatory', 'recommended', or 'optional'"
    )
    expected_discriminator: str = Field(
        description="Specific scientific metric this test resolves (e.g. 'Pre-1947 bomb-pulse C14 baseline vs modern')"
    )


class UncertaintyBounds(BaseModel):
    """Explicit probabilistic uncertainty intervals for the forensic calculation."""
    lower_bound: float = Field(ge=0.0, le=1.0, description="Lower discrepancy bound")
    upper_bound: float = Field(ge=0.0, le=1.0, description="Upper discrepancy bound")
    confidence_interval: str = Field(default="95%", description="Confidence interval percentage")


class ForensicTriageOutput(BaseModel):
    """
    Deterministic structured output schema enforced via Context-Free Grammars (GBNF)
    for Google Gemma 2 2B Instruct.
    """
    discrepancy_score: float = Field(
        ge=0.0, le=1.0,
        description="Calculated contradiction score between manifest declaration and physical traits (0.0 = full agreement, 1.0 = absolute contradiction)"
    )
    flagged_indicators: List[str] = Field(
        description="Specific empirical contradictions identified during cross-examination"
    )
    suspected_actual_species: str = Field(
        description="Forensically inferred actual taxon (scientific binomial or common name)"
    )
    cites_appendix: str = Field(
        description="Applicable CITES Appendix: 'I', 'II', 'III', or 'None'"
    )
    smuggling_mo_detected: List[str] = Field(
        default_factory=list,
        description="Matched Modus Operandi pattern IDs from historical trafficking catalog"
    )
    uncertainty_bounds: UncertaintyBounds = Field(
        description="Probabilistic bounds accounting for measurement variance"
    )
    suggested_lab_action: List[LabAction] = Field(
        description="Recommended confirmatory laboratory tests"
    )
    forensic_rationale: str = Field(
        description="Clear, concise natural language reasoning detailing why the shipment was cleared, flagged, or escalated"
    )
    legal_disclaimer: str = Field(
        default=MANDATORY_LEGAL_DISCLAIMER,
        description="Mandatory statutory notice defining AI findings as investigative triage"
    )
