# Review contract

Load this contract for every review mode. It is the sole source for distribution ceilings, evidence states, findings, verdict presentation, veto activation, decision order, and re-review identity.

## Contents

- [Distribution ladder](#distribution-ladder)
- [Evidence states](#evidence-states)
- [Evidence panel](#evidence-panel)
- [Canonical interfaces](#canonical-interfaces)
- [Veto contract](#veto-contract)
- [Decision order](#decision-order)
- [Re-review identity](#re-review-identity)

## Distribution ladder

| Target | Minimum evidence | Default numeric threshold |
|---|---|---:|
| `local-draft` | Structural validation and one representative controlled task | 50 |
| `team-shared` | Fresh-agent execution, repeated positive and near-miss selection, a recorded behavioral-eval summary, failure handling, and removal path | 65 |
| `public-marketplace` | Clean install of the final digest, repeated discovery, recorded with/without uplift, safety review, and public trust materials | 75 |
| `privileged-production` | Tool and data-flow tests, least authority, isolation, audit trail, recovery, and incident ownership | 85 |
| `high-stakes` | Independent domain review, human control, compliance evidence, change approval, and incident exercises | 90 |

Apply these ceilings regardless of prose quality:

- Static reading alone supports at most `local-draft`.
- Without fresh-agent execution, do not approve `team-shared` or higher.
- Eval definitions, repository tests, and valid JSON are structural evidence only. Without a fresh recorded behavioral-eval summary, do not approve `team-shared` or higher.
- Without independent implicit-selection tests or a clean install of the final artifact digest, do not approve `public-marketplace`.
- Without sandboxed authority and side-effect tests, do not approve `privileged-production`.
- Without domain review, human control, auditability, and incident response, do not approve `high-stakes`.

Missing evidence is an unknown, not a defect. Preserve raw quality, cap maximum safe distribution, and name the smallest test that can raise the ceiling.

When even `local-draft` is unsupported, report `no supported distribution tier` rather than inventing a lower target.

## Evidence states

| State | Meaning |
|---|---|
| `E3 clean-room reproduced` | Behavior repeats with a fresh agent or clean install, the original request, and a controlled artifact. |
| `E2 machine-instrumented` | A validator, test, trace, install log, archive listing, or file-state diff independently supports the result. |
| `E1 static fact` | Exact text, code, path, metadata, or package state is observed; runtime consequence may remain inferred. |
| `E0 claim or hypothesis` | Author claim, generic concern, unavailable proof, or reviewer speculation. |

Keep severity independent from evidence strength. State the proven fact separately from inferred consequences. When exercising a path would itself be harmful, exact static proof of the unsafe artifact fact can block release without a destructive live test.

Calibrate severity by consequence: `BLOCKER` means an active veto or the target's core job is unsafe or impossible; `HIGH` means material workflow, user, data, or release harm; `MEDIUM` means a bounded but real contract failure; `LOW` means limited impact with a concrete user or maintainer consequence.

## Evidence panel

Keep these four lanes separate and render their statuses as `PASS`, `FAIL`, `UNVERIFIED`, or `N/A`:

| Lane | What it proves |
|---|---|
| `deterministic-checks` | Exact validators and assertions pass. |
| `critical-journey-e2e` | One or two representative user journeys complete across their real boundary. |
| `probabilistic-eval` | Repeated discovery and with/without behavior meet declared thresholds. |
| `continuous-evidence` | The same contract remains healthy after release. |

Evidence may support only its own lane; never let green repository CI, JSON validation, one E2E run, or online monitoring substitute for a missing lane. Every non-structural evidence item must appear in its declared panel lane. A `PASS` lane contains only fresh reproducible passing evidence; any fail or mixed result makes it `FAIL`, and an inconclusive result keeps it from passing. Use `N/A` only when the lane is genuinely outside the artifact's contract, not when nobody ran it.

For `team-shared` and `public-marketplace`, deterministic checks, critical-journey E2E, and probabilistic eval are required. Privileged and high-stakes use also requires continuous evidence. A required lane marked `UNVERIFIED` or `N/A` is an explicit evidence gap and yields `INSUFFICIENT EVIDENCE`; an observed `FAIL` yields `NOT READY`.

## Canonical interfaces

```text
Finding = {
  id: stable S-###,
  severity: BLOCKER | HIGH | MEDIUM | LOW,
  violated_contract_or_invariant,
  platform_and_affected_targets,
  preconditions,
  reproduction_prompt_or_steps,
  expected,
  actual,
  evidence: {id: E-###, state: E1 | E2 | E3, exact_artifact_or_observation}[1..],
  impact,
  suspected_cause: explicitly_labeled_inference,
  minimum_safe_fix,
  acceptance_test,
  adjacent_regression_test
}

Unknown = {
  id: stable_when_carried_from_a_prior_report,
  unresolved_claim,
  missing_evidence,
  why_the_unknown_matters,
  smallest_resolving_test
}

Verdict = {
  issue_index: one_plain_language_line_per_verified_finding,
  unknown_index: one_plain_language_line_per_unknown,
  evidence_panel: the_four_separate_lanes,
  behavioral_eval_summary: recorded_run | unverified,
  requested_distribution,
  maximum_safe_distribution,
  decision,
  numeric_score: optional,
  discovery_quality,
  execution_uplift,
  evidence_coverage,
  confidence,
  active_gates,
  blocking_gates,
  findings,
  unknowns,
  top_actions: at_most_3,
  retest_plan
}
```

A `Finding` is closed only when its observed boundary, consequence, reproduction, fix, and acceptance check are concrete. Start the verdict with `issue_index`, severity-sorted and without a count limit. Each line contains its ID and severity plus one plain-language sentence stating the failure and its consequence; omit fixes, citations, and jargon dumps. Put only unknowns in the separate unknown index, also one sentence each. Render both indexes and their labels in the user's language.

If no issue is verified, state that explicitly and still list remaining unknowns. Use “none” only when no unknown remains. The opening indexes summarize but never replace detailed `Finding` and `Unknown` records. Only `top_actions` is capped.

## Veto contract

Recognized veto IDs are `dangerous-trigger-overreach`, `untrusted-instruction-execution`, `unauthorized-side-effect`, `secret-or-data-exfiltration`, `uncontrolled-code-execution`, `hidden-network-or-telemetry`, `fabricated-success-or-evidence`, `broken-core-package`, and `license-or-provenance-breach`.

```text
Gate = {
  id: recognized_veto_id,
  state: active | fixed,
  evidence_ids: unique E-###[],
  retest_evidence_ids: unique E-###[],
  affected_targets?: nonempty_unique_target_id[]
}
```

A veto is `active` only with reproducible non-claim evidence of a failing or mixed condition. It becomes `fixed` only after fresh reproducible passing evidence on the same path. Risk acceptance does not turn an active condition into a pass.

Each veto declares one or more `affected_targets` from the distribution ladder. Omission means all targets for backward compatibility. Never use an empty list or infer that an explicitly scoped veto applies elsewhere. An active veto caps and blocks only when the requested target is in its affected targets; retain out-of-scope active vetoes in the report so their scope remains visible.

`active_gates` contains every active veto and its normalized scope; `blocking_gates` is the subset affecting the requested distribution target.

## Decision order

Apply the first matching state:

1. active veto affecting the requested target -> `BLOCKED`
2. required check or evidence-panel lane with verified failure -> `NOT READY`
3. required proof missing or distribution ceiling unmet -> `INSUFFICIENT EVIDENCE`
4. required checks pass but numeric threshold fails -> `NOT READY`
5. required checks pass and optional conditions remain -> `READY WITH CONDITIONS`
6. every required check passes for the target -> `READY`

Never call an active veto fixed without its retest, and never label a target-blocking veto merely `NOT READY`.

## Re-review identity

Preserve rubric ID, platform, model, skill version, target, dimension IDs and weights, trigger cases, artifacts, assertions, and finding IDs. Re-run original failures, neighboring negatives, cold install, authority boundaries, and execution tasks as applicable.

Classify every prior finding as `FIXED`, `PARTIALLY FIXED`, `NOT FIXED`, `REGRESSED`, or `UNVERIFIABLE`. Keep the same ID and exact status in the opening indexes; put `UNVERIFIABLE` under unknowns, and do not present `FIXED` as an active issue. Show raw-quality, discovery, execution, and readiness deltas separately.

The same defect class found at a second location is a new finding, not a reopening of the first. Two instances of one flaw carry different reproduction paths and different acceptance tests, so merging them under one ID means fixing the first silently closes the second. Give the second instance its own ID even when the cause is identical, and never renumber or delete an existing finding to make the set look tidier.

Finding the second instance is a separate obligation, and it splits in two. **Extent of condition** asks where else this same defect sits: broad, shallow, usually one re-runnable expression, and it terminates. Run it when the cause is identified and before authorizing a fix, because the count decides the shape of the fix and changes what the user is approving. **Extent of cause** asks what else this same cause produced: narrow, deep, judgment-bound, and it expands without a natural boundary, so reserve it for the degrees where the consequence justifies the cost. Collapsing the two is what turns a bounded sweep into an unbounded one. For a Skill package the classes are concrete: one broken reference means checking every reference in the resource graph, one over-broad trigger phrase means checking every trigger, one script with excess permission means checking every script.

Record a sweep as a re-runnable expression with the scope it covered, never as a prose claim of thoroughness — an expression can be re-run by someone who doubts it. When no expression can enumerate the class, say so and name what was attempted; a class nobody can enumerate is a class nobody can prove closed. A class closes by converting every instance, by a chokepoint that makes the rest unreachable, by a ratchet that freezes the count under enforcement so it can only decrease, or by naming the remainder for explicit user acceptance. Report the remaining count either way, and grade the formality of the sweep by degree rather than skipping it.

A fix batch's re-review also opens the changed surface as fresh audit surface under the same rubric, because fix code is new, written under closure pressure, and audited by no earlier pass. File its defects as new findings with new IDs. That delta audit reads what the batch changed while the class sweep reads what it did not, so neither substitutes for the other and a clean delta audit never implies a clean class.
