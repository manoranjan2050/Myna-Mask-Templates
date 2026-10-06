#!/usr/bin/env python3
"""Myna (मैना) paper/kraft-card face-mask templates -> 6 A4 SVG pages.

All units are millimetres (viewBox 0 0 210 297 == 210mm x 297mm).
Edit the constants below and re-run:  python generate_templates.py
"""
import os
import textwrap
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = ROOT

# ====================== EDITABLE DIMENSIONS (mm) ======================
CX = 105                 # page centre line
MASK_W, MASK_H = 155, 130
FACE_TOP = 32            # (design coordinates; page 1 shifts everything down by PAGE1_DY)
PAGE1_DY = 6
EYE_DX, EYE_Y = 28, 86   # eye centre offset from centre line / height
EYE_RX, EYE_RY = 13, 11  # see-through eye opening = 26 x 22 mm
HOLE_X, HOLE_Y, HOLE_R = 36, 100, 3   # elastic holes (dia 6 mm)
BLACK_S, YELLOW_S = 1.15, 0.97        # eye-shape scales (black outer / yellow ring)
YELLOW_HX, YELLOW_HY = 14.8, 12       # yellow ring hole radii
BEAK_A_LEN, BEAK_A_W = 28, 44         # upper beak length / width
BEAK_B_LEN, BEAK_B_W = 22, 34         # lower beak length / width

FACE_A, FACE_B = 35, 60                # face outline shape (top / chin roundness)
HEAD_L, HEAD_W = 26, 11                # head-feather size
CAP_COL = "#2A1A0E"                    # dark head-cap colour (colour guide)
SIDE_SIZES = [(50, 20), (42, 17)]      # page-4 large side feathers (L, W)
SIDE_X = (26, 60, 150, 184)
DESIGN_NAME = ""
EYE_CMDS = None

# ============================= STYLES ==============================
CUT = 'fill="none" stroke="#000" stroke-width="0.7" stroke-linejoin="round" stroke-linecap="round"'
FOLD = 'fill="none" stroke="#808080" stroke-width="0.5" stroke-dasharray="3 1.8"'
GLUE = 'fill="none" stroke="#1d5fe0" stroke-width="0.7" stroke-dasharray="0.1 1.4" stroke-linecap="round"'
PLACE = 'fill="none" stroke="#bdbdbd" stroke-width="0.3"'
FONT = "Arial, 'Nirmala UI', 'Noto Sans Devanagari', Mangal, sans-serif"

BROWN, DARK, YELLOW, ORANGE = "#9A6A3A", "#2E1D12", "#F6C915", "#F08A24"
LINE_BROWN = "#4a3018"


def n(v):
    return ("%.2f" % v).rstrip("0").rstrip(".")


# ============================ HELPERS ==============================
def T(x, y, s, size=3.4, anchor="start", weight="normal", fill="#000", extra=""):
    return (f'<text x="{n(x)}" y="{n(y)}" font-family="{FONT}" font-size="{n(size)}" '
            f'text-anchor="{anchor}" font-weight="{weight}" fill="{fill}" {extra}>{escape(s)}</text>')


def build(cmds, sx=1.0, sy=1.0, ox=0.0, oy=0.0):
    """cmds -> SVG path data, scaled / mirrored (negative sx) / offset."""
    out = []
    for c in cmds:
        k = c[0]
        if k == "Z":
            out.append("Z")
        elif k == "A":
            _, rx, ry, sw, (x, y) = c
            sweep = sw if sx * sy > 0 else 1 - sw
            out.append(f"A{n(abs(rx * sx))} {n(abs(ry * sy))} 0 0 {sweep} {n(ox + x * sx)} {n(oy + y * sy)}")
        else:
            pts = " ".join(f"{n(ox + x * sx)},{n(oy + y * sy)}" for x, y in c[1:])
            out.append(k + pts)
    return " ".join(out)


def ellipse_d(cx, cy, rx, ry):
    return (f"M{n(cx - rx)},{n(cy)} A{n(rx)} {n(ry)} 0 1 0 {n(cx + rx)},{n(cy)} "
            f"A{n(rx)} {n(ry)} 0 1 0 {n(cx - rx)},{n(cy)} Z")


def P(d, style, extra=""):
    return f'<path d="{d}" {style} {extra}/>'


def svg_open(title, desc):
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="210mm" height="297mm" '
            f'viewBox="0 0 210 297">\n<title>{escape(title)}</title>\n<desc>{escape(desc)}</desc>\n'
            f'<rect x="0" y="0" width="210" height="297" fill="#ffffff"/>')


def header(s, title, sub, page, tail=""):
    if DESIGN_NAME:
        sub = sub + "   ·   " + DESIGN_NAME
    s.append(T(10, 14.5, title, 6.2, weight="bold"))
    s.append(T(10, 21, sub, 3.6, fill="#333"))
    s.append(T(200, 14.5, f"Page {page} of 6", 3, "end", fill="#666"))
    if tail:
        s.append(T(200, 21, tail, 3, "end", fill="#666"))


def legend(s):
    s.append('<g id="legend">')
    s.append('<rect x="10" y="238" width="132" height="50" rx="2" fill="none" stroke="#bbb" stroke-width="0.3"/>')
    s.append(T(14, 243.2, "LEGEND", 3.2, weight="bold"))
    rows = [(CUT, "CUT  — solid black line"),
            (FOLD, "FOLD  — dashed grey line"),
            (GLUE, "GLUE / placement guide — dotted blue line"),
            (PLACE, "PLACEMENT — thin light grey line")]
    for i, (st, lab) in enumerate(rows):
        y = 248.5 + i * 5.6
        s.append(f'<line x1="14" y1="{n(y)}" x2="34" y2="{n(y)}" {st}/>')
        s.append(T(38, y + 1.1, lab, 3.2))
    s.append(T(14, 273.5, "Print at 100% (Actual Size). Never use “Fit to page”.", 3, fill="#333"))
    s.append(T(14, 278.5, "Cut this paper template, trace it on 200–300 GSM kraft/card,", 3, fill="#333"))
    s.append(T(14, 283.5, "then cut the card piece.", 3, fill="#333"))
    s.append("</g>")


def scale_check(s):
    x, y = 150, 238
    s.append('<g id="scale-check">')
    s.append(f'<rect x="{x}" y="{y}" width="50" height="50" fill="none" stroke="#000" stroke-width="0.5"/>')
    for i in range(1, 5):
        s.append(f'<line x1="{x + 10 * i}" y1="{y}" x2="{x + 10 * i}" y2="{y + 2.5}" stroke="#000" stroke-width="0.3"/>')
        s.append(f'<line x1="{x}" y1="{y + 10 * i}" x2="{x + 2.5}" y2="{y + 10 * i}" stroke="#000" stroke-width="0.3"/>')
    s.append(T(x + 25, y + 24, "50 mm SCALE CHECK", 3.6, "middle", "bold"))
    s.append(T(x + 25, y + 30, "Each side must measure", 2.7, "middle", fill="#444"))
    s.append(T(x + 25, y + 34, "exactly 50 mm with a ruler.", 2.7, "middle", fill="#444"))
    s.append("</g>")


def badge(x, y, num, r=3.1):
    return (f'<circle cx="{n(x)}" cy="{n(y)}" r="{r}" fill="#fff" stroke="#999" stroke-width="0.4"/>'
            + T(x, y + 1.15, str(num), 3.4, "middle", "bold", "#555"))


def finish(name, s):
    s.append("</svg>")
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
        fh.write("\n".join(s))
    print("wrote", name)


# ======================== SHAPE DEFINITIONS =========================
def face_d(cx=None, top=None, w=None, h=None):
    cx, top, w, h = cx or CX, top or FACE_TOP, w or MASK_W, h or MASK_H
    hw = w / 2
    mid = top + h * 0.4615   # widest point (y=92 for the default size)
    bot = top + h
    a, b = FACE_A, FACE_B
    return (f"M{n(cx)},{n(top)} C{n(cx + a)},{n(top)} {n(cx + hw)},{n(top + 18)} {n(cx + hw)},{n(mid)} "
            f"C{n(cx + hw)},{n(top + h * 0.82)} {n(cx + b)},{n(bot)} {n(cx)},{n(bot)} "
            f"C{n(cx - b)},{n(bot)} {n(cx - hw)},{n(top + h * 0.82)} {n(cx - hw)},{n(mid)} "
            f"C{n(cx - hw)},{n(top + 18)} {n(cx - a)},{n(top)} {n(cx)},{n(top)} Z")


def feather_cmds(L, W, bend=0.0):
    def b(x, y):
        return (x + bend * (-y / L) ** 2, y)
    return [("M", b(0, 0)),
            ("C", b(.55 * W, -.12 * L), b(.62 * W, -.60 * L), b(.14 * W, -.95 * L)),
            ("Q", b(0, -1.05 * L), b(-.14 * W, -.95 * L)),
            ("C", b(-.62 * W, -.60 * L), b(-.55 * W, -.12 * L), b(0, 0)),
            ("Z",)]


def feather_d(L, W, bend=0.0):
    return build(feather_cmds(L, W, bend))


def feather_fold_d(L, bend=0.0):
    t0, t1 = 0.10, 0.80
    d = t1 - t0
    p0 = (bend * t0 ** 2, -L * t0)
    p1 = (bend * t1 ** 2, -L * t1)
    c = (bend * (t0 ** 2 + t0 * d), -L * (t0 + t1) / 2)
    return f"M{n(p0[0])},{n(p0[1])} Q{n(c[0])},{n(c[1])} {n(p1[0])},{n(p1[1])}"


def scale_cmds(w, h):
    hw = w / 2
    r = min(2.0, w / 6)
    return [("M", (-hw + r, 0)), ("L", (hw - r, 0)), ("Q", (hw, 0), (hw, r)),
            ("L", (hw, h * .5)), ("C", (hw, h * .85), (w * .22, h), (0, h)),
            ("C", (-w * .22, h), (-hw, h * .85), (-hw, h * .5)),
            ("L", (-hw, r)), ("Q", (-hw, 0), (-hw + r, 0)), ("Z",)]


WING = [("M", (0, 6)),
        ("C", (14, -2), (40, -5), (62, 2)),
        ("C", (66, 10), (64, 17), (60, 22)),
        ("A", 10.2, 9, 1, (40, 25)),
        ("A", 10.2, 9, 1, (20, 25)),
        ("A", 10.2, 9, 1, (2, 22)),
        ("Q", (-2, 14), (0, 6)), ("Z",)]

EYE = [("M", (-19, 0)), ("C", (-19, -11), (-9, -15.5), (2, -15)),
       ("C", (13, -14.5), (22, -9), (27, -4)), ("Q", (30, -1), (27, 2)),
       ("C", (22, 9), (13, 14.5), (2, 15)), ("C", (-9, 15.5), (-19, 11), (-19, 0)), ("Z",)]


def eye_shape(cx, cy, scale, mirror, hole=None, k=1.0):
    m = -1 if mirror else 1
    d = build(EYE_CMDS or EYE, sx=scale * m * k, sy=scale * k, ox=cx, oy=cy)
    if hole:
        d += " " + ellipse_d(cx, cy, hole[0] * k, hole[1] * k)
    return d


# Feather placements on the mask (design coords). Left side; right side is the mirror image.
HEAD_PL = [(88, 54, -8), (79, 58, -24), (70, 64, -40)]          # x, y, rot  (L26 W11)
SIDE_PL = [(62, 104, -118, 46, 19), (66, 112, -133, 38, 16)]      # x, y, rot, L, W
WING_PL = (44, 118, 15, 0.65)                                     # x, y, rot, scale
SCALE_PL = [(92, 134, 24, 22), (84, 139, 18, 17), (77, 143, 13, 12)]  # x, y(top), w, h


def mirror_x(x):
    return 2 * CX - x


# ========================= PAGE 1 – MAIN MASK ========================
def page1():
    s = [svg_open("Myna Mask – 01 Main Mask", "A4 cutting template for the Myna face. Print at 100%.")]
    header(s, "मैना (MYNA) — MAIN MASK", "Print at 100% / Actual Size", 1,
           "Cut 1 · brown kraft / card")
    s.append(f'<g id="piece-main-face" class="piece" transform="translate(0 {PAGE1_DY})">')
    # ---- guides (drawn first, under cut lines)
    for sgn in (1, -1):
        mir = sgn == -1
        ex = CX - EYE_DX if not mir else CX + EYE_DX
        s.append(P(eye_shape(ex, EYE_Y, BLACK_S, not mir), PLACE))
        s.append(P(eye_shape(ex, EYE_Y, YELLOW_S, not mir), PLACE))
        # head feather fan
        for (x, y, r) in HEAD_PL:
            xx, rr = (x, r) if not mir else (mirror_x(x), -r)
            s.append(P(feather_d(HEAD_L, HEAD_W), PLACE, f'transform="translate({n(xx)} {n(y)}) rotate({rr})"'))
        for (x, y, r, L, W) in SIDE_PL:
            xx, rr = (x, r) if not mir else (mirror_x(x), -r)
            s.append(P(feather_d(L, W), PLACE, f'transform="translate({n(xx)} {n(y)}) rotate({rr})"'))
        wx, wy, wr, ws = WING_PL
        if not mir:
            s.append(P(build(WING, ws, ws), PLACE, f'transform="translate({wx} {wy}) rotate({wr})"'))
        else:
            s.append(P(build(WING, -ws, ws), PLACE, f'transform="translate({mirror_x(wx)} {wy}) rotate({-wr})"'))
        for (x, y, w, h) in SCALE_PL:
            xx = x if not mir else mirror_x(x)
            s.append(P(build(scale_cmds(w, h)), PLACE, f'transform="translate({n(xx)} {n(y)})"'))
    # centre guide
    s.append(f'<line x1="{CX}" y1="{FACE_TOP + 22}" x2="{CX}" y2="{FACE_TOP + 74}" {PLACE}/>')
    # ---- crease (fold) guides – optional, curve mask around face
    s.append(f'<line x1="{CX}" y1="{FACE_TOP + 1.5}" x2="{CX}" y2="{FACE_TOP + 21}" {FOLD}/>')
    s.append(f'<line x1="{CX}" y1="{FACE_TOP + 96}" x2="{CX}" y2="{FACE_TOP + MASK_H - 1.5}" {FOLD}/>')
    # ---- beak glue footprints
    ax, bx = BEAK_A_W / 2, BEAK_B_W / 2
    s.append(P(f"M{CX - ax},108 H{CX + ax} V117 H{CX - ax} Z", GLUE))
    s.append(P(f"M{CX - bx},119 H{CX + bx} V127 H{CX - bx} Z", GLUE))
    s.append(T(CX, 113.6, "A  upper beak tab", 2.6, "middle", fill="#1d5fe0"))
    s.append(T(CX, 124.4, "B  lower beak tab", 2.6, "middle", fill="#1d5fe0"))
    s.append(T(CX, 104.8, "BEAK GOES HERE", 2.4, "middle", fill="#1d5fe0"))
    # ---- feather letters
    for sgn in (1, -1):
        dx = 0 if sgn == 1 else None
    for (lbl, x, y) in (("H", 82, 52), ("S", 50, 128), ("W", 58, 146), ("C", 90, 154)):
        for xx in (x, mirror_x(x)):
            s.append(T(xx, y, lbl, 3.6, "middle", "bold", "#aaa"))
    # ---- CUT lines
    s.append(P(face_d(), CUT, 'id="cut-face"'))
    for dx in (-EYE_DX, EYE_DX):
        s.append(P(ellipse_d(CX + dx, EYE_Y, EYE_RX, EYE_RY), CUT))
    for x in (HOLE_X, mirror_x(HOLE_X)):
        s.append(f'<circle cx="{x}" cy="{HOLE_Y}" r="{HOLE_R}" {CUT}/>')
    s.append(T(CX - EYE_DX, EYE_Y + 0.9, "EYE", 3, "middle", fill="#999"))
    s.append(T(CX + EYE_DX, EYE_Y + 0.9, "EYE", 3, "middle", fill="#999"))
    s.append(T(HOLE_X, HOLE_Y + 7.2, "hole", 2.5, "middle", fill="#999"))
    s.append(T(mirror_x(HOLE_X), HOLE_Y + 7.2, "hole", 2.5, "middle", fill="#999"))
    s.append("</g>")
    # ---- notes
    ny = 182
    s.append(f'<g id="notes">')
    s.append(T(10, ny, "SIZE & NOTES", 3.4, weight="bold"))
    notes = [
        f"Face: {MASK_W} × {MASK_H} mm (about the size of a 7–10 year-old’s face). Beak sticks out 25–30 mm.",
        f"Eye openings: {2 * EYE_RX} × {2 * EYE_RY} mm, centres {2 * EYE_DX} mm apart. Hold up to the child’s face to check.",
        f"Side holes: Ø{2 * HOLE_R} mm – use a hole punch (on the card piece), then thread elastic / string.",
        "Dashed centre creases are optional: crease gently so the mask curves round the face.",
        "Blue dotted boxes = where the beak glue tabs go.  Light grey outlines = where eye shapes and",
        "feathers go.  H = head feathers   S = large side feathers   W = wing piece   C = chin scales",
        "(these pieces are on pages 3 and 4).  Left and right sides are mirror images.",
    ]
    for i, t in enumerate(notes):
        s.append(T(10, ny + 6 + i * 5, t, 3.0, fill="#222"))
    s.append("</g>")
    legend(s)
    scale_check(s)
    finish("01_main_mask.svg", s)


# ========================= PAGE 2 – BEAK ============================
A_CUT = ("M-19,-9 L19,-9 Q22,-9 22,-6 L22,12 C22,22 12,28 0,28 C-12,28 -22,22 -22,12 "
         "L-22,-6 Q-22,-9 -19,-9 Z")
B_CUT = ("M-14,-8 L14,-8 Q17,-8 17,-5 L17,2 L21,3 Q24,3.5 24,6.5 L24,11 Q24,14 21,14.5 L17,15 "
         "C17,19 10,22 0,22 C-10,22 -17,19 -17,15 L-21,14.5 Q-24,14 -24,11 L-24,6.5 Q-24,3.5 -21,3 "
         "L-17,2 L-17,-5 Q-17,-8 -14,-8 Z")


def page2():
    s = [svg_open("Myna Mask – 02 Beak", "A4 template for the folded 3D beak. Print at 100%.")]
    header(s, "BEAK — चोंच", "Print at 100% / Actual Size", 2,
           "Cut 1 of A + 1 of B · orange card")
    # --- upper beak A at (65, 62)
    s.append(T(65, 42, "A  UPPER BEAK", 3.6, "middle", "bold"))
    s.append('<g id="piece-beak-upper" class="piece" transform="translate(65 62)">')
    s.append(P(A_CUT, CUT))
    s.append(P("M-22,0 H22", FOLD))
    s.append(P("M0,0 V24", FOLD))
    s.append(P("M-19.5,-7.5 H19.5 V-1.5 H-19.5 Z", GLUE))
    s.append(T(0, -3.3, "Glue", 2.8, "middle", fill="#1d5fe0"))
    s.append(T(24.5, 1.1, "Fold", 2.6, fill="#666"))
    s.append(T(3.6, 8, "Fold (ridge)", 2.4, fill="#666", extra='transform="rotate(90 3.6 8)"'))
    s.append("</g>")
    s.append(badge(40, 50, 1))
    s.append(badge(65, 94, 4))
    # --- lower beak B at (145, 62)
    s.append(T(145, 42, "B  LOWER BEAK", 3.6, "middle", "bold"))
    s.append('<g id="piece-beak-lower" class="piece" transform="translate(145 62)">')
    s.append(P(B_CUT, CUT))
    s.append(P("M-17,0 H17", FOLD))
    s.append(P("M0,0 V18", FOLD))
    for sg in (1, -1):
        s.append(P(f"M{17 * sg},2 V15", FOLD))
        s.append(P(f"M{19 * sg},4.8 H{22.5 * sg} V12.5 H{19 * sg} Z", GLUE))
    s.append(P("M-14.5,-6.5 H14.5 V-1.5 H-14.5 Z", GLUE))
    s.append(T(0, -2.9, "Glue", 2.6, "middle", fill="#1d5fe0"))
    s.append(T(19.5, -1.4, "Fold", 2.6, fill="#666"))
    s.append(T(1.6, 4, "Fold (valley)", 2.4, "start", fill="#666", extra='transform="rotate(90 1.6 4)"'))
    s.append(T(22, 17.8, "Glue", 2.2, "middle", fill="#1d5fe0"))
    s.append(T(-22, 17.8, "Glue", 2.2, "middle", fill="#1d5fe0"))
    s.append("</g>")
    s.append(badge(120, 50, 2))
    s.append(badge(176, 76, 3))
    s.append(badge(145, 90, 4))
    # --- scale marks / side-view diagram (not to cut)
    s.append(T(10, 112, "SIDE VIEW (diagram — do not cut)", 3.2, weight="bold"))
    s.append('<g id="side-view">')
    s.append('<line x1="30" y1="116" x2="30" y2="168" stroke="#777" stroke-width="0.5"/>')
    s.append(T(30, 114.8, "mask face", 2.6, "middle", fill="#777"))
    s.append('<path d="M30,128 L56,133 Q61,136 56,139 L30,141 Z" fill="none" stroke="#777" stroke-width="0.5"/>')
    s.append('<path d="M30,143 L52,145 Q56,147 52,149 L30,151 Z" fill="none" stroke="#777" stroke-width="0.5"/>')
    s.append('<rect x="27" y="128" width="3" height="13" fill="#bbb"/>')
    s.append('<rect x="27" y="143" width="3" height="8" fill="#bbb"/>')
    s.append('<line x1="30" y1="160" x2="60" y2="160" stroke="#777" stroke-width="0.4"/>')
    s.append('<line x1="30" y1="158" x2="30" y2="162" stroke="#777" stroke-width="0.4"/>')
    s.append('<line x1="60" y1="158" x2="60" y2="162" stroke="#777" stroke-width="0.4"/>')
    s.append(T(45, 166, "25–30 mm", 3, "middle", fill="#555"))
    s.append(T(66, 134, "A upper beak (ridge)", 2.6, fill="#777"))
    s.append(T(62, 148.5, "B lower beak (valley)", 2.6, fill="#777"))
    s.append(T(17, 135, "tab", 2.4, "middle", fill="#777"))
    s.append("</g>")
    # --- steps
    s.append(T(112, 112, "HOW TO ASSEMBLE THE BEAK", 3.2, weight="bold"))
    steps = [
        "1  Trace A and B on orange card and cut them out (cut line = solid black).",
        "2  Crease every dashed FOLD line with a ruler and a blunt pencil/pen.",
        "3  A: fold the middle ridge outwards (a roof).",
        "    B: fold the middle inwards (a valley).",
        "3  Fold B’s side tabs up, glue under A’s sides.",
        "4  Fold both base tabs back (90°). Glue them on the mask in the dotted",
        "    beak boxes on page 1: A on top, B just below.",
        "Tip: keep the beak rounded — do not crease the tip.",
    ]
    for i, t in enumerate(steps):
        s.append(T(112, 119 + i * 5.6, t, 2.8, fill="#222"))
    # 3D-ish sketch of the finished beak
    s.append(T(10, 180, "FINISHED BEAK (sketch — not a cutting line)", 3.2, weight="bold"))
    s.append(beak_sketch(60, 207, 1.5))
    s.append(T(112, 192, "Use 200–300 GSM orange card.", 3, fill="#222"))
    s.append(T(112, 198, "Glue tabs are 8–9 mm deep so the beak", 3, fill="#222"))
    s.append(T(112, 203, "stays firm. Corners are rounded and the tip", 3, fill="#222"))
    s.append(T(112, 208, "is blunt, so it is safe for children.", 3, fill="#222"))
    legend(s)
    scale_check(s)
    finish("02_beak.svg", s)


def beak_sketch(cx, cy, k):
    """Small 3/4-view sketch of folded beak (grey outline, light fills). Origin = beak base centre."""
    def pt(x, y):
        return f"{n(cx + x * k)},{n(cy + y * k)}"
    out = ['<g id="beak-sketch" stroke="#777" stroke-width="0.4" stroke-linejoin="round">']
    # lower beak (behind/below)
    out.append(f'<polygon points="{pt(-9,3)} {pt(0,2)} {pt(1.5,14)} {pt(-5,10)}" fill="#f2c9a0"/>')
    out.append(f'<polygon points="{pt(9,3)} {pt(0,2)} {pt(1.5,14)} {pt(5,10)}" fill="#e3a974"/>')
    # upper beak
    out.append(f'<polygon points="{pt(-11,-6)} {pt(0,-7)} {pt(1,9)} {pt(-6,3)}" fill="#f9d6b0"/>')
    out.append(f'<polygon points="{pt(11,-6)} {pt(0,-7)} {pt(1,9)} {pt(6,3)}" fill="#eab183"/>')
    out.append(f'<polygon points="{pt(-11,-6)} {pt(11,-6)} {pt(11,-8.5)} {pt(-11,-8.5)}" fill="#ddd"/>')
    out.append("</g>")
    return "".join(out)


# ========================= PAGE 3 – EYES ============================
def page3():
    s = [svg_open("Myna Mask – 03 Eyes", "A4 template for eye pieces. Print at 100%.")]
    header(s, "EYES — आँखें", "Print at 100% / Actual Size", 3,
           "Black + yellow + white paper")
    # Row 1 black outer
    s.append(T(10, 30, "1  EYE OUTER SHAPES — Black paper (cut 1 left + 1 right)", 3.6, weight="bold"))
    for (cx, mir, lab) in ((65, True, "LEFT eye"), (145, False, "RIGHT eye")):
        s.append(f'<g id="black-{lab[:1].lower()}" class="piece">')
        s.append(P(eye_shape(cx, 54, BLACK_S, mir, (EYE_RX, EYE_RY)), CUT))
        s.append("</g>")
        s.append(T(cx, 78.5, lab, 3, "middle", fill="#444"))
    s.append(T(105, 54, "← outward", 2.6, "middle", fill="#aaa", extra='opacity="0"'))
    # Row 2 yellow ring
    s.append(T(10, 90, "2  YELLOW EYE RINGS — Yellow paper (cut 1 left + 1 right)", 3.6, weight="bold"))
    for (cx, mir, lab) in ((65, True, "LEFT eye"), (145, False, "RIGHT eye")):
        s.append(f'<g id="yellow-{lab[:1].lower()}" class="piece">')
        s.append(P(eye_shape(cx, 113, YELLOW_S, mir, (YELLOW_HX, YELLOW_HY)), CUT))
        s.append("</g>")
        s.append(T(cx, 135, lab, 3, "middle", fill="#444"))
    # Row 3 pupils
    s.append(T(10, 148, "3  PUPILS — Black paper (several sizes, 2 of each)", 3.6, weight="bold"))
    radii = [6.5, 6.5, 5.5, 5.5, 4.5, 4.5, 3.5, 3.5]
    for i, r in enumerate(radii):
        x = 22 + i * 23.7
        s.append(f'<g class="piece" id="pupil-{i + 1}"><circle cx="{n(x)}" cy="162" r="{r}" {CUT}/></g>')
        s.append(T(x, 173.5, f"Ø{n(2 * r)}", 2.7, "middle", fill="#555"))
    # Row 4 highlights
    s.append(T(10, 185, "4  HIGHLIGHTS — White paper (optional, 2 of each)", 3.6, weight="bold"))
    hr = [2.5, 2.5, 2.0, 2.0, 1.6, 1.6, 1.2, 1.2]
    for i, r in enumerate(hr):
        x = 22 + i * 23.7
        s.append(f'<g class="piece" id="shine-{i + 1}"><circle cx="{n(x)}" cy="196" r="{r}" {CUT}/></g>')
        s.append(T(x, 203, f"Ø{n(2 * r)}", 2.7, "middle", fill="#555"))
    # layering note
    s.append(T(10, 216, "LAYER ORDER:  ① black shape around the eye opening  →  ② yellow ring on top  →", 3.0, fill="#222"))
    s.append(T(10, 221.5, "③ pupil dot (beside the opening, or on the ring)  →  ④ white highlight on the pupil.", 3.0, fill="#222"))
    s.append(T(10, 227.5, f"Holes in pieces 1 and 2 match the {2 * EYE_RX} × {2 * EYE_RY} mm eye openings on page 1 — line them up.", 3.0, fill="#222"))
    legend(s)
    scale_check(s)
    finish("03_eyes.svg", s)


# ======================== PAGE 4 – FEATHERS =========================
def page4():
    s = [svg_open("Myna Mask – 04 Feathers", "A4 template for decorative feathers. Print at 100%.")]
    header(s, "FEATHERS — पंख", "Print at 100% / Actual Size", 4,
           "Left + right are mirror images")
    pid = [0]

    def piece(d, tx, ty, fold=None, rot=0):
        pid[0] += 1
        g = f'<g class="piece" id="f{pid[0]}" transform="translate({n(tx)} {n(ty)}) rotate({rot})">'
        g += P(d, CUT)
        if fold:
            g += P(fold, FOLD)
        return g + "</g>"

    def lr(x, y, lab):
        return T(x, y, lab, 3, "middle", "bold", "#555")

    # A large side feathers
    s.append(T(10, 30, "A  LARGE SIDE FEATHERS — brown card (2 big + 2 medium)", 3.6, weight="bold"))
    for (x, (L, W), b, lab) in ((SIDE_X[0], SIDE_SIZES[0], 7, "L"), (SIDE_X[1], SIDE_SIZES[1], 6, "L"),
                                (SIDE_X[2], SIDE_SIZES[1], -6, "R"), (SIDE_X[3], SIDE_SIZES[0], -7, "R")):
        s.append(piece(feather_d(L, W, b), x, 86, feather_fold_d(L, b)))
        s.append(lr(x, 92, lab))
    s.append(T(105, 62, "mirrored pairs", 2.8, "middle", fill="#888"))
    s.append(T(105, 66, "← LEFT      RIGHT →", 2.8, "middle", fill="#888"))
    # B small head feathers
    s.append(T(10, 97, f"B  SMALL HEAD FEATHERS — dark brown / black card ({len(HEAD_PL)} + {len(HEAD_PL)})", 3.6, weight="bold"))
    nh = len(HEAD_PL)
    sp = 22 if HEAD_W <= 12 else 24
    for i in range(nh):
        L = HEAD_L + 2 if i < 2 else HEAD_L - 2
        for (x, bd, lab) in ((22 + i * sp, 3, "L"), (210 - 22 - i * sp, -3, "R")):
            s.append(piece(feather_d(L, HEAD_W, bd), x, 136, feather_fold_d(L, bd)))
            s.append(lr(x, 142, lab))
    # C wing pieces
    s.append(T(10, 148, "C  WING-LIKE DECORATIVE PIECES — brown card (1 left + 1 right)", 3.6, weight="bold"))
    s.append(piece(build(WING), 14, 160, "M10,6 Q31,2 52,8"))
    s.append(piece(build(WING, sx=-1), 196, 160, "M-10,6 Q-31,2 -52,8"))
    s.append(lr(46, 197, "L"))
    s.append(lr(164, 197, "R"))
    s.append(T(105, 175, "tip: glue wings over", 2.8, "middle", fill="#888"))
    s.append(T(105, 179, "the feathers (layer 3)", 2.8, "middle", fill="#888"))
    # D layered scales
    s.append(T(10, 206, "D  LAYERED CHIN / CHEEK SCALES — light brown or kraft card (cut 2 of each size)", 3.6, weight="bold"))
    for x, (w, h) in zip((26, 56, 82, 128, 154, 184), ((24, 22), (18, 17), (13, 12)) * 2):
        s.append(piece(build(scale_cmds(w, h)), x, 211))
    s.append(T(40, 238 - 4, "LEFT set", 2.8, "middle", fill="#888"))
    s.append(T(170, 238 - 4, "RIGHT set", 2.8, "middle", fill="#888"))
    legend(s)
    scale_check(s)
    finish("04_feathers.svg", s)


# ====================== COLOUR ART (pages 5, 6) =====================
def mask_art(uid, face=True, eyes=True, feathers=True, beak=True, holes=True, cap=True,
             face_fill=None, outline=LINE_BROWN, sw=0.8):
    g = []
    face_fill = face_fill or BROWN
    g.append(f'<clipPath id="fc{uid}"><path d="{face_d()}"/></clipPath>')
    if face:
        g.append(P(face_d(), f'fill="{face_fill}" stroke="{outline}" stroke-width="{sw}" stroke-linejoin="round"'))
        if cap:
            g.append(f'<g clip-path="url(#fc{uid})"><path d="M0,0 L210,0 L210,64 C160,82 50,82 0,64 Z" fill="{CAP_COL}"/></g>')
        g.append(P(face_d(), f'fill="none" stroke="{outline}" stroke-width="{sw}" stroke-linejoin="round"'))
    ls = f'stroke="#1a0f08" stroke-width="{sw * .6}" stroke-linejoin="round"'
    if feathers:
        for mir in (False, True):
            wx, wy, wr, ws = WING_PL
            if mir:
                g.append(P(build(WING, -ws, ws), f'fill="#6E4220" {ls}', f'transform="translate({mirror_x(wx)} {wy}) rotate({-wr})"'))
            else:
                g.append(P(build(WING, ws, ws), f'fill="#6E4220" {ls}', f'transform="translate({wx} {wy}) rotate({wr})"'))
            # white wing spots
            for (px, py) in ((12, 12), (30, 16), (48, 12)):
                px2 = -px if mir else px
                g.append(f'<ellipse cx="{n(px2 * ws)}" cy="{n(py * ws)}" rx="3.4" ry="2" fill="#fff" '
                         f'transform="translate({n(mirror_x(wx) if mir else wx)} {wy}) rotate({-wr if mir else wr})"/>')
        for mir in (False, True):
            for i, (x, y, r, L, W) in enumerate(SIDE_PL):
                xx, rr = (mirror_x(x), -r) if mir else (x, r)
                bd = (-3 if mir else 3)
                g.append(P(feather_d(L, W, bd), f'fill="{["#7B4A22", "#8F5A2C"][i]}" {ls}', f'transform="translate({n(xx)} {y}) rotate({rr})"'))
                g.append(P(feather_fold_d(L, bd), f'fill="none" stroke="#4a2c12" stroke-width="0.35"', f'transform="translate({n(xx)} {y}) rotate({rr})"'))
        for mir in (False, True):
            for i, (x, y, w, h) in enumerate(SCALE_PL):
                xx = mirror_x(x) if mir else x
                g.append(P(build(scale_cmds(w, h)), f'fill="{["#C79A66", "#B98450", "#D2AA7A"][i]}" {ls}', f'transform="translate({n(xx)} {y})"'))
        for mir in (False, True):
            for (x, y, r) in HEAD_PL:
                xx, rr = (mirror_x(x), -r) if mir else (x, r)
                g.append(P(feather_d(HEAD_L, HEAD_W, -2 if mir else 2), f'fill="#4A3020" stroke="#120a05" stroke-width="{sw * .6}" stroke-linejoin="round"',
                           f'transform="translate({n(xx)} {y}) rotate({rr})"'))
    if eyes:
        for mir in (False, True):
            ex = CX + EYE_DX if mir else CX - EYE_DX
            g.append(P(eye_shape(ex, EYE_Y, BLACK_S, not mir), f'fill="#1a120c" stroke="#000" stroke-width="{sw * .6}"'))
            g.append(P(eye_shape(ex, EYE_Y, YELLOW_S, not mir), f'fill="{YELLOW}" stroke="#b8900a" stroke-width="{sw * .6}"'))
            g.append(P(ellipse_d(ex, EYE_Y, EYE_RX, EYE_RY), f'fill="#20140a" stroke="#000" stroke-width="{sw * .6}"'))
            g.append(f'<circle cx="{n(ex + (-4 if mir else 4))}" cy="{EYE_Y - 3.5}" r="2.4" fill="#fff"/>')
            g.append(f'<circle cx="{n(ex + (3 if mir else -3))}" cy="{EYE_Y + 3}" r="1.2" fill="#fff"/>')
    if beak:
        # lower beak (behind), upper beak in front
        g.append(P("M92,122 C92,135 98,146 105,147 C112,146 118,135 118,122 Z",
                   f'fill="#D9701A" stroke="#7a3a08" stroke-width="{sw * .6}" stroke-linejoin="round"'))
        g.append(P("M105,122 V147", f'fill="none" stroke="#7a3a08" stroke-width="{sw * .5}"'))
        g.append(P("M85,108 C85,124 96,141 105,141 L105,108 Z", f'fill="#F8A83C" stroke="#7a3a08" stroke-width="{sw * .6}" stroke-linejoin="round"'))
        g.append(P("M125,108 C125,124 114,141 105,141 L105,108 Z", f'fill="#EE8420" stroke="#7a3a08" stroke-width="{sw * .6}" stroke-linejoin="round"'))
        g.append(f'<ellipse cx="97" cy="116" rx="2.2" ry="2.8" fill="#7a3a08"/><ellipse cx="113" cy="116" rx="2.2" ry="2.8" fill="#7a3a08"/>')
    if holes:
        for x in (HOLE_X, mirror_x(HOLE_X)):
            g.append(f'<circle cx="{x}" cy="{HOLE_Y}" r="{HOLE_R}" fill="#fff" stroke="{outline}" stroke-width="{sw * .6}"/>')
    return "".join(g)


def at(x, y, k, inner, cx0=105, cy0=96):
    """Place design-coordinate content so that (cx0,cy0) lands on page (x,y) at scale k."""
    return f'<g transform="translate({n(x - cx0 * k)} {n(y - cy0 * k)}) scale({n(k)})">{inner}</g>'


# ====================== PAGE 5 – COLOUR GUIDE =======================
def page5():
    s = [svg_open("Myna Mask – 05 Colour Guide", "Finished mask colour guide (not a cutting template).")]
    s.append(T(105, 30, "मैना", 22, "middle", "bold", "#3b2412"))
    s.append(T(105, 41, "एक सुंदर पक्षी", 8, "middle", "normal", "#7a4a22"))
    s.append(T(105, 48.5, "MYNA — COLOUR GUIDE  (guide only: do not cut this page)", 3.4, "middle", fill="#666"))
    s.append(at(105, 125, 1.0, mask_art("p5")))
    marks = [(1, 52, 140, "#9A6A3A"), (2, 104, 66, "#2E1D12"), (3, 155, 70, YELLOW),
             (4, 126, 140, ORANGE), (5, 62, 135, "#fff")]
    # marker positions in page coords (mask drawn with +29 dy offset: design y -> page y = y + 29)
    for (num, x, y, col) in marks:
        pass
    pm = [(1, 44, 160), (2, 105, 85), (3, 170, 112), (4, 138, 168), (5, 76, 163)]
    for num, x, y in pm:
        s.append(f'<circle cx="{x}" cy="{y}" r="4.2" fill="#fff" stroke="#000" stroke-width="0.5"/>')
        s.append(T(x, y + 1.5, str(num), 4.2, "middle", "bold"))
    # swatches
    s.append(T(10, 202, "COLOURS", 3.8, weight="bold"))
    sw = [(1, BROWN, "BROWN", "face, large side feathers, wings, chin scales"),
          (2, CAP_COL, "DARK BROWN / BLACK", "head cap & head feathers, eye shapes, pupils"),
          (3, YELLOW, "YELLOW", "eye rings (the bare patch round a Myna’s eye)"),
          (4, ORANGE, "ORANGE", "beak (upper lighter, lower darker)"),
          (5, "#ffffff", "WHITE", "eye highlights and wing spots")]
    for i, (num, col, name, use) in enumerate(sw):
        y = 207 + i * 11.5
        s.append(f'<rect x="10" y="{y}" width="14" height="9" rx="2" fill="{col}" stroke="#555" stroke-width="0.4"/>')
        s.append(T(28, y + 3.6, f"{num}  {name}", 3.4, weight="bold"))
        s.append(T(28, y + 7.6, use, 2.7, fill="#444"))
    # materials
    s.append(T(122, 202, "MATERIAL LIST", 3.8, weight="bold"))
    mats = ["Brown cardstock / kraft card (200–300 GSM)", "Black cardstock", "Yellow cardstock",
            "Orange cardstock", "White paper (also for printing templates)", "Glue (stick or fevicol) + glue tape",
            "Scissors (adult help for small pieces)", "Hole punch", "Elastic or string (about 40 cm)"]
    for i, m in enumerate(mats):
        y = 208.5 + i * 5.8
        s.append(f'<rect x="122" y="{y - 2.6}" width="3" height="3" fill="none" stroke="#555" stroke-width="0.35"/>')
        s.append(T(127, y, m, 2.9, fill="#222"))
    s.append(T(105, 284, "Tip: any colours work — a real Myna has a brown body, dark head, yellow beak patch & eye ring.", 2.8, "middle", fill="#777"))
    finish("05_colour_guide.svg", s)


# ===================== PAGE 6 – ASSEMBLY GUIDE ======================
def mini_flat_face(uid):
    g = [f'<path d="{face_d()}" fill="#E7D2AC" stroke="#000" stroke-width="2.6" stroke-linejoin="round"/>']
    for dx in (-EYE_DX, EYE_DX):
        g.append(f'<path d="{ellipse_d(CX + dx, EYE_Y, EYE_RX, EYE_RY)}" fill="#fff" stroke="#000" stroke-width="2.2"/>')
    for x in (HOLE_X, mirror_x(HOLE_X)):
        g.append(f'<circle cx="{x}" cy="{HOLE_Y}" r="{HOLE_R}" fill="#fff" stroke="#000" stroke-width="2"/>')
    return "".join(g)


def scissors(x, y, k=1.0, rot=0):
    return (f'<g transform="translate({n(x)} {n(y)}) rotate({rot}) scale({k})" stroke="#444" stroke-width="0.5" fill="none">'
            '<circle cx="-2.2" cy="3.5" r="1.8"/><circle cx="2.2" cy="3.5" r="1.8"/>'
            '<line x1="-1.6" y1="2" x2="2.6" y2="-6"/><line x1="1.6" y1="2" x2="-2.6" y2="-6"/></g>')


def arrow(x1, y1, x2, y2, col="#777"):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="0.5"/>'
            f'<circle cx="{x2}" cy="{y2}" r="0.9" fill="{col}"/>')


def dia_step2():
    g = ['<g>']
    # black, yellow, pupil, shine in an exploded row (k small)
    g.append(P(eye_shape(11, 11, BLACK_S, False, (EYE_RX, EYE_RY), 0.3), 'fill="#1a120c" stroke="#000" stroke-width="0.3" fill-rule="evenodd"'))
    g.append(T(21, 12.5, "+", 4, "middle", fill="#666"))
    g.append(P(eye_shape(31, 11, YELLOW_S, False, (YELLOW_HX, YELLOW_HY), 0.3), f'fill="{YELLOW}" stroke="#b8900a" stroke-width="0.3" fill-rule="evenodd"'))
    g.append(f'<circle cx="9" cy="28" r="3.3" fill="#1a120c"/>')
    g.append(T(16, 29.5, "+", 4, "middle", fill="#666"))
    g.append(f'<circle cx="23" cy="28" r="1.4" fill="#fff" stroke="#999" stroke-width="0.3"/>')
    g.append(scissors(36, 30, 1.0, 20))
    g.append("</g>")
    return "".join(g)


def dia_step3():
    g = []
    # flat A (left)
    g.append(P(A_CUT, 'fill="#F8C58A" stroke="#000" stroke-width="0.5" stroke-linejoin="round"', 'transform="translate(10 10) scale(0.38)"'))
    g.append(P("M-22,0 H22 M0,0 V24", 'fill="none" stroke="#777" stroke-width="1.2" stroke-dasharray="4 2.5"', 'transform="translate(10 10) scale(0.38)"'))
    g.append(P(B_CUT, 'fill="#F4A55E" stroke="#000" stroke-width="0.5" stroke-linejoin="round"', 'transform="translate(10 28) scale(0.38)"'))
    g.append(P("M-17,0 H17 M0,0 V18", 'fill="none" stroke="#777" stroke-width="1.2" stroke-dasharray="4 2.5"', 'transform="translate(10 28) scale(0.38)"'))
    g.append(arrow(22, 20, 27, 20))
    g.append(beak_sketch(34, 16, 0.85).replace('stroke="#777"', 'stroke="#7a3a08"'))
    return "".join(g)


def dia_step7(uid):
    g = []
    g.append(P(face_d(), 'fill="#CDAE7C" stroke="#4a3018" stroke-width="2.4" stroke-linejoin="round"'))
    for x in (HOLE_X, mirror_x(HOLE_X)):
        g.append(f'<circle cx="{x}" cy="{HOLE_Y}" r="{HOLE_R}" fill="#fff" stroke="#4a3018" stroke-width="2"/>')
    g.append(f'<path d="M{HOLE_X},{HOLE_Y} C-10,{HOLE_Y + 70} 220,{HOLE_Y + 70} {mirror_x(HOLE_X)},{HOLE_Y}" fill="none" stroke="#c0392b" stroke-width="3"/>')
    g.append(f'<circle cx="{HOLE_X}" cy="{HOLE_Y}" r="4.6" fill="#c0392b"/><circle cx="{mirror_x(HOLE_X)}" cy="{HOLE_Y}" r="4.6" fill="#c0392b"/>')
    g.append(T(105, 70, "BACK", 16, "middle", "bold", "#8a6b3a"))
    return "".join(g)


def page6():
    s = [svg_open("Myna Mask – 06 Assembly Guide", "Step-by-step assembly instructions (not a cutting template).")]
    s.append(T(10, 14.5, "ASSEMBLY GUIDE — कैसे बनाएँ", 6.2, weight="bold"))
    s.append(T(200, 14.5, "Page 6 of 6", 3, "end", fill="#666"))
    s.append(T(10, 21, "A child + a parent / teacher: the adult helps with scissors and the hole punch.", 3.2, fill="#333"))
    # how-to-use strip
    s.append('<rect x="10" y="25" width="190" height="20" rx="2" fill="#f6efe2" stroke="#d6c7a8" stroke-width="0.3"/>')
    strip = ["1  Print pages 1–4 at 100% on white A4 (check the 50 mm square).",
             "2  Cut out the paper templates along the solid black lines.",
             "3  Place on kraft / card (200–300 GSM), trace around each one.",
             "4  Cut the card pieces. Crease the dashed lines. Then follow steps 1–8."]
    for i, t in enumerate(strip):
        cx = 13 + (i % 2) * 95
        cy = 31.5 + (i // 2) * 8
        for j, ln in enumerate(textwrap.wrap(t, 48)):
            s.append(T(cx, cy + j * 3.6, ln, 2.8, fill="#222"))
    steps = [
        ("Cut the main face", "मुख्य चेहरा काटें",
         "Trace page 1 on brown card. Cut the outside edge and the two eye openings. Punch the two side holes."),
        ("Cut the eyes", "आँखें काटें",
         "Page 3: black shapes, yellow rings, black pupils and white highlights."),
        ("Fold & assemble the beak", "चोंच मोड़कर जोड़ें",
         "Page 2: crease the dashed lines. Glue B’s side tabs under A. Keep the tip rounded."),
        ("Attach the eyes", "आँखें चिपकाएँ",
         "Glue the black shape round each opening, the yellow ring on top, then pupil and white dot."),
        ("Attach layered feathers", "पंख परत-दर-परत चिपकाएँ",
         "Page 4: glue big feathers first, then wings and scales, and head feathers last. Let them overlap."),
        ("Attach the beak", "चोंच चिपकाएँ",
         "Fold the base tabs back. Glue them into the dotted beak boxes: A on top, B below. Hold for 30 s."),
        ("Make & attach the elastic", "इलास्टिक / डोरी लगाएँ",
         "Thread elastic or string through both side holes, knot it, and fit it to the child’s head."),
        ("Your Myna mask is ready!", "आपका मैना मास्क तैयार!",
         "Add details with markers if you like. Put it on and chirp like a Myna!"),
    ]
    bw, bh, gx, gy = 92, 53, 6, 4
    x0, y0 = 10, 49
    for i, (title, hindi, desc) in enumerate(steps):
        bx = x0 + (i % 2) * (bw + gx)
        by = y0 + (i // 2) * (bh + gy)
        s.append(f'<g id="step-{i + 1}">')
        s.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="3" fill="#fffdf8" stroke="#c9b894" stroke-width="0.4"/>')
        # diagram area
        dx, dy = bx + 3, by + 9
        s.append(f'<rect x="{dx}" y="{dy}" width="43" height="38" rx="2" fill="#fbf6ea" stroke="#eadfc6" stroke-width="0.3"/>')
        k = 0.235
        cxm, cym = dx + 21.5, dy + 19
        uid = f"s{i + 1}"
        if i == 0:
            s.append(at(cxm, cym, k, mini_flat_face(uid)))
            s.append(scissors(dx + 36, dy + 8, 1.2, 35))
        elif i == 1:
            s.append(f'<g transform="translate({dx} {dy})">{dia_step2()}</g>')
        elif i == 2:
            s.append(f'<g transform="translate({dx} {dy})">{dia_step3()}</g>')
        elif i == 3:
            s.append(at(cxm, cym, k, mask_art(uid, feathers=False, beak=False)))
        elif i == 4:
            s.append(at(cxm, cym, k * 0.92, mask_art(uid, beak=False)))
        elif i == 5:
            s.append(at(cxm, cym, k * 0.92, mask_art(uid)))
        elif i == 6:
            s.append(at(cxm, cym - 1, k * 0.8, dia_step7(uid)))
        else:
            s.append(at(cxm, cym, k * 0.92, mask_art(uid)))
            s.append('<text x="%s" y="%s" font-size="6" fill="#e0a800">★</text>' % (n(dx + 36), n(dy + 7)))
        # number badge + text
        s.append(f'<circle cx="{bx + 7}" cy="{by + 6.5}" r="4.4" fill="#D2691E"/>')
        s.append(T(bx + 7, by + 8.3, str(i + 1), 5, "middle", "bold", "#fff"))
        s.append(T(bx + 14, by + 7, title, 3.6, weight="bold", fill="#3b2412"))
        s.append(T(bx + 49, by + 15.5, hindi, 3.1, fill="#7a4a22"))
        for j, ln in enumerate(textwrap.wrap(desc, 27)):
            s.append(T(bx + 49, by + 21.5 + j * 3.9, ln, 2.8, fill="#222"))
        s.append("</g>")
    s.append(T(105, 287, "मैना — एक सुंदर पक्षी   ·   MYNA school craft project", 3, "middle", fill="#888"))
    finish("06_assembly_guide.svg", s)


EYE_ROUND = [("M", (-18, 0)), ("C", (-18, -10), (-10, -17), (0, -17)), ("C", (10, -17), (18, -10), (18, 0)),
             ("C", (18, 10), (10, 17), (0, 17)), ("C", (-10, 17), (-18, 10), (-18, 0)), ("Z",)]

BASE = dict(MASK_W=155, MASK_H=130, FACE_A=35, FACE_B=60, HEAD_L=26, HEAD_W=11, CAP_COL="#2A1A0E",
            BROWN="#9A6A3A", EYE_CMDS=None, BLACK_S=1.15, YELLOW_S=0.97, YELLOW_HX=14.8, YELLOW_HY=12,
            HOLE_X=36, SIDE_SIZES=[(50, 20), (42, 17)], SIDE_X=(26, 60, 150, 184), DESIGN_NAME="",
            HEAD_PL=[(88, 54, -8), (79, 58, -24), (70, 64, -40)],
            SIDE_PL=[(62, 104, -118, 46, 19), (66, 112, -133, 38, 16)])
DESIGNS = {
    "Design_1_Classic": dict(DESIGN_NAME="Design 1: Classic"),
    "Design_2_Round_Cute": dict(
        DESIGN_NAME="Design 2: Round & Cute", MASK_W=150, MASK_H=134, FACE_A=42, FACE_B=72, HOLE_X=38,
        BROWN="#B5803F", CAP_COL="#5B3A1E", EYE_CMDS=EYE_ROUND, BLACK_S=1.2, YELLOW_S=0.95,
        YELLOW_HX=14.6, YELLOW_HY=12, HEAD_L=22, HEAD_W=15,
        HEAD_PL=[(90, 56, -6), (80, 60, -22), (70, 66, -38)],
        SIDE_SIZES=[(48, 25), (40, 21)], SIDE_X=(30, 70, 140, 180),
        SIDE_PL=[(62, 104, -118, 44, 23), (66, 112, -133, 36, 19)]),
    "Design_3_Crested_Myna": dict(
        DESIGN_NAME="Design 3: Crested Myna", MASK_W=155, MASK_H=138, FACE_A=20, FACE_B=40,
        BROWN="#7D5A3C", CAP_COL="#1B1B22", HEAD_L=32, HEAD_W=12,
        HEAD_PL=[(93, 52, -6), (85, 55, -18), (77, 60, -30), (69, 66, -42)],
        SIDE_SIZES=[(52, 21), (44, 18)]),
}

if __name__ == "__main__":
    for folder, cfg in DESIGNS.items():
        globals().update(BASE)
        globals().update(cfg)
        OUT = os.path.join(ROOT, folder)
        os.makedirs(OUT, exist_ok=True)
        print("==", folder)
        for fn in (page1, page2, page3, page4, page5, page6):
            fn()
