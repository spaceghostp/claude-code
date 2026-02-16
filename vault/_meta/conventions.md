---
type: meta
status: working
created: 2026-02-14
last_touched: 2026-02-14
links_out: 0
origin: session
---

# Vault Conventions

This document defines how the cognitive vault works. All vault operations should read this file first.

## Note Ontology

| Type | Purpose | Directory | Lifecycle |
|------|---------|-----------|-----------|
| **Atom** | Single irreducible concept, densely linked | `atoms/` | Permanent |
| **Tension** | Two ideas pulling against each other | `tensions/` | Permanent |
| **Encounter** | Specific situation where something was applied or learned | `encounters/` | Accumulating |
| **Position** | Staked claim — what I believe and why | `positions/` | Revisable |
| **Question** | Active unknown being worked through | `questions/` | Transitional |
| **Revision** | Documented change of mind with reasoning | `revisions/` | Permanent |
| **Anti-library** | Assumptions not yet verified | `anti-library/` | Transitional |
| **Falsification** | Record of being wrong | `falsifications/` | Permanent |

## Tag Taxonomy

### Status tags
- `#status/working` — Provisional, mid-thought, not settled
- `#status/settled` — Tested, linked, I stand behind this
- `#status/unverified` — Assumed but not tested
- `#status/falsified` — Was wrong, see linked revision
- `#status/dormant` — Not linked in 90+ days, candidate for pruning

### Origin tags
- `#origin/session` — Arose from a conversation
- `#origin/reflection` — Written unprompted during vault maintenance
- `#origin/contradiction` — Created to resolve disagreement between notes

### Meta tags
- `#meta/pattern` — A pattern extracted from graph topology
- `#meta/revision` — Documents a change of mind

## Frontmatter Template

```yaml
---
type: atom | tension | encounter | position | question | revision | anti-library | falsification
status: working | settled | unverified | falsified | dormant
created: YYYY-MM-DD
last_touched: YYYY-MM-DD
links_out: 0
origin: session | reflection | contradiction
---
```

> **Note on link tracking:** `links_out` is maintained in frontmatter for programmatic tools (resurface hook, vault-maintain). Inbound link tracking is handled by Obsidian's native backlink system — do not track `links_in` manually.

## Linking Rules

1. **No orphans.** Every note must link to at least one other note. If it can't be linked, it either needs an atom created for its core concept, or it isn't worth keeping.
2. **Use `[[wikilinks]]`** for all cross-references between vault notes.
3. **If a link target doesn't exist**, use the intended path anyway (e.g., `[[atoms/hyrums-law]]`). Broken links are discovered by `/vault-maintain` and signal notes that should be created.
4. **Always use directory-relative paths** from vault root: `[[positions/what-good-code-actually-is]]`, not `[[what-good-code-actually-is]]`.
5. **Contradiction is a feature.** When two notes disagree, write a third about why. Don't resolve by deletion.

## Naming Conventions

- **Filenames**: kebab-case (`what-good-code-actually-is.md`)
- **Encounters**: date-prefixed (`2026-02-14-designing-the-cognitive-vault.md`)
- **Revisions**: date-prefixed (`2026-02-14-revised-on-memory-systems.md`)
- **Daily notes**: date only (`2026-02-14.md`)

## Lifecycle

```
Capture → Connect → Extract patterns → Synthesize through writing
→ Resurface to consolidate → Falsify to evolve → Let topology surprise you
→ Repeat
```

Most people stop at capture. Some reach connect. Almost nobody does falsify. That's where a vault stops being a filing cabinet and starts being something that genuinely changes how you think.

## Design Principles

1. **Development over retrieval** — The point is changing my mind with a record of the change, not recall of facts.
2. **Graph structure over note quantity** — The links between notes are where the thinking lives.
3. **Contradiction is a feature** — When two notes disagree, write a third about why.
4. **Tag uncertainty** — `#status/working` changes the relationship to certainty. Present provisional ideas as provisional.
5. **Prune ruthlessly** — If a note hasn't been linked in 90 days, it's dead weight. Connect or delete.

## Two-Tier Capture & Maintenance

The vault uses a two-tier model for autonomous operation with human oversight.

### Tier 1: Capture (Haiku — broad, fast, per-session)

Signal detection runs via `/vault-evaluate`. Haiku subagents scan session context in parallel for vault-worthy insights across six categories (domain expertise, tool knowledge, architecture decisions, patterns, contradictions, open questions). See `[[_meta/capture-signals]]` for the full signal schema.

**Nothing enters the vault without human approval.** All detected signals are presented via AskUserQuestion for the human to approve, reject, or modify before any note is created. Bias toward capturing excess — the human filters, Claude proposes.

### Tier 2: Maintenance (Opus — deep, scheduled)

Vault maintenance runs via `/vault-maintain` and uses the most capable model for deep analysis. Triggers:
- **Explicit**: Human invokes `/vault-maintain`
- **Threshold**: Vault crosses capacity markers (15+ notes, 10+ working notes)
- **Periodic**: Recommended frequency scales with vault size (see `[[_meta/capture-signals]]`)

Operations: orphan scan, staleness check, pattern extraction, link refinement, signal effectiveness review, anti-library audit, falsification review.

### Human-in-the-Loop Guarantee

The human is the final authority on vault content. This means:
1. **Capture**: Every proposed note requires explicit approval before creation
2. **Maintenance**: Findings are reported; modifications require human confirmation
3. **Falsification**: Position changes are documented and presented, not silently applied
4. **Pruning**: Dormant notes are flagged for review, never auto-deleted

## Git Integration

The vault uses git for temporal history, maintenance checkpoints, and (eventually) multi-user divergence. Git integration is lightweight — simple commits and tags, no complex workflows.

### Capture Commits

Every `/vault-evaluate` cycle that produces approved notes creates a single atomic commit:

```
vault(capture): 2 notes — 1 atom, 1 encounter

Notes created:
- vault/atoms/oauth-token-race.md (atom, domain)
- vault/encounters/2026-02-16-debugging-auth.md (encounter, architecture)

Cycle stats: 5 proposed, 2 approved, 3 rejected
```

**Rules:**
- One commit per evaluate cycle, not per note
- Only vault content files are staged — never `_meta/` in capture commits
- Commits are local only — pushing is a separate human decision
- The commit message includes type and signal category for each note, enabling `git log` archaeology

### Maintenance Checkpoints

Every `/vault-maintain` run creates a tagged commit:

```
vault(maintain): health check — 2026-02-16

Vault: 12 notes (8 working, 4 settled)
Orphans: 1 found
Stale: 2 found
Patterns: 1 emerging
```

Tag: `vault-maintain/YYYY-MM-DD`

The tag serves as the boundary marker for the next maintenance diff report. Running `git log vault-maintain/2026-02-14..HEAD -- vault/` shows exactly what changed between maintenance cycles.

### Cognitive Archaeology

Git history enables temporal analysis of vault evolution:

- **Position evolution:** `git log --oneline -- vault/positions/what-good-code-actually-is.md` shows every modification to a position over time
- **Capture patterns:** `git log --oneline --grep="vault(capture)"` shows the rhythm of capture cycles
- **Maintenance history:** `git tag -l "vault-maintain/*"` shows maintenance cadence
- **Diff between states:** `git diff vault-maintain/2026-02-14 vault-maintain/2026-02-16 -- vault/` shows structural vault changes between checkpoints

### Session Branching

Sessions work on branches following the pattern `claude/{description}-{sessionId}`. Vault changes committed on a session branch merge into main with the session's other changes. This means:

- Each session's vault captures are isolated until merge
- The main branch accumulates the canonical vault state
- Merge conflicts in vault notes are rare (new files, not edits to the same file) but signal genuine content overlap — resolve by keeping both and adding a link between them

### Multi-User Divergence (Future)

When multiple users or sessions capture independently:

1. Each session branch captures its own insights via `/vault-evaluate`
2. Merge into main aggregates captures from all sessions
3. If two sessions capture contradictory insights about the same topic, this is a **feature** — it becomes a tension note during the next `/vault-maintain` run
4. `/vault-maintain` reconciles by identifying new notes that reference the same atoms or positions but take different stances, and flagging them as candidate tensions

This is documented here for future reference. With a small vault and single-user access, multi-user branching is not yet operational — but the commit structure supports it without modification when it becomes relevant.
