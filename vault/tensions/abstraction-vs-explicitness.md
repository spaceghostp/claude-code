---
type: tension
status: working
created: 2026-02-14
last_touched: 2026-02-14
links_out: 4
origin: session
---

# Abstraction vs Explicitness

#status/working

## The Two Poles

### Pole 1: Abstraction

**The case for:** Abstractions reduce duplication, create reusable components, and allow high-level reasoning. A well-chosen abstraction hides complexity and lets the reader focus on what matters. Common patterns can be pulled out once and reused.

**Cost:** Each abstraction introduces an implicit contract. Callers depend on behaviors that aren't documented. Under modification pressure, these hidden dependencies break. Hyrum's Law applies: [[atoms/hyrums-law]].

### Pole 2: Explicitness

**The case for:** Explicit, duplicated code is locally obvious. You can read a function and understand everything it depends on without jumping through layers. No hidden contracts. Modifications don't surprise you with failures in distant dependents.

**Cost:** Duplication accumulates. Similar logic scattered across the codebase diverges over time. Small bugs must be fixed in multiple places. Maintenance burden grows.

## Why They Pull Against Each Other

This is not a false dichotomy. The tradeoff is real:

- **Abstraction** buys you compression (less code) and reusability but sells you coupling (implicit contracts)
- **Explicitness** buys you locality and clarity but sells you duplication and divergence

The question is not which is better — it's where the threshold lies.

## Current Stance (Provisional)

[[positions/what-good-code-actually-is]] takes a specific position: the abstraction threshold in application code is further toward duplication than most developers accept. Three instances should not yet be abstracted. Four instances, maybe.

This assumes:
- Application code changes frequently
- Hidden contracts are expensive to maintain
- Duplication in 3 copies is cheaper than the implicit contract cost of abstraction

For library code with many callers and long deprecation cycles, the calculus flips — abstraction earlier is safer.

## Unresolved Questions

- Does the threshold change with team size? (Larger teams benefit more from abstraction as documentation)
- Does it change with code lifetime? (Long-lived code has more time for implicit contracts to accumulate damage)
- Is there a way to get abstraction without the implicit contract cost?

## Links

- [[positions/what-good-code-actually-is]] — Stakes a specific claim on where this tension resolves
- [[positions/application-code-favors-explicit-duplication]] — A synthesis that reconciles this tension
- [[atoms/hyrums-law]] — Why implicit contracts are costly
