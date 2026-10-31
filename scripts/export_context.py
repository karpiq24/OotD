"""
Export the campaign context rpgnotes needs into campaign/campaign_context.json.

Usage:
  uv run python scripts/export_context.py [--output PATH]

rpgnotes reads only this file (its CAMPAIGN_CONTEXT_FILE), never the wiki, so
this script is the one place that knows both the wiki layout and the contract.
Bump SCHEMA_VERSION (here and in rpgnotes' campaign.py) for any change that is
not just a new optional field.

What goes in:
  party                 PCs: content/02-People/Bohaterowie/*.md, name + the italic
                        line under the portrait ("Minotaur Barbarian, The Doomed One")
  entities              canonical names (file names) under 02-People, 03-Locations,
                        04-Items-and-Loot, 05-Lore + aliases from [[Name|Alias]] links
                        and from each page's frontmatter `aliases:`
  phonetic_corrections  campaign/phonetic_corrections.md
  learned_rules         campaign/learned_rules.md (HTML comments stripped)
  prose_rules           campaign/proza.md, only the sections for session summaries
                        (A, shared rules, and B, summaries; HTML comments stripped)
  hotwords              campaign/whisper_hotwords.txt
  campaign_context      content/Campaign_Context.md
  timeline_preamble,    content/Timeline.md, split into its `## Sesja` sections,
  timeline              each with the entities it links

The DM Corner (private) and assets are never read. The output is deterministic,
so re-running without wiki changes leaves the file untouched.
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

SCHEMA_VERSION = 1

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / 'content'
CAMPAIGN = ROOT / 'campaign'
DEFAULT_OUTPUT = CAMPAIGN / 'campaign_context.json'

PARTY_DIR = CONTENT / '02-People' / 'Bohaterowie'
ENTITY_DIRS = {
    'people': '02-People',
    'locations': '03-Locations',
    'items': '04-Items-and-Loot',
    'lore': '05-Lore',
}
SKIPPED_DIRS = {'assets', '99-DM-Corner'}

WIKILINK_ALIAS_RE = re.compile(r'\[\[([^\]|]+)\|([^\]]+)\]\]')
WIKILINK_RE = re.compile(r'\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]+))?\]\]')
HTML_COMMENT_RE = re.compile(r'<!--.*?-->', re.S)
FRONTMATTER_ALIASES_RE = re.compile(r'(?m)^aliases:[ \t]*(.*)\n((?:[ \t]+-.*\n?)*)')


def read(path):
    return path.read_text(encoding='utf-8') if path.is_file() else ''


def public_markdown():
    """Every wiki markdown file outside assets and the DM Corner."""
    for path in sorted(CONTENT.rglob('*.md')):
        if SKIPPED_DIRS.isdisjoint(path.relative_to(CONTENT).parts):
            yield path


def frontmatter_aliases(text):
    """The `aliases:` list of a page's frontmatter, block (`  - x`) or inline (`[x, y]`) form."""
    if not text.startswith('---'):
        return []
    match = FRONTMATTER_ALIASES_RE.search(text[3:text.find('\n---', 3)] + '\n')
    if not match:
        return []
    inline = match.group(1).strip()
    items = inline.strip('[]').split(',') if inline.startswith('[') else [
        line.strip()[1:] for line in match.group(2).splitlines() if line.strip()
    ]
    return [item.strip().strip('"\'') for item in items if item.strip()]


def collect_aliases():
    aliases = defaultdict(set)
    for path in public_markdown():
        text = read(path)
        for match in WIKILINK_ALIAS_RE.finditer(text):
            canonical, alias = match.group(1).strip(), match.group(2).strip()
            if alias and alias != canonical:
                aliases[canonical].add(alias)
        aliases[path.stem].update(a for a in frontmatter_aliases(text) if a != path.stem)
    return aliases


def collect_entities(aliases):
    entities = {}
    for category, directory in ENTITY_DIRS.items():
        names = sorted({
            path.stem
            for path in (CONTENT / directory).rglob('*.md')
            if path.name != 'index.md'
        })
        entities[category] = [
            {'name': name, 'aliases': sorted(aliases.get(name, ()))} for name in names
        ]
    return entities


def unlink(text):
    """`[[Target|Shown]]` → Shown, `[[Target]]` → Target."""
    return WIKILINK_RE.sub(lambda m: (m.group(2) or m.group(1)).strip(), text)


def collect_party():
    party = []
    for path in sorted(PARTY_DIR.glob('*.md')):
        if path.name == 'index.md':
            continue
        body = read(path).split('---', 2)[-1]
        description = ''
        for line in body.splitlines():
            line = line.strip()
            if line.startswith('_') and line.endswith('_') and len(line) > 2:
                description = unlink(line.strip('_')).replace('**', '').strip()
                break
        party.append({'name': path.stem, 'description': description})
    return party


def parse_hotwords(text):
    names = []
    for line in text.splitlines():
        line = line.split('#', 1)[0]
        names.extend(part.strip() for part in line.split(','))
    return [name for name in names if name]


def summary_prose_rules(text):
    """The parts of campaign/proza.md that apply to session summaries.

    Keeps the title and intro plus the `## A.` and `## B.` sections; the wiki
    (C) and book (D) sections and the sources list stay out of the prompts.
    """
    parts = re.split(r'(?m)^(?=## )', HTML_COMMENT_RE.sub('', text))
    keep = [parts[0]] + [p for p in parts[1:] if p.startswith(('## A.', '## B.'))]
    return '\n'.join(part.strip() + '\n' for part in keep if part.strip()).strip()


def split_timeline(text):
    parts = re.split(r'(?m)^(?=## )', text)
    sessions = []
    for section in parts[1:]:
        heading, _, rest = section.partition('\n')
        links = []
        for match in WIKILINK_RE.finditer(rest):
            target = match.group(1).strip()
            if target and not target.startswith('Sesja '):
                links.append(target)
        sessions.append({'heading': heading.strip(), 'text': rest.strip(), 'links': links})
    return parts[0].strip(), sessions


def build_context():
    preamble, timeline = split_timeline(read(CONTENT / 'Timeline.md'))
    return {
        'schema_version': SCHEMA_VERSION,
        'party': collect_party(),
        'entities': collect_entities(collect_aliases()),
        'phonetic_corrections': read(CAMPAIGN / 'phonetic_corrections.md').strip(),
        'learned_rules': HTML_COMMENT_RE.sub('', read(CAMPAIGN / 'learned_rules.md')).strip(),
        'prose_rules': summary_prose_rules(read(CAMPAIGN / 'proza.md')),
        'hotwords': parse_hotwords(read(CAMPAIGN / 'whisper_hotwords.txt')),
        'campaign_context': read(CONTENT / 'Campaign_Context.md').strip(),
        'timeline_preamble': preamble,
        'timeline': timeline,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[1])
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    context = build_context()
    text = json.dumps(context, ensure_ascii=False, indent=2) + '\n'
    if read(args.output) == text:
        print(f'{args.output.relative_to(ROOT) if args.output.is_relative_to(ROOT) else args.output}: unchanged')
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding='utf-8')
    counts = ', '.join(f'{len(v)} {k}' for k, v in context['entities'].items())
    print(
        f'Wrote {args.output}: {len(context["party"])} PCs, {counts}, '
        f'{len(context["hotwords"])} hotwords, {len(context["timeline"])} timeline sessions.'
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
