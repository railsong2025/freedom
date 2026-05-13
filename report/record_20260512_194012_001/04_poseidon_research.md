# Poseidon 研究报告 — 美股组合与 AI 链机会

## 输入与研究范围

已读取 `00_metadata.md`, `01_buffett_review.md`, `02_buffett_plan.md`, `03_zeus_intelligence.md`。本报告聚焦美股组合当前 BUY/SELL，时间框架为数日至数周 swing，不给出港股或 A 股交易建议。

## 一句话结论

AI链仍是强周期主线，但组合已经重仓半导体/存储；本轮最优动作不是继续追 MU/WDC/AMD，而是卖出相对破位的 ANET，并用极小仓位在 VRT 建立数据中心电力/散热 starter。

## 请求/规划执行情况

| 计划项 | 状态 | 处理 |
|---|---|---|
| P&L进入仓位判断 | 完成 | MSFT亏损不机械卖；ANET弱势小亏可退出；MU/WDC已有暴露不追 |
| sector-first | 完成 | 半导体、存储/HBM、数据中心电力评分 |
| AI链漏斗 | 完成 | 覆盖应用、GPU、代工、存储、设备、网络、服务器、电力、PCB、安全 |
| swing verdict | 完成 | VRT=`small_starter`，ANET=`hard_veto`，其他候选等待/不追 |
| post-trade | 完成 | 使用衍生 USD 工作组合文件计算，源自 `base_short.md` 与 HKD/USD 0.1277 |

## Python 工具调用记录

| 命令 | exit | 关键输出 |
|---|---:|---|
| `analysis/cli.py pnl --portfolio-file base_short.md --prices ...` | 0 | 美股市值 38,993.91，成本 40,149.92，未实现 P&L -1,156.01 |
| `score-sector AI_infrastructure_semiconductors` | 0 | score 77.20，`tactical_overweight` |
| `score-sector data_center_power_cooling` | 0 | score 76.05，`tactical_overweight` |
| `score-sector memory_HBM_storage` | 0 | score 78.85，`tactical_overweight` |
| `score-stock VRT/MU/WDC/AMD/ANET/STX/INTC` | 0 | VRT 73.90 tactical；MU 77.60 tactical；WDC 72.80 tactical；ANET 66.15 watch |
| `score-short-term VRT` | 0 | 79.85，`tactical_only` |
| `rr VRT entry365 stop349 target399 target420 shares2` | 0 | target1 R/R 1.37 marginal；target2 R/R 2.36 positive |
| `sizing equity39977.20 entry365 stop349 cash983.29` | 0 | cash限制下 2 股，风险约 42.20，仓位 1.83% |
| `swing-verdict VRT` | 0 | `small_starter`，无 hard veto |
| `swing-verdict ANET` | 0 | `hard_veto`，原因：相对强度/量能未确认，费用后 R/R 不足 |
| `post-trade ANET SELL 5 / VRT BUY 2` | 0 | realized P&L -38.90，fees 10.00，post cash 923.29，post equity 39,965.05 |

## 上游证据采纳与降权

采纳 Zeus 的 financeBusiness 当前/历史行情、Intel 官方 Q1、White House 半导体政策、AI CAPEX 新闻证据。降权项：本地 indicators CLI 未能直接消费 MCP 数据，无法自动生成 MA/ATR；因此趋势判断用 financeBusiness 20日历史人工计算，不把缺失 ATR 伪装成精确数据。

## 当前盈亏与仓位含义

| 观察 | 投资含义 |
|---|---|
| MSFT -18.60%，亏损金额最大 | 不加仓摊低；但仓位未超 25%，云AI基本面未被证伪，暂不卖 |
| ANET -4.45%，且近期连续弱于半导体链 | 小亏可作为机会成本释放，卖出比等待“回本”更纪律化 |
| MU/WDC接近成本但单日/20日极强 | 不追加，保留已有敞口并等待盈利垫扩大 |
| NVDA +19.11% | 保留核心 AI GPU 曝光，不因盈利小额止盈 |
| 可用现金仅约 983.29 美元 | 新买入必须是小 starter，且单笔费用比例要可接受 |

## 市场环境与板块地图

| Sector/Theme | Score | Rating | Cycle Phase | Key Catalyst | Profit-Pool Direction | Main Risk | Action |
|---|---:|---|---|---|---|---|---|
| memory/HBM/storage | 78.85 | tactical_overweight | 强周期上行后段 | AI内存紧缺、CAPEX上修 | MU/WDC/STX | 垂直拉升、估值拥挤 | 持有已有，不追买 |
| AI infrastructure semiconductors | 77.20 | tactical_overweight | 强势趋势 | GPU/ASIC/代工/封装需求 | NVDA/AMD/TSM/INTC/AVGO | 出口管制、估值 | 持有已有，等待回撤 |
| data center power/cooling | 76.05 | tactical_overweight | 确认加速 | 电力/散热瓶颈、CAPEX外溢 | VRT/ETN/PWR | 高估值、高波动 | VRT 小 starter |
| cloud/applications | 65-70 | neutral/watch | 基本面好但股价分化 | AI monetization | MSFT/ORCL/PLTR | 利率与CAPEX回报质疑 | 暂不加仓 |
| networking/optical | 58-68 | neutral/watch | 分化 | AI网络需求 | ANET/CIEN/COHR | ANET短线破位 | 退出 ANET |

## AI 产业链机会漏斗

| 链条 | 核心/战术/观察 | 研究结论 |
|---|---|---|
| AI应用/云CAPEX | MSFT=观察持有 | 长期需求源仍在，但当前价格弱，不适合补仓 |
| GPU/ASIC | NVDA=核心持有；AMD=战术持有；AVGO/MRVL=观察 | 组合已有足够敞口 |
| 代工/制造 | TSM=观察持有；INTC=观察/政策弹性 | INTC独立看待，AI CPU+foundry转型已有价格反映 |
| 存储/HBM | MU/WDC=战术持有；STX=观察 | 利润池最强但太垂直，避免新增追高 |
| 先进封装/设备 | ASML/AMAT=观察 | 上游受益但政策/估值复杂，不做当前交易 |
| 光/网络 | ANET=退出候选 | 相对弱，跌破成本后未见修复 |
| AI服务器/EMS/PCB | FLEX=持有 | 已有小仓，不追 |
| 数据中心电力/散热 | VRT=战术候选 | 组合缺口，适合 2 股小 starter |
| 安全/数据基础设施 | PANW/CRWD/NET/SNOW/DDOG=观察 | 与本次现金和持仓矛盾无直接关系 |

## 候选股票评分与分层

| Tier | Ticker | Role In Thesis | Directness | Score | Valuation View | Timing | Key Risk | Action |
|---|---|---|---|---:|---|---|---|---|
| 战术候选 | MU | HBM/DRAM利润池 | 直接 | 77.60 | 估值已计入强周期 | 过热 | 回撤/盈利保护，不追 |
| 战术候选 | VRT | 数据中心电力/散热 | 直接 | 73.90 | 贵但缺口明确 | 动能突破后小回撤买 | 高估值、回撤快 | 买 2 股 starter |
| 战术候选 | WDC | 存储设备/NAND | 直接 | 72.80 | 接近成本但涨幅大 | 过热 | 周期反转 | 持有不追 |
| 战术候选 | AMD | AI GPU/CPU | 直接 | 72.05 | 高估值 | 创高附近 | 竞争与估值 | 持有不追 |
| 观察 | STX | 存储设备 | 直接 | 67.80 | 估值偏满 | 过热 | PB/盈利波动 | 不买 |
| 观察 | ANET | 网络 | 直接 | 66.15 | 基本面好但短线破位 | 弱 | 相对弱势 | 卖出 |
| 观察 | INTC | AI CPU/foundry turnaround | 直接/政策 | 65.30 | 转型估值修复 | 已急涨 | 执行风险 | 持有不追 |

## 当前交易研究草案

| Ticker | Trade Type | Limit | Stop | Target 1 | Target 2 | Trailing Stop | Max Hold | Size | Risk $ | Fee-Adjusted R/R |
|---|---|---:|---:|---:|---:|---|---|---:|---:|---:|
| ANET | 止损卖出 | 136.00 | 不适用 | 不适用 | 不适用 | 若未卖出且收复142.80再复盘 | 本次窗口 | 5 | 已知亏损38.90含费 | 退出弱项 |
| VRT | 动能突破小仓starter | 365.00 | 349.00 | 399.00 | 420.00 | 到399后止损抬至370.05或10日低点较高者 | 2-6周 | 2 | 42.20 | target1 1.37 / target2 2.36 |

## 反面论点

1. VRT 单日 +8.22%，不是低位买入，若开盘高开继续拉升，365限价可能无法成交；不能追价。
2. 组合半导体/AI链已重，新增 VRT 虽是不同环节，但仍相关于 AI CAPEX 风险。
3. ANET 退出可能卖在短线低点；但在组合已有强势AI链敞口时，弱项反弹机会成本低于纪律成本。

## Poseidon 结论

建议本次执行：卖出 ANET 5 股，限价 136.00 美元或更优；买入 VRT 2 股，限价 365.00 美元或更优。若 VRT 不回落成交，不上调限价追买；若 ANET 低于 136.00 才能成交，也不下调限价追卖。
