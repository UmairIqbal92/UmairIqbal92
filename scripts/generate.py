#!/usr/bin/env python3
"""Agent-OS profile renderer.

Generates every animated SVG in ./assets from live GitHub data (GraphQL) plus
scripts/config.json. Pure stdlib. Run with --demo for synthetic data.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import random
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
CONFIG = json.loads((ROOT / "scripts" / "config.json").read_text())

# ── palette (X / SpaceX / Grok: black, bone white, cold greys, one blue) ──────
BG = "#000000"
PANEL = "#060606"
LINE = "#1a1a1a"
LINE2 = "#262626"
TEXT = "#e7e9ea"
DIM = "#71767b"
DIM2 = "#3a3f44"
WHITE = "#ffffff"
BLUE = "#1d9bf0"

SANS = '"Inter","SF Pro Display","Helvetica Neue","Segoe UI",Roboto,Arial,sans-serif'
MONO = '"JetBrains Mono","SF Mono",Menlo,Consolas,"Courier New",monospace'

W = 1000  # canvas width for every asset


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
                 "User-Agent": "agent-os-profile"})
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.loads(r.read())
    if "errors" in payload:
        raise SystemExit(f"GraphQL error: {payload['errors']}")
    return payload["data"]


def fetch_years(login: str, token: str, created: dt.date) -> list[tuple[int, int, int]]:
    """Per-year (year, contributions, commits) since account creation."""
    this_year = dt.date.today().year
    parts = []
    for y in range(created.year, this_year + 1):
        parts.append(f'y{y}: contributionsCollection(from:"{y}-01-01T00:00:00Z", to:"{y}-12-31T23:59:59Z")'
                     '{ contributionCalendar{ totalContributions } totalCommitContributions restrictedContributionsCount }')
    q = "query($login:String!){ user(login:$login){ " + " ".join(parts) + " } }"
    u = gql(q, {"login": login}, token)["user"]
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
    stars = forks = 0
    for repo in u["repositories"]["nodes"]:
        stars += repo["stargazerCount"]
        forks += repo["forkCount"]
        for e in repo["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    return {
        "weeks": weeks,
        "total": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"] + cc["restrictedContributionsCount"],
        "prs": cc["totalPullRequestContributions"],
        "issues": cc["totalIssueContributions"],
        "reviews": cc["totalPullRequestReviewContributions"],
        "stars": stars, "forks": forks,
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
            lvl = 0 if c == 0 else min(4, 1 + c // 4)
            wk.append((day.isoformat(), c, lvl))
            day += dt.timedelta(days=1)
        weeks.append(wk)
    total = sum(c for w in weeks for _, c, _ in w)
    years = [(2021, 310, 260), (2022, 980, 800), (2023, 1640, 1400), (2024, 2210, 1900), (2025, 2860, 2400), (2026, total, int(total*.82))]
    return {
        "years": years, "alltime": sum(t for _, t, _ in years), "since": 2021,
        "weeks": weeks, "total": total, "commits": int(total * .82), "prs": 38, "issues": 21,
        "reviews": 17, "stars": 146, "forks": 32, "repos": 24, "followers": 58,
        "langs": {"Python": 420, "TypeScript": 300, "JavaScript": 160, "HTML": 70,
                  "CSS": 55, "Shell": 20, "Dockerfile": 10, "SCSS": 9},
    }


# ═════════════════════════════════════════════════════════════════════════════
# helpers
# ═════════════════════════════════════════════════════════════════════════════
def svg(w: int, h: int, body: str, label: str, style: str = "") -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{label}"><title>{label}</title>'
            f'<style>{BASE_CSS}{style}</style>{body}</svg>')


BASE_CSS = f"""
.s{{font-family:{SANS}}}.m{{font-family:{MONO}}}
.tw{{animation:tw 12s ease-in-out infinite}}
@keyframes tw{{0%,100%{{opacity:.12}}50%{{opacity:.55}}}}
.up{{opacity:0;animation:up 1.6s cubic-bezier(.16,.6,.2,1) forwards}}
@keyframes up{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
.fi{{opacity:0;animation:fi 1.8s ease-out forwards}}
@keyframes fi{{to{{opacity:1}}}}
.blink{{animation:blink 3.2s ease-in-out infinite}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
.draw{{stroke-dasharray:2000;stroke-dashoffset:2000;animation:draw 5s cubic-bezier(.2,.5,.2,1) forwards}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
.pulse{{animation:pulse 6s ease-in-out infinite;transform-origin:center;transform-box:fill-box}}
@keyframes pulse{{0%,100%{{transform:scale(1);opacity:.7}}50%{{transform:scale(1.15);opacity:.4}}}}
"""


def stars(rng: random.Random, w: int, h: int, n: int, y_max: float | None = None) -> str:
    out = []
    y_max = y_max or h
    for _ in range(n):
        x, y = rng.uniform(0, w), rng.uniform(0, y_max)
        r = rng.choice([.5, .6, .7, .8, 1.0])
        dur, delay = rng.uniform(9, 16), rng.uniform(-16, 0)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{WHITE}" class="tw" '
                   f'style="animation-duration:{dur:.1f}s;animation-delay:{delay:.1f}s"/>')
    return "".join(out)


def defs_common() -> str:
    return f"""<defs>
<filter id="g6" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="g3" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="g1" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="1.2"/></filter>
<linearGradient id="hline" x1="0" x2="1"><stop offset="0" stop-color="{WHITE}" stop-opacity="0"/><stop offset=".5" stop-color="{WHITE}" stop-opacity=".6"/><stop offset="1" stop-color="{WHITE}" stop-opacity="0"/></linearGradient>
<linearGradient id="vfade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}"/></linearGradient>
</defs>"""


def frame(w: int, h: int, r: int = 16) -> str:
    return (f'<rect width="{w}" height="{h}" rx="{r}" fill="{BG}"/>'
            f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="{r}" fill="none" stroke="{LINE}"/>')


def corner_brackets(w: int, h: int, pad: int = 18, size: int = 14) -> str:
    p, s = pad, size
    d = (f"M{p} {p+s}V{p}H{p+s} M{w-p-s} {p}H{w-p}V{p+s} "
         f"M{p} {h-p-s}V{h-p}H{p+s} M{w-p-s} {h-p}H{w-p}V{h-p-s}")
    return f'<path d="{d}" fill="none" stroke="{DIM2}" stroke-width="1"/>'


def label(x: float, y: float, s: str, size: float = 10, fill: str = DIM, anchor: str = "start",
          ls: float = 2.5, cls: str = "m", extra: str = "") -> str:
    return (f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" letter-spacing="{ls}" {extra}>{s}</text>')


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fmt(n: int) -> str:
    return f"{n/1000:.1f}k" if n >= 10000 else f"{n:,}"


# ═════════════════════════════════════════════════════════════════════════════
# 1 · hero — launch sequence
# ═════════════════════════════════════════════════════════════════════════════
def hero(c: dict) -> str:
    w, h = W, 540
    rng = random.Random(42)
    body = [defs_common(), f"""<defs>
<radialGradient id="atmo" cx="50%" cy="0%" r="70%"><stop offset="0" stop-color="{WHITE}" stop-opacity=".14"/><stop offset=".35" stop-color="{BLUE}" stop-opacity=".05"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>
<radialGradient id="flare" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{WHITE}" stop-opacity=".5"/><stop offset=".2" stop-color="{WHITE}" stop-opacity=".12"/><stop offset="1" stop-color="{WHITE}" stop-opacity="0"/></radialGradient>
<linearGradient id="planet" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b0f16"/><stop offset=".3" stop-color="#020304"/><stop offset="1" stop-color="{BG}"/></linearGradient>
<linearGradient id="limb" x1="0" x2="1"><stop offset="0" stop-color="{WHITE}" stop-opacity="0"/><stop offset=".45" stop-color="{WHITE}" stop-opacity=".9"/><stop offset=".7" stop-color="{BLUE}" stop-opacity=".7"/><stop offset="1" stop-color="{WHITE}" stop-opacity="0"/></linearGradient>
<clipPath id="wm"><rect x="500" y="150" width="0" height="120"><animate attributeName="x" from="500" to="0" begin="3.2s" dur="2.4s" fill="freeze" calcMode="spline" keySplines=".2 .6 .2 1" keyTimes="0;1"/><animate attributeName="width" from="0" to="1000" begin="3.2s" dur="2.4s" fill="freeze" calcMode="spline" keySplines=".2 .6 .2 1" keyTimes="0;1"/></rect></clipPath>
<path id="traj" d="M60 520 C 260 470, 520 330, 960 60"/>
</defs>
<rect width="{w}" height="{h}" fill="{BG}"/>"""]
    # starfield
    body.append(f'<g>{stars(rng, w, h, 70, y_max=420)}</g>')
    # planet limb
    body.append(f"""
<g>
  <ellipse cx="500" cy="1330" rx="1080" ry="920" fill="url(#atmo)"/>
  <ellipse cx="500" cy="1330" rx="1060" ry="900" fill="url(#planet)"/>
  <ellipse cx="500" cy="1330" rx="1060" ry="900" fill="none" stroke="url(#limb)" stroke-width="1.6"/>
  <ellipse cx="500" cy="1330" rx="1060" ry="900" fill="none" stroke="{WHITE}" stroke-width="10" opacity=".08" filter="url(#g6)"/>
  <circle cx="790" cy="436" r="60" fill="url(#flare)" class="pulse" style="animation-duration:9s"/>
</g>""")
    # trajectory + vehicle
    body.append(f"""
<use href="#traj" fill="none" stroke="{WHITE}" stroke-opacity=".10" stroke-width="1" stroke-dasharray="2 8"/>
<use href="#traj" fill="none" stroke="{WHITE}" stroke-opacity=".38" stroke-width="1" class="draw" style="animation-duration:10s;animation-delay:2.6s"/>
<g opacity="0"><set attributeName="opacity" to="1" begin="2.6s"/>
  <circle r="10" fill="{WHITE}" opacity=".12" filter="url(#g6)"><animateMotion dur="10s" begin="2.6s" fill="freeze" calcMode="spline" keySplines=".25 .1 .25 1" keyTimes="0;1" keyPoints="0;1"><mpath href="#traj"/></animateMotion></circle>
  <circle r="2" fill="{WHITE}"><animateMotion dur="10s" begin="2.6s" fill="freeze" calcMode="spline" keySplines=".25 .1 .25 1" keyTimes="0;1" keyPoints="0;1"><mpath href="#traj"/></animateMotion></circle>
</g>""")
    # countdown
    seq = [("T-MINUS  00:00:03", 0.0, 1.0), ("T-MINUS  00:00:02", 1.0, 1.0), ("T-MINUS  00:00:01", 2.0, .6),
           ("IGNITION", 2.6, 1.6), ("LIFTOFF", 4.2, 3.0), ("ORBIT ACQUIRED  ·  NOMINAL", 7.2, 999)]
    for s, b, d in seq:
        end = "" if d > 100 else f';<animate attributeName="opacity" to="0" begin="{b+d:.1f}s" dur=".6s" fill="freeze"/>'
        body.append(f'<text x="500" y="112" class="m" font-size="11" fill="{TEXT}" text-anchor="middle" letter-spacing="4" opacity="0">'
                    f'<animate attributeName="opacity" to="1" begin="{b:.1f}s" dur=".6s" fill="freeze"/>{end.strip(";")}{s}</text>')
    # wordmark
    body.append(f"""
<g clip-path="url(#wm)">
  <text x="500" y="232" class="s" font-size="72" font-weight="200" fill="{WHITE}" text-anchor="middle" letter-spacing="18">{esc(c['name'])}</text>
</g>
<line x1="500" y1="256" x2="500" y2="256" stroke="url(#hline)" stroke-width="1"><animate attributeName="x1" from="500" to="300" begin="5s" dur="2s" fill="freeze" calcMode="spline" keySplines=".2 .6 .2 1" keyTimes="0;1"/><animate attributeName="x2" from="500" to="700" begin="5s" dur="2s" fill="freeze" calcMode="spline" keySplines=".2 .6 .2 1" keyTimes="0;1"/></line>
<text x="500" y="286" class="m fi" font-size="12" fill="{DIM}" text-anchor="middle" letter-spacing="7" style="animation-delay:5.8s">{esc(c['title'])}</text>
<text x="500" y="316" class="s fi" font-size="15" font-weight="300" fill="{TEXT}" text-anchor="middle" letter-spacing="1" style="animation-delay:6.6s">{esc(c['tagline'])}</text>
""")
    # HUD
    body.append(corner_brackets(w, h))
    body.append(f"""
<g class="fi" style="animation-delay:.3s">
  {label(40, 46, "MISSION", 9, DIM2)}{label(40, 62, c['mission'], 10, TEXT)}
  {label(150, 46, "VEHICLE", 9, DIM2)}{label(150, 62, c['vehicle'], 10, TEXT)}
  {label(260, 46, "BASE", 9, DIM2)}{label(260, 62, esc(c['location']), 10, TEXT)}
  {label(960, 46, "STATUS", 9, DIM2, "end")}
  <circle cx="900" cy="58" r="3" fill="{WHITE}" class="blink"/>{label(960, 62, "ALL SYSTEMS GO", 10, TEXT, "end")}
</g>
<g class="fi" style="animation-delay:.6s">
  {label(40, 494, "WEB", 9, DIM2)}{label(40, 510, c['site'], 10, TEXT, ls=1.5)}
  {label(960, 494, "COMMS", 9, DIM2, "end")}{label(960, 510, c['email'], 10, TEXT, "end", ls=1.5)}
</g>
<g class="fi" style="animation-delay:6.5s">
  {label(500, 500, "▼  SCROLL FOR TELEMETRY", 8, DIM2, "middle", 3, cls="m blink")}
</g>
<rect x="0" y="0" width="{w}" height="{h}" fill="none" stroke="{LINE}"/>""")
    return svg(w, h, "".join(body), f"{c['name']} — launch sequence")


# ═════════════════════════════════════════════════════════════════════════════
# 2 · section header
# ═════════════════════════════════════════════════════════════════════════════
def header(num: str, title: str, sub: str) -> str:
    w, h = W, 56
    body = f"""{defs_common()}<rect width="{w}" height="{h}" fill="{BG}"/>
<text x="0" y="30" class="m" font-size="11" fill="{DIM2}" letter-spacing="3">{num}</text>
<text x="44" y="32" class="s" font-size="20" font-weight="300" fill="{WHITE}" letter-spacing="6">{esc(title)}</text>
<text x="{w}" y="31" class="m" font-size="10" fill="{DIM}" text-anchor="end" letter-spacing="2">{esc(sub)}</text>
<line x1="0" y1="50" x2="{w}" y2="50" stroke="{LINE}"/>
<line x1="0" y1="50" x2="0" y2="50" stroke="{WHITE}" stroke-width="1" opacity=".8"><animate attributeName="x2" from="0" to="{w}" dur="2.6s" fill="freeze" calcMode="spline" keySplines=".2 .6 .2 1" keyTimes="0;1"/></line>
<circle cx="0" cy="50" r="2" fill="{WHITE}"><animate attributeName="cx" from="0" to="{w}" dur="2.6s" fill="freeze" calcMode="spline" keySplines=".2 .6 .2 1" keyTimes="0;1"/><animate attributeName="opacity" from="1" to="0" begin="2.3s" dur=".5s" fill="freeze"/></circle>"""
    return svg(w, h, body, f"{num} {title}")


# ═════════════════════════════════════════════════════════════════════════════
# 3 · telemetry tiles
# ═════════════════════════════════════════════════════════════════════════════
def telemetry(d: dict, stamp: str) -> str:
    w, h = W, 190
    tiles = [("CONTRIB · 12M", d["total"]), (f"ALL-TIME", d["alltime"]),
             ("COMMITS · 12M", d["commits"]), ("PULL REQS", d["prs"]),
             ("STARS", d["stars"]), ("FOLLOWERS", d["followers"])]
    mx = max(1, max(v for _, v in tiles))
    body = [defs_common(), frame(w, h)]
    body.append(f'<circle cx="32" cy="30" r="3" fill="{WHITE}" class="blink"/>')
    body.append(label(44, 34, "MISSION TELEMETRY · LIVE", 10, DIM))
    body.append(label(w - 28, 34, f"{stamp}  ·  SINCE {d['since']}  ·  ISSUES {d['issues']}  ·  REVIEWS {d['reviews']}  ·  REPOS {d['repos']}", 9, DIM2, "end", 2))
    body.append(f'<line x1="28" y1="48" x2="{w-28}" y2="48" stroke="{LINE}"/>')
    tw = (w - 56) / 6
    for i, (name, val) in enumerate(tiles):
        x = 28 + i * tw
        body.append(f"""<g class="up" style="animation-delay:{.15 + i*.12:.2f}s">
<text x="{x+16}" y="76" class="m" font-size="9" fill="{DIM2}" letter-spacing="2.5">{name}</text>
<text x="{x+16}" y="126" class="s" font-size="40" font-weight="200" fill="{WHITE}">{fmt(val)}</text>
<rect x="{x+16}" y="148" width="{tw-40}" height="1" fill="{LINE2}"/>
<rect x="{x+16}" y="148" width="0" height="1" fill="{WHITE}"><animate attributeName="width" from="0" to="{(tw-40)*val/mx:.1f}" begin="{.5+i*.12:.2f}s" dur="2.2s" fill="freeze" calcMode="spline" keySplines=".2 .6 .2 1" keyTimes="0;1"/></rect>
</g>""")
        if i:
            body.append(f'<line x1="{x:.1f}" y1="64" x2="{x:.1f}" y2="160" stroke="{LINE}"/>')
    body.append(corner_brackets(w, h, 12, 10))
    return svg(w, h, "".join(body), "Mission telemetry")


# ═════════════════════════════════════════════════════════════════════════════
# 4 · star chart — custom contribution graph
# ═════════════════════════════════════════════════════════════════════════════
def starchart(d: dict) -> str:
    weeks = d["weeks"]
    cols = len(weeks)
    cell, gap = 14, 3
    pitch = cell + gap
    ox, oy = 62, 178
    w = W
    years = d["years"]
    yh = 26
    ybase = oy + 7 * pitch + 60
    h = ybase + 30 + len(years) * yh + 24
    body = [defs_common(), frame(w, h)]

    days = [x for wk in weeks for x in wk]
    longest = cur = 0
    for _, c, _ in days:
        cur = cur + 1 if c else 0
        longest = max(longest, cur)
    current = 0
    for _, c, _ in reversed(days):
        if c:
            current += 1
        else:
            break
    best = max(days, key=lambda x: x[1]) if days else ("", 0, 0)
    active = sum(1 for _, c, _ in days if c)

    body.append(label(28, 34, "CONTRIBUTION FIELD · LAST 52 WEEKS", 10, DIM))
    body.append(label(w - 28, 34, "PUBLIC + PRIVATE · ALL REPOSITORIES", 9, DIM2, "end", 2))
    body.append(f'<line x1="28" y1="48" x2="{w-28}" y2="48" stroke="{LINE}"/>')

    # stat strip
    stats = [("CONTRIBUTIONS", fmt(d["total"])), ("ALL-TIME", fmt(d["alltime"])), ("LONGEST STREAK", f"{longest}d"),
             ("CURRENT STREAK", f"{current}d"), ("BEST DAY", f"{best[1]}"), ("ACTIVE DAYS", f"{active}/{len(days)}")]
    sw = (w - 56) / 6
    for i, (k, v) in enumerate(stats):
        x = 28 + i * sw
        body.append(f'<g class="up" style="animation-delay:{.2+i*.1:.2f}s">'
                    f'<text x="{x+12}" y="72" class="m" font-size="8.5" fill="{DIM2}" letter-spacing="2">{k}</text>'
                    f'<text x="{x+12}" y="104" class="s" font-size="26" font-weight="200" fill="{WHITE}">{v}</text></g>')
        if i:
            body.append(f'<line x1="{x:.1f}" y1="62" x2="{x:.1f}" y2="112" stroke="{LINE}"/>')
    body.append(f'<line x1="28" y1="128" x2="{w-28}" y2="128" stroke="{LINE}"/>')

    # month labels
    seen = set()
    for i, wk in enumerate(weeks):
        if not wk:
            continue
        m = wk[0][0][:7]
        if m not in seen:
            seen.add(m)
            if 0 < i < cols - 3:
                name = dt.date.fromisoformat(wk[0][0]).strftime("%b").upper()
                body.append(label(ox + i * pitch, oy - 12, name, 8.5, DIM, ls=1.5))
    for j, name in ((1, "MON"), (3, "WED"), (5, "FRI")):
        body.append(label(ox - 10, oy + j * pitch + cell - 4, name, 8, DIM2, "end", 1))

    # cells
    fills = {0: "#151515", 1: "#3f3f3f", 2: "#767676", 3: "#b3b3b3", 4: WHITE}
    cells = []
    for i, wk in enumerate(weeks):
        for j, (date, cnt, lvl) in enumerate(wk):
            x, y = ox + i * pitch, oy + j * pitch
            delay = f"{i*0.03:.2f}s"
            stroke = f' stroke="{LINE2}" stroke-width=".5"' if lvl == 0 else ""
            cells.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{fills[lvl]}"{stroke} '
                         f'opacity="0"><animate attributeName="opacity" to="1" begin="{delay}" dur="1.2s" fill="freeze" '
                         f'calcMode="spline" keySplines=".2 .6 .2 1" keyTimes="0;1"/><title>{date} · {cnt} contributions</title></rect>')
    body.append("".join(cells))

    # legend
    ly = oy + 7 * pitch + 18
    body.append(label(w - 28 - 5 * 18 - 40, ly + 10, "LESS", 8, DIM2, "end", 2))
    for k in range(5):
        st = f' stroke="{LINE2}" stroke-width=".5"' if k == 0 else ""
        body.append(f'<rect x="{w - 28 - 5*18 - 30 + k*18}" y="{ly}" width="{cell}" height="{cell}" rx="3" fill="{fills[k]}"{st}/>')
    body.append(label(w - 28, ly + 10, "MORE", 8, DIM2, "end", 2))
    body.append(label(ox, ly + 10, f"PEAK {best[1]} ON {best[0]}", 8, DIM2, ls=2))

    # all-time history
    body.append(f'<line x1="28" y1="{ybase}" x2="{w-28}" y2="{ybase}" stroke="{LINE}"/>')
    body.append(label(28, ybase + 20, f"ALL-TIME HISTORY · {fmt(d['alltime'])} CONTRIBUTIONS SINCE {d['since']}", 10, DIM))
    body.append(label(w - 28, ybase + 20, "YEAR · CONTRIBUTIONS · COMMITS", 9, DIM2, "end", 2))
    mx = max(1, max(t for _, t, _ in years))
    bx, bw = 100, w - 56 - 100 - 200
    for i, (y, t, c) in enumerate(years):
        yy = ybase + 44 + i * yh
        last = i == len(years) - 1
        body.append(f"""<g class="up" style="animation-delay:{.6+i*.12:.2f}s">
<text x="28" y="{yy+4}" class="m" font-size="11" fill="{WHITE if last else TEXT}" letter-spacing="1">{y}</text>
<rect x="{bx}" y="{yy-4}" width="{bw}" height="8" rx="2" fill="{LINE}"/>
<rect x="{bx}" y="{yy-4}" width="0" height="8" rx="2" fill="{WHITE if last else '#8a8a8a'}"><animate attributeName="width" from="0" to="{bw*t/mx:.1f}" begin="{.8+i*.12:.2f}s" dur="2.2s" fill="freeze" calcMode="spline" keySplines=".2 .6 .2 1" keyTimes="0;1"/></rect>
<text x="{w-28-90}" y="{yy+4}" class="s" font-size="13" font-weight="{500 if last else 300}" fill="{WHITE if last else TEXT}" text-anchor="end">{fmt(t)}</text>
<text x="{w-28}" y="{yy+4}" class="m" font-size="10" fill="{DIM}" text-anchor="end">{fmt(c)} c</text>
</g>""")
    body.append(corner_brackets(w, h, 12, 10))
    return svg(w, h, "".join(body), "Contribution field")


# ═════════════════════════════════════════════════════════════════════════════
# 5 · propellant mix — languages
# ═════════════════════════════════════════════════════════════════════════════
def propellant(d: dict) -> str:
    langs = sorted(d["langs"].items(), key=lambda kv: -kv[1])[:8]
    total = sum(v for _, v in langs) or 1
    w, h = W, 96 + 30 * len(langs)
    body = [defs_common(), frame(w, h)]
    body.append(label(28, 34, "PROPELLANT MIX · LANGUAGE MASS FRACTION", 10, DIM))
    body.append(label(w - 28, 34, f"{len(langs)} COMPONENTS · PUBLIC REPOS", 9, DIM2, "end", 2))
    body.append(f'<line x1="28" y1="48" x2="{w-28}" y2="48" stroke="{LINE}"/>')
    # stacked gauge
    x, gx0, gw = 28, 28, w - 56
    body.append(f'<rect x="{gx0}" y="62" width="{gw}" height="6" fill="{LINE}"/>')
    for i, (name, v) in enumerate(langs):
        seg = gw * v / total
        op = 1 - i * 0.11
        body.append(f'<rect x="{x:.1f}" y="62" width="0" height="6" fill="{WHITE}" opacity="{op:.2f}">'
                    f'<animate attributeName="width" from="0" to="{max(0, seg-1.5):.1f}" begin="{.2+i*.1:.1f}s" dur="2s" fill="freeze" calcMode="spline" keySplines=".2 .6 .2 1" keyTimes="0;1"/></rect>')
        x += seg
    # rows
    for i, (name, v) in enumerate(langs):
        y = 100 + i * 30
        pct = v / total * 100
        bw = (w - 56 - 300)
        body.append(f"""<g class="up" style="animation-delay:{.3+i*.08:.2f}s">
<text x="28" y="{y+4}" class="m" font-size="9" fill="{DIM2}" letter-spacing="2">{i+1:02d}</text>
<text x="60" y="{y+4}" class="s" font-size="13" font-weight="{500 if i==0 else 300}" fill="{WHITE if i==0 else TEXT}">{esc(name)}</text>
<rect x="240" y="{y-1}" width="{bw}" height="2" fill="{LINE}"/>
<rect x="240" y="{y-1}" width="0" height="2" fill="{WHITE}" opacity="{1-i*.1:.2f}"><animate attributeName="width" from="0" to="{bw*pct/100:.1f}" begin="{.5+i*.08:.2f}s" dur="2.2s" fill="freeze" calcMode="spline" keySplines=".2 .6 .2 1" keyTimes="0;1"/></rect>
<text x="{w-28}" y="{y+4}" class="m" font-size="11" fill="{TEXT}" text-anchor="end">{pct:.1f}%</text>
</g>""")
    body.append(corner_brackets(w, h, 12, 10))
    return svg(w, h, "".join(body), "Language mass fraction")


# ═════════════════════════════════════════════════════════════════════════════
# 6 · systems check — skills from config
# ═════════════════════════════════════════════════════════════════════════════
def systems(c: dict) -> str:
    groups = c["systems"]
    rows = max(len(g["items"]) for g in groups)
    colw = (W - 56) / 2
    gh = 44 + rows * 26 + 16
    w, h = W, 64 + gh * math.ceil(len(groups) / 2) + 16
    body = [defs_common(), frame(w, h)]
    body.append(label(28, 34, "SYSTEMS CHECK · PRE-FLIGHT", 10, DIM))
    body.append(label(w - 28, 34, "ALL SYSTEMS NOMINAL", 9, TEXT, "end", 2))
    body.append(f'<circle cx="{w-176}" cy="30" r="3" fill="{WHITE}" class="blink"/>')
    body.append(f'<line x1="28" y1="48" x2="{w-28}" y2="48" stroke="{LINE}"/>')
    n = 0
    for gi, g in enumerate(groups):
        gx = 28 + (gi % 2) * colw
        gy = 64 + (gi // 2) * gh
        body.append(label(gx + 12, gy + 22, f"{gi+1:02d} · {g['group']}", 9, DIM, ls=3))
        body.append(f'<line x1="{gx+12}" y1="{gy+32}" x2="{gx+colw-12}" y2="{gy+32}" stroke="{LINE}"/>')
        for ii, (name, lvl) in enumerate(g["items"]):
            y = gy + 54 + ii * 26
            bx, bw = gx + 200, colw - 290
            n += 1
            ticks = "".join(f'<line x1="{bx + bw*k/10:.1f}" y1="{y-4}" x2="{bx + bw*k/10:.1f}" y2="{y+4}" stroke="{LINE2}"/>' for k in range(11))
            body.append(f"""<g class="up" style="animation-delay:{.2 + n*.05:.2f}s">
<text x="{gx+12}" y="{y+4}" class="s" font-size="12" font-weight="300" fill="{TEXT}">{esc(name)}</text>
{ticks}
<rect x="{bx}" y="{y-1}" width="0" height="2" fill="{WHITE}" opacity=".9"><animate attributeName="width" from="0" to="{bw*lvl/100:.1f}" begin="{.4+n*.05:.2f}s" dur="2.2s" fill="freeze" calcMode="spline" keySplines=".2 .6 .2 1" keyTimes="0;1"/></rect>
<text x="{gx+colw-12}" y="{y+4}" class="m" font-size="10" fill="{DIM}" text-anchor="end">{'GO' if lvl>=75 else 'RDY'}  {lvl:>3}</text>
</g>""")
    body.append(corner_brackets(w, h, 12, 10))
    return svg(w, h, "".join(body), "Systems check")


# ═════════════════════════════════════════════════════════════════════════════
# 7 · the swarm — agent constellation
# ═════════════════════════════════════════════════════════════════════════════
def swarm(c: dict) -> str:
    w, h = W, 340
    rng = random.Random(11)
    nodes = c["swarm"]
    cx, cy = 500, 165
    body = [defs_common(), frame(w, h)]
    body.append(f'<g opacity=".6">{stars(rng, w, h, 40)}</g>')
    body.append(label(28, 34, "THE SWARM · MULTI-AGENT CONSTELLATION", 10, DIM))
    body.append(label(w - 28, 34, f"{len(nodes)} AGENTS · 1 ORCHESTRATOR · LINKED", 9, DIM2, "end", 2))
    body.append(f'<line x1="28" y1="48" x2="{w-28}" y2="48" stroke="{LINE}"/>')
    # links: hub-spoke + ring
    paths = []
    for i, nd in enumerate(nodes):
        paths.append((f"M{cx} {cy}L{nd['x']} {nd['y']}", i))
    for i in range(len(nodes)):
        a, b = nodes[i], nodes[(i + 1) % len(nodes)]
        paths.append((f"M{a['x']} {a['y']}L{b['x']} {b['y']}", i + 10))
    for k, (d, i) in enumerate(paths):
        ring = i >= 10
        body.append(f'<path id="lk{k}" d="{d}" fill="none" stroke="{WHITE}" stroke-opacity="{.10 if ring else .25}" stroke-width="1" '
                    f'stroke-dasharray="{"2 5" if ring else "none"}" class="draw" style="animation-duration:2s;animation-delay:{.3 + k*.12:.2f}s"/>')
    # packets along spokes (both directions)
    for k in range(len(nodes)):
        delay = rng.uniform(0, 4)
        body.append(f'<circle r="1.8" fill="{WHITE}" opacity="0"><set attributeName="opacity" to=".8" begin="3s"/>'
                    f'<animateMotion dur="{rng.uniform(7,11):.1f}s" begin="{3+delay:.1f}s" repeatCount="indefinite" keyPoints="0;1;0" keyTimes="0;.5;1" calcMode="linear"><mpath href="#lk{k}"/></animateMotion></circle>')
    # hub
    body.append(f"""<g class="fi" style="animation-delay:.2s">
<circle cx="{cx}" cy="{cy}" r="30" fill="{BLUE}" opacity=".12" filter="url(#g6)" class="pulse"/>
<circle cx="{cx}" cy="{cy}" r="22" fill="{BG}" stroke="{WHITE}" stroke-width="1"/>
<circle cx="{cx}" cy="{cy}" r="34" fill="none" stroke="{WHITE}" stroke-opacity=".25" stroke-dasharray="1 4"><animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="30s" repeatCount="indefinite"/></circle>
<circle cx="{cx}" cy="{cy}" r="4" fill="{WHITE}" class="blink"/>
{label(cx, cy+52, "ORCHESTRATOR", 9, TEXT, "middle", 3)}
{label(cx, cy+66, "route · memory · supervise", 8, DIM2, "middle", 1)}
</g>""")
    for i, nd in enumerate(nodes):
        x, y = nd["x"], nd["y"]
        above = y < cy
        ty = y - 22 if above else y + 30
        body.append(f"""<g class="fi" style="animation-delay:{1.2 + i*.15:.2f}s">
<circle cx="{x}" cy="{y}" r="12" fill="{WHITE}" opacity=".12" filter="url(#g3)"/>
<circle cx="{x}" cy="{y}" r="7" fill="{BG}" stroke="{WHITE}" stroke-width="1"/>
<circle cx="{x}" cy="{y}" r="2" fill="{WHITE}" class="tw" style="animation-duration:{rng.uniform(2,4):.1f}s"/>
{label(x, ty, nd['id'], 10, WHITE, "middle", 3)}
{label(x, ty + 13, esc(nd['desc']), 8, DIM, "middle", 1)}
</g>""")
    body.append(corner_brackets(w, h, 12, 10))
    return svg(w, h, "".join(body), "Agent swarm")


# ═════════════════════════════════════════════════════════════════════════════
# 8 · manifest — builds
# ═════════════════════════════════════════════════════════════════════════════
def manifest(c: dict) -> str:
    builds = c["builds"]
    w, h = W, 70 + 58 * len(builds) + 14
    body = [defs_common(), frame(w, h)]
    body.append(label(28, 34, "PAYLOAD MANIFEST · FEATURED BUILDS", 10, DIM))
    body.append(label(w - 28, 34, f"{len(builds)} PAYLOADS · SEE {c['site'].upper()}", 9, DIM2, "end", 2))
    body.append(f'<line x1="28" y1="48" x2="{w-28}" y2="48" stroke="{LINE}"/>')
    for i, b in enumerate(builds):
        y = 70 + i * 58
        body.append(f"""<g class="up" style="animation-delay:{.2+i*.12:.2f}s">
<text x="28" y="{y+26}" class="m" font-size="10" fill="{DIM2}" letter-spacing="2">P{i+1:02d}</text>
<text x="76" y="{y+22}" class="s" font-size="15" font-weight="400" fill="{WHITE}">{esc(b['name'])}</text>
<text x="76" y="{y+40}" class="m" font-size="10" fill="{DIM}" letter-spacing="1">{esc(b['stack'])}</text>
<rect x="{w-140}" y="{y+14}" width="112" height="22" rx="11" fill="none" stroke="{LINE2}"/>
<circle cx="{w-124}" cy="{y+25}" r="2.5" fill="{WHITE}" class="blink"/>
<text x="{w-112}" y="{y+29}" class="m" font-size="9" fill="{TEXT}" letter-spacing="2">{esc(b['status'])}</text>
<line x1="28" y1="{y+52}" x2="{w-28}" y2="{y+52}" stroke="{LINE}"/>
</g>""")
    body.append(corner_brackets(w, h, 12, 10))
    return svg(w, h, "".join(body), "Payload manifest")


# ═════════════════════════════════════════════════════════════════════════════
# 9 · uplink + divider + footer
# ═════════════════════════════════════════════════════════════════════════════
def uplink(c: dict) -> str:
    w, h = W, 150
    chans = [("WEB", c["site"]), ("COMMS", c["email"]), ("GITHUB", f"@{c['handle']}"),
             ("LINKEDIN", "TODO"), ("X", "TODO"), ("TELEGRAM", "TODO")]
    body = [defs_common(), frame(w, h)]
    body.append(label(28, 34, "UPLINK · COMMUNICATION CHANNELS", 10, DIM))
    body.append(label(w - 28, 34, "RESPONSE WINDOW · 24H", 9, DIM2, "end", 2))
    body.append(f'<line x1="28" y1="48" x2="{w-28}" y2="48" stroke="{LINE}"/>')
    tw = (w - 56) / 3
    for i, (k, v) in enumerate(chans):
        x = 28 + (i % 3) * tw
        y = 78 + (i // 3) * 36
        body.append(f"""<g class="up" style="animation-delay:{.2+i*.1:.2f}s">
<circle cx="{x+16}" cy="{y-4}" r="2.5" fill="{WHITE}" class="tw" style="animation-duration:{2+i*.4:.1f}s"/>
<text x="{x+30}" y="{y}" class="m" font-size="9" fill="{DIM2}" letter-spacing="2.5">{k}</text>
<text x="{x+110}" y="{y}" class="s" font-size="13" font-weight="300" fill="{TEXT if v!='TODO' else DIM2}">{esc(v)}</text>
</g>""")
    body.append(corner_brackets(w, h, 12, 10))
    return svg(w, h, "".join(body), "Uplink")


def divider() -> str:
    w, h = W, 30
    body = f"""{defs_common()}<rect width="{w}" height="{h}" fill="{BG}"/>
<line x1="0" y1="15" x2="{w}" y2="15" stroke="{LINE}"/>
<rect x="-160" y="14" width="160" height="1" fill="url(#hline)"><animate attributeName="x" from="-160" to="{w}" dur="9s" repeatCount="indefinite"/></rect>
<circle cx="500" cy="15" r="2" fill="{DIM2}"/>"""
    return svg(w, h, body, "divider")


def footer(c: dict) -> str:
    w, h = W, 260
    rng = random.Random(99)
    body = [defs_common(), f"""<defs>
<radialGradient id="atmo2" cx="50%" cy="100%" r="70%"><stop offset="0" stop-color="{WHITE}" stop-opacity=".10"/><stop offset=".4" stop-color="{BLUE}" stop-opacity=".04"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>
<linearGradient id="limb2" x1="0" x2="1"><stop offset="0" stop-color="{WHITE}" stop-opacity="0"/><stop offset=".5" stop-color="{WHITE}" stop-opacity=".8"/><stop offset="1" stop-color="{WHITE}" stop-opacity="0"/></linearGradient>
</defs><rect width="{w}" height="{h}" fill="{BG}"/>"""]
    body.append(stars(rng, w, h, 45, y_max=170))
    body.append(f"""<ellipse cx="500" cy="-760" rx="1100" ry="900" fill="url(#atmo2)" transform="translate(0,{h+20}) scale(1,-1) translate(0,-{h+20})"/>
<ellipse cx="500" cy="1160" rx="1080" ry="900" fill="#020304"/>
<ellipse cx="500" cy="1160" rx="1080" ry="900" fill="none" stroke="url(#limb2)" stroke-width="1.4"/>
<ellipse cx="500" cy="1160" rx="1080" ry="900" fill="none" stroke="{WHITE}" stroke-width="8" opacity=".07" filter="url(#g6)"/>
<text x="500" y="96" class="m" font-size="10" fill="{DIM2}" text-anchor="middle" letter-spacing="5">END OF TRANSMISSION</text>
<text x="500" y="132" class="s" font-size="22" font-weight="200" fill="{WHITE}" text-anchor="middle" letter-spacing="3">Ship the loop, not the demo.</text>
<text x="500" y="162" class="m" font-size="10" fill="{DIM}" text-anchor="middle" letter-spacing="3">{c['site']}   ·   {c['email']}</text>
<circle cx="500" cy="200" r="2.5" fill="{WHITE}" class="blink"/>
<text x="500" y="{h-34}" class="m" font-size="8" fill="{DIM2}" text-anchor="middle" letter-spacing="3">AGENT-OS · RENDERED BY UMAIR-1 AUTOPILOT · REGENERATES EVERY 6H</text>""")
    return svg(w, h, "".join(body), "End of transmission")


# ═════════════════════════════════════════════════════════════════════════════
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--user", default=CONFIG["handle"])
    args = ap.parse_args()
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if args.demo or not token:
        if not args.demo:
            print("no GITHUB_TOKEN → demo data", file=sys.stderr)
        data = demo()
    else:
        data = fetch(args.user, token)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%MZ")
    ASSETS.mkdir(exist_ok=True)
    out = {
        "hero.svg": hero(CONFIG),
        "telemetry.svg": telemetry(data, stamp),
        "starchart.svg": starchart(data),
        "propellant.svg": propellant(data),
        "systems.svg": systems(CONFIG),
        "swarm.svg": swarm(CONFIG),
        "manifest.svg": manifest(CONFIG),
        "uplink.svg": uplink(CONFIG),
        "divider.svg": divider(),
        "footer.svg": footer(CONFIG),
        "h-01.svg": header("01", "MISSION PROFILE", "WHO · WHY · HOW"),
        "h-02.svg": header("02", "TELEMETRY", "LIVE GITHUB SIGNAL"),
        "h-03.svg": header("03", "STAR CHART", "CONTRIBUTION FIELD · 52 WEEKS"),
        "h-04.svg": header("04", "SYSTEMS", "CAPABILITY MATRIX"),
        "h-05.svg": header("05", "THE SWARM", "AGENT ARCHITECTURE"),
        "h-06.svg": header("06", "MANIFEST", "FEATURED BUILDS"),
        "h-07.svg": header("07", "TRANSMISSIONS", "LATEST WRITING"),
        "h-08.svg": header("08", "UPLINK", "GET IN TOUCH"),
    }
    for name, content in out.items():
        (ASSETS / name).write_text(content, encoding="utf-8")
    print(f"rendered {len(out)} assets → {ASSETS} ({'demo' if args.demo or not token else 'live'})")


if __name__ == "__main__":
    main()
