---
name: vault-maintain
description: Run vault maintenance — orphan scan, staleness check, pattern extraction
argument-hint: "[full|diff|orphans|stale|patterns|anti-library|falsifications]"
---

<objective>
Run periodic maintenance on the cognitive vault at `vault/`. Can run the full suite or individual checks. The vault is a knowledge graph — maintenance keeps it healthy, connected, and honest.

Input: optional focus area (defaults to full).
Argument: $ARGUMENTS
</objective>

<process>

## Step 0: Read Conventions

<step name="read_conventions">
Read `vault/_meta/conventions.md`. This is mandatory before any vault operation.
</step>

## Step 1: Vault Diff Report

<step name="vault_diff_report">
**Skip if** `$ARGUMENTS` specifies a focus area that isn't `diff` or `full`.

Use git history to show what changed in the vault since the last maintenance run. This gives observability into vault evolution over time.

1. **Find the last maintenance checkpoint:**
   ```
   git tag -l "vault-maintain/*" --sort=-version:refname | head -1
   ```
   If no maintenance tag exists, use the first vault commit:
   ```
   git log --reverse --oneline -- vault/ | head -1
   ```

2. **Show capture commits since last checkpoint:**
   ```
   git log --oneline {last_tag_or_first_commit}..HEAD -- vault/
   ```
   Count: total commits, capture commits (matching `vault(capture):`), other vault commits.

3. **Show structural changes:**
   ```
   git diff --stat {last_tag_or_first_commit} -- vault/
   ```
   From this, extract:
   - Notes added (new files)
   - Notes modified (changed files)
   - Notes deleted (removed files, if any)

4. **Summarize for the report:**
   - "Since last maintenance ({date or 'never'}): {n} vault commits, {m} notes added, {p} notes modified"
   - List the new note paths and their types
   - If no changes since last maintenance, say so — that's also useful information

This step is informational only — it modifies nothing. Its output feeds into Step 8 (Report).
</step>

## Step 2: Orphan Scan

<step name="orphan_scan">
**Skip if** `$ARGUMENTS` specifies a focus area that isn't `orphans` or `full`.

Find notes with zero inbound links:

1. Use Glob to list all `vault/**/*.md` files (excluding `_meta/` and `scripts/`)
2. For each note, extract its filename stem (e.g., `what-good-code-actually-is`)
3. Use Grep to search all other vault `.md` files for `[[filename]]` or `[[path/filename]]` references
4. Notes with zero inbound references are orphans

For each orphan, report:
- The file path
- Its type and status from frontmatter
- Suggest: connect to an existing note, or delete if it adds no value

Do not delete automatically. Present findings and let the user decide.
</step>

## Step 3: Staleness Check

<step name="staleness_check">
**Skip if** `$ARGUMENTS` specifies a focus area that isn't `stale` or `full`.

Find notes tagged `#status/working` with `last_touched` older than 30 days:

1. Use Grep to find files containing `status: working` in frontmatter
2. Parse `last_touched` date from frontmatter
3. Flag notes where `last_touched` is more than 30 days ago

For each stale note, present options:
- **Resolve**: The question has been answered or the position has settled → update status
- **Revise**: The thinking has evolved → edit the note, update `last_touched`
- **Mark dormant**: No longer actively relevant → change to `#status/dormant`

Update frontmatter `last_touched` date for any notes modified.
</step>

## Step 4: Pattern Extraction

<step name="pattern_extraction">
**Skip if** `$ARGUMENTS` specifies a focus area that isn't `patterns` or `full`.

Review encounter notes from the last 30 days:

1. Use Glob to find `vault/encounters/*.md`
2. Parse frontmatter for `created` date, filter to last 30 days
3. Extract `[[wikilinks]]` from each encounter's body
4. Count which atoms/tensions appear across multiple encounters
5. If a concept appears in 3+ encounters, flag it as an emerging pattern

For each emerging pattern:
- Name it
- List the encounters that reference it
- Suggest: create a new atom or position note if the pattern is significant enough to name

Also look for:
- **Encounters linking to zero tensions** → experiences not yet learned from
- **Atoms with only one inbound link** → concepts not yet stress-tested
- **Dense but disconnected clusters** → potential silos needing bridges
</step>

## Step 5: Anti-Library Audit

<step name="anti_library_audit">
**Skip if** `$ARGUMENTS` specifies a focus area that isn't `anti-library` or `full`.

Review notes tagged `#status/unverified`:

1. Use Grep to find files containing `status: unverified`
2. For each, check if related encounters or positions now provide evidence
3. If evidence exists: recommend promoting to atom (verified) or falsifying
4. If no evidence: leave as is, note how long it has been unverified

Present findings. Do not auto-promote or auto-falsify.
</step>

## Step 6: Falsification Review

<step name="falsification_review">
**Skip if** `$ARGUMENTS` specifies a focus area that isn't `falsifications` or `full`.

Read `vault/falsifications/things-i-was-wrong-about.md`:

1. Count total entries
2. If 3+ entries exist, look for meta-patterns:
   - Am I consistently wrong about the same type of thing?
   - Do errors cluster around specific domains or note types?
   - Is there a recurring error type (premature certainty, missing evidence, wrong abstraction level)?
3. Document any meta-patterns found

If meta-patterns are identified, suggest adding them as a `#meta/pattern` note in `vault/atoms/`.
</step>

## Step 7: Update Vault Health and Checkpoint

<step name="update_health">
Update `vault/_meta/vault-health.md` with current metrics:

1. Count notes by type (use Glob for each directory)
2. List orphans found in Step 2
3. List stale notes found in Step 3
4. List unverified assumptions from Step 5
5. Summarize emerging patterns from Step 4
6. Update the Git History section with data from Step 1
7. Record the date of this maintenance run

Use Edit to update the file in place, preserving the dashboard format.

8. **Create maintenance checkpoint:**
   Stage and commit the health dashboard and any vault notes modified during maintenance:
   ```
   git add vault/_meta/vault-health.md
   ```
   If any vault notes were modified (e.g., staleness updates to `last_touched`, status changes):
   ```
   git add vault/
   ```
   Guard against empty commit:
   ```
   git diff --cached --quiet || git commit
   ```
   Commit message format:
   ```
   vault(maintain): health check — YYYY-MM-DD

   Vault: {total} notes ({working} working, {settled} settled)
   Orphans: {n} found
   Stale: {n} found
   Patterns: {n} emerging
   ```

9. **Tag the maintenance checkpoint:**
   ```
   git tag "vault-maintain/YYYY-MM-DD"
   ```
   If a tag for today already exists (multiple maintenance runs in one day), append a counter:
   ```
   git tag "vault-maintain/YYYY-MM-DD-2"
   ```
   Check first: `git tag -l "vault-maintain/YYYY-MM-DD"` — if it exists, increment the suffix.

   This tag is what Step 1 (Vault Diff Report) uses to find the last maintenance boundary.
</step>

## Step 8: Report

<step name="report">
Present a summary to the user:

- **Git history summary** (from Step 1): commits since last maintenance, notes added/modified/deleted
- Total notes by type
- Orphans found (with suggested actions)
- Stale notes found (with suggested actions)
- Emerging patterns identified
- Unverified assumptions needing attention
- Falsification meta-patterns (if any)
- Overall vault health assessment
- Git commit and tag created for this maintenance run (show short SHA and tag name)

End with: "The vault health dashboard has been updated at `vault/_meta/vault-health.md`. Maintenance checkpoint tagged as `vault-maintain/YYYY-MM-DD`."
</step>

</process>

<rules>
## Hard Rules

1. **Read conventions first.** Always read `vault/_meta/conventions.md` before any operation.
2. **Never delete without checking backlinks.** A note that looks orphaned might be referenced by notes not yet scanned.
3. **Never auto-modify.** Present findings and let the user decide on changes. The only auto-updates are `vault-health.md` and the git checkpoint.
4. **Update `last_touched` on any note you modify.** Always use today's date.
5. **Pattern names become atoms.** If a pattern is significant enough to name, create a note for it in `vault/atoms/`.
6. **Preserve links.** When marking a note dormant, do not remove its outbound links — they may still be valuable for graph topology.
7. **Report everything.** No silent changes. Every modification is documented in the maintenance report.
8. **Tag every maintenance run.** The git tag is the boundary marker for diff reports. Always create it, even if no changes were made.
</rules>
