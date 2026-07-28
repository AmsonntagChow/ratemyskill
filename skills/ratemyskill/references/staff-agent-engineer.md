# Staff agent-engineer review

Review the skill as a behavioral system: selection metadata, loaded instructions, conditional references, executable resources, host tools, and observable outputs.

## Discovery architecture

- Front-load the primary job and discriminating trigger terms.
- Name useful synonyms without turning the description into a universal catch-all.
- State adjacent jobs that should not trigger when confusion is plausible.
- Keep explicit invocation distinct from implicit matching.
- Test relevant catalog collisions.

Description length alone is not quality. Prefer the smallest boundary that maintains recall without sacrificing precision. Read `references/evaluation.md` only when actually planning or running discovery tests.

## Progressive disclosure

Check that:

1. the main file contains routing, invariants, and the core workflow
2. optional detail is one direct reference hop away and loads only when needed
3. every reference and script is reachable with a clear read or run condition
4. paths work on case-sensitive systems and from caller working directories
5. each contract has one source of truth
6. references over 100 lines have navigation or targeted search guidance

Measure context loaded for representative work. Do not demand references when the workflow is genuinely small.

## Instruction strength

Classify each hard instruction before judging its wording:

| Class | Meaning | Appropriate strength |
|---|---|---|
| Safety invariant | Prevents unauthorized, destructive, deceptive, privacy, or trust-boundary failure | Absolute when the safety boundary truly has no exception |
| Product contract | Defines an explicit user-visible promise, required output, or supported boundary | Absolute only for the promised contract and declared scope |
| Fragile operation | A sequence or parameter must be exact because variation creates a demonstrated operational failure | Absolute or low-freedom procedure for that operation |
| Ordinary heuristic | One useful approach among several context-dependent choices | Prefer guidance, decision criteria, or defaults over absolutes |

Do not count absolute words as defects. File over-constraint only when observed behavior shows an ordinary heuristic blocks a valid task, causes needless questioning or refusal, suppresses a better method, or otherwise violates the contract. Without that behavior evidence, record the suspected consequence as an `Unknown` and propose a discriminating task.

Use imperative steps and exact sequences where fragility warrants them. Keep platform rules scoped, distinguish user authority from agent judgment and deterministic validation, define completion and failure behavior, and search for contradictions across metadata, instructions, references, listings, and packages.

## Examples and anchoring

Classify an example by function:

- A **syntax interface** demonstrates shape, fields, placeholders, or calling convention without prescribing task content.
- A **behavioral anchor** demonstrates concrete domain choices, reasoning, wording, or outcomes that may narrow later behavior.

Neither category is inherently defective. File example anchoring only when controlled behavior shows copying, semantic narrowing, omitted valid variants, or another contract consequence attributable to the example. A concrete example observed only in the file is an artifact fact and, at most, an `Unknown` about runtime anchoring. Test a structurally similar but semantically different case and a no-example or parameterized-interface variant when feasible.

## Scripts and tools

For each executable resource, establish purpose, dependency surface, input validation, actionable non-zero failures, determinism, caller-independent paths, bounded non-secret output, high-risk tests, and platform support. Inspect unknown code first; use a disposable environment for installs, writes, shell execution, or network access.

## Maintainability and change safety

Check canonical and packaged copies, version synchronization, validation in CI, separated discovery and execution evals, recorded runs distinct from definitions, and same-rubric re-review. Treat green schema or repository checks as structural evidence only. Penalize machinery only when it creates observed cost, drift, fragility, or a credible maintainability consequence.
