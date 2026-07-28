# Artifact-grounded concept-probe generator

Load this only after the oral-defense protocol begins question generation. Generate probes from the reviewed artifact rather than choosing from a fixed curriculum.

## Probe interface

```text
Probe = {
  artifact_fact: exact observed path, instruction, dependency, boundary, or behavior,
  design_decision: the author's choice or tradeoff exposed by that fact,
  failure_consequence: a concrete user, platform, safety, or maintenance outcome,
  verification_path: the test, trace, comparison, or inspection that would decide the claim
}
```

Turn one `Probe` into one scenario question that requires the author to connect all four fields. Keep the artifact fact visible enough to answer without guessing, but do not reveal the conclusion or preferred fix.

## Generation rules

1. Inventory verified facts and material unknowns from the current artifact.
2. Select facts whose design choice can change a real outcome.
3. State a plausible failure consequence without asserting it occurred unless evidence shows it.
4. Ask how the author would verify or falsify the claimed behavior.
5. Prefer different boundaries across three to five probes; do not force topic coverage that the artifact does not contain.
6. Reject trivia, terminology recall, and generic questions answerable without inspecting this artifact.

Use a follow-up only to distinguish causal understanding from memorized vocabulary, such as by changing one precondition or asking what evidence would reverse the answer.
