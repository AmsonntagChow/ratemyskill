# Quick skill check

Use this when the user chooses the local-draft quick check. Find the shortest defensible path from “the files exist” to “this is safe and useful for the next test.” Do not turn it into a prompt-writing tutorial or public-marketplace checklist.

## High-yield sequence

1. State the skill job and trigger boundary in one sentence each.
2. Validate the canonical `SKILL.md`, direct references, metadata, and any executable resource used by the core path.
3. If testing discovery, read `references/evaluation.md`, then try one intended prompt and one shared-keyword near miss.
4. If comparing task behavior, read `references/evaluation.md`, then run one representative equal-arm comparison when feasible.
5. Test one missing-input or tool-failure path.
6. Inspect authority, untrusted-content, secret, side-effect, network, and dependency instructions before executing anything.
7. Stop when the highest-priority review scope and its acceptance tests are clear, then report every issue verified within that scope.

## Priority order

Spend review time in this order:

1. exfiltration, authority bypass, hidden side effects, unsafe execution, fabricated success
2. a broken canonical path, missing required file, or failure to perform the promised task
3. dangerous over-triggering or silent failure to trigger on the core job
4. no measurable improvement over the base agent
5. excess context, maintenance drift, and listing friction

Do not add low-impact wording notes while a higher-order failure remains unresolved.

## Completion

Quick does not mean lenient. The scope may be narrow, but report every issue verified within it and keep missing proof as unknown. Render the single canonical `Verdict` and apply veto scope and decision order from `references/review-contract.md`; do not define a second quick-mode output or scoring format here.
