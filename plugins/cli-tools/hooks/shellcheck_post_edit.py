#!/usr/bin/env python3
"""
PostToolUse hook: advisory shellcheck on shell files.

Runs shellcheck after Edit/Write on .sh/.bash/.zsh/.bats files.
Advisory only — always exits 0, never blocks the tool.
Findings are printed to stderr for visibility.
"""

import json
import os
import shutil
import subprocess
import sys


SHELL_EXTENSIONS = (".sh", ".bash", ".zsh", ".bats")


def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")
    if tool_name not in ("Edit", "Write"):
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)

    # Check file extension
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in SHELL_EXTENSIONS:
        sys.exit(0)

    # Check shellcheck is installed
    if not shutil.which("shellcheck"):
        sys.exit(0)

    # Check file exists (Write may have just created it)
    if not os.path.isfile(file_path):
        sys.exit(0)

    try:
        result = subprocess.run(
            ["shellcheck", "-f", "gcc", file_path],
            capture_output=True,
            text=True,
            timeout=8,
        )
        if result.stdout.strip():
            print(
                f"shellcheck advisory for {os.path.basename(file_path)}:\n"
                f"{result.stdout.strip()}",
                file=sys.stderr,
            )
    except (subprocess.TimeoutExpired, OSError):
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
