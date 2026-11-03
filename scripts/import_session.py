"""
Import a session package from rpgnotes' outbox and assemble the session note.

Usage:
  uv run python scripts/import_session.py <N> [--outbox PATH] [--force]
  uv run python scripts/import_session.py <N> --stage [--push]
  uv run python scripts/import_session.py <N> --snapshot

rpgnotes writes one folder per session, `<outbox>/<NNN>/`, with a manifest.json
listing its files. All of them, and the manifest, are copied to
content/assets/sessions/<NNN>/: the `publish` files are listed under Metadane on
the site, the `working` ones (draft0.md, details.json, validation_report.json)
and the manifest are kept off it by quartz.config.ts's ignorePatterns. The note
content/01-Sessions/Sesja <N> - <Title>.md is then filled from
templates/Session.md with draft0.md, details.json and quotes.json, no model
involved. Finally `.imported` is written into the outbox folder, so rpgnotes'
status screen knows the wiki has it.

--stage copies the package and stops: no session note, so nothing new appears
on the site. With --push it also commits that asset folder ("<N> init") and
pushes it. rpgnotes' ./run.sh does this as soon as a package is ready; on any
workstation, /import-session then builds the note from the staged folder when
the outbox is not there.

The outbox defaults to ../rpgnotes/output next to this repo; set RPGNOTES_OUTBOX
or pass --outbox to use another one.

--snapshot copies the note, as it stands now, to private/sessions/<NNN>/
draft_pre_edit.md: the baseline /harvest-corrections diffs your edits against.
Run it after the yes/no check, before you edit the note.
"""

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SCHEMA_VERSION = 1

ROOT = Path(__file__).resolve().parent.parent
SESSIONS_DIR = ROOT / 'content' / '01-Sessions'
ASSETS_DIR = ROOT / 'content' / 'assets' / 'sessions'
PRIVATE_SESSIONS_DIR = ROOT / 'private' / 'sessions'
TEMPLATE = ROOT / 'templates' / 'Session.md'
DEFAULT_OUTBOX = ROOT.parent / 'rpgnotes' / 'output'
IMPORTED_MARKER = '.imported'


def fail(message):
    print(f'✗ {message}', file=sys.stderr)
    sys.exit(1)


def existing_notes(number):
    return sorted(SESSIONS_DIR.glob(f'Sesja {number} - *.md'))


def package_dir(number, outbox):
    """The rpgnotes outbox folder, else the copy staged in content/assets/sessions/."""
    padded = f'{number:03d}'
    for candidate in (outbox / padded, ASSETS_DIR / padded):
        if (candidate / 'manifest.json').is_file():
            return candidate
    fail(
        f'No session {number} in the rpgnotes outbox ({outbox / padded}) nor staged in '
        f'{(ASSETS_DIR / padded).relative_to(ROOT)}.'
    )


def copy_package(number, package, manifest):
    """Copy every file the manifest lists, and the manifest, into the session's asset folder."""
    target = ASSETS_DIR / f'{number:03d}'
    target.mkdir(parents=True, exist_ok=True)
    for name, kind in manifest['files'].items():
        if kind not in ('publish', 'working'):
            fail(f'manifest.json lists {name} as {kind!r}; expected publish or working.')
        source = package / name
        if not source.is_file():
            fail(f'manifest.json lists {name}, but {source} does not exist.')
        if source.resolve() != (target / name).resolve():
            shutil.copy2(source, target / name)
    if package.resolve() != target.resolve():
        shutil.copy2(package / 'manifest.json', target / 'manifest.json')
        imported_at = dt.datetime.now().isoformat(timespec='seconds')
        (package / IMPORTED_MARKER).write_text(f'{imported_at}\n', encoding='utf-8')
    return target


def git(*args):
    return subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True, text=True)


def push_assets(number, folder):
    """Commit only the session's asset folder ("<N> init"), pull, push. Other changes stay."""
    rel = str(folder.relative_to(ROOT))
    git('add', '--all', '--', rel)
    if git('diff', '--cached', '--quiet', '--', rel).returncode == 0:
        print(f'  nothing new to commit in {rel}')
        return True
    steps = (
        ('commit', ['commit', '-m', f'{number} init', '--', rel]),
        ('pull', ['pull', '--rebase', '--autostash']),
        ('push', ['push']),
    )
    for name, args in steps:
        result = git(*args)
        if result.returncode:
            print(f'✗ git {name} failed: {(result.stderr or result.stdout).strip()}', file=sys.stderr)
            if name != 'commit':
                print('  The commit stays local: push it by hand.', file=sys.stderr)
            return False
    print(f'  committed "{number} init" and pushed')
    return True


def load_manifest(package):
    path = package / 'manifest.json'
    if not path.is_file():
        fail(f'No manifest.json in {package}. Run rpgnotes for this session first.')
    manifest = json.loads(path.read_text(encoding='utf-8'))
    version = manifest.get('schema_version')
    if version != SCHEMA_VERSION:
        fail(
            f'{path} has schema version {version}, this script reads version '
            f'{SCHEMA_VERSION}. Update one of the two repos.'
        )
    if not manifest.get('complete'):
        fail(
            f'The package in {package} is incomplete (no draft0.md, details.json or '
            'quotes.json yet). Finish the rpgnotes run first.'
        )
    return manifest


def bullets(items):
    return '\n'.join(f'* {item}' for item in items)


def fill_template(number, date, title, narrative, details, quotes):
    text = TEMPLATE.read_text(encoding='utf-8')
    escaped_title = title.replace('"', '\\"')
    replacements = [
        ('"Sesja {number}: {Title}"', f'"Sesja {number}: {escaped_title}"'),
        ('{Date}', date),
        ('{Narrative Summary}', narrative.strip()),
        ('* {Event 1}', bullets(details['events'])),
    ]
    for placeholder, value in replacements:
        if placeholder not in text:
            fail(f'{TEMPLATE} has no {placeholder!r} placeholder; update this script with it.')
        text = text.replace(placeholder, value)
    return text


def note_title(details):
    """details.json's title, minus a "Sesja N:" prefix the model sometimes adds."""
    title = details['title'].strip()
    if title.startswith('Sesja ') and ':' in title:
        title = title.split(':', 1)[1].strip()
    return title


def stage(number, outbox, push):
    package = package_dir(number, outbox)
    manifest = load_manifest(package)
    if manifest.get('session_number') != number:
        fail(f'{package}/manifest.json is for session {manifest.get("session_number")}.')
    folder = copy_package(number, package, manifest)
    print(f'Staged session {number}: {len(manifest["files"])} file(s) → {folder.relative_to(ROOT)}/ (no note yet)')
    if push and not push_assets(number, folder):
        sys.exit(1)


def import_session(number, outbox, force):
    package = package_dir(number, outbox)
    manifest = load_manifest(package)
    if manifest.get('session_number') != number:
        fail(f'{package}/manifest.json is for session {manifest.get("session_number")}.')

    notes = existing_notes(number)
    if notes and not force:
        fail(
            f'{notes[0].relative_to(ROOT)} already exists. Pass --force to replace it '
            '(your edits to it are lost).'
        )

    folder = copy_package(number, package, manifest)

    details = json.loads((package / 'details.json').read_text(encoding='utf-8'))
    quotes = json.loads((package / 'quotes.json').read_text(encoding='utf-8'))['quotes']
    narrative = (package / 'draft0.md').read_text(encoding='utf-8')
    date = manifest.get('session_date')
    date = dt.date.fromisoformat(date).strftime('%d.%m.%Y') if date else '??.??.????'

    title = note_title(details)
    note = SESSIONS_DIR / f'Sesja {number} - {title.replace("/", "-")}.md'
    for old in notes:
        old.unlink()
    note.write_text(fill_template(number, date, title, narrative, details, quotes), encoding='utf-8')

    report_file = package / 'validation_report.json'
    findings = []
    if report_file.is_file():
        findings = json.loads(report_file.read_text(encoding='utf-8')).get('findings', [])
    print(f'Imported session {number} from {package}:')
    print(f'  {len(manifest["files"])} file(s) → {folder.relative_to(ROOT)}/')
    print(f'  note → {note.relative_to(ROOT)}')
    print(f'  {len(findings)} open validation finding(s) in {folder.relative_to(ROOT)}/validation_report.json')


def snapshot(number):
    notes = existing_notes(number)
    if len(notes) != 1:
        fail(f'Expected one note for session {number} in {SESSIONS_DIR.relative_to(ROOT)}, found {len(notes)}.')
    target = PRIVATE_SESSIONS_DIR / f'{number:03d}' / 'draft_pre_edit.md'
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(notes[0], target)
    print(f'Saved {notes[0].relative_to(ROOT)} → {target.relative_to(ROOT)}')


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[1])
    parser.add_argument('session_number', type=int)
    parser.add_argument('--outbox', type=Path, default=Path(os.environ.get('RPGNOTES_OUTBOX', DEFAULT_OUTBOX)))
    parser.add_argument('--force', action='store_true', help='replace an existing note for this session')
    parser.add_argument('--snapshot', action='store_true', help='save the note as draft_pre_edit.md and exit')
    parser.add_argument('--stage', action='store_true', help='copy the package into the asset folder only, no note')
    parser.add_argument('--push', action='store_true', help='with --stage: commit the asset folder and push')
    args = parser.parse_args()
    if args.push and not args.stage:
        parser.error('--push goes with --stage')
    if args.snapshot:
        snapshot(args.session_number)
    elif args.stage:
        stage(args.session_number, args.outbox.resolve(), args.push)
    else:
        import_session(args.session_number, args.outbox.resolve(), args.force)
    return 0


if __name__ == '__main__':
    sys.exit(main())
