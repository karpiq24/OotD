"""Render a session's image prompts with agy (Nano Banana) and save them as webp.

For every prompt file content/assets/sessions/{000}/{000}_*.txt that has no
matching .webp yet, runs agy once in its own work folder (.cache/render/{000}/{stem}/),
checks that image.png really exists, and converts it to
content/assets/sessions/{000}/{stem}.webp (quality 80, the size the wiki uses).

One image at a time. A failed image is retried once, then skipped. Stops at agy's
quota limit (exit code 2); rerunning later picks up only what is still missing.

    uv run python scripts/render_session_images.py 85
"""

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
MIN_BYTES = 20_000
QUOTA_RE = re.compile(r"quota|resource.?exhausted|rate.?limit|\b429\b|daily limit|too many requests", re.I)
MSG = (
    "Read prompt.txt in the current directory. Use your image generation tool (generate_image) "
    "to create one landscape (16:9) image exactly as described in prompt.txt. Save the final image "
    "as image.png in the current working directory. If generate_image is not in your own tool list, "
    "hand the job to your image-generator subagent and wait for it; never stop without an image. "
    "Reply with the absolute path of the saved file."
)


def log(line: str) -> None:
    print(f"{time.strftime('%H:%M:%S')} {line}", flush=True)


def render_one(prompt: Path, work: Path, timeout: int) -> str:
    """Returns OK, MISSING or QUOTA."""
    work.mkdir(parents=True, exist_ok=True)
    (work / "prompt.txt").write_text(prompt.read_text(encoding="utf-8"), encoding="utf-8")
    png = work / "image.png"
    png.unlink(missing_ok=True)
    out, err = work / "agy_out.md", work / "agy_err.log"
    try:
        with open(out, "w") as fo, open(err, "w") as fe:
            subprocess.run(
                ["agy", "--mode", "accept-edits", "-p", MSG],
                cwd=work, stdin=subprocess.DEVNULL, stdout=fo, stderr=fe, timeout=timeout,
            )
    except subprocess.TimeoutExpired:
        log(f"TIMEOUT {prompt.stem} after {timeout}s")
    if png.exists() and png.stat().st_size > MIN_BYTES:
        with Image.open(png) as img:
            img.save(prompt.with_suffix(".webp"), "WEBP", quality=80)
        return "OK"
    png.unlink(missing_ok=True)
    text = out.read_text(errors="ignore") + err.read_text(errors="ignore")
    return "QUOTA" if QUOTA_RE.search(text) else "MISSING"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("session", type=int)
    ap.add_argument("--timeout", type=int, default=900, help="seconds per agy run")
    args = ap.parse_args()

    num = f"{args.session:03d}"
    assets = ROOT / "content" / "assets" / "sessions" / num
    prompts = sorted(p for p in assets.glob(f"{num}_*.txt"))
    if not prompts:
        log(f"no prompt files {num}_*.txt in {assets}")
        return 1
    todo = [p for p in prompts if not p.with_suffix(".webp").exists()]
    log(f"session {num}: {len(prompts)} prompts, {len(todo)} to render")

    ok, failed = 0, []
    for i, prompt in enumerate(todo, 1):
        work = ROOT / ".cache" / "render" / num / prompt.stem
        for attempt in (1, 2):
            status = render_one(prompt, work, args.timeout)
            if status == "QUOTA":
                log(f"QUOTA {prompt.stem}: stopping, {ok} rendered, {len(todo) - i + 1} left")
                return 2
            if status == "OK":
                break
            log(f"MISSING {prompt.stem} (attempt {attempt})")
        if status == "OK":
            ok += 1
            log(f"OK {prompt.stem} [{i}/{len(todo)}]")
        else:
            failed.append(prompt.stem)

    log(f"DONE {ok} rendered, {len(failed)} failed" + (f": {', '.join(failed)}" if failed else ""))
    return 0 if not failed else 3


if __name__ == "__main__":
    sys.exit(main())
