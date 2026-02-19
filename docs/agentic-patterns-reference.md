# Agentic Patterns Reference

Extracted from WS-000-02's competence roadmap, synthesis analyses, and adversarial validation.

## 9 Anti-Patterns (Evidence-Backed)

### 1. Framework Import for Native Capabilities
Importing LangChain to get ReAct agents when Claude Code IS a ReAct agent. 91% of framework capabilities are redundant with native LLM capabilities for interactive CLI use.

### 2. Batch Eval Patterns in Interactive Contexts
Transplanting deterministic test harnesses (promptfoo-style) into non-deterministic LLM interactions. Category error: the output varies by design.

### 3. False Precision Scoring
Wrapping subjective judgments in formulas (Risk = P × I where both are guesses). The number looks precise but obscures uncertainty. Use categorical decisions (ship/review/rework) instead.

### 4. All-Coder Agent Teams
Multi-agent teams where every agent writes code. Produces merge conflicts, duplicated work, and no quality oversight. Include at least one non-coding reviewer agent.

### 5. Failed Context Inheritance
Resuming a failed agent from its corrupted context. Always spawn fresh sessions after agent failure — the failed context contains wrong assumptions that propagate.

### 6. Human Approval Theater
Requiring human approval for implementation-level decisions (variable names, import order, formatting). Reserve human judgment for architectural choices. Automate everything else via hooks/gates.

### 7. Skills Without Activation
Building skills past the working memory threshold (15+) without trigger systems. Dead skills consume tokens and create false capability signals. Build activation infrastructure before building more skills.

### 8. Premature Scheduling
Scheduling work when a gap is discovered rather than setting a measurable trigger. 7/10 deferral triggers in WS-000-02 never fired — 70% of prematurely scheduled work would have been wasted.

### 9. Unicorn Dependency Trust
Trusting framework claims about integrated capabilities. 4/5 "unicorn" frameworks had false or misleading dependency claims. Test each claimed capability independently.

## 9 AI Engineering Principles

### 1. Native-First Evaluation
Before building anything, score: VI = (Utility_skill - Utility_native) / Cost_skill. If VI < 0.25, the native capability is sufficient. Don't build.

### 2. Composition Over Capability
Compose simple primitives (hooks → files → skills) rather than importing complex frameworks. File-mediated composition is simpler and more transparent than framework abstractions.

### 3. Tests as AI Prerequisite
Without tests, AI amplifies risk, not productivity. Tests are the safety net that makes AI agent delegation viable.

### 4. Progressive Trust Delegation
Three strategies: demonstrate reliability (low-risk tasks first), defer via sandbox (contained experimentation), remove need via hooks (automated invariant enforcement). Constraints before autonomy.

### 5. Checkpoint-Based Idempotency
Multi-stage operations write JSONL checkpoints. Each stage checks before repeating. Enables session-crossing work without re-execution.

### 6. Parallel Adversarial Review
3-6 evaluators with narrow mandates, mandatory scoring, convergence-based stopping. First round catches 60%, second 25%, third 10%.

### 7. Satisficing Over Optimizing
Good enough beats optimal under time, cognitive, and token constraints. 15-line plan that starts execution beats 200-line plan that delays it.

### 8. Risk-Based Supervision
Watch closely on low-risk codebases (to learn agent patterns). Step back on high-risk codebases (to let the agent explore). Counterintuitive but calibration-optimal.

### 9. Context Engineering Over Model Selection
How you architect context (instructions, file surfacing, tool availability, memory) matters more than which model you use. Decouple intelligence from provider.

## Golden Path for New Primitives

```
1. Cynefin-classify the problem
   → Wrong domain = wrong framework

2. Run G4 Native-First check
   → VI = (Utility_skill - Utility_native) / Cost_skill
   → If VI < 0.25: don't build, native suffices

3. Check architectural compatibility
   → Hooks are advisory, not interceptive
   → File-mediated composition is the correct pattern
   → No external dependencies unless justified vs stdlib

4. Set a deferral trigger
   → "Build when condition X is met" not "build now"
   → 70% of triggers never fire (saved work)

5. Apply adversarial counter-argument
   → "Can the LLM do this when asked?"
   → If yes: the primitive adds consistency, not capability
   → Build only if the consistency value justifies token cost

6. Budget check
   → SKILL.md max 4K tokens
   → Full skill load max 15K (200K context) or 20K (1M beta)
   → 2% of context window per skill
```

## Key Numbers

- **9%**: Framework-to-CLI extraction rate (102 capabilities → 9 survivors)
- **63%**: Framework capability redundancy with Claude Code native tools
- **91%**: Capability coverage by native LLM + simple composition
- **70%**: Deferral triggers that never fired (work saved)
- **2%**: Context budget per skill
- **0.25**: VI threshold for native-first check
- **95%**: Overhead reduction from sampled monitoring (every Nth call)
