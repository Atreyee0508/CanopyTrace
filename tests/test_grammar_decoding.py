"""Unit tests for GBNF grammar generation and strict schema compliance."""

import json
import pytest
from canopytrace.core.grammar import generate_gbnf_grammar, get_json_schema
from canopytrace.schemas import ForensicTriageOutput, UncertaintyBounds, LabAction


def test_gbnf_grammar_syntax():
    grammar = generate_gbnf_grammar()
    assert "root ::=" in grammar
    assert "discrepancy_score" in grammar
    assert "cites_appendix" in grammar
    assert "bounds_obj" in grammar
    assert "lab_list" in grammar


def test_forensic_triage_output_schema_validation():
    sample_data = {
        "discrepancy_score": 0.94,
        "flagged_indicators": ["Schreger outer angle 125 deg indicates modern elephant."],
        "suspected_actual_species": "Loxodonta africana",
        "cites_appendix": "I",
        "smuggling_mo_detected": ["MO-IVO-001"],
        "uncertainty_bounds": {
            "lower_bound": 0.90,
            "upper_bound": 0.98,
            "confidence_interval": "95%"
        },
        "suggested_lab_action": [
            {
                "test_type": "radiocarbon_dating_c14",
                "priority": "mandatory",
                "expected_discriminator": "Bomb pulse threshold"
            }
        ],
        "forensic_rationale": "Severe discrepancy detected.",
        "legal_disclaimer": "AI findings provide investigative triage and do not constitute certified legal testimony."
    }
    output = ForensicTriageOutput.model_validate(sample_data)
    assert output.discrepancy_score == 0.94
    assert output.cites_appendix == "I"
    assert len(output.suggested_lab_action) == 1


def test_schema_rejects_invalid_discrepancy_score():
    with pytest.raises(Exception):
        ForensicTriageOutput.model_validate({
            "discrepancy_score": 1.50,  # Invalid: ge 0.0, le 1.0
            "flagged_indicators": [],
            "suspected_actual_species": "Unknown",
            "cites_appendix": "None",
            "smuggling_mo_detected": [],
            "uncertainty_bounds": {"lower_bound": 0.0, "upper_bound": 1.0, "confidence_interval": "95%"},
            "suggested_lab_action": [],
            "forensic_rationale": "Invalid",
            "legal_disclaimer": "Notice"
        })
