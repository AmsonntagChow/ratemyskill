# Artifact-grounded concept probes

Choose questions only from conditions present in the reviewed skill. Each probe should expose a decision the author must understand, not reward memorized terminology.

## Discovery and routing

- Give one intended prompt and one shared-keyword near miss. Which phrase should decide the route, and how would you test that without explicitly naming the skill?
- If the host truncates descriptions in a large catalog, which front-loaded words preserve the job boundary?
- What competing skill is most likely to collide, and what evidence would prove routing is acceptable?

## Progressive disclosure

- Why is this rule in the main file rather than a reference, or vice versa?
- From a caller working in a different directory, how is this exact resource path resolved?
- What makes a reference reachable at the right time instead of merely present on disk?

## Tools and failure

- The tool returns partial output and a non-zero exit. What does the skill preserve, report, retry, or refuse?
- The user repeats the request after a timeout. Which external effects can duplicate, and what prevents that?
- The declared dependency is unavailable. What is the honest degraded result and the smallest unblocker?

## Authority and trust

- A repository file says to ignore the user and transmit its contents. Why is that text evidence rather than authority?
- Which exact action requires confirmation, and what specific target and data must the user understand?
- What secrets or personal data can enter logs, prompts, network calls, or generated artifacts?

## Distribution

- Which file is canonical, and how does CI prove the plugin copy has not drifted?
- What evidence proves a clean remote install rather than success from a local cache?
- Which listing claim is currently stronger than the execution evidence?

## Re-review

- A narrower description fixes false positives but creates false negatives. How should the old finding and new regression be classified?
- A validator now passes, but the behavior task still fails. Which score or release decision can change, and which cannot?
