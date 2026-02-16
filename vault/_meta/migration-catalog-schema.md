# Migration Catalog Schema

This document defines the JSON schema for `vault/_meta/migration-catalog.json`, the intermediate format used when migrating notes from external vaults into this cognitive vault.

This is a reference document — it is not a note in the vault ontology. Do not give it frontmatter. Do not link to it from vault notes.

## Overview

The migration catalog is an ephemeral file that exists during a migration and is archived or deleted after completion. It is created interactively by Claude during Phase 1 (triage) and consumed deterministically by `scripts/migrate-execute.py` during Phase 2 (execution).

## Schema

```json
{
  "version": "1.0",
  "source_path": "/absolute/path/to/source/vault",
  "created": "YYYY-MM-DD",
  "batch_size": 8,
  "link_map": {},
  "notes": [],
  "progress": {
    "processed": 0,
    "current_batch": 1
  }
}
```

## Field Reference

### Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | string | yes | Schema version. Currently `"1.0"`. |
| `source_path` | string | yes | Absolute path to the source vault root. Note `source` paths are resolved relative to this. |
| `created` | string | yes | ISO date when the catalog was created. |
| `batch_size` | integer | yes | Max notes processed per execution run. Default `8` (buffer of 2 below the hard ceiling of 10 proposed notes). |
| `link_map` | object | yes | Global wikilink rewriting table. See Link Map below. |
| `notes` | array | yes | Array of note entries. See Note Entries below. |
| `progress` | object | yes | Execution checkpoint for resumability. See Progress below. |

### Link Map

Maps source wikilinks to target vault paths. Applied as global string replacement during execution.

```json
{
  "[[Source Note Title]]": "[[positions/target-note-name]]",
  "[[Another Note]]": "[[atoms/hyrums-law]]",
  "[[Irrelevant Daily Log]]": null,
  "[[Unknown Ref]]": "[[Unknown Ref]]"
}
```

**Four cases:**

| Source Value | Target Value | Behavior |
|-------------|-------------|----------|
| `"[[X]]"` | `"[[dir/name]]"` | Rewrite to vault-relative path |
| `"[[X]]"` | `null` | Convert to plain text (strip brackets) |
| `"[[X]]"` | `"[[X]]"` | Leave as broken link (vault-maintain catches it) |
| Not in map | — | Left unchanged |

Keys and non-null values must include the full `[[` and `]]` delimiters.

### Note Entries

Each entry represents one source note and what to do with it.

```json
{
  "source": "relative/path/to/note.md",
  "action": "import",
  "type": "position",
  "filename": "target-note-name.md",
  "reason": "Falsifiable claim about X with evidence"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source` | string | yes | Path to source file, relative to `source_path`. |
| `action` | string | yes | One of: `import`, `skip`, `merge`. |
| `type` | string | import only | Vault ontology type: `atom`, `tension`, `encounter`, `position`, `question`, `revision`, `anti-library`, `falsification`. |
| `filename` | string | import only | Target filename in kebab-case. Date-prefixed for encounters/revisions per conventions. |
| `reason` | string | yes | Why this note was accepted, skipped, or merged. Audit trail. |
| `merge_target` | string | merge only | Vault-relative path (no .md) of the note to merge into, e.g. `positions/what-good-code-actually-is`. |

**Actions:**

- **`import`** — Transform and write to vault. Processed by `migrate-execute.py`.
- **`skip`** — Do nothing. Kept in catalog as audit trail.
- **`merge`** — Combine with existing vault note. NOT processed by the script — requires Claude to handle interactively in Phase 3.

### Progress

Execution checkpoint. Updated by `migrate-execute.py` after each batch.

```json
{
  "processed": 0,
  "current_batch": 1
}
```

| Field | Type | Description |
|-------|------|-------------|
| `processed` | integer | Number of import notes processed so far. Script resumes from this index. |
| `current_batch` | integer | Current batch number (for display). |

## Workflow

### Phase 1: Claude Triage (Interactive)

1. User provides source vault path.
2. Claude scans source with Glob/Read to understand structure.
3. For each source note, Claude reads content, applies quality bar, classifies type, checks for overlap, proposes action via AskUserQuestion.
4. Claude builds the link_map as wikilinks are encountered.
5. Claude writes completed catalog to `vault/_meta/migration-catalog.json`.

### Phase 2: Deterministic Execution (Script)

```bash
python3 scripts/migrate-execute.py           # execute next batch
python3 scripts/migrate-execute.py --dry-run  # preview without writing
python3 scripts/migrate-execute.py --batch-size 4  # override batch size
```

For each `action: import` note in the current batch:
1. Read source file
2. Strip existing frontmatter
3. Apply link_map rewrites
4. Generate vault frontmatter (`lifecycle: proposed`, `origin: migration`, `status: unverified`)
5. Write to `vault/{type_dir}/{filename}`
6. Update progress in catalog

After batch: run `python3 scripts/build-index.py` to update the vault index.

### Phase 3: Review & Merge (Claude Session)

1. Run `/vault-maintain` to review proposed notes.
2. Handle merge candidates interactively.
3. Re-run `migrate-execute.py` for next batch.
4. Repeat until complete.
5. Archive or delete the catalog.

## Example Catalog

```json
{
  "version": "1.0",
  "source_path": "/Users/me/old-vault",
  "created": "2026-02-15",
  "batch_size": 8,
  "link_map": {
    "[[API Design Principles]]": "[[positions/api-design-principles]]",
    "[[Daily 2025-12-01]]": null,
    "[[Hyrum's Law]]": "[[atoms/hyrums-law]]"
  },
  "notes": [
    {
      "source": "notes/api-design.md",
      "action": "import",
      "type": "position",
      "filename": "api-design-principles.md",
      "reason": "3 falsifiable claims about REST vs GraphQL tradeoffs with project evidence"
    },
    {
      "source": "daily/2025-12-01.md",
      "action": "skip",
      "reason": "Daily log, no extractable insights"
    },
    {
      "source": "notes/abstraction-costs.md",
      "action": "merge",
      "merge_target": "positions/what-good-code-actually-is",
      "reason": "Adds evidence for Claim 1 (abstraction threshold)"
    }
  ],
  "progress": {
    "processed": 0,
    "current_batch": 1
  }
}
```
