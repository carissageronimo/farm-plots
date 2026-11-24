"""Build A5 landscape plot labels (one PDF per plot + one combined PDF)."""
import os
from PIL import Image
from reportlab.lib.pagesizes import A5, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.lib.utils import ImageReader

FONT_DIR = "/usr/share/fonts/truetype/google-fonts/ofl/archivoblack/ArchivoBlack-Regular.ttf"
pdfmetrics.registerFont(TTFont("ArchivoBlack", FONT_DIR))

BASE = "https://carissageronimo.github.io/farm-plots/#"
PLOTS = [f"{l}{n}" for l in "ABCDEFG" for n in (1, 2)]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

# Black-and-white logo: flatten alpha onto white, convert to greyscale.
HERE = os.path.dirname(os.path.abspath(__file__))
src = Image.open(os.path.join(HERE, "logo.png")).convert("RGBA")
bg = Image.new("RGBA", src.size, "white")
bg.alpha_composite(src)
grey = bg.convert("L").point(lambda v: 0 if v < 200 else 255)
grey = grey.resize((grey.width * 4, grey.height * 4), Image.LANCZOS)
grey.save(os.path.join(HERE, "logo_bw.png"))
LOGO = ImageReader(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_bw.png"))
LOGO_RATIO = src.width / src.height

W, H = landscape(A5)  # 210 x 148 mm


def draw_label(c, code, scan_size=11):
    # Thick border
    m = 6 * mm
    c.setLineWidth(3 * mm)
    c.rect(m, m, W - 2 * m, H - 2 * m)
    inner_l, inner_r = m + 7 * mm, W - m - 7 * mm
    inner_t, inner_b = H - m - 6 * mm, m + 6 * mm

    # Header: logo + farm name
    logo_h = 22 * mm
    logo_w = logo_h * LOGO_RATIO
    c.drawImage(LOGO, inner_l, inner_t - logo_h, logo_w, logo_h, mask="auto")
    name = "Essentialist Vegetable Farm"
    size = 26
    max_w = inner_r - (inner_l + logo_w + 5 * mm)
    while pdfmetrics.stringWidth(name, "ArchivoBlack", size) > max_w:
        size -= 0.5
    c.setFont("ArchivoBlack", size)
    c.drawString(inner_l + logo_w + 5 * mm, inner_t - logo_h / 2 - size * 0.35, name)

    # Rule under header
    rule_y = inner_t - logo_h - 3 * mm
    c.setLineWidth(1.2 * mm)
    c.line(inner_l, rule_y, inner_r, rule_y)

    # QR code, 86 mm, right side
    qs = 86 * mm
    qx = inner_r - qs
    qy = inner_b + 7 * mm
    w = qr.QrCodeWidget(BASE + code.lower(), barLevel="Q")
    b = w.getBounds()
    bw, bh = b[2] - b[0], b[3] - b[1]
    d = Drawing(qs, qs, transform=[qs / bw, 0, 0, qs / bh, 0, 0])
    d.add(w)
    renderPDF.draw(d, c, qx, qy)

    # Huge plot code, left side, fitted to the space
    area_w = qx - inner_l - 6 * mm
    area_top = rule_y - 4 * mm
    area_bot = inner_b + 7 * mm
    area_h = area_top - area_bot
    size = 400
    face = pdfmetrics.getFont("ArchivoBlack").face
    cap = 0.72  # approx cap height ratio for Archivo Black
    while (pdfmetrics.stringWidth(code, "ArchivoBlack", size) > area_w
           or size * cap > area_h):
        size -= 2
    tw = pdfmetrics.stringWidth(code, "ArchivoBlack", size)
    c.setFont("ArchivoBlack", size)
    c.drawString(inner_l + (area_w - tw) / 2,
                 area_bot + (area_h - size * cap) / 2, code)

    # Scan line, small, under the QR
    line = "Scan to see what is growing here"
    while pdfmetrics.stringWidth(line, "ArchivoBlack", scan_size) > qs:
        scan_size -= 0.25
    c.setFont("ArchivoBlack", scan_size)
    lw = pdfmetrics.stringWidth(line, "ArchivoBlack", scan_size)
    c.drawString(qx + (qs - lw) / 2, inner_b + 1 * mm, line)


def main():
    combined = canvas.Canvas(f"{OUT}/all-plot-labels.pdf", pagesize=(W, H))
    combined.setTitle("Essentialist Vegetable Farm plot labels")
    for code in PLOTS:
        c = canvas.Canvas(f"{OUT}/{code}.pdf", pagesize=(W, H))
        c.setTitle(f"Plot {code} label")
        draw_label(c, code)
        c.showPage()
        c.save()
        draw_label(combined, code)
        combined.showPage()
    combined.save()
    print("done", len(PLOTS))


if __name__ == "__main__":
    main()
