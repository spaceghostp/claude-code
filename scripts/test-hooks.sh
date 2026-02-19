#!/usr/bin/env bash
# Smoke tests for Claude Code hooks
# Usage: bash scripts/test-hooks.sh
set -euo pipefail

PASS=0
FAIL=0
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

pass() { PASS=$((PASS + 1)); echo "  PASS: $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  FAIL: $1"; }

# ── Test 1: audit-logger.sh ──────────────────────────────────────
echo "Testing audit-logger.sh..."
TMPDIR1=$(mktemp -d)
mkdir -p "$TMPDIR1/.claude"

AUDIT_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR1',
    'tool_name': 'Read',
    'tool_input': {'file_path': '/tmp/test.txt'},
    'hook_event_name': 'PreToolUse'
}))")

printf '%s' "$AUDIT_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/audit-logger.sh"

if [ -f "$TMPDIR1/.claude/audit-log.jsonl" ]; then
    LINE=$(cat "$TMPDIR1/.claude/audit-log.jsonl")
    # Validate it's valid JSON
    if echo "$LINE" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
        pass "audit-logger produces valid JSONL"
    else
        fail "audit-logger output is not valid JSON"
    fi
    # Check expected fields
    if echo "$LINE" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'tool' in d and d['tool']=='Read'" 2>/dev/null; then
        pass "audit-logger records tool name"
    else
        fail "audit-logger missing or wrong tool name"
    fi
    if echo "$LINE" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'params_hash' in d and len(d['params_hash'])==64" 2>/dev/null; then
        pass "audit-logger hashes params (SHA256)"
    else
        fail "audit-logger params_hash missing or wrong length"
    fi
else
    fail "audit-logger did not create audit-log.jsonl"
fi
rm -rf "$TMPDIR1"

# ── Test 1b: audit-logger.sh log rotation ────────────────────────
echo "Testing audit-logger.sh log rotation..."
TMPDIR1B=$(mktemp -d)
mkdir -p "$TMPDIR1B/.claude"

# Create an audit log with 2001 lines (exceeds 2000 threshold)
for i in $(seq 1 2001); do
    echo '{"tool":"Bash","params_hash":"abc123","timestamp":"2025-01-01T00:00:00Z","user":"test","project":"test"}' >> "$TMPDIR1B/.claude/audit-log.jsonl"
done

AUDIT_ROT_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR1B',
    'tool_name': 'Edit',
    'tool_input': {'file_path': '/tmp/test.txt'},
    'hook_event_name': 'PreToolUse'
}))")

printf '%s' "$AUDIT_ROT_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/audit-logger.sh"

LINE_COUNT=$(wc -l < "$TMPDIR1B/.claude/audit-log.jsonl")
# After rotation (2001 > 2000 → keep last 1000) plus the new entry = 1001
if [ "$LINE_COUNT" -le 1002 ]; then
    pass "audit-logger rotates log when exceeding 2000 lines"
else
    fail "audit-logger rotation failed: expected ~1001 lines, got $LINE_COUNT"
fi
rm -rf "$TMPDIR1B"

# ── Test 1c: audit-logger.sh malformed JSON fallback ─────────────
echo "Testing audit-logger.sh malformed JSON fallback..."
TMPDIR1C=$(mktemp -d)
mkdir -p "$TMPDIR1C/.claude"

STDERR_OUT=$(printf 'NOT VALID JSON' | CWD="$TMPDIR1C" bash "$SCRIPT_DIR/.claude/hooks/audit-logger.sh" 2>&1 || true)

if echo "$STDERR_OUT" | grep -q "HOOK_PARSE_FAILURE"; then
    pass "audit-logger emits parse failure warning on malformed JSON"
else
    fail "audit-logger should emit HOOK_PARSE_FAILURE on malformed JSON"
fi
rm -rf "$TMPDIR1C"

# ── Test 1d: audit-logger.sh timestamp and project fields ────────
echo "Testing audit-logger.sh timestamp and project fields..."
TMPDIR1D=$(mktemp -d)
mkdir -p "$TMPDIR1D/.claude"

AUDIT_FIELDS_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR1D',
    'tool_name': 'Glob',
    'tool_input': {'pattern': '*.ts'},
    'hook_event_name': 'PreToolUse'
}))")

printf '%s' "$AUDIT_FIELDS_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/audit-logger.sh"

if [ -f "$TMPDIR1D/.claude/audit-log.jsonl" ]; then
    LINE=$(cat "$TMPDIR1D/.claude/audit-log.jsonl")
    if echo "$LINE" | python3 -c "
import sys,json
d=json.load(sys.stdin)
assert 'timestamp' in d, 'missing timestamp'
assert 'project' in d, 'missing project'
assert 'user' in d, 'missing user'
assert d['tool'] == 'Glob', f'wrong tool: {d[\"tool\"]}'
" 2>/dev/null; then
        pass "audit-logger records timestamp, project, and user fields"
    else
        fail "audit-logger missing timestamp/project/user fields"
    fi
else
    fail "audit-logger did not create audit-log.jsonl"
fi
rm -rf "$TMPDIR1D"

# ── Test 2: detect-deploy-failure.sh ─────────────────────────────
echo "Testing detect-deploy-failure.sh..."
TMPDIR2=$(mktemp -d)
mkdir -p "$TMPDIR2/.claude"

# 2a: Non-deploy command should be ignored (no output)
NONDEPLOY_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR2',
    'tool_name': 'Bash',
    'tool_input': {'command': 'echo hello'},
    'tool_response': {'stdout': 'hello', 'stderr': '', 'exit_code': 0},
    'hook_event_name': 'PostToolUse'
}))")

printf '%s' "$NONDEPLOY_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/detect-deploy-failure.sh" 2>/dev/null
if [ ! -f "$TMPDIR2/.claude/rollback-suggested.txt" ]; then
    pass "detect-deploy-failure ignores non-deploy commands"
else
    fail "detect-deploy-failure triggered on non-deploy command"
fi

# 2b: Failed deploy should trigger rollback suggestion
DEPLOY_FAIL_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR2',
    'tool_name': 'Bash',
    'tool_input': {'command': 'kubectl apply -f deployment.yaml'},
    'tool_response': {'stdout': '', 'stderr': 'error applying', 'exit_code': 1},
    'hook_event_name': 'PostToolUse'
}))")

STDERR_OUT=$(printf '%s' "$DEPLOY_FAIL_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/detect-deploy-failure.sh" 2>&1 >/dev/null || true)
if [ -f "$TMPDIR2/.claude/rollback-suggested.txt" ]; then
    pass "detect-deploy-failure detects failed deploy (exit code)"
else
    fail "detect-deploy-failure missed failed deploy"
fi

if echo "$STDERR_OUT" | grep -q "DEPLOY_FAILURE"; then
    pass "detect-deploy-failure emits stderr warning"
else
    fail "detect-deploy-failure missing stderr warning"
fi

rm -rf "$TMPDIR2"

# 2c: Deploy with CrashLoopBackOff (exit 0 but fatal pattern)
TMPDIR2B=$(mktemp -d)
mkdir -p "$TMPDIR2B/.claude"

DEPLOY_CRASH_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR2B',
    'tool_name': 'Bash',
    'tool_input': {'command': 'kubectl apply -f deployment.yaml'},
    'tool_response': {'stdout': 'pod/myapp CrashLoopBackOff', 'stderr': '', 'exit_code': 0},
    'hook_event_name': 'PostToolUse'
}))")

printf '%s' "$DEPLOY_CRASH_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/detect-deploy-failure.sh" 2>/dev/null || true
if [ -f "$TMPDIR2B/.claude/rollback-suggested.txt" ]; then
    pass "detect-deploy-failure detects CrashLoopBackOff pattern"
else
    fail "detect-deploy-failure missed CrashLoopBackOff pattern"
fi
rm -rf "$TMPDIR2B"

# 2d: All secondary failure patterns (exit 0)
echo "Testing detect-deploy-failure.sh secondary patterns..."
for PATTERN in "ImagePullBackOff" "ErrImagePull" "OOMKilled" "timed out" "FAILED"; do
    TMPDIR2D=$(mktemp -d)
    mkdir -p "$TMPDIR2D/.claude"

    PATTERN_INPUT=$(python3 -c "import json; print(json.dumps({
        'session_id': 'test-session',
        'cwd': '$TMPDIR2D',
        'tool_name': 'Bash',
        'tool_input': {'command': 'kubectl apply -f deployment.yaml'},
        'tool_response': {'stdout': 'pod/myapp $PATTERN', 'stderr': '', 'exit_code': 0},
        'hook_event_name': 'PostToolUse'
    }))")

    printf '%s' "$PATTERN_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/detect-deploy-failure.sh" 2>/dev/null || true
    if [ -f "$TMPDIR2D/.claude/rollback-suggested.txt" ]; then
        pass "detect-deploy-failure detects '$PATTERN' pattern"
    else
        fail "detect-deploy-failure missed '$PATTERN' pattern"
    fi
    rm -rf "$TMPDIR2D"
done

# 2e: All deploy command patterns
echo "Testing detect-deploy-failure.sh deploy command patterns..."
for CMD in "docker push myimage:latest" "helm install myrelease ./chart" "helm upgrade myrelease ./chart" "terraform apply -auto-approve" "kubectl rollout restart deployment/myapp"; do
    TMPDIR2E=$(mktemp -d)
    mkdir -p "$TMPDIR2E/.claude"

    CMD_INPUT=$(python3 -c "import json,sys; print(json.dumps({
        'session_id': 'test-session',
        'cwd': sys.argv[1],
        'tool_name': 'Bash',
        'tool_input': {'command': sys.argv[2]},
        'tool_response': {'stdout': '', 'stderr': 'deploy error', 'exit_code': 1},
        'hook_event_name': 'PostToolUse'
    }))" "$TMPDIR2E" "$CMD")

    printf '%s' "$CMD_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/detect-deploy-failure.sh" 2>/dev/null || true
    if [ -f "$TMPDIR2E/.claude/rollback-suggested.txt" ]; then
        pass "detect-deploy-failure recognizes command: $(echo "$CMD" | cut -d' ' -f1-2)"
    else
        fail "detect-deploy-failure missed command: $(echo "$CMD" | cut -d' ' -f1-2)"
    fi
    rm -rf "$TMPDIR2E"
done

# 2f: Rollback file contains expected content
echo "Testing detect-deploy-failure.sh rollback file content..."
TMPDIR2F=$(mktemp -d)
mkdir -p "$TMPDIR2F/.claude"

ROLLBACK_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR2F',
    'tool_name': 'Bash',
    'tool_input': {'command': 'kubectl apply -f deployment.yaml'},
    'tool_response': {'stdout': '', 'stderr': 'timeout', 'exit_code': 1},
    'hook_event_name': 'PostToolUse'
}))")

printf '%s' "$ROLLBACK_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/detect-deploy-failure.sh" 2>/dev/null || true
if [ -f "$TMPDIR2F/.claude/rollback-suggested.txt" ]; then
    CONTENT=$(cat "$TMPDIR2F/.claude/rollback-suggested.txt")
    if echo "$CONTENT" | grep -q "Deploy failure detected" && echo "$CONTENT" | grep -q "Command:" && echo "$CONTENT" | grep -q "Consider:"; then
        pass "detect-deploy-failure rollback file contains expected fields"
    else
        fail "detect-deploy-failure rollback file missing expected content"
    fi
else
    fail "detect-deploy-failure did not create rollback-suggested.txt"
fi
rm -rf "$TMPDIR2F"

# 2g: Malformed JSON fallback
echo "Testing detect-deploy-failure.sh malformed JSON..."
TMPDIR2G=$(mktemp -d)
mkdir -p "$TMPDIR2G/.claude"

STDERR_OUT=$(printf 'INVALID JSON' | bash "$SCRIPT_DIR/.claude/hooks/detect-deploy-failure.sh" 2>&1 || true)
# Should exit gracefully (no crash)
if echo "$STDERR_OUT" | grep -q "HOOK_PARSE_FAILURE" || [ $? -eq 0 ]; then
    pass "detect-deploy-failure handles malformed JSON gracefully"
else
    fail "detect-deploy-failure crashed on malformed JSON"
fi
rm -rf "$TMPDIR2G"

# ── Test 3: suggest-tests.sh ─────────────────────────────────────
echo "Testing suggest-tests.sh..."
TMPDIR3=$(mktemp -d)
mkdir -p "$TMPDIR3/.claude"
mkdir -p "$TMPDIR3/src"

# Create a source file and its sibling test
echo "// source" > "$TMPDIR3/src/utils.ts"
echo "// test" > "$TMPDIR3/src/utils.test.ts"

SUGGEST_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR3',
    'tool_name': 'Edit',
    'tool_input': {'file_path': '$TMPDIR3/src/utils.ts'},
    'hook_event_name': 'PostToolUse'
}))")

printf '%s' "$SUGGEST_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/suggest-tests.sh"

if [ -f "$TMPDIR3/.claude/pending-tests.txt" ]; then
    if grep -q "utils.test.ts" "$TMPDIR3/.claude/pending-tests.txt"; then
        pass "suggest-tests finds sibling test file"
    else
        fail "suggest-tests did not find utils.test.ts"
    fi
else
    fail "suggest-tests did not create pending-tests.txt"
fi

# 3b: Editing a test file should be skipped
SUGGEST_TEST_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR3',
    'tool_name': 'Write',
    'tool_input': {'file_path': '$TMPDIR3/src/utils.test.ts'},
    'hook_event_name': 'PostToolUse'
}))")

# Clear pending-tests and re-run
> "$TMPDIR3/.claude/pending-tests.txt"
printf '%s' "$SUGGEST_TEST_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/suggest-tests.sh"

if [ ! -s "$TMPDIR3/.claude/pending-tests.txt" ]; then
    pass "suggest-tests skips test files"
else
    fail "suggest-tests should skip test files but didn't"
fi

# 3c: Non-Edit/Write tool should be skipped
SUGGEST_READ_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR3',
    'tool_name': 'Read',
    'tool_input': {'file_path': '$TMPDIR3/src/utils.ts'},
    'hook_event_name': 'PostToolUse'
}))")

> "$TMPDIR3/.claude/pending-tests.txt"
printf '%s' "$SUGGEST_READ_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/suggest-tests.sh"

if [ ! -s "$TMPDIR3/.claude/pending-tests.txt" ]; then
    pass "suggest-tests ignores non-Edit/Write tools"
else
    fail "suggest-tests should ignore Read tool but didn't"
fi

# 3d: Deduplication during rotation (>50 lines triggers dedup + truncation)
TMPDIR3D=$(mktemp -d)
mkdir -p "$TMPDIR3D/.claude"
mkdir -p "$TMPDIR3D/src"
echo "// source" > "$TMPDIR3D/src/app.ts"
echo "// test" > "$TMPDIR3D/src/app.test.ts"

# Seed pending-tests.txt with 55 lines including duplicates
PENDING3D="$TMPDIR3D/.claude/pending-tests.txt"
for i in $(seq 1 25); do
    echo "/fake/path/dup.test.ts" >> "$PENDING3D"
    echo "/fake/path/unique${i}.test.ts" >> "$PENDING3D"
done
# Add 5 more to reach 55
for i in $(seq 1 5); do
    echo "/fake/path/extra${i}.test.ts" >> "$PENDING3D"
done

SUGGEST_DEDUP_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR3D',
    'tool_name': 'Edit',
    'tool_input': {'file_path': '$TMPDIR3D/src/app.ts'},
    'hook_event_name': 'PostToolUse'
}))")

printf '%s' "$SUGGEST_DEDUP_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/suggest-tests.sh"

# After rotation, duplicates of dup.test.ts should be collapsed to 1
DUP_COUNT=$(grep -c "/fake/path/dup.test.ts" "$PENDING3D" 2>/dev/null || echo "0")
LINE_COUNT=$(wc -l < "$PENDING3D" 2>/dev/null || echo "0")

if [ "$DUP_COUNT" -le 1 ]; then
    pass "suggest-tests deduplicates during rotation"
else
    fail "suggest-tests did not deduplicate (found $DUP_COUNT copies of dup.test.ts)"
fi

if [ "$LINE_COUNT" -le 26 ]; then
    pass "suggest-tests caps lines after dedup (got $LINE_COUNT)"
else
    fail "suggest-tests did not cap lines after dedup (got $LINE_COUNT, expected <=26)"
fi

rm -rf "$TMPDIR3D"

rm -rf "$TMPDIR3"

# 3d: .spec.ts sibling pattern
echo "Testing suggest-tests.sh .spec pattern..."
TMPDIR3D=$(mktemp -d)
mkdir -p "$TMPDIR3D/.claude" "$TMPDIR3D/src"
echo "// source" > "$TMPDIR3D/src/api.ts"
echo "// spec" > "$TMPDIR3D/src/api.spec.ts"

SPEC_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR3D',
    'tool_name': 'Edit',
    'tool_input': {'file_path': '$TMPDIR3D/src/api.ts'},
    'hook_event_name': 'PostToolUse'
}))")

printf '%s' "$SPEC_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/suggest-tests.sh"

if [ -f "$TMPDIR3D/.claude/pending-tests.txt" ] && grep -q "api.spec.ts" "$TMPDIR3D/.claude/pending-tests.txt"; then
    pass "suggest-tests finds .spec.ts sibling"
else
    fail "suggest-tests missed .spec.ts sibling"
fi
rm -rf "$TMPDIR3D"

# 3e: _test.ts sibling pattern
echo "Testing suggest-tests.sh _test pattern..."
TMPDIR3E=$(mktemp -d)
mkdir -p "$TMPDIR3E/.claude" "$TMPDIR3E/src"
echo "// source" > "$TMPDIR3E/src/handler.ts"
echo "// test" > "$TMPDIR3E/src/handler_test.ts"

UTEST_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR3E',
    'tool_name': 'Edit',
    'tool_input': {'file_path': '$TMPDIR3E/src/handler.ts'},
    'hook_event_name': 'PostToolUse'
}))")

printf '%s' "$UTEST_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/suggest-tests.sh"

if [ -f "$TMPDIR3E/.claude/pending-tests.txt" ] && grep -q "handler_test.ts" "$TMPDIR3E/.claude/pending-tests.txt"; then
    pass "suggest-tests finds _test.ts sibling"
else
    fail "suggest-tests missed _test.ts sibling"
fi
rm -rf "$TMPDIR3E"

# 3f: __tests__ directory pattern
echo "Testing suggest-tests.sh __tests__ directory..."
TMPDIR3F=$(mktemp -d)
mkdir -p "$TMPDIR3F/.claude" "$TMPDIR3F/src/__tests__"
echo "// source" > "$TMPDIR3F/src/store.ts"
echo "// test" > "$TMPDIR3F/src/__tests__/store.test.ts"

TESTS_DIR_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR3F',
    'tool_name': 'Edit',
    'tool_input': {'file_path': '$TMPDIR3F/src/store.ts'},
    'hook_event_name': 'PostToolUse'
}))")

printf '%s' "$TESTS_DIR_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/suggest-tests.sh"

if [ -f "$TMPDIR3F/.claude/pending-tests.txt" ] && grep -q "__tests__/store.test.ts" "$TMPDIR3F/.claude/pending-tests.txt"; then
    pass "suggest-tests finds __tests__/ directory sibling"
else
    fail "suggest-tests missed __tests__/ directory sibling"
fi
rm -rf "$TMPDIR3F"

# 3g: Deduplication - same file edited twice should not duplicate entry
echo "Testing suggest-tests.sh deduplication..."
TMPDIR3G=$(mktemp -d)
mkdir -p "$TMPDIR3G/.claude" "$TMPDIR3G/src"
echo "// source" > "$TMPDIR3G/src/utils.ts"
echo "// test" > "$TMPDIR3G/src/utils.test.ts"

DEDUP_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR3G',
    'tool_name': 'Edit',
    'tool_input': {'file_path': '$TMPDIR3G/src/utils.ts'},
    'hook_event_name': 'PostToolUse'
}))")

printf '%s' "$DEDUP_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/suggest-tests.sh"
printf '%s' "$DEDUP_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/suggest-tests.sh"

if [ -f "$TMPDIR3G/.claude/pending-tests.txt" ]; then
    ENTRY_COUNT=$(grep -c "utils.test.ts" "$TMPDIR3G/.claude/pending-tests.txt" || true)
    if [ "$ENTRY_COUNT" -eq 1 ]; then
        pass "suggest-tests deduplicates entries"
    else
        fail "suggest-tests duplicated entry ($ENTRY_COUNT occurrences)"
    fi
else
    fail "suggest-tests did not create pending-tests.txt"
fi
rm -rf "$TMPDIR3G"

# 3h: No sibling test file exists — no new entry
echo "Testing suggest-tests.sh no sibling test..."
TMPDIR3H=$(mktemp -d)
mkdir -p "$TMPDIR3H/.claude" "$TMPDIR3H/src"
echo "// source with no test" > "$TMPDIR3H/src/orphan.ts"

ORPHAN_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR3H',
    'tool_name': 'Edit',
    'tool_input': {'file_path': '$TMPDIR3H/src/orphan.ts'},
    'hook_event_name': 'PostToolUse'
}))")

printf '%s' "$ORPHAN_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/suggest-tests.sh"

if [ -f "$TMPDIR3H/.claude/pending-tests.txt" ]; then
    if [ ! -s "$TMPDIR3H/.claude/pending-tests.txt" ]; then
        pass "suggest-tests produces empty file when no sibling test exists"
    else
        fail "suggest-tests added entry when no sibling test exists"
    fi
else
    pass "suggest-tests produces no file when no sibling test exists"
fi
rm -rf "$TMPDIR3H"

# 3i: File rotation — pending-tests.txt over 50 lines should be truncated
echo "Testing suggest-tests.sh file rotation..."
TMPDIR3I=$(mktemp -d)
mkdir -p "$TMPDIR3I/.claude" "$TMPDIR3I/src"
echo "// source" > "$TMPDIR3I/src/x.ts"
echo "// test" > "$TMPDIR3I/src/x.test.ts"

# Pre-fill with 55 lines
for i in $(seq 1 55); do
    echo "/fake/path/file${i}.test.ts" >> "$TMPDIR3I/.claude/pending-tests.txt"
done

ROTATE_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR3I',
    'tool_name': 'Edit',
    'tool_input': {'file_path': '$TMPDIR3I/src/x.ts'},
    'hook_event_name': 'PostToolUse'
}))")

printf '%s' "$ROTATE_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/suggest-tests.sh"

LINE_COUNT=$(wc -l < "$TMPDIR3I/.claude/pending-tests.txt")
# After rotation (55 > 50 → keep last 25) plus possibly new entry = ~26
if [ "$LINE_COUNT" -le 30 ]; then
    pass "suggest-tests rotates pending-tests.txt when exceeding 50 lines"
else
    fail "suggest-tests rotation failed: expected ~26 lines, got $LINE_COUNT"
fi
rm -rf "$TMPDIR3I"

# ── Test 4: track-context-pressure.sh ────────────────────────────
echo "Testing track-context-pressure.sh..."
TMPDIR4=$(mktemp -d)
mkdir -p "$TMPDIR4/.claude"

# Create a fake transcript file with known size
FAKE_TRANSCRIPT="$TMPDIR4/transcript.jsonl"
dd if=/dev/zero bs=1024 count=100 of="$FAKE_TRANSCRIPT" 2>/dev/null  # 100KB

PRESSURE_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR4',
    'tool_name': 'Read',
    'tool_input': {'file_path': '/tmp/test.txt'},
    'tool_response': {'stdout': '', 'stderr': '', 'exit_code': 0},
    'hook_event_name': 'PostToolUse',
    'transcript_path': '$FAKE_TRANSCRIPT'
}))")

printf '%s' "$PRESSURE_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/track-context-pressure.sh"

if [ -f "$TMPDIR4/.claude/context-pressure.jsonl" ]; then
    LINE=$(cat "$TMPDIR4/.claude/context-pressure.jsonl")
    # Validate it's valid JSON
    if echo "$LINE" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
        pass "track-context-pressure produces valid JSONL"
    else
        fail "track-context-pressure output is not valid JSON"
    fi
    # Check expected fields
    if echo "$LINE" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'transcript_bytes' in d and 'estimated_pct' in d and 'timestamp' in d" 2>/dev/null; then
        pass "track-context-pressure has required fields"
    else
        fail "track-context-pressure missing required fields"
    fi
    # Check transcript_bytes is roughly 100KB (102400)
    if echo "$LINE" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['transcript_bytes'] > 90000" 2>/dev/null; then
        pass "track-context-pressure measures transcript size"
    else
        fail "track-context-pressure transcript_bytes incorrect"
    fi
else
    fail "track-context-pressure did not create context-pressure.jsonl"
fi

# 4b: Missing transcript_path should exit cleanly (no output file)
TMPDIR4B=$(mktemp -d)
mkdir -p "$TMPDIR4B/.claude"

PRESSURE_NOXCRIPT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR4B',
    'tool_name': 'Read',
    'tool_input': {'file_path': '/tmp/test.txt'},
    'tool_response': {'stdout': '', 'stderr': '', 'exit_code': 0},
    'hook_event_name': 'PostToolUse'
}))")

printf '%s' "$PRESSURE_NOXCRIPT" | bash "$SCRIPT_DIR/.claude/hooks/track-context-pressure.sh"

if [ ! -f "$TMPDIR4B/.claude/context-pressure.jsonl" ]; then
    pass "track-context-pressure skips when no transcript_path"
else
    fail "track-context-pressure should skip without transcript_path"
fi

rm -rf "$TMPDIR4" "$TMPDIR4B"

# 4c: Log rotation — over 500 lines should be truncated
echo "Testing track-context-pressure.sh log rotation..."
TMPDIR4C=$(mktemp -d)
mkdir -p "$TMPDIR4C/.claude"

FAKE_TRANSCRIPT_C="$TMPDIR4C/transcript.jsonl"
echo '{}' > "$FAKE_TRANSCRIPT_C"

# Pre-fill with 510 lines
for i in $(seq 1 510); do
    echo '{"timestamp":"2025-01-01T00:00:00Z","transcript_bytes":1000,"estimated_pct":1}' >> "$TMPDIR4C/.claude/context-pressure.jsonl"
done

ROT_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR4C',
    'tool_name': 'Read',
    'tool_input': {'file_path': '/tmp/test.txt'},
    'tool_response': {'stdout': '', 'stderr': '', 'exit_code': 0},
    'hook_event_name': 'PostToolUse',
    'transcript_path': '$FAKE_TRANSCRIPT_C'
}))")

printf '%s' "$ROT_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/track-context-pressure.sh"

LINE_COUNT=$(wc -l < "$TMPDIR4C/.claude/context-pressure.jsonl")
# After rotation (510 > 500 → keep last 250) plus new entry = 251
if [ "$LINE_COUNT" -le 260 ]; then
    pass "track-context-pressure rotates log when exceeding 500 lines"
else
    fail "track-context-pressure rotation failed: expected ~251 lines, got $LINE_COUNT"
fi
rm -rf "$TMPDIR4C"

# 4d: Non-existent transcript file — transcript_bytes should be 0
echo "Testing track-context-pressure.sh non-existent transcript..."
TMPDIR4D=$(mktemp -d)
mkdir -p "$TMPDIR4D/.claude"

MISSING_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR4D',
    'tool_name': 'Read',
    'tool_input': {'file_path': '/tmp/test.txt'},
    'tool_response': {'stdout': '', 'stderr': '', 'exit_code': 0},
    'hook_event_name': 'PostToolUse',
    'transcript_path': '/tmp/nonexistent_transcript_file_12345.jsonl'
}))")

printf '%s' "$MISSING_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/track-context-pressure.sh"

if [ -f "$TMPDIR4D/.claude/context-pressure.jsonl" ]; then
    LINE=$(cat "$TMPDIR4D/.claude/context-pressure.jsonl")
    if echo "$LINE" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['transcript_bytes'] == 0" 2>/dev/null; then
        pass "track-context-pressure reports 0 bytes for missing transcript"
    else
        fail "track-context-pressure should report 0 bytes for missing transcript"
    fi
else
    fail "track-context-pressure did not create output for missing transcript"
fi
rm -rf "$TMPDIR4D"

# 4e: Large transcript — estimated_pct caps at 100
echo "Testing track-context-pressure.sh percentage cap..."
TMPDIR4E=$(mktemp -d)
mkdir -p "$TMPDIR4E/.claude"

LARGE_TRANSCRIPT="$TMPDIR4E/transcript.jsonl"
dd if=/dev/zero bs=1024 count=1000 of="$LARGE_TRANSCRIPT" 2>/dev/null  # 1MB (> 800KB max)

CAP_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR4E',
    'tool_name': 'Read',
    'tool_input': {'file_path': '/tmp/test.txt'},
    'tool_response': {'stdout': '', 'stderr': '', 'exit_code': 0},
    'hook_event_name': 'PostToolUse',
    'transcript_path': '$LARGE_TRANSCRIPT'
}))")

printf '%s' "$CAP_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/track-context-pressure.sh"

if [ -f "$TMPDIR4E/.claude/context-pressure.jsonl" ]; then
    LINE=$(cat "$TMPDIR4E/.claude/context-pressure.jsonl")
    if echo "$LINE" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['estimated_pct'] == 100, f'got {d[\"estimated_pct\"]}'" 2>/dev/null; then
        pass "track-context-pressure caps estimated_pct at 100"
    else
        fail "track-context-pressure should cap estimated_pct at 100 for large transcripts"
    fi
else
    fail "track-context-pressure did not create output for large transcript"
fi
rm -rf "$TMPDIR4E"

# ── Test 5: context-monitor.sh ───────────────────────────────────
echo "Testing context-monitor.sh..."

# 5a: No audit log — should exit cleanly
TMPDIR5A=$(mktemp -d)
mkdir -p "$TMPDIR5A/.claude"

MONITOR_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR5A',
    'tool_name': 'Read',
    'tool_input': {'file_path': '/tmp/test.txt'},
    'hook_event_name': 'PreToolUse'
}))")

printf '%s' "$MONITOR_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/context-monitor.sh" 2>/dev/null
if [ ! -f "$TMPDIR5A/.claude/context-pressure.txt" ]; then
    pass "context-monitor exits cleanly when no audit log exists"
else
    fail "context-monitor should not create warning without audit log"
fi
rm -rf "$TMPDIR5A"

# 5b: Below threshold — no warning
TMPDIR5B=$(mktemp -d)
mkdir -p "$TMPDIR5B/.claude"

# Create an audit log with exactly 20 lines (below default threshold of 100, and 20 % 20 == 0)
for i in $(seq 1 20); do
    echo '{"tool":"Read","params_hash":"abc","timestamp":"2025-01-01T00:00:00Z","user":"test","project":"test"}' >> "$TMPDIR5B/.claude/audit-log.jsonl"
done

BELOW_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR5B',
    'tool_name': 'Read',
    'tool_input': {'file_path': '/tmp/test.txt'},
    'hook_event_name': 'PreToolUse'
}))")

printf '%s' "$BELOW_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/context-monitor.sh" 2>/dev/null
if [ ! -f "$TMPDIR5B/.claude/context-pressure.txt" ]; then
    pass "context-monitor no warning below threshold"
else
    fail "context-monitor should not warn when below threshold"
fi
rm -rf "$TMPDIR5B"

# 5c: Sampling skip — non-20-multiple line count should be skipped
TMPDIR5C=$(mktemp -d)
mkdir -p "$TMPDIR5C/.claude"

# Create 25 lines (25 % 20 = 5 != 0 -> should skip)
for i in $(seq 1 25); do
    echo '{"tool":"Read","params_hash":"abc","timestamp":"2025-01-01T00:00:00Z","user":"test","project":"test"}' >> "$TMPDIR5C/.claude/audit-log.jsonl"
done

SKIP_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR5C',
    'tool_name': 'Read',
    'tool_input': {'file_path': '/tmp/test.txt'},
    'hook_event_name': 'PreToolUse'
}))")

printf '%s' "$SKIP_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/context-monitor.sh" 2>/dev/null
if [ ! -f "$TMPDIR5C/.claude/context-pressure.txt" ]; then
    pass "context-monitor skips on non-20-multiple line count"
else
    fail "context-monitor should skip when line count % 20 != 0"
fi
rm -rf "$TMPDIR5C"

# 5d: Above threshold with high density — should warn
TMPDIR5D=$(mktemp -d)
mkdir -p "$TMPDIR5D/.claude"

# Create 120 lines (120 > 100 threshold, 120 % 20 == 0, last 50 lines has 50 >= 40 density)
for i in $(seq 1 120); do
    echo '{"tool":"Read","params_hash":"abc","timestamp":"2025-01-01T00:00:00Z","user":"test","project":"test"}' >> "$TMPDIR5D/.claude/audit-log.jsonl"
done

WARN_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR5D',
    'tool_name': 'Read',
    'tool_input': {'file_path': '/tmp/test.txt'},
    'hook_event_name': 'PreToolUse'
}))")

STDERR_OUT=$(printf '%s' "$WARN_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/context-monitor.sh" 2>&1 || true)
if [ -f "$TMPDIR5D/.claude/context-pressure.txt" ]; then
    pass "context-monitor creates warning when above threshold with high density"
else
    fail "context-monitor should create context-pressure.txt when above threshold"
fi

if echo "$STDERR_OUT" | grep -q "CONTEXT_PRESSURE"; then
    pass "context-monitor emits CONTEXT_PRESSURE stderr warning"
else
    fail "context-monitor should emit CONTEXT_PRESSURE stderr warning"
fi
rm -rf "$TMPDIR5D"

# 5e: Custom threshold via env var
TMPDIR5E=$(mktemp -d)
mkdir -p "$TMPDIR5E/.claude"

# Create 60 lines — below default 100 but above custom 50
for i in $(seq 1 60); do
    echo '{"tool":"Read","params_hash":"abc","timestamp":"2025-01-01T00:00:00Z","user":"test","project":"test"}' >> "$TMPDIR5E/.claude/audit-log.jsonl"
done

CUSTOM_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR5E',
    'tool_name': 'Read',
    'tool_input': {'file_path': '/tmp/test.txt'},
    'hook_event_name': 'PreToolUse'
}))")

STDERR_OUT=$(printf '%s' "$CUSTOM_INPUT" | CONTEXT_PRESSURE_THRESHOLD=50 bash "$SCRIPT_DIR/.claude/hooks/context-monitor.sh" 2>&1 || true)
if [ -f "$TMPDIR5E/.claude/context-pressure.txt" ]; then
    pass "context-monitor respects CONTEXT_PRESSURE_THRESHOLD env var"
else
    fail "context-monitor should trigger with custom lower threshold"
fi
rm -rf "$TMPDIR5E"

# 5f: Warning clearance — when pressure drops, warning file should be removed
TMPDIR5F=$(mktemp -d)
mkdir -p "$TMPDIR5F/.claude"

# Create a stale context-pressure.txt
echo "old warning" > "$TMPDIR5F/.claude/context-pressure.txt"

# Create only 20 lines (below threshold, but 20 % 20 == 0 so it will check)
for i in $(seq 1 20); do
    echo '{"tool":"Read","params_hash":"abc","timestamp":"2025-01-01T00:00:00Z","user":"test","project":"test"}' >> "$TMPDIR5F/.claude/audit-log.jsonl"
done

CLEAR_INPUT=$(python3 -c "import json; print(json.dumps({
    'session_id': 'test-session',
    'cwd': '$TMPDIR5F',
    'tool_name': 'Read',
    'tool_input': {'file_path': '/tmp/test.txt'},
    'hook_event_name': 'PreToolUse'
}))")

printf '%s' "$CLEAR_INPUT" | bash "$SCRIPT_DIR/.claude/hooks/context-monitor.sh" 2>/dev/null
if [ ! -f "$TMPDIR5F/.claude/context-pressure.txt" ]; then
    pass "context-monitor clears warning when pressure drops"
else
    fail "context-monitor should remove context-pressure.txt when pressure drops"
fi
rm -rf "$TMPDIR5F"

# ── Summary ──────────────────────────────────────────────────────
echo ""
echo "Results: $PASS passed, $FAIL failed"
if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
