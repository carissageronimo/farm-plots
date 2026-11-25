"""Farm area signs (A4 landscape) and trash-bin labels (half A4, 297 x 105 mm).

Outputs (in this folder):
  area-signs-a4.pdf                 5 pages, A4 landscape, one sign per page
  bin-labels-half-a4.pdf            1 A4 page holding 2 bin labels, cut across the middle
  tarp-area-signs-2x3ft.pdf / .jpg  everything on one 2 x 3 ft tarpaulin, actual size, cut marks:
                                    5 A4 signs + 6 bin labels, sharing cut lines

Same style as the plot labels: deep brown border and band with cream logo,
main words in black on white (black ink fades least in sun).
"""
import os
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import CMYKColor, black, white
import make_labels as L
from PIL import Image
from reportlab.lib.utils import ImageReader

HERE = os.path.dirname(os.path.abspath(__file__))
F = "ArchivoBlack"
RED = CMYKColor(0, 1, 1, 0.05)
A4W, A4H = landscape(A4)          # 297 x 210 mm
BW, BH = A4W, A4H / 2             # bin label 297 x 105 mm

SIGNS = [
    dict(lines=["POST-HARVEST", "AREA"]),
    dict(lines=["WORK AREA"]),
    dict(lines=["INPUTS &", "SHREDDER"]),
    dict(lines=["COMPOST PIT"], sub="(Nabubulok)"),
    dict(lines=["NO", "SMOKING"], sub="(Bawal manigarilyo)", nosmoke=True),
]
BIN = dict(lines=["BASURA"], sub="(Di nabubulok / Non-biodegradable)")

FARM = "Essentialist Vegetable Farm"


def fit(text, max_w, size):
    while pdfmetrics.stringWidth(text, F, size) > max_w:
        size -= 1
    return size


def border(c, w, h):
    m, bw = 6 * mm, 3 * mm
    c.setStrokeColor(L.BROWN)
    c.setLineWidth(bw)
    c.rect(m, m, w - 2 * m, h - 2 * m)
    c.setStrokeColor(black)


def text_block(c, lines, sub, x, y, w, h, sub_ratio=0.5, gap_ratio=0.22, color=black):
    """Centre the main lines (+ optional sub line) in the box (x, y, w, h)."""
    cap = 0.72  # cap height ratio, Archivo Black
    size = 400
    for t in lines:
        size = fit(t, w, size)
    while True:
        sub_size = fit(sub, w, size * sub_ratio) if sub else 0
        total = len(lines) * size * cap + (len(lines) - 1) * size * 0.28
        if sub:
            total += size * gap_ratio + sub_size * cap
        if total <= h:
            break
        size -= 2
    top = y + (h + total) / 2
    c.setFillColor(color)
    c.setFont(F, size)
    for i, t in enumerate(lines):
        base = top - size * cap - i * size * (cap + 0.28)
        c.drawCentredString(x + w / 2, base, t)
    if sub:
        c.setFont(F, sub_size)
        c.drawCentredString(x + w / 2, y + (h - total) / 2, sub)


def no_smoking(c, cx, cy, r, inv=False):
    """Universal no-smoking symbol: cigarette under a red circle and slash."""
    c.saveState()
    # cigarette
    lw, lh = r * 1.35, r * 0.24
    x0, y0 = cx - lw / 2, cy - lh / 2
    fg, bg = (white, black) if inv else (black, white)
    c.setFillColor(bg)
    c.setStrokeColor(fg)
    c.setLineWidth(r * 0.05)
    c.rect(x0, y0, lw, lh, fill=1, stroke=1)
    c.setFillColor(fg)
    c.rect(x0, y0, lw * 0.28, lh, fill=1, stroke=0)          # filter
    c.rect(x0 + lw * 0.93, y0, lw * 0.07, lh, fill=1, stroke=0)  # lit end
    # smoke
    p = c.beginPath()
    sx = x0 + lw * 0.97
    p.moveTo(sx, cy + lh * 0.8)
    p.curveTo(sx - r * 0.12, cy + r * 0.32, sx + r * 0.12, cy + r * 0.45, sx, cy + r * 0.62)
    c.setLineWidth(r * 0.045)
    c.drawPath(p, stroke=1, fill=0)
    # red ring + slash
    c.setStrokeColor(RED)
    c.setLineWidth(r * 0.16)
    c.circle(cx, cy, r * 0.92, stroke=1, fill=0)
    d = r * 0.92 * 0.7071
    c.line(cx - d, cy + d, cx + d, cy - d)
    c.restoreState()


def draw_sign(c, s):
    w, h = A4W, A4H
    m = 6 * mm
    border(c, w, h)
    # brand band
    band_h = 34 * mm
    c.setFillColor(L.BROWN)
    c.rect(m, h - m - band_h, w - 2 * m, band_h, stroke=0, fill=1)
    logo_h = 22 * mm
    logo_w = logo_h * L.LOGO_RATIO
    lx = m + 12 * mm
    ly = h - m - band_h + (band_h - logo_h) / 2
    c.drawImage(L.LOGO_CREAM, lx, ly, logo_w, logo_h, mask="auto")
    size = fit(FARM, w - 2 * m - logo_w - 30 * mm, 30)
    c.setFillColor(L.CREAM)
    c.setFont(F, size)
    c.drawString(lx + logo_w + 6 * mm, h - m - band_h / 2 - size * 0.36, FARM)
    border(c, w, h)
    # body
    bx, by = m + 12 * mm, m + 10 * mm
    bw, bh = w - 2 * (m + 12 * mm), h - m - band_h - 10 * mm - by
    if s.get("nosmoke"):
        r = bh * 0.42
        no_smoking(c, bx + r, by + bh / 2, r)
        tx = bx + 2 * r + 12 * mm
        text_block(c, s["lines"], s.get("sub"), tx, by, bx + bw - tx, bh, sub_ratio=0.42)
    else:
        text_block(c, s["lines"], s.get("sub"), bx, by, bw, bh)


def draw_bin(c, s=BIN):
    w, h = BW, BH
    m = 6 * mm
    # brown side panel with cream logo
    panel = 46 * mm
    c.setFillColor(L.BROWN)
    c.rect(m, m, panel, h - 2 * m, stroke=0, fill=1)
    logo_w = panel - 12 * mm
    logo_h = logo_w / L.LOGO_RATIO
    c.drawImage(L.LOGO_CREAM, m + 6 * mm, h / 2 - logo_h / 2, logo_w, logo_h, mask="auto")
    border(c, w, h)
    bx = m + panel + 8 * mm
    text_block(c, s["lines"], s.get("sub"), bx, m + 8 * mm, w - m - 8 * mm - bx, h - 2 * m - 16 * mm,
               sub_ratio=0.3, gap_ratio=0.22)


def place(c, x, y, fn, *a):
    c.saveState()
    c.translate(x, y)
    fn(c, *a)
    c.restoreState()


def tarp(sign_fn=None, bin_fn=None, name="tarp-area-signs-2x3ft"):
    sign_fn = sign_fn or draw_sign
    bin_fn = bin_fn or draw_bin
    SW, SH = 610 * mm, 914 * mm
    X0 = (SW - 2 * A4W) / 2                 # 8 mm sides
    gh = 3 * A4H + 2 * BH                   # 840 mm
    Y0 = (SH - gh) / 2                      # 37 mm top/bottom
    out = os.path.join(HERE, name + ".pdf")
    c = canvas.Canvas(out, pagesize=(SW, SH))
    c.setTitle("Essentialist Vegetable Farm area signs and bin labels - tarpaulin 2 x 3 ft")
    top = SH - Y0
    cells = []  # (x, y, kind, payload)
    for i, s in enumerate(SIGNS):          # 3 rows of 2 A4 slots; slot 6 holds 2 bin labels
        col, row = i % 2, i // 2
        cells.append((X0 + col * A4W, top - (row + 1) * A4H, "sign", s))
    x6, y6 = X0 + A4W, top - 3 * A4H
    cells += [(x6, y6 + BH, "bin", None), (x6, y6, "bin", None)]
    for row in range(2):                    # 2 rows of 2 bin labels below
        for col in range(2):
            cells.append((X0 + col * BW, top - 3 * A4H - (row + 1) * BH, "bin", None))
    for x, y, kind, s in cells:
        if kind == "sign":
            place(c, x, y, sign_fn, s)
        else:
            place(c, x, y, bin_fn)
    # cut marks in the margins
    c.setLineWidth(0.3 * mm)
    ln, off = 5 * mm, 1.5 * mm
    side = X0 - off - 1 * mm
    for x in (X0, X0 + A4W, X0 + 2 * A4W):
        c.line(x, Y0 - off, x, Y0 - off - ln)
        c.line(x, SH - Y0 + off, x, SH - Y0 + off + ln)
    full = [top, top - A4H, top - 2 * A4H, top - 3 * A4H, top - 3 * A4H - BH, Y0]
    for y in full:
        c.line(X0 - off, y, X0 - off - side, y)
        c.line(SW - X0 + off, y, SW - X0 + off + side, y)
    c.line(SW - X0 + off, y6 + BH, SW - X0 + off + side, y6 + BH)   # split of slot 6 (right column only)
    c.showPage()
    c.save()
    return out


# ---- Reversed style: white letters on solid black --------------------------
# Black is the most sun-resistant ink and the letters are bare white tarp,
# so contrast holds as the black slowly softens toward charcoal.
_lw = Image.new("RGBA", L.src.size, (255, 255, 255, 0))
_lw.putalpha(L._m)
_lw = _lw.resize((_lw.width * 4, _lw.height * 4), Image.LANCZOS)
_lw.save(os.path.join(HERE, "logo_white.png"))
LOGO_WHITE = ImageReader(os.path.join(HERE, "logo_white.png"))


def black_ground(c, w, h):
    c.setFillColor(black)
    c.rect(0, 0, w, h, stroke=0, fill=1)
    c.setStrokeColor(white)
    c.setLineWidth(1.2 * mm)
    c.rect(7 * mm, 7 * mm, w - 14 * mm, h - 14 * mm)


def draw_sign_rev(c, s):
    w, h = A4W, A4H
    black_ground(c, w, h)
    m = 7 * mm
    head = 30 * mm
    logo_h = 18 * mm
    logo_w = logo_h * L.LOGO_RATIO
    lx = m + 10 * mm
    c.drawImage(LOGO_WHITE, lx, h - m - head / 2 - logo_h / 2 - 1 * mm, logo_w, logo_h, mask="auto")
    size = fit(FARM, w - 2 * m - logo_w - 30 * mm, 26)
    c.setFillColor(white)
    c.setFont(F, size)
    c.drawString(lx + logo_w + 6 * mm, h - m - head / 2 - size * 0.36, FARM)
    c.setStrokeColor(white)
    c.setLineWidth(0.8 * mm)
    c.line(m + 10 * mm, h - m - head, w - m - 10 * mm, h - m - head)
    bx, by = m + 12 * mm, m + 10 * mm
    bw, bh = w - 2 * (m + 12 * mm), h - m - head - 8 * mm - by
    if s.get("nosmoke"):
        r = bh * 0.42
        no_smoking(c, bx + r, by + bh / 2, r, inv=True)
        tx = bx + 2 * r + 12 * mm
        text_block(c, s["lines"], s.get("sub"), tx, by, bx + bw - tx, bh, sub_ratio=0.42, color=white)
    else:
        text_block(c, s["lines"], s.get("sub"), bx, by, bw, bh, color=white)


def draw_bin_rev(c, s=BIN):
    w, h = BW, BH
    black_ground(c, w, h)
    m = 7 * mm
    logo_w = 30 * mm
    logo_h = logo_w / L.LOGO_RATIO
    c.drawImage(LOGO_WHITE, m + 8 * mm, h / 2 - logo_h / 2, logo_w, logo_h, mask="auto")
    c.setStrokeColor(white)
    c.setLineWidth(0.8 * mm)
    x = m + 8 * mm + logo_w + 7 * mm
    c.line(x, m + 9 * mm, x, h - m - 9 * mm)
    bx = x + 8 * mm
    text_block(c, s["lines"], s.get("sub"), bx, m + 8 * mm, w - m - 8 * mm - bx, h - 2 * m - 16 * mm,
               sub_ratio=0.3, gap_ratio=0.22, color=white)


def main():
    c = canvas.Canvas(os.path.join(HERE, "area-signs-a4.pdf"), pagesize=(A4W, A4H))
    c.setTitle("Essentialist Vegetable Farm area signs (A4)")
    for s in SIGNS:
        draw_sign(c, s)
        c.showPage()
    c.save()
    c = canvas.Canvas(os.path.join(HERE, "bin-labels-half-a4.pdf"), pagesize=(A4W, A4H))
    c.setTitle("Essentialist Vegetable Farm bin labels (half A4)")
    place(c, 0, BH, draw_bin)
    place(c, 0, 0, draw_bin)
    c.setLineWidth(0.2 * mm)
    c.setDash(2 * mm, 2 * mm)
    c.line(0, BH, 4 * mm, BH)
    c.line(A4W - 4 * mm, BH, A4W, BH)
    c.showPage()
    c.save()
    print(tarp())
    c = canvas.Canvas(os.path.join(HERE, "area-signs-a4-reverse.pdf"), pagesize=(A4W, A4H))
    c.setTitle("Essentialist Vegetable Farm area signs (A4, white on black)")
    for s in SIGNS:
        draw_sign_rev(c, s)
        c.showPage()
    c.save()
    c = canvas.Canvas(os.path.join(HERE, "bin-labels-half-a4-reverse.pdf"), pagesize=(A4W, A4H))
    c.setTitle("Essentialist Vegetable Farm bin labels (half A4, white on black)")
    place(c, 0, BH, draw_bin_rev)
    place(c, 0, 0, draw_bin_rev)
    c.showPage()
    c.save()
    print(tarp(draw_sign_rev, draw_bin_rev, "tarp-area-signs-2x3ft-reverse"))




# ---- Version 2 (Nov 25): one big letter size, minimal no-smoking icon, quarter-A4 bin labels --
SIGNS2 = [
    dict(lines=["POST-", "HARVEST", "AREA"]),
    dict(lines=["WORK", "AREA"]),
    dict(lines=["INPUTS &", "SHREDDER"]),
    dict(lines=["COMPOST", "PIT"], sub="(Nabubulok)"),
    dict(lines=["NO", "SMOKING"], sub="(Bawal manigarilyo)", nosmoke=True),
]
QW, QH = A4H, A4W / 4                       # quarter A4 crosswise: 210 x 74.25 mm
LOGO_BROWN_C = CMYKColor(0.15, 0.32, 0.62, 0.30)   # close to the logo brown, readable on black
STYLES = {
    # name: ground, brand colour, brand logo image
    "brown": (L.BROWN, L.CREAM, None),
    "black": (black, LOGO_BROWN_C, None),
}


def _logo_img(colour_rgb, key):
    im = Image.new("RGBA", L.src.size, colour_rgb + (0,))
    im.putalpha(L._m)
    im = im.resize((im.width * 4, im.height * 4), Image.LANCZOS)
    p = os.path.join(HERE, f"logo_{key}.png")
    im.save(p)
    return ImageReader(p)


LOGOS = {"brown": _logo_img((249, 242, 224), "cream2"), "black": _logo_img((150, 122, 78), "brown2")}
BIG = 120  # pt: the INPUTS & SHREDDER size, used for every sign


def ground(c, w, h, style):
    g, brand, _ = STYLES[style]
    c.setFillColor(g)
    c.rect(0, 0, w, h, stroke=0, fill=1)
    c.setStrokeColor(brand)
    c.setLineWidth(1.2 * mm)
    c.rect(7 * mm, 7 * mm, w - 14 * mm, h - 14 * mm)


def no_smoking_min(c, cx, cy, r, colour):
    """Minimal line icon: outlined cigarette, small wisp, thin circle and slash, one colour."""
    c.saveState()
    c.setStrokeColor(colour)
    lw = r * 0.075
    c.setLineWidth(lw)
    cw, ch = r * 1.15, r * 0.2
    x0, y0 = cx - cw / 2, cy - ch / 2
    c.roundRect(x0, y0, cw, ch, ch * 0.2, stroke=1, fill=0)
    c.line(x0 + cw * 0.3, y0, x0 + cw * 0.3, y0 + ch)
    p = c.beginPath()
    sx = x0 + cw * 0.9
    p.moveTo(sx, y0 + ch + r * 0.1)
    p.curveTo(sx - r * 0.1, cy + r * 0.32, sx + r * 0.1, cy + r * 0.4, sx, cy + r * 0.55)
    c.drawPath(p, stroke=1, fill=0)
    c.circle(cx, cy, r, stroke=1, fill=0)
    d = r * 0.7071
    c.line(cx - d, cy + d, cx + d, cy - d)
    c.restoreState()


def draw_sign2(c, s, style):
    w, h = A4W, A4H
    g, brand, _ = STYLES[style]
    ground(c, w, h, style)
    m = 7 * mm
    head = 26 * mm
    logo_h = 15 * mm
    logo_w = logo_h * L.LOGO_RATIO
    lx = m + 10 * mm
    c.drawImage(LOGOS[style], lx, h - m - head / 2 - logo_h / 2 - 1 * mm, logo_w, logo_h, mask="auto")
    c.setFillColor(brand)
    c.setFont(F, 20)
    c.drawString(lx + logo_w + 5 * mm, h - m - head / 2 - 20 * 0.36, FARM)
    bx, by = m + 12 * mm, m + 9 * mm
    bw, bh = w - 2 * (m + 12 * mm), h - m - head - 4 * mm - by
    if s.get("nosmoke"):
        r = bh * 0.3
        no_smoking_min(c, bx + r + 4 * mm, by + bh / 2, r, white)
        tx = bx + 2 * r + 18 * mm
        text_block2(c, s, tx, by, bx + bw - tx, bh)
    else:
        text_block2(c, s, bx, by, bw, bh)


def text_block2(c, s, x, y, w, h):
    cap, lead = 0.72, 0.26
    lines, sub = s["lines"], s.get("sub")
    size = BIG
    for t in lines:
        size = fit(t, w, size)
    sub_size = fit(sub, w, size * 0.42) if sub else 0
    total = len(lines) * size * cap + (len(lines) - 1) * size * lead
    if sub:
        total += size * 0.24 + sub_size * cap
    while total > h:  # safety, should not trigger
        size -= 2
        sub_size = fit(sub, w, size * 0.42) if sub else 0
        total = len(lines) * size * cap + (len(lines) - 1) * size * lead + ((size * 0.24 + sub_size * cap) if sub else 0)
    top = y + (h + total) / 2
    c.setFillColor(white)
    c.setFont(F, size)
    for i, t in enumerate(lines):
        c.drawCentredString(x + w / 2, top - size * cap - i * size * (cap + lead), t)
    if sub:
        c.setFont(F, sub_size)
        c.drawCentredString(x + w / 2, y + (h - total) / 2, sub)


def draw_bin2(c, style, s=BIN):
    w, h = QW, QH
    g, brand, _ = STYLES[style]
    ground(c, w, h, style)
    m = 7 * mm
    logo_w = 20 * mm
    logo_h = logo_w / L.LOGO_RATIO
    c.drawImage(LOGOS[style], m + 6 * mm, h / 2 - logo_h / 2, logo_w, logo_h, mask="auto")
    x = m + 6 * mm + logo_w + 5 * mm
    c.setStrokeColor(brand)
    c.setLineWidth(0.6 * mm)
    c.line(x, m + 6 * mm, x, h - m - 6 * mm)
    bx = x + 5 * mm
    text_block(c, s["lines"], s.get("sub"), bx, m + 5 * mm, w - m - 5 * mm - bx, h - 2 * m - 10 * mm,
               sub_ratio=0.3, gap_ratio=0.22, color=white)


def tarp2(style):
    SW, SH = 610 * mm, 914 * mm
    X0 = (SW - 2 * A4W) / 2                # 8 mm sides
    top = SH - 37 * mm
    out = os.path.join(HERE, f"tarp-area-signs-2x3ft-{style}.pdf")
    c = canvas.Canvas(out, pagesize=(SW, SH))
    c.setTitle(f"Essentialist Vegetable Farm area signs - tarpaulin 2 x 3 ft ({style})")
    for i, s in enumerate(SIGNS2):
        col, row = i % 2, i // 2
        place(c, X0 + col * A4W, top - (row + 1) * A4H, draw_sign2, s, style)
    gb = top - 3 * A4H                     # bottom of the A4 grid
    by = gb - 20 * mm - QH                 # bin labels row
    for k in range(2):
        place(c, X0 + k * QW, by, draw_bin2, style)
    c.setStrokeColor(black)
    c.setLineWidth(0.3 * mm)
    ln, off = 5 * mm, 1.5 * mm
    side = X0 - off - 1 * mm
    for x in (X0, X0 + A4W, X0 + 2 * A4W):          # A4 columns: marks above and just below the grid
        c.line(x, top + off, x, top + off + ln)
        c.line(x, gb - off, x, gb - off - ln)
    for y in (top, top - A4H, top - 2 * A4H, gb):
        c.line(X0 - off, y, X0 - off - side, y)
        c.line(SW - X0 + off, y, SW - X0 + off + side, y)
    for x in (X0, X0 + QW, X0 + 2 * QW):            # bin labels
        c.line(x, by - off, x, by - off - ln)
        c.line(x, by + QH + off, x, by + QH + off + ln)
    for y in (by, by + QH):
        c.line(X0 - off, y, X0 - off - side, y)
        c.line(X0 + 2 * QW + off, y, X0 + 2 * QW + off + ln, y)
    c.showPage()
    c.save()
    return out


def main2():
    for style in STYLES:
        c = canvas.Canvas(os.path.join(HERE, f"area-signs-a4-{style}.pdf"), pagesize=(A4W, A4H))
        c.setTitle(f"Essentialist Vegetable Farm area signs (A4, {style})")
        for s in SIGNS2:
            draw_sign2(c, s, style)
            c.showPage()
        c.save()
        c = canvas.Canvas(os.path.join(HERE, f"bin-labels-quarter-a4-{style}.pdf"), pagesize=(A4H, A4W))
        c.setTitle(f"Essentialist Vegetable Farm bin labels (quarter A4, {style})")
        for k in range(2):                   # 2 labels on one A4 portrait sheet, top half
            place(c, 0, A4W - (k + 1) * QH, draw_bin2, style)
        c.showPage()
        c.save()
        print(tarp2(style))


# ---- Small labels (quarter A4 crosswise, 210 x 74.25 mm), one shared letter size -------------
SMALL = [
    dict(lines=["BASURA"], sub="(Di nabubulok / Non-biodegradable)"),
    dict(lines=["BASURA"], sub="(Di nabubulok / Non-biodegradable)"),
    dict(lines=["MATATALAS"], sub="(Sharp tools)"),
    dict(lines=["WALANG TALIM"], sub="(Dull tools)"),
    dict(lines=["WASH AREA"], sub="(Soiled)"),
    dict(lines=["WASH AREA"], sub="(Leafy)"),
]


def _small_box():
    m = 7 * mm
    logo_w = 20 * mm
    x = m + 6 * mm + logo_w + 5 * mm
    bx = x + 5 * mm
    return bx, m + 5 * mm, QW - m - 5 * mm - bx, QH - 2 * m - 10 * mm


def _small_sizes():
    bx, by, bw, bh = _small_box()
    cap = 0.72
    size = min(fit(s["lines"][0], bw, 200) for s in SMALL)
    sub = min(fit(s["sub"], bw, size * 0.42) for s in SMALL)
    while size * cap + size * 0.24 + sub * cap > bh:
        size -= 1
        sub = min(sub, size * 0.42)
    return size, sub


SMALL_SIZE, SMALL_SUB = _small_sizes()


def draw_small(c, s, style):
    w, h = QW, QH
    g, brand, _ = STYLES[style]
    ground(c, w, h, style)
    m = 7 * mm
    logo_w = 20 * mm
    logo_h = logo_w / L.LOGO_RATIO
    c.drawImage(LOGOS[style], m + 6 * mm, h / 2 - logo_h / 2, logo_w, logo_h, mask="auto")
    x = m + 6 * mm + logo_w + 5 * mm
    c.setStrokeColor(brand)
    c.setLineWidth(0.6 * mm)
    c.line(x, m + 6 * mm, x, h - m - 6 * mm)
    bx, by, bw, bh = _small_box()
    cap = 0.72
    total = SMALL_SIZE * cap + SMALL_SIZE * 0.24 + SMALL_SUB * cap
    top = by + (bh + total) / 2
    c.setFillColor(white)
    c.setFont(F, SMALL_SIZE)
    c.drawCentredString(bx + bw / 2, top - SMALL_SIZE * cap, s["lines"][0])
    c.setFont(F, SMALL_SUB)
    c.drawCentredString(bx + bw / 2, by + (bh - total) / 2, s["sub"])


def tarp3(style):
    SW, SH = 610 * mm, 914 * mm
    X0 = (SW - 2 * A4W) / 2                # 8 mm sides
    top = SH - 37 * mm
    out = os.path.join(HERE, f"tarp-area-signs-2x3ft-{style}.pdf")
    c = canvas.Canvas(out, pagesize=(SW, SH))
    c.setTitle(f"Essentialist Vegetable Farm area signs and small labels - tarpaulin 2 x 3 ft ({style})")
    for i, s in enumerate(SIGNS2):
        col, row = i % 2, i // 2
        place(c, X0 + col * A4W, top - (row + 1) * A4H, draw_sign2, s, style)
    gb = top - 3 * A4H                     # bottom of the A4 grid
    sy_top = gb - 10 * mm                  # small labels: 2 columns x 3 rows below
    for i, s in enumerate(SMALL):
        col, row = i % 2, i // 2
        place(c, X0 + col * QW, sy_top - (row + 1) * QH, draw_small, s, style)
    sb = sy_top - 3 * QH
    c.setStrokeColor(black)
    c.setLineWidth(0.3 * mm)
    ln, off = 5 * mm, 1.5 * mm
    side = X0 - off - 1 * mm
    short = 3 * mm                          # marks in the 10 mm gap between blocks
    for x in (X0, X0 + A4W, X0 + 2 * A4W):
        c.line(x, top + off, x, top + off + ln)
        c.line(x, gb - off, x, gb - off - short)
    for y in (top, top - A4H, top - 2 * A4H, gb):
        c.line(X0 - off, y, X0 - off - side, y)
        c.line(SW - X0 + off, y, SW - X0 + off + side, y)
    for x in (X0, X0 + QW, X0 + 2 * QW):
        c.line(x, sy_top + off, x, sy_top + off + short)
        c.line(x, sb - off, x, sb - off - ln)
    for k in range(4):
        y = sy_top - k * QH
        c.line(X0 - off, y, X0 - off - side, y)
        c.line(X0 + 2 * QW + off, y, X0 + 2 * QW + off + ln, y)
    c.showPage()
    c.save()
    return out


def main3():
    for style in STYLES:
        c = canvas.Canvas(os.path.join(HERE, f"area-signs-a4-{style}.pdf"), pagesize=(A4W, A4H))
        c.setTitle(f"Essentialist Vegetable Farm area signs (A4, {style})")
        for s in SIGNS2:
            draw_sign2(c, s, style)
            c.showPage()
        c.save()
        c = canvas.Canvas(os.path.join(HERE, f"small-labels-quarter-a4-{style}.pdf"), pagesize=(A4H, A4W))
        c.setTitle(f"Essentialist Vegetable Farm small labels (quarter A4, {style})")
        for p in range(0, len(SMALL), 4):    # 4 labels per A4 portrait page, cut crosswise
            for k, s in enumerate(SMALL[p:p + 4]):
                place(c, 0, A4W - (k + 1) * QH, draw_small, s, style)
            c.showPage()
        c.save()
        print(tarp3(style))


if __name__ == "__main__":
    main3()
