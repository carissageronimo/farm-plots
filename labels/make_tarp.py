"""All 14 A5 plot labels on one 2 x 3 ft tarpaulin sheet, at actual size, with cut marks.

Sheet: 2 ft x 3 ft (610 x 914 mm), portrait. Labels are turned sideways
(148 mm across, 210 mm down) in a 4 x 4 grid that shares cut lines, so cutting
straight across and down on the marks gives 16 pieces of exactly A5:
14 plot labels, 1 print note, 1 blank spare.

    python3 make_tarp.py            black and white
    python3 make_tarp.py --color    colour (deep brown band)
"""
import os
import sys
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
import make_labels as L

HERE = os.path.dirname(os.path.abspath(__file__))
SW, SH = 610 * mm, 914 * mm            # 2 ft x 3 ft
COLS, ROWS = 4, 4
CW, CH = L.H, L.W                      # cell = A5 turned sideways: 148 x 210 mm
X0 = (SW - COLS * CW) / 2              # 9 mm side margins
Y0 = (SH - ROWS * CH) / 2              # 37 mm top/bottom margins


def cut_marks(c, ln=5 * mm, off=1.5 * mm):
    """Ticks in the margins, in line with every cut."""
    c.setLineWidth(0.3 * mm)
    side = min(ln, X0 - off - 1 * mm)
    for i in range(COLS + 1):
        x = X0 + i * CW
        c.line(x, Y0 - off, x, Y0 - off - ln)
        c.line(x, SH - Y0 + off, x, SH - Y0 + off + ln)
    for j in range(ROWS + 1):
        y = Y0 + j * CH
        c.line(X0 - off, y, X0 - off - side, y)
        c.line(SW - X0 + off, y, SW - X0 + off + side, y)


def cell_origin(i):
    col, row = i % COLS, i // COLS
    return X0 + col * CW, SH - Y0 - (row + 1) * CH


def main(color=False):
    out = os.path.join(HERE, "tarp-plot-labels-2x3ft" + ("-color" if color else "") + ".pdf")
    c = canvas.Canvas(out, pagesize=(SW, SH))
    c.setTitle("Essentialist Vegetable Farm plot labels - tarpaulin sheet 2 x 3 ft")
    for i, code in enumerate(L.PLOTS):
        x, y = cell_origin(i)
        c.saveState()
        c.translate(x + CW, y)          # label turned 90 degrees, reads bottom to top
        c.rotate(90)
        L.draw_label(c, code, scan_size=13, color=color)
        c.restoreState()
    # Print note in slot 15; slot 16 left blank as a spare
    x, y = cell_origin(14)
    c.saveState()
    c.translate(x + CW, y)
    c.rotate(90)
    c.setFont("ArchivoBlack", 14)
    lines = ["Essentialist Vegetable Farm", "14 plot labels, A5 (210 x 148 mm)",
             "Tarp 2 x 3 ft. Print at 100% actual size.", "Cut straight on the marks."]
    for j, t in enumerate(lines):
        c.drawString(12 * mm, L.H - 30 * mm - j * 10 * mm, t)
    c.restoreState()
    cut_marks(c)
    c.showPage()
    c.save()
    print(out)


if __name__ == "__main__":
    main(color="--color" in sys.argv)
