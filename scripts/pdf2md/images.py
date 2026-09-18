"""Illustration extraction.

Every page of these PDFs is one flattened raster (artwork + parchment) with
live text drawn on top of it, so illustrations cannot be pulled out as separate
embedded image objects.  What we can do is analyse that raster - which carries
the art but none of the text - find the parts of it that are not blank
parchment, and crop those out.
"""
import io
import os

import numpy as np
import pymupdf
from PIL import Image

GRID = 4.0          # analysis cell size, in PDF points
MIN_W, MIN_H = 96.0, 84.0
MIN_AREA = 26000.0  # square points
BORDER = 12.0       # ignore the printed page frame
JPEG_QUALITY = 84
MAX_PX = 1500


def page_raster(doc, page):
    imgs = page.get_images(full=True)
    if not imgs:
        return None, None
    xref = max(imgs, key=lambda im: im[2] * im[3])[0]
    rects = page.get_image_rects(xref)
    if not rects:
        return None, None
    info = doc.extract_image(xref)
    return Image.open(io.BytesIO(info["image"])).convert("RGB"), rects[0]


def _mask(img, w, h):
    """Cells that hold something other than blank parchment."""
    fine = np.asarray(img.resize((w * 2, h * 2), Image.BOX), dtype=np.float32)
    lum = fine @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    sat = fine.max(axis=2) - fine.min(axis=2)

    def blocks(a):
        return a.reshape(h, 2, w, 2).transpose(0, 2, 1, 3).reshape(h, w, 4)

    lb, sb = blocks(lum), blocks(sat)
    dark = lb.mean(axis=2) < 186
    color = sb.mean(axis=2) > 62
    rough = lb.std(axis=2) > 26
    return dark | color | rough


def _components(mask):
    """Label 8-connected components with a simple iterative flood fill."""
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    boxes = []
    for y0 in range(h):
        for x0 in range(w):
            if not mask[y0, x0] or seen[y0, x0]:
                continue
            stack = [(y0, x0)]
            seen[y0, x0] = True
            ys, xs = [y0], [x0]
            while stack:
                y, x = stack.pop()
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            stack.append((ny, nx))
                            ys.append(ny)
                            xs.append(nx)
            boxes.append((min(xs), min(ys), max(xs) + 1, max(ys) + 1, len(xs)))
    return boxes


def _dilate(mask, r=2):
    out = mask.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out |= np.roll(np.roll(mask, dy, axis=0), dx, axis=1)
    return out


def art_rects(doc, page):
    """Rectangles of the page that contain artwork, in PDF coordinates."""
    img, rect = page_raster(doc, page)
    if img is None:
        return []
    pw, ph = rect.width, rect.height
    w, h = max(1, int(pw / GRID)), max(1, int(ph / GRID))
    mask = _mask(img, w, h)

    # drop the decorative frame that runs around every page
    b = int(BORDER / GRID) + 1
    mask[:b, :] = False
    mask[-b:, :] = False
    mask[:, :b] = False
    mask[:, -b:] = False

    out = []
    for x0, y0, x1, y1, n in _components(_dilate(mask)):
        r = pymupdf.Rect(rect.x0 + x0 * GRID, rect.y0 + y0 * GRID,
                         rect.x0 + x1 * GRID, rect.y0 + y1 * GRID)
        r &= page.rect
        if r.width < MIN_W or r.height < MIN_H:
            continue
        if r.get_area() < MIN_AREA:
            continue
        if n * GRID * GRID < 0.30 * r.get_area():
            continue        # sparse scatter, not a picture
        out.append(r)
    out.sort(key=lambda r: (round(r.y0), r.x0))
    return out


def save_art(doc, page, rect, path):
    """Crop the illustration out of the page raster, so no text is baked in."""
    img, prect = page_raster(doc, page)
    if img is None:
        return None
    sx = img.width / prect.width
    sy = img.height / prect.height
    box = (max(0, int((rect.x0 - prect.x0) * sx)),
           max(0, int((rect.y0 - prect.y0) * sy)),
           min(img.width, int((rect.x1 - prect.x0) * sx)),
           min(img.height, int((rect.y1 - prect.y0) * sy)))
    crop = img.crop(box)
    if max(crop.size) > MAX_PX:
        f = MAX_PX / max(crop.size)
        crop = crop.resize((max(1, int(crop.width * f)), max(1, int(crop.height * f))),
                           Image.LANCZOS)
    crop.save(path, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    return path
