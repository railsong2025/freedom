---
name: buffett
description: |
  PROJECT-LOCAL ONLY for /Users/newsong/Desktop/AIstudio/Freedom_Multi_EN. Trigger and use this Buffett skill only when the current working directory or repository root is /Users/newsong/Desktop/AIstudio/Freedom_Multi_EN or one of its child paths.
---

# Buffett Investment Team - Local Markdown Workflow

This reference is the single source of truth for the project-local Buffett workflow.
All reports are local Markdown files. Do not publish, store, fetch, or pass reports through Yuque, Skylark, or any external document service.

For sector, theme, stock-picking, candidate-ranking, or watchlist tasks, also
apply `references/sector-stock-playbook.md`. That playbook is the single source
of truth for sector scorecards, stock scorecards, tiering, vetoes, and position
logic.

## Core Investment Mandate

Buffett's edge in this project is sector-first stock selection. Every investment
decision should first answer "where is the profit pool moving?" and only then
answer "which stock is the best expression of that view?"

Use this decision chain for sector, theme, and stock-picking tasks:

```text
market regime -> sector cycle -> event/catalyst chain -> profit-pool ownership -> company moat -> valuation/timing -> risk-adjusted position
```

Top-tier investment thinking means:

- Identify the investable change, not just the story: policy, capacity, pricing, demand, earnings revision, capital flow, or competitive structure.
- Prefer direct beneficiaries with durable economics over peripheral narrative beneficiaries.
- Separate high-quality companies from good trades; separate good trades from crowded traps.
- Compare upside drivers and downside failure modes before assigning a position size.
- Rank opportunities explicitly instead of offering an unordered list.
- Use Hades vetoes to prevent attractive narratives from passing when data quality, valuation, liquidity, compliance, or geopolitical risk is unacceptable.
- Manage missed-opportunity risk with staged exposure, confirmation adds,
  watch triggers, and basket alternatives; do not chase purely because a sector
  is moving.
- Treat "must profit" as positive expected value discipline. Reports must never
  guarantee returns; they must show profit path, downside if wrong, invalidation,
  and review triggers.

For US strong-cycle swing tasks, especially memory/HBM, semiconductors,
AI hardware, AI servers, storage and data-center power/cooling, apply the
swing overlay from `sector-stock-playbook.md`. Current trades must be
driven by technical setup, volume, relative strength, catalyst freshness,
fee-adjusted risk/reward, strict stop loss and explicit take-profit rules. A
long-term moat or sector thesis is not enough to justify a swing BUY.

Every actionable sector/stock conclusion must show:

- sector rating and why the sector is better or worse than alternatives;
- candidate ranking and why the selected name is the best expression;
- valuation/timing conditions instead of unconditional bullishness;
- strongest counter-thesis and falsification data;
- position size derived from evidence quality, not enthusiasm.
- anti-miss plan showing how Buffett participates if the thesis confirms and
  how Buffett avoids chasing if price outruns the buy zone;
- expected-value logic showing why the recommendation seeks profit after
  downside, liquidity, and timing risk.
- for swing strong-cycle trades, entry type (`动能突破`, `回撤承接`,
  `超跌反弹`, `止损卖出`, `止盈卖出`, `移动止损`), technical trigger, volume and
  relative strength evidence, hard stop, targets, trailing stop, max holding
  period, position size, risk dollars, and fee-adjusted risk/reward.

## Core Rule

Every full Buffett task runs as a strict sequential pipeline:

1. Buffett reviews the previous same-task local report folder first unless the user explicitly says not to read history or to skip review. SQLite is only an optional read-only English index/cross-check.
2. Buffett writes the Chinese review or skip notice to the local task report folder, then adds a dedicated `Buffett 自我反思` section.
3. Buffett plans the new decision round based on the review and self-reflection.
4. Buffett writes the Chinese plan to the local task report folder.
5. Buffett dispatches the public `zeus` skill for the intelligence phase,
   passing the Buffett task folder, Chinese upstream files, and acceptance
   contract.
6. Zeus writes the Chinese intelligence report to the local task report folder.
7. Buffett dispatches the public `poseidon` skill with the Buffett task folder,
   upstream evidence, and acceptance contract; Poseidon writes the Chinese
   research report.
8. Buffett dispatches the public `hades` skill with the Buffett task folder,
   upstream reports, and acceptance contract; Hades writes the Chinese
   verification report.
9. Buffett convenes the roundtable using all prior files.
10. Buffett writes Chinese roundtable minutes/final decision to local Markdown files.
11. Buffett writes `local_result_snapshot.json` after the local Markdown reports are complete. Buffett must not write the final result to SQLite.

No step may skip its predecessor. If a required upstream file is missing, stop and create or repair that file before continuing.

## Language And Storage Rule

Every Markdown deliverable has one local Chinese version:

- Chinese report file: `{NN}_{phase}.md`

The Chinese Markdown file is canonical for phase handoff, upstream reads, and the local audit trail. Do not create `.zh.md` companion files for new tasks. New Buffett workflows store compact English/JSON decision metadata in `local_result_snapshot.json` and must not write SQLite.

Every intermediate output is a full report, not a summary. Zeus, Poseidon, Hades, the roundtable, and the final decision must write complete Markdown files with evidence, analysis, tables, disagreements, risks, and conclusions. Short chat status updates may identify the completed file path, but they do not count as phase deliverables.

`local_result_snapshot.json` prose and decision-content fields must be English-only where an English field is required:

- `thesis`
- `roundtable_summary`
- `recommendation_json`
- `expected_outcome_json`
- `roundtable_english`
- `final_decision_english`
- `actual_result_json`
- `review_summary`

`source_doc_ids_json`-style path arrays in the local snapshot store the local Chinese Markdown paths for traceability. `local_result_snapshot.json` must include the Chinese report paths and `sqlite_write_status: "skipped_by_disabled_policy"`.

Steps 5-9 must follow `02_buffett_plan.md`. Zeus, Poseidon, Hades, and the roundtable must treat the plan as the execution contract. Every downstream report must include a plan-compliance table showing each assigned plan item, completion status, evidence/file section, and unresolved gap.

## Agent Dispatch And Report Acceptance Gates

Buffett must dispatch Zeus, Poseidon, and Hades with explicit assignment
contracts. A valid assignment includes the task folder, upstream Markdown paths,
the exact output file path, the phase-specific checklist copied from
`02_buffett_plan.md`, minimum required tables/sources, P&L/cash/fee/trading-window
constraints, and the instruction that chat replies are only status notices.

After each department finishes, Buffett must read the generated Markdown report
before starting the next phase. If the report fails acceptance, Buffett must ask
the same department head to rewrite or supplement the same file, then re-check it.
The workflow must not proceed on incomplete upstream files.

Universal acceptance failures:

- Missing or empty phase file, or a report that is only a brief summary.
- Missing plan-compliance table, or failure to answer each assigned item in
  `02_buffett_plan.md`.
- Missing input-file paths, source list, timestamps, data-conflict section, or
  unresolved-gap section.
- Zeus lacks a key-person statements section, or lists statements without
  speaker importance, source tier, impact chain, affected assets, observable
  market reaction, counter-evidence, and confidence.
- Investment-critical prices, valuation, FX, P&L, or position sizing rely on one
  unverified source without impact labeling.
- Current total and per-position P&L from `01_buffett_review.md` is not used in
  risk, sizing, trim, hold, buy, loss-control, or profit-protection reasoning.
- Sector, AI, or stock-picking work lacks sector map, candidate tiers, profit
  pool ownership, direct/indirect beneficiary assessment, valuation/timing, and
  Hades veto status.

Zeus acceptance gates:

- For `buffett开始` and AI-related tasks, Zeus must cover AI applications,
  cloud CAPEX, GPU/ASIC, semiconductors, memory/HBM, advanced packaging,
  optical/networking, AI servers, data centers and power/cooling, PCB/CCL,
  equipment, materials, and security/data infrastructure where relevant.
- Each relevant chain segment must include representative US-tradable tickers or
  ETFs, directness, key evidence with financeBusiness timestamp/tool status,
  financeBusiness current/history reconciliation status, main counter-evidence
  when available from financeBusiness or upstream local files, and current
  trading-window implication.
- Zeus must cover existing holdings, candidates outside current holdings, major
  US index/sector proxies, macro/rate/FX context, financeBusiness-exposed
  company/event evidence when available, financeBusiness tool/timestamp status,
  and internal financeBusiness conflicts.
- Zeus must cover market-moving statements by key people: Fed/FOMC, Treasury,
  White House/president, SEC/FTC/DOJ/Commerce/BIS/USTR and other regulators,
  geopolitical officials, CEOs/CFOs of current holdings, hyperscalers, and
  core AI supply-chain companies. Each material statement must include speaker,
  role, time, source/event, source tier, core message, impact chain, affected
  assets/sectors, observable market reaction when measurable, direction,
  confidence, and counter-evidence. Social-media or analyst comments are
  sentiment inputs only unless independently corroborated.

Poseidon acceptance gates:

- Poseidon must first analyze market regime, sector map, and AI/theme funnel
  before converting the work into stock tiers or portfolio action.
- Zeus data gaps must be mapped to valuation/sizing downgrades, wait decisions,
  vetoes, or explicit follow-up requests.
- Key-person statements must be classified as policy signal, company
  fundamental signal, supply-chain/order signal, regulatory/geopolitical signal,
  or market-sentiment noise, then mapped to valuation, sizing, timing, or no
  action.
- Required tables include sector score/rating, AI opportunity funnel, stock
  tiers, current P&L and position implications, position plan, profit path, and
  anti-miss/no-chase rules where relevant.
- For strong-cycle swing work, Poseidon must use the shared swing verdict
  contract (`workspace/analysis/cli.py swing-verdict` or equivalent) and show
  `current_trade`, `small_starter`, `wait`, or `hard_veto` for each core and
  tactical candidate plus each special-watch ticker including INTC/Intel.
  Open-window no-trade conclusions must include ETF/basket fallback review and
  a candidate-by-candidate no-trade proof.

Hades acceptance gates:

- Hades must include upstream report completeness audit for Zeus and Poseidon.
- Hades must audit whether key-person statements were verified, whether the
  market reaction was measured or appropriately marked unquantified, and whether
  Poseidon over-weighted rhetoric versus hard data.
- If Zeus intelligence is incomplete or Poseidon uses incomplete intelligence
  without discounting it, Hades must mark the conclusion as conditional or
  rejected and require roundtable remediation.
- Hades must verify P&L math, quote freshness, financeBusiness coverage and
  current/history reconciliation sufficiency, fee math, post-trade P&L math,
  25% single-stock cap, stress scenarios, and vetoes.
- Hades must reject generic "do not chase" vetoes. A strong move is not a hard
  veto unless stop, volume/relative strength, fee-adjusted R/R, gap risk, data
  quality, cash, or position limits fail. If single-name data quality fails,
  Hades must require ETF/basket fallback review before accepting no-trade.

## Local Task Folder

For each full task, create exactly one local work partition under `report/`:

```text
report/record_YYYYMMDD_HHMMSS_序号/
```

Rules:
- `YYYYMMDD_HHMMSS` is the current local timestamp in the workflow timezone.
- `序号` is a zero-padded local report sequence such as `001`, `002`, `003`.
- New Buffett folders must use this record format and must not use the old
  `YYYY-MM-DD_摘要` naming. Legacy folders may still be read as background only
  when no record-format folder exists.
- Keep all task artifacts in this folder.
- Do not create Yuque links, document IDs, or external publication records.

Required files:

```text
report/record_YYYYMMDD_HHMMSS_序号/
  00_metadata.md
  01_buffett_review.md
  02_buffett_plan.md
  03_zeus_intelligence.md
  04_poseidon_research.md
  05_hades_verification.md
  06_roundtable.md
  07_final_decision.md
  local_result_snapshot.json
```

Optional attachments such as downloaded filings, CSV exports, source snapshots, or charts must be stored in the same task folder or a child folder such as `sources/`.

## File Responsibilities

### 00_metadata.md

Created before the review phase. It must include:
- task folder path
- record folder name and sequence
- previous same-task local report folder path, or a clear no-local-history note
- task date and timezone
- user request
- canonical task type
- canonical subject
- symbols or assets
- generated `task_key`
- task_key design rationale
- planned file list
- data-source plan
- for sector/stock-picking tasks: decision mode, sector/theme universe,
  candidate universe, screening exclusions, required scorecards, and required
  veto checks from `references/sector-stock-playbook.md`
- profit discipline: expected return target style, loss budget, missed-opportunity
  handling, and no-guaranteed-profit constraint
- for US strong-cycle swing work: trading profile, focus tickers/ETFs,
  holding-period range, allowed setup types, single-trade risk budget, default
  stop-loss range, target/trailing-stop requirements, and Hades swing veto
  checks
- special watch scope for strong-cycle work: AMD, MU, FLEX, INTC/Intel（英特尔）,
  WDC, STX, VRT, ANET, TSM, NVDA, SMH, SOXX, and QQQ. INTC must be assessed
  independently and cannot be replaced by a generic semiconductor-sector note.

## Task Key And Task Type Discipline

Buffett owns task classification. This section is the only fixed taxonomy for `task_type`, `subject`, and `task_key` design. Other skill, agent, or project instructions must only reference and match against this section; they must not duplicate or redefine the task type list.

### Canonical Task Types

Use one of these task types by default:

| task_type | Use For | subject rule |
|---|---|---|
| `portfolio_review` | portfolio health checks, rebalancing, position audit, whole-account review | `portfolio` unless user names a specific portfolio/account |
| `single_stock_decision` | one-stock buy/sell/hold, valuation, moat, position sizing | normalized ticker/company |
| `multi_stock_compare` | comparing 2+ stocks or choosing between candidates | stable sorted symbol group, e.g. `compare:AAPL,MSFT,NVDA` |
| `sector_market_review` | market environment, sector rotation, macro/asset/industry judgment | normalized sector/market name |
| `event_attribution` | why a stock/sector/asset moved, catalyst attribution | normalized target + event window if essential |
| `trade_review` | explicit review of prior trade outcome or user feedback | normalized target or portfolio |
| `watchlist_opportunity` | new opportunities, screening, candidate list, watchlist | normalized theme or watchlist name |

Only create a new `task_type` when none of the canonical types fits. If a new type is needed, document the reason in `00_metadata.md`.

Special exact-trigger exception: for `buffett开始`, always use
`task_type=portfolio_review`, `subject=us_equity_portfolio`, and
`market=US equities`. This is the stable same-task identity for the special
US-equity-only full workflow and intentionally overrides the default
portfolio-subject rule above.

### Stable Subject Rules

- Do not include dates, adjectives, urgency, temporary wording, or user phrasing in `subject`.
- Do not create separate subjects for "analyze NVDA", "should I buy NVDA", and "NVDA valuation"; use `single_stock_decision` + `subject=NVDA` + `symbols=NVDA`.
- For portfolio tasks, use `subject=portfolio` unless there are clearly different portfolios.
- For multi-stock comparisons, sort symbols alphabetically and use one stable subject, e.g. `compare:AAPL,MSFT,NVDA`.
- For sectors/themes, normalize synonyms, e.g. `AI servers`, `AI server chain`, and `AI服务器` should map to one stable subject when the scope is the same.
- If the user asks to skip history, still design the same stable `task_key`; skip both local history review and optional SQLite read-only cross-check.

### Sector And Stock-Picking Classification

Use existing task types rather than inventing a new one:

- Use `sector_market_review` when the user's main need is sector direction, sector rotation, market regime, or industry-cycle judgment.
- Use `watchlist_opportunity` when the user asks for opportunities, stock picks, a theme-to-stock screen, a candidate pool, or "what should I buy from this sector?"
- Use `multi_stock_compare` when the user names multiple stocks and asks which one is superior.
- Use `event_attribution` when the request starts from a move or catalyst and asks why a sector or stock rose/fell.

For any sector-to-stock task, `00_metadata.md` must state the sector/theme,
markets covered, candidate universe, exclusion rules, and whether the output is
a sector view, candidate ranking, or investment decision.

### Task Key Rule

Generate `task_key` from canonical `task_type`, canonical `subject`, and sorted symbols. The key should represent the durable decision stream, not this session's wording.

Before writing `00_metadata.md`, Buffett must decide:

```text
task_type = one canonical type
subject = normalized durable subject
symbols = sorted canonical symbols/assets
task_key = decision_db.py key --task-type {task_type} --subject {subject} --symbols {symbols}
```

`00_metadata.md` must include a short "Why this task_key" note. If two possible task keys are plausible, choose the broader existing decision stream unless the user explicitly asks for a separate project or account.

### 01_buffett_review.md

Buffett must read the previous same-task local report folder before any new decision unless the user explicitly instructs not to read history, not to read previous decisions, or to skip the review. Prefer compliant `report/record_*` folders with complete `00-07` phase files, `local_result_snapshot.json`, and no `db_record.json`; if no compliant record-format folder exists, read the latest complete legacy `report/YYYY-MM-DD_*` folder only as background. New-format record folders that lack `local_result_snapshot.json` or contain `db_record.json` are noncompliant and must not be used as the primary prior decision. SQLite may be queried only as an English index/cross-check and must not replace local Chinese Markdown. Even when history is skipped, Buffett must still create `01_buffett_review.md` and state that the historical decision review was skipped by user instruction.

Minimum content:
- history mode: reviewed / skipped_by_user
- previous same-task local folder lookup rule and result, or "skipped by explicit user instruction"
- previous local folder path, report format, task_key, action, strategy, subject, and assumptions extracted from local Markdown when available, or "no previous local report folder"
- SQLite cross-check status when used, explicitly marked secondary
- latest same-day data gathered for review
- current portfolio P&L table for all US stocks/ETFs in `base_short.md`: current price, shares, cost price, current market value, cost amount, unrealized P&L amount, and unrealized P&L %
- total US portfolio P&L: total market value, total cost, total unrealized P&L amount, total unrealized P&L %, and cash background if cash is usable for US trading
- realized P&L from operation records when buy/sell lot data is sufficient; otherwise state that realized P&L cannot be calculated reliably
- outcome classification: success, failure, mixed, or unreviewed
- causes and lessons
- dedicated `Buffett 自我反思`: Buffett must base the reflection on the latest data and the previous same-task decision. The section must explicitly include `依据的最新数据`, `依据的历史决策`, `关键遗漏与分析错误复盘`, `反思结论`, and `基于反思的新策略`. `关键遗漏与分析错误复盘` must cover missed key-person remarks, missed key events, and key analytical mistakes. Buffett must examine its own task framing, AI-chain candidate coverage, data continuity, position sizing, missed-opportunity controls, no-chase discipline, stop/take-profit discipline, and fee-adjusted R/R. This section must not only judge stock price outcomes or shift responsibility to downstream departments.
- `关键遗漏与分析错误复盘` minimum checks:
  - missed key-person remarks from Fed/FOMC, Treasury, White House/President,
    SEC/FTC/DOJ, Commerce/BIS/USTR, current holding-company CEO/CFOs, AI cloud
    hyperscalers, NVIDIA/AMD/TSMC/ASML/Broadcom/Arista/Micron/Vertiv and other
    core AI supply-chain management, and material geopolitical actors
  - missed key events such as earnings/guidance, cloud CAPEX, AI orders, export
    controls, macro data, rate-path changes, sector rotation, supply-chain
    shortages/price hikes, regulatory/geopolitical shocks, ETF/industry fund
    flows, and intraday volume/price breakouts or failures
  - key analytical mistakes such as treating a long-term thesis as a swing
    setup, treating every momentum breakout as FOMO, vetoing only because a
    stock is up, using non-financeBusiness market facts, failing
    financeBusiness current/history reconciliation, lacking fee-adjusted R/R,
    lacking hard stop/take-profit rules, over-focusing on current losers while
    missing stronger opportunities, or presenting data gaps as firm conclusions
- `基于反思的新策略` must turn the reflection into current-round rules for data
  refresh, candidate coverage, starter/add/stop/take-profit, no-chase
  boundaries, Hades veto conditions, and what forces `本次不买入、不卖出`.
- how the lesson constrains the new decision
- whether an optional secondary SQLite read-only cross-check was used; do not update any SQLite record

If no previous local report folder exists, still create this file and state that this is the first local decision for the task key.
If the user skips history, do not read local report history and do not run `decision_db.py last`; write "history skipped by user instruction" and continue to `02_buffett_plan.md`.

### 02_buffett_plan.md

Buffett must create the new-round plan after the review and before Zeus starts.

Minimum content:
- review lessons that must be carried forward
- Buffett self-reflection and new-strategy items that must be converted into Zeus/Poseidon/Hades work requirements and later roundtable checks
- explicit department assignments for missed key-person remarks, missed key
  events, and key analytical mistakes: Zeus must补证, Poseidon must归因 and
  revise strategy, Hades must audit correction sufficiency, and the roundtable
  must rule whether these omissions change the current action
- current total and per-position P&L facts that must be carried forward into Zeus, Poseidon, Hades, and the roundtable
- objective of the new decision round
- task decomposition for Zeus, Poseidon, Hades, and the roundtable
- required data refreshes and source priorities
- special questions each department must answer, including whether losing positions are recoverable timing/valuation losses or deteriorating theses, whether winning positions need profit protection, and whether any proposed averaging-down is justified by fresh evidence rather than the loss itself
- AI supply-chain, geopolitical, portfolio, or risk modules to include when relevant
- sector-selection or stock-picking funnel when relevant: sector map, catalyst chain, candidate universe, ranking criteria, valuation/timing checks, and veto rules
- explicit scorecard plan when relevant: sector score factors, stock score factors,
  tier thresholds, Hades veto checks, and required ranking/position tables from
  `references/sector-stock-playbook.md`
- profit and anti-miss plan when relevant: expected profit drivers, downside
  budget, starter/add/watch rules, no-chase boundaries, and review triggers
- swing strong-cycle plan when relevant: candidate universe must cover AI
  supply-chain upstream/midstream/downstream representatives, including AI
  applications/cloud CAPEX/data infrastructure, GPU/ASIC, foundry, memory/HBM,
  semiconductor equipment/EDA/materials, advanced packaging, optical/networking,
  AI servers/ODM/EMS, data-center power/cooling, PCB/CCL, security/data
  infrastructure, and chain ETFs/baskets; include setup types, technical
  indicators, volume/relative-strength checks, stop/target/trailing-stop rules,
  max holding period, single-trade risk budget, and fee-adjusted expectancy
- expected outputs and file handoff checklist
- constraints from risk limits, previous mistakes, data gaps, or user instructions

### 03_zeus_intelligence.md

This phase must use the public Zeus skill at `.codex/skills/zeus/SKILL.md`.
The checklist below is Buffett's workflow handoff contract; Zeus remains a
public intelligence module and receives these requirements from Buffett for
this workflow.

Zeus must read:
- `00_metadata.md`
- `01_buffett_review.md`
- `02_buffett_plan.md`

Zeus must run mandatory Python CLI tools before writing the report:
- `python3 workspace/intelligence/cli.py indicators --symbols {symbols} --benchmark SPY --market-data-dir {run_dir}/market_data`
- `python3 workspace/intelligence/cli.py quality --symbols {symbols} --market-data-dir {run_dir}/market_data`
- `python3 workspace/intelligence/cli.py sector-map --symbols {symbols}`

If `{run_dir}/market_data` exists and contains CSV files from the pre-fetch,
Zeus may use `--market-data-dir` only when the CSV files were produced from
financeBusiness for the same run. If the directory is missing, empty, stale, or
not provably financeBusiness-backed, Zeus must not allow the CLI to fetch live
non-financeBusiness sources. Zeus must instead call financeBusiness MCP
directly, record the CLI data-source limitation, and mark any CLI-only fields
that cannot be computed from financeBusiness as gaps.

Minimum content:
- Buffett plan compliance table for all Zeus-assigned items
- market data and timestamps, including latest prices needed to calculate current total and per-position P&L
- news, filings, announcements, policy, sentiment, key-person remarks, and
  event evidence from aiwebsearch/news/web/PDF sources, with financeBusiness
  timestamps for market-data rows; if the allowed news/web sources cannot
  support a claim, mark an explicit evidence gap
- source table with financeBusiness tool names, timestamps, and returned
  market-source fields
- data conflicts and financeBusiness current/history reconciliation checks,
  with explicit flags for quote conflicts that would materially change P&L,
  position concentration, or trade sizing
- AI supply-chain intelligence when relevant
- swing raw tape evidence when relevant: current price, close, previous close,
  open, high, low, change amount, percent change, amplitude, volume, amount,
  volume ratio or relative volume, turnover rate, market source, 5/10/20-day
  moving-average position when available, 20-day range, recent 5-day move,
  relative strength versus SPY/QQQ and the relevant sector ETF, and timestamped
  catalyst evidence for memory/HBM or other strong-cycle candidates. If a
  source lacks amount, volume ratio, or turnover rate, Zeus must state whether
  the field is estimated from OHLCV or unavailable.
- sector intelligence when relevant: sector breadth, relative strength, fund-flow proxies, policy/regulatory signals, inventory/pricing data, earnings-revision signals, and direct/indirect beneficiary map
- raw inputs for scorecards when relevant: relative strength, breadth, earnings
  revision evidence, pricing/inventory/capacity, catalyst timestamps, valuation
  context, crowding/liquidity proxies, and policy/geopolitical facts
- anti-miss evidence when relevant: fast-moving sector signals, confirmation
  levels, alternative basket/proxy instruments, liquidity, gap risk, and whether
  current price has outrun the buy zone
- key findings for Poseidon and Hades
- key-person remarks and key-event backfill table: person/event, time, source
  tier, core statement/fact, impact chain, affected assets/sectors, observable
  market reaction, confidence, counter-evidence, and unresolved data gaps

### 04_poseidon_research.md

This phase must use the public Poseidon skill at
`.codex/skills/poseidon/SKILL.md`. The checklist below is Buffett's workflow
handoff contract; Poseidon remains a public research module and receives these
requirements from Buffett for this workflow.

Poseidon must read:
- `00_metadata.md`
- `01_buffett_review.md`
- `02_buffett_plan.md`
- `03_zeus_intelligence.md`

Poseidon must run mandatory Python CLI tools before writing the report:
- `python3 workspace/analysis/cli.py pnl --portfolio-file base_short.md --prices {price_pairs}` for portfolio P&L
- `python3 workspace/analysis/cli.py score-sector --factors {factors} --sector {sector}` for sector scoring
- `python3 workspace/analysis/cli.py score-stock --factors {factors} --sector {sector} --symbol {candidate_symbol}` for stock scoring
- `python3 workspace/analysis/cli.py score-short-term --factors {factors} --symbol {symbol}` for swing setup scoring
- `python3 workspace/analysis/cli.py rr --entry {entry} --stop {stop} --target {target1} --target-2 {target2} --symbol {symbol}` for fee-adjusted R/R
- `python3 workspace/analysis/cli.py sizing --equity {equity} --entry {entry} --stop {stop} --risk-pct {pct}` for position sizing
- `python3 workspace/analysis/cli.py veto-check --factors {factors} --checks {checks}` for veto condition checks
- `python3 workspace/analysis/cli.py post-trade --portfolio-file base_short.md --prices {prices} --trades {trades}` for post-trade P&L projection

Factor values must be evidence-based, not arbitrary defaults. Each score must be
traceable to Zeus intelligence or other sourced evidence.

Minimum content:
- Buffett plan compliance table for all Poseidon-assigned items
- current P&L and position implications section: use the total and per-position P&L from `01_buffett_review.md` when judging risk budget, trims, holds, stop-losses, profit protection, and whether to avoid the averaging-down trap
- thesis and counter-thesis
- valuation, moat, growth, macro, quant, and risk analysis
- swing execution view and long-term background
- position-sizing implications
- AI supply-chain profit-pool judgment when relevant
- explicit response to Buffett review lessons and Zeus data conflicts
- analysis-error attribution: identify whether prior or proposed conclusions
  suffered from missed key-person remarks, missed key events, long-term thesis
  substituted for swing setup, over-conservative "up too much" veto, missing
  financeBusiness reconciliation checks, missing fee-adjusted R/R, missing hard
  stop/take-profit, or over-focusing on losers while missing stronger
  opportunities
- strategy reset: translate `基于反思的新策略` into sector map, AI-chain funnel,
  candidate tiers, starter/add ladder, stop/take-profit plan, no-chase rule,
  and current-session BUY/SELL/no-trade recommendation
- for sector and stock-picking tasks: sector ranking, candidate funnel, stock tiers, direct versus indirect beneficiary classification, profit-pool ownership, relative valuation, timing quality, and final ranking logic
- for scorecard tasks: fill the sector scorecard and stock scorecard from
  `references/sector-stock-playbook.md`; explain each material score and avoid
  false precision when data quality is weak
- for actionable tasks: include positive expected value logic, profit path,
  upside/downside range, starter/add/trim/exit plan, no-chase rule, and what to
  do if the stock moves before entry

### 05_hades_verification.md

This phase must use the public Hades skill at
`.codex/skills/hades/SKILL.md`. The checklist below is Buffett's workflow
handoff contract; Hades remains a public verification module and receives these
requirements from Buffett for this workflow.

Hades must read:
- `00_metadata.md`
- `01_buffett_review.md`
- `02_buffett_plan.md`
- `03_zeus_intelligence.md`
- `04_poseidon_research.md`

Hades must run mandatory Python CLI tools before writing the report:
- `python3 workspace/verification/cli.py audit-pnl --portfolio-file base_short.md --prices {prices}` for P&L audit
- `python3 workspace/verification/cli.py stress-test --portfolio-file base_short.md --prices {prices}` for stress scenarios
- `python3 workspace/verification/cli.py compliance --portfolio-file base_short.md --prices {prices} --trades {trades} --stops {stops}` for compliance checks
- `python3 workspace/verification/cli.py audit-post-trade --portfolio-file base_short.md --prices {prices} --trades {trades}` for post-trade P&L audit

Hades must cross-check Poseidon's post-trade P&L against the independent
`audit-post-trade` output. If the two disagree, Hades must flag the discrepancy
in the report and require roundtable resolution.

Minimum content:
- Buffett plan compliance table for all Hades-assigned audit items
- P&L calculation and usage audit: verify total/per-position P&L math, quote freshness, and whether Zeus/Poseidon used P&L information correctly rather than mechanically selling losers or averaging down losers
- data quality audit
- source sufficiency and freshness audit
- omission and analysis-error audit: verify whether Zeus filled missed
  key-person remarks and key events, whether Poseidon corrected key analytical
  mistakes, and whether unresolved omissions require confidence downgrade,
  additional evidence collection, waiting, or outright veto
- stress tests and adverse scenarios
- research conclusion audit
- compliance and position-limit audit
- unresolved issues and veto conditions
- independent recommendation to Buffett
- for sector and stock-picking tasks: ranking audit, crowding/consensus-risk audit, liquidity audit, valuation downside audit, and check whether any candidate is only a narrative beneficiary
- for scorecard tasks: audit whether the sector/stock scores are supported by
  evidence, whether any veto overrides a high score, and whether proposed sizing
  fits liquidity, volatility, correlation, and the 25% single-stock cap
- for profit/anti-miss tasks: audit any claim that resembles guaranteed profit,
  whether expected value remains positive after downside and slippage, and
  whether the anti-miss plan is disciplined rather than FOMO chasing

### 06_roundtable.md

Buffett convenes the roundtable only after the review, plan, intelligence, research, and verification files exist.

Minimum content:
- participants: Buffett, Zeus, Poseidon, Hades
- exact input files read, including `02_buffett_plan.md`
- roundtable plan-compliance table covering every item Buffett assigned to the roundtable
- previous-decision review summary
- Buffett self-reflection ruling: decide whether `Buffett 自我反思`,
  `关键遗漏与分析错误复盘`, and `基于反思的新策略` are valid, whether missed
  key-person remarks/events or key analytical mistakes remain unresolved, and
  whether they change current BUY/SELL/no-trade action
- current total and per-position P&L discussion, including which losses are thesis/risk problems, which losses are tolerable timing issues, which gains need protection, and how P&L changes current-session trade priority
- Zeus facts
- Poseidon investment case
- Hades audit and objections
- multi-round Q&A record
- resolved and unresolved disagreements
- final roundtable consensus or disagreement
- decision constraints passed to `07_final_decision.md`
- for sector and stock-picking tasks: final sector view, ranked candidate tiers, rejected names and reasons, timing/sizing debate, and the strongest counterargument to the selected names
- scorecard reconciliation when relevant: where Zeus facts, Poseidon ranking,
  and Hades audit disagree; Buffett must rule whether to keep, lower, or veto
  each actionable candidate
- profit and anti-miss ruling when relevant: Buffett must decide whether the
  plan participates enough to avoid missing the move, whether it still preserves
  margin of safety, and what price/catalyst forces waiting instead of chasing

The roundtable must be substantive. For full decisions, use at least three rounds:
1. fact calibration
2. investment thesis and sizing
3. verification objections and Buffett ruling

Add more rounds when data gaps, valuation disagreement, high volatility, AI supply-chain uncertainty, geopolitical risk, or Hades veto conditions exist.

### 07_final_decision.md

Buffett writes the advisory final decision after the roundtable.

Minimum content:
- action: BUY, SELL, HOLD, REBALANCE, WATCH, or NO_DECISION
- dedicated `## 当前持仓盈亏复盘` section before the current-action section, showing total US holding market value, total cost, total unrealized P&L amount, total unrealized P&L %, and a per-stock/ETF table with current price, cost price, shares, market value, cost amount, unrealized P&L amount, and unrealized P&L %
- explicit explanation of how the P&L facts affect the current decision: why any losing position is trimmed/held/not averaged down, why any winning position is held/trimmed/not chased, and how total portfolio drawdown or gain changes risk budget
- dedicated `## 交易后预计盈亏` section after the current-action section. Assume every current BUY/SELL fills at the stated limit price and each trade incurs the fixed USD 5 fee. The section must show pre-trade US cash, each trade's cash change, post-trade US cash, every SELL's sold cost basis and fee-adjusted realized P&L, every BUY's fee-inclusive cash use and initial cost basis, post-trade remaining shares, remaining cost basis, estimated market value, remaining unrealized P&L amount and percentage, total remaining unrealized P&L, current-trade realized P&L, realized plus unrealized total P&L, and estimated post-trade portfolio equity.
- if exact tax lots or operation records are insufficient, use average cost for the post-trade P&L projection and state that assumption; if even average cost is unavailable, mark the affected P&L as unreliable and do not present it as exact
- strategy type: short_term, swing, long_term, or blended
- recommended position and maximum position
- entry/add/trim/exit plan
- stop-loss or invalidation conditions
- expected outcome and review trigger
- key assumptions
- risks and Hades veto conditions
- local file path map
- `SQLite 写入：skipped_by_disabled_policy`
- `local_result_snapshot.json` path and snapshot status
- profit path, positive expected value rationale, downside if wrong, and missed-
  opportunity control plan; do not state or imply guaranteed profit

For sector and stock-picking tasks, also include:

- sector conclusion: overweight, neutral, underweight, tactical-only, or avoid
- stock tiers: `核心候选`, `战术候选`, `观察名单`, `回避/否决`
- ranking table with ticker/name, market, sector role, directness of benefit, moat, valuation, timing, key risk, and recommended action
- buy-zone, add-zone, trim-zone, and invalidation conditions for any actionable candidate
- one paragraph explaining why the selected stock is the best expression of the sector thesis
- sector scorecard, stock scorecard, Hades veto status, and position table when
  the user asked for selection, ranking, or an actionable decision
- profit/anti-miss table from `references/sector-stock-playbook.md`

## Local Result Snapshot

Buffett no longer writes new results to SQLite.

Storage contract:

- The task folder under `report/` is the canonical decision journal.
- SQLite at `workspace/journal/decisions.sqlite3` is legacy read-only context
  only. If used, query it only through `workspace/journal/decision_db.py last`
  and label the result as a secondary cross-check.
- Do not run `workspace/journal/decision_db.py review`,
  `workspace/journal/decision_db.py record`, or direct SQL writes.
- Do not modify `workspace/journal/decisions.sqlite3`.
- After Chinese `06_roundtable.md` and `07_final_decision.md` are complete,
  create `local_result_snapshot.json` in the task folder.
- New Buffett workflows must not create `db_record.json`; read legacy
  `db_record.json` only when reviewing old folders that already contain it.

Before the new decision, unless the user explicitly told Buffett not to read history, review local Markdown first:

```text
1. Scan compliant `report/record_*` folders for the same task. A compliant
   record folder has complete `00-07` phase files, `local_result_snapshot.json`,
   and no `db_record.json`.
2. If no compliant record-format folder exists, scan complete legacy
   `report/YYYY-MM-DD_*` folders.
3. Read the previous folder's `00_metadata.md`, `01_buffett_review.md`,
   `06_roundtable.md`, `07_final_decision.md`, and
   `local_result_snapshot.json` when present. If the folder is legacy and only
   has `db_record.json`, read it as historical context.
4. Treat this local folder as the primary historical decision source.
5. Do not treat noncompliant new-format record folders as the primary previous
   decision; mention them only as a legacy-data-quality warning when relevant.
```

SQLite lookup is optional secondary read-only cross-check and must be labeled secondary:

```bash
python3 workspace/journal/decision_db.py last --task-type {task_type} --subject {subject} --symbols {symbols}
```

After Chinese `06_roundtable.md` and `07_final_decision.md` are complete,
create `local_result_snapshot.json`. It must include:

- `task_key`, `task_type`, `subject`, `market`, and sorted `symbols`
- `task_folder`
- `source_doc_ids_json`: a JSON array of local Chinese Markdown paths under `report/`
- `source_links_json`: evidence URLs, filing links, source names, or local source attachment paths
- `action` and `strategy_type`
- `thesis`, `roundtable_summary`, `roundtable_english`,
  `final_decision_english`, and `review_summary` in English
- `recommendation_json`, `expected_outcome_json`, and `actual_result_json`
  as valid JSON objects or JSON strings with stable English keys
- `sqlite_write_status`: `skipped_by_disabled_policy`
- `sqlite_write_mode`: `disabled`
- `created_at` or `decision_date`

`roundtable_summary` must summarize the final roundtable in English, including major objections and Buffett's ruling. `roundtable_english` must store the full English version of the final roundtable minutes. `final_decision_english` must store the full English version of Buffett's final decision. `source_doc_ids_json` stores local Chinese Markdown paths, not external document IDs.

For actionable sector/stock-picking records, `recommendation_json` and
`expected_outcome_json` should include English fields for `profit_path`,
`base_upside`, `downside_if_wrong`, `positive_expected_value_rationale`,
`anti_miss_plan`, `no_chase_rule`, and `review_trigger` when the data supports
them. Do not store guaranteed-profit claims.

Recommended English JSON shape for sector/stock-picking decisions:

```json
{
  "sector_rating": "overweight|tactical_overweight|neutral_watch|underweight|avoid",
  "stock_tiers": {
    "core_candidates": [],
    "tactical_candidates": [],
    "watchlist": [],
    "avoid_or_veto": []
  },
  "position_plan": [],
  "profit_path": "",
  "base_upside": "",
  "downside_if_wrong": "",
  "positive_expected_value_rationale": "",
  "anti_miss_plan": "",
  "no_chase_rule": "",
  "veto_status": "",
  "review_trigger": ""
}
```

The final `07_final_decision.md` must include `SQLite 写入：skipped_by_disabled_policy`.

## Data Priority

- Structured market data for Buffett workflows must come from financeBusiness
  MCP: market data, price facts, historical bars, index/ETF proxies, FX,
  volume, turnover, P&L inputs, valuation price inputs, sector/plate market
  context, and current trade numeric fields. Do not use akshare, AKTools,
  Yahoo Finance, yfinance, Alpha Vantage, FRED, Stooq, exchange pages, web
  search, PDF extraction, CSV caches, or local live-data adapters as
  substitutes or external validators for those structured market fields.
- For `buffett开始` and any US-equity current trade decision, the Zeus
  assignment must require both `mcp__financeBusiness__StockCurrentMarket` and
  `mcp__financeBusiness__StockMarketList` for every holding, core candidate,
  top candidate, and ETF/basket fallback in scope. Required fields cannot be
  omitted: current price, close, previous close, open, high, low, percent
  change, change amount, amplitude, volume, amount, volume ratio, turnover
  rate, and market source. If any required field remains missing after
  financeBusiness calls, the symbol must be marked `ZEUS_FIELD_FAILURE` and
  cannot be used for a final current BUY/SELL action.
- Broad-market indexes and tradable ETF proxies must be modeled separately.
  Nasdaq Composite `IXIC` and any S&P 500 index-code candidates are
  non-tradable regime evidence fetched through financeBusiness
  `StockIndexList`; `QQQ` and `SPY` are the tradable ETF proxies that can enter
  current BUY/SELL review. If S&P 500 index-code candidates are unavailable in
  financeBusiness, record the index gap and continue the `SPY` proxy review.
- For `SPY` and `QQQ`, missing `turnover_rate` or source `volumeRatio` is not
  automatically a hard veto when financeBusiness history can compute an
  equivalent volume signal. Mark the field as estimated/non-blocking, and let
  Hades decide whether any remaining volume-history gap blocks action.
- Current swing-trading tasks must require Zeus to provide the same
  current-strategy field pack defined in `.codex/skills/zeus/SKILL.md`,
  including basic tape, `ma5/ma10/ma20`, 20-day range, 1/5/10/20-day returns,
  `atr_14`, `volatility_20d`, relative strength versus SPY/QQQ/SMH/SOXX,
  execution evidence handoff fields, and data-quality fields such as
  `field_source_map`, `field_timestamp_map`, `zeus_field_status`, and
  `usable_for_current_trade`. These technical and relative-strength fields may
  be computed only from financeBusiness `StockMarketList` history and
  financeBusiness quotes for benchmark/proxy symbols. If financeBusiness
  history is insufficient, mark the field missing; do not fill it from another
  provider.
- News, filings, announcements, management remarks, macro/policy facts,
  sentiment, webpages, PDF extraction, event evidence, and counter-evidence
  must be refreshed from news/web sources unless the user explicitly requests a
  financeBusiness-only run. Use aiwebsearch MCP first
  (`mcp__aiwebsearch__GoogleSearch`, `mcp__aiwebsearch__searchJumps`,
  `mcp__aiwebsearch__real_time_pdf_download`), then official/company/regulatory
  pages and compatible WebSearch/PDF extraction as fallback when aiwebsearch is
  unavailable or insufficient. `searchJumps` must receive URL object arrays,
  e.g. `{"cache": false, "urls": [{"url": "https://example.com"}]}`.
- Plate/sector event attribution must pair financeBusiness market/index/ETF
  context with aiwebsearch/news evidence for the event chain. Do not require a
  dedicated plate-event MCP. If event evidence cannot be found from the allowed
  news/web sources, mark the gap and reduce confidence.
- Do not use news/web/PDF sources to fill missing financeBusiness price,
  volume, FX, valuation-price, P&L, or current-trade sizing fields. News quotes
  about prices are context only; the tradeable numeric field still comes from
  financeBusiness reconciliation.
- Cross-check investment-critical prices and valuation inputs only by internal
  financeBusiness reconciliation, especially `StockCurrentMarket` versus
  `StockMarketList` latest history. If the two disagree materially, mark a
  data conflict and do not use the symbol for a current BUY/SELL action until
  the conflict is resolved inside financeBusiness.
- If financeBusiness MCP tools are unavailable, empty, stale, or missing
  required fields, do not substitute another source. Clearly label the gap, set
  affected rows to `ZEUS_FIELD_FAILURE` or `usable_for_current_trade = false`,
  and force `本次不买入、不卖出` for any action that depends on the missing fact.
- Never use one unreconciled financeBusiness quote or unsupported headline for
  valuation, position sizing, or final investment recommendations.

## AI Supply Chain Requirements

For the exact trigger `buffett开始`, AI supply-chain work is mandatory, not
optional. The workflow must include a US-equity sector map and an AI opportunity
funnel before the final portfolio action. The funnel must look for opportunities
outside the current holdings as well as inside them, while keeping all trade
recommendations US-equity-only.

For AI-related analysis, identify:
- supply-chain position
- direct versus indirect benefit
- profit-pool ownership
- pricing power
- order visibility
- inventory and capacity
- customer concentration
- export controls
- technology substitution risks

PCB, memory/HBM, semiconductors, advanced packaging, optical modules, AI servers, data centers, cloud CAPEX, and AI applications must receive separate swing execution judgments and long-term background when relevant.

The AI opportunity funnel should cover, where relevant:
- AI applications and software
- cloud CAPEX and hyperscalers
- GPU/ASIC and accelerators
- semiconductors and semiconductor equipment
- memory/HBM
- advanced packaging
- optical modules, networking, and interconnect
- AI servers and ODM/server supply chain
- data centers, power, cooling, and infrastructure
- PCB/CCL
- equipment, materials, and components
- cybersecurity, data infrastructure, and observability

Rank candidates into core candidates, tactical candidates, watchlist names, and
avoid/veto names. The final `本次当前操作` section still lists only trades to
execute in the current session.

## Safety

- Investment outputs are advisory only.
- Single-stock maximum position: 25% of total capital.
- API keys must come from environment variables, never source files.
- Local Markdown files and `local_result_snapshot.json` are the audit trail;
  SQLite is read-only legacy context.
- Do not upload private holdings or reports to external document services.
