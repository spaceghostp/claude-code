# Capture Signal Schema

> The requirements document for autonomous vault capture. Defines what constitutes a vault-worthy signal, how to detect it, and how to present it for human approval.

## Purpose

Claude should extract insights autonomously during sessions — not wait for `/vault-capture`. This schema defines the triggers. Bias: **capture excess rather than miss value**. The human reviews everything before it enters the vault. False negatives (missed insights) are worse than false positives (rejected proposals).

---

## Signal Categories

Each category represents a class of insight worth preserving. Haiku subagents scan for these in parallel.

### 1. Domain Expertise

**What**: Technical knowledge, API behaviors, platform quirks, language idioms, framework patterns that are non-obvious or hard-won.

**Examples**:
- "OAuth token refresh has a 5-second race window that causes silent logouts"
- "Python's `defaultdict` silently creates keys on access — this breaks `in` checks"
- "Terraform state locks don't release on SIGKILL — must manually unlock"

**Vault type**: `atom` (if a reusable concept) or `encounter` (if situation-specific)

**Signal strength**: High when the knowledge was *discovered through effort* rather than recalled from common knowledge. If a developer would say "I wish someone had told me that," it's a signal.

### 2. Tool/Workflow Knowledge

**What**: How tools, CLIs, editors, CI/CD, deployment pipelines, or development workflows actually behave — especially where behavior diverges from documentation.

**Examples**:
- "Claude Code's Task tool with model='haiku' runs 3x faster but can't access conversation context"
- "Git rebase --autosquash only works if commit messages start with 'fixup!' or 'squash!'"
- "Docker layer caching invalidates on any COPY that changes — order Dockerfile commands by change frequency"

**Vault type**: `atom` (reusable) or `encounter` (context-specific)

**Signal strength**: High when the knowledge reduces future friction. The test: would this save time in a future session?

### 3. Project/Architecture Context

**What**: Decisions made, trade-offs evaluated, architectural constraints discovered, system boundaries identified. The kind of context that gets lost between sessions and forces re-derivation.

**Examples**:
- "We chose event sourcing over CRUD because audit trail is a regulatory requirement"
- "The monorepo build takes 12 minutes — any PR touching shared libs blocks all teams"
- "Auth service is the only stateful component — everything else can be redeployed independently"

**Vault type**: `encounter` (decision record) or `position` (if it's a stance worth defending)

**Signal strength**: High when the context would change how you approach a future task in the same project. If losing this context means re-asking the same questions, it's a signal.

### 4. Patterns & Anti-Patterns

**What**: Recurring approaches that work, recurring approaches that fail, structural similarities across different problems.

**Examples**:
- "Every time we add a cache layer, we spend 2 sprints debugging invalidation"
- "Services that own their data schema are 3x easier to deploy independently"
- "The retry-with-backoff pattern appears in 4 different services with 4 different implementations"

**Vault type**: `atom` (named pattern) or `tension` (if it involves a trade-off)

**Signal strength**: High when the pattern has been observed 2+ times. A single instance is an encounter; a recurring instance is a pattern.

### 5. Contradictions & Surprises

**What**: Anything that contradicts an existing vault position, challenges an assumption, or produces genuine surprise. This is the highest-value signal category.

**Examples**:
- "We assumed strong types slow us down, but TypeScript caught 3 bugs this week that would have been production incidents"
- "The 'explicit over abstract' position failed here — the abstraction saved 200 lines and no one was confused"
- "This behavior directly contradicts [[positions/what-good-code-actually-is]] Claim 2"

**Vault type**: `tension` (if unresolved), `encounter` (if documenting the surprise), or triggers `/vault-falsify` (if a position needs revision)

**Signal strength**: Always high. Contradictions are the most valuable signals because they drive position evolution.

### 6. Unresolved Questions

**What**: Questions that arose during the session and weren't fully answered. Things worth investigating later. Gaps in understanding that were worked around but not resolved.

**Examples**:
- "Why does the connection pool max out at 10 when the docs say 25?"
- "Is there a way to get Obsidian's graph view to weight edges by link frequency?"
- "What happens to in-flight requests when a Kubernetes pod gets evicted?"

**Vault type**: `question` or `anti-library` (if it's an assumption that should be tested)

**Signal strength**: Medium-high. Not every open question is worth tracking — only ones where the answer would materially change future decisions.

---

## Detection Guidelines

### Bias Toward Capture

When uncertain whether something is signal-worthy, **propose it**. The human filters. Missing a genuine insight is more costly than proposing a non-insight.

### Minimum Signal Threshold

A signal must meet at least ONE of:
- It would save time or prevent an error in a future session
- It contradicts or refines an existing vault note
- It represents domain knowledge not available in documentation
- It captures a decision or trade-off that would otherwise be lost
- It names a pattern observed across 2+ instances

### What Is NOT a Signal

- Common knowledge easily found in documentation
- Temporary debugging state (unless the debugging *process* revealed something reusable)
- User preferences or style choices (unless they encode a principled position)
- Implementation details that only matter for the current task and have no future value

---

## Proposal Format

When presenting signals for human approval, each proposal must include:

```
Type: [atom|tension|encounter|position|question|anti-library]
Title: [kebab-case-filename]
Summary: [1-2 sentences — what it is and why it matters]
Links: [existing vault notes it would connect to]
```

**Conciseness requirement**: The human should be able to approve/reject in under 5 seconds per proposal. If the summary needs more than 2 sentences, it's too complex for the proposal stage — simplify, and expand after approval.

---

## Capacity Thresholds

### Capture Tier (Haiku — runs broadly, per-session)
- Trigger: End of task, natural break, or explicit `/vault-evaluate` invocation
- Model: Haiku subagents (fast, cheap, parallel)
- Scope: Current session context
- Output: Proposals for human approval

### Maintenance Tier (Opus — runs deeply, scheduled)
- Trigger: When vault reaches **15+ notes** total, OR **10+ notes** tagged `#status/working`, OR on explicit `/vault-maintain` invocation
- Model: Opus (latest, most capable)
- Scope: Entire vault
- Operations: Orphan scan, staleness check, pattern extraction, link refinement, signal schema effectiveness review, anti-library audit, falsification review
- Output: Maintenance report + vault-health dashboard update

### Capacity Escalation
As the vault grows, maintenance frequency should increase:
- **5-15 notes**: Maintain on explicit invoke only
- **15-30 notes**: Maintain every 5 sessions or on invoke
- **30-50 notes**: Maintain every 3 sessions or on invoke
- **50+ notes**: Maintain every session (lightweight check) + full maintain weekly

---

## Effectiveness Measurement

### Immediate (per-session)
- Proposals generated vs. proposals approved (approval rate)
- Did surfaced notes from `resurface.py` actually get referenced in the session?

### Medium-term (weekly, via vault-maintain)
- Orphan rate: % of notes with zero inbound links
- Re-use rate: How often notes are linked from newer notes
- Working-to-settled ratio: Are positions maturing or staying provisional?
- Signal category distribution: Which categories produce the most approved notes?

### Long-term (monthly)
- Graph density: total links / total notes (higher = more connected thinking)
- Falsification rate: How often positions are revised (too low = not testing; too high = not settling)
- Session friction reduction: Does session start context lead to fewer re-derivations?
- Coverage: Are all signal categories producing notes, or are some dormant?

---

## Schema Versioning

This document is the source of truth for capture behavior. When signal categories are added, thresholds adjusted, or measurement criteria changed, update this document and record the change in the `## Changelog` section below.

### Changelog

- **2026-02-16**: Initial schema. Six signal categories, two-tier capture/maintenance model, human-in-the-loop approval requirement.
