#!/usr/bin/env python3
"""THE WORLD TODAY - one-page newspaper of 24 November 2026 world news.

Renders entry.png (768x1024): masthead, lead Gaza story with illustration,
29 further verified stories in three columns, a Zaporizhzhia photo strip
mid-page, and a footer. 30 stories, 9 regions, every event dated
Tuesday 24 November 2026. Stdlib + Pillow only, no network, deterministic:
two runs produce byte-identical output.

Usage:  python3 main.py
Writes entry.png to $MAKEFUN_OUTPUT_DIR, or /output, or a temp dir.
If rendering fails, falls back to copying the bundled entry.png.
"""

import hashlib
import os
import shutil
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
W, H = 768, 1024
MARGIN = 14
COL_W = 740  # full content width

PAPER = (248, 244, 236)
INK = (20, 20, 20)
MUTED = (90, 86, 78)
RED = (158, 27, 27)
RULE = (40, 40, 40)
HAIRLINE = (180, 174, 162)

FONT_DIR = "/usr/share/fonts/truetype"
SERIF_BOLD = f"{FONT_DIR}/dejavu/DejaVuSerif-Bold.ttf"
SANS_BOLD = f"{FONT_DIR}/dejavu/DejaVuSans-Bold.ttf"
SANS = f"{FONT_DIR}/dejavu/DejaVuSans.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default(size=size)


def wrap(text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if fnt.getlength(trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(text, path, size, max_w, max_lines, min_size=8):
    """Shrink font until text fits in max_lines; returns (font, lines)."""
    s = size
    while s >= min_size:
        fnt = font(path, s)
        lines = wrap(text, fnt, max_w)
        if len(lines) <= max_lines:
            return fnt, lines
        s -= 1
    fnt = font(path, min_size)
    return fnt, wrap(text, fnt, max_w)[:max_lines]


def crop_to(img, tw, th, focus_y=0.5):
    """Center-crop image to target aspect, then resize to tw x th.

    focus_y (0..1) biases the vertical crop window: 0.5 is centred,
    higher values favour the lower part of the frame.
    """
    sw, sh = img.size
    target = tw / th
    if sw / sh > target:  # too wide: trim sides
        nw = int(sh * target)
        x0 = (sw - nw) // 2
        img = img.crop((x0, 0, x0 + nw, sh))
    else:  # too tall: trim top/bottom
        nh = int(sw / target)
        y0 = int((sh - nh) * focus_y)
        img = img.crop((0, y0, sw, y0 + nh))
    return img.resize((tw, th), Image.LANCZOS)


def load_scene(name, tw, th, focus_y=0.5):
    """Load a repo scene PNG, cropped to tw x th; grey placeholder if absent."""
    try:
        with Image.open(HERE / name) as im:
            return crop_to(im.convert("RGB"), tw, th, focus_y)
    except Exception:
        ph = Image.new("RGB", (tw, th), (70, 70, 70))
        d = ImageDraw.Draw(ph)
        d.text((tw // 2, th // 2), "ILLUSTRATION", fill=(220, 220, 220),
               font=font(SANS, 12), anchor="mm")
        return ph


# ---------------------------------------------------------------- stories
# (number, region tag, headline, one-line summary)
# Every figure checked against the v2 research file. Dow: AP +0.85% only.
# Hanoi: 6 dead. Shenzhou-24: crew unveiled 24 Nov; launch was 25 Nov.
STORIES = [
    (1, "GAZA",
     "ISRAEL KILLS HAMAS SECURITY CHIEF IN GAZA",
     "Israeli strike in Gaza City kills Hamas internal-security chief Naeem Abu Nahel; "
     "7 Palestinians killed in a day as the US-brokered ceasefire holds."),
    (2, "CHINA",
     "CHINA PURGES SHANGHAI PARTY BOSS CHEN JINING",
     "Xi's purge claims a 4th Politburo member: Shanghai chief Chen Jining, 62, "
     "under investigation."),
    (3, "TAIWAN",
     "TAIEX SOARS 8.99% IN RECORD DAY",
     "Taiex jumps +3,310.46 to 40,122.35, its biggest points gain ever; TSMC hits "
     "its 10% daily limit."),
    (4, "UKRAINE",
     "RUSSIAN STRIKE KILLS 2, WOUNDS 40 IN ZAPORIZHZHIA",
     "Overnight strike on a Zaporizhzhia residential area kills 2 and wounds 40, "
     "incl. a baby and children aged 4, 6 and 16."),
    (5, "SAUDI ARABIA",
     "HOUTHI DRONE HITS RIYADH TOWER, 11 HURT",
     "Houthis hit Riyadh's tallest tower, the PIF Tower, a 2nd time in a week; "
     "11 wounded."),
    (6, "FRANCE",
     "SANOFI SEALS $41BN INSMED DEAL",
     "Sanofi to buy US biotech Insmed at $175 a share \u2014 $41.0bn, the biggest "
     "pharma deal since 2023."),
    (7, "USA",
     "HUAWEI CONVICTED IN US CRIMINAL TRIAL",
     "Brooklyn jury finds Huawei guilty on 10 of 12 counts: fraud, Iran sanctions "
     "breaches, theft."),
    (8, "UNITED KINGDOM",
     "MI5 WARNS UK FIRMS OF RUSSIAN SABOTAGE",
     "MI5 warns firms supplying Ukraine's military of higher Russian sabotage "
     "risk, often arson."),
    (9, "IRAQ",
     "BAGHDAD MOVES TO SEIZE KURDISH OILFIELDS",
     "PM orders federal control of Kurdistan oilfields and border crossings after "
     "a smuggling probe."),
    (10, "ASIA MARKETS",
     "ASIA CHIP STOCKS SURGE \u2014 KOSPI 5,006, NIKKEI 58,645",
     "KOSPI +6.32% to 5,006.03; Nikkei +3.91% to 58,644.63 as the chip rally "
     "sweeps Asia."),
    (11, "USA MARKETS",
     "WALL ST: NASDAQ \u22121.5% AS NVIDIA SLIDES 5.9%",
     "Nvidia \u22125.86% to $155.38, Nasdaq \u22121.48%, S&P \u22120.50%; Dow bucks the "
     "fall, +0.85% to 50,018.70."),
    (12, "MALAYSIA",
     "MALAYSIA TO SEND BACK 6,803 MYANMAR NATIONALS",
     "PM Anwar says 6,803 Myanmar nationals go home in December, days after the "
     "ICJ genocide ruling."),
    (13, "AFRICA",
     "SENEGAL GET AFCON TITLE BACK ON APPEAL",
     "CAS reinstates Senegal's 1\u20130 extra-time win over Morocco \u2014 Senegal are "
     "African champions again."),
    (14, "GLOBAL",
     "UN: 5 WOMEN KILLED EVERY HOUR AT HOME",
     "47,000 women and girls were killed by a partner or family member in 2025 "
     "\u2014 about 5 an hour."),
    (15, "UNITED KINGDOM",
     "UK HEAT DEATHS HIT RECORD 5,258",
     "5,258 heat deaths in England in summer 2026 \u2014 the worst on record, "
     "nearly double 2022's 2,985."),
    (16, "SOUTH KOREA",
     "RUSSIAN JETS ENTER S. KOREA AIR ZONE",
     "Russian jets enter the KADIZ near Ulleung Island; Seoul scrambles "
     "fighters, warns islanders."),
    (17, "UKRAINE",
     "ZELENSKIY ADMITS UKRAINE HIT RUSSIAN SHIP",
     "Zelenskiy confirms Ukraine hit the Russian cargo ship Sparta II: "
     "\u201cWe did everything right.\u201d"),
    (18, "USA",
     "DELL REVENUE DOUBLES ON AI SERVER BOOM",
     "Dell Q3 revenue +103% to a record $54.9bn; AI server sales jump 291% "
     "to $22.0bn."),
    (19, "GAZA",
     "GAZA DECLARES MENINGITIS EPIDEMIC ALERT",
     "272 meningitis cases in October \u2014 8\u00d7 the normal rate; 15 deaths this "
     "year, infants under 1 are 71%."),
    (20, "FRANCE",
     "SARKOZY & BRUNI ORDERED TO STAND TRIAL",
     "French judges order ex-president Sarkozy and wife Carla Bruni to trial "
     "over witness tampering."),
    (21, "ETHIOPIA",
     "AMNESTY: TIGRAY SHELLING MAY BE WAR CRIMES",
     "Amnesty says army shelling of Alamata civilians killed 14 and must be "
     "probed as war crimes."),
    (22, "VIETNAM",
     "HANOI GAS BLAST KILLS 6, INJURES 10",
     "Suspected gas blast at a Hanoi hotpot eatery kills 6 and injures 10; "
     "the building partly collapses."),
    (23, "UAE",
     "UAE BUS CRASH KILLS 13, INJURES 14",
     "Bus carrying 41 hits a broken-down truck in Ras Al Khaimah; 13 dead, "
     "14 injured."),
    (24, "USA",
     "TRUMP PARDONS TURKEYS; HONOURS GIULIANI",
     "Trump pardons Thanksgiving turkeys Freedom and Feathers, then honours "
     "Rudy Giuliani with a medal."),
    (25, "COLOMBIA",
     "30 HOSTAGES SEIZED IN CARTAGENA SUPERMARKET",
     "Masked gunmen seize 30 shoppers and staff in a Cartagena supermarket; "
     "5 freed, 25 still held."),
    (26, "USA",
     "FORT HOOD KILLER SEEKS EXECUTION STAY",
     "Nidal Hasan, who killed 13 at Fort Hood in 2009, seeks a stay of his "
     "3 Dec execution."),
    (27, "SPACE",
     "PAKISTAN'S FIRST ASTRONAUT SET FOR SPACE",
     "China unveils the Shenzhou-24 crew: Zeeshan Ali, 40, will be the first "
     "Pakistani in space."),
    (28, "BANGLADESH",
     "HASINA SEEKS RETURN TO DHAKA ON DEC 16",
     "Ousted PM Hasina plans to return from exile in India on 16 Dec; Dhaka "
     "says only by extradition."),
    (29, "LATVIA",
     "LATVIA: UKRAINE WAR MAY TIP NEXT YEAR",
     "Latvia's president: the war may reach a \u201ctipping point\u201d in 2027, "
     "leading to Moscow's defeat."),
    (30, "DR CONGO",
     "EBOLA WORKERS RESCUED AFTER 3 DAYS TRAPPED",
     "WHO evacuates Ebola staff from a hospital in Akwe after 3 days "
     "sheltering amid fighting in Ituri."),
]


def draw_story(d, x, y, w, story):
    """One small story: red number+tag line, bold headline, 2-line summary.

    Fits a 60px-tall slot; font sizes shrink if a headline/summary runs long.
    """
    num, tag, headline, summary = story
    d.text((x, y), f"{num:02d} \u00b7 {tag}", fill=RED, font=font(SANS_BOLD, 9))
    hy = y + 12
    hfnt, hlines = fit_lines(headline, SANS_BOLD, 11, w, 2, min_size=9)
    ly = hy
    for ln in hlines:
        d.text((x, ly), ln, fill=INK, font=hfnt)
        ly += 12
    sfnt, slines = fit_lines(summary, SANS, 9, w, 2, min_size=8)
    ly += 1
    for ln in slines:
        d.text((x, ly), ln, fill=MUTED, font=sfnt)
        ly += 11
    return ly


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    by_num = {s[0]: s for s in STORIES}

    # ---- masthead ----
    mast = font(SERIF_BOLD, 40)
    d.text((W // 2, 8), "THE WORLD TODAY", fill=INK, font=mast, anchor="ma")
    d.line([(MARGIN, 56), (W - MARGIN, 56)], fill=RED, width=2)
    d.line([(MARGIN, 59), (W - MARGIN, 59)], fill=RULE, width=1)
    d.text((MARGIN, 64), "TUESDAY \u00b7 24 NOVEMBER 2026", fill=INK,
           font=font(SANS_BOLD, 12))
    d.text((W - MARGIN, 64), "30 STORIES \u00b7 9 REGIONS", fill=RED,
           font=font(SANS_BOLD, 12), anchor="ra")
    d.line([(MARGIN, 82), (W - MARGIN, 82)], fill=RULE, width=1)

    # ---- lead story #1: Gaza scene + headline + summary ----
    scene = load_scene("scene.png", COL_W, 104, focus_y=0.62)
    img.paste(scene, (MARGIN, 88))
    lead = by_num[1]
    lh_fnt, lh_lines = fit_lines(lead[2], SANS_BOLD, 20, COL_W, 1, min_size=16)
    for ln in lh_lines:
        d.text((MARGIN, 198), ln, fill=INK, font=lh_fnt)
    lfnt, llines = fit_lines(lead[3], SANS, 11, COL_W, 2, min_size=10)
    ly = 224
    for ln in llines:
        d.text((MARGIN, ly), ln, fill=MUTED, font=lfnt)
        ly += 14
    d.line([(MARGIN, 254), (W - MARGIN, 254)], fill=RULE, width=1)

    # ---- 3-column grid ----
    gutter = 8
    col_w = (COL_W - 2 * gutter) // 3  # 241
    col_x = [MARGIN, MARGIN + col_w + gutter, MARGIN + 2 * (col_w + gutter)]
    row_h, pitch = 60, 62

    def grid(story_nums, y0):
        y = y0
        for i in range(0, len(story_nums), 3):
            for j, n in enumerate(story_nums[i:i + 3]):
                draw_story(d, col_x[j], y, col_w, by_num[n])
            y += pitch
        return y

    # Section A: stories 2,3,5,6,7,8,9,10 (story 4 gets the photo strip)
    y = grid([2, 3, 5, 6, 7, 8, 9, 10], 262)

    # ---- Zaporizhzhia photo strip: story #4 ----
    by = y + 2
    scene2 = load_scene("scene2.png", 300, 88)
    img.paste(scene2, (MARGIN, by))
    tx = MARGIN + 310
    tw = W - MARGIN - tx
    s4 = by_num[4]
    d.text((tx, by + 1), f"04 \u00b7 {s4[1]}", fill=RED, font=font(SANS_BOLD, 9))
    hfnt, hlines = fit_lines(s4[2], SANS_BOLD, 14, tw, 2, min_size=11)
    hy = by + 14
    for ln in hlines:
        d.text((tx, hy), ln, fill=INK, font=hfnt)
        hy += 17
    sfnt, slines = fit_lines(s4[3], SANS, 10, tw, 2, min_size=9)
    sy = hy + 1
    for ln in slines:
        d.text((tx, sy), ln, fill=MUTED, font=sfnt)
        sy += 13
    d.line([(MARGIN, by + 94), (W - MARGIN, by + 94)], fill=RULE, width=1)

    # ---- Section B: stories 11-30 ----
    y = grid(list(range(11, 31)), by + 102)

    # ---- footer ----
    fy = 1006
    d.line([(MARGIN, 1000), (W - MARGIN, 1000)], fill=HAIRLINE, width=1)
    d.text((W // 2, fy), "30 stories \u00b7 9 regions  |  Sources: Reuters \u00b7 AP \u00b7 "
           "UN News \u00b7 UKHSA \u00b7 Dell \u00b7 Sanofi \u00b7 Amnesty",
           fill=MUTED, font=font(SANS, 9), anchor="ma")
    return img


def resolve_output_dir():
    """$MAKEFUN_OUTPUT_DIR, else /output, else a temp dir. Never crashes."""
    candidates = []
    env = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env:
        candidates.append(Path(env))
    candidates.append(Path("/output"))
    for cand in candidates:
        try:
            cand.mkdir(parents=True, exist_ok=True)
            probe = cand / ".write-test"
            probe.write_text("ok")
            probe.unlink()
            return cand
        except Exception:
            continue
    return Path(tempfile.mkdtemp(prefix="news-image-"))


def main():
    out_dir = resolve_output_dir()
    out_path = out_dir / "entry.png"
    try:
        img = render()
        tmp = out_dir / ".entry.tmp.png"
        img.save(tmp, "PNG")
        os.replace(tmp, out_path)
    except Exception as exc:  # never hard-exit: fall back to bundled entry
        print(f"render failed ({exc}); falling back to bundled entry.png",
              file=sys.stderr)
        try:
            bundled = HERE / "entry.png"
            if bundled.resolve() != out_path.resolve():
                shutil.copyfile(bundled, out_path)
            else:
                raise RuntimeError("bundled entry.png is the output path")
        except Exception as exc2:
            print(f"fallback copy failed ({exc2}); writing minimal image",
                  file=sys.stderr)
            try:
                img = Image.new("RGB", (W, H), PAPER)
                d = ImageDraw.Draw(img)
                d.text((W // 2, H // 2 - 20), "THE WORLD TODAY", fill=INK,
                       font=font(SERIF_BOLD, 40), anchor="mm")
                d.text((W // 2, H // 2 + 20), "TUESDAY \u00b7 24 NOVEMBER 2026",
                       fill=MUTED, font=font(SANS, 14), anchor="mm")
                img.save(out_path, "PNG")
            except Exception as exc3:
                print(f"minimal image failed: {exc3}", file=sys.stderr)
    try:
        digest = hashlib.sha256(out_path.read_bytes()).hexdigest()
        print(f"wrote {out_path} ({out_path.stat().st_size} bytes) sha256={digest}")
    except Exception as exc:
        print(f"could not verify output: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
