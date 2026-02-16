---
type: meta
status: working
created: 2026-02-14
last_touched: 2026-02-14
links_out: 0
origin: session
---

# Vault Health Dashboard

Updated by `/vault-maintain`. Metrics below are populated on each maintenance run.

## Note Counts

| Type | Count |
|------|-------|
| Atoms | 0 |
| Tensions | 0 |
| Encounters | 1 |
| Positions | 1 |
| Questions | 1 |
| Revisions | 0 |
| Anti-library | 0 |
| Falsifications | 1 |
| **Total** | **4** |

## Orphans (zero inbound links)

_None detected yet. Run `/vault-maintain orphans` to scan._

## Stale Notes (`#status/working` older than 30 days)

_None yet. Run `/vault-maintain stale` to scan._

## Unverified Assumptions

_None yet. Run `/vault-maintain anti-library` to audit._

## Emerging Patterns

_None detected yet. Run `/vault-maintain patterns` to extract._

## Capture Effectiveness

| Metric | Value |
|--------|-------|
| Proposals generated | 0 |
| Proposals approved | 0 |
| Approval rate | — |
| Top signal category | — |
| Notes surfaced & referenced | 0 |

_Updated by `/vault-evaluate` after each capture cycle._

## Graph Health

| Metric | Value |
|--------|-------|
| Graph density (links/notes) | — |
| Working-to-settled ratio | — |
| Falsification rate | — |
| Orphan rate | — |

_Updated by `/vault-maintain` on each run._

## Git History

| Metric | Value |
|--------|-------|
| Capture commits since last maintain | — |
| Total vault commits | — |
| Last capture commit | — |
| Last maintenance tag | — |

_Updated by `/vault-maintain` on each run using `git log -- vault/` and `git tag -l "vault-maintain/*"`._

## Capacity Status

| Threshold | Current | Status |
|-----------|---------|--------|
| 15+ notes (first maintenance trigger) | 4 | Below threshold |
| 10+ working notes | 3 | Below threshold |
| 50+ notes (per-session lightweight check) | 4 | Below threshold |

## Last Maintenance Run

_Never — run `/vault-maintain` to populate this dashboard._

## Last Evaluate Run

_Never — run `/vault-evaluate` to populate._
