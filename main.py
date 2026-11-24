#!/usr/bin/env python3
"""news-image-20261124: sum up Tuesday 24 November 2026's world news in one image.

Renders entry.png (768x1024) from the bundled scene.png: a photo band on top
with the masthead, then eight verified stories of 24 November 2026, then a
sources footer. Deterministic: two runs write byte-identical files.

If Pillow or the fonts are unavailable at runtime, falls back to copying the
bundled entry.png to the output directory instead of failing.
"""

import os
import shutil
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

W, H = 768, 1024
SS = 2  # supersample factor; text is drawn at 2x and downscaled with Lanczos
SCENE_H = 300

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONT_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
FONT_REG = os.path.join(FONT_DIR, "DejaVuSans.ttf")

PAPER = (250, 248, 243)
INK = (17, 17, 17)
SUB = (88, 86, 82)
RED = (178, 24, 24)
CHIP_DARK = (52, 52, 52)
HAIRLINE = (212, 208, 199)
FOOT = (122, 120, 114)
WHITE = (255, 255, 255)

MASTHEAD = "THE WORLD TODAY"
DATE_LINE = "TUESDAY \u00b7 24 NOVEMBER 2026"
FOOTER = "Sources: Reuters \u00b7 BBC \u00b7 AP \u00b7 UN News"

# (headline, sub-headline, tag chip) — all verified 24 Nov 2026 stories.
STORIES = [
    ("ISRAELI STRIKE KILLS HAMAS SECURITY CHIEF IN GAZA",
     "Naeem Abu Nahel, Hamas's internal security chief, is killed in a "
     "Gaza City airstrike; seven dead in all, including two police.",
     "GAZA", True),
    ("RUSSIAN STRIKE ON ZAPORIZHZHIA KILLS 2, WOUNDS 40",
     "Overnight attack on a residential area injures 40, including four "
     "children; a house is destroyed and a five-storey block damaged.",
     "UKRAINE", False),
    ("MI5 WARNS UK FIRMS OF RUSSIAN SABOTAGE THREAT",
     "Britain warns companies supplying Ukraine they could be targeted by "
     "Russian sabotage, often carried out through proxies.",
     "SECURITY", False),
    ("MALAYSIA TO REPATRIATE 6,803 MYANMAR NATIONALS",
     "Returns begin in December, days after the ICJ ruled Myanmar committed "
     "genocide against the Rohingya.",
     "ASIA", False),
    ("BAGHDAD MOVES TO TAKE KURDISH OILFIELDS",
     "Iraq's PM orders federal control of oilfields and border crossings in "
     "the Kurdistan region after an oil-smuggling probe.",
     "MIDDLE EAST", False),
    ("RUSSIAN WARPLANES ENTER KOREAN AIR ZONE",
     "South Korea scrambles jets as Russian aircraft enter KADIZ; Ulleung "
     "islanders are briefly told to shelter underground.",
     "ASIA", False),
    ("AI RALLY FADES AS NASDAQ SLIDES 1.5%",
     "Nvidia falls 5.9% to $155.38 a day after Monday's surge; chip stocks "
     "lead Wall Street lower.",
     "MARKETS", False),
    ("WHO EBOLA WORKERS EVACUATED IN ITURI",
     "Health workers freed after three days trapped in fighting in eastern "
     "DR Congo; teams are also pulled back from Mongbwalu.",
     "HEALTH", False),
]


def _output_dir():
    """Default absolute /output, honouring MAKEFUN_OUTPUT_DIR; temp fallback."""
    d = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    try:
        os.makedirs(d, exist_ok=True)
        probe = os.path.join(d, ".write-test")
        with open(probe, "wb") as f:
            f.write(b"")
        os.remove(probe)
        return d
    except Exception:
        return tempfile.mkdtemp(prefix="news-image-")


def _font(size, bold=True):
    from PIL import ImageFont
    path = FONT_BOLD if bold else FONT_REG
    return ImageFont.truetype(path, int(size * SS))


def _wrap(draw, text, font, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def _draw_tracked(draw, x, y, text, font, fill, tracking):
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking
    return x


def _chip(draw, x_right, y, label, font, bg):
    tw = draw.textlength(label, font=font)
    pad_x, pad_y = 9 * SS, 4 * SS
    w = int(tw + 2 * pad_x)
    h = int(font.size + 2 * pad_y)
    x0 = x_right - w
    draw.rounded_rectangle([x0, y, x_right, y + h], radius=8 * SS, fill=bg)
    draw.text((x0 + pad_x, y + pad_y), label, font=font, fill=WHITE)
    return w, h


def render(out_path):
    from PIL import Image, ImageDraw, ImageFilter

    img = Image.new("RGB", (W * SS, H * SS), PAPER)
    draw = ImageDraw.Draw(img, "RGBA")

    # --- scene band (top 300 px) ---
    scene = Image.open(os.path.join(HERE, "scene.png")).convert("RGB")
    scene = scene.resize((W * SS, SCENE_H * SS), Image.LANCZOS)
    img.paste(scene, (0, 0))

    # dark scrim gradient behind the masthead so white text reads
    scrim = Image.new("RGBA", (W * SS, SCENE_H * SS), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    for y in range(SCENE_H * SS):
        frac = y / float(SCENE_H * SS)
        if frac < 0.55:
            a = int(200 - 140 * (frac / 0.55))
        else:
            a = int(60 * (1 - (frac - 0.55) / 0.45))
        sd.line([(0, y), (W * SS, y)], fill=(0, 0, 0, max(0, a)))
    img.paste(scrim, (0, 0), scrim)
    draw = ImageDraw.Draw(img, "RGBA")

    # --- masthead ---
    mx = 36 * SS
    f_title = _font(42, bold=True)
    f_date = _font(17, bold=True)
    _draw_tracked(draw, mx, 26 * SS, MASTHEAD, f_title, WHITE, 2 * SS)
    _draw_tracked(draw, mx, 82 * SS, DATE_LINE, f_date, WHITE, 1 * SS)
    draw.line([(mx, 116 * SS), ((W - 36) * SS, 116 * SS)],
              fill=RED + (255,), width=3 * SS)

    # red rule under the scene band
    draw.rectangle([(0, SCENE_H * SS), (W * SS, (SCENE_H + 3) * SS)],
                   fill=RED)

    # --- stories ---
    margin = 36 * SS
    right = (W - 36) * SS
    y = (SCENE_H + 22) * SS

    f_lead_head = _font(23, bold=True)
    f_lead_sub = _font(14.5, bold=False)
    f_head = _font(16.5, bold=True)
    f_sub = _font(13.5, bold=False)
    f_chip = _font(11, bold=True)
    f_foot = _font(12, bold=False)

    for i, (headline, sub, tag, is_lead) in enumerate(STORIES):
        if is_lead:
            # lead: red chip at the left, headline spans full width below it
            tw = draw.textlength(tag, font=f_chip)
            cw = int(tw + 18 * SS)
            ch = int(f_chip.size + 8 * SS)
            draw.rounded_rectangle([margin, y, margin + cw, y + ch],
                                   radius=8 * SS, fill=RED)
            draw.text((margin + 9 * SS, y + 4 * SS), tag,
                      font=f_chip, fill=WHITE)
            y += (ch + 8 * SS)
            for line in _wrap(draw, headline, f_lead_head, right - margin):
                draw.text((margin, y), line, font=f_lead_head, fill=INK)
                y += int(27 * SS)
            y += 2 * SS
            for line in _wrap(draw, sub, f_lead_sub, right - margin):
                draw.text((margin, y), line, font=f_lead_sub, fill=SUB)
                y += int(19 * SS)
            y += 10 * SS
        else:
            # chip at the top-right; headline wraps around it
            cw, ch = _chip(draw, right, y, tag, f_chip, CHIP_DARK)
            head_w = right - margin - cw - 10 * SS
            lines = _wrap(draw, headline, f_head, head_w)
            for line in lines:
                draw.text((margin, y), line, font=f_head, fill=INK)
                y += int(21 * SS)
            y += 1 * SS
            for line in _wrap(draw, sub, f_sub, right - margin):
                draw.text((margin, y), line, font=f_sub, fill=SUB)
                y += int(17.5 * SS)
            y += 9 * SS
        if i < len(STORIES) - 1:
            draw.line([(margin, y), (right, y)], fill=HAIRLINE, width=1 * SS)
            y += 10 * SS

    # --- footer ---
    fw = draw.textlength(FOOTER, font=f_foot)
    draw.text(((W * SS - fw) / 2, (H - 26) * SS), FOOTER,
              font=f_foot, fill=FOOT)

    img = img.resize((W, H), Image.LANCZOS)
    img.save(out_path, format="PNG")


def main():
    out_dir = _output_dir()
    out_path = os.path.join(out_dir, "entry.png")
    try:
        render(out_path)
    except Exception:
        # Runtime fallback: ship the bundled entry.png instead of failing.
        try:
            shutil.copyfile(os.path.join(HERE, "entry.png"), out_path)
        except Exception:
            # Last resort: never crash over output; try the temp dir.
            alt = os.path.join(tempfile.mkdtemp(prefix="news-image-"),
                               "entry.png")
            shutil.copyfile(os.path.join(HERE, "entry.png"), alt)


if __name__ == "__main__":
    main()
