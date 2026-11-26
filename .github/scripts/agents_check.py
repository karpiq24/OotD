#!/usr/bin/env python3
# Vendored copy of klima-kar/platform-ci@6cd1a0648b123a04284ea12b48a37bc1e665b902 actions/agents/agents_check.py (infra#228).
# Do not edit here: change platform-ci first, then copy again and update the SHA above. CI runs the base-branch copy.
"""Agent files check: context budget and layout (runbooks/agents-md.md and jakosc-projektow.md E in klima-kar/infra).

Budget: every instruction file (AGENTS.md, CLAUDE.md, CLAUDE.local.md, GEMINI.md) <= 10 000 bytes; every skill
(<dir>/skills/<name>/SKILL.md) has `name` and `description` in its frontmatter, description <= 200 characters.
Layout: the same rules as devbox/platform/agents-check in infra (AGENTS.md instead of CLAUDE.md/GEMINI.md, skills in
.agents/skills with the symlink .claude/skills -> ../.agents/skills, no legacy .agent/, .claude/commands, .gemini/skills,
.agents/rules).

"Who touches, fixes": with --base, a problem is an error only when the change (merge-base of BASE and HEAD -> working
tree) touches its file; other problems are notices. Without --base everything is a notice (report only).
Modes: observe (default; errors are reported as warnings, exit 0) and enforce (errors fail, exit 1).
--self-test runs the sensitivity test: synthetic repositories that must trip the check (exit 2 when they do not).

Standalone on purpose (Python 3.9+ stdlib, git): public repositories, which cannot call the private platform-ci, copy
this file and run the base-branch copy (see README.md in platform-ci). Read only; runs nothing from the repository.
Exit: 0 = ok or observe mode, 1 = errors in enforce mode, 2 = usage error or failed self-test.
"""
from __future__ import annotations

import argparse
import errno
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

INSTRUCTION_MAX_BYTES = 10_000
DESCRIPTION_MAX_CHARS = 200
INSTRUCTION_NAMES = ("AGENTS.md", "CLAUDE.md", "CLAUDE.local.md", "GEMINI.md")
SKIP_DIRS = {".git", "node_modules", ".venv", "venv"}


@dataclass
class Problem:
    path: str  # file the annotation points at
    message: str
    related: list[str] = field(default_factory=list)  # touching any of these (or below) makes it an error
    kind: str = "layout"  # layout | budget
    touched: bool = False


def git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(["git", "-C", str(repo), "-c", "core.quotePath=false", *args],
                            capture_output=True, text=True, check=False)
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


def list_files(repo: Path) -> list[str]:
    """Tracked + untracked non-ignored files; without git a walk that skips the usual dependency directories."""
    if subprocess.run(["git", "-C", str(repo), "rev-parse", "--is-inside-work-tree"],
                      capture_output=True, check=False).returncode == 0:
        out = git(repo, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
        return sorted({f for f in out.split("\0") if f and os.path.lexists(repo / f)})  # minus local deletions
    files = []
    for root, dirs, names in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not os.path.islink(os.path.join(root, d))]
        rel = os.path.relpath(root, repo)
        for name in names + [d for d in os.listdir(root) if os.path.islink(os.path.join(root, d))]:
            files.append(name if rel == "." else f"{rel}/{name}")
    return sorted(set(files))


def changed_files(repo: Path, base: str) -> set[str]:
    """Files changed since the merge-base of BASE and HEAD, working tree and untracked files included."""
    if subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{base}^{{commit}}"],
                      capture_output=True, check=False).returncode != 0:
        raise RuntimeError(f"base {base!r} is not a commit here - check out with fetch-depth: 0")
    merge_base = git(repo, "merge-base", base, "HEAD").strip()
    out = git(repo, "diff", "--name-only", "--no-renames", "-z", merge_base)
    out += git(repo, "ls-files", "-z", "--others", "--exclude-standard")
    return {f for f in out.split("\0") if f}


def with_slash(prefix: str) -> str:
    return f"{prefix}/" if prefix else ""


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Top-level scalar keys of a YAML frontmatter block (plain, quoted, folded and literal scalars)."""
    lines = text.lstrip("\ufeff").splitlines()
    if not lines or lines[0].rstrip() != "---":
        return None
    try:  # the closing marker starts the line (an indented "---" is part of a block scalar)
        end = next(i for i in range(1, len(lines)) if lines[i].rstrip() in ("---", "..."))
    except StopIteration:
        return None
    body, values, i = lines[1:end], {}, 0
    while i < len(body):
        match = re.match(r"""^["']?([A-Za-z0-9_-]+)["']?:(?:\s+(.*))?$""", body[i])
        i += 1
        if not match:
            continue
        key, raw = match.group(1), (match.group(2) or "").strip()
        if raw.startswith("#"):  # `key: # comment` - the value follows on the next lines
            raw = ""
        block = []
        while i < len(body) and (not body[i].strip() or body[i][:1] in (" ", "\t")):
            block.append(body[i])
            i += 1
        while block and not block[-1].strip():
            block.pop()
        if not raw:  # value starts on the next line: skip blank and comment lines, the first other line is the value
            while block and (not block[0].strip() or block[0].strip().startswith("#")):
                block.pop(0)
            if block:
                raw = block.pop(0).strip()
        if raw[:1] in ("|", ">"):  # block scalar; the header may carry a comment (`>- # text`)
            indent = min((len(b) - len(b.lstrip()) for b in block if b.strip()), default=0)
            parts = [b[indent:] for b in block]
            values[key] = ("\n" if raw[0] == "|" else " ").join(parts).strip()
        elif raw[:1] in ('"', "'"):
            values[key] = quoted_scalar(" ".join([raw] + [b.strip() for b in block]))
        else:
            values[key] = re.sub(r"\s+#.*$", "", " ".join([raw] + [b.strip() for b in block if b.strip()])).strip()
    return values


def quoted_scalar(joined: str) -> str:
    """Value of a single- or double-quoted scalar; text after the closing quote (a comment) is ignored."""
    quote, i, out = joined[0], 1, []
    while i < len(joined):
        ch = joined[i]
        if quote == "'" and ch == "'":
            if joined[i + 1:i + 2] == "'":
                out.append("'")
                i += 2
                continue
            break
        if quote == '"' and ch == "\\" and i + 1 < len(joined):
            out.append(joined[i:i + 2])
            i += 2
            continue
        if quote == '"' and ch == '"':
            break
        out.append(ch)
        i += 1
    value = "".join(out)
    if quote == '"':
        try:  # YAML double-quoted escapes are a superset of JSON's; fall back to the raw text
            value = json.loads(f'"{value}"')
        except ValueError:
            value = value.replace('\\"', '"')
    return value


def check_budget(repo: Path, files: list[str], problems: list[Problem]) -> None:
    root = repo.resolve()
    for rel in files:
        path = repo / rel
        name = rel.rsplit("/", 1)[-1]
        parts = rel.split("/")
        is_skill = name == "SKILL.md" and len(parts) >= 3 and parts[-3] == "skills"
        related = [rel]
        if len(parts) >= 2 and parts[-2] == "skills" and path.is_symlink() and path.is_dir():
            # a symlinked skill directory: tools read <link>/SKILL.md - check the target's SKILL.md
            is_skill, related = True, [rel]
            rel, path, name, parts = f"{rel}/SKILL.md", path / "SKILL.md", "SKILL.md", [*parts, "SKILL.md"]
        if name not in INSTRUCTION_NAMES and not is_skill:
            continue
        if path.is_symlink() or path.parent.is_symlink():  # tools follow the link - check what it points to
            try:
                os.stat(path)
            except OSError as exc:
                if exc.errno == errno.ELOOP:
                    problems.append(Problem(rel, f"{rel}: a symlink loop", related, "budget"))
                    continue
            try:
                target = path.resolve(strict=False)
                related.append(target.relative_to(root).as_posix())
            except (OSError, RuntimeError):
                problems.append(Problem(rel, f"{rel}: a symlink loop", related, "budget"))
                continue
            except ValueError:
                problems.append(Problem(rel, f"{rel}: a symlink outside the repository - keep the file in the "
                                        "repository", related, "budget"))
                continue
        if not path.is_file():
            if path.is_symlink():
                problems.append(Problem(rel, f"{rel}: a dangling symlink", related, "budget"))
            continue
        if name in INSTRUCTION_NAMES:
            size = path.stat().st_size
            if size > INSTRUCTION_MAX_BYTES:
                problems.append(Problem(rel, f"{rel}: {size} B > {INSTRUCTION_MAX_BYTES} B budget - move procedures "
                                        "to skills and details to docs", related, "budget"))
        if is_skill:
            meta = parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
            if meta is None:
                problems.append(Problem(rel, f"{rel}: no YAML frontmatter (name, description)", related, "budget"))
                continue
            for key in ("name", "description"):
                if not meta.get(key, "").strip():
                    problems.append(Problem(rel, f"{rel}: no `{key}` in the frontmatter", related, "budget"))
            description = meta.get("description", "")
            if len(description) > DESCRIPTION_MAX_CHARS:
                problems.append(Problem(rel, f"{rel}: description has {len(description)} characters > "
                                        f"{DESCRIPTION_MAX_CHARS} - it is loaded into every session", related, "budget"))


def check_layout(repo: Path, files: list[str], problems: list[Problem]) -> bool:
    """Port of devbox/platform/agents-check (infra). Returns whether the repository has any agent files."""
    has_root_agents = False
    agent_files: list[str] = []  # a change to any of them makes a missing root AGENTS.md its problem
    found: dict[str, list[str]] = {}
    for rel in files:
        name = rel.rsplit("/", 1)[-1]
        if rel == "AGENTS.md":
            has_root_agents = True
        if (name == "AGENTS.md" or rel == ".mcp.json" or name in ("CLAUDE.md", "CLAUDE.local.md", "GEMINI.md")
                or re.search(r"(^|/)(\.(agents|claude|gemini|codex|agent)|_agents?)(/|$)", rel)):
            agent_files.append(rel)
        if name in ("CLAUDE.md", "CLAUDE.local.md", "GEMINI.md"):
            path = repo / rel
            if path.is_symlink():
                msg = f"{rel} - a symlink; remove it (Claude Code reads AGENTS.md by itself when there is no CLAUDE.md)"
            elif path.is_file() and "".join(path.read_text(errors="replace").split()) == "@AGENTS.md":
                msg = f"{rel} is only an @AGENTS.md adapter - remove it (it disables nested AGENTS.md in Claude Code)"
            else:
                msg = f"{rel} - move the content to AGENTS.md next to it (Claude-only instructions: .claude/rules/*.md)"
            problems.append(Problem(rel, msg, [rel]))
        wrapped = f"/{rel}/"
        for pattern in (".claude/skills", ".claude/commands", ".agent", ".agents/skills", ".gemini/skills",
                        ".agents/rules", "_agent", "_agents"):
            marker = f"/{pattern}/"
            if marker in wrapped:
                prefix = wrapped[:wrapped.index(marker)].strip("/")
                if prefix not in found.setdefault(pattern, []):
                    found[pattern].append(prefix)

    for prefix in found.get(".claude/skills", []):
        link = f"{with_slash(prefix)}.claude/skills"
        if not (repo / link).is_symlink():
            problems.append(Problem(link, f"{link}/ is a directory - move the skills to {with_slash(prefix)}.agents/skills/"
                                    " and symlink .claude/skills -> ../.agents/skills", [link]))

    def check_link(prefix: str) -> None:
        link = f"{with_slash(prefix)}.claude/skills"
        target = f"{with_slash(prefix)}.agents/skills"
        path = repo / link
        if path.is_symlink():
            if os.readlink(path) != "../.agents/skills":
                problems.append(Problem(link, f"{link} points to {os.readlink(path)}, should point to ../.agents/skills",
                                        [link, target]))
            if not path.is_dir():
                problems.append(Problem(link, f"{link} is a dangling symlink (no {target})", [link, target]))
        else:
            problems.append(Problem(link, f"no symlink {link} -> ../.agents/skills (Claude Code does not read "
                                    ".agents/skills)", [link, target]))

    link_prefixes = list(found.get(".agents/skills", []))
    link_prefixes += [p for p in found.get(".claude/skills", [])
                      if p not in link_prefixes and (repo / f"{with_slash(p)}.claude/skills").is_symlink()]
    for prefix in link_prefixes:
        check_link(prefix)
    for pattern in (".agent", "_agent", "_agents"):
        for prefix in found.get(pattern, []):
            d = f"{with_slash(prefix)}{pattern}"
            problems.append(Problem(d, f"legacy directory {d}/ - rename to {with_slash(prefix)}.agents/ (fix the paths "
                                    "in hooks and AGENTS.md)", [d]))
    for prefix in found.get(".claude/commands", []):
        d = f"{with_slash(prefix)}.claude/commands"
        problems.append(Problem(d, f"{d}/ - move the commands as skills to {with_slash(prefix)}.agents/skills/", [d]))
    for prefix in found.get(".gemini/skills", []):
        d = f"{with_slash(prefix)}.gemini/skills"
        problems.append(Problem(d, f"{d}/ - move to {with_slash(prefix)}.agents/skills/", [d]))
    for prefix in found.get(".agents/rules", []):
        d = f"{with_slash(prefix)}.agents/rules"
        problems.append(Problem(d, f"{d}/ - only Antigravity reads it; move the content to AGENTS.md", [d]))
    if agent_files and not has_root_agents:
        problems.insert(0, Problem("AGENTS.md", "no AGENTS.md in the root", ["AGENTS.md", *agent_files]))
    return bool(agent_files)


def is_touched(problem: Problem, changed: set[str]) -> bool:
    return any(c == r or c.startswith(r + "/") for r in problem.related for c in changed)


def escape(value: str, prop: bool = False) -> str:
    value = value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    return value.replace(":", "%3A").replace(",", "%2C") if prop else value


def run(repo: Path, base: str | None, mode: str, github: bool, out=sys.stdout) -> int:
    files = list_files(repo)
    problems: list[Problem] = []
    has_agent_files = check_layout(repo, files, problems)
    check_budget(repo, files, problems)
    changed: set[str] = set()
    if base:
        try:
            changed = changed_files(repo, base)
        except RuntimeError as exc:
            if mode == "enforce":
                raise
            text = f"{exc} - report only (observe mode)"
            print(f"::warning title=agents::{escape(text)}" if github else f"warning: {text}", file=out)
            base = None
    for p in problems:
        p.touched = bool(base) and is_touched(p, changed)
    errors = [p for p in problems if p.touched]
    notices = [p for p in problems if not p.touched]

    def emit(level: str, p: Problem, suffix: str = "") -> None:
        if github:
            print(f"::{level} file={escape(p.path, True)},title=agents::{escape(p.message + suffix)}", file=out)
        else:
            print(f"{level}: {p.message}{suffix}", file=out)

    for p in errors:
        if mode == "enforce":
            emit("error", p, " (this change touches it)")
        else:
            emit("warning", p, " (this change touches it; observe mode - would fail in enforce mode)")
    for p in notices:
        emit("notice", p, " (not touched by this change - fix when you edit it)" if base else "")
    if not has_agent_files:
        print("agents: no agent files - the project's first PR adds AGENTS.md (no CLAUDE.md)", file=out)
    status = "ok" if not problems else f"{len(errors)} touched by this change, {len(notices)} other"
    print(f"agents: {status} (mode {mode}, base {base or 'none - report only'})", file=out)

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if github and summary:
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write("### Pliki agentów (budżet kontekstu i układ)\n\n")  # i18n-pl
            if not problems:
                fh.write("Bez uwag.\n\n")  # i18n-pl
            else:
                fh.write(f"Tryb `{mode}`. Błąd tylko dla plików zmienionych w tym PR, reszta to uwagi "  # i18n-pl
                         "(kto dotyka, ten naprawia).\n\n| | Problem |\n|---|---|\n")  # i18n-pl
                for p in errors + notices:
                    icon = (":x:" if mode == "enforce" else ":warning:") if p.touched else ":information_source:"
                    shown = p.message.replace("|", "/").replace("\r", " ").replace("\n", " ")
                    fh.write(f"| {icon} | {shown} |\n")
                fh.write("\n")
    return 1 if errors and mode == "enforce" else 0


def self_test() -> int:
    """Sensitivity test: each case must give the expected exit code and output fragment."""
    import io

    env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}

    def sh(repo: Path, *args: str) -> None:
        subprocess.run(["git", "-C", str(repo), *args], env=env, check=True, capture_output=True)

    def write(repo: Path, rel: str, text: str) -> None:
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text(text, encoding="utf-8")

    def skill(description: str) -> str:
        return f"---\nname: s\ndescription: {description}\n---\nbody\n"

    big, ok_size = "x" * (INSTRUCTION_MAX_BYTES + 1), "x" * INSTRUCTION_MAX_BYTES
    long_desc, ok_desc = "d" * (DESCRIPTION_MAX_CHARS + 1), "ż" * DESCRIPTION_MAX_CHARS  # characters, not bytes
    base_files = {"AGENTS.md": "# a\n", ".agents/skills/s/SKILL.md": skill("short")}
    # (name, files in the base commit, files changed in the PR, expected exit in enforce mode, output fragment)
    cases = [
        ("oversized AGENTS.md in the change", base_files, {"AGENTS.md": big}, 1, "AGENTS.md: 10001 B"),
        ("AGENTS.md at the limit", base_files, {"AGENTS.md": ok_size}, 0, "agents: ok"),
        ("oversized AGENTS.md not touched", {**base_files, "AGENTS.md": big}, {"README.md": "x"}, 0, "notice: AGENTS.md"),
        ("long skill description", base_files, {".agents/skills/s/SKILL.md": skill(long_desc)}, 1, "201 characters"),
        ("description at the limit", base_files, {".agents/skills/s/SKILL.md": skill(ok_desc)}, 0, "agents: ok"),
        ("folded description", base_files,
         {".agents/skills/s/SKILL.md": "---\nname: s\ndescription: >-\n  " + "w " * 101 + "\n---\n"}, 1, "characters >"),
        ("skill without description", base_files, {".agents/skills/s/SKILL.md": "---\nname: s\n---\n"}, 1,
         "no `description`"),
        ("CLAUDE.md added", base_files, {"CLAUDE.md": "# c\n"}, 1, "CLAUDE.md - move the content"),
        ("oversized nested CLAUDE.md", base_files, {"pkg/CLAUDE.md": big}, 1, "pkg/CLAUDE.md: 10001 B"),
    ]
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        for n, (name, base_state, change, expected, fragment) in enumerate(cases):
            repo = Path(tmp) / str(n)
            repo.mkdir()
            sh(repo, "init", "-q", "-b", "main")
            for rel, text in base_state.items():
                write(repo, rel, text)
            (repo / ".claude").mkdir(exist_ok=True)
            os.symlink("../.agents/skills", repo / ".claude/skills")
            sh(repo, "add", "-A")
            sh(repo, "commit", "-q", "-m", "base")
            sh(repo, "switch", "-q", "-c", "change")
            for rel, text in change.items():
                write(repo, rel, text)
            sh(repo, "add", "-A")
            sh(repo, "commit", "-q", "-m", "change")
            buf = io.StringIO()
            code = run(repo, "main", "enforce", False, buf)
            output = buf.getvalue()
            if code != expected or fragment not in output:
                failures += 1
                print(f"FAIL {name}: exit {code} (expected {expected}), fragment {fragment!r}\n{output}")
            else:
                print(f"ok   {name}")
    if failures:
        print(f"agents self-test: {failures} case(s) FAILED - the check is not sensitive, do not trust its result")
        return 2
    print("agents self-test: OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("repo", nargs="?", default=".", help="repository directory (default: .)")
    parser.add_argument("--base", help="base commit/branch of the change (PR base); without it: report only")
    parser.add_argument("--mode", choices=("observe", "enforce"), default="observe")
    parser.add_argument("--github", action="store_true", help="GitHub annotations and $GITHUB_STEP_SUMMARY")
    parser.add_argument("--self-test", action="store_true", help="sensitivity test on synthetic repositories")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    repo = Path(args.repo)
    if not repo.is_dir():
        parser.error(f"not a directory: {repo}")
    try:
        return run(repo, args.base or None, args.mode, args.github)
    except RuntimeError as exc:
        print(f"agents: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
