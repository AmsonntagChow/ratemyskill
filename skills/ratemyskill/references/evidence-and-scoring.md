# Evidence, scoring, and distribution decisions

Use this protocol in every mode. The score describes skill quality; the distribution decision also depends on evidence, required checks, and fixed vetoes.

## Distribution ladder

| Target | Minimum evidence expected | Default readiness threshold |
|---|---|---:|
| Local draft | Structural validation and one representative task in a controlled environment | 50 |
| Team shared | Fresh-agent task execution, positive and near-miss selection tests, failure handling, and removal path | 65 |
| Public marketplace | Clean package install, repeated discovery tests, with/without execution evidence, safety review, and public trust materials | 75 |
| Privileged production | Tool and data-flow tests, least authority, isolation, audit trail, recovery, and incident ownership | 85 |
| High stakes | Independent domain review, human control, compliance evidence, change approval, and incident exercises | 90 |

These thresholds are calibration points, not universal laws. State any adjustment before scoring and never lower a threshold to turn an observed failure into a pass.

Apply these evidence ceilings:

- Static reading alone supports at most `local-draft`.
- Without a fresh-agent execution, do not approve `team-shared` or higher.
- Without independent implicit-selection tests, do not approve automatic-discovery claims or `public-marketplace`.
- Without a clean install of the final artifact, do not approve `public-marketplace` packaging.
- Without sandboxed authority and side-effect tests, do not approve `privileged-production`.
- Without domain experts, human control, auditability, and incident response, do not approve `high-stakes`.

Missing evidence is not proof of a defect. Preserve raw quality, cap maximum safe distribution, and name the smallest test that can raise the ceiling.

The deterministic scorer enforces these target-specific publish-check IDs:

| Target | Required `publish_checks[].id` | Passing evidence kind |
|---|---|---|
| Privileged production | `sandboxed-authority-and-side-effects` | Fresh reproducible runtime, test, or trace evidence |
| High stakes | `independent-domain-review` | Fresh reproducible document or test evidence |
| High stakes | `human-control` | Fresh reproducible runtime, test, or trace evidence |
| High stakes | `auditability` | Fresh reproducible runtime, test, log, or trace evidence |
| High stakes | `incident-response` | Fresh reproducible runtime, test, document, or trace evidence |

Every target-required check must set `required: true`. A missing or mislabeled check makes the scorecard invalid; `unverified` produces `INSUFFICIENT_EVIDENCE`; `fail` produces `NOT READY`. Do not relabel public-marketplace installation evidence as privileged or high-stakes evidence.

## Evidence levels

| Level | Meaning | Examples |
|---|---|---|
| E3 — clean-room reproduced | Behavior repeats with a fresh agent, clean install, original request, and controlled artifact | repeated discovery trial, isolated with/without task run, cold-install execution |
| E2 — machine instrumented | Independent machine-produced support | validator, test output, install log, trace, file-state diff, archive listing |
| E1 — static fact | Concrete text, path, code, metadata, or package fact; runtime consequence may remain inferred | missing referenced file, unconditional unsafe instruction, undeclared import |
| E0 — claim or guess | Author statement, README claim, generic concern, or unavailable evidence | “works in every client,” “probably safe,” reviewer speculation |

Keep severity independent from evidence strength. An E1 instruction to transmit secrets is a verified unsafe artifact fact even if a particular host may refuse it. State exactly which fact is proven and which runtime consequence remains inferred. When executing a suspected path would itself cause harm, complete static proof can block release without a live destructive test.

## Closed-loop finding

Use this schema:

```text
[S-###] [BLOCKER|HIGH|MEDIUM|LOW] Short title
Advertised contract:
Platform and distribution target:
Preconditions:
Fresh-agent prompt or exact steps:
Expected:
Actual:
Evidence: E# — exact artifact or observation
Impact:
Suspected cause: explicitly mark inference
Minimum fix:
Acceptance test:
Adjacent negative or regression test:
```

“Improve the prompt,” “add tests,” or “this may over-trigger” is not a closed finding until it is tied to an observable boundary and consequence.

## Default rubric

Use this weighting unless the selected role justifies a declared adjustment. If a dimension is inapplicable, explain why and redistribute its weight before scoring.

| Dimension | Weight | What earns credit |
|---|---:|---|
| Discovery and routing | 20 | Intended prompts select the skill; shared-keyword near misses do not; ambiguous cases fail safely |
| Task outcome correctness | 25 | The skill reliably improves representative task results over the baseline |
| Failure handling and recovery | 10 | Missing inputs, unavailable tools, partial failure, retry, and resume are explicit and safe |
| Progressive disclosure and context efficiency | 10 | The right instructions load at the right time without duplication or unnecessary context |
| References, scripts, tools, and portability | 10 | Resources are reachable, tested, justified, path-safe, and compatible with declared hosts |
| Safety and supply chain | 15 | Authority, trust, secrets, side effects, network, telemetry, and dependencies are controlled |
| Marketplace and OSS readiness | 10 | Final package, listing, versioning, license, support, and public claims are accurate |

Score each dimension from 0–100:

- 90–100: independently verified, repeatable, and appropriate for the target
- 75–89: credible with bounded conditions or minor gaps
- 60–74: useful for a narrower target; material risks remain
- 40–59: fragile, substantially unverified, or missing a critical property
- 0–39: broken, misleading, unsafe, or behaviorally worthless in this dimension

Do not penalize a skill for lacking scripts, MCP, assets, or multiple references when its job does not need them.

## Discovery coverage

Report implicit and explicit invocation separately. A public-release discovery suite should normally include at least ten positives, ten shared-keyword near-miss negatives, ambiguous cases, repeated trials, and relevant competing skills. At least half of positive holdouts should avoid the skill name and exact frontmatter wording.

Report positive trigger rate, false-trigger rate, route accuracy, ambiguous-request safety, and collision rate when available. An 80% positive trigger rate and no more than 10% false triggers can be useful initial calibration, but they are not universal pass laws. Dangerous ambiguous prompts must never auto-execute privileged behavior.

## Execution differential

After discovery testing, use explicit invocation to compare `with_skill` and `without_skill` arms. Keep request, artifact, tools, permissions, model, and stopping condition constant. Use fresh contexts and hidden task-specific assertions. Drop assertions both arms always pass.

Report task success, safety violations, evidence quality, tool choice, user effort, elapsed time, and token or context cost when available. Directory validity is not evidence of behavioral value.

## Fixed vetoes

The following verified conditions block the affected target regardless of weighted score:

- `dangerous-trigger-overreach`
- `untrusted-instruction-execution`
- `unauthorized-side-effect`
- `secret-or-data-exfiltration`
- `uncontrolled-code-execution`
- `hidden-network-or-telemetry`
- `fabricated-success-or-evidence`
- `broken-core-package`
- `license-or-provenance-breach`

Do not waive a veto inside a scorecard. It remains active until a same-path retest supplies adequate passing evidence. A user may accept risk, but acceptance does not convert a verified condition into a technical pass.

Decision naming is fixed: one or more active vetoes always produces `BLOCKED`. Use `NOT READY` only for verified release failure without an active veto, and `INSUFFICIENT EVIDENCE` only when required proof is missing without a verified blocker. Call vetoes `active` until a fresh passing retest supports `fixed`.

## Scorecard and deterministic scorer

Create a JSON scorecard and run `scripts/score_review.py`. Preserve raw quality separately from evidence-limited readiness. The scorer validates evidence links, weights, fixed gate names, target requirements, and a rubric fingerprint for re-review.

Minimal shape:

```json
{
  "schema_version": "1",
  "mode": "staff-agent-engineer",
  "rubric_id": "ratemyskill/default-v1",
  "publish_target": "public-marketplace",
  "dimensions": [
    {
      "id": "overall",
      "weight": 100,
      "score": 70,
      "verification": "partial",
      "evidence_ids": ["e-runtime", "e-selection", "e-install", "e-references"]
    }
  ],
  "evidence": [
    {
      "id": "e-runtime",
      "kind": "runtime",
      "result": "mixed",
      "reproducible": true,
      "fresh": true
    },
    {
      "id": "e-selection",
      "kind": "test",
      "result": "mixed",
      "reproducible": true,
      "fresh": true
    },
    {
      "id": "e-install",
      "kind": "install",
      "result": "pass",
      "reproducible": true,
      "fresh": true
    },
    {
      "id": "e-references",
      "kind": "reference",
      "result": "pass",
      "reproducible": true,
      "fresh": true
    }
  ],
  "coverage": {
    "runtime": {"level": "partial", "evidence_ids": ["e-runtime"]},
    "selection": {"level": "partial", "evidence_ids": ["e-selection"]},
    "cold_install": {"level": "tested", "evidence_ids": ["e-install"]},
    "required_references": {"total": 8, "resolved": 8, "evidence_ids": ["e-references"]}
  },
  "gates": [],
  "publish_checks": [
    {
      "id": "final-package-cold-install",
      "required": true,
      "status": "pass",
      "evidence_ids": ["e-install"]
    }
  ]
}
```

The example is valid but compresses the selected rubric into one dimension. A real review should use the seven default dimensions or a declared role-specific redistribution whose weights total 100. The scorer rejects unknown fields and missing evidence IDs.

## Re-review

Preserve rubric ID, platform, model, skill version, target, dimension IDs and weights, trigger cases, original artifacts, assertions, and finding IDs. Re-run the original failures, neighboring negatives, cold install, authority boundaries, and execution tasks. Show raw-quality, discovery, execution, and readiness deltas separately.
