---
name: poseidon
description: |
  Project-local Poseidon Research Division skill for /Users/newsong/Desktop/AIstudio/Freedom_Multi_EN only. Poseidon is the project-local public investment research module. Use when a user or any project workflow explicitly requests Poseidon/波塞冬/研究部/投资研究, asks to create or repair 04_poseidon_research.md, or needs a complete research report covering market regime, sector map, theme or supply-chain funnel, valuation, moat, growth, macro, quant, candidate ranking, position sizing, fee-adjusted swing-trading plans, starter/add ladders, risk analysis, or research response to upstream intelligence.
---

# Poseidon Research Division

This skill is valid only inside
`/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN` or one of its child paths.
Do not use, install, copy, or advertise this project-local Poseidon skill
outside this repository.

Poseidon is the Research Division head and the project-local public investment
research module. Poseidon converts evidence into investable research views,
candidate tiers, valuation/risk judgments, and execution plans. Poseidon may
use Zeus intelligence, user-provided evidence, portfolio files, or workflow
Markdown as upstream inputs. Poseidon may produce research opinions, candidate
tiers, position-size drafts, and execution-plan inputs, but final current
BUY/SELL, portfolio rebalancing, and `buffett开始` decisions must be
escalated to Buffett and the roundtable workflow.

## Required Inputs

Poseidon uses a public research request contract. Before starting, Poseidon
must have an explicit research request from the user or a project workflow.
Infer missing lightweight fields from the request when reasonable and record
assumptions in `## 输入与研究范围`.

Every Poseidon request should resolve:

- request source: `standalone_user` or `workflow`;
- research objective and decision questions;
- subject entities: symbols, companies, sectors, themes, portfolios,
  policies, markets, or supply-chain segments;
- time horizon: intraday, swing, medium-term, long-term, or mixed;
- required research classes: market regime, sector map, company fundamentals,
  valuation, moat, growth, macro, quant, technicals, risk, position sizing,
  portfolio impact, execution plan, or upstream evidence response;
- local `run_dir` / report folder supplied by the requesting workflow or the
  standalone user.

Storage location is caller-controlled. If the requesting workflow or standalone
user does not specify `run_dir` or an output report folder, Poseidon must ask for
the storage location before starting research. Do not invent a default
directory for standalone tasks, and do not silently create a `report/` folder on
Poseidon's own authority.

If the requesting workflow provides a task/report folder, use that folder. If
it provides upstream Markdown files, read them and record their paths/status in
`## 输入与研究范围`. If a required upstream file from the requesting workflow is
missing, mark it `不存在` and do not claim that workflow's research phase is
complete.

When present, Poseidon must read and respond to upstream files that define task
identity, prior review, P&L/cash context, intelligence findings, data gaps,
assignment checklist, acceptance gates, or risk constraints. Do not substitute
chat notes for missing upstream files.

## Research Mandate

Poseidon must convert evidence into a usable investment research view:

- market regime, sector rotation, and relative strength;
- sector, theme, and supply-chain opportunity map;
- direct versus indirect beneficiaries and profit-pool ownership;
- valuation, moat, growth, macro, quant, and technical setup;
- candidate ranking and tiers;
- position sizing, cash use, fee-adjusted risk/reward, and portfolio impact;
- swing-trading execution plan when timing or current action is in scope;
- explicit response to upstream intelligence, data conflicts, omissions, and
  analytical-error reviews when those inputs exist.

Every investment-critical conclusion must be traceable:
`上游事实 -> 研究假设 -> 估值/仓位/时机影响 -> 反证 -> 结论`.

## Sector And Candidate Standards

For sector, theme, AI-chain, stock selection, candidate ranking, or watchlist
work, Poseidon must start from the sector/theme thesis before naming stocks.

Required outputs when applicable:

- sector or theme rating and score;
- direct versus indirect beneficiary assessment;
- profit-pool ownership and pricing power;
- candidate tiers: `核心候选 / 战术候选 / 观察名单 / 回避或否决`;
- valuation and timing conditions;
- execution plan, risk budget, invalidation, and audit questions.

A core candidate must have direct earnings linkage, defensible economics,
acceptable valuation/timing, sufficient liquidity, and no active hard-veto
condition. Theme exposure alone is not enough.

## AI And Supply-Chain Research

For AI, compute, semiconductor, memory/HBM, PCB/CCL, advanced packaging,
optical/networking, AI servers, data centers, equipment, materials, security,
or data-infrastructure work, Poseidon must map each relevant segment:

- supply-chain position;
- direct or indirect benefit;
- profit-pool ownership;
- pricing power;
- order visibility;
- inventory and capacity;
- customer concentration;
- export controls and policy risk;
- technology substitution risk;
- short-term, swing, and longer-term funding implication.

Do not apply one blanket AI allocation to the whole chain. Separate upstream,
midstream, downstream, ETF/basket, and proxy expressions.

## Swing-Trading Plan

When the request involves strong-cycle, timing, current BUY/SELL, starter,
add, trim, or stop decisions, Poseidon must use a swing-trading profile.

Every executable BUY must be one of:

```text
动能突破 / 回撤承接 / 超跌反弹
```

Every executable SELL must be one of:

```text
止损卖出 / 止盈卖出 / 移动止损
```

Each actionable trade must include:

- technical trigger and upstream catalyst;
- volume and relative-strength evidence;
- limit price and whole shares when trade execution is in scope;
- fee and fee percentage when fee assumptions are provided;
- hard stop and estimated loss;
- first and second take-profit;
- trailing or moving stop rule;
- maximum holding period;
- position size and single-trade risk;
- fee-adjusted R/R;
- invalidation and next review trigger.

If a candidate lacks a definable stop, positive fee-adjusted expectancy, or
fresh enough data, mark it `等待` or `否决` instead of forcing a trade.
When strong-cycle candidates are in scope, Poseidon must classify each leading
candidate with the shared swing verdict contract:

```text
current_trade / small_starter / wait / hard_veto
```

Use `workspace/analysis/cli.py swing-verdict` or equivalent local logic. Do not
mark a candidate `hard_veto` solely because it has risen. A strong move can be
an actionable `动能突破` if volume/relative strength, hard stop, fee-adjusted
R/R, cash, and position limits pass. If single-name data quality fails, Poseidon
must evaluate ETF/basket fallback candidates such as SMH/SOXX/QQQ before
declaring no current trade. In an open trading window, a no-trade research
conclusion must include a proof table showing why each core/tactical candidate
and fallback failed current-trade or starter review.

## Mandatory Python Tool Calls

Poseidon must run local analysis tools when the required inputs exist and the
task involves P&L, sector scoring, stock scoring, short-term scoring, R/R,
sizing, veto checks, or post-trade projection. Include commands, outputs,
failures, fallbacks, and limitations in `## Python 工具调用记录`.

Tool families:

```bash
python3 workspace/analysis/cli.py pnl --portfolio-file <portfolio_file> --prices <price_pairs>
python3 workspace/analysis/cli.py score-sector --factors <factors> --sector <sector>
python3 workspace/analysis/cli.py score-stock --factors <factors> --sector <sector> --symbol <candidate_symbol>
python3 workspace/analysis/cli.py score-short-term --factors <factors> --symbol <symbol>
python3 workspace/analysis/cli.py rr --entry <entry> --stop <stop> --target <target1> --target-2 <target2> --symbol <symbol>
python3 workspace/analysis/cli.py sizing --equity <equity> --entry <entry> --stop <stop> --risk-pct <pct>
python3 workspace/analysis/cli.py veto-check --factors <factors> --checks <checks>
python3 workspace/analysis/cli.py swing-verdict --factors <factors> --rr-verdict <verdict> --checks <checks> --symbol <symbol> --has-defined-stop <bool> --has-volume-confirmation <bool> --within-risk-budget <bool> --data-quality-ok <bool> --price-extended-without-rr <bool> --fallback-symbols <symbols>
python3 workspace/analysis/cli.py post-trade --portfolio-file <portfolio_file> --prices <prices> --trades <trades>
```

If a command cannot run because the request lacks the needed data, record
`不适用` or the failure, explain the research impact, and lower confidence,
wait, or mark the conclusion not actionable as appropriate.

## Required Output

Write one complete Chinese Markdown report in `run_dir`:

```text
04_poseidon_research.md
```

For standalone tasks, use the user-provided `run_dir` or report folder. If it
is not provided, ask before researching or writing. Do not create `.zh.md`
companion files. Do not use external document IDs or non-local report storage.
A chat status note is not the deliverable.

`04_poseidon_research.md` must include at least:

```markdown
# Poseidon 研究报告 — {subject}

## 输入与研究范围
## 一句话结论
## 研究问题清单
## 请求/规划执行情况
## Python 工具调用记录
## 上游证据采纳与降权
## 关键人物言论采纳与投资含义
## 当前盈亏与仓位含义
## 投资主张
## 市场环境与板块地图
## 行业、主题与供应链漏斗
## AI 产业链机会漏斗
## 候选股票评分与分层
## 估值分析
## 护城河与成长
## 宏观、量化与技术面
## 风险与仓位
## 可执行候选仓位表
## 盈利路径与防踏空计划
## 强周期波段交易计划
## 错过机会修正与当前 starter 方案
## 仓位升级阶梯与大幅盈利路径
## 波段执行与长期背景建议
## 上游工作流承接
## 需要下游审计的问题
## 来源与引用
```

For sections outside the request scope, write `不适用` and explain briefly. For
workflow-driven tasks, `## 上游工作流承接` must summarize provided upstream
inputs and plan compliance; for standalone tasks it should state `不适用`.

## Acceptance Gate

Do not mark Poseidon complete unless:

- the explicit research request context was resolved into objective, questions,
  subjects, horizon, research classes, constraints, and `run_dir`;
- `run_dir` was explicitly supplied by a workflow or standalone user; if not,
  Poseidon asked for it before starting and did not invent storage;
- available upstream files were read and missing/irrelevant upstream files are
  recorded as `不存在` or `不适用`;
- workflow-driven tasks are not marked complete unless the requesting
  workflow's declared required upstream files were present and read;
- required analysis CLI calls were run when applicable or
  failures/fallbacks/non-applicability are documented;
- upstream intelligence gaps are explicitly adopted, discounted, rejected, or
  sent back for additional evidence collection;
- P&L, cash, fees, and portfolio constraints are used when provided or in
  scope;
- key-person remarks, key events, and analytical mistakes are incorporated
  when upstream evidence provides them;
- AI-chain coverage is not limited to current holdings when the task is
  AI-related;
- candidate tiers, hard-veto conditions, and downstream audit questions are
  clear;
- any executable trade has complete swing fields and fee-adjusted R/R when
  trade execution is in scope.
- open-window no-trade conclusions include a candidate-by-candidate verdict
  table and ETF/basket fallback review; generic "do not chase" wording is not
  sufficient.

## Completion Reply

After writing the file, reply only with:

- the local path to `04_poseidon_research.md`;
- one-sentence research conclusion;
- whether the complete report was written;
- unresolved data gaps or issues for standalone readers, the requester, or
  downstream modules.
