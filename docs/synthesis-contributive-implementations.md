# Synthesis: Contributive Implementations from 4 Valued Repos

**Date**: 2026-02-02
**Source repos**: promptfoo, claude-cookbooks, langchain, mastra
**Target**: Claude Code CLI v2.1.29 (27 native tools, 5 skills, 3 hooks, 3 commands)
**Method**: 4 independent adversarial deep research agents (Opus), each producing a full anatomical analysis with G4 scoring

---

## Cross-Cutting Summary

| Repo | Capabilities Analyzed | Novel Gaps | Enhancements | Redundant/Overlap | Extraction Rate |
|------|----------------------|-----------|-------------|-------------------|----------------|
| **promptfoo** | 30 | 11 (37%) | 4 (13%) | 15 (50%) | 0/30 (0%) — all rejected on adversarial review |
| **claude-cookbooks** | 36 | 5 (14%) | 5 (14%) | 26 (72%) | 4/36 (11%) — 4 BUILD, 2 DEFER, 1 SKIP |
| **langchain** | 18 | 2 (11%) | 4 (22%) | 12 (67%) | 3/18 (17%) — 3 BUILD, 2 DEFER, 1 REJECT |
| **mastra** | 18 | 4 (22%) | 3 (17%) | 11 (61%) | 2/18 (11%) — 2 BUILD, 1 DEFER |
| **TOTAL** | **102** | **22 (22%)** | **16 (16%)** | **64 (63%)** | **9 BUILD / 102 analyzed (9%)** |

### Key Finding

**63% of all analyzed capabilities across 4 repos are redundant** with Claude Code's native tools. Of the remaining 37% (novel + enhancement), only **9 survive adversarial counter-arguments** as worth building. The extraction rate is 9%.

---

## Consolidated BUILD List (9 implementations, ~3,750 tokens total)

Sorted by priority score (Impact × Feasibility / Cost):

| Rank | Source | ID | Implementation | Type | Tokens | VI Score |
|------|--------|----|---------------|------|--------|----------|
| 1 | cookbooks | E1 | Compaction Priority Hierarchy | Skill extension | +200 | 1.50 |
| 2 | cookbooks | E2 | Structured Memory Template | Skill extension | +300 | 1.00 |
| 3 | mastra | E2 | Tool Schema Conventions for MCP | Rule extension | +200 | 2.00 |
| 4 | langchain | E3 | Research Pipeline Command | New command | +400 | 1.00 |
| 5 | langchain | E6 | Memory Tiering Enhancement | Skill extension | +500 | 1.00 |
| 6 | cookbooks | E5 | Evaluator-Optimizer Command | New command | +400 | 0.375 |
| 7 | cookbooks | E7 | Tool Evaluation Criteria | Skill extension | +500 | 0.30 |
| 8 | langchain | E4 | Context Window Monitor Hook | New hook | +150 | 1.00 |
| 9 | mastra | E1 | Eval Scoring Skill | New skill | +4000 | 1.50 |

**Total token investment: ~6,650** (across 4 skill extensions, 2 new commands, 1 new hook, 1 new skill, 1 rule extension)

---

## What Was Rejected and Why

### promptfoo: 0 implementations survived

Despite having the most novel gaps (11), every proposed implementation failed adversarial review:

| Proposed | Kill Reason |
|----------|------------|
| Prompt Security Scanner | G4 violation — a 50-word prompt achieves 90% of what a 3K skill provides |
| Output Assertion Hook | Scope creep — detect-deploy-failure.sh covers the 80/20; generalizing adds maintenance burden |
| Eval Gate Command | Native Claude does this when asked — "run tests, check security, give pass/fail" |
| Risk Scoring Formula | False precision — formula designed for automated batch evals, not qualitative CLI assessment |
| Cost Tracking | Protocol limitation — hook protocol doesn't reliably expose token counts |
| Guardrail Hook | Regex bypassed trivially; inferior duplicate of native permission system |
| Eval-Lite Framework | Fundamental mismatch — deterministic testing of non-deterministic LLM outputs |

**Insight**: promptfoo's value is in **batch evaluation at scale**, which is orthogonal to Claude Code's **interactive CLI** usage. The patterns don't transfer because the usage contexts are fundamentally different. The one transferable insight — the red team attack taxonomy — belongs as a **200-token rule**, not as tooling.

### langchain: 2 implementations deferred, 1 rejected

| Deferred/Rejected | Reason |
|-------------------|--------|
| Multi-Agent Graph Orchestration | Claude's LLM IS the orchestrator — rigid graph DSL fights adaptive behavior |
| Structured Output Validation | Requires jsonschema dependency; violates zero-dependency rule |
| Tool Result Caching | PreToolUse hooks cannot short-circuit tool execution — architectural mismatch |

### mastra: 1 implementation deferred

| Deferred | Reason |
|----------|--------|
| Structured Memory Schema | Over-engineering — Mastra needs Zod schemas because code consumers require types; LLMs handle freeform text natively |

---

## Architecture-Level Insights

### The Fundamental Pattern

All 4 repos reveal the same architectural truth:

> **The value of LLM tooling shifts dramatically between programmatic frameworks and interactive agents.**

- **Frameworks** (LangChain, Mastra, promptfoo) need: declarative configs, type safety, parallel execution engines, result persistence, automated grading, deployment abstractions
- **Interactive agents** (Claude Code) need: behavioral guidance, quality floors, memory management, consistency enforcement

The 9% extraction rate reflects this fundamental mismatch. The 9 surviving implementations all share a common trait: they address the **LLM's blind spots** (consistency, structured compression, systematic research, self-evaluation) rather than trying to replicate what the LLM already does well.

### Where Each Repo's Value Actually Lives

| Repo | Primary Value | Value for Claude Code | Form |
|------|--------------|----------------------|------|
| **promptfoo** | Red team attack taxonomy (40+ categories) | Reference knowledge for security reviews | Rule (~200 tokens) |
| **claude-cookbooks** | Anthropic's official compaction/memory patterns | Proven priority hierarchies and templates | Skill extensions (~1,000 tokens) |
| **langchain** | Graduated memory compression + research discipline | Quality floors for recurring operations | Command + skill extension (~1,050 tokens) |
| **mastra** | Eval scoring protocol + tool schema conventions | Self-governance improvements | Skill + rule (~4,200 tokens) |

### Deduplication Across Repos

Three repos independently converged on the same patterns:

1. **Memory/compaction improvement**: cookbooks (E1+E2) + langchain (E6) → merge into single compact-context enhancement (+1,000 tokens total)
2. **Eval/self-assessment**: cookbooks (E3 deferred) + mastra (E1) + promptfoo (rejected) → mastra's approach is most actionable as a skill
3. **Research pipeline**: langchain (E3) is unique — no equivalent in other repos

---

## Implementation Roadmap

### Phase 1: Extend Existing Primitives (~1,200 tokens, 0 new files)

1. **compact-context/SKILL.md**: Add compaction priority hierarchy (cookbooks E1) + structured memory template (cookbooks E2) + tiered compression (langchain E6)
2. **evaluate-primitives/SKILL.md**: Add tool evaluation criteria (cookbooks E7)
3. **rules/api.md**: Add MCP tool schema conventions (mastra E2)

### Phase 2: New Commands (~800 tokens, 2 new files)

4. **commands/research.md**: Research pipeline command (langchain E3)
5. **commands/eval-optimize.md**: Evaluator-optimizer loop (cookbooks E5)

### Phase 3: New Primitives (~4,150 tokens, 2 new files)

6. **hooks/context-monitor.sh**: Context window pressure warning (langchain E4)
7. **skills/eval-output/SKILL.md**: Eval scoring skill (mastra E1)

### Conditional (Trait-Gated)

8. **rules/security.md**: Red team attack taxonomy checklist (promptfoo), loads when editing CLAUDE.md or rules/ files

---

## Governance Compliance

| Check | Result |
|-------|--------|
| G1 Goldilocks | 9 implementations across 3 phases — measured, not excessive |
| G2 Orthogonality | Each implementation has a single responsibility |
| G3 Composability | All extend or compose with existing primitives |
| G4 Native-First | All have VI ≥ 0.25 (lowest: 0.30 for cookbooks E7) |
| G5 Tier-Aware | All benefit Sonnet/Haiku users (structured guidance helps weaker models more) |
| G6 Token-Conscious | Total investment: ~6,650 tokens; no single skill exceeds 4K |

---

## Final Assessment

These 4 repos, representing 1.05M combined GitHub stars, yield **9 actionable implementations totaling ~6,650 tokens** of Claude Code primitives. The 9% extraction rate is not a criticism of the repos — they are excellent at what they do. It reflects the fundamental truth that **Claude Code's 27 native tools already cover the vast majority of what these frameworks provide**. The extractable value lies in behavioral guidance, quality floors, and self-governance patterns — not in infrastructure abstractions.
