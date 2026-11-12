"""Squalo 3D in ASCII che ruota: nuvola di punti + z-buffer (stile donut.c).
Solo libreria standard. frames(n) -> lista di n frame, ognuno e' una lista di righe."""
import math

COLS, ROWS = 54, 15
SX, SY = 14.0, 6.4          # colonne e righe per unita' (celle ~2.2x piu' alte che larghe)
CX, CY = 27.5, 7.6
CHARS = " .:-=+*#%@"
LIGHT = (0.35, 0.65, 0.68)

def _norm(v):
    l = math.sqrt(sum(c * c for c in v)) or 1.0
    return tuple(c / l for c in v)

def _r(x):
    u = min(max((x + 1.5) / 3.0, 0.0), 1.0)
    return 0.40 * math.sin(math.pi * u ** 1.6) ** 0.8 + 0.045 * (1 - u) ** 2

def _tri(a, b, c, n):
    """punti su un triangolo + normale (a due facce)"""
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
            pts.append((p, nrm, 'plate'))
    return pts

def model():
    P = []
    # corpo
    nx, na = 170, 56
    for i in range(nx + 1):
        x = -1.5 + 3.0 * i / nx
        r = _r(x)
        dr = (_r(x + 0.01) - _r(x - 0.01)) / 0.02
        for j in range(na):
            ph = 2 * math.pi * j / na
            y, z = 0.86 * r * math.cos(ph), r * math.sin(ph)
            P.append(((x, y, z), _norm((-dr, math.cos(ph), math.sin(ph))), None))
    top = lambda x: 0.86 * _r(x)
    # pinna dorsale
    P += _tri((0.62, top(0.62) - 0.04, 0), (0.0, top(0.0) - 0.04, 0), (0.12, top(0.12) + 0.62, 0), 34)
    # pinna dorsale piccola
    P += _tri((-0.85, top(-0.85) - 0.02, 0), (-1.1, top(-1.1) - 0.02, 0), (-1.08, top(-1.08) + 0.2, 0), 10)
    # coda: lobo superiore e inferiore
    P += _tri((-1.40, 0.03, 0), (-1.72, 0.0, 0), (-2.00, 0.78, 0), 28)
    P += _tri((-1.40, -0.03, 0), (-1.65, 0.0, 0), (-1.85, -0.5, 0), 20)
    # pettorali
    for s in (1, -1):
        P += _tri((0.68, -0.22, 0.30 * s), (0.22, -0.26, 0.34 * s), (0.02, -0.58, 0.95 * s), 26)
    # occhi
    for s in (1, -1):
        x = 1.12
        r = _r(x)
        P.append(((x, 0.86 * r * 0.55, r * 0.83 * s), _norm((0, 0.3, s)), "o"))
    return P

MODEL = model()

def render(theta, pitch=0.28):
    ct, st, cp, sp = math.cos(theta), math.sin(theta), math.cos(pitch), math.sin(pitch)
    zb = [[-9e9] * COLS for _ in range(ROWS)]
    out = [[" "] * COLS for _ in range(ROWS)]
    def rot(v):
        x, y, z = v
        x, z = x * ct + z * st, -x * st + z * ct
        y, z = y * cp - z * sp, y * sp + z * cp
        return x, y, z
    for p, n, ch in MODEL:
        x, y, z = rot(p)
        c, r = int(round(CX + x * SX)), int(round(CY - y * SY))
        if 0 <= c < COLS and 0 <= r < ROWS and z > zb[r][c]:
            zb[r][c] = z
            if ch == "o":
                out[r][c] = "o" if z > 0 else out[r][c]
                continue
            nx, ny, nz = rot(n)
            L = nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]
            if ch == 'plate':
                L = 0.45 + 0.55 * abs(L)
            idx = int(max(0.0, min(0.999, 0.12 + 0.88 * max(L, 0.0))) * len(CHARS))
            out[r][c] = CHARS[max(idx, 1)]
    return ["".join(row).rstrip() for row in out]

def frames(n=20, start=math.pi):
    return [render(start + 2 * math.pi * i / n) for i in range(n)]

if __name__ == "__main__":
    for f in frames(8):
        print("\n".join(f)); print("=" * COLS)
