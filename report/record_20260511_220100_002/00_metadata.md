# 00_metadata

## 任务身份

| 项目 | 内容 |
|---|---|
| 用户触发 | `$buffett 开始`，按项目 `buffett开始` 完整流程处理 |
| 运行时间 | 2026-05-11 22:01:00 CST（北京时间） |
| 交易截止 | 2026-05-12 00:00:00 CST（北京时间） |
| 任务目录 | `/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN/report/record_20260511_220100_002` |
| 输入文件 | `/Users/newsong/Desktop/AIstudio/Freedom_Multi_EN/base_short.md` |
| task_type | `portfolio_review` |
| subject | `us_equity_portfolio` |
| market | `US equities` |
| task_key | `portfolio_review:993c7d93e383` |
| report 命名 | `record_YYYYMMDD_HHMMSS_序号` |
| 上一轮本地记录 | `report/record_20260511_151843_001`，非合规背景：含 `db_record.json` 且缺 `local_result_snapshot.json` |
| SQLite 模式 | 只读交叉参考；本轮禁止写入 |

Why this task_key：`buffett开始` 是固定美股组合复盘与当前操作任务，固定为 `task_type=portfolio_review`、`subject=us_equity_portfolio`、`market=US equities`。本轮不把持仓变化或候选池写入 task_key，避免组合复盘的历史流断裂。

## 输入与资产范围

- 当前解析出的 USD 持仓：KO、MSFT、NVDA、SPY、AMD、TSM、ANET、FLEX。
- 港股持仓：腾讯控股 400 股，成本 549 港元，仅作背景，不给港股/A 股交易建议。
- 可投资资金：165,627 HKD；financeBusiness `SettleAccount` 2026-05-11 09:15:00 显示 HKD/USD=0.1278，估算约 21,167.13 USD。实际可用美元需券商换汇确认。
- 费用：每笔 BUY/SELL 固定 USD 5。
- 交易单位：整股；禁止碎股。

## 当前价格快照

| Ticker | financeBusiness StockCurrentMarket 更新时间 | 最新价 | 昨收 | 盘中涨跌 | 量比 | 状态 |
|---|---|---:|---:|---:|---:|---|
| KO | 2026-05-11 21:57:08 | 78.25 | 78.42 | -0.2168% | 1.42 | 交易中 |
| MSFT | 2026-05-11 21:57:22 | 409.71 | 415.12 | -1.3032% | 3.16 | 交易中 |
| NVDA | 2026-05-11 21:57:28 | 217.485 | 215.20 | 1.0618% | 3.27 | 交易中 |
| SPY | 2026-05-11 21:57:34 | 738.40 | 737.62 | 0.1057% | None | 交易中 |
| AMD | 2026-05-11 21:57:39 | 452.38 | 455.19 | -0.6173% | 3.00 | 交易中 |
| TSM | 2026-05-11 21:57:43 | 399.335 | 411.68 | -2.9987% | 3.96 | 交易中 |
| ANET | 2026-05-11 21:57:48 | 141.10 | 141.77 | -0.4726% | 1.31 | 交易中 |
| FLEX | 2026-05-11 21:56:59 | 143.71 | 142.17 | 1.0832% | 1.34 | 交易中 |

## 本轮重点候选与 ETF fallback

必须覆盖上一轮持仓与强周期特别观察：AMD、MU、FLEX、INTC、WDC、STX、VRT、ANET、TSM、NVDA、SMH、SOXX、QQQ、DELL。AI 全链条仍需在 Zeus/Poseidon/Hades 报告中覆盖：AI 应用/云 CAPEX、GPU/ASIC、半导体制造、存储/HBM、设备/EDA/材料、先进封装、光模块/网络、AI server/ODM/EMS、数据中心电力/散热、PCB/CCL、安全/数据基础设施与 ETF/basket。

## 数据源计划

- 结构化行情：financeBusiness MCP `StockCurrentMarket` 与 `StockMarketList` 优先；本地 CLI 使用 akshare/适配层作为第二路径，已记录 CLI 字段缺口。
- 第二来源：本地 `workspace/intelligence/cli.py indicators` 通过网络权限取到 2026-05-08 日线与技术指标，但未取得 2026-05-11 实时报价，故只用于趋势/指标，不作为当前下单价唯一依据。
- 新闻/公告/关键人物：使用官方公司 IR、SEC/FOMC 官方页、aiwebsearch/兼容搜索结果；关键事实需写影响链和反证。

## 计划文件

- `00_metadata.md`
- `01_buffett_review.md`
- `02_buffett_plan.md`
- `03_zeus_intelligence.md`
- `04_poseidon_research.md`
- `05_hades_verification.md`
- `06_roundtable.md`
- `07_final_decision.md`
- `local_result_snapshot.json`

SQLite 写入策略：`skipped_by_disabled_policy`。
