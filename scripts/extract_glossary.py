"""
Build a canonical-names glossary from the wiki content.

Usage:
  python3 scripts/extract_glossary.py                          # full glossary
  python3 scripts/extract_glossary.py path/to/transcript.txt   # filtered to names that appear in the transcript

The glossary lists every entity file under content/02-People, 03-Locations,
04-Items-and-Loot, 05-Lore as a canonical name, plus aliases harvested from
[[Canonical|Alias]] wikilinks elsewhere in content/.

Designed to be embedded verbatim into rpg-summarizer chunk subagent prompts,
so they know which proper names exist in the campaign and how to spell them.
"""

import os
import re
import sys
from collections import defaultdict

ROOT_DIR = 'content'
ENTITY_DIRS = ['02-People', '03-Locations', '04-Items-and-Loot', '05-Lore']
WIKILINK_RE = re.compile(r'\[\[([^\]|]+)\|([^\]]+)\]\]')


def collect_canonical_names():
    """Walk entity directories and collect canonical names (filename without .md)."""
    result = {}  # category -> [name, ...]
    for entity_dir in ENTITY_DIRS:
        base = os.path.join(ROOT_DIR, entity_dir)
        if not os.path.isdir(base):
            continue
        names = []
        for dirpath, _, filenames in os.walk(base):
            for fn in filenames:
                if not fn.endswith('.md'):
                    continue
                if fn == 'index.md':
                    continue
                name = fn[:-3]
                names.append(name)
        result[entity_dir] = sorted(set(names))
    return result


def collect_aliases():
    """Scan all content markdown for [[Canonical|Alias]] patterns."""
    aliases = defaultdict(set)
    for dirpath, _, filenames in os.walk(ROOT_DIR):
        if '/assets' in dirpath:
            continue
        for fn in filenames:
            if not fn.endswith('.md'):
                continue
            path = os.path.join(dirpath, fn)
            try:
                with open(path, 'r', encoding='utf-8') as fh:
                    text = fh.read()
            except OSError:
                continue
            for match in WIKILINK_RE.finditer(text):
                canonical = match.group(1).strip()
                alias = match.group(2).strip()
                if alias and alias != canonical:
                    aliases[canonical].add(alias)
    return aliases


def load_transcript_terms(transcript_path):
    """Return the lowercase text of the transcript, for substring filtering."""
    with open(transcript_path, 'r', encoding='utf-8') as fh:
        return fh.read().lower()


def name_appears(name, aliases, transcript_text):
    """Check if a name or any of its aliases appears in the transcript text.

    Uses a 5-character prefix of the canonical first word, since Polish names
    are heavily inflected ("Sybolkorax" → "Sybolkoraxa", "Sybol Koraxa") and
    transcripts often split compound names with spaces.
    """
    if not transcript_text:
        return True
    candidates = [name] + list(aliases.get(name, []))
    for candidate in candidates:
        words = candidate.split()
        if not words:
            continue
        first = words[0].lower()
        if len(first) < 5:
            continue
        # 5-char prefix is selective enough to avoid most false positives
        # while catching inflected forms and split compound names.
        if first[:5] in transcript_text:
            return True
    return False


def format_glossary(by_category, aliases, transcript_text):
    out = []
    out.append("# Kanoniczna lista nazw (kampania Odyssey of the Dragonlords)")
    out.append("")
    out.append("Te nazwy są kanoniczne — jeśli w transkrypcji widzisz fonetycznie zbliżoną")
    out.append("formę, zastosuj wariant z tej listy. Pominij imiona graczy (Bartek, Maciek,")
    out.append("Hubert, Karol) i terminy mechaniczne.")
    out.append("")
    headers = {
        '02-People': '## Postacie / Frakcje',
        '03-Locations': '## Lokacje',
        '04-Items-and-Loot': '## Przedmioty',
        '05-Lore': '## Lore / koncepcje świata',
    }
    for category, label in headers.items():
        names = by_category.get(category, [])
        filtered = [n for n in names if name_appears(n, aliases, transcript_text)]
        if not filtered:
            continue
        out.append(label)
        for name in filtered:
            line = f"- **{name}**"
            if aliases.get(name):
                alias_list = ', '.join(sorted(aliases[name]))
                line += f" — aliasy: {alias_list}"
            out.append(line)
        out.append("")
    return '\n'.join(out).rstrip() + '\n'


def main():
    transcript_text = ''
    if len(sys.argv) > 1:
        transcript_text = load_transcript_terms(sys.argv[1])
    by_category = collect_canonical_names()
    aliases = collect_aliases()
    sys.stdout.write(format_glossary(by_category, aliases, transcript_text))


if __name__ == '__main__':
    main()
