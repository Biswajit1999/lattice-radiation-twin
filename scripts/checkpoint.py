"""Validate, record, commit, push and verify one coherent milestone."""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GIT = shutil.which("git.exe") or shutil.which("git")


def run(*args: str) -> str:
    result = subprocess.run(args, cwd=ROOT, check=True, capture_output=True, text=True)
    print(result.stdout, end="")
    return result.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument("--next", required=True)
    args = parser.parse_args()
    ruff = shutil.which("ruff")
    if not GIT or not ruff:
        raise RuntimeError("Git and Ruff must be installed")
    run(ruff, "format", "--check", ".")
    run(ruff, "check", ".")
    tests = run(sys.executable, "-m", "pytest", "-q")
    previous = run(GIT, "rev-parse", "HEAD")
    remote = run(GIT, "ls-remote", "origin", "refs/heads/main").split()[0]
    state_path = ROOT / "PROJECT_STATE.md"
    state = state_path.read_text(encoding="utf-8-sig").splitlines()
    updates = {
        "- Current phase:": args.phase,
        "- Current tests and status:": tests.splitlines()[-1] + "; Ruff passed.",
        "- Last successful commit SHA:": previous,
        "- Last successful push:": f"origin/main verified at {remote} before this checkpoint.",
        "- Exact next action:": args.next,
    }
    for i, line in enumerate(state):
        for prefix, value in updates.items():
            if line.startswith(prefix):
                state[i] = f"{prefix} {value}"
    state_path.write_text("\n".join(state).rstrip() + "\n", encoding="utf-8")
    with (ROOT / "docs/BUILD_LEDGER.md").open("a", encoding="utf-8") as stream:
        stream.write(
            f"\n## {args.phase}\n\n{args.message}\n\nValidation: {tests.splitlines()[-1]}; "
            f"Ruff passed. Previous verified remote: `{remote}`. Next: {args.next}\n"
        )
    run(GIT, "add", ".")
    run(GIT, "diff", "--cached", "--check")
    run(GIT, "diff", "--cached", "--stat")
    run(GIT, "commit", "-m", args.message)
    current = run(GIT, "rev-parse", "HEAD")
    try:
        run(GIT, "push", "origin", "main")
        verified = run(GIT, "ls-remote", "origin", "refs/heads/main").split()[0]
        if verified != current:
            raise RuntimeError("Remote SHA differs from checkpoint")
    except Exception as error:
        with state_path.open("a", encoding="utf-8") as stream:
            stream.write(f"\nPush failed for {current}: {error}. Retry: `git push origin main`.\n")
        raise
    (ROOT / ".git/lattice-checkpoint.json").write_text(
        json.dumps({"sha": current, "remote_verified": True, "phase": args.phase}) + "\n"
    )


if __name__ == "__main__":
    main()
