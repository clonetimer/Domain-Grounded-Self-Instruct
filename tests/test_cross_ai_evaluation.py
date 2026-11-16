from __future__ import annotations
import copy, json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from dgsi.cross_ai_evaluation import CrossAIEvaluationError, DIMENSIONS, validate_cross_ai_evaluation

class CrossAIEvaluationSemanticTests(unittest.TestCase):
    def setUp(self):
        self.record=json.loads((ROOT/"skills/dgsi-simulation-to-sft/templates/CROSS_AI_EVALUATION_TEMPLATE.json").read_text())
        base={"provider":"p","model_id":"m","model_version":"1","run_at":"2026-11-16T00:00:00Z","settings_fingerprint":"1"*64,"raw_output_sha256":"2"*64,"candidate_count":6,"status":"COMPLETE"}
        self.record["runs"]=[dict(base,blind_alias="AI-A01"),dict(base,blind_alias="AI-B02",raw_output_sha256="3"*64)]
        self.record["status"]="ADJUDICATION_PENDING"
        self.record["adjudication"]["dimensions"]=[{"blind_alias":"AI-A01","dimension":"fact_fidelity","score":2,"evidence_note":"source checked"}]

    def reject(self,code,record=None):
        with self.assertRaisesRegex(CrossAIEvaluationError,"^"+code+"$"):
            validate_cross_ai_evaluation(record or self.record)

    def test_protocol_ready_is_valid_without_runs(self):
        r=copy.deepcopy(self.record); r["runs"]=[]; r["status"]="PROTOCOL_READY"; r["adjudication"]["dimensions"]=[]
        self.assertEqual(validate_cross_ai_evaluation(r)["run_count"],0)

    def test_unique_runs_and_partial_adjudication_valid(self):
        self.assertEqual(validate_cross_ai_evaluation(self.record)["unique_alias_count"],2)

    def test_duplicate_alias_rejected(self):
        r=copy.deepcopy(self.record); r["runs"][1]["blind_alias"]="AI-A01"
        self.reject("CROSS_AI_DUPLICATE_ALIAS",r)

    def test_duplicate_dimension_for_alias_rejected(self):
        r=copy.deepcopy(self.record); r["adjudication"]["dimensions"].append(copy.deepcopy(r["adjudication"]["dimensions"][0]))
        self.reject("CROSS_AI_DUPLICATE_SCORE",r)

    def test_unknown_alias_in_score_rejected(self):
        r=copy.deepcopy(self.record); r["adjudication"]["dimensions"][0]["blind_alias"]="AI-Z99"
        self.reject("CROSS_AI_UNKNOWN_SCORE_ALIAS",r)

    def test_unknown_alias_in_critical_failure_rejected(self):
        r=copy.deepcopy(self.record); r["adjudication"]["critical_failures"]=[{"blind_alias":"AI-Z99","failure_code":"FABRICATED_FACT","evidence_note":"unsupported"}]
        self.reject("CROSS_AI_UNKNOWN_FAILURE_ALIAS",r)

    def test_adjudicated_requires_all_dimensions_for_each_run(self):
        r=copy.deepcopy(self.record); r["status"]="ADJUDICATED"; r["adjudication"]["reference_basis"]="SOURCE_GROUNDED_HUMAN_ADJUDICATION"
        self.reject("CROSS_AI_ADJUDICATION_INCOMPLETE",r)

    def test_complete_adjudication_valid(self):
        r=copy.deepcopy(self.record); r["status"]="ADJUDICATED"; r["adjudication"]["reference_basis"]="EXPERT_ADJUDICATION"
        r["adjudication"]["dimensions"]=[{"blind_alias":a,"dimension":d,"score":2,"evidence_note":"reviewed against source"} for a in ("AI-A01","AI-B02") for d in DIMENSIONS]
        out=validate_cross_ai_evaluation(r)
        self.assertTrue(out["adjudication_complete"])
        self.assertFalse(out["training_authorized"])

    def test_adjudicated_requires_real_adjudication_basis(self):
        r=copy.deepcopy(self.record); r["status"]="ADJUDICATED"
        r["adjudication"]["dimensions"]=[{"blind_alias":a,"dimension":d,"score":2,"evidence_note":"reviewed"} for a in ("AI-A01","AI-B02") for d in DIMENSIONS]
        self.reject("CROSS_AI_ADJUDICATION_BASIS_MISSING",r)

if __name__=="__main__": unittest.main()
