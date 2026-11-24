"""All 14 A5 plot labels on one tarpaulin sheet, at actual size, with cut marks.

Sheet: 2.5 ft x 3 ft (762 x 914 mm), 3 columns x 5 rows of 210 x 148 mm labels.
Cut along the crop marks: each piece comes out exactly A5 landscape.
"""
import os
import sys
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
import make_labels as L

HERE = os.path.dirname(os.path.abspath(__file__))
SW, SH = 762 * mm, 914 * mm          # 2.5 ft x 3 ft
COLS, ROWS, GAP = 3, 5, 12 * mm
LW, LH = L.W, L.H                    # 210 x 148 mm
gw = COLS * LW + (COLS - 1) * GAP
gh = ROWS * LH + (ROWS - 1) * GAP
X0, Y0 = (SW - gw) / 2, (SH - gh) / 2


def crop_marks(c, x, y, w, h, ln=5 * mm, off=1.5 * mm):
    c.setLineWidth(0.3 * mm)
    for cx, sx in ((x, -1), (x + w, 1)):
        for cy, sy in ((y, -1), (y + h, 1)):
            c.line(cx + sx * off, cy, cx + sx * (off + ln), cy)   # horizontal tick
            c.line(cx, cy + sy * off, cx, cy + sy * (off + ln))   # vertical tick


def main(color=False):
    out = os.path.join(HERE, "tarp-plot-labels-2.5x3ft" + ("-color" if color else "") + ".pdf")
    c = canvas.Canvas(out, pagesize=(SW, SH))
    c.setTitle("Essentialist Vegetable Farm plot labels - tarpaulin sheet 2.5 x 3 ft")
    for i, code in enumerate(L.PLOTS):
        col, row = i % COLS, i // COLS
        x = X0 + col * (LW + GAP)
        y = SH - Y0 - (row + 1) * LH - row * GAP
        c.saveState()
        c.translate(x, y)
        L.draw_label(c, code, scan_size=13, color=color)
        c.restoreState()
        crop_marks(c, x, y, LW, LH)
    # Note in the empty 15th slot
    x = X0 + 2 * (LW + GAP)
    y = SH - Y0 - 5 * LH - 4 * GAP
    c.setFont("ArchivoBlack", 14)
    lines = ["Essentialist Vegetable Farm", "14 plot labels, A5 (210 x 148 mm)",
             "Print at 100% actual size.", "Cut on the crop marks."]
    for j, t in enumerate(lines):
        c.drawString(x + 8 * mm, y + LH - 25 * mm - j * 9 * mm, t)
    c.showPage()
    c.save()
    print(out)


if __name__ == "__main__":
    main(color="--color" in sys.argv)
