# /vault-maintain — Vault maintenance cycle

Read `vault/_meta/conventions.md` for the full ontology and rules before proceeding.

## Steps

### Step 0: Rebuild the index

Run via Bash: `python3 scripts/build-index.py`

This ensures the index reflects the current state of all vault files before any analysis.

### Step 1: Review proposed notes

Read `vault/_meta/index.json`. Find all notes with `lifecycle: proposed`.

For each proposed note:
1. Read the note file
2. Present it to the user via AskUserQuestion with options:
   - "Promote to active" — Change frontmatter `lifecycle: active`, `status: working`
   - "Merge with [existing note]" — Integrate content into an existing note, then delete the proposed note
   - "Delete — low value" — Delete the file
3. Execute the user's choice. If promoting, edit the note's frontmatter in place.

### Step 2: Orphan scan

From the index, find notes with zero `links_in` AND zero `links_out` (true orphans). Also find notes with zero `links_in` only (no inbound connections).

Report orphans to the user. For each:
- Suggest a link target, or
- Ask if the note should be connected or deleted

### Step 3: Staleness check

Find notes where `status: working` and `last_touched` is older than 30 days.

For each stale note, ask the user via AskUserQuestion:
- "Still working on this" — Update `last_touched` to today
- "Mark as settled" — Change `status: settled`
- "Mark as dormant" — Change `status: dormant`, `lifecycle: dormant`

### Step 4: Broken link scan

From the index, check each note's `links_out`. If a link target doesn't exist as a key in the index, it's a broken link.

Report broken links grouped by target. For each broken target that appears 2+ times:
- Suggest creating the missing note (it's clearly wanted)
- Ask the user if they want to create it now via `/vault-capture`

### Step 5: Pattern extraction

Look at the vault graph topology from the index:
- Which notes have the most inbound links? (hub notes)
- Are there clusters of notes that link to each other but not to the rest? (islands)
- Are there notes that bridge between clusters? (bridge notes)

Report any patterns worth naming as atoms or tensions.

### Step 6: Update health dashboard and index

1. Run via Bash: `python3 scripts/build-index.py` (rebuild after all changes)
2. Read the rebuilt index
3. Update `vault/_meta/vault-health.md` with current counts per type, orphan list, stale list, and timestamp
4. Note: the index's `last_maintained` field should be updated. Edit `vault/_meta/index.json` directly to set `last_maintained` to today's date and `notes_since_maintenance` to 0.
