#!/usr/bin/env python3
"""news-image-20261124 v3 — one day of world news, Tuesday 24 November 2026.

1024x1024 broadsheet: 38 verified stories, 7 regions, 19 fields, 13 drawn
feature cards, UTC timeline, IN NUMBERS strip, world-map pins, DATE CHECK.
Deterministic: identical bytes on every run. Stdlib + Pillow at render time;
if Pillow is missing, falls back to copying a bundled entry.png.
Default output is absolute /output with a temp-dir fallback chain.
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ENTRY_NAME = "entry.png"
W, H = 1024, 1024

PAPER = (247, 243, 234)
INK = (17, 17, 17)
MUTED = (107, 101, 88)
RED = (179, 35, 27)
LINE = (17, 17, 17)
LAND = (216, 210, 194)
LAND_LINE = (138, 132, 116)
BADGE = {"C": (26, 122, 58), "O": (26, 79, 156), "R": (179, 35, 27),
         "CL": (138, 109, 0)}


def resolve_output_dir():
    """Absolute /output first, then temp dir. Never crash on output."""
    for cand in ("/output", os.path.join(tempfile.gettempdir(), "news-image")):
        try:
            os.makedirs(cand, exist_ok=True)
            probe = os.path.join(cand, ".write_test")
            with open(probe, "w") as f:
                f.write("ok")
            os.remove(probe)
            return cand
        except Exception:
            continue
    return tempfile.gettempdir()


# ---------------------------------------------------------------- data
# (n, image, tag, badge, headline, summary, source)
FEATURES = [
    (1, "card1.png", "CHINA · POLITICS", "C",
     "SHANGHAI PARTY BOSS CHEN JINING UNDER PROBE",
     "Xi's purge claims a 4th Politburo member: Shanghai chief Chen Jining, 62, "
     "under investigation for 'severe violations'.",
     "Reuters · Xinhua"),
    (2, "card2.png", "USA · TECH", "C",
     "HUAWEI GUILTY ON 10 OF 12 COUNTS IN US TRIAL",
     "Brooklyn jury convicts Huawei of bank and wire fraud, Iran sanctions "
     "breaches and trade-secret theft.",
     "Reuters"),
    (3, "card3.png", "UKRAINE · WAR", "C",
     "RUSSIAN ATTACKS KILL 9 ACROSS UKRAINE IN A DAY",
     "Strikes across Ukraine kill 9 and wound 77 in a day; Zaporizhzhia flats "
     "hit, 2 killed, 44+ wounded incl. children.",
     "Kyiv Independent · Reuters"),
    (4, "card4.png", "SOUTH KOREA · SECURITY", "C",
     "RUSSIAN JETS SPARK KOREA AIR RAID ALERT",
     "Russian jets enter the KADIZ; Seoul scrambles fighters and warns islanders.",
     "Yonhap"),
    (5, "card5.png", "SOLOMON ISLANDS · DIPLOMACY", "R",
     "SOLOMONS TO LET ITS CHINA PACT LAPSE",
     "Honiara tells Beijing it won't renew the 2022 security pact in April.",
     "Sydney Morning Herald"),
    (6, "card6.png", "SENEGAL · SPORT", "C",
     "SENEGAL AFCON TITLE RESTORED ON APPEAL",
     "CAS reinstates Senegal's 1–0 extra-time win over Morocco; champions again.",
     "AP"),
    (7, "card7.png", "USA · MARKETS", "C",
     "DOW CLOSES BACK ABOVE 50,000",
     "Dow +0.85% to 50,018.70 as Nasdaq slides 1.5% and Nvidia falls 5.9%.",
     "AP · Reuters"),
    (8, "card8.png", "FRANCE · PHARMA", "O",
     "SANOFI TO BUY INSMED FOR $41BN",
     "Sanofi agrees a $175-a-share cash deal for US biotech Insmed — $41.0bn.",
     "Sanofi"),
    (9, "card9.png", "GAZA · WAR", "C",
     "ISRAEL KILLS HAMAS SECURITY CHIEF",
     "Israeli strike in Gaza City kills Hamas internal-security chief Abu Nahel.",
     "Reuters"),
    (10, "card10.png", "IRAQ · ENERGY", "C",
     "BAGHDAD ORDERS KURDISH OIL TAKEOVER",
     "Baghdad orders federal control of Kurdistan oilfields; Barzani rejects it.",
     "Reuters"),
    (11, "card11.png", "UAE · ACCIDENT", "C",
     "BUS HITS TRUCK IN RAS AL KHAIMAH: 13 DEAD",
     "Bus carrying 41 hits a broken-down truck; 13 killed, 14 injured.",
     "Gulf News"),
    (12, "card12.png", "ENGLAND · CLIMATE", "O",
     "RECORD 5,258 HEAT DEATHS IN ENGLAND",
     "Summer 2026 heat killed an estimated 5,258 in England, the worst on record.",
     "UKHSA"),
    (13, "card13.png", "FRENCH GUIANA · SPACE", "O",
     "ARIANE 6 LOFTS 36 AMAZON SATELLITES",
     "Ariane 6 launches 36 Amazon Leo satellites from Kourou at 11:14 UTC.",
     "Amazon · Arianespace"),
]

# (n, badge, headline, source)
ALSO = [
    (14, "C", "UK warns firms backing Ukraine", "Reuters"),
    (15, "C", "Slovakia MPs end postal votes", "Reuters"),
    (16, "C", "Nahel officer to face murder trial", "Reuters"),
    (17, "O", "Turkey helicopter crash kills 5", "Defence Min."),
    (18, "O", "UK sanctions Houthi leaders", "gov.uk"),
    (19, "C", "Congo rebels say advance halted", "Al Jazeera"),
    (20, "O", "Ethiopia war-crimes probe urged", "Amnesty"),
    (21, "C", "Separatist denies war crimes in Oslo", "AFP"),
    (22, "R", "Hasina plans 16 Dec return", "Reuters"),
    (23, "C", "Manila court rejects Duterte pleas", "SC"),
    (24, "C", "Pakistani named to Shenzhou-24 crew", "AP"),
    (25, "C", "India bus crash kills 4 children", "PTI"),
    (26, "C", "Hanoi eatery gas blast kills 6", "AP"),
    (27, "C", "England beat Australia in T20", "ESPNcricinfo"),
    (28, "O", "Wong backs US alliance", "DFAT"),
    (29, "C", "Vanuatu pact splits Canberra", "AAP"),
    (30, "O", "US confidence index 103.3", "Conf. Board"),
    (31, "C", "Bolsonaro still in intensive care", "AFP"),
    (32, "C", "Cartagena hostage standoff", "Reuters"),
    (33, "O", "Nigeria central bank holds at 23%", "CBN"),
    (34, "O", "UN: 5 women an hour killed by kin", "UN"),
    (35, "C", "Real Madrid 5–1 PSV in Champions League", "UEFA"),
    (36, "C", "Riyadh tower hit, 11 hurt", "Reuters"),
    (37, "C", "Gazipur garment clash", "Reuters"),
    (38, "C", "Nepal quake M5.3", "PTI/USGS"),
]

TIMELINE = [
    ("00:30", "India bus crash"), ("01:00", "Hanoi blast"),
    ("05:30", "Sanofi deal"), ("11:14", "Ariane 6 launch"),
    ("11:37", "Ukraine 9 killed"), ("15:00", "US confidence"),
    ("16:30", "Turkey crash"), ("21:00", "Dow 50,000"),
]

NUMBERS = [
    ("9", "killed in Ukraine in a day"),
    ("10 of 12", "counts: Huawei guilty"),
    ("50,000", "Dow closes back above"),
    ("$41bn", "Sanofi buys Insmed"),
    ("5,258", "heat deaths, England record"),
    ("13", "die in UAE bus crash"),
]

CHIPS = [("EUROPE", 8), ("MIDDLE EAST", 6), ("AFRICA", 5), ("ASIA", 9),
         ("OCEANIA", 4), ("AMERICAS", 5), ("WORLD", 1)]

# Simplified continent polygons in (lon, lat).
CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-75, 60),
     (-70, 42), (-80, 32), (-90, 21), (-97, 16), (-105, 20), (-115, 30),
     (-125, 40), (-125, 49), (-140, 60), (-165, 60)],  # N America
    [(-80, 10), (-75, 5), (-60, 0), (-50, -5), (-35, -8), (-40, -20),
     (-48, -28), (-58, -38), (-65, -45), (-70, -55), (-73, -40), (-70, -20),
     (-77, -5)],  # S America
    [(-10, 36), (-9, 43), (0, 48), (5, 58), (10, 62), (18, 70), (30, 70),
     (40, 68), (45, 60), (40, 50), (30, 45), (23, 40), (19, 42), (12, 44),
     (3, 43), (-2, 37)],  # Europe
    [(-6, 35), (10, 37), (20, 32), (32, 31), (43, 12), (51, 10), (48, 0),
     (40, -10), (35, -20), (32, -29), (25, -34), (18, -35), (12, -18),
     (8, 4), (-8, 5), (-17, 15), (-16, 25)],  # Africa
    [(40, 68), (60, 70), (80, 73), (110, 76), (140, 72), (160, 66),
     (178, 65), (170, 60), (158, 52), (142, 45), (135, 35), (127, 33),
     (120, 25), (110, 20), (105, 8), (100, 8), (95, 15), (90, 22), (80, 13),
     (75, 8), (70, 20), (60, 25), (55, 26), (48, 29), (43, 12), (40, 20)],
    # Asia
    [(130, 31), (132, 33), (135, 34), (138, 35), (140, 38), (141, 42),
     (143, 44), (141, 45), (139, 40), (136, 37), (133, 35)],  # Japan
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -10),
     (125, -9), (130, -4), (135, -3), (140, -8), (138, -8), (130, -3),
     (120, -2), (110, 0), (105, 2), (100, 5)],  # Indonesia
    [(113, -22), (114, -30), (115, -35), (124, -33), (130, -32), (137, -35),
     (140, -38), (147, -39), (150, -37), (153, -27), (153, -22), (146, -19),
     (142, -11), (136, -12), (132, -12), (126, -14), (122, -17), (114, -22)],
    # Australia
    [(-58, 64), (-45, 60), (-40, 65), (-30, 68), (-25, 70), (-35, 76),
     (-55, 76), (-60, 74)],  # Greenland
]

# (n, lon, lat, dx, dy) — dx/dy offset the drawn pin from the true point.
PINS = [
    (1, 121, 31, 0, 0), (2, -74, 40.7, 0, 0), (3, 35, 48, -10, -8),
    (4, 130, 37, 0, 0), (5, 160, -9, 0, 0), (6, -17, 14, 0, 0),
    (7, -74, 40.7, 16, -9), (8, 2, 49, 0, 0), (9, 34, 31, 0, 0),
    (10, 44, 33, 0, 0), (11, 56, 25, 0, 0), (12, 0, 51, -11, -8),
    (13, -53, 5, 0, 0),
]


def main():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        # No Pillow: copy the bundled entry.png if present, else fail soft.
        bundled = os.path.join(HERE, ENTRY_NAME)
        out = os.path.join(resolve_output_dir(), ENTRY_NAME)
        if os.path.exists(bundled):
            shutil.copyfile(bundled, out)
        return 0

    def font(name, size):
        for path in ("/usr/share/fonts/truetype/dejavu/%s" % name,
                     "/usr/share/fonts/dejavu/%s" % name):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
        return ImageFont.load_default()

    serif = lambda s: font("DejaVuSerif-Bold.ttf", s)
    serif_it = lambda s: font("DejaVuSerif-Italic.ttf", s)
    sans = lambda s: font("DejaVuSans.ttf", s)
    sans_b = lambda s: font("DejaVuSans-Bold.ttf", s)

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    def tw(f, text):
        return d.textlength(text, font=f)

    def wrap(f, text, width):
        lines, cur = [], ""
        for word in text.split(" "):
            trial = (cur + " " + word).strip()
            if tw(f, trial) <= width or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    # Deterministic fit: try sizes from the base size down.
    def fit(family, size0, text, width, max_lines):
        for size in range(size0, 6, -1):
            f = family(size)
            lines = wrap(f, text, width)
            if len(lines) <= max_lines:
                return f, lines
        f = family(7)
        return f, wrap(f, text, width)[:max_lines]

    def load_scene(name, w, h):
        path = os.path.join(HERE, name)
        try:
            im = Image.open(path).convert("RGB")
        except Exception:
            im = Image.new("RGB", (w, h), (210, 205, 190))
        # Center-crop to the target aspect, then resize.
        tw_, th_ = im.size
        ta, sa = w / h, tw_ / th_
        if sa > ta:
            nw = int(th_ * ta)
            x0 = (tw_ - nw) // 2
            im = im.crop((x0, 0, x0 + nw, th_))
        else:
            nh = int(tw_ / ta)
            y0 = (th_ - nh) // 2
            im = im.crop((0, y0, tw_, y0 + nh))
        return im.resize((w, h), Image.LANCZOS)

    def badge(x, y, s, letter):
        d.rectangle([x, y, x + s, y + s], fill=BADGE.get(letter, INK))
        f = sans_b(max(7, s - 4))
        t = letter
        d.text((x + (s - tw(f, t)) / 2, y + (s - f.size) / 2 - 1),
               t, font=f, fill=(255, 255, 255))

    def section_title(y, text):
        f = sans_b(11)
        d.text((14, y), text, font=f, fill=INK)
        d.line([(14, y + 13), (1010, y + 13)], fill=INK, width=1)
        return y + 16

    M = 14
    CW = W - 2 * M
    y = 4

    # 1. Header line
    f_left = sans_b(11)
    d.text((M, y), "ONE DAY OF WORLD NEWS", font=f_left, fill=INK)
    f_right = sans_b(10)
    right = ("38 STORIES · 7 REGIONS · 19 FIELDS · EVERY ONE FROM "
             "TUESDAY 24 NOVEMBER 2026")
    d.text((W - M - tw(f_right, right), y + 1), right, font=f_right, fill=INK)
    y += 18
    d.line([(M, y), (W - M, y)], fill=INK, width=2)
    y += 6

    # 2. Giant masthead
    f_mast = serif(46)
    mast = "Tuesday 24 November 2026"
    d.text(((W - tw(f_mast, mast)) / 2, y), mast, font=f_mast, fill=INK)
    y += 52
    d.line([(M, y), (W - M, y)], fill=INK, width=1)
    y += 5

    # 3. Sub-headline strip
    f_sub = serif_it(15)
    sub = "Shanghai probe  ·  Huawei guilty  ·  Russian attacks kill 9"
    d.text(((W - tw(f_sub, sub)) / 2, y), sub, font=f_sub, fill=INK)
    y += 20

    # 4. Region chips
    gap = 6
    chip_w = (CW - gap * (len(CHIPS) - 1)) // len(CHIPS)
    chip_h = 20
    f_chip = sans_b(10)
    for i, (name, count) in enumerate(CHIPS):
        x0 = M + i * (chip_w + gap)
        d.rounded_rectangle([x0, y, x0 + chip_w, y + chip_h], radius=4,
                            outline=INK, width=1)
        t = "%s %d" % (name, count)
        d.text((x0 + (chip_w - tw(f_chip, t)) / 2, y + 3), t,
               font=f_chip, fill=INK)
    y += chip_h + 6

    # 5. Timeline — THE DAY IN UTC
    y = section_title(y, "THE DAY IN UTC")
    col_w = CW / len(TIMELINE)
    f_time = sans_b(11)
    for i, (t, label) in enumerate(TIMELINE):
        x0 = M + i * col_w
        d.text((x0 + 2, y), t, font=sans_b(11), fill=RED)
        for j, ln in enumerate(wrap(sans(9), label, col_w - 6)):
            d.text((x0 + 2, y + 14 + j * 11), ln, font=sans(9), fill=INK)
        if i:
            d.line([(x0, y), (x0, y + 24)], fill=(200, 195, 180), width=1)
    y += 26
    d.line([(M, y), (W - M, y)], fill=(200, 195, 180), width=1)
    y += 4

    # 6. IN NUMBERS
    y = section_title(y, "IN NUMBERS")
    ncol = len(NUMBERS)
    col_w = CW / ncol
    for i, (num, label) in enumerate(NUMBERS):
        x0 = M + i * col_w
        f_num = serif(24)
        d.text((x0 + 2, y), num, font=f_num, fill=INK)
        for j, ln in enumerate(wrap(sans(9), label, col_w - 8)):
            d.text((x0 + 2, y + 28 + j * 11), ln, font=sans(9), fill=MUTED)
        if i:
            d.line([(x0, y), (x0, y + 50)], fill=(200, 195, 180), width=1)
    y += 50
    d.line([(M, y), (W - M, y)], fill=INK, width=1)
    y += 4

    # 7. Feature cards
    y = section_title(y, "FEATURED — 13 DRAWN STORIES")
    big_h, small_h, cgap = 172, 144, 9
    big_w = (CW - 2 * cgap) // 3
    small_w = (CW - 4 * cgap) // 5

    def card(x0, y0, w0, h0, n, imgname, tag, bd, headline, summary,
             source, big):
        d.rectangle([x0, y0, x0 + w0, y0 + h0], outline=INK, width=1)
        scene_h = 82 if big else 60
        scene = load_scene(imgname, w0 - 2, scene_h)
        img.paste(scene, (x0 + 1, y0 + 1))
        tx = x0 + 6
        ty = y0 + scene_h + 6
        f_tag = sans_b(9 if big else 8)
        num = "%02d · %s" % (n, tag)
        d.text((tx, ty), num, font=f_tag, fill=RED)
        badge(x0 + w0 - 6 - (14 if big else 12), ty - 1, 14 if big else 12, bd)
        hf, hlines = fit(serif, 12 if big else 11, headline, w0 - 12, 2)
        hy = ty + (15 if big else 13)
        for j, ln in enumerate(hlines):
            d.text((tx, hy + j * (14 if big else 13)), ln, font=hf, fill=INK)
        sf = sans(10 if big else 9)
        slines = wrap(sf, summary, w0 - 12)
        sy = hy + len(hlines) * (14 if big else 13) + 3
        for j, ln in enumerate(slines[:2]):
            d.text((tx, sy + j * (12 if big else 11)), ln, font=sf, fill=INK)
        d.text((tx, y0 + h0 - 13), source, font=sans(8 if big else 7),
               fill=MUTED)

    for i, f in enumerate(FEATURES[:3]):
        card(M + i * (big_w + cgap), y, big_w, big_h, *f, big=True)
    y += big_h + 6
    for i, f in enumerate(FEATURES[3:8]):
        card(M + i * (small_w + cgap), y, small_w, small_h, *f, big=False)
    y += small_h + 6
    for i, f in enumerate(FEATURES[8:13]):
        card(M + i * (small_w + cgap), y, small_w, small_h, *f, big=False)
    y += small_h + 8

    # 8. ALSO — 25 more, 3 columns
    y = section_title(y, "ALSO ON TUESDAY 24 NOVEMBER · 25 MORE, BY REGION")
    cols = [ALSO[0:9], ALSO[9:18], ALSO[18:25]]
    col_w = CW / 3
    f_num = sans_b(9)
    f_bdg = sans_b(9)
    f_head = sans(9)
    f_src = sans(9)
    for ci, col in enumerate(cols):
        x0 = M + ci * col_w
        for ri, (n, bd, headline, source) in enumerate(col):
            yy = y + ri * 13
            d.text((x0, yy), str(n), font=f_num, fill=INK)
            bx = x0 + 20
            d.text((bx, yy), bd, font=f_bdg, fill=BADGE.get(bd, INK))
            hx = bx + tw(f_bdg, "CL") + 6
            d.text((hx, yy), headline, font=f_head, fill=INK)
            sx = hx + tw(f_head, headline) + 5
            d.text((sx, yy), "— " + source, font=f_src, fill=MUTED)
    y += 9 * 13 + 6

    # 9. World map with pins 1–13
    y = section_title(y, "WHERE IT HAPPENED · PINS 1–13")
    map_x, map_y, map_w, map_h = M, y, 640, 76
    d.rectangle([map_x, map_y, map_x + map_w, map_y + map_h],
                outline=INK, width=1)
    def proj(lon, lat):
        return (map_x + (lon + 170) / 360.0 * map_w,
                map_y + (72 - lat) / 127.0 * map_h)
    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_LINE)
    for (n, lon, lat, dx, dy) in PINS:
        px, py = proj(lon, lat)
        cx, cy = px + dx, py + dy
        if dx or dy:
            d.line([(px, py), (cx, cy)], fill=RED, width=1)
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED,
                  outline=(255, 255, 255), width=1)
        t = str(n)
        f_pin = sans_b(7)
        d.text((cx - tw(f_pin, t) / 2, cy - 5), t, font=f_pin,
               fill=(255, 255, 255))
    lx = map_x + map_w + 14
    d.text((lx, map_y), "REGION COUNTS", font=sans_b(10), fill=INK)
    f_leg = sans(9)
    legend = [("Europe 8", "Middle East 6"), ("Africa 5", "Asia 9"),
              ("Oceania 4", "Americas 5"), ("World 1", "")]
    for ri, (a, b) in enumerate(legend):
        yy = map_y + 16 + ri * 13
        d.text((lx, yy), a, font=f_leg, fill=INK)
        if b:
            d.text((lx + 110, yy), b, font=f_leg, fill=INK)
    d.text((lx, map_y + 16 + 4 * 13 + 2),
           "Pins 1–13 = featured stories above.", font=sans(8), fill=MUTED)
    y += map_h + 6

    # 10. DATE CHECK (shrink font until the line fits; never clip)
    dc = ("DATE CHECK — Left out: COP31 ended without a deal (closed Sun 22 Nov) · "
          "Russia's warning to Estonia (statement 23 Nov) · Indonesia fire toll 26 "
          "(fire Sat 21 Nov) · Solomons–Australia treaty (signed Wed 25 Nov).")
    f_dc = sans_b(9)
    while tw(f_dc, dc) > CW and f_dc.size > 7:
        f_dc = sans_b(f_dc.size - 1)
    d.text((M, y), dc, font=f_dc, fill=INK)
    y += 13
    d.line([(M, y), (W - M, y)], fill=INK, width=1)
    y += 4

    # 11. Footer
    f_foot = sans(9)
    foot1 = "C = 2+ outlets  ·  O = official source  ·  R = one outlet  ·  CL = one side's claim"
    d.text(((W - tw(f_foot, foot1)) / 2, y), foot1, font=f_foot, fill=MUTED)
    y += 12
    foot2 = ("Every story happened or was first reported on Tuesday 24 Nov 2026 (UTC) · "
             "sources named on each item · original drawings, no photos")
    d.text(((W - tw(f_foot, foot2)) / 2, y), foot2, font=f_foot, fill=MUTED)
    y += 12

    out_dir = resolve_output_dir()
    out_path = os.path.join(out_dir, ENTRY_NAME)
    img.save(out_path, "PNG", optimize=True)
    # Also drop a copy next to main.py for inspection/bundling.
    local = os.path.join(HERE, ENTRY_NAME)
    if os.path.abspath(local) != os.path.abspath(out_path):
        shutil.copyfile(out_path, local)
    print("wrote %s (%dx%d) final_y=%d" % (out_path, W, H, y))
    return 0


if __name__ == "__main__":
    sys.exit(main())
