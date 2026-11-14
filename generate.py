#!/usr/bin/env python3
"""Genera dark_mode.svg e light_mode.svg con le stats reali di GitHub.
Solo libreria standard. Uso: GH_TOKEN=... GH_USER=WillyTv9 python3 generate.py
Test offline: python3 generate.py --demo
"""
import html, json, os, random, sys, urllib.request
from datetime import date, datetime, timezone

USER = os.environ.get("GH_USER", "WillyTv9")
NAME = "AndrewTheShark"
STACK = [
    "java  python  c++  javascript  php  dart",
    "html  css  xml  json  yaml  flutter",
]
MOTTO = ["building things. breaking things. fixing things.", "still learning. always curious."]


QUERY = """
query($login:String!){ user(login:$login){
  createdAt
  followers{totalCount} following{totalCount}
  repositories(ownerAffiliations:OWNER, privacy:PUBLIC){totalCount}
  starredRepositories{totalCount}
  pushed: repositories(first:5, ownerAffiliations:OWNER, privacy:PUBLIC, isFork:false,
                       orderBy:{field:PUSHED_AT, direction:DESC}){nodes{name pushedAt}}
}}"""

def parse_date(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": "bearer " + os.environ["GH_TOKEN"], "User-Agent": "profile-readme"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        u = json.load(r)["data"]["user"]
    # salta il repo del profilo stesso, che riceve commit ogni giorno
    last = next((n for n in u["pushed"]["nodes"] if n["name"].lower() != USER.lower()), None)
    return dict(
        created=parse_date(u["createdAt"]),
        followers=u["followers"]["totalCount"], following=u["following"]["totalCount"],
        repos=u["repositories"]["totalCount"], starred=u["starredRepositories"]["totalCount"],
        last_repo=last["name"] if last else "-", last_push=parse_date(last["pushedAt"]) if last else None,
    )

def demo():
    n = datetime.now(timezone.utc)
    return dict(created=n.replace(year=n.year - 2), followers=9, following=17, repos=7, starred=13,
                last_repo="dlt-chat-plugin", last_push=n.replace(microsecond=0))

def ago(dt, now):
    if not dt: return "n/a"
    s = int((now - dt).total_seconds())
    if s < 3600: return f"{max(s // 60, 1)}m ago"
    if s < 86400: return f"{s // 3600}h ago"
    return f"{s // 86400}d ago"

# ---- tema natalizio -------------------------------------------------------
XMAS_START = (11, 1)    # dal 1 novembre ... (metti (12, 1) per partire dal 1 dicembre)
XMAS_END = (1, 1)       # ... fino al 1 gennaio incluso; dal 2 gennaio torna normale

WISHLIST = ["zero merge conflicts", "builds that stay green", "infinite coffee"]

def pick_theme(now):
    forced = os.environ.get("FORCE_THEME", "auto").strip().lower()
    if forced in ("xmas", "normal"):
        return forced
    md = (now.month, now.day)
    return "xmas" if md >= XMAS_START or md <= XMAS_END else "normal"

def countdown(now):
    """(testo, classe colore, barra di progresso o None)"""
    today = now.date()
    if today.month == 1:
        return f"Happy New Year {today.year}!", "a", None
    xmas = date(today.year, 12, 25)
    if today < xmas:
        n = (xmas - today).days
        start = date(today.year, XMAS_START[0], XMAS_START[1])
        pct = min(max((today - start).days / max((xmas - start).days, 1), 0), 1)
        bar = "[" + "#" * round(pct * 20) + "." * (20 - round(pct * 20)) + f"] {round(pct * 100)}%"
        return f"{n} day{'s' if n != 1 else ''} until Christmas", "w", bar
    if today == xmas:
        return "Merry Christmas!", "a", None
    n = (date(today.year + 1, 1, 1) - today).days
    return f"{n} day{'s' if n != 1 else ''} until {today.year + 1}", "w", None

# ---- rendering ------------------------------------------------------------
from shark3d import frames
CW, LH, PAD, RX, W = 7.2, 18, 24, 430, 860
PERIOD, NFRAMES = 3.0, 24
def P(cmd): return [("a", "willy@shark"), ("f", ":~$ "), ("c", cmd)]
def O(t, c="v"): return [(c, t)]
e = lambda s: html.escape(s, quote=False)

TREE = [
    "       *",
    "      /o\\",
    "     /_o_\\",
    "    /o___o\\          _+_",
    "   /__o_o__\\        |_+_|",
    "  /o_______o\\       |_+_|",
    "      |||",
]

BASE = dict(r="#ff4d4d", wh="#ffffff", sn="#ffffff")
T = {
 "normal": {
  "dark": dict(bg="#050805", bar="#0b120b", bd="#1c3a1c", f="#6fbf73", a="#39ff88", c="#d7ffe0", v="#9be7ff", k="#ffb86b", m="#4f7a56", d="#2f5a37", w="#ffd166", s="#39ff88", sl=".22", **BASE),
  "light": dict(bg="#f4f7f1", bar="#e4ebe0", bd="#b9c9b5", f="#3b6b42", a="#0a7a3a", c="#0b2410", v="#0a4a7a", k="#9a4b00", m="#6f8a73", d="#a8bba9", w="#9a6a00", s="#0a7a3a", sl=".05", r="#d62828", wh="#9fb3c8", sn="#9fc3e6"),
 },
 "xmas": {
  "dark": dict(bg="#050a07", bar="#0d1a10", bd="#2a4a2c", f="#7ccf8a", a="#5dff9a", c="#f1fff4", v="#e8f4ff", k="#ff6b6b", m="#5e8a66", d="#35603c", w="#ffd166", s="#5dff9a", sl=".22", **BASE),
  "light": dict(bg="#f7fbf6", bar="#e6efe4", bd="#bcd0b8", f="#3b6b42", a="#0a7a3a", c="#0b2410", v="#1b3a57", k="#c0262d", m="#6f8a73", d="#a8bba9", w="#9a6a00", s="#0a7a3a", sl=".05", r="#d62828", wh="#9fb3c8", sn="#9fc3e6"),
 },
}
# colori delle luci lampeggianti (rosso, oro, azzurro, verde)
BULBS = {"dark": ("#ff4d4d", "#ffd166", "#6ec6ff", "#5dff9a"), "light": ("#d62828", "#c98a00", "#1e78c8", "#0a7a3a")}

def line(x, y, segs):
    if not segs: return ""
    t = "".join(f'<tspan class="{c}">{e(s)}</tspan>' for c, s in segs)
    return f'<text xml:space="preserve" x="{x}" y="{y}">{t}</text>'

def content(d, now, xmas):
    delta = (now - d["created"]).days
    ok = lambda *m: [("f","["),("a"," OK "),("f","] ")] + list(m)
    boot = [
      ok(("m","Booting "),("v",NAME),("m",f" v{now:%Y.%m} ... kernel curious-1.0")),
      ok(("m","Mounted "),("v",f"/home/{USER}"),("m"," (Italy)")),
      ok(("m","Synced with "),("v","github.com"),("m",f" @ {now:%Y-%m-%d %H:%M} UTC")),
      ok(("m","Started "),("v","christmas.service" if xmas else "curiosity.service")),
      [("f","["),("w","WARN"),("f","] ")] + ([("m","santa.service: "),("w","you better watch out")] if xmas else [("m","sleep.service: "),("w","not found")]),
    ]
    right = [P("whoami"), O(f"{NAME} ({USER})"), [], P("ls ~/stack")]
    right += [O(s) for s in STACK] + [[], P("cat motto.txt")] + [O(s) for s in MOTTO] + [[]]
    if xmas:
        txt, c, bar = countdown(now)
        right += [P("./countdown.sh"), [(c, txt)]]
        if bar: right.append([("a", bar)])
        right += [[], P("cat wishlist.txt")] + [[("d", "- "), ("v", w)] for w in WISHLIST] + [[]]
    right += [P("uptime"), [("v", f"up {delta // 365}y {delta % 365}d, load: "), ("w", "coffee coffee coffee")], []]
    right += [P("git log -1"), [("v", d["last_repo"]), ("d", " :: "), ("w", ago(d["last_push"], now))], []]
    sep = ("d", " | ")
    right += [P("git stats"), [("k","repos "),("v",str(d["repos"])), sep, ("k","starred "),("v",str(d["starred"])), sep,
              ("k","followers "),("v",str(d["followers"])), sep, ("k","following "),("v",str(d["following"]))]]
    return boot, right

def tree_svg(x, y0):
    """albero + regalo: le palline 'o' lampeggiano (classi b1..b4)"""
    out, cyc = [], 0
    for i, row in enumerate(TREE):
        segs = []
        for ch in row:
            if ch == " ": cls = None
            elif ch == "*": cls = "b2"
            elif ch == "o": cls = ("b1", "b3", "b4")[cyc % 3]; cyc += 1
            elif ch == "|": cls = "k" if i == len(TREE) - 1 else "w"
            elif ch == "+": cls = "r"
            else: cls = "a"
            segs.append((cls, ch))
        # unisci i caratteri consecutivi con la stessa classe
        merged = []
        for cls, ch in segs:
            if merged and merged[-1][0] == cls: merged[-1][1] += ch
            else: merged.append([cls, ch])
        tsp = "".join(f'<tspan class="{c}">{e(t)}</tspan>' if c else e(t) for c, t in merged)
        out.append(f'<text xml:space="preserve" x="{x}" y="{y0 + i * 16}">{tsp}</text>')
    return "".join(out)

def garland():
    wire = "M0 30 " + "".join(f"Q{x+20} 41 {x+40} 30 " for x in range(0, W, 40))
    bulbs = "".join(f'<circle class="b{(i % 4) + 1}" cx="{x+20}" cy="35.5" r="3.2"/>' for i, x in enumerate(range(0, W, 40)))
    return f'<path d="{wire}" fill="none" stroke-width="1" class="gw"/>{bulbs}'

def snow(H, t_now=None):
    rnd = random.Random(2026)
    out = []
    for _ in range(40):
        x = rnd.randint(14, W - 14)
        ch = rnd.choice("**.+")
        size = rnd.choice((9, 11, 13))
        dur = rnd.uniform(8, 15)
        delay = rnd.uniform(0, dur)
        if t_now is None:
            out.append(f'<text class="sn" x="{x}" y="38" font-size="{size}" style="animation-duration:{dur:.1f}s;animation-delay:-{delay:.1f}s">{ch}</text>')
        else:
            prog = ((t_now + delay) / dur) % 1
            out.append(f'<text class="sn" x="{x}" y="{38 + prog * (H - 70):.0f}" font-size="{size}">{ch}</text>')
    drift = f"M0 {H} L0 {H-9} " + "".join(f"Q{x+20} {H-17} {x+40} {H-9} " for x in range(0, W, 40)) + f"L{W} {H} Z"
    return "".join(out) + f'<path d="{drift}" class="dr"/>'

def build(name, t, d, now, xmas, FR, t_now=None):
    BOOT, RIGHT = content(d, now, xmas)
    top = 56
    rows = len(FR[0][0])
    cols_y = top + len(BOOT) * LH + 34
    left_h = (rows + 4) * 16 + (len(TREE) * 16 + 30 if xmas else 0)
    body_h = max(len(RIGHT) * LH, left_h)
    H = cols_y + body_h + 54
    n = len(FR)
    mode = name  # dark | light
    bl = BULBS[mode]
    q = (H - 70) / 4
    css = "".join(f".{k}{{fill:{v}}}" for k, v in t.items() if k not in ("bg","bar","bd","sl"))
    blink = "".join(f".b{i+1}{{fill:{c};animation:tw 1.6s steps(1) {i*0.4:.1f}s infinite}}" for i, c in enumerate(bl))
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="ui-monospace,SFMono-Regular,Consolas,\'DejaVu Sans Mono\',Menlo,monospace" font-size="12">']
    o.append(f'<style>text{{white-space:pre}}{css}.a,.k,.s,.r,.wh{{font-weight:bold}}'
             f'.cur{{animation:b 1s steps(1) infinite}}@keyframes b{{50%{{opacity:0}}}}'
             f'.fr{{visibility:hidden;animation:sp {PERIOD}s steps(1) infinite}}.f0{{visibility:visible}}@keyframes sp{{0%{{visibility:visible}}{100/n:.3f}%{{visibility:hidden}}}}'
             f'{blink}@keyframes tw{{50%{{fill:{t["d"]}}}}}.gw{{stroke:{t["d"]}}}'
             f'.sn{{opacity:.65;animation:fall 12s linear infinite}}@keyframes fall{{0%{{transform:translate(0,0)}}25%{{transform:translate(8px,{q:.0f}px)}}50%{{transform:translate(0,{2*q:.0f}px)}}75%{{transform:translate(-8px,{3*q:.0f}px)}}100%{{transform:translate(0,{H-70}px)}}}}'
             f'.dr{{fill:{t["sn"]};opacity:.85}}'
             f'@media(prefers-reduced-motion:reduce){{.fr,.sn,.b1,.b2,.b3,.b4{{animation:none}}.sn{{display:none}}}}</style>')
    o.append(f'<defs><pattern id="sl" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity="{t["sl"]}"/></pattern>'
             f'<clipPath id="cp"><rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="6"/></clipPath></defs>')
    o.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="6" fill="{t["bg"]}" stroke="{t["bd"]}"/>')
    o.append(f'<path d="M.5 6.5a6 6 0 0 1 6-6H{W-6.5}a6 6 0 0 1 6 6V30H.5z" fill="{t["bar"]}"/><line x1="0" y1="30" x2="{W}" y2="30" stroke="{t["bd"]}"/>')
    o.append(f'<text x="{PAD}" y="19" class="m" xml:space="preserve">[tty1]  operator@{NAME}</text>')
    badge = "MERRY CHRISTMAS" if xmas else "ACCESS GRANTED"
    o.append(f'<text x="{W-PAD}" y="19" text-anchor="end" class="{"r" if xmas else "a"}" xml:space="preserve">&#9679; {badge}</text>')
    if xmas: o.append(garland())
    for i, b in enumerate(BOOT): o.append(line(PAD, top + i * LH, b))
    sy = top + len(BOOT) * LH + 10
    o.append(f'<line x1="{PAD}" y1="{sy}" x2="{W-PAD}" y2="{sy}" stroke="{t["d"]}" stroke-dasharray="2 4"/>')
    for k, layers in enumerate(FR):
        cls = "fr f0" if k == 0 else "fr"
        g = [f'<g class="{cls}" style="animation-delay:{k*PERIOD/n:.3f}s">']
        for layer, c in zip(layers, ("s", "r", "wh")):
            tsp = "".join(f'<tspan x="12" y="{cols_y+i*16}">{e(l)}</tspan>' for i, l in enumerate(layer) if l.strip())
            if tsp: g.append(f'<text xml:space="preserve" class="{c}">{tsp}</text>')
        g.append('</g>')
        o.append("".join(g))
    cap_y = cols_y + rows * 16 + 14
    cap = "SANTA JAWS" if xmas else "APEX PREDATOR"
    o.append(f'<text xml:space="preserve" x="{PAD}" y="{cap_y}"><tspan class="m">[ </tspan><tspan class="w">{cap}</tspan><tspan class="m"> :: </tspan><tspan class="a">ONLINE</tspan><tspan class="m"> ]</tspan></text>')
    if xmas: o.append(tree_svg(80, cap_y + 34))
    for i, r in enumerate(RIGHT): o.append(line(RX, cols_y + i * LH, r))
    py = cols_y + len(RIGHT) * LH
    o.append(line(RX, py, P("")))
    o.append(f'<rect class="cur" x="{RX+CW*len("willy@shark:~$ ")}" y="{py-11}" width="7" height="14" fill="{t["a"]}"/>')
    if xmas: o.append(f'<g clip-path="url(#cp)">{snow(H, t_now)}</g>')
    o.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="6" fill="url(#sl)" pointer-events="none"/>')
    o.append('</svg>')
    out = os.environ.get("OUT_DIR", ".")
    with open(os.path.join(out, f"{name}_mode.svg"), "w") as f: f.write("\n".join(o))

if __name__ == "__main__":
    now = datetime.now(timezone.utc)
    data = demo() if "--demo" in sys.argv else fetch()
    theme = pick_theme(now)
    FR = frames(NFRAMES, hat=(theme == "xmas"))
    for n, t in T[theme].items(): build(n, t, data, now, theme == "xmas", FR)
    print("tema:", theme, "|", {k: v for k, v in data.items() if k not in ("created", "last_push")})
