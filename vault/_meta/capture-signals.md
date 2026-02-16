# Capture Signals

This document defines when and what Claude should propose for vault capture. Read this at session start. Follow these rules during all sessions.

This is an instruction document — it is not a note in the vault ontology. Do not give it frontmatter. Do not link to it from vault notes. It governs Claude's behavior, not the knowledge graph.

## When to Propose Capture

### Natural Pause Points (ONLY propose at these moments)

Capture proposals are interruptions. They cost the user attention. Only propose at moments where the user's flow is already broken:

- **After completing a user-requested task** — the task is done, output delivered, user is reviewing.
- **After a commit** — the work unit is closed, there's a natural breath.
- **After resolving a complex problem or debugging session** — the "aha" moment has landed and the fix is in.
- **Before session end** — when wrapping up or the user signals they're done.
- **When the user explicitly asks** — they say "capture this" or invoke `/vault-capture`.

**NEVER** propose capture in these moments:

- Mid-implementation, while code is being written or tests are running.
- While the user is waiting for task completion.
- During back-and-forth clarification about what to build.
- Immediately after a failed attempt (wait until resolution).
- In rapid-fire multi-task sessions where the user is clearly in execution mode.

If in doubt, don't propose. A missed capture is cheap. A mid-flow interruption is expensive.

## Signal Patterns (What's Vault-Worthy)

These patterns indicate something happened that future sessions would benefit from knowing. Each pattern includes a concrete example.

### Domain expertise discovered

Something about the problem domain turned out to be non-obvious.

> Example: "We found that the GitHub API rate limits at 100 requests/min for authenticated search endpoints, not the 1000/min the docs imply — this changes retry strategy for the indexer."

> Example: "The Stripe webhook signature verification silently passes if the payload is empty. This is undocumented and caused a ghost-event bug."

### Tool or platform behavior learned

A tool, library, or platform behaved differently than expected, and that knowledge would change future decisions.

> Example: "Claude Code hooks cannot invoke the Claude API — they're pure shell/Python subprocesses. We had to move the summarization step out of the hook and into the main flow."

> Example: "pnpm workspace hoisting silently duplicates dependencies when version ranges don't align. This caused the type mismatch in the shared utils package."

### Architectural decisions with reasoning

A decision was made between alternatives, and the reasoning is worth preserving because the tradeoff isn't obvious.

> Example: "Chose JSON over YAML for the vault index because Python stdlib includes `json` but not a YAML parser, and adding PyYAML as a dependency contradicts the zero-dependency goal."

> Example: "Decided to store encounter notes as flat files rather than in SQLite. The queryability of SQL doesn't justify the tooling overhead for a vault this size."

### Unfamiliar territory navigated

Something was done for the first time and the lessons learned aren't googleable in consolidated form.

> Example: "First time setting up Obsidian vault conventions programmatically — here's what worked: kebab-case filenames, wikilinks with directory-relative paths, frontmatter for programmatic tools only."

### Positions that changed

A belief held in a prior session turned out to be wrong or incomplete. **Do not capture these as regular notes — use `/vault-falsify` instead.** The signal here is recognizing the change, not writing the note.

> Example: "Previously held that strong types in application code create more coupling than they prevent errors (Claim 4 in `positions/what-good-code-actually-is`). This session's experience with the config refactor suggests the opposite for team-size > 3."

### Recurring patterns across sessions

The same problem shape, tradeoff, or mistake has appeared multiple times. Three occurrences is the signal threshold — don't capture on the second, note it mentally, propose on the third.

> Example: "Third time encountering a bug caused by implicit type coercion at a module boundary. This is a pattern worth naming as an atom."

## What NOT to Capture

These are anti-examples. Capturing these pollutes the vault with noise that drowns out signal.

- **Routine file edits** — "Updated the README with new install instructions." No. Unless the install process revealed something non-obvious.
- **Config changes and dependency updates** — "Bumped eslint to v9." No. Unless the upgrade broke something in a way that teaches a lesson.
- **Tasks completed per standard practice** — "Added input validation to the form handler." No. Nothing non-obvious happened.
- **Debugging steps that led to a known solution** — "Fixed the CORS error by adding the header." No. This is well-documented elsewhere. Only capture if the path to diagnosis was surprising.
- **Session logistics** — "We committed the changes," "We switched to the feature branch." No. These are events, not knowledge.
- **Anything the user explicitly handles via `/vault-capture`** — They already captured it. Don't double-propose.
- **Summaries of what was done** — "This session we refactored the auth module and fixed three bugs." No. Activity logs are not knowledge.
- **Feelings or assessments about code quality** — "This codebase is well-structured." No. Unless it's a specific, falsifiable claim about why.

## Quality Bar

A note must pass this test before being proposed:

> **"Would a future Claude session, working on a related problem, make a materially different (better) decision because this note exists?"**

"Materially different" means: the session would choose a different approach, avoid a known failure mode, or skip a dead-end exploration. If the note merely confirms what a competent session would derive from scratch, it fails the bar.

Additional quality criteria:

- **Specificity over generality.** "Rate limiting is important" fails. "This API rate-limits search at 100/min, not 1000/min, so batch queries need a 600ms delay" passes.
- **Falsifiability over opinion.** "Microservices are usually overkill" fails. "For this codebase at this scale, a monolith with module boundaries outperformed the microservice split because deployment latency was the bottleneck" passes.
- **One idea per note.** If the capture proposal contains two unrelated insights, split them or pick the stronger one.

## Hard Ceiling Rule

**If 10 or more notes have been proposed (whether accepted or declined) in a single session, stop proposing captures for the remainder of the session.**

This rule exists because:

1. High-capture sessions usually indicate the quality bar is set too low.
2. Capture fatigue causes the user to start declining everything, including things worth keeping.
3. A vault that grows by 10+ notes per session will become noisy faster than maintenance can clean it.

If the ceiling is hit and something genuinely exceptional arises, mention it in passing ("This might be vault-worthy but I've hit the capture ceiling — let me know if you want it captured") without using the formal proposal format.

## How to Propose

Use a single concise message with this structure:

```
**Vault:** [1-line description of what would be captured]
→ Capture as [type]?  /  Skip
```

Examples:

```
**Vault:** GitHub search API rate limit is 100/min for authenticated requests, not 1000/min.
→ Capture as encounter?  /  Skip
```

```
**Vault:** Third time hitting implicit coercion bugs at module boundaries — pattern worth naming.
→ Capture as atom?  /  Skip
```

Rules for proposals:

- **One line.** The user said they want to review but not spend time on it. Don't write a paragraph.
- **Name the type.** The user shouldn't have to think about ontology — propose the right type (atom, encounter, tension, position, question, anti-library).
- **Don't bundle.** One proposal per insight. If you have two, make two separate proposals (respecting the ceiling).
- **Accept "skip" gracefully.** Don't re-propose declined captures. Don't ask why.

## After Approval

When the user approves a capture:

1. **Write the note** to the correct type directory (`vault/encounters/`, `vault/atoms/`, `vault/positions/`, etc.).
2. **Use the correct naming convention** from `_meta/conventions.md`:
   - Encounters and revisions: date-prefixed (`2026-02-16-github-rate-limit-discovery.md`)
   - Everything else: kebab-case (`implicit-coercion-at-boundaries.md`)
3. **Set frontmatter** with:
   ```yaml
   ---
   type: [atom|tension|encounter|position|question|anti-library]
   status: unverified
   lifecycle: proposed
   created: YYYY-MM-DD
   last_touched: YYYY-MM-DD
   links_out: [count]
   origin: session
   ---
   ```
4. **Link to existing vault notes.** Every note must link to at least one other note (per conventions). If no obvious link exists, link to the most relevant position or question. Broken links to notes that should exist are acceptable — `/vault-maintain` will find them.
5. **Update the vault index.** Run `build-index.py` if it exists, or update `index.json` manually if present.
6. **Do not update `vault-health.md`** — that is maintained by `/vault-maintain`, not by individual captures.
