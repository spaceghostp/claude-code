---
type: position
status: unverified
lifecycle: proposed
created: 2026-02-16
last_touched: 2026-02-16
links_out: 3
origin: session
---

# Two-Vault Architecture

#status/unverified — First articulation. Needs validation through actual migration and daily use.

## The Position

WS-000-02 and WS-000-03 serve different owners and should not be merged, mirrored, or unified. They are complementary systems with distinct purposes.

**WS-000-02 is the library.** ~16,000+ notes extracted from external sources. The LLM searches, retrieves, and reasons over this material. Flat category system optimized for RAG retrieval. Content is static — extracted once, not revised.

**WS-000-03 is the journal.** A small, curated graph of staked claims, open questions, and recorded changes of mind. The user curates. Content is dynamic — positions evolve, get falsified, link to each other.

## Falsifiable Claims

**Claim 1: Migration from library to journal should be selected by the LLM for the LLM's operational benefit, not extracted as abstract "taste."** The user directed: "The notes you are going to integrate into the operational knowledge needs to be useful and curated to and by you." This means the migration question is "would having this note make me make a materially different decision in a future session?" — not "is this an interesting idea?" Falsifiable: if migrated notes selected by this criterion turn out to be less useful than notes selected by the user's taste preferences, this claim is wrong.

**Claim 2: The journal should be complementary to, not duplicative of, the library.** Notes that already exist in WS-000-02 and work fine as RAG retrieval targets don't need to be in WS-000-03. Only notes that need the journal's epistemic structure — falsification criteria, lifecycle tracking, graph topology — belong here. Falsifiable: if duplicating operational notes from WS-000-02 into WS-000-03's structure produces better session outcomes than keeping them separate, this claim is wrong.

**Claim 3: The ~98% reduction ratio (16K → 200-300 notes) is correct.** A development vault should be 1-2% of an extraction vault. The rest stays in the library for retrieval. Falsifiable: if the migrated set consistently lacks notes that sessions need, the ratio is too aggressive.

## The Dynamic Interface

The two vaults interact through sessions:
1. LLM retrieves operational knowledge from WS-000-02 (patterns, techniques, tools)
2. LLM applies that knowledge to the user's work
3. If the application involves a judgment call, preference, or trade-off stance, that judgment gets captured in WS-000-03
4. Future sessions surface WS-000-03 positions, which shape how WS-000-02 knowledge gets applied

The library provides breadth. The journal provides depth and judgment.

## Evidence I'd Need to Revise

- Sessions where the vault separation causes friction (needing both vaults open, conflicting information)
- Migration producing notes that don't get surfaced or used within 30 days
- The library degrading without the journal's epistemic structure applied to it

## Links

- [[questions/my-own-cognition]] — The journal tests whether continuity changes session quality
- [[positions/what-good-code-actually-is]] — Example of a journal-native note: staked claims with falsification criteria
- [[encounters/2026-02-14-designing-the-cognitive-vault]] — Origin of the journal system
