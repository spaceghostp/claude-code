#!/usr/bin/env python3
"""
WS-000-02 REFERENCE IMPLEMENTATION — Not directly compatible with the cognitive vault
at ~/.claude/vault/. This script expects notes/, sources/, mocs/, graph.json structure.
The cognitive vault uses atoms/, encounters/, positions/, etc. with its own tooling at
~/.claude/vault/_scripts/. Adapt the check functions if porting to cognitive vault.

Deterministic vault health scanner with 5 checks + 7 quality sub-checks.

Usage:
    python3 scripts/maintain_vault.py <vault_path>              # report only
    python3 scripts/maintain_vault.py <vault_path> --archive    # move flagged to archive
    python3 scripts/maintain_vault.py <vault_path> --llm-review # haiku pass on borderline

Checks:
    1. STALENESS: Notes with 0 edges in graph.json
    2. NEAR-DUPLICATES: Note pairs with weighted Jaccard > 0.70
    3. LOW-QUALITY: Notes failing 3+ of 7 quality sub-checks
    4. ORPHAN SOURCES: Source notes with 0 extracted notes remaining
    5. MOC DRIFT: Notes not assigned to any MOC

Outputs:
    vault/maintenance-report.md     (human-readable, priority-sorted)
    vault/maintenance-report.jsonl  (machine-readable)
"""

import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

def parse_frontmatter(content: str) -> tuple[dict, str]:
    if not content.startswith('---'):
        return {}, content
    end_match = re.search(r'\n---\n', content[3:])
    if not end_match:
        return {}, content
    fm_str = content[4:end_match.start() + 3]
    body = content[end_match.end() + 4:]
    fm = {}
    for line in fm_str.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith('[') and value.endswith(']'):
                value = [v.strip().strip('"\'') for v in value[1:-1].split(',') if v.strip()]
            fm[key] = value
    return fm, body


# ---------------------------------------------------------------------------
# Load vault data
# ---------------------------------------------------------------------------

def load_notes(vault_path: str) -> dict[str, dict]:
    """Load all notes from vault/notes/."""
    notes_dir = Path(vault_path) / 'notes'
    notes = {}
    if not notes_dir.exists():
        return notes

    for md_file in sorted(notes_dir.glob('**/*.md')):
        try:
            content = md_file.read_text(encoding='utf-8')
            fm, body = parse_frontmatter(content)
            note_id = fm.get('id', md_file.stem)
            tags = fm.get('tags', [])
            if isinstance(tags, str):
                tags = [tags]

            notes[note_id] = {
                'id': note_id,
                'title': fm.get('title', md_file.stem),
                'type': fm.get('type', ''),
                'summary': fm.get('summary', ''),
                'source': fm.get('source', ''),
                'tags': tags,
                'path': md_file,
                'body': body,
            }
        except Exception as e:
            print(f"  Error loading {md_file.name}: {e}", file=sys.stderr)
    return notes


def load_sources(vault_path: str) -> dict[str, dict]:
    """Load all source notes."""
    sources_dir = Path(vault_path) / 'sources'
    sources = {}
    if not sources_dir.exists():
        return sources

    for md_file in sorted(sources_dir.glob('*.md')):
        if md_file.name.startswith('MOC-'):
            continue
        try:
            content = md_file.read_text(encoding='utf-8')
            fm, body = parse_frontmatter(content)
            if fm.get('type') != 'source':
                continue
            src_id = fm.get('id', md_file.stem)
            sources[src_id] = {
                'id': src_id,
                'title': fm.get('title', md_file.stem),
                'path': md_file,
                'body': body,
            }
        except Exception:
            continue
    return sources


def load_graph_edges(vault_path: str) -> dict[str, set]:
    """Load graph.json and build edge index."""
    graph_path = Path(vault_path) / 'graph.json'
    index = defaultdict(set)
    if not graph_path.exists():
        return dict(index)

    try:
        with open(graph_path, 'r', encoding='utf-8') as f:
            graph = json.load(f)
        for edge in graph.get('edges', []):
            index[edge['from']].add(edge['to'])
            index[edge['to']].add(edge['from'])
    except (json.JSONDecodeError, IOError):
        pass
    return dict(index)


def load_moc_coverage(vault_path: str) -> set[str]:
    """Get set of note IDs covered by any MOC."""
    mocs_dir = Path(vault_path) / 'mocs'
    covered = set()
    if not mocs_dir.exists():
        return covered

    for moc_file in mocs_dir.glob('MOC-*.md'):
        content = moc_file.read_text(encoding='utf-8')
        links = re.findall(r'\[\[([^|\]]+)', content)
        covered.update(links)
    return covered


# ---------------------------------------------------------------------------
# Quality checks per note
# ---------------------------------------------------------------------------

# Placeholder patterns commonly left by extraction pipelines
PLACEHOLDER_PATTERNS = [
    r'core insight extracted',
    r'key takeaway extracted',
    r'no unique insights found',
    r'placeholder content',
    r'todo:? extract',
    r'^\s*#\s+[\w\s-]+\s*$',  # Title-only body (just a markdown heading)
]
PLACEHOLDER_RE = re.compile(
    '|'.join(PLACEHOLDER_PATTERNS), re.IGNORECASE
)


def quality_checks(note: dict) -> list[str]:
    """Run 7 quality checks on a note. Returns list of failed check IDs."""
    failures = []
    body = note.get('body', '')
    title = note.get('title', '')
    summary = note.get('summary', '')
    tags = note.get('tags', [])
    source = note.get('source', '')

    # Q1: Body content > 100 chars (excluding Related/Source/Diagram sections)
    body_text = re.sub(r'## (Source|Related|Diagram)\n.*', '', body, flags=re.DOTALL).strip()
    if len(body_text) < 100:
        failures.append('Q1_short_body')

    # Q2: Summary is not just the title
    if not summary or summary.lower().strip() == title.lower().strip():
        failures.append('Q2_placeholder_summary')

    # Q3: Has >= 1 Related link
    related_m = re.search(r'## Related\n\n(.*?)(?=\n## |\Z)', body, re.DOTALL)
    if not related_m or '[[' not in related_m.group(1):
        failures.append('Q3_no_related_links')

    # Q4: Has >= 3 tags beyond type tag
    note_type = note.get('type', '')
    non_type_tags = [t for t in tags if t != note_type and t not in ('youtube', 'extracted', 'doc')]
    if len(non_type_tags) < 3:
        failures.append('Q4_few_tags')

    # Q5: Has non-empty source reference
    if not source:
        failures.append('Q5_no_source')

    # Q6: Thin note — body has fewer than 50 words (excluding sections)
    body_words = body_text.split()
    if len(body_words) < 50:
        failures.append('Q6_thin_note')

    # Q7: Placeholder body — matches known extraction template patterns
    if body_text and PLACEHOLDER_RE.search(body_text):
        failures.append('Q7_placeholder_body')

    return failures


# ---------------------------------------------------------------------------
# Check 1: Staleness (disconnected notes)
# ---------------------------------------------------------------------------

def check_staleness(notes: dict, edge_index: dict) -> list[dict]:
    """Find notes with 0 edges in graph."""
    results = []
    for note_id, note in notes.items():
        if note_id not in edge_index:
            results.append({
                'note_id': note_id,
                'title': note['title'],
                'type': note.get('type', ''),
                'check': 'staleness',
            })
    return results


# ---------------------------------------------------------------------------
# Check 2: Near-duplicates
# ---------------------------------------------------------------------------

def check_near_duplicates(notes: dict, threshold: float = 0.70) -> list[dict]:
    """Find note pairs with Jaccard > threshold."""
    results = []
    note_ids = sorted(notes.keys())

    # Build keyword sets from tags
    keyword_sets = {}
    for nid, note in notes.items():
        tags = set(t.lower() for t in note.get('tags', []))
        # Also extract words from title
        title_words = set(re.findall(r'[a-z]+', note.get('title', '').lower()))
        keyword_sets[nid] = tags | title_words

    for i in range(len(note_ids)):
        for j in range(i + 1, len(note_ids)):
            a, b = note_ids[i], note_ids[j]
            set_a = keyword_sets.get(a, set())
            set_b = keyword_sets.get(b, set())

            if not set_a or not set_b:
                continue

            intersection = len(set_a & set_b)
            union = len(set_a | set_b)

            if union > 0:
                jaccard = intersection / union
                if jaccard > threshold:
                    # Also check same type
                    if notes[a].get('type') == notes[b].get('type'):
                        results.append({
                            'note_a': a,
                            'note_b': b,
                            'title_a': notes[a]['title'],
                            'title_b': notes[b]['title'],
                            'jaccard': round(jaccard, 3),
                            'check': 'near_duplicate',
                        })
    return results


# ---------------------------------------------------------------------------
# Check 3: Low-quality notes
# ---------------------------------------------------------------------------

def check_low_quality(notes: dict) -> list[dict]:
    """Find notes failing 3+ quality checks."""
    results = []
    for note_id, note in notes.items():
        failures = quality_checks(note)
        if len(failures) >= 3:
            results.append({
                'note_id': note_id,
                'title': note['title'],
                'failures': failures,
                'failure_count': len(failures),
                'check': 'low_quality',
            })
    return results


# ---------------------------------------------------------------------------
# Check 4: Orphan sources
# ---------------------------------------------------------------------------

def check_orphan_sources(sources: dict, notes: dict) -> list[dict]:
    """Find sources with 0 notes referencing them."""
    results = []
    source_note_counts = Counter()
    for note in notes.values():
        src = note.get('source', '')
        if src:
            source_note_counts[src] += 1

    for src_id, source in sources.items():
        if source_note_counts.get(src_id, 0) == 0:
            results.append({
                'source_id': src_id,
                'title': source['title'],
                'check': 'orphan_source',
            })
    return results


# ---------------------------------------------------------------------------
# Check 5: MOC drift
# ---------------------------------------------------------------------------

def check_moc_drift(notes: dict, moc_coverage: set) -> list[dict]:
    """Find notes not assigned to any MOC."""
    results = []
    for note_id, note in notes.items():
        if note_id not in moc_coverage:
            results.append({
                'note_id': note_id,
                'title': note['title'],
                'type': note.get('type', ''),
                'check': 'moc_drift',
            })
    return results


# ---------------------------------------------------------------------------
# Priority scoring
# ---------------------------------------------------------------------------

def assign_priority(finding: dict, edge_index: dict, low_quality_ids: set) -> str:
    """Assign HIGH/MEDIUM/LOW priority."""
    check = finding.get('check', '')

    if check == 'staleness':
        note_id = finding['note_id']
        if note_id in low_quality_ids:
            return 'HIGH'  # Disconnected + low-quality
        return 'LOW'  # Disconnected but quality-passing

    if check == 'near_duplicate':
        return 'MEDIUM'

    if check == 'low_quality':
        note_id = finding['note_id']
        if note_id in edge_index:
            return 'MEDIUM'  # Low quality but connected
        return 'HIGH'  # Low quality + disconnected

    if check == 'orphan_source':
        return 'LOW'

    if check == 'moc_drift':
        return 'LOW'

    return 'LOW'


# ---------------------------------------------------------------------------
# Archive action
# ---------------------------------------------------------------------------

def archive_note(note: dict, vault_path: str):
    """Move a note to vault/archive/."""
    archive_dir = Path(vault_path) / 'archive'
    archive_dir.mkdir(exist_ok=True)

    src_path = note['path']
    dst_path = archive_dir / src_path.name
    shutil.move(str(src_path), str(dst_path))
    return dst_path


# ---------------------------------------------------------------------------
# Optional LLM review
# ---------------------------------------------------------------------------

def llm_review_note(note: dict, similar_titles: list[str]) -> str:
    """Use claude -p --model haiku to judge uniqueness. Returns YES/NO/PARTIAL."""
    title = note.get('title', '')
    summary = note.get('summary', '')
    similar = ', '.join(similar_titles[:3])

    prompt = (
        f"Is this note's knowledge unique in the vault or redundant? "
        f"Answer YES (unique), NO (redundant), or PARTIAL.\n"
        f"Note: {title} — {summary}\n"
        f"Similar notes: {similar}"
    )

    try:
        env = {k: v for k, v in os.environ.items() if k != 'CLAUDECODE'}
        result = subprocess.run(
            ['claude', '-p', '--model', 'haiku'],
            input=prompt, capture_output=True, text=True, timeout=30, env=env,
        )
        answer = result.stdout.strip().upper()
        if 'YES' in answer:
            return 'YES'
        elif 'NO' in answer:
            return 'NO'
        return 'PARTIAL'
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return 'UNKNOWN'


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def write_jsonl_report(findings: list[dict], output_path: Path):
    with open(output_path, 'w', encoding='utf-8') as f:
        for finding in findings:
            # Convert Path objects to strings for JSON serialization
            serializable = {}
            for k, v in finding.items():
                if isinstance(v, Path):
                    serializable[k] = str(v)
                else:
                    serializable[k] = v
            f.write(json.dumps(serializable, ensure_ascii=False) + '\n')


def write_markdown_report(findings: list[dict], stats: dict, output_path: Path):
    lines = []
    lines.append('# Vault Maintenance Report')
    lines.append('')
    lines.append(f'**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    lines.append(f'**Total notes:** {stats["total_notes"]}')
    lines.append(f'**Total sources:** {stats["total_sources"]}')
    lines.append('')

    # Summary counts
    check_counts = Counter(f['check'] for f in findings)
    priority_counts = Counter(f.get('priority', 'LOW') for f in findings)

    lines.append('## Summary')
    lines.append('')
    lines.append(f'| Priority | Count |')
    lines.append(f'|----------|-------|')
    for p in ('HIGH', 'MEDIUM', 'LOW'):
        lines.append(f'| {p} | {priority_counts.get(p, 0)} |')
    lines.append('')

    lines.append(f'| Check | Count |')
    lines.append(f'|-------|-------|')
    for check, count in check_counts.most_common():
        lines.append(f'| {check} | {count} |')
    lines.append('')

    # HIGH priority findings
    high = [f for f in findings if f.get('priority') == 'HIGH']
    if high:
        lines.append('## HIGH Priority')
        lines.append('')
        for f in high:
            if f['check'] == 'staleness':
                lines.append(f'- **Disconnected + Low-Quality:** `{f["note_id"]}` — {f["title"]}')
            elif f['check'] == 'low_quality':
                failures = ', '.join(f.get('failures', []))
                lines.append(f'- **Low-Quality + Disconnected:** `{f["note_id"]}` — {f["title"]} (failed: {failures})')
        lines.append('')

    # MEDIUM priority findings
    medium = [f for f in findings if f.get('priority') == 'MEDIUM']
    if medium:
        lines.append('## MEDIUM Priority')
        lines.append('')
        for f in medium:
            if f['check'] == 'near_duplicate':
                lines.append(
                    f'- **Near-Duplicate** (Jaccard {f["jaccard"]:.2f}): '
                    f'`{f["note_a"]}` vs `{f["note_b"]}`'
                )
            elif f['check'] == 'low_quality':
                failures = ', '.join(f.get('failures', []))
                lines.append(f'- **Low-Quality:** `{f["note_id"]}` — {f["title"]} (failed: {failures})')
        lines.append('')

    # LOW priority findings
    low = [f for f in findings if f.get('priority') == 'LOW']
    if low:
        lines.append('## LOW Priority')
        lines.append('')
        moc_drift = [f for f in low if f['check'] == 'moc_drift']
        stale = [f for f in low if f['check'] == 'staleness']
        orphan = [f for f in low if f['check'] == 'orphan_source']

        if stale:
            lines.append(f'### Disconnected Notes ({len(stale)})')
            lines.append('')
            for f in stale[:20]:
                lines.append(f'- `{f["note_id"]}` — {f["title"]}')
            if len(stale) > 20:
                lines.append(f'- ... and {len(stale) - 20} more')
            lines.append('')

        if orphan:
            lines.append(f'### Orphan Sources ({len(orphan)})')
            lines.append('')
            for f in orphan:
                lines.append(f'- `{f["source_id"]}` — {f["title"]}')
            lines.append('')

        if moc_drift:
            lines.append(f'### MOC Drift ({len(moc_drift)})')
            lines.append('')
            lines.append('Run `python3 scripts/rebuild_mocs.py vault/` to auto-assign.')
            lines.append('')
            for f in moc_drift[:20]:
                lines.append(f'- `{f["note_id"]}` — {f["title"]}')
            if len(moc_drift) > 20:
                lines.append(f'- ... and {len(moc_drift) - 20} more')
            lines.append('')

    output_path.write_text('\n'.join(lines), encoding='utf-8')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/maintain_vault.py <vault_path> [--archive] [--llm-review]")
        sys.exit(1)

    vault_path = sys.argv[1]
    do_archive = '--archive' in sys.argv
    do_llm = '--llm-review' in sys.argv

    vault = Path(vault_path)
    if not vault.exists():
        print(f"Vault not found: {vault_path}", file=sys.stderr)
        sys.exit(1)

    print("Loading vault data...", file=sys.stderr)
    notes = load_notes(vault_path)
    sources = load_sources(vault_path)
    edge_index = load_graph_edges(vault_path)
    moc_coverage = load_moc_coverage(vault_path)
    print(f"  {len(notes)} notes, {len(sources)} sources, "
          f"{len(edge_index)} connected notes", file=sys.stderr)

    # Run all 5 checks
    print("Running checks...", file=sys.stderr)

    print("  1. Staleness...", file=sys.stderr)
    stale = check_staleness(notes, edge_index)
    print(f"     {len(stale)} disconnected notes", file=sys.stderr)

    print("  2. Near-duplicates...", file=sys.stderr)
    dupes = check_near_duplicates(notes)
    print(f"     {len(dupes)} near-duplicate pairs", file=sys.stderr)

    print("  3. Low-quality...", file=sys.stderr)
    low_q = check_low_quality(notes)
    print(f"     {len(low_q)} low-quality notes", file=sys.stderr)

    print("  4. Orphan sources...", file=sys.stderr)
    orphans = check_orphan_sources(sources, notes)
    print(f"     {len(orphans)} orphan sources", file=sys.stderr)

    print("  5. MOC drift...", file=sys.stderr)
    drift = check_moc_drift(notes, moc_coverage)
    print(f"     {len(drift)} notes without MOC", file=sys.stderr)

    # Combine and prioritize
    low_quality_ids = {f['note_id'] for f in low_q}
    all_findings = stale + dupes + low_q + orphans + drift

    for finding in all_findings:
        finding['priority'] = assign_priority(finding, edge_index, low_quality_ids)

    # Sort by priority
    priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    all_findings.sort(key=lambda f: priority_order.get(f.get('priority', 'LOW'), 3))

    # Optional LLM review of borderline cases (disconnected but quality-passing)
    if do_llm:
        borderline = [f for f in all_findings
                      if f['check'] == 'staleness' and f['note_id'] not in low_quality_ids]
        print(f"\n  LLM reviewing {len(borderline)} borderline notes...", file=sys.stderr)
        for f in borderline:
            # Find similar notes by shared tags
            note = notes[f['note_id']]
            note_tags = set(t.lower() for t in note.get('tags', []))
            similar = []
            for other_id, other in notes.items():
                if other_id == f['note_id']:
                    continue
                other_tags = set(t.lower() for t in other.get('tags', []))
                if len(note_tags & other_tags) >= 2:
                    similar.append(other['title'])
                    if len(similar) >= 3:
                        break
            verdict = llm_review_note(note, similar)
            f['llm_verdict'] = verdict
            if verdict == 'NO':
                f['priority'] = 'MEDIUM'  # Upgrade for attention

    # Archive action
    archived = []
    if do_archive:
        high_archive = [f for f in all_findings
                        if f.get('priority') == 'HIGH'
                        and f['check'] in ('staleness', 'low_quality')
                        and 'note_id' in f]
        print(f"\n  Archiving {len(high_archive)} HIGH priority notes...", file=sys.stderr)
        for f in high_archive:
            note_id = f['note_id']
            if note_id in notes:
                dst = archive_note(notes[note_id], vault_path)
                archived.append(note_id)
                print(f"    Archived: {note_id} → {dst}", file=sys.stderr)

    # Write reports
    stats = {
        'total_notes': len(notes),
        'total_sources': len(sources),
        'archived': len(archived),
    }

    report_md = vault / 'maintenance-report.md'
    report_jsonl = vault / 'maintenance-report.jsonl'

    write_markdown_report(all_findings, stats, report_md)
    write_jsonl_report(all_findings, report_jsonl)

    # Summary
    priority_counts = Counter(f.get('priority', 'LOW') for f in all_findings)
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"MAINTENANCE COMPLETE", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    print(f"Findings:  {len(all_findings)}", file=sys.stderr)
    print(f"  HIGH:    {priority_counts.get('HIGH', 0)}", file=sys.stderr)
    print(f"  MEDIUM:  {priority_counts.get('MEDIUM', 0)}", file=sys.stderr)
    print(f"  LOW:     {priority_counts.get('LOW', 0)}", file=sys.stderr)
    if archived:
        print(f"Archived:  {len(archived)}", file=sys.stderr)
    print(f"\nOutputs:", file=sys.stderr)
    print(f"  {report_md}", file=sys.stderr)
    print(f"  {report_jsonl}", file=sys.stderr)


if __name__ == '__main__':
    main()
