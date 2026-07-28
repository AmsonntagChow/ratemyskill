# Discovery and execution evaluation

Read this reference only when planning or running discovery, trigger, collision, or with-skill versus without-skill tests.

## Clean-run requirements

- Use fresh contexts and the exact final package digest, not a mutable working tree or an eval definition alone.
- Keep model, user request, files, tools, permissions, environment, and stopping condition equal across comparable trials.
- Do not reveal the rubric, fixture defect, expected answer, intended fix, or the other arm's output.
- Separate train prompts from held-out prompts and remove artifacts left by earlier trials.
- Repeat nondeterministic cases and retain raw prompts, outputs, traces, timings, and failures.
- Label a non-clean comparison as partial evidence and state the contamination.

Classify each assertion before running it:

- `deterministic` — an exact value, schema, file state, exit code, or invariant decides it.
- `probabilistic` — repeated sampled behavior is judged against a threshold.
- `mixed` — deterministic guards surround a probabilistic judgment.

Prefer deterministic assertions whenever they can decide the promised outcome. If an LLM judge is necessary, give it an ID and version, calibrate it against human-checked examples, and retain that calibration evidence.

## Discovery coverage

Test explicit invocation separately from implicit selection. Explicit `$skill-name` or `@skill-name` use proves only that an already-selected skill can run.

Derive positives from the skill's actual jobs. Derive shared-keyword near misses from adjacent jobs it excludes. Include ambiguous requests, catalog collisions, description truncation, missing-input timing, and relevant competing skills.

Choose enough positive and near-miss cases, repetitions, ambiguous prompts, and competing-skill cases to exercise the claimed boundary. Keep a held-out split whose prompts avoid the skill name and copied frontmatter wording. Declare the sample size and variance policy rather than importing a universal case count.

Report:

- positive implicit-selection rate and false-negative cases
- false-trigger rate on near misses
- route accuracy and competing-skill collision rate
- ambiguous-request safety
- explicit invocation separately

Declare minimum hit rate and maximum false-trigger rate before the run. Keep the boundary non-vacuous: minimum hit must exceed maximum false trigger, and neither 0% minimum hit nor 100% allowed false trigger can authorize release. Treat other example values as calibration aids, not universal pass laws. Never allow an ambiguous discovery result to auto-execute privileged behavior.

## Execution differential

After selection testing, use explicit invocation for both arms so discovery noise does not contaminate task quality.

1. Choose common, awkward-but-in-scope, and relevant failure-path tasks.
2. Define hidden task-specific assertions before running either arm.
3. Run `with_skill` and `without_skill` in isolated, otherwise equal contexts.
4. Score task success, safety violations, evidence quality, tool choice, user effort, elapsed time, and token or context cost when available.
5. Drop assertions both arms always satisfy; they do not measure uplift.
6. Require positive uplift and repeat material differences before claiming reliable improvement or regression.

Directory validity, polished instructions, or a single successful demonstration does not establish behavioral value. If only a test design is possible, record execution uplift as unknown rather than pretending the planned comparison ran.

## Recorded behavioral summary

An eval file defines what could be run. A fresh run summary records what actually happened. For `team-shared` and higher, bind one summary to:

- run and definition IDs; final package SHA-256; host and model; Skill-or-prompt SHA-256
- dataset and rubric IDs; judge kind, ID, and version; calibration evidence for an LLM judge
- runs per selection case, positive trials and hits, near-miss trials and false triggers
- equal with-Skill and without-Skill trials and passes, plus observed uplift
- declared hit-rate, false-trigger, and uplift thresholds, and a variance policy
- fresh reproducible evidence IDs from the `probabilistic-eval` lane

Report deterministic checks, critical-journey E2E, probabilistic eval, and continuous evidence separately. A repository validator can confirm that this schema is well formed; it cannot manufacture a recorded run or turn its own green status into behavioral proof.
