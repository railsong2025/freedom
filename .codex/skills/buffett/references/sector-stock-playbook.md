---
name: sector-stock-playbook
description: Buffett sector-first stock selection framework, scoring rules, tiering, vetoes, missed-opportunity controls, profit discipline, and required output tables.
---

# Buffett Sector And Stock Selection Playbook

This reference defines the investment thinking used by the project-local Buffett
skill whenever a task involves sectors, themes, stock picking, watchlists, or
candidate ranking.

## Prime Directive

Do not start with "which stock is popular." Start with "where is the profit pool
moving, who owns it, and what price already discounts it."

Use this chain:

```text
market regime -> sector cycle -> catalyst chain -> profit-pool ownership -> company moat -> valuation/timing -> risk-adjusted position
```

The best answer is not the most bullish answer. The best answer is the one that
separates durable earnings power from temporary narrative heat, then sizes the
opportunity according to evidence quality and downside.

## Profit And Missed-Opportunity Discipline

"Do not miss out" is a real portfolio risk, but it is not permission to chase.
"Must profit" means every actionable recommendation must have a positive expected
value path, explicit downside control, and a review trigger. It must never be
written as a guaranteed return.

Apply these rules:

- No guaranteed-profit language. Use probability, expected value, upside/downside
  ranges, and invalidation conditions.
- No trade without a profit path: name the expected driver of profit, the likely
  timeframe, the catalyst that confirms it, and the data that would disprove it.
- No all-or-nothing entry when timing risk is high. Use starter positions,
  confirmation adds, basket/ETF exposure, or alerts to reduce missed-opportunity
  risk without abandoning valuation discipline.
- No FOMO chase. If price has already moved beyond the buy zone, mark it
  `wait`, `tactical only`, or `watch`, then define the next actionable setup.
- No capital freeze. When a sector is strong but no single stock has enough
  margin of safety, use a watchlist, staged trigger plan, or diversified basket
  rather than pretending certainty.
- No thesis without a kill switch. Every position needs an exit/invalidation
  level tied to fundamentals, price action, catalyst failure, or risk budget.

## Strong-Cycle Short-Term Trading Overlay

For US memory/HBM, semiconductors, AI hardware, AI servers, data-center
power/cooling, storage, and other high-beta cyclicals, use a dedicated swing
overlay on top of the sector-first framework. The goal is not to prove a company
is good for years; the goal is to decide whether the current tape offers a
fee-adjusted positive-expectancy trade with a hard exit.

Default profile:

| Item | Default |
|---|---|
| Holding period | Several days to several weeks |
| Risk posture | Swing trading |
| Single-trade account risk | About 2% maximum unless Hades lowers it |
| Initial strong-cycle single-name exposure | Usually 5%-8% of estimated equity |
| Hard stop distance | Usually 3%-5%, adjusted for support, ATR, volatility and liquidity |
| Required trade types | `动能突破`, `回撤承接`, `超跌反弹`, `止损卖出`, `止盈卖出`, `移动止损` |

Swing setup scorecard, 0-100. The canonical factor weights and action thresholds
are defined in `workspace/interface/constants.py` (`SHORT_TERM_WEIGHTS`,
`SHORT_TERM_THRESHOLDS`). That file is the single source of truth.

Current weights from `constants.py` (do not edit here):

| Factor | Weight | What To Check |
|---|---:|---|
| Sector/theme heat | 15 | Strong-cycle group leadership, news catalyst, ETF confirmation |
| Relative strength | 15 | Stock vs SPY/QQQ and sector ETF such as SMH/SOXX |
| Volume and liquidity | 15 | Volume ratio, dollar volume, spread, ability to exit |
| Technical setup quality | 20 | Breakout, pullback support, reclaim, VWAP/MA structure, clean invalidation |
| Catalyst freshness | 10 | Earnings, guidance, price hikes, supply squeeze, policy or order evidence |
| Fee-adjusted risk/reward | 15 | Upside to target vs stop loss plus USD 5 fee and expected slippage |
| Crowding and reversal risk | 10 | Gap risk, vertical extension, crowded retail/option flow, failed breakout risk |

Swing setup action thresholds from `constants.py` (`SHORT_TERM_THRESHOLDS`):

| Score | Bias | Meaning |
|---:|---|---|
| 80-100 | Current actionable | May enter if Hades approves risk, stop, fees and timing |
| 70-79 | Tactical only | Smaller size or wait for cleaner trigger |
| 60-69 | Watch | Setup is plausible but not executable yet |
| 0-59 | Avoid/veto | No current trade |

Swing verdict contract:

- Use `python3 workspace/analysis/cli.py swing-verdict` or the equivalent
  `decide_swing_trade_verdict()` logic before turning a strong-cycle candidate
  into current action, starter, wait, or veto.
- Verdicts must be one of `current_trade`, `small_starter`, `wait`, or
  `hard_veto`. Reports may translate these into Chinese, but must keep the
  state distinction visible.
- A stock being up strongly is not by itself FOMO. Treat strength as a possible
  `动能突破` if volume/relative strength, defined stop, and fee-adjusted R/R
  pass. Mark it FOMO only when the price has moved beyond the buy zone enough
  to make R/R negative, the stop cannot be defined, volume/relative strength is
  unverified, or gap/chase conditions make the first target inadequate.
- If all single-name leaders fail because of data quality or source conflicts,
  review ETF or basket substitutes such as SMH/SOXX/QQQ before declaring
  no-trade.
- A no-trade conclusion in an open trading window must prove why each core
  candidate, tactical candidate, and ETF/basket substitute failed the verdict
  test. Generic "do not chase" wording is not enough.

Every actionable swing candidate must include:

| Ticker | Trade Type | Limit | Stop | Target 1 | Target 2 | Trailing Stop | Max Hold | Size | Risk $ | Fee-Adjusted R/R |
|---|---|---:|---:|---:|---:|---|---|---:|---:|---:|

Strong-cycle vetoes:

- Missing hard stop or undefined holding period.
- Trade justified mainly by being a hot ticker rather than a verified setup.
- First target does not compensate for the stop, fee and likely slippage.
- Volume/relative-strength signal is absent or unverified.
- Position would risk more than the approved account risk budget.
- The plan allows a failed swing trade to become a long-term bag hold.
- Entry occurs after a vertical move without a pullback, base, or confirmation
  add rule.

## Decision Modes

Use the smallest mode that satisfies the user:

| Mode | Use When | Output |
|---|---|---|
| Quick brief | User asks a narrow quote, quick view, or one catalyst check | Direct answer with sources, no full roundtable unless requested |
| Sector review | User asks sector direction, rotation, or market/industry judgment | Sector scorecard, sector rating, leading/lagging groups, key catalysts |
| Stock-picking funnel | User asks what to buy, watch, screen, or rank inside a sector/theme | Sector view plus ranked stock tiers and action conditions |
| Full decision | User asks for complete buy/sell/hold, sizing, portfolio action, or durable recommendation | Full local Markdown pipeline, local result snapshot, roundtable, final decision |

## Sector Scorecard

Score sectors from 0 to 100. Use exact numbers only when data quality supports
them; otherwise use a score range and explain the uncertainty.

The canonical factor weights and rating thresholds are defined in
`workspace/interface/constants.py` (`SECTOR_WEIGHTS`, `SECTOR_RATING_THRESHOLDS`).
That file is the single source of truth. Do not redefine weights here; if a
weight must change, update `constants.py` and regenerate this section.

Current weights from `constants.py` (do not edit here):

| Factor | Weight | What To Check |
|---|---:|---|
| Market regime fit | 10 | Liquidity, rates, risk appetite, style factor, macro cycle |
| Relative strength and breadth | 15 | Sector versus index, participation, volume, new highs/lows |
| Earnings revision direction | 15 | Consensus revision, margins, guidance, order visibility |
| Supply-demand and pricing | 15 | Capacity, inventory, pricing power, utilization, backlog |
| Catalyst quality | 15 | Directness, freshness, duration, measurable impact, repeatability |
| Valuation and expectations | 10 | Historical range, relative multiple, implied growth, sentiment |
| Capital flow and crowding | 10 | Fund flows, positioning, ownership concentration, hot-money risk |
| Policy/geopolitical risk | 10 | Regulation, sanctions, trade policy, subsidy durability, event risk |

Sector rating thresholds from `constants.py` (`SECTOR_RATING_THRESHOLDS`):

| Score | Rating | Meaning |
|---:|---|---|
| 80-100 | overweight | Strong sector, direct profit-pool shift, acceptable valuation/risk |
| 70-79 | tactical overweight | Tradable but needs tighter timing and smaller size |
| 60-69 | neutral/watch | Evidence incomplete or valuation already discounts much of the move |
| 45-59 | underweight | Weak risk/reward or mostly narrative |
| 0-44 | avoid | Poor evidence, hostile cycle, or veto risk |

## Stock Scorecard

Score stocks from 0 to 100 inside the selected sector/theme.

The canonical factor weights and tier thresholds are defined in
`workspace/interface/constants.py` (`STOCK_WEIGHTS`, `STOCK_TIER_THRESHOLDS`).
That file is the single source of truth. Do not redefine weights here.

Current weights from `constants.py` (do not edit here):

| Factor | Weight | What To Check |
|---|---:|---|
| Direct beneficiary status | 15 | Revenue/profit exposure to the sector thesis, not just label exposure |
| Moat and profit-pool ownership | 15 | Pricing power, scarcity, customer lock-in, cost/tech/channel advantage |
| Earnings visibility | 15 | Backlog, guidance, margins, utilization, contract quality, revision path |
| Valuation and margin of safety | 15 | Absolute/relative valuation, implied assumptions, downside case |
| Balance sheet and cash conversion | 10 | Leverage, liquidity, working capital, FCF, dilution risk |
| Catalyst and timing | 10 | Upcoming events, confirmation signals, invalidation speed |
| Liquidity and technical quality | 10 | Volume, trend, volatility, support/resistance, institutional access |
| Risk concentration | 10 | Customer, policy, geography, accounting, governance, substitution |

Stock tier thresholds from `constants.py` (`STOCK_TIER_THRESHOLDS`):

| Score | Tier | Action Bias |
|---:|---|---|
| 80-100 | 核心候选 | Best expression of the sector thesis; actionable if valuation and timing pass |
| 70-79 | 战术候选 | Tradable or smaller position; needs clearer catalyst or tighter risk control |
| 60-69 | 观察名单 | Monitor for price, data, or catalyst improvement |
| 0-59 | 回避/否决 | Avoid, or use only as comparison evidence |

## Veto Conditions

Any one veto can override a high score. The canonical veto condition names are
defined in `workspace/interface/constants.py` (`VETO_CONDITIONS`). That file is
the single source of truth. The Python veto checker is
`workspace/analysis/sector_scoring.py check_veto()`.

Current veto conditions from `constants.py` (do not edit here):

- single_source_critical_data: Critical price, valuation, or catalyst relies on one unverified source.
- stale_data: Data is stale for the decision horizon or timestamp is missing.
- narrative_only_beneficiary: The company is only a narrative beneficiary with no direct earnings channel.
- valuation_assumes_best_case: Valuation already assumes a best-case outcome while downside is not protected.
- fomo_justified: The recommendation is justified mainly by fear of missing out rather than positive expected value and defined risk.
- guaranteed_profit_language: The report implies certain profit, guaranteed return, or risk-free entry.
- inadequate_liquidity: Liquidity is inadequate for the proposed position size or exit plan.
- accounting_governance_risk: Accounting, governance, related-party, fraud, or auditor risk is unresolved.
- sanctions_export_risk: Sanctions, export controls, license risk, or regulatory reversal can break the thesis.
- customer_concentration: Customer concentration, inventory glut, or capacity oversupply can destroy pricing.
- stress_loss_exceeds_risk_budget: Hades identifies a stress scenario where loss exceeds the intended risk budget.

## Required Tables

For sector tasks, include:

| Sector/Theme | Score | Rating | Cycle Phase | Key Catalyst | Profit-Pool Direction | Main Risk | Action |
|---|---:|---|---|---|---|---|---|

For stock-picking tasks, include:

| Tier | Ticker/Name | Market | Role In Thesis | Directness | Score | Valuation View | Timing | Key Risk | Action |
|---|---|---|---|---|---:|---|---|---|---|

For actionable names, include:

| Ticker/Name | Initial Position | Max Position | Buy Zone | Add Trigger | Trim Trigger | Exit/Inval. | Review Trigger |
|---|---:|---:|---|---|---|---|---|

For profit and missed-opportunity control, include:

| Ticker/Name | Profit Path | Base Upside | Downside If Wrong | Expected Value | Missed-Out Risk | Anti-Miss Plan | No-Chase Rule |
|---|---|---|---|---|---|---|---|

## Position Logic

Position sizing follows evidence, not excitement.

- Core candidate: usually 5%-10% initial position, higher only when valuation,
  liquidity, diversification, and Hades audit support it; never exceed the
  project single-stock cap of 25%.
- Tactical candidate: usually 2%-5%, with explicit catalyst and stop/invalidation.
- Watchlist: 0% until price, data, or catalyst improves.
- Avoid/veto: 0%.

Adjust down for high volatility, weak liquidity, crowded positioning, uncertain
data, policy/geopolitical exposure, customer concentration, or correlated
portfolio exposure. For multi-name baskets, state both single-name caps and total
sector cap.

Anti-miss sizing:

- If sector score is high but stock timing is imperfect, use a small starter
  position only when the downside is predefined and liquidity is sufficient.
- Do not prefer a weak, lagging name merely because it has not risen. A lagging
  buy must beat the leading alternatives on score, R/R, data quality, portfolio
  fit, or Hades audit; otherwise use the leader, a starter, or an ETF/basket.
- Add only on confirmation: earnings revision, volume/relative-strength breakout,
  policy/order confirmation, margin improvement, or price reclaiming a planned
  level.
- If price gaps beyond the buy zone, do not chase automatically. Recalculate
  expected value and either wait for a pullback, use a smaller tactical size, or
  switch to a better risk/reward candidate.
- If the sector is moving but single-stock evidence is weak, consider a smaller
  basket exposure and keep single-name positions on watch until evidence improves.

## AI Supply Chain Lens

For AI-related sectors, split the chain before ranking stocks:

| Chain Segment | Directness | Profit Pool | Pricing Power | Order Visibility | Key Constraint | Veto Risk |
|---|---|---|---|---|---|---|

Separate GPU/ASIC, memory/HBM, PCB/CCL, advanced packaging, optical modules, AI
servers, data centers, cloud CAPEX, power/cooling, and AI applications. Do not
apply one blanket AI allocation to the whole chain.

## Counter-Thesis Requirement

Every sector or stock-picking conclusion must include the strongest credible
counter-thesis:

- What if the catalyst is already priced in?
- What if earnings revision does not follow price action?
- What if the direct beneficiary is elsewhere in the chain?
- What if policy, export control, or customer concentration breaks the thesis?
- What data would make Buffett change the recommendation?
