#!/usr/bin/env python3
"""The World in One Page — 22 November 2026 (revised entry).

A one-page newspaper front page drawn entirely by this program:
45 real, source-checked stories from Sunday 22 November 2026,
grouped into 7 regions, with a masthead, a lead story, four columns,
a day-in-numbers band and a source line.

Standard library only. The glyph atlas (atlas.bin, built by
build_atlas.py from DejaVu fonts) carries every character this file
prints, so the program needs no network and no installed fonts.
Run it twice and the PNG bytes are identical.

Usage:  python3 main.py            # writes out/entry.png
        MAKEFUN_OUTPUT_DIR=/output python3 main.py
"""

import binascii
import hashlib
import os
import struct
import sys
import zlib

# ---------------------------------------------------------------- page
W = 1024
H = 1024
MARGIN = 40
CONTENT_W = W - 2 * MARGIN          # 944
COL_W = 236
COL_GAP = 12
NCOLS = 4
BODY_TOP = 258
BODY_BOTTOM = 978

PAPER = (247, 243, 232)
INK = (24, 24, 24)
RED = (139, 26, 26)
FAINT = (178, 168, 148)

# Face ids match build_atlas.py.
F_MASTHEAD = 0   # serif bold 46
F_LEAD_HEAD = 1  # serif bold 29
F_LEAD_DECK = 2  # serif 13
F_HEAD = 3       # serif bold 13
F_SECTION = 4    # sans bold 11
F_SUMMARY = 5    # sans 10
F_FOOTER = 6     # sans 9
F_DATE = 7       # sans bold 10

# ---------------------------------------------------------------- data
# (section, headline, summary). The lead story is separate below.
STORIES = [
    ("MIDDLE EAST",
     "Iran hits US bases in Bahrain",
     "IRGC claims strikes on two US bases; Bahrain says defences "
     "held and two were hurt."),
    ("MIDDLE EAST",
     "Tankers hit near Hormuz",
     "Two vessels are struck leaving the Gulf; a third hits a mine and "
     "catches fire, Iranian media say."),
    ("MIDDLE EAST",
     "Trump wants a \u2018permanent\u2019 Iran deal",
     "Trump tells Fox News any deal must outlast his presidency \u2014 and "
     "plays down regime change."),
    ("MIDDLE EAST",
     "Iran masses 14 tankers off Kharg",
     "More than 14 Iranian tankers stage off Kharg Island, ready to "
     "challenge a US blockade."),
    ("MIDDLE EAST",
     "Eisenkot invites Likud to talks",
     "In Israel\u2019s coalition talks, Eisenkot invites Netanyahu\u2019s "
     "Likud to join negotiations."),
    ("EUROPE",
     "Russian missiles land in Poland",
     "Two missiles and a drone come down in the south-east; Tusk calls "
     "it a provocation."),
    ("EUROPE",
     "Finland: war \u2018spilling over\u2019",
     "Drones hit the Russian ship Sparta II in the Gulf of Finland; its "
     "crew of 16 is evacuated."),
    ("EUROPE",
     "Estonia to shut Russia border",
     "Estonia will close its border with Russia; Moscow decries a \u2018new "
     "Iron Curtain\u2019."),
    ("EUROPE",
     "EU and Indonesia sign trade pact",
     "After ten years of talks, CEPA frees up to 98.5% of tariff lines, "
     "saving exporters \u20ac600m a year."),
    ("EUROPE",
     "Germany rallies \u2018willing\u2019 allies",
     "Wadephul says the Berlin gathering sends Moscow a unified message "
     "to push for talks."),
    ("EUROPE",
     "Poland fires up Patriots",
     "Poland activates Patriot air defences and helicopters after "
     "Russian airspace violations."),
    ("RUSSIA & UKRAINE",
     "Russian strike on Lviv kills 2",
     "A barrage hits Lviv; two killed, ten hurt; Kyiv says Russia fired "
     "400+ drones."),
    ("RUSSIA & UKRAINE",
     "UK and Ukraine to build drones",
     "Kyiv and London sign deals for joint production of Ukrainian "
     "long-range strike drones in Britain."),
    ("RUSSIA & UKRAINE",
     "Zelenskyy: 109 bridge strikes",
     "Zelenskyy says Russia struck Ukrainian bridges 109 times before "
     "Kyiv hit the Crimean Bridge."),
    ("RUSSIA & UKRAINE",
     "Bulgaria backs India ceasefire plan",
     "Bulgaria endorses India\u2019s plan for a ceasefire covering "
     "the Black Sea and energy sites."),
    ("RUSSIA & UKRAINE",
     "Crimean Bridge strain admitted",
     "Moscow admits transport across the Crimean Bridge is harder after "
     "three strikes in a week."),
    ("THE AMERICAS",
     "\u2018El Chapo Isidro\u2019 captured",
     "Mexican forces seize the FBI most-wanted cartel boss in Guasave; "
     "11 killed in the raid."),
    ("THE AMERICAS",
     "Bolsonaro taken to ICU",
     "Brazil\u2019s jailed ex-president is in intensive care in Brasilia "
     "with an acute bowel obstruction."),
    ("THE AMERICAS",
     "FBI probes hack of crime database",
     "The FBI investigates an apparent hack of its crime database; the "
     "USDA was also hit."),
    ("THE AMERICAS",
     "Pentagon curbs Canada contacts",
     "The Pentagon limits \u2018social activities\u2019 with the Canadian "
     "military, a memo says."),
    ("THE AMERICAS",
     "Trump\u2013Xi\u2013Putin summit fallout",
     "After the Shenzhen trilateral, Trump again calls Putin a friend; "
     "analysts say Xi gained most."),
    ("ASIA\u2013PACIFIC",
     "Indonesia factory fire: 3 dead",
     "A blaze at a candy factory in Banten kills three; 36 workers are "
     "missing and 15 were rescued."),
    ("ASIA\u2013PACIFIC",
     "Two Indonesian volcanoes erupt",
     "Mount Ibu and Semeru erupt hours apart, sending ash hundreds of "
     "metres into the sky."),
    ("ASIA\u2013PACIFIC",
     "Modi opens Nitish Setu bridge",
     "PM Modi inaugurates the Nitish Setu bridge linking Patna and "
     "Vaishali districts in Bihar."),
    ("ASIA\u2013PACIFIC",
     "Japan to train live-fire in India",
     "In a first, Japanese forces will use Indian facilities for "
     "live-fire training."),
    ("ASIA\u2013PACIFIC",
     "Hong Kong votes for Election Committee",
     "Polls open for about 5,700 voters to elect members of Hong Kong\u2019s "
     "Election Committee."),
    ("ASIA\u2013PACIFIC",
     "India posts record 629-6 in NZ",
     "Pant\u2019s century lifts India to 629-6 in Wellington, their best "
     "Test total in New Zealand."),
    ("ASIA\u2013PACIFIC",
     "Suicide bombing kills 5 in Pakistan",
     "A suicide car bombing at a security checkpoint in Pakistan kills "
     "five and injures 13."),
    ("ASIA\u2013PACIFIC",
     "China\u2019s second cruise ship sails",
     "Adora Flora City leaves Guangzhou on a six-day maiden voyage to "
     "Hong Kong and Hue."),
    ("ASIA\u2013PACIFIC",
     "Shenzhou-24 rehearsal clears way",
     "Shenzhou-24 finishes its final rehearsal; it will carry the first "
     "Pakistani astronaut."),
    ("ASIA\u2013PACIFIC",
     "China slams FCC telecom ban",
     "Beijing opposes a US vote barring China Mobile, China Telecom and "
     "Unicom from US numbers."),
    ("MARKETS, TECH & SPORT",
     "Leapmotor profit plunges 73%",
     "China\u2019s EV maker reports Q3 net profit of 40m yuan, down 73%, "
     "despite record deliveries."),
    ("MARKETS, TECH & SPORT",
     "Foreign cash floods China tech",
     "Foreign investment in Chinese technology rises 31 percent."),
    ("MARKETS, TECH & SPORT",
     "Huawei launches phone brand OSTA",
     "Huawei unveils AI smartphone sub-brand OSTA; the first handset "
     "starts at 5,499 yuan."),
    ("MARKETS, TECH & SPORT",
     "Alibaba trims cloud outlook",
     "Alibaba cuts its near-term cloud growth outlook amid export "
     "controls, its CEO says."),
    ("MARKETS, TECH & SPORT",
     "Signal blocks phone screenshots",
     "Signal restricts mobile screenshots, citing an \u2018existential "
     "threat\u2019 from AI surveillance."),
    ("MARKETS, TECH & SPORT",
     "UN fails on \u2018killer robots\u2019",
     "The UN fails to agree rules on autonomous weapons as the \u2018killer "
     "robots\u2019 talks stall."),
    ("MARKETS, TECH & SPORT",
     "Verstappen wins wild Las Vegas GP",
     "Verstappen wins a 35-lead-change Las Vegas GP by 0.6s; Russell "
     "hits the wall late."),
    ("AFRICA & SCIENCE",
     "M6.8 quake off Timor-Leste",
     "A magnitude 6.8 quake strikes 105 km north-east of Lospalos, the "
     "USGS says."),
    ("AFRICA & SCIENCE",
     "Mlambo-Ngcuka dies at 71",
     "South Africa\u2019s ex-deputy president and former UN Women chief "
     "dies after a short illness."),
    ("AFRICA & SCIENCE",
     "South Africa murders fall",
     "Murders fall by 204 in July\u2013September, but killings still "
     "average 60 a day."),
    ("AFRICA & SCIENCE",
     "Senegal leader imposes budget",
     "President Faye signs the revised 2026 budget into force by decree "
     "after parliament rejects it."),
    ("AFRICA & SCIENCE",
     "Egypt nears $2.3bn IMF payout",
     "Egypt reaches a staff-level IMF deal on its $8bn facility, "
     "unlocking about $2.3bn."),
    ("AFRICA & SCIENCE",
     "Sodium cloud traced at Europa",
     "Keck astronomers trace the persistent sodium cloud around "
     "Jupiter\u2019s moon Europa."),
]

LEAD_KICKER = "LEAD \u2014 CLIMATE \u2022 ANTALYA"
LEAD_HEAD = "COP31 collapses with no deal"
LEAD_DECK = ("The EU, Britain, Panama and others reject a final text that "
             "omits fossil fuels. President Murat Kurum concedes \u2018no "
             "agreement\u2019 as the Antalya talks become the longest "
             "climate summit in history.")

MASTHEAD = "THE WORLD IN ONE PAGE"
DATELINE_LEFT = "SUNDAY, 22 NOVEMBER 2026"
DATELINE_RIGHT = "45 STORIES \u2022 7 REGIONS"

NUMBERS = ("THE DAY IN NUMBERS \u2014 2 killed in Lviv \u2022 11 dead in "
           "Sinaloa \u2022 36 missing in Banten \u2022 35 lead changes in "
           "Vegas \u2022 $2.3bn for Egypt")

FOOTER_LEFT = ("Sources: Reuters \u2022 AP \u2022 AFP \u2022 BBC \u2022 CNN "
               "\u2022 USGS \u2022 NYT \u2022 Euronews \u2022 Al Jazeera "
               "\u2022 Xinhua \u2022 ANTARA \u2022 FIA \u2022 Formula1.com")
FOOTER_RIGHT = "Compiled 22 Nov 2026 \u2022 No. 45"


# ---------------------------------------------------------------- atlas
# Binary layout written by build_atlas.py:
#   magic 8s, u32 face_count,
#   per face: u32 id, u32 size, u16 ascent, u16 descent, u32 glyphs,
#   per glyph: u32 face_id, u32 codepoint, i16 off_x, i16 off_y,
#              u16 advance, u16 w, u16 h, u32 data_off, u32 data_len,
#   pixel blob (8-bit grayscale).
_GLYPH = struct.Struct("<IhhHHHHII")
_FACE = struct.Struct("<IIHHI")


class Atlas(object):
    def __init__(self, path):
        with open(path, "rb") as fh:
            raw = fh.read()
        if raw[:8] != b"ATLS0001":
            raise ValueError("bad atlas magic")
        pos = 8
        (nfaces,) = struct.unpack_from("<I", raw, pos)
        pos += 4
        self.faces = {}   # face_id -> (size, ascent, descent)
        self.glyphs = {}  # (face_id, codepoint) -> glyph tuple
        face_counts = []
        for _ in range(nfaces):
            fid, size, asc, desc, count = _FACE.unpack_from(raw, pos)
            pos += _FACE.size
            self.faces[fid] = (size, asc, desc)
            face_counts.append(count)
        glyph_rows = []
        for count in face_counts:
            for _ in range(count):
                glyph_rows.append(_GLYPH.unpack_from(raw, pos))
                pos += _GLYPH.size
        blob_start = pos
        for fid, cp, ox, oy, adv, w, h, off, ln in glyph_rows:
            data = raw[blob_start + off: blob_start + off + ln]
            self.glyphs[(fid, cp)] = (ox, oy, adv, w, h, data)

    def glyph(self, face, ch):
        g = self.glyphs.get((face, ord(ch)))
        if g is None:
            g = self.glyphs.get((face, ord("?")))
        return g

    def line_height(self, face):
        _size, asc, desc = self.faces[face]
        return asc + desc

    def text_width(self, face, text):
        total = 0
        for ch in text:
            total += self.glyph(face, ch)[2]
        return total

    def wrap(self, face, text, max_w, max_lines=None):
        """Greedy word wrap; optionally cap lines, truncating with …."""
        words = text.split(" ")
        lines, cur = [], ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if self.text_width(face, trial) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        # Hard-split any line still too wide (long unbroken token).
        split = []
        for line in lines:
            while self.text_width(face, line) > max_w and len(line) > 1:
                cut = len(line) - 1
                while (cut > 0 and self.text_width(face, line[:cut]) > max_w):
                    cut -= 1
                if cut == 0:
                    cut = 1
                split.append(line[:cut])
                line = line[cut:]
            split.append(line)
        lines = split
        if max_lines is not None and len(lines) > max_lines:
            keep = lines[:max_lines]
            last = keep[-1]
            while last and self.text_width(face, last + "\u2026") > max_w:
                last = last[:-1]
            keep[-1] = last + "\u2026"
            lines = keep
        return lines


# ---------------------------------------------------------------- canvas
class Page(object):
    def __init__(self, atlas):
        self.atlas = atlas
        self.buf = bytearray(PAPER * (W * H))

    def _set(self, x, y, color, alpha=255):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            if alpha >= 255:
                self.buf[i:i + 3] = bytes(color)
            elif alpha > 0:
                for c in range(3):
                    base = self.buf[i + c]
                    self.buf[i + c] = (color[c] * alpha + base * (255 - alpha)) // 255

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(W, x + w), min(H, y + h)
        for yy in range(y0, y1):
            base = (yy * W + x0) * 3
            self.buf[base:base + (x1 - x0) * 3] = bytes(color) * (x1 - x0)

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def draw_text(self, x, y_top, face, text, color=INK):
        """Draw text with anchor (x, y_top): y_top is the ascender top."""
        cx = x
        for ch in text:
            ox, oy, adv, w, h, data = self.atlas.glyph(face, ch)
            if w and h:
                gx, gy = cx + ox, y_top + oy
                for row in range(h):
                    src = row * w
                    for col in range(w):
                        a = data[src + col]
                        if a:
                            self._set(gx + col, gy + row, color, a)
            cx += adv
        return cx

    def text_lines(self, x, y_top, face, lines, leading, color=INK):
        y = y_top
        for line in lines:
            self.draw_text(x, y, face, line, color)
            y += leading
        return y

    def globe(self, cx, cy, r, color=INK):
        """A small line-drawn globe: circle, meridians, parallels."""
        import math
        def plot(px, py):
            for dx in (0, 1):
                for dy in (0, 1):
                    self._set(px + dx, py + dy, color)
        steps = 720
        for i in range(steps):
            t = 2.0 * math.pi * i / steps
            plot(int(cx + r * math.cos(t)), int(cy + r * math.sin(t)))
            # vertical meridian ellipse
            plot(int(cx + (r * 0.45) * math.cos(t)),
                 int(cy + r * math.sin(t)))
            # tilted meridian
            a = math.cos(0.6)
            b = math.sin(0.6)
            ex = r * math.cos(t) * a
            ey = r * math.sin(t)
            plot(int(cx + ex), int(cy + ey))
            # horizontal parallel ellipses
            for fy, fr in ((-0.55, 0.83), (0.0, 1.0), (0.55, 0.83)):
                plot(int(cx + r * fr * math.cos(t)),
                     int(cy + r * fy + r * 0.22 * math.sin(t)))


# ---------------------------------------------------------------- layout
def render(page):
    at = page.atlas
    # --- masthead
    name_w = at.text_width(F_MASTHEAD, MASTHEAD)
    page.draw_text((W - name_w) // 2, 22, F_MASTHEAD, MASTHEAD)
    page.draw_text(MARGIN, 84, F_DATE, DATELINE_LEFT)
    right_w = at.text_width(F_DATE, DATELINE_RIGHT)
    page.draw_text(W - MARGIN - right_w, 84, F_DATE, DATELINE_RIGHT)
    page.hline(MARGIN, 102, CONTENT_W, INK, 2)
    page.hline(MARGIN, 106, CONTENT_W, INK, 1)

    # --- lead story + globe
    page.draw_text(MARGIN, 116, F_SECTION, LEAD_KICKER, RED)
    head_lines = at.wrap(F_LEAD_HEAD, LEAD_HEAD, 740, max_lines=2)
    y = page.text_lines(MARGIN, 136, F_LEAD_HEAD, head_lines, 36)
    deck_lines = at.wrap(F_LEAD_DECK, LEAD_DECK, 740, max_lines=2)
    y = page.text_lines(MARGIN, y + 8, F_LEAD_DECK, deck_lines, 17)
    page.globe(872, 178, 54)
    cap = "THE WORLD \u2014 22 NOV 2026"
    cap_w = at.text_width(F_FOOTER, cap)
    page.draw_text(872 - cap_w // 2, 238, F_FOOTER, cap)
    page.hline(MARGIN, 252, CONTENT_W, INK, 2)

    # --- four columns of stories, sections flowing down the page.
    # Measure every story block first, then split the sequence into
    # four columns of near-equal total height so no column is left
    # half empty. The split target rises until every column fits.
    for gx in (MARGIN + COL_W + COL_GAP // 2 - 1,
               MARGIN + 2 * COL_W + 3 * COL_GAP // 2 - 1,
               MARGIN + 3 * COL_W + 5 * COL_GAP // 2 - 1):
        page.vline(gx, BODY_TOP, BODY_BOTTOM - BODY_TOP, FAINT)
    blocks = []
    current_section = None
    for section, headline, summary in STORIES:
        head = at.wrap(F_HEAD, headline, COL_W, max_lines=2)
        summ = at.wrap(F_SUMMARY, summary, COL_W, max_lines=2)
        header_h = 24 if section != current_section else 0
        current_section = section
        block_h = header_h + 16 * len(head) + 13 * len(summ) + 10
        blocks.append((section, header_h, head, summ, block_h))
    body_h = BODY_BOTTOM - BODY_TOP
    total_h = sum(b[4] for b in blocks)
    target = total_h / NCOLS
    while True:
        heights = [0]
        for block in blocks:
            if heights[-1] > 0 and heights[-1] + block[4] > target \
                    and len(heights) < NCOLS:
                heights.append(0)
            heights[-1] += block[4]
        if max(heights) <= body_h or target >= body_h:
            break
        target += 4
    if max(heights) > body_h:
        raise SystemExit("OVERFLOW: stories do not fit in 4 columns")
    col = 0
    y = BODY_TOP
    col_h = 0
    counts = [0, 0, 0, 0]
    for section, header_h, head, summ, block_h in blocks:
        if col_h > 0 and col_h + block_h > target and col < NCOLS - 1:
            col += 1
            y = BODY_TOP
            col_h = 0
        x = MARGIN + col * (COL_W + COL_GAP)
        if header_h:
            page.draw_text(x, y, F_SECTION, section, RED)
            page.hline(x, y + 16, COL_W, INK, 1)
            y += header_h
        y = page.text_lines(x, y, F_HEAD, head, 16)
        y = page.text_lines(x, y, F_SUMMARY, summ, 13)
        y += 10
        col_h += block_h
        counts[col] += 1
        if y > BODY_BOTTOM:
            raise SystemExit("OVERFLOW: column %d runs past the body" % col)

    # --- day in numbers
    page.rect(MARGIN, 986, CONTENT_W, 1, INK)
    page.rect(MARGIN, 1006, CONTENT_W, 1, INK)
    num_w = at.text_width(F_SECTION, NUMBERS)
    page.draw_text((W - num_w) // 2, 990, F_SECTION, NUMBERS)
    # --- footer
    page.draw_text(MARGIN, 1012, F_FOOTER, FOOTER_LEFT)
    foot_w = at.text_width(F_FOOTER, FOOTER_RIGHT)
    page.draw_text(W - MARGIN - foot_w, 1012, F_FOOTER, FOOTER_RIGHT)
    return counts


# ---------------------------------------------------------------- png
def _chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF)
    return out


def encode_png(page):
    raw = bytearray()
    for row in range(H):
        raw.append(0)
        raw += page.buf[row * W * 3:(row + 1) * W * 3]
    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return bytes(png)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    atlas = Atlas(os.path.join(here, "atlas.bin"))
    page = Page(atlas)
    counts = render(page)
    png = encode_png(page)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not outdir:
        outdir = "/output" if os.path.isdir("/output") else "out"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(png)
    digest = hashlib.sha256(png).hexdigest()
    print("wrote %s (%d bytes, sha256 %s)" % (path, len(png), digest))
    print("stories=%d columns=%s" % (len(STORIES) + 1, counts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
