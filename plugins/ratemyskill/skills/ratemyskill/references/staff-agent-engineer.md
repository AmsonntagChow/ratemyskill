# Staff agent-engineer review

Review the skill as a behavioral system: selection metadata, loaded instructions, conditional references, executable resources, host tools, and observable outputs.

## Discovery architecture

- Front-load the primary job and discriminating trigger terms.
- Name important synonyms without turning the description into “use for everything.”
- State adjacent jobs that should not trigger when confusion is plausible.
- Keep explicit invocation tests separate from implicit matching.
- Test conflicts with neighboring skills when the catalog contains them.

Description length alone is not quality. Prefer the smallest boundary that maintains recall without sacrificing precision.

## Progressive disclosure

Check that:

1. the main file contains only routing, invariants, and the core workflow
2. detailed variants live one reference hop away
3. every reference and script is reachable from the main file with a clear read/run condition
4. filenames and relative paths work on case-sensitive systems
5. instructions do not duplicate the same source of truth across files
6. large references include navigation or targeted search guidance

Measure the loaded context needed for a representative task. Do not demand references when the workflow is genuinely small.

## Instruction architecture

- Use imperative actions and explicit decision points where behavior is fragile.
- Give exact sequences only for steps where variation creates risk.
- Keep platform-specific rules scoped to their platform.
- Distinguish user authority, agent judgment, and deterministic validation.
- Define completion, evidence, and failure behavior.
- Avoid relying on hidden conversation context or the author's private conventions.

Search for contradictions between the description, body, references, metadata, and package listing.

## Scripts and tools

For each executable resource, establish:

- purpose and whether a script is justified over instructions
- standard-library or declared dependency surface
- input validation and actionable non-zero failures
- deterministic behavior for the same logical input
- path resolution independent of caller working directory
- bounded output and no secret leakage
- tests for high-risk or repeatedly reused logic
- platform portability or an explicit compatibility declaration

Do not execute an unknown script before inspecting it. Use a disposable environment for code that installs packages, writes files, invokes a shell, or uses the network.

## Maintainability and change safety

Check canonical versus packaged copies, version synchronization, validation in CI, trigger and execution eval separation, and a same-rubric re-review path. Penalize needless machinery only when it creates measurable cost or drift risk.
