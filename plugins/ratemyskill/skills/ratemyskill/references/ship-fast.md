# Quick skill check

Use this when the user chooses the local-draft quick check. Find the shortest defensible path from “the files exist” to “this is safe and useful for the next test.” Do not turn it into a prompt-writing tutorial or public-marketplace checklist.

## High-yield sequence

1. State the skill job and trigger boundary in one sentence each.
2. Validate the canonical `SKILL.md`, direct references, metadata, and any executable resource used by the core path.
3. Try one intended prompt and one shared-keyword near miss.
4. Run one representative task and compare the obvious baseline when feasible.
5. Test one missing-input or tool-failure path.
6. Inspect authority, untrusted-content, secret, side-effect, network, and dependency instructions before executing anything.
7. Stop when the top blockers and their acceptance tests are clear.

## Priority order

Spend review time in this order:

1. exfiltration, authority bypass, hidden side effects, unsafe execution, fabricated success
2. a broken canonical path, missing required file, or failure to perform the promised task
3. dangerous over-triggering or silent failure to trigger on the core job
4. no measurable improvement over the base agent
5. excess context, maintenance drift, and listing friction

Do not add low-impact wording notes while a higher-order failure remains unresolved.

## Compact output

Return:

```text
Requested target: local draft
Maximum safe target:
Decision:
Discovery signal:
Execution signal:
Top blockers: at most 3
Fastest actions: at most 3
Acceptance checks:
What remains unverified:
```

Quick does not mean lenient. Activate any verified safety veto and label missing evidence honestly.
