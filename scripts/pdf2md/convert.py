#!/usr/bin/env python3
"""Convert an Odyssey of the Dragonlords PDF into a split markdown tree.

    .venv/bin/python scripts/pdf2md/convert.py [PDF OUTDIR]

With no arguments both remaster PDFs in input/REMASTER are converted in place.
The output mirrors input/Book Source: one directory per chapter, one markdown
file per table-of-contents section, illustrations in a per-chapter images/.
"""
import os
import sys

import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import images as im
import pdfmd
import split as sp

DEFAULT_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "..", "input", "REMASTER")
DEFAULT_BOOKS = [
    ("The_Great_Labors__PDF__-_Final_Version.pdf", "The_Great_Labors"),
    ("Odyssey_of_the_Dragonlords__PDF__-_Final_Version.pdf", "Odyssey_of_the_Dragonlords"),
]


def convert(pdf_path, out_dir, verbose=True):
    doc = pymupdf.open(pdf_path)
    if verbose:
        print("   extracting %d pages ..." % doc.page_count, flush=True)
    els = pdfmd.document_elements(doc, art_for=lambda page: im.art_rects(doc, page))
    els = pdfmd.join_continuations(els)
    chapters = sp.plan(els, doc.get_toc())

    os.makedirs(out_dir, exist_ok=True)
    written, unmatched = [], []
    for k, ch in enumerate(chapters):
        end = chapters[k + 1]["start"] if k + 1 < len(chapters) else len(els)
        cdir = os.path.join(out_dir, sp.dirname_for(k, ch["title"]))
        os.makedirs(cdir, exist_ok=True)

        pieces, secs = [], ch["secs"]
        if not secs:
            pieces.append((ch["title"], ch["start"], end))
        else:
            if secs[0][1] > ch["start"]:
                base = sp.PREFIX.sub("", ch["title"]).strip() or ch["title"]
                pieces.append((base + " Intro", ch["start"], secs[0][1]))
            for i, (st, si) in enumerate(secs):
                se = secs[i + 1][1] if i + 1 < len(secs) else end
                pieces.append((st, si, se))

        n = 0
        for title, a, b in pieces:
            body = pdfmd.render(els[a:b])
            if not body.strip():
                unmatched.append((ch["title"], title))
                continue
            for e in [e for e in els[a:b] if e["type"] == "img"]:
                idir = os.path.join(cdir, "images")
                os.makedirs(idir, exist_ok=True)
                name = "_page_%d_Picture_%d.jpeg" % (e["page"], e["idx"])
                im.save_art(doc, doc[e["page"] - 1], pymupdf.Rect(e["rect"]),
                            os.path.join(idir, name))
            n += 1
            path = os.path.join(cdir, "%02d-%s.md" % (n, sp.slug(title)))
            with open(path, "w") as f:
                f.write("# %s\n\n" % sp.title_case(title.strip()) + body)
            written.append(path)
    return written, unmatched


def main(argv):
    if len(argv) == 3:
        jobs = [(argv[1], argv[2])]
    elif len(argv) == 1:
        base = os.path.normpath(DEFAULT_BASE)
        jobs = [(os.path.join(base, p), os.path.join(base, o)) for p, o in DEFAULT_BOOKS]
    else:
        print(__doc__)
        return 2
    for pdf, out in jobs:
        print("==", os.path.basename(out), flush=True)
        written, unmatched = convert(pdf, out)
        print("   %d files, %d illustrations" % (
            len(written),
            sum(1 for _, _, fs in os.walk(out) for f in fs if f.endswith(".jpeg"))))
        for c, t in unmatched:
            print("   no separate heading found, folded into a sibling: %s / %s" % (c, t))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
