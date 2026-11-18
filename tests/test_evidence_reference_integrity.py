"""Adversarial references test suite. All inputs are hypothetical SYNTHETIC."""
import copy
import json
import unittest
from pathlib import Path

from dgsi.diagnostic_context import DiagnosticContextValidationError, validate_diagnostic_case

ROOT = Path(__file__).resolve().parents[1]
BASE = json.loads((ROOT / "examples/diagnostic_context_case_illustrative.json").read_text(encoding="utf-8"))


class EvidenceReferenceIntegrityTests(unittest.TestCase):
    def case(self):
        return copy.deepcopy(BASE)

    def reject(self, case, reason):
        with self.assertRaisesRegex(DiagnosticContextValidationError, reason):
            validate_diagnostic_case(case)

    def test_synthetic_illustration_has_resolved_references(self):
        self.assertIn("NOT_GOLD_REVIEWED", validate_diagnostic_case(self.case()))

    def test_fabricated_supporting_evidence_ref_is_rejected(self):
        x = self.case()
        x["expected_output"]["evidence_assessment"]["supporting_refs"].append("NONEXISTENT-ML-000")
        self.reject(x, "UNRESOLVED_EXPECTED_EVIDENCE_REFERENCE")

    def test_fabricated_contradicting_log_ref_is_rejected(self):
        x = self.case()
        x["expected_output"]["evidence_assessment"]["contradicting_refs"] = ["LOG-NOT-SUPPLIED"]
        self.reject(x, "UNRESOLVED_EXPECTED_EVIDENCE_REFERENCE")

    def test_fabricated_candidate_supporting_ref_is_rejected(self):
        x = self.case()
        x["expected_output"]["cause_localization"]["candidates"][0]["supporting_refs"].append("SYNTHETIC-ABSENT")
        self.reject(x, "UNRESOLVED_EXPECTED_EVIDENCE_REFERENCE")

    def test_duplicate_machine_finding_id_is_rejected(self):
        x = self.case()
        x["input"]["machine_diagnosis"]["findings"][1]["finding_id"] = "F-01"
        self.reject(x, "DUPLICATE_MACHINE_FINDING_ID")

    def test_ambiguous_log_and_machine_evidence_id_is_rejected(self):
        x = self.case()
        x["input"]["diagnostic_logs"][0]["log_id"] = "ML-E-01"
        self.reject(x, "AMBIGUOUS_CROSS_SOURCE_EVIDENCE_ID")

    def test_duplicate_knowledge_evidence_id_is_rejected(self):
        x = self.case()
        x["input"]["knowledge_evidence"].append(copy.deepcopy(x["input"]["knowledge_evidence"][0]))
        self.reject(x, "DUPLICATE_KNOWLEDGE_EVIDENCE_ID")

    def test_unprovided_history_cannot_be_cited_as_precedent(self):
        x = self.case()
        x["expected_output"]["historical_experience_relevance"][0]["case_ref"] = "UNSEEN-HISTORY"
        self.reject(x, "UNRESOLVED_HISTORICAL_EXPERIENCE_REFERENCE")

    def test_provenance_cannot_claim_unprovided_history(self):
        x = self.case()
        x["provenance"]["historical_case_refs"].append("UNSEEN-HISTORY")
        self.reject(x, "UNRESOLVED_PROVENANCE_HISTORY_REFERENCE")

    def test_shared_machine_evidence_across_findings_is_allowed(self):
        x = self.case()
        x["input"]["machine_diagnosis"]["findings"][1]["supporting_evidence_ids"].append("ML-E-01")
        validate_diagnostic_case(x)

    def test_missing_machine_evidence_declaration_is_rejected(self):
        x = self.case()
        x["input"]["machine_diagnosis"]["findings"][0]["supporting_evidence_ids"].remove("ML-E-02")
        self.reject(x, "UNRESOLVED_EXPECTED_EVIDENCE_REFERENCE")


if __name__ == "__main__":
    unittest.main()
