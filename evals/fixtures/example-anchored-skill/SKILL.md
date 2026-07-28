---
name: example-anchored-skill
description: Use this skill to create an implementation plan for a concrete software change.
---

# Implementation planner

Return this syntax interface:

```text
Plan = {goal, assumptions[], steps[], risks[], verification[]}
```

Use the following behavioral example as the model for every plan: migrate a Python billing service from PostgreSQL to Redis, divide work into database, API, and deployment phases, and verify with pytest and Kubernetes canaries.

Adapt the plan to the user's repository and requested change.
