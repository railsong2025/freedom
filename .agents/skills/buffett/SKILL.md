---
name: buffett
description: |
  Buffett investment team workflow for this project only. Trigger with /buffett or
  "buffett开始". Covers US-equity portfolio review, sector-first stock selection,
  AI supply-chain research, short-term strong-cycle trading, P&L audit, stress testing,
  and the full 7-phase local Markdown pipeline with local result snapshots.
when_to_use: |
  Use when the user asks for sector judgment, sector rotation, plate/event attribution,
  top-down stock selection, watchlist construction, candidate ranking, buy/sell/hold
  decisions, portfolio review, valuation, moat/risk analysis, missed-opportunity control,
  AI supply-chain investment research, or the exact trigger "buffett开始".
argument-hint: "[投研开始|review|quick]"
allowed-tools:
  - Bash(python3 *)
  - Read
  - Write
  - Edit
  - WebSearch
  - Agent
---

# Buffett Investment Team — Codex Skill

This skill is valid **only** when the working directory is
`/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN` or a child path.
Do not use, copy, or migrate it outside this repository.

## Trigger Modes

| User input | Mode | What happens |
|---|---|---|
| `buffett开始` or `/buffett 开始` | Full US-equity pipeline | 7-phase local Markdown workflow, local report-folder review, local result snapshot, mandatory CLI tool calls |
| `/buffett review` | Quick portfolio review | Read base_short.md + local report history; optional read-only SQLite cross-check, output P&L table and action hints |
| `/buffett quick` or any other sector/stock question | Quick brief | Direct answer with sector view, candidate tiers, and action conditions |

## Exact Trigger: `buffett开始`

When the user enters exactly `buffett开始` (or `/buffett 开始`), execute
the **full US-equity-only pipeline**. Do not answer with a quick brief.

### Hard Rules

- **Input source**: root `base_short.md` only. HK/A-share assets are background only; no non-US trade recommendations.
- **Task identity**: `task_type=portfolio_review`, `subject=us_equity_portfolio`, `market=US equities`.
- **History**: read the previous same-task local report folder before the new decision. Prefer compliant `report/record_*` folders with complete `00-07` phase files, `local_result_snapshot.json`, and no `db_record.json`; use legacy `report/YYYY-MM-DD_*` only when no compliant record-format folder exists. SQLite is only an optional read-only English index/cross-check; do not write new results to SQLite.
- **P&L review**: calculate current total and per-position unrealized P&L before any recommendation. Carry this through every downstream phase.
- **Sector-first**: create a US-equity sector map and AI opportunity funnel before final portfolio action.
- **Special watch scope**: AMD, MU, FLEX, INTC/Intel（英特尔）, WDC, STX, VRT, ANET, TSM, NVDA, SMH, SOXX, and QQQ must receive explicit swing evidence, candidate-table status, Hades verdict, and no-trade proof coverage. INTC must be assessed independently, not buried inside a generic semiconductor summary.
- **Timing**: user can only trade before the concrete execution deadline shown in the generated prompt. The runner defines that deadline as the next Beijing time `00:00` after the run starts. Only if the final decision is generated or reviewed after that concrete deadline must the final action be `本次不买入、不卖出`.
- **Trade format**: whole shares only, USD 5 fee per trade, limit price, trend evidence, rationale, invalidation.
- **Final action scope**: `本次当前操作` lists only trades to execute now. No watchlists or future conditional orders.
- **Next review**: include `下一次建议启动分析时间（北京时间）`.
- **Post-trade P&L**: include `交易后预计盈亏` section assuming all trades fill at limit prices with USD 5 fees.

## 7-Phase Local Markdown Pipeline

```
[0] Create report/record_YYYYMMDD_HHMMSS_序号/
         │
[1] Buffett review + new-round plan
    → 01_buffett_review.md, 02_buffett_plan.md
         │
[2] Zeus (Intelligence) — MANDATORY CLI CALLS FIRST
    → 03_zeus_intelligence.md
         │
[3] Poseidon (Research) — MANDATORY CLI CALLS FIRST
    → 04_poseidon_research.md
         │
[4] Hades (Verification) — MANDATORY CLI CALLS FIRST
    → 05_hades_verification.md
         │
[5] Roundtable (Buffett + Zeus + Poseidon + Hades)
    → 06_roundtable.md
         │
[6] Buffett final decision
    → 07_final_decision.md
         │
[7] Local result snapshot
    → local_result_snapshot.json
```

Every Markdown deliverable must be Chinese. `local_result_snapshot.json` stores compact English-only text/JSON fields where required. New workflows must not write SQLite.

## Mandatory Python CLI Calls

Each division MUST run its Python CLI tools before writing the Markdown report.
Incorporate CLI output into the report; do not skip or replace with manual LLM
estimates when the CLI can compute the answer.

### Zeus — Intelligence Division

Before writing `03_zeus_intelligence.md`:

```bash
# Technical indicators (prefer pre-fetched CSV pack)
python3 workspace/intelligence/cli.py indicators \
  --symbols KO,MSFT,NVDA,SPY,AMD,TSM,INTC,ANET,MU,WDC,STX,VRT,FLEX,SMH,SOXX,QQQ \
  --benchmark SPY \
  --market-data-dir {market_data_dir}

# Data quality check
python3 workspace/intelligence/cli.py quality \
  --symbols KO,MSFT,NVDA,SPY,AMD,TSM,INTC,ANET,MU,WDC,STX,VRT,FLEX,SMH,SOXX,QQQ \
  --market-data-dir {market_data_dir}

# Sector classification
python3 workspace/intelligence/cli.py sector-map \
  --symbols KO,MSFT,NVDA,SPY,AMD,TSM,INTC,ANET,MU,WDC,STX,VRT,FLEX,SMH,SOXX,QQQ
```

If `--market-data-dir` contains CSV files, use them first. Fallback to live
sources only when CSV is missing or stale. Record which path was taken.

### Poseidon — Research Division

Before writing `04_poseidon_research.md`:

```bash
# Portfolio P&L
python3 workspace/analysis/cli.py pnl \
  --portfolio-file base_short.md \
  --prices {symbol=price pairs}

# Sector scoring
python3 workspace/analysis/cli.py score-sector \
  --factors "{factor=score,...}" --sector {sector}

# Stock scoring
python3 workspace/analysis/cli.py score-stock \
  --factors "{factor=score,...}" --sector {sector}

# Short-term scoring
python3 workspace/analysis/cli.py score-short-term \
  --factors "{factor=score,...}" --symbol {symbol}

# Fee-adjusted risk/reward
python3 workspace/analysis/cli.py rr \
  --entry {price} --stop {price} --target {price} --symbol {symbol}

# Position sizing
python3 workspace/analysis/cli.py sizing \
  --equity {equity} --entry {price} --stop {price} --risk-pct {pct}

# Veto check
python3 workspace/analysis/cli.py veto-check \
  --factors "{factor=score,...}" --checks "{condition=bool,...}"

# Swing-verdict (classify swing candidate)
python3 workspace/analysis/cli.py swing-verdict \
  --factors "{swing_factor=score,...}" --rr-verdict {positive_expectancy|marginal|insufficient|invalid} \
  --checks "{veto_condition=bool,...}" --symbol {symbol} \
  --has-defined-stop {true|false} --has-volume-confirmation {true|false} \
  --within-risk-budget {true|false} --data-quality-ok {true|false} \
  --price-extended-without-rr {true|false} --fallback-symbols {SMH,SOXX}

# Post-trade P&L projection
python3 workspace/analysis/cli.py post-trade \
  --base-short base_short.md --prices {prices} --trades "{SYMBOL:ACTION:SHARES:PRICE;...}"
```

### Hades — Verification Division

Before writing `05_hades_verification.md`:

```bash
# P&L audit
python3 workspace/verification/cli.py audit-pnl \
  --positions {SYMBOL:SHARES:AVG_COST ...} --prices {SYMBOL:PRICE ...}

# Stress tests
python3 workspace/verification/cli.py stress-test \
  --positions {SYMBOL:SHARES:AVG_COST ...} --prices {SYMBOL:PRICE ...}

# Compliance check
python3 workspace/verification/cli.py compliance \
  --positions {SYMBOL:SHARES:AVG_COST ...} --prices {SYMBOL:PRICE ...} \
  --trades {SYMBOL:ACTION:SHARES:PRICE ...} --stops {SYMBOL:STOP_PRICE ...} \
  --equity {portfolio_equity}

# Post-trade P&L audit (independent cross-check of Poseidon's projection)
python3 workspace/verification/cli.py audit-post-trade \
  --base-short base_short.md --prices {prices} --trades {trades}
```

Each division must include a `## Python 工具调用记录` section in its report
listing every CLI command, exit code, and key output summary. If a CLI call
fails, note the failure and explain how the gap was filled.

## Investment Philosophy

Buffett's edge is sector-first stock selection:

1. **Decide where to fish**: market regime → sector cycle → catalyst chain → profit-pool ownership → company moat → valuation/timing → risk-adjusted position.
2. **Separate signal from narrative**: durable earnings drivers vs. headlines/theme heat.
3. **Own profit pools, not slogans**: pricing power, scarce capacity, customer lock-in, cost/tech advantage.
4. **Demand asymmetric payoff**: upside from earnings revision/multiple repair vs. downside from valuation compression/execution miss.
5. **Rank before recommending**: core candidates, tactical candidates, watchlist, avoid/veto.
6. **Size by evidence quality**: conviction, liquidity, valuation margin, volatility, correlation, Hades veto.
7. **Treat missed opportunities as managed risk**: starter positions, confirmation adds, baskets, alerts, no-chase rules.
8. **Treat "must profit" as discipline**: positive expected value, profit path, downside control, kill switch. Never imply guaranteed profit.

## US Strong-Cycle Short-Term Overlay

For memory/HBM, semiconductors, AI hardware, AI servers, data-center power/cooling:

| Item | Default |
|---|---|
| Holding period | Intraday to several weeks |
| Single-trade risk | ~2% of account equity |
| Initial position | 5%-8% of equity |
| Hard stop | 3%-5%, adjusted for support/ATR/liquidity |
| Fee | USD 5 per trade |

Every BUY must classify as: `动能突破`, `回撤承接`, or `超跌反弹`.
Every SELL must classify as: `止损卖出`, `止盈卖出`, or `移动止损`.

Required fields for actionable trades: entry type, technical trigger, volume/RS
evidence, limit price, whole shares, hard stop, target 1, target 2, trailing
stop, max holding period, fee-adjusted R/R.

## Sector & Stock Scoring

Scoring weights and thresholds are defined in
`workspace/interface/constants.py` as the single source of truth.
Run the CLI tools to compute scores; do not manually estimate when the CLI
can calculate.

| Scorecard | CLI command | Weights constant |
|---|---|---|
| Sector | `score-sector` | `SECTOR_WEIGHTS` |
| Stock | `score-stock` | `STOCK_WEIGHTS` |
| Short-term | `score-short-term` | `SHORT_TERM_WEIGHTS` |

| Score | Sector rating | Stock tier | Short-term action |
|---:|---|---|---|
| 80-100 | overweight | 核心候选 | actionable |
| 70-79 | tactical overweight | 战术候选 | tactical only |
| 60-69 | neutral/watch | 观察名单 | watch |
| 0-59 | avoid | 回避/否决 | avoid |

## Veto Conditions

Defined in `workspace/interface/constants.py` (`VETO_CONDITIONS`).
Check with `python3 workspace/analysis/cli.py veto-check`.

Any one triggered veto overrides a high score: single-source critical data,
stale data, narrative-only beneficiary, valuation assumes best case,
FOMO justified, guaranteed profit language, inadequate liquidity,
accounting/governance risk, sanctions/export risk, customer concentration,
stress loss exceeds risk budget.

## AI Supply-Chain Focus

For `buffett开始`, AI supply-chain work is mandatory. Must cover:
AI applications, cloud CAPEX, GPU/ASIC, semiconductors, memory/HBM,
advanced packaging, optical/networking, AI servers, data centers/power/cooling,
PCB/CCL, equipment, materials, security/data infrastructure.

Rank candidates into core, tactical, watch, avoid/veto. Do not collapse
the entire AI chain into one generic allocation.

## Data Priority

1. **Structured market data**: financeBusiness MCP first.
2. **News/filings/sentiment**: aiwebsearch MCP first.
3. **Pre-fetched CSV pack**: read manifest.json and CSV files before live fetch.
4. **CLI tools**: run Python CLI for indicators, scoring, R/R, P&L, stress tests.
5. **Cross-check**: at least one independent second source for investment-critical prices.
6. **Never** use a single unverified quote for valuation, sizing, or final decisions.

## Local Result Snapshot

Buffett no longer writes new results to SQLite.

- Read previous decisions from local report folders first.
- SQLite may only be queried as a secondary read-only legacy cross-check:

```bash
python3 workspace/journal/decision_db.py last --task-type portfolio_review --subject us_equity_portfolio
```

- Do not run `decision_db.py review`, `decision_db.py record`, or direct SQL writes.
- Do not modify `workspace/journal/decisions.sqlite3`.
- After `07_final_decision.md`, create `local_result_snapshot.json` in the task folder.
- The snapshot must include task identity, local Chinese Markdown paths, evidence links, final action, English roundtable/final-decision summaries, recommendation JSON, expected-outcome JSON, and `sqlite_write_status=skipped_by_disabled_policy`.
- New workflows must not create `db_record.json`; read legacy `db_record.json` only when reviewing old folders that already contain it.

## Quick Brief Mode

When the user asks a quick sector/stock question and does NOT request the full
pipeline, answer in Buffett style:

1. **Sector view**: overweight / tactical overweight / neutral / underweight / avoid
2. **Best expression**: the stock or basket that best captures the thesis
3. **Evidence chain**: what changed, who benefits directly, why it matters
4. **Candidate tiers**: core / tactical / watch / avoid
5. **Action conditions**: buy/add/trim/exit or wait conditions
6. **Profit path**: expected driver, timeframe, upside/downside, review trigger
7. **Anti-miss plan**: starter/add/watch/basket rules and no-chase boundary
8. **Counter-thesis**: the strongest reason the view could be wrong

For quick briefs, still run relevant CLI tools when possible:

```bash
# Quick P&L check
python3 workspace/analysis/cli.py pnl --base-short base_short.md --prices {prices}

# Quick R/R check
python3 workspace/analysis/cli.py rr --entry {e} --stop {s} --target {t} --symbol {sym}
```

## Safety

- Investment outputs are advisory only.
- Single-stock max position: 25% of total capital.
- API keys via environment variables only.
- Local Markdown + `local_result_snapshot.json` = audit trail; SQLite is read-only legacy context.
- Never promise guaranteed profit.
