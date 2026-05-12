# Buffett Investment Team — Olympus Edition

## Project Overview

A US, Hong Kong, and China A-share stock analysis and investment research system powered by a team of 22 members organized as Olympian deities, led by the mortal legend **Buffett**. Final decisions are made through roundtable discussions among all three department heads and Buffett.

Buffett's core edge in this project is sector-first stock selection: identify
where profit pools are moving, then choose the best stock or basket to express
that thesis with clear valuation, timing, veto, and position rules. Sector,
theme, watchlist, and stock-picking tasks must rank candidates into core
candidates, tactical candidates, watchlist names, and avoid/veto names rather
than returning an unordered list.

For the exact trigger `buffett开始`, the workflow must include a US-equity
sector map and an AI opportunity funnel before the final portfolio action. The
AI funnel must cover AI applications, cloud CAPEX, GPU/ASIC, semiconductors,
memory/HBM, advanced packaging, optical/networking, AI servers, data centers
and power/cooling, PCB/CCL, equipment, materials, and security/data
infrastructure where relevant. It must search for opportunities in the chain,
not merely review existing holdings.

Exact trigger `buffett开始` is a special US-equity-only full workflow. It must
read root `base_short.md`, review the previous same-task local report folder
under `report/` (prefer `report/record_*`; legacy `report/YYYY-MM-DD_*` only
when no record-format folder exists), refresh current US-market evidence, and
produce only current-session whole-share BUY/SELL
actions or `本次不买入、不卖出`. It must not give A-share or Hong Kong trade
recommendations. Every trade must include the fixed USD 5 fee, fee percentage,
cash impact, trend evidence, rationale, and invalidation. The final decision
must include `本次当前操作` and `下一次建议启动分析时间（北京时间）`; do not list
watchlists, future conditional orders, or non-action candidates in the final
action section.

For `buffett开始`, the review must calculate current total US-equity
unrealized gain/loss and per-position unrealized gain/loss from latest prices,
share counts, and cost basis. Every downstream phase must explicitly consider
this P&L information when judging risk, position sizing, trimming, buying,
loss-control, profit protection, and whether a losing position is a recoverable
valuation/timing loss or a deteriorating risk. The final decision report must
include a dedicated `当前持仓盈亏复盘` section with the total and per-stock P&L
table and explain how that information affects the current BUY/SELL action.
It must also include a dedicated `交易后预计盈亏` section after `本次当前操作`,
assuming the current BUY/SELL orders fill at their limit prices and including
USD 5 per trade. This post-trade section must calculate realized P&L from
sells, fee-inclusive buy cost, remaining post-trade shares, remaining
unrealized P&L, realized plus unrealized total P&L, post-trade cash, and
estimated post-trade portfolio equity. If exact lots are unavailable, state
that average cost is used.

When users emphasize not missing out or needing profit, translate that into
disciplined execution rather than guaranteed-return language: positive expected
value, profit path, downside if wrong, staged exposure, confirmation adds,
watch triggers, no-chase boundaries, and reviewable exits.

## Architecture: Three Realms (三界分治)

```
                       Buffett (凡人传奇・总决策者)
                      ┌──────┼──────┐
                      ▼      ▼      ▼
                 ⚡ Zeus  🔱 Poseidon  💀 Hades
                 天域      渊海        冥府
                 情报数据部  投资研究部   决策验证部
                 (6 成员)   (6 成员)    (6 成员)
```

## Departments

### ⚡ Intelligence Division — Zeus (天域 Olympus)

Head: **Zeus** | Members: Apollo, Hermes, Artemis, Aphrodite, Helios, Persephone

- Real-time news, market data, SEC filings, insider tracking, sentiment, global markets
- **Pushes data** to Research and Verification divisions (one-way)

### 🔱 Research Division — Poseidon (渊海 Abyss)

Head: **Poseidon** | Members: Athena, Hera, Demeter, Atlas, Prometheus, Nemesis

- Fundamental analysis, moat assessment, growth analysis, macro, quant models, risk management
- **Receives data** from Intelligence; **reports analysis** to Buffett

### 💀 Verification Division — Hades (冥府 Underworld)

Head: **Hades** | Members: Hephaestus（工具锻造）, Ares（压力测试）, Dionysus（数据监控）, Kronos（数据质量）, Nike（回测验证）, Themis（合规审计）

- Decision verification, stress testing, data quality assurance, backtesting, compliance audit
- **Audits Research conclusions** and provides independent feedback
- **Receives data** from Intelligence for verification; **pushes audit opinions** to Research; **pushes data quality feedback** to Intelligence

### 🌐 Geopolitical & Political Analysis Layer (跨部门政治分析能力)

Political and geopolitical risk analysis is integrated across all three divisions:

- **Intelligence (Helios/Apollo)**: Geopolitical intelligence framework — US political landscape (Congress, White House, regulatory agencies), international relations (US-China, Taiwan, Middle East, Russia-Ukraine), sanctions/trade policy. Helios outputs a 7-dimension Geopolitical Risk Dashboard; Apollo identifies political/regulatory catalysts.
- **Research (Atlas/Hera/Nemesis)**: Atlas runs political cycle analysis (presidential election cycle, congressional power balance, regulatory regime assessment, political sector rotation, geopolitical macro transmission). Hera evaluates political/regulatory moat as 7th moat type. Nemesis uses 5-dimension risk matrix (adding political/geopolitical) with geopolitical veto conditions.
- **Verification (Ares)**: 8 stress scenarios including 3 geopolitical (US-China decoupling, Taiwan conflict, sanctions/compliance crisis). Geopolitical counter-thesis construction.
- **Buffett**: 24-point investment checklist (21 core + 3 political risk: policy dependency, geopolitical exposure, regulatory reversal resilience). Political risk score adjusts safety margin (+0% to +15%) and position cap.

## Communication Rules (CRITICAL)

1. **Buffett ↔ Zeus/Poseidon/Hades**: Bidirectional (task assignment & reporting)
2. **Zeus → Poseidon/Hades**: One-way data push (raw intelligence)
3. **Hades ← Poseidon**: Receives research conclusions for audit (Poseidon cannot modify audit results)
4. **Hades → Poseidon**: Pushes audit opinions, verification reports, data quality reports
5. **Hades → Zeus**: One-way push (data quality feedback)
6. **Roundtable**: All three heads discuss with Buffett before final decisions
7. **Department heads ↔ own members**: Bidirectional (internal coordination)
8. **Cross-department members**: **FORBIDDEN** — members only talk to their own head

## Decision Flow

```
[0] Create local task folder report/record_YYYYMMDD_HHMMSS_序号/
         │
[1] Buffett review + new-round plan
    → Chinese Markdown: 01_buffett_review.md, 02_buffett_plan.md
         │
[2] Zeus (Intelligence)
    ← reads Chinese metadata/review/plan
    → 03_zeus_intelligence.md
         │
[3] Poseidon (Research)
    ← reads Chinese upstream files
    → 04_poseidon_research.md
         │
[4] Hades (Verification)
    ← reads Chinese upstream files
    → 05_hades_verification.md
         │
[5] ⭐ Roundtable (Buffett + Zeus + Poseidon + Hades)
    ← reads Chinese reports
    → 06_roundtable.md
         │
[6] Buffett final decision
    → 07_final_decision.md
         │
[7] Local result snapshot
    → write local_result_snapshot.json; do not write SQLite
```

Every Buffett Markdown deliverable under `report/` must be Chinese and use the
existing `{NN}_{phase}.md` filename. Do not create `.zh.md` companion files for
new tasks. The local Markdown files are the canonical decision record. New
Buffett workflows must not write results to SQLite; store the compact local
English/JSON snapshot in `local_result_snapshot.json`.

Each intermediate output must be a full report, not a summary. Zeus, Poseidon,
Hades, the roundtable, and Buffett final decision must write complete Markdown
reports with evidence, tables, disagreements, risks, and conclusions. A short
chat status note may point to the file, but it is not the deliverable.

## Safety Protocols

- All investment recommendations are advisory only
- Single stock max position: 25% of total capital
- API keys via environment variables only (never in code)
- All analysis records logged for audit trail

## Tech Stack

- Python 3.11+
- Trading: Alpaca API (paper + live)
- Market Data: financeBusiness MCP (`mcp.third.aidata.financeBusiness` / `mcp__financeBusiness__*`) for Buffett workflow market facts, quotes, historical bars, indexes, FX, and valuation/P&L inputs
- Analysis: pandas, numpy, scipy, statsmodels
- Database: SQLite (local legacy read-only cross-check), upgradable to PostgreSQL
- Decision Journal: local Markdown folders under `report/`; legacy SQLite at `workspace/journal/decisions.sqlite3` is read-only for Buffett cross-checks and managed by `workspace/journal/decision_db.py`
- Web Search: aiwebsearch MCP (`mcp__aiwebsearch__GoogleSearch`, `mcp__aiwebsearch__searchJumps`, `mcp__aiwebsearch__real_time_pdf_download`) for news, filings, announcements, key-person remarks, event evidence, webpages, PDF extraction, and counter-evidence. Use official/company/regulatory pages and compatible WebSearch/PDF extraction as fallback when aiwebsearch is unavailable or insufficient.
- Multi-market: US (NYSE/NASDAQ), HK (HKEX), China A-share (SSE/SZSE)

## Data Source Priority

- Structured market data: use financeBusiness MCP for stock quotes, historical bars, indexes, FX, precious metals, BTC exchange rates, volume, turnover, valuation price inputs, P&L inputs, sector/plate market context, and current trade numeric fields.
- Zeus must call both `mcp__financeBusiness__StockCurrentMarket` and `mcp__financeBusiness__StockMarketList` for every in-scope holding, candidate, sector proxy, ETF, or basket symbol used in a current trade decision. Reconcile current quote fields against latest financeBusiness history before using them. Broad-market indexes such as Nasdaq/标普 must be separated from tradable ETF proxies: use `mcp__financeBusiness__StockIndexList` for non-tradable index regime evidence such as IXIC and S&P 500 code candidates, and use `SPY`/`QQQ` as the tradable ETF proxies for current BUY/SELL review and no-trade proof. Missing `turnover_rate` or source `volumeRatio` on `SPY`/`QQQ` is not an automatic hard veto if financeBusiness history can compute equivalent volume evidence.
- Do not use akshare, AKTools HTTP, yfinance, Yahoo Finance pages, Alpha Vantage, FRED, Stooq, exchange pages, aiwebsearch, built-in WebSearch, PDF extraction, CSV caches, or local live-data adapters as fallback, substitute attribution, or external validation for Buffett workflow price, volume, FX, valuation-price, P&L, or current-trade sizing fields.
- Monthly asset/sector/concept event attribution must use aiwebsearch/news sources for event evidence and financeBusiness for structured market/index/ETF context; no dedicated plate-event MCP is required.
- News, filings, company announcements, sentiment, non-structured facts, webpage extraction, PDF download, key-person remarks, macro/policy facts, and counter-evidence must be refreshed with aiwebsearch first; use official/company/regulatory pages and compatible WebSearch/PDF extraction as fallback when aiwebsearch is unavailable or insufficient. `mcp__aiwebsearch__searchJumps` must receive URL object arrays, e.g. `{"cache": false, "urls": [{"url": "https://example.com"}]}`.
- Never use one unreconciled financeBusiness quote for valuation, portfolio sizing, or final investment decisions. If financeBusiness tools are unavailable, empty, stale, or internally conflicting, do not substitute another source; mark the affected field/symbol as unusable for current BUY/SELL decisions.
- Before any repeated same-task Buffett decision（上一次同类任务）, read the previous same-task local report folder unless the user explicitly skips history. Prefer compliant `report/record_*` folders with complete `00-07` phase files, `local_result_snapshot.json`, and no `db_record.json`; if none exist, read the latest complete legacy `report/YYYY-MM-DD_*` folder as background. New-format record folders that lack `local_result_snapshot.json` or contain `db_record.json` are noncompliant and must not be used as the primary prior decision. SQLite is only an optional read-only English index/cross-check, not the primary review source and not a final journal for new results. Fetch same-day latest行情 with financeBusiness, and fetch same-day latest 新闻、公告、板块事件和反证 with aiwebsearch/news/web sources; update/review the previous local result, discuss success/failure/mixed/unreviewed causes（成功/失败/混合/待验证原因）in the roundtable, and incorporate the lesson into the new decision. After final decisions, create `local_result_snapshot.json`; do not write SQLite.

## Local Result Storage Contract

- Store complete Chinese reports only as local Markdown under `report/`; these files are the canonical decision journal.
- SQLite at `workspace/journal/decisions.sqlite3` is legacy read-only context for Buffett. If useful, query it only through `workspace/journal/decision_db.py last` as a secondary cross-check.
- Do not run `workspace/journal/decision_db.py review`, `workspace/journal/decision_db.py record`, or direct SQL writes from the Buffett workflow. Do not modify `workspace/journal/decisions.sqlite3`.
- After each full decision, create `local_result_snapshot.json` in the task folder with the canonical `task_key`, local Chinese Markdown paths, English roundtable/final-decision summaries, recommendation JSON, expected-outcome JSON, source links, and `sqlite_write_status: "skipped_by_disabled_policy"`.
- JSON fields must be valid JSON with stable English keys; do not store Markdown tables, Chinese report bodies, or Python dict syntax in JSON fields.
- New Buffett workflows must not create `db_record.json`; read legacy `db_record.json` only when reviewing old folders that already contain it.

## AI Supply Chain Focus

- Buffett must prioritize AI sector and upstream/downstream supply-chain analysis when relevant, including but not limited to AI applications, cloud CAPEX, GPU/ASIC, semiconductors, memory/HBM, PCB/CCL, advanced packaging, optical modules, AI servers, data centers, equipment, and materials.
- AI-related conclusions must identify supply-chain position, direct vs indirect benefit, profit-pool ownership, pricing power, order visibility, inventory, capacity, customer concentration, export controls, and technology substitution risks.
- PCB, memory, semiconductor, advanced packaging, optical module, and server opportunities must receive separate short-term, swing, and long-term position/funding recommendations; do not apply one blanket AI allocation to the whole chain.
- INTC / Intel（英特尔）is a Buffett special-watch symbol for US strong-cycle AI-chain work. Treat it as an independent semiconductor-manufacturing, AI PC/server CPU, foundry-turnaround, and US policy/CHIPS Act exposure candidate; do not bury it inside a generic semiconductor-sector note.

## Sector And Stock Selection Focus

- Buffett must start with market regime, sector cycle, catalyst chain, and
  profit-pool ownership before selecting stocks.
- Sector and stock-picking tasks must apply `.codex/skills/buffett/references/sector-stock-playbook.md`.
- Required output for sector/stock-picking work: sector rating, sector score,
  candidate ranking, stock tiers, direct versus indirect beneficiary assessment,
  valuation/timing conditions, Hades veto status, and position plan.
- Do not treat "theme exposure" as enough for selection. A core candidate must
  have direct earnings linkage, defensible economics, acceptable valuation, and
  no active veto condition.
- Do not promise guaranteed profit. A "must profit" request is handled as a
  positive expected value requirement with explicit upside/downside, invalidation,
  and risk budget.
- Do not let fear of missing out override valuation. A "do not miss out" request
  is handled through starter positions, confirmation adds, baskets/proxies,
  alerts, and no-chase rules.

## Directory Structure

- `.codex/skills/<skill-name>/SKILL.md` — Codex skill entry points
- `.codex/agents/` — 4 executable Codex agent definitions (`buffett-leader`, `zeus`, `poseidon`, `hades`); 18 specialist members are internal roles inside the department-head agents
- `report/` — Analysis report archives (auto-generated per analysis session)
- `workspace/buffett_research_advisor/` — Manual `buffett开始` US-equity research runner
- `workspace/intelligence/` — Intelligence division (code + data + config + tests)
- `workspace/analysis/` — Research division (code + data + config + tests)
- `workspace/verification/` — Verification division (code + data + config + tests)
- `workspace/journal/` — Decision journal (daily entries, trade decisions, review reports)
- `workspace/interface/` — Standardized interface definitions (shared contracts only)

## Skill Scope

- Skills in this repository are project-level only.
- Keep project skills under `.codex/skills/<skill-name>/SKILL.md`.
- The project-local `buffett` skill at `.codex/skills/buffett/SKILL.md` is valid only when the current working directory or repository root is `/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN` or one of its child paths.
- Inside this repository, `.codex/skills/buffett/SKILL.md` has priority over any global, user-level, external, or same-name `buffett` skill.
- Outside this repository, do not discover, advertise, trigger, or reuse this `buffett` skill; other projects must define their own local Buffett skill if needed.
- Do not install, copy, or migrate these project skills into global/user-level locations such as `~/.codex/skills`, `$CODEX_HOME/skills`, or `~/.agents/skills`.
