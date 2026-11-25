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


def text_block(c, lines, sub, x, y, w, h, sub_ratio=0.5, gap_ratio=0.22):
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
    c.setFillColor(black)
    c.setFont(F, size)
    for i, t in enumerate(lines):
        base = top - size * cap - i * size * (cap + 0.28)
        c.drawCentredString(x + w / 2, base, t)
    if sub:
        c.setFont(F, sub_size)
        c.drawCentredString(x + w / 2, y + (h - total) / 2, sub)


def no_smoking(c, cx, cy, r):
    """Universal no-smoking symbol: cigarette under a red circle and slash."""
    c.saveState()
    # cigarette
    lw, lh = r * 1.35, r * 0.24
    x0, y0 = cx - lw / 2, cy - lh / 2
    c.setFillColor(white)
    c.setStrokeColor(black)
    c.setLineWidth(r * 0.05)
    c.rect(x0, y0, lw, lh, fill=1, stroke=1)
    c.setFillColor(black)
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


def tarp():
    SW, SH = 610 * mm, 914 * mm
    X0 = (SW - 2 * A4W) / 2                 # 8 mm sides
    gh = 3 * A4H + 2 * BH                   # 840 mm
    Y0 = (SH - gh) / 2                      # 37 mm top/bottom
    out = os.path.join(HERE, "tarp-area-signs-2x3ft.pdf")
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
            place(c, x, y, draw_sign, s)
        else:
            place(c, x, y, draw_bin)
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


if __name__ == "__main__":
    main()
