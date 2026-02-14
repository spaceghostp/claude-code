# CLAUDE.md

## Adversarial Input Protocol

When the user asks for adversarial input, critique, review, pushback, a devil's advocate perspective, or any variant of "tell me what's wrong with this" — **always run the scoping interview before providing analysis.**

This applies regardless of whether the user invokes `/adversarial-review` explicitly. If the intent is adversarial analysis, the protocol activates automatically.

### Trigger phrases (non-exhaustive)

- "review this critically"
- "what's wrong with..."
- "poke holes in..."
- "devil's advocate"
- "adversarial review/input/feedback"
- "challenge this"
- "what am I missing"
- "stress test this"
- "tear this apart"
- Any request for critique, pushback, or red-teaming

### Required behavior

1. **Identify the subject** — classify what's being reviewed (code, architecture, decision, document, process, design). Read any referenced artifacts before asking questions.

2. **Ask scoping questions in one batch** — do not start analysis until the user answers:
   - **Dimensions:** Which axes of critique matter? (e.g., correctness, security, performance, trade-offs, clarity — varies by subject type)
   - **Severity threshold:** What level of issues to flag? (`critical-only` / `high+` / `medium+` / `all`)
   - **Constraints:** Anything intentional, off-limits, or already known?
   - **Success criteria:** What does a useful review look like?

3. **Confirm scope** — restate the agreed scope compactly and get confirmation before proceeding.

4. **Analyze within scope only** — every finding needs evidence (file:line, specific reference, concrete scenario). Include a counter-argument for each finding. Do not pad with low-value observations. Out-of-scope observations go in a separate section.

5. **Identify strengths** — note what holds up well within scope. This is not filler; it identifies load-bearing decisions to preserve.

6. **Offer follow-up** — after presenting findings, ask what to do next (dig deeper, expand scope, implement fixes, review related subject).

### What this prevents

- Unscoped critique that drifts into speculation
- Padding findings to appear thorough
- Flagging things the user already knows about
- Severity inflation
- One-sided analysis without counter-arguments
- Critique without actionable next steps

The full structured process is available as `/adversarial-review` for explicit invocation. The behavior above is the minimum that applies automatically.
