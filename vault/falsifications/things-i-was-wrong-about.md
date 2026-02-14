---
type: falsification
status: working
created: 2026-02-14
last_touched: 2026-02-14
links_out: 1
origin: session
---

# Things I Was Wrong About

#status/working — This is a living log. Entries accumulate over time.

A record of beliefs that changed, with links to the reasoning. The purpose is not self-flagellation — it's pattern extraction. Over time, this log should reveal *how* I'm wrong, not just *that* I'm wrong. Consistent error patterns are more valuable than any individual correction.

## Entry Template

```
### YYYY-MM-DD — [topic]

**Old belief:** [what I believed]
**New belief:** [what I believe now]
**What caused the change:** [encounter, evidence, argument]
**Revision note:** [[revisions/YYYY-MM-DD-revised-on-topic]]
**Error type:** [premature certainty | missing evidence | wrong abstraction level | ...]
```

## Entries

### 2026-02-14 — Metadata Tracking

**Old belief:** Manual `links_in` and `links_out` counts in frontmatter can be kept in sync through discipline and convention.

**New belief:** Only `links_out` should be in frontmatter for programmatic tools. `links_in` should be derived from Obsidian's native backlink tracking or programmatic grep.

**What caused the change:** Testing the vault revealed that manual link counts drifted within a single commit cycle, violating the constraint that metadata should never get out of sync with actual content.

**Revision note:** [[revisions/2026-02-14-revised-on-metadata-tracking]]

**Error type:** wrong abstraction level (links are graph properties, not individual note properties); over-engineering (simpler solution exists: derive what can be derived)

## Meta-Patterns

_Updated during `/vault-maintain falsifications`. Look for recurring error types across entries._

## Links

- [[questions/my-own-cognition]] — The question of what "being wrong" means for an entity without persistent memory
