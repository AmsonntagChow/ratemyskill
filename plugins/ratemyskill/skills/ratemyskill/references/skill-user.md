# Skill-user review

Judge whether the skill makes a real user more successful, not whether its instructions sound sophisticated.

## Contract

Extract one sentence for each:

- user job and intended user
- trigger situations and explicit exclusions
- required inputs and available fallbacks
- promised output or state change
- completion and failure signals

Flag a promise that cannot be observed or an input requirement hidden until late execution.

## Representative tasks

Use at least one common task and one awkward but in-scope task. For strict or higher reviews, add a missing-input or partial-evidence case. When planning or running a with/without comparison, first read `references/evaluation.md` rather than defining a second comparison protocol here.

Judge:

| Dimension | Questions |
|---|---|
| Time to value | Does the skill reduce setup, back-and-forth, and user decisions? |
| Output actionability | Can the result be used directly, or is it another generic checklist? |
| Input discipline | Does it request only information that can materially change the result? |
| Failure quality | Does it preserve useful partial work and name the smallest unblocker? |
| Repeated use | Does the workflow stay stable across variants without forcing one rigid answer? |
| User control | Are consequential assumptions and side effects surfaced at the right time? |

Do not reward extra files, extra questions, or longer outputs by default. A short, reliable skill can beat an elaborate framework.

## High-signal failures

- It asks a long questionnaire before doing any useful work.
- The supposed expertise is already supplied by the base model and produces no measured uplift.
- The output format is consistent but wrong for real user decisions.
- It handles the author's demo only and collapses on an ordinary variant.
- It refuses or blocks safely solvable tasks because instructions are over-constrained.
- It silently changes the user's goal to fit its workflow.

## Verdict contribution

Report task success, user effort, failure recovery, and execution uplift separately. A user-friendly demo cannot compensate for unsafe authority or unreliable discovery.
