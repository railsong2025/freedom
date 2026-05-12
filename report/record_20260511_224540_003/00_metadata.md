# 00_metadata

## 任务身份

| 字段 | 内容 |
|---|---|
| task_key | `portfolio_review:20260511_224540_003_financeBusiness_only` |
| task_type | `portfolio_review` |
| subject | `us_equity_portfolio` |
| market | `US equities` |
| 触发语 | `buffett开始` |
| 任务目录 | `report/record_20260511_224540_003` |
| 运行开始时间 | 2026-05-11 22:45:40 CST |
| 最终持仓刷新 | 2026-05-11 22:58:47-22:59:38 CST |
| 本轮交易截止 | 2026-05-12 00:00:00 CST |
| 数据源政策 | 只使用 financeBusiness MCP；不使用 web、aiwebsearch、akshare、yfinance、Yahoo、Stooq 或本地行情缓存 |

## 输入文件

| 文件 | 用途 |
|---|---|
| `base_short.md` | 根目录基础持仓和现金记录 |
| `report/record_20260511_220100_002/` | 上一次同类任务的合规主记录 |
| `report/record_20260511_151843_001/` | 非合规背景记录；缺 `local_result_snapshot.json` 且含 `db_record.json`，不作为主记录 |

## 本轮输出

| 阶段 | 文件 |
|---|---|
| Buffett 复盘 | `01_buffett_review.md` |
| Buffett 计划 | `02_buffett_plan.md` |
| Zeus 情报 | `03_zeus_intelligence.md` |
| Poseidon 研究 | `04_poseidon_research.md` |
| Hades 验证 | `05_hades_verification.md` |
| 圆桌 | `06_roundtable.md` |
| 最终决策 | `07_final_decision.md` |
| 本地快照 | `local_result_snapshot.json` |

## financeBusiness 工具使用记录

| 工具 | 覆盖范围 |
|---|---|
| `SettleAccount` | HKD/USD=0.1278，更新时间 2026-05-11 09:15:00 |
| `StockCurrentMarket` | KO、MSFT、NVDA、SPY、AMD、TSM、ANET、FLEX、QQQ、XLK、SMH、SOXX、XLC、XLY、XLI、XLU、XLF、XLV、XLP、XLE、XLB、XLRE、MU、WDC、STX、INTC、VRT、DELL、SMCI、AVGO、MRVL、AMAT、ASML、PLTR、SNOW、ORCL、PANW、CRWD、NET、TTMI、COHR、ETN、ARM、AMZN、GOOGL、META |
| `StockMarketList` | KO、MSFT、NVDA、SPY、AMD、TSM、ANET、FLEX、MU、WDC、STX、INTC、VRT、DELL、SMH、QQQ、XLK、SOXX、COHR、AMAT、AVGO、TTMI |

## 本轮限制

financeBusiness 提供结构化价格、估值、成交、52 周区间、短历史和汇率。它不提供完整新闻原文、管理层讲话、SEC 文件、宏观发布原文或政策文本。本轮按照用户要求不调用其他数据源，因此 Zeus 将这些非结构化项标为数据缺口；Hades 不允许用未验证催化剂支持当前新买入。

