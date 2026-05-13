# Buffett 工作流元数据

## 任务身份

| 项目 | 内容 |
|---|---|
| 任务文件夹 | `report/record_20260512_194012_001/` |
| 记录序号 | `001` |
| 运行时间 | 2026-05-12 19:40:12 北京时间 |
| 当前执行截止 | 2026-05-13 00:00:00 北京时间 |
| 用户请求 | `buffett开始` |
| canonical task_type | `portfolio_review` |
| canonical subject | `us_equity_portfolio` |
| market | US equities only |
| task_key | `portfolio_review:us_equity_portfolio:20260512:ai_chain_swing` |

## 输入与范围

唯一组合输入源为根目录 `base_short.md`。港股腾讯控股与港元现金只作组合背景和现金换算，不给出港股交易建议；本次最终行动只允许美股/美股 ETF 的整股 BUY/SELL 或 `本次不买入、不卖出`。

## 当前资产与候选范围

| 类别 | 符号 |
|---|---|
| 当前美股/ETF持仓 | AMD, ANET, FLEX, INTC, KO, MSFT, MU, NVDA, SPY, TSM, WDC |
| 背景非美资产 | 0700.HK |
| 强周期/AI链重点复核 | AMD, MU, FLEX, INTC, WDC, STX, VRT, ANET, TSM, NVDA, SMH, SOXX, QQQ |
| AI链补充样本 | AVGO, ASML, AMAT, MRVL |

## 上一次同类任务

`report/` 下没有合规的 `record_*` 历史文件夹，也没有完整 legacy `report/YYYY-MM-DD_*` 文件夹。因此本次没有可作为主历史依据的本地同类决策记录。SQLite 只做只读交叉检查，`decision_db.py last --task-type portfolio_review --subject us_equity_portfolio ...` 返回 `decision: null`，不得补写 SQLite。

## 数据源计划

| 数据类别 | 计划来源 | 使用边界 |
|---|---|---|
| 价格、成交量、估值、P&L价格 | financeBusiness MCP `StockCurrentMarket` + `StockMarketList` | 不用 Yahoo/yfinance/akshare/网页价格替代 |
| 指数背景 | financeBusiness MCP `StockIndexList`，IXIC 可用；S&P 500 指数代码 SPX/GSPC/INX/SP500 返回空，以 SPY 作为可交易代理 |
| 汇率 | financeBusiness MCP `SettleAccount`，HKD/USD=0.1277，时间 2026-05-12 19:41:21 |
| 新闻、公告、人物讲话、政策 | aiwebsearch `GoogleSearch` 与 `searchJumps`；官方/公司/监管来源优先 |
| 本地计算 | `workspace/intelligence/cli.py`, `workspace/analysis/cli.py`, `workspace/verification/cli.py` |

## 计划文件

| 序号 | 文件 |
|---|---|
| 00 | `00_metadata.md` |
| 01 | `01_buffett_review.md` |
| 02 | `02_buffett_plan.md` |
| 03 | `03_zeus_intelligence.md` |
| 04 | `04_poseidon_research.md` |
| 05 | `05_hades_verification.md` |
| 06 | `06_roundtable.md` |
| 07 | `07_final_decision.md` |
| snapshot | `local_result_snapshot.json` |

## 本地修正记录

在 P&L 预跑中发现共享解析器缺少 `西部数据 -> WDC`，同时 AI 链补充样本缺少部分 sector 映射。已在 `workspace/interface/constants.py` 增补 `西部数据/WDC` 及 `STX/VRT/AVGO/ASML/AMAT` 相关映射，使本次和后续工作流不会漏计 WDC。
