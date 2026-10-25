"""Checks over content/: broken wikilinks and alias collisions.

  uv run python scripts/check_wikilinks.py            (prints the problems and a summary)
"""
import collections, re
from pathlib import Path

ROOT = Path(__file__).absolute().parent.parent
CONTENT = ROOT / 'content'
LINK = re.compile(r'(?<!!)\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]')

def frontmatter(text):
    """Only the `aliases` key is needed: block list (`  - x`) or inline list (`[x, y]`)."""
    if not text.startswith('---'): return {}
    fm = text[3:text.find('\n---', 3)]
    m = re.search(r'(?m)^aliases:[ \t]*(.*)\n((?:[ \t]+-.*\n?)*)', fm + '\n')
    if not m: return {}
    inline = m.group(1).strip()
    if inline.startswith('['):
        items = inline.strip('[]').split(',')
    else:
        items = [l.strip()[1:] for l in m.group(2).splitlines() if l.strip()]
    return {'aliases': [i.strip().strip('"\'') for i in items if i.strip()]}

files = [p for p in CONTENT.rglob('*.md') if p.name != 'index.md']
stems = collections.defaultdict(list)          # stem -> paths
aliases = collections.defaultdict(list)        # alias -> paths
for p in files:
    stems[p.stem].append(p)
    al = frontmatter(p.read_text(encoding='utf-8')).get('aliases') or []
    for a in ([al] if isinstance(al, str) else al):
        if a: aliases[str(a).strip()].append(p)
# non-markdown assets and folders are valid link targets too (Quartz resolves folder index pages)
targets = set(stems) | set(aliases) | {d.name for d in CONTENT.rglob('*') if d.is_dir()}
lower = {t.lower(): t for t in targets}

broken = collections.defaultdict(list)          # target -> [file:line]
for p in files:
    for n, line in enumerate(p.read_text(encoding='utf-8').splitlines(), 1):
        for m in LINK.finditer(line):
            t = m.group(1).strip()
            if t.endswith('.md'): t = t[:-3]
            t = t.split('/')[-1]
            if t not in targets:
                broken[t].append(f'{p.relative_to(ROOT)}:{n}' + (f'  (case: {lower[t.lower()]})' if t.lower() in lower else ''))

collide = []
for a, ps in aliases.items():
    if a in stems and any(s not in ps for s in stems[a]):
        collide.append(f'ALIAS = FILE  "{a}"  alias in {[str(p.relative_to(CONTENT)) for p in ps]}  file {[str(p.relative_to(CONTENT)) for p in stems[a]]}')
    if len(set(ps)) > 1:
        collide.append(f'SHARED ALIAS  "{a}"  in {[str(p.relative_to(CONTENT)) for p in ps]}')
dupe_stems = [f'DUPLICATE STEM "{s}": {[str(p.relative_to(CONTENT)) for p in ps]}' for s, ps in stems.items() if len(ps) > 1]

for t, v in sorted(broken.items(), key=lambda kv: -len(kv[1])):
    print(f'{t}  ×{len(v)}' + ''.join(f'\n    {x}' for x in v))
for line in collide + dupe_stems:
    print(line)
print(f'{len(files)} files, {sum(map(len, broken.values()))} broken links to {len(broken)} targets, '
      f'{len(collide)} alias collisions, {len(dupe_stems)} duplicate stems')
