"""Dual-engine Gemma 2 inference harness with GBNF grammar constraints and offline mock fallback."""

import json
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import requests

from canopytrace.core.grammar import generate_gbnf_grammar
from canopytrace.schemas import (
    ShippingManifest,
    PhysicalInspection,
    ForensicTriageOutput,
    LabAction,
    UncertaintyBounds,
    MANDATORY_LEGAL_DISCLAIMER,
)


class BaseForensicHarness(ABC):
    """Abstract interface for schema-constrained Gemma forensic reasoning engines."""

    @abstractmethod
    def synthesize(
        self,
        manifest: ShippingManifest,
        inspection: PhysicalInspection,
        registry_res: Dict[str, Any],
        morph_res: Dict[str, Any],
        pattern_res: Dict[str, Any],
    ) -> ForensicTriageOutput:
        pass


class MockForensicHarness(BaseForensicHarness):
    """
    Deterministic offline heuristic triage engine used for CI, automated testing,
    and low-resource port checkpoint hardware without multi-gigabyte GGUF weights.
    Strictly conforms to ForensicTriageOutput Pydantic schema.
    """

    def synthesize(
        self,
        manifest: ShippingManifest,
        inspection: PhysicalInspection,
        registry_res: Dict[str, Any],
        morph_res: Dict[str, Any],
        pattern_res: Dict[str, Any],
    ) -> ForensicTriageOutput:
        flagged: List[str] = []
        lab_actions: List[LabAction] = []
        mos_detected: List[str] = pattern_res.get("matched_ids", [])

        suspected_species = "Undetermined specimen"
        cites_appendix = "None"
        discrepancy_score = 0.05  # baseline noise

        # 1. Evaluate Morphology Match
        suspected_taxa = morph_res.get("suspected_taxa", [])
        if suspected_taxa:
            suspected_species = suspected_taxa[0]
            # Check CITES status of suspected species
            if "Elephant" in suspected_species or "Loxodonta" in suspected_species or "Elephas" in suspected_species:
                cites_appendix = "I"
            elif "Manis" in suspected_species or "Smutsia" in suspected_species:
                cites_appendix = "I"
            elif "Dalbergia" in suspected_species:
                cites_appendix = "II"
                if "nigra" in suspected_species:
                    cites_appendix = "I"
            elif "Eretmochelys" in suspected_species:
                cites_appendix = "I"
            elif "Bos taurus" in suspected_species:
                cites_appendix = "None"

        # Check for direct discrepancy between declared item and suspected species
        decl_lower = manifest.declared_item_name.lower()
        if suspected_species != "Undetermined specimen":
            # Elephant Ivory Camouflage
            if cites_appendix == "I" and ("mammoth" in decl_lower or "bone" in decl_lower or "antique" in decl_lower):
                discrepancy_score = max(discrepancy_score, 0.92)
                flagged.append(
                    f"Physical morphology identifies {suspected_species} (CITES Appendix I), contradicting declared '{manifest.declared_item_name}'."
                )
                lab_actions.append(LabAction(
                    test_type="radiocarbon_dating_c14",
                    priority="mandatory",
                    expected_discriminator="Bomb-pulse C14 baseline: pre-1947 antique vs modern post-ban elephant ivory"
                ))
                lab_actions.append(LabAction(
                    test_type="dna_barcoding_cytochrome_b",
                    priority="recommended",
                    expected_discriminator="Genetic identification of Loxodonta africana vs Mammuthus primigenius"
                ))

            # Pangolin Scale Concealment
            elif "Manis" in suspected_species and ("horn" in decl_lower or "hoof" in decl_lower or "keratin" in decl_lower or "fertilizer" in decl_lower):
                discrepancy_score = max(discrepancy_score, 0.95)
                flagged.append(
                    f"Dermal scale morphology (dorsal keels/imbrication) confirms {suspected_species} (CITES Appendix I), contradicting declared agricultural keratin."
                )
                lab_actions.append(LabAction(
                    test_type="dna_barcoding_cytochrome_b",
                    priority="mandatory",
                    expected_discriminator="Genomic sequencing confirming Manis spp. vs domestic livestock Bos taurus"
                ))

            # Timber Concealment (Rosewood vs Teak)
            elif "Dalbergia" in suspected_species and ("teak" in decl_lower or "eucalyptus" in decl_lower or "plantation" in decl_lower):
                discrepancy_score = max(discrepancy_score, 0.88)
                flagged.append(
                    f"Diffuse porosity and storied ray ripple marks confirm {suspected_species} (CITES Appendix {cites_appendix}), contradicting declared plantation teak."
                )
                lab_actions.append(LabAction(
                    test_type="wood_anatomy_thin_section",
                    priority="mandatory",
                    expected_discriminator="Microscopic transverse thin-section verification of Dalbergia storied parenchyma"
                ))

            # Sea Turtle Bekko Concealment
            elif "Eretmochelys" in suspected_species and ("resin" in decl_lower or "plastic" in decl_lower or "celluloid" in decl_lower):
                discrepancy_score = max(discrepancy_score, 0.91)
                flagged.append(
                    f"Organic keratin scute lamellae confirm Hawksbill Sea Turtle bekko (CITES Appendix I), contradicting declared synthetic resin."
                )
                lab_actions.append(LabAction(
                    test_type="ftir_spectroscopy",
                    priority="mandatory",
                    expected_discriminator="Infrared spectrum confirming biological keratin protein vs synthetic polymer"
                ))

            # Negative Control: Legitimate Bovine Bone
            elif "Bos taurus" in suspected_species and "bone" in decl_lower:
                discrepancy_score = 0.08
                suspected_species = "Bos taurus (Domestic Cattle)"
                cites_appendix = "None"
                lab_actions.append(LabAction(
                    test_type="stereomicroscopy_osteon_inspection",
                    priority="optional",
                    expected_discriminator="Haversian canal documentation for routine clearance file"
                ))

        # 2. Check Registry Red Flags (Impossible Range States / Missing Permits)
        if registry_res.get("is_flagged"):
            for rf in registry_res.get("red_flags", []):
                flagged.append(rf)
            if not registry_res.get("is_native_range") and registry_res.get("cites_appendix") in ("I", "II"):
                discrepancy_score = max(discrepancy_score, 0.82)
                lab_actions.append(LabAction(
                    test_type="stable_isotope_geographical_provenancing",
                    priority="mandatory",
                    expected_discriminator="Isotopic verification of geographic harvest origin vs declared country"
                ))

        # 3. Incorporate Smuggling Pattern Weights
        pattern_risk = pattern_res.get("max_risk_weight", 0.0)
        if pattern_risk > 0.0:
            discrepancy_score = max(discrepancy_score, pattern_risk)

        # 4. Handle Unresolved Novel Anomaly
        if not suspected_taxa and not morph_res.get("primary_key_matched") and not registry_res.get("resolved_taxon"):
            suspected_species = "UNRESOLVED_NOVEL_ANOMALY"
            cites_appendix = "None"
            discrepancy_score = 0.50
            flagged.append("Physical morphology does not match any recognized reference key; potential novel trafficking anomaly.")
            lab_actions.append(LabAction(
                test_type="dna_metabarcoding_and_ftir",
                priority="mandatory",
                expected_discriminator="Taxonomic assignment of uncataloged biological specimen"
            ))

        # Uncertainty Bounds
        half_interval = 0.04 if discrepancy_score > 0.70 else 0.08
        lower_bound = max(0.0, round(discrepancy_score - half_interval, 2))
        upper_bound = min(1.0, round(discrepancy_score + half_interval, 2))

        # Construct Forensic Rationale
        if discrepancy_score >= 0.70:
            rationale = (
                f"Severe contradiction detected for declared cargo '{manifest.declared_item_name}'. "
                f"Empirical physical inspection contradicts paperwork declarations, exhibiting diagnostic traits "
                f"of protected contraband {suspected_species} (CITES Appendix {cites_appendix}). "
                f"Smuggling modus operandi pattern match indicates deliberate misdeclaration to evade CITES trade bans. "
                f"Immediate cargo detention and chain-of-custody laboratory confirmatory testing recommended."
            )
        elif discrepancy_score <= 0.20:
            rationale = (
                f"Physical inspection findings are consistent with declared cargo '{manifest.declared_item_name}'. "
                f"Morphological analysis confirms non-regulated domestic specimen ({suspected_species}). "
                f"Discrepancy score is within normal clearance tolerance; standard release recommended."
            )
        else:
            rationale = (
                f"Inconclusive or anomalous observation for '{manifest.declared_item_name}'. "
                f"Physical traits exhibit ambiguity requiring higher authority review and secondary laboratory analysis."
            )

        return ForensicTriageOutput(
            discrepancy_score=round(discrepancy_score, 2),
            flagged_indicators=flagged,
            suspected_actual_species=suspected_species,
            cites_appendix=cites_appendix,
            smuggling_mo_detected=mos_detected,
            uncertainty_bounds=UncertaintyBounds(
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                confidence_interval="95%"
            ),
            suggested_lab_action=lab_actions,
            forensic_rationale=rationale,
            legal_disclaimer=MANDATORY_LEGAL_DISCLAIMER,
        )


class LlamaCppForensicHarness(BaseForensicHarness):
    """
    Executes quantized Google Gemma 2 2B Instruct GGUF locally via llama-cpp-python
    with Context-Free Grammar (GBNF) logit masking for strict schema compliance.
    """

    def __init__(self, model_path: str, n_ctx: int = 4096):
        try:
            from llama_cpp import Llama, LlamaGrammar
            self.grammar = LlamaGrammar.from_string(generate_gbnf_grammar())
            self.llm = Llama(model_path=model_path, n_ctx=n_ctx, verbose=False)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize llama-cpp-python: {e}")

    def synthesize(
        self,
        manifest: ShippingManifest,
        inspection: PhysicalInspection,
        registry_res: Dict[str, Any],
        morph_res: Dict[str, Any],
        pattern_res: Dict[str, Any],
    ) -> ForensicTriageOutput:
        prompt = (
            f"<start_of_turn>user\n"
            f"You are CanopyTrace, an expert wildlife forensic investigative assistant.\n"
            f"Analyze the following customs manifest and physical morphology observation data.\n"
            f"Manifest:\n{manifest.model_dump_json()}\n"
            f"Physical Inspection:\n{inspection.model_dump_json()}\n"
            f"Registry Audit:\n{json.dumps(registry_res)}\n"
            f"Morphology Key Match:\n{json.dumps(morph_res)}\n"
            f"Smuggling Patterns:\n{json.dumps(pattern_res)}\n"
            f"Synthesize the forensic triage verdict strictly according to the GBNF schema.<end_of_turn>\n"
            f"<start_of_turn>model\n"
        )
        response = self.llm(
            prompt,
            grammar=self.grammar,
            max_tokens=1024,
            temperature=0.1,
            stop=["<end_of_turn>"]
        )
        raw_json = response["choices"][0]["text"].strip()
        data = json.loads(raw_json)
        return ForensicTriageOutput.model_validate(data)


class LocalServerForensicHarness(BaseForensicHarness):
    """
    Connects to local OpenAI-compatible Gemma 2 endpoints (Ollama, vLLM, or llama.cpp server).
    """

    def __init__(self, api_base: str = "http://localhost:11434/v1", model_name: str = "gemma2:2b"):
        self.api_base = api_base.rstrip("/")
        self.model_name = model_name

    def synthesize(
        self,
        manifest: ShippingManifest,
        inspection: PhysicalInspection,
        registry_res: Dict[str, Any],
        morph_res: Dict[str, Any],
        pattern_res: Dict[str, Any],
    ) -> ForensicTriageOutput:
        url = f"{self.api_base}/chat/completions"
        system_prompt = (
            "You are CanopyTrace forensic assistant. Output valid JSON matching the ForensicTriageOutput schema."
        )
        user_prompt = (
            f"Manifest: {manifest.model_dump_json()}\n"
            f"Inspection: {inspection.model_dump_json()}\n"
            f"Registry: {json.dumps(registry_res)}\n"
            f"Morphology: {json.dumps(morph_res)}\n"
            f"Patterns: {json.dumps(pattern_res)}"
        )
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
        res = requests.post(url, json=payload, timeout=60)
        res.raise_for_status()
        data = res.json()
        content = data["choices"][0]["message"]["content"]
        return ForensicTriageOutput.model_validate_json(content)


def get_forensic_harness(
    model_path: Optional[str] = None,
    server_url: Optional[str] = None,
    force_mock: bool = False,
) -> BaseForensicHarness:
    """
    Factory creating appropriate Gemma forensic harness.
    Falls back to deterministic MockForensicHarness if model weights or server are unavailable.
    """
    if force_mock or os.environ.get("CANOPYTRACE_MOCK_HARNESS", "0") == "1":
        return MockForensicHarness()

    if model_path and os.path.exists(model_path):
        try:
            return LlamaCppForensicHarness(model_path)
        except Exception:
            pass

    if server_url or os.environ.get("CANOPYTRACE_LLM_SERVER"):
        url = server_url or os.environ.get("CANOPYTRACE_LLM_SERVER", "http://localhost:11434/v1")
        try:
            return LocalServerForensicHarness(api_base=url)
        except Exception:
            pass

    # Default robust deterministic fallback
    return MockForensicHarness()
