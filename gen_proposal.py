#!/usr/bin/env python3
"""Generate Tristan Sharpe sponsorship proposal PDF in GWR pink/purple theme."""
import os
from PIL import Image, ImageDraw, ImageFilter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, HexColor

# ---- Theme ----
PINK = HexColor("#ff3ea5")
PURPLE = HexColor("#a23cff")
DARK = HexColor("#0c0a12")
WHITE = HexColor("#ffffff")
MUTED = HexColor("#c9c4d6")

PINK_RGB = (255, 62, 165)
PURPLE_RGB = (162, 60, 255)
DARK_RGB = (12, 10, 18)

# 16:9 page (PowerPoint widescreen) in points
PW, PH = 960.0, 540.0
SCALE = 2  # render backgrounds at 2x for crispness
IW, IH = int(PW * SCALE), int(PH * SCALE)

IMG = "images"
TMP = "/tmp/proposal_bg"
os.makedirs(TMP, exist_ok=True)


def cover_crop(im, tw, th):
    """Resize+crop image to exactly fill tw x th (cover)."""
    im = im.convert("RGB")
    s = max(tw / im.width, th / im.height)
    nw, nh = int(im.width * s + 1), int(im.height * s + 1)
    im = im.resize((nw, nh), Image.LANCZOS)
    x = (nw - tw) // 2
    y = (nh - th) // 2
    return im.crop((x, y, x + tw, y + th))


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def make_bg(photo, out, mode="side"):
    """Compose a themed background: photo + gradient/tint overlay.
    mode='side'  -> dark panel on the left for text
    mode='cover' -> bottom-up dark fade + diagonal pink/purple tint
    mode='plain' -> full dark themed gradient (no photo), for table pages
    """
    if mode == "plain":
        base = Image.new("RGB", (IW, IH), DARK_RGB)
        ov = Image.new("RGB", (IW, IH))
        px = ov.load()
        for y in range(IH):
            for_x_step = 1
        # diagonal subtle gradient dark purple -> dark
        for y in range(0, IH, 2):
            t = y / IH
            col = lerp((18, 10, 28), (10, 9, 16), t)
            for x in range(0, IW, 2):
                tx = x / IW
                c = lerp(col, (22, 12, 30), tx * 0.5)
                px[x, y] = c
                if x + 1 < IW: px[x + 1, y] = c
            if y + 1 < IH:
                for x in range(0, IW, 2):
                    px[x, y + 1] = px[x, y]
                    if x + 1 < IW: px[x + 1, y + 1] = px[x, y]
        base = ov
        base.save(out, quality=90)
        return

    im = Image.open(os.path.join(IMG, photo))
    base = cover_crop(im, IW, IH)

    overlay = Image.new("RGBA", (IW, IH), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)

    if mode == "cover":
        # bottom-up dark fade for title legibility
        for y in range(IH):
            t = y / IH
            a = int(40 + 200 * (t ** 1.6))  # darker toward bottom
            od.line([(0, y), (IW, y)], fill=(8, 6, 14, a))
        # diagonal pink->purple tint band
        tint = Image.new("RGBA", (IW, IH), (0, 0, 0, 0))
        td = ImageDraw.Draw(tint)
        for x in range(0, IW, 2):
            t = x / IW
            c = lerp(PINK_RGB, PURPLE_RGB, t)
            td.line([(x, 0), (x, IH)], fill=(c[0], c[1], c[2], 55))
        overlay = Image.alpha_composite(overlay, tint)
    else:  # side panel
        # left panel solid-ish dark with pink tint, fading to transparent on right
        panel_w = int(IW * 0.52)
        for x in range(IW):
            if x < panel_w:
                a = 235
            else:
                # fade out
                fade = max(0, 1 - (x - panel_w) / (IW * 0.28))
                a = int(235 * fade)
            tintc = lerp(DARK_RGB, (26, 12, 30), 0.6)
            od.line([(x, 0), (x, IH)], fill=(tintc[0], tintc[1], tintc[2], a))
        # subtle pink->purple glow strip at top of panel
        glow = Image.new("RGBA", (IW, IH), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        for x in range(0, panel_w, 2):
            t = x / panel_w
            c = lerp(PINK_RGB, PURPLE_RGB, t)
            gd.line([(x, 0), (x, 14 * SCALE)], fill=(c[0], c[1], c[2], 230))
        overlay = Image.alpha_composite(overlay, glow)

    base = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
    base.save(out, quality=88)


# ---- Canvas helpers ----
def accent_bar(c, x, y, w=90, h=8):
    """Pink->purple gradient bar drawn as segments."""
    n = 40
    for i in range(n):
        t = i / (n - 1)
        col = Color(
            (PINK.red + (PURPLE.red - PINK.red) * t),
            (PINK.green + (PURPLE.green - PINK.green) * t),
            (PINK.blue + (PURPLE.blue - PINK.blue) * t),
        )
        c.setFillColor(col)
        c.rect(x + (w / n) * i, y, w / n + 0.5, h, stroke=0, fill=1)


def wrap(c, text, font, size, max_w):
    c.setFont(font, size)
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if c.stringWidth(test, font, size) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_paragraph(c, text, x, y, font, size, leading, max_w, color=WHITE):
    c.setFillColor(color)
    for ln in wrap(c, text, font, size, max_w):
        c.setFont(font, size)
        c.drawString(x, y, ln)
        y -= leading
    return y


def kicker(c, num, label, x, y):
    accent_bar(c, x, y + 22, 70, 7)
    c.setFillColor(PINK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, y, f"{num} — {label}".upper())


def text_page(c, bgfile, num, kick, title_lines, body, side="left"):
    c.drawImage(bgfile, 0, 0, PW, PH)
    x = 70 if side == "left" else PW - 70 - 360
    y = PH - 90
    kicker(c, num, kick, x, y)
    y -= 30
    c.setFillColor(WHITE)
    for tl in title_lines:
        c.setFont("Helvetica-Bold", 40)
        c.drawString(x, y - 34, tl)
        y -= 44
    y -= 16
    for para in body:
        y = draw_paragraph(c, para, x, y, "Helvetica", 14.5, 21, 380, MUTED)
        y -= 12


def cost_page(c, num, title_lines, rows):
    c.drawImage(f"{TMP}/plain.jpg", 0, 0, PW, PH)
    # heading block on right
    hx = PW - 300
    kicker(c, num, "Seasonal Costs", hx, PH - 80)
    c.setFillColor(WHITE)
    yy = PH - 110
    for tl in title_lines:
        c.setFont("Helvetica-Bold", 34)
        c.drawString(hx, yy - 30, tl)
        yy -= 40

    # table on left
    tx, tw = 55, 580
    c1, c2, c3 = 150, 300, 130  # column widths
    top = PH - 70
    # header
    hh = 30
    c.setFillColor(DARK)
    for cx, cw, lbl in [(tx, c1, "ITEM"), (tx + c1 + 6, c2, "DESCRIPTION"), (tx + c1 + c2 + 12, c3, "PRICE")]:
        c.setFillColor(HexColor("#000000"))
        c.rect(cx, top - hh, cw, hh, stroke=0, fill=1)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(cx + cw / 2, top - hh + 9, lbl)

    y = top - hh - 8
    n = len(rows)
    avail = y - 30
    rh = min(74, avail / max(n, 1) - 8)
    for i, (item, desc, price) in enumerate(rows):
        cy = y - rh
        # ITEM cell: pink->purple gradient
        seg = 30
        for s in range(seg):
            t = s / (seg - 1)
            col = Color(PINK.red + (PURPLE.red - PINK.red) * t,
                        PINK.green + (PURPLE.green - PINK.green) * t,
                        PINK.blue + (PURPLE.blue - PINK.blue) * t)
            c.setFillColor(col)
            c.rect(tx + (c1 / seg) * s, cy, c1 / seg + 0.5, rh, stroke=0, fill=1)
        # DESCRIPTION cell: dark panel
        c.setFillColor(HexColor("#17131f"))
        c.rect(tx + c1 + 6, cy, c2, rh, stroke=0, fill=1)
        # PRICE cell: purple
        c.setFillColor(PURPLE)
        c.rect(tx + c1 + c2 + 12, cy, c3, rh, stroke=0, fill=1)

        # texts
        c.setFillColor(WHITE)
        for ln_i, ln in enumerate(wrap(c, item, "Helvetica-Bold", 11.5, c1 - 14)):
            c.setFont("Helvetica-Bold", 11.5)
            c.drawCentredString(tx + c1 / 2, cy + rh / 2 + 4 - ln_i * 13 +
                                (len(wrap(c, item, 'Helvetica-Bold', 11.5, c1 - 14)) - 1) * 6.5, ln)
        # desc
        dlines = wrap(c, desc, "Helvetica", 8.8, c2 - 16)
        dy = cy + rh / 2 + (len(dlines) - 1) * 5.2
        c.setFillColor(MUTED)
        for ln in dlines:
            c.setFont("Helvetica", 8.8)
            c.drawString(tx + c1 + 14, dy, ln)
            dy -= 10.4
        # price
        c.setFillColor(WHITE)
        plines = wrap(c, price, "Helvetica-Bold", 10, c3 - 12)
        py = cy + rh / 2 + 3 + (len(plines) - 1) * 6
        for ln in plines:
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(tx + c1 + c2 + 12 + c3 / 2, py, ln)
            py -= 12
        y = cy - 8


def brand_page(c, num, reach, zones):
    """Brand exposure page: reach stat cards + branding placement chips."""
    c.drawImage(f"{TMP}/plain.jpg", 0, 0, PW, PH)
    x = 70
    kicker(c, num, "Brand Exposure", x, PH - 70)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 40)
    c.drawString(x, PH - 118, "Your brand's reach")

    # reach stat cards (wrap into rows of up to `per_row`)
    n = len(reach)
    per_row = n if n <= 4 else 3
    gap = 18
    cw = (PW - 2 * x - gap * (per_row - 1)) / per_row
    ch = 84
    top = PH - 220
    rows = (n + per_row - 1) // per_row
    for i, (val, lbl) in enumerate(reach):
        r, col_i = divmod(i, per_row)
        cx = x + col_i * (cw + gap)
        cy = top - r * (ch + gap)
        # gradient card
        seg = 40
        for s in range(seg):
            t = s / (seg - 1)
            col = Color(PINK.red + (PURPLE.red - PINK.red) * t,
                        PINK.green + (PURPLE.green - PINK.green) * t,
                        PINK.blue + (PURPLE.blue - PINK.blue) * t)
            c.setFillColor(col)
            c.rect(cx + (cw / seg) * s, cy, cw / seg + 0.5, ch, stroke=0, fill=1)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(cx + cw / 2, cy + ch - 40, val)
        c.setFont("Helvetica", 11)
        for li, ln in enumerate(wrap(c, lbl, "Helvetica", 11, cw - 16)):
            c.drawCentredString(cx + cw / 2, cy + 22 - li * 12, ln)

    bottom = top - (rows - 1) * (ch + gap)
    # placement
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(x, bottom - 44, "Where your branding appears")
    # chips
    chip_y = bottom - 92
    cx = x
    c.setFont("Helvetica-Bold", 12)
    for z in zones:
        w = c.stringWidth(z, "Helvetica-Bold", 12) + 36
        if cx + w > PW - x:
            cx = x
            chip_y -= 50
        c.setStrokeColor(PINK)
        c.setFillColor(HexColor("#17131f"))
        c.setLineWidth(1.4)
        c.roundRect(cx, chip_y, w, 36, 10, stroke=1, fill=1)
        c.setFillColor(WHITE)
        c.drawString(cx + 18, chip_y + 12, z)
        cx += w + 14


# ============ BUILD ============
print("Composing backgrounds...")
make_bg("IMG_0310.jpg", f"{TMP}/cover.jpg", "cover")
make_bg("IMG_0303.jpg", f"{TMP}/about.jpg", "side")
make_bg("IMG_0179.jpg", f"{TMP}/why.jpg", "side")
make_bg("IMG_0276.jpg", f"{TMP}/return.jpg", "side")
make_bg("IMG_0674.jpg", f"{TMP}/helps.jpg", "side")
make_bg("IMG_0660.jpg", f"{TMP}/thanks.jpg", "cover")
make_bg(None, f"{TMP}/plain.jpg", "plain")

print("Building PDF...")
c = canvas.Canvas("Sponsorship Proposal.pdf", pagesize=(PW, PH))

# --- Page 1: Cover ---
c.drawImage(f"{TMP}/cover.jpg", 0, 0, PW, PH)
accent_bar(c, 70, PH - 150, 120, 9)
c.setFillColor(WHITE)
c.setFont("Helvetica-Bold", 78)
c.drawString(66, PH - 235, "TRISTAN")
c.drawString(66, PH - 305, "SHARPE")
c.setFillColor(PINK)
c.setFont("Helvetica-Bold", 20)
c.drawString(70, 150, "KARTING DRIVER · #95")
c.setFillColor(WHITE)
c.setFont("Helvetica-Bold", 30)
c.drawString(70, 105, "Sponsorship Proposal")
c.setFillColor(MUTED)
c.setFont("Helvetica", 13)
c.drawString(70, 78, "George Whitbread Racing (GWR)  ·  Senior Rotax  ·  National Championships")
c.showPage()

# --- Page 2: About ---
text_page(c, f"{TMP}/about.jpg", "01", "About",
          ["About Tristan"],
          ["Tristan Sharpe, 18, from Nottinghamshire, discovered his passion for motorsport at an "
           "early age and developed his talent at his local kart tracks. From the outset he showed "
           "real promise, consistently finishing inside the top five.",
           "After building his race craft and experience over several seasons, Tristan progressed "
           "into owner-driver karting — beginning in four-stroke machinery before stepping up to the "
           "more demanding two-stroke category, where he regularly finished on the podium at local "
           "events.",
           "Today he competes against a high level of national competition, racing in Senior Rotax "
           "for George Whitbread Racing (GWR)."])
c.showPage()

# --- Page 3: Why ---
text_page(c, f"{TMP}/why.jpg", "02", "The Goal",
          ["Why sponsorship?"],
          ["Tristan is seeking sponsorship to help fund his karting career and deliver strong results "
           "for himself and his team. Support contributes directly to essentials such as engine hire "
           "and chassis maintenance, ensuring reliability and competitiveness on track.",
           "This backing supports his full racing programme — from national-level events to the "
           "championships he contests across the local region."])
c.showPage()

# --- Page 4: Return ---
text_page(c, f"{TMP}/return.jpg", "03", "Partnership",
          ["What you get", "in return"],
          ["In return for your support, your brand will be represented across the bodywork of the "
           "kart, Tristan's helmet, the race van and trailer, his race suit, and throughout his "
           "social media content on Instagram, TikTok and beyond.",
           "Tristan's races are live-streamed on YouTube and Facebook, reaching a worldwide audience "
           "and delivering valuable exposure for your business. As a partner, you'll also be invited "
           "to experience a race weekend trackside, with access to the team's hospitality area."])
c.showPage()

# --- Page 4b: Brand Exposure (reach + placement) ---
reach_stats = [
    ("1.3K+", "Combined followers"),
    ("51K+", "Views across platforms"),
    ("6", "Races per season"),
    ("Global", "YouTube & Facebook live"),
]
placement_zones = [
    "Helmet", "Race Suit", "Kart Side Pods", "Nose Cone",
    "Rear Bumper", "Race Van & Trailer", "Social Media Posts",
]
brand_page(c, "04", reach_stats, placement_zones)
c.showPage()

# --- Page 5: Helps ---
text_page(c, f"{TMP}/helps.jpg", "05", "Your Impact",
          ["What it helps", "Tristan with"],
          ["Every contribution goes directly towards the season's running costs: fuel, race and "
           "practice entry fees, spare parts, engines and maintenance, racing gear (helmets, "
           "graphics, suits, gloves and boots), tyres and team fees.",
           "The following pages provide a breakdown of the seasonal costs. You're welcome to cover "
           "one or more of these areas, or to discuss an alternative arrangement that suits your "
           "business. Any level of support is genuinely appreciated."])
c.showPage()

# --- Pages 6-8: Costs ---
costs1 = [
    ("TEAM FEE", "Covers team mechanics, data, fuel and coaching. A normal weekend is 3 days, Friday to Sunday.", "£170 per day / £510 a weekend over 6 weekends"),
    ("ENGINE HIRE FEE", "Covers the engine hired from the team and used over the course of the weekend.", "£150 a day over 3 days / 6 weekends"),
    ("TYRES", "Covers race/practice tyres — essential for Tristan to practice for his races.", "£220 per set"),
    ("TRACK TEST DAY FEE", "Covers the track fee per driver to test for the day.", "£100 per day"),
    ("TEAM TEST DAY FEE", "A test day with the team, including mechanics, fuel, coaching, data and the track day fee.", "£300 per day"),
]
costs2 = [
    ("KART MAINTENANCE", "Covers maintaining the kart and engine to ensure maximum results on track.", "£150 per service"),
    ("DAMAGE FEE", "Covers any damage caused at a race — an on-track incident resulting in a part being replaced.", "Up to £500 per weekend"),
    ("PROTECTIVE GEAR", "Race gear kept to standard: suits, gloves, boots, helmets, rib protectors and any custom designs (helmet paint, kart graphics, suit printing).", "Price may vary"),
    ("ENGINE MAINTENANCE", "Covers the engine being maintained for optimum performance.", "£750 per rebuild"),
    ("CHAMPIONSHIP COSTS", "Covers the championship Tristan races in; prices vary by championship and can be discussed.", "£1700 (price may vary)"),
]
costs3 = [
    ("SPARES", "Covers any spares needed after a race weekend or to prepare for a race weekend / test day.", "£350 per day over 3 days (price may vary)"),
]
cost_page(c, "06", ["Seasonal", "Costs (1)"], costs1); c.showPage()
cost_page(c, "06", ["Seasonal", "Costs (2)"], costs2); c.showPage()
cost_page(c, "06", ["Seasonal", "Costs (3)"], costs3); c.showPage()

# --- Page 9: Thank you ---
c.drawImage(f"{TMP}/thanks.jpg", 0, 0, PW, PH)
accent_bar(c, 70, PH - 150, 120, 9)
c.setFillColor(WHITE)
c.setFont("Helvetica-Bold", 60)
c.drawString(66, PH - 215, "Thank You!")
draw_paragraph(c, "Thank you for taking the time to consider this proposal. I would welcome the "
               "opportunity to discuss a partnership and work together over the coming season.",
               70, PH - 260, "Helvetica", 16, 24, 460, MUTED)
c.setFillColor(PINK)
c.setFont("Helvetica-Bold", 16)
c.drawString(70, 120, "Regards,")
c.setFillColor(WHITE)
c.setFont("Helvetica-Bold", 22)
c.drawString(70, 90, "Tristan Sharpe")
c.setFillColor(MUTED)
c.setFont("Helvetica", 12)
c.drawString(70, 64, "contact@tristansharpe.uk  ·  @tristansharpe193")
c.showPage()

c.save()
print("Saved Sponsorship Proposal.pdf")
