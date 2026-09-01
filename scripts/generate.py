#!/usr/bin/env python3
"""Profile renderer — Grok-style dark theme, clarity first.

Renders every SVG in ./assets from live GitHub data (GraphQL) + scripts/config.json.
Pure stdlib. `--demo` uses synthetic data.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import random
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
CONFIG = json.loads((ROOT / "scripts" / "config.json").read_text())

# ── tokens ───────────────────────────────────────────────────────────────────
BG = "#000000"
BORDER = "#2a2a2a"
FILL = "#101010"
WHITE = "#ffffff"
TEXT = "#e7e9ea"
MUTED = "#9a9fa5"
TRACK = "#1f1f1f"
FONT = '-apple-system,"Segoe UI","Helvetica Neue",Helvetica,Arial,sans-serif'

W = 1000
PAD = 40

# ═════════════════════════════════════════════════════════════════════════════
# data
# ═════════════════════════════════════════════════════════════════════════════
QUERY = """
query($login:String!){
  user(login:$login){
    createdAt
    followers{ totalCount }
    repositories(first:100, ownerAffiliations:OWNER, privacy:PUBLIC, isFork:false,
                 orderBy:{field:STARGAZERS, direction:DESC}){
      totalCount
      nodes{
        stargazerCount forkCount
        languages(first:10, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name } } }
      }
    }
    contributionsCollection{
      totalCommitContributions totalPullRequestContributions
      totalIssueContributions totalPullRequestReviewContributions
      restrictedContributionsCount
      contributionCalendar{
        totalContributions
        weeks{ contributionDays{ date contributionCount contributionLevel } }
      }
    }
  }
}
"""
LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def gql(query: str, variables: dict, token: str) -> dict:
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-renderer"})
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.loads(r.read())
    if "errors" in payload:
        raise SystemExit(f"GraphQL error: {payload['errors']}")
    return payload["data"]


def fetch_years(login: str, token: str, created: dt.date) -> list[tuple[int, int, int]]:
    this_year = dt.date.today().year
    parts = [f'y{y}: contributionsCollection(from:"{y}-01-01T00:00:00Z", to:"{y}-12-31T23:59:59Z")'
             '{ contributionCalendar{ totalContributions } totalCommitContributions restrictedContributionsCount }'
             for y in range(created.year, this_year + 1)]
    u = gql("query($login:String!){ user(login:$login){ " + " ".join(parts) + " } }", {"login": login}, token)["user"]
    out = []
    for y in range(created.year, this_year + 1):
        c = u[f"y{y}"]
        out.append((y, c["contributionCalendar"]["totalContributions"],
                    c["totalCommitContributions"] + c["restrictedContributionsCount"]))
    return out


def fetch(login: str, token: str) -> dict:
    u = gql(QUERY, {"login": login}, token)["user"]
    created = dt.date.fromisoformat(u["createdAt"][:10])
    years = fetch_years(login, token, created)
    cc = u["contributionsCollection"]
    weeks = [[(d["date"], d["contributionCount"], LEVELS[d["contributionLevel"]])
              for d in w["contributionDays"]] for w in cc["contributionCalendar"]["weeks"]]
    langs: dict[str, int] = {}
    stars = 0
    for repo in u["repositories"]["nodes"]:
        stars += repo["stargazerCount"]
        for e in repo["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    return {
        "weeks": weeks,
        "total": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"] + cc["restrictedContributionsCount"],
        "prs": cc["totalPullRequestContributions"],
        "issues": cc["totalIssueContributions"],
        "reviews": cc["totalPullRequestReviewContributions"],
        "stars": stars,
        "repos": u["repositories"]["totalCount"],
        "followers": u["followers"]["totalCount"],
        "langs": langs,
        "years": years,
        "alltime": sum(t for _, t, _ in years),
        "since": created.year,
    }


def demo() -> dict:
    rng = random.Random(7)
    today = dt.date.today()
    start = today - dt.timedelta(days=364 + today.isoweekday() % 7)
    weeks, day = [], start
    while day <= today:
        wk = []
        for _ in range(7):
            if day > today:
                break
            c = 0
            if rng.random() < 0.62:
                c = int(abs(rng.gauss(0, 1)) * 5 * (1.6 if day.weekday() < 5 else .6))
            wk.append((day.isoformat(), c, 0 if c == 0 else min(4, 1 + c // 4)))
            day += dt.timedelta(days=1)
        weeks.append(wk)
    total = sum(c for w in weeks for _, c, _ in w)
    years = [(2022, 980, 800), (2023, 1640, 1400), (2024, 2210, 1900), (2025, 2860, 2400), (2026, total, int(total * .82))]
    return {"weeks": weeks, "total": total, "commits": int(total * .82), "prs": 38, "issues": 0, "reviews": 0,
            "stars": 146, "repos": 24, "followers": 58,
            "langs": {"Python": 420, "TypeScript": 300, "JavaScript": 160, "HTML": 70, "CSS": 55, "Shell": 20},
            "years": years, "alltime": sum(t for _, t, _ in years), "since": 2022}


# ═════════════════════════════════════════════════════════════════════════════
# primitives
# ═════════════════════════════════════════════════════════════════════════════
CSS = f"""
text{{font-family:{FONT}}}
.in{{opacity:0;animation:in 1.1s cubic-bezier(.2,.6,.2,1) forwards}}
@keyframes in{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
.star{{animation:star 18s ease-in-out infinite}}
@keyframes star{{0%,100%{{opacity:.18}}50%{{opacity:.5}}}}
"""


def svg(h: int, body: str, title: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" '
            f'aria-label="{esc(title)}"><title>{esc(title)}</title><style>{CSS}</style>{body}</svg>')


def panel(h: int) -> str:
    return (f'<rect width="{W}" height="{h}" rx="20" fill="{BG}"/>'
            f'<rect x=".5" y=".5" width="{W-1}" height="{h-1}" rx="20" fill="none" stroke="{BORDER}"/>')


def t(x, y, s, size=15, fill=TEXT, weight=400, anchor="start", ls=0, cls="", extra=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
            f'text-anchor="{anchor}" letter-spacing="{ls}"{c} {extra}>{esc(str(s))}</text>')


def title(s: str, right: str = "") -> str:
    out = t(PAD, 50, s, 22, WHITE, 600)
    if right:
        out += t(W - PAD, 50, right, 15, MUTED, 400, "end")
    return out + f'<line x1="{PAD}" y1="72" x2="{W-PAD}" y2="72" stroke="{BORDER}"/>'


def grow(x, y, w_to, h, fill, delay, rx=0, opacity=1):
    return (f'<rect x="{x}" y="{y}" width="0" height="{h}" rx="{rx}" fill="{fill}" opacity="{opacity}">'
            f'<animate attributeName="width" from="0" to="{w_to:.1f}" begin="{delay:.2f}s" dur="1.4s" fill="freeze" '
            f'calcMode="spline" keySplines=".2 .6 .2 1" keyTimes="0;1"/></rect>')


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fmt(n: int) -> str:
    return f"{n:,}"


def stars(rng: random.Random, n: int, y_max: int) -> str:
    return "".join(
        f'<circle cx="{rng.uniform(0, W):.0f}" cy="{rng.uniform(0, y_max):.0f}" r="{rng.choice([.8, 1, 1.2])}" '
        f'fill="{WHITE}" class="star" style="animation-delay:{rng.uniform(-18, 0):.0f}s"/>' for _ in range(n))


# ═════════════════════════════════════════════════════════════════════════════
# panels
# ═════════════════════════════════════════════════════════════════════════════
def hero(c: dict) -> str:
    h = 400
    rng = random.Random(4)
    site, mail = c["site"], c["email"]
    pw1, pw2 = len(site) * 8.6 + 44, len(mail) * 8.6 + 44
    gap = 16
    x1 = (W - (pw1 + gap + pw2)) / 2
    x2 = x1 + pw1 + gap
    body = f"""<defs>
<radialGradient id="glow" cx="50%" cy="100%" r="60%"><stop offset="0" stop-color="{WHITE}" stop-opacity=".10"/><stop offset="1" stop-color="{WHITE}" stop-opacity="0"/></radialGradient>
</defs>
{panel(h)}
<rect width="{W}" height="{h}" rx="20" fill="url(#glow)"/>
{stars(rng, 26, 300)}
<path d="M-40 {h+120} Q 500 {h-110} {W+40} {h+120}" fill="none" stroke="{WHITE}" stroke-opacity=".28" stroke-width="1.2"/>
{t(500, 172, c['name'], 66, WHITE, 700, "middle", 4, "in")}
{t(500, 214, c['title'], 17, MUTED, 500, "middle", 5, "in", 'style="animation-delay:.25s"')}
{t(500, 262, c['tagline'], 22, TEXT, 400, "middle", 0, "in", 'style="animation-delay:.5s"')}
<g class="in" style="animation-delay:.8s">
<rect x="{x1:.0f}" y="300" width="{pw1:.0f}" height="42" rx="21" fill="{FILL}" stroke="{BORDER}"/>
{t(x1 + pw1/2, 327, site, 16, WHITE, 500, "middle")}
<rect x="{x2:.0f}" y="300" width="{pw2:.0f}" height="42" rx="21" fill="{FILL}" stroke="{BORDER}"/>
{t(x2 + pw2/2, 327, mail, 16, WHITE, 500, "middle")}
</g>"""
    return svg(h, body, c["name"])


def overview(d: dict) -> str:
    h = 240
    days = [x for wk in d["weeks"] for x in wk]
    longest = cur = 0
    for _, cnt, _ in days:
        cur = cur + 1 if cnt else 0
        longest = max(longest, cur)
    current = 0
    for _, cnt, _ in reversed(days):
        if cnt:
            current += 1
        else:
            break
    tiles = [("Contributions · 12 months", fmt(d["total"])),
             (f"All-time · since {d['since']}", fmt(d["alltime"])),
             ("Longest streak", f"{longest} days"),
             ("Current streak", f"{current} days")]
    body = [panel(h), title("Overview", "Live from GitHub")]
    tw = (W - 2 * PAD) / 4
    for i, (k, v) in enumerate(tiles):
        x = PAD + i * tw
        body.append(f'<g class="in" style="animation-delay:{.15+i*.12:.2f}s">'
                    f'{t(x, 110, k, 14, MUTED)}{t(x, 160, v, 44, WHITE, 600)}</g>')
        if i:
            body.append(f'<line x1="{x-18:.0f}" y1="92" x2="{x-18:.0f}" y2="176" stroke="{BORDER}"/>')
    extras = [("Commits", d["commits"]), ("Pull requests", d["prs"]), ("Stars", d["stars"]),
              ("Followers", d["followers"]), ("Public repos", d["repos"])]
    line = "    ·    ".join(f"{k} {fmt(v)}" for k, v in extras if v)
    body.append(t(PAD, 212, line, 15, MUTED, 400, cls="in", extra='style="animation-delay:.7s"'))
    return svg(h, "".join(body), "Overview")


def contributions(d: dict) -> str:
    weeks = d["weeks"]
    cols = len(weeks)
    cell, gap = 13, 4
    pitch = cell + gap
    ox, oy = PAD + 46, 124
    years = d["years"]
    yb = oy + 7 * pitch + 50          # by-year block top
    h = yb + 60 + len(years) * 34 + 20
    days = [x for wk in weeks for x in wk]
    best = max(days, key=lambda x: x[1]) if days else ("", 0, 0)
    active = sum(1 for _, cnt, _ in days if cnt)
    body = [panel(h), title("Contributions", f"Last 12 months · {fmt(d['total'])}")]
    # month labels
    seen = set()
    for i, wk in enumerate(weeks):
        if wk and wk[0][0][:7] not in seen:
            seen.add(wk[0][0][:7])
            if 0 < i < cols - 3:
                body.append(t(ox + i * pitch, oy - 14, dt.date.fromisoformat(wk[0][0]).strftime("%b"), 13, MUTED))
    for j, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        body.append(t(ox - 12, oy + j * pitch + cell - 2, name, 13, MUTED, anchor="end"))
    fills = {0: "#1a1a1a", 1: "#4b4b4b", 2: "#8d8d8d", 3: "#c9c9c9", 4: WHITE}
    cells = []
    for i, wk in enumerate(weeks):
        for j, (date, cnt, lvl) in enumerate(wk):
            x, y = ox + i * pitch, oy + j * pitch
            cells.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{fills[lvl]}" opacity="0">'
                         f'<animate attributeName="opacity" to="1" begin="{i*0.025:.3f}s" dur="1s" fill="freeze"/>'
                         f'<title>{date}: {cnt}</title></rect>')
    body.append("".join(cells))
    # legend + facts
    ly = oy + 7 * pitch + 16
    body.append(t(ox, ly + 11, f"Best day {best[1]}  ·  Active {active} of {len(days)} days", 14, MUTED))
    lx = W - PAD - 5 * 19 - 52
    body.append(t(lx - 8, ly + 11, "Less", 13, MUTED, anchor="end"))
    for k in range(5):
        body.append(f'<rect x="{lx + k*19}" y="{ly}" width="{cell}" height="{cell}" rx="3" fill="{fills[k]}"/>')
    body.append(t(W - PAD, ly + 11, "More", 13, MUTED, anchor="end"))
    # by year
    body.append(f'<line x1="{PAD}" y1="{yb}" x2="{W-PAD}" y2="{yb}" stroke="{BORDER}"/>')
    body.append(t(PAD, yb + 34, "By year", 18, WHITE, 600))
    body.append(t(W - PAD, yb + 34, f"All-time {fmt(d['alltime'])}", 15, MUTED, anchor="end"))
    mx = max(1, max(tot for _, tot, _ in years))
    bx, bw = PAD + 70, W - 2 * PAD - 70 - 110
    for i, (y, tot, _) in enumerate(years):
        yy = yb + 70 + i * 34
        last = i == len(years) - 1
        body.append(f'<g class="in" style="animation-delay:{.3+i*.1:.2f}s">'
                    f'{t(PAD, yy + 6, y, 16, WHITE if last else TEXT, 600 if last else 400)}'
                    f'<rect x="{bx}" y="{yy-5}" width="{bw}" height="12" rx="6" fill="{TRACK}"/>'
                    f'{grow(bx, yy-5, bw*tot/mx, 12, WHITE if last else "#8d8d8d", .5+i*.1, 6)}'
                    f'{t(W - PAD, yy + 6, fmt(tot), 16, WHITE if last else TEXT, 600 if last else 400, "end")}</g>')
    return svg(h, "".join(body), "Contributions")


def languages(d: dict) -> str:
    langs = sorted(d["langs"].items(), key=lambda kv: -kv[1])[:6]
    total = sum(v for _, v in langs) or 1
    h = 100 + 40 * len(langs) + 10
    body = [panel(h), title("Languages", "Public repositories")]
    bx, bw = PAD + 170, W - 2 * PAD - 170 - 90
    for i, (name, v) in enumerate(langs):
        y = 112 + i * 40
        pct = v / total * 100
        body.append(f'<g class="in" style="animation-delay:{.15+i*.1:.2f}s">'
                    f'{t(PAD, y + 6, name, 16, WHITE if i == 0 else TEXT, 600 if i == 0 else 400)}'
                    f'<rect x="{bx}" y="{y-5}" width="{bw}" height="12" rx="6" fill="{TRACK}"/>'
                    f'{grow(bx, y-5, bw*pct/100, 12, WHITE if i == 0 else "#8d8d8d", .3+i*.1, 6)}'
                    f'{t(W - PAD, y + 6, f"{pct:.0f}%", 16, TEXT, 400, "end")}</g>')
    return svg(h, "".join(body), "Languages")


def pill_row(items: list[str], x0: float, y: float, max_x: float, delay: float, out: list) -> float:
    """Lay out pills, wrapping. Returns bottom y."""
    x, ph, gap = x0, 36, 10
    for k, s in enumerate(items):
        pw = len(s) * 8.4 + 30
        if x + pw > max_x:
            x, y = x0, y + ph + gap
        out.append(f'<g class="in" style="animation-delay:{delay + k*.04:.2f}s">'
                   f'<rect x="{x:.0f}" y="{y}" width="{pw:.0f}" height="{ph}" rx="18" fill="{FILL}" stroke="{BORDER}"/>'
                   f'{t(x + pw/2, y + 23, s, 15, TEXT, 500, "middle")}</g>')
        x += pw + gap
    return y + ph


def capabilities(c: dict) -> str:
    groups = c["systems"]
    out: list[str] = []
    y = 104
    for gi, g in enumerate(groups):
        out.append(t(PAD, y, g["group"].title(), 14, MUTED, 600, ls=1))
        y = pill_row([n for n, _ in g["items"]], PAD, y + 14, W - PAD, .15 + gi * .15, out) + 30
    h = y
    return svg(h, panel(h) + title("Capabilities") + "".join(out), "Capabilities")


def pipeline(c: dict) -> str:
    stages = [("Intent", "goal & context"), ("Plan", "break it down"), ("Build", "code & design"),
              ("Verify", "evals & guardrails"), ("Ship", "deploy & observe")]
    agents = c["swarm"]
    h = 380
    body = [panel(h), title("How I build", "Agents with rails")]
    sw = (W - 2 * PAD - 4 * 28) / 5
    for i, (name, sub) in enumerate(stages):
        x = PAD + i * (sw + 28)
        body.append(f'<g class="in" style="animation-delay:{.15+i*.12:.2f}s">'
                    f'<rect x="{x:.0f}" y="96" width="{sw:.0f}" height="70" rx="14" fill="{FILL}" stroke="{BORDER}"/>'
                    f'{t(x + sw/2, 126, name, 17, WHITE, 600, "middle")}{t(x + sw/2, 148, sub, 13, MUTED, 400, "middle")}</g>')
        if i < 4:
            ax = x + sw + 14
            body.append(f'<path d="M{ax-5} 126 L{ax+5} 131 L{ax-5} 136" fill="none" stroke="{MUTED}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>')
    body.append(t(PAD, 214, "Agents in the loop", 18, WHITE, 600))
    cw = (W - 2 * PAD - 2 * 16) / 3
    for i, a in enumerate(agents):
        x = PAD + (i % 3) * (cw + 16)
        y = 236 + (i // 3) * 62
        body.append(f'<g class="in" style="animation-delay:{.7+i*.08:.2f}s">'
                    f'<rect x="{x:.0f}" y="{y}" width="{cw:.0f}" height="50" rx="12" fill="{FILL}" stroke="{BORDER}"/>'
                    f'<circle cx="{x+22:.0f}" cy="{y+25}" r="4" fill="{WHITE}"/>'
                    f'{t(x + 38, y + 30, a["id"], 16, WHITE, 600)}'
                    f'{t(x + cw - 16, y + 30, a["desc"], 14, MUTED, 400, "end")}</g>')
    return svg(h, "".join(body), "How I build")


def work(c: dict) -> str:
    builds = c["builds"]
    h = 96 + 64 * len(builds) + 10
    body = [panel(h), title("Selected work", f"More at {c['site']}")]
    for i, b in enumerate(builds):
        y = 96 + i * 64
        st = b["status"]
        pw = len(st) * 8.4 + 30
        body.append(f'<g class="in" style="animation-delay:{.15+i*.12:.2f}s">'
                    f'{t(PAD, y + 26, b["name"], 18, WHITE, 600)}{t(PAD, y + 48, b["stack"], 14, MUTED)}'
                    f'<rect x="{W-PAD-pw:.0f}" y="{y+16}" width="{pw:.0f}" height="30" rx="15" fill="{FILL}" stroke="{BORDER}"/>'
                    f'{t(W - PAD - pw/2, y + 36, st, 13, TEXT, 500, "middle")}'
                    + (f'<line x1="{PAD}" y1="{y+62}" x2="{W-PAD}" y2="{y+62}" stroke="{BORDER}"/>' if i < len(builds) - 1 else "")
                    + '</g>')
    return svg(h, "".join(body), "Selected work")


def contact(c: dict) -> str:
    rows = [("Website", c["site"]), ("Email", c["email"]), ("GitHub", f"github.com/{c['handle']}"),
            ("LinkedIn", c.get("linkedin", "")), ("X", c.get("x", "")), ("Telegram", c.get("telegram", ""))]
    rows = [(k, v) for k, v in rows if v]
    per_col = (len(rows) + 1) // 2
    h = 96 + per_col * 44 + 16
    body = [panel(h), title("Contact", "Replies within 24h")]
    cw = (W - 2 * PAD) / 2
    for i, (k, v) in enumerate(rows):
        x = PAD + (i // per_col) * cw
        y = 116 + (i % per_col) * 44
        body.append(f'<g class="in" style="animation-delay:{.15+i*.08:.2f}s">'
                    f'{t(x, y, k, 14, MUTED)}{t(x + 110, y, v, 17, WHITE, 500)}</g>')
    return svg(h, "".join(body), "Contact")


def footer(c: dict) -> str:
    h = 200
    rng = random.Random(9)
    body = f"""<defs>
<radialGradient id="glow2" cx="50%" cy="100%" r="60%"><stop offset="0" stop-color="{WHITE}" stop-opacity=".10"/><stop offset="1" stop-color="{WHITE}" stop-opacity="0"/></radialGradient>
</defs>{panel(h)}<rect width="{W}" height="{h}" rx="20" fill="url(#glow2)"/>{stars(rng, 18, 120)}
<path d="M-40 {h+90} Q 500 {h-80} {W+40} {h+90}" fill="none" stroke="{WHITE}" stroke-opacity=".28" stroke-width="1.2"/>
{t(500, 92, c['quote'], 26, WHITE, 600, "middle", 0, "in")}
{t(500, 128, f"{c['site']}   ·   {c['email']}", 15, MUTED, 400, "middle", 1, "in", 'style="animation-delay:.3s"')}"""
    return svg(h, body, "Footer")


# ═════════════════════════════════════════════════════════════════════════════
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--user", default=CONFIG["handle"])
    args = ap.parse_args()
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    live = bool(token) and not args.demo
    data = fetch(args.user, token) if live else demo()
    ASSETS.mkdir(exist_ok=True)
    for old in ASSETS.glob("*.svg"):
        old.unlink()
    out = {
        "hero.svg": hero(CONFIG),
        "overview.svg": overview(data),
        "contributions.svg": contributions(data),
        "languages.svg": languages(data),
        "capabilities.svg": capabilities(CONFIG),
        "pipeline.svg": pipeline(CONFIG),
        "work.svg": work(CONFIG),
        "contact.svg": contact(CONFIG),
        "footer.svg": footer(CONFIG),
    }
    for name, content in out.items():
        (ASSETS / name).write_text(content, encoding="utf-8")
    print(f"rendered {len(out)} assets ({'live' if live else 'demo'})")


if __name__ == "__main__":
    main()
