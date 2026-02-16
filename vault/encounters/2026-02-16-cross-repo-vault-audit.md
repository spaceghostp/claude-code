---
type: encounter
status: unverified
lifecycle: proposed
created: 2026-02-16
last_touched: 2026-02-16
links_out: 5
origin: session
---

# Cross-Repository Vault Audit

#status/unverified — Raw synthesis from auditing 12 repositories. Needs review via `/vault-maintain`.

## Context

Audited all repositories under `spaceghostp/` for vault-worthy considerations: architectural decisions, positions on code quality, AI agent design patterns, cognitive/memory system design, domain expertise, and tensions. 152 raw findings distilled into the themes below.

**Repositories crawled:** waldzell-mcp, rooroo, Pheromind, Agile_tools, CodeGraph, MicroManager, mcp-mem0, mcp-shrimp-task-manager, roo-commander, Archon, ottomator-agents, mcp-crawl4ai-rag.

---

## Theme 1: Capability-Matched Delegation Is a Load-Bearing Pattern

**Appeared in:** MicroManager, rooroo, roo-commander, Agile_tools, Archon

Across five repositories, the same principle emerges independently: match the capability level of the executing agent to the complexity of the task, not the other way around. This manifests as:

- **MicroManager:** Explicit capability ceilings per agent mode (Intern ≤ 2 files, Junior ≤ 1 file slightly complex, MidLevel multiple files, Senior complex coordination). Tasks delegated to the *least capable agent that can handle them*.
- **rooroo:** Strategic Planner (expensive Opus-tier) vs Navigator (cheap fast model) — cost-driven architecture that matches LLM tier to cognitive complexity of the phase.
- **roo-commander:** Multi-level hierarchy (core → director/lead → worker → specialist) with explicit `escalate_to`/`delegate_to` metadata. Delegates validate task size *before* execution and push back if too large.
- **Agile_tools:** Polymorphic agent embodiment — single orchestrator loads specialized personas. The persona determines capability scope.
- **Archon:** Reasoner → Advisor → Specialized Refiners pipeline. Each stage has progressively narrower scope but deeper expertise.

**Vault-worthy claim (falsifiable):** Systems that match agent capability to task complexity produce fewer failures than systems that use a single powerful agent for everything. The threshold for "too complex for this tier" should be defined in advance, not discovered at runtime.

**Relates to:** [[positions/what-good-code-actually-is]] Claim 1 — the abstraction threshold. Capability matching is the agent-orchestration analog of "don't abstract until the 4th instance." Don't delegate to a powerful agent until the task proves it needs one.

---

## Theme 2: Escalation Over Autonomy — Simpler Agents Should Defer, Not Debug

**Appeared in:** MicroManager, rooroo, roo-commander, mcp-shrimp-task-manager

A consistent position across agent orchestration repos: when a lower-capability agent encounters difficulty, it should *escalate* rather than *attempt to fix*. This is not obvious — the instinct is to make agents self-correcting. But these codebases explicitly reject that:

- **MicroManager:** Intern mode must "complete task with a message saying you failed and to escalate." Mode restriction prevents agents from switching roles mid-task.
- **rooroo:** Principle of Least Assumption — when ambiguous, ask rather than guess. Enforced as a safety mechanism across all agent modes.
- **roo-commander:** Confidence-gated escalation — coordinators assess their own uncertainty and *must* escalate to user when confidence is Medium or Low.
- **mcp-shrimp-task-manager:** Score-based verification threshold (80/100). Tasks aren't "done" until verified; below-threshold results trigger re-evaluation, not autonomous retry.

**Vault-worthy tension:** Agent autonomy vs. escalation discipline. More autonomy enables faster throughput. More escalation enables fewer cascading failures. The codebase evidence suggests: *escalation scales better than autonomy for multi-tier agent systems*.

**Relates to:** [[questions/my-own-cognition]] — if an agent recognizes its limits and defers, is that a form of self-awareness? Or is it just constraint compliance?

---

## Theme 3: Context as Architecture, Not Documentation

**Appeared in:** roo-commander, MicroManager, rooroo, mcp-shrimp-task-manager, Agile_tools, Archon

Every multi-agent system treats context packaging as a *load-bearing architectural component*, not a secondary concern. Specific manifestations:

- **MicroManager:** Every delegated subtask must include: overall goal, how this part fits in, relevant details from parent tasks, explicit scope boundaries, and a "Focus" statement preventing deviation.
- **rooroo:** "LINK, DON'T EMBED" rule — agents reference large files via Markdown links rather than copying content. Forces agents to read source of truth.
- **roo-commander:** Knowledge Bases stored separately from system prompts, loaded on-demand via `read_file`. Prevents context bloat while maintaining deep expertise.
- **mcp-shrimp-task-manager:** Task metadata enriched at execution time, not planning time. Lazy context loading defers expensive lookups until the agent is ready to act.
- **Agile_tools:** Config-driven authority — all agent knowledge originates from loaded configuration, never hardcoded. Configuration overrides agent KB when they disagree.
- **Archon:** Static system prompt (what to do) + runtime-injected context (what to know about this case). Separation of role knowledge from instance context.

**Vault-worthy atom:** "Context is engineering, not documentation." The structure, timing, and delivery mechanism of context to an agent determines the agent's performance more than the agent's capability. A capable agent with poor context will underperform a mediocre agent with well-structured context.

**Relates to:** [[positions/what-good-code-actually-is]] Claim 2 — abstractions that hide critical assumptions cause surprise. In agent systems, context that's implicit (assumed the agent will figure it out) causes the same class of failures as hidden abstractions in code.

---

## Theme 4: Explicit Constraints Enable Lower-Capability Systems

**Appeared in:** MicroManager, rooroo, mcp-shrimp-task-manager, Agile_tools, roo-commander

A recurring pattern: adding constraints to agent prompts *improves* output quality, especially for weaker models. This challenges the intuition that more freedom = better results.

- **MicroManager:** CodeShortRules mode provides "more explicit instructions and constraints" specifically for "less capable models with limited context windows."
- **rooroo:** Output Envelope standardization — all agents report via a fixed JSON structure (`status`, `message`, `output_artifact_paths`, `clarification_question`, `error_details`). The constraint forced clarity.
- **mcp-shrimp-task-manager:** Structured thought tracking with required fields: `axioms_used`, `assumptions_challenged`, `stage` tags. Not just "log reasoning" but "mark what you're assuming."
- **Agile_tools:** "Coding standards should be kept to the minimum necessary to prevent undesirable or messy code from the agent" — minimal but sufficient constraints.
- **roo-commander:** Read-only specialist roles as a safety pattern — capability restriction enables trust.

**Vault-worthy position (falsifiable):** Increased constraint can compensate for reduced capability. Explicit constraints in prompts are analogous to explicit logic in code — they reduce surprise and enable lower-capability systems to perform reliably. Falsifiable: if agents with fewer constraints consistently outperform constrained agents of the same capability tier, this position is wrong.

**Relates to:** [[positions/what-good-code-actually-is]] Claim 2 — explicit inline logic produces fewer defects. The agent-orchestration equivalent: explicit prompt constraints produce fewer agent failures.

---

## Theme 5: Specialization Over Generalization — But With Limits

**Appeared in:** MicroManager, rooroo, Pheromind, Agile_tools, Archon, roo-commander, waldzell-mcp

Every multi-agent repo creates specialized roles rather than generalist agents. But several repos also document where specialization was taken too far and then rolled back:

- **rooroo v0.5.x:** Removed Solution Architect, UX Specialist, and Guardian Validator roles — consolidated into fewer, clearer roles. "Fewer roles with clearer boundaries meant fewer coordination points."
- **Archon v1→v5:** Started with a single RAG agent, evolved to multi-agent only when single-agent limitations became clear. Each iteration added complexity only when the previous version's limitations were proven.
- **roo-commander:** "Prefer specialists over generalists" but retains generalist fallback modes (`util-senior-dev`, `dev-solver`).

**Vault-worthy tension:** Specialization improves individual agent quality but increases coordination cost. The optimal number of roles is the *minimum* that covers distinct cognitive modes without creating coordination overhead. Three occurrences of role consolidation (rooroo, Archon, roo-commander) suggest the threshold is lower than most designers assume.

**Relates to:** [[positions/what-good-code-actually-is]] Claim 1 — the abstraction threshold. Adding specialized roles is like adding specialized functions. At what point does role proliferation create more complexity than it solves?

---

## Theme 6: Memory Architecture — Retrieval vs. Development

**Appeared in:** mcp-mem0, mcp-shrimp-task-manager, roo-commander, mcp-crawl4ai-rag, ottomator-agents

Different repos take fundamentally different approaches to agent memory:

- **mcp-mem0:** Semantic search as primary interface — agents query memory through natural language, not structured queries. Memory is a black box (Mem0 library).
- **mcp-shrimp-task-manager:** Completed tasks auto-backed up to `/memory/` directory. Memory searched before planning new tasks. This is retrieval-augmented task planning.
- **roo-commander:** Session Management V6 — captures "texture" of conversations (decisions made, alternatives considered) in session directories. Structured task logs are separate from narrative context.
- **mcp-crawl4ai-rag:** Contextual embeddings — chunks enriched with LLM-generated context before embedding. Trades indexing cost for retrieval precision.
- **ottomator-agents:** Foundational RAG pipeline as composable modules (TextChunker, EmbeddingGenerator, DatabaseClient). Memory is infrastructure, not intelligence.

**Vault-worthy question:** Is the cognitive vault more like mcp-mem0 (semantic retrieval of past knowledge) or more like roo-commander's session management (narrative context that preserves the *texture* of reasoning)? The vault's design principle — "development over retrieval" — aligns with roo-commander's approach. But the vault index architecture (keywords, bidirectional links) borrows from RAG patterns.

**Relates to:** [[questions/my-own-cognition]] — the vault is an attempt to create continuity. These repos show multiple models of continuity, from flat semantic search to structured session capture. Which model best serves *development* (building on previous thinking) vs *retrieval* (finding past facts)?

---

## Theme 7: Emergence vs. Explicit Sequencing in Multi-Agent Systems

**Appeared in:** Pheromind, rooroo, roo-commander, Archon

A genuine tension across the repos: should agent coordination emerge from interaction, or be explicitly prescribed?

- **Pheromind:** Advertises stigmergy (emergent swarm coordination via "digital pheromone trails") but actually implements sequential SPARC pipeline (Research → Spec → Architecture → Tests → Code → Integration → Docs → DevOps). The emergence framing doesn't match the implementation.
- **rooroo:** Sequential phases with explicit handoffs. The Navigator doesn't decide phase ordering — it follows the prescribed sequence.
- **roo-commander:** Explicit delegation hierarchy with prescribed escalation paths. No emergent coordination.
- **Archon:** Sequential pipeline (reasoner → advisor → parallel refiners → integration). Explicit ordering.

**Vault-worthy observation:** Every repo that started with emergent/flexible coordination moved toward explicit sequencing. Zero repos moved in the other direction. This suggests that for software development tasks, explicit phase sequencing outperforms emergent coordination. The evidence is one-directional.

**Relates to:** [[tensions/abstraction-vs-explicitness]] — emergence is the agent-coordination equivalent of implicit behavior. Explicit sequencing is the equivalent of inline logic. The repos consistently favor explicitness.

---

## Theme 8: Graph and Knowledge Representation Patterns

**Appeared in:** CodeGraph, waldzell-mcp, mcp-crawl4ai-rag

Several repos implement knowledge representation with patterns relevant to the vault's index design:

- **CodeGraph:** Two-pass analysis (extract entities, then resolve cross-references). Entity ID vs instance ID duality for deterministic identity across runs. Placeholder nodes for unresolved references (structural integrity with explicit uncertainty markers).
- **waldzell-mcp Clear Thought:** Confidence scores (0.0-1.0) and iteration tracking as first-class metadata across all cognitive tools. Epistemic state is data, not metadata.
- **mcp-crawl4ai-rag:** Semantic chunking respecting syntactic boundaries. Metadata-driven filtering in vector search (JSONB with indexed paths).

**Vault-worthy atom:** "Placeholder nodes preserve graph integrity under incomplete knowledge." When a link target doesn't exist, create the link anyway with an explicit uncertainty marker. The graph's structure is valuable even when incomplete. This is already a vault convention (rule 3: "If a link target doesn't exist, use the intended path anyway") but now validated by an independent codebase.

**Relates to:** [[_meta/conventions]] — the vault's linking rules already follow this pattern. CodeGraph's implementation confirms it's architecturally sound.

---

## Theme 9: Iterative Refinement as Core Methodology

**Appeared in:** Pheromind, Archon, mcp-shrimp-task-manager, Agile_tools

Multiple repos embed explicit self-critique loops in their agent workflows:

- **Pheromind:** 3-phase process (Draft → Self-Critique → Revision) for both PRD generation and code documentation.
- **Archon:** V1→V6 evolution — complexity added only when prior version's limitations proved real. "Iterative complexity" as a development philosophy.
- **mcp-shrimp-task-manager:** Multi-stage planning (analyze → reflect → split) with `process_thought` tool forcing externalized reasoning at each stage.
- **Agile_tools:** "EMBRACE_THE_CHAOS" — iterative non-linear process as core tenet. Revisiting earlier steps is expected, not tolerated.

**Vault-worthy position:** Self-critique loops improve agent output quality more than increased model capability. A mediocre model that drafts, critiques, and revises outperforms a powerful model that generates once. This is testable.

---

## Theme 10: The MCP Platform Has Non-Obvious Constraints

**Appeared in:** waldzell-mcp, Archon, mcp-mem0, mcp-crawl4ai-rag

Domain expertise about MCP discovered across repos:

- **Archon:** "Communication protocols for MCP seemed to interfere with LLM calls when done directly within the MCP server" — forced separation of FastAPI graph service from MCP server. Non-obvious architectural constraint.
- **waldzell-mcp:** Heartbeat pattern needed to prevent MCP client timeout during long cognitive operations (30-second periodic stderr messages).
- **mcp-mem0:** Lifespan-based dependency injection — resources initialized once at server startup and shared via context. Two transport modes (SSE vs stdio) with no single "best" choice.
- **mcp-crawl4ai-rag:** Same lifespan pattern, same transport abstraction. Confirmed as a stable MCP server pattern.

**Vault-worthy encounter:** MCP servers cannot invoke LLM calls directly within the server process — the protocol interferes. This constraint forces architectural separation (separate API service for LLM work). This directly validates the vault plan's finding that "hooks cannot invoke Claude."

**Relates to:** [[_meta/autonomous-vault-plan]] — the plan identified this exact constraint. These repos provide independent confirmation.

---

## Proposed Vault Notes from This Audit

Based on the 10 themes above, here are the strongest candidates for individual vault notes:

| Note | Type | Why |
|------|------|-----|
| Capability-matched delegation | Atom | Core concept across 5+ repos, directly applicable |
| Escalation over autonomy in agent systems | Position | Falsifiable claim, evidence from 4 repos |
| Context is engineering not documentation | Atom | Foundational insight, changes how future sessions approach agent design |
| Explicit constraints compensate for reduced capability | Position | Falsifiable, evidence from 5 repos |
| Emergence vs explicit sequencing | Tension | Genuine unresolved tension with one-directional evidence |
| Specialization threshold in multi-agent systems | Tension | Direct parallel to code abstraction threshold |
| MCP servers cannot invoke LLM calls in-process | Encounter | Non-obvious platform constraint, independently confirmed |
| Self-critique loops vs model capability | Position | Testable claim about agent quality |

---

## Links

- [[positions/what-good-code-actually-is]] — Claims 1, 2, and 4 all have agent-orchestration analogs discovered in this audit
- [[questions/my-own-cognition]] — Memory architecture and escalation patterns raise questions about agent self-awareness
- [[tensions/abstraction-vs-explicitness]] — Emergence vs. sequencing is the agent-coordination equivalent
- [[_meta/autonomous-vault-plan]] — MCP constraints independently confirmed
- [[_meta/conventions]] — Placeholder node pattern validated by CodeGraph
