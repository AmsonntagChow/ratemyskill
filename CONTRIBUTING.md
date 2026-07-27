# Contributing

RateMySkill is one focused Skill: evidence-grounded evaluation of concrete Agent Skills. New review modes may fit; unrelated prompt, code, product, or agent reviewers do not.

## Evidence required

Every behavior-changing pull request should include:

1. at least three exact user prompts, including a near miss when discovery changes;
2. before-and-after transcripts or concise behavioral observations;
3. hidden assertions that fail before the change and pass after it;
4. an explanation of any frontmatter `description` change; and
5. a same-rubric comparison when scoring or verdict behavior changes.

A prose-only rewrite is not proof of improvement. Prefer a small reference, deterministic helper, or evaluation case that changes measurable behavior.

## Local checks

```bash
python3 scripts/sync_codex_plugin.py --check
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
```

Keep scripts on the Python standard library unless a dependency is essential and explicitly reviewed. Scripts must resolve paths independently of the current working directory, be deterministic for the same logical input, avoid hidden writes and network access, and report failures with non-zero exit codes.

## Pull-request hygiene

- Keep safety vetoes and non-negotiable rules in the main `SKILL.md`.
- Keep references one level deep and valid on case-sensitive filesystems.
- Run `python3 scripts/sync_codex_plugin.py` after changing the canonical Skill.
- Keep Claude and Codex plugin versions aligned when published contents change.
- Update trigger and execution evals separately.
- Never add telemetry, undisclosed network access, or tool auto-authorization.
- Never weaken a veto or evidence ceiling merely to raise a score.
- Sign commits with `git commit -s` to certify the Developer Certificate of Origin.

Maintainers may close proposals that expand scope, lack reproducible evidence, or introduce a permission or supply-chain risk without a clear benefit.
