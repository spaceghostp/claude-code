---
type: atom
status: settled
lifecycle: active
created: 2026-02-16
last_touched: 2026-02-16
links_out: 2
origin: session
---

# Hyrum's Law

#status/settled — Well-established principle with broad empirical support.

## The Concept

With a sufficient number of users of an API, all observable behaviors of your system will be depended on by somebody.

This means every abstraction boundary is a liability surface. The intended interface is a subset of the actual interface — callers depend on implementation details, error message formats, timing characteristics, and side effects that were never part of the contract. The longer an abstraction exists and the more callers it has, the larger the gap between intended and actual interface.

## Why It Matters for Code Decisions

Hyrum's Law is the mechanism by which abstraction fails. An abstraction that "saves complexity" at write time accumulates implicit contracts over read/modify time. Each caller that depends on an unintended behavior adds a constraint that isn't visible in the type signature or documentation. Modifying the abstraction then requires understanding all of these invisible constraints — which is often harder than modifying the duplicated code the abstraction replaced.

This doesn't mean abstraction is wrong. It means abstraction has a carrying cost that compounds over time and callers, and that cost is systematically underestimated at the point of introduction.

## Links

- [[positions/what-good-code-actually-is]] — Claims 1 and 2 apply this atom: abstraction's hidden contracts justify delaying abstraction and preferring inline logic
- [[tensions/abstraction-vs-explicitness]] — Hyrum's Law is the mechanism by which Side B (abstraction) fails
