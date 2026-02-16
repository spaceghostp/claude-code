---
type: tension
status: working
lifecycle: active
created: 2026-02-16
last_touched: 2026-02-16
links_out: 3
origin: session
---

# Abstraction vs. Explicitness

#status/working — Both sides have real failure modes. Not resolved.

## The Tension

Two principles that are individually correct and mutually incompatible at the boundary.

### Side A: Explicitness

Code visible at point of use. No hidden contracts. Modifications are local — you can read what happens without chasing indirection. Duplication cost is measured in lines, which is cheap. The failure mode of explicitness is **silent divergence**: copies that should have changed together but didn't, because nothing enforced their relationship.

### Side B: Abstraction

Invariants encoded once. Changes propagate consistently through a single control point. The failure mode of abstraction is **hidden assumptions**: implicit contracts ([[atoms/hyrums-law]]) accumulate at the abstraction boundary, invisible at the call site. When those assumptions break under modification, the blast radius is unpredictable.

## The Irresolvable Core

Both failure modes are real and both cause production defects. The decision of when to abstract depends on variables that aren't knowable at decision time:

- **Team size** — More contributors means more risk of silent divergence (favors abstraction), but also more risk of misunderstanding the implicit contract (favors explicitness).
- **Change frequency** — High churn favors explicitness because abstractions calcify. Low churn favors abstraction because the contract stabilizes.
- **Domain stability** — Stable domains tolerate abstraction. Domains still being understood punish premature abstraction because the wrong axis gets locked in.

The position in [[positions/what-good-code-actually-is]] stakes a claim (Claim 1: abstract at 3-4 repetitions, not 2). That claim is a heuristic for navigating this tension, not a resolution of it. The tension persists regardless of where you set the threshold.

## What Would Shift the Balance

- Evidence that early abstraction (at 2 repetitions) consistently outperforms delayed abstraction in change velocity would weaken Side A.
- Evidence that duplicated code causes fewer defects under modification than equivalent abstractions would weaken Side B.
- A clear metric for "domain stability" that could be assessed at decision time would make the tension more navigable without resolving it.

## Links

- [[positions/what-good-code-actually-is]] — The position this tension challenges, particularly Claims 1 and 2
- [[atoms/hyrums-law]] — The mechanism by which abstraction accumulates hidden contracts
- [[questions/my-own-cognition]] — Am I genuinely holding both sides of this tension, or performing balance?
