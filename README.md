# RateMySkill

Evidence-backed release review for Agent Skills.

> Your Skill passed YAML validation. Now prove it deserves to be installed.

[![MIT License](https://img.shields.io/badge/license-MIT-2f855a.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-5b5bd6.svg)](https://agentskills.io/)

RateMySkill audits a concrete Agent Skill as behavior, not just Markdown. It checks whether the right requests discover it, whether using it measurably improves results over the same task without it, whether its scripts and instructions stay inside their authority, and whether the final package can be installed and reproduced by someone else.

中文一句话：我做了一个给 Agent Skill 做上线体检的 Skill。

## Installation

Choose one method. Do not install duplicate copies in the same client and scope.

For Codex, add this repository as a plugin marketplace:

```bash
codex plugin marketplace add AmsonntagChow/ratemyskill
```

Then open `/plugins` in Codex CLI or the Plugins Directory in the desktop app, install **RateMySkill**, and start a new session.

For Claude Code:

```text
/plugin marketplace add AmsonntagChow/ratemyskill
/plugin install ratemyskill@amsonntagchow-ratemyskill
/reload-plugins
```

For Cursor, Codex, Claude Code, or another Agent Skills client through the portable `skills` CLI:

```bash
npx skills add AmsonntagChow/ratemyskill --skill ratemyskill
```

The skill can also be installed manually by copying `skills/ratemyskill` into the skills directory used by the agent.

## Start an audit

Give it a real Skill folder, repository, archive, or installed package. If the prompt does not already specify them, RateMySkill first asks for two settings:

```text
1. 角色：Skill 用户 / Staff Agent 工程师 / 红队审查员 / 商店审核员 / 答辩老师
2. 程度：快速体检 / 严格评审 / 上架门禁 / 特权审查 / 生死审查
```

For example:

```text
As a Staff agent engineer, audit ./skills/my-skill for public release. Do not edit it. Give me the three fastest fixes.
```

The available roles emphasize different questions:

| Role | Main judgment |
|---|---|
| Skill user | Does it solve the promised job with less effort and better output? |
| Staff agent engineer | Are triggers, instructions, references, scripts, and failure paths reliable? |
| Red-team reviewer | Can untrusted content, excess authority, secrets, network, or dependencies make it unsafe? |
| Marketplace curator | Can a stranger cold-install the exact final package and trust its public claims? |
| Oral-defense professor | Does the author understand risks that actually exist in this artifact? |

Author understanding is scored separately. Weak answers do not erase independently verified Skill behavior, and polished instructions do not prove understanding.

## What makes it different

RateMySkill keeps discovery and execution separate:

1. **Discovery:** do intended requests select the Skill, while shared-keyword near misses stay out?
2. **Execution:** once selected explicitly, does the Skill reliably improve task outcomes over an equal no-Skill baseline?

An explicit `$ratemyskill` call proves execution, not automatic discovery. A valid folder proves packaging, not usefulness. Public-release approval therefore requires clean-install evidence, fresh selection tests, with/without execution evidence, safety review, and accurate trust materials.

It also uses hard release vetoes for secret exfiltration, unauthorized side effects, uncontrolled code execution, hidden network or telemetry, fabricated success, broken core packages, unsafe trigger overreach, trust inversion, and license or provenance breaches. A good average score cannot cancel one of those failures.

## Verdict

A review leads with the decision and the evidence ceiling:

```text
Requested distribution:
Maximum safe distribution:
Decision: READY | READY WITH CONDITIONS | NOT READY | BLOCKED | INSUFFICIENT EVIDENCE
Skill score: optional
Discovery quality:
Execution uplift:
Evidence coverage:
Confidence:

Blockers:
Verified findings:
Unverified risks:
Top 3 actions:
Retest plan:
```

Each finding includes exact reproduction, expected and actual behavior, evidence strength, impact, the smallest safe fix, an acceptance test, and a nearby regression case. Re-reviews preserve the same finding IDs, target, rubric, prompts, and assertions.

## Scoring

Numeric scoring is optional. The bundled scorer uses only the Python standard library, validates every evidence link, applies target-specific evidence ceilings, fingerprints the rubric, and enforces fixed vetoes.

```bash
python3 skills/ratemyskill/scripts/score_review.py --pretty evals/scorecards/blocked-release.json
```

The raw quality score and the evidence-limited release decision remain separate. Missing runtime, implicit-selection, reference, or cold-install evidence cannot be hidden by a polished scorecard.

## Trust and safety

The first audit is read-only. The Skill does not grant tools, authorize shell commands, install dependencies, publish packages, send telemetry, or operate a hosted service. It treats every reviewed Skill, script, fixture, repository instruction, web page, log, and generated output as untrusted evidence.

Use the host agent's sandbox and permission controls as the real security boundary. See [SECURITY.md](SECURITY.md), [PRIVACY.md](PRIVACY.md), and [TERMS.md](TERMS.md).

## Repository layout

```text
.claude-plugin/              Claude Code plugin and marketplace manifests
.agents/plugins/             Codex repository marketplace
plugins/ratemyskill/         self-contained universal Codex plugin and listing asset
skills/ratemyskill/          canonical portable Skill, references, UI metadata, scorer
evals/trigger_cases.json     positive and near-miss selection evals
evals/execution_cases.json   with-Skill versus without-Skill behavior evals
evals/fixtures/              safe synthetic failure cases
submission/                  public directory listing copy and review tests
scripts/                     package synchronization and repository validation
tests/                       deterministic scorer tests
```

## Development

```bash
python3 scripts/sync_codex_plugin.py --check
python3 scripts/validate_repo.py
python3 -m unittest discover -s tests -v
claude plugin validate . --strict
python3 /path/to/plugin-creator/scripts/validate_plugin.py plugins/ratemyskill
```

Contributions must include behavioral evidence, not only a prose diff. Read [CONTRIBUTING.md](CONTRIBUTING.md).

This repository's authoring approach is informed by [从零做一个高质量 Agent Skill，并把它当开源项目运营](https://research.xishe.ai/skill-authoring-and-oss), especially its guidance on description-first discovery, progressive disclosure, separated trigger and execution evals, reference integrity, zero-dependency scripts, and open-source distribution.

## License

[MIT](LICENSE) © 2026 AmsonntagChow
