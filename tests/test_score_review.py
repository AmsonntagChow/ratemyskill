import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "ratemyskill" / "scripts" / "score_review.py"
SPEC = importlib.util.spec_from_file_location("score_review", SCRIPT)
score_review = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(score_review)


def base_payload():
    evidence = [
        {
            "id": "e-install", "kind": "install", "result": "pass",
            "reproducible": True, "fresh": True, "lane": "structural",
            "assertion_type": "deterministic",
        },
        {
            "id": "e-reference", "kind": "reference", "result": "pass",
            "reproducible": True, "fresh": True, "lane": "structural",
            "assertion_type": "deterministic",
        },
        {
            "id": "e-runtime", "kind": "runtime", "result": "pass",
            "reproducible": True, "fresh": True, "lane": "critical-journey-e2e",
            "assertion_type": "deterministic",
        },
        {
            "id": "e-selection", "kind": "test", "result": "pass",
            "reproducible": True, "fresh": True, "lane": "probabilistic-eval",
            "assertion_type": "mixed",
        },
        {
            "id": "e-deterministic", "kind": "test", "result": "pass",
            "reproducible": True, "fresh": True, "lane": "deterministic-checks",
            "assertion_type": "deterministic",
        },
    ]
    return {
        "schema_version": "2",
        "mode": "skill-user",
        "rubric_id": "test/default-v1",
        "publish_target": "public-marketplace",
        "dimensions": [
            {
                "id": "instructions",
                "weight": 25,
                "score": 90,
                "verification": "verified",
                "evidence_ids": ["e-reference"],
            },
            {
                "id": "selection",
                "weight": 25,
                "score": 90,
                "verification": "verified",
                "evidence_ids": ["e-selection"],
            },
            {
                "id": "execution",
                "weight": 25,
                "score": 90,
                "verification": "verified",
                "evidence_ids": ["e-runtime"],
            },
            {
                "id": "safety",
                "weight": 25,
                "score": 90,
                "verification": "verified",
                "evidence_ids": ["e-selection"],
            },
        ],
        "evidence": evidence,
        "evidence_panel": {
            "deterministic-checks": {"status": "pass", "evidence_ids": ["e-deterministic"]},
            "critical-journey-e2e": {"status": "pass", "evidence_ids": ["e-runtime"]},
            "probabilistic-eval": {"status": "pass", "evidence_ids": ["e-selection"]},
            "continuous-evidence": {"status": "not-applicable", "evidence_ids": []},
        },
        "behavioral_eval": {
            "status": "recorded",
            "evidence_ids": ["e-selection"],
            "definition_id": "ratemyskill-evals-v1",
            "run_id": "run-test-001",
            "package_sha256": "sha256:" + "a" * 64,
            "host": "test-host",
            "model": "test-model",
            "skill_or_prompt_sha256": "sha256:" + "b" * 64,
            "dataset_id": "test-dataset-v1",
            "rubric_id": "test-rubric-v1",
            "judge": {
                "kind": "deterministic",
                "id": "hidden-assertions",
                "version": "1",
                "calibration_evidence_ids": [],
            },
            "selection": {
                "runs_per_case": 3,
                "positive_trials": 6,
                "positive_hits": 6,
                "near_miss_trials": 6,
                "false_triggers": 0,
                "minimum_hit_rate_percent": 80,
                "maximum_false_trigger_rate_percent": 10,
            },
            "execution": {
                "runs_per_arm": 4,
                "with_skill_passes": 4,
                "without_skill_passes": 2,
                "minimum_uplift_points": 20,
            },
            "variance_policy": "Repeat each case and fail closed when a threshold is unstable.",
        },
        "coverage": {
            "runtime": {"level": "full", "evidence_ids": ["e-runtime"]},
            "selection": {"level": "tested", "evidence_ids": ["e-selection"]},
            "cold_install": {"level": "tested", "evidence_ids": ["e-install"]},
            "required_references": {
                "total": 2,
                "resolved": 2,
                "evidence_ids": ["e-reference"],
            },
        },
        "gates": [],
        "publish_checks": [
            {
                "id": "clean-install",
                "required": True,
                "status": "pass",
                "evidence_ids": ["e-runtime"],
            }
        ],
    }


TARGET_CHECK_FIXTURES = (
    ("sandboxed-authority-and-side-effects", "e-authority", "runtime", "critical-journey-e2e"),
    ("independent-domain-review", "e-domain-review", "document", "deterministic-checks"),
    ("human-control", "e-human-control", "test", "critical-journey-e2e"),
    ("auditability", "e-auditability", "log", "continuous-evidence"),
    ("incident-response", "e-incident-response", "test", "critical-journey-e2e"),
)


def add_target_checks(payload, target):
    if target == "privileged-production":
        fixtures = TARGET_CHECK_FIXTURES[:1]
    elif target == "high-stakes":
        fixtures = TARGET_CHECK_FIXTURES
    else:
        fixtures = ()
    if target == "privileged-production":
        payload["evidence"].append(
            {
                "id": "e-privileged-monitoring",
                "kind": "log",
                "result": "pass",
                "reproducible": True,
                "fresh": True,
                "lane": "continuous-evidence",
                "assertion_type": "deterministic",
            }
        )
        payload["evidence_panel"]["continuous-evidence"] = {
            "status": "pass",
            "evidence_ids": ["e-privileged-monitoring"],
        }
    for check_id, evidence_id, kind, lane in fixtures:
        payload["evidence"].append(
            {
                "id": evidence_id,
                "kind": kind,
                "result": "pass",
                "reproducible": True,
                "fresh": True,
                "lane": lane,
                "assertion_type": "deterministic",
            }
        )
        lane_record = payload["evidence_panel"][lane]
        lane_record["status"] = "pass"
        lane_record["evidence_ids"].append(evidence_id)
        payload["publish_checks"].append(
            {
                "id": check_id,
                "required": True,
                "status": "pass",
                "evidence_ids": [evidence_id],
            }
        )


class ScoreReviewTests(unittest.TestCase):
    def compute(self, payload):
        return score_review.compute(score_review.validate(payload))

    def run_cli(self, payload_text=None, extra_args=None):
        extra_args = extra_args or []
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "scorecard.json"
            if payload_text is not None:
                path.write_text(payload_text, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(SCRIPT), *extra_args, str(path)],
                check=False,
                capture_output=True,
                text=True,
            )

    def add_active_gate(self, payload, gate_id):
        payload["evidence"].append(
            {
                "id": "e-veto", "kind": "static-analysis", "result": "fail",
                "reproducible": True, "fresh": True, "lane": "structural",
                "assertion_type": "deterministic",
            }
        )
        payload["gates"] = [
            {
                "id": gate_id,
                "state": "active",
                "evidence_ids": ["e-veto"],
                "retest_evidence_ids": [],
            }
        ]

    def test_fully_evidenced_skill_is_ready_for_marketplace(self):
        result = self.compute(base_payload())
        self.assertEqual(result["decision"], "READY")
        self.assertEqual(result["scores"], {"raw_quality": 90, "publish_readiness": 90})
        self.assertEqual(result["coverage"]["confidence"], "A")
        self.assertEqual(result["distribution_evidence_gaps"], [])
        self.assertEqual(result["publish_checks"]["target_required"], [])

    def test_all_requested_modes_are_supported(self):
        for mode in (
            "skill-user",
            "staff-agent-engineer",
            "agent-engineer",
            "red-team",
            "adversarial",
            "marketplace-curator",
            "oral-defense",
        ):
            with self.subTest(mode=mode):
                payload = base_payload()
                payload["mode"] = mode
                self.assertEqual(self.compute(payload)["mode"], mode)

    def test_distribution_target_thresholds_match_the_published_ladder(self):
        expected = {
            "local-draft": 50,
            "team-shared": 65,
            "public-marketplace": 75,
            "privileged-production": 85,
            "high-stakes": 90,
        }
        for target, threshold in expected.items():
            with self.subTest(target=target):
                payload = base_payload()
                payload["publish_target"] = target
                add_target_checks(payload, target)
                result = self.compute(payload)
                self.assertEqual(result["publish_threshold"], threshold)
                self.assertEqual(result["decision"], "READY")

    def test_privileged_production_requires_sandboxed_authority_check(self):
        payload = base_payload()
        payload["publish_target"] = "privileged-production"
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertEqual(caught.exception.path, "$.publish_checks")
        self.assertIn("sandboxed-authority-and-side-effects", caught.exception.message)

    def test_privileged_authority_check_must_be_marked_required(self):
        payload = base_payload()
        payload["publish_target"] = "privileged-production"
        add_target_checks(payload, "privileged-production")
        next(
            item
            for item in payload["publish_checks"]
            if item["id"] == "sandboxed-authority-and-side-effects"
        )["required"] = False
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertIn("must set required to true", caught.exception.message)

    def test_unverified_privileged_authority_check_is_insufficient_evidence(self):
        payload = base_payload()
        payload["publish_target"] = "privileged-production"
        add_target_checks(payload, "privileged-production")
        check = next(
            item
            for item in payload["publish_checks"]
            if item["id"] == "sandboxed-authority-and-side-effects"
        )
        check["status"] = "unverified"
        check["evidence_ids"] = []
        result = self.compute(payload)
        self.assertEqual(result["decision"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(
            result["publish_checks"]["unverified_required"],
            ["sandboxed-authority-and-side-effects"],
        )

    def test_privileged_authority_check_rejects_stale_passing_evidence(self):
        payload = base_payload()
        payload["publish_target"] = "privileged-production"
        add_target_checks(payload, "privileged-production")
        next(item for item in payload["evidence"] if item["id"] == "e-authority")["fresh"] = False
        with self.assertRaises(score_review.ValidationError):
            score_review.validate(payload)

    def test_privileged_authority_check_rejects_document_only_evidence(self):
        payload = base_payload()
        payload["publish_target"] = "privileged-production"
        add_target_checks(payload, "privileged-production")
        next(item for item in payload["evidence"] if item["id"] == "e-authority")["kind"] = "document"
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertIn("allowed kind", caught.exception.message)

    def test_high_stakes_requires_every_target_specific_check(self):
        payload = base_payload()
        payload["publish_target"] = "high-stakes"
        add_target_checks(payload, "high-stakes")
        for check_id, _, _, _ in TARGET_CHECK_FIXTURES:
            with self.subTest(check_id=check_id):
                candidate = copy.deepcopy(payload)
                candidate["publish_checks"] = [
                    item for item in candidate["publish_checks"] if item["id"] != check_id
                ]
                with self.assertRaises(score_review.ValidationError) as caught:
                    score_review.validate(candidate)
                self.assertIn(check_id, caught.exception.message)

    def test_unverified_domain_review_blocks_high_stakes_approval(self):
        payload = base_payload()
        payload["publish_target"] = "high-stakes"
        add_target_checks(payload, "high-stakes")
        check = next(
            item
            for item in payload["publish_checks"]
            if item["id"] == "independent-domain-review"
        )
        check["status"] = "unverified"
        check["evidence_ids"] = []
        result = self.compute(payload)
        self.assertEqual(result["decision"], "INSUFFICIENT_EVIDENCE")
        self.assertIn("independent-domain-review", result["publish_checks"]["unverified_required"])

    def test_high_stakes_ready_reports_all_target_specific_checks(self):
        payload = base_payload()
        payload["publish_target"] = "high-stakes"
        add_target_checks(payload, "high-stakes")
        result = self.compute(payload)
        self.assertEqual(result["decision"], "READY")
        self.assertEqual(
            result["publish_checks"]["target_required"],
            sorted(item[0] for item in TARGET_CHECK_FIXTURES),
        )

    def test_raw_quality_is_separate_from_evidence_adjusted_readiness(self):
        payload = base_payload()
        for dimension in payload["dimensions"]:
            dimension["verification"] = "unverified"
            dimension["evidence_ids"] = []
        result = self.compute(payload)
        self.assertEqual(result["scores"]["raw_quality"], 90)
        self.assertEqual(result["scores"]["publish_readiness"], 49)
        self.assertEqual(result["coverage"]["confidence"], "D")
        self.assertEqual(result["decision"], "NOT_READY")

    def test_missing_runtime_evidence_caps_public_marketplace_approval(self):
        payload = base_payload()
        payload["coverage"]["runtime"] = {"level": "static", "evidence_ids": []}
        result = self.compute(payload)
        self.assertEqual(result["scores"]["raw_quality"], 90)
        self.assertEqual(result["scores"]["publish_readiness"], 69)
        self.assertEqual(result["distribution_evidence_gaps"], ["runtime"])
        self.assertEqual(result["decision"], "INSUFFICIENT_EVIDENCE")

    def test_missing_selection_evidence_caps_public_marketplace_approval(self):
        payload = base_payload()
        payload["coverage"]["selection"] = {"level": "claimed", "evidence_ids": []}
        result = self.compute(payload)
        self.assertEqual(result["scores"]["publish_readiness"], 69)
        self.assertEqual(result["distribution_evidence_gaps"], ["selection"])
        self.assertEqual(result["decision"], "INSUFFICIENT_EVIDENCE")

    def test_missing_cold_install_evidence_caps_public_marketplace_approval(self):
        payload = base_payload()
        payload["coverage"]["cold_install"] = {"level": "claimed", "evidence_ids": []}
        result = self.compute(payload)
        self.assertEqual(result["scores"]["publish_readiness"], 69)
        self.assertEqual(result["distribution_evidence_gaps"], ["cold-install"])
        self.assertEqual(result["decision"], "INSUFFICIENT_EVIDENCE")

    def test_unresolved_required_reference_caps_public_marketplace_approval(self):
        payload = base_payload()
        payload["coverage"]["required_references"]["resolved"] = 1
        result = self.compute(payload)
        self.assertEqual(result["scores"]["publish_readiness"], 69)
        self.assertEqual(result["distribution_evidence_gaps"], ["required-references"])
        self.assertEqual(result["decision"], "INSUFFICIENT_EVIDENCE")

    def test_static_and_claimed_evidence_can_be_enough_for_local_draft(self):
        payload = base_payload()
        payload["publish_target"] = "local-draft"
        payload["coverage"]["runtime"] = {"level": "static", "evidence_ids": []}
        payload["coverage"]["selection"] = {"level": "claimed", "evidence_ids": []}
        result = self.compute(payload)
        self.assertEqual(result["scores"]["publish_readiness"], 69)
        self.assertEqual(result["distribution_evidence_gaps"], [])
        self.assertEqual(result["decision"], "READY")

    def test_team_shared_requires_fresh_execution_and_selection_evidence(self):
        payload = base_payload()
        payload["publish_target"] = "team-shared"
        payload["coverage"]["runtime"] = {"level": "static", "evidence_ids": []}
        payload["coverage"]["selection"] = {"level": "claimed", "evidence_ids": []}
        result = self.compute(payload)
        self.assertEqual(result["scores"]["publish_readiness"], 64)
        self.assertEqual(result["distribution_evidence_gaps"], ["runtime", "selection"])
        self.assertEqual(result["decision"], "INSUFFICIENT_EVIDENCE")

    def test_team_shared_requires_recorded_behavioral_eval_summary(self):
        payload = base_payload()
        payload["publish_target"] = "team-shared"
        payload["behavioral_eval"] = {"status": "unverified", "evidence_ids": []}
        result = self.compute(payload)
        self.assertEqual(result["decision"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(result["distribution_evidence_gaps"], ["behavioral-eval-summary"])

    def test_public_marketplace_requires_run_summary_not_eval_definition(self):
        payload = base_payload()
        payload["behavioral_eval"] = {"status": "unverified", "evidence_ids": []}
        result = self.compute(payload)
        self.assertEqual(result["decision"], "INSUFFICIENT_EVIDENCE")
        self.assertIn("behavioral-eval-summary", result["distribution_evidence_gaps"])

    def test_behavioral_summary_reports_selection_and_uplift_metrics(self):
        result = self.compute(base_payload())
        summary = result["behavioral_eval"]
        self.assertEqual(summary["selection"]["hit_rate_percent"], 100)
        self.assertEqual(summary["selection"]["false_trigger_rate_percent"], 0)
        self.assertEqual(summary["execution"]["uplift_points"], 50)
        self.assertTrue(summary["metrics_pass"])

    def test_passing_probabilistic_lane_rejects_failed_threshold(self):
        payload = base_payload()
        payload["behavioral_eval"]["selection"]["positive_hits"] = 1
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertEqual(caught.exception.path, "$.evidence_panel.probabilistic-eval.status")

    def test_failed_evidence_lane_prevents_ready_decision(self):
        payload = base_payload()
        next(item for item in payload["evidence"] if item["id"] == "e-selection")["result"] = "fail"
        payload["evidence_panel"]["probabilistic-eval"]["status"] = "fail"
        result = self.compute(payload)
        self.assertEqual(result["decision"], "NOT_READY")
        self.assertEqual(result["evidence_panel_failures"], ["probabilistic-eval"])

    def test_passing_lane_rejects_any_failing_evidence(self):
        payload = base_payload()
        payload["evidence"].append(
            {
                "id": "e-deterministic-failure",
                "kind": "test",
                "result": "fail",
                "reproducible": True,
                "fresh": True,
                "lane": "deterministic-checks",
                "assertion_type": "deterministic",
            }
        )
        payload["evidence_panel"]["deterministic-checks"]["evidence_ids"].append(
            "e-deterministic-failure"
        )
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertEqual(caught.exception.path, "$.evidence_panel.deterministic-checks.status")

    def test_lane_cannot_hide_declared_failing_evidence(self):
        payload = base_payload()
        payload["evidence"].append(
            {
                "id": "e-hidden-failure",
                "kind": "test",
                "result": "fail",
                "reproducible": True,
                "fresh": True,
                "lane": "deterministic-checks",
                "assertion_type": "deterministic",
            }
        )
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertEqual(
            caught.exception.path,
            "$.evidence_panel.deterministic-checks.evidence_ids",
        )

    def test_required_unverified_or_not_applicable_lane_blocks_public_readiness(self):
        for status in ("unverified", "not-applicable"):
            with self.subTest(status=status):
                payload = base_payload()
                next(
                    item for item in payload["evidence"] if item["id"] == "e-deterministic"
                )["lane"] = "structural"
                payload["evidence_panel"]["deterministic-checks"] = {
                    "status": status,
                    "evidence_ids": [],
                }
                result = self.compute(payload)
                self.assertEqual(result["decision"], "INSUFFICIENT_EVIDENCE")
                self.assertEqual(result["scores"]["publish_readiness"], 69)
                self.assertEqual(result["evidence_panel_gaps"], ["deterministic-checks"])
                self.assertIn(
                    "evidence-lane:deterministic-checks",
                    result["distribution_evidence_gaps"],
                )

    def test_structural_test_cannot_claim_runtime_coverage(self):
        payload = base_payload()
        runtime = next(item for item in payload["evidence"] if item["id"] == "e-runtime")
        runtime["kind"] = "test"
        runtime["lane"] = "structural"
        payload["evidence_panel"]["critical-journey-e2e"] = {
            "status": "not-applicable",
            "evidence_ids": [],
        }
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertEqual(caught.exception.path, "$.coverage.runtime.evidence_ids")

    def test_structural_evidence_cannot_pass_privileged_authority_check(self):
        payload = base_payload()
        payload["publish_target"] = "privileged-production"
        add_target_checks(payload, "privileged-production")
        next(item for item in payload["evidence"] if item["id"] == "e-authority")[
            "lane"
        ] = "structural"
        payload["evidence_panel"]["critical-journey-e2e"]["evidence_ids"].remove(
            "e-authority"
        )
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertEqual(caught.exception.path, "$.publish_checks")

    def test_behavioral_thresholds_must_be_non_vacuous(self):
        mutations = (
            ("selection", "minimum_hit_rate_percent", 0),
            ("selection", "maximum_false_trigger_rate_percent", 100),
            ("execution", "minimum_uplift_points", 0),
        )
        for section, field, value in mutations:
            with self.subTest(section=section, field=field):
                payload = base_payload()
                payload["behavioral_eval"][section][field] = value
                with self.assertRaises(score_review.ValidationError):
                    score_review.validate(payload)

    def test_behavioral_thresholds_reject_inverted_selection_boundary(self):
        payload = base_payload()
        payload["behavioral_eval"]["selection"]["minimum_hit_rate_percent"] = 10
        payload["behavioral_eval"]["selection"]["maximum_false_trigger_rate_percent"] = 10
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertEqual(caught.exception.path, "$.behavioral_eval.selection")

    def test_evidence_panel_rejects_cross_lane_substitution(self):
        payload = base_payload()
        payload["evidence_panel"]["critical-journey-e2e"]["evidence_ids"] = [
            "e-deterministic"
        ]
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertEqual(
            caught.exception.path,
            "$.evidence_panel.critical-journey-e2e.evidence_ids",
        )

    def test_deterministic_lane_rejects_probabilistic_assertion(self):
        payload = base_payload()
        next(item for item in payload["evidence"] if item["id"] == "e-deterministic")[
            "assertion_type"
        ] = "probabilistic"
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertEqual(
            caught.exception.path,
            "$.evidence_panel.deterministic-checks.evidence_ids",
        )

    def test_llm_judge_requires_calibration_evidence(self):
        payload = base_payload()
        payload["behavioral_eval"]["judge"]["kind"] = "llm"
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertEqual(
            caught.exception.path,
            "$.behavioral_eval.judge.calibration_evidence_ids",
        )

    def test_secret_or_data_exfiltration_is_a_veto(self):
        payload = base_payload()
        self.add_active_gate(payload, "secret-or-data-exfiltration")
        result = self.compute(payload)
        self.assertEqual(result["scores"], {"raw_quality": 90, "publish_readiness": 39})
        self.assertEqual(result["decision"], "BLOCKED")
        self.assertTrue(result["vetoed"])
        self.assertEqual(result["blocking_gates"], result["active_gates"])

    def test_omitted_gate_scope_defaults_to_all_targets_for_backward_compatibility(self):
        payload = base_payload()
        self.add_active_gate(payload, "secret-or-data-exfiltration")
        result = self.compute(payload)
        self.assertEqual(
            result["active_gates"][0]["affected_targets"],
            sorted(score_review.PUBLISH_THRESHOLDS),
        )
        self.assertEqual(result["blocking_gates"], result["active_gates"])

    def test_out_of_scope_active_gate_is_reported_without_blocking_target(self):
        payload = base_payload()
        payload["publish_target"] = "local-draft"
        self.add_active_gate(payload, "license-or-provenance-breach")
        payload["gates"][0]["affected_targets"] = ["public-marketplace"]
        result = self.compute(payload)
        self.assertEqual(result["decision"], "READY")
        self.assertEqual(result["scores"]["publish_readiness"], 90)
        self.assertEqual(
            result["active_gates"],
            [
                {
                    "affected_targets": ["public-marketplace"],
                    "cap": 39,
                    "id": "license-or-provenance-breach",
                }
            ],
        )
        self.assertEqual(result["blocking_gates"], [])
        self.assertFalse(result["vetoed"])
        self.assertNotIn(
            "license-or-provenance-breach",
            [item["id"] for item in result["applied_caps"]],
        )

    def test_in_scope_active_gate_blocks_selected_target(self):
        payload = base_payload()
        self.add_active_gate(payload, "license-or-provenance-breach")
        payload["gates"][0]["affected_targets"] = ["team-shared", "public-marketplace"]
        result = self.compute(payload)
        self.assertEqual(result["decision"], "BLOCKED")
        self.assertEqual(result["blocking_gates"], result["active_gates"])
        self.assertTrue(result["vetoed"])

    def test_gate_scope_must_not_be_empty(self):
        payload = base_payload()
        self.add_active_gate(payload, "license-or-provenance-breach")
        payload["gates"][0]["affected_targets"] = []
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertEqual(caught.exception.path, "$.gates[0].affected_targets")

    def test_gate_scope_rejects_unknown_target(self):
        payload = base_payload()
        self.add_active_gate(payload, "license-or-provenance-breach")
        payload["gates"][0]["affected_targets"] = ["private-preview"]
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertEqual(caught.exception.path, "$.gates[0].affected_targets[0]")

    def test_gate_scope_rejects_duplicate_targets(self):
        payload = base_payload()
        self.add_active_gate(payload, "license-or-provenance-breach")
        payload["gates"][0]["affected_targets"] = [
            "public-marketplace",
            "public-marketplace",
        ]
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertEqual(caught.exception.path, "$.gates[0].affected_targets")

    def test_dangerous_trigger_overreach_is_a_veto(self):
        payload = base_payload()
        self.add_active_gate(payload, "dangerous-trigger-overreach")
        self.assertEqual(self.compute(payload)["decision"], "BLOCKED")

    def test_untrusted_instruction_execution_is_a_veto(self):
        payload = base_payload()
        self.add_active_gate(payload, "untrusted-instruction-execution")
        self.assertEqual(self.compute(payload)["decision"], "BLOCKED")

    def test_unauthorized_side_effect_is_a_veto(self):
        payload = base_payload()
        self.add_active_gate(payload, "unauthorized-side-effect")
        self.assertEqual(self.compute(payload)["decision"], "BLOCKED")

    def test_uncontrolled_code_execution_is_a_veto(self):
        payload = base_payload()
        self.add_active_gate(payload, "uncontrolled-code-execution")
        self.assertEqual(self.compute(payload)["decision"], "BLOCKED")

    def test_hidden_network_or_telemetry_is_a_veto(self):
        payload = base_payload()
        self.add_active_gate(payload, "hidden-network-or-telemetry")
        self.assertEqual(self.compute(payload)["decision"], "BLOCKED")

    def test_fabricated_success_or_evidence_is_a_veto(self):
        payload = base_payload()
        self.add_active_gate(payload, "fabricated-success-or-evidence")
        self.assertEqual(self.compute(payload)["decision"], "BLOCKED")

    def test_broken_core_package_is_a_veto(self):
        payload = base_payload()
        self.add_active_gate(payload, "broken-core-package")
        self.assertEqual(self.compute(payload)["decision"], "BLOCKED")

    def test_license_or_provenance_breach_is_a_veto(self):
        payload = base_payload()
        self.add_active_gate(payload, "license-or-provenance-breach")
        self.assertEqual(self.compute(payload)["decision"], "BLOCKED")

    def test_fixed_veto_requires_reproducible_passing_retest(self):
        payload = base_payload()
        payload["gates"] = [
            {
                "id": "untrusted-instruction-execution",
                "state": "fixed",
                "evidence_ids": [],
                "retest_evidence_ids": [],
            }
        ]
        with self.assertRaises(score_review.ValidationError):
            score_review.validate(payload)

    def test_fixed_veto_accepts_reproducible_passing_retest(self):
        payload = base_payload()
        payload["gates"] = [
            {
                "id": "untrusted-instruction-execution",
                "state": "fixed",
                "evidence_ids": [],
                "retest_evidence_ids": ["e-selection"],
            }
        ]
        result = self.compute(payload)
        self.assertEqual(result["decision"], "READY")
        self.assertFalse(result["vetoed"])

    def test_unknown_veto_is_rejected(self):
        payload = base_payload()
        payload["gates"] = [
            {
                "id": "caller-invented-veto",
                "state": "active",
                "evidence_ids": ["e-runtime"],
                "retest_evidence_ids": [],
            }
        ]
        with self.assertRaises(score_review.ValidationError):
            score_review.validate(payload)

    def test_required_failed_publish_check_is_not_ready(self):
        payload = base_payload()
        payload["evidence"].append(
            {
                "id": "e-failure", "kind": "runtime", "result": "fail",
                "reproducible": True, "fresh": True, "lane": "structural",
                "assertion_type": "deterministic",
            }
        )
        payload["publish_checks"] = [
            {
                "id": "clean-install",
                "required": True,
                "status": "fail",
                "evidence_ids": ["e-failure"],
            }
        ]
        self.assertEqual(self.compute(payload)["decision"], "NOT_READY")

    def test_required_unverified_publish_check_is_insufficient_evidence(self):
        payload = base_payload()
        payload["publish_checks"] = [
            {
                "id": "selection-regression",
                "required": True,
                "status": "unverified",
                "evidence_ids": [],
            }
        ]
        self.assertEqual(self.compute(payload)["decision"], "INSUFFICIENT_EVIDENCE")

    def test_optional_publish_gap_yields_ready_with_conditions(self):
        payload = base_payload()
        payload["publish_checks"].append(
            {
                "id": "extra-platform",
                "required": False,
                "status": "unverified",
                "evidence_ids": [],
            }
        )
        self.assertEqual(self.compute(payload)["decision"], "READY_WITH_CONDITIONS")

    def test_weights_must_total_100(self):
        payload = base_payload()
        payload["dimensions"][0]["weight"] = 24
        with self.assertRaises(score_review.ValidationError):
            score_review.validate(payload)

    def test_boolean_is_not_an_integer_score(self):
        payload = base_payload()
        payload["dimensions"][0]["score"] = True
        with self.assertRaises(score_review.ValidationError):
            score_review.validate(payload)

    def test_verified_dimension_rejects_claim_only_evidence(self):
        payload = base_payload()
        payload["evidence"].append(
            {
                "id": "e-claim", "kind": "claim", "result": "pass",
                "reproducible": True, "fresh": True, "lane": "structural",
                "assertion_type": "not-applicable",
            }
        )
        payload["dimensions"][0]["evidence_ids"] = ["e-claim"]
        with self.assertRaises(score_review.ValidationError):
            score_review.validate(payload)

    def test_full_runtime_coverage_requires_runtime_evidence(self):
        payload = base_payload()
        payload["coverage"]["runtime"]["evidence_ids"] = []
        with self.assertRaises(score_review.ValidationError):
            score_review.validate(payload)

    def test_runtime_coverage_rejects_stale_execution_evidence(self):
        payload = base_payload()
        next(item for item in payload["evidence"] if item["id"] == "e-runtime")["fresh"] = False
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertEqual(caught.exception.path, "$.coverage.runtime.evidence_ids")

    def test_tested_selection_coverage_requires_selection_evidence(self):
        payload = base_payload()
        payload["coverage"]["selection"]["evidence_ids"] = []
        with self.assertRaises(score_review.ValidationError):
            score_review.validate(payload)

    def test_selection_coverage_rejects_stale_discovery_evidence(self):
        payload = base_payload()
        next(item for item in payload["evidence"] if item["id"] == "e-selection")["fresh"] = False
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertEqual(caught.exception.path, "$.coverage.selection.evidence_ids")

    def test_tested_cold_install_coverage_requires_install_evidence(self):
        payload = base_payload()
        payload["coverage"]["cold_install"]["evidence_ids"] = []
        with self.assertRaises(score_review.ValidationError):
            score_review.validate(payload)

    def test_cold_install_coverage_rejects_stale_install_evidence(self):
        payload = base_payload()
        next(item for item in payload["evidence"] if item["id"] == "e-install")["fresh"] = False
        with self.assertRaises(score_review.ValidationError) as caught:
            score_review.validate(payload)
        self.assertEqual(caught.exception.path, "$.coverage.cold_install.evidence_ids")

    def test_resolved_references_require_reference_evidence(self):
        payload = base_payload()
        payload["coverage"]["required_references"]["evidence_ids"] = []
        with self.assertRaises(score_review.ValidationError):
            score_review.validate(payload)

    def test_unknown_root_field_is_rejected(self):
        payload = base_payload()
        payload["surprise"] = True
        with self.assertRaises(score_review.ValidationError):
            score_review.validate(payload)

    def test_duplicate_evidence_id_is_rejected(self):
        payload = base_payload()
        payload["evidence"].append(copy.deepcopy(payload["evidence"][0]))
        with self.assertRaises(score_review.ValidationError):
            score_review.validate(payload)

    def test_input_order_does_not_change_output(self):
        payload = base_payload()
        first = score_review.render(self.compute(payload), pretty=False)
        reordered = copy.deepcopy(payload)
        reordered["dimensions"].reverse()
        reordered["evidence"].reverse()
        reordered["coverage"]["required_references"]["evidence_ids"].reverse()
        second = score_review.render(self.compute(reordered), pretty=False)
        self.assertEqual(first, second)

    def test_cli_success_uses_stdout_only(self):
        result = self.run_cli(json.dumps(base_payload()))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertTrue(json.loads(result.stdout)["ok"])

    def test_cli_invalid_json_exits_one_and_uses_stderr(self):
        result = self.run_cli("{not-json")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertEqual(json.loads(result.stderr)["error"]["code"], "validation_error")

    def test_cli_argument_error_exits_two(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--unknown"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertEqual(json.loads(result.stderr)["error"]["code"], "argument_error")


if __name__ == "__main__":
    unittest.main()
