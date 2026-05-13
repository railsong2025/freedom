# Buffett 工作流元数据

## 基本信息

| 项目 | 内容 |
|---|---|
| 任务文件夹 | `report/record_20260512_221713_002/` |
| 记录序号 | 002 |
| 创建时间 | 2026-05-12 22:17:13 北京时间 |
| 当前执行截止时间 | 2026-05-13 00:00:00 北京时间 |
| 用户请求 | `buffett开始` |
| 市场范围 | US equities only |
| 交易限制 | 只输出本次当前可提交的整股 BUY/SELL；不输出港股/A股交易建议 |

## 任务身份

| 字段 | 值 |
|---|---|
| task_type | `portfolio_review` |
| subject | `us_equity_portfolio` |
| task_key | `portfolio_review:3de533b90a30` |
| task_key 依据 | exact trigger `buffett开始` 固定为美股组合复盘；symbols 使用根 `base_short.md` 的美股持仓排序生成 |

## 输入文件与上一次同类任务

| 项目 | 路径/状态 |
|---|---|
| 根持仓文件 | `base_short.md` |
| 上一次同类任务主记录 | `report/record_20260512_194012_001/` |
| 上次记录合规性 | 包含 `00_metadata.md` 至 `07_final_decision.md` 与 `local_result_snapshot.json`；未发现 `db_record.json`，可作为主历史记录 |
| SQLite | 本轮不写入；未作为主历史来源 |

## 符号范围

当前持仓：AMD, ANET, FLEX, INTC, KO, MSFT, MU, NVDA, SPY, TSM, WDC。  
强周期/AI链特殊关注与 ETF 代理：STX, VRT, SMH, SOXX, QQQ。  
指数背景：IXIC；S&P 500 非交易指数尝试 SPX/GSPC/INX/SP500，若 financeBusiness 返回空则仅用 SPY 代理。

## 数据源计划

| 数据类型 | 首选来源 | 本轮处理 |
|---|---|---|
| 当前价、成交量、量比、P&L、交易测算 | financeBusiness MCP `StockCurrentMarket` / `StockMarketList` / `SettleAccount` / `StockIndexList` | 已刷新持仓、候选与 ETF 代理 |
| 新闻、公告、关键人物、政策 | aiwebsearch `GoogleSearch` 与 `searchJumps`，优先官方/公司/监管页面 | 已采集 Intel、Arista、Vertiv、Goldman Sachs、White House、Micron 等证据 |
| 本地 CLI | `workspace/intelligence/cli.py`, `workspace/analysis/cli.py`, `workspace/verification/cli.py` | 已运行并在各阶段记录 exit 与关键输出 |

## 计划文件

| 阶段 | 输出文件 |
|---|---|
| Buffett 复盘 | `01_buffett_review.md` |
| Buffett 计划 | `02_buffett_plan.md` |
| Zeus 情报 | `03_zeus_intelligence.md` |
| Poseidon 研究 | `04_poseidon_research.md` |
| Hades 验证 | `05_hades_verification.md` |
| 圆桌 | `06_roundtable.md` |
| 最终决策 | `07_final_decision.md` |
| 本地快照 | `local_result_snapshot.json` |

