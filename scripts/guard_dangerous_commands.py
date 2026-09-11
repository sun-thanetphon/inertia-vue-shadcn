#!/usr/bin/env python3
"""
scripts/guard_dangerous_commands.py
Autonomous Pre-Execution Security Guard for Antigravity IDE.
Intercepts shell/terminal commands and rejects destructive or high-risk operations.
"""

import sys
import os
import json
import re

# Comprehensive catalog of dangerous command patterns with rationale
DANGEROUS_PATTERNS = [
    # 1. Destructive File System Deletion
    {
        "pattern": r"(?i)\brm\s+-[a-z]*r[a-z]*f\b",
        "description": "Recursive forced deletion (rm -rf)",
    },
    {
        "pattern": r"(?i)\brm\s+-[a-z]*f[a-z]*r\b",
        "description": "Recursive forced deletion (rm -fr)",
    },
    {
        "pattern": r"(?i)\b(del|erase)\s+.*(/s|/q)",
        "description": "Silent recursive deletion on Windows (del /s /q)",
    },
    {
        "pattern": r"(?i)\b(rd|rmdir)\s+.*(/s|/q)",
        "description": "Silent directory removal on Windows (rd /s /q)",
    },
    {
        "pattern": r"(?i)\bRemove-Item\b.*(-Recurse|-r\b).*(-Force|-fo\b)",
        "description": "PowerShell forced recursive deletion (Remove-Item -Recurse -Force)",
    },
    {
        "pattern": r"(?i)\bRemove-Item\b.*(-Force|-fo\b).*(-Recurse|-r\b)",
        "description": "PowerShell forced recursive deletion (Remove-Item -Force -Recurse)",
    },
    {
        "pattern": r"(?i)[\s/\\'\"]\.git\b.*(rm|del|Remove-Item|rd|rmdir)",
        "description": "Attempting to delete or tamper with .git directory",
    },
    {
        "pattern": r"(?i)(rm|del|Remove-Item|rd|rmdir).*[\s/\\'\"]\.git\b",
        "description": "Attempting to delete or tamper with .git directory",
    },

    # 2. Destructive Git Commands
    {
        "pattern": r"(?i)\bgit\s+push\s+.*(--force|-f\b)",
        "description": "Force pushing to remote repository (git push --force)",
    },
    {
        "pattern": r"(?i)\bgit\s+reset\s+--hard\b",
        "description": "Hard reset discarding uncommitted changes (git reset --hard)",
    },
    {
        "pattern": r"(?i)\bgit\s+clean\s+-[a-z]*f",
        "description": "Forced cleanup of untracked files (git clean -fdx)",
    },
    {
        "pattern": r"(?i)\bgit\s+branch\s+(-D|--delete\s+--force)\s+(main|master|develop|production)\b",
        "description": "Forced deletion of critical branches",
    },

    # 3. Destructive Database Operations
    {
        "pattern": r"(?i)\bphp\s+artisan\s+(migrate:fresh|db:wipe)\b",
        "description": "Wiping database tables via Laravel Artisan (migrate:fresh / db:wipe)",
    },
    {
        "pattern": r"(?i)\b(DROP\s+DATABASE|DROP\s+SCHEMA)\b",
        "description": "Raw SQL DROP DATABASE / SCHEMA statement",
    },
    {
        "pattern": r"(?i)\bTRUNCATE\s+TABLE\b",
        "description": "Raw SQL TRUNCATE TABLE statement",
    },

    # 4. System Destruction, Sabotage & Denial of Service
    {
        "pattern": r"(?i)\bformat\s+[a-zA-Z]:",
        "description": "Formatting disk drive",
    },
    {
        "pattern": r"(?i)\b(shutdown|reboot)\b\s*(\/|\-)",
        "description": "System shutdown or reboot command",
    },
    {
        "pattern": r"(?i)\breg\s+(delete|add)\b",
        "description": "Windows Registry manipulation (reg delete / add)",
    },
    {
        "pattern": r"(?i)\b(taskkill|Stop-Process)\b.*(csrss|smss|svchost|lsass|explorer|wininit)",
        "description": "Killing critical operating system processes",
    },
    {
        "pattern": r":\(\)\s*\{\s*:\|:&\s*\}\s*;\s*:",
        "description": "Bash Fork bomb",
    },

    # 5. Blind Remote Code Execution & Remote Script Piping
    {
        "pattern": r"(?i)(curl|wget|Invoke-WebRequest|iwr)\b.*\|\s*(bash|sh|cmd|powershell|iex|Invoke-Expression)",
        "description": "Piping remote download directly into shell interpreter",
    },
    {
        "pattern": r"(?i)\b(iex|Invoke-Expression)\s*\(.*(New-Object\s+Net\.WebClient|DownloadString|iwr|Invoke-WebRequest)",
        "description": "PowerShell direct execution of remote web content (IEX download cradle)",
    },
    {
        "pattern": r"(?i)\bpowershell\b.*(-enc\b|-encodedcommand\b)",
        "description": "Obfuscated encoded PowerShell command execution",
    },
]


def extract_command_to_check() -> str:
    """
    Extracts the command string from all possible hook invocation vectors:
    1. Command line argument (sys.argv[1])
    2. Stdin payload (JSON or plain text)
    3. Environment variables (COMMAND_LINE, TOOL_ARGS, etc.)
    """
    # Vector 1: Command line arguments
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:])

    # Vector 2: Environment variables
    for env_var in ["COMMAND_LINE", "COMMAND", "TOOL_ARGS", "TOOL_ARGUMENTS"]:
        val = os.environ.get(env_var)
        if val:
            try:
                parsed = json.loads(val)
                if isinstance(parsed, dict) and "CommandLine" in parsed:
                    return parsed["CommandLine"]
                if isinstance(parsed, dict) and "command" in parsed:
                    return parsed["command"]
            except Exception:
                return val

    # Vector 3: Stdin payload
    try:
        if not sys.stdin.isatty():
            raw_input = sys.stdin.read().strip()
            if raw_input:
                try:
                    payload = json.loads(raw_input)
                    if isinstance(payload, dict):
                        # Antigravity tool call args schema
                        if "CommandLine" in payload:
                            return payload["CommandLine"]
                        if "tool_args" in payload and isinstance(payload["tool_args"], dict):
                            return payload["tool_args"].get("CommandLine", payload["tool_args"].get("command", ""))
                        if "arguments" in payload and isinstance(payload["arguments"], dict):
                            return payload["arguments"].get("CommandLine", payload["arguments"].get("command", ""))
                        if "command" in payload:
                            return payload["command"]
                except json.JSONDecodeError:
                    return raw_input
    except Exception:
        pass

    return ""


def validate_command(command: str) -> tuple[bool, str]:
    """
    Evaluates command against the catalog of dangerous patterns.
    Returns (is_safe: bool, reason: str).
    """
    if not command:
        # Empty command is considered non-threatening to file system
        return True, ""

    normalized_command = command.strip()

    for item in DANGEROUS_PATTERNS:
        match = re.search(item["pattern"], normalized_command)
        if match:
            return False, f"{item['description']} (Matched pattern: `{match.group(0)}`)"

    return True, ""


def main():
    command = extract_command_to_check()
    is_safe, reason = validate_command(command)

    if not is_safe:
        border = "=" * 70
        print(f"\n{border}", file=sys.stderr)
        print("🚨 [ANTIGRAVITY SECURITY GUARD] DANGEROUS COMMAND BLOCKED!", file=sys.stderr)
        print(f"{border}", file=sys.stderr)
        print(f"🚫 Blocked Command: {command}", file=sys.stderr)
        print(f"⚠️  Reason: {reason}", file=sys.stderr)
        print("🛡️  Action: Command execution aborted by project safety policy.", file=sys.stderr)
        print(f"{border}\n", file=sys.stderr)
        sys.exit(1)

    # Command is clean
    sys.exit(0)


if __name__ == "__main__":
    main()
