"""Context-Free Grammar (GBNF) generator for schema-constrained Gemma 2 decoding."""

from typing import Any, Dict
from canopytrace.schemas.forensic_output import ForensicTriageOutput


def generate_gbnf_grammar() -> str:
    """
    Generates a strict Context-Free Grammar (GBNF) string matching the
    ForensicTriageOutput JSON schema.
    """
    gbnf = r'''root ::= "{" ws "\"discrepancy_score\":" ws number "," ws "\"flagged_indicators\":" ws string_list "," ws "\"suspected_actual_species\":" ws string "," ws "\"cites_appendix\":" ws appendix_val "," ws "\"smuggling_mo_detected\":" ws string_list "," ws "\"uncertainty_bounds\":" ws bounds_obj "," ws "\"suggested_lab_action\":" ws lab_list "," ws "\"forensic_rationale\":" ws string "," ws "\"legal_disclaimer\":" ws string ws "}"

bounds_obj ::= "{" ws "\"lower_bound\":" ws number "," ws "\"upper_bound\":" ws number "," ws "\"confidence_interval\":" ws string ws "}"

lab_list ::= "[]" | "[" ws lab_item ("," ws lab_item)* ws "]"
lab_item ::= "{" ws "\"test_type\":" ws string "," ws "\"priority\":" ws string "," ws "\"expected_discriminator\":" ws string ws "}"

appendix_val ::= "\"I\"" | "\"II\"" | "\"III\"" | "\"None\""

string_list ::= "[]" | "[" ws string ("," ws string)* ws "]"

string ::= "\"" ([^"\\] | "\\" (["\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]))* "\""
number ::= ("-"? ([0-9] | [1-9] [0-9]*)) ("." [0-9]+)? ([eE] [-+]? [0-9]+)?
boolean ::= "true" | "false"
null ::= "null"
ws ::= [ \t\n\r]*
'''
    return gbnf


def get_json_schema() -> Dict[str, Any]:
    """Returns the JSON schema dict from Pydantic model."""
    return ForensicTriageOutput.model_json_schema()
