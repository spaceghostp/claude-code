# Migration at Scale: 100K-1M Notes

Strategy document for migrating large external vaults. This is a reference — not a vault note. No frontmatter, no wikilinks.

## The Problem

The base migration workflow (Claude triage per note, batch_size of 8, vault-maintain between batches) cannot scale past ~200 notes. At 100K-1M notes:

- Claude can't read every note (context limits)
- A single catalog JSON with 1M entries is too large to work with
- Interactive triage per note is impossible
- A full link map won't fit comfortably in memory
- 8-note batches with vault-maintain = thousands of review cycles

## Tiered Approach

| Tier | Notes | Strategy | Human Touch |
|------|-------|----------|-------------|
| Small | 1-200 | Current workflow: interactive triage per note | Every note |
| Medium | 200-10K | Pre-filter + sample calibration + batch migration | ~100 samples + batch reviews |
| Large | 10K-100K | Partition into domains + aggressive filtering + spot-checks | ~20 samples/domain |
| Massive | 100K-1M+ | Multi-pass filtering + domain partitioning + auto-promotion | ~50 samples total |

## Phase 1: Pre-Filter (No LLM, Pure Python)

A new script (`scripts/pre-filter-vault.py`) scans source files and scores each note by structural signals. Output: one JSON line per note in `migration/_pre-filter-scores.jsonl` (streaming format — never loads full list).

### Scoring Signals

| Signal | Measurement | Max Points |
|--------|------------|------------|
| Wikilink density | links per 100 words | 30 |
| Bidirectional links | notes that link TO this note | 25 |
| Length | 200-800 words optimal | 20 |
| Recency | file mtime within 90 days | 15 |
| Heading count | ≥3 headings = structured | 10 |

### Tier-Specific Cutoffs

- **Medium**: score ≥ 40 (~30-50% reduction)
- **Large**: score ≥ 60 (~70-80% reduction)
- **Massive**: score ≥ 75 (~90-95% reduction)

A 500K-note vault at the massive tier reduces to ~25K-50K candidates.

## Phase 2: Domain Partitioning

After filtering, partition by topic cluster so each chunk is independently processable. A new script (`scripts/partition-domains.py`) groups notes by shared wikilink targets.

**Heuristic (no graph library needed):**
1. For each note, extract top 5 most-referenced wikilink targets
2. Group notes sharing ≥3 of those targets into the same domain
3. Auto-split domains exceeding 5K notes by filename prefix

Output: one catalog per domain (`migration/catalog-domain-{name}.json`). No single catalog should exceed 10K entries.

### Why Partition?

- Each domain gets its own link map (bounded, fits in memory)
- Domains can be migrated independently across sessions
- Failures in one domain don't block others
- Cross-domain links resolved in a final pass

## Phase 3: Sampling for Calibration

Before bulk migration, Claude reviews stratified samples to validate and tune the scoring.

### Sample Selection (Per Domain)

- 5 notes with score ≥ 80 (high quality)
- 5 notes with 60 ≤ score < 80 (medium quality)
- 5 notes with 40 ≤ score < 60 (borderline)
- 3 notes with score < 40 (false negative check)

**Total: ~18 per domain, max 5 domains = ~90 samples.**

### Calibration Output

`migration/_calibrated-filters.json`:

```json
{
  "global_cutoff": 65,
  "domain_overrides": {
    "programming": {"cutoff": 70, "min_links": 3},
    "philosophy": {"cutoff": 60, "min_word_count": 400}
  },
  "disabled_signals": ["recency_days"]
}
```

Claude adjusts thresholds based on which samples were accepted vs rejected. Domain-specific overrides handle different content styles (e.g., philosophy notes may be long with few links but still valuable).

## Phase 4: Migration Execution (Scaled)

### Batch Size by Tier

| Tier | Batch Size | Review Frequency |
|------|-----------|-----------------|
| Medium | 20 | Every 100 notes |
| Large | 50 | Every 500 notes |
| Massive | 100 | Every 2000 notes |

### Auto-Promotion (Large/Massive Tiers Only)

Notes with very high scores skip the `lifecycle: proposed` staging:

- **score ≥ 90**: Write with `lifecycle: active`, `status: working` (auto-promoted)
- **60-89**: Write with `lifecycle: proposed`, `status: unverified` (standard)
- **< 60**: Skip

Auto-promotion is safe because:
1. Calibration validated the scoring
2. vault-maintain still runs orphan/staleness checks
3. Falsification log handles mistakes
4. Spot-check reviews catch systematic errors

### Review Sessions

Instead of reviewing every proposed note:
1. Show summary stats: "Batch 1-500: 320 auto-promoted, 160 proposed"
2. Spot-check: 5 random auto-promoted + 10 random proposed
3. If quality holds → continue
4. If quality drops → pause, recalibrate

## Link Resolution at Scale

### Per-Domain Link Maps

Each domain builds its own link map during migration. Max size: ~5K notes × 20 links = 100K entries (fits easily in memory).

File: `migration/_linkmap-{domain}.json`

### Cross-Domain Resolution (Post-Migration)

After all domains are processed, a final script (`scripts/merge-linkmaps.py`) builds a lightweight title-to-path index:

```json
{
  "api-design-patterns": "positions/api-design-patterns",
  "cognitive-load": "atoms/cognitive-load"
}
```

This index re-scans migrated notes and rewrites any remaining broken cross-domain links. Truly broken links are left as wikilinks for vault-maintain to flag.

## Resumability

### Checkpoint File

`migration/_progress.json`:

```json
{
  "domains": {
    "programming": {"status": "completed", "notes_processed": 5000},
    "cognitive": {"status": "in_progress", "notes_processed": 1850, "last_batch": 37},
    "philosophy": {"status": "pending"}
  }
}
```

### Crash Recovery

1. Read progress → identify incomplete domain
2. Read that domain's catalog → skip to last_batch + 1
3. Resume from that batch
4. Worst case: lose last 500 notes (re-run from checkpoint)

### Checkpoint frequency: every 500 notes

After each checkpoint: update progress, rebuild domain link map, run build-index.py.

## New Scripts Needed (At Scale Only)

| Script | Purpose |
|--------|---------|
| `scripts/pre-filter-vault.py` | Structural scoring → `_pre-filter-scores.jsonl` |
| `scripts/partition-domains.py` | Co-occurrence clustering → per-domain catalogs |
| `scripts/merge-linkmaps.py` | Cross-domain link resolution (post-migration) |

These are only needed for the Large/Massive tiers. The Medium tier can use manual domain assignment and a single catalog.

## Expected Outcomes

| Source Size | Post-Filter | Post-Calibration | Final Import | Sessions |
|-------------|-------------|-------------------|-------------|----------|
| 100K | ~20K | ~12K | ~8K | 3-5 |
| 500K | ~50K | ~25K | ~15K | 5-10 |
| 1M | ~75K | ~35K | ~20K | 8-15 |

## Quality Safeguards

**False positive protection (bad notes imported):**
- Orphan detection in vault-maintain
- Staleness metric flags unlinked auto-promotions
- Spot-check reviews catch systematic scoring errors

**False negative protection (good notes missed):**
- Calibration samples include low-scoring notes
- Pre-filter scores are logged — can lower cutoffs and re-run
- Multi-tier strategy allows iterating

**Link integrity:**
- Broken links preserved as wikilinks (vault-maintain flags them)
- Cross-domain index built after all domains complete
- Link maps are idempotent — safe to rebuild

## When NOT to Use This

- Source vault has no wikilinks → link density scoring fails, use word count + headings only
- Source is not markdown → needs a format converter first (out of scope)
- Source uses non-standard link syntax → needs a custom parser in pre-filter
- Vault is >1M notes and growing → consider this a curation project, not a migration
