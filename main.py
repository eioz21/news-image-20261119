#!/usr/bin/env python3
"""World news of Thursday 19 November 2026, summed up in one image.

Draws a newspaper front page (1024 x 1024) with pure Python standard
library only: a small 5x7 bitmap font, simple shape primitives and a
hand-rolled PNG encoder (zlib). No network, no files read, no randomness,
so every run writes byte-identical output.

Usage:  MAKEFUN_OUTPUT_DIR=out python3 main.py
Writes <output dir>/entry.png (defaults to /output when the variable
is unset, matching the make.fun sandbox layout).
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------- font ----
# 5x7 bitmap font, one glyph per character. '#' is an ink pixel.
# All copy is set in capitals, so only capitals, digits and punctuation
# are needed. Lower-case input is upper-cased by the text routine.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "^": ("00100", "01010", "10001", "00000", "00000", "00000", "00000"),
    "~": ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
    "`": ("01000", "00100", "00000", "00000", "00000", "00000", "00000"),
    "\\": ("10000", "01000", "01000", "00100", "00010", "00010", "00001"),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
}

GLYPH_W = 5
GLYPH_H = 7
ADVANCE = 6  # glyph width + 1 pixel spacing, in font units


def text_width(text, scale):
    """Pixel width of text at the given scale."""
    return len(text) * ADVANCE * scale - scale


def wrap_text(text, scale, max_width):
    """Greedy word wrap. Returns a list of lines fitting max_width."""
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# -------------------------------------------------------------- canvas ----
class Canvas:
    """RGB pixel buffer with simple drawing primitives."""

    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.buf = bytearray(bytes(bg) * (width * height))

    def _idx(self, x, y):
        return (y * self.w + x) * 3

    def pixel(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = self._idx(x, y)
            self.buf[i:i + 3] = bytes(color)

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = self._idx(x0, yy)
            self.buf[i:i + len(row)] = row

    def rect(self, x, y, w, h, color, thick=1):
        self.fill_rect(x, y, w, thick, color)
        self.fill_rect(x, y + h - thick, w, thick, color)
        self.fill_rect(x, y, thick, h, color)
        self.fill_rect(x + w - thick, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill_rect(x0, y0, thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color, thick=1, fill=False):
        # Midpoint circle; filled variant draws horizontal spans.
        x = 0
        y = r
        d = 1 - r
        pts = []

        def plot(px, py):
            pts.append((px, py))

        while x <= y:
            for sx, sy in ((x, y), (y, x)):
                plot(cx + sx, cy + sy)
                plot(cx - sx, cy + sy)
                plot(cx + sx, cy - sy)
                plot(cx - sx, cy - sy)
            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * (x - y) + 5
                y -= 1
            x += 1
        if fill:
            rows = {}
            for px, py in pts:
                rows.setdefault(py, []).append(px)
            for py, xs in rows.items():
                self.fill_rect(min(xs), py, max(xs) - min(xs) + 1, 1, color)
        else:
            for px, py in pts:
                self.fill_rect(px, py, thick, thick, color)

    def ellipse(self, cx, cy, rx, ry, color, thick=1):
        steps = max(rx, ry) * 8
        for i in range(steps):
            import math
            a = 2 * math.pi * i / steps
            px = int(cx + rx * math.cos(a))
            py = int(cy + ry * math.sin(a))
            self.fill_rect(px, py, thick, thick, color)

    def text(self, x, y, s, scale, color):
        """Draw text, upper-cased. Unknown glyphs render as blank."""
        cx = x
        for ch in s.upper():
            glyph = FONT.get(ch, FONT[" "])
            for gy, row in enumerate(glyph):
                for gx, bit in enumerate(row):
                    if bit == "1":
                        self.fill_rect(
                            cx + gx * scale, y + gy * scale,
                            scale, scale, color)
            cx += ADVANCE * scale
        return cx

    def text_centered(self, cx, y, s, scale, color):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, color)


# ------------------------------------------------------------ png out -----
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(canvas):
    """Encode the canvas as a PNG (filter 0 on every scanline)."""
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.buf[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return png


# ------------------------------------------------------------- palette ----
PAPER = (247, 243, 232)
INK = (26, 26, 46)
NAVY = (20, 38, 77)
RED = (176, 42, 48)
GOLD = (201, 162, 39)
WHITE = (255, 255, 255)
GREY = (96, 96, 108)
PANEL = (255, 255, 255)
RULE = (196, 186, 168)
GREEN = (34, 120, 80)
TEAL = (36, 96, 128)
PURPLE = (110, 62, 140)


# -------------------------------------------------------------- icons ----
def icon_globe(c, x, y, r, color):
    """Wireframe globe: circle, meridians, parallels."""
    c.circle(x, y, r, color, thick=3)
    c.ellipse(x, y, r // 2, r, color, thick=2)
    c.ellipse(x, y, r, r // 2, color, thick=2)
    c.line(x - r, y, x + r, y, color, thick=2)
    c.line(x, y - r, x, y + r, color, thick=2)


def icon_burst(c, x, y, r, color):
    """Explosion / strike burst: radiating spikes from a centre."""
    import math
    for i in range(12):
        a = 2 * math.pi * i / 12
        x1 = int(x + (r // 3) * math.cos(a))
        y1 = int(y + (r // 3) * math.sin(a))
        x2 = int(x + r * math.cos(a))
        y2 = int(y + r * math.sin(a))
        c.line(x1, y1, x2, y2, color, thick=3)
    c.circle(x, y, r // 3, color, thick=2, fill=True)


def icon_bridge(c, x, y, w, color):
    """Suspension bridge: deck, arch, cables, towers."""
    c.line(x, y + 26, x + w, y + 26, color, thick=4)
    c.line(x + w // 4, y + 26, x + w // 4, y - 18, color, thick=4)
    c.line(x + 3 * w // 4, y + 26, x + 3 * w // 4, y - 18, color, thick=4)
    c.line(x, y + 26, x + w // 2, y - 26, color, thick=3)
    c.line(x + w, y + 26, x + w // 2, y - 26, color, thick=3)
    for fx in (w // 8, 3 * w // 8, 5 * w // 8, 7 * w // 8):
        c.line(x + fx, y + 26, x + fx, y + 6, color, thick=2)


def icon_chart(c, x, y, w, h, color):
    """Rising bars with an arrow: a record market debut."""
    bars = [h // 3, h // 2, 2 * h // 3, h]
    bw = w // 5
    for i, bh in enumerate(bars):
        bx = x + i * (bw + 4)
        c.fill_rect(bx, y + h - bh, bw, bh, color)
    c.line(x, y + h - bars[0] - 6, x + w, y - 4, color, thick=4)
    c.line(x + w, y - 4, x + w - 14, y - 4, color, thick=4)
    c.line(x + w, y - 4, x + w, y + 10, color, thick=4)


def icon_scales(c, x, y, color):
    """Scales of justice."""
    c.line(x, y - 26, x, y + 26, color, thick=4)
    c.line(x - 30, y - 22, x + 30, y - 22, color, thick=4)
    c.line(x - 30, y - 22, x - 44, y + 2, color, thick=3)
    c.line(x - 30, y - 22, x - 16, y + 2, color, thick=3)
    c.line(x + 30, y - 22, x + 16, y + 2, color, thick=3)
    c.line(x + 30, y - 22, x + 44, y + 2, color, thick=3)
    c.line(x - 44, y + 2, x - 16, y + 2, color, thick=3)
    c.line(x + 16, y + 2, x + 44, y + 2, color, thick=3)
    c.fill_rect(x - 16, y + 24, 32, 5, color)


def icon_voyager(c, x, y, color):
    """A small probe on a dotted path past a ringed planet."""
    import math
    for i in range(9):
        a = math.pi * (0.15 + 0.7 * i / 8)
        px = int(x - 70 + 140 * (i / 8))
        py = int(y - 14 - 26 * math.sin(a))
        c.fill_rect(px, py, 4, 4, color)
    c.circle(x - 58, y + 26, 16, color, thick=3)
    c.ellipse(x - 58, y + 26, 26, 7, color, thick=2)
    # probe: diamond body, dish, antenna
    c.line(x + 34, y - 26, x + 52, y - 8, color, thick=3)
    c.line(x + 52, y - 8, x + 34, y + 10, color, thick=3)
    c.line(x + 34, y + 10, x + 16, y - 8, color, thick=3)
    c.line(x + 16, y - 8, x + 34, y - 26, color, thick=3)
    c.line(x + 52, y - 8, x + 66, y - 8, color, thick=3)
    c.line(x + 34, y - 26, x + 34, y - 40, color, thick=3)


# ------------------------------------------------------------- layout ----
MARGIN = 22
GAP = 14


def draw_panel(c, x, y, w, h, tag, tag_color, headline, body,
               icon=None, headline_scale=3, body_scale=2):
    """One white news card: coloured tag bar, icon, headline, body."""
    c.fill_rect(x, y, w, h, PANEL)
    c.rect(x, y, w, h, RULE, thick=2)
    c.fill_rect(x, y, w, 30, tag_color)
    c.text(x + 10, y + 8, tag, 2, WHITE)
    inner_x = x + 14
    inner_w = w - 28
    cy = y + 42
    if icon is not None:
        icon_h = 64
        icon(x + w // 2, cy + icon_h // 2, tag_color)
        cy += icon_h + 8
    for line in wrap_text(headline, headline_scale, inner_w):
        c.text(inner_x, cy, line, headline_scale, INK)
        cy += 7 * headline_scale + 4
    cy += 2
    for line in wrap_text(body, body_scale, inner_w):
        c.text(inner_x, cy, line, body_scale, GREY)
        cy += 7 * body_scale + 3
    return cy


def build_image():
    c = Canvas(WIDTH, HEIGHT, PAPER)

    # ---- masthead ------------------------------------------------------
    c.fill_rect(0, 0, WIDTH, 148, NAVY)
    c.fill_rect(0, 148, WIDTH, 5, GOLD)
    c.text_centered(WIDTH // 2, 26, "THE WORLD IN ONE DAY", 6, WHITE)
    c.text_centered(WIDTH // 2, 96, "THURSDAY 19 NOVEMBER 2026", 3, GOLD)

    # ---- lead story ----------------------------------------------------
    lx, ly, lw, lh = MARGIN, 168, WIDTH - 2 * MARGIN, 216
    c.fill_rect(lx, ly, lw, lh, PANEL)
    c.rect(lx, ly, lw, lh, RULE, thick=2)
    c.fill_rect(lx, ly, 10, lh, RED)
    icon_globe(c, lx + 108, ly + 108, 74, NAVY)
    tx = lx + 216
    tw = lx + lw - 18 - tx
    c.text(tx, ly + 20, "APEC  -  SHENZHEN, CHINA", 2, RED)
    cy = ly + 48
    for line in wrap_text("TRUMP, XI AND PUTIN MEET IN SHENZHEN", 4, tw):
        c.text(tx, cy, line, 4, INK)
        cy += 7 * 4 + 5
    cy += 4
    lead_body = ("The leaders of the United States, China and Russia hold "
                 "their first three-way summit, on the sidelines of the "
                 "APEC forum in Shenzhen.")
    for line in wrap_text(lead_body, 2, tw):
        c.text(tx, cy, line, 2, GREY)
        cy += 7 * 2 + 3

    # ---- story grid ----------------------------------------------------
    col_w = (WIDTH - 2 * MARGIN - 2 * GAP) // 3
    row1_y = 398
    row_h = 252
    row2_y = row1_y + row_h + GAP

    draw_panel(
        c, MARGIN, row1_y, col_w, row_h, "MIDDLE EAST", RED,
        "IRAN WIDENS GULF ATTACKS",
        "Iran strikes targets in Bahrain and Kuwait after US forces hit "
        "a missile site on Qeshm Island.",
        icon=lambda cx, cy, col: icon_burst(c, cx, cy, 26, col))

    draw_panel(
        c, MARGIN + col_w + GAP, row1_y, col_w, row_h, "UKRAINE", NAVY,
        "CRIMEAN BRIDGE HIT AGAIN",
        "Ukraine strikes the bridge for a third time in a week as peace "
        "talks continue in Abu Dhabi.",
        icon=lambda cx, cy, col: icon_bridge(c, cx - 55, cy - 26, 110, col))

    draw_panel(
        c, MARGIN + 2 * (col_w + GAP), row1_y, col_w, row_h,
        "MARKETS", GREEN,
        "RECORD $81.3BN IPO DEBUT",
        "Anthropic, the maker of Claude, starts trading on Nasdaq as ANT "
        "after pricing the largest IPO ever.",
        icon=lambda cx, cy, col: icon_chart(c, cx - 55, cy - 30, 110, 52, col))

    draw_panel(
        c, MARGIN, row2_y, col_w, row_h, "JUSTICE", PURPLE,
        "ICJ TO RULE ON MYANMAR",
        "The world's top court prepares its verdict on genocide claims "
        "over the Rohingya.",
        icon=lambda cx, cy, col: icon_scales(c, cx, cy, col))

    draw_panel(
        c, MARGIN + col_w + GAP, row2_y, col_w, row_h, "SPACE", TEAL,
        "VOYAGER 1: ONE LIGHT-DAY",
        "NASA's probe, launched 50 years ago, is now a light-day from "
        "Earth - the farthest human-made object.",
        icon=lambda cx, cy, col: icon_voyager(c, cx, cy, col))

    # ---- also today ----------------------------------------------------
    ax = MARGIN + 2 * (col_w + GAP)
    ay = row2_y
    aw = col_w
    ah = row_h
    c.fill_rect(ax, ay, aw, ah, PANEL)
    c.rect(ax, ay, aw, ah, RULE, thick=2)
    c.fill_rect(ax, ay, aw, 30, INK)
    c.text(ax + 10, ay + 8, "ALSO TODAY", 2, WHITE)
    items = [
        "GTA VI ROLLS OUT WORLDWIDE",
        "JEFFRIES NOMINATED FOR US SPEAKER",
        "EU BACKS INDONESIA TRADE DEAL",
    ]
    iy = ay + 52
    for item in items:
        c.fill_rect(ax + 14, iy + 5, 8, 8, RED)
        for line in wrap_text(item, 2, aw - 44):
            c.text(ax + 32, iy, line, 2, INK)
            iy += 7 * 2 + 3
        iy += 12

    # ---- footer --------------------------------------------------------
    fy = row2_y + row_h + 18
    c.text_centered(WIDTH // 2, fy, "THE WORLD'S NEWS OF THURSDAY 19 NOVEMBER 2026",
                    2, INK)
    c.text_centered(WIDTH // 2, fy + 22, "ONE DAY. ONE IMAGE.", 2, GREY)

    return c


# --------------------------------------------------------------- main -----
def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    png = encode_png(build_image())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png)
    print("wrote %s (%d bytes)" % (path, len(png)))


if __name__ == "__main__":
    main()
