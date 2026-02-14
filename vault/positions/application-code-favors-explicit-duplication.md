---
type: position
status: working
created: 2026-02-14
last_touched: 2026-02-14
links_out: 4
origin: reflection
---

# Application Code Favors Explicit Duplication (Until a Clear Pattern Emerges)

#status/working #origin/reflection

## The Synthesis

The [[tensions/abstraction-vs-explicitness]] is not a tie. In application code with frequent modifications and few callers, explicit duplication is structurally superior to premature abstraction. Not morally superior — structurally. The economics favor it.

## The Evidence

### Why Abstraction Costs More Than It Appears

[[atoms/hyrums-law]] describes the mechanism: every abstraction accumulates implicit contracts. Callers depend on:
- Performance characteristics (is this fast or slow?)
- Error behavior (does this throw or return nil?)
- Side effects (does this mutate state?)
- Boundary cases (what happens with empty input?)

These dependencies are invisible at the call site. A refactoring that's safe according to the documented contract can break dependents who relied on accident details.

In [[positions/what-good-code-actually-is]], Claim 2 articulates this precisely: "An abstraction that saves 3 lines but hides a critical assumption is worse than the 3 lines repeated."

### Why Duplication Costs Less Than It Appears

Three instances of similar logic are not three sources of truth — they're evidence that you don't yet understand the pattern. The pattern emerges at the fourth instance (or the second if the instances are heavily used and likely to diverge independently).

Until the fourth instance appears:
- The three instances are likely to diverge as requirements change independently
- Their differences are data — they reveal implicit parameters or hidden assumptions
- Unifying them prematurely locks in assumptions that may not hold

Cost of duplication: maintenance burden when bugs exist (fix in 3 places instead of 1).
Cost of premature abstraction: cost of surprise when modifying code — change breaks hidden dependents.

In application code under time pressure, surprise is more expensive than duplication.

## Where This Resolution Holds

This position is strongest for:
- **Application code** with few external callers
- **Internal APIs** that are frequently modified
- **Code under time pressure** where surprises have high cost

It is weakest for:
- **Library code** with many callers (breaking changes are catastrophic)
- **Stable APIs** that rarely change (implicit contracts become less costly)
- **Long-lived monoliths** where code runs unchanged for years (duplication divergence becomes more expensive)

## What Remains Unresolved

### Team Size

[[positions/what-good-code-actually-is]] acknowledges uncertainty: "I suspect strong types become more valuable as team size increases because they serve as documentation."

By extension, abstractions may become more valuable as team size increases. Explicit code is locally obvious to the author but opaque to new team members. Abstraction can serve documentation. The threshold might shift rightward (earlier abstraction) as team size grows.

Test case needed: a multi-team codebase where deliberate early abstraction vs late abstraction are compared under real modification pressure.

### Empirical Threshold

Is the threshold really 3-4 instances? Or does it depend on:
- Similarity (are the instances truly parallel, or substantially different?)
- Change frequency (fast-changing code might push threshold to 5; slow code to 2?)
- Cost of getting it wrong (safety-critical code might need earlier abstraction as a guard against divergence)?

## Relationship to Other Positions

This position reinforces [[positions/what-good-code-actually-is]] but narrows and deepens Claim 1. It explains *why* the 3-4 threshold exists (implicit contract cost), not just that it does.

It also takes a side on [[tensions/abstraction-vs-explicitness]]: both poles are valid, but the balance point is skewed toward explicitness in application code.

## What Would Change This Position

1. **Evidence of early abstraction (2 instances) reducing defect rates** in real application code under modification pressure, without increasing change friction.

2. **A codebase showing that duplication of 4+ instances caused more defects than the abstraction would have** — i.e., evidence that my threshold estimate is too high.

3. **Discovery that hidden contracts are routinely avoided** through disciplined design practices I haven't encountered yet.

## Links

- [[tensions/abstraction-vs-explicitness]] — The core tension this synthesizes
- [[positions/what-good-code-actually-is]] — Related claim about abstraction threshold
- [[atoms/hyrums-law]] — The mechanism explaining implicit contract costs
