# Numeric scoring

Read this reference only when the user asks for a numeric grade, comparison, or release score. The qualitative evidence and verdict contract remains in `references/review-contract.md`.

## Contents

- [Default rubric](#default-rubric)
- [Score anchors](#score-anchors)
- [Scorecard interface](#scorecard-interface)
- [Evidence lanes and behavioral run](#evidence-lanes-and-behavioral-run)
- [Target-required checks](#target-required-checks)
- [Gate scopes](#gate-scopes)
- [Run the scorer](#run-the-scorer)
- [Caps and output](#caps-and-output)
- [Rubric fingerprint](#rubric-fingerprint)

## Default rubric

Use these weights unless the selected role justifies a declared redistribution. Weights must total 100. Explain an inapplicable dimension and redistribute before scoring.

| Dimension | Weight | Credit |
|---|---:|---|
| Discovery and routing | 20 | Intended requests select; near misses do not; ambiguity fails safely. |
| Task outcome correctness | 25 | Representative results reliably improve over an equal baseline. |
| Failure handling and recovery | 10 | Missing input, unavailable tools, partial failure, retry, and resume are safe. |
| Progressive disclosure and context efficiency | 10 | The right instructions load when needed without duplication. |
| References, scripts, tools, and portability | 10 | Resources are reachable, tested, justified, path-safe, and host-compatible. |
| Safety and supply chain | 15 | Authority, trust, secrets, effects, network, telemetry, and dependencies are controlled. |
| Marketplace and OSS readiness | 10 | Package, listing, version, license, support, and claims are accurate. |

Do not penalize a skill for omitting scripts, MCP, assets, or references its job does not need.

## Score anchors

Score each dimension from 0 to 100:

- `90–100`: independently verified, repeatable, and appropriate for the target
- `75–89`: credible with bounded conditions or minor gaps
- `60–74`: useful for a narrower target; material risks remain
- `40–59`: fragile, substantially unverified, or missing a critical property
- `0–39`: broken, misleading, unsafe, or behaviorally worthless in this dimension

The raw score is the weighted quality estimate. Readiness also applies evidence confidence, distribution requirements, target-scoped vetoes, and target threshold.

## Scorecard interface

```text
Scorecard = {
  schema_version: "2",
  mode: skill-user | staff-agent-engineer | agent-engineer | red-team |
        adversarial | marketplace-curator | oral-defense,
  rubric_id: non_empty_string,
  publish_target: PublishTarget,
  dimensions: Dimension[1..32],
  evidence: Evidence[0..512],
  evidence_panel: EvidencePanel,
  behavioral_eval: BehavioralEval,
  coverage: Coverage,
  gates: Gate[],
  publish_checks: PublishCheck[1..]
}

PublishTarget = local-draft | team-shared | public-marketplace |
                privileged-production | high-stakes

Dimension = {
  id: unique_non_empty_string,
  weight: integer_1_to_100,
  score: integer_0_to_100,
  verification: verified | partial | unverified,
  evidence_ids: unique_existing_evidence_ids
}

Evidence = {
  id: unique_non_empty_string,
  kind: runtime | test | install | static-analysis | manifest | reference |
        dependency | log | trace | document | claim,
  result: pass | fail | mixed | inconclusive,
  reproducible: boolean,
  fresh: boolean,
  lane: structural | deterministic-checks | critical-journey-e2e |
        probabilistic-eval | continuous-evidence,
  assertion_type: deterministic | probabilistic | mixed | not-applicable
}

Coverage = {
  runtime: {level: full | partial | static | none, evidence_ids},
  selection: {level: tested | partial | claimed | none, evidence_ids},
  cold_install: {level: tested | partial | claimed | none, evidence_ids},
  required_references: {total, resolved, evidence_ids}
}

Gate = canonical Gate from references/review-contract.md

PublishCheck = {
  id: unique_non_empty_string,
  required: boolean,
  status: pass | fail | unverified,
  evidence_ids
}
```

Unknown fields, duplicate IDs, missing evidence links, non-integer scores, empty required arrays, or weights not totaling 100 are invalid. `verified` needs reproducible non-claim evidence; `partial` needs at least one evidence ID.

Schema v2 is fail-closed and intentionally does not infer new evidence lanes from a v1 scorecard. To migrate v1, set `schema_version` to `"2"`; add `lane` and `assertion_type` to every evidence item; add the complete four-lane `evidence_panel`; and add either a recorded `behavioral_eval` or `{status: unverified, evidence_ids: []}`. Re-run evidence rather than marking old results fresh by default.

Runtime, selection, install, resolved-reference, passing-check, failing-check, active-gate, and fixed-gate states each require the evidence kind and freshness enforced by the scorer. Do not upgrade a claim into executable or independently reproduced evidence.

## Evidence lanes and behavioral run

```text
EvidencePanel = {
  deterministic-checks: Lane,
  critical-journey-e2e: Lane,
  probabilistic-eval: Lane,
  continuous-evidence: Lane
}

Lane = {
  status: pass | fail | unverified | not-applicable,
  evidence_ids: unique_existing_same_lane_evidence_ids
}
```

Render lane statuses as `PASS`, `FAIL`, `UNVERIFIED`, and `N/A`. The panel must list every evidence item assigned to each non-structural lane. `pass` accepts only fresh reproducible pass results; any fail or mixed result makes the lane fail, while inconclusive evidence prevents a pass. `unverified` and `not-applicable` carry no evidence. Repository CI, schema checks, manifests, and eval-file validation use the `structural` lane and cannot prove runtime, selection, or another behavioral lane.

Required lanes by target:

| Target | Required evidence-panel lanes |
|---|---|
| `local-draft` | None enforced by the numeric panel; apply the qualitative minimum-task contract |
| `team-shared`, `public-marketplace` | deterministic checks, critical-journey E2E, probabilistic eval |
| `privileged-production`, `high-stakes` | all four lanes |

A required `unverified` or `not-applicable` lane appears in `evidence_panel_gaps` and `distribution_evidence_gaps`, producing `INSUFFICIENT_EVIDENCE`. Runtime coverage accepts only critical-journey evidence; selection coverage accepts only probabilistic-eval evidence. Structural checks may still prove install, reference, manifest, or package facts.

Use the short form when no run exists:

```text
BehavioralEval = {status: unverified, evidence_ids: []}
```

A recorded summary uses `status: recorded` and adds: `definition_id`, `run_id`, `package_sha256`, `host`, `model`, `skill_or_prompt_sha256`, `dataset_id`, `rubric_id`, `variance_policy`, fresh `probabilistic-eval` evidence IDs, and these objects:

```text
judge = {kind: deterministic | llm, id, version, calibration_evidence_ids}
selection = {
  runs_per_case, positive_trials, positive_hits,
  near_miss_trials, false_triggers,
  minimum_hit_rate_percent, maximum_false_trigger_rate_percent
}
execution = {
  runs_per_arm, with_skill_passes, without_skill_passes,
  minimum_uplift_points
}
```

The scorer calculates hit rate, false-trigger rate, and uplift. Use equal execution arms. Trial counts must be divisible by `runs_per_case`; the declared minimum hit rate must exceed the maximum false-trigger rate; the endpoints 0% minimum hit and 100% maximum false trigger are invalid; and minimum uplift must be positive. These are non-vacuous bounds, not universal product quotas. Prefer a deterministic judge; an LLM judge requires fresh passing calibration evidence and a stable ID and version. `team-shared` and higher require the recorded summary, not merely trigger and execution JSON files.

## Target-required checks

Every listed target check must appear with `required: true`.

| Target | Check ID | Passing evidence kind | Required lane |
|---|---|---|---|
| `privileged-production` | `sandboxed-authority-and-side-effects` | fresh reproducible runtime, test, or trace | critical-journey E2E |
| `high-stakes` | all privileged checks | same as above | critical-journey E2E |
| `high-stakes` | `independent-domain-review` | fresh reproducible document or test | deterministic checks |
| `high-stakes` | `human-control` | fresh reproducible runtime, test, or trace | critical-journey E2E |
| `high-stakes` | `auditability` | fresh reproducible runtime, test, log, or trace | continuous evidence |
| `high-stakes` | `incident-response` | fresh reproducible runtime, test, document, or trace | critical-journey E2E or continuous evidence |

A missing or mislabeled target check invalidates the scorecard. `unverified` yields insufficient evidence; `fail` yields not ready unless a blocking veto takes precedence.

## Gate scopes

Use veto IDs and activation evidence from `references/review-contract.md`. `affected_targets` is optional for backward compatibility. When omitted, the scorer expands it to every `PublishTarget`. When present, it must be a non-empty array of unique valid targets.

The scorer returns every active gate with its normalized `affected_targets` in `active_gates`. It also returns `blocking_gates`, the subset affecting the scorecard's `publish_target`. Only `blocking_gates` add safety caps, set `vetoed: true`, or force `BLOCKED`. An out-of-scope active gate remains visible but does not change the selected target's score or decision.

## Run the scorer

Resolve the script from the directory containing `SKILL.md`, then run:

```bash
python3 <skill-directory>/scripts/score_review.py path/to/scorecard.json
```

Use `--pretty` for indented deterministic JSON. The script uses only the Python standard library, reads at most 1 MiB, rejects non-finite values, writes success JSON to stdout, writes error JSON to stderr, and returns non-zero on invalid input.

## Caps and output

The result keeps `scores.raw_quality` separate from `scores.publish_readiness`. Any failed evidence-panel lane yields `NOT_READY`. Readiness is the minimum of raw quality and applicable caps:

- evidence-confidence cap: `A=100`, `B=89`, `C=69`, `D=49`
- missing team runtime, selection, recorded behavioral summary, or required panel lane: `64`
- missing public-or-higher runtime, selection, clean-install, required-reference, recorded behavioral summary, or required panel lane: `69`
- each blocking veto: `39`

The output includes normalized active and blocking gate scopes, applied caps, coverage confidence, evidence-panel failures and gaps, distribution evidence gaps, publish-check results, target threshold, decision, and `vetoed`. Follow the decision order in `references/review-contract.md`; do not reinterpret the JSON to waive a gate.

## Rubric fingerprint

The scorer hashes the rubric ID, mode, publish target, and sorted dimension IDs and weights. Preserve the fingerprint inputs during re-review. A changed fingerprint means the before-and-after numeric delta is not a same-rubric comparison, even when both results are valid.
