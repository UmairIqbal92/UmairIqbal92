<!--
  ┌───────────────────────────────────────────────────────────────┐
  │  UMAIR IQBAL · AGENT-OS                                       │
  │  Every panel below is an animated SVG rendered by             │
  │  scripts/generate.py from live GitHub data + scripts/config.json │
  │  Regenerates every 6h via .github/workflows/agent-os.yml      │
  │  Edit scripts/config.json — never the SVGs.                   │
  └───────────────────────────────────────────────────────────────┘
-->

<div align="center">

<a href="https://umairiqbal.com"><img src="assets/hero.svg" width="100%" alt="Umair Iqbal — launch sequence" /></a>

</div>

<img src="assets/h-01.svg" width="100%" alt="01 · Mission profile" />

<table>
<tr>
<td width="58%" valign="top">

```yaml
# ── flight computer ──────────────────────────
callsign:   Umair Iqbal
class:      AI Solutions Architect
vehicle:    design ⇄ engineering ⇄ automation
mode:       autonomous · human-in-the-loop
base:       TODO(location)
flight_hrs: TODO(years)

mission:
  - architect agent systems that do real work
  - collapse idea → prototype → product loops
  - make AI feel premium, not gimmicky

now:
  building:  TODO(current project)
  learning:  agent evals · long-horizon memory
  open_to:   consulting · collabs · talks
```

</td>
<td width="42%" valign="top">

<br/>

| | Flight rules |
|:-:|:--|
| `01` | **Outcome over output.** Ship the loop, not the demo. |
| `02` | **Agents need rails.** Evals, guardrails, observability. Always. |
| `03` | **Design is architecture.** UX calls are system calls. |
| `04` | **Tokens are fuel.** Less context, sharper burn. |
| `05` | **Automate the toil.** Humans keep the judgment. |

<sub>⟶ <a href="https://umairiqbal.com">umairiqbal.com</a> · <a href="mailto:hello@umairiqbal.com">hello@umairiqbal.com</a></sub>

</td>
</tr>
</table>

<img src="assets/h-02.svg" width="100%" alt="02 · Telemetry" />

<img src="assets/telemetry.svg" width="100%" alt="Live GitHub telemetry" />

<img src="assets/divider.svg" width="100%" alt="" />

<img src="assets/h-03.svg" width="100%" alt="03 · Star chart" />

<img src="assets/starchart.svg" width="100%" alt="52-week contribution star chart" />

<img src="assets/propellant.svg" width="100%" alt="Language mass fraction" />

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/UmairIqbal92/UmairIqbal92/output/github-snake-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/UmairIqbal92/UmairIqbal92/output/github-snake-light.svg" />
  <img src="https://raw.githubusercontent.com/UmairIqbal92/UmairIqbal92/output/github-snake-dark.svg" alt="" width="100%" />
</picture>

<img src="assets/h-04.svg" width="100%" alt="04 · Systems" />

<img src="assets/systems.svg" width="100%" alt="Systems check — capability matrix" />

<img src="assets/h-05.svg" width="100%" alt="05 · The swarm" />

<img src="assets/swarm.svg" width="100%" alt="Multi-agent constellation" />

<details>
<summary>&nbsp;<code>▸ flight plan · reference architecture</code></summary>
<br/>

```mermaid
%%{init: {'theme':'base','themeVariables':{'background':'#000000','primaryColor':'#060606','primaryBorderColor':'#3a3f44','primaryTextColor':'#e7e9ea','lineColor':'#71767b','secondaryColor':'#060606','tertiaryColor':'#060606','fontFamily':'JetBrains Mono, SF Mono, monospace','fontSize':'12px'}}}%%
flowchart LR
  U([intent]) --> O{{orchestrator}}
  O --> P[planner]
  P --> R[research]
  P --> C[coder]
  P --> D[designer]
  R & C & D --> V[qa · evals]
  V -->|pass| S[(ship)]
  V -->|fail| P
  O <--> M[(memory)]
  C <--> T[/tools · MCP · APIs/]
  S --> OB[ops · observe]
  OB -. feedback .-> O
```

</details>

<img src="assets/h-06.svg" width="100%" alt="06 · Manifest" />

<img src="assets/manifest.svg" width="100%" alt="Payload manifest — featured builds" />

<!-- TODO(umair): pin real repos here. Pattern:
<a href="https://github.com/UmairIqbal92/REPO"><img src="https://github-readme-stats.vercel.app/api/pin/?username=UmairIqbal92&repo=REPO&theme=transparent&bg_color=000000&title_color=ffffff&text_color=71767b&icon_color=e7e9ea&border_color=1a1a1a" /></a>
-->

<img src="assets/h-07.svg" width="100%" alt="07 · Transmissions" />

<!-- BLOG-POST-LIST:START -->
- 📡 Feed not linked yet — set `feed_list` in `.github/workflows/blog-posts.yml`
<!-- BLOG-POST-LIST:END -->

<img src="assets/h-08.svg" width="100%" alt="08 · Uplink" />

<img src="assets/uplink.svg" width="100%" alt="Communication channels" />

<div align="center">

<a href="https://umairiqbal.com"><img src="https://img.shields.io/badge/umairiqbal.com-000000?style=for-the-badge&logo=googlechrome&logoColor=ffffff" alt="website" /></a>
&nbsp;
<a href="mailto:hello@umairiqbal.com"><img src="https://img.shields.io/badge/hello%40umairiqbal.com-000000?style=for-the-badge&logo=gmail&logoColor=ffffff" alt="email" /></a>
&nbsp;
<a href="https://github.com/UmairIqbal92"><img src="https://img.shields.io/badge/%40UmairIqbal92-000000?style=for-the-badge&logo=github&logoColor=ffffff" alt="github" /></a>
&nbsp;
<img src="https://komarev.com/ghpvc/?username=umairiqbal92&label=VISITORS&color=000000&labelColor=000000&style=for-the-badge" alt="visitors" />

</div>

<img src="assets/footer.svg" width="100%" alt="End of transmission" />
