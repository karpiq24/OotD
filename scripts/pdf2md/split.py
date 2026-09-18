"""TOC-driven splitting of the element stream into chapter dirs / section files."""
import os
import re
import unicodedata

ROMAN = "I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII|XIII|XIV|XV"
PREFIX = re.compile(
    r"^(?:chapter\s+\d+|part\s+(?:one|two|three|four|%s)|appendix\s+[a-z]|preface|introduction)\s*[:—-]?\s*"
    % ROMAN.lower(), re.I)


def norm(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("’", "'").replace("‘", "'").replace("—", " ").replace("–", " ")
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def slug(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("’", "").replace("'", "").replace("&", "and")
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")
    return re.sub(r"_+", "_", s)


def title_case(s):
    """TOC titles are already cased; chapter headings come in as ALL CAPS."""
    if s.isupper():
        small = {"of", "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "by"}
        words = s.title().split()
        return " ".join(w if i == 0 or w.lower() not in small else w.lower()
                        for i, w in enumerate(words))
    return s


def dirname_for(index, title):
    m = re.match(r"^Appendix\s+([A-Z])\b\s*[:—-]?\s*(.*)$", title)
    if m:
        return "Appendix-%s_%s" % (m.group(1), slug(m.group(2)) or "Contents")
    body = PREFIX.sub("", title).strip() or title
    return "%02d-%s" % (index, slug(body))


def find_heading(els, title, page, levels=(1, 2, 3, 4), window=2):
    want = norm(PREFIX.sub("", title))
    best = None
    for i, e in enumerate(els):
        if e["type"] != "h" or e["level"] not in levels:
            continue
        if abs(e["page"] - page) > window:
            continue
        got = norm(e["text"])
        if not got:
            continue
        if got == want:
            score = (0, abs(e["page"] - page), e["level"])
        elif got.startswith(want) or want.startswith(got):
            score = (1, abs(e["page"] - page), e["level"])
        else:
            continue
        if best is None or score < best[0]:
            best = (score, i)
    return best[1] if best else None


def first_index_on_page(els, page):
    for i, e in enumerate(els):
        if e.get("page", 0) >= page:
            return i
    return len(els)


def plan(els, toc):
    """Return [(chapter_title, [(section_title, start_index)])] with indices into els."""
    chapters = []
    entries = [(lvl, t.strip(), p) for lvl, t, p in toc if lvl <= 2]
    i = 0
    while i < len(entries):
        lvl, title, page = entries[i]
        if lvl != 1:
            i += 1
            continue
        kids = []
        j = i + 1
        while j < len(entries) and entries[j][0] == 2:
            kids.append(entries[j])
            j += 1
        chapters.append({"title": title, "page": page, "kids": kids})
        i = j

    # merge leading child-less chapters (Credits / About / Contents) into front matter
    front = []
    while len(chapters) > 1 and not chapters[0]["kids"]:
        front.append(chapters.pop(0))
    if front:
        chapters.insert(0, {"title": "Front Matter", "page": front[0]["page"],
                            "kids": [(2, c["title"], c["page"]) for c in front]})

    out = []
    for n, ch in enumerate(chapters):
        idx = find_heading(els, ch["title"], ch["page"], levels=(1,), window=2)
        if idx is None:
            idx = find_heading(els, ch["title"], ch["page"], window=1)
        if idx is None:
            idx = first_index_on_page(els, ch["page"])
        secs = []
        for _, st, sp in ch["kids"]:
            si = find_heading(els, st, sp, levels=(2, 3, 4), window=2)
            if si is None:
                si = first_index_on_page(els, sp)
            secs.append([st, si])
        out.append({"title": ch["title"], "start": idx, "secs": secs, "n": n})

    # enforce monotonic, non-overlapping cut points
    cuts = []
    for ch in out:
        cuts.append(("chapter", ch, ch["start"]))
        for s in ch["secs"]:
            cuts.append(("section", s, s[1]))
    last = -1
    for kind, obj, idx in cuts:
        idx = max(idx, last)
        last = idx
        if kind == "chapter":
            obj["start"] = idx
        else:
            obj[1] = idx
    return out
