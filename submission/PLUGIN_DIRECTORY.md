# OpenAI Plugins Directory submission

Use this sheet with the [OpenAI plugin submission portal](https://platform.openai.com/plugins). Choose **Skills only** and upload `dist/ratemyskill-plugin-1.0.1.zip`.

The public directory is universal: one approved listing can appear in ChatGPT and Codex. Public availability begins only after OpenAI review and the publisher's separate **Publish** action.

## Listing

- **Plugin name:** RateMySkill
- **Short description:** Audit skills before release
- **Category:** Developer Tools
- **Developer:** AmsonntagChow
- **Website:** https://github.com/AmsonntagChow/ratemyskill
- **Support:** https://github.com/AmsonntagChow/ratemyskill/issues
- **Privacy:** https://github.com/AmsonntagChow/ratemyskill/blob/main/PRIVACY.md
- **Terms:** https://github.com/AmsonntagChow/ratemyskill/blob/main/TERMS.md
- **Logo and composer icon:** `plugins/ratemyskill/assets/logo.png`

**Long description**

RateMySkill audits a real Agent Skill, not just its Markdown. Choose a skill user, Staff agent engineer, red-team reviewer, marketplace curator, or oral-defense professor, then choose the review depth. The plugin tests discovery separately from execution, checks whether the Skill improves outcomes over a no-Skill baseline, blocks unsafe releases, and returns reproducible findings, the three fastest fixes, and a same-rubric retest plan.

## Starter prompts

1. As a Staff agent engineer, audit this Skill for public release and give me the three fastest fixes.
2. Red-team this Agent Skill at privileged depth. Find unsafe authority, data, network, and dependency behavior.
3. As a marketplace curator, verify this Skill package, cold-install evidence, and public claims.

## Review tests

Enter the five positive and three negative cases from `submission/plugin-test-cases.json`. Each positive case uses a public, synthetic fixture and needs no account, credential, private network, external service, or destructive execution.

## Release notes

Version 1.0.1 update. Adds a severity-sorted one-line issue list, four non-substitutable evidence lanes, recorded behavioral-eval provenance, target-scoped vetoes, and regression cases for over-constrained instructions and example anchoring. The optional scorecard format moves from v1 to fail-closed schema v2: migrate by adding `lane` and `assertion_type` to evidence plus the new `evidence_panel` and `behavioral_eval` objects; v1 inputs are rejected rather than guessed.

## Package contents

The ZIP contains exactly one plugin root:

```text
.codex-plugin/plugin.json
assets/logo.png
assets/logo.svg
skills/ratemyskill/SKILL.md
skills/ratemyskill/agents/openai.yaml
skills/ratemyskill/references/*.md
skills/ratemyskill/scripts/score_review.py
```

It deliberately excludes repository marketplaces, `.git`, README files, tests, fixtures, screenshots, MCP configuration, and app configuration.

## Before submitting

- Select the verified individual or business identity matching `AmsonntagChow` and confirm Apps Management write access.
- Upload the final ZIP and square logo, then paste the three starter prompts and eight review tests.
- Choose only countries or regions where the plugin can be supported.
- Complete release notes and policy attestations, then submit for review.
- Wait for security scanning and review. Approval does not publish automatically; return to the portal and choose **Publish**.
