<!--
  ╔══════════════════════════════════════════════════════════════╗
  ║  UMAIR IQBAL · AGENT OS · profile README                     ║
  ║  Animated assets live in ./assets (self-hosted, no deps).    ║
  ║  Search "TODO" to fill in details as they are confirmed.     ║
  ╚══════════════════════════════════════════════════════════════╝
-->

<div align="center">

<img src="assets/hero.svg" width="100%" alt="Umair Iqbal — Agent OS boot sequence" />

<br/>

<a href="https://umairiqbal.com">
  <img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=20&duration=2600&pause=900&color=22D3EE&center=true&vCenter=true&width=760&lines=AI+Solutions+Architect;Designing+multi-agent+systems+that+ship;LLM+orchestration+%C2%B7+MCP+%C2%B7+workflow+automation;Design+%2B+engineering+in+one+loop;Turning+ideas+into+autonomous+products" alt="typing intro" />
</a>

<br/>

<a href="https://umairiqbal.com"><img src="https://img.shields.io/badge/umairiqbal.com-070b12?style=for-the-badge&logo=googlechrome&logoColor=22d3ee" alt="website" /></a>
&nbsp;
<a href="mailto:hello@umairiqbal.com"><img src="https://img.shields.io/badge/hello%40umairiqbal.com-070b12?style=for-the-badge&logo=gmail&logoColor=a78bfa" alt="email" /></a>
&nbsp;
<a href="https://github.com/UmairIqbal92"><img src="https://img.shields.io/badge/%40UmairIqbal92-070b12?style=for-the-badge&logo=github&logoColor=f1f5f9" alt="github" /></a>
&nbsp;
<img src="https://komarev.com/ghpvc/?username=umairiqbal92&label=visitors&color=0b1020&labelColor=070b12&style=for-the-badge" alt="visitors" />

</div>

<br/>

## `⟩ whoami`

<table>
<tr>
<td width="55%" valign="top">

```yaml
agent:
  name:      Umair Iqbal
  class:     AI Solutions Architect
  runtime:   design ⇄ engineering ⇄ automation
  mode:      autonomous · human-in-the-loop
  base:      TODO(location)
  uptime:    TODO(years) in the field

mission:
  - architect agent systems that do real work
  - compress idea → prototype → product loops
  - make AI feel premium, not gimmicky

currently:
  building:  TODO(current project)
  learning:  agent evals · long-horizon memory
  open_to:   consulting · collaborations · talks
```

</td>
<td width="45%" valign="top">

### Operating principles

| # | Directive |
|:-:|:--|
| 01 | **Outcome over output.** Ship the loop, not the demo. |
| 02 | **Agents need rails.** Guardrails, evals, observability, always. |
| 03 | **Design is architecture.** UX decisions are system decisions. |
| 04 | **Token efficiency is a feature.** Less context, sharper results. |
| 05 | **Automate the boring.** Humans handle judgment, agents handle toil. |

<sub>Reach me → <a href="mailto:hello@umairiqbal.com">hello@umairiqbal.com</a> · <a href="https://umairiqbal.com">umairiqbal.com</a></sub>

</td>
</tr>
</table>

<br/>

## `⟩ pipeline`

<div align="center">
<img src="assets/pipeline.svg" width="100%" alt="Intent → Plan → Act → Verify → Ship" />
</div>

<details>
<summary><b>▸ Reference architecture (expand)</b></summary>
<br/>

```mermaid
%%{init: {'theme':'dark','themeVariables':{'primaryColor':'#0b1020','primaryBorderColor':'#22d3ee','primaryTextColor':'#e2e8f0','lineColor':'#a78bfa','fontFamily':'JetBrains Mono, monospace'}}}%%
flowchart LR
  U([User / Trigger]) --> O{{Orchestrator}}
  O --> P[Planner]
  P --> R[Researcher]
  P --> C[Coder]
  P --> D[Designer]
  R & C & D --> V[Verifier · evals]
  V -->|pass| S[(Ship)]
  V -->|fail| P
  O <--> M[(Memory)]
  C <--> T[/Tools · MCP · APIs/]
  S --> OB[Observability]
  OB -.feedback.-> O
```

</details>

<br/>

## `⟩ agent.stack`

<div align="center">

**Intelligence layer**<br/>
<img src="https://skillicons.dev/icons?i=python,pytorch,tensorflow,sklearn&theme=dark" alt="ai" />
&nbsp;
<img src="https://img.shields.io/badge/LLM_Orchestration-0b1020?style=flat-square&logo=openai&logoColor=22d3ee" />
<img src="https://img.shields.io/badge/MCP-0b1020?style=flat-square&logo=anthropic&logoColor=a78bfa" />
<img src="https://img.shields.io/badge/LangGraph-0b1020?style=flat-square&logo=langchain&logoColor=34d399" />
<img src="https://img.shields.io/badge/RAG_%2F_Vector_DBs-0b1020?style=flat-square&logo=databricks&logoColor=fbbf24" />

**Build layer**<br/>
<img src="https://skillicons.dev/icons?i=nodejs,ts,js,react,nextjs,fastapi,express,tailwind&theme=dark" alt="build" />

**Automation & data**<br/>
<img src="https://skillicons.dev/icons?i=postgres,mongodb,redis,supabase,firebase,graphql&theme=dark" alt="data" />
&nbsp;
<img src="https://img.shields.io/badge/n8n-0b1020?style=flat-square&logo=n8n&logoColor=f472b6" />
<img src="https://img.shields.io/badge/Make-0b1020?style=flat-square&logo=make&logoColor=a78bfa" />
<img src="https://img.shields.io/badge/Zapier-0b1020?style=flat-square&logo=zapier&logoColor=fbbf24" />

**Ship layer**<br/>
<img src="https://skillicons.dev/icons?i=docker,aws,gcp,vercel,cloudflare,github,githubactions,linux&theme=dark" alt="ship" />

**Design layer**<br/>
<img src="https://skillicons.dev/icons?i=figma,ps,ai,xd,blender&theme=dark" alt="design" />

<sub>TODO: prune / extend to match the real stack</sub>

</div>

<br/>

## `⟩ modules`

<div align="center">

| Module | Status | What it does |
|:--|:--:|:--|
| 🧭 **Planner** | `● online` | Breaks fuzzy goals into executable task graphs |
| 🔍 **Researcher** | `● online` | Grounds decisions in sources, not vibes |
| ⚙️ **Coder** | `● online` | Production-grade Python / Node, modular by default |
| 🎨 **Designer** | `● online` | Interfaces, brand systems, motion — pixel-accountable |
| 🛰️ **Ops** | `● online` | Deploys, monitors, and keeps the loop cheap |
| 🧪 **QA** | `● online` | Evals, guardrails, regression traps for agents |

</div>

<br/>

## `⟩ builds`

<!-- TODO(umair): replace placeholders with real repos. Pattern:
<a href="https://github.com/UmairIqbal92/REPO"><img src="https://github-readme-stats.vercel.app/api/pin/?username=UmairIqbal92&repo=REPO&theme=transparent&bg_color=0b1020&title_color=22d3ee&text_color=cbd5e1&icon_color=a78bfa&border_color=1f2b3d" /></a>
-->

<div align="center">

| Build | Stack | Status |
|:--|:--|:--:|
| **TODO · flagship agent product** | LLM · MCP · Next.js | `⟳ deploying` |
| **TODO · automation framework** | n8n · Node · Postgres | `⟳ deploying` |
| **TODO · design system / toolkit** | Figma · React · Tailwind | `⟳ deploying` |

<sub>Mission log updates as builds go public → <a href="https://umairiqbal.com">umairiqbal.com</a></sub>

</div>

<br/>

## `⟩ transmissions`

<!-- BLOG-POST-LIST:START -->
- 🛰️ Feed not linked yet — set `feed_list` in `.github/workflows/blog-posts.yml`
<!-- BLOG-POST-LIST:END -->

<br/>

## `⟩ telemetry`

<div align="center">

<a href="https://github.com/UmairIqbal92">
  <img height="170" src="https://github-readme-stats.vercel.app/api?username=UmairIqbal92&show_icons=true&include_all_commits=true&count_private=true&hide_border=true&bg_color=0b1020&title_color=22d3ee&text_color=cbd5e1&icon_color=a78bfa&ring_color=22d3ee" alt="stats" />
  <img height="170" src="https://github-readme-stats.vercel.app/api/top-langs/?username=UmairIqbal92&layout=compact&langs_count=8&hide_border=true&bg_color=0b1020&title_color=22d3ee&text_color=cbd5e1" alt="languages" />
</a>

<br/><br/>

<a href="https://github.com/UmairIqbal92">
  <img src="https://github-readme-streak-stats.herokuapp.com/?user=UmairIqbal92&hide_border=true&background=0b1020&stroke=1f2b3d&ring=22d3ee&fire=fbbf24&currStreakLabel=22d3ee&sideLabels=cbd5e1&currStreakNum=f1f5f9&sideNums=f1f5f9&dates=64748b" alt="streak" />
</a>

<br/><br/>

<a href="https://github.com/UmairIqbal92">
  <img src="https://github-readme-activity-graph.vercel.app/graph?username=UmairIqbal92&bg_color=0b1020&color=cbd5e1&line=22d3ee&point=a78bfa&area=true&area_color=0e7490&hide_border=true&custom_title=Activity%20telemetry" alt="activity graph" width="100%" />
</a>

<br/><br/>

<a href="https://github.com/ryo-ma/github-profile-trophy">
  <img src="https://github-profile-trophy.vercel.app/?username=UmairIqbal92&theme=algolia&no-frame=true&no-bg=true&margin-w=8&column=7" alt="trophies" />
</a>

<br/><br/>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/UmairIqbal92/UmairIqbal92/output/github-snake-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/UmairIqbal92/UmairIqbal92/output/github-snake-light.svg" />
  <img src="https://raw.githubusercontent.com/UmairIqbal92/UmairIqbal92/output/github-snake-dark.svg" alt="contribution snake" width="100%" />
</picture>

</div>

<br/>

## `⟩ uplink`

<div align="center">

| Channel | Address |
|:--|:--|
| 🌐 Web | [umairiqbal.com](https://umairiqbal.com) |
| ✉️ Mail | [hello@umairiqbal.com](mailto:hello@umairiqbal.com) |
| 🐙 GitHub | [@UmairIqbal92](https://github.com/UmairIqbal92) |
| 💼 LinkedIn | TODO |
| 𝕏 X / Twitter | TODO |
| ✈️ Telegram | TODO |

<br/>

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&size=14&duration=3000&pause=1200&color=64748B&center=true&vCenter=true&width=600&lines=%24+echo+%22Ship+the+loop%2C+not+the+demo.%22;%24+exit+0" alt="sign-off" />

</div>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:22d3ee,50:a78bfa,100:0b1020&height=110&section=footer" width="100%" alt="" />
