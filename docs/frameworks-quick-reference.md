# Frameworks Quick Reference

Extracted from WS-000-02's 53-framework analysis. Use this as a decision aid, not a comprehensive guide.

## Cynefin Router — Classify First

Before choosing any framework, classify the problem domain:

| Domain | Signal | Approach | Frameworks |
|--------|--------|----------|------------|
| **Clear** | Cause-effect obvious | Sense → Categorize → Respond | Lean, Six Sigma, Little's Law, DFMA, Taguchi |
| **Complicated** | Expertise-discoverable | Sense → Analyze → Respond | Axiomatic Design, TRIZ, TOC, QFD, Porter's Five Forces |
| **Complex** | Retrospective visibility only | Probe → Sense → Respond | STPA, System Dynamics, Scenario Planning, Antifragility |
| **Chaotic** | No patterns, act first | Act → Sense → Respond | OODA Loop, Bounded Rationality |
| **Disorder** | Can't classify | Break into parts, classify each | Use STPA at coupling points |

## Selection Guide — Problem → Framework

| Problem | Framework | Why |
|---------|-----------|-----|
| Debug complex system failure | STPA + UCA | Control model; systematic hazard decomposition |
| Reduce dependencies | DFMA + TMPC | 3-criteria elimination test per dependency |
| Pipeline bottleneck | TOC + Little's Law | Find constraint + model queue math |
| Design an API | Axiomatic Design + QFD | Independence axiom = loose coupling; HOQ maps needs |
| Prove a bug's root cause | Koch's Postulates | 4-step causation verification |
| Resolve contradictory requirements | TRIZ Matrix + 40 Principles | Systematic contradiction resolution |
| When good enough is enough | Bounded Rationality | Satisficing threshold stops over-optimization |
| Classify problem type | Cynefin | Routes to right approach |

## Common Misapplications

| Situation | Wrong Framework | Why It Fails | Use Instead |
|-----------|----------------|-------------|-------------|
| Time pressure, no clarity | TRIZ | Requires analysis time | OODA Loop |
| Chaotic crisis | Axiomatic Design | Assumes stable requirements | OODA → Cynefin |
| Multi-causal bug | Koch's Postulates | Only handles single-cause | STPA |
| Unknown problem domain | Any specific framework | May be wrong domain | Cynefin first |

## Composition Workflows

**Architecture Refactoring**: Axiomatic Design (independence check) → DFMA + TMPC (dependency elimination) → System Dynamics (feedback effects) → TOC (find new constraint)

**Technical Debt Management**: Cynefin (classify debt type) → TOC (find bottleneck) → Lean (eliminate waste) → Throughput Accounting (measure value)

**Safety/Reliability**: STPA (hazard analysis) → UCA (unsafe control actions) → Control Theory (verify feedback loops)

**Process Optimization**: TOC (find constraint) → Little's Law (model queues) → Lean (eliminate waste) → Six Sigma (reduce variance)

## Key Principle — Axiomatic Design

The Independence Axiom applied to software:

```
[FR] = [A][DP]

Diagonal A = uncoupled (ideal) — change one DP, affect one FR
Triangular A = decoupled (OK) — one-way dependencies, order matters
Full A = coupled (redesign) — changes propagate everywhere
```

Information content: I = -log2(P) where P = probability design satisfies requirements. Minimize I across the system. High I = fragile design.
