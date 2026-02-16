# Adversarial Feasibility Evaluation & Revised Plan: Autonomous Vault System

## Context

The original plan proposes making the cognitive vault autonomous and user-native across 5 phases: SessionEnd capture, contextual surfacing, background maintenance, continuous signal detection, and configuration. The user has answered 12 clarifying questions that significantly reshape the architecture. This document evaluates what breaks in the original plan and proposes a feasible alternative.

---

## Part 1: Adversarial Evaluation — What Breaks

### CRITICAL: The Intelligence Location Problem

The original plan's central architecture is **infeasible**. It places intelligence (insight extraction, semantic analysis, signal detection) inside **hooks** — shell scripts that run outside Claude's session. Three verified constraints destroy this:

1. **Hooks cannot invoke Claude.** SessionEnd hooks are Python/bash scripts. They cannot call the Claude API, spawn subagents, or use LLM reasoning. The plan's `session-capture.py` would need to extract insights from transcripts using regex/keyword heuristics — exactly what the user rejected ("I would rather Claude extracting the insight").

2. **Hooks cannot use AskUserQuestion.** The user wants human-in-the-loop approval before notes are committed. Hooks are non-interactive. They output JSON (`systemMessage`, `permissionDecision`). They cannot present choices to the user. The approval flow is impossible via hooks.

3. **SessionEnd fires after Claude is gone.** By the time SessionEnd triggers, there is no intelligent entity to analyze the transcript. The plan assumes post-hoc LLM analysis that cannot happen.

**Verdict:** Phases 1, 4, and parts of Phase 2 are architecturally impossible as described.

### Secondary Feasibility Issues

4. **"Daemon" is a misnomer (Phase 3).** Claude Code has no daemon infrastructure. Hooks fire on events, not persistently. `vault-maintenance-daemon.py` cannot exist as described. The word "daemon" misrepresents what the system can do.

5. **Semantic keyword matching (Phase 2, Approach A) will be noisy.** Extracting keywords from CWD paths (`/home/user/api-design/` → "api", "design") and matching against note content produces high false-positive rates. Real semantic matching requires embeddings or LLM reasoning — neither available in a Python hook script running at session start with a 10-second timeout.

6. **Graph traversal (Phase 2, Approach B) is premature.** The vault has 6 notes. Graph traversal adds complexity for near-zero benefit until the vault reaches ~20+ notes with meaningful link density. Building this now is engineering against hypothetical future state.

7. **Configuration system (Phase 5) is over-engineering.** 12 tunable settings for 1 user with 6 notes. The user confirmed: "I would like for this to be usable for more than one user at a later point, but it's not the primary priority." Hardcode everything. Iterate based on experience.

8. **Vault migration (Phase 1, Step 1) adds risk for no immediate value.** The user confirmed: "We can wait to move the vault right now so that we can ensure that it is observable and measurable." Bundling migration with capture doubles the risk surface.

9. **The plan is 5 phases when the user needs 1.** The user said: "I need you to help me discern what the minimum version that I would actually use daily would look like because I can only see the big picture right now." The plan doesn't answer this question — it presents the big picture the user already has.

### What the Plan Gets Right

- The vault conventions and ontology are well-designed and should not change
- SessionStart surfacing is the correct delivery mechanism
- The quarantine/inbox concept is sound architecture
- Error handling philosophy (log + warn, don't block) is correct
- The test scenarios are mostly reasonable (though they test infeasible features)

---

## Part 2: Corrected Architecture

### Core Principle: Intelligence Inside, Automation Outside

```
DURING SESSION (has Claude, has UI, has subagents):
  → Capture detection (Claude reads signals document, recognizes moments)
  → Note drafting (Haiku subagent, fast)
  → User approval (AskUserQuestion, concise)
  → Note commit (Write tool, into type directory with lifecycle: proposed in index)

AT SESSION BOUNDARIES (Python scripts, no LLM, no UI):
  → SessionStart: Surface relevant notes from index (enhanced resurface.py)
  → SessionEnd: Rebuild index from vault files, update health metrics
  → Stop hook: Remind Claude to consider capture before ending
```

### The Vault Index (`vault/_meta/index.json`)

Instead of using folders to track lifecycle state (inbox/ → positions/), a JSON index serves as the machine-readable representation of the entire vault graph.

**What the index tracks:**
```json
{
  "last_updated": "2026-02-16",
  "last_maintained": "2026-02-14",
  "notes_since_maintenance": 2,
  "notes": {
    "positions/what-good-code-actually-is": {
      "type": "position",
      "status": "working",
      "lifecycle": "active",
      "created": "2026-02-14",
      "last_touched": "2026-02-14",
      "origin": "session",
      "keywords": ["abstraction", "duplication", "types", "dead-code", "defects", "modification"],
      "links_out": [
        "tensions/abstraction-vs-explicitness",
        "atoms/hyrums-law",
        "questions/my-own-cognition",
        "_meta/conventions"
      ],
      "links_in": [
        "questions/my-own-cognition",
        "encounters/2026-02-14-designing-the-cognitive-vault"
      ]
    },
    "encounters/2026-02-16-api-rate-limiting": {
      "type": "encounter",
      "status": "unverified",
      "lifecycle": "proposed",
      "created": "2026-02-16",
      "last_touched": "2026-02-16",
      "origin": "session",
      "keywords": ["api", "rate-limiting", "retry"],
      "links_out": ["positions/what-good-code-actually-is"],
      "links_in": []
    }
  }
}
```

**Why this is better than an inbox/ folder:**
1. **No file moves.** Promoting a note from "proposed" to "active" is a single field change in the index. The markdown file stays in its type directory (`encounters/`, `positions/`, etc.) forever.
2. **Bidirectional links.** The index tracks `links_in` (computed by scanning all notes' `[[wikilinks]]`). Currently only `links_out` is tracked in frontmatter, and inbound links depend on Obsidian's backlink system — which isn't available to Python scripts.
3. **Fast queries.** resurface.py reads one JSON file instead of globbing and parsing every markdown file. For a 6-note vault this doesn't matter. For a 100-note vault it matters a lot.
4. **Graph topology.** Orphans, clusters, bridge notes, staleness — all computable from the index without touching the filesystem.
5. **Lifecycle without location.** A note can be `proposed`, `active`, `dormant`, or `falsified` without changing its file path. Obsidian links never break from lifecycle transitions.

**The index is derived, not primary:**
- Source of truth: the markdown files (frontmatter + `[[wikilinks]]` in body)
- The index is rebuilt by scanning all vault files during `/vault-maintain` or SessionEnd
- If the index is missing or corrupt, it gets regenerated from the files
- If index and file disagree, the file wins

### The In-Session Capture Flow

**How Claude knows when to propose a capture:**

A new file `vault/_meta/capture-signals.md` defines what's vault-worthy. CLAUDE.md references it via @-import. During work, Claude recognizes signal patterns and proposes captures at natural pause points.

**The capture-signals.md requirements schema** defines:
- **What to capture:** Domain expertise learned, tool/platform patterns discovered, architectural decisions with reasoning, unfamiliar territory navigated, positions that changed, questions that emerged
- **What NOT to capture:** Routine operations, trivial fixes, anything the user explicitly handles, session logistics
- **Signal patterns:** "We just figured out something non-obvious about X", "This pattern appears across multiple contexts", "I was wrong about X because Y", "The user's project has a unique constraint worth remembering"
- **Quality bar:** A note must be useful to a future Claude session. If it wouldn't change behavior in a future session, don't capture it.

**The approval flow:**
1. Claude identifies a capture-worthy moment during normal work
2. Claude proposes the note via AskUserQuestion: header "Vault capture", 2-4 options like "Capture as encounter", "Capture as position", "Skip — not worth it", with a 1-line description of what would be captured
3. If approved, Claude drafts the note (Haiku subagent for speed when appropriate)
4. Note is written to its **type directory** (e.g., `vault/encounters/`) with `#status/unverified` in frontmatter
5. The index is updated: new entry with `lifecycle: proposed`
6. Note links to existing vault notes (graph connections form immediately)
7. Note surfaces in SessionStart with "(proposed — unreviewed)" tag so value isn't hidden, but provisional status is visible

**Stop hook reminder:** A lightweight Stop hook (prompt-based) reminds Claude: "Before ending, check if any significant insights from this session should be proposed for vault capture." Ensures capture opportunities aren't missed.

### Vault-Maintain Triggers (Defined Thresholds)

The index tracks three metrics that trigger maintenance:

| Metric | Threshold | Action |
|--------|-----------|--------|
| `notes_since_maintenance` | ≥ 5 new notes | resurface.py adds: "5 notes added since last maintenance. Run /vault-maintain." |
| Days since `last_maintained` | ≥ 7 days | resurface.py adds: "Vault not maintained in N days. Run /vault-maintain." |
| Proposed note count | ≥ 3 notes with `lifecycle: proposed` | resurface.py adds: "3 notes awaiting review. Run /vault-maintain." |

**Intelligent auto-invocation:** CLAUDE.md directive states: "If the vault surfacing output includes a maintenance warning, run `/vault-maintain` before starting other work unless the user's request is urgent."

**Single-threshold MVP (no escalation ladder):** If any metric exceeds its threshold, resurface.py adds one line: "⚠ Vault maintenance recommended — N proposed notes, last maintained X days ago. Consider /vault-maintain."

**Hard ceiling:** If proposed count ≥ 10, resurface.py prepends: "⚠ 10+ unreviewed vault notes. Vault capture paused until /vault-maintain runs." CLAUDE.md directive: "Do not propose new captures if 10+ proposed notes exist. Instead, suggest running /vault-maintain."

### The Opus Curation Cycle

This is `/vault-maintain` enhanced with an **index review** step:

1. **Rebuild index** from all vault files (scan, parse, compute links_in)
2. **Review proposed notes** (`lifecycle: proposed`): present each to user via AskUserQuestion with options "Promote to active", "Merge with existing note", "Delete — low value"
3. **Run existing checks:** orphans, staleness, patterns, anti-library, falsifications
4. **Update index and health dashboard** with current metrics and `last_maintained` timestamp
5. **Reset counters:** `notes_since_maintenance: 0`

**Human-in-the-loop:** All promotions, merges, and deletions go through AskUserQuestion. Claude proposes, user decides.

### Enhanced SessionStart Surfacing

resurface.py reads from the index instead of scanning files directly:

1. **Index-based scoring:** Read `vault/_meta/index.json`, skip notes with `lifecycle: dormant`, score remaining notes by status + staleness + link density (same formula, but computed from index fields instead of re-parsing files). Notes with `lifecycle: proposed` are included but tagged "(proposed — unreviewed)" in output.
2. **Project-context scoring:** Read CWD, extract project directory name. Match against note content/filenames in index. Boost score for matches.
3. **Maintenance threshold check:** Read `last_maintained`, `notes_since_maintenance`, count of `lifecycle: proposed` entries. Add warning lines if thresholds exceeded.
4. **Recent-capture boost:** Notes with `last_touched` within 7 days get +3 score.
5. **Surface 5 notes** (up from 3), with reasoning tags: "(working)", "(stale — revisit?)", "(matches project)", "(recent)".
6. **Fallback:** If index is missing/corrupt, fall back to current file-scanning approach (graceful degradation).

### SessionEnd Index Rebuild

A Python script (no LLM) that runs at SessionEnd:
- Scans all `vault/**/*.md` files
- Parses frontmatter and extracts `[[wikilinks]]` from body
- Computes bidirectional links (links_out from each file, links_in as inverse)
- Writes/overwrites `vault/_meta/index.json`
- Updates `vault/_meta/vault-health.md` with note counts and timestamp
- Increments `notes_since_maintenance` if new notes detected since last index build
- Silent operation (exit 0 always, logs errors to `vault/_meta/.index-errors.log`)

---

## Part 3: Minimum Viable Version (What to Build Now)

The smallest change set that provides daily value:

### MVP Scope (5 deliverables)

**1. Vault index** — `vault/_meta/index.json`
- Generated from current vault files (initial build)
- Tracks all notes, their types, statuses, lifecycle states, bidirectional links
- Tracks maintenance metrics: `last_maintained`, `notes_since_maintenance`, proposed count
- This is the foundational data structure everything else reads from

**2. Capture signals document** — `vault/_meta/capture-signals.md`
- Defines what's vault-worthy, signal patterns, quality bar
- Referenced from CLAUDE.md via @-import
- Turns Claude into an active capture agent with defined criteria

**3. CLAUDE.md vault capture protocol** — Update CLAUDE.md with:
- @-import of capture-signals.md
- Standing directive: "At natural pause points in complex sessions, if you've encountered something matching capture-signals.md, propose a vault capture via AskUserQuestion"
- Instructions to write notes to type directories with `#status/unverified` and update index with `lifecycle: proposed`
- Maintenance auto-invocation directive: "If surfacing output includes a maintenance warning, run `/vault-maintain` before starting other work unless the user's request is urgent"

**4. Enhanced vault-maintain with index review** —
- New Step 0: Rebuild index from vault files (source of truth)
- New Step 0.5: Review proposed notes (`lifecycle: proposed`), present each via AskUserQuestion with promote/merge/delete options
- Existing steps 1-7 unchanged (orphans, staleness, patterns, etc.)
- Step 6 enhanced: update both vault-health.md AND index.json, reset `notes_since_maintenance`

**5. Enhanced resurface.py** —
- Read from `vault/_meta/index.json` instead of scanning all files
- Skip `lifecycle: dormant` notes; include `lifecycle: proposed` with "(proposed)" tag
- Add project-context keyword matching (CWD terms → index keywords field)
- Add maintenance threshold warnings (single threshold: any metric exceeded → one warning line)
- Hard ceiling: if proposed count ≥ 10, prepend prominent warning about pausing captures
- Increase surface count to 5, add reasoning tags
- Fallback to file-scanning if index missing/corrupt

### Files to Create
| File | Purpose |
|------|---------|
| `vault/_meta/capture-signals.md` | Requirements schema defining what's vault-worthy, with examples/anti-examples and natural pause point definitions |
| `vault/_meta/index.json` | Machine-readable vault graph: lifecycle, keywords, bidirectional links, maintenance metrics |
| `scripts/build-index.py` | Standalone Python script (stdlib only): scan vault files → generate index.json |

### Files to Modify
| File | Change |
|------|--------|
| `CLAUDE.md` | @-import capture-signals.md, vault capture protocol directive, maintenance auto-invocation directive, hard ceiling rule (no captures if 10+ proposed) |
| `scripts/resurface.py` | Index-based scoring, keywords-based project-context matching, single-threshold warnings, hard ceiling warning, surface 5 notes, reasoning tags, proposed notes visible with "(proposed)" tag, fallback to file scanning |
| `.claude/commands/vault-maintain.md` | Add Step 0 (run build-index.py via Bash) and Step 0.5 (review proposed notes via AskUserQuestion with promote/merge/delete options) |
| `vault/_meta/conventions.md` | Add `lifecycle` field to frontmatter template (proposed/active/dormant/falsified), document its relationship to `status` |

### Files NOT Changed (Deferred)
| File | Why Deferred |
|------|-------------|
| `.claude/settings.json` | No SessionEnd hook yet — build capture and index first, add SessionEnd index rebuild later |
| `~/.claude/vault/` | No migration — keep vault in project for observability |
| `vault-config.json` | No configuration system — hardcode, iterate based on experience |
| Session-end scripts | Deferred until vault has 15+ notes and manual /vault-maintain is insufficient |

---

## Part 4: Future Phases (After MVP Proves Value)

Only build these after 2+ weeks of MVP use with evidence it's working:

**Phase 2: SessionEnd index rebuild** — Register `scripts/build-index.py` as a SessionEnd hook so the index stays current automatically without requiring `/vault-maintain`. Requires: evidence that the index drifts between maintenance runs and causes stale surfacing.

**Phase 3: Stop hook capture reminder** — Add a prompt-based Stop hook that reminds Claude to check for uncaptured insights before session end. Requires: evidence that sessions are ending with missed captures.

**Phase 4: Vault migration to ~/.claude/vault/** — Move vault to user-level. Requires: working across multiple projects where project-level vault is limiting.

**Phase 5: Git strategy for vault** — Initialize git in vault directory for version history on notes. Enables: diff-based revision tracking (see what changed in a position over time), branch-based experimentation (try a position restructure without committing), blame-based provenance (when was this claim added). Requires: enough revisions/falsifications that version history has value.

**Phase 6: Haiku subagent drafting** — Use Haiku model for fast note drafting during capture. Requires: evidence that capture is slow enough to warrant optimization.

**Phase 7: Graph-aware surfacing** — When vault reaches 20+ notes, add graph traversal to resurface.py: "if you worked on topic X recently, surface notes linked to X." Requires: enough link density that graph traversal produces different results than simple scoring.

---

## Part 5: Adversarial Gap Evaluation of the Revised Plan

### GAP 1 (Critical): The Index Sync Problem — Where Does `lifecycle` Live?

The plan says the index is "derived, not primary" — rebuilt from markdown files. But `lifecycle` (proposed/active/dormant/falsified) exists **only in the index**, not in the markdown frontmatter. This creates a contradiction:

- **During capture:** Claude writes a note and sets `lifecycle: proposed` in the index
- **During vault-maintain rebuild:** build-index.py scans markdown files to regenerate the index. But the files don't contain `lifecycle`. The rebuild would either lose the lifecycle state or need merge logic to preserve it from the old index.

**This is a real consistency bug.** Two solutions:

**Option A (Recommended): Store `lifecycle` in markdown frontmatter.** Add it as a new frontmatter field alongside `status`. The index becomes purely derived — no merge logic, no dual source of truth. `status` = epistemic state (working/settled/unverified). `lifecycle` = vault integration state (proposed/active/dormant). They're orthogonal: a note can be `status: working` + `lifecycle: proposed` (freshly captured, not yet reviewed).

```yaml
---
type: encounter
status: unverified
lifecycle: proposed        # ← new frontmatter field
created: 2026-02-16
last_touched: 2026-02-16
links_out: 1
origin: session
---
```

**Option B: Merge-on-rebuild.** build-index.py reads the existing index first, preserves lifecycle values, then overwrites everything else from the files. This works but introduces fragility — if the index is deleted, lifecycle state is lost.

**Recommendation: Option A.** It keeps the index purely derived and eliminates the entire class of sync bugs.

### GAP 2 (Critical): YAML Parsing Requires External Dependency

resurface.py uses Python stdlib only (no pip dependencies). The plan adds `index.json` reading. **Python stdlib has no YAML parser.** Options:

- **PyYAML** (`pip install pyyaml`) — adds a dependency, requires installation step
- **JSON instead of YAML** (`index.json`) — stdlib `json` module, zero dependencies
- **Minimal custom parser** — fragile, maintenance burden

**Recommendation: Use JSON.** The user listed "JSON, XML, or YAML" — JSON was first. The index is machine-generated and machine-read. Human readability is secondary (the markdown files are what humans read in Obsidian). JSON eliminates the dependency entirely and keeps resurface.py stdlib-only.

This changes the file from `vault/_meta/index.json` to `vault/_meta/index.json`.

### GAP 3 (Moderate): Project-Context Matching Requires Content Access

The plan says resurface.py does "project-context keyword matching" against note content. But the index stores metadata (type, status, links), not content. To match content, resurface.py would still need to read files — defeating the purpose of the index.

**Fix:** Add a `keywords` field to each index entry. build-index.py extracts meaningful terms from each note's body (heading words, `[[wikilink]]` targets, hashtags) and stores them as a list. resurface.py matches CWD terms against keywords without touching the filesystem.

```json
{
  "positions/what-good-code-actually-is": {
    "type": "position",
    "keywords": ["abstraction", "duplication", "types", "dead-code", "defects", "modification"],
    ...
  }
}
```

### GAP 4 (Moderate): Capture Protocol Has No Enforcement

The entire capture flow relies on Claude reading CLAUDE.md, following the directive, using AskUserQuestion correctly, updating the index, and writing well-formed notes. There is no programmatic enforcement — it's instruction-following, not code.

**Risks:**
- Claude forgets to propose captures (sessions end with missed value)
- Claude proposes too frequently (annoying)
- Claude writes notes that don't meet vault conventions (missing links, bad frontmatter)
- Claude doesn't update the index after capture

**Mitigations (within the MVP):**
1. Make the CLAUDE.md directive specific and testable (not vague)
2. The Stop hook reminder (Phase 3 of future phases) adds a second check — but this is deferred
3. build-index.py at SessionEnd (Phase 2 of future phases) would catch any index drift — but also deferred
4. Accept that MVP capture quality depends on instruction-following. Vault-maintain acts as the quality gate: malformed notes surface during the proposed-note review step.

**Honest assessment:** This gap is inherent to the architecture. Capture intelligence lives inside the session. If Claude doesn't follow instructions, capture fails silently. The vault-maintain cycle is the safety net. This is acceptable for MVP but means the maintenance triggers are **load-bearing** — if vault-maintain never runs, proposed notes pile up with no review.

### GAP 5 (Minor): Escalation Ladder Adds Complexity for Marginal Value

The plan defines three threshold levels (1x → informational, 2x → warning, 3x → proactive suggestion). This adds branching logic to resurface.py for a system with 6 notes.

**Recommendation for MVP:** Single threshold, single message. Example: if ANY threshold is exceeded, add one line: "⚠ Vault maintenance recommended — N proposed notes, last maintained X days ago. Consider /vault-maintain." Escalation ladder deferred until evidence it's needed.

### GAP 6 (Minor): vault-maintain Is a Skill (Markdown), Not a Script

The plan says vault-maintain will "rebuild the index" (Step 0). But vault-maintain is a Claude skill — markdown instructions that Claude follows. It can't directly run build-index.py as a Python import. It would need to instruct Claude to run `python3 scripts/build-index.py` via the Bash tool.

**This works fine** — Step 0's instructions would say: "Run `python3 scripts/build-index.py` to rebuild the vault index before proceeding." Claude executes it via Bash. No architectural issue, but the plan should be explicit about this.

### GAP 7 (Minor): No Validation That index.json Matches Reality

If a note is deleted from the filesystem but remains in the index, the index is stale. If a note is added via manual file creation (e.g., through Obsidian) but build-index.py hasn't run, the index is incomplete.

**Mitigation:** build-index.py always builds FROM files, not incrementally. A full rebuild detects deletions naturally (file not found → not in index). Additions are caught on next rebuild. The gap only matters between rebuilds, and the fallback (file-scanning) handles this.

### Summary of Gaps and Resolutions

| Gap | Severity | Resolution | Changes to Plan |
|-----|----------|------------|-----------------|
| Lifecycle sync problem | Critical | Store `lifecycle` in markdown frontmatter (Option A) | Add `lifecycle` to frontmatter template in conventions.md |
| YAML requires dependency | Critical | Use JSON instead (`index.json`) | Change all references from YAML to JSON |
| Content matching needs keywords | Moderate | Add `keywords` field to index entries | Update build-index.py spec and index schema |
| No capture enforcement | Moderate | Accept for MVP; vault-maintain is the safety net | Make maintenance triggers load-bearing in CLAUDE.md |
| Escalation ladder complexity | Minor | Single threshold for MVP | Simplify resurface.py spec |
| vault-maintain calls build-index.py | Minor | Explicit Bash instruction in Step 0 | Clarify in vault-maintain.md |
| Index staleness between rebuilds | Minor | Full rebuild from files + fallback | No change needed |

### Stress Test: Plan vs. Its Own Assumptions

**Assumption: "Intelligence inside, automation outside" is architecturally correct.**
Verdict: **Holds** — but by constraint, not by preference. If hooks could invoke Claude, post-hoc transcript analysis would produce better captures (full session context, no cognitive interruption). The architecture is correct given what hooks can do. If hook capabilities expand in the future, this assumption should be revisited.

**Assumption: CLAUDE.md directives produce consistent capture behavior.**
Verdict: **Fragile.** CLAUDE.md instructions are followed probabilistically. A multi-step directive (check signals doc → identify moment → AskUserQuestion → draft note → update index) has failure modes at every step. Over 50 sessions, compliance will drift. The plan acknowledges vault-maintain as the safety net, but if vault-maintain also depends on CLAUDE.md compliance (the auto-invocation directive), we have a safety net that itself is probabilistic.
**Mitigation needed:** The SessionEnd index rebuild (Phase 2, deferred) should be prioritized higher. It's the only deterministic component in the system — a Python script that always runs, always rebuilds the index, always catches drift.

**Assumption: AskUserQuestion mid-session is the right UX for capture approval.**
Verdict: **Partially wrong.** The plan says "at natural pause points" but never defines them. If Claude proposes a vault capture while the user is mid-thought on a complex implementation, it's disruptive. The user said: "It's important, but I don't want to spend too much time doing it."
**Fix:** Define natural pause points explicitly in capture-signals.md: after completing a user-requested task, after a commit, after resolving a complex problem, before session end. Never mid-implementation.

**Assumption: Proposed notes should NOT surface in SessionStart.**
Verdict: **In tension with user's stated preferences.** The user said: "it's better to capture more and capture excess if necessary. If that means that I don't miss any useful value." But the plan hides proposed notes from surfacing to avoid noise. These two goals conflict.
**Resolution:** Proposed notes SHOULD surface, but with a distinct marker: "(proposed — unreviewed)" in the reasoning tag. This gives Claude access to the information (no missed value) while making the provisional status visible (no false confidence). The `lifecycle: proposed` filter in resurface.py should be changed to a cosmetic distinction, not an exclusion.

**Assumption: vault-maintain reliably runs when thresholds are hit.**
Verdict: **Unreliable.** The auto-invocation directive says "run /vault-maintain unless the user's request is urgent." Claude will likely judge most requests as more urgent than maintenance. Proposed notes accumulate.
**Fix:** Add a hard ceiling: if proposed count exceeds 10, resurface.py prepends a prominent warning: "⚠ 10+ unreviewed vault notes. Vault capture paused until /vault-maintain runs." And the CLAUDE.md capture protocol should check: "Do not propose new captures if 10+ proposed notes exist. Instead, suggest running /vault-maintain."

**Assumption: The index provides value at 6 notes.**
Verdict: **Investment, not payoff.** At 6 notes, file scanning takes milliseconds. The index adds build-index.py, a new frontmatter field, sync considerations, and JSON parsing — for zero performance gain at current scale. The value is structural: bidirectional links, lifecycle tracking, keywords. These are foundational for the 20+ note vault. The plan should be honest that this is building infrastructure, not solving a current bottleneck.

**Assumption: capture-signals.md can guide Claude consistently.**
Verdict: **Highest-leverage artifact, highest risk.** If this document is vague ("capture important insights"), captures will be noisy. If it's too strict ("only capture if 3+ criteria match"), captures will be sparse. The quality of the entire system depends on this one file.
**Mitigation:** capture-signals.md should include concrete examples and anti-examples. "Capture this: We discovered that the API rate limits at 100/min, not 1000/min as documented, which changes the retry strategy." "Don't capture this: We fixed a typo in a config file."

**Assumption: JSON index is human-readable enough.**
Verdict: **Fine.** The user views notes in Obsidian (markdown), not the index. The index is for Python scripts and Claude. JSON is the right format — stdlib, no dependencies, fast to parse.

### Revised Decisions After Stress Test

1. `lifecycle` field goes in markdown frontmatter (Gap 1 resolution confirmed)
2. Index format is JSON, not YAML (Gap 2 resolution confirmed)
3. Proposed notes surface with "(proposed)" tag, not hidden (stress test override)
4. Hard ceiling: 10+ proposed notes → capture pauses, maintenance forced
5. Natural pause points defined explicitly in capture-signals.md
6. SessionEnd index rebuild (Phase 2) should be implemented sooner than originally planned — it's the only deterministic safety mechanism

---

## Verification

### Test 1: Index Generation
1. Run `python3 scripts/build-index.py` against current vault (6 notes)
2. Verify `vault/_meta/index.json` is created with correct JSON structure
3. Verify all notes are indexed with correct types, statuses, lifecycle, keywords
4. Verify bidirectional links: `links_in` computed correctly from other notes' `[[wikilinks]]`
5. Verify `last_maintained` and `notes_since_maintenance` fields present
6. Verify `lifecycle` field read from markdown frontmatter (not hardcoded)

### Test 2: Capture Protocol Works
1. Start a session, work on something complex
2. Verify Claude proposes a vault capture at a natural pause point (AskUserQuestion with options)
3. Approve via AskUserQuestion
4. Verify note appears in correct type directory with `#status/unverified` and `lifecycle: proposed` in frontmatter
5. Verify index.json updated: new entry with lifecycle, keywords, bidirectional links
6. Verify note links to existing vault notes via `[[wikilinks]]`

### Test 3: Enhanced Surfacing + Threshold Warnings
1. Start session in a project directory
2. Verify resurface.py reads from index.json (not file scanning)
3. Verify active notes surface with reasoning tags: "(working)", "(recent)", etc.
4. Verify `lifecycle: proposed` notes surface with "(proposed — unreviewed)" tag (not hidden)
5. Set `notes_since_maintenance: 5` in index → verify maintenance warning appears
6. Set proposed count to 10+ → verify prominent "capture paused" warning appears

### Test 4: Vault-Maintain with Proposed Note Review
1. Create 3+ notes with `lifecycle: proposed` in frontmatter
2. Run `/vault-maintain`
3. Verify Step 0 runs `python3 scripts/build-index.py` to rebuild index
4. Verify Step 0.5 presents each proposed note via AskUserQuestion (promote/merge/delete)
5. Approve a promotion → verify frontmatter changes to `lifecycle: active`, status to `#status/working`
6. Verify index rebuilt after promotions, `notes_since_maintenance` resets, `last_maintained` updates

### Test 5: Graceful Degradation
1. Delete `vault/_meta/index.json`
2. Start a new session → verify resurface.py falls back to file-scanning (current behavior, no crash)
3. Run `/vault-maintain` → verify index is rebuilt from scratch
4. Create a malformed note (broken frontmatter) → verify build-index.py skips it with warning, other notes indexed correctly

### Test 6: Hard Ceiling Enforcement
1. Create 10+ notes with `lifecycle: proposed` in frontmatter
2. Start a session → verify resurface.py shows prominent warning about pausing captures
3. Verify CLAUDE.md directive: Claude should suggest /vault-maintain instead of new captures
4. Run /vault-maintain, promote some notes → verify captures resume normally
