#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House: A Letter in One Image.

Draws a single warm invitation letter (1024x1024 PNG) to /output/entry.png.
Fully deterministic: fixed text, fixed geometry, no randomness, no time,
no network. Every pixel is produced by this program.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "/output/entry.png"

# Palette: warm cream paper, dark brown ink, one terracotta accent.
PAPER = (251, 244, 228)
PAPER_EDGE = (243, 232, 205)
INK = (58, 46, 34)
ACCENT = (178, 74, 43)
ACCENT_SOFT = (214, 138, 96)
SUN = (232, 164, 65)
LEAF = (96, 128, 84)

FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/truetype/liberation",
    "/usr/share/fonts/truetype/noto",
]


def load_font(names, size):
    """Try named font files in the usual system dirs, else Pillow default."""
    for name in names:
        for d in FONT_DIRS:
            path = os.path.join(d, name)
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


F_TITLE = lambda s: load_font(["DejaVuSerif-Bold.ttf", "LiberationSerif-Bold.ttf",
                               "NotoSerif-Bold.ttf"], s)
F_BODY = lambda s: load_font(["DejaVuSerif.ttf", "LiberationSerif-Regular.ttf",
                              "NotoSerif-Regular.ttf"], s)
F_ITALIC = lambda s: load_font(["LiberationSerif-Italic.ttf", "NotoSerif-Italic.ttf",
                                "DejaVuSerif.ttf"], s)
F_BOLD = lambda s: load_font(["DejaVuSerif-Bold.ttf", "LiberationSerif-Bold.ttf",
                             "NotoSerif-Bold.ttf"], s)


def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_sun(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SUN)
    for k in range(8):
        ang = k * math.pi / 4.0
        x1 = cx + int((r + 8) * math.cos(ang))
        y1 = cy + int((r + 8) * math.sin(ang))
        x2 = cx + int((r + 22) * math.cos(ang))
        y2 = cy + int((r + 22) * math.sin(ang))
        d.line([x1, y1, x2, y2], fill=SUN, width=5)


def draw_house(d, x, y, s):
    """Small friendly house, s = overall width in px."""
    # Walls
    d.rectangle([x, y + s * 0.45, x + s, y + s], fill=(233, 196, 138),
                outline=INK, width=3)
    # Roof
    d.polygon([(x - s * 0.08, y + s * 0.48), (x + s * 0.5, y),
               (x + s * 1.08, y + s * 0.48)], fill=ACCENT, outline=INK)
    # Door
    dw, dh = s * 0.26, s * 0.48
    d.rectangle([x + s * 0.5 - dw / 2, y + s - dh, x + s * 0.5 + dw / 2, y + s],
                fill=(122, 74, 52), outline=INK, width=3)
    d.ellipse([x + s * 0.5 + dw / 2 - 10, y + s - dh / 2, x + s * 0.5 + dw / 2 - 4,
               y + s - dh / 2 + 6], fill=(251, 244, 228))
    # Window
    ww = s * 0.22
    d.rectangle([x + s * 0.08, y + s * 0.58, x + s * 0.08 + ww, y + s * 0.58 + ww],
                fill=(255, 246, 214), outline=INK, width=3)
    d.line([x + s * 0.08 + ww / 2, y + s * 0.58, x + s * 0.08 + ww / 2,
            y + s * 0.58 + ww], fill=INK, width=2)
    d.line([x + s * 0.08, y + s * 0.58 + ww / 2, x + s * 0.08 + ww,
            y + s * 0.58 + ww / 2], fill=INK, width=2)
    # Chimney + smoke puffs
    d.rectangle([x + s * 0.68, y + s * 0.10, x + s * 0.82, y + s * 0.38],
                fill=(122, 74, 52), outline=INK, width=2)
    d.ellipse([x + s * 0.70, y - s * 0.06, x + s * 0.82, y + s * 0.06],
              fill=(200, 190, 175))
    d.ellipse([x + s * 0.76, y - s * 0.16, x + s * 0.88, y - s * 0.04],
              fill=(200, 190, 175))


def draw_cat(d, x, y, s):
    """Simple sitting cat silhouette, s = height in px."""
    body = (90, 70, 55)
    # Body
    d.ellipse([x, y + s * 0.35, x + s * 0.62, y + s], fill=body)
    # Head
    d.ellipse([x + s * 0.08, y, x + s * 0.58, y + s * 0.5], fill=body)
    # Ears
    d.polygon([(x + s * 0.12, y + s * 0.12), (x + s * 0.16, y - s * 0.12),
               (x + s * 0.30, y + s * 0.06)], fill=body)
    d.polygon([(x + s * 0.36, y + s * 0.06), (x + s * 0.50, y - s * 0.12),
               (x + s * 0.54, y + s * 0.12)], fill=body)
    # Tail curling up
    d.arc([x + s * 0.45, y + s * 0.30, x + s * 1.05, y + s * 1.05],
          start=300, end=90, fill=body, width=int(s * 0.14))
    # Eyes (closed, content)
    d.arc([x + s * 0.18, y + s * 0.22, x + s * 0.30, y + s * 0.34],
          start=180, end=360, fill=PAPER, width=3)
    d.arc([x + s * 0.36, y + s * 0.22, x + s * 0.48, y + s * 0.34],
          start=180, end=360, fill=PAPER, width=3)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- paper edge shading + double border frame ---
    d.rectangle([14, 14, W - 15, H - 15], outline=INK, width=3)
    d.rectangle([26, 26, W - 27, H - 27], outline=ACCENT, width=2)

    # --- header doodles: sun top-right, little house top-left ---
    draw_sun(d, 905, 92, 30)
    draw_house(d, 78, 52, 96)

    # --- title ---
    title = "You're Invited!"
    f_title = F_TITLE(68)
    tw = d.textlength(title, font=f_title)
    d.text(((W - tw) / 2, 62), title, font=f_title, fill=INK)

    # --- subtitle ---
    sub = "A warm invitation to visit my home in Batam, Indonesia"
    f_sub = F_ITALIC(27)
    sw = d.textlength(sub, font=f_sub)
    d.text(((W - sw) / 2, 152), sub, font=f_sub, fill=ACCENT)

    # --- divider with a small diamond ---
    d.line([150, 205, 470, 205], fill=ACCENT_SOFT, width=2)
    d.line([554, 205, 874, 205], fill=ACCENT_SOFT, width=2)
    d.polygon([(512, 196), (521, 205), (512, 214), (503, 205)], fill=ACCENT)

    # --- letter body ---
    margin = 112
    max_w = W - 2 * margin
    f_greet = F_BOLD(35)
    f_body = F_BODY(31)
    line_h = 45
    y = 238

    d.text((margin, y), "Dear Judge,", font=f_greet, fill=INK)
    y += 54

    paras = [
        "Please come visit my house in Batam, Indonesia. "
        "Grandma's chicken soto is simmering right now \u2014 and it tastes "
        "even better shared.",
        "The Wi-Fi is fast, a spare charger is already plugged in, and the "
        "sunset from my porch turns the whole sky orange.",
        "My cat will supervise you from your laptop. Consider it the "
        "warm-up act.",
        "You cannot literally visit, I know. But if you could, the kettle "
        "would already be on.",
    ]
    for pi, p in enumerate(paras):
        for line in wrap(d, p, f_body, max_w):
            d.text((margin, y), line, font=f_body, fill=INK)
            y += line_h
        y += 12 if pi < len(paras) - 1 else 0

    # --- signature, right aligned ---
    y += 14
    f_sig = F_ITALIC(33)
    f_name = F_BOLD(36)
    for text, font in [("Warmly,", f_sig), ("Petrus", f_name),
                       ("Batam, Indonesia", f_sig)]:
        tw = d.textlength(text, font=font)
        d.text((W - margin - tw, y), text, font=font, fill=INK)
        y += 46 if text != "Petrus" else 50

    # --- cat sitting at the bottom left ---
    draw_cat(d, 110, 852, 88)

    # --- wax seal beside the signature (left of it, clear of the text) ---
    cx, cy, r = 640, 880, 34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ACCENT, outline=(140, 52, 28),
              width=3)
    d.ellipse([cx - r + 7, cy - r + 7, cx + r - 7, cy + r - 7], outline=(255, 220, 200),
              width=2)
    f_seal = F_TITLE(36)
    ch = "P"
    cw = d.textlength(ch, font=f_seal)
    chh = f_seal.getbbox(ch)
    d.text((cx - cw / 2, cy - (chh[3] - chh[1]) / 2 - chh[1]),
           ch, font=f_seal, fill=(255, 240, 225))

    # --- postscript, one centered line at the very bottom ---
    f_ps = F_ITALIC(25)
    ps = "P.S. The cat has already claimed your chair."
    pw = d.textlength(ps, font=f_ps)
    d.text(((W - pw) / 2, 948), ps, font=f_ps, fill=ACCENT)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, format="PNG", optimize=True)


if __name__ == "__main__":
    main()
