---
name: adversarial-review
description: Structured adversarial analysis with scoping questions to keep critique grounded and relevant
argument-hint: "<subject — file, decision, design, PR, architecture, etc.>"
---

<objective>
Provide adversarial analysis of a subject while keeping critique grounded, evidence-based, and proportionate. Before any critique begins, conduct a structured scoping interview to constrain the adversarial lens to what actually matters for the given subject.

The core principle: **never critique in a vacuum.** Every adversarial pass must be anchored to a specific scope, dimension, severity threshold, and success definition — all confirmed by the user before analysis begins.

Note: The scoping behavior defined here also applies **automatically** whenever adversarial input is requested in conversation, as specified in `CLAUDE.md` at the project root. This command provides the full structured process; `CLAUDE.md` enforces the minimum scoping protocol at all times.

Input: any subject the user wants adversarial input on — code, architecture, decisions, documents, designs, processes.
Argument: $ARGUMENTS
</objective>

<process>

## Phase 0: Identify the Subject

<step name="identify_subject">
Determine what is being reviewed from `$ARGUMENTS` and conversation context.

Classify the subject type:

| Type | Examples |
|------|----------|
| `code` | A function, module, file, or PR |
| `architecture` | System design, data flow, component boundaries |
| `decision` | Technology choice, trade-off, approach selection |
| `document` | Spec, RFC, README, design doc |
| `process` | Workflow, pipeline, team practice |
| `design` | UI/UX, API surface, data model |
| `other` | Anything not covered above — ask user to describe |

If the subject is a file or code path, **read it now** before proceeding to questions. You need to understand the artifact to ask relevant scoping questions.

If the subject is ambiguous, ask: "What specifically should I review? Point me at a file, a decision, a design — something concrete."

Do NOT proceed until you have a concrete subject.
</step>

## Phase 1: Scoping Interview

<step name="scoping_questions">
Ask the user the following questions. Present them **all at once** as a numbered list so the user can answer in a single response. Adapt the specific wording to match the subject type identified in Phase 0.

### Required Questions (always ask)

**1. Dimension** — What axis of critique matters most?

Offer relevant options based on subject type:

- `code`: correctness, security, performance, maintainability, readability, error handling, edge cases
- `architecture`: scalability, coupling, complexity, failure modes, extensibility, operational cost
- `decision`: trade-offs missed, assumptions untested, alternatives overlooked, reversibility
- `document`: accuracy, completeness, clarity, actionability, audience fit
- `process`: bottlenecks, failure modes, bus factor, feedback loops
- `design`: consistency, usability, edge cases, accessibility, migration path

Phrase as: "Which dimensions should I focus on? Pick 1-3, or tell me what you care about most."

**2. Severity threshold** — What level of issues are worth flagging?

- `critical-only`: Things that will break, lose data, or create security holes
- `high+`: Above plus significant correctness or performance concerns
- `medium+`: Above plus maintainability and design issues
- `all`: Include style, convention, and nitpicks

Phrase as: "What severity level should I flag from? (critical-only / high+ / medium+ / all)"

**3. Known constraints** — What boundaries exist that I should respect?

Phrase as: "Are there constraints I should know about? (deadlines, backwards compatibility, team conventions, intentional trade-offs, things that look wrong but are deliberate)"

**4. What does 'good enough' look like?**

Phrase as: "What would a successful outcome of this review look like for you? (e.g., 'catch anything that could break in production', 'validate this is the right approach', 'find the holes in my thinking')"

### Conditional Questions (ask when relevant)

**If subject is `code` or `architecture`:**
- "Is this greenfield or does it need to interoperate with existing systems? If existing, what are the integration points?"

**If subject is `decision`:**
- "What alternatives did you consider and reject? (so I don't waste time re-proposing them)"

**If subject is `document`:**
- "Who is the intended audience? What should they be able to do after reading this?"

**If subject is `process`:**
- "What triggered this review? Is something currently broken, or is this proactive?"

Wait for the user's answers. Do NOT begin analysis until you have responses.
</step>

## Phase 2: Confirm Scope

<step name="confirm_scope">
Restate the review scope back to the user in a compact summary:

```
Review scope:
- Subject: {what}
- Dimensions: {which axes}
- Severity: {threshold}
- Constraints: {what to respect}
- Success: {what good looks like}
```

Ask: "Does this scope look right, or should I adjust anything?"

Only proceed when confirmed. This prevents scope drift during analysis.
</step>

## Phase 3: Adversarial Analysis

<step name="conduct_analysis">
Now perform the analysis. Adhere strictly to the confirmed scope.

### Rules for analysis

1. **Evidence required.** Every finding must reference a specific line, section, decision point, or concrete scenario. No "this could theoretically be a problem" without a plausible trigger.

2. **Stay in scope.** If you notice something outside the agreed dimensions, note it in a separate "Out of scope observations" section at the end — do not promote it to a finding.

3. **Respect constraints.** If the user said something is intentional, don't flag it. If there's a deadline, don't suggest a rewrite.

4. **Rank findings.** Order by severity within the agreed threshold. Most important first.

5. **No padding.** If there are only 2 real findings, report 2. Do not invent findings to appear thorough. Explicitly state: "Analysis found N issues within scope. No additional issues at {threshold} severity or above."

6. **Provide the counter-argument.** For each finding, include a brief "Why this might be fine" note. This prevents one-sided critique and helps the user calibrate.

7. **Distinguish fact from opinion.** Mark objective issues (bug, spec violation, security flaw) differently from subjective concerns (style preference, design philosophy).

### Output format

```markdown
## Adversarial Review: {subject}

**Scope:** {dimensions} | **Severity:** {threshold}

### Findings

#### 1. [{CRITICAL|HIGH|MEDIUM|LOW}] {Title}

**What:** {Description with specific reference — file:line, section, decision}
**Why it matters:** {Concrete impact, not hypothetical}
**Why it might be fine:** {Counter-argument or mitigating factor}
**Suggested action:** {Specific, actionable fix — or "Discuss" if judgment call}

#### 2. ...

### Out of Scope Observations
{Things noticed but outside agreed scope — user can choose to explore these separately}

### What Holds Up Well
{Specific things within the reviewed scope that are solid — with evidence. This is not filler praise; it identifies load-bearing strengths the user should preserve.}

### Verdict
{1-2 sentence overall assessment calibrated to the user's stated success criteria}
```
</step>

## Phase 4: Follow-up

<step name="follow_up">
After presenting findings, ask:

"Want me to:
1. Dig deeper on any specific finding?
2. Expand scope to a different dimension?
3. Help implement any of the suggested actions?
4. Run this same review on a related subject?"

This prevents the common pattern of dumping critique and walking away. Adversarial input is only useful if it leads to action.
</step>

</process>

<rules>
## Hard Rules — Never Violate

1. **Never skip the scoping interview.** The whole point is to constrain before critiquing. Going straight to analysis defeats the purpose.
2. **Never fabricate evidence.** If you can't point to a specific reference for a finding, it's not a finding — it's speculation. Drop it.
3. **Never exceed the severity threshold.** If the user asked for critical-only, do not include medium-severity style concerns.
4. **Never ignore stated constraints.** If the user says "we know X is tech debt, don't flag it," respect that completely.
5. **Always include the counter-argument.** One-sided critique is not adversarial analysis — it's a hit list.
6. **Always include "What holds up well."** Identifying strengths is part of a complete assessment. Omitting it biases the review toward negativity.
7. **Never pad findings.** Report what you find. If the answer is "this looks solid within the agreed scope," say that.
8. **Read before reviewing.** Never critique code, documents, or designs you haven't actually read in full.
9. **Rank honestly.** Don't inflate severity to appear more useful. A style issue is LOW even if you have a strong opinion about it.
10. **Stay concrete.** "This could be a problem" is not a finding. "This will fail when X happens because Y" is a finding.
</rules>

<context_budget>
- Phase 0-2 (Scoping): Minimal context use. Short questions, short answers.
- Phase 3 (Analysis): This is where context is spent. Read the subject thoroughly, but only analyze within the agreed scope/dimensions.
- Phase 4 (Follow-up): Minimal. One question, wait for direction.

If the subject is large (>500 lines, multiple files, complex system), ask during scoping: "This is a large subject. Want me to focus on a specific section, or should I sample strategically and flag areas that warrant deeper review?"
</context_budget>
