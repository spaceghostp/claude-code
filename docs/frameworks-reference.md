# 53 Frameworks Reference — Claude Code Operational Guide

A structured reference for framework-guided problem solving. 53 frameworks across engineering, strategy, systems theory, economics, AI, and biology — each translated to software engineering use cases.

---

## Table of Contents

- [How to Use This Reference](#how-to-use-this-reference)
- [Glossary](#glossary)
- [Quick Reference Matrix](#quick-reference-matrix)
- [Framework Selection Guide](#framework-selection-guide)
- [Cynefin Router](#cynefin-router)
- [Composition Workflows](#composition-workflows)
- [Domain 1: Deterministic Engineering (1.1–1.11)](#domain-1-deterministic-engineering)
- [Domain 2: Strategic Management (1.12–1.19)](#domain-2-strategic-management)
- [Domain 3: Systems Theory (1.20–1.30)](#domain-3-systems-theory)
- [Domain 4: Economic & Decision Theory (1.31–1.40)](#domain-4-economic--decision-theory)
- [Domain 5: Cognitive Architectures & AI (1.41–1.47)](#domain-5-cognitive-architectures--ai)
- [Domain 6: Biological & Organizational (1.48–1.53)](#domain-6-biological--organizational)
- [Cross-Reference Index](#cross-reference-index)

---

## How to Use This Reference

1. **Problem-first lookup**: Start with the [Selection Guide](#framework-selection-guide) — find your situation, get a framework.
2. **Domain browsing**: Jump to a domain section and scan framework purposes.
3. **Composition**: Use the [Composition Workflows](#composition-workflows) for multi-framework sequences.
4. **Cynefin first**: Unsure which domain? Start with the [Cynefin Router](#cynefin-router) to classify your problem.

**Tier system:**
- **Tier 1 (Direct Apply)**: Apply immediately, 5–15 min. Formula or checklist.
- **Tier 2 (Guided Apply)**: Structured walkthrough, 20–60 min.
- **Tier 3 (Expert Apply)**: Iterative, requires domain expertise, 1–8 hours.

**Operational categories:**
- **Calculator**: Input measurements/parameters → output number/formula result.
- **Classifier**: Input situation → output category/diagnosis.
- **Decomposer**: Input system → output structured breakdown.
- **Generator**: Input problem → output solutions/options.

**Math sections** are included for quantitative/computational frameworks and omitted for qualitative/conceptual frameworks.

---

## Glossary

| Term | Definition |
|------|-----------|
| **FR** | Functional Requirement — what the design must do |
| **DP** | Design Parameter — how the design does it |
| **UCA** | Unsafe Control Action — a control action that leads to a hazard |
| **HOQ** | House of Quality — QFD's correlation matrix |
| **DPMO** | Defects Per Million Opportunities |
| **S/N** | Signal-to-Noise Ratio (Taguchi) |
| **QLF** | Quality Loss Function |
| **ERRC** | Eliminate-Reduce-Raise-Create grid |
| **VSM** | Viable System Model |
| **TOC** | Theory of Constraints |
| **TCE** | Transaction Cost Economics |
| **STPA** | System-Theoretic Process Analysis |
| **SSM** | Soft Systems Methodology |
| **CATWOE** | Customer-Actor-Transformation-Worldview-Owner-Environment |
| **GST** | General Systems Theory |
| **PPO** | Proximal Policy Optimization |
| **RLHF** | Reinforcement Learning from Human Feedback |
| **CoT** | Chain of Thought reasoning |
| **SIT** | Systematic Inventive Thinking |
| **DFMA** | Design for Manufacturing and Assembly |
| **TMPC** | Theoretical Minimum Part Count |
| **PID** | Proportional-Integral-Derivative controller |

---

## Quick Reference Matrix

| # | Name | Category | Tier | Cynefin | Primary Input | Primary Output | SE Use Case |
|---|------|----------|------|---------|---------------|----------------|-------------|
| 1.1 | Axiomatic Design | Decomposer | 2 | Complicated | FRs + DPs | Design matrix + coupling analysis | API/module design: independence axiom = loose coupling |
| 1.2 | Taguchi QLF | Calculator | 1 | Clear | Measurement + target + cost constant | Loss L(y) = k(y-m)^2 | Cost-of-defect modeling for quality thresholds |
| 1.3 | Taguchi S/N Ratio | Calculator | 2 | Complicated | Measurements + objective type | S/N ratio (dB) | Test flakiness optimization, parameter tuning |
| 1.4 | TRIZ Matrix | Generator | 2 | Complicated | Improving + worsening parameters | Inventive principles | Resolving contradictory requirements |
| 1.5 | TRIZ 40 Principles | Generator | 2 | Complicated | Contradiction description | Solution templates | Creative problem solving for technical trade-offs |
| 1.6 | STPA | Decomposer | 2 | Complex | System + losses + hazards | Control structure + UCAs | Safety/reliability analysis of distributed systems |
| 1.7 | UCA Classification | Classifier | 1 | Complicated | Control action + context | 4-category failure mode | Categorizing how control actions fail |
| 1.8 | QFD | Decomposer | 2 | Complicated | Customer needs + tech specs | HOQ matrix + priorities | Mapping user requirements to engineering specs |
| 1.9 | DFMA | Decomposer | 2 | Clear | Assembly design + part list | DFA efficiency + elimination candidates | Reducing module/dependency count |
| 1.10 | TMPC (Boothroyd-Dewhurst) | Classifier | 1 | Clear | Part specifications | Keep/eliminate decision | 3-criteria test for dependency elimination |
| 1.11 | Zachman Framework | Decomposer | 3 | Complicated | System description | 6x6 artifact matrix | Enterprise architecture documentation |
| 1.12 | Blue Ocean Strategy | Generator | 2 | Complex | Industry factors + competitor positions | Strategy canvas + ERRC | Finding uncontested market space |
| 1.13 | ERRC Grid | Generator | 1 | Complicated | Industry factors + baselines | 4-quadrant action plan | Feature scope planning (keep/cut/add) |
| 1.14 | Lean Operations | Decomposer | 2 | Clear | Value stream + takt time | Waste identification + flow improvements | Eliminating waste in development pipeline |
| 1.15 | Little's Law | Calculator | 1 | Clear | Any 2 of {L, lambda, W} | The 3rd variable | Queue/WIP analysis for task pipelines |
| 1.16 | Six Sigma | Calculator | 1 | Clear | Defect count + opportunities | DPMO + sigma level | Process capability measurement |
| 1.17 | Porter's Five Forces | Classifier | 2 | Complicated | Industry data | Force ratings + profit potential | Competitive positioning analysis |
| 1.18 | Balanced Scorecard | Decomposer | 2 | Complicated | Strategy + KPIs | Performance dashboard + causality | Strategic alignment of engineering metrics |
| 1.19 | OODA Loop | Generator | 1 | Chaotic | Situation + information | Decision + tempo advantage | Rapid decision-making under time pressure |
| 1.20 | VSM | Decomposer | 3 | Complex | Org structure + communications | Viability diagnosis (S1-S5) | Org health assessment for engineering teams |
| 1.21 | TOC | Decomposer | 2 | Complicated | Process chain + capacities | Constraint ID + 5-step plan | Finding and relieving pipeline bottlenecks |
| 1.22 | Throughput Accounting | Calculator | 1 | Clear | Revenue, costs, inventory | T, NP, ROI | Financial analysis of throughput vs cost |
| 1.23 | Cynefin | Classifier | 1 | All | Situation description | Domain classification + approach | Meta-router: classify problem before choosing framework |
| 1.24 | System Dynamics | Decomposer | 3 | Complex | Variables + causal links | Stock-flow model + trajectories | Modeling feedback loops in complex systems |
| 1.25 | Cybernetics | Classifier | 2 | Complicated | System + goal + feedback | Feedback loop classification | Understanding control and regulation patterns |
| 1.26 | Control Theory (PID) | Calculator | 2 | Clear | Setpoint + PV + gains | Control signal u(t) | Auto-scaling, rate limiting, adaptive thresholds |
| 1.27 | Autopoiesis | Classifier | 3 | Complex | System description | Autopoietic/allopoietic classification | Understanding self-maintaining systems |
| 1.28 | SSM | Generator | 3 | Complex | Messy problem situation | Rich pictures + root definitions | Structuring wicked problems with multiple stakeholders |
| 1.29 | CATWOE | Decomposer | 1 | Complicated | Transformation description | 6-element root definition | Stakeholder analysis for system definitions |
| 1.30 | GST Isomorphisms | Classifier | 3 | Complex | Cross-domain observations | Structural similarities | Transferring solutions across domains |
| 1.31 | Nash Equilibrium | Calculator | 3 | Complicated | Players + strategies + payoffs | Equilibrium strategy profile | Multi-team decision analysis |
| 1.32 | Prospect Theory | Calculator | 2 | Complex | Outcomes + probabilities | Subjective value + risk prediction | Framing decisions to account for loss aversion |
| 1.33 | TCE | Classifier | 2 | Complicated | Transaction characteristics | Make vs buy recommendation | Build vs buy analysis for components |
| 1.34 | Principal-Agent | Decomposer | 2 | Complex | Objectives + info asymmetry | Contract design + incentive alignment | Aligning team incentives with outcomes |
| 1.35 | Bounded Rationality | Classifier | 1 | Complex | Decision + constraints | Satisficing threshold | Deciding when "good enough" beats optimal |
| 1.36 | Disruptive Innovation | Classifier | 2 | Complex | Incumbent + entrant trajectories | Disruption prediction | Evaluating technology adoption threats |
| 1.37 | Diffusion of Innovations | Calculator | 2 | Complex | Innovation characteristics | Adoption S-curve | Predicting feature/tool adoption rates |
| 1.38 | SIT | Generator | 2 | Complicated | Product + closed-world resources | Innovations via 5 templates | Constrained creative problem solving |
| 1.39 | Scenario Planning | Generator | 2 | Complex | Strategic question + driving forces | 2x2 scenario matrix | Planning under deep uncertainty |
| 1.40 | Antifragility | Classifier | 3 | Complex | System + stressors | Fragile/robust/antifragile classification | Designing systems that benefit from stress |
| 1.41 | ACT-R | Decomposer | 3 | Complicated | Task environment + memory | Activation levels + predictions | Cognitive load modeling for UX |
| 1.42 | SOAR | Decomposer | 3 | Complicated | Problem state + operators | Search trace + learned chunks | Problem-solving architecture design |
| 1.43 | Transformer (Attention) | Calculator | 3 | Complicated | Token sequence + weight matrices | Attention-weighted output | Understanding/designing attention mechanisms |
| 1.44 | Scaling Laws | Calculator | 2 | Complicated | N, D, C parameters | Predicted loss + optimal allocation | LLM compute budget planning |
| 1.45 | RLHF | Generator | 3 | Complex | Pretrained model + preference data | Aligned model | AI alignment and preference learning |
| 1.46 | PPO | Calculator | 3 | Complicated | Policy + reward + clipping eps | Updated policy | RL policy optimization |
| 1.47 | Chain of Thought | Generator | 1 | Complicated | Reasoning problem | Step-by-step derivation | Prompt engineering for multi-step reasoning |
| 1.48 | Hebbian Learning | Calculator | 2 | Clear | Pre/post activity + learning rate | Weight change dw | Understanding associative learning patterns |
| 1.49 | Bayesian Inference | Calculator | 1 | Complicated | Prior + likelihood + evidence | Posterior probability | Updating beliefs with evidence |
| 1.50 | Schein's Culture Model | Decomposer | 3 | Complex | Org observations + interviews | 3-level diagnosis | Diagnosing engineering culture |
| 1.51 | Core Competence | Classifier | 2 | Complicated | Capabilities + competitive landscape | Core competencies (3-test) | Identifying strategic capabilities |
| 1.52 | Soil Food Web | Decomposer | 3 | Complex | Ecosystem data + interactions | Trophic map + health assessment | Codebase ecosystem health modeling |
| 1.53 | Koch's Postulates | Classifier | 1 | Complicated | Suspected cause + symptoms | Causal confirmation (4-step) | Rigorous debugging causation protocol |

---

## Framework Selection Guide

| I need to... | Use this framework | Why |
|---|---|---|
| Debug a complex system failure | 1.6 STPA + 1.7 UCA | Models safety as a control problem; systematic hazard decomposition |
| Reduce dependencies/modules | 1.9 DFMA + 1.10 TMPC | 3-criteria elimination test for each dependency |
| Choose build vs buy | 1.33 TCE | Asset specificity analysis determines governance form |
| Classify my problem type | 1.23 Cynefin | Routes to the right approach for the right domain |
| Optimize a pipeline bottleneck | 1.21 TOC + 1.15 Little's Law | Find constraint + model queue math |
| Design an API | 1.1 Axiomatic Design + 1.8 QFD | Independence axiom = loose coupling; HOQ maps user needs |
| Plan under uncertainty | 1.39 Scenario Planning + 1.40 Antifragility | Multiple futures + convex positioning |
| Improve team dynamics | 1.50 Schein's Culture + 1.20 VSM | Deep assumptions + viability check |
| Evaluate market position | 1.17 Porter's Five Forces + 1.12 Blue Ocean | Industry structure + value innovation |
| Update beliefs with evidence | 1.49 Bayesian Inference | Prior x Likelihood = Posterior |
| Prove a bug's root cause | 1.53 Koch's Postulates | 4-step causation verification protocol |
| Resolve contradictory requirements | 1.4 TRIZ Matrix + 1.5 TRIZ 40 Principles | Systematic contradiction resolution |
| Simplify a feature set | 1.13 ERRC Grid | Eliminate/Reduce/Raise/Create quadrants |
| Make a fast decision under pressure | 1.19 OODA Loop | Observe-Orient-Decide-Act faster than competition |
| Determine when good enough is enough | 1.35 Bounded Rationality | Satisficing threshold stops over-optimization |
| Predict adoption of a new tool | 1.37 Diffusion of Innovations | S-curve adoption modeling |
| Align incentives across teams | 1.34 Principal-Agent | Find and fix information asymmetry |
| Optimize for consistency (reduce flakiness) | 1.3 Taguchi S/N | Design of experiments for noise reduction |
| Calculate cost of quality deviation | 1.2 Taguchi QLF | Quadratic loss function around target |
| Model feedback loops in architecture | 1.24 System Dynamics | Stock-flow diagrams + simulation |
| Refactor a monolith into services | 1.1 Axiomatic Design + 1.9 DFMA | Decompose by independence; eliminate coupled modules |
| Prioritize technical debt | 1.21 TOC + 1.14 Lean | Find the constraint bottleneck; eliminate waste |
| Validate specs for edge cases | 1.6 STPA + 1.53 Koch's Postulates | Safety analysis + causal verification |
| Assess org change readiness | 1.50 Schein's Culture + 1.37 Diffusion | Cultural diagnosis + adoption S-curve |
| Estimate queue/wait times | 1.15 Little's Law + 1.24 System Dynamics | Queue math + stock-flow modeling |
| Frame a proposal to get buy-in | 1.32 Prospect Theory | Loss aversion framing; present gains not costs |
| Architect for resilience | 1.40 Antifragility + 1.25 Cybernetics | Positive convexity + feedback regulation |
| Structure a wicked problem | 1.28 SSM + 1.29 CATWOE | Rich pictures + stakeholder decomposition |

### Common Misapplications (Avoid These)

| Situation | Wrong Framework | Why It Fails | Use Instead |
|---|---|---|---|
| Time pressure, no causal clarity | 1.4 TRIZ (Tier 2) | Requires analysis time you don't have | 1.19 OODA Loop (Tier 1) |
| Chaotic crisis | 1.1 Axiomatic Design | Assumes stable requirements | 1.19 OODA Loop first, then 1.23 Cynefin |
| Multi-causal bug | 1.53 Koch's Postulates | Only handles single-cause | 1.6 STPA (multi-causal control model) |
| Problem domain unknown | Any specific framework | May be wrong domain entirely | 1.23 Cynefin (classify first) |

---

## Cynefin Router

Cynefin (1.23) is the meta-framework. Use it first to classify your problem, then route to the appropriate framework set.

**Clear domain** (cause-effect obvious, best practice exists):
- Use: 1.2 Taguchi QLF, 1.15 Little's Law, 1.16 Six Sigma, 1.14 Lean, 1.9 DFMA, 1.10 TMPC
- Approach: Sense → Categorize → Respond

**Complicated domain** (cause-effect discoverable with expertise):
- Use: 1.1 Axiomatic Design, 1.4 TRIZ, 1.8 QFD, 1.21 TOC, 1.17 Porter's Five Forces, 1.33 TCE
- Approach: Sense → Analyze → Respond

**Complex domain** (cause-effect only visible in retrospect):
- Use: 1.6 STPA, 1.24 System Dynamics, 1.39 Scenario Planning, 1.40 Antifragility, 1.12 Blue Ocean
- Approach: Probe → Sense → Respond

**Chaotic domain** (no cause-effect patterns, act first):
- Use: 1.19 OODA Loop, 1.35 Bounded Rationality
- Approach: Act → Sense → Respond

**Disorder** (can't tell which domain you're in):
- Use: 1.23 Cynefin probe → gather data → re-classify
- Approach: Break the situation into smaller parts, classify each independently
- Common resolution: parts of the system are in different domains — apply domain-specific frameworks to each part, use 1.6 STPA at coupling points

---

## Composition Workflows

### Workflow 1: Product Design Pipeline
```
1.8 QFD (customer needs → engineering specs)
  → 1.1 Axiomatic Design (independence check on specs)
    → 1.9 DFMA (minimize part count)
      → 1.3 Taguchi S/N (optimize for robustness)
```
**SE use case**: Designing a new service/API from user requirements through to production-hardened implementation.

### Workflow 2: Market Entry Strategy
```
1.17 Porter's Five Forces (analyze competitive structure)
  → 1.12 Blue Ocean Strategy (find uncontested space)
    → 1.13 ERRC Grid (define value proposition)
      → 1.37 Diffusion of Innovations (target adopter segments)
```
**SE use case**: Launching a developer tool or platform — competitive analysis through adoption strategy.

### Workflow 3: Safety/Reliability Analysis
```
1.6 STPA (identify hazards and control structure)
  → 1.7 UCA Classification (categorize unsafe actions)
    → 1.26 Control Theory (verify control stability)
```
**SE use case**: Analyzing distributed system reliability — from hazard identification through control verification.

### Workflow 4: Process Optimization
```
1.21 TOC (find the constraint)
  → 1.15 Little's Law (model queue dynamics)
    → 1.14 Lean (eliminate waste)
      → 1.16 Six Sigma (measure capability improvement)
```
**SE use case**: Optimizing CI/CD pipeline, PR review queue, or deployment process.

### Workflow 5: Problem Classification
```
1.23 Cynefin (classify problem domain)
  → [domain-appropriate framework set]
```
**SE use case**: Any new problem — start here to avoid applying the wrong framework.

### Workflow 6: AI/ML Development
```
1.43 Transformer (architecture design)
  → 1.44 Scaling Laws (compute-optimal allocation)
    → 1.45 RLHF (alignment training)
      → 1.46 PPO (policy optimization)
        → 1.47 CoT (reasoning evaluation)
```
**SE use case**: End-to-end LLM development pipeline from architecture through evaluation.

### Workflow 7: Architecture Refactoring
```
1.1 Axiomatic Design (map FRs → DPs, find coupling)
  → 1.9 DFMA + 1.10 TMPC (eliminate unnecessary modules)
    → 1.24 System Dynamics (model feedback effects of changes)
      → 1.21 TOC (find the constraint limiting refactor ROI)
```
**SE use case**: Monolith-to-services refactoring, dependency reduction, module consolidation.

### Workflow 8: Technical Debt Management
```
1.23 Cynefin (classify debt type: clear/complicated/complex)
  → 1.21 TOC (find the debt item constraining throughput)
    → 1.14 Lean (identify waste in current process)
      → 1.22 Throughput Accounting (ROI of debt paydown)
```
**SE use case**: Prioritizing and justifying technical debt reduction work.

---

## Domain 1: Deterministic Engineering

Frameworks: 1.1 Axiomatic Design | 1.2 Taguchi QLF | 1.3 Taguchi S/N | 1.4 TRIZ Matrix | 1.5 TRIZ 40 Principles | 1.6 STPA | 1.7 UCA | 1.8 QFD | 1.9 DFMA | 1.10 TMPC | 1.11 Zachman

[Back to Selection Guide](#framework-selection-guide) | [Back to Cynefin Router](#cynefin-router)

### 1.1 Axiomatic Design
**Originator:** Nam Pyo Suh | **Domain:** Design theory | **Tier:** 2 | **Cynefin Fit:** Complicated

**Purpose:** Decompose requirements into design parameters while maintaining functional independence.

**SE Translation:** API and module design. The Independence Axiom maps directly to loose coupling: each functional requirement (endpoint, feature) should be satisfiable by changing exactly one design parameter (module, service) without affecting others. A diagonal design matrix = well-decoupled architecture.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Functional Requirements (FRs) | text array | Yes | What the design must do |
| Design Parameters (DPs) | text array | Yes | How the design does it |
| Design matrix entries | boolean/numeric matrix | No | Coupling indicators |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Design Matrix | NxM matrix | Coupling classification (uncoupled/decoupled/coupled) |
| Information Content | numeric | Complexity measure; lower is better |
| Independence analysis | report | Identifies coupled FRs and DPs |

**Math:**
- Design equation: `[FR] = [A][DP]` where A is the design matrix
- Information Content: `I = -log2(P)` where P is probability of satisfying FR
- Diagonal A = uncoupled (ideal). Triangular A = decoupled (acceptable). Full A = coupled (redesign).

**Execution Pipeline:**
1. List all Functional Requirements (what the system must do)
2. Map each FR to a Design Parameter (how it's implemented)
3. Build the design matrix: mark which DPs affect which FRs
4. Check for diagonal/triangular structure
5. If coupled (non-triangular), redesign to decouple
6. Calculate information content to compare design alternatives

**Constraints:**
- HARD: FRs must be defined BEFORE design begins. Wrong FRs cascade everywhere.
- HARD: Coupled designs (full matrix) cannot be optimized — must decouple first.
- SOFT: Start with customer needs, not technical solutions.
- DO NOT USE WHEN: Requirements are genuinely ambiguous (clarify first), project is exploratory, or requirements will change dramatically.

**Related:** 1.8 QFD (feeds FRs into Axiomatic Design), 1.9 DFMA (takes design output), 1.3 Taguchi S/N (optimizes parameters)

---

### 1.2 Taguchi Quality Loss Function (QLF)
**Originator:** Genichi Taguchi | **Domain:** Quality engineering | **Tier:** 1 | **Cynefin Fit:** Clear

**Purpose:** Quantify the economic cost of deviating from a target quality value.

**SE Translation:** Cost-of-defect modeling. Any deviation from "target" (ideal response time, error rate, uptime) incurs economic loss. Use to set tolerance thresholds: how much latency variance can you afford before customer cost exceeds fix cost?

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Measured value (y) | numeric | Yes | Actual quality characteristic |
| Target value (m) | numeric | Yes | Nominal/ideal specification |
| Cost constant (k) | numeric | Yes | Economic loss coefficient |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Loss L(y) | numeric | Economic loss in monetary units |
| Tolerance analysis | numeric | Recommended tolerance budget |

**Math:**
- `L(y) = k(y - m)^2`
- Cost constant: `k = A0 / D0^2` where A0 is cost at specification limit D0

**Execution Pipeline:**
1. Define the target value (ideal specification)
2. Determine the cost at the specification limit (A0)
3. Calculate k from specification limits
4. Measure actual values
5. Compute loss for each measurement
6. Use loss values to set tolerance budgets

**Constraints:**
- HARD: Loss function shape must match reality — quadratic assumption fails for asymmetric loss (e.g., overdose vs underdose).
- HARD: k must be calibrated to actual failure costs, not theoretical estimates.
- SOFT: Collect real field failure data to calibrate k.
- DO NOT USE WHEN: Loss is highly nonlinear/multimodal, you lack real cost data, or asymmetry is critical (use custom loss function).

**Related:** 1.3 Taguchi S/N (complementary — QLF for cost, S/N for robustness), 1.16 Six Sigma (both measure quality)

---

### 1.3 Taguchi Signal-to-Noise Ratio
**Originator:** Genichi Taguchi | **Domain:** Robust design | **Tier:** 2 | **Cynefin Fit:** Complicated

**Purpose:** Optimize system parameters to maximize consistency (signal) while minimizing variance (noise).

**SE Translation:** Test flakiness optimization. Design experiments to find parameter combinations (timeout, retry count, network mock fidelity) that minimize test variance. Also applicable to API response time consistency, deployment reliability.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Measured values | numeric array | Yes | Replicates of quality characteristic |
| Objective type | enum {nominal, smaller-better, larger-better} | Yes | Optimization direction |
| Target value | numeric | No | For nominal-is-best cases |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| S/N ratio | numeric (dB) | Signal-to-noise in decibels |
| Optimal parameter settings | table | Best combination per factor |

**Math:**
- Nominal-is-best: `S/N = 10 log10(mean^2 / variance)`
- Smaller-is-better: `S/N = -10 log10(sum(yi^2) / n)`
- Larger-is-better: `S/N = -10 log10(sum(1/yi^2) / n)`

**Execution Pipeline:**
1. Define the quality characteristic and objective type
2. Identify control factors (parameters you can set) and noise factors (environmental variance)
3. Design orthogonal array experiment
4. Run experiments, collect data
5. Calculate S/N ratio for each parameter combination
6. Select parameter levels that maximize S/N

**Constraints:**
- HARD: Must correctly identify which factors are "control" vs "noise."
- SOFT: Use orthogonal arrays to minimize experiment count.
- DO NOT USE WHEN: System behavior is fundamentally chaotic, or you can't run controlled experiments.

**Related:** 1.2 Taguchi QLF (cost companion), 1.16 Six Sigma (process capability), 1.14 Lean (waste context)

---

### 1.4 TRIZ Contradiction Matrix
**Originator:** Genrich Altshuller | **Domain:** Innovation | **Tier:** 2 | **Cynefin Fit:** Complicated

**Purpose:** Resolve technical contradictions by mapping improving/worsening parameter pairs to inventive principles.

**SE Translation:** When improving one system property (e.g., response time) worsens another (e.g., data completeness), look up the contradiction in the 39-parameter matrix to get suggested resolution principles.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Improving parameter | integer [1-39] | Yes | Feature being enhanced |
| Worsening parameter | integer [1-39] | Yes | Undesired side-effect |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Inventive principles | integer array (1-4 values) | Principle numbers from the 40 |
| Principle descriptions | text array | Plain-language resolution strategies |

**Math:**
- Matrix lookup: `M[improving][worsening] -> set of principle indices`

**Execution Pipeline:**
1. State the contradiction: "Improving X worsens Y"
2. Map X and Y to the 39 engineering parameters
3. Look up the matrix cell
4. Review the 1-4 suggested inventive principles
5. Apply principles to generate solution concepts
6. Evaluate and select best concept

**Constraints:**
- HARD: Must correctly identify the 39-parameter mappings — wrong parameters yield wrong principles.
- SOFT: Use multiple principles together for stronger solutions.
- DO NOT USE WHEN: There is no genuine contradiction (just do both), or the problem is in the Chaotic Cynefin domain.

**Related:** 1.5 TRIZ 40 Principles (the principles the matrix points to), 1.38 SIT (alternative innovation method)

---

### 1.5 TRIZ 40 Inventive Principles
**Originator:** Genrich Altshuller | **Domain:** Innovation | **Tier:** 2 | **Cynefin Fit:** Complicated

**Purpose:** Provide 40 generic solution strategies for resolving contradictions, derived from patent analysis.

**SE Translation:** When stuck on a technical trade-off, apply principles like Segmentation (paginate results), Dynamicity (adaptive responses), Feedback (client hints), Asymmetry (separate fast-path/complete-path endpoints), Prior Action (pre-compute).

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Contradiction description | text | Yes | Problem statement highlighting conflict |
| Current solution approach | text | No | Existing approach to critique |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Applicable principles | array | {number, name, description, example} |
| Solution templates | text array | Generic solutions using principles |

**Execution Pipeline:**
1. Describe the contradiction clearly
2. Review the 40 principles (or use 1.4 Matrix to narrow down)
3. For each suggested principle, generate at least one concrete solution
4. Rank solutions by feasibility and impact
5. Select and prototype the best

**Constraints:**
- HARD: Principles are heuristic, not algorithmic — they suggest directions, not specific solutions.
- SOFT: Generate multiple solutions per principle before selecting.
- DO NOT USE WHEN: Problem is well-defined with a known optimal solution.

**Related:** 1.4 TRIZ Matrix (selects which principles), 1.38 SIT (complementary innovation method)

---

### 1.6 STPA (System-Theoretic Process Analysis)
**Originator:** Nancy Leveson | **Domain:** Safety engineering | **Tier:** 2 | **Cynefin Fit:** Complex

**Purpose:** Identify hazards in complex systems by analyzing control structures rather than component failures.

**SE Translation:** Distributed system reliability analysis. Instead of listing what can break (FMEA), model who controls what and how control can fail. A controller (service A) issues commands to a controlled process (service B) — what happens if the command is wrong, late, missing, or stuck?

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| System description | text | Yes | System overview, scope, boundaries |
| Losses | text array | Yes | Undesirable outcomes |
| Hazards | text array | Yes | States leading to losses |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Safety control structure | diagram | Hierarchical control representation |
| Unsafe Control Actions | table | {action, loss_type, description} |
| Causal scenarios | text array | Event chains leading to losses |
| Safety requirements | text array | Constraints to prevent hazards |

**Execution Pipeline:**
1. Define system losses (data corruption, downtime, financial loss)
2. Identify system hazards (states that lead to losses)
3. Draw the control structure (controllers, controlled processes, feedback)
4. Identify Unsafe Control Actions for each controller
5. Develop causal scenarios for each UCA
6. Derive safety requirements from scenarios

**Constraints:**
- HARD: Must model the control structure accurately — missing a controller misses entire hazard classes.
- SOFT: Iterate the control structure with domain experts.
- DO NOT USE WHEN: System is purely combinatorial with no control loops (use fault tree instead).

**Related:** 1.7 UCA Classification (categorizes the UCAs), 1.26 Control Theory (verifies control stability), 1.24 System Dynamics (models feedback)

---

### 1.7 UCA Classification
**Originator:** Nancy Leveson | **Domain:** Safety analysis | **Tier:** 1 | **Cynefin Fit:** Complicated

**Purpose:** Classify how a control action can be unsafe into exactly 4 categories.

**SE Translation:** For any service call, command, or operation, systematically check: (1) not provided when needed, (2) provided incorrectly, (3) provided at wrong time, (4) stopped too soon / applied too long.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Control action | text | Yes | Specific action by controller |
| Context | text | No | Operational conditions |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Classification | enum | {not-provided, incorrectly-provided, wrong-timing, stopped-prematurely} |
| Consequence | text | Resulting hazardous state |

**Math:**
- Failure mode enumeration: `FM in {NP, IP, WT, SP}`
- Risk = `sum(P(FM_i) * severity_i)` for each category

**Execution Pipeline:**
1. Take a specific control action from STPA analysis
2. For each of the 4 categories, ask: "What if this action is [not provided | incorrect | wrong timing | stopped too soon]?"
3. Document the consequence of each failure mode
4. Rate severity and likelihood
5. Derive requirements to prevent each failure mode

**Constraints:**
- HARD: Must enumerate all 4 categories — skipping one misses a hazard class.
- SOFT: Consider environmental context for each category.
- DO NOT USE WHEN: Action has no control dimension (pure data transformation).

**Related:** 1.6 STPA (parent framework), 1.26 Control Theory (quantitative verification)

---

### 1.8 QFD (Quality Function Deployment)
**Originator:** Yoji Akao | **Domain:** Product planning | **Tier:** 2 | **Cynefin Fit:** Complicated

**Purpose:** Translate customer requirements into prioritized engineering specifications via the House of Quality matrix.

**SE Translation:** Map user needs ("fast responses," "easy onboarding," "reliable uptime") to technical specifications (cache strategy, API design, redundancy architecture) with weighted priorities. The HOQ roof reveals conflicts between specs.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Customer requirements | text array | Yes | Voice of Customer |
| Importance ratings | numeric array [1-10] | Yes | Customer priority weights |
| Technical requirements | text array | Yes | Engineering specifications |
| Relationship matrix | numeric matrix | Yes | Correlation strengths |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| HOQ matrix | numeric matrix | Populated correlations |
| Technical importance ratings | numeric array | Weighted priority per spec |
| Correlation matrix (roof) | numeric matrix | Spec interdependencies |

**Math:**
- Technical importance: `TI_j = sum(importance_i * relationship_i_j)`
- Normalized: `NTI_j = TI_j / sum(TI)`

**Execution Pipeline:**
1. Gather customer requirements and importance weights
2. Define technical requirements (engineering specs)
3. Fill the relationship matrix (how strongly each spec addresses each need)
4. Calculate technical importance ratings
5. Build the roof (spec-to-spec correlations)
6. Identify highest-priority specs and conflicts

**Constraints:**
- HARD: Customer requirements must come from actual customers, not internal assumptions.
- SOFT: Use competitive benchmarking columns to contextualize.
- DO NOT USE WHEN: No clear customer exists (internal tooling with one stakeholder — just ask them directly).

**Related:** 1.1 Axiomatic Design (takes QFD output as FRs), 1.13 ERRC Grid (alternative prioritization)

---

### 1.9 DFMA (Design for Manufacturing and Assembly)
**Originator:** Boothroyd & Dewhurst | **Domain:** Manufacturing | **Tier:** 2 | **Cynefin Fit:** Clear

**Purpose:** Minimize part count and assembly complexity through systematic design simplification.

**SE Translation:** Minimize module/dependency count. Every module, service, library is a "part." Apply the theoretical minimum part count test: does this dependency (1) move relative to others? (2) require a different material/technology? (3) need to be separate for assembly? If no to all three, eliminate it.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Assembly design | diagram/text | Yes | Component arrangement |
| Part list | table | Yes | Bill of materials |
| Assembly sequence | text array | Yes | Order of assembly steps |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| DFA efficiency index | numeric [0,1] | (3 * N_theoretical) / N_actual |
| Candidates for elimination | text array | Parts to remove or consolidate |
| Cost reduction estimate | numeric (%) | Projected savings |

**Math:**
- DFA index: `(3 * N_theoretical) / N_actual`
- N_theoretical = minimum theoretically possible parts (from 1.10 TMPC test)

**Execution Pipeline:**
1. List all parts (modules/dependencies)
2. Apply the 3-criteria test (1.10 TMPC) to each
3. Calculate theoretical minimum part count
4. Compute DFA index
5. Identify candidates for elimination or consolidation
6. Redesign and re-score

**Constraints:**
- HARD: Must apply the 3-criteria test honestly — don't keep parts for political reasons.
- SOFT: Involve assembly/deployment experts in evaluation.
- DO NOT USE WHEN: System is already at theoretical minimum, or parts are mandated by external constraints.

**Related:** 1.10 TMPC (the elimination test), 1.1 Axiomatic Design (coupling context), 1.14 Lean (waste elimination)

---

### 1.10 TMPC (Boothroyd-Dewhurst Criteria)
**Originator:** Boothroyd & Dewhurst | **Domain:** Design simplification | **Tier:** 1 | **Cynefin Fit:** Clear

**Purpose:** Determine the theoretical minimum part count by applying 3 binary criteria to each part.

**SE Translation:** For each dependency/module, ask: (1) Does it move independently at runtime? (2) Must it be a different technology/language? (3) Must it be physically separate for deployment? If all three are NO, it can be merged or eliminated.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Part specifications | object per part | Yes | {id, function, material, shape} |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Keep/eliminate decision | enum | {keep, eliminate, consolidate} per part |
| Justification | text | Reason based on 3 criteria |

**Math:**
- Keep if ANY criterion is TRUE
- Eliminate if ALL three criteria are FALSE

**Execution Pipeline:**
1. For each part/module, ask criterion 1 (independent motion?)
2. Ask criterion 2 (different material/technology required?)
3. Ask criterion 3 (must be separate for assembly/deployment?)
4. If all three are NO → candidate for elimination
5. Sum remaining keeps = theoretical minimum part count

**Constraints:**
- HARD: All 3 criteria must be evaluated — skipping one inflates part count.
- SOFT: Document rationale for borderline cases.
- DO NOT USE WHEN: Parts are mandated by regulation or external API boundaries.

**Related:** 1.9 DFMA (uses TMPC for the elimination test)

---

### 1.11 Zachman Framework
**Originator:** John Zachman | **Domain:** Enterprise architecture | **Tier:** 3 | **Cynefin Fit:** Complicated

**Purpose:** Organize architectural artifacts in a 6x6 matrix of perspectives (rows) x interrogatives (columns).

**SE Translation:** Enterprise architecture documentation. Rows = stakeholder perspectives (Scope/Business/System/Technology/Detailed/Operating). Columns = What/How/Where/Who/When/Why. Each cell is a specific artifact (data model, process flow, network diagram, etc.).

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| System description | text | Yes | Organization/system overview |
| Perspective scope | text | No | Which rows to focus on |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| 6x6 matrix | table | Architectural artifacts per cell |
| Gap analysis | text | Missing perspectives and views |

**Execution Pipeline:**
1. Define the system scope
2. For each row (perspective), populate each column (interrogative)
3. Identify gaps — cells without artifacts
4. Prioritize filling critical gaps
5. Map dependencies between artifacts

**Constraints:**
- HARD: Each cell is independent — don't merge cells or skip perspectives.
- SOFT: Start with the most critical perspective (usually System or Technology).
- DO NOT USE WHEN: System is small enough that a single architecture document suffices.

**Related:** 1.1 Axiomatic Design (detailed design), 1.20 VSM (organizational view)

---

## Domain 2: Strategic Management

Frameworks: 1.12 Blue Ocean | 1.13 ERRC Grid | 1.14 Lean | 1.15 Little's Law | 1.16 Six Sigma | 1.17 Porter's Five Forces | 1.18 Balanced Scorecard | 1.19 OODA Loop

[Back to Selection Guide](#framework-selection-guide) | [Back to Cynefin Router](#cynefin-router)

### 1.12 Blue Ocean Strategy
**Originator:** W. Chan Kim & Renee Mauborgne | **Domain:** Strategic planning | **Tier:** 2 | **Cynefin Fit:** Complex

**Purpose:** Create uncontested market space by simultaneously pursuing differentiation and low cost.

**SE Translation:** Product strategy. Instead of competing on the same features as competitors, identify factors to eliminate/reduce (saving cost) and raise/create (adding unique value). Developer tools example: eliminate complex configuration, create opinionated defaults.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Industry value factors | text array | Yes | Key attributes customers value |
| Competitor positions | numeric matrix | Yes | Score per competitor per factor |
| Your current position | numeric array | Yes | Your scores per factor |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Strategy canvas | graph | Value curves for all players |
| ERRC actions | object | {eliminate, reduce, raise, create} lists |
| Uncontested space | text | Description of blue ocean opportunity |

**Execution Pipeline:**
1. Map industry value factors
2. Score competitors on each factor (strategy canvas)
3. Score your current position
4. Apply ERRC grid (1.13) to define new value curve
5. Validate the new curve creates buyer utility
6. Test cost structure viability

**Constraints:**
- HARD: Must have accurate competitive data — wrong baselines yield wrong strategy.
- SOFT: Involve customers in validating the new value curve.
- DO NOT USE WHEN: You're in a winner-take-all market where differentiation doesn't matter (pure commodity).

**Related:** 1.13 ERRC Grid (the action tool), 1.17 Porter's Five Forces (baseline analysis), 1.37 Diffusion (adoption planning)

---

### 1.13 ERRC Grid
**Originator:** Kim & Mauborgne | **Domain:** Value proposition | **Tier:** 1 | **Cynefin Fit:** Complicated

**Purpose:** Systematically decide which factors to Eliminate, Reduce, Raise, or Create to differentiate.

**SE Translation:** Feature scope planning. For every feature/capability: should we eliminate it (nobody uses it), reduce it (over-engineered), raise it (underinvested), or create something new (unmet need)?

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Industry value factors | text array | Yes | Standard factors in the industry |
| Current factor levels | numeric array | Yes | Industry baseline |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| ERRC grid | table | 4-quadrant action plan |
| Strategic focus statement | text | Concise differentiation thesis |

**Execution Pipeline:**
1. List all value factors in the industry
2. For each factor, classify: Eliminate, Reduce, Raise, or Create
3. Validate: eliminations save cost, creations add unique value
4. Formulate strategic focus statement
5. Test with target customers

**Constraints:**
- HARD: Must actually eliminate/reduce things — if you only add, you're not doing Blue Ocean, you're doing feature bloat.
- SOFT: Aim for 2+ eliminations and 1+ creations.
- DO NOT USE WHEN: You're optimizing an existing product within its current value curve.

**Related:** 1.12 Blue Ocean (parent strategy), 1.8 QFD (alternative prioritization)

---

### 1.14 Lean Operations
**Originator:** Taiichi Ohno / Toyota | **Domain:** Operations | **Tier:** 2 | **Cynefin Fit:** Clear

**Purpose:** Eliminate the 7 wastes (muda) to maximize value-add time in a process.

**SE Translation:** Development pipeline optimization. The 7 wastes mapped to software: (1) Transport = handoffs between teams, (2) Inventory = WIP/PR backlog, (3) Motion = context switching, (4) Waiting = blocked tasks, (5) Over-processing = testing every browser for backend changes, (6) Over-production = features shipped but unused, (7) Defects = bugs requiring hotfixes.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Value stream map | diagram/text | Yes | Process flow from start to customer |
| Customer demand (takt time) | numeric | Yes | Required production rate |
| Current cycle times | numeric array | Yes | Time per step |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Takt time | numeric | Target cycle time |
| Waste identification | text array | 7-waste categories found |
| Flow improvements | text array | Specific changes |

**Math:**
- Takt time: `available_time / customer_demand`
- Flow efficiency: `value_add_time / lead_time`

**Execution Pipeline:**
1. Map the value stream end-to-end
2. Calculate takt time from demand
3. Identify the 7 wastes at each step
4. Prioritize waste elimination by impact
5. Redesign flow
6. Measure improvement

**Constraints:**
- HARD: Must map the actual process, not the ideal one.
- SOFT: Start with the biggest waste, not the easiest.
- DO NOT USE WHEN: Process is genuinely novel (no established flow to optimize).

**Related:** 1.15 Little's Law (queue math), 1.21 TOC (constraint focus), 1.16 Six Sigma (quality companion)

---

### 1.15 Little's Law
**Originator:** John Little | **Domain:** Queuing theory | **Tier:** 1 | **Cynefin Fit:** Clear

**Purpose:** Relate work-in-process, throughput rate, and cycle time: L = lambda * W.

**SE Translation:** Task queue analysis. If you have 45 pending PRs (L), arriving at 3/day (lambda), average wait is 15 days (W). To halve wait time: either halve arrivals or double review capacity.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Any 2 of {L, lambda, W} | numeric | Yes | Queue length, arrival rate, or wait time |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| The 3rd variable | numeric | Calculated from L = lambda * W |
| Sensitivity analysis | text | How changes propagate |

**Math:**
- `L = lambda * W` (exact, no assumptions needed for stable systems)
- `W = L / lambda`
- `lambda = L / W`

**Execution Pipeline:**
1. Identify the system boundary (what's "in" the queue)
2. Measure any two of {L, lambda, W}
3. Calculate the third
4. Interpret: is the bottleneck arrival rate (too many items) or service rate (too slow)?
5. Model interventions

**Constraints:**
- HARD: System must be in steady state (arrivals approximately equal departures over time).
- SOFT: Measure over a sufficient time window to smooth variance.
- DO NOT USE WHEN: System is transient (startup, burst), or queue is unbounded.

**Related:** 1.21 TOC (find the constraint), 1.14 Lean (eliminate waste in flow)

---

### 1.16 Six Sigma
**Originator:** Bill Smith / Motorola | **Domain:** Quality management | **Tier:** 1 | **Cynefin Fit:** Clear

**Purpose:** Measure and improve process capability using statistical methods; target 3.4 DPMO.

**SE Translation:** Process capability measurement for CI/CD, deployment, or any repeatable process. Calculate your sigma level: how many defects per million opportunities? A deployment process with 1% failure rate = ~3.8 sigma.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Defect count | numeric | Yes | Number of defects found |
| Opportunity count | numeric | Yes | Total opportunities for defects |
| Total units | numeric | Yes | Production volume |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| DPMO | numeric | Defects per million opportunities |
| Sigma level | numeric [1-6] | Process capability rating |
| Cpk | numeric | Process centering index |

**Math:**
- `DPMO = (defects / opportunities) * 1,000,000`
- `Cpk = min((USL - mean) / (3*sigma), (mean - LSL) / (3*sigma))`

**Execution Pipeline:**
1. Define what constitutes a "defect" and an "opportunity"
2. Collect data over a meaningful period
3. Calculate DPMO
4. Convert to sigma level
5. If Cpk < 1.33, process is not capable — identify root causes
6. Apply DMAIC (Define-Measure-Analyze-Improve-Control)

**Constraints:**
- HARD: "Defect" and "opportunity" definitions must be consistent across measurements.
- SOFT: Need sufficient sample size for statistical significance.
- DO NOT USE WHEN: Process is inherently creative/non-repeatable (research, design exploration).

**Related:** 1.3 Taguchi S/N (robustness), 1.14 Lean (waste), 1.21 TOC (constraints)

---

### 1.17 Porter's Five Forces
**Originator:** Michael Porter | **Domain:** Competitive analysis | **Tier:** 2 | **Cynefin Fit:** Complicated

**Purpose:** Analyze industry competitive structure through 5 forces that determine profitability.

**SE Translation:** Competitive positioning for developer tools, platforms, or services. The 5 forces: (1) Supplier power (cloud provider lock-in), (2) Buyer power (enterprise customers), (3) Competitive rivalry (feature parity), (4) Threat of substitutes (open-source alternatives), (5) Threat of new entrants (low barriers = more competition).

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Industry definition | text | Yes | Market boundaries |
| Supplier landscape | text array | Yes | Key suppliers |
| Buyer characteristics | text array | Yes | Customer segments |
| Substitutes | text array | Yes | Alternative products |
| Competitive intensity | text array | Yes | Competitor characteristics |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Force strength ratings | numeric [1-5] per force | Intensity scores |
| Competitive intensity | text | Overall market attractiveness |
| Strategic positioning | text | Recommended relative positioning |

**Execution Pipeline:**
1. Define the industry scope
2. Rate each of the 5 forces (1-5 intensity)
3. Identify the dominant force(s)
4. Assess overall profit potential
5. Develop strategy relative to dominant forces

**Constraints:**
- HARD: Must define industry boundaries clearly — too broad or narrow distorts analysis.
- SOFT: Update regularly as industry structure changes.
- DO NOT USE WHEN: Market is nascent (no established forces yet), or you're a monopolist.

**Related:** 1.12 Blue Ocean (escape the five forces), 1.33 TCE (make/buy decisions), 1.51 Core Competence (what to compete on)

---

### 1.18 Balanced Scorecard
**Originator:** Kaplan & Norton | **Domain:** Strategic management | **Tier:** 2 | **Cynefin Fit:** Complicated

**Purpose:** Align operational metrics to strategy across 4 perspectives: Financial, Customer, Process, Learning & Growth.

**SE Translation:** Engineering metrics alignment. Don't just track velocity — connect Learning (training, skill acquisition) to Process (deployment frequency, MTTR) to Customer (NPS, churn) to Financial (revenue, cost). Ensures engineering metrics serve business strategy.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Strategy statement | text | Yes | Vision and direction |
| KPIs per perspective | object | Yes | {perspective: [kpi, target, initiative]} |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Causality chain | graph | Learning -> Process -> Customer -> Financial |
| Performance dashboard | table | KPI tracking with variance |

**Execution Pipeline:**
1. Define strategy in one sentence
2. For each perspective, define 3-5 KPIs with targets
3. Map causal chains (how does improving Learning affect Process?)
4. Assign owners and initiatives
5. Review monthly

**Constraints:**
- HARD: Causality must be real, not assumed — validate that improving a leading indicator actually drives the lagging one.
- SOFT: Keep KPI count manageable (3-5 per perspective).
- DO NOT USE WHEN: Strategy is undefined or changing weekly.

**Related:** 1.17 Porter's Five Forces (informs strategy), 1.21 TOC (constraint focus)

---

### 1.19 OODA Loop
**Originator:** John Boyd | **Domain:** Decision-making | **Tier:** 1 | **Cynefin Fit:** Chaotic

**Purpose:** Cycle through Observe-Orient-Decide-Act faster than the competition to gain advantage.

**SE Translation:** Incident response, competitive response, rapid iteration. The key is Orient (mental model update) — the fastest team to update their understanding and act wins. Applicable to production incidents, market shifts, technology disruptions.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Situation | text | Yes | Current operational reality |
| Available information | text/data | Yes | Intelligence and sensor data |
| Decision options | text array | Yes | Possible actions |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Decision | text | Selected course of action |
| Tempo advantage | numeric | Speed vs competitor |

**Math:**
- Cycle time = `observe_time + orient_time + decide_time + act_time`
- Tempo advantage = `(their_cycle - our_cycle) / their_cycle * 100%`

**Execution Pipeline:**
1. Observe: gather raw data from the environment
2. Orient: update mental model, synthesize, identify patterns
3. Decide: select action from options
4. Act: execute immediately
5. Loop: re-observe the results

**Constraints:**
- HARD: Orientation must actually update the mental model — don't just confirm priors.
- SOFT: Optimize for Orient speed (the bottleneck for most teams).
- DO NOT USE WHEN: Decision is irreversible and high-stakes (slow down, use Bayesian analysis instead).

**Related:** 1.49 Bayesian Inference (for high-stakes decisions), 1.35 Bounded Rationality (satisficing under pressure)

---

## Domain 3: Systems Theory

Frameworks: 1.20 VSM | 1.21 TOC | 1.22 Throughput Accounting | 1.23 Cynefin | 1.24 System Dynamics | 1.25 Cybernetics | 1.26 Control Theory | 1.27 Autopoiesis | 1.28 SSM | 1.29 CATWOE | 1.30 GST

[Back to Selection Guide](#framework-selection-guide) | [Back to Cynefin Router](#cynefin-router)

### 1.20 Viable System Model (VSM)
**Originator:** Stafford Beer | **Domain:** Systems management | **Tier:** 3 | **Cynefin Fit:** Complex

**Purpose:** Diagnose organizational viability through 5 systems (S1-S5) that any viable organization must have.

**SE Translation:** Engineering org health. S1=Operations (engineering teams), S2=Coordination (processes that prevent teams from conflicting), S3=Control (engineering management), S4=Intelligence (strategy/R&D), S5=Policy (mission/values). Missing or weak systems predict organizational failure.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Organizational structure | diagram/text | Yes | Reporting lines |
| Communication channels | text array | Yes | Information flows |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Viability diagnosis | report | Health per system (S1-S5) |
| Recommendations | text array | Structural improvements |

**Execution Pipeline:**
1. Map S1 (operations — who does the work?)
2. Map S2 (coordination — what prevents conflicts?)
3. Map S3 (control — who manages resources?)
4. Map S4 (intelligence — who scans the environment?)
5. Map S5 (policy — what's the identity/purpose?)
6. Rate each system's health, identify gaps

**Constraints:**
- HARD: All 5 systems must exist — missing one means non-viable.
- HARD: Model is recursive — each S1 contains its own S1-S5.
- DO NOT USE WHEN: Organization is very small (<10 people) and informal.

**Related:** 1.50 Schein's Culture (complementary — VSM for structure, Schein for culture), 1.34 Principal-Agent (incentive alignment within systems)

---

### 1.21 Theory of Constraints (TOC)
**Originator:** Eliyahu Goldratt | **Domain:** Operations | **Tier:** 2 | **Cynefin Fit:** Complicated

**Purpose:** Identify and exploit the system's bottleneck (constraint) through a 5-step focusing process.

**SE Translation:** Pipeline optimization. Every system has one constraint limiting throughput. Find it (code review queue? CI build time? deployment approval?), exploit it (optimize the constraint), subordinate everything else to it (don't optimize non-constraints), elevate it (invest to increase capacity), repeat.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Process chain | text array | Yes | Sequence of operations |
| Capacities per step | numeric array | Yes | Maximum throughput |
| Demand | numeric | Yes | Market demand |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Identified constraint | text | Most restrictive step |
| 5-step recommendations | text array | Specific actions |
| Throughput improvement | numeric (%) | Revenue upside |

**Math:**
- Bottleneck = `min(capacity_i)` for all steps
- Current throughput = bottleneck capacity

**Execution Pipeline:**
1. **Identify** the constraint (lowest-capacity step)
2. **Exploit** the constraint (make it as efficient as possible)
3. **Subordinate** everything else (align to constraint's pace)
4. **Elevate** the constraint (invest to increase its capacity)
5. **Repeat** (the constraint has moved — find the new one)

**Constraints:**
- HARD: Only one constraint at a time — optimizing non-constraints is waste.
- SOFT: Don't elevate before exploiting (cheap fixes first).
- DO NOT USE WHEN: System has no clear sequential dependency (pure parallel processing).

**Related:** 1.15 Little's Law (queue math), 1.14 Lean (waste elimination), 1.22 Throughput Accounting (financial view)

---

### 1.22 Throughput Accounting
**Originator:** Eliyahu Goldratt | **Domain:** Financial performance | **Tier:** 1 | **Cynefin Fit:** Clear

**Purpose:** Evaluate decisions based on throughput (T), operating expense (OE), and investment (I) rather than cost accounting.

**SE Translation:** Financial analysis of engineering decisions. Throughput = revenue minus truly variable costs. Every decision should be evaluated: does it increase T, decrease OE, or decrease I? If yes to any without hurting others, do it.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Revenue per unit | numeric | Yes | Selling price |
| Totally variable costs | numeric | Yes | Direct material costs |
| Operating expenses | numeric | Yes | Fixed costs |
| Investment | numeric | Yes | Capital invested |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Throughput (T) | numeric | (revenue - TVC) * quantity |
| Net Profit | numeric | T - OpEx |
| ROI | numeric (%) | NP / investment |

**Math:**
- `T = (price - TVC) * quantity`
- `NP = T - OpEx`
- `ROI = NP / investment`

**Execution Pipeline:**
1. Calculate current Throughput
2. Calculate Net Profit and ROI
3. For each proposed change, estimate impact on T, OE, I
4. Prioritize changes that increase T (highest leverage)
5. Then changes that decrease OE, then decrease I

**Constraints:**
- HARD: Only truly variable costs go in TVC — don't include allocated overhead.
- SOFT: Throughput improvement almost always beats cost cutting.
- DO NOT USE WHEN: System has no clear revenue/throughput metric.

**Related:** 1.21 TOC (identifies what to improve), 1.15 Little's Law (flow perspective)

---

### 1.23 Cynefin Framework
**Originator:** Dave Snowden | **Domain:** Problem classification | **Tier:** 1 | **Cynefin Fit:** All

**Purpose:** Classify a situation into one of 5 domains to determine the appropriate management approach.

**SE Translation:** Meta-router. Before applying any framework, classify the problem: Clear (use best practice), Complicated (analyze with experts), Complex (probe and sense), Chaotic (act first, stabilize). Prevents the most common failure: applying the wrong type of framework to the wrong type of problem.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Situation description | text | Yes | Problem characteristics |
| Causality clarity | text | Yes | Whether cause-effect is obvious, discoverable, or unknown |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Domain classification | enum | {Clear, Complicated, Complex, Chaotic, Disorder} |
| Prescribed approach | text | Process for this domain |
| Anti-patterns | text array | Common mistakes in this domain |

**Execution Pipeline:**
1. Describe the situation
2. Ask: "Is cause-effect obvious?" → Clear
3. Ask: "Is cause-effect discoverable with analysis?" → Complicated
4. Ask: "Is cause-effect only visible in retrospect?" → Complex
5. Ask: "Is there no discernible cause-effect?" → Chaotic
6. If you can't tell → Disorder (probe to determine)
7. Apply the appropriate management approach

**Constraints:**
- HARD: Don't force-fit a domain — if uncertain, you're in Disorder.
- HARD: Complex problems cannot be solved with Complicated approaches (analysis won't work).
- SOFT: Revisit classification as understanding evolves.
- DO NOT USE WHEN: Problem is clearly technical with a known solution (just solve it).

**Related:** All other frameworks — Cynefin determines which to use.

---

### 1.24 System Dynamics
**Originator:** Jay Forrester | **Domain:** Systems modeling | **Tier:** 3 | **Cynefin Fit:** Complex

**Purpose:** Model complex systems as stocks (accumulations), flows (rates), and feedback loops to understand behavior over time.

**SE Translation:** Modeling codebase dynamics. Technical debt = stock (accumulates). Refactoring = outflow (reduces debt). Feature velocity = inflow (adds debt). Positive feedback: high velocity -> more debt -> slower velocity -> pressure for more velocity -> more debt. Find leverage points to break destructive loops.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| System variables | text array | Yes | Stock and flow quantities |
| Causal relationships | edge array | Yes | {from, to, polarity: +/-} |
| Initial conditions | numeric array | No | Starting values |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Stock-flow model | diagram/equations | System structure |
| Behavior trajectories | time-series | Behavior over time |
| Leverage points | text array | High-impact interventions |

**Math:**
- `Stock(t) = Stock(t-dt) + sum(inflows - outflows) * dt`
- Positive feedback loop: product of chain gains is positive -> exponential growth
- Negative feedback loop: product of chain gains is negative -> equilibrium

**Execution Pipeline:**
1. Identify stocks (things that accumulate)
2. Identify flows (what changes the stocks)
3. Map causal links with polarity (+/-)
4. Identify feedback loops
5. Simulate or reason about behavior over time
6. Find leverage points (where small changes have large effects)

**Constraints:**
- HARD: Must get the feedback loop polarities right — wrong polarity inverts the behavior.
- SOFT: Start with 3-5 variables, expand only as needed.
- DO NOT USE WHEN: System has no meaningful feedback (pure linear pipeline).

**Related:** 1.25 Cybernetics (control perspective), 1.26 Control Theory (quantitative), 1.40 Antifragility (resilience perspective)

---

### 1.25 Cybernetics
**Originator:** Norbert Wiener | **Domain:** Control systems | **Tier:** 2 | **Cynefin Fit:** Complicated

**Purpose:** Study control and communication in systems through feedback mechanisms.

**SE Translation:** Understanding regulation patterns. Any system with a goal and feedback is cybernetic: auto-scaling (goal=target CPU%, feedback=current utilization), rate limiting (goal=max requests, feedback=request count), feature flags (goal=safe deployment, feedback=error rate).

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| System with goal | text | Yes | Target system and desired state |
| Feedback signal | text | Yes | How deviation is measured |
| Control action | text | Yes | What adjusts behavior |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Feedback classification | enum | {negative, positive} |
| Stability assessment | text | Will system reach goal? |
| Equilibrium point | numeric | Stable operating state |

**Execution Pipeline:**
1. Define the system goal (desired state)
2. Identify the feedback signal (how deviation is measured)
3. Identify the control action (what adjusts the system)
4. Classify: negative feedback (stabilizing) or positive feedback (amplifying)
5. Assess stability: does the system converge?

**Constraints:**
- HARD: Positive feedback without bounds leads to runaway — always check for limits.
- SOFT: Most engineered systems need negative feedback for stability.
- DO NOT USE WHEN: System has no goal (pure monitoring, no control).

**Related:** 1.26 Control Theory (quantitative version), 1.24 System Dynamics (modeling), 1.20 VSM (organizational application)

---

### 1.26 Control Theory (PID)
**Originator:** Nicolas Minorsky / various | **Domain:** Automatic control | **Tier:** 2 | **Cynefin Fit:** Clear

**Purpose:** Regulate system output to match a setpoint using proportional, integral, and derivative control.

**SE Translation:** Auto-scaling, rate limiting, adaptive thresholds. P = react proportionally to current error, I = eliminate steady-state offset by accumulating past errors, D = dampen oscillation by predicting future error. Applicable to any system where you adjust a parameter to hit a target.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Setpoint | numeric | Yes | Desired output |
| Process variable | numeric | Yes | Current output |
| PID gains {Kp, Ki, Kd} | numeric triple | Yes | Tuning parameters |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Control signal u(t) | numeric | Output to actuator |
| Settling time | numeric | Time to reach steady state |
| Overshoot | numeric (%) | Peak above setpoint |

**Math:**
- `u(t) = Kp * e(t) + Ki * integral(e(t)dt) + Kd * de/dt`
- P: responds to current error
- I: eliminates steady-state error
- D: dampens oscillation

**Execution Pipeline:**
1. Define setpoint and measurement
2. Choose initial Kp (start with P-only control)
3. Add Ki if steady-state error persists
4. Add Kd if oscillation occurs
5. Tune gains until response is satisfactory

**Constraints:**
- HARD: Gains must be tuned — wrong gains cause instability or sluggishness.
- SOFT: Start with P-only, add I and D incrementally.
- DO NOT USE WHEN: System is nonlinear or discrete (use adaptive control or bang-bang).

**Related:** 1.25 Cybernetics (conceptual foundation), 1.6 STPA (safety analysis of control structures)

---

### 1.27 Autopoiesis
**Originator:** Maturana & Varela | **Domain:** Systems theory | **Tier:** 3 | **Cynefin Fit:** Complex

**Purpose:** Classify systems as self-making (autopoietic) or externally-made (allopoietic).

**SE Translation:** Understanding self-maintaining systems. A microservice that auto-heals, self-scales, and regenerates its state is autopoietic. A system that requires manual intervention for every recovery is allopoietic. Design goal: increase autopoietic properties.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| System description | text | Yes | Components and organization |
| Reproductive process | text | Yes | How system recreates itself |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Classification | enum | {autopoietic, allopoietic} |
| Boundary integrity | text | How system maintains identity |

**Execution Pipeline:**
1. Describe system components and organization
2. Ask: "Does the system produce its own components?"
3. Ask: "Does the system maintain its own boundary?"
4. Classify as autopoietic or allopoietic
5. Identify what prevents autopoiesis (if allopoietic)

**Constraints:**
- HARD: True autopoiesis requires organizational closure — partial self-maintenance doesn't qualify.
- DO NOT USE WHEN: System is inherently externally managed (no self-maintenance expectation).

**Related:** 1.20 VSM (organizational viability), 1.40 Antifragility (resilience spectrum)

---

### 1.28 Soft Systems Methodology (SSM)
**Originator:** Peter Checkland | **Domain:** Problem-solving | **Tier:** 3 | **Cynefin Fit:** Complex

**Purpose:** Structure wicked problems with multiple stakeholders through rich pictures and root definitions.

**SE Translation:** When the problem itself is unclear — multiple teams disagree on what's wrong, requirements conflict, or the situation is "messy." SSM doesn't solve the problem; it structures it enough to find actionable improvements.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Messy problem situation | text | Yes | Unstructured real-world problem |
| Stakeholder interviews | text array | Yes | Multiple perspectives |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Rich pictures | diagram | Informal visual of problem |
| Root definitions | text array | Alternative system definitions (via CATWOE) |
| Actionable changes | text array | Feasible improvements |

**Execution Pipeline:**
1. Express the problem situation (rich picture)
2. Select relevant human activity systems
3. Build root definitions using CATWOE (1.29)
4. Build conceptual models for each root definition
5. Compare models to reality
6. Define actionable changes

**Constraints:**
- HARD: Must include multiple perspectives — single-stakeholder SSM is just regular analysis.
- SOFT: Rich pictures should be informal, not formal diagrams.
- DO NOT USE WHEN: Problem is well-defined and agreed upon.

**Related:** 1.29 CATWOE (builds root definitions), 1.23 Cynefin (classifies the problem first)

---

### 1.29 CATWOE Analysis
**Originator:** Peter Checkland | **Domain:** Systems definition | **Tier:** 1 | **Cynefin Fit:** Complicated

**Purpose:** Build a complete system definition by specifying 6 elements: Customer, Actor, Transformation, Worldview, Owner, Environment.

**SE Translation:** Stakeholder analysis for any system definition. Forces you to explicitly state: who benefits (Customer), who does the work (Actor), what changes (Transformation), what belief makes this meaningful (Worldview), who could stop it (Owner), what constrains it (Environment).

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Transformation | text | Yes | What changes or is accomplished |
| Context | text | Yes | Organizational environment |
| Stakeholder list | text array | Yes | People affected |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| 6-element definition | text | Complete system definition |
| Stakeholder perspectives | text array | How each views the system |

**Execution Pipeline:**
1. Define T: What is being transformed (input -> output)?
2. Define C: Who benefits or suffers?
3. Define A: Who performs the transformation?
4. Define W: What worldview makes this meaningful?
5. Define O: Who could stop this?
6. Define E: What external constraints exist?

**Constraints:**
- HARD: Worldview (W) is the most important and most often skipped — it reveals hidden assumptions.
- SOFT: Generate multiple CATWOE definitions for the same system (different worldviews).
- DO NOT USE WHEN: System is purely technical with no human stakeholders.

**Related:** 1.28 SSM (parent methodology), 1.34 Principal-Agent (incentive analysis of actors/owners)

---

### 1.30 General Systems Theory (GST) Isomorphisms
**Originator:** Ludwig von Bertalanffy | **Domain:** Cross-domain analysis | **Tier:** 3 | **Cynefin Fit:** Complex

**Purpose:** Identify structural similarities (isomorphisms) across different domains to transfer solutions.

**SE Translation:** Cross-domain solution transfer. Exponential growth works the same in bacteria, rumors, and user signups. Feedback loops appear in thermostats, auto-scalers, and team dynamics. Recognizing isomorphisms lets you apply solutions from one domain to another.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| System observations | object array | Yes | {phenomenon, domain, properties} |
| Domain pairs | array of tuples | No | Which domains to compare |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Identified isomorphisms | text array | Structural similarities |
| Principle transfer candidates | text array | Laws applicable across domains |

**Execution Pipeline:**
1. Observe phenomena in multiple domains
2. Abstract to structural properties
3. Compare structures across domains
4. Identify isomorphisms (same structure, different substance)
5. Transfer solutions from well-understood domain to poorly-understood one

**Constraints:**
- HARD: Structural similarity doesn't guarantee behavioral similarity — validate before applying.
- SOFT: Start with well-established isomorphisms (growth, feedback, hierarchy).
- DO NOT USE WHEN: Domains are too different for meaningful structural comparison.

**Related:** All domain frameworks — GST connects them.

---

## Domain 4: Economic & Decision Theory

Frameworks: 1.31 Nash Equilibrium | 1.32 Prospect Theory | 1.33 TCE | 1.34 Principal-Agent | 1.35 Bounded Rationality | 1.36 Disruptive Innovation | 1.37 Diffusion | 1.38 SIT | 1.39 Scenario Planning | 1.40 Antifragility

[Back to Selection Guide](#framework-selection-guide) | [Back to Cynefin Router](#cynefin-router)

### 1.31 Nash Equilibrium
**Originator:** John Nash | **Domain:** Game theory | **Tier:** 3 | **Cynefin Fit:** Complicated

**Purpose:** Find strategy profiles where no player can improve by unilaterally changing their strategy.

**SE Translation:** Multi-team decision analysis. When teams make interdependent decisions (API contracts, shared resources, platform choices), Nash equilibrium predicts the stable outcome. If each team optimizes independently, where do they end up? Is that outcome good for the organization?

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Players | text array | Yes | Decision makers |
| Strategies per player | array of arrays | Yes | Available choices |
| Payoff functions | numeric matrix | Yes | Outcome per combination |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Equilibrium profile | text array | Optimal strategy per player |
| Stability analysis | text | Deviation incentives |

**Math:**
- Nash equilibrium: `(s1*, s2*, ..., sn*)` where no player can improve unilaterally
- Best response: `BR_i(s_-i) = argmax u_i(s_i, s_-i)`

**Execution Pipeline:**
1. Identify players and their available strategies
2. Build payoff matrix
3. For each player, find best response to each opponent strategy
4. Find profiles where all players play best responses simultaneously
5. Check for multiple equilibria
6. Assess if equilibrium outcome is desirable

**Constraints:**
- HARD: Players must be rational and self-interested — altruistic players need different models.
- SOFT: Check for Pareto improvements (everyone can be better off).
- DO NOT USE WHEN: Players can communicate and cooperate (use cooperative game theory instead).

**Related:** 1.34 Principal-Agent (incentive alignment), 1.32 Prospect Theory (behavioral deviations)

---

### 1.32 Prospect Theory
**Originator:** Kahneman & Tversky | **Domain:** Decision psychology | **Tier:** 2 | **Cynefin Fit:** Complex

**Purpose:** Model how people actually make decisions under risk — loss aversion, probability weighting, reference dependence.

**SE Translation:** Framing engineering decisions. People weigh losses 2.25x more than gains. "Rewrite costs $100k" (loss frame -> resistance) vs "Rewrite saves $200k in maintenance" (gain frame -> acceptance). Use to frame proposals, predict stakeholder reactions, design incentives.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Outcomes | numeric array | Yes | Gains/losses in dollars |
| Probabilities | numeric array [0,1] | Yes | Likelihood of each outcome |
| Reference point | numeric | No | Baseline (default: 0) |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Subjective value | numeric | Weighted value with loss aversion |
| Risk prediction | text | Whether prospect seems attractive |

**Math:**
- Value function: `v(x) = x^alpha` for gains, `v(x) = -lambda * (-x)^beta` for losses
- Loss aversion: `lambda ~ 2.25`
- Probability weighting: `w(p) = p^gamma / (p^gamma + (1-p)^gamma)^(1/gamma)`

**Execution Pipeline:**
1. Define outcomes and their probabilities
2. Set the reference point
3. Calculate subjective values using the value function
4. Apply probability weighting
5. Compare to rational expected value
6. Predict actual decision behavior

**Constraints:**
- HARD: Reference point matters enormously — changing it changes the decision.
- SOFT: Always consider both gain and loss frames.
- DO NOT USE WHEN: Decision makers are experienced and calibrated (they partially debias).

**Related:** 1.35 Bounded Rationality (cognitive limits), 1.49 Bayesian Inference (rational ideal), 1.34 Principal-Agent (incentive design)

---

### 1.33 Transaction Cost Economics (TCE)
**Originator:** Oliver Williamson | **Domain:** Organizational choice | **Tier:** 2 | **Cynefin Fit:** Complicated

**Purpose:** Determine whether to make (internal), buy (market), or hybrid — based on transaction characteristics.

**SE Translation:** Build vs buy analysis. High asset specificity (unique to your product) -> build. Low specificity (generic CRUD, auth, logging) -> buy/use open source. High uncertainty + high frequency + high specificity -> vertical integration (build and own).

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Asset specificity | numeric [0-100%] | Yes | Value lost if used elsewhere |
| Frequency | numeric | Yes | How often transaction occurs |
| Uncertainty | numeric [0-100%] | Yes | Environmental unpredictability |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Recommendation | enum | {make, buy, hybrid} |
| Governance form | text | Contract type |

**Math:**
- TCE score: `k1 * asset_specificity + k2 * frequency + k3 * uncertainty`
- High score -> make (vertical integration), Low score -> buy (market)
- Total cost: `production_cost + transaction_cost`

**Execution Pipeline:**
1. Rate asset specificity (how unique is this to your product?)
2. Rate frequency (how often do you need this?)
3. Rate uncertainty (how unpredictable is the environment?)
4. Calculate TCE score
5. Recommend governance form
6. Estimate total cost of each option

**Constraints:**
- HARD: Must include transaction costs, not just production costs — contracting, monitoring, enforcement.
- SOFT: Reassess when asset specificity changes (commoditization).
- DO NOT USE WHEN: Decision is purely technical with no economic dimension.

**Related:** 1.17 Porter's Five Forces (industry context), 1.51 Core Competence (strategic capability)

---

### 1.34 Principal-Agent Problem
**Originator:** Jensen & Meckling | **Domain:** Incentive alignment | **Tier:** 2 | **Cynefin Fit:** Complex

**Purpose:** Design contracts/incentives to align agent behavior with principal objectives despite information asymmetry.

**SE Translation:** Team incentive alignment. Engineers (agents) optimize for what's measured (commits, velocity, story points). Managers (principals) want outcomes (customer satisfaction, reliability). Find misalignments: are metrics driving the right behavior? Add outcome-based metrics to evaluation.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Principal objectives | text | Yes | What principal wants |
| Agent capabilities | text array | Yes | What agent can do |
| Information asymmetry | text | Yes | What principal can't observe |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Contract design | text | Compensation structure |
| Incentive alignment | numeric | How well aligned |
| Agency cost | numeric | Loss from misalignment |

**Execution Pipeline:**
1. Identify principals and agents
2. Map what each wants
3. Identify information asymmetry (what can't the principal see?)
4. Find misaligned incentives
5. Design monitoring or incentive mechanisms
6. Estimate agency cost reduction

**Constraints:**
- HARD: Perfect monitoring is impossible — must design for observable proxies.
- SOFT: Use multiple metrics to prevent gaming any single one.
- DO NOT USE WHEN: Principal and agent goals are genuinely aligned (no conflict).

**Related:** 1.31 Nash Equilibrium (game-theoretic view), 1.50 Schein's Culture (cultural dimension), 1.20 VSM (structural context)

---

### 1.35 Bounded Rationality
**Originator:** Herbert Simon | **Domain:** Decision-making | **Tier:** 1 | **Cynefin Fit:** Complex

**Purpose:** Accept that optimization is impossible under real constraints — satisfice instead.

**SE Translation:** Knowing when "good enough" beats optimal. With limited time, information, and cognitive capacity, set a minimum acceptable threshold and take the first option that meets it. Stops over-analysis, premature optimization, and infinite bikeshedding.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Decision problem | text | Yes | Choice situation |
| Cognitive constraints | text array | Yes | Time, memory, attention limits |
| Aspiration level | numeric | Yes | Minimum acceptable satisfaction |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Satisficing threshold | numeric | Minimum acceptable outcome |
| Stopping rule | text | When to stop searching |

**Math:**
- Satisfice: choose first alternative where `value(alt) >= aspiration_level`
- Optimal search cost: stop when `expected_value_of_next < search_cost`

**Execution Pipeline:**
1. Define the decision and constraints
2. Set aspiration level (what's "good enough"?)
3. Evaluate options sequentially
4. Accept first option meeting threshold
5. Stop searching

**Constraints:**
- HARD: Aspiration level must be realistic — too high = never decide, too low = bad outcomes.
- SOFT: Raise aspiration level as search progresses and you learn what's available.
- DO NOT USE WHEN: Decision is irreversible and high-stakes (invest in fuller analysis).

**Related:** 1.19 OODA Loop (speed complement), 1.32 Prospect Theory (how framing biases decisions)

---

### 1.36 Disruptive Innovation
**Originator:** Clayton Christensen | **Domain:** Innovation strategy | **Tier:** 2 | **Cynefin Fit:** Complex

**Purpose:** Predict when and how a simpler/cheaper entrant will displace an established incumbent.

**SE Translation:** Technology adoption threat assessment. When a new tool/platform is "not good enough" for current users but improving fast — watch out. Disruption occurs when the entrant's trajectory crosses the incumbent's and overshoots mainstream needs.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Incumbent trajectory | plot | Yes | Performance over time |
| Entrant trajectory | plot | Yes | Entrant's improvement curve |
| Customer value hierarchy | text array | Yes | What matters most |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Disruption prediction | text | Whether entrant will surpass |
| Timeline | numeric (years) | When trajectories cross |
| Vulnerable segments | text array | Where entrant gains first |

**Execution Pipeline:**
1. Map incumbent's performance trajectory
2. Map entrant's performance trajectory
3. Identify where trajectories intersect
4. Determine which customer segments are vulnerable first
5. Assess incumbent's response options

**Constraints:**
- HARD: Not all innovation is disruptive — must meet the specific criteria of bottom-up improvement.
- SOFT: Watch for sustaining innovations mislabeled as disruptive.
- DO NOT USE WHEN: Entrant is competing on the same performance dimension (that's sustaining innovation).

**Related:** 1.37 Diffusion of Innovations (adoption modeling), 1.12 Blue Ocean (alternative strategy)

---

### 1.37 Diffusion of Innovations
**Originator:** Everett Rogers | **Domain:** Change management | **Tier:** 2 | **Cynefin Fit:** Complex

**Purpose:** Model how innovations spread through a population following an S-curve adoption pattern.

**SE Translation:** Predicting tool/feature adoption. Innovators (2.5%) try anything, Early Adopters (13.5%) need relative advantage, Early Majority (34%) need proof and ease. Target Early Adopters first, then cross the chasm to Early Majority.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Innovation characteristics | object | Yes | {relative_advantage, compatibility, complexity, trialability, observability} |
| Social system | object | Yes | Population structure |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Adoption curve | S-curve | Cumulative adoption over time |
| Adopter categories | object | Innovators/Early/Majority/Late/Laggards |
| Adoption rate | numeric | Steepness of curve |

**Math:**
- Logistic: `N(t)/K = 1 / (1 + e^(-r(t - t0)))`
- Innovators ~2.5%, Early Adopters ~13.5%, Early Majority ~34%, Late Majority ~34%, Laggards ~16%

**Execution Pipeline:**
1. Characterize the innovation (5 attributes)
2. Identify the social system and opinion leaders
3. Predict adoption rate from innovation characteristics
4. Target the right adopter segment
5. Plan for "the chasm" between Early Adopters and Early Majority

**Constraints:**
- HARD: Must cross the chasm — many innovations die between Early Adopters and Early Majority.
- SOFT: Reduce complexity and increase trialability to accelerate adoption.
- DO NOT USE WHEN: Adoption is mandated (no choice = no diffusion curve).

**Related:** 1.12 Blue Ocean (market creation), 1.36 Disruptive Innovation (displacement)

---

### 1.38 Systematic Inventive Thinking (SIT)
**Originator:** Roni Horowitz / Genrich Altshuller | **Domain:** Innovation | **Tier:** 2 | **Cynefin Fit:** Complicated

**Purpose:** Generate innovations using 5 templates applied to the product's existing components (closed-world constraint).

**SE Translation:** Constrained creative problem solving. Instead of brainstorming from scratch, apply 5 templates to what exists: Subtraction (remove a feature), Multiplication (duplicate with variation), Division (break into parts), Task Unification (give existing component new job), Attribute Dependency (link two variables).

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Product/problem | text | Yes | Current situation |
| Closed-world resources | text array | Yes | What's available within system |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Innovations via 5 templates | array | {template, innovation, description} |
| Feasibility assessment | text | Implementation notes |

**Execution Pipeline:**
1. Inventory all components in the current system (closed world)
2. Apply each of the 5 templates systematically
3. Generate at least one innovation per template
4. Assess feasibility of each
5. Select most promising for prototyping

**Constraints:**
- HARD: Must work within closed world — don't introduce external resources.
- SOFT: Apply all 5 templates, not just the first that yields an idea.
- DO NOT USE WHEN: Problem requires fundamentally new technology not in the closed world.

**Related:** 1.4 TRIZ Matrix (complementary innovation method), 1.5 TRIZ 40 Principles (broader principle set)

---

### 1.39 Scenario Planning
**Originator:** Pierre Wack / Shell | **Domain:** Strategic planning | **Tier:** 2 | **Cynefin Fit:** Complex

**Purpose:** Build 2-4 plausible future scenarios from critical uncertainties to stress-test strategies.

**SE Translation:** Planning under deep uncertainty. When you don't know which technology will win, how the market will shift, or what regulations will come — build scenarios. Identify the 2 most uncertain driving forces, create a 2x2 matrix, develop narratives for each quadrant. Test your strategy against all 4.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Strategic question | text | Yes | What decision needs made? |
| Driving forces | text array | Yes | Major external factors |
| Critical uncertainties | text array | Yes | Most uncertain factors |
| Time horizon | numeric (years) | Yes | Planning timeframe |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| 2x2 scenario matrix | table | 4 scenarios from 2 axes |
| Scenario narratives | text array [4] | Coherent stories |
| Strategy robustness | text | Which strategy works best per scenario |
| Leading indicators | text array | Early signals |

**Math:**
- Strategy robustness = `scenarios_where_strategy_succeeds / 4`

**Execution Pipeline:**
1. Define the strategic question
2. List driving forces and critical uncertainties
3. Select the 2 most uncertain, most impactful forces
4. Build 2x2 matrix (4 scenarios)
5. Write narrative for each scenario
6. Test strategy robustness against all 4

**Constraints:**
- HARD: Scenarios must be plausible, not just possible — don't include "asteroid destroys everything."
- HARD: Scenarios are not predictions — they're for preparation.
- SOFT: Include one optimistic, one pessimistic, two mixed.
- DO NOT USE WHEN: Future is largely predictable (use forecasting instead).

**Related:** 1.40 Antifragility (robustness complement), 1.23 Cynefin (classifies uncertainty)

---

### 1.40 Antifragility
**Originator:** Nassim Nicholas Taleb | **Domain:** Risk resilience | **Tier:** 3 | **Cynefin Fit:** Complex

**Purpose:** Design systems that benefit from volatility, randomness, and stress rather than merely surviving it.

**SE Translation:** Beyond resilience. Fragile systems break under stress (monoliths under load). Robust systems survive (redundancy). Antifragile systems get better (chaos engineering -> better monitoring -> fewer incidents). Design for positive convexity: limited downside, unlimited upside.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| System description | text | Yes | What's being analyzed |
| Stressor profile | text array | Yes | Types of shocks possible |
| Current response | text | Yes | How system handles stress |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Classification | enum | {fragile, robust, resilient, antifragile} |
| Convexity analysis | numeric | Asymmetry of payoff |
| Barbell strategy | text | Safe + risky mix |

**Math:**
- Fragile: negative convexity (harm from volatility)
- Robust: convexity ~ 0
- Antifragile: positive convexity (benefits from volatility)
- Optionality value = `upside_capture - downside_exposure`

**Execution Pipeline:**
1. Describe the system and its stressors
2. Assess current response to stress (fragile/robust/antifragile?)
3. Calculate convexity: does more stress help or hurt?
4. Identify optionality: what choices does the system have?
5. Design barbell strategy: combine very safe + very risky
6. Add skin in the game: ensure decision-makers bear consequences

**Constraints:**
- HARD: Antifragility requires exposure to small stressors — complete protection creates fragility.
- SOFT: Use barbell strategy (not middle-of-road compromise).
- DO NOT USE WHEN: System is in existential crisis (stabilize first with OODA, then build antifragility).

**Related:** 1.39 Scenario Planning (uncertainty preparation), 1.24 System Dynamics (feedback modeling), 1.27 Autopoiesis (self-maintenance)

---

## Domain 5: Cognitive Architectures & AI

Frameworks: 1.41 ACT-R | 1.42 SOAR | 1.43 Transformer | 1.44 Scaling Laws | 1.45 RLHF | 1.46 PPO | 1.47 CoT

[Back to Selection Guide](#framework-selection-guide) | [Back to Cynefin Router](#cynefin-router)

### 1.41 ACT-R
**Originator:** John Anderson | **Domain:** Cognitive modeling | **Tier:** 3 | **Cynefin Fit:** Complicated

**Purpose:** Model human cognition through declarative memory (facts), procedural memory (rules), and activation-based retrieval.

**SE Translation:** Cognitive load modeling for UX and developer experience. Predict how users will remember features, which operations will be slow (high retrieval time), where cognitive overload occurs. Use activation equations to estimate interface complexity.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Task environment | text | Yes | What person is doing |
| Memory contents | object | Yes | {declarative_facts, procedural_rules} |
| Goal state | text | Yes | What person is trying to achieve |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Activation levels | numeric array | Memory strength per item |
| Retrieval predictions | text array | What will be remembered/forgotten |
| Response times | numeric array (ms) | Predicted latencies |

**Math:**
- Activation: `A_i = B_i + sum(S_j) - d * n_i`
- Retrieval probability: `P = exp(A_i / tau) / sum(exp(A_j / tau))`
- Response time: `RT = F * exp(-A / s)`

**Execution Pipeline:**
1. Define the task and goal
2. List declarative facts and procedural rules
3. Calculate activation levels
4. Predict retrieval probabilities and response times
5. Identify cognitive bottlenecks

**Constraints:**
- HARD: Must calibrate parameters to the specific population.
- DO NOT USE WHEN: Modeling expert behavior (experts use chunking not covered by basic ACT-R).

**Related:** 1.42 SOAR (alternative architecture), 1.47 CoT (reasoning perspective)

---

### 1.42 SOAR
**Originator:** Allen Newell | **Domain:** Problem-solving AI | **Tier:** 3 | **Cynefin Fit:** Complicated

**Purpose:** Model problem solving as search through a problem space, with learning from impasses.

**SE Translation:** Problem-solving architecture for AI agents. SOAR's key insight: when stuck (impasse), create a subgoal to resolve the impasse, then learn a production rule so you never get stuck the same way again. Applicable to designing learning agent architectures.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Problem state | text | Yes | Current situation |
| Operator set | text array | Yes | Possible actions |
| Long-term memory | text/rules | Yes | Learned procedures |
| Goal hierarchy | text array | Yes | Nested objectives |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Search trace | text array | Decision sequence |
| Learned chunks | text array | New production rules |
| Decision rationale | text | Explanation of choices |

**Execution Pipeline:**
1. Represent current state and goal
2. Propose applicable operators
3. Select best operator
4. If impasse: create subgoal
5. Resolve subgoal
6. Learn new production rule (chunking)

**Constraints:**
- HARD: Problem must be representable as state-space search.
- DO NOT USE WHEN: Problem has no clear state representation (use SSM instead).

**Related:** 1.41 ACT-R (alternative architecture), 1.47 CoT (reasoning chain)

---

### 1.43 Transformer Neural Network (Attention)
**Originator:** Vaswani et al. | **Domain:** Neural networks | **Tier:** 3 | **Cynefin Fit:** Complicated

**Purpose:** Process sequences by computing attention weights over all positions, enabling context-dependent representations.

**SE Translation:** Understanding and designing attention mechanisms. Core to LLM architecture. The attention mechanism: for each position, compute how much to attend to every other position based on query-key similarity, then combine values weighted by attention.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Token sequence | integer array | Yes | Encoded input |
| Weight matrices (Wq, Wk, Wv) | numeric matrices | Yes | Projection matrices |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Attention weights | numeric matrix [0,1] | Softmax probabilities |
| Context vectors | numeric matrix | Enriched representations |

**Math:**
- `Q = input * Wq, K = input * Wk, V = input * Wv`
- `Attention(Q,K,V) = softmax(QK^T / sqrt(d_k)) * V`
- Multi-head: repeat with different Wq, Wk, Wv, concatenate

**Execution Pipeline:**
1. Encode input tokens
2. Project to Q, K, V spaces
3. Compute attention scores (QK^T / sqrt(d_k))
4. Apply softmax for attention weights
5. Compute weighted combination of V
6. Concatenate multi-head outputs

**Constraints:**
- HARD: Quadratic cost in sequence length — O(n^2) attention.
- SOFT: Use multi-head attention for richer representations.
- DO NOT USE WHEN: Sequence length makes quadratic attention infeasible (use linear attention variants).

**Related:** 1.44 Scaling Laws (how to scale), 1.45 RLHF (alignment training), 1.47 CoT (reasoning evaluation)

---

### 1.44 Scaling Laws
**Originator:** Kaplan et al. / Hoffmann et al. | **Domain:** LLM design | **Tier:** 2 | **Cynefin Fit:** Complicated

**Purpose:** Predict model loss as a function of parameters (N), data (D), and compute (C) via power laws.

**SE Translation:** LLM compute budget planning. Given a compute budget, how should you allocate between model size and training data? Scaling laws give the answer: `L(N,D) ~ a/N^alpha + b/D^beta`. Chinchilla finding: roughly 20 tokens per parameter is compute-optimal.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Model parameters (N) | numeric | Yes | Number of weights |
| Training data (D) | numeric | Yes | Tokens |
| Compute budget (C) | numeric | Yes | FLOPs |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Predicted loss | numeric | Expected validation loss |
| Optimal allocation | object | {N, D} ratio |
| Scaling exponent | numeric | Power-law slope |

**Math:**
- `L(N,D) ~ a/N^alpha + b/D^beta` (alpha ~ 0.07, beta ~ 0.07)
- Chinchilla optimal: `N ~ D/20`

**Execution Pipeline:**
1. Define compute budget
2. Estimate optimal N and D from scaling laws
3. Predict expected loss at target scale
4. Compare to baselines
5. Adjust if constraints apply (memory, latency)

**Constraints:**
- HARD: Scaling laws are empirical fits — extrapolation beyond training data range is risky.
- SOFT: Validate with small-scale experiments first.
- DO NOT USE WHEN: Model architecture differs significantly from studied models.

**Related:** 1.43 Transformer (architecture), 1.45 RLHF (post-training), 1.46 PPO (optimization)

---

### 1.45 RLHF (Reinforcement Learning from Human Feedback)
**Originator:** Christiano et al. / OpenAI | **Domain:** AI alignment | **Tier:** 3 | **Cynefin Fit:** Complex

**Purpose:** Align language model outputs with human preferences using a learned reward model and RL fine-tuning.

**SE Translation:** AI alignment pipeline. Train a reward model on human preference comparisons (A vs B), then use that reward to fine-tune the base model via PPO or similar. Critical for making models helpful, harmless, and honest.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Pretrained model | neural network | Yes | Base LM |
| Human preference data | array | Yes | {prompt, response_A, response_B, preference} |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Aligned model | neural network | Fine-tuned model |
| Reward model | neural network | Preference scorer |

**Math:**
- Preference: `P(yA > yB) = sigma(r(x,yA) - r(x,yB))` (Bradley-Terry)
- Policy loss: `L = -E[log pi_theta(y|x) * r(x,y)]`

**Execution Pipeline:**
1. Collect human preference comparisons
2. Train reward model on preferences
3. Fine-tune policy with RL (using 1.46 PPO)
4. Evaluate alignment improvement
5. Iterate with more preference data

**Constraints:**
- HARD: Reward model quality limits alignment quality — garbage preferences = garbage alignment.
- HARD: Reward hacking: model may exploit reward model weaknesses.
- DO NOT USE WHEN: Sufficient labeled data exists for supervised fine-tuning (simpler).

**Related:** 1.46 PPO (optimization algorithm), 1.44 Scaling Laws (model sizing), 1.47 CoT (evaluation)

---

### 1.46 Proximal Policy Optimization (PPO)
**Originator:** Schulman et al. / OpenAI | **Domain:** Reinforcement learning | **Tier:** 3 | **Cynefin Fit:** Complicated

**Purpose:** Improve RL policies using clipped surrogate objectives to prevent destructively large updates.

**SE Translation:** The optimization engine inside RLHF. PPO constrains each policy update to stay close to the previous policy (trust region), preventing catastrophic forgetting or reward hacking.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Policy | neural network | Yes | Current policy |
| Reward signal | numeric array | Yes | Scalar reward per trajectory |
| Clipping parameter (eps) | numeric | Yes | Trust region threshold (0.1-0.3) |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Updated policy | neural network | Improved parameters |
| Value function | numeric array | Estimated returns |
| Advantage estimates | numeric array | Action advantage |

**Math:**
- Clipped loss: `L_clip = E[min(r_t * A_t, clip(r_t, 1-eps, 1+eps) * A_t)]`
- Importance ratio: `r_t = pi_new(a|s) / pi_old(a|s)`

**Execution Pipeline:**
1. Collect trajectories with current policy
2. Compute advantages
3. Compute importance ratios
4. Apply clipped objective
5. Update policy
6. Repeat

**Constraints:**
- HARD: Clipping parameter must be tuned — too loose = instability, too tight = slow learning.
- DO NOT USE WHEN: Simpler RL algorithms suffice (DPO, REINFORCE).

**Related:** 1.45 RLHF (context), 1.44 Scaling Laws (model sizing)

---

### 1.47 Chain of Thought (CoT) Reasoning
**Originator:** Wei et al. / Google | **Domain:** Reasoning | **Tier:** 1 | **Cynefin Fit:** Complicated

**Purpose:** Improve LLM reasoning by eliciting step-by-step intermediate reasoning before the final answer.

**SE Translation:** Prompt engineering for multi-step reasoning. "Let's think step by step" or providing few-shot examples with explicit reasoning chains. Dramatically improves accuracy on math, logic, and multi-step problems.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Reasoning problem | text | Yes | Question requiring multi-step logic |
| Example demonstrations | text array | No | Few-shot examples with steps |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Step-by-step derivation | text | Intermediate reasoning |
| Final answer | text/numeric | Solution |

**Math:**
- CoT effectiveness: `improvement = P_correct(with_CoT) - P_correct(without_CoT)`

**Execution Pipeline:**
1. Frame the problem
2. Prompt for step-by-step reasoning (or provide few-shot examples)
3. Verify each intermediate step
4. Check final answer consistency with intermediate steps
5. If inconsistent, re-derive

**Constraints:**
- HARD: CoT helps most on problems requiring multi-step reasoning — minimal benefit on simple lookups.
- SOFT: Verify intermediate steps, not just final answers.
- DO NOT USE WHEN: Problem is simple enough that direct answering is more efficient.

**Related:** 1.43 Transformer (underlying architecture), 1.45 RLHF (alignment context)

---

## Domain 6: Biological & Organizational

Frameworks: 1.48 Hebbian Learning | 1.49 Bayesian Inference | 1.50 Schein's Culture | 1.51 Core Competence | 1.52 Soil Food Web | 1.53 Koch's Postulates

[Back to Selection Guide](#framework-selection-guide) | [Back to Cynefin Router](#cynefin-router)

### 1.48 Hebbian Learning
**Originator:** Donald Hebb | **Domain:** Neural learning | **Tier:** 2 | **Cynefin Fit:** Clear

**Purpose:** Model synaptic strengthening: "neurons that fire together wire together."

**SE Translation:** Understanding associative learning and co-occurrence patterns. Applicable to recommendation systems, feature co-occurrence analysis, and understanding how repeated patterns strengthen associations in any learning system.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Presynaptic activity (x) | numeric [0,1] | Yes | Input activation |
| Postsynaptic activity (y) | numeric [0,1] | Yes | Output activation |
| Current weight (w) | numeric | Yes | Connection strength |
| Learning rate (eta) | numeric | Yes | Speed of adaptation |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Weight change | numeric | dw = eta * x * y |
| Updated weight | numeric | w' = w + dw |

**Math:**
- Basic Hebbian: `dw = eta * x * y`
- STDP: `dw = A+ * exp(-dt/tau+)` if pre before post, `A- * exp(dt/tau-)` if post before pre

**Execution Pipeline:**
1. Measure pre and post activity
2. Calculate weight change
3. Update weight
4. Check for stability (Hebbian alone is unstable — needs normalization)

**Constraints:**
- HARD: Pure Hebbian learning is unstable (weights grow unbounded) — must add normalization or decay.
- DO NOT USE WHEN: Learning requires error correction (use backpropagation).

**Related:** 1.43 Transformer (modern learning), 1.41 ACT-R (cognitive learning)

---

### 1.49 Bayesian Inference
**Originator:** Thomas Bayes | **Domain:** Statistical inference | **Tier:** 1 | **Cynefin Fit:** Complicated

**Purpose:** Update beliefs by combining prior probability with new evidence via likelihood.

**SE Translation:** Decision-making under uncertainty. Should we upgrade this library? Prior belief: 60% beneficial. Evidence: 5 critical CVEs found. Likelihood of CVEs given should-upgrade: 95%. Posterior: 95% should upgrade. Systematic belief updating for any uncertain decision.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Prior P(H) | numeric [0,1] | Yes | Initial belief |
| Likelihood P(E|H) | numeric [0,1] | Yes | Probability of evidence given hypothesis |
| Evidence | text/data | Yes | Observed information |
| P(E|not-H) | numeric [0,1] | No | Probability under alternative |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Posterior P(H|E) | numeric [0,1] | Updated belief |
| Bayes factor | numeric | Likelihood ratio |

**Math:**
- `P(H|E) = P(E|H) * P(H) / P(E)`
- `P(E) = P(E|H) * P(H) + P(E|~H) * P(~H)`
- Bayes factor: `BF = P(E|H1) / P(E|H0)`

**Execution Pipeline:**
1. State the hypothesis
2. Assign prior probability
3. Observe evidence
4. Estimate likelihood (how probable is this evidence if hypothesis is true?)
5. Calculate posterior
6. Update belief, repeat with new evidence

**Constraints:**
- HARD: Prior must be honest — don't set prior to 0 or 1 (prevents updating).
- SOFT: Use multiple independent pieces of evidence for stronger updates.
- DO NOT USE WHEN: Problem is deterministic (no uncertainty to update).

**Related:** 1.32 Prospect Theory (behavioral deviations from Bayesian ideal), 1.35 Bounded Rationality (when full Bayesian is too expensive)

---

### 1.50 Schein's Three Levels of Organizational Culture
**Originator:** Edgar Schein | **Domain:** Organizational culture | **Tier:** 3 | **Cynefin Fit:** Complex

**Purpose:** Diagnose organizational culture at 3 levels: artifacts (visible), espoused values (stated), and basic assumptions (implicit).

**SE Translation:** Engineering culture diagnosis. Level 1 (Artifacts): open office, sprint ceremonies, PR review process. Level 2 (Espoused values): "we value quality," "move fast." Level 3 (Basic assumptions): "shipping > correctness" or "correctness > shipping." Conflicts between levels explain dysfunctional behavior.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Observations | text array | Yes | Artifacts, behaviors, stories |
| Interview data | text array | Yes | What people say about values |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Level 1 Artifacts | text array | Visible structures and processes |
| Level 2 Espoused Values | text array | Explicit philosophy |
| Level 3 Basic Assumptions | text array | Implicit beliefs |
| Alignment/conflict map | text | Where levels are inconsistent |

**Execution Pipeline:**
1. Observe artifacts (what can you see?)
2. Interview for espoused values (what do people say they value?)
3. Infer basic assumptions (what must be true for observed behavior to make sense?)
4. Map alignment between levels
5. Identify conflicts (espoused "quality" but assumed "speed")
6. Design interventions at the assumption level

**Constraints:**
- HARD: Assumptions are invisible — must be inferred from behavior, not asked about directly.
- SOFT: Look for contradictions between espoused values and actual behavior.
- DO NOT USE WHEN: Organization is too new to have established culture.

**Related:** 1.20 VSM (structural complement), 1.34 Principal-Agent (incentive alignment)

---

### 1.51 Core Competence Identification
**Originator:** Prahalad & Hamel | **Domain:** Strategic capability | **Tier:** 2 | **Cynefin Fit:** Complicated

**Purpose:** Identify strategic capabilities that meet 3 criteria: valuable to customers, defensible, and extendable.

**SE Translation:** What should your team own? A capability is a core competence if: (1) customers care about it, (2) competitors can't easily replicate it, (3) it can be applied to future products/markets. Everything else should be bought or partnered.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Capabilities | text array | Yes | What org does well |
| Competitive landscape | text array | Yes | Competitor capabilities |
| Customer value drivers | text array | No | What matters to customers |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Core competencies | text array | Capabilities meeting 3-criterion test |
| Test results | table | {capability, valuable, defensible, extendable} |

**Execution Pipeline:**
1. List organizational capabilities
2. For each, test: valuable to customers?
3. Test: defensible (hard to imitate)?
4. Test: extendable to new markets?
5. Capabilities passing all 3 = core competencies
6. Invest in these; outsource the rest

**Constraints:**
- HARD: All 3 criteria must be met — valuable but easily copied is not a core competence.
- SOFT: Reassess regularly as markets and technology evolve.
- DO NOT USE WHEN: Organization is a startup still finding product-market fit.

**Related:** 1.33 TCE (build vs buy), 1.17 Porter's Five Forces (competitive context)

---

### 1.52 Soil Food Web Structure
**Originator:** Elaine Ingham / various ecologists | **Domain:** Ecology | **Tier:** 3 | **Cynefin Fit:** Complex

**Purpose:** Model ecosystem health through trophic interactions: who eats what, nutrient cycling, biodiversity.

**SE Translation:** Codebase ecosystem health. Decomposers (linters, formatters, dead code detectors) break down waste. Producers (feature code) create value. Predators (tests) keep producers honest. A healthy codebase has active "decomposition" — continuous cleanup, not just creation.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Ecosystem data | measurements | Yes | Community composition |
| Trophic interactions | edge array | Yes | {predator, prey, feeding_rate} |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Trophic map | diagram | Hierarchical food web |
| Health rating | numeric [0-10] | Ecosystem health |
| Resilience analysis | text | Robustness to disturbance |

**Math:**
- Trophic level: `TL_i = 1 + sum(fraction_from_j * TL_j)`
- Food web stability proportional to `(connectance * mean_interaction_strength)^(-1)`

**Execution Pipeline:**
1. Inventory organisms/tools (producers, decomposers, predators)
2. Map trophic interactions (who depends on what)
3. Assess nutrient cycling (value flow)
4. Rate overall health
5. Identify missing trophic levels (e.g., no decomposers = waste accumulates)

**Constraints:**
- HARD: Missing trophic levels (no decomposers, no predators) = unhealthy ecosystem.
- SOFT: Diversity within each level increases resilience.
- DO NOT USE WHEN: System is too small/simple for ecosystem metaphor.

**Related:** 1.40 Antifragility (resilience), 1.24 System Dynamics (modeling)

---

### 1.53 Koch's Postulates
**Originator:** Robert Koch | **Domain:** Microbiology / Causation | **Tier:** 1 | **Cynefin Fit:** Complicated

**Purpose:** Establish causation (not just correlation) through a rigorous 4-step protocol.

**SE Translation:** Rigorous debugging protocol. (1) Associate: bug is present when X is present. (2) Isolate: extract X from the system and confirm it's the suspected cause. (3) Reproduce: reintroduce X into a clean system and observe the bug. (4) Recover: confirm X is present in the newly-bugged system. If all 4 pass, X causes the bug.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| Suspected cause | text | Yes | What you think causes the problem |
| Symptoms | text | Yes | Observable effects |
| Healthy controls | text | Yes | Unaffected system for comparison |

**Outputs:**
| Output | Type | Description |
|--------|------|-------------|
| Causal confirmation | enum | {confirmed, probable, inconclusive, disproven} |
| 4-step results | table | Pass/fail per step |

**Execution Pipeline:**
1. **Associate**: Is the suspected cause present in all affected systems?
2. **Isolate**: Can you extract the cause and grow it in isolation?
3. **Reproduce**: When you introduce the cause to a healthy system, does the problem appear?
4. **Recover**: Can you re-isolate the same cause from the newly-affected system?
5. 4/4 = confirmed, 3/4 = probable, <3/4 = inconclusive or disproven

**Constraints:**
- HARD: Must test all 4 steps — skipping one leaves correlation, not causation.
- SOFT: Use clean/controlled environments for steps 3-4.
- DO NOT USE WHEN: Cause is multi-factorial (multiple interacting causes — use STPA instead).

**Related:** 1.6 STPA (for multi-causal problems), 1.49 Bayesian Inference (for probabilistic causation)

---

## Cross-Reference Index

### By Operational Category

**Calculators** (formula in -> number out):
1.2, 1.3, 1.15, 1.16, 1.22, 1.26, 1.31, 1.32, 1.37, 1.43, 1.44, 1.46, 1.48, 1.49

**Classifiers** (situation in -> category out):
1.7, 1.10, 1.17, 1.23, 1.25, 1.27, 1.30, 1.33, 1.35, 1.36, 1.40, 1.51, 1.53

**Decomposers** (system in -> structured breakdown out):
1.1, 1.6, 1.8, 1.9, 1.11, 1.14, 1.18, 1.20, 1.21, 1.24, 1.28, 1.29, 1.34, 1.41, 1.42, 1.50, 1.52

**Generators** (problem in -> solutions out):
1.4, 1.5, 1.12, 1.13, 1.19, 1.38, 1.39, 1.45, 1.47

### By Tier

**Tier 1 (Direct Apply):** 1.2, 1.7, 1.10, 1.13, 1.15, 1.16, 1.19, 1.22, 1.23, 1.29, 1.35, 1.47, 1.49, 1.53

**Tier 2 (Guided Apply):** 1.1, 1.3, 1.4, 1.5, 1.6, 1.8, 1.9, 1.12, 1.14, 1.17, 1.18, 1.21, 1.25, 1.26, 1.32, 1.33, 1.34, 1.36, 1.37, 1.38, 1.39, 1.44, 1.48, 1.51

**Tier 3 (Expert Apply):** 1.11, 1.20, 1.24, 1.27, 1.28, 1.30, 1.31, 1.40, 1.41, 1.42, 1.43, 1.45, 1.46, 1.50, 1.52

### Framework Clusters (tightly coupled sets)

1. **TRIZ cluster:** 1.4 Matrix + 1.5 Principles
2. **STPA cluster:** 1.6 STPA + 1.7 UCA + 1.26 Control Theory
3. **Taguchi cluster:** 1.2 QLF + 1.3 S/N
4. **DFMA cluster:** 1.9 DFMA + 1.10 TMPC
5. **Blue Ocean cluster:** 1.12 Blue Ocean + 1.13 ERRC
6. **TOC cluster:** 1.21 TOC + 1.15 Little's Law + 1.22 Throughput Accounting
7. **SSM cluster:** 1.28 SSM + 1.29 CATWOE
8. **AI pipeline cluster:** 1.43 Transformer + 1.44 Scaling Laws + 1.45 RLHF + 1.46 PPO
9. **Decision cluster:** 1.49 Bayesian + 1.32 Prospect Theory + 1.35 Bounded Rationality
10. **Process cluster:** 1.14 Lean + 1.16 Six Sigma
