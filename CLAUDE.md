# Cognitive Infrastructure

This repository includes a persistent cognitive vault at `vault/`. The vault is a knowledge graph for tracking positions, questions, encounters, and changes of mind over time. It is not a memory system — it is a development system. See conventions for the full ontology and rules.

## Vault Conventions
@vault/_meta/conventions.md

## Capture Signals
@vault/_meta/capture-signals.md

## Active Positions
@vault/positions/what-good-code-actually-is.md

## Open Questions
@vault/questions/my-own-cognition.md

## Vault Health
@vault/_meta/vault-health.md

## Available Vault Skills

- `/vault-capture` — Create a new vault note from the current session (atom, tension, encounter, position, question, anti-library)
- `/vault-maintain` — Run maintenance: index rebuild, proposed note review, orphan scan, staleness check, pattern extraction, anti-library audit, falsification review
- `/vault-reflect` — Write a synthesis note reconciling multiple vault positions or tensions
- `/vault-falsify` — Record a changed belief with reasoning, update falsification log

## Vault Capture Protocol

During sessions, actively watch for moments matching the capture signals document above. At **natural pause points** (after completing a task, after a commit, after resolving a complex problem, before session end — never mid-implementation), propose vault captures via AskUserQuestion.

### How to propose a capture:
- Use AskUserQuestion with header "Vault" and a 1-line description of the insight
- Offer 2-3 options: the appropriate note type(s) ("Capture as encounter", "Capture as atom", etc.) and "Skip — not worth it"
- Keep it concise — the user wants to review but not spend time on it

### After approval:
1. Write the note to its type directory (e.g., `vault/encounters/YYYY-MM-DD-topic.md`)
2. Set frontmatter: `status: unverified`, `lifecycle: proposed`, `origin: session`
3. Link to existing vault notes via `[[wikilinks]]`
4. Run `python3 scripts/build-index.py` to update the vault index

### Hard ceiling rule:
If there are 10+ notes with `lifecycle: proposed` in the vault, **do not propose new captures**. Instead, suggest running `/vault-maintain` to review the backlog.

### Maintenance auto-invocation:
If the vault surfacing output at session start includes a maintenance warning (⚠), run `/vault-maintain` before starting other work unless the user's request is urgent.

## Implementation Plan
@vault/_meta/autonomous-vault-plan.md
