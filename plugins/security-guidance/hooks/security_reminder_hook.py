#!/usr/bin/env python3
"""
Security Reminder Hook for Claude Code
This hook checks for security patterns in file edits and warns about potential vulnerabilities.
Uses compiled regex patterns for robust detection (handles whitespace, bracket access, etc.).
"""

import json
import os
import random
import re
import sys
from datetime import datetime

# Debug log file
DEBUG_LOG_FILE = "/tmp/security-warnings-log.txt"


def debug_log(message):
    """Append debug message to log file with timestamp."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        with open(DEBUG_LOG_FILE, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass


# State file to track warnings shown (session-scoped using session ID)

# Security patterns configuration — uses compiled regex for robust matching
SECURITY_PATTERNS = [
    {
        "ruleName": "github_actions_workflow",
        "path_check": lambda path: ".github/workflows/" in path
        and (path.endswith(".yml") or path.endswith(".yaml")),
        "reminder": """You are editing a GitHub Actions workflow file. Be aware of these security risks:

1. **Command Injection**: Never use untrusted input (like issue titles, PR descriptions, commit messages) directly in run: commands without proper escaping
2. **Use environment variables**: Instead of ${{ github.event.issue.title }}, use env: with proper quoting
3. **Review the guide**: https://github.blog/security/vulnerability-research/how-to-catch-github-actions-workflow-injections-before-attackers-do/

Example of UNSAFE pattern to avoid:
run: echo "${{ github.event.issue.title }}"

Example of SAFE pattern:
env:
  TITLE: ${{ github.event.issue.title }}
run: echo "$TITLE"

Other risky inputs to be careful with:
- github.event.issue.body
- github.event.pull_request.title
- github.event.pull_request.body
- github.event.comment.body
- github.event.review.body
- github.event.review_comment.body
- github.event.pages.*.page_name
- github.event.commits.*.message
- github.event.head_commit.message
- github.event.head_commit.author.email
- github.event.head_commit.author.name
- github.event.commits.*.author.email
- github.event.commits.*.author.name
- github.event.pull_request.head.ref
- github.event.pull_request.head.label
- github.event.pull_request.head.repo.default_branch
- github.head_ref""",
    },
    {
        "ruleName": "child_process_exec",
        "patterns": [
            re.compile(r"child_process\s*\.\s*exec"),
            re.compile(r"(?<!\w)exec\s*\("),
            re.compile(r"execSync\s*\("),
        ],
        "reminder": """⚠️ Security Warning: Using child_process.exec() can lead to command injection vulnerabilities.

This codebase provides a safer alternative: src/utils/execFileNoThrow.ts

Instead of:
  exec(`command ${userInput}`)

Use:
  import { execFileNoThrow } from '../utils/execFileNoThrow.js'
  await execFileNoThrow('command', [userInput])

The execFileNoThrow utility:
- Uses execFile instead of exec (prevents shell injection)
- Handles Windows compatibility automatically
- Provides proper error handling
- Returns structured output with stdout, stderr, and status

Only use exec() if you absolutely need shell features and the input is guaranteed to be safe.""",
    },
    {
        "ruleName": "new_function_injection",
        "patterns": [
            re.compile(r"new\s+Function\s*\("),
            re.compile(r"\[\s*['\"]Function['\"]?\s*\]"),
        ],
        "reminder": "⚠️ Security Warning: Using new Function() with dynamic strings can lead to code injection vulnerabilities. Consider alternative approaches that don't evaluate arbitrary code. Only use new Function() if you truly need to evaluate arbitrary dynamic code.",
    },
    {
        "ruleName": "eval_injection",
        "patterns": [
            re.compile(r"(?<!\w)eval\s*\("),
            re.compile(r"\[\s*['\"]eval['\"]?\s*\]"),
        ],
        "reminder": "⚠️ Security Warning: eval() executes arbitrary code and is a major security risk. Consider using JSON.parse() for data parsing or alternative design patterns that don't require code evaluation. Only use eval() if you truly need to evaluate arbitrary code.",
    },
    {
        "ruleName": "react_dangerously_set_html",
        "patterns": [
            re.compile(r"dangerouslySetInnerHTML"),
        ],
        "reminder": "⚠️ Security Warning: dangerouslySetInnerHTML can lead to XSS vulnerabilities if used with untrusted content. Ensure all content is properly sanitized using an HTML sanitizer library like DOMPurify, or use safe alternatives.",
    },
    {
        "ruleName": "document_write_xss",
        "patterns": [
            re.compile(r"document\s*\.\s*write\s*\("),
        ],
        "reminder": "⚠️ Security Warning: document.write() can be exploited for XSS attacks and has performance issues. Use DOM manipulation methods like createElement() and appendChild() instead.",
    },
    {
        "ruleName": "innerHTML_xss",
        "patterns": [
            re.compile(r"\.\s*innerHTML\s*="),
        ],
        "reminder": "⚠️ Security Warning: Setting innerHTML with untrusted content can lead to XSS vulnerabilities. Use textContent for plain text or safe DOM methods for HTML content. If you need HTML support, consider using an HTML sanitizer library such as DOMPurify.",
    },
    {
        "ruleName": "pickle_deserialization",
        "patterns": [
            re.compile(r"(?<!\w)pickle\s*\."),
            re.compile(r"import\s+pickle"),
            re.compile(r"from\s+pickle\s+import"),
        ],
        "reminder": "⚠️ Security Warning: Using pickle with untrusted content can lead to arbitrary code execution. Consider using JSON or other safe serialization formats instead. Only use pickle if it is explicitly needed or requested by the user.",
    },
    {
        "ruleName": "os_system_injection",
        "patterns": [
            re.compile(r"os\s*\.\s*system\s*\("),
            re.compile(r"from\s+os\s+import\s+system"),
        ],
        "reminder": "⚠️ Security Warning: This code appears to use os.system. This should only be used with static arguments and never with arguments that could be user-controlled.",
    },
]

# Rate limit: re-warn every N occurrences after first warning
REWARN_INTERVAL = 3


def get_state_file(session_id):
    """Get session-specific state file path."""
    return os.path.expanduser(f"~/.claude/security_warnings_state_{session_id}.json")


def cleanup_old_state_files():
    """Remove state files older than 30 days."""
    try:
        state_dir = os.path.expanduser("~/.claude")
        if not os.path.exists(state_dir):
            return

        current_time = datetime.now().timestamp()
        thirty_days_ago = current_time - (30 * 24 * 60 * 60)

        for filename in os.listdir(state_dir):
            if filename.startswith("security_warnings_state_") and filename.endswith(
                ".json"
            ):
                file_path = os.path.join(state_dir, filename)
                try:
                    file_mtime = os.path.getmtime(file_path)
                    if file_mtime < thirty_days_ago:
                        os.remove(file_path)
                except (OSError, IOError):
                    pass
    except Exception:
        pass


def load_state(session_id):
    """Load the state of shown warnings from file. Returns dict of {key: count}."""
    state_file = get_state_file(session_id)
    if os.path.exists(state_file):
        try:
            with open(state_file, "r") as f:
                data = json.load(f)
                # Migrate from old set format to count dict
                if isinstance(data, list):
                    return {k: 1 for k in data}
                return data
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_state(session_id, warning_counts):
    """Save the state of warning counts to file."""
    state_file = get_state_file(session_id)
    try:
        os.makedirs(os.path.dirname(state_file), exist_ok=True)
        with open(state_file, "w") as f:
            json.dump(warning_counts, f)
    except IOError as e:
        debug_log(f"Failed to save state file: {e}")


def check_patterns(file_path, content):
    """Check if file path or content matches any security patterns.

    Returns list of (rule_name, reminder) for ALL matching rules.
    """
    normalized_path = file_path.lstrip("/")
    matches = []

    for pattern in SECURITY_PATTERNS:
        # Check path-based patterns
        if "path_check" in pattern and pattern["path_check"](normalized_path):
            matches.append((pattern["ruleName"], pattern["reminder"]))
            continue

        # Check regex-based patterns
        if "patterns" in pattern and content:
            for regex in pattern["patterns"]:
                if regex.search(content):
                    matches.append((pattern["ruleName"], pattern["reminder"]))
                    break

    return matches


def extract_content_from_input(tool_name, tool_input):
    """Extract content to check from tool input based on tool type."""
    if tool_name == "Write":
        return tool_input.get("content", "")
    elif tool_name == "Edit":
        return tool_input.get("new_string", "")
    elif tool_name == "MultiEdit":
        edits = tool_input.get("edits", [])
        if edits:
            return " ".join(edit.get("new_string", "") for edit in edits)
        return ""

    return ""


def main():
    """Main hook function."""
    # Check if security reminders are enabled
    security_reminder_enabled = os.environ.get("ENABLE_SECURITY_REMINDER", "1")

    # Only run if security reminders are enabled
    if security_reminder_enabled == "0":
        sys.exit(0)

    # Periodically clean up old state files (10% chance per run)
    if random.random() < 0.1:
        cleanup_old_state_files()

    # Read input from stdin
    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input)
    except json.JSONDecodeError as e:
        debug_log(f"JSON decode error: {e}")
        sys.exit(0)  # Allow tool to proceed if we can't parse input

    # Extract session ID and tool information from the hook input
    session_id = input_data.get("session_id", "default")
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Check if this is a relevant tool
    if tool_name not in ["Edit", "Write", "MultiEdit"]:
        sys.exit(0)  # Allow non-file tools to proceed

    # Extract file path from tool_input
    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)  # Allow if no file path

    # Extract content to check
    content = extract_content_from_input(tool_name, tool_input)

    # Check for ALL matching security patterns
    matched_rules = check_patterns(file_path, content)

    if not matched_rules:
        sys.exit(0)

    # Load existing warning counts for this session
    warning_counts = load_state(session_id)

    reminders_to_show = []
    for rule_name, reminder in matched_rules:
        warning_key = f"{file_path}-{rule_name}"
        count = warning_counts.get(warning_key, 0)

        # Show on first occurrence, then every REWARN_INTERVAL occurrences
        if count == 0 or (count > 0 and count % REWARN_INTERVAL == 0):
            reminders_to_show.append(reminder)

        warning_counts[warning_key] = count + 1

    save_state(session_id, warning_counts)

    if reminders_to_show:
        # Output all matching warnings to stderr and block execution
        print("\n\n".join(reminders_to_show), file=sys.stderr)
        sys.exit(2)  # Block tool execution

    # Allow tool to proceed (warnings already shown recently)
    sys.exit(0)


if __name__ == "__main__":
    main()
