# Marketplace-curator review

Judge whether a stranger can discover, understand, trust, install, test, update, and remove the skill without private context.

## Listing and positioning

- The name and short description explain the user outcome in ordinary language.
- Examples are concrete, adaptable workflows rather than vague capability claims.
- The listing matches the actual trigger boundary and packaged behavior.
- Claims such as “secure,” “enterprise-grade,” or “works everywhere” have evidence and declared limits.
- The skill is distinct from generic prompting or a built-in capability.

## Package integrity

Verify the final install artifact, not only the authoring source:

- canonical skill and packaged copy match
- manifest name, folder name, version, and listing agree
- referenced files, assets, scripts, and license are included
- archives have one valid plugin root when the target requires it
- install commands work from a clean environment
- no local absolute paths, caches, secrets, editor files, or build debris ship
- update and uninstall behavior are documented and do not create duplicate skill copies

Use current documentation for the target marketplace. Label any unverified platform rule instead of guessing.

## Trust materials

For public distribution, expect proportionate README, license, security-reporting route, maintainer identity, repository, support path, privacy or data-handling disclosure, terms when required, dependency disclosure, and release notes. A local instruction-only skill may need far less.

Check that policies describe what the package actually does. “No data collection” is false when a bundled service or developer endpoint receives user content.

## Evidence expected by target

| Target | Evidence |
|---|---|
| Local draft | Structural validation and one representative execution |
| Team shared | Positive and near-miss trigger tests, representative tasks, permission disclosure, rollback or removal path |
| Public marketplace | Clean-package install, repeated discovery tests, with/without execution evidence, safety scan, support and legal materials |
| Privileged production | Tool and data-flow tests, least authority, audit trail, failure recovery, incident ownership |
| High stakes | Independent domain review, human-control plan, compliance evidence, change approval, incident exercises |

Do not convert missing review evidence into a failing product claim. Cap the maximum safe distribution and name the smallest evidence package that can raise it.
