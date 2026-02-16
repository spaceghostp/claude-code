# /vault-capture — Create a new vault note

Read `vault/_meta/conventions.md` for the full ontology and rules before proceeding.

## Steps

1. **Ask the user** what to capture. Use AskUserQuestion:
   - Header: "Vault capture"
   - Ask what type of note to create (atom, tension, encounter, position, question, anti-library, falsification)
   - Ask for a 1-line description of the insight or topic

2. **Check the hard ceiling.** Read `vault/_meta/index.json` and count notes with `lifecycle: proposed`. If 10+, tell the user captures are paused and suggest `/vault-maintain` instead. Stop here.

3. **Determine the filename** using conventions:
   - Encounters and revisions: `YYYY-MM-DD-topic-slug.md` (date-prefixed)
   - Everything else: `topic-slug.md` (kebab-case)

4. **Write the note** to the correct type directory (`vault/atoms/`, `vault/tensions/`, `vault/encounters/`, `vault/positions/`, `vault/questions/`, `vault/anti-library/`, `vault/falsifications/`, `vault/revisions/`).

   Frontmatter:
   ```yaml
   ---
   type: [chosen type]
   status: unverified
   lifecycle: proposed
   created: YYYY-MM-DD
   last_touched: YYYY-MM-DD
   links_out: [count of wikilinks in body]
   origin: session
   ---
   ```

5. **Link to existing vault notes.** Every note must link to at least one other note via `[[wikilinks]]` using directory-relative paths from vault root (e.g., `[[positions/what-good-code-actually-is]]`). If no obvious link exists, link to the most relevant position or question. Broken links to notes that should exist are acceptable.

6. **Write the body.** Structure depends on type:
   - **Atom:** Single concept, densely linked. Keep it tight.
   - **Tension:** Name both sides. Don't resolve — articulate why both pull.
   - **Encounter:** What happened, what was learned, what changed, open questions.
   - **Position:** Falsifiable claims, evidence needed to revise, links to related tensions.
   - **Question:** Core question, sub-questions, current hypotheses.
   - **Anti-library:** The assumption, why it's unverified, what would test it.
   - **Falsification:** Old belief, new belief, what caused the change, error type.

7. **Update the index.** Run via Bash: `python3 scripts/build-index.py`

8. **Confirm** to the user: note path, type, and link count.
