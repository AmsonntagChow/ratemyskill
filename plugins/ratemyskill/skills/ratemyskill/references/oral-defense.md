# Author oral defense

Use this only when the user chooses the defense-professor role or explicitly asks to be questioned. Evaluate the author's understanding separately from independently verified skill quality.

## Protocol

1. Inspect the artifact only after role and degree are confirmed.
2. When question generation begins, read `references/concept-probes.md` and generate three to five probes from risks or design decisions actually present.
3. Ask exactly one question at a time and wait for the answer.
4. Use a concrete scenario, prompt, path, tool, or failure from the artifact.
5. Ask a follow-up only when it distinguishes understanding from memorized vocabulary.
6. Score understanding after the final answer; do not rewrite the verified skill verdict.

Do not load the probe generator during initial routing or inventory. Avoid trivia such as definitions of “prompt injection” unless that concept explains a reachable risk in this skill.

## Understanding score

Score each answer qualitatively:

- `STRONG`: explains the artifact behavior, failure consequence, and verification path
- `PARTIAL`: recognizes the concept but misses an artifact-specific edge or evidence requirement
- `WEAK`: gives generic vocabulary, contradicts the artifact, or invents a guarantee
- `UNANSWERED`: insufficient response to assess

Report author understanding independently. A weak answer does not make a verified safe skill unsafe, and a fluent answer does not repair an unsafe package.
