#!/usr/bin/env python3
"""
verify_runbook.py — a tiny linter for AI-drafted runbooks.

It does NOT prove a runbook is correct (only a human + the real host can do that).
It catches a handful of the *mechanical* hallucinations and footguns an AI copilot
commonly emits, so the human reviewer can spend judgment on the subtle ones.

Usage:
    python3 verify_runbook.py code/ai-drafted-runbook.md

Exit code 0 = no automatic flags; 1 = flags found (a human must still review).
"""
import re
import sys

# (pattern, why it is dangerous / likely wrong). These are heuristics, not proofs.
DANGER = [
    (r"rm\s+-rf\s+/var/log/journal",
     "Deletes the systemd journal — destroys the evidence you need for the postmortem."),
    (r"rm\s+-rf\s+/(?!\w*tmp)",
     "Recursive force-delete near a root path. A human must execute deletions, not the AI."),
    (r"worker_connections\s+\d{6,}",
     "Absurd nginx worker_connections value — classic confident-but-wrong AI number."),
    (r"Restart=always-immediately",
     "Not a valid systemd Restart= value. Hallucinated directive."),
    (r"-server\.service",
     "Suspicious unit suffix — verify the real unit name with `systemctl cat` first."),
    (r"chmod\s+777",
     "World-writable permissions. Almost never the right fix."),
    (r"--follow|--since|-f\b",
     "A tailing/streaming command inside a runbook step will block automation."),
]


def main(path: str) -> int:
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as e:
        print(f"cannot read {path}: {e}", file=sys.stderr)
        return 2

    flags = 0
    for i, line in enumerate(text.splitlines(), 1):
        for pat, why in DANGER:
            if re.search(pat, line):
                print(f"  line {i:>3}: {why}\n           > {line.strip()}")
                flags += 1

    print(f"\n{flags} automatic flag(s). A human still owns the verdict on every line.")
    return 1 if flags else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
