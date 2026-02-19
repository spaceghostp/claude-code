---
globs: [".claude/skills/*/SKILL.md", ".claude/commands/*.md"]
when: { "always": true }
---

# Governance: Adding Skills & Primitives

## The Six Governance Patterns

| # | Pattern | Question | Measure |
|---|---------|----------|---------|
| G1 | **Goldilocks** | Is this the "just right" balance? | -3 to +3 (0 = optimal) |
| G2 | **Orthogonality** | Does this do exactly ONE thing? | Binary pass/fail |
| G3 | **Composability** | Can this combine with existing primitives? | Binary pass/fail |
| G4 | **Native-first** | Does Claude already do this well? | Score ≥0.75 = native sufficient |
| G5 | **Tier-aware** | Does this help Haiku/Sonnet users? | 3 tiers |
| G6 | **Token-conscious** | Does every token earn its place? | Budget thresholds |

### Governance Decision Order

```
1. Native-first (G4) → If ≥0.75, STOP — use native approach
2. Orthogonality (G2) → Must pass — single responsibility
3. Composability (G3) → Must pass — reuse existing primitives
4. Goldilocks (G1) → Validate engineering balance (-3 to +3)
5. Tier-aware (G5) → Evaluate benefit across model tiers
6. Token-conscious (G6) → Check budget compliance
```

## Before Adding a New Skill

```
1. NATIVE CHECK: Can Claude do this without a skill?
   → If yes: STOP. Document the native approach instead.

2. OVERLAP CHECK: Does an existing skill cover this?
   → If partial: Extend existing skill, don't create new.

3. TOKEN CHECK: Will SKILL.md be <4K tokens?
   → If no: Split into core + reference files.
   → Full skill load must be <15K tokens (200K context) or <20K tokens (1M beta).

4. TIER CHECK: Does this add value for Haiku/Sonnet?
   → If Opus-only benefit: Mark as optional or skip.
```

## Before Adding a New Command

```
1. Can this be a subcommand of an existing command?
2. Is this used frequently enough to warrant a command?
   → Rare operations can be invoked via skill directly.
3. Does the name conflict with existing commands?
   → Check ls .claude/commands/ before adding.
```

## G4 Native-First: Value Index

```
VI = (Utility_skill - Utility_native) / Cost_skill

Decision Thresholds:
  VI < 0        → REJECT    (native is better)
  0 ≤ VI < 0.25 → REVIEW    (marginal value)
  VI ≥ 0.25     → ACCEPT    (clear value added)
```

If VI < 0.25 for an existing skill, flag for deprecation review.

## G6 Token Budget Thresholds

Skill budget = 2% of context window (v2.1.32+). Thresholds scale with context size.

| Component | Target (200K) | Max (200K) | Max (1M beta) |
|-----------|---------------|------------|---------------|
| Skill SKILL.md | 2-4K | 4K | 4K |
| Full skill load | 8-12K | 15K | 20K |
| Command definition (simple) | <500 | 1K | 1K |
| Command definition (orchestration) | 2-4K | 6K | 6K |
| Always-loaded context | <1K | 5K | 5K |

## Redundancy Thresholds

| Score | Action | Meaning |
|-------|--------|---------|
| ≥0.75 | REJECT/DEPRECATE | Native sufficient |
| 0.50-0.74 | REVIEW | Marginal — tier-check required |
| <0.50 | ACCEPT | Clear value-add |

## Deprecation Triggers

A skill should be deprecated when:
1. Native capability improves to cover it (score ≥0.75)
2. Another skill subsumes its functionality
3. Usage patterns show it's rarely invoked
4. Token cost exceeds demonstrated value

## Consolidation Over Expansion

**Prefer:**
- Extending existing skills with new capabilities
- Creating reference files in existing skills
- Composing existing primitives

**Avoid:**
- New skills for narrow use cases
- Duplicate capabilities across skills
- Commands that could be subcommands

## Before Adding a New Hook

```
1. EVENT CHECK: Is this PreToolUse, PostToolUse, TeammateIdle, or TaskCompleted?
2. LANGUAGE CHECK: Use bash + python3 -c (project convention)
3. MATCHER CHECK: Avoid .* for PostToolUse if tool-specific matching suffices
4. DATA CHECK: Does it write to a .claude/ data file? Define rotation policy.
5. OVERLAP CHECK: Can an existing hook be extended instead?
```
