# WS-000-02 Roadmap Digest

> Extracted actionable residue from the 67-component adversarially-validated roadmap.
> Full roadmap (44K) lives in WS-000-02. This digest captures what future sessions need.

**Date:** 2026-02-18
**Source:** WS-000-02 roadmap.md + adversarial-dependency-critique.md + roadmap-validation-log.md

---

## 9 BUILD Implementations (from 102 analyzed across 4 repos)

The 9% extraction rate reflects a fundamental truth: Claude Code's 27 native tools cover 63% of what frameworks provide. The extractable value is in behavioral guidance and quality floors.

| Rank | Source | Implementation | Type | Tokens | VI Score |
|------|--------|---------------|------|--------|----------|
| 1 | cookbooks | Compaction Priority Hierarchy | Skill extension | +200 | 1.50 |
| 2 | cookbooks | Structured Memory Template | Skill extension | +300 | 1.00 |
| 3 | mastra | Tool Schema Conventions for MCP | Rule extension | +200 | 2.00 |
| 4 | langchain | Research Pipeline Command | New command | +400 | 1.00 |
| 5 | langchain | Memory Tiering Enhancement | Skill extension | +500 | 1.00 |
| 6 | cookbooks | Evaluator-Optimizer Command | New command | +400 | 0.375 |
| 7 | cookbooks | Tool Evaluation Criteria | Skill extension | +500 | 0.30 |
| 8 | langchain | Context Window Monitor Hook | New hook | +150 | 1.00 |
| 9 | mastra | Eval Scoring Skill | New skill | +4000 | 1.50 |

**Total token investment:** ~6,650 across 4 skill extensions, 2 new commands, 1 new hook, 1 new skill, 1 rule extension.

---

## 6 High-Severity Gaps (all deferred, all real)

| Gap | Description | Why It Matters |
|-----|-------------|----------------|
| **Test Generation Automation** | No auto-test generation, coverage tracking, or regression detection. 168 vault notes on testing but only 1 T1 component. | Genuine gap requiring implementation design |
| **Structured Error Recovery** | No retry, rollback, or circuit breaking for agent failures. 160 vault notes. | Needs concrete CC tooling mapping |
| **Secrets Management in Multi-Agent** | Symlinked .env only; no encryption, rotation, or audit trail. | Niche for single-user but real for teams |
| **Agent Sandbox Enforcement** | No file system boundaries for agents. `dangerouslyDisableSandbox` exists. | Security pattern gap |
| **Agent Execution Tracing** | No structured trace for debugging agent failures. | Requires custom observability infrastructure |
| **TeammateIdle/TaskCompleted Hooks** | v2.1.37 flagship hooks not leveraged anywhere. | Most actionable gap — should be first addition |

---

## 5 Unicorn Compositions (and their truth table)

### 1. Self-Bootstrapping Agent System
**Hooks + Skills + Memory + Setup = First-Session Competence + Continuous Learning**
New project -> setup hook -> domain context -> agent works and learns -> `/self-improve` captures learnings -> next session inherits.

- **Claimed deps:** Setup Hook, Domain Context Files, Session Self-Analysis, Hooks in Frontmatter
- **Actually needed:** Session Self-Analysis only (works today via `/self-improve`)
- **Status:** Partially implemented; most claimed dependencies are false

### 2. Async Human-Agent Factory
**File Queue + Worktrees + Agent Teams = Production Line**
Human drops requests in file -> each spawns a worktree agent -> parallel isolation -> review via detached HEAD -> merge.

- **Claimed deps:** File-Based Queue, Worktree Isolation, Builder-Validator
- **Actually needed:** File Queue only (worktrees are optimization, not prerequisite)
- **Status:** All pieces documented, not yet composed

### 3. Domain-Expert Agent via Vault RAG
**Vault + CLAUDE.md + /recall = Pre-Built Knowledge Graph**
Notes become queryable domain expertise. CLAUDE.md tells agent when to consult the vault.

- **Claimed deps:** CLAUDE.md, Expertise Files, /recall
- **Actually needed:** CLAUDE.md + /recall (Expertise Files don't exist)
- **Status:** 67% complete — claims "operational" but missing Expertise Files

### 4. Quality-First Autonomous Teams
**Multi-Layer Validation + Task Dependencies + TeammateIdle**
Skeptic reviews plan -> builders execute in dependency order -> validators verify -> hooks redistribute.

- **Actually needed:** All 3 components
- **Status:** Agent Teams available in v2.1.37; only honest Unicorn about its deps

### Summary: 4/5 Unicorns lie about dependencies
Unicorn dependencies are marketing, not architecture. Most work with fewer components than claimed.

---

## 9 Anti-Patterns (failure modes to avoid)

| # | Anti-Pattern | Evidence |
|---|-------------|----------|
| 1 | **"Never use compaction" dogma** | Conflicts with Opus 4.6 Compaction API beta. Use strategically. |
| 2 | **Unvetted agent skill marketplaces** | 26% vulnerability rate in community skills. Always sandbox. |
| 3 | **Agent teams without blockers** | Parallel agents without dependency blocking = wasted work on conflicting assumptions. |
| 4 | **All-coder agent teams** | Teams without non-coding reviewer = merge conflicts and quality issues. |
| 5 | **Staging on production vault** | Experimental scripts on production vault = data loss risk. |
| 6 | **Single-creator pattern inflation** | Apply critical filter when multiple components trace to one source. |
| 7 | **Unbounded agent spawning** | N agents without resource limits or merge conflict detection. |
| 8 | **Failed agent context inheritance** | Continuing after failure without cleaning corrupted context. |
| 9 | **Human approval theater** | Requiring human approval for decisions agents can self-validate. |

---

## Key Structural Findings from Adversarial Review

### Dependency assumptions are systematically flawed
- **13 false dependencies** (4 in Unicorns, 9 in tier ordering)
- **7 hidden dependency categories** (JSONL, hooks, version gates, conventions, git, runtime, filesystem)
- **4 circular dependency chains** (2 true circles requiring simultaneous development)
- **6 tier ordering fallacies** (wrong tiers for complexity/value/score)

### The biggest lies
1. Unicorn dependencies are marketing, not architecture
2. "Already implemented" means 3 different things (structural existence, manual tools, automated)
3. Tier 1 numbering creates false ordering — at least 6 items have zero dependencies on prior items
4. Hidden infrastructure dependencies doom 20+ components

### What this means
- Don't build Unicorns as packages — their component lists are aspirational
- Build T1 items in parallel — the numbered list is misleading
- Expose all hidden dependencies — or implementations will fail mysteriously
- The roadmap is 60% accurate on WHAT to build, 40% wrong on HOW components relate
