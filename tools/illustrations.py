# Top of file: scene generators for Arangath website illustrations. Each scene returns an S object; call .svg(attrs) to get an SVG string.
import math
from contextlib import contextmanager

C = 0.8660254
LABELS = True
FLOW = False   # live pages set True: adds an animatable dashed overlay on pipes (class 'flow')
# palette
CON_T, CON_L, CON_R = "#C9D3DD", "#8997A7", "#A8B5C3"   # concrete top / +y face / +x face
BLD_T, BLD_L, BLD_R = "#7F8EA0", "#56657A", "#6A7A8F"    # building roof / faces
WAT, WAT_HI = "#2F7FB8", "#7CC4EE"
STEEL = "#E8EEF3"
P_RAW, P_AIR, P_SLUDGE, P_DOSE = "#4FB3E8", "#B7A6F5", "#C98F5A", "#E3D26F"
GROUND, GRID = "#1A2531", "#26344A"
AMBER = "#F2A541"
OUT = "#0D1319"


def P(x, y, z=0):
    return ((x - y) * C, (x + y) * 0.5 - z)


class S:
    def __init__(s, pfx='a'):
        s.pfx = pfx
        s.el = []
        s.pts = []

    def _track(s, pts):
        s.pts.extend(pts)

    def poly(s, pts3, fill, stroke=OUT, sw=0.08, op=1, extra=""):
        pts = [P(*p) for p in pts3]
        s._track(pts)
        d = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
        o = f' opacity="{op}"' if op != 1 else ""
        s.el.append(f'<polygon points="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{o}{extra}></polygon>')

    def line(s, pts3, color, w, op=1, cap="round", dash=None, cls=None):
        pts = [P(*p) for p in pts3]
        s._track(pts)
        d = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
        o = f' opacity="{op}"' if op != 1 else ""
        da = f' stroke-dasharray="{dash}"' if dash else ""
        c = f' class="{cls}"' if cls else ""
        if cls == "flow" and dash:
            c += f' style="--p:{sum(float(v) for v in dash.split()):.2f}"'   # dash period, so the CSS animation loops seamlessly
        s.el.append(f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="{cap}" stroke-linejoin="round"{o}{da}{c}></polyline>')

    @contextmanager
    def g(s, layer, tip=None, key=None):
        """Wrap everything drawn inside in <g data-layer=...>. Live pages toggle layers and read data-tip / data-key.
        Static <img> use is unaffected: groups have no visual effect on their own."""
        a = f' data-layer="{layer}"'
        if key:
            a += f' data-key="{key}" data-tip="{tip}" class="hot"'
        s.el.append(f"<g{a}>")
        try:
            yield
        finally:
            s.el.append("</g>")

    def raw(s, txt, pts=None):
        if pts:
            s._track(pts)
        s.el.append(txt)

    # ---------- primitives ----------
    def box(s, x, y, z, w, d, h, t=CON_T, l=CON_L, r=CON_R, sw=0.08):
        s.poly([(x, y + d, z), (x + w, y + d, z), (x + w, y + d, z + h), (x, y + d, z + h)], l, sw=sw)
        s.poly([(x + w, y, z), (x + w, y + d, z), (x + w, y + d, z + h), (x + w, y, z + h)], r, sw=sw)
        s.poly([(x, y, z + h), (x + w, y, z + h), (x + w, y + d, z + h), (x, y + d, z + h)], t, sw=sw)

    def ground(s, x0, y0, x1, y1, step=4):
        s.poly([(x0, y0, 0), (x1, y0, 0), (x1, y1, 0), (x0, y1, 0)], GROUND, stroke=GRID, sw=0.1)
        x = x0 + step
        while x < x1:
            s.line([(x, y0, 0), (x, y1, 0)], GRID, 0.08)
            x += step
        y = y0 + step
        while y < y1:
            s.line([(x0, y, 0), (x1, y, 0)], GRID, 0.08)
            y += step

    def tank(s, x, y, z, w, d, h, t=0.6, water=0.5, cells=1):
        """open rectangular tank with water; cells split along x"""
        s.box(x, y, z, w, d, h, sw=0.08)
        # inner void (draw water + inner back walls)
        cw = (w - t * (cells + 1)) / cells
        for i in range(cells):
            ix = x + t + i * (cw + t)
            iy, id_ = y + t, d - 2 * t
            top = z + h
            wl = top - water
            # inner back walls (faces at ix plane facing +x, iy plane facing +y)
            s.poly([(ix, iy, wl), (ix, iy + id_, wl), (ix, iy + id_, top), (ix, iy, top)], CON_R, sw=0.05)
            s.poly([(ix, iy, wl), (ix + cw, iy, wl), (ix + cw, iy, top), (ix, iy, top)], CON_L, sw=0.05)
            s.poly([(ix, iy, wl), (ix + cw, iy, wl), (ix + cw, iy + id_, wl), (ix, iy + id_, wl)], WAT, sw=0.05, op=0.95)
            s.line([(ix + cw * 0.2, iy + id_ * 0.3, wl), (ix + cw * 0.6, iy + id_ * 0.3, wl)], WAT_HI, 0.12, op=0.7)
            s.line([(ix + cw * 0.35, iy + id_ * 0.65, wl), (ix + cw * 0.8, iy + id_ * 0.65, wl)], WAT_HI, 0.12, op=0.5)

    def rail(s, pts, h=1.1, post=2.0, color=STEEL):
        top = [(x, y, z + h) for x, y, z in pts]
        s.line(top, color, 0.09)
        s.line([(x, y, z + h * 0.5) for x, y, z in pts], color, 0.05, op=0.7)
        for (a, b) in zip(pts, pts[1:]):
            L = math.dist(a[:2], b[:2])
            n = max(1, int(L / post))
            for k in range(n + 1):
                f = k / n
                px, py, pz = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, a[2]
                s.line([(px, py, pz), (px, py, pz + h)], color, 0.06)

    def cyl(s, cx, cy, z, r, h, side=CON_R, side2=CON_L, top=CON_T, sw=0.08):
        (sx, sy) = P(cx, cy, z)
        rx, ry = r * math.sqrt(2) * C, r * math.sqrt(2) * 0.5
        (tx, ty) = P(cx, cy, z + h)
        s._track([(sx - rx, sy + ry), (sx + rx, ty - ry)])
        gid = f"{s.pfx}g{len(s.el)}"
        s.el.append(f'<defs><linearGradient id="{gid}" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="{side2}"></stop><stop offset="0.55" stop-color="{side}"></stop><stop offset="1" stop-color="{side2}"></stop></linearGradient></defs>')
        s.el.append(f'<path d="M{sx-rx:.2f},{ty:.2f} L{sx-rx:.2f},{sy:.2f} A{rx:.2f},{ry:.2f} 0 0 0 {sx+rx:.2f},{sy:.2f} L{sx+rx:.2f},{ty:.2f} Z" fill="url(#{gid})" stroke="{OUT}" stroke-width="{sw}"></path>')
        s.el.append(f'<ellipse cx="{tx:.2f}" cy="{ty:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" fill="{top}" stroke="{OUT}" stroke-width="{sw}"></ellipse>')
        return tx, ty, rx, ry

    def ell(s, cx, cy, z, r, fill, stroke="none", sw=0.08, op=1):
        (x, y) = P(cx, cy, z)
        rx, ry = r * math.sqrt(2) * C, r * math.sqrt(2) * 0.5
        s._track([(x - rx, y - ry), (x + rx, y + ry)])
        o = f' opacity="{op}"' if op != 1 else ""
        s.el.append(f'<ellipse cx="{x:.2f}" cy="{y:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{o}></ellipse>')

    def clarifier(s, cx, cy, r, h, rails=True, tip=None, key=None):
        with s.g("structure", tip=tip, key=key):
            s.cyl(cx, cy, 0, r, h)
            s.ell(cx, cy, h, r - 0.5, WAT)
            # launder ring + inner
            s.ell(cx, cy, h - 0.05, r - 1.3, "none", stroke=CON_T, sw=0.25)
            s.ell(cx, cy, h, r * 0.35, "none", stroke=WAT_HI, sw=0.12, op=0.7)
            for k in range(12):
                a = k * math.pi / 6
                s.line([(cx + math.cos(a) * r * 0.36, cy + math.sin(a) * r * 0.36, h), (cx + math.cos(a) * (r - 1.4), cy + math.sin(a) * (r - 1.4), h)], WAT_HI, 0.07, op=0.45)
        with s.g("equipment", tip="Scraper bridge and centre column" if tip else None, key=(key + "-eq") if key else None):
            s.cyl(cx, cy, h - 0.2, 1.1, 1.6, side="#B8C4D0", side2="#7D8B9B", top="#D8E0E8", sw=0.06)
            # bridge
            bx0, bx1 = cx, cx + r + 0.6
            s.box(bx0, cy - 0.6, h + 0.6, bx1 - bx0, 1.2, 0.35, t="#DCE3EA", l="#9AA8B7", r="#B7C3CF", sw=0.05)
            s.box(bx1 - 0.3, cy - 0.9, h - 0.1, 0.9, 1.8, 1.2, t="#D8E0E8", l="#8D9BAA", r="#A9B6C3", sw=0.05)
            if rails:
                s.rail([(bx0, cy - 0.6, h + 0.95), (bx1, cy - 0.6, h + 0.95)], h=0.9, post=1.5)
                s.rail([(bx0, cy + 0.6, h + 0.95), (bx1, cy + 0.6, h + 0.95)], h=0.9, post=1.5)

    def pipe(s, pts, color, w=0.55, valves=(), flow=None, tip=None, key=None):
        flow = FLOW if flow is None else flow
        with s.g("pipework", tip=tip, key=key):
            s.line(pts, "#0D1319", w + 0.2)
            s.line(pts, color, w)
            s.line([(x, y, z + w * 0.18) for x, y, z in pts], "#FFFFFF", w * 0.22, op=0.35)
            if flow:
                s.line(pts, "#FFFFFF", max(w * 0.3, 0.1), op=0.7, cap="butt", dash=f"{w*1.2:.2f} {w*2.6:.2f}", cls="flow")
        for v in valves:
            x, y, z = v
            (px, py) = P(x, y, z)
            q = w * 1.3
            with s.g("equipment", tip="Isolation valve", key=f"valve-{len(s.el)}"):
                s.el.append(f'<path d="M{px-q:.2f},{py-q:.2f} L{px+q:.2f},{py+q:.2f} L{px+q:.2f},{py-q:.2f} L{px-q:.2f},{py+q:.2f} Z" fill="{STEEL}" stroke="{OUT}" stroke-width="0.06"></path>')
                s.el.append(f'<line x1="{px:.2f}" y1="{py:.2f}" x2="{px:.2f}" y2="{py-q*2:.2f}" stroke="{STEEL}" stroke-width="0.12"></line><line x1="{px-q:.2f}" y1="{py-q*2:.2f}" x2="{px+q:.2f}" y2="{py-q*2:.2f}" stroke="{STEEL}" stroke-width="0.15"></line>')

    def building(s, x, y, z, w, d, h, windows=True):
        s.box(x, y, z, w, d, h, t=BLD_T, l=BLD_L, r=BLD_R)
        # parapet line
        s.line([(x, y + d, z + h - 0.3), (x + w, y + d, z + h - 0.3), (x + w, y, z + h - 0.3)], "#8FA0B3", 0.06)
        if windows:
            n = max(1, int(w / 3))
            for i in range(n):
                wx = x + (i + 0.5) * w / n - 0.6
                s.poly([(wx, y + d, z + h * 0.45), (wx + 1.2, y + d, z + h * 0.45), (wx + 1.2, y + d, z + h * 0.75), (wx, y + d, z + h * 0.75)], "#9FD3F2", sw=0.04, op=0.8)
            m = max(1, int(d / 3))
            for j in range(m):
                wy = y + (j + 0.5) * d / m - 0.6
                s.poly([(x + w, wy, z + h * 0.45), (x + w, wy + 1.2, z + h * 0.45), (x + w, wy + 1.2, z + h * 0.75), (x + w, wy, z + h * 0.75)], "#9FD3F2", sw=0.04, op=0.8)
            # door
            s.poly([(x + w * 0.15, y + d, z), (x + w * 0.15 + 1.6, y + d, z), (x + w * 0.15 + 1.6, y + d, z + 2.4), (x + w * 0.15, y + d, z + 2.4)], "#3B4A5C", sw=0.04)

    def clash(s, x, y, z, label=None, sub=None, scale=1.0):
        (px, py) = P(x, y, z)
        r = 1.1 * scale
        s.el.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="{r*1.9:.2f}" fill="{AMBER}" opacity="0.22"></circle><circle cx="{px:.2f}" cy="{py:.2f}" r="{r:.2f}" fill="none" stroke="{AMBER}" stroke-width="{0.3*scale:.2f}"></circle><circle cx="{px:.2f}" cy="{py:.2f}" r="{r*0.35:.2f}" fill="{AMBER}"></circle>')
        if label and LABELS:
            bx, by = px + 3 * scale, py + 2.5 * scale
            bw, bh = 21 * scale, 6.2 * scale
            s._track([(bx + bw, by + bh)])
            s.el.append(f'<line x1="{px+r:.2f}" y1="{py+r*0.5:.2f}" x2="{bx:.2f}" y2="{by+1.5*scale:.2f}" stroke="{AMBER}" stroke-width="{0.12*scale:.2f}"></line>')
            s.el.append(f'<rect x="{bx:.2f}" y="{by:.2f}" width="{bw:.2f}" height="{bh:.2f}" rx="{1*scale:.2f}" fill="#0D1319" stroke="{AMBER}" stroke-width="{0.15*scale:.2f}"></rect>')
            s.el.append(f'<text x="{bx+1.4*scale:.2f}" y="{by+2.6*scale:.2f}" font-family="DM Sans, sans-serif" font-weight="700" font-size="{1.9*scale:.2f}" fill="{AMBER}">{label}</text>')
            if sub:
                s.el.append(f'<text x="{bx+1.4*scale:.2f}" y="{by+4.9*scale:.2f}" font-family="DM Sans, sans-serif" font-size="{1.6*scale:.2f}" fill="#A7B4C2">{sub}</text>')

    def label(s, x, y, z, txt, color="#A7B4C2", size=1.8, anchor="start", weight=400):
        (px, py) = P(x, y, z)
        s._track([(px, py - size), (px + len(txt) * size * 0.55, py)])
        s.el.append(f'<text x="{px:.2f}" y="{py:.2f}" font-family="DM Sans, sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{txt}</text>')

    def svg(s, attrs, pad=2.0, label_=""):
        xs = [p[0] for p in s.pts]
        ys = [p[1] for p in s.pts]
        x0, y0, x1, y1 = min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad
        vb = f"{x0:.2f} {y0:.2f} {x1-x0:.2f} {y1-y0:.2f}"
        a = f' aria-label="{label_}" role="img"' if label_ else ' aria-hidden="true"'
        return f'<svg {attrs} viewBox="{vb}"{a}>' + "".join(s.el) + "</svg>"


# ---------------- scenes ----------------
def filter_block(s, x, y, cells=4):
    w, d = 22, 12
    s.tank(x, y, 0, w, d, 5.5, t=0.6, water=1.0, cells=cells)
    # walkway rails on top of cell walls (front)
    s.rail([(x, y + d, 5.5), (x + w, y + d, 5.5)], h=1.0, post=2.2)
    # pipe gallery in front (roofless)
    gy = y + d
    s.poly([(x, gy, 0), (x + w, gy, 0), (x + w, gy + 5, 0), (x, gy + 5, 0)], "#2A3848", sw=0.05)
    s.box(x, gy + 4.4, 0, w, 0.6, 3.2)  # front wall low
    for k in range(cells):
        cx = x + 0.6 + k * ((w - 0.6) / cells) + 2.3
        s.pipe([(cx, gy, 3.2), (cx, gy + 1.6, 3.2), (cx, gy + 1.6, 1.2)], P_RAW, w=0.45, valves=[(cx, gy + 1.6, 2.2)])
        s.pipe([(cx + 1.6, gy, 2.2), (cx + 1.6, gy + 3.0, 2.2)], P_AIR, w=0.35)
    s.pipe([(x - 2, gy + 1.6, 1.2), (x + w + 2, gy + 1.6, 1.2)], P_RAW, w=0.75)
    s.pipe([(x - 2, gy + 3.0, 2.2), (x + w + 1, gy + 3.0, 2.2)], P_AIR, w=0.5)


def hero():
    s = S()
    s.ground(-4, -4, 66, 44, step=4)
    # raw water inlet
    s.pipe([(-4, 22, 1.2), (4, 22, 1.2)], P_RAW, w=0.8, valves=[(1, 22, 1.2)])
    s.clarifier(15, 22, 11, 4.5)
    # sludge line from clarifier
    s.pipe([(15, 33, 0.6), (15, 40, 0.6), (36, 40, 0.6)], P_SLUDGE, w=0.55)
    # outlet to filters
    s.pipe([(26, 20, 3.0), (32, 20, 3.0), (32, 14, 3.0), (34, 14, 3.0)], P_RAW, w=0.7, valves=[(29, 20, 3.0)])
    filter_block(s, 34, 2, cells=4)
    # chemical house
    s.building(40, 28, 0, 13, 9, 5.5)
    s.pipe([(40, 32, 1.0), (30, 32, 1.0), (30, 22, 3.2)], P_DOSE, w=0.3)
    s.pipe([(46, 28, 3.0), (46, 21, 3.0)], P_AIR, w=0.45)
    s.clash(46, 23.2, 3.0, "Clash 014 · resolved", "Air main vs gallery wall", scale=1.0)
    return s


def clarifier_scene():
    s = S()
    s.ground(-2, -2, 30, 30, step=4)
    s.pipe([(-2, 14, 1.0), (3, 14, 1.0)], P_RAW, w=0.7, valves=[(0.5, 14, 1.0)])
    s.clarifier(14, 14, 11, 4.5)
    s.pipe([(14, 25, 0.6), (14, 30, 0.6)], P_SLUDGE, w=0.5)
    s.pipe([(25, 12, 3.0), (30, 12, 3.0)], P_RAW, w=0.65, valves=[(28, 12, 3.0)])
    return s


def filter_scene():
    s = S()
    s.ground(-4, -2, 28, 22, step=4)
    filter_block(s, 0, 0, cells=4)
    return s


def pump_station():
    s = S()
    s.ground(-4, -4, 26, 22, step=4)
    X, Y, W, D, H = 0, 0, 18, 14, 7
    # wet well (below ground, cut open) shown as recess
    s.poly([(2, 9, -0.01), (16, 9, -0.01), (16, 13, -0.01), (2, 13, -0.01)], "#0A1016", sw=0.05)
    s.poly([(2, 9, -4), (16, 9, -4), (16, 9, 0), (2, 9, 0)], CON_L, sw=0.05)
    s.poly([(2, 9, -4), (2, 13, -4), (2, 13, 0), (2, 9, 0)], CON_R, sw=0.05)
    s.poly([(2, 9, -2.2), (16, 9, -2.2), (16, 13, -2.2), (2, 13, -2.2)], WAT, sw=0.05, op=0.9)
    # floor slab & back walls (cutaway)
    s.poly([(X, Y, 0), (X + W, Y, 0), (X + W, Y + 9, 0), (X, Y + 9, 0)], "#B3BFCC", sw=0.06)
    s.box(X, Y, 0, 0.5, D, H)           # back-left wall (x plane)
    s.box(X, Y, 0, W, 0.5, H)           # back-right wall (y plane)
    for i in range(3):
        s.poly([(X + 0.5, Y + 2 + i * 4, 3.5), (X + 0.5, Y + 3.4 + i * 4, 3.5), (X + 0.5, Y + 3.4 + i * 4, 5.2), (X + 0.5, Y + 2 + i * 4, 5.2)], "#9FD3F2", sw=0.04, op=0.7)
    # crane beam
    s.line([(1, 7, 6.3), (17, 7, 6.3)], "#E3D26F", 0.35)
    s.line([(9, 7, 6.3), (9, 7, 4.6)], STEEL, 0.08)
    s.box(8.6, 6.6, 4.2, 0.8, 0.8, 0.5, t="#E3D26F", l="#A89A45", r="#C7B757", sw=0.04)
    # pumps
    for px in (5, 11):
        s.cyl(px, 11, -2.2, 0.9, 2.2, side="#5D7FA3", side2="#34506E", top="#7FA0C2", sw=0.05)
        s.cyl(px, 11, 0.0, 0.7, 1.6, side="#4FB3E8", side2="#2C6E99", top="#8FD0F2", sw=0.05)
        s.pipe([(px, 11, 1.6), (px, 11, 2.6), (px, 6, 2.6)], P_RAW, w=0.55, valves=[(px, 8.5, 2.6)])
    s.pipe([(3, 6, 2.6), (22, 6, 2.6)], P_RAW, w=0.8, valves=[(15, 6, 2.6)])
    s.cyl(19.5, 6, 0, 0.8, 4.2, side="#8FA0B3", side2="#56657A", top="#B7C3CF", sw=0.05)  # surge vessel
    s.clash(15, 6, 2.6, "Clash 007", "Valve vs crane path", scale=0.55)
    return s


def exploded_layers():
    s = S()
    gap = 5.0
    names = [("Structure", "#A8B5C3"), ("Process pipework", P_RAW), ("Equipment", "#B7A6F5")]
    for i, (nm, col) in enumerate(names):
        z = i * gap
        s.poly([(0, 0, z), (20, 0, z), (20, 14, z), (0, 14, z)], "#1E2B39", stroke="#3A4A5C", sw=0.1, op=0.95)
        if i == 0:
            s.box(2, 2, z, 7, 5, 1.6)
            s.box(11, 2, z, 7, 5, 1.6)
            s.box(2, 9, z, 16, 3, 1.2)
        elif i == 1:
            s.pipe([(1, 4, z + 0.6), (19, 4, z + 0.6)], P_RAW, w=0.5, valves=[(10, 4, z + 0.6)])
            s.pipe([(1, 10, z + 0.6), (14, 10, z + 0.6), (14, 4, z + 0.6)], P_RAW, w=0.4)
            s.pipe([(6, 1, z + 0.6), (6, 13, z + 0.6)], P_AIR, w=0.35)
        else:
            for px, py in ((4, 4), (9, 4), (14, 4)):
                s.cyl(px, py, z, 0.9, 1.4, side="#B7A6F5", side2="#6E5FB0", top="#D6CCFA", sw=0.05)
            s.box(3, 9, z, 5, 3, 1.5, t=BLD_T, l=BLD_L, r=BLD_R)
        s.label(22, 14, z + 0.3, nm, color="#EEF4F1", size=1.5, weight=700)
    for (x, y) in ((0, 14), (20, 14), (20, 0)):
        s.line([(x, y, 0), (x, y, 2 * gap)], "#3A4A5C", 0.08, dash="0.5 0.4")
    # audited badge
    (bx, by) = P(20, 0, 2 * gap + 2.5)
    s.el.append(f'<circle cx="{bx:.2f}" cy="{by:.2f}" r="2.2" fill="#34C17F"></circle><path d="M{bx-1.0:.2f},{by:.2f} L{bx-0.25:.2f},{by+0.8:.2f} L{bx+1.1:.2f},{by-0.8:.2f}" fill="none" stroke="#06211A" stroke-width="0.4"></path>')
    s._track([(bx - 2.2, by - 2.2), (bx + 2.2, by + 2.2)])
    s.el.append(f'<text x="{bx+3:.2f}" y="{by+0.5:.2f}" font-family="DM Sans, sans-serif" font-size="1.5" font-weight="700" fill="#34C17F">Audited</text>'); s._track([(bx+12, by)])
    return s


def laptop():
    s = S()
    s.ground(-6, -4, 30, 22, step=4)
    # laptop base
    s.box(2, 4, 0, 16, 11, 0.5, t="#3A4A5C", l="#243140", r="#2E3C4E", sw=0.06)
    s.poly([(4, 6, 0.51), (16, 6, 0.51), (16, 12, 0.51), (4, 12, 0.51)], "#2A3746", sw=0.03)
    # screen on plane x=2 (faces +x) standing up
    x0 = 2
    s.poly([(x0, 4, 0.5), (x0, 15, 0.5), (x0, 15, 9.5), (x0, 4, 9.5)], "#243140", sw=0.08)
    s.poly([(x0 + 0.02, 4.6, 1.1), (x0 + 0.02, 14.4, 1.1), (x0 + 0.02, 14.4, 8.9), (x0 + 0.02, 4.6, 8.9)], "#0F1822", sw=0.04)
    # content on screen: elevation of tank + pipe (coords y,z on plane)
    def sp(y, z):
        return (x0 + 0.03, y, z)
    s.poly([sp(5.5, 2), sp(10, 2), sp(10, 4.6), sp(5.5, 4.6)], "#8997A7", sw=0.03)
    s.poly([sp(6, 3.6), sp(9.5, 3.6), sp(9.5, 4.4), sp(6, 4.4)], WAT, sw=0.02)
    s.line([sp(10, 3), sp(13.5, 3), sp(13.5, 5.8)], P_RAW, 0.3)
    s.line([sp(5, 6.8), sp(9, 6.8)], "#EEF4F1", 0.15, op=0.8)
    s.line([sp(5, 7.6), sp(12, 7.6)], "#A7B4C2", 0.1, op=0.8)
    (cx, cy) = P(x0, 12.8, 7.2)
    s.el.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="0.9" fill="#34C17F"></circle>')
    # floating documents (BEP, EIR, templates)
    docs = [("Templates", 24, 2, 3), ("EIR", 24, 2, 7.5), ("BEP", 24, 2, 12)]
    for nm, dx, dy, dz in docs:
        s.poly([(dx, dy, dz), (dx + 5, dy, dz), (dx + 5, dy + 4, dz), (dx, dy + 4, dz)], "#DCE3EA", stroke="#8997A7", sw=0.06)
        for k in range(3):
            s.line([(dx + 0.8, dy + 0.8 + k * 1.0, dz), (dx + 4, dy + 0.8 + k * 1.0, dz)], "#8997A7", 0.08)
        s.label(dx + 5.8, dy, dz, nm, color="#EEF4F1", size=1.4, weight=700)
        s.line([(dx, dy + 2, dz), (18, 9, 0.5)], "#3A4A5C", 0.06, dash="0.4 0.4")
    return s


def long_section(attrs):
    """2D long section of a sewer, drawn as an engineering section."""
    W, H = 500, 260
    el = []
    # ground profile
    gp = [(20, 70), (90, 62), (160, 72), (240, 66), (320, 80), (400, 74), (480, 86)]
    d = "M" + " L".join(f"{x},{y}" for x, y in gp)
    el.append(f'<path d="{d} L480,230 L20,230 Z" fill="#1A2531"></path>')
    el.append(f'<path d="{d}" fill="none" stroke="#8997A7" stroke-width="2"></path>')
    # design ground dashed (older survey)
    gp2 = [(20, 76), (90, 70), (160, 76), (240, 74), (320, 84), (400, 82), (480, 90)]
    el.append('<path d="M' + " L".join(f"{x},{y}" for x, y in gp2) + '" fill="none" stroke="#B7A6F5" stroke-width="1.3" stroke-dasharray="5 4"></path>')
    # road hatch
    el.append('<rect x="200" y="60" width="90" height="10" fill="#3A4A5C"></rect>')
    # manholes
    mh = [(40, 67, 150), (180, 70, 166), (330, 81, 184), (460, 84, 200)]
    for x, gy, inv in mh:
        el.append(f'<rect x="{x-9}" y="{gy}" width="18" height="{inv-gy+8}" fill="#A8B5C3" stroke="#0D1319" stroke-width="1"></rect><rect x="{x-5}" y="{gy+2}" width="10" height="{inv-gy+2}" fill="#243140"></rect>')
        el.append(f'<text x="{x}" y="{inv+24}" text-anchor="middle" font-family="DM Sans, sans-serif" font-size="10" fill="#A7B4C2">IL {round(12.5-(inv-150)/40,2)}</text>')
    # pipe with gradient
    el.append('<path d="M40 158 L180 174 L330 192 L460 208" fill="none" stroke="#0D1319" stroke-width="11" stroke-linecap="round"></path><path d="M40 158 L180 174 L330 192 L460 208" fill="none" stroke="#4FB3E8" stroke-width="8" stroke-linecap="round"></path><path d="M40 156 L180 172 L330 190 L460 206" fill="none" stroke="#FFFFFF" stroke-width="1.5" opacity="0.35"></path>')
    el.append('<text x="72" y="150" font-family="DM Sans, sans-serif" font-size="10" fill="#8FD0F2">450 DN · 1:200</text><text x="356" y="183" font-family="DM Sans, sans-serif" font-size="10" fill="#8FD0F2">600 DN · 1:150</text>')
    # existing services
    el.append('<circle cx="250" cy="178" r="7" fill="#E3D26F" stroke="#0D1319" stroke-width="1"></circle><text x="250" y="212" text-anchor="middle" font-family="DM Sans, sans-serif" font-size="10" fill="#E3D26F">Existing water main</text>')
    el.append('<circle cx="112" cy="120" r="4" fill="#B7A6F5"></circle><text x="104" y="116" text-anchor="end" font-family="DM Sans, sans-serif" font-size="10" fill="#B7A6F5">Telecom duct</text>')
    # clash near crossing
    el.append(f'<circle cx="250" cy="180" r="16" fill="{AMBER}" opacity="0.2"></circle><circle cx="250" cy="180" r="10" fill="none" stroke="{AMBER}" stroke-width="2"></circle>')
    if LABELS: el.append(f'<rect x="190" y="94" width="136" height="34" rx="6" fill="#0D1319" stroke="{AMBER}" stroke-width="1"></rect><text x="198" y="108" font-family="DM Sans, sans-serif" font-size="10" font-weight="700" fill="{AMBER}">Crossing 03 · 180 mm</text><text x="198" y="121" font-family="DM Sans, sans-serif" font-size="9.5" fill="#A7B4C2">below minimum cover</text><line x1="250" y1="170" x2="252" y2="128" stroke="{AMBER}" stroke-width="1"></line>')
    # legend
    el.append('<g font-family="DM Sans, sans-serif" font-size="10" fill="#A7B4C2"><line x1="24" y1="30" x2="44" y2="30" stroke="#8997A7" stroke-width="2"></line><text x="50" y="34">Scanned ground</text><line x1="150" y1="30" x2="170" y2="30" stroke="#B7A6F5" stroke-width="1.3" stroke-dasharray="5 4"></line><text x="176" y="34">Design ground</text></g>')
    return f'<svg {attrs} viewBox="0 0 {W} {H}" aria-hidden="true">' + "".join(el) + "</svg>"


def header_bg(attrs):
    s = hero()
    inner = s.svg('width="720" height="280"', pad=2)
    # position on right side, faded
    return f'<svg {attrs} viewBox="0 0 1440 280" aria-hidden="true"><g opacity="0.55">' + inner.replace('<svg width="720" height="280"', '<svg x="700" y="0" width="720" height="280"') + '</g></svg>'


def datacentre():
    s = S()
    s.ground(-4, -4, 46, 34, step=4)
    X, Y, W, D, H = 0, 0, 26, 20, 6
    # hall floor + back walls (roof removed)
    s.poly([(X, Y, 0), (X + W, Y, 0), (X + W, Y + D, 0), (X, Y + D, 0)], "#3A4A5C", sw=0.06)
    s.box(X, Y, 0, 0.5, D, H, t=BLD_T, l=BLD_L, r=BLD_R)
    s.box(X, Y, 0, W, 0.5, H, t=BLD_T, l=BLD_L, r=BLD_R)
    # rack rows with LEDs and cable trays above
    for i in range(4):
        ry = 3 + i * 4.2
        s.box(3, ry, 0, 18, 1.4, 2.4, t="#2F3D4E", l="#1C2633", r="#243140", sw=0.05)
        for k in range(9):
            x = 3.6 + k * 2
            s.line([(x, ry + 1.4, 0.6), (x, ry + 1.4, 2.0)], "#4FB3E8", 0.12, op=0.8)
        s.line([(3, ry + 0.7, 3.4), (21, ry + 0.7, 3.4)], "#E3D26F", 0.35)
    # chilled water supply / return into hall
    s.pipe([(40, 8, 1.2), (24, 8, 1.2), (24, 8, 4.2), (2, 8, 4.2)], P_RAW, w=0.55, valves=[(32, 8, 1.2)])
    s.pipe([(40, 12, 1.2), (24.5, 12, 1.2), (24.5, 12, 4.8), (2, 12, 4.8)], P_AIR, w=0.55)
    # chiller / cooling yard
    for j in range(3):
        cy_ = 2 + j * 7
        s.box(32, cy_, 0, 9, 5, 2.6, t="#A8B5C3", l="#6A7A8F", r="#8997A7", sw=0.06)
        for f in range(2):
            s.ell(34 + f * 4.2, cy_ + 2.5, 2.61, 1.5, "#1C2633", stroke="#C9D3DD", sw=0.1)
            s.line([(34 + f * 4.2 - 1.2, cy_ + 2.5, 2.62), (34 + f * 4.2 + 1.2, cy_ + 2.5, 2.62)], "#C9D3DD", 0.07)
    s.clash(12, 8, 4.2, "Clash 021", "CHW pipe vs cable tray", scale=0.75)
    return s


def drainage_network():
    s = S()
    X0, X1, Y0, Y1, Z0 = 0, 44, 0, 22, -6
    # buried elements first
    s.pipe([(-1, 11, -4.2), (45, 11, -5.0)], P_RAW, w=0.9)          # sewer (falls along x)
    s.pipe([(22, -1, -1.6), (22, 23, -1.6)], "#E3D26F", w=0.5)       # existing water main
    s.pipe([(8, -1, -0.9), (8, 23, -0.9)], "#B7A6F5", w=0.3)         # telecom duct
    for mx, z in ((6, -4.35), (22, -4.6), (38, -4.85)):
        s.cyl(mx, 11, z - 0.4, 1.3, -z + 0.4, side="#A8B5C3", side2="#6A7A8F", top="#C9D3DD", sw=0.05)
    # soil cut faces (x-ray)
    s.poly([(X0, Y1, Z0), (X1, Y1, Z0), (X1, Y1, 0), (X0, Y1, 0)], "#5A4A3A", stroke="#8C7A66", sw=0.08, op=0.2)
    s.poly([(X1, Y0, Z0), (X1, Y1, Z0), (X1, Y1, 0), (X1, Y0, 0)], "#6B5A48", stroke="#8C7A66", sw=0.08, op=0.2)
    # road surface (translucent) with footpaths and markings
    s.poly([(X0, Y0, 0), (X1, Y0, 0), (X1, 4, 0), (X0, 4, 0)], "#6A7A8F", stroke=OUT, sw=0.06, op=0.3)
    s.poly([(X0, 4, 0), (X1, 4, 0), (X1, 18, 0), (X0, 18, 0)], "#243140", stroke=OUT, sw=0.06, op=0.35)
    s.poly([(X0, 18, 0), (X1, 18, 0), (X1, Y1, 0), (X0, Y1, 0)], "#6A7A8F", stroke=OUT, sw=0.06, op=0.3)
    s.line([(X0, 11, 0.01), (X1, 11, 0.01)], "#EEF4F1", 0.18, op=0.8, dash="2 1.6", cap="butt")
    for mx in (6, 22, 38):
        s.ell(mx, 11, 0.02, 1.0, "#1C2633", stroke="#C9D3DD", sw=0.12)
    # depth tag
    s.line([(44.6, 11, 0), (44.6, 11, -5.0)], "#A7B4C2", 0.07)
    s.label(45.2, 11, -2.2, "5.0 m deep", size=1.3)
    s.clash(22, 11, -1.6, "Crossing 03", "Water main 180 mm above sewer", scale=0.75)
    return s


def header_bg2(attrs, fn, pfx):
    S.__init__.__defaults__ = (pfx,)
    s = fn()
    inner = s.svg('x="700" y="0" width="720" height="280"', pad=2)
    return f'<svg {attrs} viewBox="0 0 1440 280" aria-hidden="true"><g opacity="0.55">' + inner + '</g></svg>'


def hydraulic_profile(attrs):
    """2D hydraulic profile through a treatment works: water surfaces stepping down unit to unit."""
    el = []
    F = "DM Sans, sans-serif"
    el.append('<path d="M10 200 H590" stroke="#8997A7" stroke-width="1.5"></path>')
    el.append(f'<text x="14" y="216" font-family="{F}" font-size="10" fill="#7D8A99">Ground level</text>')
    units = [("Inlet", 30, 70, 40, 150), ("Aerator", 110, 60, 58, 160), ("Clariflocculator", 200, 110, 78, 190),
             ("Filters", 340, 90, 98, 180), ("Clear water tank", 460, 110, 122, 230)]
    prev = None
    for name, x, w, wl, bot in units:
        top = wl - 14
        el.append(f'<rect x="{x}" y="{top}" width="{w}" height="{bot-top}" fill="#1A2531" stroke="#A8B5C3" stroke-width="2"></rect>')
        el.append(f'<rect x="{x+2}" y="{wl}" width="{w-4}" height="{bot-wl-2}" fill="#2F7FB8" opacity="0.85"></rect>')
        el.append(f'<path d="M{x+2} {wl} H{x+w-2}" stroke="#7CC4EE" stroke-width="2"></path>')
        el.append(f'<path d="M{x+w/2-5} {wl-6} L{x+w/2+5} {wl-6} L{x+w/2} {wl-1} Z" fill="#7CC4EE"></path>')
        el.append(f'<text x="{x+w/2}" y="{top-8}" text-anchor="middle" font-family="{F}" font-size="10.5" font-weight="700" fill="#EEF4F1">{name}</text>')
        if prev:
            px, pw, pwl = prev
            el.append(f'<path d="M{px+pw} {pwl+6} H{x}" stroke="#4FB3E8" stroke-width="5" stroke-linecap="round"></path>')
        prev = (x, w, wl)
    # hydraulic gradient line
    el.append('<path d="M30 40 L180 58 L310 78 L430 98 L570 122" fill="none" stroke="#F2A541" stroke-width="1.5" stroke-dasharray="6 4"></path>')
    el.append(f'<text x="320" y="62" font-family="{F}" font-size="10" fill="#F2A541">Hydraulic grade line</text>')
    return f'<svg {attrs} viewBox="0 0 600 240" aria-hidden="true">' + "".join(el) + "</svg>"


# ---------------- Kerala projects ----------------
# These three scenes are grouped into layers for the live models on the project pages:
#   structure / pipework / equipment (the bridge uses structure / equipment / water, as it has no pipework).
# Groups with a key carry data-tip / data-key so the page can show tooltips and a keyboard-reachable key-elements list.
def regulator_bridge(bays=8):
    s = S()
    L = bays * 6
    with s.g("structure"):
        s.poly([(-6, -14, -1), (L + 6, -14, -1), (L + 6, 16, -1), (-6, 16, -1)], "#1E2A36", stroke=GRID, sw=0.08)
    with s.g("structure", tip="River banks", key="banks"):
        s.poly([(-6, -14, 0), (-1, -14, 0), (-1, 16, 0), (-6, 16, 0)], "#3B4A3A", stroke=OUT, sw=0.06)
        s.poly([(L + 1, -14, 0), (L + 6, -14, 0), (L + 6, 16, 0), (L + 1, 16, 0)], "#3B4A3A", stroke=OUT, sw=0.06)
    # upstream (high) and downstream (low) water
    with s.g("water", tip="Upstream water, held higher by the gates", key="upstream"):
        s.poly([(-1, -14, 3.2), (L + 1, -14, 3.2), (L + 1, 0, 3.2), (-1, 0, 3.2)], WAT, stroke="none", op=0.9)
        for k in range(5):
            y = -12 + k * 2.6
            s.line([(2 + k * 3, y, 3.21), (L - 6 + k * 3, y, 3.21)], WAT_HI, 0.12, op=0.5, dash="3 2.4", cls="flow")
    with s.g("water", tip="Downstream water, at a lower level", key="downstream"):
        s.poly([(-1, 2, 0.8), (L + 1, 2, 0.8), (L + 1, 16, 0.8), (-1, 16, 0.8)], "#2A6E9E", stroke="none", op=0.85)
        for k in range(5):
            y = 5 + k * 2.2
            s.line([(4 + k * 5, y, 0.81), (L - 8 + k * 5, y, 0.81)], WAT_HI, 0.1, op=0.4, dash="3 2.4", cls="flow")
    # piers and gates, drawn bay by bay so the depth order stays right
    for i in range(bays + 1):
        x = i * 6
        with s.g("structure", tip="Pier" if i == 0 else None, key="pier" if i == 0 else None):
            s.box(x - 0.6, -0.6, -1, 1.2, 3.2, 7.2)
    for i in range(bays):
        x0, x1 = i * 6 + 0.6, (i + 1) * 6 - 0.6
        first = i == 0
        with s.g("equipment", tip="Vertical-lift sluice gate" if first else None, key="gate" if first else None):
            s.poly([(x0, 0.4, -1), (x1, 0.4, -1), (x1, 0.4, 3.6), (x0, 0.4, 3.6)], "#7FA0C2", stroke=OUT, sw=0.06)
            for zz in (0.6, 1.8, 3.0):
                s.line([(x0, 0.4, zz), (x1, 0.4, zz)], "#5D7FA3", 0.12)
        with s.g("equipment", tip="Gate hoist frame" if first else None, key="hoist" if first else None):
            s.line([(x0 + 0.3, 1.0, 6.2), (x0 + 0.3, 1.0, 9.2), (x1 - 0.3, 1.0, 9.2), (x1 - 0.3, 1.0, 6.2)], "#E3D26F", 0.22)
            s.box((x0 + x1) / 2 - 0.7, 0.4, 8.6, 1.4, 1.2, 0.8, t="#E3D26F", l="#A89A45", r="#C7B757", sw=0.04)
    # deck with road
    with s.g("structure", tip="Bridge deck and road", key="deck"):
        s.box(-1, -0.8, 6.2, L + 2, 3.6, 0.7, t="#8997A7", l="#6A7A8F", r="#7F8EA0")
        s.poly([(-1, -0.4, 6.91), (L + 1, -0.4, 6.91), (L + 1, 2.4, 6.91), (-1, 2.4, 6.91)], "#2F3D4E", sw=0.03)
        s.line([(-1, 1.0, 6.92), (L + 1, 1.0, 6.92)], "#EEF4F1", 0.12, dash="1.2 1", cap="butt")
        s.rail([(-1, 2.6, 6.9), (L + 1, 2.6, 6.9)], h=0.9, post=2.4)
    # break lines at both ends
    for x in (-1, L + 1):
        (px, py) = P(x, 1, 7.6)
        s.el.append(f'<path d="M{px-1:.2f},{py-3:.2f} l1.2,1.2 l-1.2,1.2 l1.2,1.2 l-1.2,1.2" fill="none" stroke="#EEF4F1" stroke-width="0.25"></path>')
    s.label(L * 0.05, -12, 3.3, "Upstream pond", color="#DDE4EB", size=1.5)
    s.label(L * 0.62, 12, 0.9, "Downstream", color="#DDE4EB", size=1.5)
    (tx, ty) = P(L * 0.72, 1, 15)
    s.el.append(f'<rect x="{tx-14:.2f}" y="{ty-3.2:.2f}" width="28" height="4.6" rx="2.3" fill="#0D1319" stroke="#4FB3E8" stroke-width="0.15"></rect><text x="{tx:.2f}" y="{ty:.2f}" text-anchor="middle" font-family="DM Sans, sans-serif" font-size="1.9" font-weight="700" fill="#EEF4F1">978 m · 70 sluice gates</text>')
    s._track([(tx - 14, ty - 3.2), (tx + 14, ty + 1.4)])
    return s


def house(s, x, y):
    s.box(x, y, 0, 2.4, 2.0, 1.6, t="#B8A48C", l="#8C7A66", r="#A08C74", sw=0.05)
    s.poly([(x, y, 1.6), (x + 2.4, y, 1.6), (x + 2.4, y + 2.0, 1.6), (x, y + 2.0, 1.6)], "#9A5A48", sw=0.05)
    s.poly([(x, y + 1.0, 2.4), (x + 2.4, y + 1.0, 2.4), (x + 2.4, y + 2.0, 1.6), (x, y + 2.0, 1.6)], "#B06A55", sw=0.05)


def rural_water_supply():
    """Jal Jeevan Mission scheme as described on the project page: tube wells, treatment, pumping station,
    elevated service reservoirs on columns, underground distribution mains, household connections."""
    s = S()
    with s.g("structure"):
        s.ground(-6, -4, 56, 40, step=4)
    # tube wells -> collector -> treatment unit
    s.pipe([(3, 4, 0.5), (6, 4, 0.5), (6, 16, 0.5), (10, 16, 0.5)], P_RAW, w=0.35, tip="Raw water collector", key="collector")
    s.pipe([(3, 10, 0.5), (6, 10, 0.5)], P_RAW, w=0.35)
    s.pipe([(3, 16, 0.5), (6, 16, 0.5)], P_RAW, w=0.35)
    for k, ty in enumerate((4, 10, 16)):
        with s.g("structure", tip="Tube well" if k == 0 else None, key="tubewell" if k == 0 else None):
            s.cyl(3, ty, 0, 0.6, 2.4, top="#C9D3DD")
        with s.g("equipment", tip="Tube well pump" if k == 0 else None, key="tw-pump" if k == 0 else None):
            s.box(2.4, ty - 0.5, 2.4, 1.2, 1.0, 0.8, t="#E3D26F", l="#A89A45", r="#C7B757", sw=0.04)
    s.label(0, 19, 2.6, "Tube wells", color="#DDE4EB", size=1.4, anchor="end")
    # elevated service reservoirs (far side, drawn early)
    for n, cx in enumerate((34, 46)):
        cy = 4
        with s.g("structure", tip="Elevated service reservoir on columns" if n == 0 else None, key="reservoir" if n == 0 else None):
            for dx, dy in ((-1.8, -1.8), (1.8, -1.8), (-1.8, 1.8), (1.8, 1.8)):
                s.line([(cx + dx, cy + dy, 0), (cx + dx * 0.8, cy + dy * 0.8, 10)], "#A8B5C3", 0.35)
            s.line([(cx - 1.6, cy - 1.6, 5), (cx + 1.6, cy - 1.6, 5), (cx + 1.6, cy + 1.6, 5)], "#8997A7", 0.15)
        s.pipe([(cx, cy + 2, 0.8), (cx, cy, 0.8), (cx, cy, 10)], P_RAW, w=0.35)
        with s.g("structure", tip="Elevated service reservoir on columns" if n == 0 else None, key="reservoir-tank" if n == 0 else None):
            s.cyl(cx, cy, 10, 3.0, 3.0)
    s.label(28, 0, 13.6, "Elevated service reservoirs", color="#DDE4EB", size=1.4)
    # treatment unit and pumping station
    with s.g("structure", tip="Treatment unit", key="treatment"):
        s.tank(10, 13, 0, 8, 6, 2.6, t=0.4, water=0.5, cells=2)
        s.box(10, 19.5, 0, 4, 3, 2.6, t=BLD_T, l=BLD_L, r=BLD_R)
    s.label(12, 25, 0, "Treatment unit", color="#DDE4EB", size=1.4, anchor="end")
    s.pipe([(18, 16, 1.0), (22, 16, 1.0)], P_RAW, w=0.45)
    with s.g("structure", tip="Pumping station", key="pumpstation"):
        s.building(22, 13, 0, 6, 5, 3.4)
    s.label(21, 11, 4.4, "Pumping station", color="#DDE4EB", size=1.4)
    s.pipe([(28, 16, 1.0), (34, 16, 1.0), (34, 6, 0.8)], P_RAW, w=0.45, valves=[(31, 16, 1.0)], tip="Rising main to the reservoirs", key="rising-main")
    s.pipe([(34, 16, 1.0), (46, 16, 1.0), (46, 6, 0.8)], P_RAW, w=0.45)
    # underground distribution mains
    s.pipe([(34, 6, 0.3), (34, 8, 0.3), (52, 8, 0.3)], "#34C17F", w=0.35)
    s.pipe([(46, 6, 0.3), (46, 8, 0.3)], "#34C17F", w=0.35)
    s.pipe([(52, 8, 0.3), (52, 37, 0.3)], "#34C17F", w=0.4, tip="Underground distribution main", key="dist-main")
    s.pipe([(22, 24, 0.3), (52, 24, 0.3)], "#34C17F", w=0.35)
    s.pipe([(22, 32, 0.3), (52, 32, 0.3)], "#34C17F", w=0.35)
    # households along the mains, drawn back to front
    first = True
    for hy, my in ((21, 24), (26, 24), (34, 32)):
        for hx in (24, 29, 34, 39, 44):
            with s.g("structure", tip="Household" if first else None, key="household" if first else None):
                house(s, hx, hy)
            with s.g("pipework"):
                if hy < my:
                    s.line([(hx + 1.2, my, 0.3), (hx + 1.2, hy + 2.0, 0.3)], "#34C17F", 0.15)
                else:
                    s.line([(hx + 1.2, my, 0.3), (hx + 1.2, hy, 0.3)], "#34C17F", 0.15)
            with s.g("equipment", tip="Household tap connection" if first else None, key="tap" if first else None):
                (px, py) = P(hx + 1.2, hy if hy > my else hy + 2.0, 0.5)
                s.el.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="0.45" fill="#8FD0F2" stroke="#0D1319" stroke-width="0.08"></circle>')
            first = False
    s.label(21, 39, 0.3, "Household tap connections", color="#DDE4EB", size=1.4, anchor="end")
    s.label(54, 26, 0.3, "Underground mains", color="#DDE4EB", size=1.4)
    return s


def wtp_100mld():
    """100 MLD works as described on the project page: raw water source, cascade aerator, three circular
    settling tanks, 24 filter beds, disinfection, pumping to the city through a trunk main."""
    s = S()
    with s.g("structure"):
        s.ground(-4, -4, 100, 60, step=6)
        # internal road
        s.poly([(-4, 26, 0.01), (100, 26, 0.01), (100, 30, 0.01), (-4, 30, 0.01)], "#2A3746", stroke="none")
        s.line([(-4, 28, 0.02), (100, 28, 0.02)], "#8997A7", 0.12, dash="1.4 1.2", cap="butt")
    with s.g("structure", tip="Raw water source", key="source"):
        s.poly([(-4, 4, 0.02), (-1, 4, 0.02), (-1, 20, 0.02), (-4, 20, 0.02)], WAT, stroke="none", op=0.85)
    # inlet + cascade aerator
    with s.g("structure", tip="Inlet and cascade aerator", key="inlet"):
        s.box(0, 8, 0, 6, 6, 3.2)
        for k in range(4):
            s.box(0.5 + k * 1.2, 8.5 + k * 1.2, 3.2, 5 - k * 1.2, 5 - k * 1.2, 0.6, sw=0.05)
    s.pipe([(6, 11, 2.0), (9, 11, 2.0), (9, 4, 2.0)], P_RAW, w=0.7, tip="Raw water main", key="raw-main")
    # three circular settling tanks
    for i, cxy in enumerate(((16, 4), (16, 17), (30, 10))):
        s.clarifier(cxy[0], cxy[1], 6.5, 4.0, rails=False, tip="Circular settling tank" if i == 0 else None, key="clarifier" if i == 0 else None)
    s.pipe([(9, 4, 2.0), (9.5, 4, 2.0)], P_RAW, w=0.7)
    # filter house: 24 filter beds = 2 rows x 12
    with s.g("structure", tip="Filter house (24 filter beds)", key="filters"):
        s.tank(42, 0, 0, 30, 9, 5.5, t=0.45, water=1.0, cells=12)
        s.tank(42, 13, 0, 30, 9, 5.5, t=0.45, water=1.0, cells=12)
        s.poly([(42, 9, 0), (72, 9, 0), (72, 13, 0), (42, 13, 0)], "#2A3848", sw=0.05)
    s.pipe([(42, 11, 2.2), (72, 11, 2.2)], P_RAW, w=0.8, tip="Filtered water channel", key="filtered")
    s.pipe([(42, 12, 3.2), (72, 12, 3.2)], P_AIR, w=0.5, tip="Air scour pipe", key="air")
    s.pipe([(36.5, 10, 3.0), (42, 11, 2.2)], P_RAW, w=0.8)
    # clear water reservoir (covered) + pump house
    with s.g("structure", tip="Clear water reservoir", key="cwr"):
        s.box(76, 0, 0, 14, 22, 3.2, t="#B3BFCC", l="#7F8EA0", r="#98A6B5")
        for k in range(3):
            s.box(78 + k * 4, 3, 3.2, 1.2, 1.2, 0.8, sw=0.04)
    s.pipe([(72, 11, 2.2), (76, 11, 2.2)], P_RAW, w=0.8)
    with s.g("structure", tip="Pump house", key="pumphouse"):
        s.building(78, 34, 0, 12, 8, 6)
    s.pipe([(84, 22, 1.5), (84, 34, 1.5)], P_RAW, w=0.8, valves=[(84, 30, 1.5)], tip="Outlet to the pump house", key="outlet")
    # pump sets and the new trunk main to the city
    for k, px in enumerate((80, 85, 90)):
        with s.g("equipment", tip="Pump set" if k == 0 else None, key="pumps" if k == 0 else None):
            s.cyl(px, 45, 0, 1.0, 1.8, side="#B8C4D0", side2="#7D8B9B", top="#D8E0E8", sw=0.06)
        s.pipe([(px, 46.2, 0.8), (px, 49, 0.8)], P_RAW, w=0.4)
    s.pipe([(80, 49, 0.8), (98, 49, 0.8), (98, 59, 0.8)], P_RAW, w=0.8, tip="Trunk main to the city", key="trunk")
    # chemical house (disinfection), admin
    with s.g("structure", tip="Chemical house (disinfection)", key="chem"):
        s.building(40, 36, 0, 14, 9, 5)
    with s.g("structure"):
        s.building(4, 36, 0, 12, 8, 7)
    s.pipe([(47, 36, 1.0), (47, 22, 1.0)], P_DOSE, w=0.3, tip="Disinfectant dosing line", key="dosing")
    for lbl, x, y, z, anc in (("Source", -4, 22, 0.4, "end"), ("Cascade aerator", -1, 15, 4, "end"), ("Settling tanks x3", 14, -3, 5, "start"), ("Filter house, 24 beds", 50, -2, 6, "start"), ("Clear water reservoir", 78, -2, 3.4, "start"), ("Pump house", 77, 44, 1, "end"), ("Trunk main to city", 102, 52, 0, "start"), ("Chemical house", 40, 50, 0, "end"), ("Admin", 5, 47, 7.2, "start")):
        s.label(x, y, z, lbl, color="#DDE4EB", size=2.6, anchor=anc)
    return s


if __name__ == "__main__":
    # Regenerates the static project models used on the home-page cards.
    import os
    out = os.path.join(os.path.dirname(__file__), "..", "assets", "illustrations", "projects")
    for name, fn in (("chamravattom-bridge", regulator_bridge), ("kollam-rural-water-supply", rural_water_supply), ("kollam-100mld-wtp", wtp_100mld)):
        open(os.path.join(out, name + ".svg"), "w").write(fn().svg('xmlns="http://www.w3.org/2000/svg" width="1000" height="620"'))
        print("wrote", name)
