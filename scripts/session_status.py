"""Report which sessions are somewhere in the recap pipeline, and what comes next.

Claude runs it when the user mentions a session without naming it ("draft jest",
"co z obrazkami"). Prints nothing when every session is finished.

Stages, for each content/assets/sessions/{000}/ that holds an rpgnotes manifest.json:
  staged     package is here, no session note yet          -> import
  draft      note exists, no image prompts yet             -> waiting for the user's review, then finalize
  rendering  prompts exist, some images (.webp) missing    -> render_session_images.py
Sessions on origin that are not here yet are reported too (pull needed).

    uv run python scripts/session_status.py
"""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SESSIONS = ROOT / "content" / "assets" / "sessions"
NOTES = ROOT / "content" / "01-Sessions"


def git(*args: str) -> str:
    try:
        r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, timeout=15)
        return r.stdout if r.returncode == 0 else ""
    except (subprocess.TimeoutExpired, OSError):
        return ""


def stage(d: Path) -> str | None:
    num = d.name
    n = int(num)
    note = next(NOTES.glob(f"Sesja {n} - *.md"), None)
    if note is None:
        return f"session {n}: staged, no note yet -> import it now (skill import-session)"
    prompts = list(d.glob(f"{num}_*.txt"))
    snapshot = ROOT / "private" / "sessions" / num / "draft_pre_edit.md"
    if not prompts:
        snap = "" if snapshot.exists() else " (no pre-edit snapshot!)"
        return (f"session {n}: draft '{note.name}' waiting for the user's review{snap} -> apply the "
                f"user's corrections; when they approve, finalize (skill finalize-session-recap)")
    missing = [p.stem for p in prompts if not p.with_suffix(".webp").exists()]
    if missing:
        return (f"session {n}: finalized, {len(missing)}/{len(prompts)} images missing -> "
                f"run scripts/render_session_images.py {n} in the background")
    return None


def main() -> None:
    lines = [s for d in sorted(SESSIONS.iterdir())
             if d.is_dir() and d.name.isdigit() and (d / "manifest.json").exists()
             and (s := stage(d))]

    git("fetch", "-q", "origin")
    remote = {Path(p).name for p in git("ls-tree", "--name-only", "origin/HEAD",
                                         "content/assets/sessions/").split()}
    local = {d.name for d in SESSIONS.iterdir()}
    for num in sorted(remote - local):
        if num.isdigit():
            lines.append(f"session {int(num)}: staged on origin only -> git pull, then import it")
    behind = git("rev-list", "--count", "HEAD..origin/HEAD").strip()
    if behind and behind != "0" and not any("origin only" in s for s in lines):
        lines.append(f"repo is {behind} commit(s) behind origin -> git pull before working on sessions")

    if lines:
        print("Recap pipeline status (scripts/session_status.py):")
        print("\n".join(f"- {s}" for s in lines))


if __name__ == "__main__":
    main()
