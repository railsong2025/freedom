# Buffett 新一轮工作计划

## 目标

在 2026-05-13 00:00 北京时间前，完成 US-equity-only 当前组合复盘，并只输出本次可提交的整股 BUY/SELL 或 `本次不买入、不卖出`。本轮核心问题：上一轮 ANET/VRT 轮动是否仍有效，是否需要改价，是否应完全等待。

## 必须带入下游的 P&L

| 指标 | 数值 |
|---|---:|
| 当前美股持仓市值 | 38,106.53 |
| 当前美股持仓成本 | 40,149.92 |
| 当前未实现 P&L | -2,043.39 |
| 当前未实现 P&L % | -5.09% |
| HKD现金折美元 | 983.29 |
| 估算美股组合权益 | 39,089.82 |

下游必须解释：MSFT 最大亏损为何不机械卖出；ANET 小亏为何可作为机会成本管理；MU/WDC 强周期亏损为何不能平均摊低；NVDA/SPY 盈利垫如何保护。

## Zeus 任务

| 任务 | 要求 |
|---|---|
| 当前/历史行情 | 对持仓、STX、VRT、SMH、SOXX、QQQ 调用 financeBusiness `StockCurrentMarket` 与 `StockMarketList`；记录时间、当前价、前收、涨跌、量比、成交量、区间、数据缺口 |
| 指数/ETF | IXIC 用 `StockIndexList`；S&P 500 非交易代码尝试 SPX/GSPC/INX/SP500，若空则用 SPY |
| 关键人物/事件 | Fed/FOMC、White House/Commerce/BIS/USTR、Intel、Arista、Vertiv、Micron、AI hyperscaler capex、NVIDIA/AMD/TSM/ASML/AVGO/MU/VRT 等相关讲话或事件 |
| AI链漏斗 | AI应用/云CAPEX、GPU/ASIC、代工、存储/HBM、设备/材料、先进封装、光/网络、服务器/EMS、数据中心电力/散热、PCB/CCL、安全/数据基础设施 |
| 缺口披露 | 本地 indicators CLI 若无 financeBusiness CSV，必须标为工具层缺口，不得用非 financeBusiness 替代价格 |

## Poseidon 任务

| 任务 | 要求 |
|---|---|
| P&L研究 | 用 `analysis/cli.py pnl` 复算；判断亏损是可恢复时机问题还是基本面恶化 |
| 板块评分 | 对 memory/HBM/storage、AI infrastructure semiconductors、data center power/cooling 评分 |
| 个股评分 | 重点评分 VRT、ANET、MU、WDC、AMD、NVDA、INTC、FLEX；候选分为核心/战术/观察/回避 |
| 波段计划 | 对 VRT、ANET 运行 `score-short-term` 与 `swing-verdict`；对 VRT 跑 `rr` 与 `sizing` |
| 交易草案 | 只能给当前可提交限价单：ANET SELL 5 @139.50 或更优；VRT BUY 2 @350.00 或更优；若不通过则改为不交易 |

## Hades 任务

| 审计项 | 要求 |
|---|---|
| P&L | `verification/cli.py audit-pnl` 验证 P&L |
| 压力测试 | `stress-test` 记录全组合、半导体、科技、地缘冲击 |
| 合规 | `compliance` 检查整股、现金、25%单股上限、VRT 止损、风险预算、费用 |
| Post-trade | `audit-post-trade` 独立核验交易后现金、费用、已实现/未实现 P&L |
| 否决 | 若 VRT 只有叙事无止损、R/R不足、数据过期、仓位越界、或 ANET 需要向下追卖，则否决 |

## 圆桌任务

圆桌至少三轮：事实校准、投资与仓位、验证反对意见。必须裁决：是否继续卖 ANET、是否降低 VRT 限价、是否追买 MU/WDC/STX/AMD/SMH/SOXX/QQQ、是否因 MSFT 亏损而卖出或加仓。

