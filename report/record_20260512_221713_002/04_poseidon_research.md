# Poseidon 研究报告

## 输入与范围

已读取 `00_metadata.md` 至 `03_zeus_intelligence.md`。本报告聚焦数日至数周 swing；不提供港股或 A 股交易建议。

## 计划执行情况

| 计划项 | 状态 | 结论 |
|---|---|---|
| P&L进入仓位判断 | 完成 | 亏损扩大到 -5.09%，新增买入必须小仓且有止损 |
| sector-first | 完成 | AI链仍强，但盘中风险偏好回落，板块评分降为 neutral/watch |
| AI链漏斗 | 完成 | 数据中心电力/散热仍是组合缺口 |
| swing verdict | 完成 | VRT=`small_starter`；ANET=`hard_veto` 作为新增 swing 买入，适合卖出弱项 |
| post-trade | 完成 | ANET SELL + VRT BUY 工具测算通过 |

## Python 工具调用记录

| 命令 | exit | 关键输出 |
|---|---:|---|
| `analysis/cli.py pnl --portfolio-file base_short.md --prices ...` | 0 | 美股市值 38,106.53，成本 40,149.92，未实现 P&L -2,043.39 |
| `analysis/cli.py pnl --portfolio-file portfolio_usd_working.md --prices ...` | 0 | 含折算现金后估算权益 39,089.82 |
| `score-sector memory_HBM_storage` | 0 | score 69.60，`neutral`，因拥挤/估值降权 |
| `score-sector data_center_power_cooling` | 0 | score 69.70，`neutral`，接近 tactical，但需低价 |
| `score-sector AI_infrastructure_semiconductors` | 0 | score 64.20，`neutral` |
| `score-stock VRT` | 0 | score 72.35，`tactical` |
| `score-stock ANET/MU/WDC/AMD/NVDA/INTC/FLEX` | 0 | NVDA/MU/VRT 战术；ANET/WDC/AMD 观察；INTC/FLEX 当前 swing 回避 |
| `score-short-term VRT` | 0 | 72.40，`tactical_only` |
| `rr VRT entry350 stop338 target372/399 shares2` | 0 | target1 R/R 0.99 insufficient；target2 R/R 2.57 positive |
| `sizing equity39089.82 entry350 stop338 cash983.29` | 0 | 2股，风险约34.20美元，仓位1.79%，现金受限小 starter |
| `swing-verdict VRT` | 0 | `small_starter` |
| `swing-verdict ANET` | 0 | `hard_veto`，新增买入不可行 |
| `post-trade ANET SELL 5 / VRT BUY 2` | 0 | realized P&L -21.40，fees 10.00，post cash 970.79，post equity 39,078.92 |

## 当前盈亏与仓位含义

| 观察 | 研究含义 |
|---|---|
| 总未实现亏损扩大至 -2,043.39 | 不允许继续堆同一条半导体/存储风险 |
| MSFT -19.38% | 不补仓摊低；也不因恐惧卖出，等待云AI基本面新证据 |
| MU/WDC从接近盈利转为亏损 | 说明高位拥挤回撤已发生，不能追买 |
| ANET 小亏但相对弱 | 可在反弹中退出，释放现金与注意力 |
| NVDA/SPY盈利 | 保留盈利垫，不做无必要止盈 |

## 板块地图

| Sector/Theme | Score | Rating | Cycle Phase | Key Catalyst | Profit-Pool Direction | Main Risk | Action |
|---|---:|---|---|---|---|---|---|
| memory/HBM/storage | 69.60 | neutral/watch | 强周期高位回撤 | HBM紧缺、AI内存 | MU/WDC/STX | 垂直涨幅、拥挤 | 持有已有，不追 |
| data center power/cooling | 69.70 | neutral/watch | 回撤承接观察 | AI数据中心电力/散热瓶颈 | VRT/ETN/PWR | 高估值、高波动 | 低价小 starter |
| AI infrastructure semiconductors | 64.20 | neutral/watch | 强势后降温 | GPU/ASIC/代工/封装 | NVDA/AMD/TSM/INTC | 估值、出口/关税、回撤 | 保留已有，不加 |
| cloud/applications | 60-68 | neutral/watch | 基本面好但股价分化 | AI monetization | MSFT/ORCL/PLTR | CAPEX回报与利率 | 不加 MSFT |
| AI networking/optical | 55-65 | underweight/watch | 财报后分化 | AI网络 | ANET/CIEN/COHR | 指引低于预期 | 卖 ANET 小仓 |

## AI 机会漏斗与股票分层

| Tier | Ticker | Role In Thesis | Directness | Score | Valuation View | Timing | Key Risk | Action |
|---|---|---|---|---:|---|---|---|---|
| 战术候选 | VRT | 数据中心电力/散热 | 直接 | 72.35 | 贵，但组合缺口明确 | 只在350附近回撤承接 | 估值回撤快 | BUY 2 @350 |
| 战术持有 | NVDA | GPU利润池 | 直接 | 74.40 | 估值不便宜 | 强于链条 | 监管/估值 | 持有 |
| 战术持有 | MU | HBM/DRAM | 直接 | 70.65 | 周期强但拥挤 | 今日回撤 | 周期反转 | 持有不追 |
| 观察 | ANET | AI网络 | 直接 | 67.45 | 基本面好但短线弱 | 反弹中 | 指引失望 | SELL 5 @139.50 |
| 观察 | AMD | AI GPU/CPU | 直接 | 66.45 | 估值高 | 高位回撤 | 竞争/估值 | 持有不追 |
| 观察 | WDC | 存储/NAND | 直接 | 64.10 | 强周期已反映 | 回撤 | 周期风险 | 持有不追 |
| 回避/等待 | INTC | AI CPU/foundry turnaround | 直接/政策 | 56.10 | 转型不确定 | 高量回落 | 执行风险 | 持有不加 |
| 回避/等待 | FLEX | AI服务器/EMS | 间接/直接 | 59.90 | 估值和涨幅已高 | 高位回落 | 毛利/周期 | 持有不加 |

## 当前交易草案

| Ticker | Trade Type | Limit | Stop | Target 1 | Target 2 | Trailing Stop | Max Hold | Size | Risk $ | Fee-Adjusted R/R |
|---|---|---:|---:|---:|---:|---|---|---:|---:|---:|
| ANET | 止损/换仓卖出 | 139.50 | 不适用 | 不适用 | 不适用 | 若未成交且重新站上142.80，下一轮复盘 | 本次窗口 | 5 | 实现约 -21.40 含费 | 释放弱项 |
| VRT | 回撤承接小仓 starter | 350.00 | 338.00 | 372.00 | 399.00 | 到372后不加仓；若触及399或回落破10日低点，复盘止盈/移动止损 | 2-6周 | 2 | 34.20 | T1 0.99 / T2 2.57 |

## 反面论点

1. VRT 第一目标的费用后 R/R 不足，必须依赖第二目标才有正期望；因此只能小仓 starter。
2. ANET 盘中反弹，卖出可能错过修复；但 5月初以来大幅落后，且组合没有足够现金同时保留弱项和补 VRT。
3. 半导体/AI链同步回撤可能继续扩大，本轮不加 MU/WDC/AMD/SMH/SOXX/QQQ 是为了防止组合相关性失控。

## Poseidon 结论

建议执行两笔当前限价单：SELL ANET 5 @139.50 或更优；BUY VRT 2 @350.00 或更优。若任一价格无法在 2026-05-13 00:00 北京时间前达到，不追价；未成交部分自动失效。

