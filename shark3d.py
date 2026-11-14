"""Squalo 3D in ASCII che ruota (nuvola di punti + z-buffer, stile donut.c).
render() -> 3 livelli di righe: [corpo, rosso, bianco] (rosso/bianco = cappello natalizio)."""
import math

COLS, ROWS = 54, 15
SX, SY = 14.0, 6.4
CX, CY = 27.5, 8.2
CHARS = " .:-=+*#%@"
LIGHT = (0.35, 0.65, 0.68)
FLAT = 0.82          # schiacciamento verticale del corpo

def _norm(v):
    l = math.sqrt(sum(c * c for c in v)) or 1.0
    return tuple(c / l for c in v)

def _r(x):
    u = min(max((x + 1.5) / 3.0, 0.0), 1.0)
    return 0.36 * math.sin(math.pi * u ** 1.5) ** 0.75 + 0.04 * (1 - u) ** 2

def _tri(a, b, c, n):
    nrm = _norm((
        (b[1]-a[1])*(c[2]-a[2]) - (b[2]-a[2])*(c[1]-a[1]),
        (b[2]-a[2])*(c[0]-a[0]) - (b[0]-a[0])*(c[2]-a[2]),
        (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0]),
    ))
    pts = []
    for i in range(n + 1):
        for j in range(n + 1 - i):
            s, t = i / n, j / n
            p = tuple(a[k] + s * (b[k] - a[k]) + t * (c[k] - a[k]) for k in range(3))
            pts.append((p, nrm, "plate", 0, None))
    return pts

def _surf(x, phi):
    r = _r(x)
    return (x, FLAT * r * math.cos(phi), r * math.sin(phi))

def base_model():
    P = []
    nx, na = 190, 60
    for i in range(nx + 1):
        x = -1.5 + 3.0 * i / nx
        dr = (_r(x + 0.01) - _r(x - 0.01)) / 0.02
        for j in range(na):
            ph = 2 * math.pi * j / na
            P.append((_surf(x, ph), _norm((-dr, math.cos(ph), math.sin(ph))), "solid", 0, None))
    top = lambda x: FLAT * _r(x)
    # pinna dorsale, seconda dorsale, coda, pettorali
    P += _tri((0.55, top(0.55) - 0.04, 0), (-0.02, top(-0.02) - 0.04, 0), (0.08, top(0.08) + 0.60, 0), 36)
    P += _tri((-0.85, top(-0.85) - 0.02, 0), (-1.1, top(-1.1) - 0.02, 0), (-1.08, top(-1.08) + 0.2, 0), 10)
    P += _tri((-1.40, 0.03, 0), (-1.72, 0.0, 0), (-2.00, 0.78, 0), 30)
    P += _tri((-1.40, -0.03, 0), (-1.65, 0.0, 0), (-1.85, -0.5, 0), 22)
    for s in (1, -1):
        P += _tri((0.62, -0.20, 0.27 * s), (0.18, -0.24, 0.31 * s), (0.0, -0.56, 0.95 * s), 28)
    for s in (1, -1):
        n = (0, 0, s)
        P.append((_surf(1.14, math.radians(70 if s > 0 else 290)), n, "mark", 0, "o"))   # occhio
        for x in (0.86, 0.78, 0.70):                                                         # branchie
            P.append((_surf(x, math.radians(90 if s > 0 else 270)), n, "mark", 0, "|"))
        for x in (1.20, 1.28, 1.36, 1.44):                                                   # bocca
            P.append((_surf(x, math.radians(112 if s > 0 else 248)), n, "mark", 0, "-"))
    return P

def hat_model():
    P = []
    C0, T = (0.98, 0.15, 0.0), (0.46, 0.80, 0.0)
    d = _norm(tuple(T[k] - C0[k] for k in range(3)))
    u, v = (-d[1], d[0], 0.0), (0.0, 0.0, 1.0)
    L = math.dist(C0, T)
    def ring(t, rad, layer, n=40, off=0.0):
        for j in range(n):
            ph = 2 * math.pi * j / n
            nn = tuple(math.cos(ph) * u[k] + math.sin(ph) * v[k] for k in range(3))
            A = tuple(C0[k] + (t * L + off) * d[k] for k in range(3))
            P.append((tuple(A[k] + rad * nn[k] for k in range(3)), nn, "solid", layer, None))
    for i in range(50):
        t = i / 49
        ring(t, 0.32 * (1 - t) ** 0.85 + 0.01, 1, n=max(8, int(42 * (1 - t)) + 8))
    for off in (-0.04, -0.02, 0.0, 0.02, 0.04):
        ring(0.0, 0.34, 2, n=48, off=off)
    for a in range(10):
        for b in range(14):
            th, ph = math.pi * a / 9, 2 * math.pi * b / 14
            nn = (math.sin(th) * math.cos(ph), math.cos(th), math.sin(th) * math.sin(ph))
            P.append((tuple(T[k] + 0.11 * nn[k] for k in range(3)), nn, "solid", 2, None))
    return P

BASE, HAT = base_model(), hat_model()

def render(theta, hat=True, pitch=0.28):
    ct, st, cp, sp = math.cos(theta), math.sin(theta), math.cos(pitch), math.sin(pitch)
    zb = [[-9e9] * COLS for _ in range(ROWS)]
    ch = [[" "] * COLS for _ in range(ROWS)]
    tag = [[0] * COLS for _ in range(ROWS)]
    def rot(v):
        x, y, z = v
        x, z = x * ct + z * st, -x * st + z * ct
        y, z = y * cp - z * sp, y * sp + z * cp
        return x, y, z
    for p, n, kind, layer, mark in (BASE + HAT if hat else BASE):
        x, y, z = rot(p)
        c, r = int(round(CX + x * SX)), int(round(CY - y * SY))
        if not (0 <= c < COLS and 0 <= r < ROWS):
            continue
        nx, ny, nz = rot(n)
        if kind == "mark":
            if nz > 0.35 and z + 0.02 > zb[r][c]:
                zb[r][c], ch[r][c], tag[r][c] = z + 0.02, mark, 0
            continue
        if z > zb[r][c]:
            zb[r][c] = z
            L = nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]
            if kind == "plate":
                L = 0.45 + 0.55 * abs(L)
            idx = int(max(0.0, min(0.999, 0.12 + 0.88 * max(L, 0.0))) * len(CHARS))
            ch[r][c], tag[r][c] = CHARS[max(idx, 2 if layer else 1)], layer
    return [["".join(ch[r][c] if tag[r][c] == L else " " for c in range(COLS)).rstrip() for r in range(ROWS)]
            for L in range(3)]

def frames(n=24, hat=True, start=math.pi):
    return [render(start + 2 * math.pi * i / n, hat) for i in range(n)]
