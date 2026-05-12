# 02_buffett_plan

## 本轮目标

在 2026-05-12 00:00:00 CST 前完成 US-equity-only 全流程，并给出当前整股 BUY/SELL 或 `本次不买入、不卖出`。所有事实行情和结构化市场数据只允许使用 financeBusiness。

## 任务边界

| 项目 | 约束 |
|---|---|
| 市场 | 仅美股和美股 ETF |
| 输入 | `base_short.md`、上一轮同类本地报告、financeBusiness MCP |
| 禁止 | Web、aiwebsearch、akshare、AKTools、yfinance、Yahoo、Stooq、非 financeBusiness 行情缓存 |
| 交易单位 | 整股，不允许碎股 |
| 费用 | 每笔 BUY/SELL 固定 5 USD |
| 最终当前操作 | 只列本轮立即执行的 BUY/SELL 或 `本次不买入、不卖出` |
| 记录 | 只写本地 Markdown 和 `local_result_snapshot.json`，不写 SQLite，不生成 `db_record.json` |

## 给 Zeus 的任务

Zeus 必须写入 `03_zeus_intelligence.md`：

| 要求 | 验收标准 |
|---|---|
| 持仓当前价 | KO、MSFT、NVDA、SPY、AMD、TSM、ANET、FLEX 均必须有 financeBusiness `StockCurrentMarket` |
| 持仓短历史 | 至少覆盖 2026-05-01 至 2026-05-11 的 `StockMarketList`，用于趋势判断 |
| 汇率 | HKD/USD 只能用 financeBusiness `SettleAccount` |
| US sector map | 覆盖 SPY、QQQ、XLK、SMH、SOXX、XLC、XLY、XLI、XLU、XLF、XLV、XLP、XLE、XLB、XLRE |
| AI opportunity funnel | 覆盖 AI 应用、云 CAPEX、GPU/ASIC、半导体、存储/HBM、先进封装、光通信/网络、AI 服务器、数据中心电力冷却、PCB/CCL、设备、材料、安全/数据基础设施 |
| 数据缺口 | 对 key-person remarks、key events、news/filings/source text 做显式缺口标记，不得虚构 |
| 反证 | 把价格延伸、估值过高、EPS 负、量比缺失、当日冲高回落和弱势分化列入反证 |

## 给 Poseidon 的任务

Poseidon 必须写入 `04_poseidon_research.md`：

| 要求 | 验收标准 |
|---|---|
| Sector-first | 先判定板块相对强弱，再进入个股 |
| AI 漏斗 | 每个链条环节给出直接/间接受益、利润池、定价权、估值/拥挤度和当前动作 |
| 候选分层 | 必须有 core candidates、tactical candidates、watch-only、avoid/veto current trade |
| 当前持仓 P&L | 必须说明 MSFT 大亏、FLEX 小亏、NVDA/AMD/SPY 盈利如何影响买卖 |
| swing 规则 | 必须有止损、第一目标、费用后 R/R、no-chase 边界 |
| 不得保证收益 | 用正期望、风险预算、失效条件表达，不使用保证收益语言 |

## 给 Hades 的任务

Hades 必须写入 `05_hades_verification.md`：

| 要求 | 验收标准 |
|---|---|
| P&L 审计 | 复核总市值 18,621.04、成本 19,976.83、未实现 P&L -1,355.79 |
| 合规审计 | 单股不超过估算权益 25%，交易费和现金影响正确 |
| 数据质量 | 检查 financeBusiness 当前价、短历史、量比、ETF 字段和非结构化缺口 |
| 压力测试 | 至少说明 -10%、-20%、-30%、半导体/科技冲击、地缘冲击 |
| 交易否决 | 对当前 BUY/SELL 给出批准、否决或有条件同意 |
| 交易后 P&L | 若无交易，必须验证现金、持仓、费用和已实现盈亏均不变 |

## 圆桌要求

`06_roundtable.md` 必须让 Buffett、Zeus、Poseidon、Hades 对以下事项达成结论：

1. Buffett 自我反思是否有效。
2. financeBusiness-only 数据是否足以支持当前新买入。
3. FLEX 是否触发 135.10 风控线。
4. AI 强周期的机会是否已经有足够买点，还是只是高位拥挤。
5. 最终当前操作是否为 BUY/SELL 或 `本次不买入、不卖出`。

## 预设硬性否决

| 条件 | 结果 |
|---|---|
| 任一交易缺少 financeBusiness 当前价 | 否决该交易 |
| 交易依赖新闻/讲话/文件但 financeBusiness 无法验证 | 否决当前新买入 |
| 价格已贴近 52 周高点且费用后 R/R 不足 | 否决追买 |
| FLEX 未跌破 135.10 | 不允许仅因小亏卖出 |
| MSFT 亏损但无新证据 | 不允许仅因亏损补仓 |
| 最终时间超过 2026-05-12 00:00:00 CST | 强制 `本次不买入、不卖出` |

