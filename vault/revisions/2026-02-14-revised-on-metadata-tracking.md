---
type: revision
status: settled
created: 2026-02-14
last_touched: 2026-02-14
links_out: 2
origin: session
---

# Revised: Manual Metadata Tracking Drifts Immediately

#status/settled #meta/revision

## What I Believed Before

Frontmatter should include both `links_in` and `links_out` counts to maintain programmatic access to graph topology. Manual tracking of these counts is sustainable if enforced by discipline and convention.

**Old note reference:** The initial vault design in [[encounters/2026-02-14-designing-the-cognitive-vault]] included `links_in` in all frontmatter.

## What I Believe Now

Only `links_out` should be tracked in frontmatter (for programmatic consumers like the resurface hook). `links_in` should be derived from actual backlinks using Obsidian's native graph tracking or programmatic grep of `[[wikilinks]]`. Manual link counts drift immediately because they duplicate information already present in the note content.

**New principle:** Any metadata that can be derived from source content should not be manually maintained in frontmatter. Duplication creates a synchronization problem.

## What Caused the Change

[[encounters/2026-02-14-designing-the-cognitive-vault]] documented the vault's evolution and noted: "Manual metadata drifts immediately. The `links_in` and `links_out` counts were wrong by the second commit."

This observation came from adversarial review of the vault against its own design principles. When the vault was tested against realistic use, manual link counts became incorrect within a single commit cycle.

## Why the Old Belief Was Wrong

### The Synchronization Problem

I assumed that convention (always update links_in/links_out when modifying a note) would prevent drift. But conventions require discipline, and discipline fails under time pressure. In a real development workflow:
- You modify a note, update the backlinks section, but forget to update links_in in the old notes
- You create a new link but don't increment links_out
- You refactor a note and delete a link, forgetting the decrement

The cost of maintaining accuracy is higher than the benefit of having it in frontmatter.

### The Duplication Insight

Once I recognized that `links_out` can be derived by counting `[[wikilinks]]` in the note content, it became obvious that `links_in` could similarly be derived from grep searches across all notes. Why maintain manual counts at all?

The correct design is:
- **Frontmatter:** Portable, immutable, programmatic metadata (type, status, origin, links_out)
- **Obsidian graph:** Visual, bidirectional, always-in-sync metadata (backlinks)
- **Programmatic derivation:** For tools that need accurate counts (resurface.py counts actual `[[` occurrences)

## Error Type

**Wrong abstraction level** — I abstracted the concept of "link counts" into frontmatter when links are inherently a property of the note graph, not the individual note. The abstraction was at the wrong boundary.

Secondary: **Over-engineering** — I designed for robustness (manual counts in frontmatter) before discovering a simpler solution (derive what can be derived).

## Practical Impact

This revision required:
1. Removing `links_in` from all vault note frontmatter
2. Updating `resurface.py` to count `[[` occurrences instead of reading frontmatter
3. Moving utility scripts from `vault/scripts/` to repo-level `scripts/` to keep the vault directory pure content

The refactored approach is simpler, more maintainable, and always accurate.

## Links

- [[encounters/2026-02-14-designing-the-cognitive-vault]] — Where this issue was first documented
- [[_meta/conventions]] — The conventions that should have caught this earlier
