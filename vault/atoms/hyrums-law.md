---
type: atom
status: working
created: 2026-02-14
last_touched: 2026-02-14
links_out: 2
origin: session
---

# Hyrum's Law

#status/working

## Definition

**Hyrum's Law:** With a sufficient number of users of an API, it does not matter what you promise in the contract: all observable behaviors of your system will be depended on by somebody.

## Key Properties

1. **Observable behavior ≠ documented contract** — Users depend on side effects, implementation details, and accident details that were never promised.

2. **Applies to all APIs** — Not just software libraries. Internal APIs, HTTP endpoints, configuration file formats, command-line interfaces — any interface with multiple consumers.

3. **Makes backwards-compatibility impossible** — Even changes that should be safe (like internal refactoring) can break dependents if anyone observed the behavior.

4. **Grows worse over time** — The more users you have, the more hidden dependencies accumulate. Old code written against ancient versions may depend on behaviors that are now invisible.

## Relationship to Code Quality

This is the core reason why [[positions/what-good-code-actually-is]] warns against abstractions that hide implicit contracts. Every abstraction accumulates implicit dependencies. Callers depend on:
- Performance characteristics
- Error handling behavior
- Side effects (even if undocumented)
- Implementation quirks

Under modification pressure, these hidden contracts break.

## Practical Implication

The cost of change is not just the lines of code modified — it's the cost of unexpected dependents who relied on the old behavior. This makes explicit, duplicated code sometimes cheaper than abstracted code: at least it's clear what each instance depends on.

## Links

- [[positions/what-good-code-actually-is]] — Why implicit contracts matter for code changeability
