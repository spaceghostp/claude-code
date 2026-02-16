---
name: vault-evaluate
description: Detect vault-worthy signals and propose captures for human approval
argument-hint: "[summary of session context, or leave blank for auto-detection]"
---

<objective>
Autonomously detect vault-worthy insights from the current session and present them to the human for approval before committing to the vault. This is signal-based capture — Claude extracts, the human validates.

Uses Haiku subagents for broad, parallel signal detection. Nothing enters the vault without explicit human approval.

Input: optional session context summary.
Argument: $ARGUMENTS
</objective>

<process>

## Step 0: Read Requirements

<step name="read_requirements">
Read both of these — every time, no exceptions:
1. `vault/_meta/conventions.md` — vault format and rules
2. `vault/_meta/capture-signals.md` — signal detection schema and categories

These define what to capture, how to format it, and what the approval flow looks like.
</step>

## Step 1: Gather Session Context

<step name="gather_context">
Build a concise summary of the current session's key content. Include:

- What was worked on (tasks, features, bugs, investigations)
- Technical decisions made and trade-offs evaluated
- Tools used and any non-obvious behaviors encountered
- Errors hit and how they were resolved
- Questions that came up and whether they were answered
- Any existing vault notes that were referenced or relevant

If `$ARGUMENTS` provides a summary, use it as the starting point but supplement with session context.

Keep the summary under 500 words — this is input for Haiku subagents, not a transcript.
</step>

## Step 2: Deploy Haiku Signal Detectors

<step name="signal_detection">
Launch **up to 4 parallel Haiku subagents** using the Task tool with `model: "haiku"`. Each agent scans the session summary for a specific signal category.

**Agent 1: Domain & Tool Expertise**
Prompt: "You are a signal detector for a cognitive vault. Given this session summary, identify any domain expertise or tool/workflow knowledge worth preserving. Domain expertise = non-obvious technical knowledge discovered through effort. Tool knowledge = how tools actually behave, especially where behavior diverges from docs. For each signal found, return a JSON array of objects with: type (atom or encounter), title (kebab-case), summary (1-2 sentences), and suggested_links (array of existing vault note paths). If no signals found, return an empty array. Session summary: {summary}. Existing vault notes: {list of vault note paths}."

**Agent 2: Architecture & Decisions**
Prompt: "You are a signal detector for a cognitive vault. Given this session summary, identify any architectural decisions, trade-offs, project context, or constraints that would be lost between sessions. For each signal found, return a JSON array of objects with: type (encounter or position), title (kebab-case), summary (1-2 sentences), and suggested_links (array of existing vault note paths). If no signals found, return an empty array. Session summary: {summary}. Existing vault notes: {list of vault note paths}."

**Agent 3: Patterns & Contradictions**
Prompt: "You are a signal detector for a cognitive vault. Given this session summary, identify any recurring patterns, anti-patterns, or contradictions with existing positions. Contradictions are the highest-value signals. For each signal found, return a JSON array of objects with: type (atom, tension, or encounter), title (kebab-case), summary (1-2 sentences), and suggested_links (array of existing vault note paths). Also flag if any signal contradicts an existing vault note. If no signals found, return an empty array. Session summary: {summary}. Existing vault notes: {list of vault note paths and their key claims}."

**Agent 4: Open Questions & Assumptions**
Prompt: "You are a signal detector for a cognitive vault. Given this session summary, identify unresolved questions worth tracking and assumptions that were made but not verified. Questions should be ones where the answer would materially change future decisions. For each signal found, return a JSON array of objects with: type (question or anti-library), title (kebab-case), summary (1-2 sentences), and suggested_links (array of existing vault note paths). If no signals found, return an empty array. Session summary: {summary}. Existing vault notes: {list of vault note paths}."

Before launching agents, use Glob to list all `vault/**/*.md` files (excluding `_meta/`) to provide existing note paths to each agent.
</step>

## Step 3: Aggregate and Deduplicate

<step name="aggregate">
Collect results from all subagents. Deduplicate by:

1. Merge signals with overlapping titles or summaries
2. Prefer the more specific version when two signals cover the same ground
3. If a contradiction signal was detected, prioritize it (highest value)
4. Remove anything that duplicates an existing vault note's content

Sort by estimated value: contradictions first, then domain expertise, then patterns, then decisions, then questions.
</step>

## Step 4: Present for Human Approval

<step name="human_approval">
Use AskUserQuestion to present proposals for approval. This is the critical human-in-the-loop step.

**Format each proposal as an option:**
- `label`: `"{type}: {title}"` (e.g., "atom: oauth-token-race-condition")
- `description`: The 1-2 sentence summary + which vault notes it would link to

**Rules for presentation:**
- Use `multiSelect: true` — let the human approve multiple at once
- Maximum 4 options per question (AskUserQuestion limit)
- If more than 4 proposals, use multiple questions (up to 4 questions × 4 options = 16 proposals max)
- If only 1 proposal, add a second option: "Skip — nothing to capture this session"
- Group by relevance, not by type
- Always include the question header as the signal category (e.g., "Capture" or "Vault signals")

**The human should be able to approve/reject each proposal in under 5 seconds.** If a summary is too long to scan quickly, shorten it.

If the human selects "Other", they can provide custom capture instructions — follow those.
</step>

## Step 5: Write Approved Notes

<step name="write_notes">
For each approved proposal, create a vault note following the full vault-capture protocol:

1. Generate frontmatter:
```yaml
---
type: {type}
status: working
created: {today YYYY-MM-DD}
last_touched: {today YYYY-MM-DD}
links_out: 0
origin: session
---
```

2. Write substantive body appropriate to the note type (see vault-capture rules)
3. Add `[[wikilinks]]` to related existing notes
4. Link to any broken targets intentionally (they signal notes to create)
5. Update `links_out` count in frontmatter
6. Save to `vault/{type-directory}/{filename}.md`

Use date-prefix for encounters: `YYYY-MM-DD-{title}.md`
</step>

## Step 6: Commit Vault Changes

<step name="commit_changes">
If any notes were written in Step 5, create a single atomic git commit capturing this evaluate cycle.

1. Stage only the vault content files just created:
   ```
   git add vault/atoms/ vault/tensions/ vault/encounters/ vault/positions/ vault/questions/ vault/anti-library/
   ```
   **Important:** Do NOT use `git add -A` or `git add .`. Do NOT stage `vault/_meta/` — health dashboard updates are a maintenance concern, not a capture concern.

2. Guard against empty commit:
   ```
   git diff --cached --quiet || git commit
   ```

3. Commit message format:
   ```
   vault(capture): {n} notes — {type_summary}

   Notes created:
   - {path1} ({type}, {signal_category})
   - {path2} ({type}, {signal_category})

   Cycle stats: {proposed} proposed, {approved} approved, {rejected} rejected
   ```
   Where `{n}` = number of notes created, `{type_summary}` = comma-separated types (e.g., "2 atoms, 1 encounter"), and `{signal_category}` = which detector found the signal (domain, architecture, patterns, questions).

4. Do NOT push. Commit locally only. Pushing is a separate human decision.

**Skip this step entirely** if no notes were approved in Step 4.
</step>

## Step 7: Report and Track

<step name="report">
After writing and committing approved notes, display:

- Notes created (paths)
- Links added (both existing and broken/TODO)
- Proposals rejected (for awareness — these inform future signal tuning)
- Git commit created (show the short SHA and commit message subject line, or "No commit — no notes approved")
- Current vault note count (check against maintenance thresholds in capture-signals.md)

If the vault has crossed a capacity threshold, recommend running `/vault-maintain`:
- 15+ notes total → "Consider running /vault-maintain for a health check"
- 10+ working notes → "You have {n} working notes — /vault-maintain can help settle or prune"
</step>

</process>

<rules>
## Hard Rules

1. **Nothing enters the vault without human approval.** Every proposal goes through AskUserQuestion. No exceptions.
2. **Read the signal schema first.** `vault/_meta/capture-signals.md` defines what's worth capturing. Don't freelance.
3. **Bias toward capture.** When uncertain, propose it. Let the human filter. Missing a genuine insight is worse than proposing a non-insight.
4. **Keep proposals concise.** 5 seconds per approval decision. If it takes longer, the summary is too complex.
5. **Haiku for detection, Opus for maintenance.** Signal detection uses fast/cheap subagents. Deep refinement is a separate operation (`/vault-maintain`).
6. **No orphans.** Every created note must link to at least one existing note. If nothing links, create an atom for the core concept first.
7. **Tag uncertainty.** All new notes are `#status/working` unless the human explicitly says settled.
8. **Track what was rejected.** Rejected proposals are data — they help refine the signal schema over time.
9. **Respect capacity thresholds.** Check vault size after writing. Surface maintenance recommendations when thresholds are crossed.
</rules>
