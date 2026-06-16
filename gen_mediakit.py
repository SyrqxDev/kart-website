#!/usr/bin/env python3
"""Generate a one-page Tristan Sharpe media kit (A4 portrait) for quick sponsor sharing."""
import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import Color, HexColor

PINK = HexColor("#ff3ea5")
PURPLE = HexColor("#a23cff")
DARK = HexColor("#0c0a12")
PANEL = HexColor("#17131f")
WHITE = HexColor("#ffffff")
MUTED = HexColor("#c9c4d6")

W, H = A4  # 595 x 842 pt portrait
os.makedirs("marketing", exist_ok=True)
TMP = "/tmp/mediakit"
os.makedirs(TMP, exist_ok=True)


def gcolor(t):
    return Color(PINK.red + (PURPLE.red - PINK.red) * t,
                 PINK.green + (PURPLE.green - PINK.green) * t,
                 PINK.blue + (PURPLE.blue - PINK.blue) * t)


def grad_rect(c, x, y, w, h):
    seg = 40
    for s in range(seg):
        c.setFillColor(gcolor(s / (seg - 1)))
        c.rect(x + (w / seg) * s, y, w / seg + 0.6, h, stroke=0, fill=1)


def hero_image(src, tw, th, out):
    im = Image.open(src).convert("RGB")
    s = max(tw / im.width, th / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    x = (im.width - tw) // 2
    y = (im.height - th) // 2
    im = im.crop((x, y, x + tw, y + th))
    # darken for legibility
    from PIL import ImageDraw
    ov = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for j in range(th):
        a = int(60 + 150 * (j / th) ** 1.4)
        d.line([(0, j), (tw, j)], fill=(8, 6, 14, a))
    im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    im.save(out, quality=88)


def wrap(c, text, font, size, max_w):
    c.setFont(font, size)
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if c.stringWidth(t, font, size) <= max_w:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


c = canvas.Canvas("marketing/Media Kit.pdf", pagesize=A4)
c.setFillColor(DARK)
c.rect(0, 0, W, H, stroke=0, fill=1)

# ---- HERO ----
hero_h = 250
hero_image("images/IMG_0310.jpg", int(W * 2), int(hero_h * 2), f"{TMP}/hero.jpg")
c.drawImage(f"{TMP}/hero.jpg", 0, H - hero_h, W, hero_h)
M = 42
# accent bar
grad_rect(c, M, H - 92, 90, 7)
c.setFillColor(WHITE)
c.setFont("Helvetica-Bold", 40)
c.drawString(M - 2, H - 138, "TRISTAN SHARPE")
c.setFillColor(PINK)
c.setFont("Helvetica-Bold", 13)
c.drawString(M, H - 162, "KARTING DRIVER  ·  #95  ·  SENIOR ROTAX")
c.setFillColor(MUTED)
c.setFont("Helvetica", 11)
c.drawString(M, H - 180, "George Whitbread Racing (GWR)  ·  National Championships")
c.setFont("Helvetica-Bold", 12)
c.setFillColor(WHITE)
c.drawString(M, H - 222, "Sponsorship & partnership opportunities")

y = H - hero_h - 28

# ---- REACH STATS ----
stats = [("1.3K+", "Combined followers"), ("51K+", "Views / platforms"),
         ("6", "Race rounds"), ("Global", "Live broadcast")]
gap = 12
cw = (W - 2 * M - gap * 3) / 4
ch = 70
for i, (val, lbl) in enumerate(stats):
    x = M + i * (cw + gap)
    grad_rect(c, x, y - ch, cw, ch)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 21)
    c.drawCentredString(x + cw / 2, y - 32, val)
    c.setFont("Helvetica", 8)
    c.drawCentredString(x + cw / 2, y - ch + 14, lbl)
y -= ch + 30

# ---- WHERE YOUR BRAND APPEARS ----
c.setFillColor(WHITE)
c.setFont("Helvetica-Bold", 15)
c.drawString(M, y, "Where your brand appears")
y -= 22
zones = ["Kart bodywork", "Helmet", "Race suit", "Van & trailer", "Social media", "Live streams"]
cx, chip_y = M, y - 22
c.setFont("Helvetica-Bold", 9.5)
for z in zones:
    w = c.stringWidth(z, "Helvetica-Bold", 9.5) + 26
    if cx + w > W - M:
        cx = M; chip_y -= 34
    c.setStrokeColor(PINK); c.setLineWidth(1)
    c.setFillColor(PANEL)
    c.roundRect(cx, chip_y, w, 24, 7, stroke=1, fill=1)
    c.setFillColor(WHITE)
    c.drawString(cx + 13, chip_y + 8, z)
    cx += w + 9
y = chip_y - 28

# ---- WHY IT WORKS ----
c.setFillColor(WHITE)
c.setFont("Helvetica-Bold", 15)
c.drawString(M, y, "Why partner with Tristan")
y -= 20
points = [
    "A dedicated, professional young driver competing at national level.",
    "Genuine exposure on track and across an engaged social audience.",
    "Races live-streamed to a worldwide audience on YouTube & Facebook.",
    "Flexible support — from a single race to a full season, or in-kind.",
    "Sponsorship is a marketing expense and is typically tax-deductible.",
]
c.setFont("Helvetica", 10.5)
for p in points:
    c.setFillColor(PINK); c.setFont("Helvetica-Bold", 11)
    c.drawString(M, y - 10, "›")
    c.setFillColor(MUTED); c.setFont("Helvetica", 10.5)
    for ln in wrap(c, p, "Helvetica", 10.5, W - 2 * M - 16):
        c.drawString(M + 16, y - 10, ln); y -= 14
    y -= 4
y -= 8

# ---- SUPPORT FROM ----
sup_h = 56
grad_rect(c, M, y - sup_h, W - 2 * M, sup_h)
c.setFillColor(WHITE)
c.setFont("Helvetica-Bold", 16)
c.drawString(M + 18, y - 26, "Support from £170")
c.setFont("Helvetica", 10.5)
c.drawString(M + 18, y - 44, "Fund a day, a set of tyres, a weekend or a full season — tailored packages welcome.")
y -= sup_h + 28

# ---- CONTACT ----
c.setStrokeColor(HexColor("#232838")); c.setLineWidth(1)
c.line(M, y, W - M, y)
y -= 22
c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 12)
c.drawString(M, y, "contact@tristansharpe.uk")
c.setFillColor(MUTED); c.setFont("Helvetica", 10.5)
c.drawString(M, y - 16, "tristansharpe.uk   ·   Instagram @tristansharpe193   ·   TikTok @tristan.sharpe.racing")

c.showPage()
c.save()
print("Saved marketing/Media Kit.pdf")
