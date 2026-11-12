#!/usr/bin/env python3
"""Genera dark_mode.svg e light_mode.svg con le stats reali di GitHub.
Solo libreria standard. Uso: GH_TOKEN=... GH_USER=WillyTv9 python3 generate.py
Test offline: python3 generate.py --demo
"""
import html, json, os, sys, urllib.request
from datetime import datetime, timezone

USER = os.environ.get("GH_USER", "WillyTv9")
NAME = "AndrewTheShark"
STACK = [
    "java  python  c++  javascript  php  dart",
    "html  css  xml  json  yaml  flutter",
]
MOTTO = ["building things. breaking things. fixing things.", "still learning. always curious."]

from shark3d import frames
FRAMES = frames(20)
ROWS = len(FRAMES[0])
PERIOD = 2.4

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

# ---- rendering -----------------------------------------------------------
CW, LH, PAD, RX, W = 7.2, 18, 24, 430, 860
def P(cmd): return [("a", "willy@shark"), ("f", ":~$ "), ("c", cmd)]
def O(t, c="v"): return [(c, t)]
e = lambda s: html.escape(s, quote=False)

T = {
 "dark": dict(bg="#050805", bar="#0b120b", bd="#1c3a1c", f="#6fbf73", a="#39ff88", c="#d7ffe0", v="#9be7ff", k="#ffb86b", m="#4f7a56", d="#2f5a37", w="#ffd166", s="#39ff88", sl=".22"),
 "light": dict(bg="#f4f7f1", bar="#e4ebe0", bd="#b9c9b5", f="#3b6b42", a="#0a7a3a", c="#0b2410", v="#0a4a7a", k="#9a4b00", m="#6f8a73", d="#a8bba9", w="#9a6a00", s="#0a7a3a", sl=".05"),
}

def line(x, y, segs):
    if not segs: return ""
    t = "".join(f'<tspan class="{c}">{e(s)}</tspan>' for c, s in segs)
    return f'<text xml:space="preserve" x="{x}" y="{y}">{t}</text>'

def content(d, now):
    delta = (now - d["created"]).days
    boot = [
      [("f","["),("a"," OK "),("f","] "),("m","Booting "),("v",NAME),("m",f" v{now:%Y.%m} ... kernel curious-1.0")],
      [("f","["),("a"," OK "),("f","] "),("m","Mounted "),("v",f"/home/{USER}"),("m"," (Italy)")],
      [("f","["),("a"," OK "),("f","] "),("m","Synced with "),("v","github.com"),("m",f" @ {now:%Y-%m-%d %H:%M} UTC")],
      [("f","["),("a"," OK "),("f","] "),("m","Started "),("v","curiosity.service")],
      [("f","["),("w","WARN"),("f","] "),("m","sleep.service: "),("w","not found")],
    ]
    right = [P("whoami"), O(f"{NAME} ({USER})"), [], P("ls ~/stack")]
    right += [O(s) for s in STACK] + [[], P("cat motto.txt")] + [O(s) for s in MOTTO] + [[]]
    right += [P("uptime"), [("v", f"up {delta // 365}y {delta % 365}d, load: "), ("w", "coffee coffee coffee")], []]
    right += [P("git log -1"), [("v", d["last_repo"]), ("d", " :: "), ("w", ago(d["last_push"], now))], []]
    sep = ("d", " | ")
    right += [P("git stats"), [("k","repos "),("v",str(d["repos"])), sep, ("k","starred "),("v",str(d["starred"])), sep,
              ("k","followers "),("v",str(d["followers"])), sep, ("k","following "),("v",str(d["following"]))]]
    return boot, right

def build(name, t, d, now):
    BOOT, RIGHT = content(d, now)
    top = 56
    cols_y = top + len(BOOT) * LH + 34
    body_h = max(len(RIGHT) * LH, (ROWS + 4) * 16)
    H = cols_y + body_h + 54
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="ui-monospace,SFMono-Regular,Consolas,\'DejaVu Sans Mono\',Menlo,monospace" font-size="12">']
    css = "".join(f".{k}{{fill:{v}}}" for k, v in t.items() if k not in ("bg","bar","bd","sl"))
    o.append(f'<style>text{{white-space:pre}}{css}.a,.k,.s{{font-weight:bold}}.cur{{animation:b 1s steps(1) infinite}}@keyframes b{{50%{{opacity:0}}}}.fr{{visibility:hidden;animation:sp {PERIOD}s steps(1) infinite}}.f0{{visibility:visible}}@keyframes sp{{0%{{visibility:visible}}{100/len(FRAMES):.2f}%{{visibility:hidden}}}}@media(prefers-reduced-motion:reduce){{.fr{{animation:none}}}}</style>')
    o.append(f'<defs><pattern id="sl" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity="{t["sl"]}"/></pattern></defs>')
    o.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="6" fill="{t["bg"]}" stroke="{t["bd"]}"/>')
    o.append(f'<path d="M.5 6.5a6 6 0 0 1 6-6H{W-6.5}a6 6 0 0 1 6 6V30H.5z" fill="{t["bar"]}"/><line x1="0" y1="30" x2="{W}" y2="30" stroke="{t["bd"]}"/>')
    o.append(f'<text x="{PAD}" y="19" class="m" xml:space="preserve">[tty1]  operator@{NAME}</text>')
    o.append(f'<text x="{W-PAD}" y="19" text-anchor="end" class="a" xml:space="preserve">&#9679; ACCESS GRANTED</text>')
    for i, b in enumerate(BOOT): o.append(line(PAD, top + i * LH, b))
    sy = top + len(BOOT) * LH + 10
    o.append(f'<line x1="{PAD}" y1="{sy}" x2="{W-PAD}" y2="{sy}" stroke="{t["d"]}" stroke-dasharray="2 4"/>')
    n = len(FRAMES)
    for k, fr in enumerate(FRAMES):
        cls = "fr f0" if k == 0 else "fr"
        rows = "".join(f'<tspan x="12" y="{cols_y+i*16}">{e(l)}</tspan>' for i, l in enumerate(fr) if l.strip())
        o.append(f'<text xml:space="preserve" class="s {cls}" style="animation-delay:{k*PERIOD/n:.3f}s">{rows}</text>')
    cap_y = cols_y + ROWS * 16 + 14
    o.append(f'<text xml:space="preserve" x="{PAD}" y="{cap_y}"><tspan class="m">[ </tspan><tspan class="w">APEX PREDATOR</tspan><tspan class="m"> :: </tspan><tspan class="a">ONLINE</tspan><tspan class="m"> ]</tspan></text>')
    for i, r in enumerate(RIGHT): o.append(line(RX, cols_y + i * LH, r))
    py = cols_y + len(RIGHT) * LH
    o.append(line(RX, py, P("")))
    o.append(f'<rect class="cur" x="{RX+CW*len("willy@shark:~$ ")}" y="{py-11}" width="7" height="14" fill="{t["a"]}"/>')
    o.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="6" fill="url(#sl)" pointer-events="none"/>')
    o.append('</svg>')
    out = os.environ.get("OUT_DIR", ".")
    with open(os.path.join(out, f"{name}_mode.svg"), "w") as f: f.write("\n".join(o))

if __name__ == "__main__":
    now = datetime.now(timezone.utc)
    data = demo() if "--demo" in sys.argv else fetch()
    for n, t in T.items(): build(n, t, data, now)
    print("ok:", {k: v for k, v in data.items() if k not in ("created", "last_push")})
