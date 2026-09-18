"""Layout-aware PDF -> Markdown converter for the Odyssey of the Dragonlords books.

The PDFs are InDesign exports with a very consistent font system, so element
classification is driven by (font family, size) instead of generic layout ML.
Reading order is recovered with a recursive XY-cut so the two-column body text
is never interleaved.
"""
import re
import unicodedata

import pymupdf

# --------------------------------------------------------------- font system

HEADING_SIZE_LEVEL = {21.0: 2, 16.0: 3, 13.0: 4}   # P22Sting-SC700
DROPCAP_SIZE = 50.5
ORNAMENT_FONTS = {"Wingdings-Regular", "Wingdings", "ZapfDingbats"}
HANDWRITE_FAMS = {
    "Trattatello", "Satisfy", "OvertheRainbow", "Brizel", "Condiment",
    "Dominican", "DominicanSmallCaps", "Sheila", "Abuget", "Zeyada",
    "P22", "CalNeuland", "Bilbo", "Rochester", "Diogenes",
}

PUA = re.compile(r"[-]")
LIG = {"ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl", "ﬅ": "st", "ﬆ": "st"}
SOFT = "­"


def fam(font):
    return font.split("-")[0]


def style_of(font):
    f = font.lower()
    return ("bold" in f or "black" in f or "semibold" in f), ("italic" in f or "oblique" in f)


def clean(s):
    for k, v in LIG.items():
        s = s.replace(k, v)
    s = PUA.sub("", s)
    s = s.replace("\x8a", "—").replace(" ", " ")
    s = "".join(c for c in s if unicodedata.category(c) != "Cc")
    return s


# --------------------------------------------------------------- line model

class Line:
    __slots__ = ("runs", "text", "font", "size", "color", "kind", "page",
                 "x0", "y0", "x1", "y1", "raw", "box", "blk")

    def __init__(self, ln, page):
        self.page = page
        self.x0, self.y0, self.x1, self.y1 = ln["bbox"]
        raw_spans = ln["spans"]
        self.raw = "".join(s["text"] for s in raw_spans)
        fonts = {s["font"] for s in raw_spans if s["text"].strip()}
        self.kind = "ornament" if fonts and fonts <= ORNAMENT_FONTS else None

        self.runs = []
        for s in raw_spans:
            t = clean(s["text"])
            if not t:
                continue
            b, i = style_of(s["font"])
            self.runs.append({"t": t, "b": b, "i": i, "font": s["font"],
                              "size": round(s["size"], 1), "color": s["color"],
                              "x0": s["bbox"][0], "x1": s["bbox"][2]})
        self.text = "".join(r["t"] for r in self.runs)
        pick = [r for r in self.runs if r["t"].strip()]
        ref = max(pick, key=lambda r: (r["size"], len(r["t"])), default=None)
        self.font = ref["font"] if ref else ""
        self.size = ref["size"] if ref else 0.0
        self.color = ref["color"] if ref else 0
        self.box = False
        self.blk = -1

    @property
    def bbox(self):
        return (self.x0, self.y0, self.x1, self.y1)


class Block:
    __slots__ = ("lines", "x0", "y0", "x1", "y1", "kind")

    def __init__(self, lines):
        self.lines = lines
        self.x0 = min(l.x0 for l in lines)
        self.y0 = min(l.y0 for l in lines)
        self.x1 = max(l.x1 for l in lines)
        self.y1 = max(l.y1 for l in lines)
        self.kind = None


class ImageLine:
    """Stands in for an illustration so it can take part in the layout sort."""
    kind = "image"
    text = ""
    runs = ()
    box = False

    def __init__(self, rect, page, idx):
        self.x0, self.y0, self.x1, self.y1 = rect
        self.page = page
        self.idx = idx
        self.blk = -1


# --------------------------------------------------------------- reading order

def merge_rows(lines):
    """InDesign emits each tab-separated column as its own line; stitch lines
    that share a baseline back into one logical line, left to right."""
    rows = []
    for l in sorted(lines, key=lambda l: (l.y0, l.x0)):
        placed = False
        for row in rows:
            r = row[0]
            h = min(l.y1 - l.y0, r.y1 - r.y0)
            ov = min(l.y1, r.y1) - max(l.y0, r.y0)
            if h > 0 and ov > 0.6 * h:
                row.append(l)
                placed = True
                break
        if not placed:
            rows.append([l])
    out = []
    for row in rows:
        row.sort(key=lambda l: l.x0)
        head = row[0]
        if len(row) > 1:
            runs = []
            for l in row:
                if runs:
                    runs.append({"t": " ", "b": False, "i": False, "font": head.font,
                                 "size": head.size, "color": head.color,
                                 "x0": l.x0, "x1": l.x0})
                runs.extend(l.runs)
            head.runs = runs
            head.text = "".join(r["t"] for r in runs)
            head.x1 = max(l.x1 for l in row)
            head.y1 = max(l.y1 for l in row)
        out.append(head)
    out.sort(key=lambda l: (l.y0, l.x0))
    return out


def _x_gaps(blocks, x_lo, x_hi, min_w=10.0):
    """Vertical whitespace corridors running the full height of the region."""
    iv = sorted((b.x0, b.x1) for b in blocks)
    gaps, edge = [], x_lo
    for a, b in iv:
        if a - edge >= min_w:
            gaps.append((edge, a))
        edge = max(edge, b)
    return gaps


def _y_bands(blocks, gap=6.0):
    order = sorted(blocks, key=lambda b: b.y0)
    bands, cur, edge = [], [], None
    for b in order:
        if cur and b.y0 - edge >= gap:
            bands.append(cur)
            cur, edge = [], None
        cur.append(b)
        edge = b.y1 if edge is None else max(edge, b.y1)
    if cur:
        bands.append(cur)
    return bands


def order_region(blocks, x_lo, x_hi):
    """Column-aware reading order.

    1. A block spanning most of the region separates it: read everything above
       it, then the block, then everything below.
    2. Otherwise cut into columns along full-height whitespace corridors.
    3. If some element bridges the gutter (a centred chapter header, a caption),
       fall back to horizontal bands and re-try the column cut inside each.
    """
    if len(blocks) <= 1:
        return list(blocks)
    width = x_hi - x_lo
    full = [b for b in blocks if (b.x1 - b.x0) >= 0.72 * width]
    if full:
        f = min(full, key=lambda b: (b.y0, b.x0))
        above = [b for b in blocks if b is not f and b.y1 <= f.y0 + 2]
        below = [b for b in blocks if b is not f and b.y1 > f.y0 + 2]
        return order_region(above, x_lo, x_hi) + [f] + order_region(below, x_lo, x_hi)

    gaps = _x_gaps(blocks, x_lo, x_hi)
    if gaps:
        bounds = [x_lo] + [(g[0] + g[1]) / 2 for g in gaps] + [x_hi]
        out = []
        for i in range(len(bounds) - 1):
            lo, hi = bounds[i], bounds[i + 1]
            col = [b for b in blocks if lo <= (b.x0 + b.x1) / 2 <= hi]
            if col:
                out.extend(order_region(col, min(b.x0 for b in col),
                                        max(b.x1 for b in col)))
        return out

    bands = _y_bands(blocks)
    if len(bands) > 1:
        out = []
        for band in bands:
            out.extend(order_region(band, min(b.x0 for b in band),
                                    max(b.x1 for b in band)))
        return out
    return sorted(blocks, key=lambda b: (b.y0, b.x0))


# ------------------------------------------------------------- classification

def classify(line):
    """Assign a semantic kind to a line from its dominant font."""
    if line.kind == "ornament":
        return "ornament"
    f, sz = line.font, line.size
    family = fam(f)
    txt = line.text.strip()
    if not txt:
        return "blank"

    if family == "Diogenes":
        return "chaptertitle"
    if f.startswith("P22Sting-SC700"):
        if sz >= 40:
            return "dropcap"
        lvl = HEADING_SIZE_LEVEL.get(sz)
        return "h%d" % lvl if lvl else "maplabel"
    if f.startswith("P22Sting"):
        if abs(sz - 14.0) < 0.3:
            return "chapternum"
        if abs(sz - 8.5) < 0.3:
            return "runninghead"
        return "maplabel"
    if family == "AGaramondPro":
        if abs(sz - 13.2) < 0.5 and txt.isdigit():
            return "pagenum"
        return "body"
    if family == "Seravek":
        if sz >= 14:
            return "sb_name"
        if abs(sz - 12.0) < 0.4:
            return "sb_section"
        if abs(sz - 11.0) < 0.4:
            return "side_title"
        if abs(sz - 10.0) < 0.4 and f.endswith("Medium"):
            return "table_title"
        if sz <= 7.5:
            return "table_head"
        if abs(sz - 9.5) < 0.4 and "Italic" in f:
            return "sb_type"
        return "side"
    if family in HANDWRITE_FAMS:
        return "hand"
    return "body"


def page_blocks(page, pno, art=()):
    """Text blocks of a page, in reading order, with per-line kinds assigned.
    `art` is a list of illustration rectangles, laid out alongside the text."""
    blocks = []
    for b in page.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        lines = []
        for ln in b["lines"]:
            l = Line(ln, pno)
            if l.text.strip() or l.kind == "ornament":
                lines.append(l)
        if lines:
            blocks.append(Block(lines))
    for blk in blocks:
        for l in blk.lines:
            l.kind = classify(l)
    keep, dropped = [], []
    for blk in blocks:
        blk.lines = [l for l in blk.lines
                     if l.kind not in ("runninghead", "pagenum", "blank", "maplabel")]
        (keep if blk.lines else dropped).append(blk)
    for k, r in enumerate(art):
        keep.append(Block([ImageLine(r, pno, k)]))
    if not keep:
        return []
    x_lo = min(b.x0 for b in keep)
    x_hi = max(b.x1 for b in keep)
    ordered = order_region(keep, x_lo, x_hi)
    assert len(ordered) == len(keep), "block lost on page %d" % pno
    for n, blk in enumerate(ordered):
        blk.lines = merge_rows(blk.lines)
        for l in blk.lines:
            l.blk = n
    return ordered


# ------------------------------------------------------------------ rendering

TERMINAL = tuple('.!?:;"”’)…')
WORD_TAIL = re.compile(r"[A-Za-z][A-Za-z'’]*$")
WORD_HEAD = re.compile(r"^[A-Za-z][A-Za-z'’]*")
VOCAB = set()
HYPH_STATS = {"joined": 0, "hyphenated": 0}


def build_vocab(doc):
    """Words the book spells out somewhere without a line break.

    InDesign encodes *every* break as a soft hyphen, including breaks at a real
    hyphen ("six-armed"), so the discretionary hyphen alone cannot say whether
    to keep it.  Comparing both candidate spellings against the rest of the
    book decides it."""
    VOCAB.clear()
    for page in doc:
        broken = False
        for line in page.get_text("text").split("\n"):
            toks = re.findall(r"[A-Za-z][A-Za-z'’-]*", line)
            if broken and toks:
                toks = toks[1:]         # tail of a word split by the line break
            broken = line.rstrip().endswith(SOFT)
            if broken and toks:
                toks = toks[:-1]        # head of a word split by the line break
            for t in toks:
                VOCAB.add(t.lower().strip("'’-"))
    return VOCAB


def keep_hyphen(prev, nxt):
    a = WORD_TAIL.search(prev)
    b = WORD_HEAD.search(nxt)
    if not a or not b:
        return False
    left, right = a.group(0).lower(), b.group(0).lower()
    if left + right in VOCAB:
        return False
    if left + "-" + right in VOCAB:
        return True
    return left in VOCAB and right in VOCAB
ABILITIES = ("Str", "Dex", "Con", "Int", "Wis", "Cha")


def join_runs(lines):
    """Concatenate the runs of several lines into one run list, undoing the
    line-breaking hyphenation InDesign inserted."""
    out = []
    for i, l in enumerate(lines):
        runs = [dict(r) for r in l.runs if r["t"]]
        if not runs:
            continue
        if out:
            prev = out[-1]
            ptxt = prev["t"].rstrip()
            if ptxt.endswith(SOFT):
                nxt = runs[0]["t"].lstrip()
                if keep_hyphen(ptxt[:-1], nxt):
                    prev["t"] = ptxt[:-1] + "-"
                    HYPH_STATS["hyphenated"] += 1
                else:
                    prev["t"] = ptxt[:-1]
                    HYPH_STATS["joined"] += 1
            elif ptxt.endswith(("-", "—", "–", "/")):
                prev["t"] = ptxt
            else:
                prev["t"] = ptxt + " "
        out.extend(runs)
    return out


def merge_runs(runs):
    """Merge adjacent runs of equal emphasis.  Whitespace-only runs are style
    neutral so that "**a** **b**" collapses to "**a b**" instead of leaving
    stray markers around the space."""
    merged = []
    for r in runs:
        blank = not r["t"].strip()
        if merged and (blank or (merged[-1]["b"] == r["b"] and merged[-1]["i"] == r["i"])):
            merged[-1]["t"] += r["t"]
        else:
            merged.append({"t": r["t"], "b": r["b"], "i": r["i"]})
    return merged


def render_runs(runs, force=None):
    """Runs -> inline markdown, keeping emphasis markers off the whitespace."""
    parts = []
    for r in merge_runs(runs):
        t = r["t"]
        if not t.strip():
            parts.append(t)
            continue
        b, i = (r["b"], r["i"]) if force is None else force
        mark = "***" if b and i else "**" if b else "*" if i else ""
        lead = t[:len(t) - len(t.lstrip())]
        trail = t[len(t.rstrip()):]
        parts.append(lead + mark + t.strip() + mark + trail)
    s = "".join(parts)
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace(SOFT, "")
    # emphasis wrapped around bare punctuation is a run artefact, not intent
    s = re.sub(r"(\*{1,3})([^\w\s*]{1,3})\1", r"\2", s)
    return s


def cells_of(line, gap=5.0):
    """Split a line's runs into table cells on horizontal whitespace."""
    cells, cur, edge = [], [], None
    for r in line.runs:
        if not r["t"].strip():
            continue
        if cur and r["x0"] - edge > gap:
            cells.append(cur)
            cur = []
        cur.append(r)
        edge = r["x1"]
    if cur:
        cells.append(cur)
    return [(c[0]["x0"], render_runs(c)) for c in cells]


# ------------------------------------------------------------ element builder

MAP_KEY = re.compile(r"^(?:[A-Z]{0,2}\d{1,3}[.:]?\s*){2,}$")

SIDE_KINDS = {"side", "table_head"}
SB_KINDS = {"sb_name", "sb_type", "sb_section"} | SIDE_KINDS


def mark_boxes(blocks):
    """Read-aloud boxes are delimited by Wingdings ornament rules; flag every
    line that falls between an opening and a closing rule."""
    inside = False
    prev_orn = False
    for blk in blocks:
        for l in blk.lines:
            if l.kind == "ornament":
                if not prev_orn:
                    inside = not inside
                prev_orn = True
                l.box = False
            else:
                prev_orn = False
                l.box = inside
    return blocks


def para_split(lines):
    """Split a run of same-kind lines into paragraphs on block boundaries and
    on vertical spacing."""
    if len(lines) < 2:
        return [lines]
    pitches = sorted(lines[i + 1].y0 - lines[i].y0 for i in range(len(lines) - 1))
    pitch = pitches[len(pitches) // 2]
    groups, cur = [], [lines[0]]
    for a, b in zip(lines, lines[1:]):
        if a.blk != b.blk or (pitch > 0 and (b.y0 - a.y0) > pitch * 1.45) \
                or runin_start(a, b):
            groups.append(cur)
            cur = []
        cur.append(b)
    groups.append(cur)
    return groups


RUNIN = re.compile(r"^[“‘(]?[A-Z0-9]")


def runin_start(prev, line):
    """A bold lead-in on its own line, right after a finished sentence, is a
    new paragraph rather than a continuation."""
    head = next((r for r in line.runs if r["t"].strip()), None)
    if not head or not head["b"] or not RUNIN.match(head["t"].lstrip()):
        return False
    return prev.text.rstrip().endswith(TERMINAL)


def statblock_element(lines, page):
    """Render a Seravek stat block as structured markdown."""
    head = ["##### " + render_runs(join_runs(lines[:1]), force=(False, False))]
    i = 1
    if i < len(lines) and lines[i].kind == "sb_type":
        head.append("*%s*" % render_runs(join_runs([lines[i]]), force=(False, False)))
        i += 1

    abilities, rest = [], []
    for l in lines[i:]:
        toks = re.split(r"\s+", re.sub(r"[*]", "", l.text).strip())
        if toks and toks[0] in ABILITIES:
            j = 0
            while j + 3 < len(toks) + 1:
                if toks[j] in ABILITIES:
                    abilities.append(toks[j:j + 4])
                    j += 4
                else:
                    j += 1
        elif l.kind != "table_head":
            rest.append(l)

    # group the remaining lines into paragraphs, breaking at section headers
    groups, cur = [], []
    for l in rest:
        if l.kind == "sb_section":
            if cur:
                groups.append(("p", cur))
                cur = []
            groups.append(("h", [l]))
        elif cur and cur[-1].blk == l.blk:
            cur.append(l)
        else:
            if cur:
                groups.append(("p", cur))
            cur = [l]
    if cur:
        groups.append(("p", cur))

    stats, body, seen_section = [], [], False
    for kind, ls in groups:
        if kind == "h":
            seen_section = True
            body.append("")
            body.append("**%s**" % render_runs(join_runs(ls), force=(False, False)))
            body.append("")
        else:
            txt = render_runs(join_runs(ls))
            if not txt:
                continue
            (body if seen_section else stats).append(txt)

    out = list(head)
    out.append("")
    if stats:
        out.append("  \n".join(stats))
    if abilities:
        out.append("")
        out.append("| | Score | Mod | Save |")
        out.append("|---|---|---|---|")
        for r in abilities:
            out.append("| **%s** | %s |" % (r[0], " | ".join(r[1:])))
    out.extend(body)
    md = re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()
    return {"type": "statblock", "page": page, "md": md}


def table_element(title, lines, page):
    rows = []
    for l in merge_rows(list(lines)):
        cs = cells_of(l)
        if cs:
            rows.append((l.y0, cs))
    if not rows:
        return None

    # Column count: the width most rows agree on.  Right-aligned numeric cells
    # sit at slightly different x per row, so cluster on the widest gaps rather
    # than on a fixed tolerance.
    counts = {}
    for _, cs in rows:
        counts[len(cs)] = counts.get(len(cs), 0) + 1
    ncols = max(counts, key=lambda k: (counts[k], k))
    ncols = max(ncols, 2)
    xs = sorted({round(x, 1) for _, cs in rows for x, _ in cs})
    if len(xs) < 2:
        return None
    if len(xs) > ncols:
        gaps = sorted(((xs[i + 1] - xs[i], i) for i in range(len(xs) - 1)), reverse=True)
        cut = sorted(i for _, i in gaps[:ncols - 1])
        cols, start = [], 0
        for c in cut:
            cols.append(xs[start])
            start = c + 1
        cols.append(xs[start])
    else:
        cols = xs
    if len(cols) < 2:
        return None

    def col_of(x):
        return min(range(len(cols)), key=lambda k: abs(x - cols[k]))

    grid = []
    for _, cs in rows:
        row = [""] * len(cols)
        for x, t in cs:
            k = col_of(x)
            row[k] = (row[k] + " " + t).strip()
        grid.append(row)

    # a header cell that wrapped onto two lines shows up as a short leading row
    for _ in range(2):
        if len(grid) > 1 and all(not (a and b) for a, b in zip(grid[0], grid[1])) \
                and sum(1 for c in grid[0] if c) < len(cols):
            head, nxt = grid.pop(0), grid.pop(0)
            grid.insert(0, [(a + " " + b).strip() for a, b in zip(head, nxt)])
        else:
            break

    md = []
    if title:
        md.append("**%s**" % title)
        md.append("")
    md.append("| " + " | ".join(grid[0]) + " |")
    md.append("|" + "|".join("---" for _ in cols) + "|")
    for row in grid[1:]:
        md.append("| " + " | ".join(row) + " |")
    return {"type": "table", "page": page, "md": "\n".join(md)}


def undouble(text):
    """Chapter titles are set twice (drop shadow); keep one copy."""
    w = text.split()
    if len(w) >= 2 and len(w) % 2 == 0 and w[:len(w) // 2] == w[len(w) // 2:]:
        return " ".join(w[:len(w) // 2])
    return text


def looks_tabular(lines):
    multi = [l for l in lines if len(cells_of(l)) >= 2]
    return len(multi) >= 2 and len(multi) >= len(lines) * 0.6


def take_while(seq, i, pred):
    j = i
    while j < len(seq) and pred(seq[j]):
        j += 1
    return j


def build_elements(blocks, page):
    seq = [l for blk in mark_boxes(blocks) for l in blk.lines]
    for l in seq:
        if not hasattr(l, "box"):
            l.box = False
    els, i, dropcap = [], 0, None

    def para(lines, style):
        nonlocal dropcap
        for grp in para_split(lines):
            txt = render_runs(join_runs(grp))
            if not txt:
                continue
            if dropcap and style == "body":
                txt = dropcap + txt
                dropcap = None
            els.append({"type": "p", "style": style, "page": page, "text": txt})

    while i < len(seq):
        l = seq[i]
        k = l.kind
        if k == "ornament":
            i += 1
            continue
        if k == "image":
            els.append({"type": "img", "page": l.page, "idx": l.idx,
                        "rect": (l.x0, l.y0, l.x1, l.y1)})
            i += 1
            continue
        if k == "chapternum":
            els.append({"type": "chapternum", "page": page,
                        "text": re.sub(r"\s+", " ", l.text.strip())})
            i += 1
            continue
        if k == "chaptertitle":
            j = take_while(seq, i, lambda x: x.kind == "chaptertitle")
            words, seen = [], set()
            for x in seq[i:j]:
                t = undouble(re.sub(r"\s+", " ", x.text.strip()))
                if t and t not in seen:
                    seen.add(t)
                    words.append(t)
            text = undouble(" ".join(words))
            els.append({"type": "h", "level": 1, "page": page, "text": text})
            i = j
            continue
        if k == "dropcap":
            dropcap = l.text.strip()
            i += 1
            continue
        if k in ("h2", "h3", "h4"):
            j = take_while(seq, i, lambda x: x.kind == k)
            text = render_runs(join_runs(seq[i:j]), force=(False, False))
            if MAP_KEY.match(text):
                i = j
                continue
            els.append({"type": "h", "level": int(k[1]), "page": page, "text": text})
            i = j
            continue
        if k == "sb_name":
            j = take_while(seq, i + 1, lambda x: x.kind in SB_KINDS and x.kind != "sb_name")
            els.append(statblock_element(seq[i:j], page))
            i = j
            continue
        if k == "table_title":
            title = render_runs(join_runs([l]), force=(False, False))
            j = take_while(seq, i + 1, lambda x: x.kind in SIDE_KINDS)
            tbl = table_element(title, seq[i + 1:j], page)
            if tbl:
                els.append(tbl)
            else:
                els.append({"type": "p", "style": "side", "page": page,
                            "text": "**%s**" % title})
                para(seq[i + 1:j], "side")
            i = j
            continue
        if k == "side_title":
            title = render_runs(join_runs([l]), force=(False, False))
            j = take_while(seq, i + 1, lambda x: x.kind in SIDE_KINDS)
            els.append({"type": "sidebar", "page": page, "title": title})
            para(seq[i + 1:j], "side")
            i = j
            continue
        if k in SIDE_KINDS:
            j = take_while(seq, i, lambda x: x.kind in SIDE_KINDS)
            chunk = seq[i:j]
            tbl = table_element(None, chunk, page) if looks_tabular(chunk) else None
            if tbl:
                els.append(tbl)
            else:
                para(chunk, "side")
            i = j
            continue
        if k == "hand":
            j = take_while(seq, i, lambda x: x.kind == "hand")
            para(seq[i:j], "hand")
            i = j
            continue
        j = take_while(seq, i, lambda x: x.kind == "body")
        if j == i:
            j = i + 1
        chunk = seq[i:j]
        boxed = [x for x in chunk if x.box]
        if boxed and len(boxed) == len(chunk):
            para(chunk, "box")
        else:
            para(chunk, "body")
        i = j
    return els


# --------------------------------------------------------------- document pass

def document_elements(doc, progress=None, art_for=None):
    build_vocab(doc)
    els = []
    for pno in range(doc.page_count):
        page = doc[pno]
        els.append({"type": "page", "page": pno + 1})
        art = art_for(page) if art_for else ()
        els.extend(build_elements(page_blocks(page, pno + 1, art), pno + 1))
        if progress:
            progress(pno)
    return els


def join_continuations(els):
    """Rejoin paragraphs broken by a column or page break."""
    out = []
    for e in els:
        if (e["type"] == "p" and out and out[-1]["type"] == "p"
                and out[-1]["style"] == e["style"] and e["style"] != "hand"):
            prev = out[-1]["text"]
            nxt = e["text"]
            tail = prev.rstrip("*_ ")
            lead = nxt.lstrip("*_ ")
            if (tail and lead and not tail.endswith(TERMINAL)
                    and (lead[0].islower() or lead[0] in "“‘("
                         or (nxt.startswith("*") and tail[-1:].islower()))
                    and not prev.endswith("|")):
                glue = "" if prev.endswith(("-", "—", "–")) else " "
                out[-1] = dict(out[-1], text=prev + glue + nxt)
                continue
        out.append(e)
    return out


def render(els):
    """Element stream -> markdown text."""
    lines, pending_side_title = [], None

    def push(s=""):
        lines.append(s)

    for e in els:
        t = e["type"]
        if t == "page":
            push()
            push('<span id="page-%d"></span>' % e["page"])
            push()
        elif t == "chapternum":
            continue
        elif t == "h":
            if e["level"] == 1:
                continue        # the file already carries the chapter title
            push()
            push("#" * e["level"] + " " + e["text"])
            push()
        elif t == "sidebar":
            pending_side_title = e["title"]
        elif t == "img":
            push()
            push("![](images/_page_%d_Picture_%d.jpeg)" % (e["page"], e["idx"]))
            push()
        elif t == "table":
            push()
            push(e["md"])
            push()
        elif t == "statblock":
            push()
            push(e["md"])
            push()
        elif t == "p":
            style = e["style"]
            txt = e["text"]
            if style in ("box", "side", "hand"):
                if pending_side_title:
                    push()
                    push("> [!info] " + pending_side_title)
                    pending_side_title = None
                elif lines and lines[-1].startswith(">"):
                    push(">")
                else:
                    push()
                if style == "hand":
                    txt = "*%s*" % txt if not txt.startswith("*") else txt
                push("> " + txt)
            else:
                push()
                push(txt)
                push()
    md = "\n".join(lines)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip() + "\n"
